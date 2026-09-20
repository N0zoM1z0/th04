# TH04 item_splashes_init v390

## Scope

This packet formally reviews the last provisional MAIN C/C++ boundary:
`item_splashes_init()` at load `0x13F16` / file
`0x15716`, size `0x1A`.

The function is admitted to the reviewed authored C/C++ denominator as
source-present but blocked. No exact credit is claimed.

## Boundary closure

Fresh target-bound Ghidra constructs 26 contiguous instruction bytes from
analysis address `0x23F16` through `0x23F2F`. The current candidate
MAP publishes `item_splashes_init()` at `13A9:0486`, and exact
`item_splashes_add()` begins at the next public `13A9:04A0`.
There is no hidden switch table or padding inside the reviewed function extent.

The near-target scaffold body differs from target at exactly one byte,
relative offset `0x0B`: target `XOR AX,AX` encodes as
`31 C0`, while TC4J emits `33 C0`.

## Compiler negatives

A bounded pseudo-register matrix confirms that ordinary natural spellings do
not recover the target direction:

- `_AX = 0`, XOR-self assignment, and XOR-self expression all emit
  `33 C0`;
- subtract-self emits `2B C0`;
- AND-zero emits a three-byte immediate form.

The historical ReC98 implementation uses inline `REP STOSW`, but that
source was introduced by commit `f9182987 [Decompilation] [th04/th05]`.
It is therefore not independent original-source provenance and is not accepted
as a shortcut to exactness.

## Maintained source

`src/main/item/splashes_init.cpp` provides a pure-C++ semantic
implementation using standard `memset` plus the last-ID reset. The source
contains no inline assembly.

The reproducible source-presence probe

`python3 scripts/probes/replay_th04_item_splashes_init_natural.py`

compiles it with the pinned TC4J 4.02 toolchain into valid IT_SPL_U_TEXT OMF.
TC4J lowers `memset` to a FAR library call, producing **28 bytes** of
CODE versus the **26-byte** target body. Probe receipt SHA-256 is
`e66385b0faf6fd2a5392c704096eb4c0fdd89de98999e0fdaadc52d06d18b963`.

## Review result

The fail-closed function reviewer admits only
`th04-main-fn-23f16` as a new reviewed nonexact row. Historical note
normalizations in the trial output are deliberately not merged.

After v390, MAIN has no provisional/unreviewed authored C/C++ boundaries.
`item_splashes_init()` remains blocked until a natural producer explains
both the inline fill shape and the target XOR encoding without target-derived
inline assembly.
