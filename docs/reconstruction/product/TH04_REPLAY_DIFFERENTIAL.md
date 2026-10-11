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
agree at all 15,988 boundaries. This accepts that recorded schema and reset,
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

### v1367 complete DGROUP stream and pool ownership

Final CI passes377 tests and live target/Ghidra mutation controls. Forty new
observer/reader controls include explicit short mapped-page rejection and a
per-demo verdict that rejects any of the nine pool differences. Final independent
reader source is frozen in `demo-dgroup-v1367/final-reader-source/`; executed
producer v2/v3 sources and earlier failed results stay separate. Final retention
reclaims140,111,872 allocated B before journals, preserving all evidence and the
reusable product cache. Native worktree remains clean and unchanged.

The added read-only GDB hardware watch records all65536 DGROUP bytes at every
stage_frame write1..3996, continuing through the unchanged observer's natural
terminal3996 decision and all four MAIN processes. This seam follows actor
updates, rendering, input_reset_sense, page flip and sound update, but precedes
modulo counters and score_update_and_render. It is distinct from the ordinary
before-update consumed-input rows. Every complete scalar/caller trace must
remain byte-identical to its independent ordinary parent.

Original capture `dos-demo-v1367-original-dgroup-v2/` completes in382.33s;
independent readback validates all15984 records, complete ordinary trace,
producer/source/file identities, process/load/CPU addresses and page mappings.
Original producer helpers are frozen in `demo-dgroup-v1367/consumer-source-v2/`;
the candidate uses v3. GDB reads conventional host RAM through its own page walk,
without guest memory accessors, guest writes, input injection or raster skipping.
Each run uses one CPU/nice15, dummy SDL, muted mixer,512MiB inferior and1536MiB
GDB virtual-address limits. No compiler or emulator rebuild is required.

Target-observed stage_state_init CIRCLE_TEXT(0AAF):73DB..74A5, file136CB..13795,
SHA-256 `f41ff21e…`, issues nine clear_dwords calls. The reader attests each
actual destination/count/callee in both original and the candidate's linked
owner against its MAP, then compares the entire raw extent, including inactive
slots, unused bytes and ES-relative enemy script offsets. No pointer masking
or copied target bytes enter product code.

| Pool | Count x stride | Original DGROUP offset | v1366 candidate DGROUP offset |
| --- | --- | --- | --- |
| shots | 68 x18 | B55E | 8E31 |
| enemies | 32 x64 | 8A92 | 7B04 |
| sparks | 96 x16 | 53E2 | B31A |
| bullets | 440 x26 | 5A22 | 4974 |
| custom_entities | 32 x26 | B204 | 453C |
| circles | 16 x10 | 9594 | 7A54 |
| items | 32 x20 | AF34 | 8885 |
| pointnums | 400 x16 | 9634 | 9548 |
| gather_circles | 16 x42 | 9292 | 854E |

Final candidate capture completes in349.18s. Independent
`dos-demo-v1367-dgroup-comparison-final.json` passes every3996 updates in each of the
four demos: all24952 bytes in the nine pools, graze and post-reset input/Shift
agree without normalization. Each side's complete ordinary scalar/caller trace
is byte-identical to its ordinary parent; the paired scalar reader also passes
all15988 before-update/terminal input/score/RNG boundaries. Each DG2 stream retains3996 x65536 bytes (261,881,856 B) of raw
data plus headers. Compressed stream identities are retained in the receipts. No game source/native worktree or historical exact state
changes in this batch.

Two observer controls remain negative evidence. v1 wrongly treats the warm
MAIN BSS byte clear3996 ->3840 ->0 as a frame increment; its Demo1 full stream
and failed Demo2 startup remain retained. FrameSequence now waits for zero
before requiring all consecutive increments. Separately, the first reader
wrongly equates post-reset input with the REC byte: original consumed frame160
has20h, while stage_frame161 has0000h. The current decoder preserves these
post-reset bytes and compares them with the candidate; the unchanged ordinary
observer still checks every consumed REC/Shift byte. These are observer/reader
contract corrections, not demonstrated product failures.

DG1 stores raw64KiB blocks; DG2 stores a reversible XOR with the preceding
full block before gzip. A separate byte-wise fixture encoder verifies full
reconstruction; truncated/equal prefixes, missing/duplicate/order errors,
wrong process/load/CPU/frame/stage, changed consumer/file identities, incomplete
ordinary controls and illegal page mappings are rejected. Full DGROUP evidence
remains available for later boss/player/global state owners. Pool equality alone
does not accept those owners, VRAM/palette, process teardown, x64 fidelity,
cross-emulator behavior or historical exactness.

```sh
python3 scripts/probes/capture_th04_dos_demos.py --original \
  --emulator-receipt .analysis/runtime/emulators/demo-observer-build-v1365/receipt.json \
  --font-bmp .analysis/runtime/candidates/dos-demo-v1365-original/FREECG98.BMP \
  --demos 4 --timeout 1200 --dgroup-stream --output-dir PRIVATE-NEW-ORIGINAL
# Candidate: replace --original with --build-dir and --map from the v1366 recipe.
python3 scripts/probes/compare_th04_demo_dgroup.py \
  --original .analysis/runtime/candidates/dos-demo-v1367-original-dgroup-v2 \
  --candidate .analysis/runtime/candidates/dos-demo-v1367-candidate-dgroup-v3 \
  --original-full .analysis/runtime/candidates/dos-demo-v1365-original \
  --candidate-full .analysis/runtime/candidates/dos-demo-v1366-candidate \
  --original-consumer .analysis/reconstruction/probes/demo-dgroup-v1367/consumer-source-v2/scripts/probes \
  --candidate-consumer .analysis/reconstruction/probes/demo-dgroup-v1367/consumer-source-v3/scripts/probes \
  --map .analysis/reconstruction/probes/product-20261010-160320-2282c931-main/source/obj/main-native.map \
  --output PRIVATE-NEW-POOL-COMPARISON.json
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
Next expand remaining global/presentation/process observations at proved shared boundaries, and ordinary
movement/Shot/Bomb/hit/death/Continue and complete routes. Commit/push
root and native changes separately with `gpt-6.1-sol: ...` English messages.

### v1368 pointer-free global state and coverage

Reuse the immutable v1367 streams and their independent ordinary controls;
no new game launch, product build or bulky capture is needed. Add
`--global-states` to the complete v1367 comparison command, with a fresh
`--output` path. The final receipt is
`.analysis/runtime/candidates/dos-demo-v1368-globals-comparison-final.json`.
It passes all four demos,3996 updates each, including the previous nine pools,
graze and post-reset input/Shift plus22 state blocks totaling104 B/update.

`th04_demo_globals.py` pins original Japanese MAIN identity and each actual
instruction's segment:offset, operand and member addend. Candidate state symbols
must belong to its MAP's DGROUP, fit the complete extent, and have the equivalent
decoded instruction operand in the bounded linked code owner. The player and
Stage4 windows also include their preceding static helpers. The unknown reset
byte remains `byte_259A7`: original0AAF:594D clears DGROUP4667; candidate
`shots_reset()` clears DGROUP953F. It does not map to `_shot_last_id`; the
instruction witness rejects that candidate. No callback/pointer normalization
or target-derived product code is introduced.

| State | Original DGROUP offset | Candidate DGROUP offset | Bytes |
| --- | --- | --- | ---: |
| Boss | 53CA | 4932 | 24 |
| Boss state bytes | BCDE | 4958 | 16 |
| Boss hitbox radius | BCF0 | 496A | 4 |
| Boss timeout | 23ED | 0553 | 1 |
| Midboss | 53B4 | 8CB2 | 22 |
| Midboss active | 46B2 | 8CC8 | 1 |
| Stage4 initialized aim toggle | 185E | 1060 | 1 |
| Player motion | 464E | 8E14 | 12 |
| Option current / previous point | 466C /4670 | 8E20 /8E24 | 4 each |
| Option sprite number | 4674 | 8E28 | 2 |
| Hit / invincibility / respawn | 4669 /4662 /4663 | 8E2A /8E2B /8E2F | 1 each |
| Previous input | 464C | 953C | 2 |
| Power / shot level / shot time / miss time | 4664 /4665 /4666 /466A | 8E2C /8E2D /8E2E /8E30 | 1 each |
| Laser time / style | 42C8 /42CA | 9527 /9529 | 2 /1 |
| Unnamed shot reset byte | 4667 | 953F | 1 |

Complete structures include inactive bytes; every difference rejects the demo
even when bullets/graze agree. Distinct-value and nonzero-frame counts expose
coverage limits. Boss has only one24-byte value per demo, and timeout/hitbox
stay at setup; hit/miss/respawn are zero throughout. Boss combat and player
death/respawn therefore remain unaccepted. Midboss has709/739/482/523 distinct
records and is active707/737/480/523 frames respectively. Player motion has
2307/2567/2357/2417 distinct records; Demo2 laser time has192 distinct values
and3770 nonzero frames. Equality of a constant setup field is not a combat test.

Ownership, coverage and nine frozen reader/test inputs are under
`.analysis/reconstruction/probes/demo-globals-v1368/`. Twelve new public test
groups mutate each104 state bytes, original/candidate opcode/operand/immediate,
member addend, symbol/segment/extent and complete code window. A byte pattern
embedded across other instructions is rejected. Existing observer/trace gates
remain mandatory. Runtime evidence is DOSBox-X-specific and cannot promote
historical exactness or establish original/native parity. Native remains at
`06922ce`, unchanged. README/PORTING_STATUS now describe active work and the
actual separate DOS/native frontiers.

Final `python3 scripts/ci.py` passes389 public tests, complete tracking/catalog
checks,20-target calibration and live Ghidra attestation/mutation controls;
`git diff --check` passes. Its log is `demo-globals-v1368/root-ci.log`.
Post-CI cleanup retires522 source-backed Python caches, reclaiming8,724,480
allocated B before journals. A separate reader checks every retained source,
49 protected hashes, nine frozen reader inputs and complete comparison hashes;
`final-independent-readback.json` passes. No observed stream or build cache retires.

### v1369 raw video observation contract

`--video-stream --video-layout RECEIPT` uses the same frame-counter watch and
natural four-demo terminal decisions as DGROUP capture. It reads emulator host
backing memory directly, never invoking guest memory/I-O accessors. Every update
stores279809 B: stage1, TRAM16384, all262144 graphics bytes (four64KiB planes,
two32KiB pages each), full analog768/digital8/text32 palettes, raw GDC464 and
eight selector/mode bytes. XOR/gzip is reversible and includes invisible plane
tails and inactive palette entries. No rendered-pixel mask is applied.

The small `probe_th04_demo_video_layout.py` compiler probe uses the retained
emulator's own pinned g++8/config and GNU14 ABI options. Twelve header/config/
video-source inputs attest against the pinned DOSBox-X archive; fifteen ELF
symbol extents agree. Compiler-observed VGA size535896, memory pointer offset
535824 and GDC size232 are pinned in the reader; the two GDC objects occupy464 B.
The receipt is `demo-video-v1369/attested-layout/receipt.json`. This builds only
a tiny host-layout program, not the emulator or game. Runtime ELF symbol biases,
backing-memory extent and CPU/display page pointers must agree with selectors.

The comparator requires complete before-update scalar/caller trace identity
against each independent ordinary parent. It then compares every raw plane,
TRAM and palette byte, page/mode selectors, both GDC parameter RAMs and selected
programmed display/scroll fields. All raw GDC bytes remain in the stream;
scan-address/raster/FIFO/drawing-clock internals are counted separately from
programmed presentation state. This distinction does not establish a complete
scanout/timing comparison. Every component contributes to the demo verdict,
and first divergence retains both complete raw blocks with bounded byte causes.
Distinct-value/nonzero coverage accompanies each compared component.

The first producer remains failed before the first video frame: the GDB Python
global `prefix` becomes `/usr/`, causing an attempted `/usr/-demo-1.bin.gz` write.
The local libstdc++ auto-load script assigns `prefix` from the common prefix of
`/usr/lib/x86_64-linux-gnu` and `/usr/share/gcc/python`. Task-specific
`th04_stream_prefix` and related names remove the collision. The failed receipt,
source v1, actual auto-load source and namespace readback remain under
`demo-video-v1369/`; corrected producer v2 is frozen separately. Do not reuse
failed execution directories or call this an original-game differential.

### v1369 complete video differential and carpet ownership

Corrected original/candidate captures complete in413.97s/402.65s, respectively;
their full ordinary scalar/caller traces are byte-identical to the independent
v1365/v1366 parents. Both execute the archived `producer-source-v2` helpers.
`dos-demo-v1369-video-comparison.json` reads every3996 records in all four demos.
All text, palettes, selectors and programmed GDC fields agree. Graphics fail:

| Demo | First stage_frame write | Completed update | Differing frames |
| --- | ---: | ---: | ---: |
| 1 (Stage4) | 2 | 1 | 3459 |
| 2 (Stage1) | 1729 | 1728 | 594 |
| 3 (Stage3) | 658 | 657 | 1259 |
| 4 (Stage2) | 1349 | 1348 | 435 |

The complete raw GDC objects differ in all3996 frames per demo; the excluded
scan/raster/FIFO/clock internals remain diagnostic rather than a programmed-state
verdict. This is not complete scanout timing or cross-emulator acceptance.

Demo1 first differs only in blue page0:2340 bytes at byte columns40..47,
physical rows0..399 (pixels320..383). Adjacent16-pixel words exchange places;
page1 follows at write3. Original STAGES_TEXT(0AAF):3FB6 loads table190C;
3FCB stores tile_ring4D40. Stage4 render3FF4 references table190C at403D/4079.
The original initialized DGROUP(2134):190C table is144 bytes/3x24 words.
The candidate MAP owns `_CARPET_TILE_IMAGE_VOS` atDGROUP(23FB):18D0, within
initialized DATA with no overlapping MZ relocations. Full data comparison
finds12 wrong words: levels0/1/2 place special tiles49/51/53 in columns19/21
instead of original18/20. These map to playfield-left32 plus18*16=320.
This is target-observed static data and runtime-observed graphics evidence;
the causal repair needs a fresh cold build and runtime replay.

`check_th04_carpet_image_table.py` validates target size/hash/MZ, all four actual
instruction witnesses, candidate producer/MAP identity, full DATA extent and
relocation exclusions before comparing every word. Six synthetic test groups
mutate all72 words and reject BSS/short/duplicate ownership, wrong DGROUP,
relocations and truncation. The symbolic maintained ASM changes only the
right-hand column order; no target byte array or historical carpet/checkerboard
exactness work is introduced. Before-repair evidence is
`demo-video-v1369/carpet-table-before.json`.

```sh
python3 scripts/probes/compare_th04_demo_video.py \
  --original .analysis/runtime/candidates/dos-demo-v1369-original-video-v2 \
  --candidate .analysis/runtime/candidates/dos-demo-v1369-candidate-video-v2 \
  --original-full .analysis/runtime/candidates/dos-demo-v1365-original \
  --candidate-full .analysis/runtime/candidates/dos-demo-v1366-candidate \
  --original-consumer .analysis/reconstruction/probes/demo-video-v1369/producer-source-v2/scripts/probes \
  --candidate-consumer .analysis/reconstruction/probes/demo-video-v1369/producer-source-v2/scripts/probes \
  --output PRIVATE-NEW-VIDEO.json
