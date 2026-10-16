# Semantic and x64 port status

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

Updated 2026-10-17. The full native goal remains active on `port/modern-64`.
The latest verified route snapshot was recorded under
`.analysis/worktrees/native-natural-clear-v1432/`, but the 2026-10-16 audit
found the entire old worktree directory absent. Root-level reports/archives and
published source remain; frozen programs and 94 protected route files need
recovery before complete replay. See [new-agent handoff](NEXT_AGENT_HANDOFF.md).
Historical sections below retain their producer scope and original paths.
Root `main` keeps the standalone DOS
product and indexes native findings. A root `git push` does not commit or push
native worktree changes.

Original/reconstructed DOS ordinary Stage1 now passes two repeated pairs at
3,996 updates, including two natural deaths/respawns and ordered RNG calls
(v1434). The keyboard adapter observes original OP menu count64; prior startup
seed mismatches remain rejected. This headless hardware-keyboard fixture does
not accept complete actor pools/pictures, Boss combat, campaigns or Windows.
New v1435 full DGROUP captures additionally agree on nine complete pools and22
state blocks, with three pools empty. Aggregate acceptance stays rejected for156
post-reset input differences despite equal consumed inputs and scalar controls.
Current v1436 additionally passes all configured full VRAM/text/palette/display
regions for the ordinary fragment including deaths/respawns. Raw GDC timing
still differs every frame; companion post-reset input differs at155samples.
Boss/full lifecycle/physical/Windows stay open. A v1437 bounded7,500-update pair now covers actual Boss phases0/1/2 with
matching input/RNG/pools/states and258 retained post-reset input differences.
Original naturally reaches Game Over at7547; held Shot waits for release in
that UI, not a confirmed IRQ fault. Boss pictures/defeat and paired process
routes remain open. Native full-picture acceptance remains separate;
see [current handoff](RE_HANDOFF.md).

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

See the [bounded differential evidence](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md).

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
every frame, physical scanout or campaigns. Primary DOS beyond this bounded suffix, native Stage2 update 9836, NP2, Windows, pristine provenance and
historical exactness remain open. Both full development goals remain active.

See the [bounded differential evidence](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md).

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

## Historical title gates (v1450; BB phase inference withdrawn)

Clock/string/row and complete primitive observations remain valid. The old
constructed natural-BB interpretation and its source preview are refuted by
v1451 actual entries/pictures. The archived first "negative" uses the correct
pre-scroll phase. Old receipts/source/programs/journals remain immutable; use
the focused differential note for the correction and replay context.

## Historical native natural routes and strict clear gate (v1432)

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

Published native head: `c0a1060371c5f8ba758ca8b10f6cbc99063ba3d6`.

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

Published native head: `853e012509849ae2f218972594e67eb6fd591ceb`.

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

Published native head: `58383ea13fc6d5b942777c9a4cbbc01097e2d571`.

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

Published native head: `7db5699ef72067848ad4970bbf0e8da9d69e6c56`.

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

Published native head: `e8b0a2c17090ba639bba44fbccc64c48838b8dc0`.

## Native elapsed Game Over and Continue/Quit (v1427)

The actual Game Over scene now consumes elapsed time throughout cell masks,
title movement, release/press, Continue menu and final black-out4. Every
frame_delay clears only Count1. Keyboard reset follows the five menu drawing
requests; subsequent menu loops retain pre/post OR and a new press. Shared
Animation handles input_wait(0) and all eighteen fade4 palette publications.
MAIN actor/STD/player/RNG updates stay suspended during this scene. Continue saves before resetting
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

Published native head: `26ab740fe4dcb473643d63149f462193f6020a3f`.

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

Published native head: `a25591759592837971901699e9a3342aeca73071`.

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

Published native head: `9caa2dbb633fa48e130bb92bbbf060a39a7c10a9`.

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

Published native head: `bd67182a844a4c6c5a8d6c23954d240ce3b05e25`.

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

