#!/usr/bin/env python3
"""Bound the remaining active-TLINK switch surface on current OP/MAINE candidates.

Only linker flags are changed. Product source, OMF objects, and relocation-table
bytes are never edited. The probe asks whether library dictionary handling,
code packing, or far->near optimization can explain the current packed R/T
frontier without disturbing target-equal payload/layout surfaces.
"""
from __future__ import annotations

import argparse
from collections import Counter
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
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts")]
from lib.pc98 import parse_mz  # noqa: E402

RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
PREFIX = b"-c -s -E "
VARIANTS = {
    "ignore_extended_dictionary": b"-c -s -e ",
    "no_extended_dictionary_switch": b"-c -s ",
    "pack_code_segments": b"-c -s -E -P ",
    "inhibit_far_to_near": b"-c -s -E -f ",
}
EXPECTED = {
    "th04-op": {
        "stem": "op",
        "source_exe_sha256": "78468a2ae389ba9c97fb7b391355e4eda2cb750f84f3cc4abf3e34802bceafbd",
        "source_map_sha256": "cd2e0a35b1d1262dca398db0302ab68243179cf18edfac2e1ec0810acf2ef334",
        "source_rsp_sha256": "e612cd0d20a735fd66158ad9622d452e25821776886637af4d72459f63daa9f5",
        "relocations": 804,
        "stable_sha256": "78468a2ae389ba9c97fb7b391355e4eda2cb750f84f3cc4abf3e34802bceafbd",
        "far_sha256": "5ef461f5ec5e6f1802bb334c4fdac4f0251e2c85eb99e9f6e8e477e1cd29d36c",
        "far_relocations": 1050,
        "far_program_differences": 1221,
    },
    "th04-maine": {
        "stem": "maine",
        "source_exe_sha256": "9b14cad4fc3bbd079890cd15d64de03d3c7159fb2b4ae38dab111bdfc8a0df60",
        "source_map_sha256": "1dd895faa6c7fbfc537c2d56a95ff5ea693aa923b7f5701bb922f170dbfae4e0",
        "source_rsp_sha256": "eecc30a34375c046e5f4c10a93bbd26be40fac869a313d15cb45321916d0c875",
        "relocations": 559,
        "stable_sha256": "9b14cad4fc3bbd079890cd15d64de03d3c7159fb2b4ae38dab111bdfc8a0df60",
        "far_sha256": "136ecd38b1a9d0aec64a7378e776171dc72b98ee13149a946388235d934b53a8",
        "far_relocations": 804,
        "far_program_differences": 1215,
    },
}
HELP_SNIPPETS = (
    b"/e  Ignore extended dictionaries",
    b"/E  Process extended dictionaries",
    b'/f  Inhibit optimizing far calls to near',
    b"/P[=dd]  Pack code segments",
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="tlink-switch-surface-v441-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def toolchain() -> tuple[Path, str]:
    cfg = tomllib.loads((ROOT / "config/toolchain.toml").read_text())
    item = next(row for row in cfg["surfaces"] if row["id"] == "active-tlink")
    path = ROOT / item["path"]
    digest = sha_path(path)
    if digest != item["sha256"]:
        raise ValueError("active TLINK identity drift")
    raw = path.read_bytes()
    for snippet in HELP_SNIPPETS:
        if snippet not in raw:
            raise ValueError(f"active TLINK help surface drift: {snippet!r}")
    return path, digest


def relink(source_dir: Path, artifact: str, variant: str, flags: bytes, output: Path) -> dict[str, object]:
    expected = EXPECTED[artifact]
    stem = expected["stem"]
    work = output / artifact / variant / "source"
    shutil.copytree(source_dir, work, symlinks=True)
    rsp = work / f"obj/th04/{stem}.@l"
    data = rsp.read_bytes()
    if not data.startswith(PREFIX):
        raise ValueError(f"{artifact}: response prefix drift")
    rsp.write_bytes(flags + data[len(PREFIX):])
    exe = work / f"bin/th04/{stem}.exe"
    map_path = work / f"obj/th04/{stem}.map"
    exe.unlink(missing_ok=True)
    map_path.unlink(missing_ok=True)
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    command = ["wine", str(RUNNER), "-e", "-x", "tlink", rf"@obj\th04\{stem}.@l"]
    done = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=180)
    log = output / artifact / variant / "link.log"
    log.write_text(json.dumps(command) + f"\nflags={flags.decode()}\nexit={done.returncode}\n" + done.stdout + "\n" + done.stderr)
    if done.returncode or not exe.is_file() or not map_path.is_file():
        raise RuntimeError(f"{artifact}/{variant}: TLINK failed")
    image = exe.read_bytes()
    mz = parse_mz(image)
    if not mz.valid:
        raise ValueError(f"{artifact}/{variant}: invalid MZ")
    return {
        "flags": flags.decode().strip(),
        "response_sha256": sha_path(rsp),
        "exe_sha256": sha_bytes(image),
        "exe_size": len(image),
        "map_sha256": sha_path(map_path),
        "program_image_sha256": sha_bytes(mz.program_image),
        "program_image_size": len(mz.program_image),
        "relocation_count": len(mz.relocations),
        "relocation_sites": [row.linear for row in mz.relocations],
        "log_sha256": sha_path(log),
    }


