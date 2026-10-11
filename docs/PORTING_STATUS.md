# Semantic and x64 port status

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

Updated 2026-10-11. The full native goal remains active on `port/modern-64`, in
`.analysis/worktrees/port-modern-64/`. Root `main` keeps the standalone DOS
product and indexes native findings. A root `git push` does not commit or push
native worktree changes.

## Current products and acceptance

| Product | Accepted scope | Remaining boundary |
| --- | --- | --- |
| Historical reconstruction | OP 93/93, MAIN 493/495, MAINE 72/72, ZUN 3/3 authored functions | Function acceptance is not whole-file exactness; MAIN carpet/checkerboard deferred |
| Standalone PC-98 DOS | Four local-source products, repaired normal/invincible packages; user reports complete Normal routes/save | Automated natural dense Lunatic, timing/audio and second-emulator coverage remain separate |
| Semantic readable | Assets, heap, input/timing, scroll, bullets/VM/shots/items, RNG, score and process contracts clarified | Resume only for a concrete native blocker; old exact replay failures remain failed |
| Native x64 | Typed Linux/Windows gameplay, renderer, asset, lifecycle, persistence and sound owners with scoped Oracles | Full physical host/game-route acceptance remains open |

Target files pass local identity/format checks but remain
`candidate-local-attested`; external pristine-dump provenance is unresolved.
No native observation promotes a historical exact unit.

## Native progress

The v1362 GNU Reimu A / Lunatic / Turbo0 candidate is now terminal and
accepted by the independent `verify_natural_slowdown.py` reader: 88,249 route
refreshes plus 792 refreshes in a separate Scores process. It reaches all six
stages without Continue, exits registration by Esc, returns to fresh OP, and
stores real section3 clear mask1 at the physical rename and final file. The nine
other decoded score partitions and CFG stay unchanged; no pending file remains.
Final MAIN: stage5/frame13,649, lives7, misses6, score units5,597,294.

Natural density reaches439 bullets. At >=320 there are571 refreshes/287
slowdown2; at >=400 there are240/129. Complete deadlines/terminal counts pass.
At >=400, update P95/P99/max are6.61/8.50/13.37ms with no update exceeding its
own admission period. This is instrumented GNU/private-Xvfb/shared-WSL evidence;
uninstrumented physical FPS and original DOS parity remain unaccepted. Generic
traces do not expose every inner Ending phase. Audio opens remain zero.

Two actual ordinary X early-hit cancellations occur in Stage4, preserving miss
count while consuming stock, starting Bomb, clearing respawn and setting
invincibility255. The last-life proactive policy branch remains dry-controlled
only. Separate ordinary window probes pass early/closed cases (1,039/1,048
refreshes): early X cancels frame394 hit at395; closed-window X at401 remains
rejected at404 (stock2, Bomb inactive, miss1, respawn61). The first late probe
stays failed: its cleanup incorrectly expected MAIN Esc to return to OP, while
the host Escape handler exits MAIN directly. This is a probe cleanup failure,
not a demonstrated Bomb failure or original Escape-parity acceptance.

Retained GNU Reimu A routes:

| Route | Route + independent Scores refreshes | Scope |
| --- | --- | --- |
| Normal/Turbo1 | 89,008 +794 | Six stages/noContinue, physical clear/freshOP/restart |
| Lunatic/Turbo1 | 88,927 +790 | Physical clear; dense slowdown2 absent |
| Lunatic/Turbo0 | 88,249 +792 | Physical clear plus natural dense slowdown2 gates |
| Extra | 30,388 +790 | NoContinue, full eight A gaiji, physical clear/restart |

Prior UBSan Normal all-clear acceptance is revoked: mask0x19 is an unplayed
sentinel even though bit0 is set. The v1360 GNU Turbo0 attempt also stays failed
(88,267 refreshes, Final Stage miss13, masks0x19); its separate795-refresh
Scores reader and bounded dense slowdown observations remain valid. Require
mask<4 plus the selected shot bit, never bit0 alone. All these jobs are terminal;
do not poll or revive dated PID/tool handles from historical active-job files.

