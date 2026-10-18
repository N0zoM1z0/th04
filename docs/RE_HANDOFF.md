# TH04 current handoff

Updated 2026-10-18. Build the complete maintained DOS four-product game and
faithful native x64 game; both goals remain active. Original Japanese DOS versus
reconstructed DOS is the primary behavioral comparison. Keep English code/docs,
gpt-6.1-sol: commits and frequent pushes to main and native HEAD:port/modern-64.

## Sampler and pending IRQ frontier (v1487)

Original MAIN pair75 at Stage2/frame249 receives a rising Shot make after all
8 scalar loads, inside the joystick PUSHF/CLI/POPF wrapper. RX is at relative
0000:3663 with IF=0,278 cycles after entry; BIOS writes at360 and return is391.
Sampler reset/sense/return are130E:06BC/06C4/07C4; actual load10FC,CS240A,DS3230.
Independent unchanged-target execution from a genuine prior reset reproduces
the RX low16 registers,segments and normalized flags. All3 later IF-enabled
boundaries preserve Sense32; Reset controls yield0 despite final BIOS Shot2.
Original scalar reads remain inferred,not directly traced. Broad MEM_READ hooks
break the far return even on pinned Unicorn2.1.4; BIOS-only10-byte hooks pass.

Native InterruptRequest separates pending request,IF eligibility,actual CPU
acceptance and later BIOS read. A fresh authored stalled COM records actual
CPU_Interrupt(vector9,type0) before IF clears. GNU/UBSan match27 operations,
10 actual ticks,5 RX callbacks and4 accepts/reads;4 independent BIOS writes
agree. Four compiled defects and3 invalid acceptance controls reject. All16
old trace comparisons remain byte-identical. See the main-branch existing
TH04_REPLAY_DIFFERENTIAL note for exact evidence classes,commands and limits.

Only2 standalone inputs change. PIC masks,priority,EOI,dispatch latency and
native elapsed time remain external. Next record complete original timer and
scalar-read events,justify elapsed/dispatch ownership,then integrate into the
real frontend and cold-replay affected game products. Preserve all raw failures;
no fitted hold,latch or fixed RX-to-BIOS delay. Both full goals remain active.

## Maintained products and comparison limits

Native source is573 files with closure
824998852f83267a4e528a0cc6b0c605cd59e70238589ecf15e18abd07c1abd2.
The new standalone sampler-irq-v1487-component retains three programs. The
previous v1485 component remains573/af655e9e under its historical source. Only
the two standalone inputs change; no native game/core or DOS source changes.

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

Use DOS-root .analysis/reconstruction/probes/sampler-irq-v1487/recover.py:
87034 inherited identities,9888 unchanged aliases and no new net storage credit.
The previous closed clock phase retains its separate accounting:
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

Phase entry heads were main9c43c13/nativef142852; read actual heads and the latest
finish receipt. Finish focused comparison, tracking, python3 scripts/ci.py in
both branches and git diff --check; commit/push both branches. ci.py ignores
arguments, so --help runs the entire CI. Complete product goals remain active.
