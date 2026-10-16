# Original DOS, reconstructed DOS and native fidelity

Updated 2026-10-16. The user's primary requested comparison
is original Japanese TH04 DOS versus reconstructed TH04 DOS. Native x64 also
must preserve game state and effects. These are two differential surfaces;
neither native host agreement nor successful native clears establishes them.

## Bounded ordinary video replay contract (v1438)

`compare_th04_ordinary_video.py` now admits the observed after-update terminal
contract used by the 7,500-update Boss prefix. It takes the frame count from
the attested capture receipt, checks terminal load/DGROUP/CPU context against
the video stream, and preserves the existing ABI, source, mapping, CRC and
complete-stream guards. The default Demo and ordinary extent remains 3,996.
Independent scalar baselines must have identical terminal class, extent,
dialogue cue and emulator configuration as well as product/reset identities.
Truncating both streams equally cannot satisfy the longer contract.

Public controls cover an explicit 7,500-record stream, refusal under the old
default or a longer requested extent, metadata truncation, terminal CPU drift,
mapping overflow, ELF bias, and mismatched baseline extent/dialogue/exit/config.
The video reducer still compares all 38 complete configured regions and counts
raw GDC differences separately. This tooling change alone establishes no new
Boss-picture or campaign acceptance. New builds/captures use a separate v1438
namespace; missing historical v1437 MAIN/MAP receipts remain unchanged.

## Actual bounded Boss combat and Game Over wait (v1437)

Root CI486 tests, catalog, tracking, private target/database and Oracle mutation
checks pass; final diff check passes.

The new after-update bounded contract extends ordinary capture without changing
the emulator observer or guest bytes. `--end-after N` keeps the attested Demo
terminal hook at DemoPlay, which ordinary mode does not call. All real L/I/R
records remain intact; no invented T record. A mapped frame-write watch stores
complete DGROUP and a real terminal snapshot atN. It contains current fields,
resident, CPU/segments, observed RNG counters and actual instruction bytes.
The host observer FILE is flushed with guest RAM/register/PIC preservation
checks; complete gzip streams close, then GDB kills this disposable capture.
This is an observed prefix, explicitly not a natural game/process exit.

Original terminal7500 is relative MAIN0AAF:01B3 `A3 8A 53`, load10FC,
CS1BAB, DGROUP3230. Relocated MZ/code, MAP owner, WORD-store operand, terminal
CPU PC, frame/stage/resident, full field shapes and every logged RNG counter are
checked. Complete DGROUP's last fields must equal the separate terminal. New
scalar samples are I0..N-1; the final after-update snapshot is not relabeled as
an I sample. Both final prefixes have exactly7500 updates/records. Old3996
Demo and ordinary contracts remain distinct; their tests continue to pass.

The initial original6000 prefix was valid but Boss stayed setup-only. An
unmodified9000 continuation waited at6548 while held Shot prevented an input
change. Normal Enter press/release device events after releasing Shot at that
observed stall advance the scene. Source dialog opcode'$' uses wait-for-change;
this interpretation is supported by successful real input, not actor or clock
patches. The same cue and source input producer drive original and candidate;
all consumed pre-update inputs and initial RNG/settings agree.

At7500 the actual battle has952 distinct Boss24-byte blocks, phases0/1/2,
HP range0..3050 and600 nonzero-phase samples from6900. Both cover five natural
losses. All36 pre-update fields and2,837 ordered RNG calls agree, including final
pending calls; nine complete pools and22 state owners agree through the longer
extent. The aggregate remainsfalse for258 end-of-update key_det samples. Full
Boss pictures, victory/teardown/campaign and physical/general input timing are
not accepted. A fixed index before the next natural event does not complete
those requirements.

The longer original attempt independently reaches **natural Game Over** at
7547 on the sixth hit, with remaining-lives1 before player_update. That routine
only decrements when rem_lives>1; otherwise it calls gameover_run(). A virtual
no-frame-progress diagnostic reads guest PC/RAM without altering them. At
5000ms it shows relative130E:00E3, inside frame_delay(1). Stack returns to
130E:0149 in input_wait_for_change's release loop, whose caller returns at
MAIN0AAF:3B1E. Target0AAF:3B19 is `9A 33 01 0E 13`, the actual Game Over wait0
call. DGROUP2AB2 Count1=0 is a single observation during that loop, not proof
that IRQ stopped. Held Shot blocks the release-first UI; do not misclassify the
wait as a Boss division/renderer hang, nor invent completion for a9000 timeout.
First incomplete attempts and immutable source variants are kept separately.

Public replay:

```sh
python3 scripts/probes/capture_th04_dos_ordinary_prefix.py --original \
  --end-after 7500 --dialog-at-frame 6548 --emulator-receipt PINNED \
  --font-bmp PRIVATE_FONT --output-dir NEW_ORIGINAL
python3 scripts/probes/capture_th04_dos_ordinary_prefix.py \
  --end-after 7500 --dialog-at-frame 6548 --build-dir FROZEN_NORMAL --map ITS_MAP \
  --emulator-receipt PINNED --font-bmp PRIVATE_FONT --output-dir NEW_CANDIDATE
python3 scripts/probes/compare_th04_bounded_ordinary.py NEW_ORIGINAL NEW_CANDIDATE \
  --original-main .analysis/targets/th04/main.exe --output /tmp/boss-prefix.json
```

Expected comparison exit1 retains the post-reset input mismatch; scalar,
actor_pools and global_states component flags aretrue. Optional
`--stall-diagnostic-ms 5000` records an incomplete wait snapshot, never a passed
prefix. Five actual terminal frame/exit/owner/opcode/RNG counterexamples reject;
six synthetic terminal tests independently reject malformed contexts. Complete
readonly pixel pairing was not performed for the longer battle.

Replay `.analysis/reconstruction/probes/dos-ordinary-boss-v1437/` routes source
variants, first6000, incomplete9000/dialog attempts, wait diagnostics, final7500
pair, controls and retention. Captures `dos-ordinary-boss-v1437-{original,
original-9000,original-dialog,original-diagnostic,original-7500,candidate-7500}`
are under `.analysis/runtime/candidates/`. Owned24paths/31blocks retire289.43MiB
net into1.69MiB anchored archive after SHA/CRC/full temporary size/mode/nsmtime
restores and protected readback. Compressed memory, opcode/stack diagnostics,
original/compiler/emulator artifacts, source and receipts stay live.
`recover.py --restore` restores the retired image/font/raw aliases.

Next pair Boss pictures and the natural Game Over/Continue/process surface;
complete reconstruction/native behavior remains the objective.

## Ordinary complete video and retained timing differences (v1436)

Root CI480 tests, catalog, tracking, private target/database and Oracle mutations
pass; final diff check passes.

The ordinary Normal ReimuA Stage1 fragment now has complete paired video
capture for3,996 actor updates, including both natural deaths/respawns.
All38 configured video regions are byte-identical: complete two-page/four-plane
VRAM262144B, TRAM16384B, analog768B/digital8B/text32B palettes, all modes and
configured GDC parameter/display fields. No game-area/tail/attribute mask.
Each raw279809B block also retains the full464B GDC structures. Those raw
structures differ onall3996frames: clock/raster/FIFO/drawing internals remain
outside accepted programmed display-state equality and physical scanout stays
open. This does not accept Boss combat/full stage/campaign/process transitions.

Video capture reuses the unchanged pinned read-only observer and the existing
ordinary keyboard adapter. It automatically includes DGROUP capture on the
same mapped actual frame increment. Its independent TH04OV1 gzip/XOR stream
records each frame/load/data/CPU identity and complete block, separately from
Demo contracts. First stage remains0. Initial/final extent, order, full bodies,
gzip EOF/CRC and all runtime video backing/page mappings are checked.

Fresh small compiler probe verifies535896B VGA_Type and232B PC98_GDC_state,
all configured offsets and15 ELF symbol widths, against12 archive/config
inputs and the retained observer's pinned compiler/binary. A single runtime ELF
bias and backing-memory page selectors are required. Source changes cannot
silently reuse that ABI receipt. No emulator/game rebuild, guest VRAM accessor
or register/clock/game-state write is performed by the memory observer.

Both original MAIN077440a3 and frozen normal MAINf21a5c7c start from identical
physical config/scores, original supporting products and all pinned archives.
They consume Shot20h/Shift0 and match all36 scalar fields and1,369 ordered RNG
calls, independently against frozen v1434 plain baselines. The full9-pool/22-state
companion also passes its component fields. Its aggregate is stillfalse for155
post-reset input samples; this new count belongs only to this producer, while
v1435's156 remains retained. The causes/timing interpretation remain inferred.
Video passed=true does not erase that companion failure.

All plane/page sequences vary: distinct-frame counts are1999/1998,1999/1998,
1999/1998,1999/1994 across B/R/G/E pages0/1. TRAM has1471 distinct blocks.
The three empty custom/circle/gather pools retain no active-path coverage;
Boss state remains setup-only. These coverage limits cannot become whole-game
acceptance through a full-frame count.

The full original3996-record video stream is read through CRC/EOF. Separate
bounded reducer controls use its first three actual frames:15 independent
last-byte plane/page, text, palette, mode and display-pitch flips reject at
frame2 in the intended region. A raw scan-address flip remains a counted raw
GDC difference without falsely changing programmed-state acceptance. Six public
protocol tests reject Demo magic, missing/duplicate/order, truncated body,
wrong stage, trailing data and CRC corruption. Existing pixel/region tests
continue to exercise every plane/page including unused tail bytes.

Replay namespace `.analysis/reconstruction/probes/dos-ordinary-video-v1436/`
binds `comparison.json`, companion `pools.json`, controls, fresh ABI receipt,
source snapshot and retention. Captures are `dos-ordinary-video-v1436-{original,
candidate}` under `.analysis/runtime/candidates/`. Public capture adds:

```sh
--video-stream --video-layout .analysis/reconstruction/probes/dos-ordinary-video-v1436/video-layout/receipt.json
```

`compare_th04_ordinary_video.py` uses the same original/candidate plus
`--original-baseline`, `--candidate-baseline`, `--baseline-sources`,
`--original-main` and `--output` arguments as the pool comparator. Video exits0;
companion pool comparison exits1 because its input-sample mismatch is retained.
All complete video/DGROUP records remain compressed and live (~30.52MiB video
and2.53MiB DGROUP per program), preserving raw diagnostics and further owners.
Owned8-path/20-block HDI/font/raw-trace retirement releases90.18MiB net with
0.90MiB anchor archive; original HDI is unchanged. SHA/CRC/full temporary
size/mode/nsmtime recovery and protected proofs pass before deleting aliases.
`recover.py --restore` restores captured images/raw traces. Eight explicitly
restored v1434 baseline aliases were checked and returned to archived state,
removing91.07MiB temporary expansion (not additional new net reclamation).

Next: longer ordinary Boss/process capture, then paired original/native full
pictures. Full hardware timing, cross-emulator and Windows remain separate.

## Ordinary complete pools and input phase frontier (v1435)

Root CI474 tests, catalog, tracking, private target/database checks and Oracle
mutations pass; final diff check passes. Aggregate runtime rejection below
remains independent of those control-plane gates.

The new `--dgroup-stream` capture composes an independent read-only memory
monitor with the ordinary keyboard adapter. A watch on the attested observer's
MAIN process counter arms a mapped stage_frame watch. Every actual increment
1..3996 captures all65536 DGROUP bytes, CPU load/data segments, paging state
and complete logical/physical page mappings. Frames are XOR-delta gzip encoded
under a separate ordinary TH04OG1 contract. No Demo rotation/replay assumption
is used. BSS zeroing, contiguous increments, exact extent, full bodies and
footer/CRC are checked; full uninterpreted bytes remain recoverable.

The frame write follows actors/render, reset-sense, slowdown wait, scroll,
page flip and sound update, before modulo counters and score update. Target-derived
nine clear-call extents and candidate MAP/clear-helper guards attest the pools;
22 state extents retain their separate target/candidate instruction witnesses.
Every byte, including inactive records/padding and enemy ES-relative script
offsets, is compared. Callback/code pointers outside those owners are excluded
from claimed state; complete DGROUP bytes are kept without normalization.

Nine pools and22 states agree at all3996 frames. Whole extents are shots1224B,
enemies2048B, sparks1536B, bullets11440B, custom_entities832B, circles160B,
items640B, pointnums6400B and gather_circles672B. Raw changing-frame counts are
3895/3023/1400/1619/0/0/1451/421/0 respectively. These counts show byte changes,
not active entity counts. The three zero pools have no active-branch coverage.
Both natural deaths/respawns are covered; Boss remains setup-only.

**Aggregate passed=false remains authoritative.** Post-reset Shift and stage
graze match, but key_det differs at156 frame-write samples. First is frame5,
after update4, original20h/candidate0. The ordinary next loop calls input_sense
at MAIN0AAF:00AE→130E:06C4 before the pre-update input seam; target Shot OR
is130E:075D `83 0E 74 39 20`. Consumed inputs and all36 scalar/RNG fields still
match each other and their independent v1434 no-DGROUP baselines. Later OR-sense
is observed; CPU/IRQ/autorepeat phase as the cause of intermediate differences
remains inferred. Physical timing and general input equivalence stay open.
Do not drop the post-reset field to turn the aggregate green.

The initial stream pair was also inadmissible: original consumed frame1 had0
instead of Shot20h, candidate and independent baseline had20h. Final transport
queues Shot at the observed menu trigger's+2200 virtual milliseconds, after the
last Return release and before MAIN loads. Only keyboard device API calls are
used; guest RAM/CPU/segment/PIC guards remain. Both final scalar controls pass.
First source/receipts/streams and explicit rejection remain retained.

Historical baselines bind their actual frozen controller source bytes through
an explicit source snapshot. Changed current controller text cannot silently
restamp an older execution. Live unchanged emulator/header sources retain their
original pins. Baseline images/trace aliases are temporarily restored from the
v1434 anchor archive, checked, then returned to their archived state.

Original complete self-control and nine single tail-byte pool counterexamples
fail exactly at frame1000 in the intended pool; inactive record bytes are also
covered. Six public protocol tests reject missing/duplicate frames, truncated
final body, wrong stage, trailing records and gzip CRC failure. Full pictures,
Boss combat, process transitions, cross-emulator/Windows and complete campaigns
remain outside acceptance. No product C++/ASM source or exact ledger changed.

Replay namespace `.analysis/reconstruction/probes/dos-ordinary-pools-v1435/`
contains final `comparison.json`, `controls.json`, first failure, source snapshot
and retention. Final captures are `dos-ordinary-pools-v1435-v2-{original,candidate}`
in `.analysis/runtime/candidates/`. Public pool command:

```sh
python3 scripts/probes/compare_th04_ordinary_pools.py ORIGINAL_STREAM CANDIDATE_STREAM \
  --original-baseline ORIGINAL_PLAIN --candidate-baseline CANDIDATE_PLAIN \
  --baseline-sources FROZEN_SOURCE_TREE --original-main .analysis/targets/th04/main.exe \
  --output /tmp/ordinary-pools.json
```

Expected exit1 reflects the retained post-reset input mismatch. The report
separately binds actor_pools_passed=true/global_states_passed=true and
post_reset_input_passed=false. Original/candidate scalar controls pass.
Owned16-path/25-block anchor retirement releases181.04MiB net with1.10MiB
archive after full SHA/CRC/temp metadata restores and protected readback.
Already-compressed full DGROUP streams remain live. `recover.py --restore`
restores images/raw traces. Eight explicitly restored v1434 aliases were
re-deleted after SHA/mode/nsmtime checks, removing91.07MiB temporary expansion;
this is not additional net reclamation. Original targets, HDI anchor, compiler/
emulator, frozen programs, source and all receipts remain protected.

## Ordinary keyboard boundary and repeated state pairing (v1434)

Root CI passes468 tests, tracking, catalog, private target/database checks and
Oracle mutations; final diff check passes.

Two independent original/reconstructed DOS Stage1 pairs now pass3,996 completed
updates each. Original MAIN077440a3 and frozen ordinary MAINf21a5c7c consume
Shot0020/Shift00 in3,997 pre-update samples (0..3996) plus one terminal. All36
configured state fields and1,369 ordered RNG calls agree per pair. Original
v7→v8 and candidate v7→v8 repeated comparisons also pass. Both have resident
miss_count0→1→2, two hit samples,142 respawn samples and896 Midboss-active
samples. Boss24-byte state remains constant setup. Whole ordinary actor/effect
pools, pixels, Boss fights and full campaign/process parity remain unaccepted.

