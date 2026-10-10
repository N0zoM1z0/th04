# Original DOS, reconstructed DOS and native fidelity

Updated 2026-10-11 for agent handoff. The user's primary requested comparison
is original Japanese TH04 DOS versus reconstructed TH04 DOS. Native x64 also
must preserve game state and effects. These are two differential surfaces;
neither native host agreement nor successful native clears establishes them.

## Starting state and current evidence

Root `main` owns the standalone DOS source. Native `port/modern-64` is a separate
worktree at `.analysis/worktrees/port-modern-64/`; commit and push it separately.
Read both current handoffs and inspect both Git statuses before taking ownership.
One writable reconstruction session at a time. All known v1362/v1364 native
game trials are terminal. The DOS demo observer is a separate, muted replay
surface; it does not revive those native jobs.

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
The v1366 paired DOS demos cover complete consumed-input/score/RNG extents:
all four pass after restoring Stage4 midboss's initialized toggle. The v1365
Demo1 failure remains retained. Full actor/presentation/process parity and complete
original/native gameplay-pixel comparison remain open.

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

## Capture and comparison contract

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

### Checked-in DOS demo capture

`build_th04_demo_emulator.py` builds the pinned DOSBox-X source with a
normal-core observer. Its host-RAM reads walk VM86 page tables without using
guest memory accessors or setting page-table accessed bits. It changes no game
bytes, registers, input, guest clock or drawing. Builds use one job, nice15,
one CPU, a50% CPU duty budget and1GiB address-space limit. Captures run serially
with nice15, one CPU and512MiB address-space limit, SDL dummy and mixer disabled.

`capture_th04_dos_demos.py` starts GAME.BAT from a new pinned-data image, lets
OP naturally rotate through the four demos and records the actual MAIN load.
The independent reader compares each entire initial load module with the
MZ loader's relocated bytes, retaining load segment, CR0 and CR3. Candidate
DGROUP, field addresses and helper locations come from that product's
hash-attested MAP. Both products' replay seams and six ring cursor increments
are guarded against their own executable instructions.

The update boundary is original MAIN0AAF:00B7 / normal candidate0708:066D,
after the input callback returns. The terminal-condition boundary is original
0AAF:0975 / candidate0708:0091, after both replay writes and before the
`stage_frame <3996` comparison. The final capture stops there; it does not
accept the final fade, DOS teardown, save or fresh-OP transition. Intermediate
demos continue through the ordinary handoff to get the next demo.

Rows retain consumed input, raw shift, frame/stage, eight score digits, both
pending score counters, LCG, all256 ring bytes, the full word cursor, player
position/power/hit/invincibility/respawn and resident stock/credit/miss/Bomb
counts. IRAND and all six ring-accessor entries have an external caller log;
both process-total and relative-since-first-boundary counts, helper sequence
and mask/divisor arguments are compared.
This catches an extra full ring wrap even when the word cursor agrees.
Actor-pool and graze snapshots now diagnose Demo1's failure. Complete actor
traces, VRAM/palette, sound-state and native x64 comparisons remain separate work.

```sh
python3 scripts/probes/build_th04_demo_emulator.py \
  --archive .analysis/runtime/emulators/dosbox-x-199aa35f.tar.gz \
  --output-dir .analysis/runtime/emulators/NEW
python3 scripts/probes/capture_th04_dos_demos.py --original \
  --emulator-receipt .analysis/runtime/emulators/NEW/receipt.json \
  --font-bmp PRIVATE-FREECG98.BMP \
  --output-dir .analysis/runtime/candidates/NEW-original
python3 scripts/probes/capture_th04_dos_demos.py \
  --build-dir .analysis/build/th04-normal --map ATTESTED-MAIN-MAP \
  --emulator-receipt .analysis/runtime/emulators/NEW/receipt.json \
  --font-bmp PRIVATE-FREECG98.BMP \
  --output-dir .analysis/runtime/candidates/NEW-candidate
python3 scripts/probes/compare_th04_dos_demos.py \
  --original .analysis/runtime/candidates/NEW-original \
  --candidate .analysis/runtime/candidates/NEW-candidate \
  --output .analysis/runtime/candidates/NEW-comparison.json
```

