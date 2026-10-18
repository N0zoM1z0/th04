# Native TH04 current handoff

Updated 2026-10-18. Build the complete maintained DOS four-product game and
faithful native x64 game; both goals remain active. Original Japanese DOS versus
reconstructed DOS is the primary behavioral comparison. Keep English code/docs,
gpt-6.1-sol: commits and frequent pushes to main and native HEAD:port/modern-64.

## Original scalar reads and admission frontier (v1488)

Two new original captures complete the same 260-update Stage3 prefix after the
normal preceding stages. Stage index 2 means Stage3; the earlier v1487 prose
calling field 2 Stage2 was a naming error, not a different artifact.

The first run observes 208 post-load AH values across 26 sampler calls and 231
complete timer transactions. Unchanged original instructions reproduce every
intermediate/final latch in 25 calls after a genuine reset; existing GNU/UBSan
input consumers agree. The 1157 clock records and 850 admission records derive
zero regressions while keeping 231 raw regressions. Fourteen actual CPU IRQ9
acceptances record IF before dispatch: RX-to-BIOS is 58 cycles thirteen times
and 87 once. The masked break is MAIN0000:3A96; acceptance at MAIN0AAF:0005 is
44 cycles later, followed by 43 to BIOS. Keep old joystick 82 and authored 16
separate. CPU/PIC priority and dispatch are owners, not a fixed delay.

The second run keeps the old window selections and adds only a lazy pair75
chain. Its eight values are 0,0,0,2,0,0,0,0; entry/return already have Shot2.
Both fresh runs therefore fail to reproduce old75's rising make inside CLI.
Old75's scalar values remain inferred; do not transfer new observations or
retime old data. All 24 overlapping first-run records retain raw clock/GDC
and some BIOS differences. The code and per-run results are in the existing
main-branch TH04_REPLAY_DIFFERENTIAL note and evidence/knowledge ledgers.

Maintained helpers: scripts/probes/th04_sampler_scalars_gdb.py rotates one lazy
hardware slot; pc98_sampler_cpu.py replays the unchanged target with pinned
Unicorn2.1.4 and explicit BIOS/OPNA stubs. The public observer equals the executed
lazy source byte for byte; the public CPU helper preserves earlier outputs.
Two real compiled latch defects each reject one actual sample. No expected latch
is seeded, and neither a return-time matrix nor old timestamps replace actual
read values.

Next make a code change in the real native frontend: connect elapsed time,
Typematic/Receiver/pending IRQ and actual dispatch through separate owners,
using independently consumed bytes and the existing latch/UI flow. The live
frontend still converts host state directly into BIOS samples. Do not repeat
whole routes solely to hunt old75, or fit a phase, hold or admission delay.
Cold-replay affected game products and measure the resulting differences.
Both full product goals and all strict negative cases remain active.

## Maintained products and comparison limits

Native game source remains 573 files, closure
824998852f83267a4e528a0cc6b0c605cd59e70238589ecf15e18abd07c1abd2.
Native code76f980e owns the isolated pending-IRQ component. Its retained v1487
three-program cohort and the older v1485 component remain under their original
closures. No native/DOS game source or product changes in v1488; only three
private latch-control programs compile. The live peripheral join is still open.

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

Use DOS-root .analysis/reconstruction/probes/original-scalar-v1488/recover.py:
9897 aliases, 87297 inherited identities and nine new exact metadata restores.
Actual/archive consumers preserve nine outputs and both compiled rejections.
Two additional image restores verify the inherited-base XOR recipes. Final
providers cost0.7109375MiB for85.140625MiB raw retirement; all other retained
phase files/directories and3MiB reserve leave70MiB conservative local cleanup
relative to the raw peak, not below phase-entry storage. Keep every inherited
provider, source capsule, current/late/finish binding and actual program/link
input. Historical staging is reader-only; restore bytes/mode/nsmtime before
builds or CI. See ANALYSIS_RETENTION.md.

Heavy jobs run serially in a user systemd service with CPUQuota=35%, MemoryHigh=256M,
MemoryMax=768M, MemorySwapMax=0, TasksMax=64, Nice=19, LimitCORE=0 and taskset -c 1.
Read back actual cgroup limits. Use GHIDRA_HEADLESS_MAXMEM=384M and
JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1. Keep runs muted/headless and avoid
host keys/focus. Clean terminal intermediates after checking exact recovery.

Phase entry heads were main7cd75dc/native76f980e; read actual heads and the latest
finish receipt. Finish focused comparison, tracking, python3 scripts/ci.py in
both branches and git diff --check; commit/push both branches. ci.py ignores
arguments, so --help runs the entire CI. Complete product goals remain active.
