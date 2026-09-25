#!/usr/bin/env python3
"""Bounded TC4.02 probe for SCORE codec rotate intrinsics; negative exactness evidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked
from replay_th04_op_playchar_menu_initial import SNAPSHOT, sha_file

STDLIB = ROOT / ".analysis/toolchain/installed/tc40j/INCLUDE/STDLIB.H"
STDLIB_SHA = "73a522bb6e4381f1c800a4fdd192b183768888675ebb8601a0263daac5a36a45"

PLAIN_SOURCE = r'''
#include <stdlib.h>

volatile unsigned char sink;

unsigned char near test_crotr(unsigned char feedback)
{
    return _crotr(feedback, 3);
}

unsigned char near test_rotr(unsigned char feedback)
{
    return (unsigned char)_rotr(feedback, 3);
}

unsigned char near test_builtin_rotr(unsigned char feedback)
{
    return (unsigned char)__rotr__(feedback, 3);
}

void near test_local_crotr(void)
{
    unsigned char feedback = sink;
    feedback = _crotr(feedback, 3);
    sink = feedback;
}

void near test_local_rotr(void)
{
    unsigned char feedback = sink;
    feedback = (unsigned char)_rotr(feedback, 3);
    sink = feedback;
}

void near test_local_builtin_rotr(void)
{
    unsigned char feedback = sink;
    feedback = (unsigned char)__rotr__(feedback, 3);
    sink = feedback;
}
'''

PRAGMA_SOURCE = r'''
#include <mem.h>
#include <stdlib.h>

#pragma intrinsic memcpy
#pragma intrinsic _crotr
#pragma intrinsic _rotr

volatile unsigned char sink;

unsigned char near test_crotr(unsigned char feedback)
{
    return _crotr(feedback, 3);
}

void near test_local_crotr(void)
{
    unsigned char feedback = sink;
    feedback = _crotr(feedback, 3);
    sink = feedback;
}

void near test_local_rotr(void)
{
    unsigned char feedback = sink;
    feedback = (unsigned char)_rotr(feedback, 3);
    sink = feedback;
}
'''


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def find_asm(work: Path, filename: str) -> Path:
    stem = Path(filename).stem.lower()
    exact = work / "obj/th04" / f"{stem}.asm"
    if exact.is_file():
        return exact
    # Fallback for DOS 8.3 shortening if a future probe uses a longer basename.
    prefix = stem[:5]
    candidates = sorted((work / "obj/th04").glob(prefix + "*.asm"))
    if len(candidates) != 1:
        raise RuntimeError(f"expected one generated ASM for {filename}, got {candidates}")
    return candidates[0]


def compile_surface(work: Path, output: Path, label: str, filename: str, source: str) -> dict[str, object]:
    path = work / filename
    path.write_text(source, encoding="ascii")
    log = output / f"compile-{label}-{filename}.log"
    run_checked(
        [
            "wine", str(RUNNER), "-e", "-x", "tcc", "-S", "-I.", "-O", "-b-", "-3",
            "-Z", "-d", "-DGAME=4", "-ml", "-DBINARY='O'", "-nobj/th04/", filename,
        ],
        work,
        log,
    )
    asm = find_asm(work, filename)
    text = asm.read_text(encoding="cp437", errors="replace")
    log_text = log.read_text(encoding="utf-8", errors="replace")
    return {
        "asm_path": asm,
        "asm_text": text,
        "asm_sha256": sha_file(asm),
        "log_text": log_text,
        "log_sha256": sha(log_text.encode("utf-8")),
    }


def check_plain(text: str) -> dict[str, object]:
    if text.count("call\tfar ptr __crotr") < 2:
        raise RuntimeError("_crotr no longer lowers to FAR RTL call")
    if text.count("call\tfar ptr __rotr") < 2:
        raise RuntimeError("_rotr no longer lowers to FAR RTL call")
    if text.count("ror\tax,3") < 2:
        raise RuntimeError("__rotr__ no longer lowers to 16-bit ROR AX,3")
    lowered = text.lower()
    if "ror\tbyte ptr" in lowered or "ror\tbyte " in lowered:
        raise RuntimeError("unexpected byte-memory ROR appeared in TC4 intrinsic surface")
    if "ror\tal,3" in lowered:
        raise RuntimeError("unexpected 8-bit ROR AL,3 appeared in TC4 intrinsic surface")
    return {
        "crotr_far_call_count": text.count("call\tfar ptr __crotr"),
        "rotr_far_call_count": text.count("call\tfar ptr __rotr"),
        "builtin_rotr_ax_count": text.count("ror\tax,3"),
        "byte_memory_ror_count": lowered.count("ror\tbyte"),
        "ror_al_count": lowered.count("ror\tal,3"),
    }


def check_pragma(text: str, log_text: str) -> dict[str, object]:
    warnings = log_text.count("Ill-formed pragma")
    if warnings != 2:
        raise RuntimeError(f"expected two ill-formed pragma warnings for _crotr/_rotr, got {warnings}")
    if text.count("call\tfar ptr __crotr") < 2:
        raise RuntimeError("pragma surface unexpectedly changed _crotr lowering")
    if text.count("call\tfar ptr __rotr") < 1:
        raise RuntimeError("pragma surface unexpectedly changed _rotr lowering")
    return {
        "ill_formed_pragma_warning_count": warnings,
        "control_memcpy_intrinsic_pragma_present": "#pragma intrinsic memcpy" in PRAGMA_SOURCE,
        "crotr_far_call_count": text.count("call\tfar ptr __crotr"),
        "rotr_far_call_count": text.count("call\tfar ptr __rotr"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        ap.error("output must be a new directory below .analysis/reconstruction/probes")

    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    if not STDLIB.is_file() or sha_file(STDLIB) != STDLIB_SHA:
        raise RuntimeError("pinned TC4.02 STDLIB.H drift")

    header = STDLIB.read_text(encoding="cp437", errors="replace")
    required = (
        "unsigned char  _RTLENTRY   _crotr(unsigned char __value, int __count);",
        "unsigned       _RTLENTRY   __rotr__(unsigned __value, int __count);",
        "#define  _rotr(__value, __count)  __rotr__(__value, __count)",
    )
    if any(item not in header for item in required):
        raise RuntimeError("TC4.02 rotate declarations/macros drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        copy_compact_snapshot(SNAPSHOT, work, "op")

        plain = compile_surface(work, output, label, "rot758.cpp", PLAIN_SOURCE)
        pragma = compile_surface(work, output, label, "rot759.cpp", PRAGMA_SOURCE)

        builds[label] = {
            "plain_source_sha256": sha(PLAIN_SOURCE.encode("ascii")),
            "plain_asm_sha256": plain["asm_sha256"],
            "plain_log_sha256": plain["log_sha256"],
            "plain_observation": check_plain(str(plain["asm_text"])),
            "pragma_source_sha256": sha(PRAGMA_SOURCE.encode("ascii")),
            "pragma_asm_sha256": pragma["asm_sha256"],
            "pragma_log_sha256": pragma["log_sha256"],
            "pragma_observation": check_pragma(str(pragma["asm_text"]), str(pragma["log_text"])),
        }

    # Debug/private-symbol text can differ across isolated DOS worktrees.
    # The compiler-mechanism oracle is the structured lowering observation.
    def stable(build: dict[str, object]) -> dict[str, object]:
        return {
            "plain_source_sha256": build["plain_source_sha256"],
            "plain_observation": build["plain_observation"],
            "pragma_source_sha256": build["pragma_source_sha256"],
            "pragma_observation": build["pragma_observation"],
        }

    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("independent TC4 rotate-intrinsic semantic observations differ")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TC4.02 SCORE byte-rotate intrinsic surface; negative exactness mechanism",
        "artifacts_impacted": ["th04-op", "th04-maine"],
        "target_opcode": "C0 4E FF 03 (ROR byte ptr [BP-1],3)",
        "toolchain_header": str(STDLIB.relative_to(ROOT)),
        "toolchain_header_sha256": STDLIB_SHA,
        "driver_sha256": sha_file(Path(__file__).resolve()),
        "builds": builds,
        "result": "no-admissible-byte-ror-intrinsic",
        "findings": [
            "_crotr(unsigned char,3) is an RTL FAR call to __crotr, including for a byte local.",
            "_rotr(unsigned,3) remains an RTL FAR call to __rotr under the pinned OP flags.",
            "Direct __rotr__ is a compiler intrinsic but operates on 16-bit unsigned and lowers to ROR AX,3, not an 8-bit memory rotate.",
            "TC4.02 rejects #pragma intrinsic _crotr and #pragma intrinsic _rotr as ill-formed while accepting the existing #pragma intrinsic memcpy syntax as the control form.",
            "No tested TC4.02 rotate surface emits ROR byte ptr [BP-1],3.",
        ],
        "limit": (
            "This is a bounded compiler-mechanism negative probe. It does not prove historical source spelling "
            "and does not grant or revoke exactness by itself. It closes the previously untested TC4.02 rotate-"
            "intrinsic path for the maintained SCORE codec frontier."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    # Keep the durable receipt/logs but prune copied source trees.
    for label in ("a", "b"):
        shutil.rmtree(output / label)

    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha_file(path),
        "result": receipt["result"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
