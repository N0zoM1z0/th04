#!/usr/bin/env python3
"""Reproduce TH04 packed T extent by file-backing the shared MASTER BGM BSS.

This is a provenance/mechanism packet, not a claim that the historical source
spelled these BSS variables as explicit zero initializers.  It combines:

* two TH04 A/B targeted relinks with a symbolic all-zero 0xC6 BGM BSS;
* two TH05 cold builds using the same symbolic storage mechanism;
* independently restored TH05 OP/MAINE targets as cross-game evidence;
* pinned DIET -B -G packing of the TH04 mechanism candidates;
* a private target-derived P-only control proving that once the already-known
  two-byte snd_load difference is corrected, the packed files become raw exact.

No final MZ header, relocation table, object record, or packed stream is edited.
"""
from __future__ import annotations

import argparse
from collections import Counter
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

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.pc98 import parse_mz  # noqa: E402
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, run_checked  # noqa: E402
from probe_th04_maine_segment_topology_v470 import tasm  # noqa: E402
from probe_th04_master_object_split import build, sha  # noqa: E402
from replay_diet145f import check_toolchain  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_bgm_bss_fileback_v492.asm.in"
TEMPLATE_SHA = "395c74a5aed6116aa4fb61630c56df563e91ebc5f34998398d45aaa9915ed93c"
ZERO_BGM_SHA = "a6eab4025a7c9c0877549f6e5d790f66af88ee7f2320e814954e638d8051f812"

TH04 = {
    "op": {
        "base_exe": "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274",
        "base_map": "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee",
        "trial_exe": "994f80821d2918f0071e28f6e82d6ed660eac1d8473a532fd70fb743008f87ee",
        "trial_map": "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee",
        "packed_trial": "3eb7ca16dbca2a61962c678028865771bee969840366d1cbae6a758464db422d",
        "base_file": 73636, "trial_file": 76864,
        "base_load": 69028, "trial_load": 72256,
        "base_minalloc": 612, "trial_minalloc": 410,
        "relocs": 804,
        "program_diff_offsets": [0xDE8B, 0xDE8C],
        "target_restored_sha": "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
        "target_packed_size": 42290,
        "natural_packed_size": 42289,
        "data_source": "th04_op_master_data_tail.asm",
        "data_object": "opmdata.obj",
        "response": "obj/th04/op.@l",
        "exe": "bin/th04/op.exe",
        "map": "obj/th04/op.map",
    },
    "maine": {
        "base_exe": "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c",
        "base_map": "014d8dfdf31a2c42c39e76288f23842cff7bd84fb6534f6d46479ba5d8b0838e",
        "trial_exe": "27c17df711ed08f4c4bcada9b4ba699914d08cb164cd1444c36f1994527bab8a",
        "trial_map": "014d8dfdf31a2c42c39e76288f23842cff7bd84fb6534f6d46479ba5d8b0838e",
        "packed_trial": "ab131825ec17ab8da69a5f137ef2eb4b4c47f692a6fc735cf7298d2cab9d3a2e",
        "base_file": 65998, "trial_file": 69218,
        "base_load": 62414, "trial_load": 65634,
        "base_minalloc": 817, "trial_minalloc": 615,
        "relocs": 559,
        "program_diff_offsets": [0xD1D3, 0xD1D4],
        "target_restored_sha": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
        "target_packed_size": 38035,
        "natural_packed_size": 38034,
        "data_source": "th04_maine_master_data_tail.asm",
        "data_object": "mainemdata.obj",
        "response": "obj/th04/maine.@l",
        "exe": "bin/th04/maine.exe",
        "map": "obj/th04/maine.map",
    },
}