Registration, lifecycle/Continue/HUD, stage/Ending/Extra, score/config, demo,
MusicRoom/unlocks and muted sound owners have separate component/integration
evidence. Eight actual GNU/UBSan Continue cases and ten GNU setup/corrupt-file
cases are retained. Startup combinations cover27 GNU/UBSan and19 earlier
Windows cases. Broader character/shot/rank/Ending/Extra routes, actual Windows
display/input, physical audio and uninstrumented performance remain open.

No C++ rebuild: compiled producer485 inputs/`00af24f7…`, GNU game
`dbe17225…`, UBSan `029e7ba1…`, Windows `5b6cf2c3…` remain v1356. The completed
route uses frozen consumer491/`d25ba16e…`. Actual Bomb probes use archived
consumer492/`3135f76e…`; handoff formatting changes only that Python probe's
layout, preserves its AST, and freezes current492/`4ed57dab…` separately.
Do not restamp old runtime receipts with current source identities.

Primary native receipts: `.analysis/port64/bomb-input-v1362/` (completed route,
independent-natural-v1364.json, actual-rescues-v1364.json) and
`.analysis/port64/bomb-window-v1364/` (early/late/failed probes, independent
readback, both492-input source snapshots). All paths here are relative to the
native worktree. See its `docs/port64/evidence/host-window.md` for replay details.

## Comparison priority for the next agent

The user's primary comparison is **original Japanese DOS versus reconstructed
DOS**, both through the PC-98 game route. Native x64 must also preserve gameplay
state and effects. Native-host equality and successful native clears do not
replace either comparison. Start with the four bundled demos, then bounded
recorded ordinary play; compare score, consumed input, RNG and actor state at
the same logical boundary, followed by VRAM/palette/effects and process/save
transitions. See [DOS/native differential handoff](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md).

TH08 is a read-only workflow reference, not TH04 evidence. Its active worktree
is dirty; do not edit it, run its builds, change its database or launch its game.
Complete trace/end/input-consumption guards and first-divergence diagnostics
are the useful parts to adapt. Retained four-demo DOS traces pass their
full input/score/RNG schema, nine raw actor/effect pools and 22 Boss/Midboss/player
state blocks. Retained DGROUP streams cover3996 updates per demo; scalar traces
also retain each terminal decision. Boss state stays at setup throughout these
demos; death and respawn are not exercised. Other globals, Boss combat and
process teardown remain open.

Raw video comparison retains every graphics/text/palette byte on both pages
at all3996 updates per demo. Text, palettes, page selectors and selected programmed GDC fields
agree. Complete v1372 replay accepts all 38 compared video regions in all four
demos, with 3996 updates and zero differing updates each. The missing Stage 4
lighting-animation cell shifted later cels; the corrected symbolic table
removes all 1032 remaining Demo 1 graphics differences. Cold MAIN changes only
17 animation DATA bytes. Point-number multiplier indices 10/11, packed bullet
boxes and carpet image columns remain verified. Raw scanout timing and process
teardown stay open. Historical
focused point-number replay remains blocked before comparison by an incompatible
bullet/add.cpp header in the old scaffold; it grants no fresh exact credit.

v1373 implements the native point-number pool and event/render joins that were
missing at06922ce. Item pickups select white/yellow and retain base-point/pull
multiplier semantics; bullet zaps insert white numbers. Original CPU controls
at two loads agree on830 complete state/list/request rows and494 full indexed
screens on GNU/UBSan, with two additional full400-slot render cases. Five source
mutants reject. The69 GNU products pass68 CTests; two focused UBSan products
and five headless frontend pictures perhost pass. These are component and
integration-smoke claims, not complete natural original-DOS/native picture
parity. Earlier full-route and Windows receipts retain their own producers.
The same read-only audit finds the native Stage 4 lighting formula already
preserves the original cel 5/column 2 exception. Its component Oracle excludes
original dirty-page transients replaced by full host redraw; paired presentation
acceptance remains separate from the data formula.
Current native host traces still lack complete RNG seed/ring/call-count fields and paired
original-DOS gameplay evidence.

## TODO, in order

1. Extend accepted four-demo original/reconstructed DOS comparison to other
   global owners, remaining raw graphics differences and process teardown, then
   recorded ordinary play covering Boss combat and death/respawn.
   Preserve identical data/config/saves,
   logical input, complete-trace gates and first-divergence diagnostics.
2. Extend the same comparison to native x64. Attest input mapping, RNG ring and
   process state, score units, update order and dialogue boundaries; then compare
   rendering/effects, VRAM/palette and save/process transitions.
