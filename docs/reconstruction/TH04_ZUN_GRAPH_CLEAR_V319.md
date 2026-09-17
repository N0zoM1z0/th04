# ZUN PC-98 graph clear support migration, v319

The pinned `ZUN.COM` target and decoded payload remain the v317 identities.
The target resident component's `GRAPH_CLEAR` body is decoded payload
`_TEXT:0xF64..0xF87`, 36 bytes, SHA-256
`a210c6bc7dcf7fb2fb44e2e37d14d82d535f71511f0bbfda30d481c5da6c2a07`.
The target `RET` is followed by a real even-boundary `NOP` before the next
support member at `0xF88`. The candidate MAP and gap-free target decode agree
on the complete extent. The independent historical master-library assembly
corroborates the GRCG behavior and near ABI; it is candidate source, not an
exact Oracle.

[Maintained shared TASM source](../../src/shared/pc98/graph_clear.asm) uses
the mutable VRAM segment and word-count symbols, writes black through the
GRCG tile ports, clears the selected page, restores `DI`, and turns GRCG off.
The `GRAPH_CLEAR` public spelling, word segment alignment, and trailing
`EVEN` are needed for the historical linker layout. This is a standalone
assembly translation unit; no target byte array or inline assembly is used.

Run `python3 scripts/probes/replay_th04_zun_graph_clear.py --output-dir
.analysis/reconstruction/probes/v319-zun-graph-clear-final-ab`. Two isolated
TC4J/TASM/TLINK builds use checked-in ZUN C++ and shared assembly source.
TASM emits a deterministic valid 36-byte CODE contribution, SHA-256
`46f3bad51bb1860265b7b30d15fe7ae8e5a0fa0b7f169f8e85711ff71acc0e75`.
The raw object SHA-256 is
`a65e3d01ce9ac0b0fcb6151eb35c4b02407b289ec5cf3901e63df241a1ed996f`.
The MAP places the local object at `_TEXT:04F6` for `0x24` bytes and contains
no external `grpclear` member. Both linked resident components remain
**byte-identical** to the v317 component, SHA-256
`a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab`.
The local source's linked 36 bytes also equal the target body at
`0xF64..0xF87` when compared at their respective component offsets.
Receipt SHA-256:
`7dfb7a1e096046889db9742a5a0281222d20e74829ae5107658df6bcecc21f04`.

This removes one support member from the external library dependency without
changing the current candidate executable. Most support, ZUNINIT, MEMCHK,
ONGCHK, and the packed product build remain external. The resident component
still differs from the target at 4241 bytes because `_main` and later layout
remain nonexact. This library-origin unit is source-present; no artifact-local
exact acceptance or authored-function credit is claimed.
