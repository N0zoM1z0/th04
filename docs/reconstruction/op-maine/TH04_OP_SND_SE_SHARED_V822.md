# TH04 OP shared sound producer provenance bound (v822)

## Result

OP `SND_SE_PLAY` at payload `0xE2F2` (57 bytes) and `_snd_se_update` at
`0xE32C` (76 bytes) remain **blocked**. OP therefore stays at **87/93**
decoded-exact authored functions.

v822 is still substantive progress: the two functions are no longer open
code-generation mysteries. Their complete physical producer is now bounded,
their exact target code shape is reproducible in two cold links, and the
remaining blocker is specifically independent authored-source provenance.

No packed-file or whole-`OP.EXE` exactness is claimed.

## Same-game producer evidence

MAIN and OP independently map one complete `0x86` SHARED contribution to
`th04/snd_se.cpp`:

- MAIN: `130E:07D2`, `0x86`
- OP: `0DA1:08E2`, `0x86`

The pinned OP `snd_se.obj` has 20 legal OMF fixup operands. Masking exactly
those operands in the two target contributions leaves identical fixed bytes
with SHA-256:

`2300d500c2b4d9701f49ffec4647cb4e199296543253796ddb1f6804603dae9f`

This is strong evidence that MAIN and OP share the same TH04 binary producer.
It does **not** by itself prove the spelling of the original C/C++ source.

## Natural maintained-source negative

The maintained OP sources remain stable negatives:

- `SND_SE_PLAY`: 60 bytes, target 57
- `_snd_se_update`: 77 bytes, target 76

The former uses the ordinary BP-frame parameter path and ordinary table index
lowering. The latter differs at the current sound-effect index construction.

v820 already showed that TC4J's `-B` / TASM32 backend does not change these
natural outputs.

## Exact diagnostic candidate

A temporary diagnostic source shape uses:

- the frame-free `BX=SP` parameter helper; and
- the `BL` load plus cleared `BH` current-index helper.

With those helpers, two isolated TC4.02/TLINK rounds reproduce all of the
following:

- complete `0x86` `th04/snd_se.cpp` producer;
- 57-byte `SND_SE_PLAY`;
- 76-byte `_snd_se_update`;
- accepted OP linked EXE/MAP;
- all 804 ordered MZ relocations.

Every raw difference count is zero. This establishes the missing machine-code
shape, but still grants no authored-source credit.

## Why the functions remain blocked

Local pinned ReC98 Git history traces the required helper spelling to commit:

`c85f444b07debfdf02d842ad51d7b4d918198f94`

Subject:

`[Decompilation] [th02/th03] Sound effect playback`

The same commit contains the exact low-level markers used by the diagnostic
shape, including `_BX = _SP`, `_BL = snd_se_playing`, and `_BH ^= _BH`.
Crucially, the surrounding comments explicitly say `MODDERS` should replace
these forms with ordinary parameter/index expressions.

That makes these helpers target-derived decompilation constructs, not
independent evidence of ZUN's authored TH04 source. Same-game target identity
cannot cure that provenance problem.

Therefore both functions remain `blocked`. Promotion requires materially new
evidence such as a pre-decompilation source snapshot, an independently
corroborated historical producer using the same low-level source mechanism, or
a compiler/source mechanism that reaches the target without importing the
decompilation helper spelling.

## Replay

Checked-in probe:

`scripts/probes/probe_th04_op_snd_se_shared.py`

Archived diagnostic receipt:

`.analysis/reconstruction/receipt-archive/v822-op-snd-se-shared-diagnostic-receipt.json`

SHA-256:

`2509adb3b0153514025544f0b2b55aa399ddca52c0a4e5e884e28ca19f0696ef`

The receipt has `accepted_state = "blocked"` and `source_credit = false`.

## Remaining OP blockers

OP remains 87/93 with six reviewed blockers:

- `nopoly_b_put`
- `SND_LOAD`
- `SND_SE_PLAY`
- `_snd_se_update`
- `egc_copy_rect_1_to_0_16`
- internal `egc_start_copy`

For the two sound functions, future work should target source provenance rather
than repeating the already-closed natural codegen or `-B` experiments.
