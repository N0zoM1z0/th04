# Resume TH04 reconstruction

Updated 2026-10-18. Complete DOS/native goals remain active. Read actual heads
and DOS-root receive-clock-v1494/finish.json. Native code 19c1d37 separates RX
service deadlines from CPU observations. Original CPU/boot timing remains open.

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

## UART receive event clock (v1494)

Native code 19c1d37 anchors an RX callback's IRQ1 check to its queued service
deadline. A late CPU observation no longer shifts the check forward. CPU
acceptance, unmask, EOI and a stalled UART's read/restart retain their own
observation times. The default host runs peripheral callbacks at their exact
deadlines; original CPU instruction cost and a common boot epoch stay open.

The current product header agrees with exact pinned UART/PIC/queue source over
220 scenarios/12320 state rows, covering late callbacks, unread overrun, a full
ring, blocked CPU and unmasking. The pre-change consumer differs in 3758 rows;
a wrong chained-transfer anchor differs in 5313. Both controls compile and exit 0.
17 source bodies are byte-attested. The actual emulator ELF confirms the
service-index branch; five operand/branch defects reject. Queue storage, explicit
time input, CPU interrupt entry and unused TX paths are bounded Oracle adapters.
Source and binary evidence belong to one emulator family, not hardware validation.

Two retained authored microfixtures provide 12 RX callbacks with lateness below
one native quantum. They do not distinguish the late-RX hypotheses. No fresh
original-game capture or observed original runtime fault is claimed; this is a
source/compiler correction. Raw time and service-index fractions remain separate.

Current source has 573 files, closure fe7dca75f53a7a665681672eb0b25710ff7cbac06a82390ec8ad33d325b903a9.
All five affected consumers are cold compiled per role (15 objects/12 programs),
with 112 unrelated core objects reused per role by SHA. Frontend/original-ISA,
physical keys and claim limits are in the main-branch TH04_REPLAY_DIFFERENTIAL
note. This is not an all-source cold cohort or full campaign acceptance.

Next establish CPU availability, BIOS/EOI instruction cost, other IRQ producers
and the common boot epoch. All historical strict negatives remain unclosed;
both complete DOS/native goals stay active.

## Earlier PIC evidence

The v1492 first16 window and v1491 authored real-mode probe remain in the
focused comparison note and prior public snapshots. Their pre-dispatch-policy
statements describe code 91c0e94, not the new cfe5ac7 default check event.

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
