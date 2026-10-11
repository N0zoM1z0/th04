# Ending evidence

## Palette fade speed and zero-wait completion (v1413)

`maine::Animation` now follows the original palette fade's WORD argument and
signed loop condition. A positive signed WORD waits `1 + 17 * speed` refreshes;
zero and 8000h..FFFFh wait only for the initial alignment. The previous owner
spread a zero-speed fade across another 16 refreshes and used the host's full
integer value for speeds outside the signed WORD range.

Both original OP and MAINE implement fade-in at 0000:0622 (67 bytes) and
fade-out at 0000:0666 (62 bytes), including their complete `RETF 2` exits.
`verify_palette_animation.py` executes these instructions at loads 1000/3333
with explicit one-refresh wait consumers. The 96 controls cover both directions
and speeds 0, 1, 2, 4, 16, 32767, 32768, 65535, 65536, 131071, -1 and -32768.
Each retains all 18 palette calls, 19 tone stores and every wait. The original
temporarily stores 102 or -2 before clamping; those stores remain in the raw
transcripts. Native comparison observes the final tone at each refresh, folding
multiple palette calls that occur without another wait.

Fresh GNU Release and optimized UBSan/bounds builds of the complete Animation
owner each pass all 24 native vectors. An actual compiled 328585f predecessor
fails 14 vectors, while its ten ordinary positive-speed vectors still agree.
This checks the logical refresh sequence; hardware IRQ cadence and DAC scanout
belong to their separate owners.

Frozen producer 528/dbdbcbe5 and complete controls are retained in the isolated
`native-palette-zero-v1413` tree under
`.analysis/port64/native-palette-zero-v1413/`. `verify_closure.py` checks its
source archive, full wait carriers, both compiler outputs, predecessor failures
and 803 frozen text-proof files. CI passes 345 tests. No historical exact
ledger is promoted by this native recovery.

## Text Gaiji memory addressing (v1408)

The shared native `TextPlane` now uses the original `GAIJI_PUTCA/PUTSA`
addresses and store sequence. The row segment is the mutable text base plus
Y*10, truncated to a WORD; the starting offset is X*2, also truncated.
`put()` writes each attribute before its glyph half. `put_string()` writes
every glyph first, then fills attributes using WORD(end-start)/2. A string
of 16,384 characters wraps its offset and fills zero attributes.

These writes can cross rows, spill past the last visible cell, or alias the
attribute bank. The owner retains visible codes at A0000h..A0F9Fh and
attributes at A2000h..A2F9Fh in the existing arrays. Other physical addresses
use 256-byte pages allocated on demand. Normal render-frame copies retain
roughly 8 KiB rather than a full real-mode memory image. Packed 8000-byte
snapshots, overlays and rectangle copies continue to use the visible banks.
MAIN's HUD/Game Over and MAINE registration consume this owner directly.

The maintained `verify_text_address.py` executes original MAIN 0000:1B0C/1B50
and MAINE 0000:0FC4/1008 at loads 1000/3333. It uses the DOS root's attested
original-instruction adapter and captures complete 80000h..DFFFFh memory,
ordered WORD writes and return ES. All 664 native fixtures match all 2,656
original results, and the packed visible banks match the physical projection.
Inputs cover all 256 byte glyphs, additional WORD characters, coordinate and
attribute boundaries, alternate text bases, NUL and lengths through 32,768.
The native comparison checks memory; the separate v1407 DOS comparison checks
the far-call ABI. Guest source-memory aliasing and physical display timing
remain outside this logical string owner.

A cold native core and five selected programs build. Text addressing, HUD,
player lifecycle/Game Over, score registration and registration scene contracts
pass. Optimized UBSan/bounds reproduces the same 664 native results. A compiled
predecessor rejects X80/Y0 and the 2,049-character fixture. Its right-edge
visible output differs in 8 bytes. For the long string, its partially written
visible banks agree even though it throws before completing the original
writes; visible screenshots alone would miss that failure.

Producer 524/6f214e8c, complete compressed memory/write records, GNU/UBSan
programs, compiled predecessor and source archive are retained under
`.analysis/port64/native-text-address-v1408/`. Replay with a fresh build:

```sh
python3 port64/verify_text_address.py --dos-root /path/to/th04-dos-root \
  --native /path/to/th04-port64-text-address-contracts --output /fresh/proof
```

Add `--reference /path/to/original-comparison` to reuse the complete original
transcript. The private `verify_closure.py` checks current source/programs,
replays every retained original write against its seed, and checks frozen
v1405 and DOS v1407 proof identities. Historical exact remains 661/663.

## Gaiji graphics character and string addressing (v1405)

