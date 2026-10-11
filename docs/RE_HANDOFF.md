# TH04 native branch handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

Updated 2026-10-11. The full reconstruction/native goal stays active. DOS main
indexes all four bundled demos in complete compared state/video regions;
scanout, ordinary Boss/death/process and full native pairing remain open.
Historical exactness remains separate; target canonicality is candidate-local-attested.

v1398 adds a native unsigned VSYNC counter and explicit rational raster clock.
The components preserve START/END, carry skips, 16-bit wrap, Count1-only wait
reset and an independent display phase. Frontend integration is the next step:
active PMD readiness still uses admitted-refresh sampling and Logo still uses
fixed logical waits. No wait-scheduler repair is claimed yet.

Original OP load 10FC / DGROUP 2030 is independently verified at decoded
0000:25D6, immediately before Count1 increments. Two complete muted Linux
GAME.BAT captures at CPU 24000/36000 record all 106/102 counted IRQs, 143/139
scalar boundaries and 119/111 GDC callbacks. IRQ deadlines derive from master
AW 80 / HS 8 / HFP 10 / HBP 8, AL 400 / VS 8 / VFP 7 / VBP 25, character clock
2631575 Hz and the pinned emulator's explicit 100 ns adjustment / float delay. IRQ and GDC blink
have distinct phases. Callback-to-target-increment latency varies 50–138 /
64–142 CPU cycles; do not encode a fixed service delay or fit wait durations.
The extra IRQ observer changes measured wait brackets relative to v1397;
retain each capture's own producer and times.

Current native producer: 512 files,
efea1700368644b07a03040b9b60bd12335413d3b842c9a76aa72046f4475dea.
New port64/pc98_vsync.hpp and its contracts are registered in CMake / explicit
source manifest. DOS product source, flags and fingerprint 6f5898dd are
unchanged. Cold GNU builds 72 programs / passes 70 CTests; optimized UBSan
builds 8 selected targets / passes 5 sound/VSYNC contracts. Native Counter and
RasterClock separately reproduce 208 target IRQ records and 230 host raster
callbacks under both builds. Wrong Count2 reset, blink-phase substitution and
carry removal reject; the 31-kHz carry test is synthetic, not original runtime
acceptance. Four public IRQ-reader mutation tests also pass.

Eight fresh default native CLI routes (none/pmd/pmdb2/pmd86 × GNU/UBSan)
complete startup, all four demos and fresh OP. Every 129-file output set equals
its immutable v1396 profile baseline. This is current-source regression,
not whole-picture or combined frontend IRQ timing acceptance. Earlier window,
original/DOS Demo and physical evidence keeps its own frozen identity.

Replay indices from DOS root:
.analysis/reconstruction/probes/native-irq-clock-v1398/ and
.analysis/worktrees/port-modern-64/.analysis/port64/native-irq-clock-v1398/.
Original reader original-reader-v1/receipt.json SHA 334d6fde92b5c797163ae6bdcd9d60e88f285782a3864c0ba0abe837650d2342;
native probe-v3/receipt.json SHA 00084b0e54e6d9a750a0547718c593c6e8411139c2c8e6af71fd7eed4a16cbf6.
The first probe's unsupported C++20 option and second probe's early-rounded
PIC admission remain failed. V3 uses supported C++17 and upward integer-ns
admission, preserving the rational phase formula and original floating times.

Cleanup recovery uses the new v1398 reader, which attests current 512/efea and
old frozen 510/ea5c producers separately. Old v1396/v1397 strict readers now
reject the changed current manifest; do not edit or restamp those proofs.

```sh
python3 .analysis/reconstruction/probes/native-irq-clock-v1398/verify_retention.py
# Restore only needed owned files before complete replay:
python3 .analysis/reconstruction/probes/native-irq-clock-v1398/verify_retention.py --restore --prefix .analysis/runtime/candidates/dos-op-v1398-irq-
# Previous complete archives / frozen producers:
python3 .analysis/reconstruction/probes/native-irq-clock-v1398/verify_retention.py --parent v1397
python3 .analysis/reconstruction/probes/native-irq-clock-v1398/verify_retention.py --parent v1396
```

Add --restore and a narrow --prefix for archived parent inputs. Lossless
retirement of 3,110 files / 1,451 blobs reclaims 528.63 MiB after its 39.20 MiB
archive and journal. Full CRC/EOF, member/temporary-restore metadata and
694 protected proof hashes pass. Full CI passes root 451 / native 345 tests;
post-CI source-backed caches reclaim another 16.32 MiB (1,051 files).
Total current net cleanup is 544.95 MiB. Tracking/diff checks pass.
Complete source freezes, original scalar/GDC streams, selected current
programs, compiled negative controls, failed attempts and old proofs remain
protected. Use fresh namespaces for another capture, build or reader.

Next connect PMD busy service and inherited unsigned IRQ waits to FrontEnd,
preserving clear-before-frame_delay versus clear-after-Logo and global raster
phase. Resource/CPU/bus/graphics elapsed inputs need a defensible model; do not
fit startup ages or use GDC blink as the IRQ counter. v1397 BGM-off zero-wait
and active inherited-count controls remain mandatory, alongside v1398 full
IRQ progression. Physical/second-emulator timing, full pictures, broader
combat/process, chip/audio and Windows input/audio remain open. MAIN historical
carpet/checkerboard exactness stays deferred. Goal remains active; targets
remain candidate-local-attested. Continue CPU0/nice19 serial muted Linux work.

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