The input trigger is an **observation** of original OP's own menu counter
increment, not assignment of a seed. Fresh attested original stub replay at
loads1000/2000 gives69028 normalized payload bytes/804 observed relocations,
SHA13222cb6. OP main0A74:0C37..0D5E body SHA is c61aada7; its0D2F instruction
`66 26 FF 47 14` increments DWORD ES:[BX+14], the resident.rand field.
DGROUP is0F34 and the preceding LES reads its far pointer at1A64. These are
payload observations; no packed-file exactness or pristine provenance claim.

GDB hardware-watches mapped RAM after locating a unique aligned HUMAConfig
resident with legal rank/configuration. Before MAIN initializes credits, use
cfg_lives/cfg_bombs at3A/3B, not remaining/credit life fields. VM86 paging is
walked through host RAM; a raw physical MemBase scan does not locate this
logical resident reliably. Counter reaching64 queues Enter through the unchanged
`KEYBOARD_AddKey(KBD_KEYS,bool)` API. Runtime first-key snapshots independently
bind CS:IP=1B70:0D2F (OP load10FC), DS2030, ES:BX=9FEF:0000 and resident9FEF0.

Subsequent Enter press/release events use virtual PIC deadlines relative to
that observed boundary. After MAIN's attested full-module entry record, the
adapter queues held Shot and disables its watches. Mapped conventional640KiB,
48-byte guest CPU registers,136-byte segment state and PIC time are unchanged
before/after every API call. Keyboard device queue/IRQ changes are intended
input. This is a headless emulator API adapter; no OS/Windows input or physical
CPU/scanout/timing acceptance follows. Actual keyboard/PIC/ABI source agrees
with the pinned emulator archive. Observer binary/core/config are unchanged.

Absolute PIC millisecond scheduling alone is disproved for this fixture:
repeated original runs enter MAIN with seeds1C/1D. The older v1433 wall-clock
pair's3F/33 rejection remains. Batch GDB post-event delivery, C-language bool
parsing, raw physical resident scan and pre-MAIN credit-field detection failures
are retained separately. Their zero/partial/Demo captures are not ordinary
acceptance. All four accepted v7/v8 captures observe and enter with seed40h.

`ordinary_profile()` previously aliased Demo's global hook list. A second
original profile within one interpreter then failed its Demo terminal guard.
It now copies hooks before changing the terminal. Full repeated readbacks pass;
a private target-backed test also preserves the original Demo profile.
Seventeen focused tests and actual original self/repeat controls pass. Six
input/initial-RNG mutations reject before state verdict; an admitted hit
mutation at1600 fails at that field. Five actual-record keyboard trigger/owner/
IP/register-extent/time counterexamples reject. Runtime pointers and resident
performance counters remain raw evidence outside the compared state scope.

Public replay uses a fresh output directory for each run:

```sh
python3 scripts/probes/capture_th04_dos_ordinary_prefix.py --original \
  --emulator-receipt .analysis/runtime/emulators/demo-observer-build-v1365/receipt.json \
  --font-bmp PRIVATE_FONT --output-dir .analysis/runtime/candidates/NEW_ORIGINAL
python3 scripts/probes/capture_th04_dos_ordinary_prefix.py \
  --build-dir FROZEN_NORMAL_BUILD --map ITS_ATTESTED_MAP \
  --emulator-receipt .analysis/runtime/emulators/demo-observer-build-v1365/receipt.json \
  --font-bmp PRIVATE_FONT --output-dir .analysis/runtime/candidates/NEW_CANDIDATE
python3 scripts/probes/compare_th04_dos_ordinary_prefix.py \
  .analysis/runtime/candidates/NEW_ORIGINAL .analysis/runtime/candidates/NEW_CANDIDATE \
  --original-main .analysis/targets/th04/main.exe --output /tmp/ordinary-prefix.json
```

Replay namespace `.analysis/reconstruction/probes/dos-clock-input-v1434/` binds
source/API attestation, fresh OP payload, v7/v8 pairs, full repeat/mutation controls
and failures. Accepted captures are `dos-clock-input-v1434-v8-{original,candidate}`
in `.analysis/runtime/candidates/`. Only MAIN is replaced; original OP/MAINE/ZUN,
all archives and starting physical config/scores are checked by the comparator.
No C++/ASM build or historical exact promotion is part of this batch.

Owned40-path/19-content retirement initially reclaimed349.96MiB with89.17MiB
archive. A fully verified second compaction reuses unchanged pinned HDI
SHA0d5ea773 as an anchor and stores only differing64KiB chunks plus other blobs.
All40 reconstructed contents, sizes, modes/nsmtime and protected inputs pass
before deleting the superseded full archive. The final1.51MiB archive reclaims
another87.66MiB, about437.6MiB total. `recover.py --restore --prefix PREFIX` in
the replay namespace restores images/traces losslessly; `compaction.json` binds
the original retention journal and anchor. The original HDI is never written.
`verify_retention.py` is the historical first-format reader; use `recover.py`
for current recovery. Sources/programs/receipts remain live. Next: complete
ordinary actor/effect capture, longer Boss combat and process lifecycle.

## Ordinary Stage 1 prefix and rejected admission (v1433)

Original MAIN077440a3 and frozen ordinary producer1426 MAINf21a5c7c each
complete Normal ReimuA Stage1 through frame3996. Original OP/MAINE/ZUN stay
identical; legal physical MIKO.CFG options010600020101 use rank1/lives6/bombs0.
All game-data archives and starting scores/configuration are checked. Inputs
are real held Shot from a private owned TCP-disabled Linux Xvfb, muted; no
resident/actor/hit/score/clock writes. This adapter is separate from the unchanged
read-only observer. Both runs consume Shot0020 and raw Shift00 throughout.

Observer I is original MAIN0AAF:00B7, after the indirect input callback and before
actor update. Its ordinary terminal is the actual following JZ at0AAF:00BC,
not DemoPlay. Both sites are instruction-guarded; candidate MAP places them at
0708:066D/0672. Existing kind2 frame3996 predicate stops before that frame's actor
update. There are3997 I rows (0..3996), one identical T row and3996 completed
updates; do not reuse the Demo comparator's rotation/extent contract.

Both relocated complete MAIN modules equal their own executable plus MZ
relocations. All36 fields and RNG call counters/addresses are read back. Each
run has two nonzero hit samples,142 respawn samples,40 distinct miss-time values,
and resident miss_count0→1→2. Midboss active varies; Boss's24-byte state stays
constant setup. Original has925 observed RNG events, candidate1268.

These event totals **do not establish a source mismatch**. Entry resident.rand
is0000003F original versus00000033 candidate; initial LCG bytesac6e5001 versus
3056c70f and initial randring differ. The new admission gate rejects the pair
before any state verdict. Wall-clock menu-key timings produce different OP
seeds. Next bind ordinary start input to a guarded original OP virtual tick;
never set RNG directly. Longer capture remains necessary for actual Boss combat.

The comparator independently checks images, original supporting products and
archives, starting physical files, MZ relocation, MAP/instruction-derived field
ownership, contiguous samples, full ordered RNG counters and terminal extent.
Matching consumed input/stage and initial RNG/settings are required. Actual
original self-comparison passes; six single input/RNG perturbations are rejected
before state comparison, and a hit perturbation at1600 is reported as an admitted
state failure. Nine public tests cover these admission distinctions. Full actor
pools, pixels, resident performance counters and full campaign remain outside
this prefix's scope; runtime pointers are retained separately.

Two failed Xvfb auto-display starts have zero game samples. A diagnostic v3
includes an external Return and is not the replayable v4 pair. Auto-display
failed to create its listener; an explicitly owned display14333 passed process/
owner/TCP-disabled checks. SDL's X11 backend is available. All attempts remain
recorded; no failure is relabeled as accepted gameplay.

Replay namespace: `.analysis/reconstruction/probes/dos-ordinary-prefix-v1433/`.
`capture-v4.py`, `controls.py` and the public comparator reproduce this bounded
experiment. `comparison.json` returns admitted=false/first_difference=null.
Completed captures are `dos-ordinary-prefix-v1433-v4-{original,candidate}` below
`.analysis/runtime/candidates/`. Owned18-path/9-blob retirement releases181.84MiB
net;37.42MiB archive, content hashes/CRC/temp metadata restore/protected proofs
all pass. `verify_retention.py --restore` restores the required images/raw traces
before rerunning:

```sh
python3 scripts/probes/compare_th04_dos_ordinary_prefix.py \
  .analysis/runtime/candidates/dos-ordinary-prefix-v1433-v4-original \
  .analysis/runtime/candidates/dos-ordinary-prefix-v1433-v4-candidate \
  --original-main .analysis/targets/th04/main.exe --output /tmp/ordinary-prefix.json
```

Expected exit1 is the explicit admission rejection, not a crashed capture.
Root CI passes460 tests, catalog, tracking, private target/database checks and
Oracle mutations; diff check passes. The original candidate-local-attested
provenance gap remains.

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

## Item-spawn splash state and foreground dots (v1382)

Observed MAIN_03 13A9:0486..049F clears 80 bytes at DGROUP 2134:41F6
and the separate cursor at 4250. The ten bytes at 4246..424F are separate
storage. 04A0..04E5 admits the selected eight-slot ring entry and advances
its cursor even when busy; admitted state has radius/previous32 and time16.
The physical suffix includes the two following alignment bytes. 04E8..0521
ages nonfree records by32, retaining previous radius and removing at512;
flag2 becomes free on the next update. The time byte remains unchanged.
Original items_add creates a splash only after admitting an ordinary item.
The separate miss-drop producer does not use that path. items_update ages
splashes after the complete item-slot loop.

Actual original render 0AAF:168C..170E (file D97C..D9FE,131 bytes) uses
64 four-angle increments, actual vector2_at, signed-word coordinate wrap,
subpixel playfield rejection and the actual scroll helper. Its raw dot leaf
0AAF:1842..185D (file DB32..DB4D,28 bytes) issues one byte mask per point.
The GRCG color/mask adapter retains full256000-pixel output and ordered dots.
Native typed Splashes now joins item Pool allocation/update/reset and draws
white dots before item sprites, retaining all record fields and ring admission.

311 original CPU state/ordered-dot controls per GNU/optimized UBSan compare
full81-byte state, wrapped/negative radius/center/flag cases and three captured
natural states; ten reserved sentinel bytes remain unchanged. Actual muted
SDL-dummy idle OP→four demos→OP agrees on all15984 full81-byte records,
including inactive fields and cursor. Active frames are1146/688/1192/904;
all eight cursors occur per demo. Missing/duplicate lastrow, lastcursor,
lastinactive-radius and firstframe controls all reject. Frozen imported DOS/
compiled-native readers reproduce splash and shake receipts on both variants
except separately pinned ownsourceSHA.

All103 changes across three full256000-index actual samples equal original
white dots: Demo1frame1952 26→0, Demo3frames3379/3709 60/17→0. The other37
entire index/RGB sample hashes remain unchanged. All40 full canonical text
planes,15988 selected scalar/count boundaries and15984 full shake states/
requests pass. All126 entire capture files match between hosts; complete parent
state/shake trace bytes remain identical. Fresh current-producer nine full
actor/effect pools pass15984x24952B, retaining inactive/spare bytes and translating
only enemy script IDs to original STD-relative offsets. The missing splash
owner was outside those nine pools; scalar equality could not detect it.

The first direct CPU-mask decode with recorded GDC line rejected. Actual helper
DGROUP4278 reads drawing scroll300/40/275, while programmed display lines are
301/41/276 at these seams. Drawing-relative dot geometry explains the pixels;
physical GDC command/scanout mapping remains unaccepted. The failed assertion,
subsequent owner-size decode failure and frozen-source ROOT import failure
remain retained with their source/logs. The successful replay uses a freshv3
owner and distinctv2 component directories, preserving all failed artifacts.
No copied bitmap, original DS painting or picture crop/mask enters the product.

The producer pins509 inputs, manifest
add39f3c33de91719b93c0510350b09223ec973612ebaf45b317b1dec400b44c.
Five inputs change: item_pool.cpp/.hpp,view.cpp,demo_picture_frontend_checks.inl
and verify_demo_pictures.py. The Pool header/layout change invalidates earlier
native core binaries. Fresh GNU cold build has71 programs and69 passing CTests;
optimized UBSan cold core/game/trace/shake yields3 programs with no fullUBSan
CTest claim. All new programs and full source snapshots retain this producer.
Older products keep their own source identities. DOS inputs/fingerprint,
original targets and historical exact acceptance remain unchanged; provenance
stays candidate-local-attested. Fresh preflight/live MAIN attestation pass.

39 of40 sampled game areas now have zero differences. Demo1frame1 remains
124439 pixels; initial background and all complete picture margins/cache/RGB/
physical scanout, broader Boss/death/process/Windows pairing remain open.
Recipes: DOS-root .analysis/reconstruction/probes/native-white-v1382/
inspect_splashes-v3.py,build_native.py,verify_splashes-v2.py,validate_remaining.py,
compare_splashes.py,verify_pixel_change.py,reader_controls.py,freeze_readers.py.
Receipts: native .analysis/port64/native-white-v1382/. Jobs stay CPU0/nice15,
serial, muted/headless. Full pools are already gzip-restoration verified.

## v1382 terminal validation and recovery

All jobs are terminal. Main441/live Ghidra and native345/target CI pass;
unavailable private native gates skip. GNU cold71 programs/69CTest and UBSan
cold3 targets remain pinned; full81-byte splash/nine-pool/scalar/shake/text,
five malformed-trace rejection and frozen-reader controls pass. No Windows,
physical scanout, full pictures or historical exact promotion is accepted.

Lossless retirement reclaims 193,658,880 allocated bytes (184.7 MiB) before
journal cost: 975 complete sample/capture/build files and 1,044 source-backed
caches. Complete restoration/SHA/size/mode/nsmtime/gzip EOF, 22,622 protected
hashes, 509 source pins and unchanged DOS fingerprint pass before and after
deletion. Two complete native-pool streams already reclaimed 774,946,816
allocated bytes after full gzip restore/SHA/length/EOF verification. Combined
net allocated recovery is 968,605,696 bytes (923.7 MiB) before journal
cost. All71 GNU/3 UBSan programs, both component probes, old programs, frozen
sources, original references, full pool archives and failed attempts stay live.
The cleanup log is excluded while writing; previous proofs remain immutable.

From DOS root, restore retired samples/build inputs before CPU/graphics/reader
replay with python3 .analysis/reconstruction/probes/native-white-v1382/verify_retention.py --restore.
Without --restore it performs temporary complete readback. Old v1381 proof
retains its fb26d509 source scope and cannot attest current add39f3c inputs.
Native full pool gzip archives are already complete and require no new capture.

## Stage4 background publication and tail copies (v1383)

Target-observed MAIN_01_TEXT 0AAF:0098..0212 (file C388..C502) calls
non-Bomb background through DGROUP 2134:4268 at 00DE, before stage_render
through 432C at 0113. Actual original initial fill 0AAF:0FB2..0FFC,
full-tile loop 20C8..2109 and carpet callback 3FF4..40FD explain the first
Demo 1 discrepancy. Its fixed inactive page still contains the initial MAP;
its fixed active page adds actors to that background. The callback changes the
ring afterward. All 124,439 old game-area differences are pre-callback versus
post-callback background pixels. GDC page selection is never chosen for fit.

Runtime-observed 0AAF:0FFE..10B3 (file D2EE..D3A3, 182 B) copies the tail's
combined current/previous integer row advances using the post-callback and
refilled ring. Forty-eight actual CPU controls, heights 1..16, retain ordered
source/destination WORD requests across tile-row and 400-row wrap. EGC latch
and hardware setup are explicit adapters; larger heights and physical scanout
remain unaccepted. The snapshot-only e516f7f3 intermediate closes the 40 game
area samples but adds 2,100 incorrect edge pixels. It is retained and not
promoted. This counterexample requires preserving both publication surfaces.

Native view now retains the ordinary draw's carpet ring, then substitutes the
post-tail ring only for copied physical rows. No first-frame special case or
actor/RNG/score workaround is introduced. One input changes among 509:
port64/view.cpp; final manifest
50ca49c65df70cc75b5807df0a3e218dcdaba5a847e780092ed1618bd2fc6496.
GNU and optimized UBSan cold-compile that TU and relink with SHA-attested
unchanged v1382 core/main/audio/ymfm objects. The earlier whole cold build,
69 CTests and full nine-pool comparison keep their v1382 producer identities;
this is not a new whole-current cold/CTest/full-pool claim.