The comparator independently reads the initial products/config/save, loaded
MAIN and complete trace. Each demo must contain exactly3996 update boundaries
plus its terminal condition at3996, with the expected rotation/stage/character/
shot and every consumed input/shift byte. Timeout, equal truncated prefixes,
duplicate/missing/out-of-order rows, inconsistent caller counts, changed reset
files and wrong terminal consumption fail closed. It reports all four per-demo
verdicts and nearby rows at the first difference. Public synthetic controls
exercise these rejection paths without committing original assets.

### v1365 complete captures and failed Demo1 frontier

The pinned private emulator is
`.analysis/runtime/emulators/demo-observer-build-v1365/receipt.json`, binary
SHA-256 `6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1`.
The ordinary candidate is `.analysis/build/th04-normal/`, MAIN SHA-256
`cb4c5b667f9a2d5a5c3ef62865fdc926a74a100155068c63e5dfbd019362b70c`.
Its historical MAP was recovered alone from the retained product archive;
`.analysis/runtime/emulators/demo-observer-v1365/main-native.map` matches the
producer receipt's SHA-256
`3f8b2393a1bc34fe1ba0d9bed47860ba30d371a23a2953d8cb9026d12fe79942`.
No product rebuild or product-source edit occurs in this batch.
This claim belongs to those executed product hashes. The later semantic-source
clarification commits are not a new runtime producer; establish the archived
producer/current-source bridge before implementing a repair or claiming a
current cold build. Retain the first consumer snapshot and the seven current
probe/test sources under `demo-observer-v1365/consumer-source-v2/`; do not
restamp old receipts with its manifest hash.

Original and candidate receipts are respectively
`.analysis/runtime/candidates/dos-demo-v1365-original/receipt.json` and
`dos-demo-v1365-candidate/receipt.json` under the same directory. Both complete
all four demos, totaling15,984 update boundaries and four terminal conditions
per side. Loaded MAIN bytes/relocations, independent reset/asset readback and
every recorded consumed input/raw-shift byte pass. All four MAIN loads are10FC;
original DGROUP3230, candidate DGROUP34F7. Final independent comparison:
`.analysis/runtime/candidates/dos-demo-v1365-comparison-v3.json`, SHA-256
`c96307526298c4763d5d15e73e67550b2206222605e231a733efe735c31c537c`.
The comparator exits1 because the behavioral claim fails, not because a capture
is truncated or invalid.

| Demo | Sampled boundaries | Result |
| --- | --- | --- |
| 1 |3997 complete;3343 equal preceding rows | First input/score/RNG-schema difference at3343 |
| 2 |3997 | Pass |
| 3 |3997 | Pass |
| 4 |3997 | Pass |

At Demo1/frame3343, original/candidate score digits are
`0008060600050200` / `0000080600050200`, pending delta65/453, pending per-frame
step2/14, ring cursor0086/0088 and total ring calls3206/3208. LCG, consumed
input/raw shift, sampled player position/lifecycle and resident stock agree
there. The candidate's two extra calls are `randring2_next16_and(31)` at
MAIN156A:02E5, return156A:03E6 inside `sparks_add_random`. Helper kinds and
mask/divisor sequences also agree at preceding captured boundaries.

`--snapshot-frames 3341 3342 3343` adds a read-only GDB hardware watch on the
guest stage-frame word in host RAM. It dumps DGROUP at the stage_frame write,
after actors but before modulo counters and score update; this is **earlier**
than the next before-update I row. The inferior remains single-CPU/nice15 with
512MiB address-space limit; GDB needs1536MiB virtual address allowance, with
observed RSS about90MiB. The first512MiB GDB attempt failed at host startup;
its log/receipt remain in `dos-demo-v1365-original-watch/`. Subsequent diagnostic
receipts explicitly keep `capture_complete=false`. An early stop never enters
the complete-demo acceptance path. GDB stops can alter wall timing; these are
scoped diagnostic observations, with their entire raw input/RNG prefix checked
against the ordinary complete capture.

`inspect_th04_demo_snapshots.py` independently verifies the full parent capture,
diagnostic prefix, pins, frame/load/DGROUP identity and snapshot files. Original
pool ownership is MAIN DGROUP:5A22 (440 records of26 bytes), graze DGROUP:BCBC;
candidate MAP gives DGROUP:4972 and79E7. This routing reuses the target-backed
native bullet/enemy CPU Oracle offsets, not a native parity claim.
`dos-demo-v1365-actor-watch.json` verifies all six dumps at3341..3343: both have
graze59 at3341/3342, then original59/candidate60 at3343. Forty-eight live bullets
already differ at3341, including angles, velocities and positions. Thus3343 is
the first sampled score/RNG difference, not the first actor-state difference.

