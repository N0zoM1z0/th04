# TH04-local BFNT sprite service

2026-09-28 native product-build batch. `super_sprite.cpp` owns BFNT pattern
registration, cancellation, release, and `SUPER_PUT` for MAINE. The separate
`super_state.asm` owns `super_buffer`, `super_patnum`, `super_patdata[512]`, and
`super_patsize[512]` in DGROUP with C/Pascal aliases. The product sources name
no ReC98 path. These are semantic owners; target-byte exactness is not claimed.

The pinned OP/ending PAR contains `SCNUM2.BFT`, SHA-256
`8c4715c11dcdd6ed63fdb0897268ade0cbdb4bc0ecf7b94c6294329ff645d03b`:
20 patterns, each 16×16 pixels, four packed color planes, one 48-byte palette,
and no extension header. The checked-in
`scripts/probes/probe_th04_native_super_runtime.py` extracts it from the
hash-checked HDI and PAR, executes a separate small-model historical
`masters.lib` BFNT loader, and executes the TH04-only large-model implementation
through the local PAR hook and as a loose DOS file. Both loaders produce the
same FNV-1a hash for all 3,200 stored mask/color bytes (`A24A77B5`) and the
converted 48-byte palette (`81529745`). The local fake-VRAM test draws three
patterns at unaligned and edge-clipped positions, then checks all four
32,000-byte plane buffers (`0BE615EA`). It also checks pattern cancellation,
free/reload, missing/bad files, hook shutdown, and 256 valid test-MZ
relocations at load segments `0x2000` and `0x6000`. Receipt SHA-256:
`fc981ebb45b3891319dbb35997da59adf2a9b90a479c749b477b453548a15eca`.

Two cold MAINE no-support links compile 128 TH04-owned translation units
(82 C/C++, 46 ASM) without warnings and leave exactly four BGM symbols:
`BGM_INIT`, `BGM_FINISH`, `BGM_READ_SDATA`, `BGM_SOUND`. All 128 link-relevant
and timestamp-normalized OMF objects agree. BGIMAGE alone has raw timestamp
drift. First no-support receipt SHA-256:
`252061159a52d858c8c64fb5065bb497aa37d2f32a11a0f3a4dec0cb010c1d6e`.

A diagnostic link with the pinned historical library resolves the four BGM
names with its known extended-dictionary warning. The MAP places local
`SUPER_FREE` at `07C9:47AC`, `SUPER_ENTRY_BFNT` at `07C9:47CE`, and
`SUPER_PUT` at `07C9:4B8E`; these are candidate link addresses, not target
MAINE addresses. Its MZ has 649 valid relocation sites at DOS load segments
`0x2000` and `0x6000`. The call audit checks 33 far returns, 141 relocated
direct far calls, and one same-CS far call. Calibration, MZ, and call-audit
receipt SHA-256 values are respectively
`3807bfda0e9e17a83bd1f3603bbafaaa7335dcb8f184e5f71844b764ee5b0caf`,
`bbf1ccac1825ce71f9b5c179ca024388a33200d57cd3b5c024a4b15113b1e963`,
and `04f6ad1e5c0bb12f4875d070e490af006753266d017460033cb24c67c07c89ae`.
The historical library is only a diagnostic input to this MZ.

The historical BFNT loader is near/small-model; its isolated harness is a
behavioral data Oracle, not a product link input. The local `SUPER_PUT`
implements the final four-plane pixel result through masked byte-sized planar writes and
leaves GRCG off. Its fake-VRAM test establishes the pixel transformation;
the OP animation scenario below covers one real-emulator path, while MAINE
page selection and ending display remain untested. Pinned
BFNT files have zero extension length; nonzero extension metadata and
transparent colors other than zero need separate coverage before reuse. The
historical `super_charfree` callback is outside this MAINE BFNT path.

## Byte-sized rendering and animation timing

