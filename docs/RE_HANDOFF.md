# TH04 native branch handoff

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

## Retained native producer routing

Earlier Cutscene, Staff, MAINE, Demo, palette, IRQ and text producers
retain their original source/evidence identities. See the [VSync note](reconstruction/product/TH04_NATIVE_VSYNC_V864.md), [porting status](PORT64.md), and the subject index. Prior handoff detail remains in Git;
current open owners are listed above. Archives restore into fresh paths.

## Comparison priority for the next agent

The user's primary comparison is **original Japanese DOS versus reconstructed
DOS**, both through the PC-98 game route. Native x64 must also preserve gameplay
state and effects. Native-host equality and successful native clears do not
replace either comparison. Start with the four bundled demos, then bounded
recorded ordinary play; compare score, consumed input, RNG and actor state at
the same logical boundary, followed by VRAM/palette/effects and process/save
transitions. See [paired demo evidence](port64/evidence/demo.md).

TH08 is a read-only workflow reference, not TH04 evidence. Its active worktree
is dirty; do not edit it, run its builds, change its database or launch its game.
Complete trace/end/input-consumption guards and first-divergence diagnostics
are the useful parts to adapt. Retained DOS demos accept complete selected scalar/pool/video comparisons.
Retained native producers accept selected scalar/RNG/count fields and nine
complete pools. v1385 preserves the six parent trace/save hashes and 40 entire
index/TRAM samples; whole pictures, original display epoch and broader
gameplay/process routes remain open.

## Replay and finish

```sh
python3 scripts/preflight.py
python3 scripts/ci.py
git diff --check
```

Use [status](PORT64.md), [host-window evidence](port64/evidence/host-window.md)
and [retention](ANALYSIS_RETENTION.md). Source/program/profile archives retain
producer identities; restore into fresh paths. One Borland/Wine writer at a
time. Never open an audio backend/device in these validations.