3. Expand native full routes across characters/shots/ranks/Endings/Continue and
   Extra. Current accepted GNU Reimu A routes do not cover every combination.
4. Verify uninstrumented natural dense Lunatic performance and broader host
   pacing. The completed Turbo0 instrumented route closes its scoped dense gate.
5. Actual Windows display/input and physical audio remain unavailable under the
   user's no-host-GUI/no-device constraint. Do not launch or work around it.

Historical exactness remains a separate ledger. The two deferred MAIN cases
are not prerequisites for this behavioral comparison.

## Delivery and storage

A fresh experimental current GUI is installed at
`/mnt/d/Entertainment/Game/Touhou/th04-reconstruct/native-port64-v1354/`.
`start-muted.bat` and `start-linux-muted.sh` explicitly mute; independent host
saves and Normal/3-life/2-Bomb defaults preserve all 21 preceding DOS/package
files. Source archives/profiles accompany the binaries. Windows input automation
remains rejected; physical audio, dense timing and full-goal acceptance remain.

v1355 scoped cleanup keeps all 204 programs, producer/consumer source archives,
compiler/CMake metadata, traces, physical files, captures and failed attempts.
It retires 1190 regenerable build files / 70 completed contract-stage files after
two full recovery archives / 144 members read back, net 596836352 allocated bytes.
An independent replay verifies 2847 protected hashes and all 1260 absent files.
The three earlier desktop stages retire 20 files, net 35110912 bytes; the terminal
GUI stage and archived failed consumer materialization retire 494 files,
net 22450176 bytes. Immutable capture sharing keeps 324 complete BMP/PCM paths
and hashes, net 210509824 bytes. Counts subtract their journals/archives but
exclude final receipt size. No original input, accepted program or save deleted.
Post-CI pruning retires 1020 source-backed Python caches, net 16822272 allocated
bytes; root `.analysis/cleanup/host-route-post-ci-caches-v1355.json` records
source/hash readback. Both CIs pass, including root live Ghidra replay/mutations.

Follow [retention](ANALYSIS_RETENTION.md); never blanket-delete `.analysis/`.

Detailed historical batch evidence remains in ledgers, subject notes and Git.
Use [handoff](RE_HANDOFF.md), [semantic contracts](SEMANTIC_READABILITY.md) and
`python3 scripts/status.py` for current authority instead of old progress labels.

Native v1374 additionally accepts four complete original/native MAIN demos on
23 selected before-update/terminal fields and exact RNG counts (15,988 boundaries
per GNU/UBSan host). The Stage 1 midboss now receives the fractional scroll
accumulator. Native v1375 also accepts all nine complete actor/effect pools at 15,984
pre-score updates after restoring Midboss yellow bonus popups. Paired pictures,
other globals, scanout and ordinary Boss/death/process routes remain open.
See the current handoff.

Native v1376 additionally exercises the actual idle OP→four demos→OP FrontEnd,
retaining all15988 selected state/count matches. Raw TRAM revealed a missing
DEMO PLAY label; original timer72/gaiji/position/C3 attributes constrain its
renderer repair. GNU/optimized UBSan compare40 complete label spans including
frames72/73/74.
v1377 aligns the presentation seam after the complete update. All40 sampled
complete8000-byte canonical TRAM planes agree on GNU and optimized UBSan,
including score/HUD; all15988 selected state/count boundaries still pass.
Full graphics/RGB, physical blink/scanout and whole-picture acceptance remain
open. New consumers retain the immutable v1376 compiled producer; see the
current handoff and differential note.

v1378 repairs the missing native Midboss shake event consumer. Original CPU
MAIN_01_TEXT0AAF:2246..2315 agrees on3262 state/movement controls. All15984
complete demo shake globals/requests and prior scalar/nine-pool controls agree.
Demo1 frame3379 diagnostic game-area differences drop55357→430, confined to
top rows16/17; full graphics/RGB and physical scanout remain unaccepted.
Final immutable509-input producer9346e951… is cold-built on GNU; details and
replay are in the differential note and native docs/port64/evidence/demo.md.