Actual muted SDL-dummy idle OP→four demos→OP agrees at all 15,988 selected
scalar/count boundaries, 15,984 full shake states/requests and 81-byte splash
records, and 40 complete 8,000-byte canonical TRAM samples. All 126 entire
capture files match between GNU and UBSan; parent scalar/shake/splash traces
remain byte-identical. All 40 standard sampled game areas now have zero
differences. First-frame full-picture differences fall 224,211→94,316 and
second-frame 97,672→94,316: all 133,251 changed pixels equal the fixed original
page, including 124,439 first-frame game-area pixels and 3,356 second-frame
edge pixels. Other 38 entire index/RGB samples remain unchanged. Full graphics,
margins/cache/RGB, physical GDC/scanout and broader routes remain open.

Three separate instrumented GNU producers retain immutable before/intermediate/
final sources and programs, changing only ten capture frame numbers. Complete
original Demo 1 VP3 stream/source/CRC/EOF checks cover all 3,996 records. The
additional lighting samples 1663/1664/1665/1666/1667/1668/1696/1697/1728/1729
all agree on game area and complete text. Frame 1666 repairs another 7,498
pixels. Their complete scalar/shake/splash traces equal final ordinary GNU.
These ten samples have separate producer identities and do not turn 40 ordinary
samples into full native video acceptance.

First incorrect callback-address assertion, omitted archived-reference path,
39-unchanged-picture assumption, and missing retired VP3 images are retained.
Separate corrected readers restore only required immutable inputs. Old producers
and recipes are not restamped. A temporarily stopped verified reader resumes
only after both compiler jobs are terminal, preserving its original live handle.

Recipes: DOS-root .analysis/reconstruction/probes/native-initial-v1383/
for ownership/counterexamples; native-initial-v1383-v2/ for final builds,
run_validations.py, verify_pixel_change.py, phase_control.py, verify_phase.py
and frozen reader replay. Receipts: native .analysis/port64/native-initial-v1383-v2/.
All heavy work uses CPU0 at low priority; all actual launches are muted/dummy.
No DOS source, original target or historical exact acceptance changes.

## v1383 terminal validation and recovery

All jobs are terminal. Main 441/live Ghidra and native 345/target CI pass;
unavailable private native gates skip. Final ordinary GNU/optimized UBSan and
separate extra GNU lighting controls, fixed-page full changed-pixel checks,
48 actual tail-copy controls and frozen reader replay pass. Only view.cpp
changes; v1382 whole-cold/69CTest/full-nine-pool producers stay separate.

Lossless retirement reclaims 455,786,496 allocated
bytes (434.7 MiB) before journal cost:
1,073 complete sample/capture/build/restored-image files and
1,044 source-backed caches. Full temporary restoration,
SHA/size/mode/nsmtime/gzip EOF, 24,916 protected hashes,
509 source pins and unchanged DOS fingerprint pass before and after deletion.
All seven new ordinary/diagnostic programs, old programs, frozen sources,
failures, complete original references and full pools remain retained. The
snapshot-only intermediate and reader failures are not restamped or promoted.

From DOS root, restore archived sample/build/image inputs before replay:

```sh
python3 .analysis/reconstruction/probes/native-initial-v1383-v2/verify_retention.py --restore
```

Without --restore it performs complete temporary readback. Old v1382 proof
keeps its add39f3c source scope and cannot attest current 50ca49c6 inputs.
Whole native pictures/cache/margins/RGB/scanout/broader gameplay remain open.

## MPN palette ownership and full RGB composition diagnostics (v1384)

Target-observed MAIN 0AAF:03E0..06DF stage setup calls MPN_LOAD at
0AAF:0E0C..0E80 after the stage's temporary BMT/BFT palette. Two compiled
call sites at 05D9/0651 share the other stages' tail. Shared 130E:0189..01AD
MPN_PALETTE_SHOW and 01AE..0240 MPN_LOAD_PALETTE_SHOW preserve the six-byte
header followed by 48 RGB bytes. All 40 complete original analog-palette
snapshots equal the selected MPN high nibbles: ST03/ST10/ST02/ST01. Marisa
Stage1 uses ST10; its earlier yellow color zero is also overwritten. The first
probe incorrectly expected eight unmerged calls and decoded load-linear offsets;
it remains failed, with a separate segment-aware v2 reader.

Native now selects the final MPN palette, including Stage1 playchar selection
and subsequent stage installations. Only view.cpp changes among 509 source
inputs (manifest ba6eff48774660b31367e68f4674362defed48110b666a7ed5cf410efa951839).
GNU and optimized UBSan cold-build that TU/relink using attested unchanged
v1382 core/main/audio/ymfm objects. Whole-current cold/69CTest/full-pool and
ordinary Boss-route acceptance are not claimed.

Both actual muted SDL-dummy OP→four demos→OP producers have 126 identical
complete capture files. All 40 entire graphics-index and canonical TRAM samples
remain unchanged, preserving their zero sampled game-area differences. Six
complete state/shake/item-splash/display/save hashes equal their v1383 parent;
the parent's 15,988 selected boundaries and 15,984 shake/splash comparisons
keep their separate original reader identity. MPN selection changes 720,358
actual full-picture sample RGB pixels.

The independent compositor compiles unchanged line rendering, font BMP loading,
text-row logic and GDC address stepping from the pinned DOSBox-X archive
199aa35f (archive d990ece1…, binary 6e1a6e70…). Seven complete source files
equal the archive. g++8 SHA9cab0384… reproduces sizeof232 and all old offsets,
including newly checked master cursor_blink_state offset196. It retains all
40 complete 640×400 RGB outputs for captured, forced-visible and forced-hidden
blink; fixed captured pages are used, without cropping or hiding cache bytes.

Full raw emulator RGB still differs in 28 samples: 12 raw-zero samples are
the initial curtains. The pinned emulator's 4→6→8 bit replication yields,
for example, 6→25→101 and 8→34→138, versus native 102/136. An explicit
diagnostic projection to 17×n leaves exactly five 556-pixel differences:
Demo1/3709, Demo2/3379, Demo4/1952,3379,3996. Captured master blinkstate0
suppresses the DEMO PLAY glyphs there; native currently ignores attribute bit2.
Forced-visible blink plus that diagnostic projection gives 40 zeros. This is
neither raw equality nor complete-picture acceptance. Native DAC conversion is
unchanged; recovering the independent refresh/blink clock is the next owner.

Font RAM is reconstructed from pinned FREECG98.BMP and GAMEFT.BFT, with explicit
text-scroll/CRT defaults. Those additional registers and live CG mutations
were not captured, and programmed-frame reconstruction does not attest physical
scanout. Capture those surfaces and the blink clock before broader acceptance.
No original executable, DOS product input or historical exact state changes.

Recipes: DOS-root .analysis/reconstruction/probes/native-composite-v1384/;
receipts/sources/programs: native .analysis/port64/native-composite-v1384/.
prepare.py restores 200 complete old inputs into a fresh namespace, leaving
v1383 proofs immutable. Preparation and composition producers reserve fresh
output namespaces. For existing capture-reader replay, restore retired inputs
then use compare_final.py and verify_control.py. The independent
replay_compositor.py instead temporarily recovers only 41 archived inputs,
reproduces all 120 complete RGB hashes and rejects analog-nibble/blink controls
(the latter changes 556 pixels), then removes all temporary files. It needs no
permanent restoration. The post-retirement reader and receipt have separate
source hashes and do not expand the earlier protected inventory.

## Independent text blink clock and attribute order (v1385)

Runtime-observed original VP3 streams contain 15,984 complete master/slave GDC
blink triples. The thin reader checks all 279,809 bytes of each XOR record,
CPU/load/DGROUP headers, complete stream SHA and gzip CRC/EOF, reproducing all
40 parent samples. Both GDC triples agree; rate is 32, states 0..3 and counts
0..31. Modulo-128 refresh deltas include zero at Demo1/2 and Demo3/1968,
and two at Demo3/1954 and /1963. These are residues, not proof of absolute
unobserved time. Display refreshes cannot be replaced by the Demo frame number.

The unchanged pinned DOSBox-X cursor_advance source provides a separate
compiler/runtime Oracle. Its state0 hides blinking text for 32 refreshes and
states1..3 show it for 96. Native MAIN now supplies its persistent display
clock to both text-overlay APIs. Headless admission includes slowdown;
Linux/Windows source paths use monotonic elapsed time at the existing
17,730,496 ns period. OP, waits and MAIN replacement preserve the counter.
Repaint and host catch-up admissions do not advance it twice. The initial
zero is a native epoch; original boot phase is not calibrated. Physical
Windows remains untested, and other TextPlane callers retain the default
visible phase until their owner is independently handled.

For mask0x02 blink, the font becomes zero before reverse mask0x04, preserving
reverse cells when hidden. Eight secret/blink/reverse cases and 80 complete
640×400 text-layer pairs agree with the unchanged independent DOSBox-X line
emitter. Both native RGB and ARGB agree in all 88 cases. This controlled
Oracle explicitly uses zero graphics, black graphics palette and reconstructed
BMP/GAMEFT font RAM. Live CG mutations, text-scroll/CRT and scanout are not
accepted. The first reporting script failed only while writing its receipt;
its script/log remain retained and separate corrected v2 replay passes. The
first instrumented clock adapter also lacked <cstring>; its failed sources/log
are retained and a separate v2 observer adds that include. Product inputs stay
unchanged by these private corrections.

Four source inputs change among 509, manifest
a47f0496c18261ff4650515b1c2cd6413451a44d8879b6b3b21fc032aec89c6f. GNU is a fresh whole cold build of all
71 programs with all 69 CTests passing. Optimized UBSan cold-builds the game,
trace and shake targets, without a full UBSan CTest or new nine-pool claim.
Actual muted SDL-dummy OP→four demos→OP produces 127 identical complete
GNU/UBSan capture files. All 40 entire indices/TRAM and six parent state,
shake, item-splash, display and save hashes remain unchanged; prior original
readers and complete nine-pool producers retain their identities.

All 15,988 native refresh rows replay the unchanged original counter. A
separate instrumented FrontEnd checks 17 logical refreshes, nine host-time
jumps including a 12,800-refresh stall, repeated repaint, double admission and
backwards time; its 127 common capture files remain identical. Phase-inversion
and per-Demo reset controls reject. Native sample phases are fixed by this
trace, never chosen to minimize original picture differences.

Blink changes 2,780 sampled RGB pixels. Full 640×400 raw RGB versus
captured original phase has 12/40 zeros; the explicit DAC projection has
32/40 zeros. Fixed native-phase projection has 40/40 zeros. The captured-phase diagnostic unequal sample count grows from five to eight,
because native and original epochs are still distinct. This implements the
blink rule without claiming original-phase agreement. All raw
mismatches remain recorded; this does not establish whole-picture, original
absolute phase or physical scanout acceptance. Next capture live CG RAM and
text-scroll/CRT surfaces and recover original absolute refresh/scanout timing,
then extend paired ordinary Boss/death/process routes. No DOS product input or
historical exact state changes; candidate-local-attested provenance remains.

Recipes: DOS-root .analysis/reconstruction/probes/native-blink-v1385/;
receipts/programs/frozen inputs: native .analysis/port64/native-blink-v1385/.
read_clock.py, verify_overlay_v2.py, clock_frontend_v2.py, compare_final.py and
verify_control.py retain their distinct source identities. Restore retired
inputs before replay. v1384 ba6eff48 proofs cannot attest live a47f0496 source.

## Live FONT, text/CRT registers and original refresh time (v1386)

A new complete original VP4 capture extends the previous complete-update seam
at MAIN 0AAF:00B7 / terminal 0AAF:0975 (load10FC, DGROUP3230). It retains the
same original executable, 24,000-cycle muted emulator, reset files, image and
ordinary observer. Each of 15,984 records now carries 808,255 bytes: the full
VP3 video block, actual 516 KiB FONT, eleven text/CRT bytes and 51 raster/time
bytes. The actual compiler confirms vga+312 FONT size528384, 27 ELF symbols,
old ABI and cursor/width/time offsets; all source/target/stream/header/CRC/EOF
and complete starting-image readbacks pass. No emulator or product rebuild.

All 15,984 FONT snapshots share SHA-256
4619804429e024bb4e3770b242408797f25425c42c8fc1822afdbaff9bec147e.
The earlier BMP/GAMEFT directwrite model differs in exactly 32 bytes,
0x560..0x57F: ANK V/W. Its writes skipped the actual A9 port high-byte guard.
The complete archived writer predicate rejects 0056/0057. A separate asset
model with that predicate reproduces all 528,384 bytes at every record, without
copying observed FONT into source. Earlier 40-picture/88-controlled-text results
retain their limited identity; they never established whole FONT RAM. Native
already falls back to BMP for zero-high-byte ANK, so no native repair is made.

All eleven text/CRT fields are stable: first scanline0, last15, blank16, no
scroll, CRT/monochrome/attr4 false. Hide-odd and allow-scanline-effect are true,
where the earlier emitter used false; slave doublescan is false, so those
branches do not affect these samples. Captured cursor/width values are also
used by the new emitter. The unchanged independent line/GDC bodies now consume
actual full FONT and registers rather than font/default adapters. All forty
complete 640×400 captured/on/off RGB outputs are retained. Their captured RGB
matches the old adapter's sampled outputs exactly. Font inversion, first text
raster and CRT shift alter 202,985, 6,695 and 3,914 full-frame pixels; malformed
full extents reject. Actual surfaces are consumed, not silently ignored.

All 15,984×38 old programmed regions still agree with immutable VP3. Full raw
prefix equality has 15,959 records; all 25 unequal records retain every byte
and value. The actual header compiler places scan_address170, row_line173,
display_partition174 and remaining_lines176 in each 232-byte GDC. Those derived
master/slave raster fields account for every unequal byte. Programmed-frame
regeneration does not attest physical raster/scanout equality.

The new original's 15,988 selected scalar/caller/reset boundaries also agree
with the frozen current native a47f0496 parent. All 127 parent capture hashes
are recovered unchanged. No new native execution/build/full-pool claim is made;
its v1385 whole GNU71/69CTest and optimized UBSan3 receipts keep their identity.
New full RGB versus native remains 12/40 raw-zero and 28 unequal; explicit DAC
diagnostics have 32/40 zeros and eight blink-phase cases. Native-phase projection
has 40/40 diagnostic zeros, without full-picture or original-phase acceptance.

Actual vga.draw.delay.framestart/PIC ticks/vtotal reveal a constant original
refresh period of 17.72322658483988 ms. All 15,980 within-Demo time transitions
agree with GDC phase without fitting an epoch. Demo1/2 and Demo3/1968 have zero
event time; Demo3/1954 and /1963 have 35.4464531697 ms, two refreshes. They are
literal zero/two events in this pinned scenario, strengthening v1385's residues.
Native still uses 17.730496 ms (56.4 Hz approximation). Recover the timing owner
and calibrate native cadence, then original boot/process timing, before absolute
phase/scanout acceptance. Boss/death/process and cross-emulator routes stay open.
DOS product fingerprint6f5898dd, native509 manifesta47f0496 and historical exact
states are unchanged; candidate-local-attested provenance remains a gap.

Recipes: DOS-root .analysis/reconstruction/probes/native-cg-v1386/;
new original .analysis/runtime/candidates/dos-demo-v1386-original-cg-v1/;
receipts/programs native .analysis/port64/native-cg-v1386/. Replay read_full.py,
read_prefix.py, verify_font.py, compose.py, attest_raster.py and verify_control.py
after restoring retired inputs. The new capture and old VP3/adapter/producer
proofs retain separate identities; none is restamped.

The additional controlled V/W plane compares all768000 RGB bytes equal between
the retained currentnative RGB/ARGB APIs and actual capturedCG, while the old
font adapter differs71 pixels. This directly verifies the native ANK fallback.
The first readonly counting recipe repeatedly read fullfiles per pixel; a
separate v2 reads eachfile once and reproduces the same output hash/count. Both
passed scripts/receipts are retained. Replay verify_ank_v2.py after recovery.

## Calibrated native refresh cadence (v1387)

The original VP4 GDC/time streams independently explain the recorded period.
All 15,984 complete records, headers, CPU/load identities and gzip CRC/EOF pass;
the thin reader retains the complete 464-byte GDC pair and 51-byte time block.
The actual archived PC98 branch of VGA_SetupDrawing, its fps calculation and
vtotal assignment reproduce every observed 17.723226584839878 ms value.
Master mode fields are 80 words, 400 lines, HFP10/HS8/HBP8 and VFP7/VS8/VBP25:
106 character clocks by 440 lines at 21.0526 MHz divided by eight. Changing
HFP, VBP or the 31 kHz clock branch changes the result. Original MAIN remains
077440a3, load10FC/DGROUP3230, seam0AAF:00B7/terminal0AAF:0975. The emulator,
archive, actual header/compiler and generated model are pinned. This establishes
the recorded emulator mode; physical-board and cross-emulator timing stay open.

