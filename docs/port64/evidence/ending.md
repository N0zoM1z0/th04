# Ending evidence

Historical bounded results, preserved from `docs/PORT64.md`. Current state is
[the port overview](../../PORT64.md). Original CPU execution and adapter scope
remain explicit; successful component controls do not accept complete gameplay.

## MAINE Ending script and graphics owner

v1291 adds `cutscene::Script` and `cutscene::Scene` as native C++ owners.
`Script` preserves the three-digit/default parser, twelve-byte filenames,
WORD cursor wrap, mask order, Escape sampling and graphics/page/palette/audio
requests. Its clock separates release/press waits, explicit frame delays,
non-skippable palette fades and song-measure waits. A sound owner must explicitly
complete a measure wait; key input cannot stand in for song progress.
`Scene` owns both640x400 indexed graphics pages, the saved480x64 text-box
background, palette and current PI slot. It decodes supplied resources at
runtime and performs quarter selection, EGC mask copies, graphics-font effects
and gaiji drawing. The asset collection must outlive the Scene: its loaded PI
slot borrows a stable picture-map entry. No original font, picture, script or
executable is embedded.

Fresh execution of the pinned MAINE DIET wrapper at load1000/2000 recovers the
same62,414-byte payload and559 relocation sites. Packed SHA is670de6ba;
payload SHA is7495ae43. The active Ghidra database attests the packed wrapper;
the decoded function observations below use the hash-bound raw payload, not an
invented decoded-database attestation. Provenance remains
`candidate-local-attested`. Original0A05:07F7 dispatcher and0A05:0DAC animation
execute their own instructions in the control oracle. External consumers are
intercepted; original0CC7:058C font/effect kernels additionally execute against
an explicit supplied CGROM adapter in the pixel oracle.

Important target-specific behavior:

- The picture rectangle is160,64,320,200. The standalone DOS dispatcher
  candidate's left-zero constant cannot supply this native owner; a source name
  or historical acceptance is insufficient to attest its include context.
- MAINE samples key_det bit0010 for Escape. Frontend MAIN action masks require
  explicit translation. Ending text uses graphics page1, with no per-character
  delay; the interval controls the text-box mask passes.
- `k` waits without publishing the box; `@` clears both pages without replacing
  the saved background. Preserve both quirks when composing later flows.
- `_ED000.TXT` supplies the two-byte string ",4" too. Original halfwidth font
  effects operate on AL with WORD weights and a little-endian rotated store;
  aligned heavy/bold/black spill dots differ from fullwidth text. Native keeps
  these dots rather than correcting the original renderer.

Validation at `.analysis/port64/maine-ending-v1291/`:

- Eight actual scripts and ten synthetic controls at four held-input states
  produce72cases/86,614 complete ordered records, invariant across two original
  load segments and identical GNU, Wine and optimizedUBSan consumers.
- An independent NumPy raster consumes original requests and target mask words.
  Eight routes have twelve checkpoints each:192 complete indexed pages and96
  palettes/page-selection/scroll/tone states match on all three builds.
-264 full-frame font controls cover six fullwidth/ANK/space/kana strings,
  four weights, eight alignments and additional positions/colors. Both original
  relocation loads agree with each native consumer. The route gallery executes
  another1,025 per-route string/weight/align controls.
- Three incremental builds pass30CTest each and produce31AMD64 executables.
 28 prior GNU products are raw-identical;28 prior PE products differ only in
  timestamp/checksum.26 prior UBSan products remain raw-identical. The changed
  dialogue owner passes its independent original script/activation/font oracle;
  eight existing PI/UI/MAIN smoke fixtures retain their prior hashes.

`verify_cutscene_windows.ps1` executes the same binaries on actual Windows,
including all30 contracts,72 script streams,17 PI decodes,264 font controls
and192 pages/96 palettes. It compares complete bytes against the attested GNU
references and preserves the original producer receipts separately.

Replay from the native worktree:

```sh
python3 port64/verify_cutscene.py --target ../../targets/th04/maine.exe \
  --decoded-dir ../../port64/maine-ending-v1291/decoded-original \
  --hdi ../../runtime/images/zun.hdi \
  --exe .analysis/port64/linux-live-v1251/th04-port64-cutscene-contracts \
  --output-dir NEW-control
python3 port64/verify_cutscene_pixels.py --target ../../targets/th04/maine.exe \
  --decoded-dir ../../port64/maine-ending-v1291/decoded-original \
  --hdi ../../runtime/images/zun.hdi --font-bmp SUPPLIED-FONT \
  --exe .analysis/port64/linux-live-v1251/th04-port64-cutscene-contracts \
  --reference-dir NEW-control --output-dir NEW-gallery
```

PI decode is a separately regressed dependency: the complete decoder body is
unchanged except for external ownership. This gallery is not independent
validation of the original PI decoder or a physical PC-98 video capture.
Mask/font acceptance covers actual Ending inputs and the stated font matrix;
arbitrary hardware clipping, all unused font effects and real audio timing are
separate. No DOS source, exact/unit/function ledger or published Windows GUI is
changed. Next join MAIN's score/run counters and MAINE resource lifetime to this
owner, then implement Staff Roll, verdict and registration. The ordinary native
preview still holds at the Ending transfer; component success is not full-game
completion. Semantic work stays limited to concrete port ambiguities.

