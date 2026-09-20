#!/usr/bin/env python3
"""Probe TC4J's two producer paths for MOV BX,AX encoding.

This records a compiler fingerprint only. It does not authorize inline assembly
inside snd_load() and grants no exactness credit.
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
FLAGS = ("-c", "-ml", "-O", "-b-", "-3", "-Z", "-d")
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import parse_omf  # noqa: E402


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def index(data: bytes, pos: int) -> tuple[int, int]:
    first = data[pos]
    if first < 0x80:
        return first, pos + 1
    return ((first & 0x7F) << 8) | data[pos + 1], pos + 2


def pstr(data: bytes, pos: int) -> tuple[str, int]:
    n = data[pos]
    return data[pos + 1:pos + 1 + n].decode("latin-1"), pos + 1 + n


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
            ni, pos = index(data, pos)
            ci, pos = index(data, pos)
            _oi, pos = index(data, pos)
            segments.append((names[ni], names[ci]))

    chunks: list[tuple[int, bytes]] = []
    for record in records:
        if record.record_type != 0xA0:
            continue
        data = record.data
        seg, pos = index(data, 0)
        offset = int.from_bytes(data[pos:pos + 2], "little")
        pos += 2
        if segments[seg - 1][1] == "CODE":
            chunks.append((offset, data[pos:]))

    size = max(offset + len(payload) for offset, payload in chunks)
    out = bytearray(size)
    for offset, payload in chunks:
        out[offset:offset + len(payload)] = payload
    return bytes(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="tc4-mov-bx-ax-", dir=parent))
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

    sources = {
        "natural": (
            "#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n"
            "#include <dos.h>\n"
            "void near probe(void) { _BX = _AX; }\n"
            "#pragma option -k.\n"
        ),
        "inline": (
            "#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n"
            "void near probe(void) { asm { mov bx, ax; } }\n"
            "#pragma option -k.\n"
        ),
    }
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    results = {}
    for name, text in sources.items():
        source = output / f"{name}.cpp"
        source.write_text(text)
        command = [
            "wine", str(runner), "-e", "-x", "tcc",
            *FLAGS, f"-I{ROOT / '_reference/ReC98'}", source.name,
        ]
        done = subprocess.run(
            command, cwd=output, env=env, capture_output=True, text=True, timeout=120
        )
        (output / f"{name}.log").write_text(
            json.dumps(command) + f"\nexit={done.returncode}\n"
            + done.stdout + "\n" + done.stderr
        )
        obj = output / f"{name}.obj"
        if done.returncode or not obj.is_file():
            raise ValueError(f"{name} probe compilation failed")
        code = code_bytes(obj)
        (output / f"{name}.code").write_bytes(code)
        results[name] = {
            "source_sha256": sha(source.read_bytes()),
            "object_sha256": sha(obj.read_bytes()),
            "code_hex": code.hex(),
            "code_sha256": sha(code),
        }

    if bytes.fromhex(results["natural"]["code_hex"]) != bytes.fromhex("8bd8c3"):
        raise ValueError("natural producer no longer emits 8B D8 C3")
    if bytes.fromhex(results["inline"]["code_hex"]) != bytes.fromhex("89c3c3"):
        raise ValueError("inline assembler no longer emits 89 C3 C3")

    receipt = {
        "schema_version": 1,
        "claim_scope": "TC4J MOV BX,AX encoding fingerprint; no snd_load promotion",
        "tcc_sha256": compiler["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "flags": list(FLAGS),
        "results": results,
        "conclusion": (
            "TC4J ordinary pseudoregister assignment emits 8B D8, while its "
            "integrated inline assembler emits 89 C3 for the same MOV BX,AX semantics."
        ),
        "limit": (
            "This explains the target encoding mechanism but does not establish "
            "independent original-source provenance for TH04 snd_load."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "conclusion": receipt["conclusion"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