```

A comparison exit1 with these first differences is the expected game rejection,
not a malformed capture. The reader's28 new public control groups reject each
plane/page/tail/text/palette/mode/programmed-GDC mutation and damaged frame/
extent/producer/MAP/ELF/source/control identities. Raw clock-only differences
are retained and counted without silently becoming programmed differences.

The repaired cold MAIN is199455 bytes, SHA-256
`07d4d640e51a8e466237b167815f4446fe2497e36ec1d0128f451559e0d9a7fc`.
Its producer is `product-20261010-181420-9d4128b5-main/receipt.json`:193 C++,155
ASM,8 state and4 sprite producers pass, with zero reused C++ roots. IRQ/vector
and dispatch-table audits pass. Its full MAP remains `2ee564c3…`, byte-identical
to v1366. Independent whole-file comparison changes only24 bytes in the 12 DATA
words; every header, relocation, code, remaining data and overlay byte stays
unchanged. The144-byte table hash is now the target's `1a31a3f8…`.
The package `.analysis/build/th04-demo-carpet-v1369/` explicitly retains the old
unchanged OP/MAINE/ZUN identities. Historical exact ownership does not include
this standalone ASM data owner; its new ledger row remains `source-present`.
Its original source language is unproved, so `origin=unknown`; maintained
symbolic ASM does not itself establish original-ASM or authored C/C++ origin.
The historical authored-byte denominator and all exact states stay unchanged.

The complete repaired ordinary capture `dos-demo-v1369-carpet-candidate/` and
comparison `dos-demo-v1369-carpet-comparison.json` pass all15988 scalar/RNG
boundaries. The independent repaired video capture
`dos-demo-v1369-carpet-candidate-video/` remains byte-identical to that complete
ordinary scalar/caller parent and uses archived producer v2. Its full result is
`dos-demo-v1369-carpet-video-comparison.json`: all15984 video records validate,
with no malformed-capture rejection. Demo1 now matches every compared region
through write490; its first remaining graphics difference is491. Other demos'
complete region hashes/verdicts and first1729/658/1349 remain unchanged. All
text/palette/selector/selected-GDC comparisons pass. Full raw GDC diagnostics
remain retained. The original early blue mismatch is causally repaired; overall
graphics, native x64 and historical exact completion remain rejected.

| Repaired Demo | First remaining write | Differing frames |
| --- | ---: | ---: |
| 1 | 491 | 2909 |
| 2 | 1729 | 594 |
| 3 | 658 | 1259 |
| 4 | 1349 | 435 |

Use the video command above with candidate `dos-demo-v1369-carpet-candidate-video`
and candidate-full `dos-demo-v1369-carpet-candidate` for repair replay. The
candidate build/MAP are `.analysis/build/th04-demo-carpet-v1369/` and
`product-20261010-181420-9d4128b5-main/source/obj/main-native.map`. No emulated
memory patch is applied. Scalar capture must finish independently before video.
The private `run_repair.py` records these exact sequential commands/phase logs,
requires full scalar acceptance, rejects invalid video negatives and checks all
Demo2/3/4 complete region summaries unchanged. All jobs must be terminal before
immutable-copy sharing or source-backed post-CI cache retirement.

A bounded earlier frame491 pellet-list readback retains11 active entries with
matching VRAM addresses and matching relative sprite offsets. Original
TILE_TEXT0AAF:1EAC/1EB9 observes countBCC6/list86D2; candidate MAP owns79ED/7624.
These are diagnostic observations only, not a complete effect-list Oracle or
proof of the remaining graphics cause. The raw lists, target/candidate block
hashes and actual distinct offset bases remain in `pellet-frontier-prefix.json`.

Final CI passes423 public tests,20-target calibration and live Ghidra/mutation
controls; `git diff --check` passes. The first CI log before origin review stays
separate. Final `origin=unknown` DATA ownership preserves the historical exact
byte denominator and all accepted function states. Post-CI cleanup retires529
regenerable source-backed caches/8,830,976 B; three complete immutable-copy
sharing passes reclaim161,304,576 B. Total170,135,552 allocated B (about162.3MiB)
before journals. Independent readback verifies306 protected hashes and26 frozen
source inputs, no remaining public caches, full scalar acceptance and expected
raw-video rejection. All12 full video streams503,789,277 stored B, both cold
caches, original inputs, ordinary/DGROUP traces and failed producers remain.
Native worktree and installed Windows packages remain unchanged; no GUI/key/
physical-audio trial or exact promotion occurs.

## v1370: packed bullet invalidation dimensions

The remaining Demo1 write491 difference is an old pellet residue, not an absent
new pellet. Bounded complete-stream readback at writes487..492 observes the same
sprite on both sides at489/490. At491/492 the original retains its old R/G/E
page1 pixels at physical rows259..266, byte columns8/9; the candidate clears
these pixels. Both active pellet lists drop12 to11 at490. Full raw bullet236
records agree: flag1 at489, flag2 at490, flag0 at491; prev=(592,5984). Page-back
and both page scroll positions also agree across the recorded prefix. These
prefixes localize the problem; they do not establish new full-stream acceptance.

Observed original MAIN TILE_TEXT(0AAF):1FA8..203D, fileE298,150 B including EVEN,
uses DWORD box assignment at1FBE/1FDF and DWORD shift at1FF3/1FFF. The standalone
product context instead declared `_tile_invalidate_box:byte` under `.186`.
Compiler-observed old product instructions assign/shift only the first byte;
two Pascal WORD pushes preserve argument values but change the producer shape.
The old complete MAP contribution is148 B. Successful assembly had not checked
this operand contract. The historical exact owner uses the separate original
scaffold context, so its accepted source/body and historical state are unchanged.

An independent Unicorn CPU replay loads the attested original and old candidate
MZs with DOS relocations, then substitutes each recorded DGROUP write490 state.
It executes the complete `tiles_render()` invalidation chain up to entry of
`tiles_redraw_invalidated()`. All67 ordered positions agree;12 pellet calls pass
8x8 originally versus8x32 in the candidate. Physical half-tile rows32/33,column2
are unmarked originally and marked by the old candidate. The old pellet's
previous y5984/16=374 gives top386 for the original8-high box, which the observed
invalidator rejects at the384-pixel boundary. The erroneous32-high box gives
374 and remains eligible, then scrolling wraps it into the residue's region.
This replay is a bounded seam-state CPU experiment, not a complete next-frame
or PC-98 hardware replay.

The maintained product-only context now uses `.386` and a DWORD external for
the packed x/y words. `check_th04_bullet_invalidation.py` compares the complete
reviewed owner after independently checking its DATA bindings and near callee;
only those addresses are substituted. No instruction, immediate, branch or
padding byte is discarded. The old product is explicitly rejected. Five public
negative-control groups reject every non-address-byte mutation, wrong DATA
binding, wrong near-call target, short/long extent and duplicate/misplaced MAP
ownership. This contract is diagnostic and cannot promote raw exactness.

The first cold compilation links and passes IRQ/vector/bullet-switch checks,
but `build.py` rejects publication because adding the checker during the build
changes its conservative probe-source fingerprint. Its compiled150-byte owner
passes the complete contract; MAIN c6c5ed0a… and MAP69790a7a… are retained as
unpublished compiler observations. The completed failed publication is retained
separately as `cold-main-input-drift.log`; a frozen-input full cold repetition is
required before runtime validation. Do not bypass the input-change guard or
label this first output a published product.

The frozen repeat passes normal publication with all193 C++/155 ASM/8 state/
4 sprite objects and zero reused C++ roots. MAIN199455 B SHA-256
`c6c5ed0ac012b6a4036db434e5d828e60c1edb474137973dce14be3c220dd9a9`,
MAP`69790a7a686e177ff5d281e0a28e63c4062b529d527c368b3300ac62d64b7d4b`.
Both full files are byte-identical to the unpublished first compilation.
Comparing every old/new cold OMF object validates360 complete objects:344 raw
identities and359 identities after normalizing only dependency timestamps.
The sole changed producer is the bullet invalidator's standalone context.
Its complete150-byte linked instruction contract now agrees with the target
after the declared address substitutions. The144-byte repaired carpet table
also passes unchanged. Historical accepted bodies/counts are not promoted.

The ordinary package `.analysis/build/th04-demo-invalidate-v1370/` retains the
unchanged older OP/MAINE/ZUN products with their separate receipts. The fresh
MAIN producer receipt is
`.analysis/reconstruction/probes/product-20261010-191225-23c93740-main/receipt.json`.
Reproduce the cold product with `python3 scripts/build.py --only main
--output-dir FRESH-build`; the complete sequential capture/comparison command is
`nice -n 15 taskset -c 0 env PYTHONDONTWRITEBYTECODE=1 python3
.analysis/reconstruction/probes/demo-render-v1370/run_repair.py` (use fresh run
paths; completed capture images are immutable). This repeats ordinary, full
video and full DGROUP captures with independent ordinary controls. The executed
producer source and checker/reader/test/context inputs are separately frozen as
`producer-source/` and `reader-source/`; freeze probe source too before a cold
build because `product_input_fingerprint.py` deliberately includes it.

All fresh ordinary3996-update demos plus their terminal decisions pass15988
input/rawShift/score/RNG/caller/resident boundaries. The fresh full DGROUP replay
also passes15984 updates:9 pools24952 B plus22 state owners104 B, input/Shift and
graze, with identical independent ordinary traces. Midboss distinct-value and
Boss-setup-only coverage remains the same; death/respawn and actual Boss combat
stay unexercised. The post-repair CPU seam-state chain matches all67 ordered
positions/boxes and all1600 dirty flags; both hotspot flags are0.

Complete video accepts every one of38 compared regions across3996 updates each
in Demo2/3. Demo1 first differs at write1678 (after update1677),1032 differing
updates; Demo4 first1349 (after update1348),181. Both text planes, full palettes,
mode/selectors and selected programmed GDC fields match throughout all four.
Raw GDC scan/raster/FIFO/clock differs3996 times per demo and stays diagnostic.
This accepts scoped raw region state, not full scanout timing or the full game.
Remaining first blocks show Demo1 B/R/G page0 row375,columns13/17/40/41 (3/2/2
changed bytes); Demo4 B/G/E page1 rows103..110,columns26..30 (31/33/33 bytes).
`remaining-video-frontier.json` retains exact source-block hashes and locations;
a point-number, spark or clipping cause has not yet been proved.

Current reports are `dos-demo-v1370-invalidate-comparison.json`,
`dos-demo-v1370-invalidate-video-comparison.json` (expected overall reject), and
`dos-demo-v1370-invalidate-dgroup-comparison.json` under the private candidates
root. Original parents and executed consumer paths are explicit in the frozen
sequential controller. No native worktree change or Windows GUI/physical-audio
trial occurs; ordinary Boss/death/process and cross-emulator/native parity
remain required future work.

Final CI passes428 tests plus20-target/live Ghidra/mutation controls. Post-CI
cleanup removes533 source-backed caches8,871,936 B.178 immutable-copy paths
reclaim74,018,816 B; four full candidate video gzip files restore bit-for-bit
from baseline XOR before retiring162,811,904 B; the rejected cold source's
1769-entry PAX archive preserves every file byte/mode/ns mtime and retires
6,684,672 B. Total252,387,328 allocated file B (about240.7MiB) before journals.
All baseline/delta streams, diagnostic bits, first blocks, scalar/DGROUP traces,
receipts and frozen sources remain. Restore the original gzip files before
using the unchanged complete reader; commands are in ANALYSIS_RETENTION.md.
A one-bit delta mutation rejects before decode. Independent final readback
checks367 protected hashes/17 frozen inputs and all4 original gzip digests.
The initial retention reader catches its writer completing the initially empty
cleanup log; that failure/source stay retained. Reader v2 allows only a verified
log/terminal-receipt before/after bridge. Every other data/source hash is strict.
All jobs terminal; native worktree and installed Windows packages unchanged.

## v1371: point-number multiplier glyph indices

Observed original MAIN CIRCLE_TEXT0AAF:12F5/12FB passes glyph indices10/11
for the two multiplier cels. Its complete renderer is154 B at1274, fileD564;
the following register-ABI `@pointnum_put` is106 B at130E. The standalone
renderer body and context incorrectly define4/5, selecting digit glyphs instead.
The target-derived point-number sprite table at DGROUP2134:098A and the prior
product's DGROUP23FB:285E agree across all1536 B, SHA-256
`32d4b60a041d3d88f337340fc8b96686dcfb22d698c900f70b12606159734066`.
This is a selector error, with no change to the glyph assets.

`check_th04_pointnum_renderer.py` validates target and product MZ identities,
complete unique MAP ownership, both DATA bindings, all five near-call operands,
and the CS-relative self-modifying width-store address. Only those verified
address words are substituted; glyph operands and all remaining instruction
bytes stay in the comparison. It also compares the complete sprite table.
The prior c6c5ed0a product fails only at renderer offsets130/136. Six negative
control groups cover every other instruction byte, address binding, call target,
self-store address, complete extent and MAP-owner ambiguity. These diagnostics
never promote product or historical exactness.

Private bounded CPU replay uses recorded Demo4 DGROUP update1349 actors and
alive pointers, restores the prior update1348 scroll word, loads each relocated
MZ at its recorded load segment, and executes the complete renderer/blitter.
Original/candidate make10 ordered glyph calls but differ at call4: top103,
left214, glyph 10 versus4; the next call at222 uses11 versus5. Ordered VRAM
writes differ69 versus63; tile-register OUT sequences and sprite bytes agree.
All97 changed VRAM bytes in the retained first full video blocks lie within
the differing draw-mask bits. This supports the source attribution; full fresh
runtime replay is the causal gate. Probe scripts/results are under
`.analysis/reconstruction/probes/demo-render-v1371/`.

Demo1 negative trials keep a separate scope: at update1678 its point-number
alive list is empty; the10 spark calls and80 writes agree. A CPU seam-state
invalidation chain from update1677 agrees on155 ordered positions/boxes and
1600 dirty flags. The93 active post-top pellet records at1678 also agree after
substituting only their sprite-base addresses. These experiments do not execute
the complete preceding stage VM/background/hardware state, and do not resolve
the remaining single-row graphics cause.

The fresh zero-cache product compiles all193 C++/155 ASM/8 state/4 sprite
objects and publishes199455 B MAIN SHA-256
`8439b0b0393894125868eb2bee1c75f53ca44daf221bd6ef619a84d7f781f33f`.
The complete MAP remains69790a7a…, and only file offsets46636/46642 change,
4->10 and5->11. All360 OMF objects attest:344 raw identities,359 identities
with only dependency timestamps normalized; only the renderer producer differs.
The complete linked renderer and earlier bullet/carpet diagnostics pass.
The new kernel on prior recorded Demo4 state now agrees with original10 calls,
69 writes and all OUT sequences, retaining separate kernel/state-producer hashes.

Historical focused replay is attempted with the 122-owner dependency closure:
`python3 scripts/replay_th04_main_exact_units.py --unit
th04-main-pointnums-render-v138 --run-id FRESH-run`. Its first cold compilation
fails at scaffold `th04/main/bullet/add.cpp`: missing `ANGLE_PER_SPRITE` and
`bullet_t::from_group`. This extends the already retained v1239 incoherent-header
hazard. It does not reach the second build or raw comparison, and grants no
fresh exact credit. The complete failed frozen `repo-inputs/` and A build remain
at `.analysis/reconstruction/exact-unit-replay/gpt61-v1371-pointnum-symbol-focused/`.
The failed controller/log/phase remain distinct from `run_runtime_repair.py` and
`runtime-phase.json`, which continue the authorized standalone runtime checks.
Do not widen scaffold allowlists or label this failed attempt a raw rejection.

A read-only native audit at06922ce separately freezes four whole source files
under `native-readonly-source/`, with clean Git status and complete digest
readback in `native-readonly-gap.json`. `port64/main_state.cpp:414` records bullet
`point_number` events but consumes only sparks/gather; its item callback at697
updates HUD/sound without consuming `yellow_point_number`. `port64/view.cpp:1074`
paints items followed by enemy bullets without a point-number draw pass. The
public bullet/item interfaces expose those effects. This identifies a concrete
native integration surface to audit/implement: the400-slot popup pool/lifecycle,
widths, white/yellow order and original10/11 multiplier glyphs. It is source
inspection, with no native build/run/write or new runtime acceptance.

The first full video reader rejects the frozen consumer's missing
`th04_demo_dgroup_stream.gdb` before payload comparison. All four capture streams
are already complete and remain untouched. `late-consumer-freeze.json` checks
the helper against the executed capture receipt's exact SHA-256 before copying;
the other three frozen consumers agree already. Initial controller/log/report
stay retained, and `run_runtime_tail_v2.py` independently rereads the same full
captures into a fresh `dos-demo-v1371-pointnum-video-comparison-v2.json`, then
continues fresh DGROUP capture. Do not restamp the old receipt, overwrite its
failed report, or call the initial consumer failure a demonstrated game mismatch.
Freeze non-Python GDB consumers as well as Python dependencies for future runs.

Fresh ordinary replays agree on15984 updates plus4 terminal decisions. The
fresh complete DGROUP replay passes nine raw pools24952 B plus22 pointer-free
states104 B at all15984 updates, input/Shift/graze and independent ordinary
controls. Boss24B stays setup/distinct1; hit/death/respawn remain unexercised.
Full video v2 verifies all3996 records per demo and own ordinary traces.
Demos2/3/4 agree in all38 compared regions: all181 old Demo4 differing updates
vanish. Demo1 remains first1678/after1677 with1032 differing updates, only B/R/G
page0 physical row375 at columns13/17/40/41 in the first block. All TRAM/palettes/
modes/selectors/selected programmed GDC fields agree. Raw GDC clocks/scan/FIFO
remain diagnostic with3996 differences per demo; complete scanout is unaccepted.
This is a causal graphics repair plus preserved actor/scalar state, with one
remaining source cause and separate ordinary/process/native validation work.

Current product receipt:
`.analysis/reconstruction/probes/product-20261010-200541-8c23e354-main/receipt.json`.
Reproduce cold MAIN with `python3 scripts/build.py --only main --output-dir
FRESH-build`, then sequential capture/check commands in the retained controllers,
using fresh run/report paths and all executed Python/GDB consumer dependencies.
Successful full reports are `dos-demo-v1371-pointnum-comparison.json`,
`dos-demo-v1371-pointnum-video-comparison-v2.json` (overall equality rejects only
Demo1), and `dos-demo-v1371-pointnum-dgroup-comparison.json`. All ordinary, video,
DGROUP and reader jobs are terminal. Historical exactness remains unchanged.

Final CI passes434 tests plus20-target calibration/live Ghidra mutation controls.
Terminal immutable sharing covers57 paths/77 protected hashes, reclaiming
73,854,976 allocated B. Four complete candidate video gzip files restore to
original full digests/sizes before sparse baseline-XOR retention retires
162,910,208 B. All raw clocks, invisible tails and record headers are retained.
A fresh one-bit archive mutation rejects before decode. The failed historical A
source is retained as2784 PAX entries/16,350,880 file-payload B with byte/mode/
nanosecond-mtime checks, reclaiming18,526,208 B; its raw git archive separately
restores byte-for-byte from gzip, reclaiming8,040,448 B. Frozen maintained inputs
and A build log remain, and failed compilation stays failed.

After final CI,533 source-backed caches retire8,876,032 B; cleanup stdout is
outside the protected probe tree, avoiding the prior self-log completion issue.
Total reclamation is272,207,872 allocated file B/about259.6MiB before journals.
`final-independent-readback.json` checks199 protected hashes,20 frozen inputs,
all4 full gzip restores,2784 PAX entries, raw input tar recovery and4 native
source files, plus complete current verdicts and434-test CI. Original captures,
all earlier failed reports, complete source snapshots and the successful cold
product cache remain. All jobs are terminal; Windows packages/native worktree
are unchanged. See retention for fresh-path restoration commands.

## v1372 Demo 1 scroll-copy attribution and carpet lighting mask

Read-only GDB host-VRAM watches independently replay original MAIN and the
prior repaired product through the first demo. Fresh snapshots at stage-frame
writes 1677/1678 agree in every compared region at 1677 and reproduce the
retained first 1678 difference. The actual guest writer is the scroll copier:
original CIRCLE_TEXT(0AAF):1073 and candidate CIRCLE_TEXT(0708):2FB5, both
loaded at 10FC. Their complete 182-byte routine agrees outside DATA operands.
Each side records five intermediate host B-plane changes at three watchpoints;
the emulator clears and ORs parts of a word within one guest instruction.
These are host change events, not five separate guest stores.

All 800 tile-ring words and 1600 dirty flags agree at the earlier snapshot.
At 1678 the copied ring row is 23 (375/16); columns 4/6/18 disagree.
The recorded SI values equal each side's ring word plus 7*80, while DI
addresses the same destination. Thus the differing source words precede the
VRAM result; a GRCG/EGC timing explanation is unnecessary for this frontier.
The other changed mask column, 16, already names the same tile image and does
not change that ring word. An initial reader's four-column assertion failed;
a separate v2 reader preserves that negative and verifies the three-column
observation. Original and candidate lighting cel 4/level 0 agree.

The original animation table is MAIN DGROUP(2134):199C..1A5B, file244DC,
192 bytes (eight cels by 24 columns). CIRCLE_TEXT0AAF:3FAB/4026 reference199C;
401F/40BD establish the adjacent cel word1A5C and maximum cel7. The prior
maintained table differs in17 cells in cels4..7, SHA276df582 versus original
a8281fe5. The image-offset table remains correct. Source inspection of HEAD shows
row lengths24/24/24/23/24/24/24/24: cel3 has a missing untouched entry. The
loaded cel3 still looks correct because cel4 starts with untouched2, but
subsequent cels shift by one cell and the last loaded cell is linker padding.
The animation activates the
central pair at cel1, then two more columns on each side per cel through7.
Preserve the original anomaly: cel5/column2 is already-replaced0 before its
normal replacement1 at cel6. Maintained symbolic TASM rules express this wave
and exception, yielding all192 original bytes in the quick OMF readback.
The data owner remains source-present with unknown original source language;
no historical exact unit or authored-byte percentage is promoted.

`check_th04_carpet_animation_table.py` checks original size/hash/MZ, actual
instruction witnesses, complete192 cells, candidate producer/MAP identity,
initialized DATA ownership and relocation exclusion. Seven new test groups
mutate every cell, relocate every byte, and reject incomplete/duplicate/BSS
ownership, wrong DGROUP, invalid original tags and short/extra extents. The
existing image-table helper accepts an explicit extent while retaining its
144-byte default. All13 focused animation/image controls pass.

An independent Unicorn helper trial uses the fresh1677 snapshots, cel4 and
target level1. Original versus prior candidate disagrees on complete1600B
ring/1600B dirty blocks. A third trial replaces only candidate animation DATA
with192 bytes generated by the attested TASM object; both final blocks and the
300 normalized store multiset agree. Store ordering is not claimed, and this
controlled candidate trial is not a fresh whole-frame repair acceptance.

Private replay sources and journals are under
`.analysis/reconstruction/probes/demo-writer-v1372/`. `v2/run_writer.py`
launches the two bounded reads serially; `read_writer_v2.py` binds guest
instructions to the complete relocated MZ image and the retained first blocks.
`carpet_cpu.py` performs the three bounded CPU trials. Use a fresh private
output before rerunning scripts with exclusive output creation. The first
GDB version lacked the public lib import path and stopped before guest
execution; its source/log/receipt remain intact. The custom watchpoint reader
inherits the driver's1536MiB address-space limit; it does not apply the standard
stream helper's512MiB inferior limit. This override is separately recorded
in `row-writer-resource-clarification.json`, preserving the generic receipt.
Every launch is muted/headless; native06922ce and Windows packages are untouched.

The zero-cache MAIN build passes193 C++,155 ASM,8 state and4 sprite objects.
MAIN remains199455B, SHAa7966251; only17 animation DATA bytes change. All360
OMF objects attest,343 raw and359 dependency-time-only normalized identities
agree; the sole changed producer is carpet_state.asm. The complete MAP changes
one ownership length014F->0150 (335->336B), reclaiming the former alignment
byte for the final declared animation cell. All other MAP bytes, following
resource-state address23FB:1A20, code, headers, relocations and other file bytes
remain unchanged. MAP is86798b62; it must not be called byte-identical to69790a7a.
The first controller's expected-identical-MAP assertion rejected this valid
owner change after cold build success; its source/log are retained. A separate
`run_repair_tail_v2.py` verifies precisely that one MAP-line change and continues
from the completed product, without rebuilding or restamping old evidence.
The complete animation/image/bullet-box/point-number contracts pass. The
executed public sources and GDB dependencies were copied into `producer-source/`
before the build. Complete four-demo scalar/video/DGROUP replay is running;
retain its terminal result before claiming a complete causal repair.

A read-only native06922ce audit freezes stage4.cpp/stage4.hpp/verify_carpet.py
and the existing Stage4 note. Its animation formula already preserves the
correct wave and cel5/column2 exception; image columns18/20 are also correct.
No native table synchronization is needed for this DOS short-row defect.
The existing component Oracle separately checks all192 original DATA cells,
but its published scope excludes original dirty-page VRAM transients replaced
by host full redraw. Keep native state/DATA confidence separate from paired
presentation acceptance. This inspection adds no new native build or runtime
claim; the native worktree stays clean.

Fresh complete ordinary replay accepts all15988 scalar/terminal boundaries.
The independently captured video replay also passes: all four demos agree in
all38 compared regions at3996 updates each, with zero differing frames and no
first difference. All1032 remaining Demo1 differences disappear, while the
other three demos stay accepted. This causally closes the short-row animation
DATA defect for the bundled-demo presentation scope. Complete raw GDC
scan/raster/FIFO/clock bytes remain retained and diagnostic; full scanout,
process teardown, ordinary Boss/death/respawn and native parity remain open.
Fresh full DGROUP acceptance also passes: all15984 updates, nine raw pools
24952B plus22 pointer-free states104B, input/Shift and graze. Both independent
video/actor capture traces reproduce the complete ordinary controls.

Final `scripts/ci.py` passes441 tests,20-target calibration, tracking and live
Ghidra/mutation controls; `git diff --check` passes. Cleanup starts only after
all build/game/reader jobs terminate.78 terminal immutable paths share matching
bytes/modes, reclaiming139792384B with128 protected hashes. Four new full video
gzip files restore byte-exactly through original-v1369-baseline XOR archives;
this preserves every header, raw GDC clock, encoded frame and invisible tail,
reclaiming163233792B. A one-bit delta corruption rejects before decode.
Post-CI535 source-backed caches retire8892416B. Independent final readback
checks270 protected hashes,26 frozen inputs, all4 full gzip recoveries, the
current product fingerprint and all ordinary/video/DGROUP verdicts. Total
reclamation311918592 allocated file B (about297.5MiB) before journals.
Successful cold objects, complete scalar/actor evidence and all failed-control
sources/logs remain. Mutable phase/stdout files stay outside the protected tree.

Use `demo-writer-v1372/restore_video_stream.py` without options to verify all
recoveries, or add `--output-directory
.analysis/runtime/candidates/dos-demo-v1372-animation-candidate-video` to restore
all four full gzip files before unchanged-reader replay. Restoration refuses
existing outputs. Full runtime commands are recorded in `run_repair_tail_v2.py`;
final verification/retention in `run_finish.py`, with terminal phase journals
and raw logs. These scoped results do not close full scanout, ordinary Boss/
death/process, cross-emulator or native x64 acceptance.


## v1373 native point-number rings and foreground join

This advances the native source gap observed at06922ce. The DOS v1372 package
and its four complete demo comparisons remain unchanged. `port/modern-64`
now owns400 point-number records, two200-slot overwrite rings and the retained
alive-list boundary. Items insert white/yellow base scores with the pull
multiplier; bullet-zap events insert white numbers. Update precedes these
insertions, so fresh slots join rendering on the next update. Rendering follows
its retained pointers, writes widths once per simulation frame and appends the
original multiplier cells10/11. The view consumes cached glyphs after items
and before enemy bullets, mapping physical rolling rows to the host display.

Original target/MZ identity and a fresh MAIN database attestation pass. Bounded
original entries are CIRCLE_TEXT(0AAF):11C2/1204/1274/130E/1120 and
main_03(13A9):0300/031A/4F5E. DGROUP(2134) owns pool9634 (6400B), cursors3ECE/
3ECF, list3ED0 (401 near pointers), first-yellow41F2 and the 12*128B mono font098A.
The original font is read from supplied HDI MAIN, not embedded in code. Every
preshift is checked against its unshifted row. The original24 stationary updates,
later eight-subpixel rise, clipping, age 37 remove and next-update free are
preserved, including previous-Y/padding on overwrite and unused pointer-list
tails. This is native migration, not new historical exact credit.

`port64/verify_point_numbers.py` executes the original add/digit/update/render/
put/scroll bodies at load 1000/2000. DS 8000/SS 7000 and pool/scroll inputs are
explicit component adapters. The existing independent GRCG shadow observes
actual glyph stores/ports on a patterned 640*400 indexed screen; the original
self-modifying width instruction executes. Only near-pointer representation
becomes index+1; all 6400 pool bytes, both cursors, all 401 list entries, the
first-yellow marker and four neighboring sentinel bytes are compared.

GNU8 and optimized nonrecovering UBSan each pass830 state/request cases and 494
complete indexed pictures. These cover all numeral/multiplier cels, bit
alignments, lower-edge wrap, both colors, overwritten/removed retained list
slots, integer boundaries and a39-update lifecycle. Two further complete400-slot
list tests (dispersed/overlap, all flag values0..3) emit 1892 ordered glyph requests
perpicture; both hosts match original full state/pixels at both loads.

All five source-only mutations return normally with830 rows and are rejected:
early rise first differs129; shortened ring33; wrong yellow intensity297;
digit4 multiplier301; immediate free129. Complete wrong outputs/source/link
commands remain. A constructed all-zero original number does not return within
200000 instructions and emits2150 requests. Native rejects that input explicitly;
this negative is not ordinary gameplay acceptance. In-font leading glyph 10/11
for10000/11000 values is preserved; outside-font values are not accepted.

Fresh GNU builds69 AMD64 programs and passes 68 CTests. Focused UBSan builds the
portable core, popup contracts and frontend. Actual pickup contracts exercise
white, yellow max-value and doubled collection, list admission and multiplier
requests. Five muted no-window MAIN/combat images per host agree; they establish
integration smoke and host consistency, not original full-scene pixels. New
producer496-input manifest is707d129ae6730d6e316ec359fa8b27a948403ef117283898556c374f04b48791.
Old v1356 natural-route/timing/Windows products retain their own identities and
scope. No Windows program/window/key injection or package update occurs.

The first 766-case run retains its own executed496-file source pins. The final
producer snapshot freezes all496 inputs plus the22 actually imported public
Python dependencies, including unchanged native script dependencies. A fresh
frozen-reader replay passes300 state/request rows and three complete pictures
at both loads. Every old receipt keeps its original source identity. Fresh
private receipts live in the native worktree at
`.analysis/port64/pointnum-v1373/`; root orchestration/database witnesses live at
`.analysis/reconstruction/probes/pointnum-port-v1373/`.

Replay in the native worktree, with fresh output directories:

```sh
nice -n 15 taskset -c 0 env PYTHONDONTWRITEBYTECODE=1 \
  python3 port64/verify_point_numbers.py \
  --target .analysis/targets/th04/main.exe \
  --exe .analysis/port64/pointnum-v1373/build-gnu/th04-port64-pointnum-contracts \
  --output-dir .analysis/port64/pointnum-v1373/FRESH