TH05 = {
    "op": {
        "base_exe": "732f9659e987c1837a6def7b3d83b3b150b39c991928bba14eadec09272b4eb6",
        "base_map": "da2598ec3f3c707fdc968d0d9dcca5cddf333beb9b8241d76d123ee0970af907",
        "trial_exe": "93938bb9f5a3e42408393d6da712271b7b7e42174a11de630afedbb9deded25a",
        "trial_map": "da2598ec3f3c707fdc968d0d9dcca5cddf333beb9b8241d76d123ee0970af907",
        "base_file": 78284, "trial_file": 80906,
        "base_load": 73164, "trial_load": 75786,
        "base_minalloc": 584, "trial_minalloc": 420,
        "target_restored_sha": "1caaa7f804146838e8771ae69487005f1ccd70cc8369dcb62e8adaf6addad71c",
        "target_load": 75786, "target_minalloc": 420,
    },
    "maine": {
        "base_exe": "60352c7ebb454be48da8516d5647df6d757e0f2d5a6262dbb678167cb925f1a4",
        "base_map": "27bece1e57bc7c11e7dc5a949baeacb10cd88391d581130c250616ecfaaa5277",
        "trial_exe": "7db550ff824f7e74b3682c4afe283e3bfcacb1061d9fe9698c1d3eb27480424b",
        "trial_map": "27bece1e57bc7c11e7dc5a949baeacb10cd88391d581130c250616ecfaaa5277",
        "base_file": 77422, "trial_file": 80038,
        "base_load": 73326, "trial_load": 75942,
        "base_minalloc": 2697, "trial_minalloc": 2533,
        "target_restored_sha": "247a7b90bb912562999da15267fe6e98fa72c8cccdbab3f1a88eee37c82fc9a4",
        "target_load": 75958, "target_minalloc": 2533,
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="bgm-bss-fileback-v492-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def public_load(map_path: Path, symbol: str) -> int:
    text = map_path.read_text(encoding="cp437", errors="replace")
    matches = re.findall(
        rf"^\s*([0-9A-F]{{4}}):([0-9A-F]{{4}})\s+(?:idle\s+)?{re.escape(symbol)}\s*$",
        text,
        re.M,
    )
    values = sorted({(int(seg, 16) * 16) + int(off, 16) for seg, off in matches})
    if len(values) != 1:
        raise ValueError(f"{map_path}: {symbol} public ambiguity: {values}")
    return values[0]


def apply_template(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v492 template identity drift")
    shutil.copy2(TEMPLATE, work / "libs/master.lib/bgm[bss].asm")


def diet_env(work: Path) -> dict[str, str]:
    e = os.environ.copy()
    e.update(
        SDL_VIDEODRIVER="dummy",
        SDL_AUDIODRIVER="dummy",
        XDG_CACHE_HOME=str(work / "cache"),
        XDG_CONFIG_HOME=str(work / "config"),
        XDG_DATA_HOME=str(work / "data"),
    )
    return e


def run_diet(work: Path, dosbox: Path, cfg: Path, command: str, log_name: str) -> None:
    cmd = [
        str(dosbox), "-defaultconf", "-defaultmapper", "-conf", str(cfg),
        "-fastlaunch", "-nogui", "-nomenu", "-exit", "-time-limit", "30",
        "-c", f'mount c "{work}"', "-c", "c:", "-c", f"{command} > {log_name}", "-c", "exit",
    ]
    p = subprocess.run(cmd, cwd=ROOT, env=diet_env(work), capture_output=True, text=True, timeout=40)
    (work / f"host-{log_name.lower()}").write_text(p.stdout + p.stderr)
    log = work / log_name.upper()
    if p.returncode or not log.is_file() or "Success!" not in log.read_bytes().decode("cp437", errors="replace"):
        raise RuntimeError(f"DIET command failed: {command}")


def restore_crossgame(target_id: str, out: Path, diet: Path, dosbox: Path, cfg: Path) -> bytes:
    manifest = load_target_manifest(ROOT / "config/targets.toml")
    art = find_artifact(manifest, target_id)
    packed = read_verified_artifact(ROOT, art)
    name = "OP.EXE" if "-op-" in target_id else "MAINE.EXE"
    w = out / target_id
    w.mkdir(parents=True)
    shutil.copy2(diet, w / "DIET.EXE")
    (w / name).write_bytes(packed)
    run_diet(w, dosbox, cfg, f"diet.exe -ra {name}", "RESTORE.LOG")
    return (w / name).read_bytes()


def pack_preimage(preimage: bytes, art: str, out: Path, diet: Path, dosbox: Path, cfg: Path) -> bytes:
    w = out / f"pack-{art}"
    w.mkdir(parents=True)
    shutil.copy2(diet, w / "DIET.EXE")
    name = "IN.EXE"
    (w / name).write_bytes(preimage)
    run_diet(w, dosbox, cfg, f"diet.exe -B -G {name}", "PACK.LOG")
    return (w / name).read_bytes()


def validate_bgm_span(mz, map_path: Path) -> dict[str, object]:
    part = public_load(map_path, "_bgm_part")
    timer = part - 4
    span = mz.program_image[timer:timer + 0xC6]
    if len(span) != 0xC6 or digest(span) != ZERO_BGM_SHA or any(span):
        raise ValueError(f"{map_path}: target/candidate BGM span is not exact zero 0xC6")
    return {"timerorg_load": timer, "bgm_bss_end": timer + 0xC6, "zero_span_sha256": digest(span)}


def build_th04_pair(source: Path, art: str, output: Path, label: str, target_raw: bytes, target_packed: bytes, diet: Path, dosbox: Path, cfg: Path) -> dict[str, object]:
    spec = TH04[art]
    work = output / label / art / "source"
    shutil.copytree(source, work, symlinks=True)
    base_exe = work / spec["exe"]
    base_map = work / spec["map"]
    if sha(base_exe) != spec["base_exe"] or sha(base_map) != spec["base_map"]:
        raise ValueError(f"{label}/{art}: v489 source identity drift")
    base = parse_mz(base_exe.read_bytes())
    base_sites = [r.linear for r in base.relocations]
    if len(base_exe.read_bytes()) != spec["base_file"] or len(base.program_image) != spec["base_load"] or base.header.minimum_extra_allocation != spec["base_minalloc"]:
        raise ValueError(f"{label}/{art}: v489 extent/minalloc drift")

    apply_template(work)
    tasm(work, output, f"{label}-{art}-bgm-zero", spec["data_source"], spec["data_object"])
    exe = work / spec["exe"]
    mp = work / spec["map"]
    exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
    rsp_arg = "@" + spec["response"].replace("/", "\\")
    run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", rsp_arg], work, output / f"link-{label}-{art}.log")

    raw = exe.read_bytes(); mz = parse_mz(raw); target = parse_mz(target_raw)
    sites = [r.linear for r in mz.relocations]; target_sites = [r.linear for r in target.relocations]
    if sha(exe) != spec["trial_exe"] or sha(mp) != spec["trial_map"]:
        raise ValueError(f"{label}/{art}: v492 output identity drift")
    if len(raw) != spec["trial_file"] or len(mz.program_image) != spec["trial_load"] or mz.header.minimum_extra_allocation != spec["trial_minalloc"]:
        raise ValueError(f"{label}/{art}: target T/minalloc surface drift")
    if mz.program_image[:len(base.program_image)] != base.program_image:
        raise ValueError(f"{label}/{art}: pre-existing program image changed")
    extra = mz.program_image[len(base.program_image):]
    if any(extra) or len(extra) != spec["trial_load"] - spec["base_load"]:
        raise ValueError(f"{label}/{art}: file-backed T tail is not the expected all-zero extent")
    if sites != base_sites or sites != target_sites or len(sites) != spec["relocs"]:
        raise ValueError(f"{label}/{art}: relocation table drift")
    diffs = [i for i, (a, b) in enumerate(zip(mz.program_image, target.program_image)) if a != b]
    if diffs != spec["program_diff_offsets"]:
        raise ValueError(f"{label}/{art}: remaining program difference drift: {diffs}")
    if sha(Path(target_raw_path := output / f"_unused-{label}-{art}")) if False else False:
        pass
    span = validate_bgm_span(mz, mp)
    if span["bgm_bss_end"] != len(mz.program_image):
        raise ValueError(f"{label}/{art}: TH04 T EOF is not exact BGM BSS end")

    packed = pack_preimage(raw, f"{label}-{art}-natural", output, diet, dosbox, cfg)
    if digest(packed) != spec["packed_trial"] or len(packed) != spec["natural_packed_size"]:
        raise ValueError(f"{label}/{art}: natural-T packed identity drift")
    if len(target_packed) != spec["target_packed_size"] or len(packed) + 1 != len(target_packed):
        raise ValueError(f"{label}/{art}: expected one-byte packed size frontier drift")

    # Private target-derived control: change only the known adjacent snd_load bytes.
    patched = bytearray(raw)
    for off in diffs:
        patched[mz.header.header_size + off] = target.program_image[off]
    patched_b = bytes(patched)
    if patched_b != target_raw:
        raise ValueError(f"{label}/{art}: P-only control did not reach exact target-restored MZ")
    packed_control = pack_preimage(patched_b, f"{label}-{art}-pcontrol", output, diet, dosbox, cfg)
    if packed_control != target_packed:
        raise ValueError(f"{label}/{art}: P-only control did not pack raw exact")

    return {
        "exe_sha256": sha(exe), "map_sha256": sha(mp),
        "file_size": len(raw), "load_image_bytes": len(mz.program_image), "minalloc": mz.header.minimum_extra_allocation,
        "relocation_count": len(sites), "relocation_table_target_exact": sites == target_sites,
        "base_program_prefix_unchanged": True,
        "file_backed_zero_tail_bytes": len(extra), "file_backed_zero_tail_sha256": digest(extra),
        "bgm_span": span,
        "remaining_program_diff_offsets": [hex(x) for x in diffs],
        "natural_packed_sha256": digest(packed), "natural_packed_size": len(packed),
        "target_packed_sha256": digest(target_packed), "target_packed_size": len(target_packed),
        "p_only_control_preimage_sha256": digest(patched_b),
        "p_only_control_packed_sha256": digest(packed_control), "p_only_control_raw_exact": True,
    }


def build_th05(source: Path, output: Path, label: str, targets: dict[str, bytes]) -> dict[str, object]:
    work = output / label / "th05" / "source"
    shutil.copytree(source, work, symlinks=True)
    for art in ("op", "maine"):
        spec = TH05[art]
        if sha(work / f"bin/th05/{art}.exe") != spec["base_exe"] or sha(work / f"obj/th05/{art}.map") != spec["base_map"]:
            raise ValueError(f"{label}/th05-{art}: baseline identity drift")
    apply_template(work)
    build(work, output / f"build-{label}-th05.log")

    result = {}
    for art in ("op", "maine"):
        spec = TH05[art]
        exe = work / f"bin/th05/{art}.exe"; mp = work / f"obj/th05/{art}.map"
        raw = exe.read_bytes(); mz = parse_mz(raw); target = parse_mz(targets[art])
        base_raw = (source / f"bin/th05/{art}.exe").read_bytes(); base = parse_mz(base_raw)
        if sha(exe) != spec["trial_exe"] or sha(mp) != spec["trial_map"]:
            raise ValueError(f"{label}/th05-{art}: zero-BGM cold-build identity drift")
        if len(raw) != spec["trial_file"] or len(mz.program_image) != spec["trial_load"] or mz.header.minimum_extra_allocation != spec["trial_minalloc"]:
            raise ValueError(f"{label}/th05-{art}: extent/minalloc drift")
        if mz.program_image[:len(base.program_image)] != base.program_image:
            raise ValueError(f"{label}/th05-{art}: base program prefix changed")
        extra = mz.program_image[len(base.program_image):]
        if any(extra):
            raise ValueError(f"{label}/th05-{art}: added extent is not all zero")
        if digest(targets[art]) != spec["target_restored_sha"] or len(target.program_image) != spec["target_load"] or target.header.minimum_extra_allocation != spec["target_minalloc"]:
            raise ValueError(f"{label}/th05-{art}: restored target identity/surface drift")
        target_span = validate_bgm_span(target, mp)
        trial_span = validate_bgm_span(mz, mp)
        if trial_span != target_span:
            raise ValueError(f"{label}/th05-{art}: BGM span projection drift")
        if art == "op":
            if len(mz.program_image) != len(target.program_image) or trial_span["bgm_bss_end"] != len(target.program_image):
                raise ValueError(f"{label}/th05-op: zero-BGM mechanism did not reproduce target T extent")
        else:
            if trial_span["bgm_bss_end"] != len(mz.program_image) or len(target.program_image) - len(mz.program_image) != 16:
                raise ValueError(f"{label}/th05-maine: expected independent 16-byte post-BGM target tail drift")
        result[art] = {
            "exe_sha256": sha(exe), "map_sha256": sha(mp),
            "base_file_size": len(base_raw), "trial_file_size": len(raw),
            "base_load_image_bytes": len(base.program_image), "trial_load_image_bytes": len(mz.program_image),
            "trial_minalloc": mz.header.minimum_extra_allocation,
            "target_restored_sha256": digest(targets[art]), "target_load_image_bytes": len(target.program_image),
            "target_minalloc": target.header.minimum_extra_allocation,
            "base_program_prefix_unchanged": True,
            "file_backed_zero_tail_bytes": len(extra), "file_backed_zero_tail_sha256": digest(extra),
            "bgm_span": trial_span,
            "target_bytes_after_bgm_span": len(target.program_image) - target_span["bgm_bss_end"],
        }
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--op-source-dir", type=Path, required=True)
    ap.add_argument("--maine-source-dir", type=Path, required=True)
    ap.add_argument("--th05-source-dir", type=Path, required=True)
    ap.add_argument("--op-target-restored", type=Path, required=True)
    ap.add_argument("--maine-target-restored", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    output = output_dir(args.output_dir)
    op_source = args.op_source_dir.resolve(); maine_source = args.maine_source_dir.resolve(); th05_source = args.th05_source_dir.resolve()
    op_target_raw = args.op_target_restored.resolve().read_bytes(); maine_target_raw = args.maine_target_restored.resolve().read_bytes()
    if digest(op_target_raw) != TH04["op"]["target_restored_sha"] or digest(maine_target_raw) != TH04["maine"]["target_restored_sha"]:
        raise ValueError("TH04 target-restored identity drift")

    diet, dosbox, cfg, _, tool = check_toolchain("th04-op")
    manifest = load_target_manifest(ROOT / "config/targets.toml")
    op_packed_target = read_verified_artifact(ROOT, find_artifact(manifest, "th04-op"))
    maine_packed_target = read_verified_artifact(ROOT, find_artifact(manifest, "th04-maine"))
    th05_targets = {
        "op": restore_crossgame("th05-op-smoke", output / "crossgame-restores", diet, dosbox, cfg),
        "maine": restore_crossgame("th05-maine-smoke", output / "crossgame-restores", diet, dosbox, cfg),
    }
    if digest(th05_targets["op"]) != TH05["op"]["target_restored_sha"] or digest(th05_targets["maine"]) != TH05["maine"]["target_restored_sha"]:
        raise ValueError("TH05 target-restored identity drift")

    builds = {}
    for label in ("a", "b"):
        builds[label] = {
            "th04": {
                "op": build_th04_pair(op_source, "op", output, label, op_target_raw, op_packed_target, diet, dosbox, cfg),
                "maine": build_th04_pair(maine_source, "maine", output, label, maine_target_raw, maine_packed_target, diet, dosbox, cfg),
            },
            "th05": build_th05(th05_source, output, label, th05_targets),
        }
    # Ignore only filesystem-specific log paths; all recorded result dictionaries must be deterministic.
    if builds["a"] != builds["b"]:
        raise ValueError("A/B v492 result dictionaries differ")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 OP/MAINE BGM-BSS file-backing mechanism plus TH05 cross-game corroboration; no historical-source promotion",
        "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA,
        "diet_toolchain": tool,
        "zero_bgm_span_sha256": ZERO_BGM_SHA,
        "builds": builds,
        "observed_effect": (
            "File-backing the shared 0xC6 MASTER BGM BSS with explicit symbolic zero data is sufficient to reproduce the TH04 target-restored T extent and derived minalloc exactly in both OP and MAINE, while preserving all pre-existing program bytes and the already target-exact relocation tables. Pinned DIET -B -G then produces packed files exactly one byte shorter than target; a private control that changes only the known two adjacent snd_load program bytes reaches the exact target-restored MZ and packs raw-exact to both original targets. Independent TH05 cold builds corroborate the same BGM file-backing structure: TH05 OP reaches the real restored target extent/minalloc exactly, and TH05 MAINE reaches the exact BGM end/minalloc while its real target has one additional 16-byte post-BGM tail. All four TH04/TH05 target-restored BGM spans are the same 198 zero bytes."
        ),
        "limit": (
            "This packet proves a natural TASM/TLINK mechanism and cross-game target structure, but does not prove that the original ZUN source declared MASTER BGM BSS as initialized zero. The independently attested historical masters.lib b_data.OBJ has no BSS LEDATA (v430/v491), so the historical trigger may instead be another library version, a monolithic object spelling, or a post-link transform. The explicit-zero template remains replay/provenance evidence and is not promoted as maintained authored source. The P-only packed control is target-derived diagnostic evidence only."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp), "receipt_sha256": sha(rp),
        "th04_T_surface_exact": True,
        "th05_op_T_surface_exact": True,
        "p_only_controls_packed_raw_exact": True,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
