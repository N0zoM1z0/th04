# TH04 OP SCORE codec hybrid closure (v821)

## Scope

This packet closes the two OP SCORE codec blockers at decoded-function level:

- `scoredat_decode()` at payload `0xC57A`, 173 bytes;
- `scoredat_encode()` at payload `0xC627`, 101 bytes.

It does **not** claim pristine original-source recovery, packed `OP.EXE`
ownership, or whole-artifact exactness.

## Why the old frontier changed

The v760/v820 negative results remain valid for the natural compiler routes:
TC4J's documented rotate intrinsics do not emit the target byte-memory
`ROR ...,3`, and TC4J `-B` followed by TASM32 still reproduces the same
nonexact natural bodies.

v821 adds a different kind of evidence rather than contradicting those
negatives. The pre-decompilation TH03 targets independently contain the same
byte-memory rotate inside their SCORE codec functions:

- TH03 OP `sub_B168` encode ROR at `0xB1CB`;
- TH03 OP `sub_B20D` decode ROR at `0xB222`;
- TH03 MAINL `sub_AEF0` encode ROR at `0xAF6A`;
- TH03 MAINL `sub_ADA9` decode ROR at `0xADBE`.

The later ReC98 decompilation replaces those historical machine-code bodies
with one symbolic inline 8-bit ROR primitive and explicitly notes that TC4.0J
only exposes 16-bit rotate intrinsics. That decompilation is **not** treated as
original-source proof. It is independent machine-mechanism corroboration,
analogous to the accepted BGIMAGE hybrid precedent.

TH05 was intentionally excluded from the final v821 provenance argument.
Although TH05 targets contain similar byte-memory ROR windows, the maintained
TH05 SCORE assembly uses a different register-rotate form and the observed
windows were not independently bound strongly enough to the same codec owner.

## Maintained source boundary

The maintained OP sources keep loop structure, iteration direction,
checksum/dataflow, memory accesses, key handling, calls, returns, and
surrounding control flow in C++. Only the irreducible 8-bit rotate remains
symbolic inline assembly.

The source contains no `__emit__`, copied opcode arrays, `#pragma codestring`,
object patching, or relocation rewriting.

## Focused cold replay

Run:

```sh
python3 scripts/probes/replay_th04_op_score_codecs_hybrid.py \
  --output-dir .analysis/reconstruction/probes/v821-op-score-codecs-focused-001
```

The replay re-attests the TH03 provenance, compiles both maintained OP codec
sources in two isolated rounds, validates OMF identity/FIXUPP sites, rebuilds
the complete grouped SCORE owner, and relinks OP.

Accepted identities:

- decoder SHA-256: `5efe0d5065947fa7bc698dba06267ca16d3b34b3e90369907e14451fc9d0e2a5`;
- encoder SHA-256: `737bdcca37820fb3848004e60f12b6e8121470668ea058fb233be1bac7e3b69f`;
- grouped `SCORE_TEXT` CODE size: `0x71D`;
- grouped CODE SHA-256: `1792cb712472c9bebb41e53da7720535202722a9f17ec347d84d99ea558e08b5`;
- linked OP candidate SHA-256: `c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274`;
- ordered relocations: `804`.

The standalone decoder has 18 legal OMF fixups and the encoder 12. After
masking only those relocation words, both have zero non-fixup differences.
Both linked function slices are raw-zero in both cold rounds.

Archived focused receipt:
`.analysis/reconstruction/receipt-archive/v821-op-score-codecs-focused-receipt.json`

SHA-256:
`d2d1c802a0d5393c04266714049532182251d3dd88044561d4a549ab83a25fba`

## Canonical acceptance

The current-ledger canonical replay checks all 87 accepted OP decoded functions,
not just the SCORE producer. All 87 are raw-zero, including both v821 codecs.

Archived canonical receipt:
`.analysis/reconstruction/receipt-archive/v821-op-score-codecs-canonical-receipt.json`

SHA-256:
`99e8403129f6ba3b13c6801523bd344bcb745d84b55daeea679b024e64096dfd`

This moves OP from 85/93 to **87/93** accepted authored decoded functions.
The remaining six blockers are `nopoly_b_put`, `SND_LOAD`, `SND_SE_PLAY`,
`_snd_se_update`, `egc_copy_rect_1_to_0_16`, and internal `egc_start_copy`.

## Limits

- The inline ROR is justified only at this narrow codec primitive.
- The evidence does not justify broader pseudo-register or target-derived ASM
  forcing in other blocked functions.
- The TH03 decompilation is corroboration, not provenance of ZUN's original
  C/C++ spelling.
- Packed-file byte ownership, DIET closure, and standalone product construction
  remain separate work.
