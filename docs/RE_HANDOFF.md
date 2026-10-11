# TH04 native branch handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

Updated 2026-10-11. The full reconstruction/native goal stays active. DOS main
indexes all four bundled demos in complete compared state/video regions;
scanout, ordinary Boss/death/process and full native pairing remain open.
Historical exactness remains separate; target canonicality is candidate-local-attested.

v1399 corrects native repeated VSYNC_START: it clears Count1/Count2 and
selects the cadence increment while preserving the accumulator. v1398 wrongly
cleared that accumulator. Its zero-phase startup/Demo observations remain valid;
they do not validate repeated START with nonzero phase.

New independent Unicorn execution runs complete original OP START0000:2552–25BB,
GDC query0000:15C2–1617 and IRQ0000:25C6. Twelve cases vary load10FC/3333,
BIOS mode bits0/C and accumulator0/12345/65535. Installed ownership0xFB,
no IRQ inside START and BIOS AH31 responses are explicit diagnostic inputs;
all original instructions execute unchanged with proper far return/IRET frames.
START writes no accumulator. With phase65535/modeC, the next IRQ skips counting.
Current GNU/UBSan match12/12. Frozen v1398 matches only4 zero-phase cases;
8 nonzero-phase cases reject and2 gain a spurious counted IRQ. This is a seeded
CPU diagnostic, not a natural31kHz or physical timing claim.

Current native producer:512 files,
5474b8e36c4f90908803a8a94e95f22dad4c131e3a435af921ca5aacb7587a74.
Only pc98_vsync.hpp / its contracts change. Fresh cold GNU builds72 programs /
passes70 CTests; optimized UBSan builds8 targets / passes5 selected contracts.
Fresh current-source probes also reproduce all208 original IRQ records and230
raster callbacks. Eight new full startup/four-Demo/fresh-OP routes retain all129
baseline output files per driver profile. Old producer/proofs keep their own
identities; no old receipt is restamped.

Important next ownership issue: src/shared/hardware/vsync_irq.asm in both DOS
source trees still explicitly clears cadence_skip_accumulator on START. Direct
original OP execution falsifies that reset under these controlled inputs.
DOS source/fingerprint6f5898dd remains unchanged in this native-only correction;
its current24kHz demo proofs remain scoped and cannot accept this31kHz/repeated-
START corner. Next fix and separately cold-replay the shared DOS assembly before
frontend integration. Also preserve query-before-increment-selection/count-clear
ordering: current source clears those fields before querying; test an IRQ
interleaved with the BIOS query in the next bounded unit. Historical exact units / MAIN deferred cases are not
promoted or rewritten by this observation.

Original full-clock IRQ evidence v1398 remains separately scoped: load10FC /
DGROUP2030,106/102 counted IRQs,143/139 scalar rows and119/111 GDC callbacks.
Raster geometry AW80/HS8/HFP10/HBP8, AL400/VS8/VFP7/VBP25 gives characterHz2631575,
horizontal106/vertical440/retrace407. Source-defined100ns emulator adjustment /
float delay is explicit. Counter service latency varies50–138 /64–142 cycles;
extra hooks perturb wait brackets. Do not fit an ISR duration or alias blink
with IRQ Count1. See the focused note for immutable captures and reader commands.

Replay indices from DOS root:
.analysis/reconstruction/probes/native-vsync-lifecycle-v1399/ and
.analysis/worktrees/port-modern-64/.analysis/port64/native-vsync-lifecycle-v1399/.
Public original reader:

```sh
python3 scripts/runtime/verify_op_vsync_lifecycle.py --output-dir .analysis/reconstruction/probes/NEW-vsync-lifecycle
```

It pins packed/decoded OP,804 diagnostic relocs, Unicorn binary, complete
instruction/memory-write traces and target frames. Current source, compiled
caller and parent target receipts are separately pinned. Current followup uses
one CPU/nice19 serial work on CPU1 because user processes occupy CPU0; original
v1398 timing captures retain their original CPU0 identity. No Windows GUI,
focus, host keys or audio device is used by this work.

Recovery uses the new v1399 verify_retention.py. It independently attests current
512/5474b8, frozen v1398 512/efea and older510/ea5c. Old strict readers reject
the changed current source; do not edit them.

```sh
python3 .analysis/reconstruction/probes/native-vsync-lifecycle-v1399/verify_retention.py
python3 .analysis/reconstruction/probes/native-vsync-lifecycle-v1399/verify_retention.py --parent v1398
```

Use --restore / a narrow --prefix for owned archived inputs; --parent v1397 or
v1396 routes earlier archives. Full source, original raw streams, failed/old
producers and compiled negatives remain protected. Full CI passes root451/native345;
current retirement/cache cleanup reclaims 484.68 MiB net. Full CRC/temporary
restore/688 protected proofs pass. Details are in the focused note/private
receipts. Prior v1398 cleanup remains separately indexed at544.95 MiB.

After shared DOS lifecycle correction, connect independent PMD busy service and
inherited unsigned IRQ waits to FrontEnd, preserving clear-before-frame_delay /
clear-after-Logo, accumulator and global raster phase. Scene still samples once
per admitted refresh and uses fixed Logo waits. Default CPU/resource/graphics
elapsed work needs a model. Full pictures, broader combat/process,
physical/second-emulator scanout, chip/audio and Windows input/audio remain open.
Goal stays active; targets remain candidate-local-attested. Next heavy work
remains single-core/low-priority/serial and muted.

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
