# TH04 MAIN randring2 AND owner (v212)

## Target and boundary

The locally attested Japanese MAIN.EXE is pinned to SHA-256
077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b.
Its provenance remains candidate-local-attested. The complete near Pascal
randring2_next16_and(unsigned int) body is MAIN_032_TEXT 13A9:02D0..02E4,
load 0x13D60..0x13D74, file 0x15560..0x15574, size 0x15. The target slice
SHA-256 is 76c1425512e9bb1aee3ce84148365b6196b9ad42bbf0adc4cdbc7533aa3ef69a.
There are no MZ relocation sites in the extent. Target Ghidra has one
contiguous 21-byte body and 25 observed callers; the TASM PROC and candidate
MAP agree on its entry. Independent raw decoding ends in RET 2. The NOPs at
load 0x13D5F and 0x13D75 are separate layout bytes.

The target body is byte-identical to the previously accepted
randring1_next16_and body in CIRCLE_TEXT. The maintained natural producer is
src/main/math/randring2_next16_and.cpp, SHA-256
d6dd87c6f8ee5c09299871b6dde632af3a4eeb5817777d1c473d65c83f2c67d6.
It uses the attested TC86 pseudo-register/stack-peek idiom and declares the
word cursor with low-byte increment. No target opcode array or inline assembly
was added to the product source.

## Compiler and linker findings

The old randring.inc macro uses the AND procedure's argument name in the
following MOD procedure. An initial diagnostic cold build failed after AND
was externalized because MOD's @mask symbol became undefined. Naming MOD's
own argument @mask resolves that implicit dependency without changing its
instructions. The replay source transform applies the externalized AND and
argument correction only for GAME=4; other games retain the original macro
definition. The early diagnostics receive no exactness credit.

A subsequent diagnostic build placed the C++ body one byte early at 13A9:02CF.
The original assembler's one-byte NEXT16 alignment was source-extracted into
th04/r2gap.asm using a hash-pinned macro span and a MAIN_032_TEXT template.
This is a zero-credit replay scaffold, not part of the new authored function.
The accepted MAP then has rr2next.cpp at 02C2 size 0xD, r2gap.asm at 02CF
size 1, rr2and.cpp at 02D0 size 0x15, and the residual th04_main.asm at 02E6.
TLINK supplies the separate 02E5 alignment before the residual MOD body.

The final rr2and.obj A/B SHA-256 is
e310b2b25a617b7a3fc35953d970923030c52a036c94081e730e6bfee5b35559;
the object is valid TC86 Borland C++ 4.02 Intel OMF. The focused two-cold
111-owner replay gptweb-v212-randring2-and-focused-candidate-005 passes
raw bytes, exact MAP, empty ordered relocation overlap, OMF and determinism;
receipt SHA-256 is
22c88346c223c8c932180fb4e5875ec217ac02695531430110f7aa55dd33db37.
The candidate-state 248-owner aggregate passes twice with failures=[] and
receipt SHA-256
f850f41edf787e9fd5c07e707624bbdbed891eb29ab746108176cf7222817614.
After ledger promotion, the 248-owner final aggregate also passes twice with
failures=[] and receipt SHA-256
dd5e63fbc838f722643b55744c7e319d60d23cb38ae7d5f326ddf2843b77a38b.
The A/B candidate MAIN digest is
d859d5e5547baa963a6a2b441c771f7af865334e497143b85e0d5ca87d2c6a9e;
whole-image equality is not claimed.

The strict target Ghidra/TLINK/owner reviewer admits th04-main-fn-23d60;
report SHA-256 is
7aaeacd85882210b655b972647862eabeb64e706c52126d0a24aeac8a486a96a.
The live MAIN reviewed ledger is now **75,665 / 81,324 exact C/C++ bytes**
and **462 / 485 exact functions**. Thirteen authored candidates remain
unreviewed and 24 remain blocked; original-style ASM is tracked separately.

## Reproduction and limits

Run python3 scripts/preflight.py and python3 scripts/ghidra.py th04-main check,
then the repository replay script with the focused and final run IDs above.
Run python3 scripts/validate_tracking.py, python3 scripts/status.py,
python3 scripts/ci.py, and git diff --check after edits. The receipt JSONs
under .analysis/reconstruction/exact-unit-replay bind each cold build to the
target, toolchain, source, object, MAP, and accepted extents.

The original developer's source spelling remains inferred. This exact claim
covers the complete maintained 21-byte owner and its empty relocation overlap.
Standalone product build closure, runtime checks, whole MAIN image equality,
and independent pristine provenance remain open.