ctest --test-dir .analysis/port64/pointnum-v1373/build-gnu \
  --parallel 1 --output-on-failure
```

Precise native ownership and adapter limits are in branch
`docs/port64/evidence/point-numbers.md`. Complete natural original/native
state/RNG/foreground/process pairing, original dirty-page transients and
physical scanout remain open. The next fidelity work should capture complete
native demo state and RNG/ring/call counts at the same logical boundary as the
retained original DOS demos; native-host equality cannot substitute for it.

Final main CI 441/live Ghidra and native CI 313/target checks pass; the native
private Ghidra/tool gates skip where unavailable. All jobs are terminal. Lossless
retention reclaims 502460416 allocated file B (about 479.2 MiB).23 full raw/text/
mutant streams restore byte-exactly with modes and nsmtimes; 3093 protected
hashes and 496 current source pins read back. Successful current build objects
stay available. Retired 1040 public caches are source-backed. CI's explicit
compileall creates them despite PYTHONDONTWRITEBYTECODE; the initial absence
assertion rejects after complete archives succeed. Its source/log and partial
journal remain; a separate v2 reader resumes, restores all streams and passes.
Use native `.analysis/port64/pointnum-v1373/restore_streams.py` without options
for full verification, or `--restore` before unchanged old-reader commands.
Restoration refuses different existing files; private evidence is never
normalized or restamped. Retention/readback journals remain immutable.

## v1374 native before-update state and RNG pairing

The native branch adds an ordinary headless MAIN adapter and an independent
reader of the complete v1365 original DOS reference. All four correct zero-based
ST00..ST03 replay/STD/MAP inputs are decoded from the attested archive; original
valid scores/configuration are supplied directly. The existing DOS reader
revalidates complete capture identities and all caller/input/terminal records.

The old native producer first differs in Demo 2 at frame3533: score bytes and
accumulators differ, and original ring cursor B9 versus native B8 reflects one
missing spark draw. Original shots7/15 hit one frame earlier. MAIN's Stage 1
midboss detachment adds fractional BYTE DGROUP2134:4276 to Y; its instruction
witness is MAIN_032_TEXT13A9:065C..0669. The native caller supplied the separate
whole-pixel WORD distance corresponding to DGROUP:427A. Its midboss Y was three
subpixels high. A separate fraction field/getter repairs only native ownership;
DOS source/products and historical acceptance remain unchanged.

GNU and nonrecovering optimized UBSan now accept all 15,988 boundaries across
four complete demos, comparing 23 scalar/player/score/RNG fields and exact LCG/
ring call counts. Both complete native traces agree. A source-only reintroduction
of the distance adapter executes all rows and rejects at the same3533 boundary;
697 original versus696 native ring calls distinguish it without relying only
on a wrapping cursor. Eight public reader controls reject truncation/order,
terminal, score, complete-ring and wrapped-count mutations.

This is selected before-update state acceptance, including the four terminal
callbacks. It excludes complete actor/effect pools, caller-family identity,
original/native pictures, physical scanout/timing, front-end/process teardown,
ordinary Boss/death routes and actual Windows acceptance. Original CPU midboss
controls remain a separate component Oracle. Initial one-based scratch inputs
and default-option adapters keep their own failed/bounded receipts and sources;
no older natural-route or Windows evidence is relabeled as current.

Current public replay is native `port64/verify_demo_state.py --dos-root ROOT
--original ROOT/.analysis/runtime/candidates/dos-demo-v1365-original --exe
.analysis/port64/native-demo-v1374/build-gnu/th04-port64-demo-state-trace
--output-dir FRESH`. Focused native ownership and limits continue in its
`docs/port64/evidence/demo.md`. All launches remain muted/headless and heavy
commands use CPU0/nice15 serially.

Final v1374 checks pass main 441/live Ghidra and native 321/target gates; native
private Ghidra/tool gates skip when unavailable. The frozen current reader
replays all 15,988 boundaries independently. GNU 70/68 CTests and focused UBSan 3
retain 498 sources/current manifest ff0b3bde…. Five pictures per host match as smoke
evidence. Complete 699 original midboss controls, 450 tile controls and setup pass
per host; original load2000/DS8000 adapters remain explicit. All handles terminal.

Lossless retention retires 26 streams and 1041 source-backed caches, reclaiming
166055936 allocated B (about 158.4 MiB) before journals. Full restoration/readback
and 8904 protected hashes pass; current source pins and DOS fingerprint agree.
Sources, failures, current build objects and old Windows/DOS products remain.
Use native `.analysis/port64/native-demo-v1374/restore_streams.py` with no options
to verify all recoveries, or `--restore` before unchanged old raw-path readers.

### v1375 complete native demo actor/effect pools

The new read-only actor observer runs immediately after native frame increment,
before periodic performance and score/extend. The original DGROUP stream seam
also follows actors, rendering, input reset and sound update but precedes modulo
counters and score. Observer-enabled stdout must remain byte-identical to a
separate complete ordinary selected-state run with actual CFG/scores/assets.
The independent DOS reader validates all original stream/ordinary/consumer/
target/process/load/CPU/page-map identities and complete gzip EOF/CRC.

The first eight-pool GNU pair accepts shots, enemies, sparks, bullets, custom
entities, circles and gather circles. Only pointnums differ, first at demo1/2/3/4
frames3379/3709/1952/3059, for618/288/2045/938 frames. Full captures retain this
failure. Original 13A9:64DE..6547 zeroes DGROUP988, consumes both position RNG
calls and calls yellow_add0300 with1280. Native Midboss actors already emit those
positions/rewards and update score/RNG, but MAIN's sink ignored the point event.
Adding the yellow consumer at that synchronous boundary repairs the full pool.
The item owner additionally retains unused/unknown bytes and sprite WORD16;
original items_add13A9:9FA8..A03D clears byte15/pullWORD18 and selects patterns44..50
from DGROUP2134:2322 while preserving byte1 and previous coordinates.

Final GNU/optimized UBSan compare all15984 updates on all nine complete pools
(24952 bytes/update) with zero differences. All inactive/padding fields remain;
enemy native IDs become actual STD-relative offsets, never masked pointers.
Complete15988 selected scalar/terminal fields and exact RNG counts also pass.
Removing only the Midboss consumer reproduces all four first pool differences;
selected scalar state and the other eight pools still pass. Eight public reader
controls reject inactive-tail/pointer/missing/duplicate/truncated/wrong-demo rows.
Frozen current native+DOS reader dependencies replay the same full acceptance.

GNU cold baseline plus bounded MAIN/item/trace rebuild yields70 programs/68 CTests.
Final UBSan core/trace is cold-built, one program; no full UBSan CTest claim.
Current producer has500 files, manifest656a05d9…. No DOS source/product or
historical exactness change. Other globals, original/native pictures/scanout,
ordinary Boss/death/process and Windows remain open. Older component and natural
route producers are retained with their own identities.

From the native worktree, with absolute DOS_ROOT pointing to the main worktree:

```sh
nice -n 15 taskset -c 0 env PYTHONDONTWRITEBYTECODE=1 \
  python3 port64/verify_demo_pools.py --dos-root "$DOS_ROOT" \
  --original "$DOS_ROOT/.analysis/runtime/candidates/dos-demo-v1365-original" \
  --original-dgroup "$DOS_ROOT/.analysis/runtime/candidates/dos-demo-v1367-original-dgroup-v2" \
  --original-consumer "$DOS_ROOT/.analysis/reconstruction/probes/demo-dgroup-v1367/consumer-source-v2/scripts/probes" \
  --exe .analysis/port64/native-pools-v1375/build-gnu/th04-port64-demo-state-trace \
  --output-dir FRESH
