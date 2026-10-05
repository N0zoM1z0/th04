#!/usr/bin/env python3
"""Compare the product-owned TH04 MAIN bullet API with pinned headers."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import describe_omf  # noqa: E402

PRIVATE = (ROOT / ".analysis/reconstruction/probes").resolve()
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA256 = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
LOCAL_HEADER = ROOT / "src/main/bullet/bullet.hpp"
LOCAL_TYPES = ROOT / "src/main/bullet/types.hpp"
LOCAL_MOTION = ROOT / "src/main/playfield/motion.hpp"
REFERENCE_FILES = (
    "platform.h",
    "pc98.h",
    "th01/math/subpixel.hpp",
    "th01/main/playfld.hpp",
    "th01/rank.h",
    "th02/main/entity.hpp",
    "th02/main/playfld.hpp",
    "th02/main/scroll.hpp",
    "th02/sprites/cels.h",
    "th04/main/bullet/types.h",
    "th04/main/bullet/bullet.hpp",
    "th04/main/playfld.hpp",
    "th04/main/rank.hpp",
    "th04/main/scroll.hpp",
    "th04/math/motion.hpp",
    "th04/sprites/cels.h",
)
FLAGS = ("-c", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml")
TEST = r'''#include <stddef.h>
#include "th04/main/bullet/bullet.hpp"

void probe_bullet_template(void)
{
    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.patnum = 7;
    bullet_template.origin.x.v = TO_SP(8);
    bullet_template.origin.y.v = TO_SP(12);
    bullet_template.velocity.x.v = TO_SP(1);
    bullet_template.velocity.y.v = TO_SP(2);
    bullet_template.group = BG_RING;
    bullet_template.angle = 0x20;
    bullet_template.speed.v = TO_SP(3);
    bullet_template.count = 8;
    bullet_template.delta.spread_angle = 6;
    bullet_template.special_motion = BSM_NONE;
    bullet_template_tune();
}

void probe_bullet_spawn(void)
{
    bullets_add_regular_easy();
    bullets_add_regular_normal();
    bullets_add_regular_hard_lunatic();
    bullets_add_special_easy();
    bullets_add_special_normal();
    bullets_add_special_hard_lunatic();
    bullets_add_regular_fixedspeed();
    bullets_add_special_fixedspeed();
    bullets_and_gather_invalidate();
}

void probe_bullet_state(void)
{
    bullet_t near &bullet = bullets[0];
    bullet.flag = F_ALIVE;
    bullet.age = 1;
    bullet.pos.cur.x.v = TO_SP(4);
    bullet.pos.velocity.y.v = TO_SP(1);
    bullet.spawn_group = BG_SINGLE;
    bullet.speed_cur.v = 2;
    bullet.angle = 0x10;
    bullet.spawn_flag = BSF_ACTIVE;
    bullet.move_flag = BMF_REGULAR;
    bullet.special_motion = BSM_NONE;
    bullet.speed_final.v = 3;
    bullet.u1.turns_done = 1;
    bullet.u2.angle.turn_by = 2;
    bullet.patnum = 4;
    bullet_special.turns_max = 2;
    bullet_special.speed_delta.v = 1;
    bullet_template_special_angle.v = -1;
}

int probe_bullet_layout(void)
{
    return (
        sizeof(entity_flag_t)
        + sizeof(PlayfieldPoint)
        + sizeof(PlayfieldMotion)
        + sizeof(bullet_spawn_flag_t)
        + sizeof(bullet_move_flag_t)
        + sizeof(bullet_special_motion_t)
        + sizeof(bullet_special_angle_t)
        + sizeof(bullet_t)
        + sizeof(BulletTemplate)
        + sizeof(bullet_special)
        + sizeof(bullets)
        + BULLET_KILLBOX_W + BULLET_KILLBOX_H
        + BULLET_DIRECTION_SPRITE_ANGLE_STEP
        + PELLET_COUNT + BULLET16_COUNT + BULLET_COUNT
    );
}
'''


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_omf_sha256(data: bytes) -> str:
    """Hash link semantics while ignoring dependency/comment records."""

    digest = hashlib.sha256()
    offset = 0
    while offset < len(data):
        if offset + 3 > len(data):
            raise ValueError("truncated OMF record header")
        record_type = data[offset]
        size = int.from_bytes(data[offset + 1:offset + 3], "little")
        end = offset + 3 + size
        if end > len(data):
            raise ValueError("truncated OMF record")
        if record_type != 0x88:
            digest.update(data[offset:end])
        offset = end
    return digest.hexdigest()


def compile_variant(
    label: str,
    root: Path,
    includes: tuple[str, ...],
    env: dict[str, str],
    output: Path,
    test_source: str,
) -> dict[str, object]:
    (root / "obj").mkdir(parents=True)
    (root / "test.cpp").write_text(test_source, encoding="ascii")
    command = [
        "wine", str(RUNNER), "-e", "-x", "tcc", *FLAGS,
        *(f"-I{include}" for include in includes),
        "-nobj/", "test.cpp",
    ]
    result = subprocess.run(
        command, cwd=root, env=env, capture_output=True, text=True, timeout=240
    )
    (output / f"compile-{label}.log").write_text(
        json.dumps(command) + f"\nexit={result.returncode}\n"
        + result.stdout + result.stderr,
        encoding="utf-8",
    )
    if result.returncode:
        raise RuntimeError(f"TC4J failed; inspect compile-{label}.log")
    obj = root / "obj/test.obj"
    data = obj.read_bytes()
    omf = describe_omf(data)
    if not omf["valid"] or omf["module_name"] != "test.cpp":
        raise RuntimeError(f"unexpected {label} OMF structure")
    return {
        "harness_sha256": hashlib.sha256(test_source.encode("ascii")).hexdigest(),
        "object_sha256": hashlib.sha256(data).hexdigest(),
        "semantic_omf_sha256": semantic_omf_sha256(data),
        "record_counts": omf["record_counts"],
        "translator_comments": omf["translator_comments"],
        "dependency_paths": omf["dependency_paths"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(PRIVATE):
        parser.error("output must be a new private directory")

    subprocess.run(
        [sys.executable, "scripts/preflight.py"], cwd=ROOT, check=True,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        [sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT, check=True,
        stdout=subprocess.DEVNULL,
    )
    if sha(RUNNER) != RUNNER_SHA256:
        raise ValueError("MS-DOS Player identity drift")

    output.mkdir(parents=True)
    reference = output / "reference"
    local = output / "local"
    reference.mkdir()
    local.mkdir()
    for relative_text in REFERENCE_FILES:
        relative = Path(relative_text)
        destination = reference / "tree" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "_reference/ReC98" / relative, destination)
        # The maintained bullet declaration intentionally reuses the pinned
        # TH04 playfield/rank scaffolding.  Keep those own-artifact headers in
        # the local probe tree as the aggregate replay does, while leaving the
        # candidate bullet header itself out so the product wrapper remains the
        # exercised include.
        if relative_text != "th04/main/bullet/bullet.hpp":
            destination = local / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "_reference/ReC98" / relative, destination)
    shutil.copytree(ROOT / "src", local / "src")

    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    # The maintained header deliberately gives two fields/constants semantic
    # names. Compile equivalent source spellings against the pinned historical
    # header so this probe keeps testing generated ABI rather than source-level
    # identifier compatibility.
    reference_test = TEST.replace("spawn_group", "from_group").replace(
        "BULLET_DIRECTION_SPRITE_ANGLE_STEP", "ANGLE_PER_SPRITE"
    )
    reference_result = compile_variant(
        "reference", reference, ("tree",), env, output, reference_test
    )
    local_result = compile_variant(
        "local", local, ("src/main/include", "."), env, output, TEST
    )
    passed = (
        reference_result["semantic_omf_sha256"]
        == local_result["semantic_omf_sha256"]
    )
    receipt = {
        "schema_version": 2,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "TH04 MAIN product-owned bullet header ABI",
        "runner_sha256": RUNNER_SHA256,
        "compiler_flags": FLAGS,
        "local_header_sha256": sha(LOCAL_HEADER),
        "local_types_sha256": sha(LOCAL_TYPES),
        "local_motion_sha256": sha(LOCAL_MOTION),
        "reference_header_sha256": sha(
            ROOT / "_reference/ReC98/th04/main/bullet/bullet.hpp"
        ),
        "reference_types_sha256": sha(
            ROOT / "_reference/ReC98/th04/main/bullet/types.h"
        ),
        "reference": reference_result,
        "local": local_result,
        "passed": passed,
        "limit": (
            "Compiler-observed declaration and layout equivalence for the exercised "
            "TH04 bullet API; the cold aggregate replay remains the staged "
            "code/layout gate and bullet BSS ownership is separate."
        ),
    }
    (output / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "passed": passed,
        "semantic_omf_sha256": local_result["semantic_omf_sha256"],
    }, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