`dos-demo-v1365-actor-spawn.json` verifies an additional paired set at3330..3332.
At the stage_frame3331 write (after update3330), newly spawned slots392..415
have age0 and equal origins, but group angles5A/46 versus61/3F and different
velocities. Older slots416..439 already differ at3330. Route the next bounded
investigation through enemy script/template generation and bullet angle
production; this ownership hypothesis is **inferred**, and the responsible
instruction/source defect and earliest actor divergence remain unproved.
Do not patch graze/scoring or overwrite these failed receipts to make the four
demo claim pass. No exact state is promoted. Snapshot replay uses the capture
commands above plus `--demos 1 --snapshot-frames ...`; readback example:

```sh
python3 scripts/probes/inspect_th04_demo_snapshots.py \
  --original .analysis/runtime/candidates/dos-demo-v1365-original-spawn \
  --candidate .analysis/runtime/candidates/dos-demo-v1365-candidate-spawn \
  --original-full .analysis/runtime/candidates/dos-demo-v1365-original \
  --candidate-full .analysis/runtime/candidates/dos-demo-v1365-candidate \
  --map .analysis/runtime/emulators/demo-observer-v1365/main-native.map \
  --frames 3330 3331 3332 --output PRIVATE-NEW-READBACK.json
```

The16 public comparator controls and root CI pass, including live Ghidra target
attestation and mutation controls. Final CI uses one CPU, nice15, a50% duty
budget and512MiB Java heap. Owned emulator objects/archives, failed host-startup
generated copies and source-backed Python caches retire1,043 files and
866,148,352 allocated B before retained journal overhead; independent readbacks
verify absent paths and protected inputs. Debug stripping additionally reduces
the private ELF by134,207,784 bytes. Cleanup never retires complete captures,
actor dumps, failed logs/receipts, maps, source snapshots or original inputs.

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

### v1366 Stage4 midboss stack initialization

Target-observed MAIN DGROUP(2134):185E is initialized DATA with value1.
The bounded stack helper MAIN13FF:1037..112D (file16827..1691D)
increments this byte at offset1072, then tests bit0 at1093. These segment
offsets include the group's10h alignment seam; file addresses are authoritative.
The existing v149 exact scaffold aliases `byte_22B9E db 1` to the same symbol.
Its exact C++ helper does not own the standalone state declaration.

The ordinary v1365 candidate declares `_midboss4_aim_toggle` as BSS in
`src/main/midboss/state.asm`. Both that declaration and `m4_update.cpp` have
byte-identical source hashes to their archived20261003 producer records:
`e88b5f12a9d30154fd839e33ebf432d7a7faa180a635cd807925768447b06fb6` and
`1319d8397de0af2cb9c34c12f2b683e7225d8cc3b8c7b829d6a98f10368e4c0c`.
The independent static state checker rejects that old MAP's BSS ownership.

The extended snapshot reader observes original/candidate toggles2/1 at3330,
3331 and3332, with equal midboss phase frames40/41/42. The template angles are
4E/3F at3330 and46/3F at3331..3332. Pattern-stack increments the toggle before
choosing its fixed or aimed branch. Original and candidate IATAN2 instruction
shapes and all256 table bytes agree in this bounded diagnostic. The wrong
standalone initializer explains the branch reversal; full post-fix replay is
the independent causal gate.

The fresh ordinary MAIN cold build uses193 C++ roots,155 ASM,8 state and4
sprite producers with zero reused C++ roots and no compile/assemble/link
failures. IRQ/vector and bullet-dispatch audits pass. MAIN remains199,455 bytes,
SHA-256 `161325264e9e6dd4eb65c6718120c283ce000803c06250326c2d61f246c7c5ab`;
MAP SHA-256 `2ee564c3e935869a9b94002ca05b30e2337c695a787a2aa6bada83bc03a61b36`.
Static readback confirms initialized DATA at candidate DGROUP(23FB):1060
contains1. Its cold receipt is
`.analysis/reconstruction/probes/product-20261010-160320-2282c931-main/receipt.json`.
Only MAIN is rebuilt; the independent ordinary package
`.analysis/build/th04-demo-angle-v1366/` explicitly retains the old unchanged
OP/MAINE/ZUN producer identities. The old ordinary/invincible and Windows
packages remain available. Freeze runtime consumers separately from the cold
producer's conservative all-probe fingerprint; diagnostic-script additions do
not restamp the producer. Final consumers are archived in
`demo-angle-v1366/consumer-source/`.