```

`ubsan-nine/` pins the sanitized program. `initial-pair/` preserves the rejected
8-pool/v1 reader and its producer; `mutant-pair/` preserves the new9-pool control.
`frozen-source/` retains500 native files plus actually imported DOS dependencies.
Every complete native pool stream is compressed and fully restored/read back
before its expanded copy is removed. Original streams and consumer sources stay
immutable. All runtime claims remain scenario-specific and locally attested.

Final CI passes main441/live Ghidra and native329/target checks (unavailable
private native gates skip). Retention reclaims2038489088 allocated B before
journals, preserving/restoring five full pool streams and ten text streams,
retiring1042 source-backed caches.8904 prior protected hashes,500 current source
pins,71 programs and DOS fingerprint pass. Current builds and failures stay;
verify recovery with native native-pools-v1375/verify_retention.py. All jobs terminal.

## Actual native FrontEnd pictures and DEMO PLAY text (v1376)

The new `--demo-pictures DIR` runs ordinary idle OP entry, four bundled demos
and natural return to OP without a host window or audio. It copies the attested
starting score/CFG files and checks both unchanged after the route. The public
reader validates the full original ordinary trace, complete15984 video records,
CRC/EOF/load/CPU/ABI/consumer identities and pinned legal HDI before comparison.
All15988 selected scalar/count boundaries agree on the actual FrontEnd.

The initial GNU/optimized UBSan v3 captures retain28 full displays each. Their
complete selected state passes, but each of16 post-curtain samples lacks54 of72
DEMO PLAY text code/attribute bytes. This is a specific missing renderer owner;
score-tail timing cannot explain this constant middle-of-playfield label.
The original stage-enter owner, MAIN_01_TEXT0AAF:62B3..6348 (file125A3,150 bytes),
checks the72 timer, demo resident byte and writes nine gaiji at column18/row12
with attributeC3. DGROUP2134:1C20 retains the actual terminated label. Native
`main_text_plane` now applies these semantics on demos after enter completion,
including the frozen demo exit display. Ordinary-play callers keep their mode.
GNU/optimized UBSan v4 accept all40 complete72-byte spans, including frames72/73/74 in each
demo. All15988 scalar/count boundaries still pass. Eight public controls test
complete sample order, last bytes, TRAM banks, bit order, page selection, address
wrap/partitions and unsupported GDC modes. Earlier initial adapter failure
omitted `enable_registration`; no MAIN actor ran, so it is a probe failure.

The full640×400 graphics comparison remains diagnostic: original samples at
frame-counter write before score/background tail, native after complete
FrontEnd update. Retain full256000 indexed bytes,768000 text-composited native
RGB bytes,8000 canonical TRAM bytes, and complete279809-byte original snapshots.
Do not crop or mask invisible graphics to manufacture equality. Original MPN
uploader MAIN_01_TEXT0AAF:0E0C..0E80 (fileD0FC,117 bytes) populates100 image slots
in both physical pages at left576..639. Original reverse blank TRAM can cover
this cache. Native first-frame black curtain likewise follows reverse blank
TRAM; the earlier graphics-only original PNG omitted this text layer. All12
initial full canonical TRAM samples agree. Later score/HUD differences need aligned
sampling; physical blink/FIFO/scanout and original composited RGB stay open.

Programmed GDC decoding uses the pinned emulator's partition SAD/LEN, pitch40,
row-height1 and analog four-plane display-page model. It rejects unsupported
IM/WD/mode/extent. Its28 overlapping original hashes independently match the
earlier NumPy decoder; this is model cross-checking, not physical scanout proof.
Fresh Ghidra/target/header/entry/relocation/load and raw owner witnesses are
retained in root `.analysis/reconstruction/probes/native-pictures-v1376/`.
Use its `attest_picture_owners.py --target TARGET --database ATTESTATION
--output FRESH.json` to replay both owners. Earlier scratch address-base mistakes
are retained and rejected; complete corrected owner digests agree with the
existing accepted extents. Target provenance remains candidate-local-attested.

From the native worktree, using absolute DOS_ROOT:

```sh
nice -n15 taskset -c0 env PYTHONDONTWRITEBYTECODE=1 \
  python3 port64/verify_demo_pictures.py --dos-root "$DOS_ROOT" \
  --original "$DOS_ROOT/.analysis/runtime/candidates/dos-demo-v1365-original" \
  --original-video "$DOS_ROOT/.analysis/runtime/candidates/dos-demo-v1369-original-video-v2" \
  --original-consumer "$DOS_ROOT/.analysis/reconstruction/probes/demo-video-v1369/producer-source-v2/scripts/probes" \
  --hdi "$DOS_ROOT/.analysis/runtime/images/zun.hdi" \
  --exe .analysis/port64/native-pictures-v1376/build-gnu-v4/th04-port64 \
  --output-dir FRESH
