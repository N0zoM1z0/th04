# TH04 current handoff

Session handed off at the user's request on 2026-10-18. The complete maintained
DOS four-product game and faithful native x64 objectives are unfinished. Resume
on a new user instruction. Keep English code/docs and gpt-6.1-sol: commits.

## Host joystick input and handoff (v1497)

Native code ea41be4 connects SDL and WinMM joystick producers to both window
backends, menu edges, held UI actions and MAIN's live byte sampler. Native host
policy uses the first two axes/first hat, button 0 Shot/confirm and button 1
Bomb/cancel, with a half-range analog threshold. A connection or focus regain
must first be neutral. Missing devices and failed initialization leave keyboard
input available. Raw SDL axis/button bindings vary by device; this is an explicit
host policy, not an original PC-98 device or timing observation.

Complete injected APIs execute all 131072 X/Y axis values and 64 hat/button
combinations in GNU and UBSan without opening devices. Original unchanged MAIN
instructions reproduce 64 production pin mappings per role and nine actual
frontend latches per role. Two compiled exit-0 mapping defects each reject 32
cases. Both real headless frontends enter MAIN through three controller menu
confirmations, move Right/Down, sample Shot and handle unplug across four frames
and nine polls. Observer off/on pools/frame/RNG agree. The prior 31-poll keyboard
and 81-read elapsed controls also pass. These are shared frontend tests, not
actual SDL/Win32 windows or controller acceptance.

Current source: 577 files,
51b9f3887346d5b444bbfd07d296b83175be420acda95c9598f250cae6647734.
The initial cohort cold-builds four affected objects per role and freshly
relinks 92 GNU/8 UBSan/5 Windows programs. GNU 88 CTests and seven UBSan controls
pass. A WinMM continuous-POV/query-header correction then cold-builds nine backend
objects: three GNU objects retain exact bytes; source-location metadata changes
UBSan objects, so both UBSan and Windows app/joystick programs are relinked.
Three unchanged View objects retain their initial compiler identities. Current
105 program paths and all 12 object identities are in correction.json's receipt;
use program_paths, since the current products span two directories. This is
not an all-source cold cohort. Windows remains compile/link only.

Source/objects/commands and the rejected equality assumption remain private and
recoverable. The canonical corrected source capsule is under the first
host-joystick-v1497-final directory despite that driver's later failure; do not
delete it. See the focused differential note for API references and scope.

## Verification limits and remaining work

Original CPU/OPNA service timing, common boot epoch, other IRQ producers,
actual controllers, continuous display, full source/native campaigns, Windows
runtime and NP2/hardware remain open. Historical exactness is unchanged.
Original-versus-original retains 30 tail/23 raw-GDC differences; source-DOS's
19-key/23-GDC and native physical 40-tail/7837-boundary failures remain separate.
Old75 is inferred, not a directly captured scalar sample; do not hunt another
whole route solely for that phase. Earlier complete state/picture agreements
retain their original source vectors and scenarios. See the differential note.

Next connect CPU/OPNA service ownership and common-reset timing without fitted
input words or fixed IRQ delays. Preserve independent physical, UART, PIC,
BIOS-byte, Shift and game-latch owners. Reuse the retained comparisons before
planning another capture. Do not reopen deferred MAIN exactness cases.

## Recovery and cleanup

The user authorized retirement of unnecessary history on 2026-10-19.
Use DOS-root `.analysis/cleanup/retire-history-20261019/recover.py` and its
`keep.json`/`aliases.json` for the scoped current handoff. The cumulative
v1497/storage recovery contract is retired; older full-history commands can
refer to intentionally deleted payloads. Historical receipts remain unchanged.
See `ANALYSIS_RETENTION.md` for retained baselines and the deletion receipt.

Current 105 programs, 12 object identities, source capsules and reused link
inputs stay available. Build only affected targets in fresh directories; do
not automatically rebuild all programs or replay every historical phase.
Shared ABI/layout changes and exact promotions still require their proper gates.
The retirement removes 65202 files and reduces storage from 15.31 to 7.93 GiB
(7.38 GiB net). No product compilation or relink is performed.

## Resource limits and checks

Heavy jobs remain serial at CPUQuota=35%, CPU1/Nice19, hard 768MiB/no swap,
64 tasks/LimitCORE0. Ordinary checks use soft 256MiB. View retains GNU/Windows
O3/GGC5/4096 soft 640MiB or UBSan O0/GGC1/1024 soft 768MiB; UBSan main.cpp uses
O2/GGC5 soft 320MiB if rebuilt. Initial cohort peak: 683098112 bytes,
zero OOM kills. Keep Ghidra384MiB/one Java processor and all checks muted/headless.
Do not launch Windows GUI/input/audio tests or operate physical host devices.

The v1497 handoff CIs passed (root 593/native 354). Current retirement
checks are recorded in retire-history-20261019/verification.json.
The historical full recovery predates retirement; use the scoped cleanup checks.

Entry heads were root 10e464b/native e0c6569; use actual Git heads and the latest
finish receipt for final publication. Root and native are distinct worktrees.
Push root main and native HEAD:port/modern-64 separately. Finish tracking,
scripts/ci.py in both branches and git diff --check. ci.py ignores --help and
runs the entire CI. No current cohort may be incrementally rebuilt.

Original MAIN: 156258 bytes/1136 relocations,
077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b.
Source MAIN: 200279 bytes/1183 relocations,
778641ab845bcd67c6888bacc049e2cfa20fddda844681d3d2fd164f8386abc9.
DOS products remain .analysis/build/dos-four-products-v1443. Pinned provenance
remains candidate-local-attested; target/unit exactness is unchanged.
