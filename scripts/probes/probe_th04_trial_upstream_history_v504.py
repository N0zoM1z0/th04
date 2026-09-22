#!/usr/bin/env python3
"""Audit pinned ReC98 mainline history for TH04 trial/prototype provenance."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
REC98 = ROOT / "_reference" / "ReC98"
PINNED = "b6ba5b0a529edbb31efdf8c0e939263804f8ee47"
TERMS = ("GEN_TS1", "gen_ts1", "東方幻想郷　体験版", "体験版", "taiken", "trial")

def git(*args: str) -> bytes:
    return subprocess.run(["git", "-C", str(REC98), *args], check=True, capture_output=True).stdout

def text(*args: str) -> str:
    return git(*args).decode("utf-8", errors="replace")

def grep_text(*args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(REC98), *args],
        capture_output=True,
    )
    if done.returncode not in (0, 1):
        raise subprocess.CalledProcessError(
            done.returncode, done.args, output=done.stdout, stderr=done.stderr
        )
    return done.stdout.decode("utf-8", errors="replace")

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def make_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="v504-trial-upstream-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    out.mkdir(parents=True)
    return out

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    out = make_output(args.output_dir)
    if text("rev-parse", "HEAD").strip() != PINNED:
        raise ValueError("pinned ReC98 HEAD drift")

    tree_hits = {}
    history_hits = {}
    bundle = bytearray()
    for term in TERMS:
        tree = grep_text("grep", "-n", "-i", "-F", term, PINNED, "--", "th04").splitlines()
        history = text("log", PINNED, "--format=%H %aI %s", f"-S{term}", "--", "th04").splitlines()
        tree_hits[term] = tree
        history_hits[term] = history
        bundle.extend(term.encode("utf-8") + b"\0")
        bundle.extend("\n".join(tree).encode("utf-8") + b"\0")
        bundle.extend("\n".join(history).encode("utf-8") + b"\0")

    nonempty_tree = {k:v for k,v in tree_hits.items() if v}
    nonempty_history = {k:v for k,v in history_hits.items() if v}
    if nonempty_tree or nonempty_history:
        raise ValueError(f"unexpected trial marker: tree={nonempty_tree} history={nonempty_history}")

    receipt = {
        "schema_version": 1,
        "claim_scope": "pinned ReC98 mainline TH04 trial/prototype provenance search",
        "pinned_rec98_commit": PINNED,
        "mainline_commit_count": int(text("rev-list", "--count", PINNED).strip()),
        "root_commits": text("rev-list", "--max-parents=0", PINNED).splitlines(),
        "terms": list(TERMS),
        "current_tree_hits": tree_hits,
        "pickaxe_history_hits": history_hits,
        "search_bundle_sha256": sha(bytes(bundle)),
        "conclusion": (
            "Pinned ReC98 mainline has no current TH04 hit and no historical content-change "
            "hit for GEN_TS1, Japanese trial markers, taiken, or trial. It supplies no hidden "
            "TH04 trial producer or trial-derived source provenance for the final blockers."
        ),
        "limit": (
            "Only history reachable from pinned ReC98 HEAD is audited. External archives, "
            "deleted refs, and the actual 1998 public trial binary are outside scope. "
            "No source or exactness credit is granted."
        ),
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "mainline_commit_count": receipt["mainline_commit_count"],
        "tree_hit_count": sum(len(v) for v in tree_hits.values()),
        "history_hit_count": sum(len(v) for v in history_hits.values()),
        "search_bundle_sha256": receipt["search_bundle_sha256"],
    }, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
