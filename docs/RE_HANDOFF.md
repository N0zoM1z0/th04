# TH04 native branch handoff

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

Updated 2026-10-11. The full reconstruction/native goal stays active. DOS main
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
