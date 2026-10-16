# Stage Lifecycle evidence

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

This is a separate root-owned DOS comparison;native code/acceptance retain their v1455 producer.

Sixteen owned capture image/font/raw aliases are archived in six blobs. Net
release is 157.621 MiB after archive, gzip and both journal files. The chain
verifies 24890 distinct protected hashes, including all 21663 parent
hashes and the two old public capture paths. New protected recipes use private
immutable copies. Actual archive restoration and fresh-output reducer replays
reproduce both failed state aggregates and the passing video regions before
SHA/mode/nsmtime verification and retirement of all sixteen aliases. No borrowed
files or duplicate cleanup credit. Use `replay_restored_v2.py --output-dir NEW`
for repeatable recovery; initial receipts, snapshots and replay remain unchanged.

## Recorded elapsed display fixture (v1455)

Native `d22e190` adds an optional recorded-time replay through the existing
elapsed display interface. Both cold GNU and optimized UBSan programs match
**all 59 complete 640x400 RGB pictures and all 59 active TRAM samples** at their
recorded score-return times. All 9835 selected updates, nine pools, four Boss
blocks, homing, consumed input, Continue/save, popup/title rows and 2665 actual
BB calls still pass. Source closure: 565/533075c0; GNU 87 programs/83 CTests pass.

The independent raw PIC clock predicts all 9896 original phase/count observations
without fitting a phase. Only frame numbers and elapsed nanoseconds enter native.
Default logical timing still fails three samples by 407 pixels each on this new
capture; the old v1454 two-sample failure remains unchanged. This fixture accepts
completed display boundaries, not natural OP/loader/UI-interior or CPU/I/O timing,
every frame, physical scanout or campaigns. Primary original/reconstructed DOS
beyond 8000, native Stage2 update 9836, NP2, Windows, pristine provenance and
historical exactness remain open. Both full development goals remain active.

Evidence is runtime-observed under the pinned DOSBox-X binary
`6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1`.
Pinned MAIN remains 156258 bytes/SHA `077440a3c4e9ab52...`, 1136 relocations,
entry 0000:0000 and candidate-local-attested provenance. Fresh preflight and
full MAIN Ghidra/MZ attestation pass. Original load is 10FC and DGROUP is 3230.
After-actor observations are relative MAIN 0AAF:01B3; sampled score returns are
0AAF:0207. The extra actor 9836 is a partial tail, excluded from native acceptance.

The source/ELF/compiler ABI witness binds 8-byte PIC ticks and signed cycle
counts, GDC size 232 and phase/count/rate offsets 196/197/198. No debugger host
function is called. One extra hardware execution breakpoint observes actual
master cursor advances only until actor 1; the loader watch retires before the
actor watch is allocated. Later timestamps reuse existing actor/score stops.
Every clock row retains raw CPU registers/segments and a read-only assertion.
Every actor GDC hash/three clock bytes matches the complete CRC-checked ordinary
video stream; all 59 score rows bind complete checkpoint video and CPU context.

The first actual display initialization is PIC 15/8 ms: frame_start equals the
raw PIC rational and mode_time_base, with mode frame count zero. This supplies
the independent origin. Fixed constructor phase/count zero replays all 1084
short-probe and 1109 full-probe master entries without resynchronization. The
existing rounded 17723227 ns native period then predicts both phase and count
at all 107 short and 9896 full business boundaries, with zero differences.
Raw blink bytes are verdicts; the exported file contains only frame/ns rows.
Score-return times replace actor times on the 59 picture frames. Frame 0 display
is excluded; its native output checks only the common constructor reset.

The two captures have different elapsed startup durations. Selected state,
RNG/input, all nine native pool bytes and final CFG/SCR identities reproduce
v1454; timing-observer inertness is not established. Do not reuse one capture's
timestamps with another or relabel the old logical failures. On this new capture,
default logical mode fails 9349/9600/9700 by 407 pixels each. Its complete 177
outputs equal the prior b23a program on the same capture. Recorded-time GNU and
UBSan agree on all 177 outputs and each independently matches original RGB/TRAM.
The live product blink algorithm, display period and logical gameplay clock did
not change. Intermediate blocking UI polls remain explicit component stimuli.

Twelve actual-data controls reject wrong PIC rationals, CPU boundaries, extents,
read-only assertions, prefix/score phases, rate, epoch, period and native clock
outputs. A separately compiled producer reads all elapsed times but omits both
existing `observe_text_time` calls. Its 9835 selected state/pool/input/homing/save
gates pass, while required actual clock output rejects all 9836 boundaries.
An input file alone cannot satisfy recorded-time acceptance.

Replay from the DOS repository root, using fresh output names and restoring
only the four full-capture aliases from the closed journal first:

```sh
python3 scripts/probes/attest_th04_display_clock.py \
  --capture .analysis/runtime/candidates/native-clock-phase-v1455-original \
  --main .analysis/targets/th04/main.exe --output .analysis/NEW-clock.json \
  --times-output .analysis/NEW-display-ns.txt
python3 .analysis/native/port64-recovery-v1445/port64/verify_ordinary_state.py \
  --dos-root . --original .analysis/runtime/candidates/native-clock-phase-v1455-original \
  --exe .analysis/native/port64-recovery-v1445/.analysis/port64/clock-phase-v1455-final/gnu/th04-port64 \
  --output-dir .analysis/NEW-elapsed --frontend --require-homing --updates 9835 \
  --recorded-display-time
```

The immutable `full-watch/` capture snapshot and `full-capture.log` under
`.analysis/reconstruction/probes/native-clock-phase-v1455/` record the capture
recipe. Its `capture.py --original` uses the pinned emulator receipt, font,
video layout, `--end-after 9836 --dialog-at-frame 6548 --dialog-checkpoints
--continue-at-frame 7547 --post-boss-dialog-at-frame 9348`. Public clock reports,
private producer manifests, cold source archive/builds, all raw time evidence,
negative controls and the default failures remain distinct.

Verified recovery restores eight owned capture aliases and the actual compiled
ignored-time counterexample, replays it and both cold 9835-update producers, then
checks SHA/mode/nsmtime and retires all nine aliases. All 177 picture/index/TRAM
identities reproduce per program; the counterexample still rejects all 9836
clock boundaries while its selected gameplay gates pass. No borrowed files.

The closed retention journal preserves all 18400 parent hashes and verifies
21663 protected hashes. It retires 1214 owned files into 129 blobs:
500.203 MiB after archive/gzip, or 482.402 MiB after the three journal files too.
The initial journal mistakenly froze its still-open console log; preserve it and
use `closed-retention.json` for the explicit one-log metadata correction and
`recover_closed.py` / `replay_restored_v2.py` for recovery. No target, source,
producer, capture, old failure or parent journal was rewritten.

## Explosion palette and dialogue back-page repairs (v1454)

Native `4b3bf1d` fixes the measured full-picture failures at 9284 and 9349.
Both fresh GNU and optimized UBSan programs retain all 9835 selected ordinary
updates, nine pools, four Boss blocks, homing, player input, Continue/save,
popup/title rows and 2665 actual BB calls. All 59 complete pictures are compared:
**57 RGB samples pass; 9600 and 9700 still differ 407 pixels each**. All 59 active
TRAM samples pass. Source closure: 565/b23a708a; GNU 87 programs/83 CTests pass.
Stage2 update 9836, full campaigns, raw graphics-plane identity, elapsed/scanout
parity, NP2, Windows, pristine provenance and historical exactness remain open.

The original remains the pinned candidate-local-attested Japanese MAIN. Fresh
preflight and full Ghidra/MZ attestation pass. Original DOSBox-X capture remains
the immutable v1453 post-Boss-v2 input at load10FC/DGROUP3230. Four archived
capture aliases are borrowed by exact journal ownership; they are not new cleanup.

Palette observation and repair:

- Actual after-score9284 DGROUP 03A4 contains150; the old native completed display
  reads100. A private observer of producer 565/3cf3900b reproduces all 204 old
  frontend outputs, including 177 complete BMP/index/TRAM files, before its new
  clock/State observations are used. Original MAIN 0AAF:6FA3 calls big explosion
  renderer MAIN 0AAF:2E65; its actual 2F21 store writes150 to shared PaletteTone03A4.
- Seven isolated original Unicorn2.1.4 cases reproduce150/100 and the148..106
  decay, plus an inactive case preserving incoming73. The real polar/aging/
  palette instructions run; only existing sprite draw ABI seams are intercepted.
  Each final compiler also passes all 900 original foreground/explosion vectors.
- Native State now publishes Boss foreground palette writes after preparation.
  The blank graphics beneath TRAM select a black source palette entry and use
  the live toned DAC, so they also brighten during the flash. This replaces a
  literal black RGB fill; it is not a fitted pixel region. Old158776-pixel9284
  failure becomes zero across the complete640x400 picture.

Dialogue page observation and repair:

- Actual original 9348 player/animate/run/return CPU, stack, code and full memory
  contexts retain their v1453 independent witness. Original MAIN 0AAF:2C19 copies
  front to back before 2C1C enters dialog_run; 2C29 selects DGROUP46FC back.
  At run entry all 70,656 physical playfield bytes across four planes agree
  between pages. During the script that back stays unchanged; front differs
  in9,928 bytes from portrait drawing. Actual9349 displays the copied back.
- Native dialogue now starts from the completed front snapshot before the
  blocked player/Boss prefix. Its pre-portrait boxed copy survives the resumed
  suffix; Bomb and actors draw over that base. Repaints, pause/GameOver snapshots
  and fades share the same frame owner. The next ordinary update releases it;
  new MAIN installation clears ownership. Native indexed-plane identity is
  still unproved; the claim here is observed page ownership and full RGB.
- The first compiled prototype incorrectly retained the portrait-bearing
  front and still failed19351 pixels. Switching only its copied-page accessor
  to the pre-script back makes the complete9349 picture equal. The actual
  failed producer, source and result remain. Eleven real raw-context negatives
  reject copy/back/portrait/CPU-page/display/role/frame/extent corruption.
  vramop17 includes flags above page bit0; the first unmasked-byte assertion
  failure remains, and the public reader correctly interprets that page bit.
- Review restored the existing Bomb require_cdg(0) resource check before
  publication. Initial candidate cold programs/results remain immutable; the
  final checked directories bind the restored guard to a new source closure.
  The initial direct-alias pin lookup and doubled-v2 executable-path failures
  are also retained as failed attempts, not successful observations.

Remaining clock gate:

The unchanged old observer records native refresh 10808/visible1 at 9600, versus
original master GDC phase 0, and native11008/visible0 at 9700, versus original phase3.
TRAM is equal. A diagnostic copy of original projection changes only blink
visibility and accounts for all 407 pixels at each boundary. This is a
counterfactual explanation, never acceptance or a target phase fed into native.
Final checked programs still reject those two actual complete pictures. Window
elapsed-time handling and this logical headless admission path are separate;
measure the actual elapsed origin/work/reset scenario before changing clocks.
Do not fit an offset, mask blink pixels, or waive the59-sample whole-picture gate.

Replay index: `.analysis/reconstruction/probes/native-defeat-pixels-v1454/`.
`final/cold-source.json` freezes the565-file source; checked GNU 87/cache and
optimized UBSan game/Orange/cold cores live under native
`.analysis/port64/defeat-pixels-v1454-checked-final/`. `final/validate.py` records
all 9835 state/entry/popup and 59 full RGB/TRAM gates in `final/result.json`.
`probe_palette_writer.py`, `page_controls.py`, `display-diagnosis.json` and
`dialog-pages-witness.json` retain separate original/compiler/native evidence.
Public reader: `scripts/probes/attest_th04_dialog_pages.py`. Restore journaled
capture aliases before strict original readers; use fresh outputs and preserve
all earlier receipts. Initial89.664MiB observer retirement is separate from
final retention. Both complete reconstruction/native goals remain active.

Verified retirement preserves 18400 protected hashes. The final journal
retires 2164 owned files in 136 blobs and releases
576.953 MiB after archive and new gzip recipes. The earlier observer journal, covering206 files, separately releases 89.664 MiB; disjoint total 666.617 MiB.
Final checked GNU 87/cache, UBSan game/Orange/cold cores, all 59 GNU pictures,
original compressed captures/live fonts and all source/failed/clock/page proofs
remain live or losslessly recoverable. `recover_initial.py` restores the
retired display observer/duplicate frontend inputs;`recover.py` handles final
owned intermediates. Both verify SHA/CRC/mode/nsmtime. Use fresh replay outputs.

`replay_restored.py` selects the one archived wrong-front executable by equality,
then actually reruns old/GNU/UBSan 9835-update programs. All 177 complete native
picture/index/TRAM observations and selected state/entry/popup results reproduce.
Old9349 still differs 19351 pixels; corrected9349 is zero. Actual9600/9700 retain
407 pixels each. Hash-identical complete comparison inputs reproduce the same
verdicts; no target phase is substituted. The restored owned executable and four
borrowed capture aliases verify metadata then retire. Borrowed bytes receive
no new cleanup credit. Earlier v1453 journals and missing historical94 files
remain unchanged and outside the current owned accounting.

## Boss defeat, post-Boss dialogue and bonus event integration (v1453)

Native `791203f` extends the actual original/native comparison to **9835
updates**, through Orange defeat, post-Boss dialogue, stage bonus and leave.
Both cold GNU and optimized UBSan programs pass selected state/RNG/input,
global homing, nine pools, four Boss blocks, Continue/save, popup/title rows
and 2665 actual BB calls over 9834 intervals. Source565/3cf3900b.
All59 active-TRAM samples pass; the complete-picture gate retains 4
whole RGB failures at frames 9284, 9349, 9600, 9700. Keep these failures.
Stage2 update9836, complete campaigns, raw graphics-plane identity, physical
scanout, NP2, Windows and historical exactness remain open.

The original is the pinned candidate-local-attested Japanese MAIN; no pristine
provenance claim is added. Fresh preflight and segment-aware database checks
pass. Capture uses pinned DOSBox-X ELF6e1a6e70, load10FC, DGROUP3230, with
raw I0..9835 and three device-driven release/Enter waits. The first capture
exhausts optional debugger watchpoints; the second times out in post-Boss
text; the first post-Boss watcher follows a disproved player ordering. All
failures and the complete fourth capture remain distinct immutable inputs.
The successful capture ends before executing Stage2 update9836.

Original observations and native integration repairs:

- Phase254 leaves the global homing target written by enemies/midboss intact.
  Original far13A9:6013 calls common13A9:ACB3 at63F8 and bypasses the normal
  homing tail at63FD. Six isolated Unicorn2.1.4 executions retain both a real
  incoming target and the none sentinel, including phase254->255. Native had
  republished stale Boss snapshot homing; actual `shots_fire` then consumed
  two extra random bytes at9288. Test the entry phase so5->254 still publishes
  its normal tail once. The repaired global matches9835 original boundaries.
- Original Boss bonus13A9:6548 calls yellow allocator13A9:0300. Six isolated
  original executions check1/3/10 rewards and ring wrap. Native Orange already
  emitted point events, but State ignored them; the first missing yellow
  pool slots occurred after update8015. The existing point model now receives
  these events. Do not confuse this Boss helper with the Midboss helper64DE.
- Actual frame9348 executes player0AAF:5FCF before text animate0AAF:2BFB,
  run0AAF:2A7C and return13A9:AE19. Raw CPU/conventional memory/DGROUP/code
  and BP/near-far return chain prove main return0109 and player return00F4.
  Player consumes Shot32, then UI returns Enter8192. Literal executed player
  input is recorded once; resumed suffixes do not relatch it. STD dialogue6548
  waits before player, while GameOver7547 and post-Boss9348 wait after it.
  Twenty-two real-context negatives reject wrong ownership/order and cues.
- Bonus context now reads live Continue/miss/Bomb totals. Actual Continue1,
  credit6, power94, graze23 and18 points yield12330*3/10*8/10=2959,
  followed by195 score drain to2764. Default Continue0 had awarded3699.
  Existing arithmetic is retained. Persistent TRAM receives SJIS/gaiji events
  once at bonus application and the Bomb HUD consumes its existing event.
  The former direct RGB text layer is removed; leave replaces cells in order.
  Intermediate actual replays separately retain the missing labels and the
  remaining Bomb glyph defect. Complete performance-state coverage remains open.

The prior38-frame reader remains unchanged. The new blink-aware reader checks
all59 complete640x400 RGB images and all8000 active TRAM bytes per sample.
A pinned-header ABI probe gives GDC size232 and blink/count/rate196/197/198;
the pinned ELF text renderer independently reads pc98_gdc+0xc4. Projection
uses the captured original phase, never feeds it to native and fits no offset.
Actual9349 font/video controls change407 pixels at phase0;phases1/2/3 agree.
Bad phase/count/rate, ABI, emulator and source identities fail. Hidden/raw
index differences stay diagnostic and cannot establish graphics-plane identity.

Replay index: `.analysis/reconstruction/probes/native-boss-extent-v1453/`.
`hud-fixed/cold-source.json` pins the final565-file closure; final GNU87/83
CTests and optimized UBSan game/Orange use fresh directories under native
`.analysis/port64/boss-bonus-v1453-final/`. `validate_hud.py` records the full
9835-update state/entry/popup gates; `compare_final_pictures.py` records the
separate59-sample failures in `result.json`. The actual original capture is
`.analysis/runtime/candidates/native-boss-extent-v1453-postboss-original-v2/`.
Use the explicit third wait and actual `postboss-witness-final.json`.
Earlier exploratory inputs and incomplete captures are not accepted replays.

