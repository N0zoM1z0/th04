from __future__ import annotations

import json
import subprocess
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import replay_th04_main_exact_units as replay


class MapContributionTests(unittest.TestCase):
    def test_segment_qualifier_disambiguates_multi_segment_module(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            map_path = Path(temporary) / "main.map"
            map_path.write_text(
                " 0AAF:11A4 09B6 C=CODE   S=CIRCLE_TEXT G=MAIN_01 M=th04_main.asm ACBP=48\n"
                " 13A9:0300 0062 C=CODE   S=MAIN_032_TEXT G=MAIN_03 M=th04_main.asm ACBP=48\n",
                encoding="cp437",
            )
            with self.assertRaisesRegex(RuntimeError, "got 2"):
                replay.map_contribution(map_path, "th04_main.asm")
            start, size, line = replay.map_contribution(
                map_path, "th04_main.asm", "CIRCLE_TEXT"
            )
            self.assertEqual(start, 0x0AAF0 + 0x11A4)
            self.assertEqual(size, 0x09B6)
            self.assertIn("S=CIRCLE_TEXT", line)

    def test_segment_qualifier_fails_closed_when_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            map_path = Path(temporary) / "main.map"
            map_path.write_text(
                " 0AAF:11A4 09B6 C=CODE S=CIRCLE_TEXT G=MAIN_01 M=th04_main.asm ACBP=48\n",
                encoding="cp437",
            )
            with self.assertRaisesRegex(RuntimeError, "segment MAIN_032_TEXT, got 0"):
                replay.map_contribution(
                    map_path, "th04_main.asm", "MAIN_032_TEXT"
                )


class UnitDependencyTests(unittest.TestCase):
    def test_dependency_closure_preserves_manifest_order(self) -> None:
        entries = [
            {"id": "base"},
            {"id": "middle", "requires_units": ["base"]},
            {"id": "leaf", "requires_units": ["middle"]},
        ]
        resolved = replay.resolve_unit_dependencies(entries, {"leaf"})
        self.assertEqual([entry["id"] for entry in resolved], ["base", "middle", "leaf"])

    def test_dependency_closure_rejects_unknown_required_unit(self) -> None:
        entries = [{"id": "leaf", "requires_units": ["missing"]}]
        with self.assertRaisesRegex(RuntimeError, "unknown required unit missing"):
            replay.resolve_unit_dependencies(entries, {"leaf"})


class ProducerOverrideTests(unittest.TestCase):
    def test_logical_unit_uses_standalone_producer_without_trigger(self) -> None:
        entry = {
            "id": "prefix",
            "map_module": "prefix.cpp",
            "object_path": "prefix.obj",
            "producer_override_when_unit": "tail",
            "producer_map_module": "combined.cpp",
            "producer_object_path": "combined.obj",
            "producer_map_mode": "contains",
        }
        self.assertEqual(
            replay.resolved_producer_outputs(entry, {"prefix"}),
            ("prefix.cpp", "prefix.obj", "exact"),
        )

    def test_logical_unit_uses_fused_producer_when_trigger_selected(self) -> None:
        entry = {
            "id": "prefix",
            "map_module": "prefix.cpp",
            "object_path": "prefix.obj",
            "producer_override_when_unit": "tail",
            "producer_map_module": "combined.cpp",
            "producer_object_path": "combined.obj",
            "producer_map_mode": "contains",
        }
        self.assertEqual(
            replay.resolved_producer_outputs(entry, {"prefix", "tail"}),
            ("combined.cpp", "combined.obj", "contains"),
        )

    def test_active_override_fails_closed_when_output_is_incomplete(self) -> None:
        entry = {
            "id": "prefix",
            "map_module": "prefix.cpp",
            "object_path": "prefix.obj",
            "producer_override_when_unit": "tail",
            "producer_map_module": "combined.cpp",
        }
        with self.assertRaisesRegex(RuntimeError, "producer override lacks"):
            replay.resolved_producer_outputs(entry, {"prefix", "tail"})


class RepoInputSnapshotTests(unittest.TestCase):
    def test_snapshot_freezes_overlay_and_detects_live_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            snapshot = root / "snapshot"
            source = root / "source"
            repo.mkdir()
            source.mkdir()
            maintained = repo / "unit.cpp"
            maintained.write_bytes(b"first\n")
            entry = {
                "id": "unit-a",
                "repo_source": "unit.cpp",
                "source_mode": "overlay",
                "overlay_path": "unit.cpp",
            }
            with patch.object(replay, "ROOT", repo), patch.object(
                replay, "REC98_COMPAT", repo / "compat" / "rec98"
            ):
                paths = replay.repo_input_paths([entry], [], [])
                receipt = replay.materialize_repo_snapshot(snapshot, paths)
                maintained.write_bytes(b"second\n")
                overlays = replay.overlay_sources(
                    source, [entry], repo_root=snapshot
                )
                self.assertEqual((source / "unit.cpp").read_bytes(), b"first\n")
                self.assertEqual(overlays[0]["sha256"], replay.digest_bytes(b"first\n"))
                with self.assertRaisesRegex(RuntimeError, "repository input changed"):
                    replay.verify_repo_snapshot(receipt)

    def test_snapshot_rejects_drift_during_capture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            snapshot = root / "snapshot"
            repo.mkdir()
            maintained = repo / "unit.cpp"
            maintained.write_bytes(b"first\n")
            real_digest_file = replay.digest_file
            mutated = False

            def mutate_before_verify(path: Path) -> str:
                nonlocal mutated
                if path == maintained and not mutated:
                    mutated = True
                    maintained.write_bytes(b"second\n")
                return real_digest_file(path)

            with patch.object(replay, "ROOT", repo), patch.object(
                replay, "digest_file", side_effect=mutate_before_verify
            ):
                with self.assertRaisesRegex(RuntimeError, "changed while snapshotting"):
                    replay.materialize_repo_snapshot(snapshot, [Path("unit.cpp")])

    def test_snapshot_rejects_symlinked_live_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            snapshot = root / "snapshot"
            repo.mkdir()
            target = repo / "real.cpp"
            target.write_bytes(b"body\n")
            (repo / "unit.cpp").symlink_to(target.name)
            with patch.object(replay, "ROOT", repo):
                with self.assertRaises(FileNotFoundError):
                    replay.materialize_repo_snapshot(snapshot, [Path("unit.cpp")])


class Rec98CompatTests(unittest.TestCase):
    def test_forwarding_layer_is_materialized_and_attested(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            compat = root / "compat" / "rec98"
            source = root / "source"
            header = compat / "th02" / "hardware" / "frmdelay.h"
            header.parent.mkdir(parents=True)
            header.write_text('#include "th02/hardware/frmdelay.h"\n', encoding="utf-8")
            source.mkdir()
            with patch.object(replay, "REC98_COMPAT", compat):
                receipt = replay.materialize_rec98_compat(source)
            copied = source / "compat" / "rec98" / "th02" / "hardware" / "frmdelay.h"
            self.assertEqual(copied.read_bytes(), header.read_bytes())
            self.assertEqual(receipt[0]["path"], "th02/hardware/frmdelay.h")
            self.assertEqual(receipt[0]["sha256"], replay.digest_file(header))

    def test_forwarded_fragment_resolves_only_one_line_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            compat = Path(temporary) / "compat"
            header = compat / "th02" / "hardware" / "frmdelay.h"
            header.parent.mkdir(parents=True)
            header.write_text('#include "th02/hardware/frmdelay.h"\n', encoding="utf-8")
            source = b'#include "compat/rec98/th02/hardware/frmdelay.h"\nbody\n'
            with patch.object(replay, "REC98_COMPAT", compat):
                resolved, used = replay.resolve_rec98_forwarders(source)
            self.assertEqual(resolved, b'#include "th02/hardware/frmdelay.h"\nbody\n')
            self.assertEqual(used, ["th02/hardware/frmdelay.h"])


class SourceSplitTests(unittest.TestCase):
    def fixture(self, root: Path, *, suffix: bool = True) -> tuple[Path, dict[str, object]]:
        repo = root / "repo"
        source = root / "source"
        repo.mkdir()
        source.mkdir()
        (repo / "fragment.cpp").write_text("tail\n", encoding="utf-8")
        (repo / "wrapper.cpp").write_text('#include "tail.cpp"\n', encoding="utf-8")
        scaffold = source / "impl.cpp"
        scaffold.write_text("head\ntail\n" if suffix else "tail\nhead\n", encoding="utf-8")
        (source / "Tupfile.lua").write_text('"base.cpp",\n', encoding="utf-8")
        split: dict[str, object] = {
            "id": "fixture-split",
            "trigger_units": ["unit-a"],
            "scaffold_path": "impl.cpp",
            "repo_fragment": "fragment.cpp",
            "remove_mode": "suffix",
            "fragment_overlay_path": "tail.cpp",
            "repo_wrapper": "wrapper.cpp",
            "wrapper_overlay_path": "extra.cpp",
            "build_file": "Tupfile.lua",
            "build_anchor": '"base.cpp",\n',
            "build_insert": '"extra.cpp",\n',
        }
        return source, split

    def test_source_split_is_exact_and_build_ordered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, split = self.fixture(root)
            with patch.object(replay, "ROOT", root / "repo"):
                receipts = replay.apply_source_splits(source, [split], {"unit-a"})
            self.assertEqual((source / "impl.cpp").read_text(encoding="utf-8"), "head\n")
            self.assertEqual((source / "tail.cpp").read_text(encoding="utf-8"), "tail\n")
            self.assertEqual(
                (source / "extra.cpp").read_text(encoding="utf-8"),
                '#include "tail.cpp"\n',
            )
            self.assertEqual(
                (source / "Tupfile.lua").read_text(encoding="utf-8"),
                '"base.cpp",\n"extra.cpp",\n',
            )
            self.assertEqual(len(receipts), 1)
            self.assertEqual(receipts[0]["fragment_offset"], 5)
            self.assertEqual(receipts[0]["fragment_size"], 5)

    def test_source_split_rejects_non_suffix_fragment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, split = self.fixture(root, suffix=False)
            with patch.object(replay, "ROOT", root / "repo"):
                with self.assertRaisesRegex(RuntimeError, "not the scaffold suffix"):
                    replay.apply_source_splits(source, [split], {"unit-a"})


class ScaffoldExtractionTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, Path, dict[str, object]]:
        repo = root / "repo"
        source = root / "source"
        repo.mkdir()
        source.mkdir()
        scaffold = source / "scaffold.asm"
        scaffold.write_text("head\nBEGIN\nbody old\nEND\ntail\n", encoding="utf-8")
        template = repo / "wrapper.asm.in"
        template.write_text("prefix\n{{EXTRACTED_SPAN}}\nsuffix\n", encoding="utf-8")
        span = "BEGIN\nbody old\nEND\n".encode("utf-8")
        extraction: dict[str, object] = {
            "id": "fixture-extraction",
            "trigger_units": ["unit-a"],
            "scaffold_path": "scaffold.asm",
            "scaffold_sha256": replay.digest_file(scaffold),
            "encoding": "utf-8",
            "start": "BEGIN\n",
            "end": "END\n",
            "span_sha256": replay.digest_bytes(span),
            "template_source": "wrapper.asm.in",
            "output_path": "generated.asm",
            "replacements": [
                {"old": "old", "new": "new", "expected_count": 1},
            ],
        }
        return source, repo, extraction

    def test_scaffold_extraction_is_hash_bound_and_adapted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, repo, extraction = self.fixture(root)
            receipts = replay.apply_scaffold_extractions(
                source, [extraction], {"unit-a"}, repo_root=repo
            )
            self.assertEqual(
                (source / "generated.asm").read_text(encoding="utf-8"),
                "prefix\nBEGIN\nbody new\nEND\n\nsuffix\n",
            )
            self.assertEqual(len(receipts), 1)
            self.assertEqual(receipts[0]["span_size"], len(b"BEGIN\nbody old\nEND\n"))
            self.assertEqual(receipts[0]["replacements"][0]["count"], 1)
            self.assertEqual(
                (source / "scaffold.asm").read_text(encoding="utf-8"),
                "head\nBEGIN\nbody old\nEND\ntail\n",
            )

    def test_scaffold_extraction_rejects_span_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, repo, extraction = self.fixture(root)
            extraction["span_sha256"] = "00" * 32
            with self.assertRaisesRegex(RuntimeError, "span SHA-256 mismatch"):
                replay.apply_scaffold_extractions(
                    source, [extraction], {"unit-a"}, repo_root=repo
                )

    def test_repo_input_paths_include_prebuild_inputs(self) -> None:
        prebuild = {
            "driver": "scripts/compile_tc4j_pc98_ide.py",
            "repo_source": "src/main/boss/mugetsu_main033.cpp",
            "repo_inputs": ["scripts/probe_tc4j_pc98_ide.py", "config/runtime.toml"],
        }
        paths = replay.repo_input_paths([], [], [], [], [prebuild])
        self.assertIn(Path("scripts/compile_tc4j_pc98_ide.py"), paths)
        self.assertIn(Path("src/main/boss/mugetsu_main033.cpp"), paths)
        self.assertIn(Path("scripts/probe_tc4j_pc98_ide.py"), paths)
        self.assertIn(Path("config/runtime.toml"), paths)

    def test_repo_input_paths_include_extraction_template(self) -> None:
        extraction = {"template_source": "wrapper.asm.in"}
        paths = replay.repo_input_paths([], [], [], [extraction])
        self.assertIn(Path("wrapper.asm.in"), paths)


class BuildInsertTests(unittest.TestCase):
    def fixture(self, root: Path, *, duplicate_anchor: bool = False):
        repo = root / "repo"
        source = root / "source"
        repo.mkdir()
        source.mkdir()
        (repo / "align.c").write_text("#pragma option -WX -zCSHARED -k-\n", encoding="utf-8")
        anchor = '"before.cpp",\n"anchor.c",\n'
        text = anchor + ('"middle.cpp",\n' + anchor if duplicate_anchor else '') + '"after.cpp",\n'
        (source / "Tupfile.lua").write_text(text, encoding="utf-8")
        entry = {
            "id": "fixture-insert",
            "trigger_units": ["unit-a"],
            "repo_source": "align.c",
            "overlay_path": "extra/align.c",
            "build_file": "Tupfile.lua",
            "build_anchor": anchor,
            "build_insert": '"extra/align.c",\n',
        }
        return repo, source, entry

    def test_build_insert_is_source_and_anchor_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo, source, entry = self.fixture(Path(temporary))
            with patch.object(replay, "ROOT", repo):
                receipts = replay.apply_build_inserts(source, [entry], {"unit-a"})
            self.assertEqual(
                (source / "extra" / "align.c").read_bytes(),
                (repo / "align.c").read_bytes(),
            )
            self.assertEqual(
                (source / "Tupfile.lua").read_text(encoding="utf-8"),
                '"before.cpp",\n"anchor.c",\n"extra/align.c",\n"after.cpp",\n',
            )
            self.assertEqual(receipts[0]["source_sha256"], replay.digest_file(repo / "align.c"))
            self.assertEqual(receipts[0]["trigger_units"], ["unit-a"])

    def test_build_insert_rejects_ambiguous_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo, source, entry = self.fixture(Path(temporary), duplicate_anchor=True)
            with patch.object(replay, "ROOT", repo):
                with self.assertRaisesRegex(RuntimeError, "expected one build anchor"):
                    replay.apply_build_inserts(source, [entry], {"unit-a"})


class BuildReplacementTests(unittest.TestCase):
    def fixture(self, root: Path, *, duplicate_anchor: bool = False):
        source = root / "source"
        source.mkdir()
        anchor = '"a.cpp",\n"b.cpp",\n"c.cpp",\n'
        text = anchor + ('"middle.cpp",\n' + anchor if duplicate_anchor else '') + '"after.cpp",\n'
        (source / "Tupfile.lua").write_text(text, encoding="utf-8")
        entry = {
            "id": "fixture-replacement",
            "trigger_units": ["unit-a"],
            "build_file": "Tupfile.lua",
            "build_anchor": anchor,
            "build_replacement": '"a.cpp",\n',
        }
        return source, entry

    def test_prebuild_object_rejects_escaping_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            entry = {
                "id": "bad-prebuild",
                "trigger_units": ["unit-a"],
                "driver": "../escape.py",
                "source_path": "unit.cpp",
                "output_path": "unit.obj",
                "receipt_path": "unit.json",
            }
            with self.assertRaises(RuntimeError):
                replay.apply_prebuild_objects(source, [entry], {"unit-a"})


    def test_prebuild_object_materializes_frozen_repo_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            live = root / "live"
            frozen = root / "frozen"
            source = root / "source"
            for base in (live, frozen, source):
                base.mkdir()
            for base in (live, frozen):
                (base / "scripts").mkdir()
                (base / "src").mkdir()
                (base / "scripts" / "driver.py").write_text("# driver\n", encoding="utf-8")
                (base / "src" / "producer.cpp").write_text("natural();\n", encoding="utf-8")
            entry = {
                "id": "fixture-prebuild",
                "trigger_units": ["unit-a"],
                "driver": "scripts/driver.py",
                "repo_source": "src/producer.cpp",
                "source_path": "generated/producer.cpp",
                "output_path": "obj/producer.obj",
                "receipt_path": "obj/producer.json",
            }

            def fake_run(command, **kwargs):
                output = source / "obj" / "producer.obj"
                receipt = source / "obj" / "producer.json"
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b"OMF")
                receipt.write_text(
                    json.dumps({
                        "source": "generated/producer.cpp",
                        "output": "obj/producer.obj",
                        "source_sha256": replay.digest_file(source / "generated" / "producer.cpp"),
                        "object_sha256": replay.digest_file(output),
                    }),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, stdout="ok")

            with (
                patch.object(replay, "ROOT", live),
                patch.object(replay.subprocess, "run", side_effect=fake_run),
                patch.object(
                    replay,
                    "describe_omf",
                    return_value={
                        "valid": True,
                        "dependency_timestamp_normalized_sha256": "11" * 32,
                    },
                ),
            ):
                receipts = replay.apply_prebuild_objects(
                    source, [entry], {"unit-a"}, repo_root=frozen
                )
            self.assertEqual(
                (source / "generated" / "producer.cpp").read_bytes(),
                (frozen / "src" / "producer.cpp").read_bytes(),
            )
            self.assertEqual(receipts[0]["repo_source"]["path"], "src/producer.cpp")
            self.assertEqual(
                receipts[0]["repo_source"]["sha256"],
                replay.digest_file(frozen / "src" / "producer.cpp"),
            )

    def test_build_replacement_is_anchor_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source, entry = self.fixture(Path(temporary))
            receipts = replay.apply_build_replacements(source, [entry], {"unit-a"})
            self.assertEqual(
                (source / "Tupfile.lua").read_text(encoding="utf-8"),
                '"a.cpp",\n"after.cpp",\n',
            )
            self.assertEqual(receipts[0]["trigger_units"], ["unit-a"])
            self.assertNotEqual(
                receipts[0]["build_file_original_sha256"],
                receipts[0]["build_file_patched_sha256"],
            )

    def test_build_replacement_rejects_ambiguous_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source, entry = self.fixture(Path(temporary), duplicate_anchor=True)
            with self.assertRaisesRegex(RuntimeError, "expected one build anchor"):
                replay.apply_build_replacements(source, [entry], {"unit-a"})