v1379 paints the full ordinary400-row background ring before motion, removing
Demo1frame3379 remaining430 game-area differences on GNU/optimized UBSan.
Allselected scalar/shake/text checks remain equal; nine other nonzero samples
are unchanged. Onlyview.cpp is cold-built/relinked against attested unchanged
v1378 dependencies; no new whole-current cold/CTest or fullpicture claim.

v1380 corrects Marisa laser color to the original pre-update modulo, removing
11,384 color differences in four Demo 2 samples; all ten sampled Demo 2 game
areas now agree on GNU/optimized UBSan. Five other nonzero samples remain.
All selected scalar/shake/text checks pass, all 125 captures agree between
variants, and parent state/shake traces remain byte-identical. Only view.cpp
changes among 509 inputs; previous whole cold/CTest/pool evidence retains its
producer. Whole graphics/RGB/scanout and broader pairing remain open.


v1381 restores whole-pool white/purple pellet passes from the original caller
and actual leaf execution. All 40 overlap color differences disappear:
Demo 1 frame3996 32→0, frame1952 34→26. Other 38 complete index/RGB samples
remain unchanged. All scalar/shake/text checks pass on GNU/optimized UBSan;
parent state/shake traces remain byte-identical. Ordinary circles are excluded
at all five former remaining samples. Four nonzero samples and full pictures/
scanout/broader pairing remain open; the bounded view build retains prior core
and whole cold/CTest/full-pool producer identities.

v1382 adds the missing eight-slot item-spawn splash owner and white foreground
dots. GNU/optimized UBSan pass311 originalCPU component cases each and all15984
complete81-byte natural splash records. All103 late-sample pixels disappear;
39 of40 sampled game areas now agree, with initialDemo1 still different. Other37
entire index/RGB samples remain unchanged. Fresh cold GNU71 programs/69CTest
and optimizedUBSan3 core/game/trace/shake products pass all nine full pools,
selected scalars,shake and complete text checks. Old products retain separate
producer identities. Drawing-relative CPU geometry does not accept programmed
GDC/physicalscanout; complete pictures/cache/margins/RGB/broader routes remain.

v1383 preserves Stage4 background draw inputs before the carpet callback and
applies the tail's current/previous row copies from the updated ring. Actual
original CPU controls explain the first 124,439 game-area discrepancies;
48 tail-copy controls cover tile and 400-row wrap. All 40 standard sampled
game areas now agree on GNU/UBSan; all 133,251 first/second-picture changes
equal original indices and 38 entire samples stay unchanged. Ten separate GNU
lighting fields/full text samples agree, repairing 7,498 frame1666 pixels.
Complete scalar/shake/splash/text traces remain unchanged. View-only cold builds
retain separate v1382 whole-cold/69CTest/nine-pool producers. Snapshot-only
edge failure stays unaccepted; full pictures/cache/margins/RGB/scanout/broader
routes remain open.

## Complete RGB diagnostic frontier (v1384)

Native now selects the final MPN stage palette after BMT/BFT setup, including
MarisaST10. Actual GNU/optimized UBSan126 captures match; all40 entire indices/
TRAM and parent state/shake/splash/display/save traces stay unchanged. The fix
changes720358 sampleRGB pixels;40 game-area index diagnostics remain zero.
Independent attested emulator composition retains full rawRGB:12 curtain
samples zero,28 unequal. Explicit DAC projection isolates5×556 Demo-label
blink pixels, not whole-picture acceptance. Recover blink refreshes/liveCG/
textscroll/CRT/scanout before broader picture and ordinary route pairing.
Current509 manifestba6eff48 changes only view.cpp; bounded TU builds reuse
attested v1382 objects. Old cold/CTest/pool/proof identities remain separate.
See the current handoff and focused differential note for replay commands.

## MAIN text blink and independent display clock (v1385)

Native now preserves blink-before-reverse and supplies a persistent display
clock to MAIN text. All15988 native rows replay unchanged GDC source;
80 complete controlled text layers plus8 attribute cases match independent
DOSBox-X output. Original15984 triples expose zero/two-refresh residues;
original absoluteepoch is uncalibrated. FreshGNU71/69CTest and UBSan3cold
produce127 equal ordinary captures with40 unchanged entire indices/TRAM
and6 parent trace/save hashes. Priorfullpool identity stays separate.
LiveCG/textCRT/absolutephase/scanout and broader routes remain open.

## Complete FONT/register and original time observations (v1386)