Verified retention preserves 16595 protected hashes. The final journal
retires 4118 owned aliases/intermediates in 203 blobs, releasing
1025.941 MiB after archive and new gzip recipes. The earlier
two exploratory raw pool streams separately released 455.738 MiB;
disjoint total 1481.680 MiB. Final GNU87/cache, UBSan game/Orange/cold cores,
all59 GNU pictures, original compressed captures/live fonts and all source,
negative and failed-attempt receipts remain live or losslessly recoverable.
`recover.py` verifies SHA/mode/nsmtime; `replay_restored_exact.py` restores one
actual archived missing-TRAM program plus four owned original aliases. Old,
GNU and UBSan9835-update replays reproduce all177 BMP/index/TRAM observations
and selected state gates;the old title failure and corrected title passes remain.
All five owned aliases and eight borrowed prior aliases verify and retire;
borrowed aliases receive no new cleanup credit. Use exact executable selection:
the first recovery's prefix also restored86 contract programs;all extras were
verified and retired before the corrected replay. Its failed source/log remain.
The first picture aggregate also counted `title-rows.bin` as a picture;its
failed count/log remain separate from the completed59-sample comparisons.
Replay in a fresh output namespace;never overwrite sealed inputs or receipts.

Next locate actual graphics/palette/text writers at the retained failing
boundaries before accepting complete pictures or extending Stage2/process
transitions. Also continue the primary original/reconstructed DOS comparison
using its own MAP/segment identities; original0AAF code points must not be
applied to the reconstructed MZ. No DOS unit or exact ledger is promoted.

## Boss circle clipping and complete sampled pictures (v1452)

Native `a8e0165` fixes the seven remaining v1451 score-area graphics samples.
Actual private pixel-write traces identify the Orange entrance circle at
center (232,40), radius 326, color 9 as the writer of (557,64) at update 6740.
Both trace programs reproduce the frozen producer's selected 8000-update state
and all 38 complete BMP/index/TRAM observations before the repair.

Original MAIN far `0000:11EC` reads DGROUP clipping words 032C..033A.
All 38 captured after-score DGROUPs retain `(32,16)-(415,383)`, with zoom 0;
the native circle helper had assumed the default whole-screen rectangle.
The helper now accepts a clip rectangle,and the common Boss-circle call supplies
that observed stage rectangle. This preserves the target's clipped-bottom-row
asymmetry. Isolated original execution and both compiler profiles verify
900 render vectors and 1053 circle vectors,including 135 stage-clip cases.
Other Boss/disc/rectangle and actor rendering paths are outside this repair.
The first primitive run passed comparisons but failed its legacy Unicorn receipt
lookup. `controls_wrapper.py` aliases the already loaded Unicorn2 CDLL for that
path field only;its hash pins engine 2.1.4/ddb196ec. The successful reruns execute
900 render and 1053 circle vectors per profile,including 135 stage-clip cases.
The logging failure and the wrapper import failure remain retained;neither is
a successful receipt.

Both fresh GNU and optimized UBSan programs now match **all 38 complete 640x400
RGB pictures** at actual score return `0AAF:0207`:zero differing pixels,
including the seven previously failing frames6740,6741,6753,6765,6772,6773,6774.
The uncorrected real producer still reproduces 1377 differing pixels;changing
one complete-picture pixel independently fails the same comparator.
Both profiles preserve selected 21 scalar/RNG/input fields,nine complete pools,
four Boss blocks,Continue,CFG/SCR,popup state/rows and title state/three rows
over 8000 updates,plus 2665 actual BB calls over 7999 intervals. Repeat paints
preserve pools/RNG/input and full pixels. All 15988 native Demo state boundaries
stay equal. GNU 87 programs and 83 CTests pass;source closure 565/394e53f4.

Evidence: `.analysis/reconstruction/probes/native-score-pixels-v1452/`.
Original capture remains the immutable DOSBox-X v1451 score capture with live
font/video/DGROUP;the v1450 constructed-BB Oracle remains refuted. The correct
pre-scroll title phase from `a8a67af` is retained. Old negative reports and
retention journals remain unchanged. Restore the v1451 score capture's four
archived aliases before strict original readers,and verify/retire them afterward
without counting borrowed files as new cleanup.

Verified retention archives 640 owned aliases/intermediates in 255 blobs,
releasing 254.469 MiB after archive and new gzip recipes; all 13102 protected
hashes remain equal. Current GNU87/cache, UBSan game/Orange/cold cores, all38
GNU pictures, complete original compressed font/video/memory and the old failed
producer remain recoverable or live. `recover.py` verifies SHA/mode/nsmtime.
`replay_restored.py` restores one owned archived actual writer, borrows four
v1451 original aliases and reruns it plus both repaired8000-update programs.
Every selected state/entry/popup gate and all38 BMP identities reproduce;
the old writer still fails1377 pixels and both current profiles pass. All five
aliases verify and retire afterward. The four borrowed aliases receive no new
cleanup credit; previous journals and failed attempts remain unchanged.

Next extend the original/native comparison beyond 8000 toward Boss defeat and
process/campaign completion. These 38 samples establish programmed-display
agreement,not every frame or physical scanout. Other globals,full routes,NP2,
Windows,canonicality and historical exactness remain open. Both full goals
remain active.

## Historical v1451 producer: title phase repaired, seven pictures failed

Native `a8a67af` restores the original pre-scroll title phase. The v1450
constructed BB-call Oracle and its pending-background preview are withdrawn.
Original MAIN relative `0AAF:0148` calls overlay1 before scroll_driver at018A;
after-actor DGROUP at01B3 already contains the later scroll. Actual BB entry
`0AAF:15AA` records top94/scroll326 at update74; the later DGROUP scroll325
made the old Oracle invent top93. That Oracle falsely accepted the wrong
producer and rejected the correct one on43 intervals. Old reports stay unchanged.

Three complete original8001-update captures use **DOSBox-X**, not NP2; the
old emulator label is corrected. New code-fetch observers record2665 real BB
calls over7999 armed intervals2..8000 and38 live font/video/DGROUP checkpoints
at actual score return `0AAF:0207`. Both new cold GNU/UBSan programs agree on
all actual arguments,8000 title fields/three complete text rows and popup
rows/state, plus selected gameplay/input/RNG,nine pools,four Boss blocks,
Continue and CFG/SCR. All38 complete playfields (141312 pixels each),stage
bands and BGM bands match. Repeated paints preserve state/RNG and whole pixels.

**Whole-picture aggregate remains FAILED** on7 samples6740,6741,6753,6765,
6772,6773,6774:1377 total differing pixels in the right score area. Their complete
visible TRAM banks are equal; first target graphics index1 differs from native9
or15. At6740 the first pixel is557,64. Trace actual render_main writers next;
do not assume an owner or hide it with a HUD/clip mask. Actual post-score evidence
eliminates the earlier score-tail observation mismatch but does not waive this gap.

Source565/ea71e83c,87 GNU programs/83 CTests,optimized UBSan game and
all15988 native Demo state boundaries pass their scoped gates. Title-contract
executables are byte-identical to prior7895x2 proofs; that reuse is explicit,
not a new run. Evidence lives under
`.analysis/reconstruction/probes/native-title-pixels-v1451/`. Public readers are
`compare_th04_dos_title_entries.py` and `compare_th04_dos_title_pictures.py`.
The old `compare_th04_dos_titles.py` is a historical refuted-BB diagnostic.

Verified retention retires559 newly owned aliases/intermediates in
287 blobs, releasing257.988MiB after archive and new gzip recipes;
10590 protected hashes stay equal. `recover.py` verifies/restores SHA/mode/nsmtime.
`replay_restored.py` restores5 owned aliases,reruns the actual wrong-phase and
both current8000-update programs,and reproduces all38 BMPs per program.
The seven whole-picture failures also reproduce. Those5 aliases verify and
retire again;no borrowed/missing old file is counted. Current GNU87/cache,
UBSan game/title/cold cores,complete original compressed data/font/entries and
GNU38 scene pictures remain live. Restore aliases before strict capture readers
or archived UBSan/baseline picture paths;new title/popup row readers use `.gz`.

Next resolve the7 actual full-picture samples,then extend beyond8000 toward
Boss defeat/process/campaign completion. Complete pictures outside these samples,
other globals,physical scanout/timing,NP2 cross-emulator,Windows,canonicality and
historical exactness remain open. Both full development goals stay active.

The actual original order is overlay1 at MAIN_01_TEXT0AAF:0148,scroll driver
at018A,frame write at01B3,score call at0204 and actual return at0207. A hash-pinned
callee replay is only as valid as its caller state/time. Reversing the later
title clock and dissolve sprite did not reverse the later scroll driver. The
v1450 "43-frame fix" was a false inference; v1451 restores the earlier authored
argument phase and checks actual runtime registers/stack instead.

The actual BB observer watches code reads at0AAF:15AA. It attests CS:IP,DS,
left/top/cel registers,caller return63F0,opcode,stage counter,scroll and unchanged
CPU state. A full stream records2665 calls over intervals2..8000,including zero
counts. The first actor boundary arms the stream; no unobserved interval is
claimed. Independent font/entry/score-return observers preserve the same complete
8001-update selected state,resident and keyboard/RNG event sequence across three
original captures. All are DOSBox-X6e1a6e70,not NP2.

The first view-only diagnostic links unchanged v1450 cold main/audio/core
inputs and adds38 actual scene repaints. It retains the wrong preview and fails
43 real BB intervals and11 title-picture samples. Final a8a67af source cold-builds
all87 GNU consumers/83CTest and optimized UBSan game/title consumers. Both pass
actual entry,full title rows and all38 complete playfield RGB comparisons.
Complete pictures compare640x400 with no ignored pixel region. Their aggregate
still fails on the7 score-area samples; band/playfield verdicts stay separate.

Original after-actor and native after-full-update images initially also differ
on score text. The new observer reads original video/font/DGROUP at actual
score-return instruction0207. Source/CPU evidence selects this phase before the
comparison; there is no fitted frame delay. The remaining7 samples have identical
complete visible character/attribute banks and different underlying graphics.
`remaining-picture-gap.json` records exact points,indices and colors for tracing.
Do not "fix" it with a blanket HUD or playfield clip.

GDC row_height at host offset172 is uint8_t; offset173 is live row_line. The
first stronger guard read a WORD and rejected frame6549's16-line mode as528.
Pinned pc98_gdc.h and live snapshots distinguish them. The corrected programmed
projection uses the BYTE field and explicitly excludes live scan timing. A
row_line mutation preserves the projection; row_height17 rejects. The original
font/palette/VRAM data are unchanged. This expands a correctly typed gate; it
does not mask a hardware state or establish physical scanout.

Every selected repaint executes twice and compares all nine pool bytes,RNG,
clock and full RGB/indices. The target projection uses actual same-boundary
528384-byte font RAM,complete raw VRAM/palettes/GDC and immutable CPU context.
English/Japanese title fonts therefore no longer rely on an assumed font bank.
A changed pixel outside both title bands still fails the whole-picture Oracle.
Field/BB/text mutations,truncation/trailing records and row-height controls also
reject. GNU/UBSan's complete title-contract executable SHAs match the retained
7895-case/two-load receipts,so these unchanged components are reused rather than
rerun. No whole-game or historical exact promotion follows.

Replay actual entry arguments and actual post-score pictures with fresh outputs:

```sh
python3 scripts/probes/compare_th04_dos_title_entries.py \
  --original RESTORED_SCORE_CAPTURE --native NEW_FRONTEND \
  --target PINNED_MAIN --output NEW_ENTRY_REPORT
python3 scripts/probes/compare_th04_dos_title_pictures.py \
  --original RESTORED_SCORE_CAPTURE --native NEW_FRONTEND \
  --target PINNED_MAIN --native-root NATIVE_CHECKOUT \
  --phase after-score --output NEW_PICTURE_REPORT
```

The second command must currently exit1 for the whole-picture gap,while its
title/playfield verdicts pass. Retain that failure. A debugger argument snapshot
and a disassembler view are not interchangeable Oracle evidence.

## Historical title gates (v1450; BB phase inference withdrawn)

This section preserves the historical v1450 interpretation. Its actual-BB
phase and first-"negative" claims are refuted by v1451 above; old JSON remains
unchanged. Clock/TRAM/primitive observations keep their narrower scope.

Native `3bf2aea` restores stage numbers/names, BGM strings, separate title/Boss
clocks and the shared graphics dissolve. Original MAIN relative `0AAF:6446`
and `0AAF:66A5` are the owners; DGROUP `1BBC/1BDC` owns their string tables.
The original ordinary capture's BGM row differs from v1449 on334 frames,
first99. That old report remains FAILED. Both new cold GNU/optimized UBSan
programs match all8000 title fields, three complete80-column character/attribute
rows and actual BB calls. Popup rows/state and the selected gameplay/input/RNG,
nine pools, four Boss blocks, Continue and CFG/SCR remain equal.

Each profile passes7895 original-instruction cases at loads1000/3333, comparing
complete16KiB TRAM, all title state, BB calls and four complete32KiB GRCG planes.
GNU builds87 programs and passes83 CTests. All15988 old/current native Demo
state boundaries, six late popup BMPs and dialogue-prefix BMP remain equal. The first
title producer passed text but misplaced43 frames of BB draws by1px. Its actual
source/program SHA is recovered and its failure reruns. The corrected owner
reads the result of the pending background update without advancing live state.

Source565/02e852a2 and receipts live under
`.analysis/reconstruction/probes/native-bgm-title-v1450/`. Native replay is
`port64/verify_titles.py`; use pinned Unicorn2.1.4. Its older1.0.2 engine rejects
this strlen/RETF path. Hardware callbacks explicitly stop and rethrow errors.
The GRCG adapter and pinned3072-byte file-backed BB extent are explicit.

Verified archival retires1332 owned aliases/intermediates in
1079 blobs, releasing115.574MiB after archive and new gzip recipes;
7293 protected hashes remain. `recover.py` restores by SHA/mode/nsmtime.
`replay_restored.py` reruns old BGM334, first-scroll43 and both final actual
8000-update programs, then verifies/retires one owned and four borrowed original
aliases separately. Old journals/totals and the94 missing files are unchanged.

Next compare natural title/picture bands with same-boundary font/video evidence,
then extend beyond8000 toward Boss defeat and process/campaign completion.
Complete natural pictures, other globals, physical timing/scanout, Windows,
canonicality and historical exactness remain open. Both full goals stay active.

The two callback clocks are BYTEs at DGROUP46A0/1B63. They share dissolve
sprite1BB6; lengths are separate WORDs4680/4682/4686, rather than one contiguous
three-WORD array (4684 is the stage-title ID). BGM ID469A and callback469C are
retained. Stage0/Reimu selects name IDs0/0; the other stage/character mappings,
all17 BGM IDs and the alternate Gengetsu ID are covered by original instructions.
Text first appears at title frame25, repeats while cel22 lasts, and wipes at192.
In the observed ordinary run, BGM occupies99..265 and6574..6740. The title callback
expires at299 with sprite0; the Boss callback expires at6774 retaining sprite16.
Expiry and BYTE-wrap controls distinguish these resets.

TXT.BB is2048 bytes. TXT2.BB is also2048, but original loader0AAF:6A61 reads
only its first1024. The3072 loaded bytes have SHA256
`00d1f591a385dbe5f8ac92d2c73cabc863e93d4a012d8291a901bc1316af804e`.
The Python FAT/PAR path attests the parent archive before deriving this extent.
No target executable instructions or original assets enter maintained source.
Display strings are semantic Shift-JIS data checked through original tables,
strlen and text instructions. Native Graphics uses actual private file assets.

`verify_dos_hud_titles.py` executes original title, strlen, text/gaiji, scroll and
BB instructions. It replaces no callee; a near-return sentinel ends the call.
Actual OUT7C/7E controls an explicit GRCG RMW adapter. Actual STOSD/MOVSD masks
write four independently seeded planes; unexpected CPU VRAM reads reject.
The standalone comparison reads all147456 native TRAM/graphics bytes per case,
including untouched regions. All595 original instruction addresses are retained
as target execution observations, not independent disassembler Oracles.

Old Unicorn1.0.2 produces an invalid16-bit CS:IP on this actual strlen/RETF path
at both loads and is rejected after44 visited addresses. Unicorn2.1.4 is isolated
under the private batch directory, with its shared-library hash in every final
component receipt. Its target results additionally agree with the independent
ordinary DOSBox-X recording. Pinned1.x ctypes callbacks swallow Python exceptions:
the new hardware/code guards stop emulation first and rethrow after emu_start.
Negative controls reject a synthetic mask, unexpected OUT, changed field,
changed BB coordinate, changed text byte, truncation and trailing records.

The first natural row/state comparison passed but43 BB coordinate frames failed,
first74: original physical top93, first native94. FrontEnd commits background
advancement after State returns; overlay1 needs the resulting origin. The repair
runs that same background update on a private value for the title's coordinate
query. Live background/actors are not advanced twice. The target-derived call
reader still rejects the first actual executable and accepts the corrected one.
This is a phase ownership fix, not a fitted1px offset.

The first diagnostic executable was overwritten by the next incremental link.
`preserve_negative.py` reconstructs its565-file receipt-pinned source closure,
rebuilds at the original path, and requires its original executable SHA before
admitting the recovered counterexample. It then restores/rebuilds the positive
source and requires that prior executable SHA too. No receipt is restamped.
The recovered archive and actual negative executable remain replayable.

