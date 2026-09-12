# TH04 CIRCLE point-number render/put original-style assembly reconstruction (v140)

## Scope

This packet closes the v138 source-language/origin question for two adjacent
reviewed functions in `th04-main / MAIN.EXE` while keeping original-style
assembly separate from authored C/C++ accounting:

- target: `th04-main`, candidate-local-attested SHA-256
  `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`;
- segment/group: `CIRCLE_TEXT` / `MAIN_01`;
- `POINTNUMS_RENDER`: `0AAF:1274`, load `0xBD64`, file `0xD564`, size `0x9A`;
- `@pointnum_put`: `0AAF:130E`, load `0xBDFE`, file `0xD5FE`, size `0x6A`;
- next public: `SHOT_LASER_PUT_RAW` at load `0xBE68`;
- neither reviewed extent overlaps an MZ relocation.

Fresh target-bound Ghidra observes one contiguous 154-byte renderer and one
contiguous 106-byte put helper. Ghidra reports one direct renderer caller at
linear `0x1AB88`; the renderer calls the scroll helper at linear `0x1BC10` and
`@pointnum_put`, while the put helper has no direct callees. These are
provisional semantic observations only. Raw target decoding, the pinned TASM
listing, and TLINK public positions independently delimit the two extents.

## Why the renderer is not treated as natural C/C++

The TH04 renderer owns a code write. At load `0xBDC1`, target instruction
`MOV CS:[0x12E9],CX` writes the computed current point-number width into the
immediate operand of its own later width-store instruction at load `0xBDD6`.
The write therefore depends on the exact code layout of the renderer itself.

The v138 legal TC4J work intentionally did not manufacture this with inline
assembly, `#pragma codestring`, copied bytes, a fabricated code pointer, or a
target patch. No maintainable natural C/C++ producer has been demonstrated for
this target behavior. `src/main/pointnum/render.asm` instead names the code
location symbolically as `@@set_width+3`; TASM resolves the owned code address.
This is an irreducible original-style assembly classification, not a claim that
this repository possesses the author's historical source text.

TH05 does not provide a same-code renderer shortcut. Its independently attested
original `MAIN.EXE` has a different point-number renderer at load
`0xE216..0xE288` (0x73 bytes). That renderer uses stored width data and has no
`CS: MOV [imm],CX` self-modifying store. The TH04 renderer classification is
therefore local target evidence and is not inherited merely from subsystem
proximity or from ReC98.

## Independent TH05 evidence for `@pointnum_put`

The registered private TH05 target has SHA-256
`c41f6e6b9a97b2433acc576ceaee800707c8d4ea7e498150a259663c8fa7d4f0`.
Its load module contains exactly one operand-wildcarded match for the complete
TH04 0x6A-byte put skeleton, at load `0xBE3A`. The exact TH05 slice SHA-256 is
`9f1e9b9452e1002fd1fde3966cd5c0989a5b8b80eaafd787edc6b8a627642f59`.

TH04 and TH05 differ at only two of the 106 bytes: the linked `_sPOINTNUMS`
offset word. Zeroing that one word in each original target produces the same
SHA-256:

`35d832b1626fed64893e30b7fd6fcf10fe8e0ad7df232ce0b484c4a3f9503048`.

Thus all 104 non-link-address bytes are identical across the two original
targets, including the frameless register ABI, `LODSW`, `LOOP`, the vertical
wrap path, `XCHG CX,BX`, register restoration, and final `RET`. Static TH05
call sites at loads `0xE270` and `0xE279` both target `0xBE3A` from the TH05
renderer.

The same full skeleton is absent from the registered TH02 and TH03 MAIN
images. ReC98's TH05 scaffold happens to include the TH04 reconstructed
`num_put.asm`, but that source relationship is not the evidence used for this
classification; the cross-game claim above comes directly from the two private
original target byte streams.

v138 also supplies negative compiler evidence. Two warning-free legal TC4J
fastcall/register probes emit 0x87-byte BP-framed bodies with explicit
load/add and countdown tests rather than the target `LODSW` / `LOOP` /
`XCHG CX,BX` producer class. The stable TH04/TH05 target shape plus that
negative compiler evidence and exact symbolic TASM replay support the
original-style assembly classification without asserting provenance of the
historical source text.

## Maintained source and physical producer

The maintained sources are:

- `src/main/pointnum/render.asm`, SHA-256
  `26e3f010d822e89816f7166ba41b66fd49465a9d693de2eec2ad6eb67e4d771e`;
