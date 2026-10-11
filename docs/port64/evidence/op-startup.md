# OP startup state and frontend ownership

## PMD service and counted startup waits (v1401)

The native startup now services PMD at its next live timer deadline while
waiting for a measure. Logo waits consume the inherited unsigned Count1 and
clear it afterwards; ordinary frame delays clear Count1 before waiting. The
inactive music fallback also clears Count1 for its zero-frame delay. These
orders follow the retained original OP wait observations from v1397.

`Scene::advance_elapsed()` connects those waits to the frontend's raster clock
and sound timeline. `ClockedPlayer::until_timer()` preserves fractional clock
time when selecting the next service point. Resource work, startup waits and
later refreshes share the raster phase; clearing Count1 leaves Count2 running.
The existing logical-step interface remains available for component callers.

The 512-file producer has manifest
`60cf449182995f0010c8d36513afa55411113aeddc10291aef9e98374409c6e8`.
Its cold GNU build produces 72 programs and passes 70 CTests; optimized UBSan
produces nine selected programs and passes six contracts. Three compiled
mutations reject clearing before a Logo wait, omitting the inactive zero-delay
clear, and servicing PMD only once per refresh. Deadline and elapsed-partition
checks cover the restored functions. The mutation readiness clock is synthetic;
original ownership comes from the separately retained OP observations.

Private receipts are under `.analysis/port64/native-startup-waits-v1401/`.
`current-verification.json` verifies all producer/current source pairs,
81 program hashes and saved test outcomes. Whole-picture and physical timing
comparisons retain their earlier scope.

v1346 implements the one-time ZUNsoft logo/fireworks and the OP title sequence.
This closes the bounded control corpus and muted frontend ownership below.
v1347 independently checks every pixel in the recorded corpus below. Full
startup integration, physical timing/audio, natural complete routes and a newly
delivered GUI remain open. Historical DOS acceptance is unchanged.
Targets retain candidate-local-attested provenance.

## Independent startup pixels (v1347)

The producer re-executes all fifteen callers at loads1000/2000 and preserves
v1346's complete147,830rows after removing its additional raw-palette reads.
It executes unchanged OP0000:2B66..2F0B clipped SUPER, including the shared
2B60..2B65 early-return tail. Original code/data reset before each draw retains
self-modifying kernel ownership. Pattern staging, clip bounds and GRCG planar
shadow are explicit adapters. Each of23,600 distinct stencils runs at both
loads on zero and patterned sixteen-color backgrounds:94,400 kernel calls.
Fully clipped sprites may correctly perform zero writes.

Every refresh, including initial and completion frames, captures both640x400
indexed pages,48 raw-RGB bytes,48 four-bit DAC bytes and768,000 shown-RGB
bytes. All5,879frames/7,525,684,384uncompressed bytes agree with GNU8, optimized
UBSan and actual Windows. Complete stream SHA256:
`920d29c62071875a47351063d179ec8820ff007e0558dac3aa334b7d22b94ac6`.
The reference separately agrees with4,311 original palette/access/shown
checkpoints. Additional reads observe the original45-component clear and BFNT
raw palette publication; native palette formulas do not produce those reads.

PI decoding uses the separately frozen v1346 decoder. Title slices are640x108
and overwrite only the band beginning atY38, retaining the page's remaining
white area. PI/header lifetime, page copy/clear/fill/background, BFNT staging,
refresh/input/measure and sound calls remain declared adapters. Four-bit DAC
expansion is the existing emulator-source corroborated display mapping;
this corpus is not physical video, chip accuracy or complete original OP.
Actual Windows redirects the binary BaseStream directly to gzip, asserts
AMD64 PE32+ and hashes the full decompressed stream with its exact length.
There is no CRT text normalization in the pixel comparison.

Four source-only renderer variants all preserve the prior147,830 control
rows, but fail pixels: self-page copy atframe0/offset0; clearing the page
before a108-row slice atframe69/offset256000; a one-pixel sprite shift at
frame352/offset370099; and RGB from the accessed page atframe69/offset586793.
Each rejection has a complete mismatching frame, rather than a crash verdict.
The first variant compile failed due to a missing LCG translation unit; its
log remains diagnostic, and the corrected explicit-input builds are retained.

