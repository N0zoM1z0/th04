#!/usr/bin/env python3
"""Test whether active TLINK switches reorder MAIN stage-session relocations.

This diagnostic relinks one retained cold object snapshot; it is not an exact
reconstruction replay and does not promote any unit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / ".analysis/reconstruction/exact-unit-replay/gptweb-v214-demo-fixupp-diagnostic-001/a/source"
SNAPSHOT_RESPONSE_SHA256 = "b2ce7be007aa044e83321333bd3a0febc85496d2035cf66be37f863b6bcba2fe"
SNAPSHOT_SESS_SHA256 = "3816b5f0aaabe5e8646243d22fbe13d40e97f53f012a398ae95ec76ae426f6ad"
SNAPSHOT_MAIN_SHA256 = "1c1bcec509b775a6fa994d403d573ede75e74b8781ac5f0db06eb124d5fbae21"
VARIANTS = (
    ("baseline", "-c -s -E"),
    ("without_c", "-s -E"),
    ("without_s", "-c -E"),
    ("without_E", "-c -s"),
    ("without_s_E", "-c"),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relocations(image: bytes) -> list[int]:
    count = int.from_bytes(image[6:8], "little")
    table = int.from_bytes(image[0x18:0x1A], "little")
    if image[:2] != b"MZ" or table + 4 * count > len(image):
        raise ValueError("invalid MZ relocation table")
    return [
        int.from_bytes(image[table + 4 * i:table + 4 * i + 2], "little")
        + 16 * int.from_bytes(image[table + 4 * i + 2:table + 4 * i + 4], "little")
        for i in range(count)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="demo-tlink-switches-", dir=parent))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(private):
            parser.error("output directory must be new and below .analysis")
        output.mkdir(parents=True)

    targets = tomllib.loads((ROOT / "config/targets.toml").read_text())["artifacts"]
    target_info = next(item for item in targets if item["id"] == "th04-main")
    target = (ROOT / target_info["private_path"]).read_bytes()
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise ValueError("MAIN target identity failed")
    target_sites = [site for site in relocations(target) if 0xAED0 <= site < 0xB3EE]
    if len(target_sites) != 52 or target_sites[0] != 0xB2DA:
        raise ValueError("target stage-session relocation order changed")

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    linker = next(item for item in surfaces if item["id"] == "active-tlink")
    if sha((ROOT / linker["path"]).read_bytes()) != linker["sha256"]:
        raise ValueError("active TLINK identity failed")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    runner_sha = sha(runner.read_bytes())
    response = (SNAPSHOT / "obj/th04/main.@l").read_bytes()
    if not response.startswith(b"-c -s -E "):
        raise ValueError("retained response file has unexpected switch prefix")
    original_image = (SNAPSHOT / "bin/th04/main.exe").read_bytes()
    original_sha = sha(original_image)
    sess_obj = (SNAPSHOT / "obj/th04/sess.obj").read_bytes()
    if (
        sha(response) != SNAPSHOT_RESPONSE_SHA256
        or sha(sess_obj) != SNAPSHOT_SESS_SHA256
        or original_sha != SNAPSHOT_MAIN_SHA256
    ):
        raise ValueError("retained v214 link inputs differ from pinned receipt")

    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    command = ["wine", str(runner), "-e", "-x", "tlink", r"@obj\th04\main.@l"]
    builds: dict[str, dict[str, object]] = {}
    with tempfile.TemporaryDirectory(prefix="work-", dir=output) as temp:
        work = Path(temp) / "source"
        shutil.copytree(SNAPSHOT, work, symlinks=True)
        rsp = work / "obj/th04/main.@l"
        image_path = work / "bin/th04/main.exe"
        for name, flags in VARIANTS:
            rsp.write_bytes(flags.encode() + response[len(b"-c -s -E"):])
            image_path.unlink(missing_ok=True)
            done = subprocess.run(
                command, cwd=work, env=env, capture_output=True, text=True, timeout=180
            )
            (output / f"{name}.log").write_text(
                json.dumps(command) + f"\nflags={flags}\nexit={done.returncode}\n"
                + done.stdout + "\n" + done.stderr
            )
            if done.returncode or not image_path.is_file():
                raise ValueError(f"{name}: TLINK failed")
            image = image_path.read_bytes()
            sites = [site for site in relocations(image) if 0xAED0 <= site < 0xB3EE]
            if len(sites) != 52 or sites[-1] != 0xB2DA:
                raise ValueError(f"{name}: candidate stage-session relocation order changed")
            builds[name] = {
                "flags": flags,
                "response_sha256": sha(rsp.read_bytes()),
                "image_sha256": sha(image),
                "image_size": len(image),
                "stage_relocation_count": len(sites),
                "stage_relocation_order_sha256": sha(b"".join(site.to_bytes(4, "little") for site in sites)),
                "same_as_retained_snapshot": image == original_image,
            }
    if any(not entry["same_as_retained_snapshot"] for entry in builds.values()):
        raise ValueError("a linker switch changed the candidate image; inspect before recording")
    receipt = {
        "schema_version": 1,
        "claim_scope": "MAIN DEMO_TEXT stage-session TLINK switch control; no exact promotion",
        "target_sha256": target_info["sha256"],
        "target_first_stage_relocation": "0xB2DA",
        "snapshot_response_sha256": sha(response),
        "snapshot_sess_obj_sha256": sha(sess_obj),
        "snapshot_main_sha256": original_sha,
        "tlink_sha256": linker["sha256"],
        "runner_sha256": runner_sha,
        "command": command,
        "builds": builds,
        "result": "removing current -c/-s/-E switches leaves the whole candidate image unchanged; site 0xB2DA stays last",
        "limit": "The original target OMF and historical TLINK invocation are unavailable.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
