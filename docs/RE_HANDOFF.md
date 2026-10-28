# TH04 current handoff

Current priority (2026-10-27): native Windows x64 functional playability.
The user authorizes muted background Windows testing with process-local input
hooks and temporary no-life-loss patches. Overall flow takes priority over
original DOS pixel/timing identity; defer further UBSan work for this task.
Keep English code/docs and gpt-6.1-sol: commits.

## Portable64 Windows release (2026-10-27)

The repository README now opens with a release notice and the public
[gameplay video](https://www.youtube.com/watch?v=ryCOOMZ5PBI).
The README includes numbered data/setup and Windows/Linux build steps.
[PREPARE_DATA.md](PREPARE_DATA.md) documents original two-floppy installation,
installed-file hashes and the portable preparation script; [PORTABLE.md](PORTABLE.md)
covers runtime/build options. The previous landing page is preserved in
[README_HISTORY.md](README_HISTORY.md).

The new native `port64/prepare_assets.py` prepares the supported installed
Japanese full-version files into a portable-only FAT12 container and prepares
pinned font/rhythm resources. Published EXE resident checks retain all65outputs
against the old image, including27BMPs/9PCMfiles; five synthetic importer tests
pass. [Data preparation evidence](reconstruction/product/TH04_PORTABLE_DATA_PREPARATION.md)
records geometry, identities, independent mtools readback and scope.

The public-source cold Windows x64 product is
`8257fbf8e952690ab8963844ba92f810399f9f67ca74db463ca006aaf3fbe750`.
Only the game and two audio checks are cold built (128steps), without private
cache/game-data inputs. Actual Windows Music Room/input and full Normal87454 /
earned Extra27871 pass with unchanged complete state/input/CFG/SCR. Original
ST02 register/IRQ and32sec mixed PCM plus alias-control bytes retain the
previous validated values; silent real WinMM has0drops. The source program is
unchanged from8a178d24; PE identity/RVAs are separately attested for release.
[Portable setup/build documentation](PORTABLE.md) now separates download/run,
external inputs, saves, audio profiles, Windows/Linux builds and packaging.
Public source is `port/modern-64`; main remains the DOS reconstruction branch.
The Windows release ZIP uses an allowlist and excludes game data, fonts/ROMs
and saves. The optional no-death launcher remains bound to attested hashes.
Historical portable README snapshots move to native
`docs/port64/PORTABLE_HISTORY.md`; their old runtime limits stay historical.
This publication batch changes docs/build/package tooling, not game C++ code.

## Current portable audio fidelity (2026-10-27)

The sole D-drive product is `8a178d24c284e1703c4ffa71e0b68c4a4f0845481604b7e2655dae16c9752940`.
IRQ-compacted key-off/on pairs were lost before synthesis; committing each key
edge restores repeated FM attacks. Bad Apple bass RMS421.26 versus independent
libopna424.34 (old26.75). Corrected FM/SSG balance and bandlimited48kHz output
also remove the dominant masking and reduce the authored alias control44.8dB.
Three original PMD86 start writes are restored;32sec ST02/ST00/OP register
streams match the original driver under the recorded IRQ schedule. A discarded
operator-pipeline-delay patch does not explain the fault and is not shipped.
Both23-song corpora/two-loop Stage3 controls, actual Music Room navigation,
silent real-WinMM0drop, full Normal87454/earned Extra27871 and preserved state,
input/CFG/SCR comparisons pass. Manual BATs retain pmd86/ROM and sound enabled;
background tests stay muted. No user volume/save or DOS-exact changes.
See [fidelity evidence](reconstruction/product/TH04_PORTABLE_AUDIO_FIDELITY.md).
The [preceding profile/transport evidence](reconstruction/product/TH04_PORTABLE_AUDIO_PROFILE.md)
is historical and did not independently establish synthesis fidelity.

## Ending/registration rendering and seamless invincibility (2026-10-27)

UI/no-death baseline Windows product `2dfd38e8eafefde4f0f428633c6dc3c31c1dd1ca6ff1211bfedc8d6d37f2e4a2` batches MAINE copies, packed pictures,
glyph rows and registration colors. All eight Ending graphics scripts/11 files
and 112 registration files remain byte-equal; actual Windows Ending→name→save→OP
controls pass. Cursor taps respond on the first sampled refresh; the held-key
33-refresh initial delay is retained. Writer-close is about 3 ms in this fixture.
The no-life-loss BAT now enables true no-death before both collision latch paths;
protected Normal 87454 and earned Extra 27871 have zero misses/respawns and close
correctly. Ordinary contact still dies normally. Both manual BATs enable sound and share the sole packaged `th04-port64.exe`;
the temporary smooth filename and old executable are removed.
See [UI/no-death evidence](reconstruction/product/TH04_PORTABLE_UI_AND_INVINCIBILITY.md).

## Earlier portable rendering and Extra frame delay (2026-10-27)

Earlier Windows x64 release `eaa05bdde3c21f702df7b6d9885aa78813216a18449d34e56b296f85fe437e3a` fixes a retained
defeat delay that made Gengetsu run at half speed. Fully rendered Extra29251
passes; current NormalReimuA90294 also clears all six stages/GoodEnding/freshOP
with complete logical states/inputs equal the earlier release.1151 dense samples
now request1 rather than2, while128 defeat admissions
retain2. Original MAIN0AAF:0002 (fileC2F2) independently resets the request.
Tile/sprite rows, color conversion and Windows deadline waiting are optimized.
Actual window/input/Bomb/pause, Stage2 transition and Bomb snapshot controls pass.
The user deleted the old preview; the complete D:\Entertainment\Game\Touhou\th04-reconstruct package is recreated and hash-verified.
Both BAT launchers enable audio; automated tests remain explicitly muted.
See [render/performance evidence](reconstruction/product/TH04_PORTABLE_RENDER_PERFORMANCE.md).

## Earlier Windows functional smoke (2026-10-27)

The retained Windows x64 release product passes an actual inactive-desktop
hooked window/input/Bomb/pause/close test with zero audio opens. No gameplay
source or executable file was changed. A memory-only no-life-decrement patch
then completes Normal Reimu A (90294), Normal Marisa B (85134), and same-session
Normal-earned Extra Reimu A (29251), including expected endings, registration,
physical score checksums/clear masks and fresh OP. An unmodified 34651-admission
route reaches natural Game Over/registration/fresh OP and agrees with GNU on
all inputs, states and final CFG/SCR. Component pause, Continue, score and
configuration controls also pass. Full clears are logical replay controls,
not continuous window play or ordinary difficulty acceptance.

Private result index: DOS-root `.analysis/host-smoke-20261027/verification.json`.
Preview: `D:\Entertainment\Game\Touhou\th04-reconstruct`;
`Play.bat` is ordinary and `Play-no-life-loss.bat` patches only its new process.
The current launchers enable audio and use separate saves. The latter includes earned test unlocks.
Physical input/audio and continuous visual quality are ready for manual review.
See [functional test scope and replay](reconstruction/product/TH04_WINDOWS_FUNCTIONAL_SMOKE.md).

The following v1497 sections retain the historical product-build identities;
"Windows compile/link only" there describes that earlier batch.

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
Do not launch on the user's active desktop or operate physical host devices.
The isolated muted Windows tests authorized on 2026-10-27 are described above.

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
