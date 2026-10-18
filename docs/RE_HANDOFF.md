# Native TH04 current handoff

Updated 2026-10-18. Build the complete maintained DOS four-product game and
faithful native x64 game; both goals remain active. Original Japanese DOS versus
reconstructed DOS is the primary behavioral comparison. Keep English code/docs,
gpt-6.1-sol: commits and frequent pushes to main and native HEAD:port/modern-64.

## Original IRQ1 monitor and ROM return (v1495)

Root probe code 6fb50c5 records the original normal boot through eight Stage1
updates: six complete IRQ1 paths and 96 supplemental observations. The full
MAIN load module is attested before use; provenance remains candidate-local-attested.
131 complete timer transactions audit 657 clock records and 1091 admission
records, plus the separate ISR stream, with zero canonical clock regressions.
The MAIN entry remains a raw snapshot outside that timer audit.

CPU acceptance first enters a protected-mode monitor. Its IRET reaches the
V86 BIOS entry F000:E96A; it does not finish the keyboard IRQ. The BIOS callback
returns at F000:E96E with ISR1 still set. The generated ROM tail issues
OUT 00h,20h at F000:E971, then IRET at F000:E974 restores the entire captured
interrupted CPU context. Three port reads (43h,41h,43h) consume each byte and
update the BIOS bitmap without changing guest CPU state inside the callback.

Independent ROM-tail CPU checks pass and five semantic defects reject; source,
interval and replay details are in the main-branch TH04_REPLAY_DIFFERENTIAL note.
Native code stays 19c1d37 with the unchanged 573-file fe7dca75 source closure.
Its current programs/objects/link inputs retain their entry identities; this
batch does not rebuild products. Next establish the CPU service owner, common
boot epoch and other IRQ producers before full campaign comparison. Default
native immediate CPU/BIOS/EOI remains an explicit portable policy. Complete
DOS/native fidelity and historical strict negatives remain open.

## Earlier PIC evidence

The v1492 first16 window and v1491 authored real-mode probe remain in the
focused comparison note and prior public snapshots. Their pre-dispatch-policy
statements describe code 91c0e94, not the new cfe5ac7 default check event.

## Maintained products and comparison limits

The previous full cold source vector is 573 files, closure
60714a70f0bcda09f2689ad548242081ca80847bc9016da8ba115369e6da4298.
The fresh frontend-peripheral-v1489-gc cohort contains 91 GNU programs
with 87 passing CTests, 7 UBSan programs and 4 Windows compile-only programs.
UBSan uses fresh O2 core objects and an explicit O0 override for view.cpp after
the O2 and O1/GGC5 frontend attempts hit the unchanged 768M hard cap.
The successful View profile is O0 with GGC min-expand=1/min-heapsize=1024. The override object
hash is checked after CMake links; its exact command qualifies the attempted
O2 compile_commands entry. All source/header digests stay unchanged.
Both stock host-adapter runs preserve all 130 previous complete outputs through
13377 Stage3 updates. This is a regression of the old host-input scenario;
it does not accept the connected default peripheral's full campaign.
112 of 113 GNU core objects match the retained old cohort byte for byte;
all affected header consumers were cold-built regardless. DOS products and
historical artifact/unit exactness are unchanged.

The retained full-game sampled-device-v1481-final cohort still binds its original
571-file closure 10d8adb1fbdac1495f2b8a5180fa21e1808003bba8ebe2a6cd396ae4567b4f01:
GNU 90 programs/86 CTests, UBSan five and Windows two compile checks. Never label
that full-game cohort as rebuilt under 573. Programs, link inputs and private
GNU observers remain physical. Neither old cohort may be incrementally built;
never invoke CTest there, including --show-only.

