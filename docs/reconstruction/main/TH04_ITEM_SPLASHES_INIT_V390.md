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


## v395 exact hybrid closure

v390 correctly kept the function blocked when the only known exact spelling
came from decompilation inline assembly. v395 adds independent provenance that
changes the classification without relaxing the byte gate: TH05 directly
reuses the TH04 item-splash translation unit, and the independently attested
TH05 MAIN target contains one matching 26-byte initializer with the same
DS-to-ES setup, `31 C0` zeroing, `REP STOSW`, last-ID reset, and
epilogue.

The maintained exact fragment is
`src/main/item/splashes_init.inl`. Only `xor ax,ax` and
`rep stosw` are symbolic low-level statements; surrounding code remains
authored C++. Pinned TC4J compiles the complete IT_SPL_U_TEXT translation unit
without changing the separately exact add/update suffix.

Focused replay `gpt-web-item-splashes-init-v395-focused-001` passes two
cold builds with `failures=[]`; receipt SHA-256 is
`5049ce5be50591385ee3d4c50460a463cb39a492ae9c2611f1cf8c17b10caef3`.
The 26-byte logical owner is target-identical, MAP-exact inside the unchanged
0x9C IT_SPL_U_TEXT contribution, has empty relocation overlap, and comes from
valid deterministic TC86 OMF.

Candidate aggregate
`gpt-web-item-splashes-init-v395-aggregate-candidate-001` passes all 269
default owners twice. After promotion, independent final aggregate
`gpt-web-item-splashes-init-v395-aggregate-final-001` again passes all
269 owners twice with `failures=[]`; final receipt SHA-256 is
`b5810190e492ea0a7bb5403c61d9b0f5f8d6f53bf657ccfdcbbac7a4d2fed57c`.

The reviewed function is exact as of v395.
