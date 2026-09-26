# TH04 OP EGC rectangle-copy hybrid closure (v825)

## Result

`egc_copy_rect_1_to_0_16()` at OP decoded payload `0xE378` is now
decoded-exact from maintained narrowed hybrid source. Its reviewed body is
`0x6F` / 111 bytes and ends at `0xE3E6`; the following `0x90` at `0xE3E7`
remains producer layout before the independently accepted v824
`egc_start_copy()` helper.

This moves OP from **88/93** to **89/93** accepted authored functions. Four
reviewed blockers remain:

- `nopoly_b_put`
- `SND_LOAD`
- `SND_SE_PLAY`
- `_snd_se_update`

Nothing in v825 establishes a packed-file offset or whole-`OP.EXE` exactness.

## Rechecking the v757 source assumption

v757 correctly closed the physical `0xB0` `th04/egcrect.cpp` producer, but the
exact-looking ReC98 implementation came from a `[Decompilation]` commit and
used broad inline assembly, pseudoregister shaping, and codestring layout.
v825 does not inherit that source spelling as authority.

Maintained source now lives at:

`src/op/hardware/egc_copy_rect_1_to_0_16.inl`

The decompilation-only parameter loads `asm { mov ax, left; }` and
`asm { mov dx, top; }` are gone. Ordinary TC4J pseudoregister assignments
`_AX = left;` and `_DX = top;` emit the target BP-relative parameter loads.

## Independent release-target evidence

The TH04 111-byte target body has SHA-256:

`3a4dfb3ccd7e3c021dd3548f4f338e221a682ccafa6e012575f6e5864bc68e22`

Pinned DIET restoration independently exposes two TH05 descendant outer
functions:

| Target | Payload offset | Size | SHA-256 |
| --- | ---: | ---: | --- |
| TH05 OP | `0xE2D8` | 123 | `bd5300759a8d6360f9bfcf2df8c0025289903e749039642ed78fc992a0d1be1a` |
| TH05 MAINE | `0xF402` | 123 | `7f22580f40ff81745c5e2e31b37479e9404718eecc2fdcf7c46c5166de6bf2ea` |

After masking only their normal linked address operands, the two TH05 fixed
bodies are identical, normalized SHA-256:

`04f8b7e735d9d01a18d7032ebd8b99ea63b085b0dae3c132f27c0e9aa8a87682`

TH05 adds an out-of-range guard and omits TH04's leading `CLD`, but preserves
the same parameter/register allocation and rectangle-to-VRAM arithmetic.

Additional release-target evidence bounds the retained low-level operations:

- TH03 OP independently contains immediate page-1 `OUT 0xA6,AL` followed by an
  `ES:[DI]` read.
- `MOV AX,DX / STOSW` occurs in registered TH02, TH03, TH04, and TH05 release
  targets.
- The v824 helper called by this function is independently byte-identical in
  TH05 OP and MAINE.

These observations corroborate machine mechanisms, not the exact spelling of
ZUN's original source.

## Narrow symbolic boundary

Most of the function remains C++/TC4J source:

- BP-relative parameter loads;
- coordinate-to-VRAM-offset arithmetic;
- width and stride arithmetic;
- row and word loop state;
- EGC mode word write;
- final `egc_off()` call.

Symbolic low-level source is restricted to:

1. `CLD` for TH04's forward string-store loop;
2. `SHL BX,1` and `SHL CX,1`;
3. two immediate-port `OUT 0xA6,AL` page switches;
4. `STOSW` plus `LOOP`.

The maintained source contains no `__emit__`, opcode arrays,
`#pragma codestring`, object/MZ patching, or post-link byte patch.

## Negative controls

The remaining symbolic forms were retained only after testing ordinary compiler
surfaces.

- `_BX <<= 1` and `_CX <<= 1` select `ADD reg,reg`, not target `SHL reg,1`.
- Ordinary `outportb(0xA6, value)` selects the DX-port form, not immediate
  `OUT 0xA6,AL`.
- Replacing historical parameter-load assembly with ordinary TC4J pseudoregister
  assignments preserves the exact target loads.
- The complete outer function is identical to target before link after masking
  only three normal 16-bit link fields.

The nearby v824 helper was also rechecked during this work: ordinary
`outportb(0x6A, ...)` changes its target immediate-port EGC-enable sequence,
and ordinary zero writes choose `XOR AX,AX` instead of target `SUB AX,AX`.
Those controls support retaining its already accepted narrow boundary rather
than broadening it.

## Focused replay

Checked-in driver:

```sh
python3 scripts/probes/replay_th04_op_egc_copy_rect_hybrid_v825.py \
  --output-dir .analysis/reconstruction/probes/v825-op-egc-copy-hybrid-002
```

Two isolated TC4.02/TLINK rounds reproduce:

- linked outer SHA-256
  `3a4dfb3ccd7e3c021dd3548f4f338e221a682ccafa6e012575f6e5864bc68e22`;
- complete `0xB0` object CODE SHA-256
  `92335bb098e3abbd079a469c866f982a2ac678a170ff3056bb28d7808578bed3`;
- complete linked `0xB0` producer SHA-256
  `2322e97ef7c81b397c759eeb8d427ebd522dfe18fa193c9dccdcd07b26aa52a4`;
- accepted OP linked image SHA-256
  `c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274`;
- accepted OP MAP SHA-256
  `65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee`;
- all 804 ordered MZ relocations.

Focused receipt:

`.analysis/reconstruction/receipt-archive/v825-op-egc-copy-hybrid-focused-receipt.json`

SHA-256:

`984291bce653fe242c33003e85eedd1572c71e062f7e0cec02c3840a52ec649d`

## Canonical acceptance

The v825 canonical decoded-function replay contains 89 accepted OP functions.
All 89 have `raw_difference_count = 0`, including both EGC functions.

Canonical receipt:

`.analysis/reconstruction/receipt-archive/v825-op-egc-copy-canonical-receipt.json`

SHA-256:

`5df5f441a94e5ce3aadfdd102b84abdba1ffcb4730e92bcdd329b91429b65eca`

## Next OP frontier

The EGC translation unit is no longer in the authored-function blocker queue.
The remaining four blockers are all source-provenance/codegen frontiers:

- `nopoly_b_put`: 30 bytes, natural memcpy semantics but wrong segment-setup
  order;
- `SND_LOAD`: 234 bytes, complete function explained except TH04-only `89 C3`
  source provenance;
- `SND_SE_PLAY`: exact machine shape known, independent authored-source
  provenance open;
- `_snd_se_update`: exact machine shape known, independent authored-source
  provenance open.

Future work should seek materially new compiler or historical source evidence,
not retry already-bounded forcing forms.
