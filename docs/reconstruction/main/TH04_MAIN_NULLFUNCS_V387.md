# TH04 MAIN NULLFUNC natural-C++ closure (v387)

## Scope

This packet formally accepts the two one-byte target callbacks that were
previously in the provisional/unreviewed queue:

- `NULLFUNC_NEAR`: load `0xBCAE`, file `0xD4AE`, one byte
  `RET` (`C3`).
- `NULLFUNC_FAR`: load `0xBCB0`, file `0xD4B0`, one byte
  `RETF` (`CB`).

The adjacent `EVEN` bytes at `0xBCAF` and `0xBCB1`, plus
the preceding `randring1_next16_mod()` body and its alignment byte,
remain zero-credit hash-bound replay plumbing. They are not attributed to
either callback.

## Natural TC4J mechanism

A normal empty TC4J function receives a BP stack frame. With
`#pragma option -k-`, empty `extern "C"` Pascal callbacks naturally
emit exactly one byte. Pascal linkage also naturally exports the target public
names: `NULLFUNC_NEAR` emits `C3`, while `NULLFUNC_FAR`
emits `CB`. No inline assembly, literal target byte array, binary patch,
or target-derived function body is used.

## Physical CIRCLE_TEXT layout

The v387 cold replay preserves the original physical order:

    0AAF:11A4  001A  replay-only randring1 MOD + alignment
    0AAF:11BE  0001  th04/nulln.cpp   (NULLFUNC_NEAR)
    0AAF:11BF  0001  replay-only NOP
    0AAF:11C0  0001  th04/nullf.cpp   (NULLFUNC_FAR)
    0AAF:11C1  0001  replay-only NOP
    0AAF:11C2        residual CIRCLE_TEXT scaffold

The legacy `_demo_input_null` name used by the later fused DEMO producer
is a zero-code linker alias to `NULLFUNC_NEAR`; it does not add or modify
bytes.

## Replay acceptance

Current-config focused replay
`gpt-web-nullfunc-v387-focused-005` passes two cold builds with
`failures=[]`. Receipt SHA-256:
`1b0b7348ef2891514751504ca3a17eea415577b0a618c36cb0039318326dfb3b`.

The 261-owner candidate aggregate
`gpt-web-nullfunc-v387-aggregate-candidate-002` also passes twice with
`failures=[]`. Receipt SHA-256:
`616e457db6513b3450d94992204704a54e6e6fbd122abea6fa0f5a2aff624ade`.

After formal boundary/function acceptance, the independent post-promotion
aggregate `gpt-web-nullfunc-v387-aggregate-final-001` passes all 261
default owners twice with `failures=[]`. Receipt SHA-256:
`5450ddca56533691f2963d7518d143ad90099888578c75200d4121c38aff0ab2`. Both final candidate MAIN images are SHA-256
`5b66159a13a11f235fcf484aedf5a6f99464978e758dfa7c9138cecce6a5050b`.

Because these two bytes were previously provisional and excluded from the
reviewed denominator, formal acceptance expands the reviewed authored byte
denominator from 83,441 to 83,443 while adding the same two exact bytes.
Four provisional small boundaries totaling 113 bytes remain outside that
denominator.
