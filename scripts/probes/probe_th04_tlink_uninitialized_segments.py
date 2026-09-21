#!/usr/bin/env python3
"""Replay TLINK /i against the current TH04 OP/MAINE packed frontier.

The pinned TLINK 6.10 binary identifies /i as "Initialize all segments".
This probe tests that *natural linker mechanism* without changing product source,
object bytes, or relocation-table bytes.  It also includes explicitly
private/target-derived controls to distinguish the current P/R/T packed surfaces.
Those controls are diagnostics only and are forbidden as product inputs.
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
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.pc98 import parse_mz  # noqa: E402
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact  # noqa: E402
from replay_diet145f import check_toolchain, run_once  # noqa: E402

RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
# Same local runner identity pinned by the MASTER.LIB probes.
RUNNER_SHA256 = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"

EXPECTED = {
    "th04-op": {
        "exe_name": "op.exe",
        "map_name": "op.map",
        "rsp_name": "op.@l",
        "baseline_exe_sha256": "78468a2ae389ba9c97fb7b391355e4eda2cb750f84f3cc4abf3e34802bceafbd",
        "baseline_map_sha256": "cd2e0a35b1d1262dca398db0302ab68243179cf18edfac2e1ec0810acf2ef334",
        "baseline_rsp_sha256": "e612cd0d20a735fd66158ad9622d452e25821776886637af4d72459f63daa9f5",
        "target_restored_sha256": "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
        "baseline_packed_sha256": "901cd032a87d1a3c96b64792c903d52d970ce33ac04d4d839b5e60b51a7282eb",
        "baseline_packed_size": 42256,
        "rt_packed_size": 42289,
        "target_packed_size": 42290,
        "tlink_i_exe_sha256": "24730458d6caf3600bce74754d0eb08699f0df944c03cd74987acf50926081e3",
        "tlink_i_exe_size": 83424,
        "tlink_i_program_size": 78816,
        "tlink_i_packed_sha256": "107f32d639b48a3814f2a49f4119dd087221f5dbaf6eeb1bb1d3d8c75b901ade",
        "tlink_i_packed_size": 42383,
        "target_pr_on_i_packed_sha256": "2a0d1e4f0b19750b9a3f9243ce459b67ad6f77ee5e537702f8b4fa7db4246836",
        "target_pr_on_i_packed_size": 42369,
        "relocations": 804,
    },
    "th04-maine": {
        "exe_name": "maine.exe",
        "map_name": "maine.map",
        "rsp_name": "maine.@l",
        "baseline_exe_sha256": "9b14cad4fc3bbd079890cd15d64de03d3c7159fb2b4ae38dab111bdfc8a0df60",
        "baseline_map_sha256": "1dd895faa6c7fbfc537c2d56a95ff5ea693aa923b7f5701bb922f170dbfae4e0",
        "baseline_rsp_sha256": "eecc30a34375c046e5f4c10a93bbd26be40fac869a313d15cb45321916d0c875",
        "target_restored_sha256": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
        "baseline_packed_sha256": "c893e94928eb690a005fa4f46d5a618451cee949d433f097f3ddd212c158234c",
        "baseline_packed_size": 37989,
        "rt_packed_size": 38034,
        "target_packed_size": 38035,
        "tlink_i_exe_sha256": "90255401b803fd788d484999827702d521f95e67c364004a031864e218a2ba9b",
        "tlink_i_exe_size": 79056,
        "tlink_i_program_size": 75472,
        "tlink_i_packed_sha256": "971c9d156a7d4742007ee6edae3a9bf01f33e630ba86341263ffbca6e9ae6b01",
        "tlink_i_packed_size": 38202,
        "target_pr_on_i_packed_sha256": "e4316c9e10bebdb191783f96bcd5c41b3c500017b3aaad7babeb6ec61927bb48",
        "target_pr_on_i_packed_size": 38154,
        "relocations": 559,
    },
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="tlink-uninitialized-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def linker_identity() -> tuple[Path, str]:
    config = tomllib.loads((ROOT / "config/toolchain.toml").read_text())
    surface = next(row for row in config["surfaces"] if row["id"] == "active-tlink")
    linker = ROOT / surface["path"]
    digest = sha_path(linker)
    if digest != surface["sha256"]:
        raise ValueError("active TLINK identity drift")
    return linker, digest


def relocation_sites(data: bytes) -> list[int]:
    image = parse_mz(data)
    if not image.valid:
        raise ValueError("invalid MZ")
    return [row.linear for row in image.relocations]


def patch_tlink_i_response(path: Path) -> None:
    data = path.read_bytes()
    prefix = b"-c -s -E "
    if not data.startswith(prefix) or b" -i " in data[:64]:
        raise ValueError(f"unexpected TLINK response prefix: {path}")
    path.write_bytes(b"-c -s -E -i " + data[len(prefix):])


def relink_i(source: Path, artifact: str, output: Path, label: str) -> dict[str, object]:
    expected = EXPECTED[artifact]
    work = output / f"{artifact}-{label}" / "source"
    shutil.copytree(source, work, symlinks=True)
    rsp = work / "obj/th04" / expected["rsp_name"]
    patch_tlink_i_response(rsp)
    exe = work / "bin/th04" / expected["exe_name"]
    map_path = work / "obj/th04" / expected["map_name"]
    exe.unlink(missing_ok=True)
    map_path.unlink(missing_ok=True)
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    command = [
        "wine", str(RUNNER), "-e", "-x", "tlink",
        rf"@obj\th04\{expected['rsp_name']}",
    ]
    done = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=180)
    log = output / f"{artifact}-{label}-link.log"
    log.write_text(json.dumps(command) + f"\nexit={done.returncode}\n" + done.stdout + "\n" + done.stderr)
    if done.returncode or not exe.is_file() or not map_path.is_file():
        raise RuntimeError(f"{artifact}/{label}: TLINK /i failed")
    data = exe.read_bytes()
    mz = parse_mz(data)
    if not mz.valid:
        raise ValueError(f"{artifact}/{label}: /i output is invalid MZ")
    if len(data) != expected["tlink_i_exe_size"] or sha_bytes(data) != expected["tlink_i_exe_sha256"]:
        raise ValueError(f"{artifact}/{label}: /i executable identity drift")
    if len(mz.program_image) != expected["tlink_i_program_size"] or mz.header.minimum_extra_allocation != 0:
        raise ValueError(f"{artifact}/{label}: /i MZ extent/minalloc drift")
    return {
        "work": work,
        "exe": exe,
        "map": map_path,
        "response_sha256": sha_path(rsp),
        "exe_size": len(data),
        "exe_sha256": sha_bytes(data),
        "map_sha256": sha_path(map_path),
        "program_size": len(mz.program_image),
        "minimum_extra_paragraphs": mz.header.minimum_extra_allocation,
        "relocation_count": len(mz.relocations),
        "relocation_sites": [row.linear for row in mz.relocations],
        "link_log_sha256": sha_path(log),
    }


def target_controls(baseline: bytes, restored: bytes) -> tuple[bytes, bytes]:
    base = parse_mz(baseline)
    target = parse_mz(restored)
    if not base.valid or not target.valid or base.header.header_size != target.header.header_size:
        raise ValueError("baseline/target-restored MZ topology drift")
    if len(base.relocations) != len(target.relocations):
        raise ValueError("baseline/target-restored relocation count drift")
    rb = base.header.relocation_table_offset
    re = rb + 4 * len(base.relocations)
    extra = restored[len(baseline):]
    if not extra or any(extra):
        raise ValueError("target-restored tail is no longer nonempty/all-zero")

    rt = bytearray(baseline)
    rt[rb:re] = restored[rb:re]
    rt[2:6] = restored[2:6]
    rt[10:12] = restored[10:12]
    rt.extend(extra)

    prt = bytearray(rt)
    hs = base.header.header_size
    prt[hs:hs + len(base.program_image)] = restored[hs:hs + len(base.program_image)]
    if bytes(prt) != restored:
        raise ValueError("PRT control no longer equals target-restored MZ")
    return bytes(rt), bytes(prt)


def target_pr_on_i(i_image: bytes, restored: bytes) -> bytes:
    image = parse_mz(i_image)
    target = parse_mz(restored)
    if not image.valid or not target.valid or image.header.header_size != target.header.header_size:
        raise ValueError("/i/target-restored MZ topology drift")
    if len(image.relocations) != len(target.relocations):
        raise ValueError("/i/target-restored relocation count drift")
    rb = image.header.relocation_table_offset
    re = rb + 4 * len(image.relocations)
    hybrid = bytearray(i_image)
    hybrid[rb:re] = restored[rb:re]
    hs = image.header.header_size
    hybrid[hs:hs + len(target.program_image)] = restored[hs:hs + len(target.program_image)]
    # Deliberately retain /i's own MZ size fields, minalloc=0, and full trailing
    # zero image.  This is a target-derived control, never a product candidate.
    return bytes(hybrid)


def packed_summary(record: dict[str, object], target: bytes) -> dict[str, object]:
    packed = Path(str(record["packed_path"])).read_bytes()
    return {
        "size": len(packed),
        "sha256": sha_bytes(packed),
        "raw_exact": packed == target,
        "guest_log_sha256": record["guest_log_sha256"],
    }


def inspect_artifact(
    artifact: str,
    source: Path,
    restored_path: Path,
    output: Path,
    diet_binary: Path,
    dosbox: Path,
    diet_config: Path,
    options: list[str],
) -> dict[str, object]:
    expected = EXPECTED[artifact]
    exe = source / "bin/th04" / expected["exe_name"]
    map_path = source / "obj/th04" / expected["map_name"]
    rsp = source / "obj/th04" / expected["rsp_name"]
    for path, digest in (
        (exe, expected["baseline_exe_sha256"]),
        (map_path, expected["baseline_map_sha256"]),
        (rsp, expected["baseline_rsp_sha256"]),
        (restored_path, expected["target_restored_sha256"]),
    ):
        if not path.is_file() or sha_path(path) != digest:
            raise ValueError(f"{artifact}: input identity drift: {path}")

    target = read_verified_artifact(
        ROOT, find_artifact(load_target_manifest(ROOT / "config/targets.toml"), artifact)
    )
    baseline = exe.read_bytes()
    restored = restored_path.read_bytes()
    base_sites = relocation_sites(baseline)
    restored_sites = relocation_sites(restored)
    if len(base_sites) != expected["relocations"] or Counter(base_sites) != Counter(restored_sites):
        raise ValueError(f"{artifact}: relocation-site multiset drift")

    pack_root = output / "pack"
    pack_root.mkdir(exist_ok=True)
    baseline_pack = packed_summary(
        run_once(f"{artifact}-baseline", exe, pack_root, expected["exe_name"].upper(),
                 diet_binary, dosbox, diet_config, options), target
    )
    if (
        baseline_pack["size"] != expected["baseline_packed_size"]
        or baseline_pack["sha256"] != expected["baseline_packed_sha256"]
        or baseline_pack["raw_exact"]
    ):
        raise ValueError(f"{artifact}: baseline packed frontier drift")

    rt, prt = target_controls(baseline, restored)
    controls = output / "controls"
    controls.mkdir(exist_ok=True)
    rt_path = controls / f"{artifact}-RT.exe"
    prt_path = controls / f"{artifact}-PRT.exe"
    rt_path.write_bytes(rt)
    prt_path.write_bytes(prt)
    rt_pack = packed_summary(
        run_once(f"{artifact}-RT", rt_path, pack_root, expected["exe_name"].upper(),
                 diet_binary, dosbox, diet_config, options), target
    )
    prt_pack = packed_summary(
        run_once(f"{artifact}-PRT", prt_path, pack_root, expected["exe_name"].upper(),
                 diet_binary, dosbox, diet_config, options), target
    )
    if rt_pack["size"] != expected["rt_packed_size"] or rt_pack["raw_exact"]:
        raise ValueError(f"{artifact}: RT packed control drift")
    if prt_pack["size"] != expected["target_packed_size"] or not prt_pack["raw_exact"]:
        raise ValueError(f"{artifact}: PRT packed control is no longer raw exact")

    linked = [relink_i(source, artifact, output, label) for label in ("a", "b")]
    if any(row["exe_sha256"] != linked[0]["exe_sha256"] for row in linked[1:]):
        raise ValueError(f"{artifact}: TLINK /i A/B executable mismatch")
    for row in linked:
        if Counter(row["relocation_sites"]) != Counter(restored_sites):
            raise ValueError(f"{artifact}: TLINK /i relocation multiset drift")
        i_data = Path(row["exe"]).read_bytes()
        if len(i_data) <= len(restored) or any(i_data[len(restored):]):
            raise ValueError(f"{artifact}: TLINK /i extra tail is no longer all-zero")

    i_packs = []
    for label, row in zip(("a", "b"), linked):
        record = run_once(
            f"{artifact}-i-{label}", Path(row["exe"]), pack_root,
            expected["exe_name"].upper(), diet_binary, dosbox, diet_config, options
        )
        summary = packed_summary(record, target)
        if (
            summary["size"] != expected["tlink_i_packed_size"]
            or summary["sha256"] != expected["tlink_i_packed_sha256"]
            or summary["raw_exact"]
        ):
            raise ValueError(f"{artifact}: TLINK /i packed result drift")
        i_packs.append(summary)
    if i_packs[0] != i_packs[1]:
        raise ValueError(f"{artifact}: TLINK /i packed A/B mismatch")

    i_image = Path(linked[0]["exe"]).read_bytes()
    pri = target_pr_on_i(i_image, restored)
    pri_path = controls / f"{artifact}-target-PR-on-I.exe"
    pri_path.write_bytes(pri)
    pri_pack = packed_summary(
        run_once(f"{artifact}-target-PR-on-I", pri_path, pack_root,
                 expected["exe_name"].upper(), diet_binary, dosbox, diet_config, options), target
    )
    if (
        pri_pack["size"] != expected["target_pr_on_i_packed_size"]
        or pri_pack["sha256"] != expected["target_pr_on_i_packed_sha256"]
        or pri_pack["raw_exact"]
    ):
        raise ValueError(f"{artifact}: target-PR-on-/i control drift")

    return {
        "baseline": {
            "exe_size": len(baseline),
            "exe_sha256": sha_bytes(baseline),
            "map_sha256": sha_path(map_path),
            "response_sha256": sha_path(rsp),
            "packed": baseline_pack,
        },
        "target_restored_sha256": sha_bytes(restored),
        "relocation_multiset_exact": True,
        "target_derived_controls": {
            "RT": {"input_sha256": sha_bytes(rt), "packed": rt_pack},
            "PRT": {"input_sha256": sha_bytes(prt), "packed": prt_pack},
        },
        "tlink_i": {
            "builds": [
                {k: v for k, v in row.items() if k not in {"work", "exe", "map", "relocation_sites"}}
                for row in linked
            ],
            "packed": i_packs[0],
            "extra_tail_vs_target_restore_bytes": len(i_image) - len(restored),
            "extra_tail_vs_target_restore_all_zero": True,
        },
        "target_derived_payload_relocation_on_tlink_i": {
            "input_sha256": sha_bytes(pri),
            "packed": pri_pack,
            "retains_tlink_i_file_extent": True,
            "retains_tlink_i_minalloc_zero": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--op-source-dir", type=Path, required=True)
    parser.add_argument("--op-target-restored", type=Path, required=True)
    parser.add_argument("--maine-source-dir", type=Path, required=True)
    parser.add_argument("--maine-target-restored", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    output = output_dir(args.output_dir)

    if not RUNNER.is_file():
        raise ValueError("MS-DOS runner missing")
    runner_sha = sha_path(RUNNER)
    # Existing probes pin this runner; record the observed identity here as an
    # independent guard without making the linker experiment depend on PATH.
    if runner_sha != RUNNER_SHA256:
        raise ValueError(f"MS-DOS runner identity drift: {runner_sha}")
    linker, linker_sha = linker_identity()
    linker_help = b"/i   Initialize all segments"
    if linker_help not in linker.read_bytes():
        raise ValueError("active TLINK /i help string drift")

    artifact_args = {
        "th04-op": (args.op_source_dir.resolve(), args.op_target_restored.resolve()),
        "th04-maine": (args.maine_source_dir.resolve(), args.maine_target_restored.resolve()),
    }
    artifacts = {}
    toolchains = {}
    for artifact, (source, restored) in artifact_args.items():
        if not source.is_dir():
            raise ValueError(f"missing source tree: {source}")
        diet_binary, dosbox, diet_config, options, toolchain = check_toolchain(artifact)
        toolchains[artifact] = {**toolchain, "pack_options": options}
        artifacts[artifact] = inspect_artifact(
            artifact, source, restored, output,
            diet_binary, dosbox, diet_config, options,
        )

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 OP/MAINE current packed frontier plus natural TLINK /i uninitialized-trailing-segment negative; target-derived controls are private diagnostics only",
        "active_tlink_path": str(linker.relative_to(ROOT)),
        "active_tlink_sha256": linker_sha,
        "active_tlink_i_help": "/i   Initialize all segments",
        "runner_sha256": runner_sha,
        "diet_toolchains": toolchains,
        "artifacts": artifacts,
        "conclusion": (
            "The current natural candidates still pack 34 bytes (OP) and 46 bytes (MAINE) short of target. With target-derived relocation+tail controls (RT), each packs exactly one byte short; adding the remaining two-byte snd_load payload (PRT) is raw exact. Natural active-TLINK /i is a real linker mechanism for file-backing uninitialized trailing segments, but it over-materializes the image (minalloc=0) and packs 93 bytes (OP) / 167 bytes (MAINE) over target. Even target-derived payload+relocation controls on top of /i's own extent remain 79/119 bytes over target. Therefore active TLINK 6.10 /i is not an equivalent T preimage for these packed targets."
        ),
        "limit": (
            "The RT/PRT and target-payload/relocation-on-/i controls copy target-derived bytes only inside ignored private analysis and cannot be product source or exact reconstruction evidence. This probe closes only the active TLINK 6.10 /i route; other historical linker versions or independently attested object/topology mechanisms remain separate questions."
        ),
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(receipt_path),
        "receipt_sha256": sha_path(receipt_path),
        "op_baseline_packed": artifacts["th04-op"]["baseline"]["packed"]["size"],
        "op_rt_packed": artifacts["th04-op"]["target_derived_controls"]["RT"]["packed"]["size"],
        "op_i_packed": artifacts["th04-op"]["tlink_i"]["packed"]["size"],
        "maine_baseline_packed": artifacts["th04-maine"]["baseline"]["packed"]["size"],
        "maine_rt_packed": artifacts["th04-maine"]["target_derived_controls"]["RT"]["packed"]["size"],
        "maine_i_packed": artifacts["th04-maine"]["tlink_i"]["packed"]["size"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
