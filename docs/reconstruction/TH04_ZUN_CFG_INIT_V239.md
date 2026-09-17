# ZUN.COM `cfg_init` source recovery (v239)

## Target and boundary

The pinned Japanese `ZUN.COM` is a DIET-packed MZ file, SHA-256
`0a12e9a489d3b704a77cf04ca3062ee48f298a9df6d237dc7dad46986e2d116e`,
with `candidate-local-attested` provenance. The target identity, MZ structure,
and live Ghidra database passed this session's checks. Independent target-stub
replay gives a 13,422-byte load-invariant payload, SHA-256
`baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.

`cfg_init(resident_t __seg *)` occupies payload `_TEXT` `0xDCF..0xE66`,
`0x98 / 152` bytes, SHA-256
`8fc23f22f653db2afd65ad4cdab19776f5e9f1cdbbfa9de2dd407426fed9bfa2`.
Gap-free 16-bit decode ends at `RET` at `0xE66`; `_main` begins with `ENTER`
at `0xE67` and calls `cfg_init` from `0xF3E`. The body has an internal create
path, a checksum-failure jump back to it, and eight call targets. Its writes
cover the default options, resident segment, debug flag, and stored checksum.
The newly created-file path writes an uninitialized checksum byte; the source
preserves that observed behavior.

## Maintained source and replay

[Source](../../src/zun/config/cfg_init.cpp) is a complete natural C++
translation unit for this function and its default options/debug data. It uses
the observed near 8086/Tiny ABI and checked-in `compat/rec98/` forwarding
headers for still-unlocalized declarations. It contains no copied target code,
inline assembly, inert padding, or cross-game source include. The ReC98 source
was treated as a hypothesis and checked against the target's body and an
independently compiled object.

The pinned TC4J 4.02 command profile is `-c -I. -O -b- -3 -Z -d -DGAME=4 -mt`
with source `#pragma option -2`. In two isolated v214 source snapshots,
compiling the maintained TU yields valid OMF and identical 152-byte `_TEXT`
CODE, SHA-256
`4c80c1405ba9994053738757cbdad5478425ff6ff92baf455c8f2f4c32383fd4`.
Replacing only `cfg_init` plus its owned data in the diagnostic ReC98
`res_huma.cpp` wrapper leaves the complete 404-byte C++ CODE contribution
identical to the original candidate. Pinned TLINK then produces identical A/B
6,360-byte `RES_HUMA.COM` components, SHA-256
`cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110`.
The component's file bytes `0x267..0x2FE` match the independently decoded
target `cfg_init` slice exactly; the `0x100` COM load bias explains its MAP
offset `0x367`.

Two downstream `zungen`/`comcstm` replays give identical 13,422-byte ZUN flat
payloads, raw equal to the target-stub payload. DIET 1.45f `-B` packs the A/B
payloads to identical 7,754-byte files, raw equal to the packed target. The
private probe receipt is
`.analysis/reconstruction/probes/v239-zun-res-huma/receipt.json`, SHA-256
`62762a101340346c210e0309df051e4bef98db6780734b7a8083918920426449`;
the DIET A/B receipt is
`.analysis/reconstruction/diet-replay/v239-zun-product-cfg-ab/receipt.json`,
SHA-256 `bc1e44c46f603d6f8d7c4ade84bc88c4e504edfe93383ca326d24855d2e59d01`.
The checked-in diagnostic replay is
`python3 scripts/probes/replay_th04_zun_cfg_init.py`; its independent v240
A/B rerun passed with receipt SHA-256
`ffa2e671a54c71d91df1abdc13cabfdab8edd052c855cd4f4a804e28fdfdf525`.

## Acceptance boundary

This promotes one ZUN unit to **source-present** and its target function
boundary to reviewed. It does not promote unit or artifact exactness. The
diagnostic composite still gets `_main` from ReC98's `th02/res_init.cpp`,
ZUNINIT/MEMCHK from target-derived assembly, ONGCHK from an external binary,
and support/pipeline code from ReC98. Removing `_main`'s three no-op source
barriers shrinks its C++ CODE contribution from 404 to 398 bytes, so that
upstream form cannot be credited as natural maintained source. A standalone
checked-in TH04 build and a packed-artifact unit-coordinate acceptance route
remain to be built before exact promotion.
