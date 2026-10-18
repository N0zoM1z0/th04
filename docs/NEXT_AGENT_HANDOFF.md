# Resume TH04 reconstruction

Updated 2026-10-18. Complete DOS/native goals remain active. Read actual heads
and DOS-root irq-service-v1495/finish.json. Root probes distinguish protected
monitor and V86 BIOS returns; native code stays 19c1d37. CPU/boot ownership stays open.

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

Heavy work stays serial: CPUQuota35%, MemoryHigh256M, MemoryMax768M,
MemorySwapMax0, CPU1/Nice19, TasksMax64 and LimitCORE0. Only View uses the
recorded compile-only soft/profile exceptions in RE_HANDOFF; do not repeat the
known O2/O1 sanitizer failures. Keep runs muted/headless, Windows compile/link
only, and use no physical host keys/focus/audio or device workarounds.