Natural graphics evidence here compares actual ordered BB calls and their
primitive separately; it does not compare an entire native picture with original
scanout. Text rows compare complete characters/attributes, not font pixels.
Late popup/prefix BMP equality is native regression evidence; v1449's six
same-boundary original font projections keep their own narrower scope.

Replay with the matching native branch and a fresh output directory:

```sh
PYTHONPATH=PRIVATE_UNICORN_2_1_4 python3 port64/verify_titles.py \
  --dos-root DOS_ROOT --exe COLD_TITLES_CONTRACT \
  --bb ATTESTED_LOADED_BB --output-dir NEW_COMPONENT
PYTHONPATH=PRIVATE_UNICORN_2_1_4 python3 scripts/probes/compare_th04_dos_titles.py \
  --original RESTORED_ORIGINAL --native NEW_FRONTEND \
  --target PINNED_MAIN --bb ATTESTED_LOADED_BB --output NEW_REPORT
```

The original strict reader requires the four borrowed font-capture aliases;
restore them with v1449/recover.py and its font-original prefix. New title/popup
row readers consume verified `.bin.gz` aliases directly. The v1450 recovery
replay covers actual old BGM334, recovered first-scroll43 and both final games.
The unused Unicorn static library is archived; its dynamic tool stays live.

## Common MAIN popup rendering repaired (v1449)

Native `da4ee5f` adds the real popup clock, pending-ID replacement, bonus digits
and persistent TRAM writes for BONUS, FULL POWERUP, high score and Extend.
The original `0AAF:67E8` callback runs after overlay1 and before score drain.
Rendering a host repaint no longer recreates a blank playfield text plane.

Fresh GNU/optimized UBSan builds preserve the complete 8000-update selected
state/input/RNG, nine pools, four Boss blocks and CFG/SCR result. Both now match
the complete 80-column popup character/attribute row and all popup fields at
all 8000 boundaries. The old actual renderer differs on 256 frames: BONUS and
FULL POWERUP each last 128 updates. Each compiler profile also passes 7689
original-instruction component cases at load segments 1000/3333, with complete
16KiB TRAM and ABI checks. GNU builds 86 programs and passes 83 CTests; all 15988
old/current native Demo state boundaries remain equal.

The first `a9e09a7` producer passed its configured after-actor checks but cleared
retained BONUS during the following score return: actual original code keeps
25000, while its default-argument request stores0. The corrected overload leaves
the shared amount unchanged unless an explicit bonus producer supplies it.
Actual popup+score CPU/native composition now passes at both loads,including
that return boundary. Default arguments are compiled into callers,so complete
new cold builds recompile MAIN and every affected caller. Initial source/
programs/reports remain unchanged and their narrower positive observations stay
valid. Final source 561/f28cc274 includes this correction.

An additional original 8001-update capture reads actual 528384-byte font RAM,
raw video, DGROUP and unchanged CPU context at six declared frames. Those six
full-width popup bands (6144 pixels each) match both native programs exactly;
used live glyph bits also match the pinned BFT. This accepts instantaneous
programmed-display projections, not physical scanout or complete pictures.

The historical v1449 BGM334 aggregate failure remains unchanged; v1450 has a
separate new-producer acceptance above.
Broader pictures, other globals, process/campaign, Windows and historical exactness
remain open. Source 561/f28cc274 and replay receipts live under
`.analysis/reconstruction/probes/native-pickup-video-v1449/`. Public readers are
`scripts/runtime/verify_dos_hud_popup.py` and `scripts/probes/compare_th04_dos_popup.py`;
native component replay uses port64/verify_popup.py with --dos-root. Both full
development goals remain active.

The native popup owner is `port64/hud_popup.hpp/.cpp`. It keeps one requested
ID rather than an event queue: a different request replaces the current label
only at clock 64 or later. Expiry at 128 clears the popup line, resets its byte
clock and removes the callback. Same-ID requests do not restart that clock.
The original shift buffer, label length, current/destination columns, reached
flag and bonus dword are all retained and compared. Bonus numeric rendering
includes the fixed trailing continues digit. All four labels, bonus boundaries
including FFFFFFFFh, same-frame writes and request changes around 63/64 are
covered by actual original popup/points/CRT/gaiji/text execution. There are no
callee adapters; only a near-return sentinel terminates each component call.
The two load segments have distinct relocated data and code ownership.

MAIN applies item full-power requests after bullets update, bullet-zap bonus
requests in the bullet sink and score/Extend requests after the frame boundary.
Overlay1 writes first; popup writes follow it. Actual rendering consumes the
persistent text memory instead of blanking it during every repaint. Stage
initialization disables the popup callback without inventing a clock reset.
The original source/binary exact-state ledgers and Borland layout are unchanged.

The diagnostic old renderer is an unchanged v1448 cold core/main/audio with
only the text-observation harness recompiled into view.cpp. Its source closure
is the v1448 frozen producer plus baseline-diff.tar.gz; new popup files in that
archive are explicitly unlinked candidate material. Baseline/current complete
selected state and raw pool streams agree. The strict popup row differs first
at 3995 and again at 7641; the old code's first full-power band differs by 78 pixels,
then 594 for the fully drawn label. Current GNU/UBSan differ by zero in all six
sample bands. The raw popup-row comparison covers all 80 columns,160 character
bytes and 160 attribute bytes, with no ignored-byte mask. Popup state is emitted
at the actual actor observer before score-tail requests; row observations have
no score-tail writer. The separate BGM-row failure remains in every report.

Two original captures are admitted: original-v2 carries the complete 8001 video/
DGROUP prefix, and font-original additionally binds six live font snapshots.
Their starting image/files and all observed pre-I state/resident/RNG/input events
agree. Retained real native output is independently re-compared against the
font capture without rerunning or changing either original receipt. All nine
complete pools at each font checkpoint agree. The calibrated font array is at
VGA offset 312, size 528384, within the attested 535896-byte object. Pinned g++8
headers and four relevant font/drawing source files agree with the exact source
archive. The captured font state, not an assumed asset bank, supplies pixel bits.
GDC text origin/pitch/height/enable, white text palette, raw TRAM, graphics,
GRB/DAC expansion and double-wide sequencing are checked. Six 6144-pixel samples
are distinct temporal observations, not a whole-animation or full-screen result.

The first copied capture driver completed raw observations but failed finalization
because adjacent video-helper aliases were missing. It has no admission receipt.
The fresh original-v2 producer includes those unchanged helpers; the first run,
its terminal error and full raw compressed data remain separate. An early pixel
projection also rejected the GDC origin because it confused partition-length
bits with address bits. Its failed source/log are retained; the corrected
projection validates the low address bits. No failed report is restamped.

Replay after restoring this batch's owned capture aliases:

```sh
python3 .analysis/native/port64-recovery-v1445/port64/verify_popup.py \
  --dos-root "$PWD" \
  --exe .analysis/native/port64-recovery-v1445/.analysis/port64/popup-v1449-final/gnu/th04-port64-popup-contracts \
  --output-dir NEW_COMPONENT
python3 scripts/probes/compare_th04_dos_popup.py \
  --original .analysis/runtime/candidates/native-pickup-video-v1449-font-original \
  --native .analysis/reconstruction/probes/native-pickup-video-v1449/final-gnu-observation/frontend \
  --target .analysis/targets/th04/main.exe --output NEW_ROW_REPORT.json
```

The second command intentionally returns1 while BGM remains different; inspect
popup_passed and the separate row/state verdicts. Never turn that aggregate into
a pass by discarding row 23. Complete commands and the final frozen 561-file source are in final-cold-source.json,
final component/run receipts and final-result.json. Initial e918678d reports
cover the earlier after-actor surface; score-tail-negative.json adds its later
counterexample without rebinding those reports.

Verified archival retires 255 owned capture/prototype/intermediate/raw aliases
into 245 blobs:34.573MiB archive and339.895MiB released after its archive. All 255 recoveries
pass SHA/CRC/mode/nsmtime;2550 protected digests remain equal. Restoring five
owned aliases and rerunning three actual 8000-update programs reproduces the old
popup failure and both current passes,including selected state/pools/Boss/input/
GO/prefix/saves and six complete BMPs; BGM334 remains. Those five aliases are
verified and retired again. Current GNU cache/programs,UBSan game+popup,both new
cold cores and complete compressed original memory/video/font/source stay live.
Use recover.py before strict capture readers or replay_restored.py for the
complete restore/run/retirement cycle. Text-row readers also accept the verified
.gz streams directly. Old94 missing files and prior journals remain untouched.

A separate final journal retires 240 newly owned intermediates/aliases in 238
blobs:3.418MiB archive,23.809MiB after its archive and2524 protected hashes. Both journals total363.703MiB after archives; five new row-gzip recipes use
0.488MiB,leaving363.215MiB released after both. The initial255/245 journal remains unchanged. Four
borrowed font-capture aliases verify and retire without being counted twice.
replay_final.py restores those four plus two owned score diagnostic programs,
reruns the old 0 / corrected 25000 results and both final 8000-update games,then
verifies metadata and retires them separately. Use recover_final.py for final
intermediates and recover.py for the initial capture aliases.

Final root CI573 with live MAIN database/mutation checks and native CI354 pass;
git diff --check passes in both trees. Native private Ghidra skips because its
project is absent; the actual database replay is in DOS root.

## Native Continue and full-power pickup repaired (v1448)

Native source `7bdcd60` now applies item collection's clear effect to the real
bullet owner. An actual ordinary Game Over/Continue reaches a full-power pickup
at update 7640. The old executable leaves bullets active; original MAIN instead
sets DGROUP2134:BCBA to20, then19 next update. Its first visible state/pool
failure is boundary 7642. The failed executable, source and reports remain.

A fresh original 8001 capture and complete cold GNU/optimized UBSan builds pass
8000 updates: 21 selected state/RNG fields, actual player input, nine complete
pools, four Boss blocks and complete CFG/SCR bytes. GNU 85 programs / 82 CTests pass.
Five original code-fetch/caller/memory checkpoints at frame7547 establish that
player0AAF:5FCF consumes20h before Game Over0AAF:3A51; the later menu2000h resumes
that same call through5FCA/00F4. Keep this distinct from STD dialogue before
player_update. The real ranked Continue changes only decoded score section 1;
all ten full 16-bit checksums and the complete encoded file agree.

Producer 557/8284f2cd freezes every maintained source before both cold builds.
Final consumer 557/3e985ee3 changes only the Python save-scope text/reporting;
all compiled inputs are unchanged. Five real negative reader controls pass.
Replay/source: `.analysis/reconstruction/probes/native-continue-v1448/`,
`result.json`, `cold_build.py`, `finalize_consumer.py`, `continue-witness.json`.
Public original reader: `scripts/probes/attest_th04_continue_checkpoints.py`.
Native save/UI controls are component stimuli; blocking timing, complete
pictures/TRAM/scanout, other globals, full process/campaign, Windows and exact
promotion remain open. Continue these comparisons; both development goals stay active.

The original run uses configured Normal/ReimuA, seed 64, lives 6, bombs 0, Turbo on;
it injects keyboard release/Enter only at the declared blocking owners. It does
not inject actor/life/score state. Original load10FC gives DGROUP3230. The five
Continue checkpoints include complete 640KiB conventional memory, 64KiB DGROUP,
raw video,CPU/segments and target opcodes. Credit-applied0AAF:3CDE follows the
actual score[0] increment. The miss-helper return validates BP+2=610A;
player-return00F4 validates the preceding direct call. Generic entry-stack
validation would use the wrong stack surface at those interior returns.

The full-power target branch is MAIN_035_TEXT13A9:A2DF..A2EB, target file
1F56F..1F57A: compare clear_time with20 and write20 only when smaller. Runtime
DGROUP after actors7640/7641/7642 shows power1/128/128 and clear0/20/19.
The nine pools first diverge at7642 in bullet movement/positions/patterns; the
score pending accumulator becomes7857 in original after those actors. Native
item::collect already produced bullets_cleared, but State::update discarded it.
The correction dispatches that existing effect at item collection, after
bullets_update, and preserves the larger active clear timer. The live MAIN
regression checks20 on collection and19 after exactly one following update.
No target source, accepted Borland layout or historical byte state changes.

The extended ordinary FrontEnd drives the real Game Over owner for 189 advances
while the simulation remains at 7547, then completes 7548 once. It records the
actual prefix argument before the block and retains that observation through
UI polling. It does not override gameplay input or repeat the player prefix.
Release/Enter polling remains an explicitly declared component policy;189 is
not an original wait-duration claim. The public consumer requires witness
coverage for every observed Game Over frame and checks actual frame freeze,
entry/return,Continue digit,player sample and final physical files.

Both final producers yield identical selected scalar/full-pool/Boss,input/UI
trace,prefix and physical-file outputs. GENSOU.SCR changes identically in both
executions: decoded section 1 inserts CONTINUE at zero-based place 2 using the
pre-reset score. CFG remains unchanged. This observes the actual ranked Turbo
save branch, not just restored life/Bomb counts. Encoded keys and all ten 192-byte
decoded payloads agree, including full 16-bit checksums. Full pictures at the
pickup/menu and scene timing still need separate comparison; the earlier single
pre-script graphics sample does not cover them.

The frozen cold-producer Python verifier had an incorrect unranked-scope
sentence. The separately frozen final consumer corrects that sentence and
reports changed decoded sections. The source diff is exactly that one Python
file; no compiled source/header changed. The earlier diagnostic receipts remain
unchanged, including their narrower/inaccurate scope text. The initial native
failure is retained as a counterexample rather than converted into acceptance.

Replay with restored capture aliases:

```sh
python3 scripts/probes/attest_th04_continue_checkpoints.py \
  --capture .analysis/runtime/candidates/native-continue-v1448-original \
  --main .analysis/targets/th04/main.exe --output NEW_WITNESS.json
python3 .analysis/native/port64-recovery-v1445/port64/verify_ordinary_state.py \
  --dos-root "$PWD" --frontend --updates 8000 \
  --original .analysis/runtime/candidates/native-continue-v1448-original \
  --exe .analysis/native/port64-recovery-v1445/.analysis/port64/continue-v1448/gnu/th04-port64 \
  --output-dir NEW_OBSERVATION
```

The complete commands and selected executable hashes are frozen in final receipts.
The private capture.py/keyboard/continue_watch.py closure is bound by its
original receipt. Existing v1447 public capture helpers remain unchanged so
that its protected original evidence can still replay.

Verified retention archives 243 owned aliases/intermediates into 243 content blobs:
21.612 MiB archive,54.297 MiB net released,2338 protected hashes checked. Restore/
CRC/SHA/mode/nsmtime checks pass. Restoring five original/prototype aliases and
rerunning three real 8000-update programs reproduces the old 7642 failure and both
current successes, including full selected output/save/GO traces. The five aliases
are checked and retired again. Current GNU programs/cache,UBSan game,both new
cold cores and complete compressed captures remain. Use recover.py to restore
capture aliases, or replay_restored.py for restore/run/retirement. The old 94
missing files are unrelated and no historical receipt is rebound.

## Original dialogue/player input boundary corrected (v1447)

The v1446 input interpretation and the `13e6676` latch are withdrawn. Actual
original MAIN code-fetch/caller checkpoints at load `10FC` show STD `0AAF:2454`,
dialog `0AAF:2BFB/2A7C`, then player `0AAF:5FCF`, all at frame 6548. Dialogue occurs
before player_update. The loop sample contains `20h` (Shot), but player entry
contains `2000h` (Enter). The old comparator confused these boundaries. Its state/
pool/Boss results remain; player-input acceptance is withdrawn. Old receipts
are unchanged and affected evidence/knowledge is explicitly reclassified.

Native `a7f9bea` removes that latch and keeps live dialogue keys. Public capture
--dialog-checkpoints and attest_th04_dialog_checkpoints.py bind target code,
CPU/stack, conventional/DGROUP memory, raw video and observer sources. Native
--frontend requires this witness for blocked frames. A fresh public original
capture of 7,501 updates supports GNU/UBSan 7,500-update comparisons: 21 state/RNG
fields, actual player input, nine full pools and four Boss blocks agree.
The real old executable fails only player input at 6548 (`20h` versus `2000h`).

One pre-script sample also matches player/RNG fields, all nine pools and all
141,312 pixels of the instantaneous programmed-GDC playfield graphics projection.
Box subregions overlap that playfield; they are not extra samples. Independent
emulator rendering source matches its pinned archive and corroborates GRB/DAC
conversion. TRAM, full pictures/scanout and physical timing remain open.
Eight real inner controls check PC/frame/code/caller/memory/input ownership.

Source closure557/f6c6e393 has fresh main/view/audio builds against unchanged attested
cold GNU/UBSan cores. Fresh dependencies cover 130 own files; 231 reused core
dependencies/library hashes and 82 unchanged core contracts pass. This is a
leaf rebuild, not a fresh complete cold-core build. Final root CI 573 with live
MAIN database/mutation checks and native CI 354 pass. Native private Ghidra
skips because its project is absent; the real database replay is in DOS root.

Verified archival retires 26 owned aliases in 17 blobs: 346.137 MiB net after a
39.959 MiB archive. SHA/CRC/mode/nsmtime and 258 protected hashes pass. Four
restored 7,500-update FrontEnds reproduce two old input failures and two current
passes, with complete selected state/pool/Boss/file/prefix outputs. Five aliases
are verified and retired again. Current GNU cache/programs, selected UBSan game/
cold cores and full compressed capture/RAM/video/source evidence remain. Failed
layout and 6549-stop captures stay distinct. Old missing 94 files are unrelated.

