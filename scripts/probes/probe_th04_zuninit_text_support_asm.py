#!/usr/bin/env python3
"""Cold-assemble symbolic ZUNINIT SJIS/VRAM text support against release targets."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/probes"))

from lib.omf import describe_omf, parse_omf  # noqa: E402
from replay_th04_zun_source_only import PAYLOAD, PAYLOAD_SHA256  # noqa: E402

SOURCE = ROOT / "src/zun/zuninit/text_support.asm"
TASM = ROOT / ".analysis/toolchain/wineprefix/drive_c/TASM50/bin/TASM32.EXE"
TASM_SHA256 = "ba50fe547863b96242d98cff54cdf95ab268a8682395afad172eedbfc46c5b26"
TARGET_START = 0x7B0
TARGET_SIZE = 0x4D
TARGET_SHA256 = "6bedcd29d5f95303e05e868d625f84a494b8cec386b5ba3684fd03a374256017"
CONVERTER_SIZE = 0x12
CONVERTER_SHA256 = "044ce9480a0506ffac42aeaf78844e0266262c10ffd075d2c861a7a78689adf8"
RENDERER_SIZE = 0x3B
RENDERER_SHA256 = "0c5a90f8b85153d3c668f033651cddedbe2a635e2cfdcf8345e4ec5f8f8c6fb6"

CROSSGAME = {
    "th02-zun-smoke": {
        "component_offset": 1476,
        "component_runtime_converter": 0x1F0,
        "component_runtime_renderer": 0x202,
        "component_size": 0x56E,
        "component_sha256": "27fe52738878c1fa267c5dc82b0d70957d72dca5a6da375620a74d163b61e2d8",
    },
    "th05-zun-smoke": {
        "component_offset": 1779,
        "component_runtime_converter": 0x19C,
        "component_runtime_renderer": 0x1AE,
        "component_size": 0x3F1,
        "component_sha256": "6091d53910b5a4bbcd132d663dc9531d8ea65cff95baf4307a3cd5e768e1e8b1",
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_audit() -> dict[str, object]:
    text = SOURCE.read_text(encoding="utf-8")
    code_lines = []
    forbidden_directives = []
    for raw in text.splitlines():
        line = raw.split(";", 1)[0].strip().lower()
        if not line:
            continue
        code_lines.append(line)
        if line.startswith(("db ", "dw ", "dd ", "dq ", "dt ", "incbin ", "include ")):
            forbidden_directives.append(line)
    if forbidden_directives:
        raise RuntimeError(f"symbolic ZUNINIT owner contains byte/data injection: {forbidden_directives}")
    return {
        "source_sha256": sha(SOURCE.read_bytes()),
        "noncomment_line_count": len(code_lines),
        "forbidden_byte_or_include_directives": forbidden_directives,
        "uses_only_symbolic_instructions_and_labels": True,
    }


def target_crosscheck(code: bytes) -> dict[str, object]:
    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text(encoding="utf-8"))
    artifacts = {row["id"]: row for row in manifest["artifacts"]}
    results = {}
    for artifact, spec in CROSSGAME.items():
        info = artifacts[artifact]
        target = (ROOT / info["private_path"]).read_bytes()
        if len(target) != info["size"] or sha(target) != info["sha256"]:
            raise RuntimeError(f"{artifact}: private target identity drift")
        start = spec["component_offset"]
        component = target[start:start + spec["component_size"]]
        if len(component) != spec["component_size"] or sha(component) != spec["component_sha256"]:
            raise RuntimeError(f"{artifact}: release target ZUNINIT component identity drift")
        converter_local = spec["component_runtime_converter"] - 0x100
        converter = component[converter_local:converter_local + CONVERTER_SIZE]
        if converter != code[:CONVERTER_SIZE]:
            raise RuntimeError(f"{artifact}: converter differs from symbolic TH04 owner")
        renderer_local = spec["component_runtime_renderer"] - 0x100
        renderer = component[renderer_local:renderer_local + RENDERER_SIZE]
        results[artifact] = {
            "component_file_offset": start,
            "component_sha256": sha(component),
            "converter_equal_symbolic_owner": True,
            "converter_sha256": sha(converter),
            "renderer_sha256": sha(renderer),
            "renderer_equal_th04_symbolic_owner": renderer == code[CONVERTER_SIZE:],
        }
    if not results["th02-zun-smoke"]["renderer_equal_th04_symbolic_owner"]:
        raise RuntimeError("TH02 renderer no longer equals TH04 symbolic owner")
    if results["th05-zun-smoke"]["renderer_equal_th04_symbolic_owner"]:
        raise RuntimeError("TH05 renderer unexpectedly became byte-identical to TH04")
    return results


def object_code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    sections = [
        record.data[3:]
        for record in records
        if record.record_type == 0xA0 and record.data[1:3] == b"\0\0"
    ]
    if len(sections) != 1:
        raise RuntimeError(f"symbolic ZUNINIT owner expected one zero-offset LEDATA section, got {len(sections)}")
    return sections[0]


def build_one(label: str, output: Path) -> dict[str, object]:
    saved = output / label
    saved.mkdir(parents=True)
    environment = os.environ.copy()
    environment.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    with tempfile.TemporaryDirectory(prefix=f"zuninit-text-{label}-", dir=output) as tmp:
        work = Path(tmp)
        source = work / "TEXTSUP.ASM"
        shutil.copyfile(SOURCE, source)
        os.utime(source, (946684800, 946684800))
        command = [
            "wine", r"C:\TASM50\BIN\TASM32.EXE",
            "/m", "/mx", "/kh32768",
            "TEXTSUP.ASM,TEXTSUP.OBJ,TEXTSUP.LST",
        ]
        completed = subprocess.run(
            command, cwd=work, env=environment,
            capture_output=True, text=True, timeout=120,
        )
        (saved / "assemble.log").write_text(
            json.dumps(command) + f"\nexit={completed.returncode}\n"
            + completed.stdout + completed.stderr,
            encoding="utf-8",
        )
        obj = work / "TEXTSUP.OBJ"
        listing = work / "TEXTSUP.LST"
        if completed.returncode or not obj.is_file() or not listing.is_file():
            raise RuntimeError(f"{label}: TASM32 assembly failed")
        omf = describe_omf(obj.read_bytes())
        if (
            not omf["valid"]
            or omf["module_name"] != "TEXTSUP.ASM"
            or omf["dependency_paths"] != ["TEXTSUP.ASM"]
            or omf["record_counts"].get("PUBDEF") != 2
            or omf["record_counts"].get("LEDATA") != 1
        ):
            raise RuntimeError(f"{label}: invalid symbolic TASM OMF owner layout")
        listing_text = listing.read_text(encoding="cp932", errors="replace")
        expected_proc_lines = (
            ("0000", "ZUNINIT_SJIS_TO_JIS", "proc near"),
            ("0012", "ZUNINIT_SJIS_TO_JIS", "endp"),
            ("0012", "ZUNINIT_TEXT_PUT", "proc near"),
            ("004D", "ZUNINIT_TEXT_PUT", "endp"),
        )
        for offset, symbol, directive in expected_proc_lines:
            pattern = rf"^\s*\d+\s+{offset}\s+{symbol}\s+{directive}\s*$"
            if not re.search(pattern, listing_text, re.MULTILINE):
                raise RuntimeError(f"{label}: TASM PROC ownership drift at {offset} {symbol}")
        code = object_code(obj)
        if len(code) != TARGET_SIZE or sha(code) != TARGET_SHA256:
            raise RuntimeError(
                f"{label}: symbolic TASM CODE mismatch size={len(code)} sha={sha(code)}"
            )
        records = parse_omf(obj.read_bytes())
        fixupp = [r for r in records if r.record_type == 0x9C]
        if fixupp:
            raise RuntimeError(f"{label}: standalone text-support owner unexpectedly has FIXUPP records")
        (saved / "text_support.obj").write_bytes(obj.read_bytes())
        (saved / "text_support.lst").write_bytes(listing.read_bytes())
        (saved / "text_support.code").write_bytes(code)
        return {
            "object_sha256": sha(obj.read_bytes()),
            "code_size": len(code),
            "code_sha256": sha(code),
            "converter_sha256": sha(code[:CONVERTER_SIZE]),
            "renderer_sha256": sha(code[CONVERTER_SIZE:]),
            "fixupp_record_count": 0,
            "public_count": 2,
            "proc_extents": ["0000..0011", "0012..004C"],
            "omf_translator_comments": omf["translator_comments"],
            "listing_sha256": sha(listing.read_bytes()),
        }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        ap.error("output must be a new direct child of .analysis/reconstruction/probes")

    payload = PAYLOAD.read_bytes()
    preflight = subprocess.run(
        [sys.executable, "scripts/preflight.py"], cwd=ROOT,
        check=True, capture_output=True, text=True,
    )
    if not TASM.is_file() or sha(TASM.read_bytes()) != TASM_SHA256:
        raise RuntimeError("pinned TASM32 binary identity drift")
    if sha(payload) != PAYLOAD_SHA256:
        raise RuntimeError("TH04 decoded ZUN payload identity drift")
    target = payload[TARGET_START:TARGET_START + TARGET_SIZE]
    if len(target) != TARGET_SIZE or sha(target) != TARGET_SHA256:
        raise RuntimeError("TH04 ZUNINIT text-support target identity drift")

    audit = source_audit()
    output.mkdir()
    builds = {
        "a": build_one("a", output),
        "b": build_one("b", output),
    }
    # TASM prints the wall-clock assembly time in each listing header and in
    # ??TIME. Keep both original listings as diagnostics; determinism is gated
    # on the actual OMF and emitted CODE, which have stable digests.
    deterministic_fields = set(builds["a"]) - {"listing_sha256"}
    if any(builds["a"][key] != builds["b"][key] for key in deterministic_fields):
        raise RuntimeError("symbolic ZUNINIT text-support cold OMF/CODE builds differ")
    code = (output / "a/text_support.code").read_bytes()
    if code != target:
        raise RuntimeError("symbolic text-support CODE differs from complete target extent")
    crossgame = target_crosscheck(code)

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "symbolic original-style TASM owner for TH04 ZUNINIT SJIS converter + VRAM renderer",
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_extent": "th04-zun/com-payload/0x7B0+0x4D",
        "target_sha256": TARGET_SHA256,
        "probe_source_sha256": sha(Path(__file__).read_bytes()),
        "preflight_stdout_sha256": sha(preflight.stdout.encode()),
        "tasm32_sha256": TASM_SHA256,
        "source": "src/zun/zuninit/text_support.asm",
        "source_audit": audit,
        "builds": builds,
        "listing_digest_limit": "TASM LST headers and ??TIME contain the wall-clock assembly time; OMF and CODE are deterministic.",
        "crossgame_release_targets": crossgame,
        "function_extents": [
            {
                "semantic_name": "zuninit_sjis_to_jis",
                "payload_offset": "0x7B0",
                "size": CONVERTER_SIZE,
                "sha256": CONVERTER_SHA256,
                "abi": "AX=Shift-JIS code -> AX=JIS row/cell",
            },
            {
                "semantic_name": "zuninit_text_put",
                "payload_offset": "0x7C2",
                "size": RENDERER_SIZE,
                "sha256": RENDERER_SHA256,
                "abi": "AX=VRAM offset, DX=CS-relative $-terminated Shift-JIS string",
            },
        ],
        "exact_symbolic_owner": True,
        "source_provenance": (
            "Original-style symbolic assembly reconstruction supported by independent release-target "
            "lineage and runtime semantics; not a claim that the maintained text is the literal historical source."
        ),
        "limit": (
            "This proves the maintained 0x4D physical assembler owner and cross-game lineage. "
            "It does not by itself grant decoded-C++ function acceptance or whole-ZUN exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "code_sha256": TARGET_SHA256,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
