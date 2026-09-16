# TH04 Stage 2 midboss renderer reconstruction (v196)

## Scope

v196 reviews and naturally reconstructs the Stage 2 midboss render callback in
the locally attested TH04 `MAIN.EXE` target:

- segment: `MAI_TEXT` in group `MAIN_01`;
- target map address: `0AAF:214A`;
- load-module offset: `0xCC3A..0xCCD5`;
- file offset: `0xE43A..0xE4D5`;
- size: `0x9C / 156` bytes;
- target slice SHA-256:
  `014fc001cac26ab247a2b65ae8b075bd6daebb269d666a45564566f05bd333f3`.

The private executable remains ignored operator input with
`candidate-local-attested` canonicality. It is not patched, replaced, moved, or
published by this reconstruction.

## Target-first boundary and callback ownership

Fresh target-bound Ghidra constructs one contiguous 156-byte body at analysis
`0x1CC3A..0x1CCD5`. Pinned TASM and target raw decode independently close the
same body through its terminal near `RET`; the next local entry is the reviewed
scroll driver `sub_CCD6` at load `0xCCD6`.

Ghidra reports no direct callers because this function is installed through a
near callback pointer. The already exact `stage2_setup()` target body provides
an independent call-routing anchor: at analysis `0x2E0C2` it stores near offset
`0x214A` into `_midboss_render_func`. Maintained TH04 setup source expresses the
same assignment as `midboss_render_func = midboss2_render;`. Runtime midboss
setup later transfers that pointer into `midboss_render`, which the gameplay
loop invokes.

The target body has three Ghidra callees. The same-group call is the already
exact `scroll_subpixel_y_to_vram_seg1()` at `0AAF:1120`. The other two are FAR
`SUPER_ROLL_PUT_1PLANE` and `SUPER_ROLL_PUT`, and their target MZ segment-word
relocations occur at load `0xCCB9` and `0xCCCB` respectively.

## Natural source

Maintained source is `src/main/midboss/m2_render.cpp`, SHA-256
`2498c00775f9ab24b5c26f3c8c29a5ef547d55b2a539cdf5e876fbd323ee1b2c`.
The source is ordinary Turbo C++ and contains no inline assembly, codestring,
target-derived byte array, synthetic padding, or ABI lie.

The first semantic compiler hypothesis already produced the complete target
instruction skeleton at exactly 156 CODE bytes. The target-shaped source keeps
`left` and `patnum` as register locals and `top` as the single stack local,
naturally producing the target `ENTER 2`, SI/DI saves, coordinate conversion,
three sprite-animation branches, normal and white-plane render paths, and near
return.

One historical behavior is intentionally preserved. `patnum` is assigned only
for `midboss.sprite` values 0, 1, and 2. A value outside that set reaches the
render macro with the prior SI value, exactly as in the target. Adding a default
initializer would be a behavioral/code-generation repair rather than a faithful
reconstruction.

## Physical MAI_TEXT ownership

Before v196, the monolithic `th04_main.asm` object contributed one `0x17E`-byte
`MAI_TEXT` region from `0AAF:20C8` through `0AAF:2245`. Target-first review
splits that contribution into three physical pieces:

- retained monolithic prefix: `0AAF:20C8`, size `0x82`;
- natural `th04/m2r.cpp`: `0AAF:214A`, size `0x9C`;
- zero-credit replay-only scroll suffix: `0AAF:21E6`, size `0x60`.

The retained `0x82` prefix consists of `tiles_render_all()`,
`egc_start_copy_noframe()`, and the source-owned alignment `NOP` at load
`0xCC39`. The alignment byte remains outside the natural midboss owner.

The following `sub_CCD6` body was boundary-reviewed in v195 but still has no
accepted source/origin verdict. v196 therefore does not turn it into product
source or grant exactness credit. Instead, exact replay uses the repository's
hash-bound `scaffold_extractions` mechanism to copy that original scaffold span
into an Oracle-only symbolic wrapper. The extraction is bound to original
`th04_main.asm` SHA-256
`c872e7c1d94d571fc62e6b14e0960b89ef882f46df60a1d8467d117b9e0e549b`
and extracted-span SHA-256
`c74871efaf6f24a1b336ecd56aa37a36af7055e459b9032cb3fe48e92874cccd`.
The maintained wrapper template is
`config/replay/th04_mai_scroll_suffix_v196.asm.in`, SHA-256
`38527e4a49f0d391c95d760aabc9d3f0396463064c76b73d39deb111e5c6fce3`.

Splitting the local scroll suffix across objects requires generated visibility
for three pre-existing symbols: `sub_B835`, `byte_250FE`, and
`_scroll_last_delta`. v196 publishes those existing labels for reconstruction
linkage only. Focused and aggregate linked replay prove that this changes no
owned code/data bytes or ordered relocations. These generated publics are not
claimed as original-target MAP evidence.