Final source manifest: `df9ce765c305847b34fd3eb3e0dd8bcfe9029d0a923d4ea8937d3f6cd3125262`
(196 files). `source-freeze.json` and `build-review.json` bind current sources,
all31 executables per build and the actual-Windows reference identities.
After verification,1,368 completed Wine/UBSan/Windows pixel/font files are
losslessly gzip-archived, reclaiming320.3MiB;116 active executable/Windows-root
hashes are unchanged. The current GNU reference gallery remains expanded.
`output-archive-receipt.json` records every member and readback. Restore an
archived output with `gzip -d -- PATH.bin.gz` before direct historical comparison.

## MAIN-to-MAINE Ending integration

The v1292 frontend continues ordinary MAIN into all eight Good/Bad Ending
scripts. The preceding v1291 component supplies the script/page/font owner;
this batch supplies the executable lifetime, resident publication and host
presentation. Staff Roll, verdict and registration are subsequent owners.

`run_statistics` copies the eight displayed HUD digits and cumulative run
counters. It deliberately excludes pending score, as MAIN0AAF:3CEE saves those
existing bytes before GameExecl0AAF:3D0D. Completed-frame statistics increment
at the actual tail, so the nonreturning Ending call excludes that suffix. STD
counts stop at the boss callback and survive Stage replacement. Stage reset now
clears item entities while retaining items_spawned; the target's complete nine
clear regions do not own MAIN DATA:2398. Headless checks use no host clock;
interactive slow-frame statistics sample host work in17,730,496ns periods.
That host sample is a backend approximation, not measured original PC-98 timing.

`maine::Ending` writes GOOD/FF/type0 or BAD/FE/type1 before song fade4 and the
mandatory MAIN blackout. The observed0000:0666 loop makes eighteen palette
calls over273 VSync waits; Escape cannot bypass it. Publication precedes the
native resource-release callback, which runs while the old MAIN generation and
LCG still exist. Entering MAINE then creates a fresh process-local LCG at1.
The original additionally frees an optional EMS handle after score publication
and before its other counters; native EMS storage is absent. Original release
order and execl's explicit failure return/stack path are checked separately;
those adapters do not execute a full DOS replacement.

MAIN host actions translate cancellation explicitly to MAINE key_det0010;
other held actions become a wait key. MAINE's unsigned song-measure comparison
requires actual reported progress when audio is active. The current inactive
backend executes the original minimum-frame fallback instead. Story graphics
use their shown/access pages, palette tone and scroll; old MAIN/TRAM resources
are gone. Window and headless frontends use the same owner.

Validation at `.analysis/port64/maine-join-v1292` includes:

- Original MAIN72 Good/Bad/EMS publication and cleanup-order controls;
 378 frame-counter wrap/unsigned-threshold vectors; the full fade loop.
- At decoded MAINE loads1000/2000,120 sound-mode/fallback/measure controls and
 24 palette-output controls. Palette bytes are RGB: redAC, greenAA, blueAE.
- Three fast incremental builds,31 AMD64 products and30CTest per host.
 Linux, Wine and optimizedUBSan each traverse24 natural menu/STD/dialogue/boss
 routes, covering two characters, actual A/B choices, Easy/Normal/Lunatic and
 idle/shot final battles. Each compares576 complete pages,288 palette/state
 checkpoints and288 RGB frames against the independently checked v1291 gallery.
 Actual Windows consumes the same resident/counter/fade and route references.
-442 original stage-reset/midboss seed controls and four native Stage1-to-Stage2
 routes. The reset consumer's executable bytes remain identical through the
 final GUI-only diagnostic-log edit. The complete9 original clear regions,
 retained353 process draws and cumulative item-spawn sentinel are checked.

The old fixture drivers pressed Right on the shot screen, which only responds
to Up/Down. Their B-labelled Stage4/5/6 paths were actually A; retain their
pixel/phase evidence with that narrowed input scope. This batch fixes all four
such drivers and asserts the real resident character/shot selection for the
new matrix. A separate negative finding corrects the v1291 PNG-only RGB
swizzle; its indexed pages/palette bytes and original font controls are intact.
The original indexed references and the new CPU palette controls drive current
RGB comparisons directly. Windows state streams useCRLF; compare their integer
records, while complete page/palette/BMP hashes remain strict. A source-snapshot
mutation guard also rejected development checks that spanned adding verifier
files; accepted frozen controls are stored separately.

No DOS source or exact ledger changes. Original targets remain
candidate-local-attested; decoded MAINE binds payload7495ae43, while its active
Ghidra database attests the packed wrapper. The reference PI decoder is a
separately regressed dependency. No physical PC-98 capture, full original-game
route, music synthesis, player-death/Bomb/Continue/Extra behavior, host FPS or
saved-score completion is claimed by this Ending batch.

The validated v1292 Windows preview is published under
`D:\Entertainment\Game\Touhou\th04-reconstruct\port64-preview\v1292-ending-join`;
root `start-th04-port64.bat` uses the new GUI. The versioned launcher uses its
own original HDI/font, while the root launcher retains the user's normal image.
Both English launchers state the Staff Roll frontier. Previousv1290 GUI/launcher
are retained and2,169 pre-existing Windows files outside the two authorized
native replacements keep their hashes. DOS launchers/products/config/saves are
unchanged; publication does not auto-launch the GUI.
After full readback,8,640 completed render buffers/BMPs are gzip-archived,
reclaiming3.21GiB;553 protected original-reference/active-binary/Windows-root
hashes stay unchanged. Original CPU traces and v1291 raw indexed references
remain expanded. Restore v1292 media using `gzip -d -- PATH.bin.gz` or
`PATH.bmp.gz` before direct historical consumers; the archive receipt records
every original/compressed digest.96 derived v1291 PNGs have correctedRGB
presentation with original indexed/palette hashes retained in a separate receipt.
