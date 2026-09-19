# ZUN buffered file-read support migration, v325

The pinned `ZUN.COM` decoded payload contains a 180-byte `FILE_READ` body at
`0x1046..0x10F9`, SHA-256
`ba0aa97e36e670ba472356fe022772f3d69e574dea729ecce208691030209280`.
The candidate linker MAP projects it to `_TEXT:05D8` for `0xB4` bytes. This
range follows the [resident-data support](TH04_ZUN_RESDATA_V323.md). The
target identity and decoded payload are checked by the replay script; the
segment label comes from the compiler/linker projection.

[Maintained TASM source](../../../src/shared/dos/file_read.asm) implements the
near Pascal `FILE_READ` ABI: a far buffer pointer, a word count, and `RET 6`.
It reads through the shared file buffer or directly through DOS interrupt
21h. The historical master-library source corroborates the algorithm and
symbol ownership; it is candidate source rather than an exact Oracle. This
assembly translation unit contains no copied target bytes.

Run `python3 scripts/probes/replay_th04_zun_file_read.py --output-dir
.analysis/reconstruction/probes/v325-zun-file-read-final-ab`. Two cold
TC4J/TASM/TLINK rounds compile checked-in ZUN C++ and assemble local
`GRAPH_CLEAR`, `RESDATA`, and `FILE_READ`. Each round reconstructs the pinned
diagnostic library's 640-member physical order, compares an original-member
control with a local-member archive, and validates OMF framing and the MAP.
The local 180-byte OMF CODE matches the extracted historical `filread` member
byte-for-byte; its unlinked CODE SHA-256 is
`ca364a9a2ea5d5c4f5303dad086217316cadf8cee8240b4a41e4986ba5dee047`.
The local member remains at physical position 165 and contributes no data.

Both controls and local candidates link to the same 6360-byte resident
component, SHA-256
`a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab`,
and the same MAP SHA-256
`9798e11f400727f4c5b2a0e22d9fd72f5d202f48eb79ffb4b24f68e3bbb07053`.
The linked 180-byte slice equals the decoded target range. Receipt SHA-256:
`36bb01d0df468750ea4f348c30175b54d7130ceb88737f5b7fbeef55b5ed0570`.

The diagnostic component still differs from the target at 4241 raw bytes.
Other support members and composite inputs remain external, `_main` is six
bytes short, and packed ZUN exact acceptance remains open. This library-origin
unit is source-present without artifact-local exact promotion.