- `src/main/pointnum/put.asm`, SHA-256
  `833cef4da5a728ecf813d498601db726197bb87cf59f19ca66571c3b5b6c5c86`.

They are symbolic TASM include owners overlaid onto the pinned scaffold paths
`th04/main/pointnum/render.asm` and `th04/main/pointnum/num_put.asm`. They do
not contain target-derived byte arrays, inline emitted machine bytes,
`#pragma codestring`, fake returns, inert padding, or target patching.

The physical TASM producer remains `th04_main.asm`. In the accepted aggregate
map its `CIRCLE_TEXT` contribution is:

```text
0AAF:11A4 09B6 C=CODE S=CIRCLE_TEXT G=MAIN_01 M=th04_main.asm ACBP=48
```

and the publics remain exactly at `0AAF:1274` and `0AAF:130E`. Since the same
module contributes code to many other segments, v140 extends the replay
inspector with an optional `map_segment` qualifier. A contribution is still
required to resolve uniquely; an absent or ambiguous module+segment match fails
closed. Two unit tests cover successful segment disambiguation and the missing
segment rejection.

The first focused attempt,
`gptweb-v140-pointnum-render-put-focused-candidate-001`, reached the inspection
stage but failed before any exactness verdict because the older inspector found
15 `th04_main.asm` contributions and did not use `CIRCLE_TEXT` to disambiguate
them. This was replay infrastructure history, not a byte or target rejection.
No source was changed to address that failure.

## Exact replay

With both units still ledgered as candidates, focused replay was run serially:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-pointnums-render-v138 \
  --run-id gptweb-v140-pointnum-render-put-focused-candidate-002
```

The dependency closure contains 110 owners. Both isolated builds pass. Receipt
SHA-256 is
`9781ebcf56dbeda5d9276dcfa7e2f7109aeb875995dc6656e58e8998c5de60ea`.
The exact renderer slice SHA-256 is
`050de3154e84536347926fc05edef5a5a5f1db0d67de4c4fa11f6702c45a1c2f`;
the exact put slice SHA-256 is
`e5f760af38c2a844797b17a2052359a819736e69997df376252a91f2a1c9e63d`.
Both target/candidate ordered relocation overlaps are empty. The focused
`th04_main.obj` dependency-timestamp-normalized OMF SHA-256 is
`713b1cf017e41f285ee7040fa970fb9394836a7d68ff05ef725c3f50b36f376d`
in both cold builds and reports `Turbo Assembler Version 5.0`.

Before promotion, the complete default cohort was rebuilt twice:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --run-id gptweb-v140-pointnum-render-put-aggregate-candidate-001
```

All 175 default owners pass. Receipt SHA-256 is
`05ee78508891005c7a3073fe7950583a0d6ac94f5fa9f40b31edac13786d74a3`.
The aggregate producer OMF normalized SHA-256 is
`9de45cff560aabcab98046cff483b8491150025777628b74e41fde5b21897283`.
It differs from the focused producer identity because the complete aggregate
activates additional hash-bound transforms in the same large `th04_main.asm`
object; within each gate the A/B normalized OMF identity is deterministic, and
the two declared point-number slices remain identical.

Only after that candidate-state aggregate passed were the two units promoted to
`original-asm/exact`, their boundary observations moved from
`authored/reconstruct/blocked` to `original-asm/attest-asm/unreviewed`, and the
two rows removed from the authored-function ledger. The post-promotion aggregate
then rebuilt all 175 owners twice again:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --run-id gptweb-v140-pointnum-render-put-aggregate-final-001
```

It also passes with receipt SHA-256
`4479103d3374eb16d410176c1519e9c4f9a66dcbbac0044e14d12aed52f2b97e`.
Both final aggregate builds produce candidate MAIN SHA-256
`ad3892d8093df45c1fb6452e288dcd6e9f8cfb0b900909c3686827fa9efc47f8`.
No previously accepted owner regresses.

## Accounting and limits

This origin correction removes 260 bytes and two functions from the reviewed
authored C/C++ denominator; it does not add two authored exact functions.
After promotion the live authored accounting is 47,564 / 47,771 exact bytes
(99.566683%) and 300 / 305 exact functions (98.360656%). Original-style ASM is
tracked separately.

Crossing 99.5% on the current reviewed authored-byte ledger is not a completion
claim. The function percentage remains below the campaign pressure target, the
boundary denominator remains expandable, and hundreds of authored candidates
remain unreviewed. This packet also does not establish a standalone TH04 product
build, runtime-storage identity, runtime scenario validation, pristine target
provenance, or Factory acceptance.
