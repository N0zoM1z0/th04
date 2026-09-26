# OP strict natural-source frontier (v766, current-state addendum v821)

All 93 authored OP function candidates have reviewed physical boundaries. At
v766, 85/93 had accepted decoded exactness and eight entries were blocked.

**Current-state addendum (v821):** `scoredat_decode` and `scoredat_encode` are
now decoded-exact through the narrowly scoped cross-game-corroborated hybrid
producer documented in `TH04_OP_SCORE_CODECS_HYBRID_V821.md`. Current OP state
is **87/93 exact with six blockers**. The SCORE entries and v820 compiler
negatives below remain historical evidence about failed natural compiler paths;
they are no longer current blockers.

The 16 original-ASM observations still have reviewed target bounds and
raw-matching decoded source modules. The current six authored blockers remain
`blocked` in the ledger pending materially new source-provenance or compiler
evidence.

## Historical v766 blocker list

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

### v820 TC4J assembly-backend control

ZUN resident _main invalidated one earlier assumption: direct TC4J and the
compiler's -B assembly-output path are not always interchangeable. v820
therefore retests that producer mechanism rather than treating the old OP
direct-compiler negatives as exhaustive.

probe_th04_op_assembly_backend_frontier.py builds maintained source twice per
case with direct TC4J and with TC4J -B followed by pinned TASM32 5.0. Short,
byte-identical source aliases avoid DOS 8.3 generated-ASM naming artifacts. The
five results are deterministic:

| Function | Target | -B / TASM32 | Raw differing bytes |
| --- | ---: | ---: | ---: |
| nopoly_b_put | 30 | 30 | 17 |
| scoredat_decode | 173 | 197 | 180 |
| scoredat_encode | 101 | 111 | 52 |
| SND_SE_PLAY | 57 | 60 | 48 |
| _snd_se_update | 76 | 77 | 43 |

In every case, the -B / TASM32 CODE is byte-identical to that function's
established direct-TC4J natural candidate. Thus the ZUN producer mechanism does
not change the segment-order, byte-rotate, BP-frame/index, or BL/BH lowering
that blocks these five OP functions. This is a bounded negative, not a general
claim about all TC4J source.

Retained receipt:

.analysis/reconstruction/receipt-archive/v820-op-assembly-backend-frontier-receipt.json

SHA-256:
a3ecaa4e360d384d219ce853ca2ba198e7a34e5c95e1ac60c1a4776e005208e1

SND_LOAD remains separately bounded by its TH04-only 89 C3 encoding and
existing compiler/TASM controls. The EGC pair remains a source-provenance
problem: its exact-looking ReC98 low-level form originates in a decompilation
commit, so v820 does not use it as authored source.

### v821 SCORE codec hybrid closure

v820 remains correct that direct TC4J and TC4J `-B`/TASM32 do not naturally
produce the target SCORE byte-memory rotations. v821 adds independent TH03
OP/MAINL machine-code corroboration for the same byte-local ROR primitive.
Only that irreducible ROR remains symbolic; the rest of the codec logic stays
in maintained C++. Focused replay reproduces the complete `0x71D` SCORE_TEXT
producer and all 804 ordered relocations, and the archived canonical replay
checks all 87 accepted OP decoded slices raw-zero.

Focused receipt SHA-256: `d2d1c802a0d5393c04266714049532182251d3dd88044561d4a549ab83a25fba`.
Canonical receipt SHA-256: `99e8403129f6ba3b13c6801523bd344bcb745d84b55daeea679b024e64096dfd`.

This closes only the two OP SCORE blockers. It does not prove original-source
spelling, packed OP.EXE exactness, or justify broader low-level forcing.

The result is a strict frontier, not a claim that the historical spellings are
impossible in principle. Further OP progress should require materially new
compiler behavior, independently sourced historical code, or stronger
provenance for a low-level source mechanism. Repeating equivalent C++ spellings
is not useful.

The current artifact order can advance once this OP frontier is recorded;
the six current blockers remain the OP exactness queue when new evidence arrives.
