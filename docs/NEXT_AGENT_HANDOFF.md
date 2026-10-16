# TH04 reconstruction and native handoff

Updated 2026-10-17. Both full development goals remain active. Continue one
bounded claim with current evidence; historical function acceptance is not
whole-game completion. Keep all new code/docs in English and use frequent
`gpt-6.1-sol: ...` commits and pushes.

## Published code baselines and working paths

| Purpose | Code baseline | Current location |
| --- | --- | --- |
| DOS reconstruction/tools | `main: 1d023b3` (later evidence commits follow) | This checkout |
| Native x64 | `port/modern-64: d22e190` (later evidence commits follow) | `.analysis/native/port64-recovery-v1445/` |
| Normal four-source DOS cohort | `product-20261016-065147-3427b48f` | `.analysis/build/dos-four-products-v1443/` |
| Current native cold programs/cache | 565/533075c0 | Native `.analysis/port64/clock-phase-v1455-final/{gnu,ubsan}` |

Do not use the older `.analysis/build/th04/` as the latest validated producer.
MAIN is 200279 bytes/SHA `778641ab845bcd67...`, with 1183 relocations. Its own MAP
is `.analysis/reconstruction/probes/product-20261016-065147-3427b48f-main/source/obj/main-native.map`
(SHA `42d7d2c7a93ee6d0...`). Pinned original MAIN is 156258 bytes/SHA
`077440a3c4e9ab52...`, 1136 relocations, header 6144, entry 0000:0000. Full pinned
identities and provenance are in `config/targets.toml`.

## Startup

Read `AGENTS.md`, [current state](RE_HANDOFF.md), [architecture](ARCHITECTURE.md),
[workflow](RE_WORKFLOW.md), [Oracle policy](ORACLES.md), [knowledge base](KNOWLEDGE_BASE.md)
and relevant local skills. Query `config/knowledge.csv` before experiments.
Target provenance remains `candidate-local-attested`, not pristine-dump proof.

```sh
git status --short
git ls-remote --heads origin main port/modern-64
git -C .analysis/native/port64-recovery-v1445 status --short
taskset -c 1 nice -n 19 python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/ghidra.py th04-main check
```

Use one low-priority CPU for heavy work, one Borland/Wine build writer, and muted
Linux headless/private TCP-disabled Xvfb launches. The user is using Windows:
no Windows GUI, focus changes or host-key injection. Emulator keyboard API
stimuli stay inside the recorded private emulator scenario.

## Original/reconstructed DOS Boss suffix (v1456)

The primary DOS comparison now reaches **9836 after-actor checkpoints**, with
loop samples I0..I9835 and 9835 complete update boundaries. Both independent
no-video and video pairs agree on configured scalar fields, all 5052 ordered RNG
calls (354 LCG/4698 ring), nine complete pools and 22 state blocks. The video
pair agrees on all 38 configured regions across all 9836 checkpoints: both
pages/all four graphics planes, full TRAM, palettes, modes and programmed GDC
fields. Each side's complete pool/state digests match its no-video control.

**Aggregate acceptance remains false:** no-video retains 302 post-reset input
differences, video retains 312, and complete raw GDC differs on all 9836 video
checkpoints. Across all four captures, complete initial/final CFG/SCR bytes agree; all ten
full 16-bit score checksums validate and real Continue changes decoded section 1.
The original and candidate use their own files/MAP/CS/DS. This is MAIN-only
replacement with original OP/MAINE/ZUN/assets, not a full four-product campaign.
Complete update 9836, Stage2 transitions, interior UI, physical timing, NP2,
Windows, pristine provenance and historical exactness remain open.

Native v1455 independently matches 9835 selected updates and all 59 full RGB/TRAM
samples in its recorded elapsed display fixture. GNU 87/83 CTests and optimized
UBSan 2 passed. The independent raw PIC model predicts all 9896 actual original
phase/count observations without a fitted phase; native receives frame/ns only.
Default logical mode retains three 407-pixel failures on that capture, while
v1454's two failures remain unchanged. This does not accept autonomous native
OP/loader/UI-interior/CPU timing or complete original/native campaigns.