Native host_window.hpp now uses 17,723,227 ns, the nearest integer nanosecond
to the rational 1,865,600,000,000 / 105,263 ns. The remaining quantization is
0.415160 ns per refresh instead of the old 7,269.415160 ns drift. The window
trace reader uses the same accepted cadence. Only those two inputs change in
the 509-file producer, manifest03351541…; public DOS inputs/fingerprint and
historical exact states stay unchanged. The shared clock reaches host admission,
MAIN refresh observation, continuous text time and frontend sound durations.
Legacy component fixtures using explicit old-duration intervals do not represent
the current hardware cadence and retain their fixed-duration scope.

A fresh whole cold GNU build produces 71 programs and passes all 69 CTests.
Optimized UBSan/bounds cold-builds the game, demo trace and shake targets; no
full UBSan CTest or new full-nine-pool claim follows. Actual muted SDL-dummy
OP→four demos→OP yields 127 identical complete files in both variants and the
frozen a47f0496 parent. All 15,988 selected original scalar/RNG/caller boundaries
are compared again from the complete original raw trace with relocated-load,
profile/schema/input guards. Original full starting-image validation retains
its v1386 producer/retention identity, rather than becoming a new capture.

An independent actual Schedule probe uses the archived model's event times,
checking 20,000 before/after refresh boundaries. Current cadence passes; the
frozen old 56.4 Hz source rejects. A separate instrumented actual FrontEnd
checks logical admission17 and host boundaries through 1,000,000 refreshes,
against the unchanged GDC counter. Repaint, simulation double counting and
backwards-time controls pass; its 127 ordinary capture hashes are unchanged.
An actual muted private Linux Xvfb startup/Marisa B/input/focus/release/exit
route passes all recorded cadence deadlines and opens no audio device.
Windows foreground/input, physical display/audio and dense pacing stay open.

All forty entire native index/text/RGB samples remain unchanged. The immutable
independent emitter regenerates all 120 captured/on/off original RGB frames
from restored actual FONT/CRT inputs, reproducing their full hashes. Whole raw
RGB still has 12/40 zeros, explicit DAC diagnostics32/40 and eight blink-phase
cases; fixed native-phase projection40/40 is diagnostic only. Cadence calibration
does not align the separate original boot/process epoch or accept physical
scanout. Recover a common reset/boot/process elapsed timeline independently;
never fit offsets per Demo. Broader ordinary Boss/death/process pairing remains.

Recipes: DOS-root .analysis/reconstruction/probes/native-cadence-v1387/;
native receipts .analysis/port64/native-cadence-v1387/. Use attest_timing_v2.py,
cadence_controls.py, compare_final.py and run_window.py. The initial timing
reader's archive iterator reset failed its input guard before compiling or
reading records; its source/log are retained. Separate v2 enumerates the archive
once and passes. Earlier a47f0496 and font/raster proofs keep their original
source/evidence scopes; no old proof is restamped as current03351541.

## Common boot GDC clock and initial callback (v1388)

The literal zero-origin hypothesis was tested before changing native source:
all 15,984 retained original GDC/time records satisfy
`floor(framestart / period) + 1` modulo128, without a fitted offset. Fresh
read-only original boot capture then independently observes both constructors,
zero out-of-line cursor parameter entries and every timer callback after both GDC advances.
The complete ELF timer/function/site witnesses are checked before installing
breakpoints. Constructor returns are state0/count0/rate32; the first display
callback at PIC event/mode base1.875ms immediately increments both counts to1.
`VGA_SetupDrawing` calls the timer directly before the first waited interval.
The callback precedes `RENDER_StartUpdate`, so paint suppression does not suppress
clock advancement. No out-of-line parameter-entry events were observed. The model includes the
parameter body, but that path is unexercised and its ABI/reset semantics are
not accepted by this capture.

The complete new stream has {'C': 2, 'E': 2, 'V': 21151, 'F': 15988}. Original MAIN stays077440a3,
load10FC/DGROUP3230, scalar seam0AAF:00B7/terminal0AAF:0975. All15,988 initial,
before-update and terminal scalar clocks are included. An independent C++ model
uses the unchanged archived cursor body, with a narrow explicit
constructor adapter checked against actual constructor returns. Every clock
triple passes. Blind callback counts predict every actual master/slave phase;
all15,988 ordinals also equal the literal zero-origin formula. All15,984 thin
541-byte per-Demo records agree with matching boundary payloads and pass complete
gzip/header/CRC/EOF checks. Original reset, target, observer, ELF and compiler
identities remain pinned. This is evidence for the pinned emulator scenario.

Native view.cpp now starts its persistent display count at1 to admit that
immediate initialization callback. Only this source input changes from03351541
in the509-file producer, manifestf2b03ebb…. Fresh whole cold GNU produces71
programs and passes69 CTests; optimized UBSan/bounds cold-builds game/trace/shake.
Actual muted SDL-dummy OP→four demos→OP produces127 identical variant files.
Relative to the retained033 parent only text-refreshes.txt changes; the other126
full hashes stay identical. Fresh original selected input/score/player/RNG/caller
state comparisons cover15,988 boundaries. Prior full-nine-pool claims retain
their original producer identities. DOS public inputs/fingerprint are unchanged.

Independent timing/GDC-body controls check initial1 plus17 logical admissions,
host boundaries through1,000,000 refreshes, repaint/double counting/backwards
rejection, and20,000 actual Schedule boundaries; the old cadence rejects.
A separate actual FrontEnd experiment reads recorded original event ordinals
and normalizes `(events-1) * 17,723,227ns` to canonical interval units. Its
visible field is an assertion, never a clock input. All15,988 boundary event counts and
blink states plus15,984 ending-step admissions pass without global/per-Demo fitting; state and40 wholeTRAM match;playfieldindex diagnostics zero;wholeindex
inequalities retained. Restoring only the old zero initializer rejects at initial callback
admission. This explicit recorded-clock fixture is distinct from the default
native boot/OP/loading/process elapsed timeline and raw PIC nanosecond equality.

The immutable original FONT/CRT emitter regenerates120 full sampled references.
Default raw RGB remains12/40 zeros, explicit DAC diagnostics37/40.
The separate original-event-clock fixture gives raw12/40 zeros and explicit
DAC diagnostics40/40, eliminating its blink-phase diagnostic cases while
retaining all raw palette inequalities. Whole-picture acceptance, physical
scanout, raw PIC CPU fractional timing, broader paired Boss/death/process routes
and actual Windows input/audio remain open. Fresh actual muted private Linux
Xvfb startup/Marisa B/input/focus/release/exit passes with zero audio device opens.

Fresh V2 passes boot/scalar/clock completeness but its epoch differs from the
retained v1386 reference:15,983 updates shift by-27 display events and Demo4/1
by-26;19 sampled visible states differ. Config files are identical. These
observations reject using old captured-phase references with the new clock.
The initial V3 comparator wrongly required entire original index equality;
source and prior contracts confirm native index exports omit some pixel-only
HUD/text work. All full index inequalities remain recorded; game-area diagnostics
are separate from full RGB equality. V4 then rejects556pixels atDemo4/3709:
its before-step count rows are correct, but repainting the completed frame
precedes admitting that frame's recorded clock. V5 uses one-row lookahead to
admit the endpoint before repaint, then consumes that row once at its next
before-step trace. All15,988 boundaries and15,984 endpoints pass; only that
oneRGB file changes from the earlier fixture. Independent full RGB is unmasked.

V3 adds40 fresh complete808255-byte FONT/CRT/VRAM/palette/GDC/time snapshots
at the same fixed stopped scalar boundaries, so all new captured-phase RGB
references use their actual same-capture clock. Phase0/1 reference hashes still
match the immutable older emitter/reference, while captured phase keepsV3
identity. Default elapsed-time causes and debugger overhead remain separate.

V1's900-second host guard ended after Demo1/2, so it fails four-Demo completeness;
its partial gzip lacks a complete footer and is retained only as a failed attempt.
Fresh V2 combines the two refresh stops at the attested ELF0x5626aa site and
uses bulk clock reads, with a2400-second host guard and unchanged24000 guest
cycles/reset/route. Complete V2 and fresh V3 are accepted separately, never as a continuation
or repair of partial V1. No guest/emulator source or target bytes were patched.

Recipes: DOS-root .analysis/reconstruction/probes/native-epoch-v1388/;
native receipts .analysis/port64/native-epoch-v1388/. Use run_capture_v3.py,
read_boot_v3.py, common_clock_v5.py, cadence_controls.py and compare_final_v5.py in
fresh output namespaces. Original boot capture and live source inputs require
retention recovery before replay when owned expanded files have been retired.
Next investigate native versus original boot/OP/loading/process CPU/I/O cost
owners; retain raw RGB/scanout and broader route questions independently.

## Native analog DAC expansion (v1389)

Compiler-observed pinned DOSBox-X PC-98 scanout expands analog4-bit values
to6 bits, then6 to8 bits. Its16 RGB values are
0,16,32,48,69,85,101,117,138,154,170,186,207,223,239,255.
The archive-attested unchanged original functions compile with pinned g++8;
51,712 input/tone checks pass and12/16 values reject the old nibble×17 rule.
This is emulator policy evidence; physical DAC, live xlat32 and cross-emulator
RGB remain unobserved in this batch.

Native producer7223a35552eaac88e80fdc2166f1f1f9803ab688788efcc3a1c2167ddfc00e3d freezes510 files. Seven display
consumers use pc98_palette.hpp, keeping tone arithmetic in the four-bit domain.
Six independent original-instruction Oracle adapters and four portrait checks update only RGB expansion
and pass extracted statement/value-domain controls; original instruction
execution and palette ownership stay separate. main.cpp PI-to-BMP remains a
linear raw asset preview, distinct from display scanout.

Fresh whole cold GNU71 programs/69 CTests and optimized UBSan3 pass. Actual
muted four-Demo GNU/UBSan127 outputs are identical. Exactly28 full RGB files
change fromf2; all87 non-RGB outputs and12 RGB outputs retain full hashes.
Original selectedstate/RNG, counters, palette, canonicalTRAM, indices and shake
therefore keep the retained proof identity; no new original boot capture or
full-nine-pool promotion is claimed. Fresh actual FrontEnd V5 clockfixture
admits15,988 boundaries and15,984 endpoints using the same retainedV3 original
clock; visible is assertion only, no fitted offsets.

Forty retained originalV3 FONT/CRT/VRAM/palette/GDC/time samples regenerate120
whole640×400 RGB references with the unchanged independently attested renderer.
Every reference hash matches its previous accepted counterpart. All40 complete
fixture RGB files now equal original raw RGB with no normalization, tolerance,
crop or phasefit. Defaultphase rawRGB equals37/40. Only three original/default
blink-phase cases remain. The oldf2 complete same-clock RGB control is recovered
selectively with archive/member hashes and rejects28/40;12 black/white cases
are insensitive. Whole-index inequalities are retained in their original
diagnostic domain and cannot be used as whole scanout acceptance.

Fresh original MAIN GameOver TRAM helpers replay at1000/2000 and compare
46 whole indices/TRAM/RGB snapshots (47472000 bytes).
Fresh decoded MAINE registration helpers replay at1000/2000 and compare
91 complete consumer snapshots. Palette scanout is an explicit
emulator-source adapter; original text/drawing instructions are independently
executed. These do not attest scene timing/audio/saves or broader OP processes.
Actual private muted Linux Xvfb input/window checks pass with0 audio opens.

The initial GNU attempt was explicitly stopped to update the six reference
adapters, then the final producer was cold-built in new directories. Its
immutable initialsource, logs and stop receipt stay separate;24.27 MiB of
regenerable aborted objects/programs were cleared with a source-backed journal.
A later preflight also finds four scene portrait checks with legacy RGB expansion;
they now import an independently exercised scalar adapter. The first adapter
statement probe failed because its synthetic DAC fixture serialized NumPy int64
bytes rather than uint8. Its original source/log/pipeline failure are retained
in initial-replay-v2; corrected finalV3 cold GNU/UBSan and all controls replay
from a new frozen namespace. No failed probe becomes acceptance. The first frozen GameOver run then fails
at import before target execution because native scripts are outside the frozen
port64-only tree. V4 adds PYTHONPATH to the attested native scripts; its separate
continuation reuses only closed passed V3 receipts and reruns the pending target
consumers. Both failed harness logs and their source are retained. V4 then records both
original loads but correctly rejects byte0 because the coordinator supplied
the game executable rather than its graphics-consumer contract executable.
V5 uses the pinned player-lifecycle/registration/cutscene contract programs
and fresh output directories; the truncated-native control remains negative. The first final comparator
then fails to import the retained observer dependency; V6 adds only its
attested scripts/probes search path and independently regenerates all references.
Its original failed source/log stay unchanged; no comparator data is edited.
Final cleanup/recovery is indexed in docs/ANALYSIS_RETENTION.md.

Replay from DOS root (fresh outputs required):
.analysis/reconstruction/probes/native-dac-v1389/ contains freeze_source.py,
build_native.py, capture_native.py, dac_oracle.py, adapter_controls.py,
common_clock.py, run_window.py, pipeline_v6.py and compare_v6.py. Native receipts are
.analysis/port64/native-dac-v1389/. OriginalV3 boot/fullsample and clock receipts
remain in v1388; regenerate each frozen producer in a fresh namespace.

Next: default boot/loading/process elapsed-time owners under observer-overhead
controls. Raw PIC fractional timing, physical/cross-emulator DAC and scanout,
broader paired Boss/death/process routes and Windows input/audio remain open.
All target provenance remains candidate-local-attested; no DOS exact promotion.

## Full OP validation startup and controlled clock pair (v1390)

The previous --demo-pictures entry did not request MainAssets.full_startup;
ordinary windows did. Its default37/40 fullRGB comparison is scoped to that
compact headless entrance against retained originalV3, not ordinary window or
full OP startup timing. Current frozen510 producer bdc1fb56f80b1d5d987c89a1cfe63cea9da155eb6ef8eb662c10480dd02c4b5e
changes only main.cpp and demo_picture_frontend_checks.inl. Demo captures now
load the complete existing startup resources and run the ordinary startup
controller. Actual startup callbacks independently record one resident Logo and
five completed OP titles: before each of four natural idle demos and fresh OP
after Demo4. The existing muted capture profile uses --pmd-driver none;
logo measure waiting therefore remains an explicit adapter boundary rather than
original PMD/audio timing acceptance. No visual startup is bypassed, logo repeated, or new per-demo clock offset
introduced. This corrects validation admission; ordinary window admission was
already fullstartup. Final OP ready is fresh native coverage, not an original
complete process/teardown/physicalclock claim.

Cold GNU71 programs/69 CTests and optimized UBSan/bounds3 pass. Actual muted
SDL-dummy four-Demo runs produce128 identical files. Changes from compact
v1389 are ['demo2-frame1952.rgb', 'text-refreshes.txt', 'demo4-frame74.rgb', 'demo2-frame3996.rgb', 'startup-events.txt', 'demo1-frame3709.rgb', 'demo4-frame73.rgb']. Selected state/RNG/callcounts
agree at all15,988 before-update/terminal seams against both fresh originals.
Other actor/presentation proofs keep their prior producer identities. Actual
muted private Linux Xvfb input/focus/release/exit passes with0 audio opens.

Original controlled pair uses the same projected collector/ELF/config/reset/
input/full40sample plan. Only TH04_CLOCK_OBSERVER_DELAY_NS0 versus5000000
changes, sleeping after the first128 post-both-GDC V observations. Measured
host overhead: [{'requested_delay_ns': 0, 'calls': 128, 'elapsed_ns': 0, 'scope': 'Host sleep after first128 complete recordedV callbacks;no guestwrites'}, {'requested_delay_ns': 5000000, 'calls': 128, 'elapsed_ns': 654057090, 'scope': 'Host sleep after first128 complete recordedV callbacks;no guestwrites'}]. No guest registers, memory, scheduling
requests, input, recorded phase or target bytes are patched. Original MAIN
SHA077440a3, scalar0AAF:00B7 and terminal0AAF:0975, load10FC/DGROUP3230
remain independently guarded. Both complete event streams replay independently
compiled archive-attested original GDC advance bodies; every15,988 frame seam
and15,984 thin row agrees. Constructors and parameter coverage retain explicit
limits. Selected/caller comparison passes. The event difference histogram is
{'5': 15987, '6': 1}; 2501 boundary
visible phases differ. Within-MAIN event increment histograms:
[{'1': 15977, '0': 5, '2': 2}, {'1': 15975, '0': 6, '2': 3}]. This is one controlled pair and cannot
prove universal host-observer effects or their absence. Without repeated
zero-delay controls, the five-event shift cannot be attributed specifically to
the sleep rather than ordinary run-to-run jitter. Keep absolute epochs
distinct; do not correct original data or fit native offsets. The full pair
receipt records all raw region differences of80 whole snapshots separately.
All40 paired raw text/graphics/both-pages/palette/modes/FONT/CRT regions are
identical; only GDC and raster-time spans differ.