Published native head: `c97cced9e61cb5d32998da13996cfd11faebc2b4`.

## Complete native Demo blackout WORD behavior (v1421)

Published `port/modern-64`: `b5fa7d8`.
`demo::Fade` now truncates speed to WORD, applies the original signed condition,
and waits once before every blackout. Zero and negative WORD speeds then
publish all eighteen tones on the same admission. Positive speed keeps
`1 + 17*speed` refreshes. All nineteen tone writes remain, including the
transient -2 immediately before final zero. The actual entry caller consumes
the palette publication sink and paints its retained indices.

Cold GNU and optimized UBSan producer 538/07b8ebd6 each build the complete
core/frontend and two selected contracts. All 48 retained OP/MAINE
0000:0666..06A4 original blackout controls agree with twelve native vectors:
216 publications, 228 tone stores and complete waits per compiler. The actual
6307e8d Demo owner rejects seven vectors under a bounded clock. Both actual
entry captures retain all eighteen frames/4,608,000 DAC-projected pixels,
with no MAIN update. Native CI 345 passes; historical exact remains 661/663.

Replay: `.analysis/worktrees/native-demo-fade-word-v1421/.analysis/port64/native-demo-fade-word-v1421/`.
Full wait carriers, source/programs, current images and 7,854 parent pins are
retained. Verified compiler/cache cleanup releases 35.46 MiB net. Continue
remaining actual scene-wait integration and function recovery; this is a
logical refresh/publication model, not physical IRQ/CPU timing acceptance.

## Native indexed demo-entry fade (v1420)

Published `port/modern-64`: `6307e8d48adc58b7073699e9d93549c37c03898b`.
Demo entry now keeps the raw menu palette and pixel indices. Each fade step
uses the original four-bit DAC tone conversion before expanding colors to
RGB8. It replaces the old scaling of cached RGB8 pixels.

GNU and optimized UBSan each capture eighteen actual pending OP frames,
stopping before MAIN updates. All 4,608,000 pixels agree with the projection
of 36 complete original OP 0000:1DE0..1EEA palette instruction controls at
loads 1000/3333. Pixel indices, process generation and RNG stay fixed through
the fade. The old RGB8 formula projection differs in sixteen frames; this is
an explicit formula diagnostic, not a compiled predecessor or full original
OP scanout comparison.

Cold source 537/08ff3fc2 builds the complete core/frontend and two related
contracts per compiler. Final 537/6175165a fixes only the reader and capture
include; both frontends recompile while their original core hashes stay
identical. Initial reset-schema/storage-setup failures, old frontends and both
source freezes remain. Native CI 345 passes; historical exact stays 661/663.

Replay: `.analysis/worktrees/native-demo-palette-v1420/.analysis/port64/native-demo-palette-v1420/`.
`verify_closure.py` reads all original I/O and full images, both source archives
and 6,893 parent pins. Verified compiler/cache retirement releases 35.92 MiB
net. Continue remaining function/caller recovery and actual scene waits;
physical scanout and broader gameplay remain open.

## Joined native palette output and counter delays (v1419)

Published `port/modern-64`: `85fe1f30af27a1aee1a8822f2e950c95cafa2a11`.
Shared `pc98_palette::show()` restores the three complete 266-byte originals:
MAIN 0000:1F04, OP 0000:1DE0 and MAINE 0000:19EC. It keeps signed WORD
truncation, tone clamping, analog output and the notebook LCD branch with its
original masks, weighting, query polarity and port order. Startup's actual
DAC consumer and six other display consumers use this source.

Fresh joined producer 536/3ba0ba42 retains the published live WORD delay and
bulk IRQ owner. GNU Release and optimized UBSan/bounds each cold-build the
complete core/frontend and nine related programs, pass nine selected CTests,
and agree on 20,832 retained original palette I/O/DAC controls. Each also
passes 144 original delay consumers, 36 real ISR controls and 2,008 independent
integer/raster vectors. Native CI passes 345 tests. The actual prior startup
source rejects 288 of 1,368 analog controls. Historical exact stays 661/663.

