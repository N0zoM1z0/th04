# Native TH04 current handoff

Updated 2026-10-18. Build the complete maintained DOS four-product game and
faithful native x64 game; both goals remain active. Original Japanese DOS versus
reconstructed DOS is the primary behavioral comparison. Keep English code/docs,
gpt-6.1-sol: commits and frequent pushes to main and native HEAD:port/modern-64.

## Original V86 PIC/BIOS window (v1492)

The pinned original MAIN completes its first 16 Stage1 actor updates in the
normal boot route. Before target observations, the complete relocated 150114-byte
module equals the pinned Japanese target at actual entry MAIN load 10FCh:0000;
DGROUP is 3230h. Provenance remains candidate-local-attested.
The read-only capture has 1613 records, 33 paired sampler calls and five physical
Z edges whose calls preserve guest CPU, all conventional RAM and raw counters.
Readback words are observations with no expected-word assertion or assignment.

All 361 observed hardware accepts occur in V86: vector8=272, vector9=9,
vector10=16, vector20=31 and vector21=33. Nine keyboard BIOS callback returns
at F000h:E96Eh retain primary ISR1; subsequent guest port0/20h writes at
F000h:E971h clear it. These are observed callback/port contexts, not a ROM dump.
The maintained reducer checks raw controller layouts, CPU guards, accepts and
separate BIOS/EOI ordering. A fresh current-header UBSan consumer agrees over
36 normal-primary dispatch snapshots and 361 primary EOIs (397 rows).
A compiled exit-0 EOI defect and four coherent data defects reject.
The 64 slave EOI transitions are audited separately, not native slave arbitration.

Actual MAIN entry has master IMR79h; this stage window has IMR78h and slave
IMR CCh/DCh. Cascade7 is genuinely in service in this window, with the pinned
ignore-in-service workaround enabled. Native selection comparisons exclude
that active cascade domain. NMI/trap guards are recorded but their active paths
are not exercised. The native keyboard-only FDh mask and immediate default
CPU/read/EOI remain portable policies; this capture does not replace them with
original boot masks, other device producers or a CPU scheduler. Raw clocks are
not an audited elapsed epoch or UART-to-BIOS latency. No fixed delay is fitted.

The successful window arms frequent hooks after completed stage initialization;
MAIN entry is one complete-module/PIC snapshot. The earlier broad-entry run
hits its 600-second deadline with zero actor updates and remains a separate
incomplete result. Preparation A fails before launch and remains preserved.
Capture C's inherited extension metadata names the earlier observer hash;
capture-scope-amendment.json binds the actual executed capsule hash and window
without rewriting the raw receipt or sources. The maintained GDB module is
byte-identical to that executed observer. Both observations use one emulator,
not independent hardware Oracles.

Evidence: DOS-root .analysis/reconstruction/probes/original-pic-v1492, especially
original-pic-audit.json, projection-verdict.json, capture-scope-amendment.json
and retention/retention.json. Recheck with scripts/probes/reduce_th04_original_pic.py
or the exact recovery readers after retirement. The native 573-file source
closure remains f9b57540e6c2b86fd91fac87ceb54fd729ab1f9d55a71b8f294eaaed8ec43c4a;
no game source changes, full rebuild, campaign acceptance or exact promotion occur.
Next connect the observed dispatch/producer/mask lifecycle and elapsed epoch;
do not hunt old75 with another full route. Existing strict negatives and both
complete DOS/native goals remain active.

## Primary PIC and separate BIOS/EOI ownership (v1491)

Native code 91c0e94 replaces the live Device's request-only latch with normal
fixed-priority primary PIC state. Masking retains requests; IF alone cannot
admit a keyboard request while a higher-priority line remains in service.
CPU acceptance, BIOS data read and EOI are separate operations. Reading BIOS
data leaves the service bit set; another request cannot re-enter that line
until EOI. The default window explicitly accepts, reads and sends nonspecific
EOI at the same portable event time. This is not original ISR instruction cost.

The authored real-mode internal-DOS probe observes 41 PIC snapshots, three real
CPU accepts (one timer/two keyboard), two BIOS callback returns and three guest
EOI writes. IF is 1 while IRQ0 is masked but still in service and keyboard is
pending; IRQ0 EOI admits keyboard. Both BIOS returns retain IRQ1 service until a later
20h write to port 0. All 41 primary snapshots and 18 Device operations agree. Device replay
uses ordinal time labels, not measured original latency. Independent extracted
pinned PIC source agrees over 33,554,432 IF/priority selections and 2304 EOI
cases. Source replay is independent of the native implementation but shares
the emulator family with the live capture; it is not a second hardware Oracle.
Three compiled exit-0 defects reject: ignoring higher service, erasing
masked requests, and ending PIC service during the BIOS read.