Only two public verifiers and their manifest entries changed.461 maintained
verification inputs have manifest
`3af8cef1ce57711a8291548646902831a665cc910fb124dcd4f3af82ea27fb4c`.
All C++/headers/CMake inputs and195 executable hashes remain unchanged; their
v1346 producer stays459inputs/
`b62c3026fcfa814ccce48906485e6c191c51c760486455421b04fee3c2aaf61f`.
`source-bridge-v1.json` attests this distinction. Neither producer nor consumer
receipts are restamped. Both repository CIs pass; no DOS unit is promoted.

Private scope: `.analysis/port64/startup-pixels-v1347/`. The successful frozen
producer is named `original-dev-v1` and retains that recorded path. Consumers
are `consumer-linux-v1`, `consumer-ubsan-v1`, and `windows-receipt-v1.json`;
`aggregate-receipt-v1.json` closes identities. Source archives, complete
compressed streams and failed/negative observations stay private.

```sh
python3 port64/verify_op_startup_pixels.py --target TARGET --decoded-dir DECODED \
  --hdi HDI --decoder FROZEN_DECODER --control-reference V1346_ORIGINAL \
  --output FRESH_ORIGINAL
python3 port64/verify_op_startup_pixels.py --reference ORIGINAL \
  --product-profile V1346_PRODUCTS --exe STARTUP_CONTRACT --output FRESH_CONSUMER
powershell.exe -NoProfile -ExecutionPolicy Bypass \
  -File port64/verify_startup_pixels_windows.ps1 -PlanFile PLAN
```

The Windows plan binds binary/fixtures/assets/script hashes, original receipt,
separate verifier/product manifests, expected complete stream SHA256 and frame
count/size. Regenerate path fields in a fresh owned stage before replay; never
reuse the retired writer path. All runs stay muted without an audio backend.

## Original execution and adapters (v1346)

The producer executes the unchanged decoded OP at load segments 1000 and 2000:

- OP 0A74:0CB6..0CE2: resident logo decision and demo-dependent title call;
- OP 0A74:1305..1763: pyro spawn/update, palette helper and logo;
- OP 0A74:2592..281D: title sequence;
- OP 0000:204E..2077: process-local LCG;
- OP 0DA1:01A8..01C3: signed fixed-point polar calculation;
- OP 0000:0622..06A2 and 1DE0..1E48: fades and analog palette/DAC arithmetic.

PI decode/load/free, BFNT registration, indexed page/background consumers,
input samples, refresh and measure readiness, and sound calls are guarded
adapters. The shared original CPU engine is not a physical PC-98 emulator.
The original module, 804 relocation sites, packed input, HDI, decoder, engine
and producer source archive have recorded identities. The active OP database
was independently re-attested from the root worktree.

Fifteen fixtures cover title with/without demo BGM, two LCG seeds, no skip,
first-frame skip, an unsampled odd-refresh pulse, later skips, active measure
readiness, and nonzero retained raw palettes. GNU8, optimized UBSan and actual
Windows compare all 147,830 state/request text rows, including every serialized
256-slot pyro array, LCG, raw palette, DAC and access/shown page state at wait
boundaries. Windows CRT CRLF is normalized to LF; this is a semantic text-row
comparison, not historical raw-byte exactness.

Normal logo+title is 533 refreshes without a measure wait; title alone is 175.
The first-sample skip consumes 277 refreshes, fading over the original two-
refresh logo frames. An odd-refresh key pulse is not sampled. Active frontend
waits query the installed driver's real song measure, rather than a fixed logo
clock. BFNT registration changes raw RGB without showing the DAC. The title
still uses the retained PI header palette after freeing its pixel allocation.

## Actual frontend and storage boundary

Three driver profiles each run all nine BGM/SE choices plus missing and bad
configuration cases. A second invocation starts a separate host process and
reopens its own score/configuration files. Each of GNU8, optimized UBSan and
actual Windows has 336 equal capture files across 66 settings/restarts; the
final physical files also agree. All launches are muted, with no audio device
or backend. Captured mixed PCM and indexed/RGB frames establish host
consistency; they are not independent physical-chip or complete-pixel Oracles.