Replay is under each owned tree's `.analysis/port64/`, in
`native-palette-show-v1418` and `native-palette-show-join-v1419`.
The original v1415/v1417 captures keep their own source identities. Current
source freezes, selected programs and 5,945 parent pins remain; verified
compiler/cache retirement releases 101.02 MiB net across both producers.
Continue shared elapsed scene-wait ownership. Physical LCD scanout, broader
paired routes and Windows remain open; this recovery ran no game campaign.

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
broader Boss/death/process, physical LCD scanout and Windows remain open.

Published native head: `dcbe8f73c0a5e36b93fc2117252ffe71055e7c71`.

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

Published native head: `c2d8363606d73090f2ad47062788a5b497622647`.

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

Published native head: `9a7f380a2ef7d947dec2207f0552effcf01d032b`.

## Combined DOS text and VSync recovery (v1411)

Current MAIN/OP/MAINE include both mutable `TextVramSeg` reads and the
installed-owner VSync wait. Serial rebuilding compiles changed source freshly
and validates reused objects; links, IRQ audits and MAIN bullet tables pass.
Producer 1,425/82ade790 passes 3,156 ordinary-text, 2,656 Gaiji, 528 VSync wait
and 324 lifecycle comparisons. All four complete ordinary-text bodies retain
the original MAIN match after mapping the text-variable data operand.

The isolated `dos-text-vsync-join-v1411` tree retains source, products/MAPs,
wait OMFs, full transcripts and replay/retention readers. Its closure also
checks 776 frozen text-only and 858 frozen wait-only files independently.
See [text recovery](reconstruction/product/TH04_NATIVE_TEXT_CHARACTER_V1409.md)
and [VSync recovery](reconstruction/product/TH04_NATIVE_VSYNC_V864.md).
Historical authored exact remains 661/663; native stays at 328585f.
Verified retirement reclaims 33.45 MiB from the combined compiler/cache
copies; temporary v1410 restores return to their existing archive.
Continue native scene waits and hardware owners before long game campaigns.

## Frozen DOS installed-owner VSync wait (v1408)

Shared `vsync_wait.cpp` now chooses the original branch once at entry:
installed IRQ waits for any unsigned Count1 change; otherwise it waits for
the next GDC blank. Neither path clears Count1/Count2. The owner is a public
byte alias of START/END's existing saved PIC mask, with no additional storage.

Cold all-four-product producer 1425/d9383fa5 passes links, MZ/IRQ audits and
MAIN bullet tables. Complete original MAIN 0000:2462, decoded OP 0000:2648
and decoded MAINE 0000:2206 each have 38-byte waits; compiled contributions
are 49 bytes. Three-artifact comparisons pass 528 controls at loads 1000/3333,
including 72 real ISR/IRET injections and 24 midwait owner changes. Existing
START/IRQ/END retains 324 controls. The real polling-only predecessors each
reject 136 installed-owner cases while their 40 unowned cases still agree.

Fresh muted four-Demo runs pass all 15,988 original consumed-input/score/RNG
boundaries. This is a selected-state regression; earlier whole-pool/video
acceptance retains its own frozen producer. Raw register differences are
recorded, including different artifact DS layouts and incidental AX/DX/FLAGS;
no complete register, byte-exact or physical latency claim is made.

Replay index/products: `.analysis/reconstruction/probes/dos-vsync-wait-v1408/`.
`focused.json`, `negative-final.json` and `demo-regression.json` record commands;
`verify_retention.py --restore --prefix <owned path>` restores archived inputs.
Verified retirement reclaims 52.39 MiB from 3,584 owned paths/1,450 blobs.
Stopped observer diagnostic logs separately reclaim 346.77 MiB losslessly.
Final products/MAPs, wait OMFs, original/compiled transcripts and failure
readers remain. See [VSync recovery](reconstruction/product/TH04_NATIVE_VSYNC_V864.md).

