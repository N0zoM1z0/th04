#!/usr/bin/env python3
"""Bound TC4J's -B/TASM32 producer path on the remaining natural OP blockers.

ZUN's resident _main demonstrated that TC4J's assembly-output backend can change
real code generation. This probe asks the same materially new question for five
OP functions whose maintained ordinary C/C++ source is still nonexact. It does
not use target-derived assembly, pseudoregister forcing, or source mutations.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from replay_th04_op_help_put import SNAPSHOT, RUNNER, loose_segment_bytes  # noqa: E402
from replay_th04_zun_source_only import source_closure  # noqa: E402

TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
TARGET_SHA256 = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
FLAGS = (
    "-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml",
    "-DBINARY='O'", "-nobj/th04/",
)


@dataclass(frozen=True)
class Case:
    name: str
    source: str
    alias: str
    segment: str
    target_offset: int
    target_size: int
    target_sha256: str
    natural_size: int
    natural_sha256: str


CASES = (
    Case(
        "nopoly_b_put",
        "src/op/music/nopoly_put.cpp",
        "src/op/music/npb.cpp",
        "OP_MUSIC_TEXT",
        0xBFA7,
        0x1E,
        "f9af3bf25fe94b1ca89ef5ad9bdacd77a87cfc401450a378a12428ea1f409083",
        0x1E,
        "e4f9fc0ead018e7bf3ffe49ece3c288a9d7523560bc3eb215ff14e82b668b78e",
    ),
    Case(
        "scoredat_decode",
        "src/op/score/scoredec.cpp",
        "src/op/score/sdec.cpp",
        "SCORE_TEXT",
        0xC57A,
        0xAD,
        "5efe0d5065947fa7bc698dba06267ca16d3b34b3e90369907e14451fc9d0e2a5",
        0xC5,
        "d6565f1fa0376d312af42faa70e079becd1adc284905e5b1c21a16024af23a1e",
    ),
    Case(
        "scoredat_encode",
        "src/op/score/scoreenc.cpp",
        "src/op/score/senc.cpp",
        "SCORE_TEXT",
        0xC627,
        0x65,
        "737bdcca37820fb3848004e60f12b6e8121470668ea058fb233be1bac7e3b69f",
        0x6F,
        "f2013be58b023969908a2c5e249da7f5945f076f07147021bff27cd5a92e53c1",
    ),
    Case(
        "SND_SE_PLAY",
        "src/shared/sound/se_play.cpp",
        "src/shared/sound/sepl.cpp",
        "SHARED",
        0xE2F2,
        0x39,
        "fea779b877971c519c0729a6f0546e60f37225a2a675cd3fa4dc0975eef884b8",
        0x3C,
        "4519e45ef064d7af3fb2d4be6d870277e558dfc3bb940cbe8fa5b70a7653e624",
    ),
    Case(
        "_snd_se_update",
        "src/op/sound/se_update.cpp",
        "src/op/sound/seup.cpp",
        "SHARED",
        0xE32C,
        0x4C,
        "a9e451577270f1d448bd39c71b2c4e69570357b1090111740df0b440931cf5f5",
        0x4D,
        "4e317f24d1f54c95e37ce43450bb187bdec40909a30c3898e0ec3e55959106a1",
    ),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def environment() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    return env


def toolchain_identity() -> dict[str, str]:
    config = tomllib.loads((ROOT / "config/toolchain.toml").read_text(encoding="utf-8"))
    surfaces = {row["id"]: row for row in config["surfaces"]}
    result = {}
    for ident in ("active-tcc", "active-tasm32"):
        row = surfaces[ident]
        path = ROOT / row["path"]
        actual = sha_file(path)
        if actual != row["sha256"]:
            raise RuntimeError(f"{ident} identity drift")
        result[ident] = actual
    if not RUNNER.is_file():
        raise RuntimeError("pinned DOS compiler runner missing")
    result["runner"] = sha_file(RUNNER)
    return result


def raw_difference_count(left: bytes, right: bytes) -> int:
    common = sum(a != b for a, b in zip(left, right))
    return common + abs(len(left) - len(right))


def materialize_case(work: Path, case: Case) -> dict[str, str]:
    closure = source_closure(ROOT, (case.source,))
    hashes = {relative: sha_file(ROOT / relative) for relative in closure}
    for relative in closure:
        destination = work / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)

    # TC4J maps long source basenames through DOS 8.3 names. A short alias keeps
    # generated ASM names stable and avoids '~' leaking into a generated segment
    # identifier. The bytes are identical to the maintained translation unit.
    alias = work / case.alias
    alias.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / case.source, alias)
    if alias.read_bytes() != (ROOT / case.source).read_bytes():
        raise RuntimeError(f"{case.name}: alias source bytes differ")
    return hashes


def run_compiler(command: list[str], cwd: Path, log: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment(),
        capture_output=True,
        text=True,
        timeout=120,
    )
    log.write_text(
        json.dumps(command) + f"\nexit={completed.returncode}\n"
        + completed.stdout + completed.stderr,
        encoding="utf-8",
    )
    return completed


def build_case(case: Case, label: str, root: Path, target: bytes) -> dict[str, object]:
    work = root / case.name / label / "source"
    work.parent.mkdir(parents=True)
    copy_compact_snapshot(SNAPSHOT, work, "op")
    source_hashes = materialize_case(work, case)

    stem = Path(case.alias).stem
    obj = work / "obj/th04" / f"{stem}.obj"
    asm = work / "obj/th04" / f"{stem}.asm"
    obj.unlink(missing_ok=True)
    asm.unlink(missing_ok=True)

    direct_command = [
        "wine", str(RUNNER), "-e", "-x", "tcc", *FLAGS, case.alias
    ]
    direct = run_compiler(
        direct_command, work, root / case.name / f"{label}-direct.log"
    )
    if direct.returncode or not obj.is_file():
        raise RuntimeError(f"{case.name}/{label}: direct TC4J compile failed")
    direct_code = loose_segment_bytes(obj, case.segment)
    if len(direct_code) != case.natural_size or sha(direct_code) != case.natural_sha256:
        raise RuntimeError(
            f"{case.name}/{label}: direct natural codegen drift: "
            f"{len(direct_code)} {sha(direct_code)}"
        )
    (root / case.name / f"{label}-direct.code").write_bytes(direct_code)

    obj.unlink()
    asm.unlink(missing_ok=True)
    bmode_command = [
        "wine", str(RUNNER), "-e", "-x", "tcc", "-B", *FLAGS, case.alias
    ]
    bmode = run_compiler(
        bmode_command, work, root / case.name / f"{label}-bmode-tcc.log"
    )
    if not asm.is_file():
        raise RuntimeError(
            f"{case.name}/{label}: TC4J -B produced no ASM "
            f"(exit {bmode.returncode})"
        )
    asm_data = asm.read_bytes()
    (root / case.name / f"{label}.asm").write_bytes(asm_data)

    obj.unlink(missing_ok=True)
    tasm_command = [
        "wine", "cmd", "/d", "/c",
        (
            r"set PATH=C:\TASM50\BIN;C:\TC4\BIN;%PATH%"
            rf"&&tasm32 /m /mx /kh32768 /t obj\th04\{stem}.asm "
            rf"obj\th04\{stem}.obj"
        ),
    ]
    assembled = run_compiler(
        tasm_command, work, root / case.name / f"{label}-bmode-tasm.log"
    )
    if assembled.returncode or not obj.is_file():
        raise RuntimeError(f"{case.name}/{label}: pinned TASM32 assembly failed")

    bmode_code = loose_segment_bytes(obj, case.segment)
    (root / case.name / f"{label}-bmode.code").write_bytes(bmode_code)
    if bmode_code != direct_code:
        raise RuntimeError(
            f"{case.name}/{label}: -B/TASM32 changed natural CODE; "
            "this is new evidence and must be inspected rather than recorded as a negative"
        )

    return {
        "source_sha256": source_hashes,
        "direct_code_size": len(direct_code),
        "direct_code_sha256": sha(direct_code),
        "bmode_asm_sha256": sha(asm_data),
        "bmode_code_size": len(bmode_code),
        "bmode_code_sha256": sha(bmode_code),
        "target_size": len(target),
        "target_sha256": sha(target),
        "target_equal": bmode_code == target,
        "raw_difference_count": raw_difference_count(target, bmode_code),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error(
            "output directory must be new directly below .analysis/reconstruction/probes"
        )

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    tools = toolchain_identity()
    if sha_file(TARGET) != TARGET_SHA256:
        raise RuntimeError("restored OP target identity drift")
    mz = parse_mz(TARGET.read_bytes())
    if not mz.valid:
        raise RuntimeError("restored OP target is not a valid MZ")

    output.mkdir(parents=True)
    results: dict[str, object] = {}
    for case in CASES:
        target = mz.program_image[case.target_offset:case.target_offset + case.target_size]
        if len(target) != case.target_size or sha(target) != case.target_sha256:
            raise RuntimeError(f"{case.name}: target slice identity drift")
        a = build_case(case, "a", output, target)
        b = build_case(case, "b", output, target)

        stable_keys = (
            "source_sha256", "direct_code_size", "direct_code_sha256",
            "bmode_asm_sha256", "bmode_code_size", "bmode_code_sha256",
            "target_size", "target_sha256", "target_equal", "raw_difference_count",
        )
        if any(a[key] != b[key] for key in stable_keys):
            raise RuntimeError(f"{case.name}: cold rounds differ")
        if a["target_equal"]:
            raise RuntimeError(
                f"{case.name}: assembly backend reached target equality; "
                "inspect and promote through the normal exactness path"
            )
        results[case.name] = {
            "payload_offset": f"0x{case.target_offset:X}",
            **{key: a[key] for key in stable_keys},
        }

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": (
            "OP compiler-frontier negative: TC4J -B generated ASM plus pinned "
            "TASM32 compared with direct TC4J for five maintained natural C/C++ blockers"
        ),
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA256,
        "toolchain_sha256": tools,
        "flags": list(FLAGS),
        "cases": results,
        "all_bmode_equal_direct": all(
            row["bmode_code_sha256"] == row["direct_code_sha256"]
            and row["bmode_code_size"] == row["direct_code_size"]
            for row in results.values()
        ),
        "all_still_nonexact": all(not row["target_equal"] for row in results.values()),
        "conclusion": (
            "Unlike ZUN resident _main, these five OP natural producers are invariant "
            "under the TC4J assembly-output backend. -B/TASM32 reproduces the same "
            "nonexact CODE as direct TC4J for nopoly_b_put, both SCORE codecs, "
            "SND_SE_PLAY, and _snd_se_update."
        ),
        "limit": (
            "This does not cover SND_LOAD's already separately bounded 89 C3 encoding "
            "or the EGC pair whose only exact-shape candidate is provenance-blocked "
            "low-level source. No OP exact state changes."
        ),
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(receipt_path),
        "receipt_sha256": sha_file(receipt_path),
        "cases": {
            name: {
                "target_size": row["target_size"],
                "candidate_size": row["bmode_code_size"],
                "raw_difference_count": row["raw_difference_count"],
            }
            for name, row in results.items()
        },
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