Replay/source/recovery: `.analysis/reconstruction/probes/native-dialog-prefix-v1447/`.
Original: `native-dialog-prefix-v1447-public-original`; use recover.py before
readers, or replay_restored.py for restore/replay/retirement. Native tree:
`.analysis/native/port64-recovery-v1445/`. The closed retirement log is pinned
only in a separate final closure; no old journal or receipt is rebound.
Continue Game Over/Continue input/resident/score ownership and complete pictures.
Broader process/campaign, Windows and historical exactness remain open.

## Historical v1446 result and superseded input interpretation

V1447 supersedes the player-input interpretation and latch described below.
The original dialogue is in the earlier STD callback, before player_update;
pre-loop20h is not the actual player-entry2000h. Retained comparisons establish
selected state/pool/Boss agreement only. The following records the disproved
v1446 inference and its historical producers; use the corrected witness above.

Source `13e6676` preserves Stage1's gameplay input across blocking dialogue
refreshes. Target MAIN `0AAF:00F1` calls player_update at `0AAF:5FCF` before the
Boss callback through `DGROUP 2134:432C` at `0AAF:0113`; load `10FC` is recorded.
The executed predecessor consumed 0 at update 6548 instead of original `20h`.
Its 21 selected fields and nine pools still matched: the held-shot interval
made this input error invisible to that earlier comparison. The fixed real
FrontEnd retains the selected gameplay key/Shift while dialogue owns its
separate release/Enter samples. It does not edit game state or original captures.

Fresh source closure of 557 files (d246f71f) builds 85 GNU programs, passes 82 CTests and
also builds an optimized UBSan core/game. The ordinary Normal/ReimuA seed64/lives6/bombs0 comparison
now covers 7,500 completed updates and 7,501 boundaries through real dialogue and
Boss phases 0/1/2: actual gameplay inputs, 21 fields/full RNG state and counts,
nine complete pools, and four complete Boss blocks (45 bytes, including spare
state bytes) agree with original DOS. Dialogue has 803 frozen admissions and
804 advances under declared component keys; these are not original timing.
Five natural losses end with one life. Native initialization uses an explicit
OP counter of 64 and menu API; natural startup/input delivery is not accepted.

Public replay: native port64/verify_ordinary_state.py --frontend --updates 7500
with --dos-root, --original, --exe and a fresh --output-dir. Canonical proof/source/recovery:
`.analysis/reconstruction/probes/native-ordinary-front-v1446/`. The writable
native tree remains `.analysis/native/port64-recovery-v1445/`.
Intermediate dialogue/player-prefix pictures, remaining globals/Game Over/
Continue, Boss defeat, whole routes, scanout/timing, Windows and historical
exactness remain open. Next extend the actual FrontEnd through Game Over and
Continue using original captured inputs and separate blocking-owner evidence.

Eight actual reader controls pass, including independent sampled-input/Boss
mutations and strict default/configured extents. Compiler dependencies cover 350
actual own files; fresh GNU core and ymfm archives equal v1445 byte for byte.
Verified archival retires 249 owned files in 244 blobs, releasing544.664 MiB net
after a 9.607 MiB archive. SHA/CRC/mode/nsmtime and 2,296 protected hashes pass.
Restored predecessor/fixed prototype and current GNU/UBSan FrontEnds reproduce
the complete 7,500-update outputs; only the predecessor repeats its actual-input
failure. Two restored executable aliases retire again; six borrowed original
aliases return to their older archive state without counting as new cleanup.
Current GNU cache/85 programs, selected UBSan game/libraries, all sources and
complete original/current compressed captures remain. Use recover.py and
replay_restored.py in this batch's namespace. The active retirement log is
explicitly excluded until the final closure; no journal/log receipt is restamped.
Missing old 94 files remain a separate historical gap.

Cold C++ producer13e6676 remains557/d246f71f. Current Python consumer48db31c
is557/7c4b8576: only verify_demo_pools.py restores the default Demo truncation
diagnostic after the first native CI found its message regression. All350
compiled own inputs and cold executables are unchanged. Fresh separate GNU/
UBSan consumer replays and eight current-reader controls reproduce all admitted
results. The first failed CI and every old producer/runtime receipt remain
unchanged; current-consumer.json and consumer-replay.json bind both identities.

Final gates pass: root CI573 with live MAIN database and Ghidra mutation
checks, native CI354, and both tracking/diff checks. Native private Ghidra is
skipped because this checkout has no project; the actual database replay is
in the DOS root. Keep the initial native message-regression CI as a negative.

## Ordinary natural Continue and physical old-score publication (v1352)

The optional eighth route-plan field is `pilot` (0 avoiding, 1 stationary
shot). The old six/seven-field plans retain default 0. Pilot 1 changes keys
only; actual original-data bullets/contact drive hit/death/Game Over. Existing
configuration remains physical input: Lunatic/lives option 1/Bombs 0/Turbo,
BGM2/SE1. The first Game Over receives Shot pulses, the second Esc. Each
unranked/ranked scenario reaches registration/fresh OP in 1,551 advances.
MAIN frame 432 stays frozen for 189 refreshes then resumes its suffix to 433;
frame 630 stays frozen for 222 refreshes before quit. No actor/life injection,
synthetic stage or Continue callback substitutes for this ordinary route.

The default physical table has a lowest 1,000-unit score; natural first score
520 does not rank and correctly adds no `CONTINUE` row. The ranked initial
fixture changes only the selected rank3 table's ten score rows to zero,
recomputes its checksum/encryption and preserves the other nine records.
Filesystem observers on GNU/UBSan read complete rename-published files: old
520 units and credit byte 0 under `CONTINUE`, then separate final registration.
Every nonselected decoded payload survives. This is declared physical test
input, not score/state injection or a pristine original-data claim.

All three hosts agree on 3,102 advances/1,252 startup refreshes/16 full captures
and final physical files. Actual Windows also passes all 64 current contracts.
Recorded input/power/life/Bomb/score subsets drive original MAIN relative
0AAF:3971..3CEE at loads1000/2000; four configured scenes reproduce 58,424
requests/refreshes on original/GNU/UBSan. Unrecorded overflow/dream/delta/auxiliary
score fields are explicit zero adapters; save/HUD/vsync/video/process remain
component adapters. Separate native whole-file observations support persistence.

The public source equals the independent cold compiled materialization in all
467 inputs (`f0d72042...`); 195 programs build and 64 contracts pass per host.
GNU/MinGW each have 103 core objects raw-equal to v1351. Seven default pilot
Hard B/16-advance captures and physical saves still agree on all hosts; four
GNU/UBSan invalid-pilot/trailing controls reject before writes. Prior complete
four routes and GNU Hard B retain their `e3448a63...` producer. No fresh full
Lunatic clear/physical clock/performance/audio-device/current GUI claim follows.

An avoiding Lunatic attempt instead reaches Stage6 bad Ending/fresh OP in
83,534 advances without a Continue menu; it is rejected as Continue coverage.
Its redundant UBSan attempt is deliberately cancelled, with partial outputs
and terminal readback retained. A wrong-worktree control edit leaves a consumer
referencing an unclosed full profile; rejection occurs before game entry. Fresh
v2 waits all three terminal builds and full-profile closure. An overbroad
ranked-write assessment also rejects the correctly unranked 520 case; narrower
unranked acceptance and ranked physical fixtures use new receipts. Never
relabel or restamp these negative/cancelled observations.

Replay: private `natural-continue-v1352/{run-stationary-v2.py,run-ranked-v1.py,
assess-v3.py,original-keys-v1.py,windows-v1.py,aggregate-v1.py}` and their frozen
source/product profiles. Use fresh outputs/source snapshots for every replay.

Scoped terminal cleanup reclaims 591,622,144 allocated bytes net (564.2 MiB).
Two complete recovery archives precede retirement of the closed 244-file
Windows stage and 1,145 generated build files. Independent readback checks
3,165 protected hashes and all 315 members; current/preceding programs,
source snapshots, native captures/physical saves and failed/cancelled attempts
remain. Restore archived Windows data into a new replay scope; never overwrite
an accepted receipt or retired stage's provenance.

Both final CIs pass, including root live Ghidra replay and Oracle mutation
checks. `final-readback-v1.json` freshly checks the preserved current source,
product/corpus/negative evidence hashes and both recovery archives. Post-CI
source-backed cleanup separately checks 1,012 public sources and retires their
Python caches, reclaiming 16,347,136 allocated bytes net after journal overhead.
Root receipt: `.analysis/cleanup/natural-continue-post-ci-caches-v1352.json`.

## Maintained ordinary route entry and real shot choice (v1351)

`--natural-route-checks DIR` runs the maintained executable directly, with no
rewritten frontend or private entry hook. It requires headless `--hdi`,
`--font-bmp`, explicit `--save-dir` and `--mute`; it conflicts with `--title`
and `--startup-checks`. Place `route-plan.txt` in the independent save directory:
`rank character limit repaint continues extra [shot]`. Rank is 0..3,
character/shot 0..1, Extra/repaint 0..1. A fresh setup fixture physically saves
the requested rank with legal six lives/two bombs/Turbo; existing configuration
is preserved. Extra reads physically earned score availability. All chosen
movement/shot/Bomb keys, held startup refreshes and menu actions are recorded.
`--render` in the public verifier paints startup as well as each route refresh.

The first public source (`6fdd2b98...`) completes all four preceding ordinary
shot A routes on GNU8, optimized UBSan and actual Windows. The complete recorded
streams and physical files agree across hosts and with the v1350 baseline;
three added captures record startup inputs, menu actions and the static menu.
Each host's own Normal save admits Extra in a new process. `aggregate-v1.json`
binds this closed 195-program/64-contract-per-host scope; no whole original
route, physical input/clock/performance or all-rank/shot acceptance follows.

A real Hard/Reimu B attempt exposes a route-control bug: right changes the
character screen, while the shot screen accepts up/down. Actual MAIN enters A;
the declared B validator rejects acceptance after 89,414 advances. Its files,
physical saves and failure remain. The correction uses down and checks actual
character/shot at entry. Isolated maintained-source GNU Hard B then completes
89,114 advances, Ending, registration and fresh OP. It visits no Game Over,
so the allowed Continue branch remains unexercised. The corrected source is
published only after all old guarded readers close. Final 467-input source
is `e3448a63...`; the new cold product vector is a separate generation.

`verify_natural_routes.py` binds the ordinary public executable/source profiles
and supports legacy or current capture references. The corrected GNU full
route initially imports byte-attested unchanged core libraries; its private
receipt's inherited `product_profile_sha256` label identifies the source
profile, so use `shot-entry-linux-v2/receipt.json` and
`fixed-public-source-bridge-v2.json` for explicit source/archive/compiler linkage.
Cold final products now complete 195 programs and 64 contracts per host. The
current GNU whole program is raw-equal to the successful full Hard B program;
all three hosts agree on actual B entry, 16 ordinary advances, seven captures
and physical files. `current-shot-bridge-v2.json` binds these current products.
Final full four-route producers `linux-v3`, `ubsan-v3` and actual Windows v3
all close with exit 0. `aggregate-v3.json` accepts the final-source corpus:
270,193 route advances, 2,504 startup advances, 49 full capture files per host,
all recorded inputs/telemetry/captures/physical files equal across hosts and
the preceding public generation. Each host physically earns Normal saves and
uses them to enter Extra in a new process. Real Continue remains unexercised.

Eight GNU/UBSan entry negatives reject missing save destination, window/startup
conflicts and invalid shot before output/save writes. An initial UBSan launch
predates completion of the full product-profile writer; missing-file failure
occurs before game entry/output creation. Writer closure precedes fresh v2
execution. Both failures remain distinct from accepted receipts.
The first Windows short-check path conversion also rejects before Windows
entry; it attempted to convert a Linux HDI path before staging the copy. Its
failure stays separate; fresh v2 uses the owned Windows path and passes.

Recovery below `.analysis/port64/public-routes-v1351/` preserves two fully
read-back archives for terminal static libraries and the closed Windows64
contract stage. It retires 199 stage files/1,145 generated files, retaining
2,942 protected hashes; net 571,826,176 allocated bytes reclaimed. Independent
`retention-readback-v1.json` rechecks every archive member and protected file.
A second pass retires 215 closed contract/short-shot stage files and 1,145
generated files with two separate full-member recovery archives. Independent
`retention-readback-v2.json` verifies 2,941 protected hashes and all 286 members;
net reclamation is 586,735,616 allocated bytes. Both passes total
1,158,561,792 bytes (1,104.8 MiB). Route programs, captures and saves remain.

Both CIs pass, including root live Ghidra replay and Oracle mutation checks.
`final-control-readback-v1.json` freshly reattests both 195-program vectors,
all final sources/archive members, contracts, full-route/Hard B links and
recovery archive hashes. Post-CI cleanup removes 1,012 public source-backed
Python caches, checks all 1,012 sources and reclaims 16,347,136 allocated bytes
net under root `.analysis/cleanup/public-entry-post-ci-caches-v1351.json`.
Old producer snapshots stay immutable; all replay outputs must be fresh.

## Each-refresh routes and terminal host repaint (v1350)

The four v1349 ordinary key-only prototypes now paint every route refresh on
GNU8, optimized UBSan and actual Windows. All 270,193 recorded route advances,
37 complete capture files and physical final saves per host agree with the
deferred baseline, except the declared `result.txt` render flag. Each host's
own Normal-earned files admit Extra in a new process. Startup wait rendering
is outside this route loop; neither all ranks/shots/Continue nor physical
input/clock/performance follows from this comparison.

Separately, the actual GUI loops used only post-refresh `animated()` to admit
repainting. Completing startup makes that value false. Logical full/skip
controls on three hosts distinguish 24,214 stale pixels from the correct
static menu. Actual Linux SDL event/texture/present callbacks with dummy video,
and actual Win32 timer/WM_PAINT callbacks in nonactivating offscreen windows,
reproduce the same old/fixed results: zero versus one final update, 24,214
versus zero mismatching pixels. The two source variants have identical frame
observation, video and auto-close adapters; only the public paint gate differs.
This accepts terminal callback admission, not physical display or performance.

`view.cpp` now retains the pre-refresh animation state alongside the new state.
All 195 products build in the independent `port64-presentation-v1350` workspace;
64 contracts pass on GNU8/UBSan/actual Windows. The source bridge checks every
one of the 467 listed source inputs against current public source. Four previously
separate note/route controls enter `verify.PORT_FILES` only after all frozen
writers/readers close. A cold checkout restores the launcher's declared CRLF;
normalized text is identical to the former live LF copy. Older source/program
receipts are preserved without restamping. Old v1349 probes replay from their
archived source snapshots; their profile must not be paired with new source.

Receipts below `.analysis/port64/route-render-v1350/`:
`aggregate-render-v1.json`, `product-source-bridge-v1.json`,
`presentation-{linux,ubsan}-receipt-v4.json`,
`presentation-windows-{receipt,readback}-v5.json`,
`window-linux-receipt-v2.json`, `window-windows-{receipt,readback}-v2.json`.
Frozen source/compiler/link metadata and stable controls accompany them.
`prepare-window-v2.py` derives both observed GUI variants; native/Windows
launch scripts preserve commands and initial/final physical files. Replays
require fresh destinations. Source/program production remains separate from
public route entry and current GUI delivery.

Early probes remain inconclusive: setup completion was not physically saved;
an imported core omitted its PUBLIC include/GAME/ymfm interface; omitted GCC8
filesystem linkage crashed before observation; omitted MinGW static runtimes
failed before entry. Same-object relinks restore canonical dependencies and
pass. Their failures, sources and link receipts are retained, not rewritten.
Link-input archives restore exact libraries/object aggregates/failed probes;
ordinary object/dependency files regenerate from pinned source and flags.

Scoped cleanup retains both 195-program vectors and the independent compiled
source worktree. Eight fully read-back archives recover seven owned Windows
stages and static link inputs/failed probes. The first guard rejected four
protected cache removals; exact stable copies restore them. Its live-log
immutability error and original failure remain recorded. Fresh
`retention-receipt-v2.json` checks 13,737 immutable hashes and records 866 stage
files/1,843 generated files retired, net 1,206,464,512 allocated bytes reclaimed
(1,150.6 MiB). Existing accepted receipts are never restamped.

Fresh `terminal-readback-v1.json` independently verifies all archive members,
the 13,737 immutable hashes, both 195-program vectors and compiler/cache/link
metadata, plus all 467 public/candidate/archive source inputs. Original/current
music and route receipt links retain their identities after cleanup.

Final root/native CIs and whitespace checks pass. Root also replays the live
Ghidra database and mutation controls; native private database checks skip
because that checkout has no database. A separate source-backed post-CI cache
journal retires 1,037 public Python caches/17,686,528 allocated bytes while
preserving all 1,037 source hashes.

## Ordinary key-only logical routes (v1349)

GNU8, optimized UBSan and actual Windows AMD64 each complete the following
ordinary-mode prototype routes. Inputs choose movement, shot and Bomb from
observed native state; they never change actors, hit/life/score/stage/clear
state. Initial configuration uses the legal six-life/two-bomb menu settings.
No Continue occurs. The Normal-earned physical score file admits Extra in a
new process on the same host, including Windows; no unlock bit is injected.

| Route | Route advances | Ending entry | Misses / Bombs used |
| --- | ---: | --- | ---: |
| Reimu Easy, five stages | 72434 | `_ED001.TXT` | 2 / 10 |
| Reimu Normal, six stages | 88934 | `_ED000.TXT` | 8 / 21 |
| Marisa Normal, six stages | 79214 | `_ED100.TXT` | 5 / 15 |
| Reimu Extra, both bosses | 29611 | Extra MAINE | 3 / 8 |

