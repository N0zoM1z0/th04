# Resume TH04 reconstruction

Updated 2026-10-18. Complete DOS/native goals remain active. Read actual heads
and DOS-root dispatch-epoch-v1493/finish.json. Native code cfe5ac7 adds delayed
PIC checks and separate CPU availability. Original CPU/boot timing remains open.

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

## Delayed PIC checks and original timer audit (v1493)

Native code cfe5ac7 adds a separate delayed PIC check to the live keyboard
path. A ready UART byte latches the request; IF alone cannot bypass the pending
check. IF, normal-trap decoder and NMI availability remain separate CPU gates.
Mask/EOI transitions can schedule a check, accepted IRQs rearm it, and a blocked
CPU preserves an already raised check. Callbacks may arrive after their deadline.
The window uses the independently observed 406 ns configuration, rounded upward
to 234 peripheral quanta. CPU acceptance, BIOS read and EOI after that check
remain an explicit immediate portable policy, not original ISR instruction cost.

The normal original boot completes eight Stage1 updates. Complete relocated
MAIN attestation precedes observations; provenance is candidate-local-attested.
130 complete timer transactions audit 1069 packet records, removing 130 raw
bookkeeping regressions with zero canonical regressions. MAIN entry remains a
separate raw snapshot. Five actual UART completions show Check0/Pending1, then
the delayed callback sets Check1/Pending0 before V86 CPU acceptance. The five
canonical observation intervals are 15 emulator counter cycles each; they are
not a physical UART-to-BIOS delay. Ten recorded queued event deadlines remain
distinct from CPU observation time and round to the same 234-quanta policy.
The current gate reproduces 85 observed normal-primary states; the earlier
strict-deadline candidate rejects actual late callbacks. Active cascade routing
outside these bounded intervals remains excluded.

Source replay, fresh affected-product builds, frontend/original-ISA checks and
claim limits are detailed in the main-branch TH04_REPLAY_DIFFERENTIAL note.
Current source has 573 files, closure
e7aa088c4202b23c339f9129a4cc267f2e85ea27ea2dc4fc538e626242f62783.
This is 15 fresh affected objects/12 programs with 112 unrelated core objects
reused per role, not an all-source cold cohort or full campaign acceptance.

Next bind CPU availability, BIOS/EOI cost, other IRQ producers and boot epoch.
Keep peripheral event deadlines distinct from CPU observation time, including
late transport callbacks. Default host callbacks run at their exact deadlines.
All historical strict negatives remain unclosed; both full goals stay active.

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
