# ZUN FIL file-state DATA / BSS library replacement (v535)

This packet replaces the external MASTER fil member with maintained symbolic
TASM. The member is library support, not authored ZUN exactness.

## Physical ownership

The physical archive member is at zero-based MASTER index 163. It contributes
empty _TEXT, initialized _DATA of 0x04 bytes at candidate _DATA:17A6, and
uninitialized _BSS of 0x14 bytes at candidate _BSS:19DA.

The decoded target has the four initialized DATA bytes at payload
0x220E..0x2211: 00 00 FF FF, SHA-256
b7d1b3a1104cc86b1cea310793cf777002db0517281d135a02de079b0ea87c23.
These are file_BufferSize = 0 and file_Handle = -1.

The BSS owner contains file_Pointer, file_Buffer, file_BufferPos,
file_BufPtr, file_InReadBuf, file_Eof, and file_ErrorStat, with their
underscore aliases. BSS is uninitialized and has no bytes in the COM file.
It therefore has no target raw-byte extent; its acceptance is strictly OMF
SEGDEF/PUBDEF plus MAP/link layout.

## Maintained source and OMF

src/shared/dos/file_state.asm emits the same physical topology: empty _TEXT,
four-byte _DATA, and 0x14 _BSS. Two isolated TASM32 5.0 assemblies are
byte-identical. The link-relevant OMF SHA-256 is
70ec111491abefe0181bec46a21a994ab636dbe87991b5ce85a56363726d311b.

The extracted historical member is SHA-256
d4076f83e6d4fd4aa297a606ed2b9c1a0e7168e3ba7bab18b8b9e68af525ba45.
Local TASM uses different OMF record organization but preserves segment sizes,
DATA LEDATA, all public names and offsets, and final linked bytes.

## TASM5 public-order quirk

The original resident MAP and the local TASM5 MAP differ only in the display
order of _file_BufferPos and file_BufferPos at address 0000:19E2 in Publics
by Value. Multiple natural PUBLIC / LABEL / EQU declaration variants were
tested; whenever both real PUBDEF symbols exist, TASM5 preserves this ordering.

The replay does not normalize arbitrary MAP differences. A dedicated
fail-closed comparator permits only this exact two-line swap at 0000:19E2;
line count, all other MAP lines, segment contributions, public addresses, and
names must remain identical. Original MAP SHA-256:
9798e11f400727f4c5b2a0e22d9fd72f5d202f48eb79ffb4b24f68e3bbb07053.
Local MAP SHA-256:
3b93fe383819cd4734393064192481a10ffaf814d5468c209dc27aa6e5c0820c.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_zun_file_state.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The accepted v535 receipt is
.analysis/reconstruction/probes/v535-zun-file-state-002/receipt.json,
SHA-256
9b5854d18669b8c87f7bd60706c5659b0de52b6eab3ab7ec37070779ed2a7047.

The four initialized DATA bytes raw-match target. The BSS SEGDEF size/public
layout matches the historical owner. Replacing fil at archive index 163 leaves
the complete 6360-byte resident candidate byte-identical, SHA-256
a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab.
The target residual remains 4241 bytes.

## Acceptance boundary

units.csv records separate initialized-DATA and BSS support units. The BSS
unit intentionally has no artifact/file offset. Neither changes authored ZUN
exactness.

The next support work should inventory the remaining resident CRT/libc modules
before choosing another owner. Do not migrate CRT members merely to reduce an
external-dependency count; keep producer and layout evidence explicit.
