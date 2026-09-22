#!/usr/bin/env python3
"""Audit every pinned TH04 commit that changes [MAGNet2010] provenance tags."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC98 = ROOT / "_reference" / "ReC98"
PRIVATE = (ROOT / ".analysis").resolve()
PINNED = "b6ba5b0a529edbb31efdf8c0e939263804f8ee47"
HISTORY = [
    "37fb6eba32e769df2b0db7d0b4d7efc01343113d",
    "61a2df2d71bd2f2dacce260db28d2101115b7709",
    "a6a805f008cb2ca3bae72dabdfad133627e461ac",
    "3c27fbc3bd3bda310bf5491e2d6a819de118dd11",
    "ccca7bf6ee9607bc31f2e1226399b578c6e2d571",
    "fe33d49e0a4e2e0f349de10d587387aa7d392a1f",
    "3e99a30c17443bcad0d9c806f4812b918325f935",
    "e1f3f9fe0b783e0bbbe1dd79625d6ec7469e34b7",
    "c99c1bc3310f8594d682a6193c0279dd11cb36ff",
]
PATHS = {
    HISTORY[0]: ["th04/demo.h", "th04/mem.h", "th04/mem.inc"],
    HISTORY[1]: ["th04/ems.h", "th04/ems[bss].asm", "th04/mem.h", "th04/mem.inc"],
    HISTORY[2]: ["th04/hardware/input[bss].asm"],
    HISTORY[3]: ["th04/hardware/inputvar.h"],
    HISTORY[4]: ["th04/main/ems.hpp", "th04/mem.h"],
    HISTORY[5]: ["th04/main/ems.cpp", "th04/mem.inc"],
    HISTORY[6]: ["th04/main/ems.cpp"],
    HISTORY[7]: ["th04/hardware/inputvar.h", "th04/main/demo.cpp", "th04/main/demo.hpp"],
    HISTORY[8]: ["th04/main/demo.hpp"],
}
BLOCKERS = ("checkerb", "checkerboard", "carpet", "stages", "snd/load", "snd_load")

def git(*args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(REC98), *args], check=True, capture_output=True
    ).stdout

def text(*args: str) -> str:
    return git(*args).decode("utf-8", errors="replace")

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def make_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction" / "probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="v496-magnet-history-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    out.mkdir(parents=True)
    return out

def tagged_delta(commit: str) -> tuple[dict[str, list[str]], bytes]:
    patch = git("show", "--format=", "--unified=0", commit, "--", "th04")
    path = None
    hits: dict[str, list[str]] = {}
    for line in patch.decode("utf-8", errors="replace").splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
        elif (
            path
            and line.startswith(("+", "-"))
            and not line.startswith(("+++", "---"))
            and "[MAGNet2010]" in line
        ):
            hits.setdefault(path, []).append(line)
    return hits, patch

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    out = make_output(args.output_dir)

    if text("rev-parse", "HEAD").strip() != PINNED:
        raise ValueError("pinned ReC98 HEAD drift")
    history = text(
        "log", "--reverse", "--format=%H", "-S[MAGNet2010]", "--", "th04"
    ).splitlines()
    if history != HISTORY:
        raise ValueError(f"MAGNet2010 history drift: {history}")

    records = []
    all_paths: set[str] = set()
    bundle = bytearray()
    for commit in history:
        hits, patch = tagged_delta(commit)
        paths = list(hits)
        if paths != PATHS[commit]:
            raise ValueError(f"tag-bearing path drift for {commit}: {paths}")
        bad = [p for p in paths if any(t in p.lower() for t in BLOCKERS)]
        if bad:
            raise ValueError(f"final-blocker tag path in {commit}: {bad}")
        added = sum(x.startswith("+") for xs in hits.values() for x in xs)
        removed = sum(x.startswith("-") for xs in hits.values() for x in xs)
        meta = text("show", "-s", "--format=%aI%n%s", commit).splitlines()
        records.append({
            "commit": commit,
            "date": meta[0],
            "subject": meta[1],
            "tag_paths": paths,
            "tag_lines_added": added,
            "tag_lines_removed": removed,
            "patch_sha256": sha(patch),
            "role": "initial transcription" if commit in HISTORY[:3] else "later migration",
        })
        all_paths.update(paths)
        bundle.extend(patch)

    tags = text("grep", "-n", "-F", "[MAGNet2010]", PINNED, "--", "th04").splitlines()
    if len(tags) != 13:
        raise ValueError(f"current tag count drift: {len(tags)}")
    current_bad = [line for line in tags if any(t in line.lower() for t in BLOCKERS)]
    if current_bad:
        raise ValueError(f"current final-blocker tag hit: {current_bad}")
    bundle.extend("\n".join(tags).encode())

    receipt = {
        "schema_version": 2,
        "claim_scope": "complete pinned ReC98 TH04 MAGNet2010 transcription lineage",
        "pinned_rec98_commit": PINNED,
        "history": records,
        "initial_transcription_commits": HISTORY[:3],
        "all_tag_bearing_paths": sorted(all_paths),
        "current_tag_count": len(tags),
        "current_tag_lines": tags,
        "current_final_blocker_tag_hits": current_bad,
        "source_bundle_sha256": sha(bytes(bundle)),
        "conclusion": (
            "All nine pinned commits that change TH04 [MAGNet2010] tag counts keep "
            "their tag-bearing hunks in demo, input, EMS, or memory files. The three "
            "initial 2019 transcription commits cover demo/memory, EMS/memory, and "
            "key_det/shiftkey. No historical or current tag-bearing path reaches "
            "checkerboard, carpet/stages, or snd_load."
        ),
        "limit": "Upstream transcription provenance only; not an exactness Oracle.",
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "source_bundle_sha256": receipt["source_bundle_sha256"],
        "history_commit_count": len(history),
        "tag_bearing_path_count": len(all_paths),
        "conclusion": receipt["conclusion"],
    }, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
