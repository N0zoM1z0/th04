# TH04 MAIN CIRCLE_TEXT randring filler (v211)

## Target and boundary

The locally attested Japanese MAIN.EXE has SHA-256
077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b.
Its canonicality remains candidate-local-attested. The complete near
randring_fill() body occupies CIRCLE_TEXT 0AAF:1168..117F, load
0xBC58..0xBC6F, file 0xD458..0xD46F, size 0x18. The target slice SHA-256 is
42c2cd75d930070226e8d40f836ee38666b7a541ba6c472902ad8a594b12ae89.
Its only MZ relocation is ordered entry 186 at load 0xBC5F. The body ends
with RET; exact randring1_next16() begins at the next byte, 0xBC70.
Target Ghidra has one contiguous 24-byte body at analysis address 0x1BC58;
the candidate MAP and TASM public agree on the entry. These views establish
the boundary, while raw target bytes remain the acceptance reference.

The routine fills the 256-byte ring backward using far IRand(), then clears
the full word cursor. The maintained natural producer is
src/main/math/randring_fill.cpp, SHA-256
8bd8d1c03765ece782a84ec2e2996749a837e2c4241236be7af3fd2d0c589fff.
Its declarations model the target word cursor, byte ring, and far Pascal RNG
ABI. No target opcodes, inline assembly, fake return, or inert padding were
added.

## Compiler and link result

A pinned TC86 Borland C++ 4.02 probe with the decrement as a separate statement
emitted 26 bytes: OR SI,SI appeared between DEC SI and JGE. Moving the
decrement into the loop condition emitted the target 24-byte instruction
sequence naturally. The maintained C++ object in both focused cold builds is
valid Intel OMF, SHA-256
332c5f84855db57090ab49ef73adde1c918e2fc4aeaf9a87ea11b13808077748.

The v183 replay-only cirs183.asm contribution becomes a zero-code structural
anchor only when this new unit is selected. th04/rfill.cpp occupies its former
link position immediately before r1next.cpp. The focused A/B MAP places it at
0AAF:1168, size 0x18, and the candidate's sole overlapping ordered
relocation is the target's load 0xBC5F.

Focused two-cold replay gptweb-v211-randring-fill-focused-candidate-001
selects 113 dependency owners and passes raw bytes, MAP, ordered relocations,
OMF, and determinism. Receipt SHA-256:
a78b4001882237127f1f80a6a3f07df76de31cd81d0dfebbf0e6aa7b6b3fbf6e.
The candidate-state 247-owner aggregate
gptweb-v211-randring-fill-aggregate-candidate-001 passes twice with
failures=[], receipt SHA-256
f236b7270bc2682c19c8bd852c44078705ebb51621ea5f2327adf6a275862710.
After ledger promotion, the 247-owner
gptweb-v211-randring-fill-aggregate-final-001 also passes twice with
failures=[], receipt SHA-256
a4568869891d1374ec737338f95dad8d0b0a952be929d5f3d7004a122fc33809.
The accepted target/candidate slice hashes are identical. The aggregate
candidate MAIN digest 1932b7feb681e3fa198d24a10cd93a70ce2cb6d400d1ecab39545cafa26b9f9b
is unchanged from v210; this is not a whole-executable exact claim.

The independent function reviewer admits th04-main-fn-1bc58 from the
contiguous target Ghidra body, TLINK public, and exact owner without losing any
old authored-function row. Its report SHA-256 is
a95d4f800b9b90d133c0ee674bdccf02353620093b1ad31c1ee9b67f2c759c61.
The live MAIN reviewed denominator is now **75,644 / 81,303 exact C/C++ bytes**
and **461 / 484 exact functions**. Fourteen MAIN authored candidates remain
unreviewed; 24 remain blocked. Original-style ASM remains a separate track.

## Remaining limits

The original developer's source spelling is inferred from compiler and target
evidence; the attested claim is exact maintained natural-source ownership over
this complete extent. Standalone TH04 product build closure, whole-image
equality, runtime scenarios, and independent pristine provenance remain open.