Both isolated and published-main CI pass 451 tests, targets/calibration,
ledgers and catalog. Live-main Ghidra/JDK, MAIN database and mutation gates
also pass; all three original databases were attested before work.
Source-backed own/main caches reclaim another 8.49/8.52 MiB, bringing this
batch to 416.18 MiB net. Frozen DOS 30-file and native 1,235-file parent
closures retain their hashes. All 1,425 live-main input files match the cold
producer byte for byte after four pre-existing EOL representations are journaled and
normalized to Git/attributes LF; logical Git source is unchanged by that step.

Historical exact remains 661/663. The text-variable gap is closed in v1411
above; native scene waits, physical timing, broader routes and Windows
acceptance remain open.

## Frozen DOS ordinary text writers (v1410)

Both text ASM owners now read the maintained `TextVramSeg` instead of adding
a fixed A000h. The character writer keeps its full WORD ANK/JIS/Shift-JIS
conversion; the string writer keeps its lead-byte handling, store order,
wrapped attribute count and far Pascal ABI.

Cold MAIN/OP/MAINE builds pass links, IRQ audits and MAIN bullet tables.
The complete 87-byte character body in all three products and the 114-byte
MAIN string body agree with original MAIN after mapping only the text
variable's data offset. MAIN passes 1,680 full memory/write/ABI comparisons
at loads 1000/3333; OP/MAINE each pass 738 against the shared MAIN character
contract. The prior Gaiji owners retain 2,656 original comparisons.
The compiled v1407 MAIN predecessor differs in all 80 alternate-base controls,
including return ES. Far strings use independent RAM outside the loaded image.

Producer 1,425/451a46f7 and selected products are in the isolated
`dos-text-character-v1410` tree. Complete records and readers are under
`.analysis/reconstruction/probes/dos-text-character-v1410/` there. See
[text writer recovery](reconstruction/product/TH04_NATIVE_TEXT_CHARACTER_V1409.md).
Historical authored exact remains 661/663; native remains at 328585f.
CI passes 451 tests. Verified retirement reclaims 21.14 MiB net; complete
current records and 30 frozen DOS parent files retain their hashes.
Join these writers with the recovered DOS VSync owner above and verify
the combined producer before long game campaigns. The full goal stays active.

## Native ordinary text writers (v1409)

`TextPlane` now recovers the complete WORD character input and the original
Shift-JIS byte-stream conversion. It preserves mutable text bases, WORD
addresses, NUL handling, malformed pairs and glyph/attribute aliases. HUD,
Game Over and the real frontend use the recovered character writer.

All 65,536 WORD characters and 65,536 two-byte strings agree with original
MAIN 0000:229E/22F6 on both visible banks. A separate 840-case corpus agrees
on complete 80000h..DFFFFh memory at loads 1000/3333: 1,680 comparisons.
Cold GNU and optimized UBSan/bounds reproduce the results; prior Gaiji retains
all 2,656 comparisons. The frontend builds, six component contracts and
native CI 345 pass. No game campaign was needed for this function recovery.

Native `port/modern-64` is at 328585f, producer 526/3e7d5e33. Complete evidence
is in `port-motion-v1402/.analysis/port64/native-sjis-text-v1409/`.
Verified cache retirement reclaims 14.50 MiB net; the closure reader checks
all current proofs and 780 frozen parent files. See
[ordinary text recovery](reconstruction/product/TH04_NATIVE_TEXT_CHARACTER_V1409.md).

Original instructions read `TextVramSeg` at DGROUP 2134:0768. The DOS ASM
references are recovered by v1410 above. Historical authored exact acceptance
remains 661/663. The full reconstruction/native goal stays active.
The palette VSync review remains a separate frozen producer.
Root CI passes 451 tests and the updated ledgers; target preflight passes.

