# TH04 current handoff

Development and the full reconstruction/native goal are active. The user is
using Windows: keep launches muted, use Linux headless/private Xvfb, and do
not open Windows GUI, change focus or inject host keys. Windows acceptance
remains open. Updated 2026-10-12.

## Native elapsed Game Over and Continue/Quit (v1427)

The actual Game Over scene now consumes elapsed time throughout cell masks,
title movement, release/press, Continue menu and final black-out4. Every
frame_delay clears only Count1. Keyboard reset follows the five menu drawing
requests; subsequent menu loops retain pre/post OR and a new press. Shared
Animation handles input_wait(0) and all eighteen fade4 palette publications.
MAIN actor/STD/player/RNG work remains paused. Continue saves before resetting
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