Each fresh full FONT/CRT/VRAM/palette/GDC/time sample verifies complete hash,
gzip CRC/EOF and same-boundary F clock payload. The unchanged independent
original scanout renderer emits240 full RGB references from these80 samples.
Separate actual FrontEnd fixtures admit each capture's recorded event ordinals
at15,988 boundaries and15,984 endpoints before paint. Original visible is an
assertion only; no phasefit/crop/tolerance/normalization is applied. Raw complete
640x400 RGB is zero40/40 for each supplied-clock capture,80/80 total. Whole
canonical TRAM equals; whole native/index inequalities remain diagnostic.
Default fullstartup rawRGB counts against each separate original are
{'baseline': {'default_raw_zero': 32, 'common_raw_zero': 40}, 'host-delay': {'default_raw_zero': 30, 'common_raw_zero': 40}}. These counts describe sampled default headless timing only.
The clock fixture supplies MAIN seam ordinals; startup prefix, inter-process
CPU/loading times and final OP elapsed-time ownership remain unpaired. The
zero-initial-callback one-field control rejects at initial admission.

An initial wrapper syntax typo failed before any original launch; the log is
retained and the corrected wrapper runs in baseline-v2.log. No failed harness
becomes acceptance. All replay source/receipts/logs and neworiginal compressed
streams remain private under native-clock-owners-v1390. pipeline_v2.py is serial
CPU0/nice19; compare_native.py finishes the independent raw reductions.
Default boot/process CPU-I/O clock ownership, physical/cross-emulator scanout,
Boss/death/fullprocess pairing and Windows input/audio remain open. Targets
remain candidate-local-attested; no DOS exact acceptance changes.

## Physical configuration and repeated startup clocks (v1391)

The demo picture harness copied MIKO.CFG without enabling configuration loading.
The incoming ten bytes are `020302020101ef9f000b`; the six options are rank 2,
lives 3, bombs 2, BGM 2, SE 1 and turbo 1. Native defaults used rank 1. Because
the demos locally select Hard, prior selected-state and pixel checks missed
this admission error. Current `demo_picture_frontend_checks.inl` enables the
existing configuration owner before registration, records actual configure
requests, and checks the complete physical CFG after fresh OP returns ready.
No native core, DOS source, compiler flags or historical exactness changes.

The current frozen 510-file producer is c6a90f57e662cbbe85cec9b55047f0ffce5df818067725f687b548f4d2579010.
Cold GNU builds 71 programs and passes 69 CTests; optimized UBSan/bounds builds
the game, trace and shake programs. Eight actual muted runs cover `none`,
`pmd`, `pmdb2` and `pmd86` separately under GNU and UBSan. Each pair produces
129 byte-identical files. All nine OP/MAIN configure requests agree with the
six incoming physical options. All 10 CFG and 1,960 score bytes remain unchanged
and agree with independent FAT readback of the fresh original's final disk.
Selected state, RNG and draw counts match at all 15,988 original seams for
each profile. One resident Logo and five completed titles include final fresh
OP ready. Private Linux Xvfb startup/input/focus/release/exit passes with zero
audio opens; Windows host interaction remains excluded.

| Native profile | Measure request to first SUPER_load | First MAIN refresh | Default raw RGB against fresh zero-repeat |
| --- | --- | --- | --- |
| none | 0 refreshes | 1,193 | 31/40 |
| pmd | 94 refreshes | 1,287 | 34/40 |
| pmdb2 | 94 refreshes | 1,287 | 34/40 |
| pmd86 | 94 refreshes | 1,287 | 34/40 |

These are observed spans through the installed native provider, not an original
PMD measure, board, audio or driver-equivalence claim. They do not justify a
94-refresh constant or selecting a driver to fit original picture phase. ROM
identity remains strict: PMDB2 uses the previously attested 8,192-byte MAME
ADPCM ROM SHA `53afd0fa9c62eda3e2be939e23f3adf48a2af8ad37bb1640261726c5d5adeba8`.
The first LLE-format selection was rejected before launch; corrected captures
use fresh `-v2` directories and retain that negative.

A new original zero-delay run reuses the immutable v1390 collector projection,
ELF, reset, config, input and sample plan. MAIN SHA starts `077440a3`; locations
are MAIN 0AAF:00B7/0975 with load 10FC and DGROUP 3230. Complete C2/E2/V21113/
F15988 events independently replay archived original GDC advance bodies; all
15,988 seams and 15,984 thin rows agree. Parameter-entry coverage remains zero.
Fresh complete scalar/caller digests match both retained closed v1390 readers;
those identities are reused, not re-executed or restamped. All 120 complete
original snapshots (40 per capture) are freshly read with hash, gzip CRC/EOF
and same-boundary F-clock guards. Raw text, graphics, palettes, modes, FONT and
CRT agree across all three captures; GDC and raster-time differ.

The original baseline to this zero-repeat shifts event ordinals by 8 at all
15,988 seams, with 3,999 visible phase changes. The old delayed pair shifted
by 5 at 15,987 seams and 6 at one, with 2,501 phase changes. Thus a five-event
shift is not a unique diagnostic of the inserted sleep. This is neither a
causal effect estimate nor proof that sleep has no effect. Keep absolute epochs
separate and do not correct recorded clocks or fit native offsets.

The fresh original's 40 complete FONT/CRT/VRAM/palette/GDC/time samples produce
120 independent full RGB references. A current actual FrontEnd `none` fixture
admits that original's ordinals at all seams/endpoints before painting. Whole
canonical TRAM agrees and complete raw RGB is zero for 40/40 samples, without
normalization, crop, tolerance or fitted phase. Its zero-initial-callback
control rejects at admission. All four ordinary profiles also match 40/40
references evaluated at each profile's own counter phase; their default
31/40 and 34/40 counts above remain diagnostics. Whole graphics-index
inequalities are separately diagnostic. Fixture startup-prefix/final-OP
clock ownership and original audio timing remain unpaired. Prior v1390 80/80
supplied-clock evidence keeps its original producer identity.

A meaningful one-call negative removes only `scene.enable_configuration()`
from a clone of the current capture. Its CLI completes successfully and all
prior 128 output files remain byte-identical, including state, RGB, clocks,
startup and physical saves. Only the new configuration trace differs: all
nine generations use rank 1. The independent physical-option reader rejects
it at the first OP configure event. Physical file equality and demo pixels
alone cannot prove that the live process loaded configuration.

Private replay: root `.analysis/reconstruction/probes/native-startup-clock-v1391/`
and native `.analysis/port64/native-startup-clock-v1391/`. Jobs run serially on
CPU0/nice19. `pipeline.py` stopped at the ROM guard; `pipeline_v2.py` stopped
at a reference-reader import pointing at a namespace without the collector.
`pipeline_v3.py` closes the corrected comparisons. The first source-freeze
parent guard also rejected an incorrect parent before acceptance. All failed
sources/logs/negative receipts remain preserved; none is acceptance.
Configuration and clock controls, full comparisons and window receipts must
be closed before lossless retirement of objects, duplicate captures, expanded
references and disposable disks. Restore through `verify_retention.py --restore`;
without that option it checks archive CRC/EOF, member SHA/mode/size/nsmtime,
inherited protected receipts and all frozen producer pins.

Next identify original startup/loading and resolved PMD clock owners using
independent event evidence. Default process clocks, physical/cross-emulator
scanout, paired Boss/death/process routes and Windows input/audio remain open.
The goal stays active; candidate-local-attested provenance and deferred MAIN
historical exactness are unchanged.


## Cold PMD installation and original OP timer ownership (v1392)

Original `GAME.BAT` selects the resident PMD driver before unpacking OP. Two
new read-only normal-core captures use the unchanged attested DOSBox-X ELF,
original packed OP SHA `8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f`,
pinned reset/config/assets and board 86c. They stop on the host before the first
ordinary menu body, without guest writes, input injection or audio devices.
This is a bounded OP startup observation, not a completed DOS process.

The complete 69,028-byte runtime decoded load equals the pinned decoded target
with all 804 ordered relocations applied. Load is 10FC, DGROUP 2030; startup
CS is relative 0A74 (runtime 1B70), shared sound CS relative 0DA1 (runtime 1E9D).
PMD service 9 returns AX=4802, resolved BGM=2/SE=1/MIDI-possible=0, IVT60 is
098A:0103 with PMD magic. Resident options are rank/lives/bombs/BGM/SE/turbo
2/3/2/2/1/1; Logo flag changes 0→1. Prefix/type observations do not prove
whole resident COM byte equality or physical board identity. The packed OP
Ghidra database is attested but is not the decoded semantics Oracle.

| Original boundary | Relative CS:IP | Timer-capture display ordinal |
| --- | --- | --- |
| driver reply | 0DA1:02F2 | 80 |
| Logo entry | 0A74:14F5 | 80 |
| measure entry | 0DA1:0370 | 88 |
| measure return | 0DA1:039D | 180 |
| Logo complete | 0A74:0CC4 | 537 |
| title complete | 0A74:0CE3 | 736 |
| ordinary menu entry | 0A74:0756 | 745 |

Both captures wait 92 display events for measure 2. Independently replayed
complete GDC streams admit all 24 startup boundaries; parameter-entry coverage
is zero. Whole-load byte and GDC counter mutations reject. The reusable ROOT
reader is `scripts/runtime/verify_op_startup_clock.py`; supply both capture
directories, the closed v1391 original GDC model/receipt and a fresh output.
Restore archived HDIs first when rerunning image identity checks.

The timer capture observes 2,326 host rows: 1,003 register writes, 985 schedules
and 338 Timer B callbacks. Function memory witnesses and original emulator
source bind `fmtimer_setreg`, `pc98_fm_dosbox_fmtimer_setevent` and the B callback.
PIC time is read directly as ticks plus the CPU fractional cycle budget; no
host timing function is called. First B enable occurs with register 0 and queues
73.728 ms. The following write of 200 changes the next period without replacing
that deadline. During the measure-entry-to-return interval, 48 B callbacks occur.
Actual measure-entry-to-return time is 1,637.469333 ms. Installation-first-schedule
to Logo playback is 245.638500 ms; playback-to-last B callback is 1,637.881542 ms.
These baselines are distinct. Timer formulas are the attested DOSBox implementation
(18 us × (1024−A), 288 us × (256−B)), not physical chip acceptance.

Native previously constructed an already running post-install Timer B with
register 200: 16.128 ms. Actual installation updated the PCM chip and mirror,
but not the live logical timer. The application now explicitly constructs cold
ClockedPlayer/PcmPlayer state, then routes each real installation write to both
logical timers and PCM. Standalone post-install fixtures preserve the default
`TimerEpoch::installed`; application ResidentPmd uses `TimerEpoch::cold`.
At 8 MHz the constructor now has A deadline 147,456 and B deadline 589,824
cycles, with zero elapsed PCM cycles/samples. No synthetic loading offset is added.

Current frozen 510-file producer: `9cfe100a84ac0a325d498b9b81602298009e462643b2cfa453947fe85bc1b049`. Six PMD source/test files change;
DOS sources/flags/headers and fingerprint `6f5898dd9de51259628f27929b60b0ed77431bacd933270689c07bfc06a1592d`
remain unchanged. Cold GNU builds 71 programs and passes 69 CTests. Optimized
UBSan/bounds builds six explicit targets and executes all three PMD contracts.
The real LOGO.M86/MIKO.EFC service probe produces four complete tables identical
under GNU and UBSan. Cold measure 2 occurs at the 1,707 ms sample. Supplying the
original observed installation age as a typed diagnostic input yields 1,638 ms,
near the separately observed playback-to-last-callback interval. This does not
pair default native loading or justify encoding that age as a product offset.
Two one-variable constructor controls complete with zero elapsed time but reject:
old installed epoch gives B=129,024 cycles; PCM-only install gives B=0.

Eight actual muted GNU/UBSan routes cover none/pmd/pmdb2/pmd86, each pair with
129 identical output files. State/RNG/draws/shake/indices/canonical TRAM/config
and complete physical save files are bit-identical to retained v1391 original-
paired captures. This reuses those closed digests; the original four-Demo raw
state reader is not reexecuted or restamped. Nine options requests, one resident
Logo, five completed titles and final fresh OP ready pass. The default native
measure-to-SUPER_load span is 0/97/97/97 refreshes, first MAIN 1193/1290; original
92 cannot be compared as a universal waiting constant. All 40 retained compressed
original raw samples are freshly CRC/EOF/hash/F-clock guarded and emit 120 full
RGB references. Default RGB zeros remain 31/40 for none and 34/40 active; own-
counter-phase 40/40 is diagnostic. Prior supplied-original-clock 40/40 remains
accepted only under its old producer; no current supplied-clock fixture rerun.
Private Linux Xvfb input/focus/release/exit passes with zero audio opens.

Replay from DOS root: `.analysis/reconstruction/probes/native-pmd-startup-v1392/`;
native consumers: `.analysis/port64/native-pmd-startup-v1392/`.
Original captures: `.analysis/runtime/candidates/dos-op-v1392-pmd-{startup,timers}/`.
`verify_op_startup_clock.py`, `run_native_probe_current.py`, `run_native_probe_ubsan.py`,
`installation_controls.py` and `compare_current_v3.py` close distinct receipts.
The two rejected reducer setup attempts keep their sources/logs and provide no
acceptance. Before full replay restore this batch with `verify_retention.py --restore`.
Do not rerun closed producers into old output paths. The next owner is actual
CPU/file-loading elapsed time from PMD installation to first Logo playback and
subsequent OP waits, followed by broader paired process/combat routes. Whole
picture/default startup clocks, physical/cross-emulator scanout and Windows
input/audio remain open. Historical exactness/provenance is unchanged.


## Original OP loading work and completion guards (v1393)

Two complete read-only original GAME.BAT/PMD86 captures change only fixed CPU
budget, 24,000 versus 36,000. Initial HDI/config/save/assets, font, observer
profile and original emulator are identical; configuration bytes differ only
at the cycles line. No guest bytes, input, schedules or phases are injected.
Both captures stop on the host before the first ordinary menu body. Targets
remain candidate-local-attested; full process and physical timing are open.

Original packed OP SHA starts `8fc3b67f`. Each full 69,028-byte runtime load
matches the pinned decoded target plus all 804 ordered relocations. Load is
10FC, DGROUP 2030; decoded-entry DS is initial PSP 10EC. Thirty pinned target
points emit 41 scalar boundaries, plus a separately guarded decoded entry.
Independent complete GDC stream replay passes with zero parameter-entry
coverage. Whole-load byte, GDC counter, DOS return-frame and fractional PIC-time
mutations reject. Each F context, same-boundary payload, gzip CRC/EOF and target
opcode is checked. The reusable ROOT command is
`scripts/runtime/verify_op_loading_clock.py`; its second closed verifier output
adds emulator/source identity and exercises the positive load comparator on the
mutation. The first narrower verifier keeps its producer/receipt identity.

The host functions CPU_Interrupt, CPU_IRET, CPU_RET and the observer's whole-load
hex writer have full ELF/runtime memory witnesses. Raw PIC ticks and signed
CPU budgets determine time without calling a host timing function. Guest INT21
observations run only from first Timer B installation schedule through measure
entry. There are 62 file requests and 61 matched IRET returns in each capture.
Request paths, read sizes, returned AX and carry outcomes agree. The remaining
request is the parent OP child-exec; stopping inside OP cannot claim that it
returned. Both logical resource paths and nested physical archive paths appear;
this is a prefix file observation, not acceptance of all DOS/driver APIs.

| Original interval / target boundary | 24,000 cycles | 36,000 cycles |
| --- | --- | --- |
| first B installation schedule → decoded entry | 49.808208 ms | 33.431667 ms |
| decoded entry → OP main routine entry, 0A74:0C37 | 0.789667 ms | 0.526222 ms |
| OP main entry → game_init return, 0A74:0C56 | 19.844542 ms | 13.683194 ms |
| gaiji begin 0A74:0C6B → completion 0A74:0C79 | 40.258875 ms | 34.996528 ms |
| Logo entry 0A74:14F5 → PI load return 0A74:1523 | 66.984250 ms | 44.623833 ms |
| palette return 0A74:152A → PI put return 0A74:1534 | 61.656000 ms | 41.043750 ms |
| PI free return 0A74:1542 → page-copy return 0A74:1549 | 6.728833 ms | 4.474528 ms |
| page-copy return → background-snap return 0A74:154E | 1.707667 ms | 1.122917 ms |
| complete installation-first-B → Logo play command | 255.036542 ms | 178.822806 ms |