The first standalone `SUPER_PUT` updated all four VRAM planes once per opaque
pixel. OP's ZUN Soft animation can issue 256 calls and visit 154,624 candidate
pixels in one frame; MAIN's big boss explosion can issue 16 calls over a
48×48 BFNT pattern. The maintained renderer now composes transparent masks
and colors per destination byte, including unaligned and clipped placements.
The DOS fake-VRAM test still produces screen hash `0BE615EA`; an independent
48×48 randomized comparison passed 45 clipped and unaligned positions. This
is a native product performance change, not a historical exactness promotion.

An isolated old/new OP startup comparison used the same pinned DOSBox-X
binary (SHA-256 `30a5fdf8fa95abaf7bae1a9e624ccfc9e26e5357a19cc567bf3a2ac659699258`),
disk-data source, and 10/20/30-second checkpoints. The old build remained in
the ZUN Soft fireworks at 30 seconds (`frame.png` SHA-256
`325fead5e24d9508531a2b1e1483e538169025e193e0ed2e9620938d27c52c48`);
the changed build reached the title menu (`7c1babb62b297a462173ed7428416af138059fa1d5e3d25bf84f10c3de029356`).
Private receipts are under
`.analysis/runtime/candidates/super-perf-{before,after}-20261002/run-logo/receipt.json`.
This is a bounded wall-clock observation under one emulator configuration,
not a full-game timing or Windows-host acceptance claim.

## Destination-byte pass

The next native product iteration composes each destination byte from the
current and preceding BFNT source bytes. The earlier byte-sized renderer could
read and write the same destination twice at an unaligned X coordinate. The
new renderer computes the visible row/byte interval once, then writes every
visible destination byte at most once. A fully opaque mask overwrites the four
planes directly without first reading VRAM. The GRCG-off port write still
occurs even when the sprite is entirely clipped.

The isolated PC-98 fake-VRAM replay passes the same `0BE615EA` screen hash
with 260 valid MZ relocation sites at
`.analysis/reconstruction/probes/super-clipped-20261003-a/receipt.json`.
Independent Python checks cover 500 randomized planar compositions and 10,000
randomized clipping intervals, including negative and right/bottom positions.
These checks support pixel equivalence for the tested cases, not target byte
equality. OP's cache-validated build passes the native link/IRQ audit and is
77,836 bytes (SHA-256
`a698f3749118d2c71e42997012629384a6d60a9147d26717fff7828dfb24f745`).

Four private startup runs compared the previous renderer, destination-byte
composition, opaque overwrite, and preclipped intervals with the same pinned
Linux DOSBox-X binary (SHA-256 `30a5fdf8…`), disk-data source, and
18/20/22/24/26/28/30/32-second checkpoints. At 24 seconds the previous
renderer still displays the moving title text, while the final variant has
already reached the following blank transition; all variants display the same
title menu at 30 seconds. Receipts are under
`.analysis/runtime/candidates/super-{dstbyte-before,dstbyte-after,opaque-after,clipped-after}-20261003/run-logo/receipt.json`.
This is a bounded timing observation; Windows-host frame pacing, boss defeat
and stage-5 Yuuka combat still need replay.

Replay the focused runtime gate with a fresh private directory:

```text
python3 scripts/probes/probe_th04_native_super_runtime.py --output-dir .analysis/reconstruction/probes/NEW-super
```

Replay full-link structure with fresh private directories, serializing the
three Borland builds:

```text
python3 scripts/probes/probe_th04_native_maine_link.py --without-support --output-dir .analysis/reconstruction/probes/NEW-super-a
python3 scripts/probes/probe_th04_native_maine_link.py --without-support --output-dir .analysis/reconstruction/probes/NEW-super-b
python3 scripts/probes/compare_th04_native_maine_link.py .analysis/reconstruction/probes/NEW-super-a .analysis/reconstruction/probes/NEW-super-b
python3 scripts/probes/probe_th04_native_maine_link.py --output-dir .analysis/reconstruction/probes/NEW-super-lib
python3 scripts/probes/audit_th04_native_maine_mz.py --link-receipt .analysis/reconstruction/probes/NEW-super-lib/receipt.json --output-dir .analysis/reconstruction/probes/NEW-super-mz
python3 scripts/probes/audit_th04_native_maine_call_abi.py --link-receipt .analysis/reconstruction/probes/NEW-super-lib/receipt.json --output-dir .analysis/reconstruction/probes/NEW-super-call
```

