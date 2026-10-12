# TH04 current handoff

Development and the full reconstruction/native goal are active. The user is
using Windows: keep launches muted, use Linux headless/private Xvfb, and do
not open Windows GUI, change focus or inject host keys. Windows acceptance
remains open. Updated 2026-10-12.

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

## DOS shared SMEM and graph page copy (v1423)

`heap.cpp` now owns the upward SMEM cursor alongside descending HMEM.
`SMEM_WGET` preserves the WORD rounding, shared boundary, segment carry and
AX/CF distinction; zero bytes can return valid FFF8. Release is an unchecked
rewind with all registers/flags preserved. Page copy now borrows this
workspace and keeps the original wrapped-DI count after the first copy.
The mutable DOS reserve also keeps the original small-block branch.

Final producer 1,426/e60c079f uses the 466389e9 cold C++/ASM donor with verified
unchanged-object reuse and a freshly assembled independent far-call ABI.
All 1,242 MAIN/OP/MAINE allocator controls and 160 OP/MAINE page-copy controls
agree with original instructions at load 1000/3333. The real old v1415 page
copy rejects eight zero/exact-capacity controls and keeps eight ordinary
pixel/port controls. Six ABI call bindings, links/MZ/IRQ and MAIN bullet
switches pass. The original failed MAINE near-call producer remains retained.
CI passes all 451 tests, tracking, catalog and private target checks.
Verified compiler/archive and source-backed cache cleanup releases 54.43 MiB
net. Historical authored exact remains 661/663; no game campaign was run.

Replay: `.analysis/worktrees/dos-smem-page-copy-v1423/.analysis/reconstruction/probes/dos-smem-page-copy-v1423/`.
Products: `.analysis/build/smem-page-copy-v1423/` inside that frozen tree.
See [SMEM ownership](reconstruction/product/TH04_NATIVE_HEAP_V863.md) and
[page copy](reconstruction/product/TH04_NATIVE_GRAPH_COPY_V862.md).
Continue remaining function recovery and native scene integration.

## Retained producer routing

| Subject | Retained producer | Evidence and recovery |
| --- | --- | --- |
| Registration numeral requests/WORD slots | v1429,548/fc9b02eb | VSync note, `native-numeral-slot-v1429` full controls/recovery |
| Full Game Over/Continue/Quit | v1427,544/4a62eb34 | VSync note, `native-gameover-elapsed-v1427` receipts |
| MAIN good/bad/Extra elapsed fade16 | v1426,543/70986a2b | VSync note, `native-main-exit-fade-v1426` receipts |
| Cutscene/Ending elapsed requests | v1425,542/59d19121 | [VSync note](reconstruction/product/TH04_NATIVE_VSYNC_V864.md), `native-cutscene-elapsed-v1425` receipts |
| Staff elapsed dissolve/measure | v1424,541/83933826 | VSync note, `native-staff-elapsed-v1424` receipts |
| Verdict/Congratulations and MAINE waits | v1423,540/bc9bb404 | VSync note, `native-maine-demo-word-join-v1423` receipts |
| Demo WORD blackout/indexed DAC entry | v1421/v1420 | [Porting status](PORTING_STATUS.md), scoped original fade/palette controls |
| Palette, IRQ and ordinary/Gaiji text owners | v1407–v1419 | Porting status and VSync note; each original/DOS/native producer retains its own identity |
| DOS SMEM/HMEM and page-copy workspace | v1423,1426/e60c079f | [Heap](reconstruction/product/TH04_NATIVE_HEAP_V863.md), [page copy](reconstruction/product/TH04_NATIVE_GRAPH_COPY_V862.md) |

Prior phase descriptions are historical producer scope. They do not override
current remaining work above. Full receipts live under ignored `.analysis/`;
[retention recovery](ANALYSIS_RETENTION.md) routes verified archives. Earlier
handoff detail remains in Git and the focused subject notes.

## Retained acceptance and next work

Historical authored acceptance remains 661/663: OP 93/93, MAIN 493/495,
MAINE 72/72 and ZUN 3/3. MAIN carpet/checkerboard are deferred. Function
acceptance does not imply whole-file exactness. Targets remain
candidate-local-attested; pristine-dump provenance is unresolved.

Retained original/reconstructed DOS bundled demos agree on consumed input,
score/RNG, nine complete pools, 22 state blocks and every configured video
region at 3996 updates each. These paths exercise Midboss; Boss combat,
death/respawn and complete process transitions still need paired checks.
Native selected-state/pool/shake/splash and sampled game-area results retain
their original frozen producers; default route hash equality here is scoped
regression, not new complete-picture acceptance.

Older native original instruction/pixel/font corpora and Linux
Normal/Lunatic/Extra/save/restart routes retain their frozen producers. The
previous UBSan Normal-clear claim remains revoked: mask0x19 is a sentinel;
require mask<4 plus the selected shot bit. Current component route acceptance
above does not restore that full-route claim.

Continue bounded function recovery and native scene integration, then paired
original DOS/reconstructed DOS/native behavior checks. Preserve Windows host
focus, original inputs, saves, shared writer worktrees and frozen evidence.
TH08 stays read-only. Serialize actual builds and clean owned intermediates
only after their journals and recovery checks pass.

## Commands and navigation

Run python3 scripts/preflight.py before target-dependent work, then the
focused comparison, python3 scripts/ci.py and git diff --check. Use fresh
probe namespaces, CPU1/nice19, one Borland/Wine writer and muted headless runs.
See [differential evidence](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md),
[VSync ownership](reconstruction/product/TH04_NATIVE_VSYNC_V864.md),
[retention recovery](ANALYSIS_RETENTION.md), [workflow](RE_WORKFLOW.md)
and [subject index](reconstruction/README.md). Earlier chronological handoff
material remains in Git and the focused notes; it is not the live work queue.
