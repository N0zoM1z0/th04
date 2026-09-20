# TH04 DIALOG_TEXT rendering primitives v182

## Scope

This packet reviews the three contiguous dialog rendering helpers immediately
between the exact STD-transition prefix and exact `dialog_box_fade_in_animate()`
in `th04-main / MAIN.EXE / DIALOG_TEXT`:

| Function | Map extent | Load extent | File extent | Size | Target SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| `dialog_box_put(unsigned int,unsigned int,int)` | `0AAF:24CE..2525` | `0xCFBE..0xD015` | `0xE7BE..0xE815` | `0x58` | `af5983f066c69171e413871fc47e45fd19cfac8e4c4fd0b4a55993f3483eca05` |
| `playfield_copy_front_to_back()` | `0AAF:2526..255D` | `0xD016..0xD04D` | `0xE816..0xE84D` | `0x38` | `e1cd2f3c0ea1a49cd6f4fe06fe7892e725ea4be52df8cb377d5645cfe9ef56db` |
| `dialog_face_unput_8(unsigned int,unsigned int)` | `0AAF:255E..25A7` | `0xD04E..0xD097` | `0xE84E..0xE897` | `0x4A` | `92bf02c01c4988928966aaea832ffc36c68b85afcfb505466e37e24255f7bc12` |

The complete reviewed window is `0xDA / 218` bytes, target SHA-256
`3f2b47655411684fb0c01460b3bb254599e145fbab18b8eb6d9bd0cbb0a125ae`.
Exact STD-transition ownership ends at load `0xCFBD`; exact
`dialog_box_fade_in_animate()` starts at the next byte after this packet,
`0xD098` / `0AAF:25A8`. The private target remains
`candidate-local-attested`; this packet does not establish independent pristine
release provenance.

## Boundary and layout review

Fresh target-bound Ghidra reports one contiguous body for each entry with
exactly `0x58`, `0x38`, and `0x4A` body bytes. Target raw decoding independently
closes `RET 6` at load `0xD013..0xD015`, `RET` at `0xD04D`, and `RET 4` at
`0xD095..0xD097`. The next TLINK public starts immediately after each function.

The retained current candidate `th04/dialog.cpp` OMF is valid and has SHA-256
`5890695059052be4ee3d7ad7393491c74840e4226bd75f7b0eb79c2a463f778c`.
Its MAP places the four consecutive publics at exactly `0AAF:24CE`, `2526`,
`255E`, and exact fade-in `25A8`. The containing candidate MAP has SHA-256
`d1a8ca2ce94b29c7dfc8590271c7d40d1805f471e8956d398d2d4841e6a14321`.

The target ordered MZ relocation overlap for the reviewed window is load
`[0xD091, 0xD049, 0xCFCB]`. The retained linked candidate has the same ordered
site sequence. Therefore the v182 blocker is not function placement, public
order, relocation ownership, or relocation-site order.

## Historical candidate and the twelve linked-byte differences

The ReC98 scaffold is a useful source-shape hypothesis but is not authoritative
and cannot be accepted as maintained natural source here because the relevant
helpers contain inline assembly. Its linked candidate nevertheless localizes
the remaining historical-module mismatch sharply: the complete `0xDA` target
window differs at exactly twelve bytes, representing six semantically
identical register-to-register instruction encodings.

`dialog_box_put()` differs at three instructions:

- target `01 D0` versus candidate `03 C2`, both `ADD AX,DX`, twice;
- target `89 C7` versus candidate `8B F8`, both `MOV DI,AX`.

`playfield_copy_front_to_back()` is byte-identical in that historical candidate
slice. `dialog_face_unput_8()` differs at three instructions:

- target `89 C3` versus candidate `8B D8`, both `MOV BX,AX`;
- target `01 D8` versus candidate `03 C3`, both `ADD AX,BX`;
- target `01 C7` versus candidate `03 F8`, both `ADD DI,AX`.

