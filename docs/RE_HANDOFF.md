# TH04 current handoff

> Current workflow: follow the **Highest priority** section in `AGENTS.md`.
> Prefer affected exact comparisons and useful Markdown knowledge. Ordinary
> notes do not require full CI, native replay or document-hash/pin refreshes.
> Older broad validation instructions apply only when their impact is relevant.


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

Preview: `D:\Entertainment\Game\Touhou\th04-reconstruct`;
`Play.bat` is ordinary and `Play-no-life-loss.bat` patches only its new process.
The current launchers enable audio and use separate saves. The latter includes earned test unlocks.
Physical input/audio and continuous visual quality are ready for manual review.
See [functional test scope and replay](reconstruction/product/TH04_WINDOWS_FUNCTIONAL_SMOKE.md).

The following v1497 sections retain the historical product-build identities;
"Windows compile/link only" there describes that earlier batch.

## Input and timing work

The shared frontend supplies live keyboard and joystick bytes to MAIN. It
preserves read order, Shift, optional active-low joystick pins and Reset/Sense
latch behavior. Original MAIN execution and injected host controls support the
functional mapping. Actual controller behavior and original CPU/OPNA timing
remain separate questions.

Original-versus-original retains 30 tail/23 raw-GDC differences; source DOS has
19 key/23 GDC differences, and the native physical-input fixture has 40 tail/
7837 boundary differences. These observations have different scenarios. Do not
fit IRQ delays or repeat a full route solely to hunt old75's inferred phase.
See [the focused comparison note](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md)
for the useful findings and next experiment.

## Working state

Source and Git history replace old source capsules. Historical programs,
captures, cleanup journals and their recovery aliases are disposable; use
fresh output for the next comparison. Keep original inputs, active tools,
Ghidra projects, exact ledgers and complete comparison drivers. See
[retention](ANALYSIS_RETENTION.md) and [workflow](RE_WORKFLOW.md).

Default `python3 scripts/ci.py` is private-input-free and does not compile,
launch analyzers or regenerate documentation. Run affected exact/tool checks
separately. Build heavy jobs serially, headless and muted; preserve game-specific
writable state. Root `main` and `port/modern-64` are separate worktrees.