Each route reaches registration, writes its independent host score and returns
to fresh OP. Across four cases,270193 route advances/37 whole capture files
perhost agree: full recorded key/telemetry streams, stage/fresh-OP BMPs, entry
metadata and physical final `GENSOU.SCR`/`MIKO.CFG`. Startup wait advances are
outside these route-loop counts. GNU Easy with every-refresh rendering also
agrees with deferred presentation for all72434 inputs/telemetry, eight capture
files and final saves. This is native host consistency, not an independent
original whole-route comparison or a physical timing claim.

The prototype uses current maintained `main.cpp` and `view.cpp` with two
declared test-entry hooks: include `pilot.inl`, and route the startup-check
entry to `run_natural_route_probe`. Ordinary GUI constructors enable the same
configuration/registration owners plus separate host timing. No game body is
changed. All103 GNU core objects and all103 MinGW core objects are raw-equal
to recorded current195product objects from the v1348 pre-retirement journal.
This compiler bridge binds the gameplay hypothesis; it does not promote DOS
exactness. Current195programs remain unchanged. Three stable prototype programs
and their source/compiler/cache-link profiles are separate from that vector.

`port64/natural_route_probe.inl` and `verify_natural_routes.py` are maintained
replay controls. Their own hashes/source archive bind them while existing
Python/PowerShell membership stays frozen for the live138song producer. Add
these two entries, along with the two note verifiers, to `verify.PORT_FILES`
only after the producer and guarded consumers close. The GNU public verifier
replays all four cases against the independently retained first native runs.

Receipts: `.analysis/port64/route-exploration-v1349/aggregate-receipt-v5.json`,
`{linux,ubsan}-v5/`, `public-linux-v5/`, `windows{,-extra}-receipt-v5.json`,
`windows{,-extra}-save-readback-v5.json`, `render-partition-v4.json`,
`{gnu,windows}-core-object-bridge-v5.json`.

```sh
python3 port64/verify_natural_routes.py --host linux \
  --binary .analysis/port64/route-exploration-v1349/program-linux-v5 \
  --product-profile .analysis/port64/route-exploration-v1349/programs-v5.json \
  --source-profile .analysis/port64/route-exploration-v1349/source-profile-v5.json \
  --hdi ../../runtime/images/zun.hdi --font /path/to/FREECG98.bmp \
  --reference .analysis/port64/route-exploration-v1349/linux-v5 \
  --extra --output NEW-ROUTE-OUTPUT
```

For UBSan choose its attested stable program and host. Restore the archived
Windows stage or generate a fresh guarded plan using `verify_windows_current.ps1`;
the separate Extra plan copies Windows's own Normal-earned physical saves.
Private source archives/retained CMake flags reconstruct the two hooks and
prototype build. Use fresh output paths. The earlier unoptimized pilot dies
in Stage2 and is exploratory evidence only; its source/logs remain, but its
scratch executable was superseded before an accepted raw recovery claim.

Terminal `retention-before-v5.json`/`retention-receipt-v5.json` protect5358files,
retire993terminal/generated files after full two-archive member readback and
reclaim410439680allocated bytes net (391.4MiB scoped). The Windows normal/
Extra stage recovers from `windows-stage-recovery-v5.tar.gz`; the first-load
song stage separately recovers from the audio directory's
`firstload-windows-stage-recovery-v1.tar.gz`. Current195programs/six private
stable programs and all native raw captures/saves remain. Private CMake
intermediates regenerate; cached duplicate executables recover from stable
v5 copies. All live original/song-watch writers stay excluded.

Fresh `terminal-readback-v5.json` passes after retirement, including both
archive/member/capture readbacks, current195programs and frozen original tools.
Root and native final CI pass; root Ghidra replay/mutation smoke passes.

Product CLI/GUI integration, complete startup presentation, remaining ranks,
shots/Continue scenarios, host input/refresh/slowdown and dense Lunatic
performance remain. Full138song closure remains separate. All launches stay
muted; no audio device opens and no current GUI is published.

Historical bounded results, preserved from `docs/PORT64.md`. Current state is
[the port overview](../../PORT64.md). Original CPU execution and adapter scope
remain explicit; successful component controls do not accept complete gameplay.

## Stage-clear and all-clear bonus

`port64/stage_bonus.*` now owns both original reward calculations, the ordered
text/gaiji/performance/HUD requests, Bomb increment and all-clear extend-disable
side effect. Ordinary native Stage1 consumes this owner exactly once after its
post-boss dialog and shows a colored bonus TRAM layer over graphics tone60.
This advances the v1260 frontier above: the preview now stops on the actual
bonus screen. Score drain, leave overlay, persistent resident statistics and
next-stage resource handoff remain the next integration work; freezing there
does not establish a complete stage transition.

Independent original MAIN CPU controls execute main03 13A9:9C31 (ordinary),
9E06 (all clear),99FE/9A89 formatters,9AFF/9B59 multiplier helpers and actual
main01 0AAF:1874/188E performance arithmetic. At load2000, CS33A9/2AAF,
DS8000 copied from relocated DATA, all1,837 cases agree on complete score delta,
Bomb count, performance, extends and palette tone, plus ordered text/gaiji
bytes/coordinates/colors and performance/HUD calls. There are986 ordinary and
851 all-clear controls, including the complete modifier matrix, five ranks,
Extra, unhandled byte values, word component wrapping, byte Bomb/performance
wrapping, life underflow, pre-modifier threshold neighbors and score-delta
overflow. Linux ELF64, Wine/MinGW PE32+ and optimized GNU UBSan/bounds all
execute the same original CPU producer independently. Video consumers are
intercepted; these controls prove math/state/requests, not complete rendering.

Preserve these original details:

- Reward units are ten points; value gaiji append the final zero. Component
  values first wrap as unsigned16-bit values, then widen. This includes
  graze×5 and `(remaining_lives-1)×1000/3000`; zero lives is not clamped.
- Life-credit, Continue and rank multipliers each perform their own unsigned
  multiply/divide-by10 and truncate. Extra has no rank multiplier. A zero final
  defeat-bonus byte applies a zero multiplier and skips the other descriptions.
- Ordinary performance thresholds use the unmodified subtotal, even when
  timeout zeros the award. The Bomb byte increments on every ordinary clear,
  including timeout/zero point items; then no-miss/low-Bomb performance raises
  run in order. All clear sets extends10 and does not grant a Bomb or change
  performance.
- Raise performs wrapped byte addition plus unsigned upper clipping; lower
  performs wrapped byte subtraction plus signed lower comparison. The target
  arithmetic executes, rather than being replaced by an Oracle adapter.

`bonus_text.hpp` localizes the maintained MAIN DATA strings with readable
Japanese comments. The CPU Oracle found the candidate timeout description at
`src/main/stage/bonus_state.asm` has eight full-width spaces before ×; pinned
MAIN DATA2134:1F79 has seven. The portable table corrects this one character.
The DOS owner is unchanged because changing its data extent would require
separate layout/build validation. Candidate DATA observations are not inherited
as original facts. Negative receipt: `bonus-v1261/candidate-text-mismatch.json`.

Native fixtures still start eight natural Stage1 routes from the OP handoff
with real gameplay and no injected reward or Boss start. Their final snapshot
now includes the actual bonus; the first four images/counters and all prior
shot/combat/midboss/diagnostic Orange images remain unchanged. Three extra ticks
leave delta/Bomb unchanged, proving the front end does not award repeatedly.
The current native prototype has no death/Bomb/Continue consumers, so those
live counters remain zero; only the isolated original CPU cases cover their
nonzero reward effects. Colored TRAM uses actual font/game gaiji and cell
replacement, including blank glyphs. Blink and complete original color/page
composition are not established by the snapshot controls.

Ten contracts and40 natural checkpoints agree Linux/Wine/UBSan. Native Windows
headless replay also passes ten contracts and the40 BMPs/48 counters. The
Windows root native executable and English launcher are refreshed with a
versioned backup under `port64-preview/v1261`; DOS files/launchers/assets are
unchanged. No native Windows GUI pacing or original full-route claim.

```bash
python3 port64/verify_bonus.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-bonus-contracts \
  --output-dir .analysis/port64/bonus-v1261/cpu-linux-attested
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-bonus-v1261-final/receipt.json
```

Receipts: `bonus-v1261/cpu-{linux,windows,ubsan}-attested/receipt.json`,
`integration-review.json`, `native-windows-receipt.json` and
`verification-bonus-v1261-final/receipt.json`. The same independent rejecting
adapter control checks that a Unicorn callback exception cannot silently pass.
Semantic remains stopped; next implement score drain and actual stage leave /
resource transition, not additional naming work.

## Score drain and extends

The current native MAIN ends each ordinary simulation frame with the original
score owner, after its frame counter and periodic performance raise. Actor/item
awards enter one pending accumulator. Score update transfers that amount into
eight little-endian decimal bytes, preserves continues in digit0, compares the
complete high score and dispatches extends. Life/performance changes and the
20-frame bullet-clear minimum feed the actual simulation; sound, life-HUD and
popup remain requests pending their consumers. HUD score rows56:4/6 now use
the original game gaiji and remain bright over dimmed graphics.

Pinned MAIN main01 0AAF:6BD4..6CA2 (update),6BA2..6BD3 (HUD),4316..43B5
(extend) and actual1874 performance raise are independently executed at load2000,
CS2AAF, isolated DS8000 copied from target DATA2134, resident9000:0000.
All4,690 transitions agree Linux GCC8.4, MinGW13 PE32+ under Wine and optimized
UBSan/bounds:3,759 isolated controls plus five retained-state sequences926 steps
and their five initial calls. Subsequent awards are injected into each owner's
retained state; target outputs are not reseeded into native after each tick.
Complete decimal/high-score/temp/HUD bytes, pending/frame dwords, life/clear/
performance/extend/popup state and ordered requests agree. The rejection control
also proves a failed Unicorn callback cannot silently pass. Identity remains
candidate-local-attested; no DOS exact claim follows from portable equality.

Keep the target's low-word-only frame-delta assignment even when a fixture's
high word is nonzero. Preserve the five temporary-digit writes and six AAA
iterations, including nondecimal AF/two-byte carry controls. The highest score
byte remains unnormalized. Extend predicates compare digit6/7 directly rather
than a total integer threshold, then raise performance/increment extends before
the life-cap check. Granting a life from99 produces100; the next grant is
suppressed. Continue and score digit0 share target DATA2134:4349 (confirmed by
0AAF:3CDA increment and43C0 reset skipping digit0). Maintained DOS storage
places a separate `_continues_used` byte before `_score`; that candidate layout
cannot establish the native ownership contract. DOS source is unchanged.

The live900-frame pickup/drain control conserves all awards, grants two extends
once, emits SE7 requests and publishes a20-frame clear timer. Eleven contracts
pass Linux/UBSan/Wine/native Windows. Forty natural Normal/Lunatic character/
shot-idle snapshots and counters agree Linux/Wine/UBSan/native Windows. The
old60-frame BMP is independently recreated with the saved v1261 PE; exactly960
pixels change inside the two new HUD rows, with every other pixel retained.
This pixel mask justifies the new MAIN fixture hash; other fixture changes may
also reflect real extends/performance changes, not just HUD.

At the end of the score batch this Stage1 preview still froze at the bonus;
the following departure batch connects its same-frame continuation and clocks.
Saved high-score loading, life-HUD, popup/audio, death/Bomb/Continue lifecycle,
resident publication and later resources/Ending/save remain separate work.
Current source/build receipts and English native launcher are packaged under
Windows `port64-preview/v1262`; the root native executable is refreshed only
after delivered hash checks. DOS products/launchers/assets are unchanged.
No full-route, original TRAM/palette composition or GUI frame-pacing claim.

```bash
python3 port64/verify_score.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-score-contracts \
  --output-dir .analysis/port64/score-v1262/cpu-linux-attested
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-score-v1262-attested/receipt.json
```

Receipts: `score-v1262/cpu-{linux,windows,ubsan}-attested/receipt.json`,
`target-owners.json`, `render-review/receipt.json`, `integration-review.json`,
`native-windows-receipt.json`, and `verification-score-v1262-attested/receipt.json`.
Stop naming work here; next resume the actual boss-update frame after blocking
dialog, then port the416/488 leave/next-stage handoff without skipping it.

## Stage enter and departure

Ordinary Stage1 now enters through the original black TRAM gaiji mask, completes
its blocked post-boss dialog inside the same actor frame, awards/drains its
bonus, and executes the416/488 leave sequence. The actor prefix runs once;
paused dialog ticks do not move actors or consume RNG. On continuation the
saved contexts feed items/gathers/render, overlay, frame/periodic performance
and score. Deferred tone60 is applied when that frame completes; the dialog
snapshot retains the palette previously displayed. Removing the former extra
front-end dim prevents the bonus scene from being dimmed twice.

Observed pinned MAIN owners at load2000: main01 CS2AAF, unloaded0AAF:
enter62B3..6348, leave6349..63B4, black6287..62B2; main03 CS33A9,
unloaded13A9: common defeatACB3..AE86. Isolated DS8000 is copied from
relocated DATA2134; resident9000:0000. Gameplay-loop0AAF:0098..0212/fileC388
places player/shots/bullets/enemies before the far boss callback at0105,
items/gathers after it, overlay0148 before clock01A8 and score0204. Database
attestation is the root `.analysis/ghidra/database-attestations/th04-main.json`.
These are target/runtime observations, not a new DOS exact promotion; pinned
target provenance remains candidate-local-attested.

Enter/leave share DATA2134:1B62. Enter draws at nonzero multiples of8 using
byte gaiji64-time/8 and retains72 when it changes callback to titles. Leave
decrements first; at416 it starts72→71, at488 zero-time black fill clears the
callback. TRAM is replaced across24×23 gaiji cells, not blended over retained
bonus letters; the score rows outside the playfield remain bright. Actual
GAMEFT gaiji57 independently explains all8,726 changed pixels in the60-frame
fixture relative to the saved v1262 PE; all other pixels remain identical.
Title/BGM/demo overlay consumers and original complete video timing are separate.

Common defeat adds wrapped stage graze before dialog, then calls bonus exactly
once. At416 it requests sound fade10; at488 it increments resident stage/ascii,
sets quit2 and requests one delay frame before finishing the ordinary frame.
TH04 ordinary leave does not flush pending score; remaining score carries into
the next session. The live application publishes graze/lives/Bombs/stage/ascii
without replacing MAIN, reseeding its LCG or falsely loading Stage2 resources.
Further input is held at that unloaded request. The current preview ends with
black playfield and bright score, pending the actual Stage2 loader and actors.

Independent original CPU controls cover all256 timer bytes, interval/wrap
boundaries and1,929 departure cases. Original machine context pauses at the
far dialog callee and resumes at its actual return address; held ticks preserve
the caller state. Three retained489-tick original departure→leave→score sequences
exercise pending1,20,000,000 and2,000,000,000, including nonzero pending at
stage advance. In total4,331 input commands/7,265 complete state and ordered
request records match GCC8.4 Linux, MinGW13 PE32+ under Wine, optimized
UBSan/bounds and actual Windows PE execution. A rejecting callback remains a
required negative control. Forty focused original Orange phase255 snapshots
also preserve the prior serialized boss/pool/global/RNG contract.

The first fixture was rejected at frame1 because Python native-aligned Bh
inserted a padding byte, writing256 to target53DA. Explicit packed little-endian
<Bh restores the intended phase/frame bytes. Keep the rejecting observation;
an adapter packing error is not permission to change target semantics.

Twelve contracts pass Linux/UBSan/Wine/native Windows. Eight natural Normal/
Lunatic character/shot-idle Stage1 routes produce64 identical BMPs and72
counters across all hosts, through bonus,416 fade, late mask and488 request.
Controls check actors/RNG do not repeat on dialog resume, bonus/fade/next-stage
requests occur once, and the unloaded Stage2 request freezes further updates.
These are headless behavior/picture controls, not measured GUI frame pacing.
Windows package `port64-preview/v1263` and root native launcher are refreshed
after delivered hashes; DOS products/assets and normal/invincible launchers
are unchanged.

Stage2 session/resource initialization, midboss/Kurumi, final/Extra Ending
dispatch, saved high score/life HUD/popup/audio/death/Bomb/Continue/Ending/save
remain outside this slice. Later run initialization must reset accumulated
resident graze at its actual owner; these scenarios start a fresh application.
When loading Stage2, preserve global pending score while resetting only the
proved stage-owned counters/pools, then activate the correct resources/boss.
Do not merely relabel Stage1 or reuse Orange as a placeholder.

```bash
python3 port64/verify_transition.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-transition-contracts \
  --output-dir .analysis/port64/leave-v1263/cpu-linux-attested-final
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-leave-v1263-final/receipt.json
```

Receipts: `leave-v1263/cpu-linux-attested-final/receipt.json`,
`cpu-{windows,ubsan}-attested-final/receipt.json`, `target-owners.json`,
`gameplay-loop-owner.json`, `render-review/receipt.json`,
`orange-departure-cpu-linux/receipt.json`, `integration-review.json`,
`native-windows-cpu.json`, `native-windows-receipt.json`, and
`verification-leave-v1263-final/receipt.json`. Semantic remains stopped;
next port the actual Stage2 session/resource/actor boundary.

## Stage actor-session preparation

This section records the v1264 preparation frontier. The following Stage2
midboss section advances that actor integration beyond2600 to the Kurumi gate.

