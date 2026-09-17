# ZUN C++ source-only compile closure, v314

The pinned `ZUN.COM` is the 7,754-byte `candidate-local-attested` Japanese
target, SHA-256 `0a12e9a489d3b704a77cf04ca3062ee48f298a9df6d237dc7dad46986e2d116e`.
Its decoded payload SHA-256 is
`baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.
The reviewed C++ entries are `_TEXT` `cfg_init` `0xDCF..0xE66` and `_main`
`0xE67..0xF62`.

`src/zun/runtime/api.hpp` now declares only the DOS, file, graphics, and
resident-allocation calls these maintained ZUN sources use. Its near Pascal
ABI and `ResData` argument widths are compiler-observed by comparing the
complete object CODE against the earlier pinned build. In the diagnostic
ReC98 composite, the upstream wrapper still supplies its support library
declarations; the product TUs compile with this local header independently.

Run `python3 scripts/probes/replay_th04_zun_source_only.py --output-dir
.analysis/reconstruction/probes/v314-zun-source-only-ab`. The script attests
the target and toolchain, creates two isolated directories containing **only**
the two maintained `.cpp` files and four checked-in local headers, fixes their
timestamps for deterministic Borland OMF, and compiles both with pinned TC4J
4.02 `-O -b- -3 -Z -d -DGAME=4 -mt`. No ReC98 source or header is available
inside either compiler working directory.

Both rounds produce byte-identical valid objects. Standalone `cfg_init` CODE
remains 152 bytes, SHA-256
`4c80c1405ba9994053738757cbdad5478425ff6ff92baf455c8f2f4c32383fd4`;
standalone `_main` remains 246 bytes, SHA-256
`24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea`.
Receipt SHA-256 is
`a627e067040a9c4afdc3fc86061c55bb96955609a9d20158aa121f640e7977a3`.
The separate v312 A/B composite diagnostics also retain the prior target-equal
`cfg_init` linked bytes and DIET-packed candidate, and the same 246-byte
natural `_main`.

This closes source/header compilation for these two C++ translation units.
The original ZUN `_main` is 252 bytes, and the ZUNINIT, MEMCHK, ONGCHK,
support-library, linker, and packed-product inputs are not yet a checked-in
standalone build. No ZUN unit or artifact is promoted to exact.