The four BGM names now form the MAINE no-support link frontier. `MIKO.EFS`
is the same 8,284-byte beeper-effect input in both PAR archives (SHA-256
`12045fed57d7c5a07da0047ae13c6607cbc78155cfbf5baa719fc310131de607`).
Its parser, sound buffers, timer/vector ownership, and PC-98 beeper output require a separate
bounded batch. Native MAINE still needs a TH04-only successful link, complete
relocation and ABI checks, and a game-entry PC-98 runtime scenario.

## Semantic preservation on semantic/readable

The 2026-10-03 batch names BFNT header fields, packed pixel pairs, appended
pattern slots, mask/color planes, allocation rollback and destination-byte
clipping in `src/shared/hardware/super_sprite.cpp`. It retains declaration
order, integer widths, expression order, exported ABI and rendering behavior.
Comments distinguish raw BRG palette bytes from DAC updates, clarify that
transparent color zero generates the mask, and document clipped/opaque writes
and the GRCG-off effect even for fully clipped calls.

Dependency-validated fast builds of MAIN, OP and MAINE remain identical to
the preceding PAR/CDG source build in every MZ byte and ordered relocation:
192,351/77,740/70,614 bytes; SHA-256 `dbbfa404…`, `c8ac4d73…`, `0a2d3ce8…`;
1,178/814/660 relocation entries. Build inventory:
`.analysis/build/semantic-super-readable/build.json`. Each comparator receipt
is `.analysis/ARTIFACT.EXE.semantic-super-compare.json`.

The independent historical-library BFNT reference retains pattern hash
`A24A77B5` and palette hash `81529745`; the product fake-VRAM renderer retains
screen hash `0BE615EA` for unaligned, negative and lower-right placements.
Trailing cancellation, free/reload, malformed/missing files and PAR/loose-file
controls pass. The probe audits 260 MZ relocations at load segments 0x2000
and 0x6000. Receipt:
`.analysis/reconstruction/probes/semantic-super-runtime-20261003/receipt.json`.

```text
python3 scripts/build.py --only main op maine --output-dir .analysis/build/semantic-super-readable --main-cpp-cache .analysis/reconstruction/probes/product-20261003-032654-4e1e8830-main --op-cache .analysis/reconstruction/probes/product-20261003-032654-4e1e8830-op --maine-cache .analysis/reconstruction/probes/product-20261003-032654-4e1e8830-maine --progress
python3 scripts/compare_artifacts.py .analysis/build/semantic-resource-readable/MAIN.EXE .analysis/build/semantic-super-readable/MAIN.EXE --json
python3 scripts/probes/probe_th04_native_super_runtime.py --output-dir .analysis/reconstruction/probes/semantic-super-runtime-20261003
```

Repeat the comparator for OP and MAINE. These are source-to-source compiler
preservation and bounded DOS service observations; no target state is promoted,
and this batch does not validate the ending screen or stage-4 top-edge graphics.

## Native planar performance batch, 2026-10-03

The user confirms full Normal Windows routes and their Ending/save handoff,
and that the Stage 6 top stripe is absent. The remaining performance reports
concern the opening, late Yuuka chase crosses and Ending dialogue. These are
manual observations, not a timed cross-emulator comparison.

`src/shared/hardware/planar_blit.asm` owns two semantic native kernels in an
independent CS, without writable code operands. `TH04_COPY_WORDS` replaces
the page copy's two C word loops with REP MOVSD and an odd-word tail. It retains
the existing allocation, four plane order, source/destination page switches,
GRCG-off side effect and free. SI, DI, DS, ES and the caller's direction flag
are preserved; the far Pascal call returns with RETF 10.

`TH04_SPRITE_UNCLIPPED` handles validated full-screen-enclosed sprites of
1..32 bytes by 1..255 rows. The caller turns GRCG off and dispatches before
constructing clipping-only far-pointer arrays. One shifted alpha row is reused
for all four planes, and empty rows skip those planes. Even row widths compose
two destination bytes at a time with swapped words and SHRD. The final unaligned
carry stays a single-byte write, including at physical column 79. Odd widths
use the byte path. Both paths preserve the same alpha mask, plane order and
background bits; edge placements retain the preceding C clipping algorithm.
The far Pascal entry preserves SI, DI, DS, ES and BP and returns with RETF 8.

