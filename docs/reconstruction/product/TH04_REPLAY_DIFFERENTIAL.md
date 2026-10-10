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
to v1366. Independent whole-file comparison changes only24 bytes in the12 DATA
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
