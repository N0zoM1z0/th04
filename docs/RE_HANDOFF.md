# TH04 current handoff

Updated 2026-10-18. Build the complete maintained DOS four-product game and
faithful native x64 game; both goals remain active. Original Japanese DOS versus
reconstructed DOS is the primary behavioral comparison. Keep English code/docs,
gpt-6.1-sol: commits and frequent pushes to main and native HEAD:port/modern-64.

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

Use DOS-root .analysis/reconstruction/probes/dispatch-epoch-v1493/recover.py.
It chains 90353 incoming identities, including all three v1492 late files,
and 10219 exact aliases. All 19 new restores preserve SHA, size, mode and
nsmtime; two restored input programs execute and the maintained epoch reader
passes with all restored inputs. Exact archive readers also validate the retired
clock/admission streams without restoring them. Keep all current 12 game
programs/15 objects/link inputs, source capsules, compiled semantic controls,
negative observations and every inherited provider. The entry vector reuses the
canonical v1491 capsule; only the changed current source gets a new capsule.
Closed new regular allocations save 84185088 bytes after provider cost.
The separately canceled unused outputs remove 9023488 disposable bytes;
that is not scientific alias credit or a phase-entry storage decrease.
Never build or invoke CTest in retired cohorts; use a fresh replay directory.
See ANALYSIS_RETENTION.md for source vectors, profiles and exact consumers.

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
