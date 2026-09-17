#!/usr/bin/env python3
"""Diagnostic A/B ZUN.COM replay with maintained cfg_init source.

The remaining ZUN inputs come from pinned ReC98 snapshots. Passing this probe
does not promote an exact unit or establish a standalone TH04 build.
"""

from __future__ import annotations

import argparse
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
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import parse_omf  # noqa: E402
from inspect_dialog_fixup_order import code_ledata  # noqa: E402

SNAPSHOT = ROOT / ".analysis/reconstruction/exact-unit-replay/gptweb-v214-demo-fixupp-diagnostic-001"
SOURCE = ROOT / "src/zun/config/cfg_init.cpp"
RESIDENT_HEADER = ROOT / "src/shared/config/resident.hpp"
CFG_HEADER = ROOT / "src/shared/config/cfg.hpp"
DEFAULTS_HEADER = ROOT / "src/zun/config/defaults.hpp"
UPSTREAM_SOURCE_SHA = "6590a16417c60dd4858b962463f1433e6a66ff675001e27ec32083a7198e7b12"
BASELINE_COM_SHA = "cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110"
BASELINE_FLAT_SHA = "baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e"
TARGET_CFG_SHA = "8fc23f22f653db2afd65ad4cdab19776f5e9f1cdbbfa9de2dd407426fed9bfa2"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def code(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    groups = code_ledata(records, "_TEXT")
    if not groups or groups[0][0] != 0:
        raise ValueError(f"missing _TEXT CODE at offset zero: {path}")
    result = bytearray(groups[-1][1])
    cursor = 0
    for start, end, record_number, _ in groups:
        if start != cursor:
            raise ValueError(f"noncontiguous _TEXT LEDATA: {path}")
        result[start:end] = records[record_number - 1].data[3:]
        cursor = end
    return bytes(result)


def run(cmd: list[str], cwd: Path, log: Path, env: dict[str, str] | None = None) -> None:
    completed = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
    log.write_text(
        json.dumps(cmd, ensure_ascii=False) + f"\nexit={completed.returncode}\n"
        + completed.stdout + "\n" + completed.stderr
    )
    if completed.returncode:
        raise RuntimeError(f"command failed ({completed.returncode}): {log}")


def wine_env() -> dict[str, str]:
    env = os.environ.copy()
    env["WINEPREFIX"] = str(ROOT / ".analysis/toolchain/wineprefix")
    env["WINEDEBUG"] = "-all"
    env["MSDOS_PATH"] = r"C:\TC4\BIN;C:\TASM50\BIN"
    return env


def wine_cmd(*args: str) -> list[str]:
    return ["wine", str(ROOT / "_reference/ReC98/bin/msdos.exe"), "-e", "-x", *args]


def materialize_local_headers(work: Path) -> None:
    for source in (RESIDENT_HEADER, CFG_HEADER, DEFAULTS_HEADER):
        relative = source.relative_to(ROOT)
        destination = work / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())


def localize_wrapper_includes(upstream: str) -> str:
    changes = (
        ('#include "th01/rank.h"\n', '#include "src/zun/config/defaults.hpp"\n'),
        ('#include "th04/resident.hpp"\n', ''),
        ('#include "th04/snd/snd.h"\n', ''),
        ('#include "th04/formats/cfg.hpp"\n', ''),
    )
    for old, new in changes:
        if upstream.count(old) != 1:
            raise ValueError(f"unrecognized upstream include: {old.strip()}")
        upstream = upstream.replace(old, new)
    return upstream