```

Use build-ubsan-v4 for the instrumented FrontEnd. v3 cold main/view (and UBSan
audio) TUs and v4 cold view TUs reuse the unchanged v1375 core/ymfm libraries;
this is explicitly a bounded frontend build, not whole-current cold/CTest or
Windows acceptance. All producer sources and actual link dependencies are
pinned separately. Retained v1375 nine-pool acceptance keeps its own producer;
no DOS input, original bytes, physical Windows product or historical exactness
state changes in this batch. Next align the full presentation boundary before
claiming pictures; do not treat every raw diagnostic difference as a source bug.

Final502-source producer manifest is6a997fe129eda10206e39323891f13da65187adc2aed5e91af4cf9bf45141db0.
GNU/optimized UBSan final capture bytes agree completely; frozen reader imports
reproduce2×15988 selected boundaries and2×40 label spans while consuming all
15984 original records. Main441/live Ghidra and native337/target CI pass; absent
native private gates skip. No Windows or DOS product launch/build occurs here.

All jobs terminal. Native native-pictures-v1376 retention reclaims291966976
allocated B before journals, fully preserving671 archived raw display/state/
intermediate files and retiring1043 source-backed caches. Full restored hashes,
modes/nsmtimes and gzip CRC/footer/EOF pass;8904 older protected hashes,502 source
pins and4 new/71 old programs remain equal. Use verify_retention.py for temporary
restored readback, or --restore before frozen_readback.py/verify_initial_label.py
and old object reuse. The public reader uses fresh outputs and retained programs.

## Post-update presentation seam and complete native TRAM (v1377)

The v1376 late score/HUD difference was sampled across unequal boundaries.
Original TH04VD2 stopped at the stage_frame write, before mod counters,
performance/score and background-tail work. Native FrontEnd pictures followed
the complete update. Keep those old observations under their original seam.
New TH04VP3 captures the next ordinary I header (MAIN_01_TEXT0AAF:00B7) or
terminal T header (:0975), following the previous complete iteration; I0 is
seen exactly once and excluded, frames1..3996 remain complete. No guest bytes
or inputs change. Entire ordinary scalar/caller traces must match their
independent v1365 original and v1372 reconstructed parents exactly.

The separate projected consumer changes only the DGROUP BOUNDARY constant,
video magic and the GDB sampling body. Donor driver/ROOT, ordinary observer,
host-RAM mapping, ELF, legal image and video ABI remain pinned. A single
CoreNormal+0x1DE software breakpoint observes scalar headers instead of every
emulated instruction; its19 bytes are488b2df3a37304488b1b4883c4204839eb7434.
ELF instructions/symbols separately attest cpu_regs48B/IP+32 and Segs136B/
CS+8/DS+24 (Segs values are64-bit, of which the segment lowWORD is read).
Guest CS:IP/DS must agree with the role's attested profile on every record.
Receipts are root .analysis/reconstruction/probes/native-presentation-v1377/.
The original v1 import projection and v2 untyped DWARF attempts stay failed;
the v3 raw-host reader completes every record. The host-site v1 attempt to
expect a16-bit DS load is rejected by real64-bit MOV; the corrected probe
checks its RIP-relative destination, rather than assuming its instruction.

Native public verify_demo_present.py consumes all15984 original video records,
validates CRC/EOF/target/load/ABI/source identities, then pairs unchanged
v1376 GNU/optimized UBSan FrontEnd programs from their lossless archives.
Both still match all15988 selected scalar/count boundaries. At40 samples
(frames1/2/3/72/73/74/1952/3379/3709/3996 in each demo), all8000 canonical TRAM
bytes agree, including all72 label bytes. These are complete selected text
planes, rather than acceptance of every text frame or all16384 raw TRAM bytes.
All256000 graphics indices remain compared diagnostically. Original font/
blink/composited RGB, physical scanout, broader routes and other globals stay
open. No masks/crops accept a picture, no C++ rebuild occurs, and immutable
compiled producer502/6a997fe1 remains separate from the505-file new consumer.

Current native evidence is .analysis/port64/native-presentation-v1377/; run
port64/capture_demo_present.py with the pinned emulator/video-layout/font and
a fresh consumer/output directory, selecting --original or the v1372 build/MAP.
Then run port64/verify_demo_present.py with --dos-root, --original,
--ordinary-reference, --original-consumer, --native-evidence (v1376), and a
fresh --output-dir. Every launch remains muted dummy-SDL; Windows is untouched.

Both original v3 and reconstructed v4 post-update captures complete4×3996
records, preserving the full independent ordinary scalar/caller trace. The
complete DOS pair passes all38 compared video regions at every record, including
both graphics pages/four planes, full raw TRAM, palettes and selected programmed
GDC fields. Raw GDC internals differ at every frame and remain diagnostic.
Replay: root native-presentation-v1377/compare_present.py uses the projected
consumer first, then the unchanged root compare_th04_demo_video.py; do not run
the old-format CLI with its script directory taking import precedence.
Original effective nice19 follows outer15 plus donor15 (inferred); candidate
CPU0/nice15 is separately runtime-observed in process-resource-observation.json.
DOS source fingerprint remains6f5898dd…; no new DOS build is needed for this
consumer-only boundary experiment. Current consumer505/8b0f702a is distinct
from the immutable v1376 compiled producer502/6a997fe1.

Frozen consumer replay produces a byte-identical complete receipt, including
each full text/graphics diagnostic row and all15988 scalar/count boundaries.
Graphics location reducer retains every256000-pixel comparison:30/40 samples
agree within x32..415/y16..383, while ten differ there. The nonzero samples are
Demo1 frames1/1952/3379/3996, Demo2 1952/3379/3709/3996 and Demo3 3379/3709.
Every full graphics frame still differs. These diagnostic rectangles/maps
do not accept cropped pictures. Check displayed/pending pages and physical
scanout timing before treating any remaining indexed difference as a renderer
source defect. Native graphics-diagnostic.json retains full hashes, counts,
80×80 location maps and colour histograms; original/raw native pixels stay pinned.

Final main441/live Ghidra and native345/target CI pass; unavailable native private
gates skip. Retirement reclaims153010176 allocated B (145.9 MiB) before journals:
128 complete HDI/raw snapshot copies and1044 source-backed caches. All9692
protected hashes,505 source pins, unchanged DOS fingerprint and complete archive
restore/SHA/mode/nsmtime/gzip EOF pass. Recovery is root
.analysis/reconstruction/probes/native-presentation-v1377/verify_retention.py;
add --restore before reading retired HDIs/snapshot paths. Complete VP3 streams,
original references, programs, source snapshots and failures stay pinned.

## Native Midboss shake consumer (v1378)

The display-page hypothesis does not explain the retained forty samples:
current and pending selectors agree, pending wait is zero, and GDC first line
agrees with native scroll. Choosing the other page increases most differences.
Both original physical MPN cache banks agree with all128 bytes of every asset
image at every sample. Demo2 uses Marisa ST10.MPN, not Reimu ST00.MPN; the first
wrong-asset cache experiment is retained separately as a rejected hypothesis.

Target-observed MAIN_01_TEXT0AAF:2246..2315 (fileE536..E605,208B) consumes
DGROUP2134:427E/4280/4282 signedWORD x/y/timer and :185C signedBYTE redraw.
Nonzero timer writes x=-2 for mod2 zero, otherwise+2; y=-2 for unsignedmod4<=1,
otherwise+2, then decrements the WORD. Four far EGC calls (MAIN_00_TEXT0000:
0A22/0B24/0C34/091C) pass the complete32,0,415,399 rectangle and shift count.
Horizontal movement precedes vertical. Movement sets redraw2; a nonzero redraw
decrements, executes actual tiles_invalidate_all0AAF:2052, and clears x/y.
Counter wrap remains16/8-bit. Stage session clears x/y but preserves timer and
redraw; a fresh MAIN instance starts zero. These are target observations,
not a new exactness promotion or a physical EGC pixel acceptance.

Native Midboss producers already emitted twelve-frame shake events; MAIN only
recorded them. The new playfield_shake owner consumes the timer, updates at the
original modulo phase, and retains the applied shifts separately from cleared
post-state globals. Final graphics movement precedes Bomb page retention and
text overlay. It moves physical x32..415/y0..399 through the400-line scroll
ring, X thenY, retaining vacated strips. That physical edge model is inferred
and invariant-tested; the CPU Oracle records EGC requests rather than executing
hardware blits. Ordinary Boss direct offsets and Bomb interaction remain open.

Original CPU execution compares3262 complete globals/EGC-request cases with
the native checker, including signedWORD timer and signedBYTE redraw wrapping;
an injected adapter rejection propagates. Thirty-six labelled full256000-pixel
shift/scroll cases check every exterior, vacated-strip and wrapped-row pixel.
Actual headless FrontEnd idleOP→four demos→OP captures retain every shake state:
all15984 updates agree on the complete7-byte original globals and actualCPU-
derived applied x/y/invalidation. The reader uses original DGROUP modulo bytes;
only observed12-frame Midboss requests are inferred from timer transitions,
and unexpected transitions reject. Existing15988 selected scalar/count
boundaries and all nine complete pools at every update remain compared.

Demo1 frame3379 diagnostic playfield differences fall55357→430. All430 remaining
pixels lie at y16/17, consistent with the native background clipping before
vertical motion; that ownership is not repaired or accepted here. All forty
full8000-byte canonical TRAM samples remain equal. Every complete graphics
frame is retained/compared diagnostically; fullRGB/font/blink/scanout and the
initial carpet, laser and circle pixel differences remain open. No crop/mask
accepts pictures. Private recipes and immutable producer sources live under
root .analysis/reconstruction/probes/native-pages-v1378/ and native
.analysis/port64/native-pages-v1378/. Public owner Oracle:

```sh
nice -n 15 taskset -c 0 python3 port64/verify_playfield_shake.py \
  --target "$DOS_ROOT/.analysis/targets/th04/main.exe" \
  --exe .analysis/port64/native-pages-v1378/build-gnu-v2/th04-port64-shake-checks \
  --output-dir FRESH