Packed PI rows now use a format-derived 256-entry pair table. Each lookup
expands two high-nibble-first pixels into B/R/G/E bytes; four lookups make an
eight-pixel group. Horizontal clipping and the cutscene's hidden VRAM row 400
retain the preceding behavior. No game pixels or target bytes supply the table.
These native service bodies have no historical exact unit acceptance; the
historically accepted MAIN state-clear helper retains its default byte extent.

Three successive source reviews covered register/stack ownership and caller
side effects, shifted masks and row carry, and transparent/physical-boundary
cases. The final independent scalar-pixel CPU replay passes 460 controls:
168 regular sprite cases, 14 size/clipping/boundary cases, 262 packed row cases,
four complete Yuuka entity-render calls and 12 word-copy cases. The maximum
255-row unaligned baseline exceeds the initial two-million-instruction budget;
that rejected run is not a pixel mismatch. Raising only the diagnostic budget
to ten million permits the complete call and all physical-corner guards pass.

The actual native Yuuka near renderer with 31 synthetic live crosses executes
1,063,853 instructions before versus 343,020 after, with identical complete
four-plane buffers. The eight ordinary 32-by-32 shifted random-mask calls use
67.89% fewer instructions in aggregate. Packed rows use 75.18% fewer across
the 262 controls; a complete 640-pixel hidden-row call drops from 23,951 to
4,997. These are bounded CPU instruction costs, not measured Windows FPS.

The final DOS BFNT loader/lifecycle harness still reproduces the historical
pattern/palette hashes A24A77B5/81529745 and fake-VRAM hash 0BE615EA. The packed
DOS harness independently exercises all 256 pair values in every source-byte
position against scalar pixels, in addition to clipping controls. Both pass.

```text
python3 scripts/probes/probe_th04_native_planar_kernels.py --build-dir .analysis/build/th04-normal --baseline-manifest .analysis/render-corner-20261003/before-build.json --baseline-exe .analysis/render-corner-20261003/before-MAIN.EXE --output-dir .analysis/reconstruction/probes/planar-kernels-v1233-boundaries-ready
python3 scripts/probes/probe_th04_native_super_runtime.py --output-dir .analysis/reconstruction/probes/planar-super-v1233-final
python3 scripts/probes/probe_th04_native_pack_put_runtime.py --output-dir .analysis/reconstruction/probes/planar-packed-v1233-final
```

Uninstrumented ordinary Normal gameplay is visible and its former corner
pellet is absent at seven checkpoints. A seeded Marisa/Normal Good Ending
still reaches registration, accepts input and persists 12,345,678 in section 6
only. All ten checksums pass, changed-section digits are valid and the other
nine encoded sections are unchanged. The fixture bypasses gameplay/OP and
uses zero resident sound; its final black frame does not accept return to OP.
Runtime receipts:

```text
.analysis/runtime/candidates/planar-v1233-normal/run/{receipt,corner-control}.json
.analysis/runtime/candidates/planar-v1233-ending/run/{receipt,score-save-control}.json
```

The batch preserves game update logic, Shift movement and configured slowdown
policy. The user's actual late-attack Turbo/Shift/frame-time state and Windows
flow after this optimization still need the next playtest. No native whole-MZ
equality or new historical exact promotion is claimed.

Actual Windows `build-th04.cmd -Normal` and default `build-th04.cmd` both pass
in fast mode, with English progress and verified object/ZUN reuse. Final run IDs
are `product-20261003-065425-02e7e387` (normal) and
`product-20261003-065757-d2c168ee` (invincible). Complete image/bin products equal
the already tested export; both variants retain their preceding GENSOU.SCR and
MIKO.CFG byte hashes. Publication control:
`.analysis/render-corner-20261003/windows-fast-control.json`. The commands build
through the existing Windows-to-WSL toolchain bridge; a native Windows compiler
migration is not claimed.