def build(label: str, snapshot: Path, output: Path, target_cfg: bytes,
          target_defaults: bytes) -> dict[str, str]:
    if sha((snapshot / "th04/res_huma.cpp").read_bytes()) != UPSTREAM_SOURCE_SHA:
        raise ValueError(f"{label}: unexpected upstream C++ source")
    if sha((snapshot / "bin/th04/res_huma.com").read_bytes()) != BASELINE_COM_SHA:
        raise ValueError(f"{label}: unexpected baseline RES_HUMA.COM")
    if sha((snapshot / "bin/th04/zun.com").read_bytes()) != BASELINE_FLAT_SHA:
        raise ValueError(f"{label}: unexpected baseline flat ZUN.COM")

    work = output / "work" / label / "source"
    shutil.copytree(snapshot, work, symlinks=True)
    saved = output / "outputs" / label
    saved.mkdir(parents=True)
    local = work / "th04/zun/config/cfg_init.cpp"
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_bytes(SOURCE.read_bytes())
    materialize_local_headers(work)
    (work / "th04/cfginit.cpp").write_text('#include "th04/zun/config/cfg_init.cpp"\n')

    upstream = localize_wrapper_includes(
        (work / "th04/res_huma.cpp").read_bytes().decode("cp932")
    )
    if upstream.count("char debug = 0;") != 1 or upstream.count("#define LOGO") != 1:
        raise ValueError(f"{label}: unrecognized upstream cfg_init boundary")
    start = upstream.index("char debug = 0;")
    end = upstream.index("#define LOGO")
    if start >= end:
        raise ValueError(f"{label}: invalid upstream source order")
    wrapper = (upstream[:start] + '#include "th04/zun/config/cfg_init.cpp"\n\n'
               + upstream[end:]).encode("cp932")
    (work / "th04/res_huma.cpp").write_bytes(wrapper)
    (saved / "res_huma_wrapper.cpp").write_bytes(wrapper)

    env = wine_env()
    cflags = ["-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-mt", "-nobj/th04/"]
    steps = (
        ("cfginit-object", wine_cmd("tcc", *cflags, "th04/cfginit.cpp"), "obj/th04/cfginit.obj", "cfginit.obj"),
        ("res-huma-object", wine_cmd("tcc", *cflags, "th04/res_huma.cpp"), "obj/th04/res_huma.obj", "res_huma.obj"),
        ("res-huma-link", wine_cmd("tlink", r"@obj\th04\res_huma.@l"), "bin/th04/res_huma.com", "res_huma.com"),
        ("zun-composite", wine_cmd("bin/Pipeline/zungen.com", "obj/Pipeline/zun_stub.bin",
                                    "obj/th04/zuncom.@z", "obj/th04/zuncom.bin"),
         "obj/th04/zuncom.bin", "zuncom.bin"),
        ("zun-flat", wine_cmd("bin/Pipeline/comcstm.com", "th04/zun.txt", "obj/th04/zuncom.bin",
                               "obj/Pipeline/cstmstub.bin", "621381155", "bin/th04/zun.com"),
         "bin/th04/zun.com", "zun.flat.com"),
    )
    for name, cmd, relative_output, saved_name in steps:
        generated = work / relative_output
        generated.unlink(missing_ok=True)
        run(cmd, work, saved / f"{name}.log", env)
        if not generated.is_file():
            raise ValueError(f"{label}: missing {relative_output}")
        (saved / saved_name).write_bytes(generated.read_bytes())
    (saved / "res_huma.map").write_bytes((work / "obj/th04/res_huma.map").read_bytes())

    standalone = code(saved / "cfginit.obj")
    composite = code(saved / "res_huma.obj")
    component = (saved / "res_huma.com").read_bytes()
    flat = (saved / "zun.flat.com").read_bytes()
    if len(standalone) != 0x98 or standalone != composite[:0x98]:
        raise ValueError(f"{label}: maintained cfg_init CODE differs from composite")
    if len(composite) != 0x194 or component[0x267:0x2FF] != target_cfg:
        raise ValueError(f"{label}: cfg_init linked bytes or contribution extent differ")
    if component[0x14FF:0x1505] != target_defaults:
        raise ValueError(f"{label}: linked six-byte default options differ from target")
    if sha(flat) != BASELINE_FLAT_SHA:
        raise ValueError(f"{label}: full flat ZUN output differs from target payload")
    return {
        "standalone_object_sha256": sha((saved / "cfginit.obj").read_bytes()),
        "standalone_code_sha256": sha(standalone),
        "composite_object_sha256": sha((saved / "res_huma.obj").read_bytes()),
        "composite_code_sha256": sha(composite),
        "map_sha256": sha((saved / "res_huma.map").read_bytes()),
        "component_com_sha256": sha(component),
        "flat_com_sha256": sha(flat),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-a", type=Path, default=SNAPSHOT / "a/source")
    parser.add_argument("--snapshot-b", type=Path, default=SNAPSHOT / "b/source")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--keep-workdirs", action="store_true")
    args = parser.parse_args()
    private_root = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        probe_root = private_root / "reconstruction/probes"
        probe_root.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="zun-cfg-replay-", dir=probe_root))
    else:
        output = args.output_dir.resolve()
        if not output.is_relative_to(private_root) or output.exists():
            parser.error("output directory must be new and below .analysis")
        output.mkdir(parents=True)
    if not SOURCE.is_file():
        parser.error("maintained cfg_init source is missing")

    targets = tomllib.loads((ROOT / "config/targets.toml").read_text())["artifacts"]
    target = next(item for item in targets if item["id"] == "th04-zun")
    if sha((ROOT / target["private_path"]).read_bytes()) != target["sha256"]:
        raise ValueError("pinned packed ZUN target identity failed")
    payload = (ROOT / ".analysis/reconstruction/v218-th04-zun-diet/payload.bin").read_bytes()
    if sha(payload) != BASELINE_FLAT_SHA or sha(payload[0xDCF:0xE67]) != TARGET_CFG_SHA:
        raise ValueError("attested decoded payload identity failed")

    target_cfg = payload[0xDCF:0xE67]
    target_defaults = payload[0x2067:0x206D]
    if target_defaults != bytes.fromhex("FF 03 02 01 01 01"):
        raise ValueError("target six-byte default options changed")
    if (target_cfg[0x11:0x14] != bytes.fromhex("B9 06 00")
            or target_cfg[0x34:0x36] != bytes.fromhex("6A 0A")
            or target_cfg[0x6E:0x70] != bytes.fromhex("6A 06")):
        raise ValueError("target cfg size and resident offset instructions changed")
    builds = {
        "a": build("a", args.snapshot_a.resolve(), output, target_cfg, target_defaults),
        "b": build("b", args.snapshot_b.resolve(), output, target_cfg, target_defaults),
    }
    if builds["a"]["standalone_code_sha256"] != builds["b"]["standalone_code_sha256"]:
        raise ValueError("A/B standalone CODE differs")
    for field in ("composite_code_sha256", "map_sha256", "component_com_sha256", "flat_com_sha256"):
        if builds["a"][field] != builds["b"][field]:
            raise ValueError(f"A/B {field} differs")

    diet_dir = output / "diet"
    run([
        sys.executable, str(ROOT / "scripts/probes/replay_diet145f.py"), "th04-zun",
        "--candidate-a", str(output / "outputs/a/zun.flat.com"),
        "--candidate-b", str(output / "outputs/b/zun.flat.com"),
        "--output-dir", str(diet_dir),
    ], ROOT, output / "diet.log")
    diet = json.loads((diet_dir / "receipt.json").read_text())
    if not diet.get("packed_raw_exact") or not diet.get("packed_outputs_identical"):
        raise ValueError("DIET A/B packed target comparison failed")
    receipt = {
        "schema_version": 1,
        "claim_scope": "diagnostic source-present cfg_init overlay; no exact promotion",
        "artifact": "th04-zun",
        "target_sha256": target["sha256"],
        "target_payload_sha256": sha(payload),
        "target_cfg_init_sha256": sha(target_cfg),
        "target_default_options_payload_offset": "0x2067",
        "target_default_options_hex": target_defaults.hex(),
        "product_source_sha256": sha(SOURCE.read_bytes()),
        "resident_header_sha256": sha(RESIDENT_HEADER.read_bytes()),
        "cfg_header_sha256": sha(CFG_HEADER.read_bytes()),
        "defaults_header_sha256": sha(DEFAULTS_HEADER.read_bytes()),
        "builds": builds,
        "diet_receipt_sha256": sha((diet_dir / "receipt.json").read_bytes()),
        "packed_raw_exact": True,
        "limitations": "Remaining ZUN source, libraries, and composite tools are supplied by pinned ReC98 snapshots; not a standalone checked-in build.",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    if not args.keep_workdirs:
        shutil.rmtree(output / "work")
    print(json.dumps({"receipt": str(output / "receipt.json"), "packed_raw_exact": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
