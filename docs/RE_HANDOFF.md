# TH04 native branch handoff

## Joined palette fade recovery (v1414)

Current producer 530/4dc27bde combines the palette WORD fix with the published
wait/text owner at 9a7f380. Cold GNU Release and optimized UBSan/bounds each
build the complete core, actual frontend and four selected contract programs.
Both pass the palette, MAINE cutscene, startup and GDC contracts and all 24
palette timelines against the retained 96 original instruction controls.
Native CI passes 345 tests. This is a focused integration; the v1412 full
79-program/77-CTest build remains bound to its own frozen producer.

Evidence is in the isolated `native-palette-join-v1414` tree under
`.analysis/port64/native-palette-join-v1414/`. `verify_closure.py` checks the
530-file source archive, current programs and 1,635 frozen parent files.
Verified archive retirement releases 25.64 MiB; source-backed Python cache
cleanup releases another 15.70 MiB. Continue recovering native hardware and
scene owners before longer game validation.

## Palette fade WORD recovery (v1413)

`maine::Animation` truncates fade speed to the original WORD and follows its
signed test. Zero and negative WORD speeds now finish after the single initial
refresh; positive speeds retain `1 + 17 * speed` waits. Original OP/MAINE
0000:0622 and 0000:0666 pass 96 instruction controls at loads 1000/3333.
Fresh GNU and optimized UBSan Animation builds each pass 24 native vectors;
the actual 328585f predecessor fails 14. Complete tone stores, palette calls
and wait streams remain available, including the transient 102/-2 tone.

Frozen producer 528/dbdbcbe5 is in the isolated `native-palette-zero-v1413`
tree, phase `.analysis/port64/native-palette-zero-v1413/`. Its closure verifies
the source archive, complete original controls, compiler outputs and 803 frozen
text-proof files. CI passes 345 tests; verified cache retirement releases
0.13 MiB net. See [Ending evidence](port64/evidence/ending.md).
The v1414 integration above contains this source and freshly builds its
frontend and affected MAINE components.

The v1409 records below describe their frozen producer. DOS text/VSync has
since been integrated at a07dbc0; native wait/text is published at 9a7f380.

v1409 restores MAIN's ordinary text character/string writers in `TextPlane`.
`put_character()` accepts the full WORD input, including ANK, JIS and Shift-JIS;
HUD initialization, Game Over and the actual frontend now use it. `put_sjis()`
retains the original byte conversion, NUL handling, WORD addresses and final
wrapped-count attribute fill, including malformed byte pairs.

Original MAIN 0000:229E/22F6 passes all 65,536 WORD characters and all 65,536
two-byte strings at a fixed visible position. Another 840 fixtures match full
80000h..DFFFFh memory at loads 1000/3333: 1,680 comparisons. Cold GNU and focused
UBSan/bounds reproduce every output. The frontend, six selected programs and
six component contracts build/pass; prior text Gaiji retains 2,656 comparisons.
The compiled predecessor rejects edge, kana, bad-trail and long-string inputs.
The long string differs in 8,386 physical bytes while its partial visible banks
agree, so complete memory and the failure status are retained.

Producer 526/3e7d5e33 and complete evidence are under
`.analysis/port64/native-sjis-text-v1409/` in `port-motion-v1402`.
See [text character recovery](port64/evidence/hud.md). Original instructions
read mutable DGROUP 2134:0768; the DOS root's two text ASM owners still use
fixed A000h and need a separate cold recovery. Historical exact remains 661/663.
Continue source recovery before long game campaigns.

Native CI passes 345 tests. Verified archiving retires 250 compiler-cache
paths; 515 source-backed Python caches bring cleanup to 14.50 MiB net.
The closure reader checks all current proofs and 780 frozen parent files.

v1408 migrates the original `GAIJI_PUTCA/PUTSA` writer semantics into
`TextPlane`, used by MAIN HUD/Game Over and MAINE score registration. WORD
coordinates and the mutable text base now select physical addresses without
visible-cell clipping. Strings write all glyphs before filling attributes
with the wrapped count. Existing visible banks stay directly stored; other
addresses use sparse pages, keeping ordinary frame copies near 8 KiB.

All 664 native fixtures agree with original MAIN 0000:1B0C/1B50 and MAINE
0000:0FC4/1008 at loads 1000/3333: 2,656 full memory comparisons. Optimized
UBSan/bounds reproduces every result. Cold core/five programs and five related
contracts pass. The compiled predecessor rejects X80/Y0 and a 2,049-character
string; the first has eight visible byte differences. The string's partial
visible banks agree, demonstrating why the comparison retains the full memory
window and the failure status.

Producer 524/6f214e8c and complete proofs are under
`.analysis/port64/native-text-address-v1408/` in the `port-motion-v1402`
worktree. See [text writer recovery](port64/evidence/ending.md). DOS root
`main` already carries its separate v1407 recovery at a71607f. Historical exact
remains 661/663. Continue with ANK/Shift-JIS text writer address semantics;
defer long game campaigns while function migration remains open.
CI passes 345 tests. Verified archiving retires 242 compiler-cache paths;
515 source-backed Python caches bring cleanup to 13.04 MiB net. Current
source/program/transcript closure and 757 frozen native parent files pass.

