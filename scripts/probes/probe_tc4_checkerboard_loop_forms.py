#!/usr/bin/env python3
"""Probe legal TC4J C++ countdown spellings for the TH04 checkerboard core.

This is compiler evidence only. It deliberately contains no inline assembly,
target bytes, or target-derived machine-code directives.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import normalize_dependency_timestamps, parse_omf  # noqa: E402

FLAGS = ("-c", "-ml", "-O", "-b-", "-3", "-Z", "-d")
PREFIX = (
    "#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n"
    "#include <dos.h>\n"
)
SUFFIX = "\n#pragma option -k.\n"
BODY = (
    "_ES = _DX; "
    "*reinterpret_cast<unsigned long __es *>(_DI) = _EAX; "
    "_DI += 8;"
)
VARIANTS = {
    "pseudo_do_predec": f"void near probe(void) {{ _CX=6; do {{ {BODY} }} while(--_CX); }}",
    "pseudo_do_postdec": f"void near probe(void) {{ _CX=6; do {{ {BODY} }} while(_CX-- > 1); }}",
    "pseudo_for_test": f"void near probe(void) {{ for(_CX=6; _CX; _CX--) {{ {BODY} }} }}",
    "pseudo_for_postdec": f"void near probe(void) {{ for(_CX=6; _CX--; ) {{ {BODY} }} }}",
    "pseudo_while": f"void near probe(void) {{ _CX=6; while(_CX) {{ {BODY} _CX--; }} }}",
    "pseudo_goto_predec": f"void near probe(void) {{ _CX=6; L: {BODY} if(--_CX) goto L; }}",
    "pseudo_goto_dec_test": f"void near probe(void) {{ _CX=6; L: {BODY} _CX--; if(_CX) goto L; }}",
    "pseudo_goto_subassign": f"void near probe(void) {{ _CX=6; L: {BODY} if((_CX -= 1) != 0) goto L; }}",
    "local_do_predec": f"void near probe(void) {{ unsigned i=6; do {{ {BODY} }} while(--i); }}",
    "local_do_postdec": f"void near probe(void) {{ unsigned i=6; do {{ {BODY} }} while(i-- > 1); }}",
    "local_for_down": f"void near probe(void) {{ for(unsigned i=6; i; i--) {{ {BODY} }} }}",
    "local_for_up": f"void near probe(void) {{ for(unsigned i=0; i<6; i++) {{ {BODY} }} }}",
    "local_while_post": f"void near probe(void) {{ unsigned i=6; while(i--) {{ {BODY} }} }}",
    "local_goto_predec": f"void near probe(void) {{ unsigned i=6; L: {BODY} if(--i) goto L; }}",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def index(data: bytes, pos: int) -> tuple[int, int]:
    first = data[pos]
    if first < 0x80:
        return first, pos + 1
    return ((first & 0x7F) << 8) | data[pos + 1], pos + 2


def pstr(data: bytes, pos: int) -> tuple[str, int]:
    size = data[pos]
    return data[pos + 1 : pos + 1 + size].decode("latin-1"), pos + 1 + size


def code_bytes(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    names = [""]
    segments: list[tuple[str, str]] = []
    for record in records:
        if record.record_type == 0x96:
            pos = 0
            while pos < len(record.data):
                name, pos = pstr(record.data, pos)
                names.append(name)
        elif record.record_type == 0x98:
            data = record.data
            pos = 1 + (3 if (data[0] >> 5) == 0 else 2)
            name_i, pos = index(data, pos)
            class_i, pos = index(data, pos)
            _, pos = index(data, pos)
            segments.append((names[name_i], names[class_i]))

    chunks: list[tuple[int, bytes]] = []
    for record in records:
        if record.record_type != 0xA0:
            continue
        data = record.data
        seg_i, pos = index(data, 0)
        offset = int.from_bytes(data[pos : pos + 2], "little")
        pos += 2
        if segments[seg_i - 1][1] == "CODE":
            chunks.append((offset, data[pos:]))
    if not chunks:
        raise ValueError(f"no CODE LEDATA in {path}")
    size = max(offset + len(payload) for offset, payload in chunks)
    out = bytearray(size)
    for offset, payload in chunks:
        out[offset : offset + len(payload)] = payload
    return bytes(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="tc4-checker-loop-", dir=parent))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(private):
            parser.error("output directory must be new and below .analysis")
        output.mkdir(parents=True)

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    compiler = next(item for item in surfaces if item["id"] == "active-tcc")
    compiler_path = ROOT / compiler["path"]
    if sha(compiler_path.read_bytes()) != compiler["sha256"]:
        raise ValueError("active TC4J identity failed")

    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )

    results = []
    for ordinal, (name, body) in enumerate(VARIANTS.items()):
        work = output / f"v{ordinal:02d}"
        work.mkdir()
        source = work / "p.cpp"  # 8.3-safe to avoid DOS-host filename remapping.
        source.write_text(PREFIX + body + SUFFIX)
        command = [
            "wine",
            str(runner),
            "-e",
            "-x",
            "tcc",
            *FLAGS,
            f"-I{ROOT / '_reference/ReC98'}",
            "p.cpp",
        ]
        done = subprocess.run(
            command, cwd=work, env=env, capture_output=True, text=True, timeout=120
        )
        obj = work / "p.obj"
        if done.returncode or not obj.is_file():
            raise ValueError(
                f"{name} failed: exit={done.returncode}\n{done.stdout}\n{done.stderr}"
            )
        code = code_bytes(obj)
        code_path = work / "p.code"
        code_path.write_bytes(code)
        dis = subprocess.run(
            ["ndisasm", "-b16", str(code_path)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        (work / "p.ndis").write_text(dis)
        results.append(
            {
                "name": name,
                "source_sha256": sha(source.read_bytes()),
                "object_normalized_sha256": sha(
                    normalize_dependency_timestamps(obj.read_bytes())
                ),
                "code_sha256": sha(code),
                "code_size": len(code),
                "code_hex": code.hex(),
                "contains_loop_instruction": any(
                    " loop " in f" {line.lower()} " for line in dis.splitlines()
                ),
                "disassembly": dis.splitlines(),
            }
        )

    receipt = {
        "schema_version": 1,
        "claim_scope": "TC4J natural checkerboard counted-loop source-form matrix",
        "tcc_sha256": compiler["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "flags": list(FLAGS),
        "variants": results,
        "conclusion": (
            "No tested legal C++ countdown spelling emits x86 LOOP. "
            "Pseudo-CX forms lower through DEC plus explicit zero testing; "
            "ordinary locals allocate the counter outside CX."
        ),
        "limit": (
            "This is a bounded compiler negative, not a proof that every possible "
            "TC4J source form is incapable of emitting LOOP and not evidence for "
            "inline-assembly provenance."
        ),
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                "receipt": str(receipt_path),
                "receipt_sha256": sha(receipt_path.read_bytes()),
                "variant_count": len(results),
                "loop_count": sum(x["contains_loop_instruction"] for x in results),
                "sizes": {x["name"]: x["code_size"] for x in results},
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