The v1484 original completes Stage3 and reaches actual Stage4 init/score1.
Against the preceding original, all 13378 pool/state snapshots, 13377 heads,
four literal players, 23 full RGB/TRAM/DAC/tone samples and the complete raw
loop/RNG wire agree. Strict timing remains false: 30 tail words and 23 raw GDC
samples differ. Of 3402 sampler pairs, 3362 stable CPU replays pass, 39 precede
a genuine reset and pair75 changes BIOS during execution. Its latch result is now separately
confluent across the three later IF-enabled boundaries; scalar reads were not
directly captured, so keep3362 stable replays and this1 bounded proof distinct. All 247 observed
tail returns bind the same-run after-reset actor field. Preserve failed capture
A's 7833-snapshot truncated extent and genuine SIGINT separately from full B.

The corrected v1481 physical-device case completes 13377 Stage3 updates, all
13378 pool/state snapshots, four literal players and 22 full RGB samples; its
40 post-tail input differences remain a distinct failure. All 29616 poll
transitions replay unchanged original sampler instructions. The raw-BIOS movie
and its 7837 Enter agreement are separate from physical delivery. Stock GNU/
UBSan regressions retain 130 previous output hashes, 407 blink pixels and 1805
keys. Source-DOS's 19 keys/23 GDC failures are another surface; do not subtract
counts across scenarios or borrow acceptance. Continuous display, common-reset
campaigns, full four-source/native campaigns, Windows runtime and NP2/hardware
remain open.

Original MAIN:156258 bytes/1136 relocations,
077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b.
Source MAIN:200279 bytes/1183 relocations,
778641ab845bcd67c6888bacc049e2cfa20fddda844681d3d2fd164f8386abc9.
DOS four-product cohort remains .analysis/build/dos-four-products-v1443.
Provenance remains candidate-local-attested; artifact/unit exactness is unchanged.
Keep MAIN 0AAF:0153/0158 tail reset, 0AAF:01B3 actor seam and literal 0AAF:5FCF player entry
distinct. Historical Elly, BIOS-movie, UI and failed-prefix details stay in the
main differential note and evidence/knowledge ledgers.

## Recovery, resources and finish

Use DOS-root .analysis/reconstruction/probes/irq-service-v1495/recover.py
for exact hashes/restores and replay_retained_v2.py for the frozen ISR reader.
It chains 91002 incoming identities, including three v1494 late files, and
10261 exact aliases after 36 new retirements. Each actual restore preserves
SHA, size, mode and nsmtime and is removed before restoring the next. Current
and frozen maintained readers replay through explicit exact-byte providers.
Closed capture images/fonts/logs/wires save 149401600 bytes after new gzip and
alias-manifest allocation cost; this is not a phase-entry storage decrease.
Keep all failed observer sources/receipts, semantic controls, current products,
source capsule and inherited providers. No new native build or source gzip is
created. Never build or invoke CTest in retired cohorts.

Heavy work stays serial at CPUQuota=35%, CPU1, Nice=19, 64 tasks,
MemoryMax=768M, no swap and no cores. Normal checks use MemoryHigh=256M.
Only View uses the recorded compiler profiles: GNU/Windows O3 with GGC
min-expand=5/min-heapsize=4096 and soft 640M; UBSan View O0 with GGC
min-expand=1/min-heapsize=1024 and soft 768M. Other UBSan core objects retain
O2. Restore soft 256M before controls. The retained v1494 affected build peaked
at 610803712 bytes with zero OOM kills; v1495 runs no compiler. Historical
O2/O1 sanitizer failures and resource amendments remain retained; do not repeat those failed profiles.
Keep emulators muted/headless and Windows compile/link only. Do not use host
keys/focus, physical audio, or GUI/device workarounds.

The v1495 focused comparison, current/frozen archive readers, root CI
(593 tests), native CI (354 tests) and both diff checks pass. Full provider
recovery is required before final push.

v1495 entry heads were main b490824/native 16faf41; read actual heads and the latest
finish receipt. Finish focused comparison, tracking, python3 scripts/ci.py in
both branches and git diff --check; commit/push both branches. ci.py ignores
arguments, so --help runs the entire CI. Complete product goals remain active.
