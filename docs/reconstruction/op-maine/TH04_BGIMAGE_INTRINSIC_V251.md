# OP/MAINE BGIMAGE copy intrinsic control (v251)

The pinned decoded OP and MAINE BGIMAGE target extents are respectively
`mz-load-module/SHARED 1000:E428..E4F7` and `1000:D626..D6F5`, each 208
bytes. The target slices each contain **two** `F3 66 A5` (`REP MOVSD`)
instructions: one loop copies four VRAM planes to segment buffers, and the
other copies them back. Target identity and decoded payload SHA-256 are checked
by the replay, as in [v247](TH04_BGIMAGE_NATURAL_V247.md).

A bounded compiler hypothesis asked whether TC4J's `__memcpy__` intrinsic
could produce those loops from natural product C++. The control changes only
the eight copy calls in the current BGIMAGE TU; it uses a temporary tree with
the three checked-in TH04 files and pinned TC4J standard headers, without a
ReC98 source/header tree.

```sh
python3 scripts/probes/probe_th04_bgimage_copy_intrinsic.py --output-dir .analysis/reconstruction/probes/v251-bgimage-intrinsic-replay
```

Both controls compile to valid OMF. Ordinary `memcpy` emits 269 SHARED CODE
bytes and no inline `REP MOVS` instruction. `__memcpy__` emits **275** CODE
bytes, SHA-256
`0fda142075ee054b404697745d151c30f01f9cb31e3ca5f782215f260b1865c3`,
with eight `F3 A5` (`REP MOVSW`) instructions and no `REP MOVSD`.
Its external set drops `_memcpy` while preserving the BGIMAGE and HMem
symbols. The private receipt SHA-256 is
`a0dd27bfbece7d683fe625bb46b317ceebcb66d0d56fee54809dc65c7ab73751`.

This rejects the pinned `__memcpy__` intrinsic as the target copy-loop
producer. It does not prove that every natural TC4J expression fails, nor
classify the historical source as handwritten assembly. The six BGIMAGE
functions remain source-present and nonexact; no product source changed.
