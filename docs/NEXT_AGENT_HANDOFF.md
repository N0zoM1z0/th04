# Resume TH04 reconstruction

Updated 2026-10-18. Complete DOS/native goals remain active. Read actual heads
and DOS-root joystick-byte-source-v1496/finish.json. Native code 72ab70a
completes optional live joystick sampling. CPU/bus/boot ownership remains open.

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

## Live byte joystick sampling (v1496)

Native code 72ab70a completes optional joystick enable/pin callbacks in the
live byte path: eight BIOS bytes, Shift store, enable, then active-low pins only
when enabled. Low six actions OR into the existing Reset/Sense latch.
Original MAIN 130E:07AB..07C4 queries Shift before calling 0000:366A..3675;
only that helper brackets OPNA with CLI/POPF and preserves incoming IF0/1.
Bus/CPU timing remains the producer's responsibility.

Root command 33cfaa4, scripts/probes/verify_pc98_input_bytes.py, checks 7168
controlled cases/14336 target calls plus 16 IF controls/64 extra calls. The old
byte API differs in 1000 action rows; current values/read traces agree. Four
compiled exit0 semantic defects reject. Real MAIN and shared FrontEnd checks
cover all 14336 actions and four joystick-driven frames/nine polls. Independent
original ISA reproduces the nine measured latches; observer state equality,
existing 31 polls/81 elapsed reads/21 physical keys pass. See the main-branch
TH04_REPLAY_DIFFERENTIAL note for controls and limits.

Source has 573 files, closure 856cd0831427893d73c1660ccd41db022a593cb2cb2657db7df2f72020bcf2ed.
Cold affected objects: GNU55/UBSan29/Windows26; all 102 programs are fresh relinks
with 474 unchanged inputs by SHA. GNU 87 fresh-directory CTests and six UBSan
controls pass; Windows 4 is compile/link only. This is not all-source cold replay.
Next connect host/OPNA pin production and its masked CPU service, common boot
epoch and other IRQ producers. Full campaigns/continuous display, Windows
runtime and NP2/hardware remain open. Both complete-game goals stay active.

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

Heavy work stays serial: CPUQuota=35%, CPU1/Nice19, hard 768MiB, no swap,
64 tasks and no cores. Normal checks use MemoryHigh=256MiB. View uses GNU/Windows
O3 GGC5/4096 soft 640MiB, or UBSan O0 GGC1/1024 soft 768MiB. UBSan main.cpp now
uses O2/GGC5 soft 320MiB after a recorded 256MiB pressure stall; its fresh 320MiB
object replay is byte-identical and has no high/OOM events. The original journal
entry's nominal 256 field is qualified by main-soft-amendment.json. Cohort peak
616353792 bytes/no OOM. Do not repeat historical failed View O2/O1 profiles.
Keep emulators muted/headless and Windows compile/link only; no physical host
keys/focus/audio or device workarounds.