The complete retained candidate window SHA-256 is
`6f01e3635b4dd5391fe49e074bb633a00fa2d6ee6cb83246c538a9268e9ba464`.
This near-match is diagnostic evidence only. It does not grant exactness to any
function.

## Maintained natural source

Maintained source is `src/main/dialog/render_primitives.inl`, SHA-256
`641b3a18f725302e11ebd3f54eef0c976c1880ea47276b0d822faf99f2fe5923`.
It preserves the PC-98 GRCG/EGC semantics without inline assembly, copied target
bytes, `#pragma codestring`, fake returns, inert padding, or target patching.
The target string/loop operations are expressed as ordinary C++ loops and the
BX wrap check as an ordinary mask condition.

A bounded contextual probe replaced only the corresponding source span in a
retained cold source tree, compiled the normal TH04 dialog translation unit
with TC86 Borland C++ 4.02, and restored all temporary source/object paths. The
resulting OMF is valid, raw SHA-256
`b926e909b5c364c7a5f940f2051cf15c7c836779627855e92623be25ab2a6c95`
and dependency-timestamp-normalized SHA-256
`43c09ecea141fa8faad872df8287cbaf4150e90a58fd14493f1f7bad98d31107`.
It compiles without warnings.

The natural replacement moves the following public by only `0x14` bytes total:

- `dialog_box_put()`: target/historical candidate `0x58`, natural probe `0x62`;
- `playfield_copy_front_to_back()`: `0x38` -> `0x3D`;
- `dialog_face_unput_8()`: `0x4A` -> `0x4F`.

The extra bytes are the compiler's ordinary expansion of target assembly-critical
operations. The word fill becomes a store plus `DEC CX / MOV AX,CX / OR AX,AX /
JNZ`; each target `LOOP` expands similarly. The mask expression becomes
`TEST BL,7`, not target `TEST BX,0007`.

## Bounded compiler-producer negatives

A current-session command-line TC4J micro-probe tested the obvious natural
pseudo-register spellings. Its valid OMF SHA-256 is
`3283be7ef89f4fa6dd7de9887b3d218777adfc63d24b916760789635d58d7862`.
Both `_AX = (_AX + _DX)` and `_AX += _DX` emit `03 C2`; `_DI = _AX` emits
`8B F8`; `_BX = _AX` emits `8B D8`; `_AX += _BX` emits `03 C3`; and
`_DI += _AX` emits `03 F8`. Mask/modulo forms emit `TEST BL,7`. Explicit `_CX`
and ordinary register-count loops emit `DEC / MOV / OR / JNZ`, never `LOOP`.

A genuinely different producer was also tested. The original TC4J PC-98 IDE
integrated compiler was run through the repository's diagnostic producer probe
under pinned DOSBox-X PC-98. Receipt SHA-256 is
`0bba0e27d5dd77f150e7012d18fb6c1423e98c507848e70c822c88d735f0f525`;
the generated OMF SHA-256 is
`2047f9fae060fe71a5baabb79cb190d9a0bbe94f0722d7b8db836781bac9e986`.
The probe function `_BX = _AX` still emits `8B D8`, exactly like command-line
TCC and not target `89 C3`. The integrated compiler therefore does not explain
the opcode-direction difference.

Pinned TC4J headers expose no `STOSW` or `LOOP` intrinsic. The upstream ReC98
scaffold obtains `REP STOSW`, `TEST BX,7`, and `LOOP` through inline assembly;
that mechanism is explicitly prohibited for maintained natural reconstruction.
No further spelling matrix is justified without a new falsifiable producer or
compiler-IR mechanism.

## Function-accounting consequence

All three functions are now `reviewed / authored / blocked`, attached to the
reviewed `th04-main-dialog-render-primitives-v182` `0xDA` unit. The historical
candidate's byte-identical `playfield_copy_front_to_back()` slice receives no
function exactness credit because the maintained inline-asm-free source is
nonexact and this packet does not establish an allowed exact producer.