The replay-only TASM suffix objects have run-dependent raw OMF metadata hashes.
This does not get hidden or promoted into a determinism claim: in both focused
and aggregate A/B builds, the suffix `LEDATA` and `FIXUPP` records are
byte-identical, with combined semantic-record SHA-256
`1d95c4bafde6deb4f760816b0edb63d3b001190a3dc1695c959936f94155bbac`.
The linked 0x60 auxiliary extent also passes raw, MAP, and ordered-relocation
gates. Natural `m2r.obj`, by contrast, is byte-deterministic as an entire OMF
file.

## Exact replay

Focused two-cold replay:

- run: `gptweb-v196-midboss2-focused-candidate-003`;
- selected dependency closure: 130 units;
- failures: `[]`;
- receipt SHA-256:
  `69203f63aecde63985b3caf23d50fe7fd0f225a1791e633113aa4e788c6644d7`;
- A/B natural `m2r.obj` SHA-256:
  `47d114eef35d21f0613b9fbe3bf4ba5e68b767a2fe72f5650b4a9c512108f7ce`;
- A/B MAP SHA-256:
  `02ecfe94ffc0313fa06d887f26aca6e78e6f242d80450a678b29a9bda2ad4976`;
- A/B focused overlay MAIN SHA-256:
  `52e03c09bddf1e17ef457ad26af47d119b621e66892e02689145fb8904f9126d`.

Candidate no-unit aggregate before promotion:

- run: `gptweb-v196-midboss2-aggregate-candidate-001`;
- 234 candidate-state default owners, twice;
- failures: `[]`;
- receipt SHA-256:
  `bc8f0120fb5f7d50fe9e3b85f1d12f1098497416eeb6422d13677d0613f609af`.

Post-promotion aggregate:

- run: `gptweb-v196-midboss2-aggregate-final-001`;
- 234 tracked default exact owners, twice;
- failures: `[]`;
- receipt SHA-256:
  `0a54dc8e899dc808b5b9c337fefeaf70f34b4737e691164b52b86dee835375dd`;
- tracked manifest SHA-256:
  `3b935189fe00d4b3199d1abcbdcf5ad91b8f1a0f6e1b97da110c968f57a0d370`;
- A/B natural `m2r.obj` SHA-256:
  `47d114eef35d21f0613b9fbe3bf4ba5e68b767a2fe72f5650b4a9c512108f7ce`;
- A/B MAP SHA-256:
  `8d047ff471d025c2c60c92926d34cd89aae2e7735ac9088222593cb531f2f106`;
- A/B overlay MAIN SHA-256:
  `44e65ec09456f930770248545ed449e46ec74f927db0781c607bf93e598dd72c`.

The overlay executable is an exactness Oracle for declared owned extents, not a
standalone TH04 product build and not a whole-image exact claim.

## Independent function review

`scripts/review_th04_main_functions.py` admits the function through its strict
automatic path. The Ghidra body is contiguous, starts at the matching TLINK
public, and lies wholly inside the exact natural owner. The reviewer trial
report SHA-256 is
`a8ea2987680ede200f89ec1f6c9bf551d57760de3d5c8a43a3cd8a5c1d3f31ba`.

The trial ledger contains exactly one ID absent from the live ledger:
`th04-main-fn-1cc3a`. Only that validated row is imported; the reviewer is not
allowed to reorder unrelated historical rows.

## Other TH04 artifacts

The attested unpacked OP/MAINE/ZUN payloads were screened explicitly rather
than assuming MAIN ownership:

- OP: 69,028 bytes, SHA-256
  `13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`;
- MAINE: 62,414 bytes, SHA-256
  `7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c`;
- ZUN: 13,422 bytes, SHA-256
  `baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.

The longest contiguous exact matches to the complete 156-byte MAIN body are
only 8 bytes in OP, 6 in MAINE, and 4 in ZUN. This is bounded negative routing
evidence only. It does not prove uniqueness in a global corpus and transfers no
MAIN source or exactness credit to the other artifact queues.

## Accounting and continuation

Live reviewed MAIN accounting after v196 is **75,482 / 81,141 exact C/C++ bytes
(93.025721%)** and **458 / 481 exact C/C++ functions (95.218295%)**. Generated
progress separately reports 75,482 exact bytes and 91.85% of its conservative
confirmed authored-byte denominator. Original-style ASM remains a separate
**29 units / 4,370 bytes** track.

The next connected MAI_TEXT packet is the remaining `0x82` monolithic prefix at
load `0xCBB8..0xCC39`: `tiles_render_all()` (`0x42` bytes),
`egc_start_copy_noframe()` (`0x3F` bytes), and the final alignment `NOP`. Review
the two logical function boundaries, physical alignment ownership, callers,
callees, relocations, and natural-source/origin evidence together before
splitting that final MAI prefix. `sub_CCD6` and `sub_B835` remain reviewed
source/origin unknowns; do not resume blind source-spelling searches without a
new compiler/source mechanism.
