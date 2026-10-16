# TH04 native 64-bit bring-up

## Ordinary dialogue/player boundary (v1447)

Source a7f9bea removes v1446's incorrect Stage1 input latch. Original checkpoints
show STD dialogue before player_update: frame6548's loop sample is Shot20h,
while the actual player entry sees Enter2000h. The verifier now requires original
instruction-fetch/caller/memory evidence for every blocking frame. Loop and
player inputs have separate reference boundaries.

```sh
python3 port64/verify_ordinary_state.py --frontend --updates 7500 \
  --dos-root DOS_CHECKOUT --original RESTORED_CHECKPOINT_CAPTURE \
  --exe CURRENT_GAME --output-dir FRESH_OUTPUT
```

Create that original with the DOS checkout's capture_th04_dos_ordinary_prefix.py
using --dialog-checkpoints --dialog-at-frame 6548 --end-after 7501 and an attested
--video-layout. The standard capture publishes dialog-checkpoint-sources.json.
The verifier binds it automatically; an explicitly frozen older observer may
supply --dialog-observer-profile FILE. A blocked capture without player-entry
evidence rejects. The first6549-stop capture remains inadmissible to the generic
keyboard reader because it ends before the gameplay-Shot restoration.

GNU/UBSan7500 updates match actual player input,21 state/RNG fields,nine full
pools and four Boss blocks. One pre-script state/pool checkpoint and141312
programmed-GDC playfield graphics pixels also match. Fresh game translation
units link unchanged attested cold cores; this is not a full new cold-core build.
TRAM/full pictures/scanout, Game Over/Continue and whole-game/Windows remain open.
The old v1446 state/pool/Boss receipts remain; their player-input inference is
withdrawn. See [current handoff](../docs/RE_HANDOFF.md).

## Ordinary collision-latch recovery (v1445)

Current source8a2092b publishes collision hits before completed-frame observers.
Fresh GNU and optimized UBSan agree with original DOS on3996 ordinary Normal
ReimuA updates,21 fields/LCG-ring state and counts, and nine complete actor pools,
including two natural deaths/respawns. GNU builds85 programs and passes82 CTests;
native CI354 passes. This is an explicitly initialized MAIN component, not
natural OP timing, full pictures or a complete game comparison.

Build with `cmake -S port64 -B .analysis/port64/current -DCMAKE_BUILD_TYPE=Release`
and `cmake --build .analysis/port64/current --parallel 1`. The target
`th04-port64-ordinary-state-trace` and `port64/verify_ordinary_state.py` replay
the component from a current DOS checkout's attested original route. Restore
that capture's image/raw aliases before verification. Use fresh output paths.
The old missing frozen worktrees remain a historical replay gap; new source,
builds and receipts have separate identities. See [current handoff](../docs/RE_HANDOFF.md).

## Native OP palette VSync wait recovery (v1407)

Fixed native base48e05da now separates palette VSYNC_WAIT from frame_delay.
Original decoded OP0000:2648..266D (38 bytes) branches on DGROUP0856:
installed IRQ snapshots Count1 at1AC6 and waits for any change; otherwise it
finishes the current GDC blank and waits for the next rising blank. Neither
path clears Count1 or Count2 (1AC8). Native startup palette fades retain
both words; frame_delay and Logo retain their different clear orders.
Original fade helpers0000:0622..0664 and0666..06A3 call2648 before
the palette loop and once per speed-loop iteration (0632/0643/0676/0687).

Cold producer524/d9edcdf5 passes77 GNU programs/75 CTests and13 optimized
UBSan programs/10 focused contracts. Each compiler passes32 unchanged-original
controls at load1000/3333 and432 independent ideal raster/cadence vectors
(1296 waits), including FFFF-to-zero and status/IRQ edge separation.
Count1/GDC inputs are explicit consumer stimuli, not measured physical IRQs.
The real48e05da startup predecessor fails the new counter-retention contract.
Eight fresh muted startup/fourDemo/freshOP routes retain all129 output hashes
per profile from frozen v1404; each passes15988 original selected-state boundaries.

The first cold build failed the valid-final-edge overflow contract (74/75).
Its source/program/logs remain frozen; v2 repairs exhaustion and passes.
This batch changes native wait/startup source, with no new DOS product or
historical exact promotion. The older25-byte compiler-service observation describes only the polling
producer, not the complete original function. Shared DOS vsync_wait.cpp still implements only
port polling; recover its installed-owner branch in a separate cold replay.
Other native scene wait adapters, CPU/loading/ISR costs, complete pictures,
Boss/death/process, second-emulator and Windows acceptance remain open.

Review branch: review/native-gdc-poll-v1407. Replay index:
.analysis/reconstruction/probes/native-gdc-poll-v1407/; native receipts:
.analysis/port64/native-gdc-poll-v1407-v2/. Original extent SHA-256:
989ba1d57373892c48f460097161f08d5391388535059d007327fda0f4e45b20.
Focused commands are in validate.py/focused.json; original/native reader:
port64/verify_gdc_poll.py. Recovery reader: verify_retention.py
(--restore/--prefix for owned archived paths). Frozen v1404's736-file closure
and3179-path/1489-blob archive pass without modifying old receipts.

Verified archive retirement reclaims502.05 MiB net from this batch's
successful/failed build intermediates, nonselected programs and duplicate
capture outputs. Full path/hash/size/mode/nsmtime, CRC, every blob and protected
proof are checked before deletion. Source freezes, selected programs, complete
original controls/native vectors and failure evidence remain live.
Both isolated full CI gates pass (root451/native345), with ledgers and diff checks.
Pinned private targets/calibration pass; isolated private Ghidra/JDK checks skip,
while original OP database was actually attested in root before recovery.
Source-backed owned post-CI caches reclaim another16.35 MiB; this batch
reclaims518.40 MiB net, disjoint from prior frozen cleanup.

Goal active; CPU1/nice19 serial and muted; no Windows GUI/focus/keys/audio.

## Earlier frozen milestones

Work remains active. The v1389 analog DAC repair gives 40/40 complete raw RGB
samples under supplied original display-event timing, and 37/40 with default
timing; three blink-phase cases remain. Full physical scanout and broader
route acceptance remain open. See the current handoff for evidence and recovery.

 v1375 pairs all four ordinary demos with original DOS:
nine complete actor/effect pools (24,952 record bytes at each of 15,984 updates)
and 15,988 selected input/score/player/RNG/count boundaries agree on GNU/UBSan.
A missing Midboss yellow bonus consumer is repaired; item records preserve spare
bytes and sprite WORDs. The source mutation leaves selected state equal but
rejects the point-number pool at the original four first differences. GNU's
70 programs pass 68 CTests; eight pool-reader controls and frozen reader replay
pass. This accepts bundled-demo pool state; pictures, other globals, ordinary
Boss/death/process routes and current Windows execution remain open. See
[current handoff](../docs/RE_HANDOFF.md) and
[demo evidence](../docs/port64/evidence/demo.md).

v1376 exercises that selected state through actual idle OP→four demos→OP and
repairs the missing yellow DEMO PLAY text and blink attribute. GNU/optimized
UBSan compare40 complete label spans around/after fade-in. `--demo-pictures DIR` and `verify_demo_pictures.py`
retain full indexed/RGB/TRAM displays, qualify different original/native seams
and explicitly leave whole-picture/physical blink/scanout acceptance open.

Older milestone paragraphs below retain their own producers and scope.

v1347 closes the independent recorded startup pixel corpus. Fifteen two-load
original cases produce5,879 complete two-page/raw-palette/DAC/shown-RGB frames;
GNU8, optimized UBSan and actual Windows agree.94,400 clipped SUPER executions
and4,311 original palette/page checkpoints constrain the explicit adapters.
Four renderer mutants pass all prior147,830state/request rows but fail pixels.
Only verifiers changed:461 inputs have manifest
`3af8cef1ce57711a8291548646902831a665cc910fb124dcd4f3af82ea27fb4c`;
195 unchanged programs retain their459-input v1346 producer
`b62c3026fcfa814ccce48906485e6c191c51c760486455421b04fee3c2aaf61f`.
Receipts: `.analysis/port64/startup-pixels-v1347/`;
[ownership and replay](../docs/port64/evidence/op-startup.md).
Full startup integration, PPS/external ADPCM, complete natural routes, host
timing/performance and a current GUI remain open. All runs stay muted;
no physical video/chip or historical exactness is accepted.


v1346 joins original logo/fireworks/title control and muted frontend startup.
15 two-load cases/147,830 complete state/request rows agree on GNU8,
optimized UBSan and actual Windows; four wrong source variants reject.
Three driver profiles by11 settings and separate-process restarts produce336
matching files per host; final physical saves agree. A declared finite STD
reaches ordinary Game Over, MAINE and fresh OP without forced lifecycle state.
459 inputs bind195 AMD64 programs;64 contracts pass per host. Independent
startup pixels/full startup integration, PPS/external ADPCM, natural routes,
host timing and new GUI delivery remain open. No DOS exactness is promoted.

Current v1346 source manifest:
`b62c3026fcfa814ccce48906485e6c191c51c760486455421b04fee3c2aaf61f`.
Receipts: native `.analysis/port64/startup-v1346/`;
[ownership and replay](../docs/port64/evidence/op-startup.md).

v1345 recovers FM3 C6 subtrack activation, CF slot/voice ownership,
C7/C8 detunes, special pitch and shared mode on all three drivers. FM26
aliases D-F and restores all four shared tracks after effects;86/B2 append
three tracks.66 distinct two-PSP cases/55,836 complete rows agree on GNU8,
optimized UBSan and actual Windows. Nine source-only variants reject; the
initial pitch-clipped LFO control remains inconclusive in its own receipt.
453 maintained inputs bind192 AMD64 products;63 contracts pass per host.
GNU/UBSan each regress783,936 earlier complete rows, resident services/PCM
and muted frontends; Windows regresses resident/three frontend profiles.
PPS/external ADPCM, full startup, natural routes and host timing remain.
No new GUI, physical chip accuracy or historical exactness is accepted.

v1345 source manifest: `1689400f6154f6ef377d41357a802a1d6a75129e19449068c81a431e26ef50b0`.
Receipts: native `.analysis/port64/fm3-recovery-v1345/`; ownership, distinct
case accounting, adapter limits and replay: [FM3 evidence](../docs/port64/evidence/pmd-fm3.md). Older producer and
consumer identities remain unchanged.

