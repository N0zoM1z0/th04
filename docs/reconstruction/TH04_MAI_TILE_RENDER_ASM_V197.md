# TH04 MAI_TEXT tile renderer / EGC setup reconstruction (v197)

## Scope

v197 reviews and exactly reconstructs the remaining physical `MAI_TEXT` prefix
in the locally attested TH04 `MAIN.EXE` target as evidence-backed original-style
symbolic assembly:

- group / segment: `MAIN_01 / MAI_TEXT`;
- target map start: `0AAF:20C8`;
- load-module extent: `0xCBB8..0xCC39`;
- file extent: `0xE3B8..0xE439`;
- physical size: `0x82 / 130` bytes;
- target slice SHA-256:
  `30db68d11fd2a8c61a7bdd99be811c382bf386739551525b7945b5cb63e5fd9d`.

The owner contains two logical functions and one source-owned alignment byte:

- `tiles_render_all()`: load `0xCBB8..0xCBF9`, `0x42` bytes;
- `egc_start_copy_noframe()`: load `0xCBFA..0xCC38`, `0x3F` bytes;
- alignment `NOP`: load `0xCC39`, one byte.

The private executable remains ignored operator input with
`candidate-local-attested` canonicality. It was not patched, replaced, moved,
or published.

## Boundary and relocation closure

Fresh target-bound Ghidra constructs both function bodies as single contiguous
ranges of exactly 66 and 63 bytes. Target raw decode independently closes each
body through its terminal near `RET`, and the standalone byte at `0xCC39` lies
outside both function bodies. The exact v196 `midboss2_render()` owner starts at
the immediately following load address `0xCC3A`.

`tiles_render_all()` has two provisional Ghidra callers and two callees. Its
internal near call targets `egc_start_copy_noframe()`. Its other call is the FAR
MASTER.LIB `EGC_OFF` entry. Exactly one MZ relocation overlaps the complete
`0x82` physical owner: relocation index 230, segment-word load address
`0xCBF5` / target table address `0AAF:2105`, inside the FAR `EGC_OFF` call.
`egc_start_copy_noframe()` has five provisional callers and no callees.

The final v196 map still assigned all `0x82` bytes to monolithic
`th04_main.asm`, followed by natural `m2r.cpp` at `0AAF:214A +0x9C` and the
zero-credit replay-only `maisuf196.asm` suffix at `0AAF:21E6 +0x60`. v197
externalizes only the historical `render_a.asm` include and leaves the v196
owner boundaries unchanged.

## Why this is not promoted as natural C++

ReC98 is not used as source authority here. Its tracked history explicitly
introduced the TH04/TH05 all-tile renderer as reverse engineering in 2019, so
the existing `render_a.asm` is only a source-shape hypothesis.

The original targets provide independent evidence. TH05 `MAIN` preserves the
same complete 63-byte EGC helper followed by the same alignment `NOP`. The
immediately preceding TH05 renderer preserves the same 66-byte register,
segment-register, `LOOP`, and control-flow architecture, modulo linked
`_tile_ring` and FAR `EGC_OFF` operands. TH04 `MAINE` independently preserves
the same first 62 bytes of the EGC I/O core, but wraps it in its own BP frame:
`PUSH BP; MOV BP,SP; [62-byte core]; POP BP; RET`. Thus MAIN and MAINE belong to
the same low-level producer family but have different ABI/frame shapes and do
not transfer exactness to one another. TH04 `OP` shares only the initial
20-byte EGC activation sequence, while `ZUN` has no meaningful complete-helper
match.

A bounded legal TC4J probe tested the ordinary `<dos.h>`
`outportb()`/`outport()` route under the production MAIN compiler profile. It
compiled successfully but emitted 73 CODE bytes rather than the target 63:

- a BP frame is generated;
- byte ports use `MOV DX,port; OUT DX,AL`, not target `OUT imm8,AL`;
- word-port evaluation loads DX before AX rather than the target AX-then-DX
  sequence;
- zero is optimized to `XOR AX,AX`.

Borland `outp`/`outpw` are aliases of the same intrinsics. The only inspected
route that produces immediate-port `OUT imm8,AL` is ReC98's `_outportb_` macro,
which explicitly uses `__emit__` byte emission and is prohibited by repository
exactness policy. It therefore provides no natural-source path.

For the renderer, existing repository-local TC4J evidence is also directly
applicable rather than being replaced by a blind spelling matrix. Earlier
low-level tile and checkerboard probes show that ordinary loops and explicit
`_CX` countdowns do not reproduce the target source-level `LOOP` / ES-copy
architecture. The independent TH05 target preserves the same architecture.
Together with the port-I/O result, this supports classifying the complete
physical producer as original-style assembly while leaving historical source
text unknown.

## Maintained symbolic source and standalone OMF probe

Maintained source is `src/main/tile/render_all.asm`, SHA-256
`05546fe82310a8232cee65eba272c9c1f856b46cf22e64480ac914eb290ed61e`.
It contains symbolic identifiers, constants, control flow, segment declarations,
and the maintained EGC macro. It contains no target-derived byte arrays,
codestrings, synthetic data padding, or target patching.

The standalone TASM32 5.0 probe emits a valid 1,689-byte Intel OMF object with:

- one 130-byte `MAI_TEXT` LEDATA record;
- two public function symbols;
- one FIXUPP record;
- object SHA-256
  `002050adcf690f9ca466c228941efdaa0a4e3e3a2c21062d90fe314ced2ecf98`.

Before linking, exactly four target-byte positions differ: the `_tile_ring`
offset addend and the FAR `EGC_OFF` offset. Those fields are exactly the two OMF
fixups. All remaining 126 CODE bytes already match the target. Linked replay is
therefore required for exactness and supplies the actual verdict below.

## Focused and aggregate exact replay

Focused two-cold replay:

- run: `gptweb-v197-mai-prefix-focused-candidate-001`;
- selected dependency closure: 131 units;
- failures: `[]`;
- receipt SHA-256:
  `8f0ce73a02d3dd7599cef47e4e4c48b04afb7605d6525535b75bd8fbf5dd2d0c`;
- manifest SHA-256:
  `5fb0ac8fc0f7ec8e01add935a7a389df9a84d06cec7f5f9295a982ebc704b4e5`;
- A/B `maipre197.obj` SHA-256:
  `f97de1d0de91a52049707789e7cef3785f326158760b4a9fea60aaa4b1e28a08`;
- A/B MAP SHA-256:
  `5c2b238885dfebe63b33d3d6b1e64b2f3b46137aa6aab202e70ca6e9cc9c86f4`;
- A/B overlay MAIN SHA-256:
  `b6dbff73b689d21f313f2a492a563d72272291b902967996017e033b1ba8d458`.

The v197 owner itself reports `raw=True`, `map=True`, `relocs=True`, size 130,
and target slice SHA-256 `30db68d1...` in both builds.

Candidate no-unit aggregate before promotion:

- run: `gptweb-v197-mai-prefix-aggregate-candidate-001`;
- 235 candidate-state default owners, twice;
- failures: `[]`;
- receipt SHA-256:
  `55857c713399919f6dfbb1f87b0580abfcc5c9d302a45d19fbf722384f0a4f3e`;
- manifest SHA-256:
  `59874231d5ff2ced9f37f4c8884d324a1c8a22785426e4a4dd3c1128dbaf26f2`;
- A/B MAP SHA-256:
  `0465b4e10041a2c2dd718e89c8432a97a7668a53af171f2c52285e191676c375`;
- A/B overlay MAIN SHA-256:
  `a07df1577dae48c3513627f5fd5c593f037bc1a4d103e8e7a010386024e8b759`.

Post-promotion no-unit aggregate:

- run: `gptweb-v197-mai-prefix-aggregate-final-001`;
- 235 tracked default exact owners, twice;
- failures: `[]`;
- receipt SHA-256:
  `3e11427714c344d23c9bb646d476f7252d4900ed0614907aa30ccf430082afa5`;
- manifest SHA-256:
  `59874231d5ff2ced9f37f4c8884d324a1c8a22785426e4a4dd3c1128dbaf26f2`;
- A/B `maipre197.obj`, MAP, and overlay MAIN identities are unchanged from the
  candidate aggregate.

The final map makes the physical split explicit: monolithic `th04_main.asm`
contributes zero `MAI_TEXT` bytes at this seam, maintained
`th04\\maipre197.asm` owns `0AAF:20C8 +0x82`, natural v196 `m2r.cpp` remains
`0AAF:214A +0x9C`, and replay-only v196 `maisuf196.asm` remains
`0AAF:21E6 +0x60`.

## Ledger plane and accounting

The two logical functions are intentionally moved from `reconstruct` to the
separate `attest-asm` boundary queue. They are not inserted into
`config/th04_main_authored_functions.csv`, and no C/C++ function-review policy
is added. This follows the repository's existing original-ASM ontology: an
exact physical assembly owner does not become a C/C++ exact function.

Consequently, reviewed C/C++ MAIN accounting remains **75,482 / 81,141 exact
bytes (93.025721%)** and **458 / 481 exact functions (95.218295%)**. The
independent original-style ASM track rises to **30 exact units / 4,500 bytes**.
MAIN boundary routing changes from 512 reconstruction candidates / 56 ASM
attestations to **510 reconstruction candidates / 58 ASM attestations**.

Across all four artifacts, the reconstruction queue becomes 689 authored
function candidates. OP, MAINE, and ZUN remain separate reconstruction queues;
no source or exactness credit is transferred from MAIN.

## Verification-plane limits and continuation

Full final `python3 scripts/ci.py` returns `CI: PASS`, including target
verification, cross-game Oracle calibration, Ghidra/JDK identity, live Ghidra
database replay, and Ghidra Oracle mutation smoke.

This packet establishes repository-native exact physical ownership for the
`0x82` MAIN assembly producer. It does not establish standalone TH04 product
compile/link closure, whole-image exactness, runtime-storage identity, runtime
scenario validation, portable runtime validation, independent pristine-release
provenance, or Factory Truth-Kernel acceptance.

The next evidence-connected structural packet should review the adjacent
low-level tile/bomb-background cohort `tiles_bb_put_raw()` at load `0xBF16`
(size `0x7D`) and `tiles_bb_invalidate_raw()` at load `0xBF94` (size `0x64`).
Both remain unreviewed target-derived assembly candidates and can now be tested
against the TH04/TH05 low-level tile producer evidence established here. Review
the pair together with their shared data/segment assumptions and the seam to
neighboring routines rather than collecting isolated small-function wins.