The next-stage actor API now operates on the existing MAIN owners instead of
creating a new gameplay session. It clears the seven implemented entity pools,
resets player current/previous position, firing time/style, stage point/dream
counts, graze/zap and gather/circle setup. It preserves process-wide score/
pending score, power/overflow/performance, input latch/velocity, shot volley and
hit-spark cycles, bullet clear timer/template/counters, gather center and spark
ring-offset high byte. Score HUD refresh does not drain pending awards.

The original random call order is ring256 → item drop1 → spark angles96,
all from the existing process LCG. Twenty-four double resets retain the same
original machine and native owners between calls:706 draws, with no reseeding
from target output. Stage2 preparation validates its STD before mutating owners
or consuming RNG. The actual departure request is required; MAIN generation,
resident statistics and score remain in the same application.

Observed pinned MAIN load2000/isolated DS8000 owners: main01 unloaded0AAF
runtime06E0..07AD, stage-state73DB..74A5, shots-reset593A..5953,
ring1168..117F and sparks1824..1841; main03 unloaded13A9
items9F8B..9FA7, midboss-reset642C..6453 and Stage2 setupA623..A6F5.
Actual library IRand2000:2172 and score HUD6BA2 execute. Original stage-state
clears nine complete physical extents, checked independently with upper EAX0
on entry to the register-ABI REP STOSD helper. Native custom-entity/point-popup
owners are absent; these target clear checks do not claim their implementation.
Clipping/hardware, shot-level dispatch, item splashes, Bomb, thick lasers,
point numbers and remaining HUD callees use explicit adapters.

The Stage2 midboss seed changes start2600, HP750, sprite0, current/previous
position3072,-512 and velocity0,16; inactive phase/frame/damage metadata stays.
All256 phase-byte controls execute actual original midboss_reset and stage2_setup
and compare the22-byte midboss state plus active flag. Boss/Kurumi callbacks,
rank-dependent boss fields and resource consumers are not ported by this seed.
Native MAIN holds before frame2600 so it cannot invoke the Stage1 callback
under a Stage2 identity.

All928 selected original CPU controls agree Linux GCC8.4, Wine-hosted MinGW13
PE32+, optimized UBSan/bounds and actual Windows x64. There are648 isolated
actor resets,24 retained double resets and256 midboss seeds. The checkpoints
include selected persistent metadata, all96 spark angles, all256 ring samples,
post-clear actor flag/position emptiness and score/HUD bytes. Rejected callback
control remains mandatory; these are bounded state claims, not whole-session
or DOS exactness claims. Identity remains candidate-local-attested.

Four controlled native Normal/Lunatic character routes finish natural Stage1,
retain its actual awards and then load original ST01.STD/ST01.MAP. They execute
10,400 total Stage2 frames, reject invalid STD before mutation and stop at2600
with midboss2 pending. Their counters agree Linux/Wine/UBSan/native Windows.
This is actor/STD/background-state integration without Stage2 visual resources,
full original gameplay or GUI pacing comparison. Thirteen contracts and the
previous64 Stage1 BMPs/72 counters agree all hosts and remain identical to v1263.

The GUI still ends at the unloaded Stage2 request. The new actor API is used
only by controlled integration until its caller replaces stage-owned sprites,
MAP/MPN/palette/portraits/dialog state and joins midboss2/Kurumi. Shared player
resources remain resident. Test package `port64-preview/v1264` contains current
x64 executables, native Windows verification and private stage fixtures; the
root GUI executable remains v1263. DOS source/assets/launchers are unchanged.
Do not advertise full Stage2 gameplay based on this preparation API.

```bash
python3 port64/verify_session.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-session-contracts \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --output-dir .analysis/port64/session-v1264/cpu-linux-final
```

Receipts: `session-v1264/target-owners.json`,
`cpu-{linux,windows,ubsan}-final/receipt.json`, `native-windows-session.json`,
`native-windows-receipt.json`, `integration-review.json`, and
`verification-session-v1264-final/receipt.json`. Initial invalid-style fixtures
were rejected by the existing shot-checkpoint guard; valid styles are now seeded
explicitly. The target/native actor code was not weakened to accept corruption.
Semantic remains stopped. Next implement Stage2 resources and midboss2.

## Player hit, death and Bomb state producer

v1301 introduces `player::Lifecycle`, using the existing movement and shot
trigger owners. It implements original player-update, miss-update, Bomb entry
and Bomb render-state dispatch. This is a component, not live MAIN integration:
character Bomb graphics and the blocking Game Over/Continue scene must join
before gameplay consumes the hit latch. Fire, miss-item, HUD and sound requests
retain order; a missing last-life consumer throws instead of accepting a fake
Game Over return. All verification remains silent.

Original MAIN relative `0AAF:54C4..553A` (player_bomb), `571A..581D` (Bomb
render-state dispatch), and `5E98..610D` (miss/player update) execute at loads
1000/2000, with explicit DS8000/SS7000/resident9000 adapters. Actual movement,
position clamp, point motion, trigger branches and performance-lower instructions
execute. Fire/items/HUD/sound/Game Over/character-graphics calls have guarded
ABI adapters and do not accept those consumers. Header/file identity and root
live MAIN Ghidra attestation pass. Targets remain candidate-local-attested.
Use the boundary ledger's payload offset or authored ledger's file_offset;
analysis_linear/address fields include the analysis load base and are not file
positions. An early scratch disassembly read the wrong region through that
confusion; no state, name or source claim was accepted from it.

The original decrements invincibility before checking the retained hit byte.
A newly accepted hit limits the laser clock to33 before the separate shots
update, arms miss40/invincibility192/respawn72 and clears velocity. The same
player update advances respawn and decrements miss, giving eight opportunities
to deathbomb before the miss32 loss. Shot-trigger time stays frozen during
respawn. At miss32, item drops precede power loss, dream loss, HUD/shot-level,
sound2, performance cap/lower and wrapped resident miss count. At miss0, position
becomes192,368 with velocity0,-32; remaining lives>1 decrements lives, resets
bomb stock and arms clear32. The remainder of the72-refresh motion reaches y304.
Valid dream indices0..7 are controlled; invalid host death indices are rejected.

Bomb entry rejects bombing, no stock, disabled and miss<=32. A deathbomb clears
miss/hit/respawn; stock/HUD precede bombing/frame0/invincibility255/background,
clear192/sound13/pull/used count. Render dispatch preserves BB cel0..15, frame48
scroll-off/palette14 backup and replacement, frame176 restore/sound15/scroll-on,
frame177 hardware scroll request, tone recovery through225 and cleanup at226.
There are227 render updates from frame0 through226. All byte/word wraps and
retained option/palette fields are explicit; host X is translated to MAIN Bomb
bit10 rather than its old dialog bit800/keypad movement meaning.

8,235 isolated controls and four retained260-refresh sequences produce10,319
complete state/request records at each original load. GNU/optimized UBSan/actual
Windows agree byte-for-byte with the same reference. These include corrupt-but-
representable byte flags, timer/stock/counter wraps, movement/trigger boundaries,
all256 Bomb frames, invincibility1-hit behavior, same-refresh deathbomb, last-life
call boundaries and full respawn/Bomb cleanup. An altered Shot fixture changes
clock/requests and is rejected by the untouched original comparison.

Three builds retain35 AMD64 products each and pass34 contracts. The250-file
manifest is `dc88a3e9e12c79f7f64b1b8561a7c2455af4dbe12f6e177dbf49ddf1a7b13496`.
Receipts are under `.analysis/port64/player-lifecycle-v1301/`:
`original-linux-final/receipt.json`, `actual-windows-final/receipt.json`,
`platform-review.json`, native traces, CTest logs and `comparator-mutation.json`.
Replay `verify_player_lifecycle.py --target ../../targets/th04/main.exe --exe
.analysis/port64/linux-live-v1251/th04-port64-player-lifecycle-contracts
--output-dir FRESH`; the Windows verifier consumes that pinned two-load reference
and runs all34 contracts. No physical timing/audio, live player death/Bomb,
Continue, pixel or DOS exact claim. Next implement the missing graphics and
blocking scene, then join this producer and real hit/stock/ranking publication.

## Game Over clock and Continue file ownership

v1302 adds `gameover::Scene`, `gameover::Menu` and separate MAIN score-file
operations. This remains a component: live MAIN suspension, Game Over TRAM
rendering, actual Continue host persistence and Bomb character graphics have
not joined. Target and original CPU observations are separate from native host
observations. Root MAIN database attestation and pinned file/MZ checks pass;
canonicality remains candidate-local-attested. No DOS exact claim follows.

Original MAIN relative `0AAF:3971..3CEE` executes the cell fades, full Game Over
owner/menu and actual score-reset body at loads1000/2000. The original
`130E:0133..0187` release/press loop and `00D7..00EA` frame-delay body execute;
keyboard samples and a recorded refresh counter replace device/IRQ consumers.
Original `0000:0666..06A3` black-out instructions execute with explicit vsync and
palette-show adapters. TRAM, ranking-save, HUD, shot-level, song and process
execution are guarded consumers, not accepted implementations in this control.

Initial out32 + in36 + the27-refresh letter slide reaches acknowledgement at
refresh95. Wait0 has no timeout and ORs two samples; a held acknowledgement key
cannot also accept Continue. The menu supports one vertical toggle per released
press; simultaneous directions toggle once, and Cancel takes priority. Final
Stage (stage_id5) dispatches Bad Ending immediately. Extra (stage_id6) still
shows/acknowledges Game Over, then skips Continue. Used-credit byte subtraction
wraps exactly; ordinary three-credit exhaustion skips the menu. Continue saves
before resetting power1/dream-items0/lives/bombs and score digits1..7/deltas/
extends/popup; dream_score, high score and unrelated buffers remain under their
original ownership. A failed save prevents reset. Continue fades take32+36
refreshes. Quit publishes ES_SCORE before song-fade4 and palette-blackout4;
initial synchronization plus17 four-refresh steps totals69, then requests MAINE.

MAIN file ownership differs materially from the previously attested MAINE
owner. Original relative `0AAF:18BA..1939`, `7F1A..81D7` and original TC4J LCG
`0000:2172..219C` execute with guarded byte-store adapters and actual memory-copy
instructions. MAIN encode takes low/high bytes of ONE RNG word. Its recreate
uses10 draws and writes ten sections; save uses ONE draw and writes only the
selected section. MAINE instead uses two RNG draws per key and save re-keys all
ten sections with22 draws. MAIN character selection tests resident ASCII'1'
exactly. Continue always loads/recreates, including non-turbo; turbo inserts the
8-gaiji CONTINUE name if ranked, marks ordinary stage1+stage_id or Extra stage1,
and writes only then. Ties precede existing equal rows; name terminators, unused
bytes, cleared mask, nonselected sections and trailing bytes retain ownership.

Final-source controls: 2,003 menus /43,661 records, 64 full scenes /677,160
records, and2,985 MAIN file cases /27,710 records. Each agrees between two
original loads, GNU, optimized UBSan and actual Windows. All34 contracts pass
per host. Retained10,319 lifecycle and1,288 MAINE score controls also agree on
all three hosts. Altering a Continue fixture's turbo flag changes the trace and
is rejected by the untouched reference. Initial development streams passed
comparison but were rejected by source-manifest guards after concurrent source
edits; final producers reran against the frozen257-file manifest. No rejected
run enters accepted evidence.

One first actual-Windows contract run reported `cannot replace native score
file` in the separate host-store consumer. Three isolated16-case retries and
the complete34-contract/differential rerun pass. The original error code and
cause are unknown; this is not a diagnosed Windows/antivirus defect. The failed
command/log remains under `actual-windows-failed-first/`. Keep failure
propagation and verify real Continue saves/restarts when the live owner joins.

Manifest: `85bfb562d43d6328cf738530a13c9320a90ffb2ab21fb0ffb3dda05aa29f3a7c`.
Receipts under `.analysis/port64/gameover-v1302/`: `menu-linux-final/`,
`scene-linux-final/`, `main-score-linux-final/`, `actual-windows-final/`,
`platform-review.json`, `comparator-mutation.json`. Replay checked-in
`verify_gameover.py`, `verify_gameover_scene.py`, `verify_main_score.py` with
`--target ../../targets/th04/main.exe --exe CACHE/CONTRACT --output-dir FRESH`;
`verify_gameover_windows.ps1` consumes the three fresh original references and
runs all34 contracts. All launches remain silent; no audio device is opened.

Periodic storage cleanup, requested by the user, reclaimed980,566,016 allocated
bytes this batch. Completed v1300 graphics/frontend and current v1302 traces
were independently read back before immutable hard-link deduplication. Failed
or superseded development streams were retired with path/size/hash records.
Final capture paths and receipts remain; original targets/HDI, source and three
build caches are unchanged. `cleanup-receipt.json` / `final-capture-storage.json`
record protection checks and reclaimed bytes. Never overwrite a shared capture
inode; use fresh replay directories. This is storage maintenance, not new game
acceptance or permission to delete pinned tools/inputs.

## Character Bomb state and graphics

v1303 reconstructs the two character render bodies at MAIN relative
`0AAF:555D..5623` and `5623..571A`, and the retained48-star producer at
`581D..593A`. Target identity is the pinned156,258-byte MAIN; independent
original execution uses loads1000/2000, explicit DS8000 and guarded stack
returns. Actual RNG, polar-vector and growing-circle instructions execute.
The logical comparison adapts fill/CDG/mono and sound calls into ordered
requests; it compares the complete288-byte star array,160-byte circle pool,
shared-ring cursor, tone/change/color and all requests.

The graphic control executes original BB553A/1426/74D8, fill751A/7578,
CDG130E:05D4..0639, mono152A..15A9 and GRCG setup/color instructions. An
explicit visible640x400 shadow handles GRCG TDW/RMW and direct B/R/G/I plane
stores. Independent HDI/PAR and BFNT input decoding supplies BB0/1.BB,
BB0/1.CDG and MIKO16.BFT; the native raster never produces the reference.
Both loads agree on full retained indexed screens. Physical display pages,
scroll registers, pacing and audio remain outside this claim.

Observed behavior retained by the native implementation:

- BB has16 cells,24 columns and23 rows; one bits replace16x16 tiles. Physical
  rows wrap at400, including scroll offsets383/384/399.
- The character picture is384x274 at(32,56). The fill kernel replaces only
  rows16..55 and330..383:94 rows, preserving the central picture rectangle.
- At frame48 each of48 stars draws X/Y from the shared ring. Reimu rejects
  the inclusive X band2048..4096 and derives speed by signed division by9;
  Marisa adds160 to a byte-sized random value, preserving byte wrap.
- Updates preserve signed-WORD position wrapping and arithmetic-right-shift
  pixel coordinates. Reimu retains X at an out-of-bounds respawn and sets Y6144;
  Marisa alternates left-edge and bottom-edge respawn by star-index parity.
- Growing-circle calls at frames81..160 depend on the retained mod4 byte,
  rather than recomputing it from a convenient host counter. Reimu creates two
  polar points; Marisa consumes the additional bounded RNG draw. Full pools
  preserve attempted requests even when allocation fails.
- State advances once per render dispatch. Repaints consume const cached draws;
  they do not repeat particle motion or shared RNG consumption. Circle drawing
  remains the existing separate foreground owner.

Final controls:1,236 state cases/2,252 records, including independently retained
128-refresh character sequences;294 pixel cases/548 full screens,
140,288,000 compared pixels. GNU8.4, optimized undefined/bounds UBSan and actual
Windows AMD64 all agree;34 contracts pass per host.105 products bind263 source
files to manifest
`c0fbe950be3e6f7a4bf794ea357d0c92d6d1859e8c4684296e77137b47d11751`.
A one-bit star-speed fixture mutation is rejected against the unchanged original
state reference. This accepts a Bomb component, not live death/Bomb gameplay.

One development pixel fixture omitted caller GRCG setup for a standalone star
entry. The bounded negative replays a first mismatch at pixel402 (wrong original0,
native2). Executing actual1666/1672 caller setup restores complete pixel equality.
The correction changes Oracle preconditions, not product behavior. Preserve
this distinction; a mono graphics callee does not own its caller's hardware mode.

Replay with fresh output directories using `verify_player_bomb.py`,
`verify_player_bomb_pixels.py` and `verify_player_bomb_windows.ps1`. Final receipts,
source/product hashes and recorded actual Windows command live under
`.analysis/port64/bomb-v1303/`; `review_results.py` reads back the complete native
streams. Captures use gzip; actual Windows hashes binary stdout without creating
an additional140MB raw dump. Eight superseded generated streams are retired
with hashes, reclaiming13,643,776 allocated bytes while2,379 protected source,
cache, input and final-reference files remain unchanged.

Next join these graphics with the player lifecycle and Game Over TRAM owner,
then suspend live MAIN at its actual last-life boundary, save Continue before
resetting resources, and resume the remaining frame once. Extra, full HUD/OP,
audio/configuration and complete natural route/performance validation remain
in the full goal; all launches remain muted.

## Game Over TRAM rendering

v1304 adds `gameover::Renderer` and extends the existing registration TextPlane
with retained initial WORD banks and bounded ANK writes. Game Over owns no new
actor update: the renderer receives frozen indexed graphics/palette, applies
ordered TRAM requests and composes the scene's tone. Repainting consumes const
state and does not advance its clock or any RNG. This remains a component;
its scene, player lifecycle, Bomb dispatch and Continue host save have not
joined live MAIN. All runs are silent and open no audio device.