Native `Canvas` now follows MAINE's `GRAPH_GAIJI_PUTC` and
`GRAPH_GAIJI_PUTS` address arithmetic. Both entries calculate the row as
Y*80 modulo 65536, then add unsigned X/8. The string entry retains DI and
adds STEP to the residual bit shift before the next character. Recalculating
each character from a host X coordinate loses that continuity when X or STEP
crosses a WORD boundary. Both entries write a two-byte word followed by the
spill byte at the incremented WORD address.

The recovered consumer handles script characters and shared Gaiji strings
used by score registration, rankings and verdicts. It preserves the installed
256-character BFT bank, header padding and color masking. For example,
X640/Y0 draws at row 1, while Y4096 aliases Y0. Unlike the graphics-font
renderer, Gaiji's row formula does not alias Y1024 to Y0.

`verify_gaiji_address.py` executes the original MAINE 0000:3760 character
entry and 0000:36B6 string entry at load 2000, with DGROUP 0E53 and VRAM A800.
The input adapter supplies deterministic BFT glyph bytes selected by the
original CGROM port writes. All 2,833 complete seeded 640x400 pages agree:
2,148 character controls cover every bank character at eight bit alignments
and coordinate edges; 685 string controls cover negative/large/zero steps,
NUL termination, long strings and WORD pointer wrap. Header padding includes
0, 17, 34 and 65535. Original Pascal return/stack cleanup, DS/SI/DI/BP and the
interrupt flag are checked.

A cold native core and five selected programs build successfully. Five
related component contracts pass. The current font program also reproduces
all 1,037 retained v1404 original pages. Optimized UBSan/bounds checks the
Gaiji caller and Canvas against the same 2,833 original pages. The compiled
predecessor fails the right-edge component contract and a complete original
page comparison (116 pixels at X640/Y0).

Producer 522/bac23324, source archive, original compressed pages, old/new
programs, compiler metadata and receipts are retained under
`.analysis/port64/native-gaiji-address-v1405/` in the isolated
`port-motion-v1402` worktree. Replay with a freshly built Gaiji contract:

```sh
python3 port64/verify_gaiji_address.py --target /path/to/original/maine.exe \
  --decoded-dir /path/to/decoded-original \
  --native /path/to/th04-port64-gaiji-address-contracts --output /fresh/proof
```

`--reference /path/to/original-comparison` replays the retained complete pages.
The comparison covers the installed Gaiji bank and visible A800 page. The DOS
`graph_gaiji.cpp` implementation still needs its string/address migration;
this batch changes native source and leaves the historical exact ledger intact.

## Graphics-font WORD addressing (v1404)

The native `Canvas` now follows MAINE's `GRAPH_PUTSA_FX` address arithmetic.
The original renderer shifts Y in a WORD before calculating its row address,
adds unsigned X/8, and carries DI across the complete string. It writes the
two-byte glyph word before the third Kanji spill byte, preserving DI wrap.
For example, X640/Y0 draws at the start of row 1, and Y1024 aliases Y0.
Clipping each glyph to screen coordinates discarded these visible writes.

`draw_text()` keeps that address sequence for both script text and the shared
`put_text()` consumer. Font weights 0..7, default spacing 16, halfwidth weight
expansion, ROR and little-endian writes retain their original behavior.
Gaiji drawing keeps its existing implementation.

The maintained `verify_font_address.py` executes original MAINE 0CC7:058C at
load 2000, with its decoded 559 relocations and DGROUP 0E53. A deterministic
2048x2048 monochrome BMP supplies CGROM input; original port writes select its
rows and columns. The reader captures actual original VRAM writes and compares
the entire 640x400 indexed page, including the seeded background. All 1,037
controls agree: eight effects, all eight X alignments, ANK/kana/fullwidth and
mixed strings, color masking, signed coordinate extremes, right-edge spill,
WORD wrap and string continuity. Original FAR return and stack/BP preservation
are checked. The adapter projects the visible A800 page; physical display and
arbitrary font-spacing settings remain separate.

The cold native core and three selected contract programs build successfully.
All three component contracts pass. Optimized UBSan/bounds on the font caller,
Canvas and font decoder reproduces the same1,037 saved original pages. The
compiled predecessor differs in 119 pixels for X640/Y0/"AB" and rejects the
new right-edge component contract.

Frozen producer 520/774cc800, complete compressed original pages, selected
programs, compiler metadata and receipts are retained under
`.analysis/port64/native-font-address-v1404/` in the isolated
`port-motion-v1402` worktree. Replay against a freshly built contract program:

```sh
python3 port64/verify_font_address.py --target /path/to/original/maine.exe \
  --decoded-dir /path/to/decoded-original \
  --native /path/to/th04-port64-font-address-contracts --output /fresh/proof
```

Use `--reference /path/to/original-comparison` to check another compiled
consumer against the retained pages. This native function recovery leaves
the historical DOS exact ledger unchanged.

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