## Native text Gaiji migration (v1408)

`TextPlane` now uses the original WORD addresses and glyph/attribute sequence,
including row spills, mutable text bases and wrapped string attribute counts.
Sparse pages preserve writes outside the directly stored visible banks used
by HUD, Game Over and score registration.

All 664 native fixtures match 2,656 original MAIN/MAINE memory results at
loads 1000/3333. Optimized UBSan/bounds reproduces them. Cold core/five
programs, five related contracts and native CI 345 pass. The compiled
predecessor rejects edge and 2,049-character controls; the rejected string's
partial visible banks agree, so complete memory and failure status matter.

Native `port/modern-64` commit 8f7f7d5 has producer 524/6f214e8c. Proofs:
`port-motion-v1402/.analysis/port64/native-text-address-v1408/`. Verified
cleanup reclaims 13.04 MiB net, with complete proofs and frozen parents intact.
See [text writer recovery](reconstruction/product/TH04_NATIVE_GAIJI_TEXT_V860.md).
The v1409 ordinary-text recovery above extends this owner. Historical exact remains 661/663.
The palette VSync review below is a separate frozen producer, pending integration.

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
controls at load 1000/3333 and432 independent ideal raster/cadence vectors
(1296 waits), including FFFF-to-zero and status/IRQ edge separation.
Count1/GDC inputs are explicit consumer stimuli, not measured physical IRQs.
The real48e05da startup predecessor fails the new counter-retention contract.
Eight fresh muted startup/fourDemo/freshOP routes retain all129 output hashes
per profile from frozen v1404; each passes15988 original selected-state boundaries.

The first cold build failed the valid-final-edge overflow contract (74/75).
Its source/program/logs remain frozen; v2 repairs exhaustion and passes.
This batch changes native wait/startup source, with no new DOS product or
historical exact promotion. The older25-byte compiler-service observation describes only the polling
producer, not the complete original function. At that frozen native producer, shared DOS was polling-only. The separate
v1408 DOS cold replay above now recovers its installed-owner branch.
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

## Retained DOS text Gaiji recovery (v1407)

`gaiji_text.cpp` now restores the mutable text base, original store order,
wrapped attribute count and return ES for `GAIJI_PUTCA/PUTSA`. Original
MAIN and MAINE match all 2,656 complete memory/write/state controls at
load 1000/3333, including long strings whose glyphs alias attributes.
The compiled predecessor has 40 final memory differences and 426 ES differences.
The previous graphics Gaiji functions retain all 4,800 controls with the new
OP/MAINE products.

Three affected products were rebuilt with freshly compiled changed source
and verified unchanged-object reuse. Links, IRQ audits and MAIN bullet tables
pass. Product inputs are 1,425 files / fb50205b; ZUN keeps its prior product.
Historical exact remains 661/663. The full goal stays active.

Replay index: `.analysis/reconstruction/probes/dos-text-gaiji-v1407/`;
products: `.analysis/build/th04-text-gaiji-v1407/`. See
[text Gaiji recovery](reconstruction/product/TH04_NATIVE_GAIJI_TEXT_V860.md).
The native `TextPlane` migration is indexed in v1408 above.
Continue function recovery before long game campaigns.

Root CI passes 451 tests, ledgers, catalog and private target/database checks.
Verified archiving retires 7,143 owned cache paths; source-backed Python
caches bring cleanup to 38.00 MiB net. Complete original/compiled memory
transcripts, selected products and frozen parent proofs remain.

## Previous DOS Gaiji recovery (v1406)

`src/shared/hardware/graph_gaiji.cpp` now preserves continuous string byte
addresses, WORD/spill writes across FFFFh and return ES. Original OP and MAINE
entries agree with the final linked products on all 4,800 component controls
at load 1000/3333. The compiled predecessor has 150 address-mask differences;
write-width and ES comparisons reject all 2,400 predecessor controls.

