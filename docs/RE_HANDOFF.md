# Native TH04 current handoff

Updated 2026-10-18. Build the complete maintained DOS four-product game and
faithful native x64 game; both goals remain active. Original Japanese DOS versus
reconstructed DOS is the primary behavioral comparison. Keep English code/docs,
gpt-6.1-sol: commits and frequent pushes to main and native HEAD:port/modern-64.

## Physical keys and ordered host delivery (v1490)

Native code 5626571 feeds Win32/SDL keydown/keyup delivery into the persistent
keyboard before UI aliases. Arrows and keypad cardinal keys occupy distinct
BIOS bits. Return/keypad Return and left/right Shift keep distinct physical
identities despite sharing scans. OS repeats do not restart firmware repeat;
releasing its owner does not transfer repeat to another held key. Short pulses
survive between game polls. Focus loss serializes releases; focus gain alone
does not synthesize makes. Snapshot fixtures retain an explicit stable order.

The time is host delivery time, not platform event timestamps or original
physical time. Timer/RX events at or before delivery precede the new edge.
The available-CPU policy remains explicit. Original IF/PIC masks, priority,
EOI, latency, boot epoch and event-timestamp conversion remain open.

All 21 key scans/matrices agree with the pinned DOSBox-X mapping. Unchanged
MAIN130E:06BC..07C4 reproduces 21 explicit stable BIOS fixture words, with
neutral joystick and given INT18 modifier status. An exit-0 alias-fold mutant
fails four keypad cases. Portable controls cover event order, short pulses,
same-scan releases, OS repeat suppression and focus ownership. Current GNU
and UBSan retain 31 real observation-on/off frontend polls and their original
sampler comparison. The new live elapsed-source API passes four frames/nine
polls/81 byte-and-Shift reads. The retained actual COM IRQ fixture preserves
27 operations/four accepts. No fresh original host-timing capture is claimed.

Current source is 573 files, closure
efee7a9f86af08612690a06723671a147d7431125d8c6c07b40ab967e96e7b22.
The ordered-host-keys-v1490 replay cold-compiles all four host_window.hpp
consumers per role and links three programs each for GNU, UBSan and Windows.
It reuses 112 unrelated core objects per role and unchanged link inputs by SHA.
This is bounded affected replay, not a fresh all-source cohort or 87-CTest
rerun. GNU/UBSan focused controls pass; Windows is compile/link only.
GNU/Windows View uses O3/GGC5; UBSan View uses O0/GGC1 with UB/bounds retained.
Old full cohorts keep their own source closures and acceptance scopes.

Heavy jobs stay serial 35%CPU, CPU1, Nice19, hard 768MiB/no swap/64 tasks/core 0.
Checks use 256MiB soft; View alone uses recorded 640/768MiB compile profiles.
Build peak is 579.215 MiB; this batch has zero OOM kills.
The two real v1489 compiler OOM failures remain preserved. Caps are unchanged.
No physical host keys/focus/audio or GUI workarounds were used.

Next measure original request/timer/accept/read ownership and first differences.
Do not fit a phase/fixed IRQ delay or hunt old75 with another full route.
Common-reset DOS/native campaigns, Windows runtime and NP2/hardware remain
open. Existing strict negatives and both full goals remain active; historical
DOS products/source and exactness states are unchanged.

## Persistent keyboard and scalar MAIN input (v1489)

Native code a4e97bd connects the actual Win32 and SDL MAIN paths to a persistent
keyboard, UART, pending IRQ and BIOS owner. The device survives application
process generations. Physical host changes, 1 ms firmware ticks, serialized
arrivals, CPU acceptance and BIOS reads remain separate operations. Elapsed
nanoseconds convert to integer peripheral quanta with a retained remainder;
splitting an elapsed interval preserves the configured continuously available
CPU policy. Focus loss serializes releases and stops repeat ownership.

MAIN consumes groups 7, 9, 8, 5, 2, 0, 3, 6 independently, then reads Shift.
Reset clears before the first callback; each group ORs into the game latch
before the next read. Observation.before still records the pre-operation latch.
The physical observation is a vector of consumed bytes, not necessarily one
instantaneous matrix. Existing whole-sample movies and the latch/UI flow remain.

The real headless FrontEnd passes four frames, nine polls and 81 byte/Shift
reads, including a make arriving after the tail's Shot read and a focus release.
The retained 31-poll observation-on/off scenario also passes independent original
sampler execution in both current GNU and UBSan programs. Twenty-five actual
original action words, using 200 directly observed byte values after a genuine
reset, agree through the new byte sampler. Shift is a given zero input here,
not a new independent INT18 status observation; joystick pins are neutral.
Two compiled exit-0 defects reject: late Shot consumption fails the portable
interleaving, while Sense overwrite fails actual original action words.
The persistent Device also preserves all 27 operations/four CPU accepts of the
independently checked actual DOS COM IRQ fixture.

The window explicitly selects an always available CPU service policy at event
boundaries. It does not model the original CPU/PIC masks, priority, EOI, dispatch
latency or boot phase. Host aliases still aggregate as before; simultaneous
polled edges use a declared stable order. This is a functional integration,
not acceptance of default physical timing or a fitted serial-to-BIOS delay.
Original 58/87-cycle, old 82-cycle and authored 16-cycle cases stay separate.
Next compare the connected path against original request/timer/accept/read
boundaries and measure the first differences; recover the remaining CPU/time
and physical-key ownership. Do not hunt old75 with another whole-route capture.
Both complete DOS/native goals and every strict negative remain active.

## Maintained products and comparison limits

Native source is 573 files, closure
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

Phase entry heads were main62d507c/native5a960e1; read actual heads and the latest
finish receipt. Finish focused comparison, tracking, python3 scripts/ci.py in
both branches and git diff --check; commit/push both branches. ci.py ignores
arguments, so --help runs the entire CI. Complete product goals remain active.
