# Native TH04 current handoff

Updated 2026-10-18. Build the complete maintained DOS four-product game and
faithful native x64 game; both goals remain active. Original Japanese DOS versus
reconstructed DOS is the primary behavioral comparison. Keep English code/docs,
gpt-6.1-sol: commits and frequent pushes to main and native HEAD:port/modern-64.

## Current clock and admission frontier (v1486)

Main code 86873ce attests complete keyboard timer transactions. The pinned host
ELF writes PIC_Ticks before crediting CPU_CycleLeft and subtracting one from
queued indices. Actual instruction boundaries are TIMER_AddTick+17h/+42h/+81h.
A tick hardware watch can therefore observe a temporarily uncredited budget.

Fresh authored COMs deliver two physical requests at tick-write or timer-return.
They preserve different orders: 535 ticks/549 operations versus 536/550. Both
pass through existing cold GNU/UBSan peripherals; twelve independent software/
hardware BIOS write pairs agree. Complete 2677/2682-record clock traces derive
zero merged regressions while retaining 535/536 raw regressions. Six actual-proof
mutations reject, and eight focused unit tests pass. Direct raw tick-edge time
fails the real native monotone-time guard. Four prior default reports remain
byte-identical after adding optional --audit-clock.

The unchanged original V86 stream binds 65 complete external transfers. Thirteen
stage-plan queued/service deadlines agree; all 52 clock-controller transfers have
exactly one millisecond temporary excess, covering every recorded regression.
CPU carry is -1 in 51 cases and -17 once. The original controller source watches
the tick write. Its old capture lacks the complete host instruction-phase trace;
keep the original raw samples and the bounded boundary inference distinct.
Do not apply a guessed correction to unobserved phases or round away CPU carry.

Next record timer phases and actual scalar sampler/IRQ reads in original V86,
including unstable sampler pair 75 at loop 249. Then justify native elapsed time
and admission semantics before wiring the peripheral into the frontend. The
component still receives recorded RX/CPU-read boundary times; guest IRQ latency
and native game-clock ownership remain open. Original V86 RX-to-BIOS is usually
58 cycles (304/346); the authored internal-DOS 16-cycle observation is separate.
Preserve latch/UI behavior, actual repeat ordering and each raw negative case. No fitted hold, expected word or
fixed transport-to-BIOS admission delay is justified.

Use the main-branch docs/reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md for
the replay surface, evidence classes and earlier complete/failed comparisons.

## Maintained products and comparison limits

Native source remains 573 files, closure
af655e9e1ef5ac7702fbf07a8bca4b8946f8655b3fb71b59a5c24ba74d1f1b87.
The isolated keyboard-device-v1485-component cohort retains three programs:
GNU/UBSan execute; Windows is compile-only. Native b774aa9 owns the peripheral;
no native/DOS product source, compiler flags, link input or cohort changes here.

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
a genuine reset and pair 75 changes BIOS during execution. All 247 observed
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

Use DOS-root .analysis/reconstruction/probes/keyboard-clock-v1486/recover.py:
9888 exact aliases, 86710 inherited identities, eight new SHA/size/mode/nsmtime
restores and actual/archive readers preserving eight prototype/public model
reports plus the raw-clock rejection. Conservative phase-local cleanup net is
14 MiB after archives, all retained nonarchive phase files and a 3 MiB reserve.
Keep every inherited provider, current/late/finish identity, current product/link
input, source capsule and unique witness. See ANALYSIS_RETENTION.md. Historical
source staging is reader-only; restore current bytes/mode/nsmtime afterward and
never run CI or a build while staged.

Heavy jobs run serially in a user systemd service with CPUQuota=35%, MemoryHigh=256M,
MemoryMax=768M, MemorySwapMax=0, TasksMax=64, Nice=19, LimitCORE=0 and taskset -c 1.
Read back actual cgroup limits. Use GHIDRA_HEADLESS_MAXMEM=384M and
JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=1. Keep runs muted/headless and avoid
host keys/focus. Clean terminal intermediates after checking exact recovery.

Phase entry heads were main 40a2f60/native 59884d9; read actual heads and the latest
finish receipt. Finish focused comparison, tracking, python3 scripts/ci.py in
both branches and git diff --check; commit/push both branches. ci.py ignores
arguments, so --help runs the entire CI. Complete product goals remain active.