Both affected products were cold-built, then the ES correction freshly compiled
Gaiji with verified unchanged-object reuse. Final OP/MAINE links and IRQ audits
pass. Product inputs are 1,425 files / cfaa77bf; MAIN and ZUN keep their prior
frozen products. Historical exact remains 661/663. The full goal is active.

Replay: `.analysis/reconstruction/probes/dos-gaiji-v1406/`; final products:
`.analysis/build/th04-gaiji-v1406-final/`. The maintained
`scripts/runtime/verify_dos_gaiji.py` compares actual original/product
instructions. The phase's `verify_closure.py` checks source/program pins and
complete transcript carriers. See [Gaiji recovery](reconstruction/product/TH04_NATIVE_GRAPH_GAIJI_V861.md).
Continue function and native-owner recovery before long game campaigns.

Root CI passes 451 tests, ledgers, catalog and private target/database Oracles.
Lossless retirement removes 5,565 owned cache paths after archive and
metadata readback; 629 protected files and final closure still pass.
Source-backed Python caches add 8.48 MiB reclamation;
combined cleanup is 31.14 MiB net. Programs, MAPs and complete proofs remain.

Native `port/modern-64` is at 8f7f7d5, including GRCG, font and Gaiji
address recovery. The separate startup/motion integration on
`review/startup-motion-join-v1403` is frozen at 514 files / c2f8d689.
Its verified snapshot predates those renderer changes. Attest a combined
producer when integrating the two histories. The v1401 startup implementation
already reached `port/modern-64` through fffcc83.

v1403 integrates remote motion recovery a0b6149 with the independently
validated startup waits. Verified integration producer514/c2f8d689 is frozen;
CMake's new motion contract and its verifier are now both included in the
complete source manifest. Fresh GNU builds73 programs/71CTests; optimized
UBSan builds10 programs/7 contracts. Unchanged original MAIN0000:1DA8..1E13
and table2134:021E execute at load 1000:184908 vectors per compiler agree,
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
No old receipt was edited to claim the new producer. The frozen DOS parent
is a34c1357; current v1406 source is indexed above.
Historical exact counts/canonicality are unchanged.

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

Retained v1401 native producer is512/60cf4491. OP startup now waits on the
independent unsigned IRQ owner and services PMD at timer deadlines within an
elapsed admission. It preserves inherited Logo counts and clears inactive zero
fallbacks. Cold70GNU/6UBSan contracts, three compiled negative controls,
132 frontend configuration/restart cases and eight full four-Demo routes pass.
Each route matches original selected state at15988 boundaries. Only startup
and text-clock traces change for PMD profiles; other127 outputs remain equal to
frozen v1399. No-driver retains all129. Current GNU/UBSan outputs match completely.
Default loading/graphics/CPU costs, physical timing and other scene adapters
remain open. Frozen v1400 DOS source is retained; its three-artifact108-case and
four cold product/Demo evidence remains separately pinned. See the handoff.

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
Later four-demo observations pair selected input/score/player/RNG state and
nine complete actor/effect pools with original DOS. Broader ordinary gameplay,
complete pictures and process transitions remain unpaired.

## TODO, in order

1. Extend accepted four-demo original/reconstructed DOS comparison to other
   global owners, full scanout timing and process teardown, then
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

The previously delivered experimental GUI package is retained at
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
dots. GNU/optimized UBSan pass311 originalCPU component cases each and all 15,984
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

## Retained physical configuration and startup clocks (v1391)

Native development is active. Demo validation now loads the physical
configuration before running one Logo, four natural demos and a fresh OP title.
Nine observed OP/MAIN configuration requests match the incoming file; complete
CFG and score files stay unchanged. Cold GNU passes 69 CTests. Each of four
muted driver profiles (`none`, `pmd`, `pmdb2`, `pmd86`) produces 129 identical
GNU / optimized UBSan capture files, with selected state, RNG and draw counts
matching all 15,988 original boundaries.

