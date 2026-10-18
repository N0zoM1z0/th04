# Resume TH04 reconstruction

Updated 2026-10-18. Complete DOS/native goals remain active. Read actual heads
and DOS-root cpu-pic-v1491/finish.json. Native code 91c0e94 adds normal primary
PIC gating and separate BIOS-read/EOI ownership. Original CPU/clock timing remains open.

## Resume instruction

```text
Continue the full TH04 goal with English code/docs and gpt-6.1-sol: commits.
Read AGENTS.md, RE_HANDOFF, ARCHITECTURE, RE_WORKFLOW, ORACLES and the main-branch
TH04_REPLAY_DIFFERENTIAL note. Inspect both worktrees, preflight all targets and
attest the active database before target-dependent work. Provenance remains
candidate-local-attested. Use one serial heavy job in the user service:
CPUQuota35%, MemoryMax768M, MemorySwapMax0, TasksMax64, Nice19,
MemoryHigh256M for checks; use the recorded compiler/TU soft-limit exceptions,
LimitCORE0, taskset CPU1. Read actual cgroup values; Ghidra384M/one Java processor.
Keep runs muted/headless; no host keys/focus or physical device workarounds.
Continue validating the connected native frontend elapsed/peripheral/dispatch join,
with physical requests, firmware ticks, UART arrivals, CPU availability/acceptance
and BIOS reads as separate owners. Preserve per-byte sample semantics and the
existing game latch/UI. Do not fit a phase, hold, expected word or fixed IRQ delay.
The prior 208-read/231-timer and lazy eight-read runs are complete but do not reproduce
old75's local BIOS phase; keep old75 inferred and all raw negatives separate.
Do not run another whole route solely to hunt that old phase. Cold-replay every
affected game product, then measure remaining state/effect/input differences.
Finish focused comparison, tracking, both scripts/ci.py runs and git diff --check.
Commit/push main and native HEAD:port/modern-64. Leave both full goals active.
```

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

## Retained v1489 full cold products and recovery

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

Use DOS-root .analysis/reconstruction/probes/frontend-peripheral-v1489/recover.py.
It chains 87553 inherited bindings, all current/late/finish identities and
10189 exact aliases. Actual metadata restores and explicit archive readers
must preserve the current outputs and their semantic rejection controls.
Retain every inherited provider, source capsule, current program and link input.
The canceled first CMake prefix is disposable: its commands, source capsule,
terminal pressure/journal evidence and metadata inventory remain; its unused
probes/partial objects are removed without scientific cleanup credit.
Cumulative raw/regular output retirement is 1819.8671875 MiB, with no new
archive cost. Before final publication, all retained batch/cohort files and
directories cost 130.64453125 MiB; a 4 MiB publication reserve leaves a 1685 MiB
conservative cumulative retention balance. This is not an instantaneous raw
peak or a decrease below phase-entry storage. Duplicate gzip intermediates,
disposable caches and temporary restores/replays receive no extra credit.
The current cohort retains programs and link inputs after CMake bookkeeping
pruning; never incrementally build or invoke CTest there. Use a fresh directory.
See ANALYSIS_RETENTION.md for the exact journals and recovery consumers.

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