Pinned MAIN target/file/MZ checks and the root live database attestation pass;
canonicality remains candidate-local-attested. Original relative
`0000:1B0C..1BA6` (gaiji putc/puts), `229E..2368` (ANK putc/puts) and
`0AAF:625B..62B3` (playfield wipe/black) execute at loads1000/2000, with explicit
DS8000/SS7000 and DATA0768=A000 text segment adapters. Every character and
attribute store and the original FAR return instructions execute. No return
adapter or target code patch is used by this new TRAM control.

Wipe and black cover rows1..23 and columns4..51 only; they preserve margins and
HUD cells. Both write character0020, paired respectively with attribute00E1
and0005. Gaiji retains both half-cell codes/attributes, including column79
spill and overlapping pairs. Game Over's two-space ANK erasure is a separate
operation. Text colors/reverse masks are independent of analog graphics tone.
RGB composition uses hash-pinned DOSBox-X video policy and supplied FREECG98;
frozen graphics/palette and CGROM are explicit adapters, not original physical
video. General Shift-JIS console conversion is outside this bounded owner.

There are200 complete640x400 indexed/TRAM/RGB snapshots,206,400,000 compared
bytes per host. Each original load performs105,210 text calls and511,500 TRAM
stores. The controls cover256 gaiji, ASCII1..127, zero/single glyph behavior,
NUL-terminated strings, half-cell overlap/spill, eight attributes, tones0..200,
playfield-only wipe/black and seven retained scene request sequences. These
scene requests consume the earlier64-case/two-load v1302 original clock trace;
its target, trace, fixtures and unchanged scene/producer dependencies are
hash-bound. This does not re-execute full scene clocks in the new graphics
producer or widen v1302's input/IRQ/sound/process adapters.

GNU8.4, optimized undefined/bounds UBSan and actual Windows AMD64 agree on the
complete stream. All158 prior independent registration snapshots still agree
on every host, including both graphics pages, palette, raw TRAM and RGB;
this guards the shared TextPlane change. All34 contracts pass per host.
105 current AMD64 products bind267 files to manifest
`7a25a243535773ce3a5bd9eb22cf898511e87cb3daafec96ace8deaae8ab6345`.
An input-only W→B mutation is rejected at snapshot7, raw byte260168:
original attributeE1 versus native05. The unchanged original reference and
source are retained; the negative proves the raw TRAM comparison can reject a
wrong erase policy before relying on screen similarity.

Replay `verify_gameover_render.py --target ../../targets/th04/main.exe --hdi
../../runtime/images/zun.hdi --font-bmp FONT --exe CACHE/CONTRACT
--scene-reference .analysis/port64/gameover-v1302/scene-linux-final
--output-dir FRESH`. The Windows verifier consumes that current-source two-load
reference and the retained158-snapshot registration reference. Current receipts,
commands and full readback are under `.analysis/port64/gameover-render-v1304/`;
`review_results.py` binds all105 products and consumes every native gzip stream.
No live GUI, complete route, physical pacing/audio or DOS exact claim follows.

Storage cleanup gzip/readback-compacts the two new GNU/UBSan registration
captures and retires two superseded46-snapshot development streams after
checking their complete original prefix against the new reference. This
reclaims398,381,056 allocated bytes with4,167 protected source/cache/target/HDI/
final-reference files unchanged. Actual Windows separately retires203,511,584
logical raw bytes after compressed readback; its allocation is not added to
that total. Final references and active caches remain. Use fresh output paths,
never overwrite an existing hard-linked capture or rerun a destructive cleanup
against a completed batch.

Next suspend live MAIN at the actual last-life boundary, join this TRAM and
Bomb renderer, save Continue before resetting resources and resume the frame
suffix once. Extra/full HUD/OP/audio/configuration and complete natural routes/
restart/dense Lunatic validation remain required by the full goal.

## Live MAIN lifecycle suspension and Continue persistence

v1305 joins player lifecycle into `gameplay::State`. Hit latches from bullets,
enemies and NPC/laser owners are consumed before the real player prefix; miss
state reaches item pickup suppression. Fire and miss drops consume the shared
owners at their original boundaries. Character Bomb dispatch executes after
items/gathers and before boss foreground; its graphics remain a frontend TODO.
Miss/Bomb counters and resources publish to the resident owner. Boss/player
palette and circle state share explicit setters; stage palettes supply color14.

A last-life call yields a blocking Game Over scene. Actor/STD/random/frame
owners remain frozen; successful Continue resumes only the interrupted frame
suffix. `HostStore.save_continue` replays new MAIN I/O operations through real
writer-close commits before reset. Existing complete files preserve unrelated
sections; recreation and ranked save retain MAIN's single-word RNG keys. The
frontend binds this real callback and honors Bomb scroll suppression. Windows
replacement failures now include their Win32 error code.

GNU, optimized UBSan and actual Windows pass34 contracts and the explicit
player-checkpoint integration controls. Traces and three actual host files agree,
including ten sections, non-Turbo read-only behavior, restart and blocked writes.
Fresh original MAIN at loads1000/2000 replays10,319 lifecycle records,2,003
menus,64 Game Over scenes and2,985 file controls; all complete native consumers
agree on the three hosts. Original fire/items/HUD/graphics/filesystem adapters
remain as documented by their separate components. This is not an original
joined-frame or complete ordinary-route comparison.

A separate finite synthetic STD uses ACTIVATE(sprite128,hp1,score0), WAIT100
and KILL, spawning one contact enemy at frame64 and player(192,320). Ordinary
MAIN pauses at104 after105 STD prefixes, resumes to105 with105 prefixes, then
executes prefix106 next frame. A real HostStore is attached. The actor-control
negative consumes no hit. Three hosts agree on trace/save; a private repeated-
prefix mutation is rejected. Its fixture/commands/digests remain under
`.analysis/port64/lifecycle-join-v1305/`. Recompile the documented
`std_contact_probe.cpp` against each current core library and use a fresh save
directory; this is a synthetic scheduling probe, not an original stage asset.

Current receipts: `platform-review.json`, `std-contact-receipt.json`,
`prefix-mutation.json`, `cleanup-receipt.json` and the host/original subdirectories
in that root.267 listed source files bind manifest
`1f229fe18a56c9a9401c9e3f8beb1b871ac750f23c8b7b47238050d460927020`;
two new integration-verifier digests are separately bound in platform review.
105 product identities are checked.87,998,464 allocated bytes are reclaimed
with2,845 protected files unchanged; completed shared captures are immutable.
Replay all writers into fresh paths.

GUI Game Over graphics/keyboard ownership, death/Bomb indexed rendering and
Quit-to-MAINE remain unfinished. Score-only MAINE must register, then run verdict,
then enter fresh OP; Ending's ordering cannot be reused blindly. Interactive
constructors default to ordinary lifecycle. Retained long preview controls
explicitly use `actor_control` and print that hit consumption is disabled. No
GUI publication, natural route, physical timing or audio backend is accepted.

## Player death and invincibility rendering

v1306 recovers original MAIN relative `0AAF:610D..625B` (file `0x123FD`,
load-module `0x10BFD`, extent `0x14E`) into `port64/player_render.*`.
The pinned original SHA-256 is
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`;
root MAIN database/header/relocation/load/sample attestation passes.
Provenance remains `candidate-local-attested`. DOS source and acceptance states
are unchanged; this is portable semantic/runtime evidence.

Original caller, polar-vector and scroll-helper instructions execute at loads
`1000` and `2000`, with DS8000 and SS7000. The request control adapts only
SUPER/tiny graphics call ABIs. The pixel control executes the original
`0000:2D3E`, `0000:2B78` and `0AAF:1A56` kernels and their actual returns.
Independent BFNT planar/tiny-mask staging and a visible GRCG/direct-plane write
shadow supply bounded input/hardware adapters. Physical pages, invalid kernel
coordinates, CGROM, display timing and audio are outside this claim.

GNU8.4, optimized UBSan and actual Windows AMD64 agree on 6,637 complete request
records and 259 complete640x400 indexed screens (66,304,000 pixels). Each host
passes34 contracts.105 current ELF/PE AMD64 products bind274 listed files,
including the two v1305 lifecycle integration verifiers previously bound
separately. Manifest:
`fc1c6e9271fc99ab55ee9e615eee31b708730396939c6f1131f5540a771fa24a`.
Request SHA-256:
`92a465c171e568458392959cdb11daa52b012eb480b35d6c90880d47c9c061be`.
Complete indexed-stream SHA-256:
`4aef30abab8f8d3730eec9254e1da65506dea58b96d18a93d5c1b9dc206c9733`.

The producer preserves signed16 radius interpretation, truncating signed
halving at the second ring, byte angle negation/increments, signed polar
rounding, word coordinate wrap and the original clipping boundaries. Scroll
conversion adds the line only when enabled and adjusts by400 once. Miss1
emits no requests; miss2..32 emits clipped death explosions, with no body or
options. Normal rendering chooses its cel from signed X velocity and blinks
white only when actual invincibility is nonzero and retained frame-mod4 is0.

An early native test wrongly required eight explosions on every death frame.
Two-load original controls for the stationary192,320 sequence establish8/6/6/4
requests at miss32/16/8/2; the corrected live checks preserve clipping.
A private source-only mutation changes white phase0 to1. The independent
original request comparator rejects269 cases; product source is unchanged.

Live MAIN caches requests before its frame increment. Death, first Bomb blink
and frozen Game Over/Continue checkpoints pass on all three hosts. Continue
trace now includes the cached player request; prior fields and the three real
host-file outputs remain unchanged. The frontend source consumes this cache,
including physical-row-to-display-row conversion, and both backends compile.
This establishes source integration and bounded native invariants, not a
published GUI or a complete natural route. Frozen Game Over TRAM/keyboard,
Bomb graphics and shared lifecycle palette dispatch and Quit registration→verdict→fresh OP remain.

Replay with fresh output directories only:

```sh
python3 port64/verify_player_render.py --target ../../targets/th04/main.exe --hdi ../../runtime/images/zun.hdi --exe .analysis/port64/linux-live-v1251/th04-port64-player-lifecycle-contracts --output-dir FRESH_OUTPUT
python3 port64/verify_player_render.py --target ../../targets/th04/main.exe --hdi ../../runtime/images/zun.hdi --exe .analysis/port64/ubsan-live-v1251/th04-port64-player-lifecycle-contracts --reference-dir ORIGINAL_OUTPUT --output-dir FRESH_OUTPUT
# Actual Windows: verify_player_render_windows.ps1 with fresh output,
# -ExecutableDirectory, -ReferenceDirectory and the current -SourceManifest.
python3 port64/verify_lifecycle_join.py --exe .analysis/port64/linux-live-v1251/th04-port64-live-contracts --output-dir FRESH_OUTPUT
python3 .analysis/port64/player-render-v1306/readback.py
```

Private evidence root `.analysis/port64/player-render-v1306/` retains platform
review, current source manifest, original/consumer compressed captures, actual
Windows commands/receipts, clipping control and mutation replay inputs.
`cleanup-receipt.json` records2,662,400 allocated bytes reclaimed with2,795
protected files unchanged. Superseded development captures/staged assets,
negative executable and Python caches are retired. Independently generated,
byte-readback verified request streams share immutable hardlinks. Current
original inputs, final references, pinned tools and three active caches stay.
All runs are muted; no audio backend/device is opened.

## Live Game Over frontend

v1307 joins the Game Over renderer, held input and refresh clock to ordinary
MAIN. The frontend captures its last completed indexed display before the
last-life prefix, retains graphics and a separate text plane, and consumes
scene requests synchronously. The final Continue wipe is captured before the
interrupted MAIN suffix resumes and releases this graphics owner. Discrete Esc
cannot close or advance an active Game Over scene; held sampling owns it.
Dialog/resource gates cannot intercept its keys. Game Over uses one refresh
per clock even when the suspended gameplay requested deliberate slowdown.

Actual OP options/character selection and an authored finite STD script drive
real enemy contact, not an injected hit or forced death. Two characters,
repaint-every-frame versus delayed repaint, held acknowledgement, Continue,
Esc Quit, direction-selected Quit, three consumed credits and the fourth
Game Over, and a real failed writer produce20 scenes per host. MAIN first
suspends at frame104/STD105; subsequent deaths occur at340/341,540/541,740/741.
Actor/STD/player/shared-ring state freezes during the scene. Continue commits
the separate host file before reset, reopens/checks it, resumes one suffix,
and advances STD only on the following frame. Quit remains at the pending
score-only MAINE request; registration/verdict/fresh OP are the next owner.

Original MAIN Game Over/menu/fade/input-loop instructions execute at loads1000
and2000 with each captured initial state and exact held-key timeline. The
native complete event sequence and final state agree; failed host writes
compare the original request prefix through the attempted save, with native
fail-before-reset assertions. Original TRAM gaiji/ANK/wipe/black stores execute
separately over those independently compared requests. The new score consumer
executes original relative `0AAF:6BA2..6BD4`, including its near return and calls
to original gaiji puts, using original reset digits/high score. DATA:1ECE's NUL
is asserted from the original initialized data rather than manufactured.
Each load performs280,614 text calls and1,340,784 TRAM stores.

There are322 complete indexed/TRAM/RGB displays,332,304,000 bytes per host.
GNU8.4, optimized undefined/bounds UBSan and actual Windows agree on every
byte and all151 output files. All34 contracts pass per host; the200 preceding
Game Over renderer controls also pass on current GNU/UBSan products.
105 AMD64 products bind277 files to current consumer manifest
`cf916d8658c50a70ac87d278bdaff72e924187158b724049eb1467f084fce30e`.
The independent two-load producer retains manifest
`05b9e17e7ea6194e18fa82dc3e072baa9291b631ffd5edabce684481bd360ff1`.
Later consumers verify target/data/font identity, that producer manifest, all
scenario/host output hashes and every display byte. They do not relabel old
original observations with the new candidate's manifest or claim reexecution.

Two rejected development approaches are retained. A direction pulse too close
to acknowledgement/confirmation either failed to finish or selected Continue;
the final fixture requires the intended Quit route and two released samples
at each boundary. Windows initially differed only by CRLF in82 journal files,
after its full display stream already agreed. Journals now explicitly write
LF in binary mode; comparison never normalizes away those file differences.
A private source-only omission of the score TRAM consumer is rejected in60
snapshots, first at clock114/byte257089. Product source remains unchanged by
the mutation; its source/commands/producer/difference receipts remain private.

The initial last-completed native graphics, palette and currently maintained
overlay/score text are supplied input adapters. This does not establish the
original interrupted MAIN physical page/display, full HUD, or shared lifecycle
palette behavior. CGROM and emulator RGB policy are explicit adapters; life/
bomb HUD, audio, DOS ranking I/O and process execution remain request adapters.
Real native host commits are a separate observed path. No GUI publication,
complete natural route, physical PC-98 timing/audio or DOS exact promotion
follows. Bomb pixels/shared palette and score-only MAINE remain next.

Replay into fresh directories only:

```sh
python3 port64/verify_gameover_join.py --target ../../targets/th04/main.exe --hdi ../../runtime/images/zun.hdi --font-bmp PRIVATE_FONT --exe .analysis/port64/linux-live-v1251/th04-port64 --output-dir FRESH_ORIGINAL
python3 port64/verify_gameover_join.py --target ../../targets/th04/main.exe --hdi ../../runtime/images/zun.hdi --font-bmp PRIVATE_FONT --exe .analysis/port64/ubsan-live-v1251/th04-port64 --reference-dir FRESH_ORIGINAL --output-dir FRESH_CONSUMER
# Actual Windows: verify_gameover_join_windows.ps1 with fresh output,
# -ExecutableDirectory, -ReferenceDirectory, -Hdi, -FontBitmap, -SourceManifest.
python3 .analysis/port64/gameover-join-v1307/readback.py
```

The private evidence root retains original/current consumer receipts, manifests,
compressed streams, Windows commands, negative controls and diagnostic journals.
Cleanup reclaims123,744,256 allocated bytes with3,926 protected files unchanged.
Completed independent scene files share immutable hardlinks after byte readback;
never replay a writer in place. Pinned inputs, original references, receipts and
three active caches remain. Every launch is muted and opens no audio device.

## Live Bomb graphics and shared palette

v1309 working tree, 2026-10-09: MAIN retains its completed-frame Bomb dispatch
before lifecycle increments bomb_frame. Frontend loads both BB/CDG resources,
consumes physical-scroll BB tiles or cached character draws before foreground
actors, and applies shared palette14/tone. Explicit scroll0/177 requests update
the display origin separately from the internal tile ring. Two physical pages
retain the null-background interval49..176; frame176 retains the preceding
back page while frame177 restores background ownership. Cached draws from175
are not replayed during the final fade. Every completed Bomb frame prepares
its page even when a headless consumer postpones visible repainting.

The current native black HUD-margin initialization remains an explicit adapter:
select its black palette entry before indexed retention. Full HUD is not added.
Bullet clear time is synchronized from the already updated shared bullet owner
before the Bomb render boundary, rather than retaining a stale lifecycle mirror.

`--bomb-checks DIR` uses actual OP/character selection, finite authored STD
contact and held X. Both characters exercise ordinary Bomb, the real deathbomb
window and a rejected late deathbomb followed by normal death and Bomb. Each
route runs227 Bomb frames; always-painted and deferred-paint variants yield
12 scenes and2,724 records per GNU/optimized UBSan. Repaint pairs agree on all
1,362 state inputs/outputs and126 complete capture tuples.252 snapshots each
contain pre-Bomb, post-Bomb, final foreground physical indices and full RGB
(387,072,000 raw bytes per host). GNU/UBSan journals and every capture byte agree.
All34 contracts pass per executed host;105 current AMD64 products bind284 files
with manifest a53f3772996984b7e69fd223a1e0c4a52b225d16fd9758362be8e5c7060151fd.

`verify_bomb_join.py` executes original MAIN0AAF:571A and the character/star,
RNG and circle bodies at loads1000/2000. All2,724 lifecycle records, stars,
circles, shared cursor and explicit scroll requests agree. At252 checkpoints,
original BB/fill/CDG/mono kernels agree on64,512,000 Bomb-layer indices. Final
native foreground indices independently reproduce all displayed RGB bytes.
Captured native pre-Bomb state/ring/page, resource handles, sound and scroll are
explicit adapters; this is not an independent original complete MAIN/background/
page-driver run. Physical timing, audio and whole-game routes remain unaccepted.

A source-only mutant omits the frontend character graphics consumer while
retaining real state production. The original pixel control rejects frame48
at32,16 (15 versus4). Game Over322 full displays and the score-only28 success/
failed-writer routes regress on current GNU. Current Windows AMD64 builds,
but actual Windows execution fails before PowerShell under WSL vsock. Git
index writes remain read-only. No GUI publication or historical exact promotion.

Receipts, readback, raw-byte comparison and mutation recipe are below
`.analysis/port64/bomb-join-v1309/`. Preserve final references, three live caches
and recovery patches; all replay output directories must be fresh.

```sh
python3 port64/verify_bomb_join.py --target ../../targets/th04/main.exe \
  --hdi ../../runtime/images/zun.hdi --font SUPPLIED-FONT \
  --exe .analysis/port64/linux-live-v1251/th04-port64 --output-dir NEW