The active PMD profiles spend 94 native refreshes between the measure request
and first SUPER_load; `none` spends zero. Original PMD measure/audio timing
remains unpaired. A one-call configuration bypass keeps all previous 128 files
identical but uses the wrong rank at every configuration point; the new
independent option check rejects it.

A same-source original zero-delay repeat shifts refresh ordinals by 8 relative
to the prior baseline. The prior delayed pair shifted by 5 or 6. That shift
cannot uniquely diagnose inserted sleep; keep each capture's clock separate.
With the fresh original's supplied clock, all 40 complete raw RGB samples match
an independent renderer without normalization, crops or fitted offsets.
Default native counts are 31/40 for `none` and 34/40 for the active profiles;
these are timing diagnostics. Prior 80/80 supplied-clock evidence retains its
original producer identity. Boot/loading/process clock ownership, physical
and cross-emulator scanout, broader paired routes and Windows input/audio
remain open. See the handoff for scoped evidence and cleanup recovery.

Retained producer: `c6a90f57e662cbbe85cec9b55047f0ffce5df818067725f687b548f4d2579010`. Native commit: `927ce48`.
See the handoff and focused differential note for evidence and recovery.

## Cold PMD installation and original OP timers (v1392)

Native development is active. The application PMD driver now installs from cold
chip state and applies installation writes to both logical timers and PCM.
Read-only original OP captures show the first Timer B period is **73.728 ms**;
the previous native state incorrectly began at 16.128 ms. Two independent
installation controls reject the old state and the PCM-only update.

Cold GNU passes 69 CTests; optimized UBSan passes three PMD contracts. Four
muted driver profiles each produce 129 identical GNU / UBSan capture files.
Demo state, RNG, draws, shake and physical configuration/save files remain
identical to the retained original-paired captures at all 15,988 selected seams.
One Logo and five completed titles include the final fresh OP ready.

Default active-PMD waiting now spans 97 native refreshes; the bounded original
OP captures span 92. This is not full startup-clock acceptance: original CPU
and file-loading time still need paired owners. Complete default RGB matches
remain 31/40 for none and 34/40 for active profiles; own-counter-phase 40/40 is
diagnostic. Earlier supplied-original-clock matches retain their original
producer identity. Broader paired gameplay/process routes, physical scanout
and Windows input/audio remain open. See the handoff for evidence and cleanup.

v1392 producer (unchanged in v1393): `9cfe100a84ac0a325d498b9b81602298009e462643b2cfa453947fe85bc1b049`. Native commit: `28b3f95`.
See the current handoff and focused differential note for complete scoped evidence.

## Original OP loading work and clock owners (v1393)

Native development is active. The repaired PMD application still installs from
cold state with the original observed 73.728 ms first Timer B period. New
read-only OP captures separate startup loading and drawing work: changing only
CPU budget from 24,000 to 36,000 reduces the Logo PI load phase from 66.98 to
44.62 ms and its drawing phase from 61.66 to 41.04 ms. Gaiji work scales
differently; there is no universal startup-delay constant.

The unchanged native producer retains its cold GNU 69 CTests, three optimized
UBSan PMD contracts and four driver-profile Demo comparisons. New GNU / UBSan
service probes with each original's measured installation age agree within
1 ms sampling; zero-age controls complete but fail the same timing check.
These diagnostics do not pair default native loading clocks. A real interrupted
GDB capture exited zero without completion; the new reader rejects it.

Retained Demo state/RNG/draw/shake/configuration/save evidence covers 15,988
selected seams. Complete default RGB counts remain scoped diagnostics, with
broader gameplay/process, physical scanout and Windows input/audio still open.
See the handoff for current evidence, limits and cleanup recovery.

Unchanged native producer: `9cfe100a84ac0a325d498b9b81602298009e462643b2cfa453947fe85bc1b049`. Native evidence commit: `7416a91`.