The fail-closed function-review trial adds exactly the three IDs
`th04-main-fn-1cfbe`, `th04-main-fn-1d016`, and `th04-main-fn-1d04e`, removes
none, and has report SHA-256
`b4425cf334cdc9923ba75caef7303dac084e8edbb67c33254ad2d9fb5296588f`.
Unrelated generic-writer normalization changes were deliberately not adopted.

## Oracle and verification-plane status

No v182 focused exact replay was run, and no v182 candidate-state or
post-promotion exact aggregate replay was run. The natural source is known
nonexact before those gates, so running promotion Oracles would be misleading.
The retained linked candidate/map observations are diagnostics from already
existing replay state, not a new exactness receipt.

v182 establishes reviewed target boundaries, maintained natural source, valid
TC4J compilation, exact historical MAP/public placement, exact ordered
relocation-site overlap, and durable compiler/producer negatives. It does not
establish exact function/extent reconstruction, standalone TH04 production
compile/link closure, whole-image exactness, runtime-storage identity, runtime
scenario validation, portable-runtime validation, independent pristine-release
provenance, or Factory Truth-Kernel acceptance.

## Continuation

DIALOG_TEXT authored function coverage is now closed at this seam: following
fade-in and script-parameter functions are exact, v180 `dialog_op()` and
`dialog_run()` are reviewed blocked, and later animate/init/exit functions are
exact. The next structural boundary route should therefore leave DIALOG_TEXT.
The strongest current MAIN candidate is the dense unreviewed CIRCLE_TEXT cohort
starting at load `0xB9D6` with `TILES_INVALIDATE_AROUND` (`0xCC` bytes), then
reconcile its adjacent tile, bounding-box, item-splash, shot-laser, and spark
owners before attempting source reconstruction. Do not assume that contiguous
TASM PROCs share one historical producer; close include/module seams first.


## v382 cross-game producer shape and loop-optimizer surface

An independently attested TH05 MAIN target closes an important ambiguity in
the v182 codegen diagnosis. Bounded raw signature scans locate the same three
shared functions contiguously at TH05 load `0x13A3E`, `0x13A96`, and
`0x13ACE`, again with sizes `0x58`, `0x38`, and `0x4A`. After ordinary linked
operands are allowed to differ, the bodies preserve the same low-level
architecture as TH04: `dialog_box_put()` keeps target-direction `ADD`/`MOV`,
`REP STOSW`, and `TEST BX,7`; both EGC copy helpers keep compact `LOOP`,
and `dialog_face_unput_8()` keeps the target-direction `MOV BX,AX`,
`ADD AX,BX`, and `ADD DI,AX`. The fixed-byte agreement is 84/88, 51/56,
and 69/74 respectively. Private receipt SHA-256:
`d18c838d321f106270979bbda09dae736c53641d884362c0f1765c5efe49f0c5`.

This is strong cross-game producer corroboration, not permission to declare
the functions original ASM. Local ReC98 history introduces the corresponding
inline-assembly implementations in explicit decompilation commits
`35d6fe30`, `36166192`, and `a06996af`; there is no independent recovered
standalone-ASM provenance.

A separate compiler-surface probe followed a new falsifiable mechanism:
Borland C++ documentation describes `-Ol` loop optimization as compacting
loops into string operations. The maintained natural fragment still compiles
to the known `0x62/0x3D/0x4F` public sizes under the accepted TC4J profile.
However, the pinned Japanese `TCC.EXE` rejects command-line `-Ol`, and the
compiler also rejects `#pragma option -Ol` and `-Ol-`. Thus that documented
optimizer path is not available through the attested compiler surface used by
this repository.

The v382 conclusion is deliberately conservative: the three functions remain
reviewed/authored/blocked. The target/cross-game evidence says the compact
shape is deliberate and reused, while the accepted natural compiler surface
still cannot express it. Do not replace this packet with standalone symbolic
TASM merely to manufacture exactness. Resume it only if a distinct, replayable
natural producer mechanism is found.