The first BGM/SE case per driver uses an authored legal finite STD. Real
ordinary contact reaches Game Over, Quit enters score-only MAINE, registration
and verdict return to fresh OP, and that OP runs its unskippable 175-refresh
title. No hit/life/score/MAINE completion is forced. This bounded child route
is not a natural six-stage run.

Configuration loads before setup/startup; score-file construction and scan
wait until the title returns. The logo flag publishes at logo completion,
while the final process LCG is transferred before score recreation consumes
it. Fresh OP reloads the physical configuration before its title, keeps the
resident PMD and its clock, skips the already-shown logo and resets the local
LCG. An independent process restart displays the logo again. Repaint does not
consume refreshes, LCG or PMD time.

A developmental frontend run exposed a stale MAINE screen during configuration
reload. The retained GDB backtrace names render -> enable_configuration ->
restore_fresh_op. OP now publishes its screen before that load can repaint.
Other developmental failures include a malformed authored STD and a producer
cancelled because aggregate linking replaced its decoder input. Those logs are
diagnostic failures, not accepted producers. The final original run uses a
separately frozen decoder copy and closes its source/input hashes unchanged.

Four source-only variants are rejected: immediate skip fade, wrong pyro speed
modulus, incorrect high-tone palette rounding, and wrong BFNT load order.
Resident service/frontend regressions retain all three profiles and their
prior Music Room/MAIN/declared registration-child limits on GNU and UBSan.
All 64 contracts pass on GNU, UBSan and actual Windows.

## Identity and replay

459 maintained inputs bind 195 AMD64 products (65 per host).
Source manifest: `b62c3026fcfa814ccce48906485e6c191c51c760486455421b04fee3c2aaf61f`.
Private scope: `.analysis/port64/startup-v1346/` in the native worktree.

```sh
python3 port64/verify_op_startup.py --target TARGET --decoded-dir DECODED \
  --hdi HDI --decoder FROZEN_DECODER --output FRESH_ORIGINAL
python3 port64/verify_op_startup.py --reference ORIGINAL \
  --exe STARTUP_CONTRACT --output FRESH_CONSUMER
python3 port64/verify_startup_join.py --hdi HDI --font FONT --rom ROM \
  --original-reference ORIGINAL --binary GNU --binary UBSAN --output FRESH
```

Final receipts are `original-final-v2/receipt.json`,
`control-{linux,ubsan}-final-v1/receipt.json`, `frontend-final-v1/receipt.json`,
`windows-{component,contracts,frontend}-receipt.json`,
`windows-save-readback.json`, `counterproofs-final-v1/receipt.json`,
`resident-regression-final-v1/receipt.json` and `product-profile-final-v1.json`.
Producer/consumer archives and frozen decoder remain separate. Actual Windows
uses the checked-in `verify_windows_current.ps1` with retained typed plans;
the private startup text consumer/plan are retained and hash-bound as inputs.
Cleanup journals and recovery archives supply the retired Windows stage and
experimental programs; replay always uses fresh destinations.

## Remaining gates

The recorded independent clipped SUPER/GRCG pixel corpus is closed; broaden setup/fresh OP failure controls and original complete startup
integration. Full natural Normal/Extra routes, audio usage/remaining owners,
host refresh/input/slowdown/Lunatic timing and GUI publication remain. This
batch does not resolve PPS/external ADPCM or prove unused ownership from the
absence of bank files in the supplied archives.

Terminal retention verifies 11 archives/2121 protected hashes, retires
2575 files and shares 886 immutable equal captures. Measured reclamation
is 1447223296 allocated bytes. The source/program/cache/input identities
remain unchanged; native objects/static libraries are regenerated by CMake.

## Demo configuration and active measure waits (v1391)

The actual Demo route now enables the existing configuration owner before
registration/startup. All nine OP/MAIN requested option sets equal the incoming
physical CFG, independently checked against the raw file. Four separately
named muted driver profiles pass under GNU and optimized UBSan: one resident
Logo, four pre-Demo titles and fresh final OP ready. Measure request to first
SUPER_load spans zero refreshes for none and 94 for each active provider;
first MAIN is refresh 1,193 versus 1,287. This is native event evidence, not
original PMD board/measure/audio pairing. The bypass negative and repeated
original clocks are indexed in [demo evidence](demo.md). Do not encode this
span as a constant or select a driver to fit original RGB phase.


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

## v1400 shared DOS lifecycle correction

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
