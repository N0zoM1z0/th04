#!/usr/bin/env python3
"""Audit pinned ReC98 history and the MAGNet2010 leak for final-blocker provenance.

This probe is intentionally provenance-only. It verifies that ReC98's 2023
checkerboard/carpet decompilations use low-level assembly, then checks whether
the independently documented MAGNet2010 TH04 source leak can witness those
operations. It must not grant source or exactness credit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
REC98 = ROOT / "_reference" / "ReC98"

PINNED_REC98 = "b6ba5b0a529edbb31efdf8c0e939263804f8ee47"
CHECKER_COMMIT = "45df9ec0c688e7e463c690112ed61d3a734b1cc6"
CARPET_COMMIT = "2aae476a855101c2d86fb192a71b2e74d34feaca"
DEMO_ASM_COMMIT = "4c888ee4ade6aca57b56eae3ecc5673f0dafdf9b"
MAGNET_DOC_COMMIT = "7c80fb01f2847330e153d296b5b93be7bc2a75f3"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> bytes:
    done = subprocess.run(
        ["git", "-C", str(REC98), *args],
        check=True,
        capture_output=True,
    )
    return done.stdout


def git_text(*args: str) -> str:
    return git(*args).decode("utf-8", errors="replace")


def show(rev_path: str) -> str:
    return git_text("show", rev_path)


def new_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction" / "probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="v495-upstream-provenance-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def require(haystack: str, needle: str, label: str) -> None:
    if needle not in haystack:
        raise ValueError(f"{label}: missing expected text {needle!r}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    output = new_output(args.output_dir)

    head = git_text("rev-parse", "HEAD").strip()
    if head != PINNED_REC98:
        raise ValueError(f"pinned ReC98 HEAD drift: {head}")

    for commit in (CHECKER_COMMIT, CARPET_COMMIT, DEMO_ASM_COMMIT, MAGNET_DOC_COMMIT):
        resolved = git_text("rev-parse", commit).strip()
        if resolved != commit:
            raise ValueError(f"commit drift: {commit} -> {resolved}")
        subprocess.run(
            ["git", "-C", str(REC98), "merge-base", "--is-ancestor", commit, PINNED_REC98],
            check=True,
            capture_output=True,
        )

    checker = show(f"{CHECKER_COMMIT}:th04/main/checkerb.cpp")
    checker_parent_asm = show(f"{CHECKER_COMMIT}^:th04_main.asm")
    require(checker, "asm { loop put_loop; }", "checkerboard decompilation")
    require(checker_parent_asm, "loop\tloc_120B4", "checkerboard parent ASM")
    require(checker_parent_asm, "sub_12076\tproc near", "checkerboard parent ASM")

    carpet = show(f"{CARPET_COMMIT}:th04/main/stage/stages.cpp")
    carpet_parent_asm = show(f"{CARPET_COMMIT}^:th04_main.asm")
    for needle in (
        "push\tds;",
        "pop \tes;",
        "asm { mul bx; }",
        "asm { lodsb; }",
        "asm { shl\tdi, 1; }",
        "asm { loop column_loop; }",
    ):
        require(carpet, needle, "carpet decompilation")
    require(carpet_parent_asm, "sub_EA8A\tproc near", "carpet parent ASM")
    require(carpet_parent_asm, "loop\tloc_EAB0", "carpet parent ASM")

    contributing = show(f"{PINNED_REC98}:CONTRIBUTING.md")
    require(contributing, "[MAGNet2010]", "ReC98 provenance documentation")
    require(contributing, "handling demo recording and the setup", "MAGNet2010 scope")
    require(contributing, "of the game's EMS area", "MAGNet2010 scope")

    magnet_hits = git_text(
        "grep", "-n", "-F", "[MAGNet2010]", PINNED_REC98, "--", "th04"
    ).splitlines()
    if not magnet_hits:
        raise ValueError("no MAGNet2010-tagged TH04 identifiers")
    if any("checkerb" in line.lower() or "stages.cpp" in line.lower() for line in magnet_hits):
        raise ValueError("MAGNet2010 unexpectedly tags a final-blocker source file")

    demo_asm_history = git_text(
        "log", "--format=%H", "-S_asm {", PINNED_REC98, "--", "th04/main/demo.hpp"
    ).splitlines()
    if not demo_asm_history or demo_asm_history[0] != DEMO_ASM_COMMIT:
        raise ValueError(f"demo_end inline-ASM history drift: {demo_asm_history[:3]}")

    commit_meta = {}
    for label, commit in (
        ("checkerboard_decompilation", CHECKER_COMMIT),
        ("carpet_decompilation", CARPET_COMMIT),
        ("demo_end_inline_asm_introduction", DEMO_ASM_COMMIT),
        ("magnet_reference_documentation", MAGNET_DOC_COMMIT),
    ):
        commit_meta[label] = git_text(
            "show", "-s", "--format=%H%n%aI%n%s", commit
        ).splitlines()

    bundle = (
        checker.encode()
        + checker_parent_asm.encode()
        + carpet.encode()
        + carpet_parent_asm.encode()
        + contributing.encode()
        + "\n".join(magnet_hits).encode()
        + "\n".join(demo_asm_history).encode()
    )

    receipt = {
        "schema_version": 1,
        "claim_scope": "TH04 final blocker upstream/source-provenance audit",
        "pinned_rec98_commit": PINNED_REC98,
        "source_bundle_sha256": sha(bundle),
        "checkerboard": {
            "decompilation_commit": CHECKER_COMMIT,
            "observed_inline_asm": ["LOOP put_loop"],
            "parent_state": "target-derived monolithic th04_main.asm disassembly",
            "classification": "upstream decompilation evidence, not independent historical source",
        },
        "carpet": {
            "decompilation_commit": CARPET_COMMIT,
            "observed_inline_asm": [
                "PUSH DS / POP ES",
                "MUL BX",
                "LODSB",
                "SHL DI,1",
                "LOOP column_loop",
            ],
            "parent_state": "target-derived monolithic th04_main.asm disassembly",
            "classification": "upstream decompilation evidence, not independent historical source",
        },
        "magnet2010": {
            "documented_scope": "TH04 MAIN demo recording and EMS setup",
            "tagged_identifier_count": len(magnet_hits),
            "tagged_identifier_lines": magnet_hits,
            "final_blocker_file_hits": [],
            "demo_end_inline_asm_first_reconstruction_commit": DEMO_ASM_COMMIT,
            "conclusion": (
                "The independent MAGNet2010 leak does not witness checkerboard, "
                "carpet_lighting_put_new, snd_load, or the later ReC98 demo_end inline assembly."
            ),
        },
        "commit_metadata": commit_meta,
        "conclusion": (
            "Pinned upstream history supports an ASM reconstruction hypothesis for "
            "checkerboard/carpet, but supplies no independent historical source-origin "
            "evidence for the remaining 27 TH04 MAIN bytes. No exact promotion is authorized."
        ),
    }

    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "source_bundle_sha256": receipt["source_bundle_sha256"],
        "magnet_tagged_identifier_count": len(magnet_hits),
        "conclusion": receipt["conclusion"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
