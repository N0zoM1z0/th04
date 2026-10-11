# TH04 native branch handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

Updated 2026-10-11. The full reconstruction/native goal stays active. DOS main
indexes all four bundled demos in complete compared state/video regions;
scanout, ordinary Boss/death/process and full native pairing remain open.
Historical exactness remains separate; target canonicality is candidate-local-attested.

v1394 isolates original Gaiji I/O work. Four read-only GAME.BAT/PMD86 captures
cross fixed CPU budgets 24,000 / 36,000 with default / zero 8-bit I/O delay.
Other configuration bytes, original HDI/reset/assets/font/emulator are identical.
Each full 69,028-byte OP load and 804 ordered relocations agrees with the pinned
decoded target. Load 10FC, DGROUP 2030; nine attested points yield 264 scalar
rows including 256 read-glyph entries. Complete GDC model replay, port tables,
raw PIC arithmetic and load/port/time/GDC mutation rejection pass. Controlled
host stop at OP 0A74:0C79, before the next instruction, is not process completion.

Gaiji 0A74:0C6B→0C79 takes 40.235458 / 34.996667 ms with default I/O delay,
versus 17.134000 / 11.404611 ms when only 8-bit delay is zero. Actual read-all
0:1450→1471 and write-all 0:14BE→14E1 have 8,192 reads and 25,604 writes
including selectors. Default delay [864,559,1118] ns and pinned integer debit
arithmetic account for 22.829167 / 23.412333 ms of Gaiji-only work. Separate
aggregate removed-cycle remainders remain recorded; zero-delay window debits
are zero. CPU-normalized zero-delay ratio is 1.001591. This identifies the
principal DOSBox-X I/O owner, not a physical ISA/CGROM delay or native constant.

Three failed observer attempts retain their logs/partial streams and are
rejected as incomplete: pre-guest Python indentation; a local window splitting
an MZ relocation at 0A74:0C70; and the pinned DGROUP guard rejecting borrowed-DS
write-glyph 0:1474. The accepted observer expands the relocation window and
uses host I/O counters enabled only in the two transfer windows. Original
emulator guards and target bytes remain unchanged.

Native source is unchanged at 510-file producer
9cfe100a84ac0a325d498b9b81602298009e462643b2cfa453947fe85bc1b049.
Retained v1392 GNU/UBSan build, Demo and private Xvfb proofs retain their
identities; no native build/runtime acceptance is rerun here. v1393 observed
Logo PI loading/drawing and supplied-age/zero-age diagnostics remain distinct.
Native assets load in port64/main.cpp before resident PMD construction in
port64/view.cpp; DOS installation precedes OP loading. Next implement explicit
elapsed-work ownership through resources, drawing and process entry, with
independent diagnostics before changing default clocks. Do not fit an emulator
bus cost, fixed startup age or display-event count into product behavior.

Replay producers/receipts: DOSroot
.analysis/reconstruction/probes/native-gaiji-clock-v1394/; native copies under
.analysis/port64/native-gaiji-clock-v1394/. Public ROOT reader:
scripts/runtime/verify_gaiji_io_clock.py. Restore retired verifier/HDI inputs:

```sh
python3 .analysis/reconstruction/probes/native-gaiji-clock-v1394/verify_retention.py --restore
```

Lossless content deduplication retires 49 logical files into 15 unique blobs,
reclaiming 604.43 MiB across this batch. Entire gzip CRC/EOF, logical member
SHA/size/mode/nsmtime and protected proof checks precede removal. The earlier
temporary archive container is retired after all its logical members verify;
compressed wrapper bytes are not a replay claim. Raw completed/failed inner
captures, scripts, receipts and logs remain immutable and live. Build outputs
were not generated. Both full CI gates pass (root 441 / native 345 tests),
with ledger and diff checks. Source-backed post-CI caches reclaim 16.69 MiB.

Goal remains active; MAIN historical carpet/checkerboard exactness is deferred,
targets remain candidate-local-attested and DOS fingerprint 6f5898dd is unchanged.
Full default pictures, broader paired combat/process, physical/cross-emulator
scanout and Windows input/audio remain open. Continue CPU0/nice19 serial muted
Linux work; Windows GUI/focus/host keys remain excluded.

See the focused differential note for detailed evidence and prior proof limits.

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