# Optimized UBSan: its current executable, fresh output and --reference-dir
# pointing to the independently completed GNU reference.
python3 .analysis/port64/bomb-join-v1309/review_results.py
```

Scoped cleanup reclaims173,391,872 allocated bytes (about165MiB), retires27
prototype/mutant files and shares227 immutable score regression files. All5,118
protected file hashes remain unchanged. Cleanup recipe/receipt stays with the
final references; previous v1308 recovery patches remain intact.

## Ordinary collision-latch boundary recovery (v1445)

Original MAIN's hit BYTE at DGROUP2134:4669, load10FC, is1 before updates3078
and3284 in the attested Normal/ReimuA seed64 ordinary prefix. Fresh c0a1060
native LifeState reports0 there, while its separate collision snapshots cause
the correct next-update death. All nine pools and every other selected scalar
already agree. The first reader incorrectly used resident48 (end_sequence37h)
for misses; the accepted reader uses49/50 and guards the initial layout.

main_state.cpp now aggregates the existing pending-collision owners at both
the player-consumption boundary and the completed collision/render boundary.
Lifecycle's visible hit latch therefore agrees before the next update without
changing the two deaths or any actor records. This is a maintained model change,
not a trace-field substitution or original guest-state write.

Source8a2092b has556 maintained inputs, manifest49984d82. Separate fresh GNU85-
program and optimized UBSan full-core/ordinary-tracer builds agree at3997
pre-update/prefix boundaries on21 fields, complete LCG/ring bytes and exact
post-initialization draw counts. Nine complete pools compare3996 updates,
including inactive slots and spare bytes. Only enemy script identifiers use
the existing proved STD-relative address translation. End state is lives4,
misses2. Both variants produce identical state and pool streams. The original
complete7547-record source stream is drained through CRC/metadata validation
after selecting this3996-update extent.

The new trace has its own TH04OP1 pool header and P prefix marker, never a
synthetic Demo terminal. Explicit seed/options/assets and consumed inputs
initialize a native MAIN component through ordinary application APIs; no
natural native OP input timing is claimed. The cold predecessor remains an
executed negative with exactly the two hit differences and equal pools.
Seven actual reader counterexamples reject missing/duplicate boundaries,
fake Demo terminal, cleared hit, wrong resident interpretation, changed RNG
count and a changed inactive custom slot. Four complete old/new native Demo
state streams match at15988 boundaries; this is a regression, not renewed
original-DOS Demo/pixel acceptance.

Replay: DOS-root `.analysis/reconstruction/probes/native-recovery-v1445/`.
Fresh checkout: DOS-root `.analysis/native/port64-recovery-v1445/`.
Native build paths: `.analysis/port64/ordinary-v1445/{gnu,ubsan}/`.
Use port64/verify_ordinary_state.py with --dos-root, --original, --exe and a
fresh --output-dir. Native CI354/82 GNU CTests pass; actual root MAIN database
attestation passes. A fixed reference-tree symlink is used only for CI's
Tupfile Oracle, after compilation. Existing reference documentation edits
are retained. Missing historical native worktrees are not restored or restamped.

Other globals, ordinary dialogue/Boss/Game Over/Continue, natural process
timing, complete pictures, campaigns, Windows and historical exactness remain
outside this result. Continue source recovery and the original/native comparison.

Verified retention retires742 owned files into619 content blobs, releasing
245.527 MiB net after a13.660 MiB archive. Full SHA/CRC/mode/nsmtime checks
and3087 protected hashes pass. Restored four ordinary component executables
and both native Demo executables reproduce complete retained outputs and
pool digests; nine owned aliases are verified and retired again. Six borrowed
original aliases return to their older archived state and are not counted as
new cleanup. Current GNU programs/cache and selected UBSan programs remain.
The first journal bound a still-empty redirected log and correctly rejects;
its bytes and reader remain unchanged. A distinct retention-final.json and
recover_final.py bind the closed terminal log. replay_restored_v2.py also
restores borrowed original aliases and requires the identical first replay
report, so the recovery is repeatable. Historical missing94 files remain open.


## Actual Stage1 to Stage2 initialization ownership (v1457)

Original/reconstructed DOS returns from gameplay at9837, after the earlier
actor9836 stop. Original0AAF:0207 at9836 has quit0;0AAF:0081 at9837 has quit2.
Both initialize Stage2 in the same process and reset its local frame to0.
LCG calls rise354 to707 during actual initialization; ring calls remain4698.
First MAIN initialization consumed353 LCG calls, the existing native relative
counter origin. Ring counts accumulate native per-fill counters. The fixture
assigns no gameplay state, RNG value, clock phase or stage/frame.

The first actual native producer has601 differing point-number snapshots and
1201 differing Boss query records across init and600 complete Stage2 updates.
Original0AAF:7470/7473/7476 supplies DGROUP9634 and640 dwords to the clear
helper. Native stage initialization now clears all400 records, including
inactive bytes, and separately resets allocation cursors. The external alive
list retains its distinct update ownership. The existing session contract
seeds inactive bytes and checks that clear/preservation split. Kurumi setup
was correct; `boss_snapshot()` now selects the prepared optional stage owner
before activation instead of returning stale Orange.

The optional `stage-epoch-plan.txt` fixture advances the real scene through
its actual request/resource-install/init boundaries and600 Stage2 updates.
`stage_epoch_trace.inl` observes actual owners; it does not replace simulation
or rendering. Initial565-file diagnostic build omitted this new include from
PORT_FILES. It remains diagnostic; final acceptance uses a new cold566-file
187b574f closure that includes it.

Fresh GNU87 programs/83CTests and optimized UBSan2 pass. Both actual programs
match1203 selected bridge/init/actor-score records, nine complete pools at init
and600 updates, consumed inputs, homing, Boss fields and continuous RNG. Their
complete Stage2 state/pool wires are identical. Sixteen volatile post-reset
key snapshots remain measured separately. DOS still fails18 post-reset input
and1807 raw-GDC snapshots despite equal9pools/22states/38configured video regions.

Both current programs reproduce the distinct v1455 elapsed fixture:9835
selected updates, all59 complete RGB/TRAM pairs and177 full observations,
with real input/homing/Boss/pools/Continue/save/title/popup gates. Four borrowed
historical aliases verify SHA/mode/nsmtime before retirement, without new
cleanup credit. Stage2 pictures, natural loader/UI/CPU timing, full original
campaigns, NP2, Windows, physical input/audio/rendering and exactness remain open.
Historical default-logical failures remain unresolved.

Current programs/cache: `.analysis/port64/stage-epoch-v1457-final/{gnu,ubsan}`.
Root-owned proof bundle, privately linked here:
`.analysis/reconstruction/probes/dos-stage2-boundary-v1457/`.
Use `native-final-result.json`, `public-final-{gnu,ubsan}` and
`legacy-regressions/receipt.json`. The root's maintained boundary tools replay
actual original/source/native observations; keep every failed vector.


## Stage2 boundary and native reset retention (v1457)

Verified retention archives2732 owned generated files into1676 content blobs,
releasing1385.176 MiB after archive, gzip and both journal files. All28575
protected hashes verify, including all24890 parent identities. Actual recovery
restores12 owned capture aliases and the pre-fix executable, executes it and
both retained repaired GNU/UBSan programs from fresh input-only fixtures, then
replays the frozen DOS/native consumers. The old native failure remains false;
both repaired vectors remain true. All13 restored aliases verify SHA, size,
mode and nsmtime before retirement. Four borrowed v1455 aliases were separately
verified and retired without cleanup credit. Current final GNU/cache/UBSan
cores and all complete compressed original evidence remain live. New backing
paths are immutable private files; older journals and missing-file gaps remain.

The root-owned bundle contains retention/retention.json, recover.py and
replay_restored.py. Every replay uses fresh output names; old journals,
initial source-list gap evidence and failed vectors remain unchanged.


## Stage2 Midboss battle through3200 (v1458)

Original/reconstructed DOS now complete3200 Stage2 updates in the same process,
including Midboss activation at actor2601 and600 battle updates. The NPC remains
active at3200 withHP100/phase1/frame39; defeat is not accepted. Comparable loop
fields/7787 ordered RNG calls,9 full pools/22 states and38 configured video
regions agree over9607 bridge/actor/score/loop snapshots. Aggregate remainsfalse
for248 post-reset input and9607 raw-GDC records. Older18 and302/312 failures
retain their own captures.

Maintained native closure566/3747e671 adds direct22-byte Midboss/active telemetry
and permits declared16-bit diagnostic extents. No gameplay repair was needed
in this span. ColdGNU87 programs/83CTests and optimizedUBSan2 match6403 selected
records and3201 complete9-pool snapshots,input/homing/Boss/Midboss/RNG;both also
reproduce old9835 selectedupdates and59 RGB/TRAM elapsed pairs/177 observations.
Native116 volatile post-reset samples remain separately measured. Stage2 native
pictures,natural clocks,full NPC defeat/campaigns,NP2/Windows remainopen.

The initial reader kept a newly disabled watchpoint per checkpoint. A controlled
stop at1709 remainsincomplete. The new bounded collector reuses7 watchpoints;
actual original/source maxima are10 total including3 baseline. A standalone
public-class3200-switch test and six resource mutations pass;ten new actual
capture-data negatives also reject. Full CFG/SCR bytes match with16-bit score
checksums;Continue changes section1. Preserve the oldfailedcapture/source.
Current programs: native `.analysis/port64/stage2-midboss-v1458-final/{gnu,ubsan}`.
Current root-owned bundle: `.analysis/reconstruction/probes/dos-stage2-midboss-v1458/`.
Recovery/retention is closed below. Next extend through the actual Midboss reset;
do not infer death from a fixed stop or copy target state into native.


### Closed3200 recovery

Archive311 owned generated files into125 content blobs,
releasing1288.430 MiB after archive, gzip and both journal files. All32386
protected hashes verify, including28575 parent identities, all51 prior
finish.late_protected entries and the old finish identity. Actual recovery
restores17 owned aliases (12 complete-capture aliases,4 incomplete-capture
aliases and the private executable), executes allthree pinned native programs
from fresh input-only fixtures, and replays frozen DOS/native consumers.
Both actual standalone GDB probes reproduce growth versus bounded caching;
the controlled original still rejects. Every restored alias verifies SHA,
size,mode and nsmtime before retirement. Earlier borrowed13 reader-control
aliases and4 elapsed-fixture aliases receive no cleanup credit. Keep current
final GNU/cache/UBSan cores and all compressed complete/incomplete evidence.

The fixed cached reader has a real public-class GDB switch probe;the original
per-checkpoint creation pattern remains a retained negative. Midboss defeat
and new native pictures are open;do not reinterpret the3200 boundary as death.


## Observed Stage2 Midboss defeat and reset (v1459)

Original and reconstructed DOS now complete 3500 Stage2 updates in the same
process. The observed Midboss activates at 2601, enters defeat at 3349,
reaches phase3/HP0 at 3413 and resets at 3414; 86 further updates retain
its inactive raw state. All comparable loop fields, 7861 ordered RNG calls
(707 LCG/7154 ring), nine complete pools, 22 states and 38 configured video
regions agree across 10507 bridge/actor/score/loop snapshots. Each side binds its
own MZ/MAP/CS/DS, opcode, DGROUP, video and full conventional-memory witnesses.
Aggregate remains false for 174 post-reset key and 10507 raw-GDC records.
Older v1458 248/9607, v1457 18/1807 and v1456 302/312/9836 failures remain separate.
These are MAIN replacements with original OP/MAINE/ZUN/assets.

Retained native 8cd826e telemetry and complete 566-file/3747e671 cold programs
match 7003 selected records and 3501 full nine-pool snapshots in both GNU and
optimized UBSan. Consumed inputs, homing, Boss/Midboss state and continuous RNG
agree; 144 volatile post-reset key samples are measured separately. No gameplay
repair was needed. Existing cold GNU 87 programs/83 CTests and UBSan2 remain the
producers. The separate v1458 replay of 9835 selected updates and 59 full RGB/TRAM
elapsed pairs remains valid for these unchanged programs. This new component
accepts the observed Midboss lifecycle, not native Stage2 pictures or natural
OP/loader/UI/CPU clocks.

The lifecycle gate requires actual activation, attack, nonpositive HP, defeat,
exit, reset and at least 64 post-reset updates. Original reset13A9:642C and
source reset157C:661B each have independently decoded callback/active/HP stores
and their own far relocation. Full-memory witnesses immediately around each
transition verify the near invalidate/render and far update null callbacks;
addresses are never normalized across executables. Thirteen lifecycle/MZ and
ten actual original/source callback mutations reject. The bounded debugger
still uses seven cached points, with ten total registered objects on each side.
Complete initial/final CFG/SCR bytes match, all ten full 16-bit score checksums
validate, and Continue changes decoded section1.

Current root-owned bundle: `.analysis/reconstruction/probes/dos-midboss-reset-v1459/`.
Use paired-{gnu,ubsan}, lifecycle-{gnu,ubsan}, result.json, files.json and
reset-callback-controls.json. Programs stay in native
`.analysis/port64/stage2-midboss-v1458-final/{gnu,ubsan}`.

| Owner | Original MAIN | Reconstructed MAIN |
| --- | --- | --- |
| Reset function | 13A9:642C, file1B6BC | 157C:661B, file1D7DB |
| Midboss22 | DGROUP2134:53B4 | DGROUP242E:8CBA |
| Active | DGROUP2134:46B2 | DGROUP242E:8CD0 |
| Invalidate/render near callbacks | 46B4/46BA | 8CD2/8CD8 |
| Update far callback | 46B6 | 8CD4 |
| Own near/far null functions | 0AAF:11BE/11C0 | 0708:1002/1001 |

The first lifecycle consumer used the ordinary profile instead of the attested
full profile and rejected with KeyError(main_path). Its failed pipeline/logs and
reader-profile-failure.json remain separate. The corrected reader and complete
GNU/UBSan reruns establish this gate; no failed result was restamped.

Both actual loads are10FC. The reset immediate far segment is relocated by each
MZ at13A9:643F /157C:662E. Read-back pointers use loaded segment1BAB /1804.
These are target and runtime observations, distinct from source names or native
host pointers. Native22-byte NPC/active telemetry agrees but makes no host
function-address equivalence claim.

```sh
python3 scripts/probes/compare_th04_stage_boundary.py \
  --stage2-updates 3500 --require-midboss --require-bounded-watchpoints \
  --original .analysis/runtime/candidates/dos-midboss-reset-v1459-original \
  --candidate .analysis/runtime/candidates/dos-midboss-reset-v1459-candidate \
  --native-root .analysis/native/port64-recovery-v1445 \
  --native-frontend .analysis/reconstruction/probes/dos-midboss-reset-v1459/native-gnu/frontend \
  --native-receipt .analysis/reconstruction/probes/dos-midboss-reset-v1459/native-gnu/receipt.json \
  --output-dir .analysis/NEW-stage2-paired
python3 scripts/probes/compare_th04_midboss_reset.py \
  --stage2-updates 3500 \
  --original .analysis/runtime/candidates/dos-midboss-reset-v1459-original \
  --candidate .analysis/runtime/candidates/dos-midboss-reset-v1459-candidate \
  --paired-comparison .analysis/NEW-stage2-paired/native-comparison.json \
  --native-frontend .analysis/reconstruction/probes/dos-midboss-reset-v1459/native-gnu/frontend \
  --native-receipt .analysis/reconstruction/probes/dos-midboss-reset-v1459/native-gnu/receipt.json \
  --output .analysis/NEW-midboss-reset.json
```

Restore journal-owned aliases before strict readers, using recover.py --restore
--path EXACT, and verify/retire them afterward. Paired reduction exits0 when it
finishes; the DOS aggregate flag remainsfalse. Native/lifecycle success cannot
waive the failed key/raw-GDC vector. Runtime observations use the pinned
DOSBox-X6e1a6e70; Japanese target canonicality remainscandidate-local-attested.