The complete finer interval list telescopes to the measured installation age.
PI load/put phases scale approximately with inverse CPU budget; the bracketed
intervals include argument/setup overhead and are not isolated device timings.
Gaiji work does not scale uniformly, so applying one global CPU factor to the
whole startup is not supported. The hardware/IO/wait contribution needs a
separate bounded observation. Both new measure waits span 93 display events,
versus the prior v1392 captures' 92. They are per-capture phases, not a target
refresh constant. Display ordinals and PIC installation age stay distinct.

Native product source remains unchanged: current 510-file producer
`9cfe100a84ac0a325d498b9b81602298009e462643b2cfa453947fe85bc1b049`.
GNU and optimized UBSan service programs are restored from the attested v1392
lossless archive and keep their closed producer/build identities. No fresh
native cold build, Demo picture or window acceptance is claimed in this batch.
With real LOGO.M86/MIKO.EFC and typed observed ages 255,036,542 / 178,822,806 ns,
full GNU/UBSan tables agree; measure 2 occurs at the 1,645 / 1,641 ms sample.
Original playback-command-to-last-callback is 1,644.611500 / 1,640.185222 ms;
errors are 0.388500 / 0.814778 ms, below the 1 ms observation step. Changing only
supplied age to zero still completes successfully at 1,707 ms, but the same
independent timing gate rejects it as 62.388500 / 66.814778 ms late. These are
conditional service diagnostics, not product offsets, native default loading,
complete PIC/IRQ latency or physical-chip/audio equivalence.

The first broad interrupt observer remained enabled during high-frequency
INT60 measure polling and was terminated. GDB returned zero and the first
wrapper marked passed, but it had no completion observation or terminal marker.
The actual strict reader rejects this counterexample. Fresh V2 wrappers require
41-row menu completion, its hash and terminal log; DOS hooks are disabled at
measure entry while timer/GDC observations continue. The first attempt's source,
log, misleading wrapper and incomplete inner gzip remain immutable failure
material. Lossless outer archiving does not make that inner stream complete.

Replay from DOS root: `.analysis/reconstruction/probes/native-op-loading-v1393/`;
native consumer receipts: `.analysis/port64/native-op-loading-v1393/`.
Accepted captures use `dos-op-v1393-loading-{base,cpu36000}-v2`. Original reader:

```sh
python3 scripts/runtime/verify_op_loading_clock.py \
  --capture .analysis/runtime/candidates/dos-op-v1393-loading-base-v2 \
  --capture .analysis/runtime/candidates/dos-op-v1393-loading-cpu36000-v2 \
  --rejected-capture .analysis/runtime/candidates/dos-op-v1393-loading-base \
  --model-dir .analysis/worktrees/port-modern-64/.analysis/port64/native-startup-clock-v1391/original-zero-repeat/boot-model-v3 \
  --model-receipt .analysis/worktrees/port-modern-64/.analysis/port64/native-startup-clock-v1391/original-zero-repeat/boot-observation-v3.json \
  --output-dir .analysis/NEW-loading-verifier
```

Restore HDIs/expanded inputs with this batch's `verify_retention.py --restore`
before full replay. `native_age_probe.py`, `zero_age_control.py` and `compare.py`
close separate receipts. Use fresh namespaces; never rewrite old proofs or
restart solely because a live observation is slow. Next isolate gaiji waits and
establish an explicit elapsed-work handoff through startup resource/draw/process
owners. Default native clocks, full pictures, broader paired combat/process
routes, physical/cross-emulator scanout and Windows input/audio remain open.


## Original Gaiji I/O elapsed work (v1394)

Four fresh read-only original GAME.BAT/PMD86 captures cross fixed CPU budgets
24,000 / 36,000 with default / zero **8-bit** I/O delay. Other configuration
bytes, original HDI/reset/assets/font, packed OP and emulator are identical.
Sixteen- and 32-bit delay settings remain unchanged. Each run stops before
executing OP 0A74:0C79, immediately after successful Gaiji initialization.
This is a bounded host stop, not process completion or physical bus timing.

Each entire 69,028-byte runtime OP load and its 804 ordered relocations agree
with the pinned decoded target. Load 10FC, DGROUP 2030; nine target points yield
264 scalar rows including all 256 read-glyph entries. Complete gzip CRC/EOF,
GDC model replay, scalar contexts and fractional PIC arithmetic pass. Loaded
byte, port count, fractional time and GDC counter mutations reject. The current
public reader also projects the complete observed I/O table by guest CS/port.
Three actual incomplete observer attempts are rejected; earlier receipts and
producer versions are preserved, rather than recertified by the newer reader.

Original target read-all 0:1450→1471 and write-all 0:14BE→14E1 execute 256
16-row glyph transfers. Host IO_ReadB/IO_WriteB breakpoints run only inside these
two windows and have full pinned ELF/runtime memory witnesses. Actual Gaiji
counts match the target loops: read-all reads A9 8,192 times and writes 68 twice,
A1/A3 256 times each, A5 8,192 times; write-all has the same selector writes plus
8,192 writes to A9. Other guest/PMD/BIOS port calls remain in a separate table.

| Original Gaiji interval | 24,000 default | 36,000 default | 24,000 delay 0 | 36,000 delay 0 |
| --- | --- | --- | --- | --- |
| initialization 0A74:0C6B→0C79 | 40.235458 ms | 34.996667 ms | 17.134000 ms | 11.404611 ms |
| read-all 0:1450→1471 | 14.559458 ms | 14.160278 ms | 2.194042 ms | 1.454056 ms |
| write-all 0:14BE→14E1 | 12.851417 ms | 12.331944 ms | 2.193083 ms | 1.457972 ms |

The unchanged pinned DOSBox-X `iohandler.cpp` is source evidence: at
`last_callback == 0`, read debit is floor(CPU_CycleMax × ns / 1,000,000), write
debit is floor(CPU_CycleMax × ns × 3 / 4,000,000). Actual default ns values are
864 / 559 / 1118; only the first changes to zero. CPU auto-adjust is disabled.
The cumulative removed-cycle counter resets in auto-adjust code, so it is
usable across these fixed-budget windows; it also includes non-Gaiji owners.

Observed counts account for 294,430 / 454,190 read-all debit cycles and
253,470 / 388,654 write-all cycles at the two budgets: 22.829167 / 23.412333 ms
total. Aggregate removed counters exceed these Gaiji-only debits by 1,035 /
1,591 and 1,020 / 1,453 cycles respectively; preserve that remainder, rather
than label it all as Gaiji or physical hardware waiting. With delay zero both
aggregate window debits are zero. Whole Gaiji zero-delay CPU-normalized elapsed
ratio is 1.001591. The nonuniform default phase is principally emulator I/O
work; no universal CPU factor or physical CGROM delay follows. Times belong to
these fresh captures and do not overwrite the v1393 loading epochs.

The first observer failed GDB Python indentation before guest execution. The
next reached the backup return but rejected an 8-byte hook window ending in one
byte of a relocation at 0A74:0C70; the complete load was correct. Expand that
window to nine bytes. A third attempt tried a normal-core glyph-write hook at
0:1474 while write-all had borrowed DS; the pinned observer's DGROUP guard
correctly terminated it. The accepted observer uses bounded host I/O counters
instead, keeping the original emulator and guard unchanged. Failure logs and
partial inner streams retain their failed status.

Native product source remains the same 510-file `9cfe100a` producer and DOS
fingerprint `6f5898dd`. No new build, native full startup, Demo or window proof
is claimed. Static maintained-source review finds native assets loaded in
`port64/main.cpp` before application resident PMD construction, whereas DOS
installation precedes OP loading. The next ownership task is an explicit
elapsed-work handoff through assets, drawing and process entry. This evidence
does not justify fitting the emulator's 864 ns delay or a constant age into
native product behavior. Physical/cross-emulator, full default pictures,
broader combat/process routes and Windows input/audio remain open.

Replay from the DOS root, restoring retired inputs first:

```sh
python3 .analysis/reconstruction/probes/native-gaiji-clock-v1394/verify_retention.py --restore
python3 scripts/runtime/verify_gaiji_io_clock.py \
  --capture .analysis/runtime/candidates/dos-op-v1394-gaiji-base-v4 \
  --capture .analysis/runtime/candidates/dos-op-v1394-gaiji-cpu36000-v4 \
  --capture .analysis/runtime/candidates/dos-op-v1394-gaiji-delay0-v4 \
  --capture .analysis/runtime/candidates/dos-op-v1394-gaiji-cpu36000-delay0-v4 \
  --model-dir .analysis/worktrees/port-modern-64/.analysis/port64/native-startup-clock-v1391/original-zero-repeat/boot-model-v3 \
  --model-receipt .analysis/worktrees/port-modern-64/.analysis/port64/native-startup-clock-v1391/original-zero-repeat/boot-observation-v3.json \
  --output-dir .analysis/NEW-gaiji-verifier
```

Private producers/receipts are under
`.analysis/reconstruction/probes/native-gaiji-clock-v1394/`; native copies under
`.analysis/port64/native-gaiji-clock-v1394/` bind the original ROOT receipt bytes.
Use fresh capture/output namespaces for another producer execution; restoring
proof inputs does not reset execution images for rerunning the old wrapper.

Lossless retirement reclaims 604.43 MiB, retaining 49 logical members in 15
unique blobs with full CRC/EOF/SHA/mode/nsmtime and protected proof checks.
Both CI gates pass (root 441 / native 345), ledger/diff checks pass and another
16.69 MiB of source-backed caches is removed after CI.


## Resident elapsed work through actual OP startup (v1395)

Native now exposes typed resource/graphics/process work intervals through
`sound::Timeline::advance_work`. An application-resident Timer/PCM owner
progresses before local process creation and across process gaps. Inside a
process, the same entry advances its beeper and mix. Pending refresh wait is
consumed first, cleared and charged only once by the retained guard. Unknown
work kinds and intervals above one second reject before any advancement.
Longer sources must partition intervals; there is no fixed loading cost.

`MainAssets::installed_work`, `op_entry_work` and `startup_work` carry explicit
inputs to the maintained frontend. Installation intervals apply before OP
sound entry; OP entry intervals apply after process-local setup, and event
intervals apply after real renderer/sound consumers. Process-local beeper
ownership and resident identity remain separate. The default adapters are
empty, so these changes do not introduce a fitted age, 864 ns bus delay or
refresh count into the CLI. GDC/text refresh ownership is still separate.

The frozen current producer has 510 files, manifest
`55459c6f487e25ce39e0b8499b89f52936e0273c536905e94b8a7764426fdb7e`. Six maintained files change: sound runtime/scenes declarations,
scene implementation/contracts and view declarations/implementation. Cold GNU
builds all 71 programs and passes 69 CTests. Optimized UBSan builds seven
selected targets and passes four sound contracts, including the new
pre-process/pending-wait/process-gap/PCM-attribution checks. The earlier 9cfe
producer and its proofs retain their original identities.

A separate headless caller includes the unchanged frozen `view.cpp`, links
the cold product core/chip archives and instantiates the actual FrontEnd.
Real OP PI/BFNT, LOGO.M86, MIKO.EFC, strict ROM and physical configuration are
supplied. It admits the two independently verified original v1393 epochs
through the new adapters, split at decoded entry, Logo entry, PI load/palette/
draw/free, page copy/snapshot/clears and song load. Durations come from rounded
cumulative PIC boundaries; they telescope without fitting a native outcome.
They are bracketed original intervals, not native per-function CPU estimates.
The original observations and verifier receipt remain unchanged.

| Original CPU profile / typed input | 24,000 | 36,000 |
| --- | --- | --- |
| admitted first-B-to-PLAY epoch | 255,036,542 ns | 178,822,806 ns |
| actual frontend measure readiness | 93 refreshes | 93 refreshes |
| native PLAY-to-ready sample | 1,648,260,111 ns | 1,648,260,111 ns |
| original PLAY-to-last-B-callback | 1,644,611,500 ns | 1,640,185,222.222 ns |
| sample error | 3.648611 ms | 8.074889 ms |

Both sample errors are within the actual frontend's 17.723227 ms refresh.
This is coarser than the earlier standalone 1 ms service probe and is not IRQ
latency/chip equivalence. Twelve actual caller executions (two inputs × three
modes × GNU/UBSan) reach Logo readiness and complete first OP startup; complete
output tables agree between compilers. The successful zero-work controls wait
97 refreshes but reject the independent PLAY epoch. Graphics-only removal
still aliases the positive 93 refreshes, yet loses original elapsed work and
rejects the same gate. Completion and wait count cannot validate forwarding.

Eight fresh default CLI executions cover none/pmd/pmdb2/pmd86, full startup,
four natural demos and fresh OP readiness. All 129 files in each compiler pair
are identical to the corresponding retained v1392 baseline outputs. This is a
new source-bound regression result, not restamping old receipts or creating
whole-picture/default-clock acceptance. Prior raw RGB diagnostic limits remain:
31/40 none and 34/40 active profiles; broader original timing remains open.
Actual private Linux Xvfb startup/selection/input/focus/release/exit passes,
with zero audio device opens. Windows GUI and host input remain excluded.

Replay producers are under
`.analysis/reconstruction/probes/native-elapsed-work-v1395/`; native receipts
and source freeze under `.analysis/port64/native-elapsed-work-v1395/`.
`build.py`, `build_frontend_probe_v2.py`, `run_frontend_proof.py`,
`capture_native.py`, `pipeline.py` and `compare.py` close separate receipts.
The first caller compilation failed for a missing root include path; V2 adds
both frozen root and port64 includes, leaving its failed source/log untouched.
Restore retired build/program/RGB inputs before reading/replaying them:

```sh
python3 .analysis/reconstruction/probes/native-elapsed-work-v1395/verify_retention.py --restore
```

Use fresh output/source namespaces for another execution. Next supply defensible
deterministic default work inputs and connect the distinct GDC epoch; do not
substitute host wall time or fitted startup offsets for an original CPU/bus
model. Physical/cross-emulator, broad combat/process, full pictures, Windows
input/audio and historical MAIN exactness remain open. DOS fingerprint
6f5898dd is unchanged; no DOS source, flags or headers change.

Lossless retirement reclaims about 472.70 MiB; all logical build/video/state
contents, mode/nsmtime and protected frozen-source/receipt hashes are retained.

## GDC text clock through elapsed OP work (v1396)

Maintained view.cpp previously forwarded work only to resident sound. Its
headless text counter advanced by admitted refreshes, losing resource/drawing
intervals between them. The same frontend work entry now advances both owners,
retaining sub-refresh time. `MainAssets::display_elapsed_ns` supplies the time
from initial GDC callback to PMD installation, independently of the sound epoch.
When an external elapsed-time observer takes ownership, it retains the current
fractional origin and suppresses logical work/refresh admission into display
time; external observation covers that time. Default adapters and epoch remain
empty/zero. There is no fixed startup age, copied event count or bus-delay fit.

Frozen native producer: 510 files, `ea5c016d0cd40bcb453bd9f6c27c6ec24c2513ec63342fa8be2fa8d6acc85d43`. Only view.cpp/view.hpp change;
DOS source/headers/flags and fingerprint 6f5898dd remain unchanged. Cold GNU
builds 71 programs and passes 69 CTests. Optimized UBSan builds seven selected
targets and passes four sound contracts and the actual frontend caller.

The independent original v1393 verifier/observations keep their old identities.
Original OP load is 10FC, DGROUP 2030. Named hooks are decoded segment:offset:
Logo 0A74:14F5, PI loaded 0A74:1523, PI drawn 0A74:1534, second song-command
entry 0DA1:0264 (the PLAY observation), and measure end 0DA1:039D. The later
logo-started hook 0A74:15D5 is a separate boundary, preserving the source claim.
Its complete GDC stream binds the initial post-both callback state [0,1,32],
first frame start and cadence. Raw PIC cycle budgets bind first Timer-B schedule
and every target loading boundary. New inputs subtract first-GDC from first-B,
then admit the same original loading work through maintained frontend adapters.
The observed counter fields are assertions only. Two profiles have different
initial display timestamps; do not substitute a universal 1.875 ms epoch.

| Original CPU profile | 24,000 | 36,000 |
| --- | --- | --- |
| first GDC callback | 1.875 ms | 1.916666667 ms |
| first-B display age (rounded input) | 162,850,542 ns | 113,377,278 ns |
| decoded entry count | 12 | 9 |
| Logo entry count | 16 | 12 |
| PI loaded count | 20 | 14 |
| PI drawn count | 23 | 17 |
| PLAY count | 24 | 17 |
| measure-ready count | 117 | 110 |

