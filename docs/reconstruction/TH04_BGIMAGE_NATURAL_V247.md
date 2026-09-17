# OP/MAINE BGIMAGE natural source (v247)

## Target extent and ownership

The pinned packed `OP.EXE` and `MAINE.EXE` targets pass `preflight.py`; their
active Ghidra databases pass `ghidra.py ... check`. The independent DIET-stub
payloads from [v218](TH04_PACKED_PAYLOAD_FRONTIER_V218.md) have SHA-256
`13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`
and `7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c`.
Offsets below are **decoded MZ load-module offsets**, not packed-file offsets.
The Ghidra analysis load segment is `1000h`, so OP `1000:E428` corresponds to
analysis linear `1E428h` and MAINE `1000:D626` to `1D626h`.

| Body | OP load extent | MAINE load extent | Bytes | Boundary evidence |
| --- | --- | --- | ---: | --- |
| `bgimage_snap` | `E428..E48F` | `D626..D68D` | 104 | Target disassembly reaches far return; TLINK public agrees with start. |
| `bgimage_put` | `E490..E4C4` | `D68E..D6C2` | 53 | Target starts immediately after preceding far return and ends at far return; TLINK public agrees. MAINE Ghidra omitted its function entry. |
| function-external alignment | `E4C5` | `D6C3` | 1 | Target `NOP`; excluded from authored function sizes. |
| `bgimage_free` | `E4C6..E4F7` | `D6C4..D6F5` | 50 | Target ends at far return before the next MAP owner. |

The 208-byte OP and MAINE target slices have respective SHA-256
`cf61e4083c86599e123e65ceb3d64a83012283ac40128fbc7f69fbc911dba050`
and `bab5569b6f9bd6ee07585d28cbcb8bb7db191c9e70fc9054a3746d47086a04b8`.
Both equal the same offsets in the v214 cold ReC98-overlay candidate MZ load
modules. This is a target/candidate observation, not an authored-source result.

## Maintained source and compiler observation

`src/shared/hardware/bgimage.cpp` and `.hpp` express the observed four planar
VRAM copies and `HMem` allocation/free in natural C++. The local B/R/G/E
structure has four two-byte segment pointers with compile-time offset checks.
The source has no inline assembly, copied target bytes, `codestring`, or inert
padding. The four plane segments and 32,000-byte size are explicit local
constants; the v214 headers currently supply `HMem` through the checked-in
compatibility forwarder.

Run:

```sh
python3 scripts/probes/replay_th04_bgimage_natural.py --output-dir .analysis/reconstruction/probes/v247-bgimage-product-replay
ndisasm -b16 -o 0xD626 .analysis/reconstruction/probes/v247-bgimage-product-replay/maine-target.bin
```

The replay verifies packed target hashes, decoded payload hashes, the two
208-byte target/candidate slices, and the pinned TC4J binary. It compiles the
maintained TU in two isolated v214 source snapshots with
`-c -I. -O -b- -3 -Z -d -DGAME=4 -ml`, validates OMF checksums, and compares
A/B objects. Both produce the same valid 30-record OMF object, SHA-256
`72871eb61681b7fe7f67155ca2b9d068deab2eaec3aab9f5b5924295c7c8e918`,
with **269** SHARED CODE bytes, SHA-256
`cde62d0489910adbc3c9af62ba47c1a5b33750d8638d1ae26ffbed8d1739c0e8`.
The final 50 unlinked CODE bytes for `bgimage_free` equal the v214 candidate
object's final 50 bytes, SHA-256
`051c7b582818659381d1ed35a4c7721dc51069c3eeb46adc0ce45ac14a4bcdbf`.
The private replay receipt is
`.analysis/reconstruction/probes/v247-bgimage-product-replay/receipt.json`.

This establishes source presence for three 207-byte function bodies in each
artifact. The natural CODE is 61 bytes longer than the target's **208-byte
physical extent**, which also contains the external one-byte `NOP`; its
`memcpy` calls replace the target's inline `REP MOVSD` loops. The free-tail
match alone does not satisfy any function's full linked byte/relocation gate.
No standalone link, packed-file equality, or exact promotion follows. The
historical original OMF producer and all other OP/MAINE owners remain open.
