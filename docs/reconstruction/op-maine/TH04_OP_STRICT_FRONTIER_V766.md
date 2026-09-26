# OP strict natural-source frontier (v766, current-state addenda v821-v826)

All 93 authored OP function candidates have reviewed physical boundaries. At
v766, 85/93 had accepted decoded exactness and eight entries were blocked.

**Current-state addendum (v826):** `scoredat_decode` and `scoredat_encode`
remain decoded-exact through the narrowly scoped v821 cross-game-corroborated
hybrid producer. v824 additionally promotes the internal 63-byte
`egc_start_copy`: independently restored TH05 OP and MAINE release targets
contain the complete helper verbatim, and maintained source restricts
non-ordinary code to two corroborated hardware/compiler primitives totaling
34 bytes. Canonical v825 passes 89/89 accepted OP slices raw-zero after the adjacent
111-byte rectangle-copy closure described below. v826 additionally closes
`nopoly_b_put`: independently restored TH03/TH04/TH05 OP release targets share
the complete normalized 30-byte GAME>=3 producer, and canonical v826 passes
90/90 accepted OP slices raw-zero.

Current OP state is **90/93 exact with three blockers**. The historical v766/v820
negative compiler results remain valid for the source forms they tested.

The 16 original-ASM observations still have reviewed target bounds and
raw-matching decoded source modules. The current three authored blockers remain
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

SND_LOAD is now bounded more tightly by v823: TC4J integrated inline assembly
reproduces its TH04-only 89 C3 encoding with no other decoded-program or
relocation change, while the available source witnesses remain decompilation-derived. The historical EGC decompilation source is no longer the accepted boundary: v824/v825 replace it with narrowed hybrids backed by independent release-target machine-code evidence.

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

The current OP exactness queue is now the three provenance-only sound blockers:
`SND_LOAD`, `SND_SE_PLAY`, and `_snd_se_update`.

### v823 SND_LOAD complete-producer provenance bound

v823 reopens the 234-byte SND_LOAD blocker at full-function scale rather than
testing another small source spelling. Two natural cold wrapper builds retain
8B D8 and the established baseline. Two diagnostic cold wrapper builds change
only the candidate _BX=_AX line to TC4J integrated inline asm { mov bx, ax; };
the complete 234-byte function then matches the target raw-zero. Comparing the
natural and diagnostic decoded OP images yields exactly two changed offsets,
0xDE8B and 0xDE8C. MAP ownership remains th04/snd_load.cpp and all 804 ordered
MZ relocations remain identical.

The provenance check is intentionally stricter than the codegen check. The
pinned v401 snapshot contains 345 unique TC86 4.02 objects and exactly one
other CODE occurrence of 89 C3. That object is th02/player_b.obj, and its source
explicitly contains asm { mov bx, ax; }; Git history binds the line to a
[Decompilation] commit. The TH04 snd_load candidate _BX=_AX line is likewise
introduced by [Decompilation] [th04] snd_load().

Therefore v823 closes the machine-code mechanism but does not grant authored
source credit. SND_LOAD stays blocked pending an independent historical source
witness or other provenance-bearing TH04 producer.

Focused diagnostic receipt SHA-256:
b958943a35c7916ab4a8bc80a9f2dd97bcc25a968ff4a315547f71d6dc37f161.


### v824 EGC-start hybrid closure

v824 supersedes only the internal `egc_start_copy` acceptance decision from the
historical blocker list above. The complete 63-byte helper is present
byte-for-byte in independently restored TH05 OP and MAINE targets. Maintained
source avoids `__emit__`, opcode arrays, codestrings, and post-link patching;
non-ordinary source is limited to a 28-byte PC-98 hardware block and a 6-byte
TC4J pseudoregister primitive. The surrounding `0xB0` producer and all 804 OP
relocations remain unchanged in two cold links.

The 111-byte `egc_copy_rect_1_to_0_16` entry is decoded-exact as of v825. See
`TH04_OP_EGC_START_HYBRID_V824.md`.


### v825 EGC rectangle-copy hybrid closure

v825 extends the v824 EGC work to the complete 111-byte
`egc_copy_rect_1_to_0_16` outer body. TH05 OP and MAINE independently preserve
the same descendant register/allocation and rectangle-arithmetic architecture.
The maintained source removes decompilation-only parameter-load assembly and
keeps symbolic source only for bounded x86/PC-98 primitives: CLD, two SHL-by-one
instructions, immediate page-select OUTs, and STOSW/LOOP. It contains no
`__emit__`, codestring, target-byte array, object patch, or post-link patch.

Two cold TC4.02/TLINK rounds reproduce the 111-byte function, the already
accepted 63-byte helper, the complete 0xB0 producer, OP EXE/MAP, and all 804
ordered relocations. Canonical replay checks 89/89 accepted OP slices raw-zero.
Original-source spelling and packed-file exactness remain separate claims.

Focused receipt SHA-256: `984291bce653fe242c33003e85eedd1572c71e062f7e0cec02c3840a52ec649d`.
Canonical receipt SHA-256: `5df5f441a94e5ce3aadfdd102b84abdba1ffcb4730e92bcdd329b91429b65eca`.

### v826 nopoly_B_put cross-game hybrid closure

v826 supersedes only the nopoly_b_put acceptance decision from the historical
v766 blocker list. TH03, TH04, and TH05 OP release targets each contain exactly
one normalized 30-byte GAME>=3 body after masking only the linked _nopoly_B
word; TH02 is a nonmatching GAME<3 control. Maintained source removes the
decompilation __memcpy__ helper and keeps segment values/count in ordinary
TC4J. Symbolic source is limited to DS save/restore, the release-target XOR
encoding direction, and REP MOVSW.

Two cold TC4.02/TLINK rounds reproduce the complete 0x6A5 OP_MUSIC_TEXT
producer, OP EXE/MAP, the 30-byte body, and all 804 ordered relocations.
Canonical replay checks 90/90 accepted OP slices raw-zero.

Focused receipt SHA-256:
26405281b33c09142e3eec074fe62791614717bd25ef12e27178c4a5232102ca.

Canonical receipt SHA-256:
cab1b089612158f70a983e9f277e3c9146b9b937c6d5c515785257fcd70adcde.