v1405 restores native `GRAPH_GAIJI_PUTC`/`PUTS` row addressing and continuous
string DI/STEP behavior in `Canvas`. Original MAINE 0000:3760/36B6 at load 2000
matches 2,833 complete seeded pages, covering the 256 installed bank characters,
bit shifts, coordinate edges and string steps. Focused UBSan/bounds reproduces
all pages; the compiled predecessor differs in 116 pixels at X640/Y0. Cold core,
five programs/contracts and the 1,037 retained original font pages pass.
Producer 522/bac23324 and receipts are under
`.analysis/port64/native-gaiji-address-v1405/` in the isolated
`port-motion-v1402` worktree. See [Gaiji recovery](port64/evidence/ending.md).
CI passes 345 tests. Verified compiler-cache archiving and source-backed Python
cache cleanup reclaim 11.7 MiB net; current source/program/proof closure passes.
Next migrate the DOS `src/shared/hardware/graph_gaiji.cpp` string/WORD stores:
its current per-character coordinate calculation loses pointer continuity at
WORD boundaries. This batch changes native source; historical exact remains
661/663. The full reconstruction/native goal remains active.

v1404 restores `GRAPH_PUTSA_FX` WORD addresses in native `Canvas`: truncated
Y shift, unsigned X/8, continuous string DI, and WORD/spill write order.
Original MAINE 0CC7:058C at load 2000 agrees with all 1,037 complete seeded pages;
focused UBSan/bounds reproduces them. Cold core/three selected programs and
three component contracts pass. The compiled predecessor differs in 119 pixels
at X640/Y0. Producer 520/774cc800 and receipts are under
`.analysis/port64/native-font-address-v1404/` in the isolated
`port-motion-v1402` worktree. See [font recovery](port64/evidence/ending.md).
CI passes 345 tests. Completed compiler caches are verified in an archive
before removal; source-backed Python caches are removed, reclaiming 11.6 MiB
net. Programs, source and complete original pages remain; the private
`verify_closure.py` checks the current source and retained proof carriers.
DOS historical exact counts remain 661/663. Continue source migration before
long game campaigns; graphics/resource elapsed-work owners remain open.

v1403 recovers the full unsigned-WORD filled-circle loop and stage horizontal
clipping in `grcg_raster.cpp`. The shared native disc consumer now accepts
radii above512, including wrapped/negative-WORD requests. Fresh original
execution matches35 complete request streams (1,418,847 calls),605 horizontal
write masks and20 filled-circle masks. Two component contracts and a focused
UBSan/bounds replay pass; the predecessor rejects radius513. Producer518/
193e94a7 and receipts are under `.analysis/port64/native-grcg-v1403/` in the
isolated `port-motion-v1402` worktree. See [raster evidence](port64/evidence/stage-5.md).
DOS source and historical exact counts stay unchanged. Continue function
recovery and migration before long game campaigns.

v1402 restores IATAN2's complete signed displacement behavior in native
`motion::angle_to()`, replacing the blanket -32768 rejection with original
signed magnitude comparison, low-byte lookup and DIV fault handling. All
184,908 original-instruction vectors agree, including 514 original faults.
See [core evidence](port64/evidence/core.md) and the scoped native receipt under
`.analysis/port64/native-motion-v1402/`. DOS source and historical exact counts
are unchanged. Continue function migration before long game campaigns.

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

Updated 2026-10-12. The full reconstruction/native goal stays active. DOS main
indexes all four bundled demos in complete compared state/video regions;
scanout, ordinary Boss/death/process and full native pairing remain open.
Historical exactness remains separate; target canonicality is candidate-local-attested.

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

Current native source: v1401,512 files/60cf4491 (`port/modern-64`).
Startup PMD busy waits now service the next resident timer deadline; ordinary
frame delays clear Count1 before waiting and Logo waits clear it afterwards.
The inactive zero-frame fallback still clears Count1. FrontEnd shares raster
phase across work and refreshes, preserving Count2. Cold GNU72 programs/70
CTests and optimized UBSan9 programs/6 contracts pass; three compiled mutations
reject wrong reset order and refresh-only PMD service. Current/frozen source
and81 program identities verify in
`.analysis/port64/native-startup-waits-v1401/current-verification.json`.
See [startup ownership](port64/evidence/op-startup.md).
Prior v1399/v1400 receipts retain their frozen source identities and scope.
Current native CI passes345 tests.626 completed compiler-cache files are
archived with individual byte checks before removal, reclaiming21.74 MiB net;
all81 programs, source snapshots and compiler metadata remain. Recovery carrier:
`.analysis/port64/native-startup-waits-v1401/compiled-cache.tar.gz`.

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

Next recover CPU/resource/graphics elapsed-work owners and their call order.
Prioritize function recovery and migration with focused checks before long
game campaigns. Full pictures,
Boss/death/process, second-emulator/physical scanout and Windows input/audio stay
open. Goal active; targets candidate-local-attested. CPU1/nice19 single-core,
serial and muted; no Windows GUI/focus/host keys/audio device is used.

Prior demo/point-number/presentation experiments are indexed in
[demo evidence](port64/evidence/demo.md) and their immutable private receipts.
Historical producer502/v1376 and consumer505/v1377 keep their original identities.
Earlier ordinary GNU Reimu A Normal/Lunatic/Extra clear/save/restart routes and
dense slowdown observations retain their v1356 producer; see
[host-window evidence](port64/evidence/host-window.md). The prior UBSan Normal
clear remains revoked (mask0x19 is a sentinel), and the v1360 route and first
late Bomb probe remain failed. Require mask<4 plus the selected shot bit.

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