def inspect_artifact(source_dir: Path, artifact: str, output: Path) -> dict[str, object]:
    expected = EXPECTED[artifact]
    stem = expected["stem"]
    exe = source_dir / f"bin/th04/{stem}.exe"
    map_path = source_dir / f"obj/th04/{stem}.map"
    rsp = source_dir / f"obj/th04/{stem}.@l"
    for path, digest in (
        (exe, expected["source_exe_sha256"]),
        (map_path, expected["source_map_sha256"]),
        (rsp, expected["source_rsp_sha256"]),
    ):
        if not path.is_file() or sha_path(path) != digest:
            raise ValueError(f"{artifact}: source identity drift: {path}")
    baseline_data = exe.read_bytes()
    baseline = parse_mz(baseline_data)
    baseline_sites = [row.linear for row in baseline.relocations]
    if len(baseline_sites) != expected["relocations"]:
        raise ValueError(f"{artifact}: baseline relocation count drift")

    builds = {name: relink(source_dir, artifact, name, flags, output) for name, flags in VARIANTS.items()}
    stable_names = ("ignore_extended_dictionary", "no_extended_dictionary_switch", "pack_code_segments")
    for name in stable_names:
        row = builds[name]
        if row["exe_sha256"] != expected["stable_sha256"]:
            raise ValueError(f"{artifact}/{name}: executable changed")
        if row["map_sha256"] != expected["source_map_sha256"]:
            raise ValueError(f"{artifact}/{name}: MAP changed")
        if row["relocation_sites"] != baseline_sites:
            raise ValueError(f"{artifact}/{name}: relocation order changed")

    far = builds["inhibit_far_to_near"]
    if far["exe_sha256"] != expected["far_sha256"] or far["relocation_count"] != expected["far_relocations"]:
        raise ValueError(f"{artifact}/f: output identity drift")
    far_data = (output / artifact / "inhibit_far_to_near" / "source" / f"bin/th04/{stem}.exe").read_bytes()
    far_mz = parse_mz(far_data)
    n = min(len(far_mz.program_image), len(baseline.program_image))
    program_differences = sum(a != b for a, b in zip(far_mz.program_image[:n], baseline.program_image[:n])) + abs(len(far_mz.program_image) - len(baseline.program_image))
    if program_differences != expected["far_program_differences"]:
        raise ValueError(f"{artifact}/f: program difference count drift: {program_differences}")
    if Counter(far["relocation_sites"]) == Counter(baseline_sites):
        raise ValueError(f"{artifact}/f: relocation multiset unexpectedly unchanged")

    for row in builds.values():
        row.pop("relocation_sites")
    return {
        "baseline": {
            "exe_sha256": sha_bytes(baseline_data),
            "map_sha256": sha_path(map_path),
            "response_sha256": sha_path(rsp),
            "program_image_sha256": sha_bytes(baseline.program_image),
            "relocation_count": len(baseline_sites),
        },
        "builds": builds,
        "far_noopt_program_difference_count": program_differences,
        "stable_variants_are_byte_identical": list(stable_names),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--op-source-dir", type=Path, required=True)
    parser.add_argument("--maine-source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    output = output_dir(args.output_dir)
    if not RUNNER.is_file() or sha_path(RUNNER) != RUNNER_SHA:
        raise ValueError("runner identity drift")
    linker, linker_sha = toolchain()
    artifacts = {
        "th04-op": inspect_artifact(args.op_source_dir.resolve(), "th04-op", output),
        "th04-maine": inspect_artifact(args.maine_source_dir.resolve(), "th04-maine", output),
    }
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "active TLINK 6.10 dictionary/code-pack/far-call switch surface on current TH04 OP/MAINE topology; no authored or packed exactness claim",
        "active_tlink_path": str(linker.relative_to(ROOT)),
        "active_tlink_sha256": linker_sha,
        "runner_sha256": RUNNER_SHA,
        "help_surface": [snippet.decode() for snippet in HELP_SNIPPETS],
        "artifacts": artifacts,
        "conclusion": (
            "Replacing /E with /e, removing the extended-dictionary switch entirely, and enabling /P all reproduce the current OP/MAINE executables and MAPs byte-for-byte, including relocation order. /f instead changes more than 1.2k program-image bytes and changes relocation counts/multisets (OP 804->1050; MAINE 559->804), so it cannot explain the current R/T frontier while preserving the already target-equal payload layout."
        ),
        "limit": (
            "This closes only these active TLINK 6.10 switch mechanisms. It does not establish the historical command line, historical pre-DIET MZ, or behavior of a different linker version."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha_path(rp),
        "op_far_relocations": artifacts["th04-op"]["builds"]["inhibit_far_to_near"]["relocation_count"],
        "maine_far_relocations": artifacts["th04-maine"]["builds"]["inhibit_far_to_near"]["relocation_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