v1344 recovers primary FM B6 feedback and B8 operator total-level commands,
including byte rotation/wrap, masked software state and disabled FM26 parts.
Three original drivers at PSP1000/2000 yield 84 cases/101,448 complete rows;
GNU8, optimized UBSan and actual Windows agree. Five source-only variants reject;
two initially inconclusive controls become discriminating with corner inputs.
451 maintained inputs bind 189 AMD64 products; all 62 contracts pass per host.
GNU/UBSan also regress 602,448 earlier musical/effect rows, resident services
and bounded muted frontend captures. FM3 extra subtracks/slot ownership/special
pitch, PPS/external ADPCM, full startup, natural routes and host timing remain.
No new GUI or historical exactness is accepted; all runs remain muted.

v1344 source manifest: `81260aeae14b62a1f175844a52a00bb25f122fa938f45524a19b103fb718912b`.
Receipts: native `.analysis/port64/pmd-fm3-v1344/`; details and replay:
[FM operator evidence](../docs/port64/evidence/pmd-musical-fm.md#primary-feedback-and-operator-total-level-controls). Earlier producer and consumer manifests keep their own identities.

v1343 joins CPU-only resident PMD to the actual native frontend. One driver
survives OP/MAIN/MAINE/fresh OP; controls and beeper remain process-local.
Actual capability selects M26/M86, and Ending/Staff waits query the new song's
real measure. All launches stay muted without an audio device/backend.

Original OP controls coupled to the three original COM drivers cover 72 cases
at PSP1000/2000. GNU8, optimized UBSan and actual Windows compare 9,204 complete
records and 21,103,632 FM-mode stereo PCM frames per host; each executes 36
unique service streams. SE2 mixed PCM is host-consistency evidence only.
Three profiles by nine BGM/SE choices each produce 65 equal frontend files on
all hosts, including live Music Room/MAIN and a declared registration child.
Six source-only variants reject; an earlier stale-query variant is inconclusive.
451 maintained inputs bind 189 AMD64 products; 62 contracts pass per host.
Independent control/driver engines share typed buffers, not a physical DOS
address space; PCM arithmetic shares pinned ymfm. No physical chip accuracy,
natural full-route or historical exactness acceptance follows.

v1343 source manifest:
`fded844658566dd8bb32f1298a68664a0f45e55d22676f2e979efe5380cf9964`.
Receipts: native `.analysis/port64/pmd-resident-v1343/`; detailed ownership,
failures and replay: `../docs/port64/evidence/pmd-resident.md`.
Earlier PCM/clock corpora retain their own identities. FM3/PPS/external ADPCM,
full original logo/startup, natural Linux/Windows routes and host
refresh/input/slowdown/Lunatic performance remain unfinished. No new GUI is
published; the last delivered native package remains v1296.
DOS acceptance and candidate-local-attested provenance are unchanged.


v1331 adds native PMD SSG effects with 40 semantic instruments, signed sweeps,
priority admission, stop/restart and ordered register writes. GNU/optimized
UBSan each compare 79,488 original effect rows and 3,942 constructed music/drum
sharing rows. The sequence now compares all selected mask bits: 134,274 short
and 49,164 longer rows per host pass without v1330's SSG exclusion.
394 sources bind 156 AMD64 products; 51 CTests pass per Linux host. Musical
OPN/FM effects, synthesis, physical clocks and frontend PMD capability remain
unfinished; all runs stay muted. Current evidence/recovery is native
`.analysis/port64/pmd-v1331/`; see native `docs/port64/evidence/pmd-ssg.md`.
Cleanup preserves 1,046 protected hashes and reclaims about 195 MiB. Current
Windows execution and Git commit/push remain pending. DOS acceptance is unchanged.

v1330 adds a native PMD bytecode/timer-state owner: musical part/rhythm
parsing, note lengths, mutable loops, tempo/bar commands, fade and stop/restart.
GNU/optimized UBSan each compare134274 original control rows in138 cases;
12 longer cases compare49164 rows per host. SSG drum/SE mask bit1 remains an
explicitly excluded ownership surface, with raw original rows retained.
390sources bind153AMD64products;50CTests pass perLinuxhost. Native OPN/FM/SSG
synthesis, physical timers and frontend PMD capability remain absent. All runs
stay muted; full natural routes/currentWindows/Lunatic timing remain. Evidence
and recovery: native `.analysis/port64/pmd-v1330/`; details: native
`docs/port64/evidence/pmd-sequence.md`. DOS acceptance is unchanged.

v1329 establishes an independent original PMD driver reference: all three
HDI-resident drivers execute 138 M26/M86 cases at two PSP segments, recording
52,992 Timer B states and complete OPN writes.102 FM SE and six fade/restart
controls pass; fixed96tick measure and missing-ack adapters reject. LOGO uses
24ticks permeasure while OP uses96; actual driver state must supply measures.
This changes verification source only: native PMD/FM remains absent and all
150 C++ products retain v1328 identities. Reference/consumer manifests remain
separate. Current private references/recovery: native
`.analysis/port64/pmd-v1329/`; details: native
`docs/port64/evidence/pmd-driver.md`.

v1328 joins process-owned sound timelines across post-logo OP, MAIN and
MAINE: actual options, Scores, Music Room, cutscenes, Staff Roll and
registration. Fresh MAINE keeps an empty EFS; BGM option restart applies
pending SE mode without reloading effects. GNU/optimized UBSan each execute
216 original OP option cases, 32 MAINE entries and 8,834 control snapshots at
two loads; all 1,150 frontend output files agree. MAIN's 3,574,464 PCM samples
per host regress. All outputs of 24 Ending and eight Extra actor controls
agree; these disable hit consumption. An MAINE EFS-reload mutant rejects.
384 sources bind 150 AMD64 products; 49 CTests pass per Linux host. All launches
stay muted. PMD/OPN synthesis/real measures, complete startup audio, full
natural routes, actual Windows and Lunatic timing/performance remain. DOS
acceptance is unchanged. Current evidence/full pending-source recovery:
native `.analysis/port64/sound-scenes-v1328/`; details:
native `docs/port64/evidence/sound-scenes.md`.

Owned terminal cleanup reclaims 1,508,634,624 allocated bytes (about 1.40 GiB)
from 6,357 duplicate files and one retired mutant executable. 13,175 protected
hashes remain unchanged at that boundary; sources, inputs, references and all
current programs remain. Windows interop and shared Git metadata still reject;
no current Windows execution/commit/push is claimed.

See [OP/MAINE scene evidence](../docs/port64/evidence/sound-scenes.md), [MAIN sound evidence](../docs/port64/evidence/sound-main.md) and
[beeper evidence](../docs/port64/evidence/beeper.md). The current owner
queue is in [PORT64](../docs/PORT64.md#remaining-owners); older subsystem
paragraphs describe their own historical batches.

The sound-control component now preserves original mode detection, command
routing, SE priority/duration and sound-resource requests.13198 independent
original cases pass on GNU/UBSan;370sources bind141AMD64products and46CTests
pass perLinuxhost. PMD/FM synthesis and frontend audio joining remain.
See [sound control evidence](../docs/port64/evidence/sound-control.md).

First audio setup now runs before score reads and ordinary menus when the
independent host configuration requests rankFF.84 original instruction cases,
780 complete displays and9 actual BGM/SE combinations with process restart
pass on GNU/optimized UBSan.366sources bind138AMD64products;45CTests pass per
Linux host. Every launch stays muted. Audio and complete natural routes remain.
See [setup evidence](../docs/port64/evidence/setup.md).

Idle OP now runs all four original recorded demos, returns on any mapped physical
key or frame3996, fades in original order and rebuilds fresh OP. Each Linux host
passes16 real visits and43 contracts;132 AMD64 products bind352 sources. Demo
forces Hard/Turbo/power128 locally while preserving menu settings. Component
checks independently execute original callbacks/startup; frontend captures
compare GNU/UBSan. All launches stay muted, with no audio backend opened.
See [demo evidence](../docs/port64/evidence/demo.md).

Music Room now runs from the real OP menu, retains polygon/playing state on
revisit, rebuilds menu resources and returns to Game.32 original child cases,
171 polygon controls,395 complete displays and12 frontend visits pass; GNU
and optimized UBSan each pass42 contracts.129 AMD64 products bind346 sources.
All launches remain muted; no audio backend is opened.
See [Music Room evidence](../docs/port64/evidence/op-music.md).

OP Scores now runs in its retained OP process with original row/rank assets,
held paging, ordered fades/release and physical saved-score reads.135 original
caller cases,640 complete displays and12 actual menu/MAIN routes pass; GNU and
optimized UBSan each pass41 contracts.126 AMD64 products bind339 sources.
Actual Windows execution remains unavailable; every launch stays muted.
See [ranking evidence](../docs/port64/evidence/op-score.md#op-ranking-viewer-v1320).

The retained live MAIN HUD and physical highest-score load are joined with
150 original first-stage caller controls. The HUD component passes5926 two-load original instruction controls,
75 complete TRAM/RGB controls and40 CTests perLinuxhost. It retains signed
life/Bomb widths, WORD Dream wrap and shared HP animation semantics. Repaint does not
reinitialize or advance them. See [HUD evidence](../docs/port64/evidence/hud.md).

Extra runs actual ST06 resources/STD, the timed midboss, three retained `_DM06`
dialogues and both Mugetsu/Gengetsu battles, then all-clear and MAIN blackout16
into dedicated Extra MAINE: delay100, registration real host save, CONG04/14,
verdict and fresh OP/second MAIN. GNU/optimized UBSan each pass 39 contracts;
eight shooting/Bomb/paint actor controls agree on 336 files/312 BMPs and all
three original dialogue/resource sequences. Player-hit consumption is disabled
and the unlock/availability adapted in these long controls. Startup/fresh OP now
reads closed physical scores, applies original rank/character/shot unlocks and
preserves the original Extra-only Marisa/B fallback. Independent two-load OP
checks cover 556 cases; 34 physical restart and 6 registration child scenes enter
Extra without unlock adapters. Complete ordinary Extra, audio/config persistence and complete routes remain.
Windows is cross-build only; all launches stay muted.
See [Extra evidence](../docs/port64/evidence/extra.md) and
[OP score evidence](../docs/port64/evidence/op-score.md).

This branch keeps the playable PC-98 DOS build intact and develops a separate
native port. The current GUI reads a user-supplied TH04 HDI, decodes the original
assets and runs the title/options, character/shot selection, Stages1 through6.
Stages1 and2 include their actual STD waves, midboss, pre-dialog, ordinary boss,
post-dialog, clear bonus and departure. Stage3 continues its STD waves and
midboss, Elly battle, post-dialog, clear bonus and departure. Stage4 runs its
STD waves, carpet lighting, two midboss encounters and character-dependent
NPC dialogue. Both characters continue through their respective Reimu/Marisa
Boss battle, post-dialog, clear bonus and departure into Stage5 STD waves, scrolling stars and Yuuka pre-dialogue.
Stage5 has no midboss; it includes Yuuka's battle, post-dialogue and departure.
Normal/Lunatic continue through Stage6 waves, dialogue and Yuuka's final
battle, then all-clear, Good Ending, Staff Roll, assessment and congratulations.
Easy follows its Bad Ending through the same post-Ending owners.
On Linux the window uses SDL2; on Windows it uses Win32/GDI.
Arrow keys move, Z fires, Shift slows movement; release then press Enter or Z
to advance dialogue. After congratulations and the original100-refresh delay,
registration accepts arrows, Z/Enter, X to erase and Esc to save, then returns
to fresh OP. Player death and frozen Game Over/Continue are joined with bounded
frontend controls. The v1308 working tree joins Quit's score-only MAINE route
with bounded GNU/optimized UBSan controls; actual Windows replay is pending.
Bomb graphics/shared palette are joined in v1309 with bounded GNU/optimized
UBSan and two-load original Bomb-layer controls. HUD and Extra are now joined under the bounded controls above; audio and
complete natural routes remain pending. Actual Windows v1308/v1309 replay is pending.
The native preview does not embed
original executables or assets and makes no DOS byte-exact claim.

All launches stay muted (`--mute` is also explicit in the Windows launcher).
Scores use a separate `GENSOU.SCR` under `$XDG_DATA_HOME/th04` or
`$HOME/.local/share/th04` on Linux, `%LOCALAPPDATA%\TH04` on Windows; override
with `--save-dir DIR`. Original writer closes commit through a temporary file
and atomic replacement. An I/O failure blocks the return to OP. Files shorter
than ten196-byte sections are recreated by an explicit host repair; score-core
short-read behavior remains unchanged. HDI inputs stay read-only.

`--registration-checks DIR` runs30 seeded child-scene fixtures, including all
ten sections, both name exits, save/reload, fresh OP and second MAIN. This
does not exercise a complete natural gameplay route. See the
[registration evidence](../docs/port64/evidence/score-registration.md#registration-scene-and-host-save).

`--score-route-checks DIR` drives24 actual OP/finite-STD shot/contact/Quit
routes through registration, verdict, fresh OP and second MAIN, plus4 real
writer failures. These are bounded authored-STD controls, not full-game routes.
Use `verify_score_route.py` or `verify_score_route_windows.ps1` with fresh
directories; all launches remain muted.

The two Stage4 Boss owners have independent original CPU state/event,
foreground/backdrop and indexed-pixel controls. Marisa additionally owns four
bits, ten attacks and the target's signed line clipping rules. Gameplay uses
an explicit native repair for the original variable-duration flystep zero
divisor; original-state controls keep that repair disabled. See the bounded
[Stage4 render evidence](../docs/PORT64.md#stage4-marisa-battle-and-rendering).

Semantic clarification follows concrete reconstruction and native owners. Current evidence
and limitations live in [PORT64.md](../docs/PORT64.md), while the older subsystem
sections below retain their bounded historical scope.

The portable core also models the DOS executable chain as guarded in-process
states over one fixed-width resident object. Contracts cover normal, Extra and
the four demo launches; MAIN statistics publication; Good/Bad, Extra and
score-only MAINE routing; direct MAIN-to-OP return; and MAINE-to-OP retention.
These process contracts are now joined to gameplay, MAINE and fresh OP.
Demo frontend playback is joined under the recorded-demo controls above.

`Lcg32` is the fixed-width process-local generator underneath portable random
state. It reproduces the unsigned modulo-2^32 update and 15-bit result on both
Linux and Windows, including signed-boundary vectors. The application state
keeps OP's menu-frame accumulator in the resident object, resets local state to
1 at each modeled executable transition, copies the resident seed on MAIN
entry, applies the demo seed 318, and exposes MAINE's verdict re-seed as an
explicit event so route ordering stays visible.

`SharedRandomRing` preserves
the single stream shared by both historical accessor families, the descending
256-call fill, overlapping little-endian samples, byte-sized cursor advance,
AND/MOD reduction order and the layout-defined `0xFF00` boundary sample. The
boundary is synthesized explicitly, so the x64 implementation never reads
outside its array. A zero MOD divisor becomes a defined host exception after
the sample has advanced, matching the original state order around 8086 `DIV`.

`item_system` builds the first MAIN gameplay contract on that stream. It
models the 32-slot fixed pool's miss-drop allocation, three velocity fields,
big-item slot, unused distinct draw, per-item power/point draw and one-life
full-power override. Fixed-width score state covers the point/dream tables,
Bomb multiplier, power overflow, collection/miss performance carries and the
wrapped unsigned pickup rectangle. The big-power cap is evaluated before the
portable table lookup, yielding the same cap/reward without the DOS source's
transient out-of-range access.

The architecture follows the separation used by TH08's modern port: the
historic compiler/link path remains the reconstruction baseline, while CMake
builds a new host product. TH08's current modern product is still 32-bit;
TH04's 16-bit segmented ABI and PC-98 hardware need a wider runtime boundary
before gameplay sources can compile for x64.

Linux build and independently verified image smoke:

```sh
cmake -S port64 -B .analysis/port64/linux -DCMAKE_BUILD_TYPE=Release
cmake --build .analysis/port64/linux --parallel
ctest --test-dir .analysis/port64/linux --output-on-failure
python3 port64/smoke.py --exe .analysis/port64/linux/th04-port64 \
  --hdi .analysis/runtime/images/zun.hdi
```

Windows x64 cross-build from Linux:

```sh
cmake -S port64 -B .analysis/port64/windows \
  -DCMAKE_TOOLCHAIN_FILE="$PWD/port64/mingw64-toolchain.cmake" \
  -DCMAKE_BUILD_TYPE=Release
cmake --build .analysis/port64/windows --parallel
WINEDEBUG=-all python3 port64/smoke.py --runner wine \
  --exe .analysis/port64/windows/th04-port64.exe \
  --hdi .analysis/runtime/images/zun.hdi
```

For native Windows development, use a 64-bit CMake generator and build the
same `port64` source directory. Example command on Windows:

```cmd
th04-port64.exe --hdi D:\path\to\your\th04.hdi --title
```

The resource CLI prints a FNV32 hash of the 4-bit packed pixels. `CONG10.PI` and
`CONG14.PI` must yield `232AE649` and `EDFA0534` on the attested HDI; these
match the independent 16-bit DOS decoder probe. The generated BMP is an
inspection artifact and is never written into the HDI. This slice supports
PI images with embedded palettes, as used by these fixtures.

`--title-screenshot FILE.bmp` performs the complete OP1.PI + SFT2.CD2 +
CAR.CD2 main-menu composition without opening a window.
`--options-screenshot FILE.bmp` adds the SFT1.CD2 numerals and renders the
default Options state. Linux and Windows x64 produce the same 640x400 BMPs
with SHA-256 `b52ea861...` and `a064338b...`.
`--character-screenshot` and `--shot-screenshot` render the two selection
stages; their shared cross-host hashes are `c1a795a3...` and `12aa7616...`.
`--handoff-screenshot` retains the static handoff fixture (`0b2c0f8c...`).
`--main-screenshot` requires an HDI and drives a 60-frame movement/item scene
with seven explicitly injected item types (`4cbbe895...`); these fixture items
are not injected into ordinary interactive sessions.
`--shooting-screenshots DIR` writes all four full-power shooting fixtures to
an existing directory. Each fixture collects an explicitly injected full-power
item and holds Z for 66 frames; ordinary windows start at power 1.
`--midboss-screenshots DIR` runs four 4500-frame Stage 1 fixtures (both
characters, held Z or no shot) and saves six checkpoints each. They use actual
STD waves, background, shots and effects; player death is joined, with full natural-route validation pending.
Independent original-CPU state/render/tile/setup controls:

```sh
python3 port64/verify_midboss.py --target .analysis/targets/th04/main.exe \
  --hdi .analysis/runtime/images/zun.hdi \
  --exe .analysis/port64/linux/th04-port64-midboss-contracts \
  --output-dir .analysis/port64/midboss-control
```

The portable contract target
also consumes `src/main/bullet/group_types.hpp` and checks 64-bit pointer
width, byte-sized angles/group codes, spread/ring geometry, aim and template
rotation wrapping, half-turn directional-sprite reuse, and OP menu/config
transitions. It additionally checks the complete portable process-handoff
contract and rejects invalid cross-phase transitions. The contract output also
reports `randring=SHARED_OVERLAP lcg=PROCESS_LOCAL32` after checking LCG
vectors, executable/resident seed lifetimes, an LCG-backed 256-call fill, all
256 cursor positions and the consuming zero-divisor failure path. It also
reports `items=FIXED_WIDTH_SAFE` after checking enemy-drop cadence, shared-ring
consumption, full/sparse pool allocation, one-life override, scoring caps,
performance carries and pickup boundaries.

A GNU x86-64 debug build also passes these contracts with
`-fsanitize=undefined,bounds`, including unsigned wrap, process resets, the
full LCG-backed random-ring fill and the above-cap big-power scoring case.

The live MAIN contracts additionally cover Q12.4 wrapping, negative arithmetic
shifts, angle/polar motion, conflicting input priority, Shift speed, clamping,
item gravity, attraction, deferred release, pickup/miss ordering and BFNT
palette/row decoding. `verify_movement.py` independently executes the pinned
original MAIN player-move body under Unicorn for all 256 direction masks and
compares the native vectors. This validates the isolated primitive; it does
not establish full player update or original frame timing.

Optional window integration replay (requires Xvfb, xdotool, ImageMagick and Pillow):

```sh
xvfb-run -a -s '-screen 0 1600x1000x24' python3 port64/verify_window.py \
  --exe .analysis/port64/linux/th04-port64 \
  --hdi .analysis/runtime/images/zun.hdi \
  --output-dir .analysis/port64/window-linux
```

For Wine/Win32 use `--runner wine` and the Windows executable. This checks
actual held keys, visible movement, slower Shift movement and Esc exit with
loose time bounds; native Windows pacing remains a separate observation.

`stage_background` decodes the MPN last-image index and B/R/G/I planes once,
translates MAP VRAM addresses into portable tile IDs, initializes the 25-row
ring in STD order, and preserves the byte scroll accumulator, initial chunk
length speed and pre-advance display origin. The host redraws the playfield
from this ring while retaining the original Stage 1 scroll state sequence.
The independent original-CPU oracle covers initial fill and 6,715 frames
through termination, including 64 stopped frames. Original MPN renderer calls
also match all 32,768 indexed pixels of both character tile sets.

```sh
python3 port64/verify_background.py --target .analysis/targets/th04/main.exe \
  --hdi .analysis/runtime/images/zun.hdi \
  --exe .analysis/port64/linux/th04-port64-live-contracts \
  --output-dir .analysis/port64/background-cpu
```

Use `--runner wine` for the PE32+ contract executable. Scroll EGC copies and
graphics calls are intercepted in this oracle; it proves bounded software
state and MPN pixels rather than complete PC-98 video or gameplay.
`verify_window.py --playchar marisa` covers the other character. Its visible
movement check now matches nontransparent original BFNT sprite pixels against
the scrolling window, rather than assuming a black background.

`player_shots` preserves descending volley allocation order, all four routes
and ten power levels, cycle resets, allocation-dependent random consumption,
old option coordinates at laser startup, hit-animation countdown and the
frame collision cache. Releasing Z finishes the remaining volleys of the
18-frame cycle. Hit tests retain diminishing damage, Bomb/boss division order,
odd-frame laser damage and spark phase. Spark requests now dispatch through the live effect adapter; the isolated
shot CPU oracle still intercepts them. Sound remains separate. The host stops
at 68 slots rather than importing the original allocator's observed overrun.

```sh
python3 port64/verify_shots.py --target .analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux/th04-port64-shot-contracts \
  --output-dir .analysis/port64/shots-cpu
```

The relocated original CPU agrees on 4,072 trigger/producer/update/hit
checkpoints, including all timer bytes, both characters/shot types, all levels,
homing targets, sparse/full pools, laser phases, hit edges and repeated calls.
Spark calls are recorded and intercepted. A separate negative control observes
the original allocation overrun; the host boundary is tested with sanitizers.
Both character windows pass held-Z firing and release against original sprite
pixels. Windows validation runs under Wine; native Windows pacing is untested.

Stages1..6 now connect their ordinary waves, bosses and clear transitions.
At this historical milestone, remaining owners included Extra, HUD, death/Bomb
transitions and audio; the current joined owners and remaining queue are above.
Saved configuration and Ending/score persistence also remain. This historical slice predates later joined owners; use the current handoff
for remaining gameplay and fidelity work.

`stage_program` dispatches original STD waves without catch-up; midboss skips
consume the wave. `enemy_system` preserves inclusive timed movement, immediate
setup chains, script loops, clipping, Lunatic autofire, performance intervals,
shot damage, homing, kill/drop scoring and animation. Render-state mutations
occur once per simulation frame. Synchronous fire/sound/tile/spark requests
retain the original call boundaries; item drops and bullet tune/add are
connected synchronously now. Spark RNG/effects now dispatch synchronously too; player death remains absent.

```sh
python3 port64/verify_enemy.py --target .analysis/targets/th04/main.exe \
  --hdi .analysis/runtime/images/zun.hdi \
  --exe .analysis/port64/linux/th04-port64-enemy-contracts \
  --output-dir .analysis/port64/enemies-cpu
mkdir -p .analysis/port64/combat
.analysis/port64/linux/th04-port64 --hdi .analysis/runtime/images/zun.hdi \
  --combat-screenshots .analysis/port64/combat
```

Use `--runner wine` with the PE32+ contract executable. The CPU oracle compares
9,414 VM vectors, 896 hit/lifecycle cases, all seven schedules and 12,600 actual
Stage 1 enemy update/render frames. It records ordered intercepted requests
and renderer coordinates/cels, not complete graphics pixels or gameplay.
The combat fixture holds Z for 1,200 original Stage 1 frames per character,
with normal initial power and no injected entities/items/score. Both host
products kill 26 enemies and reach power 7; their images and counters agree.


`enemy_bullets` retains rank/performance byte arithmetic, descending separate
pools, cloud timing, first-close-frame graze, collision, clear decay, zap
bonuses and the original optional count-based slowdown. Enemy firing and spark requests consume
the same ring immediately; gather requests capture templates for later release.
The host draws small pellets procedurally and other bullets from original BFNT.

```sh
python3 port64/verify_bullets.py --target .analysis/targets/th04/main.exe \
  --hdi .analysis/runtime/images/zun.hdi \
  --exe .analysis/port64/linux/th04-port64-bullet-contracts \
  --output-dir .analysis/port64/bullets-cpu
```

Use `--runner wine` for the PE32+ contract executable. Scoped original CPU
comparison covers 36,216 tune/add/update checkpoints and 2,400 joint
STD/enemy/bullet frames. A separate 72-case original GRCG shadow checks the
procedural 8x8 pellet glyph, including the repeated lower row and Y roll.
Two negative controls retain original zero-count ring IDIV exceptions; the
native product skips those rings as the playable DOS repair does.
`--combat-screenshots DIR` now also writes `reimu-bullets.bmp` and
`marisa-bullets.bmp`: OP-selected Lunatic, 900 frames without Z, five live
bullets per image. These are natural Stage 1 fixtures without injected
entities. They are not dense-barrage timing measurements. Five contracts,
cross-host BMPs/counters and UBSan/bounds pass. This earlier bullet-only oracle
excludes gather/spark callees; their next integration is covered below. Full
routes and player death remain incomplete.


`effects` initializes spark angles with the same process generator after the
256-call ring fill and item initialization. Only free spark attempts consume
random samples; occupied attempts still advance the offset. Circular bursts
preserve word numerator wrapping. Gather circles move/shrink after items and
restore the already tuned full bullet scratch on release without retuning.
Both effects render from procedural geometry, without embedded original sprites.

```sh
python3 port64/verify_effects.py --target .analysis/targets/th04/main.exe \
  --hdi .analysis/runtime/images/zun.hdi \
  --exe .analysis/port64/linux/th04-port64-effect-contracts \
  --bullet-exe .analysis/port64/linux/th04-port64-bullet-contracts \
  --output-dir .analysis/port64/effects-cpu
```

Use `--runner wine` with both PE32+ executables. The independent original CPU
oracle compares 3,075 complete-state/render controls, 648 spark/gather glyph
controls and 2,400 controlled Normal/Lunatic integration frames. The latter
inject targeted shot-cache/gather inputs to exercise real original callee
chains; ordinary windows do not inject these. Six contracts, cross-host
fixtures and GNU UBSan/bounds pass. The original zero-count circle division
fault is a separate negative control; the host throws a defined exception.
The real 1200-frame Stage 1 shooting scenes now yield 24 kills/score5,720/power6,
and the Lunatic 900-frame scenes contain six live bullets per character. Spark
RNG integration changes the earlier partial fixture's sequence. Full routes,
bosses, death/Bomb, HUD/audio and Ending/save remain to be migrated.


`--bomb-checks DIR` drives12 muted OP/finite-STD/X scenes through ordinary Bomb,
deathbomb and rejected late deathbomb. `verify_bomb_join.py` compares original
Bomb instructions and252 captured Bomb layers at two loads. Pre-Bomb native
state/page and hardware adapters are explicit; complete ordinary routes and
physical timing remain unaccepted. Repaint does not advance Bomb effects/RNG.


`--mugetsu-checks DIR` runs16 muted OP Extra/STD/first-dialog/Mugetsu actor
controls using actual character/shot selection. Player-hit consumption is
disabled and the unlock bit is adapted; real shooting and Bomb remain active.
`verify_extra_dialog.py` compares independent original script/resource requests
at two loads; `verify_mugetsu_join.py` compares actual frontend requests and
cross-host/repaint captures. The frontier is frozen `gengetsu_dialog_pending`,
not complete Extra, original whole pixels or ordinary player survival.


`--gengetsu-checks DIR` runs 16 muted OP Extra/STD/two-dialogue/two-boss actor
controls through the third-dialogue gate. Actual character/shot selection,
shooting, two Bombs in each shooting scene, wave/lasers/columns and cached
repaint are exercised. `verify_extra_handoff.py` executes the original bounded
second-dialogue handoff at two loads; `verify_gengetsu_join.py` compares original
ordered dialogue/resource requests and complete native cross-host captures.
Use fresh directories. Completed retained outputs are immutable. These controls
exclude ordinary survival, original whole-scene pixels and complete Extra.


`--extra-clear-checks DIR` runs eight muted actual OP/Extra actor controls with
both characters/shots and paint/no-paint pairs. Three retained dialogues lead
to one all-clear award and frozen `end_extra` request at clock 416. Two genuine
Bombs per scene and release/press pauses are exercised. Use
`verify_gengetsu_join.py --extra-clear` for all three original ordered requests
and complete cross-host/paint capture equality; `verify_extra_departure.py`
executes the bounded original third-dialogue return and nonreturning exit.
MAIN blackout/Extra MAINE, saved-score unlocks and full ordinary survival remain
pending. The older `--gengetsu-checks` explicitly retains its third-dialogue
control gate. Completed outputs stay immutable; always use fresh directories.


`--extra-maine-checks DIR` extends the eight actual OP/Extra shooting actor
controls through real end_extra,273-refresh MAIN blackout16, fresh MAINE's
100-refresh wait, registration writer-close, Extra congratulations, verdict,
fresh OP and second MAIN. Every independent score directory is reopened to
check all ten sections. Use `verify_gengetsu_join.py --extra-maine` for complete
host/paint equality and the three original dialogues; `verify_extra_maine_join.py`
compares captured outgoing statistics/fade and original MAIN/MAINE caller order
at two loads. Child durations and resource/exec consumers are explicit adapters.
`verify_fresh_main.py` independently executes the original session-reset prefix;
local score digits and resident graze reset while outgoing published resident
digits remain retained. Saved OP unlock reading and full ordinary survival are
still pending. Always supply `--mute` and use fresh output directories.

The current v1374 producer adds a headless original/native Demo state reader.
Four complete demos agree on 23 selected fields and exact RNG draw counts on
GNU/optimized UBSan after the Stage 1 fractional-scroll caller repair. GNU 70
programs/68 CTests and focused UBSan 3 are current. See
[the bounded demo evidence](../docs/port64/evidence/demo.md#v1374-originalnative-main-state-pairing).
Full actor-pool, original/native picture and process fidelity remains open.

## Joined native palette waits and text writers (v1412)

The native merge retains both parents: ordinary WORD/Shift-JIS and Gaiji text
producer `328585f`, and palette wait producer `f2a51e2`. Cold producer
528/768091dc builds all 79 programs and passes all 77 CTests under both GNU
Release and optimized UBSan/bounds. The earlier selected UBSan subset is
historical evidence; this producer checks the complete graph.

Both compilers pass 32 original OP 0000:2648 wait controls at loads 1000/3333,
432 raster/cadence vectors (1,296 waits), 2,656 MAIN/MAINE Gaiji comparisons,
all 65,536 WORD characters and 65,536 two-byte inputs, and 1,680 complete
ordinary-text memory controls. Original Gaiji entries are MAIN 0000:1B0C/1B50
and MAINE 0000:0FC4/1008; ordinary entries are MAIN 0000:229E/22F6.
Retained original transcripts keep their target/helper pins and are read in
full; their receipts are not reassigned to the new native source.

Actual old `328585f` startup source fails the Count1-clear check (expected
exit 1). Eight muted SDL dummy routes (GNU/UBSan × none/pmd/pmdb2/pmd86)
complete startup, four demos and fresh OP. Each retains all 129 prior output
hashes and passes 15,988 original selected-state boundaries. GNU/UBSan output
sets agree. This remains scoped runtime agreement, with no exact, complete
picture, physical CPU/IRQ timing or Windows acceptance claim.

Private replay: `.analysis/reconstruction/probes/native-wait-text-v1412/`;
producer: `.analysis/worktrees/native-wait-text-v1412/.analysis/port64/native-wait-text-v1412/`.
`focused.json` records commands. `verify_retention.py --restore --prefix`
restores owned archived paths; retirement reclaims 508.31 MiB net.
Source, selected programs, full comparison streams, receipts and the real
predecessor remain. Continue bounded native scene wait/hardware recovery;
broader Boss/death/process routes, complete pictures and Windows remain open.

## Native MAINE delay and black-fade boundaries (v1413)

Isolated native producer 530/96e2008a restores shared Animation's logical
WORD parameter boundaries. A zero frame_delay continues on the same call;
negative arguments become unsigned WORD waits. Black fades align once, then
use signed WORD speed: nonpositive values skip all per-group waits. The
optional PaletteSink reports every fade-generated palette_show, including
all 18 updates on one admission for zero speed. Explicit tone requests stay
in RequestSink. This is a logical refresh projection, with no shared Count1
owner, CPU execution cost or elapsed raster/IRQ timing claim.

Both cold GNU and optimized UBSan/bounds build all 80 programs and pass all
78 CTests. Complete original MAINE 0CC7:0033..0047 frame_delay and
0000:0622..06A3 black fades pass 72 cases at loads 1000/3333; the actual
0000:2206..222B wait executes inside each fade. Count1 pulses are explicit
stimuli and palette_show is a guarded tone observer. All 36 native vectors
match, including WORD truncation, zero and 7FFFh/8000h boundaries.

The actual 9a7f380 Animation predecessor differs in all seven complete
boundary traces. Current Congratulations retains 32 original branches,
50 original fade/key clocks and 20 complete PI-page comparisons per compiler;
verdict retains 916 state/request cases and 10 clock/key controls. Their
pixel references retain their earlier native decoder producer. Eight muted
startup/four-Demo/fresh-OP routes retain all 129 prior hashes per profile and
15,988 original selected-state boundaries each. No exact/full-game promotion.

Replay: `.analysis/reconstruction/probes/native-maine-animation-v1413/`;
producer: `.analysis/worktrees/native-maine-animation-v1413/.analysis/port64/native-maine-animation-v1413/`.
`focused-gnu.json`, `focused-ubsan.json` and `focused.json` record commands.
Use `th04-port64-cutscene-contracts` for Congratulations/verdict helpers;
frozen port readers need read-only `PYTHONPATH=ROOT` for the HDI parser.
Failed missing-parser/wrong-program recipes remain. Verified retirement
reclaims 505.69 MiB net; full source/projections, selected programs and
predecessor remain. Continue actual elapsed scene wait ownership; physical
timing, complete pictures, broader Boss/death/process and Windows stay open.

## Joined native MAINE wait consumers (v1416)

Joined native producer 532/037b0f2e restores shared Animation's logical
WORD parameter boundaries. A zero frame_delay continues on the same call;
negative arguments become unsigned WORD waits. Black fades align once, then
use signed WORD speed: nonpositive values skip all per-group waits. The
optional PaletteSink reports every fade-generated palette_show, including
all 18 updates on one admission for zero speed. Explicit tone requests stay
in RequestSink. This is a logical refresh projection, with no shared Count1
owner, CPU execution cost or elapsed raster/IRQ timing claim.

Both cold GNU and optimized UBSan/bounds build all 81 programs and pass all
79 CTests. Complete original MAINE 0CC7:0033..0047 frame_delay and
0000:0622..06A3 black fades pass 72 cases at loads 1000/3333; the actual
0000:2206..222B wait executes inside each fade. Count1 pulses are explicit
stimuli and palette_show is a guarded tone observer. All 36 native vectors
match, including WORD truncation, zero and 7FFFh/8000h boundaries.

Both compilers also retain 96 OP/MAINE original fade controls and 24 native
timelines from the independent palette producer. Both target identities,
complete fade extents and all 96 retained wait streams are re-attested.

The actual latest 6b0e1ba Animation predecessor differs in three complete
delay traces; its four fade traces already agree. Current Congratulations retains 32 original branches,
50 original fade/key clocks and 20 complete PI-page comparisons per compiler;
verdict retains 916 state/request cases and 10 clock/key controls. Their
pixel references retain their earlier native decoder producer. Eight muted
startup/four-Demo/fresh-OP routes retain all 129 prior hashes per profile and
15,988 original selected-state boundaries each. No exact/full-game promotion.

Replay: `.analysis/reconstruction/probes/native-maine-wait-join-v1416/`;
producer: `.analysis/worktrees/native-maine-wait-join-v1416/.analysis/port64/native-maine-wait-join-v1416/`.
`focused-gnu.json`, `focused-ubsan.json` and `focused.json` record commands.
Use `th04-port64-cutscene-contracts` for Congratulations/verdict helpers;
frozen port readers need read-only `PYTHONPATH=ROOT` for the HDI parser.
Failed missing-parser/wrong-program recipes remain. Verified retirement
reclaims 505.93 MiB net; full source/projections, selected programs and
predecessor remain. Continue actual elapsed scene wait ownership; physical
timing, complete pictures, broader Boss/death/process and Windows stay open.

## Native IRQ counter and frame_delay primitive (v1417)

Producer 534/8a83575e adds live `vsync::Delay`: construction clears only
Count1 and truncates the argument to WORD; readiness polls the current
unsigned word. A different consumer can reset Count1 and extend the wait.
Positive delays remain pending without an IRQ owner, with no GDC fallback;
zero clears Count1 and returns immediately even when uninstalled.

Counter bulk advancement preserves the original carry-skip recurrence and
both wrapped words with full-width UINT64 arithmetic. It returns the full counted-IRQ
total without intermediate multiplication overflow. RasterClock's path with
no observers uses this recurrence and integer edge search; the callback
overload still emits every IRQ. Actual startup uses the path with no observer.
This enables large WORD delays/cadence inputs without billions of host loops.
Elapsed MAINE/registration Scene integration and physical CPU/IRQ latency
remain open; a new primitive is not full-scene acceptance.

Both cold GNU and optimized UBSan/bounds build all 82 programs and pass all
80 CTests. Complete original frame_delay bodies MAIN 130E:00D7,
OP 0DA1:002B and MAINE 0CC7:0033 (21 bytes each) pass 144 consumer controls
at loads 1000/3333. Separate 36 actual original ISR/IRET injections gate the
counter recurrence. Consumer word changes are explicit stimuli. Independent
Python big integers check 280 bulk and 1,728 delay/raster vectors, including
UINT64_MAX and the 4,294,901,760-IRQ wait boundary. No physical timing claim.

Three compiled mutations reject 25 overflow, 1,428 Count2-reset and 576
signed-threshold cases. Existing wait consumers retain 32 original controls,
432 native vectors and 1,296 waits per compiler. Eight muted actual
startup/four-Demo/fresh-OP routes retain all 129 prior hashes per profile and
15,988 original selected-state boundaries each; GNU/UBSan outputs agree.

Replay: `.analysis/reconstruction/probes/native-counter-delay-v1417/`;
producer: `.analysis/worktrees/native-counter-delay-v1417/.analysis/port64/native-counter-delay-v1417/`.
`focused.json`, build receipts and `verify_counter_delay.py` record the gates.
`verify_retention.py --restore --prefix` restores owned archived paths.
Verified retirement reclaims 506.12 MiB net. Source freeze, full original/
integer projections, selected programs and compiled mutations remain.
Historical exact remains 661/663; actual elapsed consumers, complete pictures,
broader Boss/death/process, native LCD mapping and Windows remain open.

## Native elapsed MAINE consumers (v1423)

Development remains active. Verdict and Congratulations in normal Ending,
Score and Extra now share the live raster/IRQ counter owner. Their black
fades, WORD frame delays and signed input waits consume elapsed time rather
than host repaint counts. Initial fade alignment keeps Count1; delay clears
only Count1. Input release combines samples before and after the wait;
negative timeouts still release first, while zero and 9999 repeat the press
wait. A completed child returns unused time to its parent. The registration
entry delay 100 starts at the actual child completion. New MAINE/OP processes
reset counter BSS while retaining raster phase; clock and audio advance once.

Final union retains analog/LCD palette output, indexed Demo entry and the
original WORD Demo blackout with all18 palette publications and19 tone stores.
Cold producer 540/bc9bb404 builds all 84 programs and passes all 82 CTests
under GNU Release and optimized UBSan/bounds. Each compiler agrees with 576
complete original MAINE fade/delay/input controls at loads 1000/3333 and 288
coarse plus 288 one-millisecond partition vectors. The original key and
palette calls use guarded adapters, with independent ideal IRQ stimuli;
physical CPU/I/O/ISR latency is not measured.

The attested original entries are MAINE 0000:0622/0666 (black fades),
0CC7:0033..0047 (frame_delay), 0CC7:020A..025F (input_wait), and
0000:2206..222B (the full wait inside each fade). These are runtime-observed
instruction controls; the pinned targets remain candidate-local-attested.
`run.py` records the serial cold commands and `focused.py` the exact original
and actual-route commands. New replay needs a fresh producer directory.

Actual Score (24 routes plus four write failures), Extra (16 actor-control
routes with hit consumption disabled), and 24 Ending routes exercise the new
consumers and phase publication. Ending/Staff/verdict/Congratulations keep complete page
and palette checks; display RGB is projected from original MAINE palette I/O
through the retained analog DAC model. The historical RGB8 formula remains
separate. Shared palette and actual eighteen-frame Demo-entry controls are
replayed against the final producer. Compiled one-variable mutations cover
fade counter clearing, post-only key samples, the 9999 sentinel and discarded
handoff time. The first stopped-entry mutation rejects no configured vectors
and remains an inconclusive wrong-site probe; the completion-site mutation
is independently compiled and rejects160 complete traces. Eight muted default
routes retain all129 prior hashes, selected original states and GNU/UBSan
parity. This regression does not promote complete original pictures.

Registration proper, Cutscene/Ending script, Staff and MAIN fade still have
legacy wait owners. Their full elapsed counter history, physical timing,
broader Boss/death/process routes and Windows acceptance remain open.
Historical exact remains 661/663. This is scoped runtime agreement.

Replay: `.analysis/reconstruction/probes/native-maine-demo-word-join-v1423/`;
producer: `.analysis/worktrees/native-maine-demo-word-join-v1423/.analysis/port64/native-maine-demo-word-join-v1423/`.
The preliminary v1418/v1420/v1422 cold producers and failed recipes retain their
own identities. Stage retirement saves 1,254.54 MiB net and keeps all 8,420
paths in a fully verified content archive. The superseded539 producer keeps
both complete build graphs and its completed GNU route/image proof; its UBSan
Extra job was deliberately stopped after remote WORD Demo source advanced. The stage retention reader accepts
`--restore --prefix` for owned original paths. Final retirement and publication
receipts record the remaining checks and current commit.

Stage archive readers are under `.analysis/reconstruction/probes/native-maine-stage-retention-v1422/`
and `.analysis/reconstruction/probes/native-maine-indexed-stage-retention-v1423/`.
The latter saves another 984.19 MiB net across 4,538 owned paths, including
the deliberately interrupted UBSan campaign; its logs and source identity remain.

Final verified retirement releases 1961.42 MiB net. Both complete program graphs, source freeze and original controls remain.

## Native elapsed Staff Roll (v1424)

Staff's actual scene and Ending caller now use the shared raster/IRQ owner.
The three dissolve loops poll the inherited unsigned Count1 against2, then
clear only Count1 after success. They do not use frame_delay's entry reset.
MAINE 0A05:1298,1325,13C6 each has CMP/JB then MOV Count1,0; the complete
0A05:0E80..1736 Staff extent remains pinned. Shared black fades align once,
preserve Count1 and publish all eighteen palette updates. Inactive measure
waits execute a live WORD frame_delay; active waits query after load/start,
preserve counters and service supplied measure deadlines. The actual audio
bridge uses the resident PMD timer deadline. Keys do not skip Staff.

Whole original Staff, black fades, wait and snd_delay_until_measure
0CC7:03D6..0407 instructions execute at loads1000/3333. Graphics/files and
measure replies are guarded adapters; ideal IRQ and one-second measure
stimuli remain separate from physical CPU/I/O/audio costs. Both cold GNU and
optimized UBSan/bounds producer541/83933826 build84 programs and pass82 CTests.
Each passes48 original controls,24 coarse and24 one-ms partitions, covering
inactive BGM, progressing measure and no measure progress. Existing576
MAINE controls/288 partitions also pass on the same frozen producer.

Each actual muted no-driver frontend completes24 Ending/Staff/verdict/
Congratulations routes. Independent checks cover576 Ending pages/288 RGB
frames,48 Staff pages,48 verdict pages and48 Congratulations pages. Current
RGB uses complete original palette I/O with the retained DAC projection.
These are component images and route invariants, not physical full scanout.
Real active-PMD paired scene timing, other scene wait owners, broader gameplay
and Windows remain open. Historical exact stays661/663.

Compiled whole-scene clear-before and clear-both mutations reject complete
original traces. A relative-threshold mutant passes coarse input but fails
one-ms input. The first development build had that same API misuse; its
program, source, failed partial trace and corrected replay remain separately
identified. until_count requires the absolute threshold2. Native CI345 passes.

Replay: `.analysis/reconstruction/probes/native-staff-elapsed-v1424/`;
producer: `.analysis/worktrees/native-staff-elapsed-v1424/.analysis/port64/native-staff-elapsed-v1424/`.
`verify_staff_elapsed.py` supplies original controls and full time/counter/
request comparisons; `focused.py` records actual route/page commands.
Verified content/SHA/CRC/metadata/temp-restore retirement releases908.95 MiB
net. Sourcefreeze, all programs, full control transcripts and failures remain.
`verify_retention.py --restore --prefix` restores owned archived paths. The
source target remains candidate-local-attested; this is scoped runtime agreement.

## Native elapsed Cutscene/Ending script (v1425)

Actual Ending scripts now share the raster/IRQ owner through Script, Canvas
and Ending. Parsing and queued graphics requests remain shared with the
logical helper. Zero frame_delay clears Count1 and resumes on the same
admission; input_wait preserves release-first, pre/post OR and signed WORD
budgets. Shared Animation now handles both white fades as well as black,
including initial VSync, signed WORD speed and eighteen palette updates.
MAINE white bodies0000:222C..22AB are pinned alongside black00622/0666,
frame_delay0CC7:0033..0047, input_wait020A..025F and measure03D6..0407.
The two complete original parser/helper bodies0A05:07F7..0D6B and0DAC..0E7F
execute unchanged. File/font/graphics, palette I/O and keyboard consumers
remain explicit adapters, with ideal IRQ and one-second measure stimuli.

Original cutscene checks high-byte key_det bit0x10 (word0x1000); portable
cutscene bit0x10 is a projection. The Oracle maps this explicitly. Escape is
sampled only at the next outer iteration; releasing it during a queued mask
cannot change that command. A completed owner returns unused elapsed time;
actual Ending forwards audio once and retains the Staff/verdict lifecycle.
Active measures query after load/start and use supplied service deadlines;
inactive measures use live WORD frame_delay. This is not physical timing.

Cold producer542/59d19121 builds all84 programs and passes82 CTests under
GNU Release and optimized UBSan/bounds. Each passes ten complete scripts
(eight original Ending plus two mixed/measure controls),960 original cases
at loads1000/3333,480 coarse and480 one-ms partitions. Same-source Staff
48 original/24 partitions and MAINE576 original/288 partitions also pass.
Each actual muted inactive-BGM frontend passes24 Ending/Staff/verdict/
Congratulations routes and independent component images:576 Ending pages,
288 original-DAC-projected RGB frames and48 pages each for the later owners.
The retained PI/font/kernel galleries keep their independent source identity.

Compiled zero-to-one delay rejects36 mixed cases; discarded completion time
rejects28 mixed and24 real-script cases; wrong full-word Escape rejects12 in
each subject. Unmodified compiled control passes. Native CI345 and tracking
pass. The initial malformed vector schema/configuration attempts are retained;
they were setup failures, not source/runtime acceptance.

Remaining MAIN fade, registration and other wait owners, real active-PMD
paired scene timing, physical CPU/I/O/scanout, broader gameplay and Windows
remain open. Historical exact stays661/663; targets are candidate-local-attested.
Replay: `.analysis/reconstruction/probes/native-cutscene-elapsed-v1425/`;
producer: `.analysis/worktrees/native-cutscene-elapsed-v1425/.analysis/port64/native-cutscene-elapsed-v1425/`.
`verify_cutscene_elapsed.py` records full original/native time/request/key/
counter streams; `focused.py` records actual routes and image comparisons.
Verified path/hash/size/mode/nsmtime/content/CRC/temp-restore retirement saves
1619.52 MiB net. Full transcript aliases and captures are recoverable via
`verify_retention.py --restore --prefix`; source, programs, vectors and summaries
remain live. The goal stays active.

## Native elapsed MAIN good/bad/Extra exit fade (v1426)

The actual normal good/bad and Extra callers now consume black-out16 through
shared elapsed Animation. Initial VSync retains inherited Count1; all eighteen
palette publications and273 nominal counted waits remain. Completion publishes
statistics and releases MAIN before resetting fresh MAINE counter BSS. Raster
phase and unused elapsed time cross the handoff; clock/audio service occurs once.
Extra's delay100 starts at the actual fade completion. Host admissions need not
number273. The legacy no-clock helper remains a separate logical model.

Observed MAIN relative CS:IP0000:B7B9/B7E4/B80F complete three exits (124 bytes),
0000:0622..06A3 black fades and0000:2462..2487 IRQ-owned wait execute unchanged
at loads1000/3333. DGROUP2134 counters2AB2/2AB4/2ABA, increment0772 and active
owner0774 are explicit. Sound0204 and nonreturning execl are guarded seams;
ideal IRQ stimuli do not measure CPU/I/O, sound or DOS-loader latency.
The targets remain candidate-local-attested; historical exact stays661/663.

Cold producer543/70986a2b builds all84 programs and passes82 CTests under GNU
Release and optimized UBSan/bounds. Each compiler agrees with144 original
controls and72 coarse plus72 one-ms partitions across all three callers,
WORD wrap, carry skips and inherited raster phase. The actual release callback
also checks statistics publication and old generation/RNG before fresh MAINE.
Same-source MAINE576/288 and Staff48/24 controls pass. Each actual muted
inactive-BGM frontend completes24 Ending/Staff/verdict/Congratulations routes
and8 Extra actor-control routes, including fresh OP and a second MAIN.
Independent images retain576 Ending pages/288 original-DAC-projected RGB frames
and48 pages each for Staff, verdict and Congratulations. These are component
controls, not a complete physical scanout or general gameplay acceptance.

Compiled actual Ending/Extra clear-at-entry, clear-before-publication and
double-consume-remainder mutations reject original counter/time streams;
the separately compiled unchanged control passes. Native CI345 passes.
The first frozen producer f055b102 passed both84/82 graphs and fade controls,
but its ordinary Ending gallery rejected held Escape crossing the newly
same-admission MAINE handoff. That failed source/program/capture is retained.
The final input releases Escape before the last fade group; product remainder
forwarding is unchanged. All acceptance uses the new543/70986a2b cold producer.

Replay: `.analysis/reconstruction/probes/native-main-exit-fade-v1426/`;
producer: `.analysis/worktrees/native-main-exit-fade-v1426/.analysis/port64/native-main-exit-fade-v1426-v2/`.
`verify_main_exit_fade.py` records complete original/native palette/time/counter
streams; `focused_v2.py` records actual callers and independent image checks.
Path/hash/size/mode/nsmtime/content/CRC/temp-restore retirement releases
1365.12 MiB net; first-producer retirement releases another469.25 MiB.
Both archive readers support `--restore --prefix`. Frozen sources, all programs,
full original controls, failed attempts and acceptance receipts remain retained.

Game Over fade4, registration proper and other wait owners, real active-PMD
paired timing, physical CPU/I/O/scanout, broader gameplay and Windows remain
open. Continue source recovery and migration; the full goal stays active.

## Native elapsed Game Over and Continue/Quit (v1427)

The actual Game Over scene now consumes elapsed time throughout cell masks,
title movement, release/press, Continue menu and final black-out4. Every
frame_delay clears only Count1. Keyboard reset follows the five menu drawing
requests; subsequent menu loops retain pre/post OR and a new press. Shared
Animation handles input_wait(0) and all eighteen fade4 palette publications.
During Game Over, MAIN actor/STD/player/RNG updates stay suspended. Continue saves before resetting
resources and resumes the suspended frame once. Quit publishes ES_SCORE and
song fade0204 before black-out4, then passes unused time to fresh MAINE delay100.
MAIN now initializes its own counter BSS while retaining raster phase.

Original MAIN0AAF:3971..3CEE (load-module E461..E7DD,893 bytes), frame_delay
130E:00D7..00EB, input_wait130E:0133..0186 and black fades0000:0622..06A3
execute unchanged at loads1000/3333. Full legal MZ relocation/DGROUP2134 and
seeded live2AB2/2AB4/2ABA counters are retained. Resident scratch9000:0000
lies outside both load modules, DGROUP and stack. Graphics, keyboard, ranking,
HUD, sound and final dispatch have guarded ABI adapters. Stage5 Bad Ending
is a dispatch seam. Ideal IRQ does not measure physical CPU/I/O/loader/audio.
Targets remain candidate-local-attested; historical exact stays661/663.

Cold 544/4a62eb34 GNU Release and optimized UBSan/bounds each build 84 programs
and pass 82 CTests. Each matches432 complete original controls and216
coarse plus216 one-ms partitions, including full E/K/time/counter streams,
Continue/Quit/held-release/no-input, WORD wrap, carry skips and stage4/5/6.
Each actual frontend passes24 finite-STD last-life scenes, real Continue
writes/failure/resource restore/credit exhaustion and repaint independence.
Independent original instruction/font/palette controls compare386 entire
displays (indices, TRAM and RGB;398352000 bytes) at loads1000/2000.
Each also passes24 actual score-only MAINE/save/verdict/fresh OP/second MAIN
routes and four failed writers. Existing144 MAIN exit and576 MAINE controls
pass. Eight default Demo profiles retain all129 prior hashes per profile,
original selected states and GNU/UBSan parity. This is scoped component/route
agreement, not complete physical scanout or general gameplay acceptance.

Compiled actual-source clear-both, early-menu-key and discarded-remainder
mutations reject full original streams; unchanged compiled control passes.
Native CI345 passes. Initial development sampled reset keys before menu draw;
its first mismatch at row8472, source/program and complete failed trace remain.
The corrected overload draws first, then samples. First cold b77968de passed
full GNU and Game Over checks but rejected a score delay boundary101 vs100: a
partial admission was counted as a refresh. Corrected ScoreRoute ticks count
completed IRQ/verdict waits; elapsed handoff behavior remains retained. Original-only cache replay
requires identical Original AST, edge helper, targets, vectors and full trace
hashes; it never converts a failed native result into acceptance.

Replay: `.analysis/reconstruction/probes/native-gameover-elapsed-v1427/`;
producer: `.analysis/worktrees/native-gameover-elapsed-v1427/.analysis/port64/native-gameover-elapsed-v1427-v2/`.
`verify_gameover_elapsed.py` records complete original/native E/K/counter/time;
`verify_gameover_join.py` checks actual suspension/host writes and full displays.
Verified journal/SHA/CRC/content/mode/nsmtime/temp-restore retirement releases
1768.58 MiB net. Source/all programs/fixtures/receipts/failures remain retained;
raw transcript aliases and owned captures restore via `verify_retention.py
--restore --prefix`. Large display streams are already gzip with full hashes.

Registration proper and other wait owners, real active-PMD paired timing,
physical CPU/I/O/scanout, broader gameplay and Windows remain open. Continue
source recovery and migration; the full goal stays active.

## Native elapsed registration and all three callers (v1428)

Actual registration now uses shared elapsed Animation for black-in2,
input_wait0 and black-out1, and live Count1-only frame_delay1 for editing.
Alphabet/cursor and accepted command drawing precede keyboard reset. Sense
ORs the pre-wait and post-wait samples; BYTE repeat keeps its30/even/wrap rule.
File operations are consumed one at a time, with writer-close before free/
clear/fade. A failed host operation freezes the scene and Score/Extra parent;
later admissions neither retry I/O nor advance registration ticks/RNG/route.
The outer clock can continue. Successful completion returns unused time.

Normal Ending begins registration on its delay100 completion admission;
Score and Extra pass time directly to registration and then verdict or
Congratulations. Clock/audio service occurs once, and new process counter BSS
keeps raster phase. Legacy no-clock helpers remain separate logical models.

Pinned MAINE decoded0A05:27C4..2B5F menu, score0A05:20F9..24B5 and process
RNG0000:1C5A..1C83 execute unchanged. Fades0000:0622..06A3, frame_delay
0CC7:0033..0047, input_wait0CC7:020A..025F and full0000:2206..222B wait execute
with DGROUP0E53/live0EFA/0EFC/0F02 and ideal IRQ at loads1000/3333.
The62414-byte decompressor payload/559 relocation observations retain their
candidate-derived container topology gap; target canonicality remains
candidate-local-attested. Graphics, keyboard, successful file/sound have
guarded ABI seams; CPU/I/O/audio/loader costs and physical scanout are unmeasured.

Cold545/b4519b50 GNU Release and optimized UBSan/bounds each build84 programs
and pass82 CTests. Each agrees with544 original controls and272 coarse plus
272 one-ms partitions: full E/K/palette/edit-loop/file/RNG/counter/time streams,
ranked/unranked/Extra, WORD wrap/carry skips, held-repeat BYTE wrap, chords,
missing/partial/corrupt file recreation and blocked input. Each actual frontend
passes24 score-return routes/four writer failures,30 seeded saves/restarts,
8 Extra actor-control routes and24 Ending-to-registration/fresh OP/second MAIN
routes. Independent checks retain576 Ending pages/288 original-DAC RGB frames
and48 pages each for Staff/verdict/Congratulations. Existing432 Game Over and
576 MAINE controls pass. Eight default Demo profiles preserve129 prior hashes
each, original selected states and GNU/UBSan parity. No general-game or exact
promotion follows; historical exact stays661/663.

Compiled actual Scene fade-counter clear, pre-draw reset and lost-remainder
mutations reject whole original streams; unchanged compiled control passes.
Native CI345 passes. First probe omitted constructor tone0 palette-show; its
short137 input also let zero HI pass checksum after an empty read, producing
invalid numeral indices rejected by the native renderer. Original core/control
continued with drawing as an adapter; actual unsafe drawing is unmeasured.
This remains an explicit renderer/input boundary, not accepted equivalence.
Valid partial and corrupt selected sections separately recreate and pass.
Second development passed272 controls but the failed Score owner threw on its
next elapsed admission; the new frozen failure matches the retained native
no-retry policy. All failed source/program/trace/journals remain distinct.

Replay: `.analysis/reconstruction/probes/native-registration-elapsed-v1428/`;
producer: `.analysis/worktrees/native-registration-elapsed-v1428/.analysis/port64/native-registration-elapsed-v1428/`.
`verify_registration_elapsed.py` owns full original/candidate streams;
`focused.py` owns actual parent routes and image commands. Verified journal/
SHA/CRC/content/mode/nsmtime/temp-restore retirement saves2435.09 MiB net,
plus42.04 MiB from three preliminary caches. Source/all programs/
fixtures/receipts/failures remain live; archived raw aliases/captures restore
with `verify_retention.py --restore --prefix`. Stage reader is under
`native-registration-stage-retention-v1428`. Only owned intermediates retired.

Other wait owners, malformed-score unsafe graphics, real active-PMD paired
timing, physical CPU/I/O/scanout, broader gameplay and Windows remain open.
Continue source recovery and migration; the full goal stays active.

## Native registration numeral requests and WORD slots (v1429)

The actual Renderer now consumes recovered numeral requests. Original MAINE
0A05:24B6..2599 uses signed IDIV/remainder after zero-extending the highest
byte and subtracting A0; high bytes0,10,...150 therefore have legal remainder0.
The former negative-high guard incorrectly rejected these rows. Lower seven
bytes still pass raw WORD patterns. SUPER0000:275E..290F doubles that WORD
with16-bit wrap before reading DGROUP0E53 pointer0F0C and dimensions130C.
Pattern8000 aliases0; FF60 reads pointer0DCC and dimensions11CC. The original
has no zero-size early return and can read low memory. The portable renderer
accepts only slots owned by loaded SCNUM2; unowned RAM remains an explicit
boundary. No blank pixels, invented memory, or malformed-file acceptance.

Cold548/fc9b02eb GNU Release and optimized UBSan/bounds each build84 programs
and pass82 CTests. Original instructions agree at loads1000/3333 for131,072
slot controls and16,384 complete row controls. Each native compiler agrees
on65,536 slots and8,192 rows (every byte value at each digit position, both
characters/banks, alternating row0/9).64 new complete graphics captures agree
on both pages, raw palette/TRAM and composed RGB against original drawing/
SUPER at loads1000/2000. BFNT/CGROM/GRCG and RGB scanout remain explicit
adapters. Both actual frontends pass30 seeded registration/save/restart routes.
Four compiled mutations reject signed remainder, byte clamping, incorrect WORD
wrap and the old high-byte guard; unchanged compiled control passes.
Historical exact remains661/663; physical video/CPU timing remains open.
Initial producer548/e1668317 passed the first load but its callback compared
Unicorn memory-hook linear EIP as segment IP at load3333 and rejected its own
control. Failed source/programs/logs remain distinct; current Oracle normalizes
EIP against the recorded load segment and traps callback errors explicitly.

Replay: `.analysis/reconstruction/probes/native-numeral-slot-v1429/`;
producer: `.analysis/worktrees/native-numeral-slot-v1429/.analysis/port64/native-numeral-slot-v1429-v2/`.
`verify_numeral_slots.py` executes original row/SUPER lookups; `pixels.py`
owns the new actual Renderer image controls. Verified archive/content/CRC/
mode/nsmtime/temp-restore retirement saves525.26 MiB net;
all source/programs/receipts/fixtures remain live, retired cache/captures and
stream aliases restore with `verify_retention.py --restore --prefix`.
The reader also verifies/restores `supplement-retention` registration captures
against their original protected hashes.
Continue source recovery and migration. Unsafe unowned score RAM, other waits,
active-PMD paired timing, physical scanout, broader gameplay and Windows remain
open. The full goal stays active.

## Native SUPER byte kernel and registration consumer (v1430)

The actual registration Renderer now uses recovered mask/B/R/G/E byte passes,
including the four X-byte/width alignment branches and original GRCG ports.
Owned SCNUM2 pixels generate planar storage once; release clears that owner.
The kernel accepts explicit source-read and hardware-write callbacks, preserving
WORD SI/DI wrap, cross-boundary WORD reads, signed patched row strides and
ordered byte/WORD writes. It does not manufacture process or low-memory bytes.

Original MAINE 0000:275E..290F executes its self-modifying body with DF clear,
controlled geometry and a seeded source at9000:0000, at loads1000/3333.
A zero height means256 rows. Even-aligned zero width enters the CH loop256
times; odd-aligned zero width decrements the WORD count to255, with first/last
byte reads. Both read512 bytes per row per pass, including source wrap.
These are provider controls, not observations of natural malformed-file RAM.
SUPER_ENTRY_AT 0000:2610..2683 also shows initial dimension-table clearing
without pointer-table clearing; actual process startup ownership remains open.

Cold551/e9fa254c GNU Release and optimized UBSan/bounds each build84 programs
and pass82 CTests. Both agree with492 original controls /
246 native vectors on all1,489,840 ordered read/port/write
events. All shifts, both byte alignments, odd/even/zero/large widths, zero
height and wrapped source/destination coordinates are covered. Each compiler
passes155 complete drawing captures (the entire prior drawing fixture corpus
plus64 signed-high-digit captures) and30 actual registration/save/fresh OP/
second MAIN routes. Pixel controls retain BFNT/CGROM/GRCG/scanout adapters.
Five compiled mutations reject zero-height/width returns, source reset per
plane, wrong source wrap and unsigned stride; unchanged control passes.

Initial551/425fc58e reached the original final RETF6 with all preceding drawing
events, but Unicorn's mixed return lost the target IP. The current Oracle
checks actual CA0600 and the original return stack, then adapts only that
return boundary. Failed source/programs/trace remain distinct. CPU timing,
physical GRCG/scanout, unowned malformed-score RAM, other waits, broader gameplay
and Windows remain open. Historical exact stays661/663; the full goal is active.

Replay: `.analysis/reconstruction/probes/native-super-kernel-v1430/`;
producer: `.analysis/worktrees/native-super-kernel-v1430/.analysis/port64/native-super-kernel-v1430-v2/`.
`verify_super_kernel.py` owns original streams; `pixels.py` owns full drawings.
Archive/content/CRC/mode/nsmtime/temp-restore retirement saves
835.30 MiB net. Source/all programs/fixtures/receipts remain
live; cache, captures and original/native aliases recover with
`verify_retention.py --restore --prefix`. Continue actual RAM-provider ownership
and remaining source recovery/migration.

## Native MAIN pause, resume and Quit (v1431)

Ordinary MAIN Esc now enters its pause menu. Actors, stage, player resources,
score and RNG remain suspended while IRQ/audio/text blink service continues.
The original three gaiji labels at26:12/14/15 and their C1/E9 attributes are
retained. Up/Down toggles once per release/press; Esc selects Resume, Z/Enter
confirms, and Q returns Quit immediately without the three space erasures.
Other confirmations wait for final release and erase four ANK cells per row.
The completed pause returns latched keys and unused time. The caller resumes
its suspended frame once; Quit publishes run state and returns to fresh OP,
with released MAIN resources and a clean second MAIN. Pause Esc is consumed
by that menu and is not requeued as a new pause after Resume.

Original MAIN DEMO_TEXT0AAF:07DF..08FD (load0B2CF..0B3ED,287 bytes), full
input_wait130E:0133..0186, frame_delay130E:00D7..00EB and VSYNC_WAIT0000:2462..
2487 execute with legal MZ relocations/DGROUP2134 at loads1000/3333.
Initial/final busy reset-sense loops sample immediately then at explicitly
chosen counted-edge observation points, without clearing Count1. Those points
are keyboard/CPU cadence adapters, not measured polling costs. Menu waits
preserve actual Count1-only clearing and pre/post OR. Physical CPU, keyboard,
active-PMD timing and full-game paired acceptance remain open.

Cold554/31e6b3d7 GNU Release and optimized UBSan/bounds each build84 programs
and pass82 CTests. Each agrees with768 original controls and
384 coarse plus384 one-ms partitions on complete events/keys/
counters/time/selection/result/latch streams. Eight actual frontend routes per
compiler cover both characters and Esc/Z/menu-Quit/Q, actor/score/RNG freeze,
raw menu TRAM, resource release/fresh OP/second MAIN.16 original putsa/putca
controls at loads1000/2000 validate all12 occupied menu cells' code/attribute
words per compiler; other cells and full graphics are outside that check.
Each ordinary SDL/private TCP-disabled Linux Xvfb run additionally exercises
Esc/Z Resume, Q Quit and second MAIN, with read-only traces and zero audio
opens. No actor/hit/score/clock writes or Windows focus/input are used.
Four compiled mutations reject cancel-as-Quit, Q erasure, skipped release and
stale live key_det; unchanged compiled control passes.

Retained dev384-control failure differed only in live key_det during waits;
reset-sense and OR-sense now update that observable field before STOP. The
first actual fixture wrongly started from missing/setup CFG; a valid encoded
configuration fixes its own entry. A dummy-video window probe and later real
SDL Esc requeue failure remain distinct. Compiler namespace failures and all
source/program/trace evidence are retained. Prior UBSan Normal-clear acceptance
stays revoked:0x19 is an unplayed sentinel after a failed survival route; this
batch does not retry or promote that full-route claim.

Replay: `.analysis/reconstruction/probes/native-main-pause-v1431/`;
producer: `.analysis/worktrees/native-main-pause-v1431/.analysis/port64/native-main-pause-v1431-v5/`.
`verify_main_pause.py` owns original controls; `window.py` owns private SDL keys.
Content/CRC/mode/nsmtime/temp-restore retirement saves256.67 MiB net.
Source/all programs/fixtures/receipts/failures remain live or losslessly recover
with `verify_retention.py --restore --prefix`. Full goal stays active; broader
Boss/death/process parity, unowned score RAM, other waits, physical scanout and
Windows remain open. Historical exact stays661/663.

## Current native natural routes and strict clear gate (v1432)

The route reader now requires the requested character/rank/shot partition's
actual physical clear mask below4 plus its shot bit, all ten full16-bit score
checksums, complete stage coverage, correct Ending and registration/fresh OP
without Continue.0x19 and high-bit masks remain unplayed even when bit0 is set.
Easy's five-stage Bad Ending and Extra's separate stage6 process are checked
against their own extents; Normal requires six stages and Good Ending.

Current unchanged cold554/31e6b3d7 GNU and optimized UBSan each pass
Easy ReimuA, Normal ReimuA, Normal MarisaA and earned Extra ReimuA. All use
ordinary key-only advice in Mode::ordinary, legal six-life/two-bomb setup,
physical configuration/scores and no actor/hit/life/score/stage/clock writes.
Extra starts from the same-run Normal-earned file in a new process. Each route
has clear mask1 and returns to fresh OP, with no Continue. GNU/UBSan complete
key/19-field MAIN-state/startup/menu/capture and save files agree for all four routes:
72434, 88914, 79214, 29611 admissions, 270,173 per compiler.
These are logical headless routes with render_every0 and retained checkpoints,
not complete pictures, original full-game parity, OS delivery or timing claims.

The executed consumer is554/a79f199f. All553 other maintained inputs,
including every compiled source/header/CMake input and the C++ route helper,
match the frozen producer. Only verify_natural_routes.py changed; no C++ build
or parent producer restamp. The reader explicitly records both identities and
rejects compiled-input differences. Nine public tests and a real complete
Normal trace/file control plus six full-checksum-valid counterexamples reject
missing/wrong-shot/sentinel/high masks, Bad Ending and omitted stages.

Prior failed UBSan/window Normal acceptance stays revoked in its own producer
scope. Current headless GNU/UBSan clear evidence is new and separate. Broader
shots/ranks/death/Continue, original/reconstructed DOS/native campaign parity,
full pictures, physical CPU/I/O/scanout, active-PMD timing and Windows remain
open. Historical exact stays661/663; full reconstruction/migration is active.

Replay: `.analysis/reconstruction/probes/native-natural-clear-v1432/`;
results: `.analysis/worktrees/native-natural-clear-v1432/.analysis/port64/native-natural-clear-v1432/`.
The frozen programs remain under `native-main-pause-v1431-v5`. `comparison.py`
verifies all complete captures and saves; `mutations.py` owns actual-file
counterexamples. Verified content/CRC/mode/nsmtime/temp-restore retirement
saves81.78 MiB net; route/state/input captures recover with
`verify_retention.py --restore --prefix`. All source, programs, saves, plans,
receipts and archive remain retained. Continue paired ordinary-game behavior.
