# Original DOS, reconstructed DOS and native fidelity

Updated 2026-10-10 for agent handoff. The user's primary requested comparison
is original Japanese TH04 DOS versus reconstructed TH04 DOS. Native x64 also
must preserve game state and effects. These are two differential surfaces;
neither native host agreement nor successful native clears establishes them.

## Starting state and current evidence

Root `main` owns the standalone DOS source. Native `port/modern-64` is a separate
worktree at `.analysis/worktrees/port-modern-64/`; commit and push it separately.
Read both current handoffs and inspect both Git statuses before taking ownership.
One writable reconstruction session at a time. No new game or compiler build
is started during this handoff. All known v1362/v1364 game trials are terminal.

Pinned originals are in `config/targets.toml`; every used file must pass
`scripts/preflight.py` identity, format and MZ checks. Their provenance remains
`candidate-local-attested`. The original MAIN SHA-256 is
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`;
the original HDI SHA-256 is
`0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd`.
Do not replace them with translation or patched package inputs. Ordinary
reconstructed DOS, invincible DOS, diagnostic instrumentation and native x64
are distinct candidates. Start parity work with the ordinary DOS candidate.

Existing original/native CPU probes cover bounded functions and guarded
services. Actual GNU native Reimu A Normal, Lunatic and Extra routes have
physical save/restart evidence; Turbo0 has scoped dense slowdown acceptance.
There is no accepted complete paired original-DOS/reconstructed-DOS gameplay
trace or complete original/native gameplay-pixel comparison yet.

Historical authored-function acceptance is OP93/93, MAIN493/495,
MAINE72/72, ZUN3/3 in the boundary inventory. MAIN's separate authored-function
ledger has494 rows; do not conflate its denominator with495 candidates. These
counts are not whole-file exactness. Carpet/checkerboard exact cases remain
deferred. Progress comes from the ledgers and `scripts/status.py`.

## First bounded comparison: bundled demos

TH04 already has four bundled `DEMO1..4.REC` members of the MAIN archive in the
HDI. Each contains4000 input bytes followed by4000 raw shift bytes. Existing
demo work identifies fixed playback and initialization; it is a useful starting
fixture rather than a reason to invent a new replay format first.

Read the native worktree's `docs/port64/evidence/demo.md`, `port64/verify_demo.py`
and `port64/verify_demo_join.py`. They document the original component Oracle's
adapters and the native integration boundary. Native integration executes full
demo callbacks; original component probes do not execute all original actors
or the complete DOS process teardown. Keep that limitation explicit.

The existing target-backed demo note records relative executable addresses:
OP0A74:0289..032D rotation; MAIN0AAF:08FE..0948 load;
MAIN0AAF:0949..0997 playback. Re-attest the database before using its address
observations. Record runtime load segment and candidate map independently;
do not assume original and reconstructed link addresses agree.

Important setup/boundary contracts from that existing note:

- Rotation1..4 selects stages3/0/2/1, characters Reimu/Marisa/Reimu/Marisa,
  shots A/A/B/B. Demo forces local Hard/Turbo without overwriting resident CFG.
- Highest-score loading uses the incoming process seed; demo reseeds318
  afterward, before the ring/drop/spark prefix consuming353 draws. Missing/bad
  score repair is a separate startup case because it consumes RNG.
- Observe gameplay-consumed input **after** DemoPlay, not only physical keys.
  A physical action can abort playback; shift alone is replaced by the replay.
- At frame3996 replay bytes are copied but gameplay does not update. Capture
  and validate this terminal decision separately rather than fabricating a
  final simulation row. Raw shift bytes must not be prematurely normalized.

## Capture and comparison contract to implement

Run original DOS and ordinary reconstructed DOS serially with the same
attested emulator/config/data/font, independent copies of identical starting
save/config files and the same fixture. Never reuse a mutated execution image
as the other run's reset state. Pin all four game products actually executed,
not only MAIN; retain executable/map/source and load-segment identity.

Choose one named logical boundary from the gameplay owner, then attest its
original instruction location and reconstructed producer location. Logical
calculations, rendering, waits, dialogue, process replacement and host refresh
are different clocks. Do not align using screenshots or elapsed wall time.
Capture input after replay/latching plus stage/frame, subpixel position,
score digits/pending delta/credit, graze, power, lives/Bombs, hit/respawn/
invincibility, enemy/item/bullet/shot/Boss state and RNG state.

TH04 RNG is not TH08's RNG layout. Preserve the process-local32-bit LCG and
the shared256-byte ring with its word cursor and low-byte-only advance.
`src/main/math/randring_state.asm` documents the cursor255 overlapping-word
case; `src/main/math/randring_fill.cpp` fills backward. A modulo cursor alone
cannot detect an extra full ring wrap. An external observation count and
caller log are needed if claiming identical RNG consumption. Derive widths,
units and wrapping from TH04 owners/evidence. Do not import TH08 addresses.

Compare semantic state first, then inspect the first divergence with nearby
frames, callers and actor-pool dumps. Separately compare original/rebuilt DOS
VRAM planes, palette, page/scroll state and deterministic visual effects at
equivalent presentation boundaries. For x64 compare the corresponding logical
frame and renderer output through the existing planar/palette conversions.
Muted PMD/MMD state or register writes can be compared without an audio device.

Acceptance must reject missing/duplicate/out-of-order rows, skipped stages,
different consumed input, mismatched initial assets/config/saves, truncated
equal prefixes, timeout and incorrect terminal input consumption. Prefix
diagnostics are useful but never a complete parity pass. Retain compact trace
fingerprints and first-difference context; compress only after complete
readback. Validate any accelerated/no-rasterization observer against ordinary
timing before using it to accept gameplay or effects.

The existing native `host_window::Snapshot` / `window.tsv` has score, lifecycle,
input and timing fields but lacks process RNG state/ring/call counts. It also
reports host refresh snapshots rather than a proved shared original-DOS
calculation boundary. Extend observations deliberately; do not label the
88k-row native route logs as original replay parity.

## Reuse and negative results

Read-only TH08 reference:
`/home/pentester/coding/codex_ida/th08-reconstruction/th08/`.
Its `docs/REPLAY_TESTING.md`, `scripts/compare-replay-traces.py`,
`scripts/test-replay-suite.py` and `scripts/replay-external-observer.py` show
complete-capture guards, canonical schema/row hashing, gameplay input sampling,
relative RNG generations and first-difference context. Its current worktree is
dirty and owned by ongoing work: do not edit/build/run it or change its database.
This is cross-game workflow corroboration, not TH04 parity evidence.

TH04 emulator-side precedent is
`scripts/probes/build_th04_cpu_fault_emulator.py` plus
`th04_emulator_fault_observer.inl`: pinned private DOSBox-X with no guest writes.
It observes CPU exceptions only; it does not implement frame replay capture.
`scripts/probes/inspect_th04_play_trace.py` reduces instrumented reconstructed
DOS48-byte records. It lacks RNG and a complete original counterpart; it is not
a ready full parity runner. Prefer attested read-only emulator observation over
patching original game bytes. Cross-emulator validation remains open.

Retain the failed UBSan all-clear and v1360 Turbo0 receipts. Mask0x19 is
unplayed; bit0 alone is an invalid clear gate. The first v1364 late-Bomb probe
failed its cleanup assumption: actual native host Escape exits MAIN directly.
The reconstructed DOS gameplay source instead routes INPUT_CANCEL through
`pause()`. This is a concrete input/process surface to investigate, not a new
verified original-runtime mismatch. Do not change it during the handoff.

## Operating constraints and first commands

The user is actively using Windows: no host GUI launch, foreground activation,
host-key injection or hidden/offscreen workaround. Every launch stays muted;
never open a physical audio backend/device. Use SDL dummy headless checks or
attested private TCP-disabled Linux Xvfb for any required window/input run.
Preserve user game packages, original images, fonts, compiler installations,
receipts and saves. Clean owned regenerated outputs periodically; no blanket
`.analysis/` deletion. Recovery is indexed in `docs/ANALYSIS_RETENTION.md`.

```sh
git status --short
git -C .analysis/worktrees/port-modern-64 status --short
python3 scripts/preflight.py
python3 scripts/status.py
# Before using raw database observations:
python3 scripts/ghidra.py th04-main check
# End each coherent batch:
python3 scripts/ci.py
git diff --check
```

The first next-agent implementation should be one paired bounded demo capture
and a fail-closed first-divergence comparator. Then expand to all four demos,
ordinary movement/Shot/Bomb/hit/death/Continue and complete routes. Commit/push
root and native changes separately with `gpt-6.1-sol: ...` English messages.
