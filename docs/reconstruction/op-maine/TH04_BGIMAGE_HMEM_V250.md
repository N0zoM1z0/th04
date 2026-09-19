# BGIMAGE local HMem ABI declaration (v250)

The OP and MAINE target slices and boundaries remain those reviewed in
[v247](TH04_BGIMAGE_NATURAL_V247.md): OP decoded MZ load
`1000:E428..E4F7`, MAINE `1000:D626..D6F5`, each 208 bytes including one
function-external NOP. Their pinned packed targets, decoded payloads, and
active Ghidra databases passed the same session's identity checks. The target
`bgimage_snap` calls `hmem_allocbyte` four times with a pushed `0x7D00` word
and receives each segment in `AX`; `bgimage_free` pushes one segment per far
call to `hmem_free`. The v214 candidate object resolves these calls through
`HMEM_ALLOCBYTE` and `HMEM_FREE` externals. This constrains the local ABI
declarations; the candidate header is corroboration, not target source.

`src/shared/memory/hmem.hpp` now declares only these two far Pascal entries.
`src/shared/hardware/bgimage.cpp` calls them directly, removing its dependency
on the ReC98 `master.hpp` compatibility forwarder. No master.lib declaration
was copied into `compat/rec98/`; other product units may still use that
forwarder. The new header is shared because the memory service is used by
multiple TH04 artifacts, while this specific BGIMAGE producer is shared by OP
and MAINE.

Run:

```sh
python3 scripts/probes/replay_th04_bgimage_natural.py --output-dir .analysis/reconstruction/probes/v250-bgimage-local-hmem-replay
```

Two isolated TC4J builds produce identical valid OMF objects, SHA-256
`c1e3f3f82d34c9a66e35ac1baeda961abb6ee4c42cfe38db632d4345afd29769`,
and the same 269 SHARED CODE bytes as the earlier v247 product source,
SHA-256
`cde62d0489910adbc3c9af62ba47c1a5b33750d8638d1ae26ffbed8d1739c0e8`.
The external symbol **set** is unchanged from v247:
`_memcpy`, `_bgimage`, `HMEM_ALLOCBYTE`, and `HMEM_FREE`. Their OMF index order
changes because the header dependencies changed, so raw FIXUPP records and
object hashes are not byte-identical. The private receipt SHA-256 is
`1b4547a2a45d12b08b3ac6d31fbcb00586ccf87b0162bc6557f15d49eef086db`.

The same replay also compiles `bgimage.cpp` from a temporary tree containing
**only the three checked-in TH04 product files** listed in the receipt, plus
the pinned TC4J standard headers. No ReC98 source/header tree is present in
that compile. Its valid 27-record OMF object, SHA-256
`dfdf689ae42edc7975183c646fe8cebd87a559de2812aec97f42efcb05e46ef0`,
has the same 269 CODE bytes and external symbol set as both overlay builds.

This is compiler-observed ABI/header migration. It preserves source presence
and the same nonexact 269-versus-208-byte physical-code gap. No standalone
artifact link, packed-file equality, or exact-state promotion follows. The new header
does not affect any accepted exact unit; BGIMAGE is source-present in both
artifacts.

The later [v251 intrinsic control](TH04_BGIMAGE_INTRINSIC_V251.md) emits
`REP MOVSW` rather than the target's `REP MOVSD`; it does not change the
maintained source or exactness state.