The main evidence route is [the bounded differential note](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md).
Current private DOS report root is `.analysis/reconstruction/probes/dos-boss-extent-v1456/`;
use `result.json`, both state vectors, `video-regions.json`, `files.json`, controls,
producer/source closures and the final closure. The scalar report's legacy
`complete_updates=9836` counts loop samples: actor 9836 is a partial suffix,
not complete-loop acceptance. Native Stage2 update 9836 remains unaccepted.

## Next work

1. Observe the real suffix after actor 9836, stage/frame reset and STD rebind.
   Extend original/source DOS and native using each file's own MAP, CS/DS and
   explicit STD/Continue/post-Boss waits. Avoid guessing observer ordering or
   changing gameplay to match an unaligned checkpoint.
2. Locate actual input reset/IRQ/read ownership at the first post-reset mismatch
   (checkpoint 5/after update 4), retaining both 302/312 vectors. Raw GDC,
   elapsed/physical timing, every-frame RGB and native raw-plane identity remain
   separate requirements. Equal consumed input alone cannot waive these gates.
3. Continue complete four-product process/campaign and cross-emulator validation.
   Earlier v1443 nine-entry/first7547/second600 MAIN components are retained,
   together with OP confirmation/readiness and post-reset failures. Natural OP,
   full endings/routes, NP2, Windows and physical audio/input/rendering remain open.

Only edit product semantics for a reproduced difference or concrete ownership
requirement. Preserve source layout/ABI, canonicality gaps and historical exact
ledgers; do not reopen the two deferred MAIN exactness cases.

## Replay and retention

Use `scripts/probes/capture_th04_dos_boss_suffix.py` for the new second-dialogue
cue. The older capture/keyboard public paths are frozen backing inputs in old
recovery recipes; preserve them. `--source-snapshot` checks exact expected source
hashes and supports the first independently attributed original control without
restamping a receipt. All four captures and full replay sources remain distinct.

Sixteen owned capture image/font/raw aliases are archived in six blobs. Net
release is 157.621 MiB after archive, gzip and both journal files. The chain
verifies 24890 distinct protected hashes, including all 21663 parent
hashes and the two old public capture paths. New protected recipes use private
immutable copies. Actual archive restoration and fresh-output reducer replays
reproduce both failed state aggregates and the passing video regions before
SHA/mode/nsmtime verification and retirement of all sixteen aliases. No borrowed
files or duplicate cleanup credit. Use `replay_restored_v2.py --output-dir NEW`
for repeatable recovery; initial receipts, snapshots and replay remain unchanged.

```sh
python3 .analysis/reconstruction/probes/dos-boss-extent-v1456/replay_restored_v2.py \
  --output-dir .analysis/reconstruction/probes/NEW-suffix-recovery
```

Use fresh output names. The repeatable recovery restores only owned aliases,
runs the actual retained reducers, verifies SHA/mode/nsmtime and retires them.
For manual strict readers restore the exact required aliases with `recover.py`
and return them to archived state after verification; do not count them twice.
Frozen native v1455 has its own closed journal and recovery tools in its subject
note. Keep current GNU programs/cache, UBSan cores, sources and all compressed
original observations. Never substitute a new build into an old producer seal.

The historical `.analysis/worktrees/` directory is absent despite Git records.
Native v1432's 94 protected files and old v1437 candidate MAIN/MAP paths remain
missing. Old archives do not fully restore that tree. Do not repopulate missing
frozen paths, prune registrations to conceal loss, or count absence as cleanup.

## Build, verify and publish

Use a fresh namespace for any source build:

```sh
python3 scripts/build.py --output-dir .analysis/build/NEW-products
python3 scripts/ci.py
git diff --check
```

Run relevant focused comparisons before CI. Keep aggregate failures explicit.
Commit/push root and native separately when each changes, then verify both remote
heads and clean worktrees. Native push is `git push origin HEAD:port/modern-64`.
A source name, successful build, screen or native-host equality is not byte exact.
Only the full configured cold/raw/relocation Oracle set promotes exact state.

## Direct continuation instruction

Continue the active TH04 reconstruction/native goal from these current files.
Inspect worktrees and authoritative receipts first. Work on the actual Stage2
boundary or retained input mismatch, preserve the full goal and every failed
gate, use modest resources and periodic verified cleanup, and publish concrete
reviewable progress with updated focused evidence and concise handoffs.
