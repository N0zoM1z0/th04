# OP strict natural-source frontier (v766)

All 93 authored OP function candidates now have reviewed physical boundaries.
85/93 have accepted natural-source decoded exactness. The remaining eight are
not unresolved boundary problems.

After the OP original-ASM source and boundary campaign, all 16 separate
original-ASM observations have reviewed target bounds and raw-matching
decoded source modules. The eight authored entries below are now marked
`blocked` in the boundary ledger pending new source-provenance or compiler
evidence. This state records a concrete missing prerequisite; it does not
assert that exact reconstruction is impossible.

This checkpoint consolidates the current compiler/provenance frontier rather
than lowering the acceptance bar.

## Remaining eight

- nopoly_b_put, payload 0xBFA7, 30 bytes. The ordinary intrinsic memcpy path is
  already the correct size and uses REP MOVSW, but TC86 evaluates/loads the
  source segment before setting ES and saving DS. the v766-retained v761 surface test additionally checks
  direct __memcpy__ and pragma-intrinsic __memcpy__; both are byte-identical to
  the same non-target lowering. The cross-game exact-looking form uses explicit
  segment pseudoregisters and receives no source credit.
- scoredat_decode, 0xC57A, 173 bytes. The target contains two in-place
  ROR byte ptr [BP-1],3 operations. Natural shift/or source is 197 bytes.
  v760 proves _crotr is an RTL FAR call, _rotr is also an RTL call under the
  pinned 16-bit flags, and direct __rotr__ is only a 16-bit ROR AX,3.
- scoredat_encode, 0xC627, 101 bytes. The target contains one in-place byte
  ROR. Natural _crotr source is 111 bytes. The same v760 TC4.02 intrinsic
  surface emits no admissible byte-memory ROR.
- SND_LOAD, 0xDDCA, 234 bytes. The remaining fixed mismatch is target 89 C3
  versus natural 8B D8 for MOV BX,AX. Existing corpus/cross-game/IDE/TASM
  probes show natural TC4J/TASM choose 8B D8; the accepted corpus only produces
  89 C3 where source explicitly uses inline assembly.
- SND_SE_PLAY, 0xE2F2, 57 bytes. Ordinary Pascal C++ uses a BP frame and
  AL/AH parameter/index lowering. The target stack/BX/BL/BH form is reproduced
  only by explicit stack/register shaping, which is diagnostic-only.
- _snd_se_update, 0xE32C, 76 bytes. Ordinary source is 77 bytes because byte
  array indexing zero-extends through AL/AH then BX. v762 tests natural
  register-local alternatives: register unsigned char spills through a BP
  local; register unsigned int allocates SI. None emits the target
  MOV BL / XOR BH pair. Explicit BL/BH shaping remains diagnostic-only.
- egc_copy_rect_1_to_0_16, 0xE378, 111 bytes. v757 closes the physical body,
  following NOP and producer layout, but the current exact-shape candidate
  deliberately uses inline ASM, Borland pseudoregisters and codestring NOPs.
- internal egc_start_copy, 0xE3E8, 63 bytes. v757 closes the body and final NOP,
  but the same source-provenance restriction applies.

## New bounded negative mechanisms

v760 closes the previously untested TC4.02 rotate-intrinsic route. Its retained
receipt is:

.analysis/reconstruction/receipt-archive/v760-tc4-score-rotate-intrinsics-receipt.json

SHA-256:
e80a367d760da8dffd0a7118490ddcaf7da31d371c2a2fee4e8510e52b2bb9ec

v766 consolidates the additional nopoly __memcpy__ and SE-update register-local
surface experiments together with the existing blocker evidence:

.analysis/reconstruction/receipt-archive/v766-op-strict-frontier-receipt.json

SHA-256:
b56646240cd6946cda850686aae0d029b38924b0e4fbc8d33aa05c3dc807aac3

The result is a strict frontier, not a claim that the historical spellings are
impossible in principle. Further OP progress should require materially new
compiler behavior, independently sourced historical code, or stronger
provenance for a low-level source mechanism. Repeating equivalent C++ spellings
is not useful.

The current artifact order can advance once this OP frontier is recorded;
these eight blockers remain the OP exactness queue when new evidence arrives.