class SourceReplacementTests(unittest.TestCase):
    def test_source_replacement_is_hash_and_offset_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            source = root / "source"
            repo.mkdir()
            source.mkdir()
            replacement = repo / "replacement.cpp"
            replacement.write_text("natural();\n", encoding="utf-8")
            scaffold = source / "impl.cpp"
            original = b"head\nlowlevel();\ntail\n"
            scaffold.write_bytes(original)
            match = b"lowlevel();\n"
            entry = {
                "id": "unit-replace",
                "repo_source": "replacement.cpp",
                "source_mode": "replace",
                "patch_path": "impl.cpp",
                "scaffold_sha256": replay.digest_bytes(original),
                "replace_offset": original.index(match),
                "replace_size": len(match),
                "replace_sha256": replay.digest_bytes(match),
            }
            with patch.object(replay, "ROOT", repo):
                receipt = replay.overlay_sources(source, [entry])
            self.assertEqual(scaffold.read_text(encoding="utf-8"), "head\nnatural();\ntail\n")
            self.assertEqual(receipt[0]["mode"], "replace")
            self.assertEqual(receipt[0]["replace_offset"], original.index(match))
            self.assertEqual(receipt[0]["replacement_sha256"], replay.digest_file(replacement))

    def test_source_replacement_rejects_span_hash_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            source = root / "source"
            repo.mkdir()
            source.mkdir()
            (repo / "replacement.cpp").write_text("natural();\n", encoding="utf-8")
            original = b"head\nlowlevel();\ntail\n"
            (source / "impl.cpp").write_bytes(original)
            match = b"lowlevel();\n"
            entry = {
                "id": "unit-replace",
                "repo_source": "replacement.cpp",
                "source_mode": "replace",
                "patch_path": "impl.cpp",
                "scaffold_sha256": replay.digest_bytes(original),
                "replace_offset": original.index(match),
                "replace_size": len(match),
                "replace_sha256": replay.digest_bytes(b"different();\n"),
            }
            with patch.object(replay, "ROOT", repo):
                with self.assertRaisesRegex(RuntimeError, "source span SHA-256 mismatch"):
                    replay.overlay_sources(source, [entry])

    def test_source_replacement_rejects_scaffold_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            source = root / "source"
            repo.mkdir()
            source.mkdir()
            (repo / "replacement.cpp").write_text("natural();\n", encoding="utf-8")
            (source / "impl.cpp").write_text("changed();\n", encoding="utf-8")
            entry = {
                "id": "unit-replace",
                "repo_source": "replacement.cpp",
                "source_mode": "replace",
                "patch_path": "impl.cpp",
                "scaffold_sha256": replay.digest_bytes(b"original();\n"),
                "replace_offset": 0,
                "replace_size": len(b"original();\n"),
                "replace_sha256": replay.digest_bytes(b"original();\n"),
            }
            with patch.object(replay, "ROOT", repo):
                with self.assertRaisesRegex(RuntimeError, "scaffold SHA-256 drift"):
                    replay.overlay_sources(source, [entry])


class SourceTransformTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, dict[str, object], bytes]:
        source = root / "source"
        source.mkdir()
        original = b"head\ncall old\nbegin\nraw\x93line\nend\ndata db 1\n"
        (source / "impl.asm").write_bytes(original)
        entry: dict[str, object] = {
            "id": "fixture-transform",
            "trigger_units": ["unit-a"],
            "patch_path": "impl.asm",
            "encoding": "latin-1",
            "scaffold_sha256": replay.digest_bytes(original),
            "ops": [
                {"id": "rename", "kind": "replace", "old": "call old", "new": "call new"},
                {"id": "export", "kind": "insert_before", "anchor": "data db 1\n", "text": "public _data\n_data label byte\n"},
                {"id": "remove", "kind": "remove_between", "start": "begin\n", "end": "end\n", "replacement": "extrn natural:near\n"},
            ],
        }
        return source, entry, original

    def test_source_transform_is_scaffold_and_anchor_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source, entry, original = self.fixture(Path(temporary))
            receipts = replay.apply_source_transforms(source, [entry], {"unit-a"})
            expected = b"head\ncall new\nextrn natural:near\npublic _data\n_data label byte\ndata db 1\n"
            self.assertEqual((source / "impl.asm").read_bytes(), expected)
            self.assertEqual(receipts[0]["scaffold_sha256"], replay.digest_bytes(original))
            self.assertEqual(receipts[0]["patched_sha256"], replay.digest_bytes(expected))
            self.assertEqual(len(receipts[0]["ops"]), 3)

    def test_source_transform_accepts_explicit_scaffold_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source, entry, original = self.fixture(Path(temporary))
            entry.pop("scaffold_sha256")
            other = replay.digest_bytes(b"other scaffold")
            entry["scaffold_sha256_any"] = [other, replay.digest_bytes(original)]
            receipts = replay.apply_source_transforms(source, [entry], {"unit-a"})
            self.assertEqual(receipts[0]["scaffold_sha256"], replay.digest_bytes(original))
            self.assertEqual(
                receipts[0]["allowed_scaffold_sha256"],
                [other, replay.digest_bytes(original)],
            )

    def test_source_transform_rejects_hash_outside_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source, entry, _ = self.fixture(Path(temporary))
            entry.pop("scaffold_sha256")
            entry["scaffold_sha256_any"] = [replay.digest_bytes(b"other scaffold")]
            with self.assertRaisesRegex(RuntimeError, "scaffold SHA-256 drift"):
                replay.apply_source_transforms(source, [entry], {"unit-a"})

    def test_source_transform_rejects_scaffold_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source, entry, _ = self.fixture(Path(temporary))
            (source / "impl.asm").write_bytes(b"changed\n")
            with self.assertRaisesRegex(RuntimeError, "scaffold SHA-256 drift"):
                replay.apply_source_transforms(source, [entry], {"unit-a"})

    def test_source_transform_optional_replace_accepts_zero_or_one_match(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            patch = source / "sample.asm"
            for original, expected_count, expected_text in (
                ("head\r\npublic OLD\r\ntail\r\n", 1, "head\r\ntail\r\n"),
                ("head\r\ntail\r\n", 0, "head\r\ntail\r\n"),
            ):
                patch.write_text(original, encoding="latin-1", newline="")
                transform = [{
                    "id": "optional-public-handoff",
                    "trigger_units": ["unit"],
                    "patch_path": "sample.asm",
                    "encoding": "latin-1",
                    "scaffold_sha256": replay.digest_bytes(original.encode("latin-1")),
                    "ops": [{
                        "id": "drop-old-public",
                        "kind": "replace_optional",
                        "old": "public OLD\r\n",
                        "new": "",
                    }],
                }]
                receipts = replay.apply_source_transforms(source, transform, {"unit"})
                self.assertEqual(receipts[0]["ops"][0]["count"], expected_count)
                with patch.open("r", encoding="latin-1", newline="") as stream:
                    self.assertEqual(stream.read(), expected_text)

    def test_source_transform_optional_replace_rejects_multiple_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            patch = source / "sample.asm"
            original = "public OLD\r\npublic OLD\r\n"
            patch.write_text(original, encoding="latin-1", newline="")
            transform = [{
                "id": "optional-public-handoff",
                "trigger_units": ["unit"],
                "patch_path": "sample.asm",
                "encoding": "latin-1",
                "scaffold_sha256": replay.digest_bytes(original.encode("latin-1")),
                "ops": [{
                    "id": "drop-old-public",
                    "kind": "replace_optional",
                    "old": "public OLD\r\n",
                    "new": "",
                }],
            }]
            with self.assertRaisesRegex(RuntimeError, "zero or one match"):
                replay.apply_source_transforms(source, transform, {"unit"})

    def test_source_transform_rejects_ambiguous_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source, entry, _ = self.fixture(Path(temporary))
            path = source / "impl.asm"
            original = path.read_bytes() + b"data db 1\n"
            path.write_bytes(original)
            entry["scaffold_sha256"] = replay.digest_bytes(original)
            with self.assertRaisesRegex(RuntimeError, "expected one insertion anchor"):
                replay.apply_source_transforms(source, [entry], {"unit-a"})


class AuxiliaryObjectTests(unittest.TestCase):
    def test_auxiliary_object_requires_valid_omf_and_records_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            (source / "residual.obj").write_bytes(b"fixture")
            description = {
                "valid": True,
                "sha256": "raw",
                "dependency_timestamp_normalized_sha256": "normalized",
                "module_name": "residual.asm",
                "translator_comments": ["TASM"],
                "dependency_paths": ["residual.asm"],
            }
            with patch.object(replay, "describe_omf", return_value=description):
                result = replay.inspect_auxiliary_objects(
                    source, ["residual.obj"]
                )[0]
            self.assertTrue(result["valid"])
            self.assertEqual(result["normalized_sha256"], "normalized")
            self.assertEqual(result["module_name"], "residual.asm")


class ZeroCodeObjectTests(unittest.TestCase):
    def omf_description(self, *, ledata: int) -> dict[str, object]:
        return {
            "valid": True,
            "sha256": "raw",
            "dependency_timestamp_normalized_sha256": "normalized",
            "record_counts": {"SEGDEF": 2, "GRPDEF": 1, "LEDATA": ledata},
        }

    def test_zero_code_object_requires_segdefs_and_no_ledata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            (source / "anchor.obj").write_bytes(b"fixture")
            with patch.object(
                replay, "describe_omf", return_value=self.omf_description(ledata=0)
            ):
                result = replay.inspect_zero_code_objects(source, ["anchor.obj"])[0]
            self.assertTrue(result["zero_code"])
            self.assertEqual(result["ledata_count"], 0)
            self.assertEqual(result["segdef_count"], 2)

    def test_zero_code_object_rejects_ledata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            (source / "anchor.obj").write_bytes(b"fixture")
            with patch.object(
                replay, "describe_omf", return_value=self.omf_description(ledata=1)
            ):
                result = replay.inspect_zero_code_objects(source, ["anchor.obj"])[0]
            self.assertFalse(result["zero_code"])
            self.assertEqual(result["ledata_count"], 1)


if __name__ == "__main__":
    unittest.main()
