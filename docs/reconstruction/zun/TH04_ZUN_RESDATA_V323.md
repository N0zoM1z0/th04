# ZUN resident-data support migration, v323

The pinned packed `ZUN.COM` is SHA-256
`0a12e9a489d3b704a77cf04ca3062ee48f298a9df6d237dc7dad46986e2d116e`;
its decoded payload is verified by the replay script. The target resident
`RESDATA_EXIST` / `RESDATA_CREATE` extent is decoded payload
`0xF88..0x1045`, 190 bytes, SHA-256
`cd6d5f0b78835208fd872ae3a3a39028edad3eb99a74a9e5b22158f3fcc7187d`.
The associated ten-byte identifier is at decoded payload `0x2204..0x220D`,
SHA-256 `f9031965db29afa581cffeff71a7a1038ab9036eb9feba4c3ddb2dab61cc52f5`.
These are target observations; the `_TEXT` and `_DATA` segment names come from
the compiler/linker projection. The target Ghidra database passed its MZ and
sampled-byte attestation during this packet.

[Maintained TASM source](../../../src/shared/dos/resdata.asm) searches the DOS
MCB chain and allocates a resident block with the historical near Pascal
three-word ABI (`RET 6`). It preserves the original strategy selection and
MCB ownership behavior. The independent historical master-library assembly
corroborates the algorithm; it is candidate source, not an exact Oracle.
The checked-in file is symbolic source, with no embedded target byte array.

Run `python3 scripts/probes/replay_th04_zun_resdata.py --output-dir
.analysis/reconstruction/probes/v323-zun-resdata-archive-final-ab`. Two cold
TC4J/TASM/TLINK rounds build the checked-in ZUN C++ objects and local shared
assembly. The script checks OMF framing and reproduces the original 640-member
diagnostic master library in its **physical** order. TLIB's alphabetical
listing cannot preserve that order: an ordinary object-list insertion moves
the ten-byte data contribution, while `-+resdata` moves the member to the end
and shifts later code. Rebuilding the diagnostic archive with the local member
at physical position 162 keeps the original MAP ownership. The external
library is still an Oracle input; it is not a checked-in product dependency.

In both rounds, local TASM emits exactly the target's 190 code bytes and ten
data bytes. The original-member control and local-member candidate each link
to the same 6360-byte component, SHA-256
`a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab`,
with the same MAP SHA-256
`9798e11f400727f4c5b2a0e22d9fd72f5d202f48eb79ffb4b24f68e3bbb07053`.
MAP places code at `_TEXT:051A` for `0xBE` bytes, data at `_DATA:179C`
for `0x0A` bytes, and `RESDATA_CREATE` at `_TEXT:0562` in the candidate
component. Receipt SHA-256:
`03dadb43dabdf77946172aa9f22604a64b987042936ffcada554ff2ec97e0362`.

The complete diagnostic resident component still has 4241 differing bytes
against the decoded target component. `_main` remains 246 rather than 252
bytes, other library members and composite inputs remain external, and the
packed ZUN artifact is not source-closed. Both RESDATA ranges are recorded as
library-origin source-present, with no artifact-local exact promotion.