Complete candidate capture `dos-demo-v1366-candidate/receipt.json` and independent
`dos-demo-v1366-comparison.json` live under `.analysis/runtime/candidates/`.
Comparison against the retained complete v1365 original passes all four demos,
each3996 updates plus terminal3996:15,984 gameplay rows and4 terminal rows.
Consumed input/raw shift, score/pending counters, process LCG, all ring bytes,
cursor, helper counts/kinds/masks/divisors and sampled player/resident state
agree at all15,988 boundaries. This accepts that recorded schema and reset,
not whole actor pools, presentation, process teardown, cross-emulator or x64
parity. The failed v1365 comparison remains independently addressable.

The fix moves only this byte to `_DATA db 1` and adds `_DATA` to this owner's
DGROUP declaration. The historical exact replay continues to use its own
initialized scaffold; no accepted exact extent includes this standalone ASM
owner. The native x64 `midboss4::State` already starts `aim_toggle=1`; this
does not establish full native parity or require a native source change.

Private static/bridge/readback receipts are in
`.analysis/reconstruction/probes/demo-angle-v1366/`. The fresh original GDB
capture at3282/3299/3315/3331 retains a byte-identical prefix of the complete
v1365 ordinary original trace. It observes toggle1 through the preceding pattern
and toggle2 at the first stack spawn3315. The diagnostic still cannot accept
complete gameplay or effect parity.

The paired v1366 diagnostic at the same four stage-frame writes passes full
440*26-byte bullet-pool comparison, with zero differences at every snapshot.
Midboss toggle1/1/2/2, phase frames65/9/25/41, template angles00/00/4E/46 and
graze59 match. Original/candidate pools are DGROUP5A22/4974, with grazeBCBC/79E9.
`dos-demo-v1366-stack-readback.json` independently validates both diagnostic
prefixes against their complete parents and every dump hash. This specifically
removes the old3315-spawn/3331-angle frontier; earliest unrelated actor differences
and unsampled effects remain open.

Final CI passes337 public tests, private target/calibration checks and live
Ghidra attestation/mutation controls; `git diff --check` passes. The new static
state Oracle has five synthetic mutation controls, including rejection of BSS
even when the backing file contains1. Historical exact states remain unchanged.
Terminal immutable-capture deduplication plus514 public Python-cache retirements
reclaim141,602,816 allocated B before journal overhead; independent final
readback preserves source/products/inputs/full traces/dumps. The new11MiB cold
product cache stays usable. No native worktree write or Windows GUI/audio test
occurs in this batch.

```sh
python3 scripts/probes/check_th04_midboss4_initial_state.py \
  --build-dir .analysis/build/th04-demo-angle-v1366 \
  --map .analysis/reconstruction/probes/product-20261010-160320-2282c931-main/source/obj/main-native.map \
  --output PRIVATE-NEW-STATIC.json
python3 scripts/probes/inspect_th04_demo_snapshots.py \
  --original .analysis/runtime/candidates/dos-demo-v1366-original-stack \
  --candidate .analysis/runtime/candidates/dos-demo-v1366-candidate-stack \
  --original-full .analysis/runtime/candidates/dos-demo-v1365-original \
  --candidate-full .analysis/runtime/candidates/dos-demo-v1366-candidate \
  --map .analysis/reconstruction/probes/product-20261010-160320-2282c931-main/source/obj/main-native.map \
  --frames 3282 3299 3315 3331 --output PRIVATE-NEW-STACK.json
```

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

The Demo1 score/RNG failure is repaired by the Stage4 initialized-state owner.
Next expand complete actor/effect observations at proved shared boundaries, and ordinary
movement/Shot/Bomb/hit/death/Continue and complete routes. Commit/push
root and native changes separately with `gpt-6.1-sol: ...` English messages.
