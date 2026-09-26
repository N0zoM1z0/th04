# TH04 OP internal EGC-start hybrid closure (v824)

## Result

The internal `egc_start_copy()` helper at OP decoded payload `0xE3E8`
(size `0x3F`, 63 bytes) is now decoded-exact from maintained hybrid source.

This moves OP from **87/93** to **88/93** accepted authored functions. The
adjacent 111-byte `egc_copy_rect_1_to_0_16()` at `0xE378` remained blocked at v824 and is subsequently decoded-exact in v825.
Nothing here establishes a packed-file offset or whole-`OP.EXE` exactness.

## Why v757 was not enough

v757 correctly closed the physical `th04/egcrect.cpp` producer:

- `egc_copy_rect_1_to_0_16()`: `0xE378..0xE3E6`, `0x6F` bytes;
- one source/compiler NOP at `0xE3E7`;
- internal `egc_start_copy()`: `0xE3E8..0xE426`, `0x3F` bytes;
- one trailing NOP at `0xE427`.

Its exact-looking candidate was nevertheless derived from a ReC98
`[Decompilation]` source and used broad inline assembly/pseudoregister shaping.
That was sufficient for a diagnostic producer replay, not authored-source
acceptance.

v824 therefore reopens the source boundary rather than trusting that candidate.

## Independent target corroboration

The complete TH04 OP helper has SHA-256:

`622c9606a69af201c244d98bd4564fb6bdd159da63951e9e240d4ab038701b85`

Pinned DIET 1.45f restores two independently attested TH05 release targets.
Each contains exactly one byte-identical copy of the full 63-byte helper:

| Target | Restored helper offset | Result |
| --- | ---: | --- |
| TH05 OP | `0xE354` | complete `0x3F` bytes identical |
| TH05 MAINE | `0xF47E` | complete `0x3F` bytes identical |

For TH05 OP, the pinned v401 MAP independently binds a `0xBC`
`th05/egcrect.cpp` owner at load `0xE2D8`. That complete 188-byte release-target
producer is byte-identical to the v401 cold-build producer, and the shared
helper begins at relative `+0x7C`.

A useful correction came from TH05 MAINE: its candidate MAP position did not
identify the release-target helper directly. Searching the independently
restored target instead located the unique helper at `0xF47E`. The earlier
layout assumption was therefore not reused as target authority.

This cross-game evidence corroborates the complete machine mechanism; it does
not claim the spelling of ZUN's original C/C++.

## Narrow maintained source boundary

Maintained source:

`src/op/hardware/egc_start_copy.inl`

The helper is partitioned into four verified byte ranges:

| Range | Bytes | Classification |
| --- | ---: | --- |
| `0x00..0x1B` | 28 | symbolic low-level GRCG/BIOS-shadow/immediate-port EGC-enable primitive |
| `0x1C..0x30` | 21 | ordinary C++ EGC ACTIVE/READ/MASK word writes |
| `0x31..0x36` | 6 | TC4J pseudoregister address-zero primitive |
| `0x37..0x3E` | 8 | ordinary C++ BITLENGTH write and compiler return |

The maintained fragment contains no emitted opcode arrays, `__emit__`,
`#pragma codestring`, copied instruction bytes, object patch, or post-link
patch.

The first low-level block symbolically expresses PC-98 hardware operations:
GRCG TDW mode, BIOS shadow update while preserving FLAGS/ES, and the immediate
port `OUT 6Ah,AL` EGC-enable sequence.

The second low-level primitive is source-level register semantics:

    _DX = EGC_ADDRRESSREG;
    _AX -= _AX;
    outport(_DX, _AX);

TC4J lowers it to the target `MOV DX,04ACh / SUB AX,AX / OUT DX,AX`. This is
not arbitrary byte forcing: the complete six-byte sequence is present in all
three independently observed target helpers.

## Negative controls

The source boundary was reduced experimentally rather than assumed.

- Ordinary `outportb(0x6A, value)` uses the DX-port form rather than target
  immediate-port `OUT 6Ah,AL`.
- Ordinary `outport(EGC_ADDRRESSREG, 0)` selects `XOR AX,AX` instead of target
  `SUB AX,AX`.
- Moving the arithmetic zero into the `outport()` expression changes
  instruction order.
- Ordinary/register local zero variables allocate BX or fold differently and
  produce 56/59-byte helpers rather than the target 63 bytes.

Thus the retained low-level source is restricted to mechanisms that the
ordinary compiler surfaces do not reproduce.

## Focused cold replay

Run:

    python3 scripts/probes/replay_th04_op_egc_start_copy_hybrid_v824.py \
      --output-dir .analysis/reconstruction/probes/v824-op-egc-start-hybrid-003

Two isolated TC4.02/TLINK rounds reproduce:

- helper SHA-256
  `622c9606a69af201c244d98bd4564fb6bdd159da63951e9e240d4ab038701b85`;
- complete `0xB0` `th04/egcrect.cpp` CODE SHA-256
  `92335bb098e3abbd079a469c866f982a2ac678a170ff3056bb28d7808578bed3`;
- linked producer SHA-256
  `2322e97ef7c81b397c759eeb8d427ebd522dfe18fa193c9dccdcd07b26aa52a4`;
- accepted OP linked image SHA-256
  `c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274`;
- all 804 ordered MZ relocations.

Focused receipt:

`.analysis/reconstruction/receipt-archive/v824-op-egc-start-hybrid-focused-receipt.json`

SHA-256:

`d1c675b3741b734e1e24780495b6cc8b99f929c80b2f3fed1bfce23a15d0680c`

## Canonical acceptance

The current decoded-function ledger now contains 88 accepted OP functions.
The canonical replay rebuilds every backend and checks all 88 complete slices.
All 88 have `raw_difference_count = 0`.

Canonical receipt:

`.analysis/reconstruction/receipt-archive/v824-op-egc-start-canonical-receipt.json`

SHA-256:

`e2655248ab4426fabce88c5f1ed1c0c3d663de3d551e60fe9f2707773fdd5da5`

## Remaining OP blockers

Five reviewed authored functions remain nonexact:

- `nopoly_b_put`
- `SND_LOAD`
- `SND_SE_PLAY`
- `_snd_se_update`
- `egc_copy_rect_1_to_0_16`

The next EGC work should attack the 111-byte outer rectangle-copy function
itself. v824's helper closure must not be used to transfer exact credit to that
larger function.