```

The full GNU cold build has71 programs and69 passing CTests. Final producer
pins509 inputs, manifest9346e9513312ac094a289e3da52ee2706f7a6d854941b81dde8a03ac168d97dd.
The first standalone Oracle Path-versus-bytes error, whole-build missing
namespace alias and complete-reader wrongROOT import failure remain retained.
Do not reuse the old whole DGROUP consumer as an import prefix: import actual
DOS-root scripts/probes first and pass old sources as attestation only.

Optimized UBSan cold core/game/trace/shake yields3 programs with no fullUBSan
CTest claim. Both hosts pass complete shake/scalar/nine-pool controls and all40
canonical textplanes; their125 entire capture files agree byte for byte.
Removing only MAIN's timer event consumer from frozen producer source rejects
13 updates/demo, first3379/3710/1953/3059, while selected scalar/counts stayequal.
The mutant program/source/link/capture/receipt remain pinned. Six trace controls
reject missing/duplicate rows, lastframe/lasttimer/appliedshift/invalidation drift.
Frozen native509 and actual importedDOS/producer-attestation sources reproduce
both complete shake receipts, with only their separatelypinned ownsourceSHA
different. Frozen/imported consumer identities do not restamp older binaries.

## v1378 terminal validation and recovery

All v1378 jobs are terminal. Main441/liveGhidra and native345/target CI pass;
unavailable private native gates skip. Initial unregistered Oracle label and
cleanup log-lifetime failures stay retained: archive restoration passed before
retirement; final gate rejected its own writing log, then a distinctv2 journal
pinned that log after terminal. No archive/program/source bytes were repaired.
Lossless retirement reclaims324722688 allocated B (309.7MiB) before journal
cost:1390 full raw/sample/build-intermediate files and1044 source-backed caches.
Full restored SHA/size/mode/nsmtime/gzip EOF,15620 protected hashes,509 source
pins and unchanged DOS fingerprint pass. All71GNU/3UBSan/newmutant programs,
complete frozen sources, original references and failure receipts stay live.
Recovery from DOS root: python3 .analysis/reconstruction/probes/native-pages-v1378/verify_retention.py --restore before old raw-capture/graphics/frozen-reader paths.
Use no options for full temporary readback. v1377 restore proof retained its
then-current505 scope; its live-source check must not be restamped to509.

## Complete ordinary background ring before shake (v1379)

Target MAIN_01_TEXT0AAF:20C8..2109 (fileE3B8..E3F9,66B) starts destination
WORD7804 (physicalrow384/x32), ringWORD5340 (4D40+24*64), and iterates24 tiles
of16 rows before walking backward through25 ring rows. The unchanged explicit
EGC setup/off leaves are hardware adapters. Actual original instruction
execution produces9600 distinct WORD copy requests covering x32..415 and
all400 physical rows. A four-plane latch shadow uses each target-selected
source/destination, rather than substituting a native coordinate formula.

The original Demo1frame3379 DGROUP stream supplies the full25x32 tile ring;
ST03.MPN supplies all128bytes/image. Recorded movement(-2,+2) and displayline34
are preserved. The independently replayed fulltile page agrees on all768
pixels of y16/17; the retained oldnative page differs at430 of those pixels.
This is an adapted EGC component and actual-state edge observation, not
physical hardware, whole scene, RGB or scanout acceptance. Fresh preflight and
live MAIN database attestation pass; provenance stays candidate-local-attested.

Native view previously painted stage tiles only at y16..383. Ordinary tiles
now paint the full400-row ring before movement. Boss backdrop transition masks
retain their23-visible-row bounds, avoiding unsigned mask-row underflow. Only
view.cpp changes among509 producer inputs. GNU and optimized UBSan cold-compile
that translation unit and relink with SHA-attested unchanged v1378 main/audio/
core/ymfm inputs. This is a bounded cold frontend build, not a new whole-current
cold build or69-CTest claim. Producer manifest:
8e77830c1ca94c052e718b9f96d1ac1d6712af8abdbd6f3ced1c1167e1d21c09.

Actual muted SDL-dummy idleOP→four demos→OP compares complete selected scalar/
shake traces and all40 full canonical text planes. Full graphics/RGB samples
remain retained diagnostically. Demo1frame3379's game-area differences now
fall430→0. Nine other nonzero game-area samples are unchanged; no new game-area
difference appears. Do not crop/mask this result into a whole-picture claim.
Initialcarpet, Marisa laser and circle pixel differences, fullgraphics/RGB/
font/blink/scanout, Boss offsets/Bomb interaction and broader paired routes
remain open. Prior v1378 complete-pool and69CTest receipts retain their own
unchanged core/program producers; they are not restamped with the new view hash.

Recipes: root .analysis/reconstruction/probes/native-ring-v1379/
prove_full_ring.py, build_frontends.py, run_validations.py; evidence native
.analysis/port64/native-ring-v1379/. Each uses fresh outputs, CPU0/nice15;
all launches stay muted/dummySDL. No original/DOS source or target bytes change.

## v1379 terminal validation and recovery

All v1379 jobs are terminal. Main441/live Ghidra and native345/target CI pass;
private unavailable native gates skip. Frozen full-reader replay reproduces
both complete shake receipts, apart from its separately pinned source hash.
Lossless retirement reclaims153083904 allocated B (146.0MiB) before journalcost:
342 complete sample/capture/build files and1044 source-backed caches. All16713
protected hashes,509 source pins, full restoration/SHA/size/mode/nsmtime/gzip
EOF and unchanged DOS fingerprint pass before and after deletion. The active
cleanup producer log is explicitly excluded until terminal; old proofs remain
immutable. Two new FrontEnd programs and all older programs/sources stay live.
From DOS root, use python3 .analysis/reconstruction/probes/native-ring-v1379/verify_retention.py --restore before reading retired captures, fulltile pixels or relink objects;
without --restore it performs temporary complete readback. Old v1378 proof
retains its then-current509/9346e951 scope and cannot attest live8e77830c source.

## Marisa laser presentation color phase (v1380)

Observed MAIN_01_TEXT 0AAF:3704..37C7 (file F9F4..FAB7, 196 bytes)
loads DGROUP 2134:538C at 3786 and adds 8 for the GRCG color. It renders
before the complete update tail increments the frame modulo. The actual raw
laser blitter is 0AAF:1378..13DA (file D668..D6CA, 99 executable bytes);
the following alignment byte is outside this executable extent.

Runtime-observed execution of this caller and its actual STOSB/STOSW blitter
uses four complete, attested original Demo 2 DGROUP states. Recorded display
scroll selects the visible row; GRCG color/masks use an explicit adapter.
Every former game-area difference is palette index 8 versus 9 with the same
beam geometry: frames 1952/3379/3709/3996 differ at 4216/2967/2186/2015
pixels. All 11,384 pixels equal the original CPU beam color; the old native
pixel equals that color XOR 1. Full 256,000-pixel beam outputs are retained.
This accepts an adapted component observation, with physical scanout open.

Native State::frames() already includes the update tail. Using
8 + ((frames - 1) & 1) repairs this color phase. GNU and optimized UBSan
actual muted SDL-dummy idle OP→four demos→OP captures now have zero game-area
differences in all ten sampled Demo 2 frames. The five other nonzero samples
remain unchanged: Demo 1 frames 1/1952/3996 and Demo 3 frames 3379/3709.
All 40 full canonical text planes, 15,988 selected scalar/count boundaries
and 15,984 complete shake states/requests pass. All 125 complete files agree
between variants; complete parent state/shake traces remain byte-identical.
Full graphics/RGB samples remain diagnostic, with no crop or mask acceptance.
Initial background and circle effects, broader routes and scanout remain open.

Only view.cpp differs from v1379 among 509 producer inputs. Manifest:
f5791751c2473da2efaa4bf86e7265ce5c99f6ab23c4f1dc166248cd2b555cbf.
Both variants cold-compile that TU and relink attested unchanged dependencies;
this is a bounded build. Previous whole cold/69-CTest and complete-pool receipts
keep their original producers. The first parent receipt-path failure is retained
with its source and log. Frozen imported DOS/native readers independently
reproduce both complete shake receipts except their pinned source hashes.
No DOS product inputs, target bytes or historical exact acceptance change.
Fresh preflight and live MAIN database attestation pass; target provenance
remains candidate-local-attested.

Recipes: DOS-root .analysis/reconstruction/probes/native-shot-render-v1380/
attest_laser.py, build_frontends.py, run_validations.py, freeze_readers.py.
Receipts: native .analysis/port64/native-shot-render-v1380/. All heavy jobs use
CPU0/nice15 serial execution; all launches remain muted and headless.

## v1380 terminal validation and recovery

All v1380 jobs are terminal. Main 441/live Ghidra and native 345/target CI pass;
unavailable private native gates skip. Full parent/current sample hashes show
36 complete index/RGB samples unchanged. All 11,384 pixel changes in the other
four complete index pictures equal the actual original CPU beam and original
pixels on both variants. This further bounds the repair; whole pictures stay open.

Lossless retirement reclaims 156,069,888 allocated bytes (148.8 MiB) before
journal cost: 354 complete sample/capture/build files and 1,044 source-backed
caches. Full restoration/SHA/size/mode/nsmtime/gzip EOF, 17,815 protected
hashes, 509 source pins and unchanged DOS fingerprint pass before and after
deletion. The cleanup log is excluded while writing. Two new FrontEnd programs,
all old programs, frozen sources, original references and failures stay live.
From DOS root, restore retired inputs before CPU/graphics/reader/relink replay:

```sh
python3 .analysis/reconstruction/probes/native-shot-render-v1380/verify_retention.py --restore
```

Without --restore, it performs temporary complete readback. Old v1379 proof
retains its then-current 8e77830c scope and cannot attest live f5791751 sources.

## Whole-pool pellet color passes (v1381)

Observed MAIN_01_TEXT 0AAF:81F5..82FF (file 144E5..145EF, 267 bytes)
calls the complete white top pass before the complete purple bottom pass.
The actual leaves are 1EAC..1F3C (file E19C..E22C, 145 bytes) and
1F3E..1FA7 (file E22E..E297, 106 bytes). The intervening EVEN byte belongs
to the physical ASM owner and is outside either executable body.

Target instructions 1F2E/1F30 overwrite DGROUP 2134:86D2 coordinate pairs
with bottom VRAM and shifted-sprite offsets. The retained post-render DGROUP
list cannot be passed directly to the top renderer as left/top coordinates.
A bounded inverse recovers byte-column plus shift from sprite base 181C and
physical top row from bottom row minus three modulo 400. Executing the actual
top body must reconstruct every original post-top pair. Complete roundtrips
pass for all 60/98 pellets at Demo 1 frames 1952/3996.

Runtime-observed GRCG write-mask adaptation executes the same raw target leaves
with whole-pool passes and with per-pellet interleaving. The latter lets a later
white top overwrite an earlier purple bottom. All 8/32 changed pixels equal
original color 9 and former native color 15. Full 256,000-pixel results from
both target-body execution orders are retained. This does not accept physical
GRCG timing or complete original pictures.

Native view now finishes the 16px bullet sprites, draws all procedural white
pellet pixels, then all procedural purple pixels. GNU and optimized UBSan
actual muted SDL-dummy idle OP→four demos→OP close Demo 1 frame3996 32→0 and
frame1952 34→26. All 40 changes in the two complete index pictures agree with
the original CPU and original pixels; the other 38 full index/RGB hashes are
unchanged. All 40 full canonical text planes, 15,988 selected scalar/count
boundaries and 15,984 complete shake states/requests pass. All 125 capture files
agree between variants; complete parent state/shake trace bytes remain equal.

An independent negative probe executes the ordinary circle caller 0AAF:1C28
at all five formerly nonzero natural samples. Its pool has no alive records
and all calls issue zero raw GRCG circle requests. This excludes that ordinary
pool here; it does not exercise or accept the raw circle leaf. Remaining game-area
samples are Demo 1 frames 1/1952 (124439/26 pixels) and Demo 3 frames 3379/3709
(60/17). Their white-pixel and initial-background causes remain unproved;
full graphics/RGB/scanout and broader routes remain open.

Only view.cpp changes among 509 producer inputs; manifest:
fb26d5099584000e576c66c9dc5a7822ec64745c2b05058de6404e15b3481440.
Both variants cold-compile that TU and relink SHA-attested unchanged dependencies.
This is a bounded build; earlier whole cold/69-CTest/full-pool receipts retain
their own producers. Frozen imported DOS/native readers reproduce both complete
shake receipts except their separately pinned source hashes. Fresh preflight
and live MAIN database attestation pass; provenance remains candidate-local-attested.
No DOS inputs, target bytes or historical exact acceptance change.

Recipes: DOS-root .analysis/reconstruction/probes/native-circle-v1381/
inspect_circles.py, prove_pellet_passes.py, build_frontends.py, run_validations.py,
verify_pixel_change.py, freeze_readers.py. Receipts: native
.analysis/port64/native-circle-v1381/. Jobs run CPU0/nice15 serial; launches stay
muted/headless. The batch path preserves its initial circle investigation.

## v1381 terminal validation and recovery

All v1381 jobs are terminal. Main 441/live Ghidra and native 345/target CI pass;
unavailable private native gates skip. Full parent/current sample hashes show
38 complete index/RGB samples unchanged. All 40 pixel changes in the other
two complete index pictures equal the actual original CPU pellet passes and original
pixels on both variants. This further bounds the repair; whole pictures stay open.

Lossless retirement reclaims 156,139,520 allocated bytes (148.9 MiB) before
journal cost: 354 complete sample/capture/build files and 1,044 source-backed
caches. Full restoration/SHA/size/mode/nsmtime/gzip EOF, 18,924 protected
hashes, 509 source pins and unchanged DOS fingerprint pass before and after
deletion. The cleanup log is excluded while writing. Two new FrontEnd programs,
all old programs, frozen sources, original references and failures stay live.
From DOS root, restore retired inputs before CPU/graphics/reader/relink replay:

```sh
python3 .analysis/reconstruction/probes/native-circle-v1381/verify_retention.py --restore
```

Without --restore, it performs temporary complete readback. Old v1380 proof
retains its then-current f5791751 scope and cannot attest live fb26d509 sources.