All twelve original loading/readiness counter assertions per input pass in
actual maintained FrontEnd with real PI/BFNT/music/effect/config and strict
ROM. Sixteen executions (two inputs × four modes × GNU/UBSan) complete first
OP startup; complete compiler output tables agree. Sound PLAY equals the supplied phase input:
255,036,542 / 178,822,806 ns after installation, with 93-refresh readiness.
Zero-work and graphics-only removal reject the independent epochs/counters.
A separate display-only control keeps every sound interval and the same PLAY /
READY sound state, but never advances its external display clock: completion
and sound gates pass, while original display assertions reject. These gates
must remain independent. An actual extra frontend checks one-nanosecond crossing
of a fractional external origin, no double logical refresh and rollback rejection.

Eight fresh default CLI runs cover all four driver profiles, full startup,
four natural demos and fresh OP ready. All 129 files per run equal their
corresponding immutable v1395 baseline pins. Muted private Linux Xvfb
startup/selection/input/focus/release/exit passes with zero audio device opens.
This renews scoped regression for the current source, not old receipts.

The original cadence is 17.72322658483988 ms; the native interval remains the
previous rounded 17,723,227 ns. Counter agreement here does not prove exact
sub-refresh timing, hardware wait-edge alignment or physical scanout. Explicit
bracketed loading inputs are not native per-function CPU estimates. Default
resource/graphics/initial-epoch costs, full pictures, broader combat/process,
chip/IRQ/audio, cross-emulator and Windows acceptance remain open.

Replay producers: `.analysis/reconstruction/probes/native-gdc-work-v1396-v2/`;
current source freeze and receipts: `.analysis/port64/native-gdc-work-v1396-v2/`.
Restore retired inputs before another replay and use fresh namespaces:

```sh
python3 .analysis/reconstruction/probes/native-gdc-work-v1396-v2/verify_retention.py --restore
```

The original three-mode preparation stays immutable. A separate supplemental
mode-3 reset readback binds both physical save files; each actual caller checks
and records starting/final reset-file hashes before/after execution.

V1 source 8657d4a2 is retained as rejected: actual GNU initialization prefix
counts are +1 in ten places per CPU while ENTRY/READY agree. V2 moves OP
initialization before the first headless refresh admission; epochs and work
inputs are unchanged. Original failed receipt/producer stays immutable under
`.analysis/reconstruction/probes/native-gdc-work-v1396/`.

Lossless retirement reclaims 472.69 MiB; all logical build/video/state
contents and protected source/receipt identities remain recoverable.

## Original OP wait ownership (v1397)

Observed pinned OP decoded payload SHA 13222cb6, packed target 8fc3b67f;
69028-byte payload and 804 ordered candidate-derived relocation sites remain
diagnostic topology, not packed-file exactness. Runtime load 10FC, DGROUP 2030.
Capstone reads complete bounded instructions from the hash-attested payload:

- 0DA1:002B frame_delay (21 bytes) clears DGROUP:1AC6 before the unsigned
  comparison; zero therefore clears then returns. Far return consumes 2 bytes.
- 0DA1:0370 snd_delay_until_measure (49 bytes) uses that service only when
  DGROUP:09E1 is zero. Active BGM repeatedly queries INT60 / INT61 AH5 and
  compares AX with the target measure; it neither resets Count1 nor calls a
  VSYNC delay. Far return consumes both 16-bit arguments (4 bytes).
- 0A74:16DD is the input_reset_sense far call immediately before the Logo
  wait. 16E2 polls Count1 >=2; 16E9 clears it; 16EF is after that clear and
  before the page switch. Hooks avoid the inner busy loop.
- IRQ vector points to decoded 0000:25C6. Its bounded prefix selects DGROUP,
  adds [0854] to the 16-bit cadence accumulator [1ACE] and skips both counter
  increments on carry. Otherwise [1AC6] / [1AC8] increment separately from GDC
  blink state. The skip accumulator is static target evidence here, not a
  newly measured hardware/31-kHz runtime model.

Three runtime-observed actual original GAME.BAT routes stop read-only at the
second Logo Count1 reset, before its page switch. Scalar memory includes both
16-bit IRQ counters and IVT0A. Complete original payload, source/tool inputs,
relocated hook windows, full PIC fractions, matched guest DOS returns and
complete GDC streams pass the independent reader/model. There are 37 named
boundaries, 38 full clock checkpoints, and 119 / 111 / 27 GDC events. The last
terminal scalar is recorded by the GDB reader before the emulator resumes;
its separate F record and opcode/address identity are required. No guest
memory/register writes, driver calls or input injection are performed by the
observer. Normal GAME.BAT writes its own diagnostic file; initial and final
full disk hashes remain separate. All launches are Linux SDL dummy and muted.

| Scenario | Measure start → ready Count1 | First Logo enter → pass / Count2 | First bracket | Second bracket |
| --- | --- | --- | --- | --- |
| FM86, CPU24000 | 10 → 103 | 104 → 104 / 104 | 0.010875 ms | 23.755833 ms |
| FM86, CPU36000 | 7 → 100 | 100 → 100 / 100 | 0.009028 ms | 18.852361 ms |
| BGM off, CPU24000 | 10 → 0 | 1 → 2 / 11 → 12 | 7.599583 ms | 31.722333 ms |

The first bracket includes input_reset_sense before the unsigned wait test.
Active first waits admit zero new counted interrupts. Every second wait
enters Count1=0, passes Count1=2 and clears it; Count2 continues (106 / 102 /
14 at the terminal reset). All first resets likewise preserve Count2.
BGM-off frame_delay(0) has zero IRQ progress and clears Count1 in 0.000250 ms.
The control changes only initial MIKO.CFG byte3 (BGM) and byte9 (checksum);
the independent reader reconstructs the initial disk hash from the retained
unmodified preparation image. Executables, drivers, GAME.BAT and other inputs
are independently read from the final physical disk and remain pinned.

Each second IRQ wait progresses by two while crossing one observed GDC seam;
BGM-off first progresses by one while crossing zero. Do not use display/blink
callback counts as IRQ Count1/Count2, even though v1396 correctly forwards
elapsed work to the display owner. These are distinct timing phases.

The public reader rejects busy-reset / fallback-reset, missing Logo reset,
below-threshold passage, false PIC time and changed GDC counter controls. Six
public tests additionally cover unsigned wrap, an IRQ immediately after reset,
truncated pairs and second-counter extent. The initial 33-hook capture is a
real failed attempt: the pinned observer permits at most32. Its failed wrapper
and logs stay failed; V3 removes the unreachable menu hook and leaves code and
inputs unchanged. The BGM preparation's first import failure and two rejected
reader versions remain preserved separately. The second reader incorrectly
compared the final disk with its initial control disk; the final reader checks
the reconstructed initial hash plus the separate final hash and physical
inputs, without normalizing guest output.

Native Scene::advance currently queries the measure once per logical refresh;
run_logo_frame always waits two more ticks. Original evidence falsifies these
as general wait ownership semantics. This batch changes no native/DOS product
source: native remains510/ea5c016d at49b2fa5 and DOS fingerprint6f5898dd. The
existing v1396 cold-build/caller/default-Demo proofs remain unchanged; no fresh
native build or original/native timing equivalence follows from this Oracle.
Next model active PMD service without an extra logical frame, separately own
unsigned IRQ Count1/Count2 and phase, and preserve reset-before-frame_delay
versus inherited-count-and-reset-after-Logo. Do not fit the measured brackets
or use a universal next-GDC-edge wait. Default work costs, physical/second-
emulator timing, full pictures, broader combat/process and Windows remain open.

Replay from the DOS root, restore the owned image/font archive first:

```sh
python3 .analysis/reconstruction/probes/native-vsync-waits-v1397/verify_retention.py --restore
python3 scripts/runtime/verify_op_wait_clock.py \
  --capture .analysis/runtime/candidates/dos-op-v1397-waits-base-v3 \
  --capture .analysis/runtime/candidates/dos-op-v1397-waits-cpu36000-v3 \
  --capture .analysis/runtime/candidates/dos-op-v1397-waits-bgm-off-v4 \
  --model-dir .analysis/worktrees/port-modern-64/.analysis/port64/native-startup-clock-v1391/original-zero-repeat/boot-model-v3 \
  --model-receipt .analysis/worktrees/port-modern-64/.analysis/port64/native-startup-clock-v1391/original-zero-repeat/boot-observation-v3.json \
  --output-dir .analysis/reconstruction/probes/NEW-wait-reader
```

Accepted independent receipt: .analysis/reconstruction/probes/native-vsync-waits-v1397/reader-v3/receipt.json,
SHA 7da54bf954debd9fe61f82e64d70f0b5c5772dcce0d62939411304a4e9b65157. Source, full scalar/GDC streams, terminal logs/receipts, negative
results and earlier current producer freeze stay protected.

Both complete CI gates pass (root447/native345), tracking and diff checks pass.
Lossless retirement of only18 current disposable image/font files reclaims
218.40 MiB; all5 complete blobs and116 current protected proofs read back.
A separate post-CI1050-file source-backed cache journal recovers16.38 MiB.
No original target, host package/save, complete stream or old producer is
removed; failed attempts stay failed. See retention for exact recovery.

## Original IRQ raster phase and native counter primitive (v1398)

Target evidence remains candidate-local-attested. Session preflight passes;
packed OP database attestation is READY. Decoded payload69028B SHA13222cb6,
804 ordered diagnostic relocations84972ed5 and full relocated memory pass
independently. Runtime load10FC/DGROUP2030, IRQ0000:25D6 executes before
Count1[1AC6] then Count2[1AC8]; cadence increment[0854] / accumulator[1ACE]
are zero in both retained24kHz routes. Frame delay0DA1:002B and Logo0A74:16E2 /
16E9 keep v1397's distinct reset contracts. No exact unit promotion follows.

Two fresh read-only GAME.BAT captures add all IRQ-before-increment boundaries
and the pinned emulator's VGA_VertInterrupt callback. The32-hook cap is
preserved by removing the unused title_start hook. CPU24000/36000 cover
143/139 scalar rows,144/140 full GDC checkpoints,119/111 display callbacks and
106/102 armed callback / guest IRQ pairs. Complete raw load, relocations,
physical inputs, PIC fractions, full clock stream, DOS calls/returns and terminal
second-Logo reset pass scripts/runtime/verify_op_irq_clock.py with the independent
GDC model. Both counters progress completely; Count1-only Logo clears preserve
Count2. Missing IRQ, changed counter/skip, blink alias and frame-start mutations
reject, in addition to inherited wait/load/clock controls and four public tests.

Pinned DOSBox-X source schedules IRQ at float(vrstart+0.0001ms), where
vrstart=(AL+VFP)*horizontal_total/characterHz. Snapshot master AL400/AW80,
HS8/HFP10/HBP8/VS8/VFP7/VBP25 gives horizontal106, vertical440,
retraceStart407, characterHz=21052600/8=2631575 and period17.72322658484ms.
First display epochs1.875 /1.916666667ms remain independently observed;
no fitted initial age. IRQ callbacks precede the next GDC frame callback.
Actual PIC dispatch lateness ranges0.005797–12.832709 /0.011797–1.377072 CPU
cycles; callback-to-0000:25D6 varies50–138 /64–142 cycles. These are scoped
instrumented emulator observations. Additional IRQ hooks change second-Logo
brackets to25.046208 /18.527528ms, while v1397 retains23.755833 /18.852361ms;
both have the same inherited104/100 firstwait and terminal106/102 Count2.
Do not replace one capture's timing with another or infer uninstrumented
physical timing. No fixed CPU service latency is derived.

Native port64/pc98_vsync.hpp implements unsigned16-bit Counter, carry skips,
START/END, Count1-only clear and an inverse counted-wait query. RasterClock
uses explicit geometry/display epoch, rational character-cycle phase and a
zero-latency ideal-edge adapter convention. START never resets beam phase.
Default IRQ adjustment is zero; only this emulator comparison supplies its
source-defined100ns adjustment. Counter CPU instruction records and raster
schedule records are checked separately; this is not combined frontend timing
acceptance. Source manifest512/efea1700, DOS fingerprint6f5898dd unchanged.

Cold GNU builds72 programs /70 CTests; optimized UBSan builds8 selected
programs /5 sound/VSYNC CTests. Their compiled probes reproduce all208
counter records and230 host callback deadlines, with integer-ns source schedule
difference at most2ns and byte-identical GNU/UBSan output. The original float
time remains retained. Input v1 rounded PIC admission too early at two points;
failedprobe-v2 logs remain. V3 rounds admission upward to ns rather than changing
the raster formula. Probe-v1's C++20 option is unsupported by the pinned GNU
compiler; V3 uses C++17. Failed sources/programs/logs stay independently frozen.
Compiled one-variable mutations reject Count2 clearing and blink-phase edges;
a synthetic carry-disabled contract also rejects (not an original31kHz run).

Eight current-source actual CLI routes cover none/pmd/pmdb2/pmd86 under GNU /
UBSan, complete startup/four demos/fresh OP. Every129-file output set equals
its closed v1396 profile baseline. Prior GUI/physical/full-picture limits remain
owned by their earlier sources. The new component is deliberately staged:
Scene/FrontEnd still need busy PMD service without logical refresh admission,
IRQ ownership installation, inherited Logo wait and the distinct clear sites.
Default CPU/resource/graphics work and physical/second-emulator phase remain
open. The old coarse verify_op_startup.py service stub that always supplies two
wait counts cannot establish this integration's correctness.

Current replay surface (DOS root):

```sh
python3 .analysis/reconstruction/probes/native-irq-clock-v1398/verify_retention.py --restore --prefix .analysis/runtime/candidates/dos-op-v1398-irq-
python3 scripts/runtime/verify_op_irq_clock.py \
  --capture .analysis/runtime/candidates/dos-op-v1398-irq-base-v1 \
  --capture .analysis/runtime/candidates/dos-op-v1398-irq-cpu36000-v1 \
  --model-dir .analysis/worktrees/port-modern-64/.analysis/port64/native-startup-clock-v1391/original-zero-repeat/boot-model-v3 \
  --model-receipt .analysis/worktrees/port-modern-64/.analysis/port64/native-startup-clock-v1391/original-zero-repeat/boot-observation-v3.json \
  --output-dir .analysis/reconstruction/probes/NEW-irq-reader
```

Accepted original receipt334d6fde… at native-irq-clock-v1398/original-reader-v1/;
native receipt00084b0e… at native .analysis/port64/native-irq-clock-v1398/probe-v3/.
Source freeze/current builds/default regression all have fresh identities;
older producers remain unchanged. Complete retirement/CI counts appear below.

Lossless retirement of 3,110 current logical files / 1,451 unique blobs
reclaims 528.63 MiB, retaining 39.20 MiB archive plus journal. Complete gzip
CRC/EOF, member hashes and every temporary restored size/mode/nsmtime pass
before deletion; all 694 protected current proofs pass after. New retention
reader independently verifies frozen old510/ea5c and current512/efea. The old
v1396 primary and text archives are composed; the first one-archive checker
remains failed with its own source/logs. Old proofs are not restamped. Complete
original raw/GDC streams, current source/probes/selected executables and failed
attempts remain live. See current handoff/retention for exact restore commands.

Both full CI gates pass (root 451 / native 345 tests), with tracking and diff
checks. Post-CI source-backed Python cache cleanup retires 1051 files,
recovering a separate 16.32 MiB after its journal. Total current net cleanup:
544.95 MiB. The cache journal is disjoint from lossless archive retirement;
retained source regenerates these caches. Goal remains active.

## Repeated START retains cadence phase (v1399)

A late direct target re-read invalidates one v1398 generalization: START does
not clear accumulator[1ACE]. OP decoded0000:2552–25BB queries GDC mode through
0000:15C2–1617, selects increment[0854]=0/13311 and clears Count1[1AC6] /
Count2[1AC8] before testing installed mask[0856]. It does not reset accumulator;
END0000:2600–2646 likewise has no counter/accumulator reset. START's source
comment and native model had incorrectly inherited the semantic DOS assembly's
extra reset. v1398's full zero-phase24kHz observations, archived old source and
successful compilation stay valid at their narrow scope; they do not support
nonzero-phase restart semantics.

