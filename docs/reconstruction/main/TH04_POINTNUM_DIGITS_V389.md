# TH04 POINTNUM_DIGITS_SET v389

## Scope

This packet closes the formerly provisional 37-byte helper
`POINTNUM_DIGITS_SET` at load `0x189EE` / file
`0x1A1EE`. It is accepted on the repository's separate original-style
ASM plane and does not change the reviewed authored C/C++ denominator.

## Producer provenance

ReC98 commit `c6b17b0c`,
`[Reverse-engineering] [th04/th05] Point number popup add functions`,
simultaneously recovers separate TH04 and TH05 digit ASM producers. The
independently attested TH05 MAIN target preserves the same stack-fed repeated
division architecture: divisor-table traversal in SI, AX:DX division, byte
stores, compact LOOP, final remainder store, RET 4, and trailing NOP.

This is independent producer-lineage evidence, not target-byte transfer.

## Maintained symbolic source

The maintained source is `src/main/pointnum/digits.asm`. It keeps
`_FIVE_DIGIT_POWERS_OF_10` external and derives the GAME4 divisor-table
offset from the point-digit count. No linked address or machine-byte array is
embedded.

Pinned TASM32 emits a `0x26` physical MAIN_033_TEXT contribution:
`0x25` logical function bytes followed by the source-owned NOP. Only the
37-byte function receives logical credit.

## Replay proof

Focused staged replay `gpt-web-pointnum-digits-v389-focused-004` passes
twice with `failures=[]`; receipt SHA-256 is
`d516713d6c31f1924d999c6192772748e7b86704bc34433ca8fde9add89e2dc8`.

The logical owner has target-identical raw SHA-256
`9da89f77da3eef12cb56b2727a41f36a306e57511cc5757327a356fcd50b2b28`,
exact MAP placement at `13A9:4F5E`, empty ordered relocation overlap,
and valid deterministic TASM OMF. The following exact Kurumi producer remains
at `13A9:4F84`.

Candidate aggregate
`gpt-web-pointnum-digits-v389-aggregate-candidate-001` passes all 264
default owners twice. After promotion, independent final aggregate
`gpt-web-pointnum-digits-v389-aggregate-final-001` again passes all 264
owners twice with `failures=[]`; final receipt SHA-256 is
`a2d7deabd90a0a67658677d75ce49d14e2349efc39cf5f142437cd7b72661a05`.

The boundary now lives on the `original-asm / attest-asm` plane. It is
removed from the C/C++ provisional queue without changing the C/C++ exact
denominator.
