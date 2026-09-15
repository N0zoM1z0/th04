# TH04 CIRCLE_TEXT tile core v184

## Scope

This packet reviews and reconstructs the complete pre-scroll CIRCLE_TEXT tile
core in `th04-main / MAIN.EXE`:

| Owner | Map extent | Load extent | File extent | Size |
| --- | --- | --- | --- | ---: |
| CIRCLE tile core | `0AAF:0EE6..111F` | `0xB9D6..0xBC0F` | `0xD1D6..0xD40F` | `0x23A` |

The target owner SHA-256 is
`0442cf41e550709cead0b65ae590288af06b6e2b0fbd1b988d023cba591a8e88`.
Exact v183 `scroll_subpixel_y_to_vram_seg1()` begins at the immediate next load
byte, `0xBC10` / `0AAF:1120`. The private target remains
`candidate-local-attested`; no pristine-release provenance is claimed.

The physical owner contains four logical functions and one source-owned
alignment byte:

| Function / layout | Load extent | Size |
| --- | --- | ---: |
| `TILES_INVALIDATE_AROUND` | `0xB9D6..0xBAA1` | `0xCC` |
| `TILES_FILL_INITIAL` | `0xBAA2..0xBAEC` | `0x4B` |
| TASM `EVEN` NOP | `0xBAED` | `0x1` |
| `sub_BAEE` | `0xBAEE..0xBBA3` | `0xB6` |
| `tiles_redraw_invalidated()` | `0xBBA4..0xBC0F` | `0x6C` |

Fresh target-bound Ghidra constructs the four function bodies with exactly
`0xCC`, `0x4B`, `0xB6`, and `0x6C` bytes. Raw 16-bit decoding independently
closes their returns and proves the `0xBAED` byte is outside the preceding
logical body. Ghidra remains provisional semantic evidence and receives no
exactness credit.

## Physical layout and relocations

The v183 accepted cold MAP exposed the entire window as the final zero-credit
`th04\cirpre.asm` residual at `0AAF:0EE6`, size `0x23A`. v184 replaces that
residual with maintained symbolic source while preserving the already exact
v137/v183 owners on both sides.

The target has exactly one ordered MZ relocation overlapping the owner:

- load `0xBC0B`, map address `0AAF:111B`, target relocation-table index 185.

It is the segment word of the terminal FAR `EGC_OFF` call inside
`tiles_redraw_invalidated()`. Focused and aggregate candidates have the same
owner-local relocation address and segment:offset. Absolute relocation-table
indices may differ because the full candidate image has a different header/link
closure; owner-local ordered overlap is the relevant exactness surface.

## Origin review

The four entries were previously listed as authored C/C++ reconstruction
candidates largely because they lived in target-derived TASM scaffolding. v184
does not inherit that classification.

Independent TH05 target comparison gives a distinct producer signal:

- TH05 load `0xBAD2` uniquely preserves the complete `0xCC`
  `tiles_invalidate_around` low-level architecture, including the direct
  `REP STOSB` dirty-tile fills;
- TH05 load `0xBC6E` preserves the same `0xB6` register/segment/`LOOP`
  tile-copy architecture used by TH04 `sub_BAEE`;
- TH05 load `0xBDAE` preserves the complete `0x6C`
  `tiles_redraw_invalidated()` architecture through its return, including the
  EGC setup, `LOOP` tile copy, and FAR `EGC_OFF` call;
- the TH05 initial-fill path independently uses FS-addressed data and
  `REP MOVSD`, matching the low-level producer mechanism of the TH04 fill path
  while game-specific section handling differs.

This comparison is target-to-target evidence. ReC98 source and history were
consulted only as hypotheses. Its three tile bodies were introduced in
reverse-engineering commits and were not treated as historical-source proof.

## Legal TC4J producer negatives

Three bounded TC86 Borland C++ 4.02 probes test the relevant mechanisms under
the normal optimized large-model profile without inline assembly, byte
emission, target patches, or ABI lies.

Ordinary byte, word, and dword copy/fill loops emit BP-framed
`DEC / OR / JNZ` loops and never emit target `LOOP` or REP string forms. Probe
source SHA-256 is
`ea079237f90fcfaaaffe9ecab34c5b5ade0837f996f65a592d3d1a4ece7b430f`;
object SHA-256 is
`59082b9964945b486212d1ec6fd8b3ceeb5418187a1086a7e5f35a5b8a139737`.

`memset()` emits a FAR runtime call. Legal Borland `__memset__()` inlines
`REP STOSW` followed by a residual `REP STOSB`; it does not emit the target's
direct CL-counted `REP STOSB` producer. Probe source SHA-256 is
`3cbba9848df0d1bcc241c3fd1d07d2fc1111fd1e85071e795ae755128a807d04`;
object SHA-256 is
`0555a7d8e6043594d97772cf7c5b0fb9f477b7779148a5422218205c6d2ce0e3`.

Legal `__memcpy__(dst, src, 48)` emits `MOV CX,0x18; REP MOVSW`, not the
TH04 fill path's `MOV CX,0x0C; REP MOVSD`. Probe source SHA-256 is
`bcdceff621ab88948b4a4939160597bd61aa7ba6755f102e1d627a9e45c881f9`;
object SHA-256 is
`50c7337f3c790696374b36d1f06a77d6bfd17c7e558ad51578dc722bcef24227`.

The combined target and compiler evidence supports original-style assembly. It
does not mean that a `.asm` filename or ReC98 text was accepted as authority.

## Maintained symbolic source