scripts/runtime/verify_op_vsync_lifecycle.py now independently executes the
complete original START/GDC-query/IRQ instructions under pinned Unicorn1.0.2.
The packed OP42290B identity/MZ structure, decoded69028B13222cb6,804 ordered
relocs84972ed5 and decoded receipt bind the target; topology remains diagnostic
and candidate-local-attested. Two relocated loads10FC/3333, mode bits0/C and
phases0/12345/65535 give12 scenarios. Explicit seeds model one prior counted
IRQ (Count1/2=1, increment=phase, accumulator=phase), installed mask0xFB and
callback segment0. BIOS AH31 replies are typed; all other BIOS calls reject.
No IRQ occurs inside START. Real far ret4 / caller retf / IRET frames and all
DGROUP writes / full opcode traces are retained. This is a controlled CPU
semantic diagnostic, not natural full31kHz, DOSBox timing or physical acceptance.

Original START preserves phase in all12 runs. One actual original IRQ after
START with phase65535/modeC adds13311 with carry, leaves accumulator13310 and
counts unchanged. Current native GNU/optimized UBSan matches12/12 full tuples;
published frozen v1398 builds/exits0 but matches only4 zero-phase cases. Its
8 nonzero-phase states reject;2 cases count an extra IRQ. This independent
negative distinguishes successful compilation and zero-state tests from the
actual contract. A failed comparator draft's syntax error remains separately
frozen; it never produced an accepted comparison.

Only native pc98_vsync.hpp / its contract source change,512-file manifest5474b8e3.
Counter START now clears only the two counters and selects increment; initialized
memory supplies initial accumulator0. END/START retains prior cadence phase.
Global RasterClock phase remains separate. Fresh GNU72 programs /70 CTests and
UBSan8 targets /5 CTests pass. Fresh compiled probes also pass208 original
counted IRQ records /230 raster callbacks from immutable v1398 parent inputs;
all old raw/source/report pins are rechecked. Eight fresh full default
none/pmd/pmdb2/pmd86 GNU/UBSan CLI routes reproduce all129 immutable v1396
baseline outputs each. No frontend wait integration or exact promotion follows.

The shared DOS source in both trees still clears cadence_skip_accumulator.
That candidate statement differs from independently executed original OP. DOS
fingerprint6f5898dd is unchanged in v1399; its earlier24kHz demos cannot falsify
this zero-phase corner. Next bounded unit must correct and cold-replay this
shared assembly (including lifecycle/state/layout checks) before PMD busy-
service / inherited-IRQ frontend wiring. MAIN historical deferred exactness and
current historical acceptance stay separate. Do not silently edit old proofs.

Replay from DOS root:

```sh
python3 scripts/runtime/verify_op_vsync_lifecycle.py --output-dir .analysis/reconstruction/probes/NEW-vsync-lifecycle
```

Current private index: native-vsync-lifecycle-v1399/ (DOS-root probes and native
port64 outputs). original-public-v4/receipt.json pins complete12-case execution;
native lifecycle-v2/receipt.json pins new GNU/UBSan and rejected old-v1398 output.
New source/cold-build/IRQ/default-profile receipts are independent; earlier
namespaces remain unchanged. Current single-core/nice19 work uses CPU1 while
user CPU0 is occupied; original timing observations are not recollected or
restamped. Windows GUI/focus/keys/audio remain excluded.

Both complete CI gates pass (root451/native345 tests), tracking/diff checks pass.
Lossless retirement of 3104 current files / 1447 unique blobs
reclaims 468.27 MiB after its 16.88 MiB archive/journal.
Full gzip CRC/EOF, every temporary restored SHA/size/mode/nsmtime and all
688 current protected hashes pass; frozen old v1398 proof is separately
verified. A disjoint post-CI 1053-file source-backed cache journal recovers
another 16.41 MiB. Current v1399 net cleanup totals 484.68 MiB. Combined
v1398 + v1399 accounting is disjoint for owned build/capture namespaces and
counts each final regenerated cache set once; no old target/proof/host save is
removed. Source freeze, full original/compiled negatives and selected current
programs remain live. Recovery reader: native-vsync-lifecycle-v1399/
verify_retention.py (--restore/--prefix; --parent v1398/v1397/v1396).

Next shared-DOS replay must also preserve original mode-query-before-increment-
selection/count-clear ordering. Current assembly clears those fields before
BIOS query. The installed/no-IRQ-inside-START diagnostic here deliberately
does not validate an IRQ interleaved with that query; add that controlled case
when repairing the shared assembly.

## v1400 shared DOS START phase and query ordering

v1400 repairs the shared DOS VSYNC_START owner in both source trees. Query GDC
before selecting the increment and clearing Count1/Count2; preserve the cadence
accumulator. The original MAIN0000:236C, OP0000:2552 and MAINE0000:2110 all have
that order. Their IRQs0000:23E0/25C6/2184 compare callback segments at DGROUP
0770/0852/03FE; callback pointers begin at MAIN076E, OP0850 and MAINE03FC. These are original-relative offsets plus recorded load,
not bare linear emulator addresses.

Each corresponding current root MAIN/OP/MAINE linked product passes108 seeded
instruction comparisons at loads10FC/3333: GDC extension absent/present,
mode0/C, phase0/12345/65535 and prior increment0/13311/65535. An authored
BIOS STI/NOP/IRET mock outside loaded images permits a real original/candidate
IRQ to nest with its own IRET frame before mode selection. Actual BIOS/CRT
wrapper code and physical31kHz are not exercised. Frozen old source still
passes the old DOS vector/callback/END test but rejects96/108 new scenarios.

Cold root build completes all four products (MAIN199471, OP79388, MAINE72246,
ZUN7723 bytes). Actual IRQ vectors, CS renderer operands and MAIN bullet jump
tables pass. Root product fingerprint a34c1357be6dc472ec44800b2fe275a7cbba6ba5344ab7002cc516e2411995d5;
1425 input files are frozen. A fresh muted fixed24000 GAME.BAT/four-Demo route
agrees with immutable original input/score/RNG at15984 gameplay plus4 terminal
boundaries. This is current selected-state regression, not a fresh whole-video,
actor-pool or physical timing acceptance. Historical exact producers are separate.

Original OP diagnostic seed correction: older v1399/v1400 drafts cleared1AD0,
not the callback pointer0850. Actual callback bytes were already zero and no
callback ran. Corrected seed plus operand guards retain all12 old complete
instruction/state/write traces. Old receipts remain unchanged; v2 BIOS mock
hook-CS draft failed and is retained. v4 is the accepted nested-frame reader.

Native x64 source manifest stays512/5474b8e3; no C++ product changed or rebuilt.
The native branch also carries the shared ASM correction; its distinct dormant
DOS graph has not received a whole-product build here. Prior native v1399
70GNU/5UBSan and eight129-file profiles keep their frozen scope/identities.

Replay/retention index (DOS root):
.analysis/reconstruction/probes/dos-vsync-lifecycle-v1400/.
Maintained tools: scripts/runtime/verify_dos_vsync_lifecycle.py and corrected
verify_op_vsync_lifecycle.py. Use --original-artifact main/op/maine with the
current executable/MAP/source; all traces/pins are in linked-*-v4 receipts.
Recovery: python3 .analysis/reconstruction/probes/dos-vsync-lifecycle-v1400/verify_retention.py;
add --restore --prefix for owned archived inputs. Old v1399 strict live-source
readers reject the changed DOS fingerprint; the new check-parent.py verifies
its frozen closure/CRC/blobs separately, without restamping.

Cleanup net 56.03 MiB after archive/journal (15.55 MiB archive),
with 7264 paths/1481 blobs/2351 protected proofs checked;
current source, products/MAPs, old/new compiled controls, original raw evidence
and fresh demo trace remain. Full CI passes root451/native345; source-backed post-CI caches reclaim
16.44 MiB separately, for 72.47 MiB net this batch.

Next connect native PMD busy service and inherited unsigned IRQ waits to
FrontEnd, preserving clear-before-frame_delay / clear-after-Logo, cadence and
global raster phase. Scene still samples measure once per refresh and uses fixed
Logo waits. CPU/resource/graphics elapsed work needs a model. Full pictures,
Boss/death/process, second-emulator/physical scanout and Windows input/audio stay
open. Goal active; targets candidate-local-attested. CPU1/nice19 single-core,
serial and muted; no Windows GUI/focus/host keys/audio device is used.

## v1401 native elapsed startup waits

Updated 2026-10-12. Reconstruction and native development remain active.
v1401 connects OP startup in the native FrontEnd to the independent unsigned
IRQ counter/raster clock. Ordinary frame waits clear Count1 before waiting;
Logo inherits Count1 and clears it after passing. Inactive BGM executes the
frame_delay(0) clear; active PMD is serviced at resident timer deadlines inside
an elapsed admission, without adding a logical refresh. Resource/drawing work
advances the same clock. OP process entry clears counts while preserving raster
phase and cadence accumulator. The default adapter uses ideal24kHz raster
edges with zero CPU/command/ISR latency; it does not fit captured elapsed times.

Original OP decoded DA1:002B(21bytes), DA1:0370(49bytes), A74:16DD(25bytes)
and 0000:25C6 IRQ prefix are re-attested from the pinned payload. Frozen complete
v1397 CPU24000/36000 witnesses retain first active Logo Count1=104/100 and zero
counted IRQ progress; BGM-off clears10->0, then first Logo waits1->2. These
are reused original runtime observations, not fresh emulator runs. The new
native tests reject compiled clear-before-Logo, missing zero fallback and
once-per-refresh PMD mutants. Elapsed batching and fractional PMD deadlines
pass; timer deadlines are checked on three boards at three frequencies.

Native producer512/60cf4491 is frozen. A complete cold GNU build passes70
CTests; optimized UBSan builds9 programs and passes6 selected contracts.
Original legacy startup control15 fixtures executes at loads1000/2000;
GNU/UBSan retain identical scripted-wait event/state traces. This legacy adapter
is separate from timed FrontEnd acceptance. Actual muted frontend matrix passes
132 configuration/restart cases (three PMD profiles, two phases, two compilers,
11 cases each), including six fixture GameOver/MAINE/freshOP paths. These finite
STD fixtures are not new natural six-stage routes.

Eight actual full startup/fourDemo/freshOP captures pass direct original15988
selected-state comparisons each. GNU/UBSan match all129 output hashes per
profile. With PMD enabled only startup-events.txt and text-refreshes.txt differ
from frozen v1399; the other127 outputs, including indexed/RGB/text samples,
shake and splash states, agree. No-driver captures retain all129 baseline files.
No full original picture, physical scanout or elapsed-time equality is claimed.

Root DOS source is unchanged at product fingerprint a34c1357; v1400 retains
its three108-case linked lifecycle comparisons and four-product/Demo proof.
Historical exactness is unchanged; canonicality remains candidate-local-attested.

Replay index: .analysis/reconstruction/probes/native-startup-waits-v1401/
(DOS root) and .analysis/port64/native-startup-waits-v1401/ (native worktree).
Use build.py/validate.py in a fresh namespace, with the frozen source and actual
HDI/font/ROM pins. original-witness.json binds unchanged v1397 ownership;
original-legacy-v1 is the newly executed scripted-wait corpus. check_parent.py
verifies immutable v1399/v1400 archives and closure separately from current
source; do not restamp their strict live-source readers. Restore narrowly with
verify_retention.py --restore --prefix; all proofs/source/selected executables
stay retained. Archive 26.28MiB; net cleanup 817.00MiB before post-CI caches.

Next model default resource/graphics/CPU work and validate timed startup
boundaries against independent original IRQ/PMD observations. Other scenes
retain refresh adapters. Full pictures, Boss/death/process parity, a second
emulator, physical31kHz/scanout and Windows input/audio remain open. Runs use
CPU1/nice19, one serial writer, SDL dummy and mute; no Windows focus or host
keys/audio device. Goal stays active.
Focused commands (DOS root, fresh private outputs):

```sh
PYTHONDONTWRITEBYTECODE=1 taskset -c 1 nice -n 19 python3 .analysis/reconstruction/probes/native-startup-waits-v1401/build.py gnu
PYTHONDONTWRITEBYTECODE=1 taskset -c 1 nice -n 19 python3 .analysis/reconstruction/probes/native-startup-waits-v1401/build.py ubsan
PYTHONDONTWRITEBYTECODE=1 taskset -c 1 nice -n 19 python3 .analysis/reconstruction/probes/native-startup-waits-v1401/validate.py
python3 .analysis/reconstruction/probes/native-startup-waits-v1401/verify_retention.py
```

Frozen old proof inputs are kept unchanged. The first current witness-reader
attempt compared Python tuples with JSON lists and failed; the accepted reader
normalizes only that representation. It retains the old receipt SHA and complete
original timing values. This is not target/runtime data normalization.

Cleanup recovery caveat: the first deletion stopped at a missing compiler
object. All archive blobs had passed CRC/SHA and temporary readback, but the
full original path/mtime journal had not been persisted before deletion.
Receipt-pinned Demo/program contents were recovered; regenerated files have
new filesystem attributes. The final journal is written before deletion and
supports full current-path metadata recovery. 511 auxiliary blobs retain
content SHA/size without original path/mtime metadata. They remain in the final
content union; compiler intermediates can be cold-regenerated. Failed scripts
and logs, cleanup-recovery.json and the complete blob union are retained.
Concurrent source commits/motion work were observed during this interval;
causation of the object disappearance is unproved. Avoid overlapping writers.

Final isolated-checkout CI passes root451/native345, plus tracking and diff
checks. Borrowed pinned targets pass identity/format checks; private Ghidra
project replay skips because those isolated checkouts have no project. Source
and runtime proof identities remain separately pinned. Source-backed review CI
caches reclaim 16.32MiB separately, for 833.32MiB net this batch;
review worktrees are temporary and their tracked document state is preserved.

## v1403 combined producer re-attestation

v1403 integrates remote motion recovery a0b6149 with the independently
validated startup waits. Current native producer514/c2f8d689 is frozen;
CMake's new motion contract and its verifier are now both included in the
complete source manifest. Fresh GNU builds73 programs/71CTests; optimized
UBSan builds10 programs/7 contracts. Unchanged original MAIN0000:1DA8..1E13
and table2134:021E execute at load1000:184908 vectors per compiler agree,
including514 original DIV faults. Complete expanded comparison transcripts
match between GNU/UBSan. The compiled old blanket -32768 rejection fails.
This accepts the bounded corpus and explicit native fault surface; it is not
an exhaustive four-coordinate Cartesian product or historical byte exactness.

Eight fresh current startup/fourDemo/freshOP profiles each match original
selected state at15988 boundaries and every129 frozen v1401 output hashes.
Startup/IRQ code itself is unchanged. Physical timing, default resource/CPU
costs, full pictures and broader Boss/death/process remain open. Continue
bounded source recovery before long game campaigns. Windows GUI/focus/host
keys/audio opens remain excluded while the host is in use.

The original native push encountered a concurrent non-fast-forward remote
motion commit. Both histories were merged without force pushing. v1401 proofs
remain frozen at512/60cf4491, including its132 frontend fixture cases and
70GNU/6UBSan checks; their strict live-source reader correctly rejects current
source. A new reader verifies its archive/1150-file closure independently.
No old receipt was edited to claim the new producer. Root DOS source stays
unchanged at a34c1357; historical exact counts/canonicality are unchanged.

Current replay index: .analysis/reconstruction/probes/native-startup-motion-join-v1403/
(DOS root); native .analysis/port64/native-startup-motion-join-v1403/.
Use build.py, validate.py and verify_retention.py in a fresh namespace;
check_frozen_parent.py reads old proofs and the expected strict-reader rejection.
All current source/program/vector/capture inputs are pinned. The read-only
original MZ target, complete1136 relocation topology and two separate compiler
outputs remain distinct evidence. Runs are CPU1/nice19, serial and muted.

Additional owned cleanup 468.70MiB after 16.93MiB archive. Full current
path/hash/size/mode/nsmtime journal is persisted before any archive/deletion.
CRC/EOF, all blobs, every temporary metadata restore and protected proofs pass.
No prior producer is retired. The v1401 initial auxiliary-metadata caveat remains
explicit in retention notes; current v1403 paths have full recovery metadata.

Final current-tree CI passes root451/native345, tracking and diff checks.
Root's actual private target/database/Oracle mutations pass; native private DB
checks skip absent projects. Additional post-CI source-backed caches reclaim
16.52MiB. v1403 total net cleanup is
485.22MiB; disjoint v1401+v1403 retirement/caches total 1318.54MiB
(1.29GiB), excluding temporary review-worktree removal.

The latest remote port/modern-64 is ce48946 and separately adds GRCG circle /
stage-line recovery. Its renderer changes are not part of this514-file verified
snapshot. This snapshot is published on review/startup-motion-join-v1403;
merge it only after selecting one writable source session and attesting the
combined producer. Both incoming histories are preserved. The older v1401
startup implementation itself already reached port/modern-64 through fffcc83.