## Original Gaiji I/O elapsed work (v1394)

Development remains active. Four fresh original OP captures isolate the
emulator I/O owner: default Gaiji loading is 40.235458 / 34.996667 ms at fixed
24,000 / 36,000 cycles; only changing 8-bit I/O delay to zero gives 17.134000 /
11.404611 ms. Actual 8,192 read / 25,604 write accesses and pinned integer debit
rules account for 22.829167 / 23.412333 ms of Gaiji work. Complete loaded target,
GDC replay, raw PIC clocks and negative controls pass. This is DOSBox-X timing,
not a physical bus or fitted native wait.

Native source remains the 510-file `9cfe100a` producer; this batch changes only
evidence/docs and adds the ROOT Gaiji verifier. Next establish elapsed-work
handoffs across native asset loading, drawing and process entry. Previous
GNU/UBSan/Demo/window proofs keep their old producer identities; default clocks
and broader fidelity remain open. See the handoff and focused differential note.
Native evidence commit: de21a71.

## Resident elapsed work through OP (v1395)

Explicit resource/graphics/process intervals now advance resident Timer/PCM
across process gaps and local mix during a process, flushing pending wait once.
Actual maintained OP frontend callers using independent original v1393 work
inputs pass in GNU/UBSan. PLAY epochs of 255.036542 / 178.822806 ms and
93-refresh readiness have sample errors of 3.648611 / 8.074889 ms, within one
frontend refresh. Zero and graphics-only controls complete but fail the same
epoch gate; removing graphics can still alias 93 refreshes. Default work
adapters remain empty.

Current cold GNU builds 71 programs and passes 69 CTests; optimized UBSan
builds seven targets and passes four sound contracts. Eight default captures
across four driver profiles reproduce all 129 retained outputs each. Private
muted Linux Xvfb passes with zero audio device opens. Default resource/GDC
pairing, full pictures and broader routes remain open.
Native manifest: 55459c6f487e25ce39e0b8499b89f52936e0273c536905e94b8a7764426fdb7e.
Native commit: 955de04.

## Display time through OP loading work (v1396)

Explicit work now advances both resident sound and headless GDC text time,
retaining fractional refresh time. Independently observed first-display-to-PMD
epochs plus original work reproduce all twelve OP loading/readiness counter
assertions per CPU input in actual maintained frontend GNU/UBSan executions.
A display-only control preserves sound timing but rejects display counters.
External observation retains fractional origin and excludes double admission.

Cold GNU 71 programs / 69 CTests, optimized UBSan seven selected targets / four
sound contracts, sixteen actual callers, eight default four-profile captures
and private muted Linux Xvfb pass. All 129 default outputs per run retain their
v1395 identities. Default CPU/bus/resource/graphics costs and wait-edge
semantics, full pictures and broader routes remain open.
Native manifest: ea5c016d0cd40bcb453bd9f6c27c6ec24c2513ec63342fa8be2fa8d6acc85d43. Native commit: 49b2fa5.

## Distinct original OP waits (v1397)

Three complete original routes (FM86 CPU24000/36000 plus BGM-off CPU24000)
show active measure polling preserves Count1, so the first Logo wait inherits
104/100 and returns with zero new counted interrupts. BGM-off frame_delay(0)
clears Count1 and returns immediately; loading leaves Count1=1 before Logo.
Count1 clears after Logo waits while Count2 continues. Two counted IRQs can
cross one GDC observer seam; preserve their distinct phases.

Independent public wait reader and counter/PIC/GDC mutation controls pass;
product source remains v1396 native49b2fa5/ea5c016d and DOS6f5898dd. Native
refresh-sampled measures and fixed two-tick Logo waits still need replacement
by the proved busy-service / IRQ-count owners. No new build/full-picture or
exactness claim. See current handoff, focused differential note and retention.

Native documentation commit: `19e5356`; the product source producer stays
`49b2fa5` / 510-file `ea5c016d`.