Maintained source is `src/main/tile/circle_core.asm`, SHA-256
`2c1d13b36a5d2dddc74423fb6fb3acdd392e6c481598954f71d721da559c9aea`.
It contains symbolic register/segment operations, constants, labels, and calls;
it contains no copied target byte arrays, codestrings, fake returns, inert
padding, or target patching.

A standalone TASM32 5.0 probe produces a valid single OMF module. The cleaned
probe object SHA-256 is
`c1706a2b19a57aa49220607998152186d997116fc91ca8c56a78d11ea0444adc`.
It has one `CIRCLE_TEXT` LEDATA of exactly `0x23A` bytes and four PUBDEF offsets:

- `TILES_INVALIDATE_AROUND` at `0x000`;
- `TILES_FILL_INITIAL` at `0x0CC`;
- `sub_BAEE` at `0x118`;
- `@TILES_REDRAW_INVALIDATED$QV` at `0x1CE`.

The invalidator's standalone external-size expression is written as the
symbolic constant `(TILES_MEMORY_X * TILE_FLAGS_Y)` rather than relying on an
assembler-visible size of an external object. This preserves the historical
operation without embedding a target-derived byte value.

## Replay plumbing

The accepted v183 scroll unit still lists `cirpre.obj` as an auxiliary object.
Simply deleting that object caused the first v184 focused attempt to fail before
byte comparison. v184 therefore keeps the historical auxiliary contract but
hash-bound transforms generated `cirpre.asm` into a valid zero-CODE OMF while
`circlep.asm` owns the `0x23A` contribution.

A second control-plane attempt failed because the empty scaffold still declared
`public sub_BAEE`. The final transform also removes that declaration. These two
failures have no exactness meaning; neither reached the target-byte Oracle.

The final MAP sequence is:

- `th04\circlep.asm`: `0AAF:0EE6`, `0x23A` CODE;
- `th04\cirpre.asm`: `0AAF:1120`, `0x000` CODE;
- `th04/scroll1.cpp`: `0AAF:1120`, `0x28` CODE;
- `th04\motion1.asm`: `0AAF:1148`, `0x20` CODE;
- `th04\cirs183.asm`: `0AAF:1168`, `0x18` zero-credit residual;
- `th04/r1next.cpp`: `0AAF:1180`, `0x0D` CODE.

## Exact Oracle results

Final focused replay is
`gptweb-v184-circle-tile-core-focused-003`. Receipt SHA-256 is
`a1f8c1439b068d20cd9d6536cbefe73bc6613532765765ca290927043e7a28dc`.
It selects 113 owners and passes both isolated cold builds with no failures.
A/B `circlep.obj` SHA-256 is
`3a144ccf7ca78d69f11ff3e301eed945df9465170ab69cd26a9e46cd33b8d8d8`;
A/B MAP SHA-256 is
`217d0d640ee5457af4528c284a4901f93424087bc576bbd298c0bd5e3f5a2c5c`.
All 570 linked owner bytes equal the target SHA-256
`0442cf41e550709cead0b65ae590288af06b6e2b0fbd1b988d023cba591a8e88`.

Promotion candidate aggregate is
`gptweb-v184-circle-tile-core-aggregate-candidate-001`. Receipt SHA-256 is
`20ae069ba46b48a5f32cc025588bea98e4f69aaacd6f4238ef0ff09275fec284`.
All 217 candidate-state default owners pass twice. The temporary manifest was
restored byte-for-byte after the run.

Post-promotion aggregate is
`gptweb-v184-circle-tile-core-aggregate-final-001`. Receipt SHA-256 is
`2a47f20590e2d7a2496049a338db41e16c903e02faa1dd9440a3aeb88f372e62`.
All 217 tracked default owners pass twice. A/B `circlep.obj` remains
`3a144ccf...`; A/B MAP is
`691369e5f89b461ef4aab47fd4c4a66843db8495d0673f1bca3a99a863dee399`;
and A/B candidate MAIN is
`6685687e0f7554e4f84395e71cabac1f2e3babccaa76abaa86877846108145a4`.

## Accounting and verification planes

The four logical entries move from the authored-C++ reconstruction queue to the
original-style ASM attestation queue. The physical `0x23A` unit is exact on the
ASM reconstruction surface. It therefore does not increase or decrease the
reviewed authored-C/C++ byte or function numerator/denominator.

After promotion, MAIN reviewed authored-C/C++ accounting remains
`74,921 / 80,406` exact bytes (`93.178370%`) and `451 / 474` exact functions
(`95.147679%`). Boundary routing becomes 532 authored-C/C++ reconstruction
candidates and 36 original-style ASM attestation observations.

This packet establishes exact reconstruction only for this symbolic ASM owner.
It does not establish standalone TH04 production compile/link closure,
whole-image identity, runtime-storage identity, runtime-scenario validation,
portable-runtime validation, independent pristine-release provenance, or
Factory Truth-Kernel acceptance. OP.EXE, MAINE.EXE, and ZUN.COM remain
independent queues and receive no MAIN credit.

## Continuation

The next structural MAIN route should not stop at the isolated `0x18`
`randring_fill()` helper. The stronger next packet is the dense CIRCLE_TEXT
renderer seam immediately after the already exact point-number blitter:
load `0xBE68..0xC34D`, size `0x4E6`.

That window begins with `SHOT_LASER_PUT_RAW`, then contains backdrop/tile-BB
helpers, `items_invalidate()`, GRCG helpers, item-splash and spark
render/update/invalidate routines, and ends immediately before provisional
`sub_C34E`. It mixes corroborated and provisional boundaries and is therefore a
better boundary/origin packet than another isolated small-function win. Close
physical producer/include seams, relocation ownership, callers/callees, and the
`0xC34E` boundary before choosing C++ versus original-ASM source forms.