The observed emulator has cascade-ignore mask 80h. It is inactive in this
fixture because cascade 7 stays masked and is never in service. IRQ13 projects
to that pending masked primary cascade; slave arbitration is not accepted.
The exhaustive source comparison explicitly uses normal primary mode without
that workaround. Actual ROM stub bytes remain unavailable through the bounded
conventional-RAM reader; EOI is observed at the guest port write, not inferred
from a claimed ROM dump. This is an authored COM, not original TH04 V86 timing.
The reused launcher
retains legacy clock-phase labels; capture-scope-amendment.json explicitly
corrects them to guest-marker input and no new timer-transaction observations. The raw
receipt and all executed sources remain unchanged.

Physical identities and host delivery order from v1490 remain. MAIN reads
7,9,8,5,2,0,3,6 then Shift independently; reset clears first and Sense ORs.
Current GNU/UBSan retain 31 observation-on/off frontend polls with independent
original sampler checks, plus four elapsed frames/nine polls/81 reads and all
21 stable physical-key fixtures. The old 27-operation IRQ projection remains
byte-identical under its explicit collapsed read/EOI policy; it is not new EOI
timing proof. The new 18-operation live-derived fixture preserves that boundary.

Current source is 573 files, closure
f9b57540e6c2b86fd91fac87ceb54fd729ab1f9d55a71b8f294eaaed8ec43c4a.
The cpu-pic-v1491 replay cold-compiles all five affected header consumers per
role and links four programs each for GNU/UBSan/Windows. It reuses 112 unrelated
core objects per role by SHA. This is 15 fresh objects/12 current programs,
not a new all-source cold cohort or 87-CTest rerun. Windows is compile/link only.
GNU/Windows View uses O3/GGC5; UBSan View uses O0/GGC1 with UB/bounds retained.

Heavy work stays serial 35%CPU, CPU1, Nice19, hard 768MiB/no swap/64 tasks/core 0.
Checks/recovery use 256MiB soft; only View compilation uses 640/768MiB soft.
Current build peak is 585.574 MiB with zero OOM kills.
The two actual v1489 compiler OOM failures remain preserved. Caps are unchanged.

Next bind original CPU dispatch, IF/IRQ-check scheduling, NMI/trap, other IRQ
producers, cascade/special modes, boot masks and elapsed epoch. Do not fit a
serial-to-BIOS delay or hunt old75 with another full route. Common-reset full
DOS/native campaigns, Windows runtime and NP2/hardware remain open. Both full
goals and all strict negatives remain active; historical DOS exactness is unchanged.

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

Use DOS-root .analysis/reconstruction/probes/original-pic-v1492/recover.py.
It chains 90152 incoming identities (including all three v1491 late files)
and 10200 exact aliases after eight new retirements. All eight actual restores
preserve SHA, size, mode and nsmtime; the maintained capture CLI passes with
the restored disks and fonts. Keep the two compressed execution-disk providers,
all records/source capsules/current programs and every inherited provider.
Closed new regular allocations save 93208576 bytes after provider cost;
this is not a phase-entry storage decrease or repeated historical credit.
The canonical v1491 source capsule supplies the unchanged 573-file vector.
Use a fresh build directory; never build or invoke CTest in retired cohorts.
See ANALYSIS_RETENTION.md for the exact recovery journals and consumers.

Heavy work stays serial, CPUQuota=35%, MemoryMax=768M, no swap, Nice=19, CPU1,
64 tasks and no cores. Normal checks use MemoryHigh=256M. The first attempt
stalls above 90% memory-pressure time; GGC min-expand=5/min-heapsize=4096 reduces
compiler heap use. The giant FrontEnd TU uses compile-only soft exceptions,
up to the existing 768M hard cap. The O2 and O1/GGC5 attempts hit that cap;
retain its failure and journal. GNU CTest returns to 256M under the original
supervisor. The resumed driver compiles only View at O0, verifies all preserved
fresh O2 core hashes and the override object after linking, and restores 256M
before every UBSan control. Windows is a fresh compile-only directory. The
attempted compile_commands entry is qualified by resume-o0/view-override.json;
never call this an uninterrupted uniform-O2 build. Both initial resource
amendments and the failed supervisor remain explicit. Runtime checks use 256M.
Keep emulators muted/headless; Windows remains compile-only. Do not use host
keys/focus, physical audio, or GUI/device workarounds.

Phase entry heads were main62d507c/native5a960e1; read actual heads and the latest
finish receipt. Finish focused comparison, tracking, python3 scripts/ci.py in
both branches and git diff --check; commit/push both branches. ci.py ignores
arguments, so --help runs the entire CI. Complete product goals remain active.
