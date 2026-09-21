#!/usr/bin/env python3
"""Read DIET 1.45f's hidden -^ metadata from TH04 packed executables.

UPDATE.DOC bundled with the pinned public DIET 1.45f release documents -^ as a
test-version diagnostic that reveals information while DIETing/unDIETing. This
probe runs only that read-only diagnostic on copied packed inputs under the
already-attested DOSBox-X profile and parses the internal filetype/dlzflag/
packsize/packcrc/unpacksize fields. It never modifies product source or targets.
"""
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
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.targets import find_artifact, load_target_manifest, read_verified_artifact  # noqa: E402
from replay_diet145f import check_toolchain  # noqa: E402

SIZE_RE = re.compile(r"filesize=([0-9A-F]+)")
META_RE = re.compile(
    r"filetype=([0-9A-F]+)\s+dlzflag=([0-9A-F]+)\s+"
    r"packsize=([0-9A-F]+)\s+packcrc=([0-9A-F]+)\s+unpacksize=([0-9A-F]+)"
)


V436_RECEIPT_SHA256 = "c21073e17762709d0be818bcc888fd6a2db142dbb72361927745ae80826f594d"
TARGET_EXPECTED = {
    "th04-op-target": (0x02, 0x30, 0xA342, 0xE124, 0x12C40, 496),
    "th04-maine-target": (0x02, 0x30, 0x92A3, 0x97CF, 0x10E62, 496),
}
BASELINE_EXPECTED = {
    "th04-op-baseline": (0x02, 0x30, 41760, 48940, 73636, 496),
    "th04-maine-baseline": (0x02, 0x20, 37545, 45923, 65998, 444),
}
FACTOR_EXPECTED = {
    "th04-op": {
        "base": (0x30, 41760, 73636, 496),
        "P": (0x30, 41761, 73636, 496),
        "R": (0x30, 41746, 73636, 496),
        "PR": (0x30, 41747, 73636, 496),
        "T": (0x30, 41807, 76864, 496),
        "PT": (0x30, 41808, 76864, 496),
        "RT": (0x30, 41793, 76864, 496),
        "PRT": (0x30, 41794, 76864, 496),
    },
    "th04-maine": {
        "base": (0x20, 37545, 65998, 444),
        "P": (0x20, 37546, 65998, 444),
        "R": (0x20, 37491, 65998, 444),
        "PR": (0x20, 37492, 65998, 444),
        "T": (0x30, 37590, 69218, 496),
        "PT": (0x30, 37591, 69218, 496),
        "RT": (0x30, 37538, 69218, 496),
        "PRT": (0x30, 37539, 69218, 496),
    },
}
UPDATE_DOC_MARKER = (
    b"Since this is a test version, there is a new optional\r\n"
    b"              command to reveal information in the process of\r\n"
    b"              DIETing and unDIETing.\r\n"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def metadata_tuple(row: dict[str, object]) -> tuple[int, int, int, int, int, int]:
    return (
        int(row["filetype"]), int(row["dlzflag"]), int(row["packsize"]),
        int(row["packcrc"]), int(row["unpacksize"]),
        int(row["header_overhead_vs_packsize"]),
    )


def factor_tuple(row: dict[str, object]) -> tuple[int, int, int, int]:
    return (
        int(row["dlzflag"]), int(row["packsize"]), int(row["unpacksize"]),
        int(row["header_overhead_vs_packsize"]),
    )


def outdir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="diet145f-meta-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def diagnostic(label: str, artifact: str, packed: bytes, output: Path) -> dict[str, object]:
    diet, dosbox, config, options, toolchain = check_toolchain(artifact)
    name = "OP.EXE" if artifact == "th04-op" else "MAINE.EXE"
    work = output / label
    work.mkdir()
    shutil.copy2(diet, work / "DIET.EXE")
    (work / name).write_bytes(packed)
    env = os.environ.copy()
    env.update(
        SDL_VIDEODRIVER="dummy",
        SDL_AUDIODRIVER="dummy",
        XDG_CACHE_HOME=str(work / "cache"),
        XDG_CONFIG_HOME=str(work / "config"),
        XDG_DATA_HOME=str(work / "data"),
    )
    guest = f"diet.exe -^ {name.lower()} > DEBUG.LOG"
    command = [
        str(dosbox), "-defaultconf", "-defaultmapper", "-conf", str(config),
        "-fastlaunch", "-nogui", "-nomenu", "-exit", "-time-limit", "30",
        "-c", f'mount c "{work}"', "-c", "c:", "-c", guest, "-c", "exit",
    ]
    completed = subprocess.run(
        command, cwd=ROOT, env=env, capture_output=True, text=True,
        timeout=40, check=False,
    )
    (work / "host.log").write_text(completed.stdout + completed.stderr)
    log_path = work / "DEBUG.LOG"
    if completed.returncode != 0 or not log_path.is_file():
        raise RuntimeError(f"{label}: DIET -^ execution failed")
    log_bytes = log_path.read_bytes()
    log = log_bytes.decode("cp437", errors="replace")
    match = META_RE.search(log)
    if match is None:
        raise ValueError(f"{label}: DIET -^ metadata not found: {log!r}")
    filetype, dlzflag, packsize, packcrc, unpacksize = [int(x, 16) for x in match.groups()]
    size_match = SIZE_RE.search(log)
    if size_match is None or int(size_match.group(1), 16) != len(packed):
        raise ValueError(f"{label}: DIET reported file size drift")
    return {
        "artifact": artifact,
        "packed_size": len(packed),
        "packed_sha256": sha(packed),
        "filetype": filetype,
        "dlzflag": dlzflag,
        "packsize": packsize,
        "packcrc": packcrc,
        "unpacksize": unpacksize,
        "header_overhead_vs_packsize": len(packed) - packsize,
        "debug_log_sha256": sha(log_bytes),
        "host_log_sha256": sha((work / "host.log").read_bytes()),
        "toolchain": toolchain,
        "pack_options_manifest": options,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--v436-dir", type=Path, required=True)
    ap.add_argument("--v432-op-dir", type=Path, required=True)
    ap.add_argument("--v432-maine-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    output = outdir(args.output_dir)
    v436 = args.v436_dir.resolve()
    v436_receipt_path = v436 / "receipt.json"
    if not v436_receipt_path.is_file() or sha(v436_receipt_path.read_bytes()) != V436_RECEIPT_SHA256:
        raise ValueError("v436 receipt identity drift")
    receipt = json.loads(v436_receipt_path.read_text())
    if receipt.get("schema_version") != 1:
        raise ValueError("v436 receipt schema drift")

    # The same pinned public release that supplies DIET.EXE also documents -^.
    diet_manifest = __import__("tomllib").loads((ROOT / "config/diet145f.toml").read_text())
    archive = ROOT / diet_manifest["tool"]["archive_path"]
    if sha(archive.read_bytes()) != diet_manifest["tool"]["archive_sha256"]:
        raise ValueError("DIET archive identity drift")
    with zipfile.ZipFile(archive) as bundle:
        update_doc = bundle.read("UPDATE.DOC")
    if UPDATE_DOC_MARKER not in update_doc or b"' -^ '    :option" not in update_doc:
        raise ValueError("bundled DIET -^ documentation marker drift")

    manifest = load_target_manifest(ROOT / "config/targets.toml")
    inputs: list[tuple[str, str, bytes]] = []
    for artifact, stem in (("th04-op", "OP.EXE"), ("th04-maine", "MAINE.EXE")):
        target = read_verified_artifact(ROOT, find_artifact(manifest, artifact))
        inputs.append((f"{artifact}-target", artifact, target))
        for suffix in ("baseline", "RT", "PRT", "i-a", "target-PR-on-I"):
            path = v436 / "pack" / f"{artifact}-{suffix}" / stem
            if not path.is_file():
                raise ValueError(f"missing v436 packed control: {path}")
            inputs.append((f"{artifact}-{suffix}", artifact, path.read_bytes()))

    results = {label: diagnostic(label, artifact, data, output) for label, artifact, data in inputs}
    for label, expected in {**TARGET_EXPECTED, **BASELINE_EXPECTED}.items():
        if metadata_tuple(results[label]) != expected:
            raise ValueError(f"{label}: DIET metadata drift: {metadata_tuple(results[label])}")
    # PRT must reproduce the target's complete compressed-data metadata, while
    # RT differs by exactly one compressed-data byte and CRC in both artifacts.
    for artifact in ("th04-op", "th04-maine"):
        target = results[f"{artifact}-target"]
        prt = results[f"{artifact}-PRT"]
        rt = results[f"{artifact}-RT"]
        for field in ("filetype", "dlzflag", "packsize", "packcrc", "unpacksize", "header_overhead_vs_packsize"):
            if prt[field] != target[field]:
                raise ValueError(f"{artifact}: PRT metadata field {field} differs from target")
        if int(target["packsize"]) - int(rt["packsize"]) != 1:
            raise ValueError(f"{artifact}: RT compressed-data size is not exactly one byte short")

    factorial_results = {}
    factorial_dirs = {
        "th04-op": args.v432_op_dir.resolve(),
        "th04-maine": args.v432_maine_dir.resolve(),
    }
    expected_receipts = {
        "th04-op": "1e677bac8d6fbda8fac0293b036f0d715b726745230ef325005bed4240815bff",
        "th04-maine": "e9fd36d657a7c8d57159bf09765ad93308761d4339a45bbe2e6cca5275f14365",
    }
    for artifact, directory in factorial_dirs.items():
        receipt_path = directory / "receipt.json"
        if not receipt_path.is_file() or sha(receipt_path.read_bytes()) != expected_receipts[artifact]:
            raise ValueError(f"{artifact}: v432 factorial receipt identity drift")
        stem = "OP.EXE" if artifact == "th04-op" else "MAINE.EXE"
        for factor in ("base", "P", "R", "PR", "T", "PT", "RT", "PRT"):
            packed_path = directory / factor / stem
            if not packed_path.is_file():
                raise ValueError(f"missing v432 packed factorial: {packed_path}")
            key = f"{artifact}-factor-{factor}"
            factorial_results[key] = diagnostic(key, artifact, packed_path.read_bytes(), output)
            observed = factor_tuple(factorial_results[key])
            if observed != FACTOR_EXPECTED[artifact][factor]:
                raise ValueError(f"{key}: factorial metadata drift: {observed}")

    # In MAINE, the T surface alone selects the 0x30 DLZ form and 496-byte
    # overhead; P/R alone remain on 0x20 / 444-byte overhead. OP is 0x30 in
    # every factorial cell. This is a packer-format observation, not source credit.
    maine_pre_t = [factorial_results[f"th04-maine-factor-{x}"] for x in ("base", "P", "R", "PR")]
    maine_with_t = [factorial_results[f"th04-maine-factor-{x}"] for x in ("T", "PT", "RT", "PRT")]
    if any((int(row["dlzflag"]), int(row["header_overhead_vs_packsize"])) != (0x20, 444) for row in maine_pre_t):
        raise ValueError("MAINE pre-T DLZ mode drift")
    if any((int(row["dlzflag"]), int(row["header_overhead_vs_packsize"])) != (0x30, 496) for row in maine_with_t):
        raise ValueError("MAINE T-selected DLZ mode drift")

    out = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "DIET 1.45f hidden -^ packed-metadata observation; target/current/private-control diagnostic only",
        "diet_update_doc": "bundled UPDATE.DOC: 1.45d->1.45f adds -^ to reveal information in DIETing/unDIETing",
        "results": results,
        "factorial_results": factorial_results,
        "observations": {
            "target_unpacked_sizes": {"th04-op": 0x12C40, "th04-maine": 0x10E62},
            "target_unpacksize_equals_v228_restored_file_size": True,
            "rt_packsize_shortfall_bytes": {"th04-op": 1, "th04-maine": 1},
            "maine_t_surface_selects_dlzflag_0x30": True,
            "maine_t_surface_selects_header_overhead_496": True,
        },
        "conclusion": (
            "The packed targets themselves record unpacksize 0x12C40 (OP) and 0x10E62 (MAINE), exactly the v228 -RA restored file sizes. Thus the target DIET metadata independently attests the prepack file-length T surface even though it does not reveal the lost historical relocation order or prove how TLINK produced the trailing extent. In both artifacts RT is exactly one compressed-data byte short and PRT matches target metadata; in MAINE, T alone switches DLZ mode from 0x20/444-byte overhead to the target 0x30/496-byte form."
        ),
        "limit": (
            "Target-derived RT/PRT/target-PR-on-I files are ignored private diagnostics. "
            "Metadata observation gives no authored-source or exactness credit."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "results": {
            key: {k: row[k] for k in ("dlzflag", "packsize", "packcrc", "unpacksize", "header_overhead_vs_packsize")}
            for key, row in {**results, **factorial_results}.items()
        },
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