All 15,984 new original VP4 records carry the complete 516 KiB FONT memory,
eleven text/CRT fields and actual PIC/raster times. FONT is stable. The old
direct asset model fails at 32 ANK V/W bytes; the actual A9 write-port guard
model matches all 528,384 bytes. All 38 old programmed regions match, while
25 complete raw GDC records retain raster differences.

Rendering with the actual FONT/register inputs reproduces the earlier 40
samples. The original period is 17.72322658483988 ms versus native's
17.730496 ms approximation; cadence calibration is the next bounded task.
The 509 product source inputs (a47f0496…) and retained v1385 build/capture
identities are unchanged. Physical scanout, full raw RGB, original phase,
broader routes and historical exact acceptance remain open. See the current
handoff for replay recipes and evidence scopes.

## Calibrated native cadence (v1387)

All 15,984 original GDC/time records reproduce the archived timing model;
native now uses the nearest period, 17,723,227 ns. Fresh GNU69 CTests,
optimized UBSan3 targets and127 identical ordinary Demo files pass. Independent
20,000 scheduling and1,000,000 frontend-refresh controls reject the old cadence;
an actual private Linux window/input route also passes. Producer03351541 has
two changed inputs. Full-font/register references and original selected-state
checks remain retained. RawRGB12/40, DAC diagnostics32/40 and eight phase cases
remain; original common boot/process epoch is the next owner. Physical scanout,
broader paired routes, Windows and historical exact acceptance remain open.

## Original common boot clock (v1388)

Fresh boot/four-Demo capture observes GDC constructors0/0/32 and an immediate
first callback0→1. Blind display-event counts and unchanged counter
body reproduce all15,988 original phases without offsets. Native producer
f2b03ebb admits this initial event; onlyview.cpp changes. FreshGNU69CTest,
UBSan3 and actualfour-Demo127 files pass;126 hashes match the033 parent.

A separate actual FrontEnd recorded-event-clock experiment reproduces all
15,988 count/blink rows, selected state, 40 complete text planes and game-area index diagnostics; whole
index differences remain; explicitDAC
RGBdiagnostics match 40/40, raw RGB 12/40. Oldzero negativecontrol rejects.
Defaultboot/loading/process CPU-I/Oelapsed owners,rawpalette/RGB,physicalscanout,
broaderpairedBoss/death/process andWindows remainopen. The full goal staysactive.

## Native raw RGB palette owner (v1389)

Seven display consumers now use the recorded PC-98 DAC4→6→8 expansion.
FreshGNU69CTest, optimizedUBSan3, actualfourDemo127 identicalvariant files,
privateLinuxXvfb and two-load GameOver/MAINEregistration consumer checks pass.
Only28 fullRGB files differ fromf2; all87 non-RGB files keep old hashes.
Explicitoriginal-clock samples now match40/40 whole rawRGB without projection;
defaultphase matches37/40. Oldlinear sameclock rejects28/40. These are scoped
programmed-frame samples, not physicalscanout/defaultboot/wholepicture acceptance.
Default elapsed-time owners, physical/liveDAC/cross-emulator output, broader
paired routes and Windows remain open. The goal stays active. See the handoff.

## Full OP startup and observer control (v1390)

Native demo validation now runs the Logo and title startup before four natural
demos, then completes a fresh OP title. Cold GNU passes 69 CTests; muted GNU
and optimized UBSan produce 128 identical capture files. Selected state, RNG
and draw counts match both fresh original captures at all 15,988 boundaries.
The analog 4→6→8-bit DAC and 17.723227 ms refresh period retain their prior proofs.

With each original capture's supplied display-event clock, all 40 complete raw
RGB samples match the independent renderer: 80/80 across the fresh pair, without
normalization, crops or fitted offsets. Default full-startup headless captures
match 32/40 and 30/40 against the separate originals. The earlier 37/40 result
applied to compact headless entry against retained V3.

These muted captures use `--pmd-driver none`; PMD measure waits and original
audio timing remain unpaired. Boot/loading/process clock ownership, physical
and cross-emulator scanout, broader paired routes and Windows input/audio remain
open. Development stays active; see the handoff for evidence and cleanup recovery.

Producer: `bdc1fb56f80b1d5d987c89a1cfe63cea9da155eb6ef8eb662c10480dd02c4b5e`. See the differential note and current handoff.
