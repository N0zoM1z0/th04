# ZUN FILE_ROPEN library replacement (v528)

This packet replaces the external MASTER filropen member in the ZUN resident
diagnostic link with maintained symbolic TASM source. It is library support,
not authored ZUN exactness.

## Function and module

The decoded target FILE_ROPEN function occupies payload 0x1174..0x11A9,
size 0x36 / 54 bytes, SHA-256
93f82add9fb6bbde2532b0fe425029be749eea77f8582977456e8676ead80e3b.

Unlike FILE_CREATE, FILE_ROPEN fills its entire 0x36-byte module. The final
instruction is RET 2 and there is no function-external alignment byte.

Maintained source src/shared/dos/file_ropen.asm uses the historical near
Pascal ABI, symbolic MASTER file-state globals in _DATA/DGROUP, and the
external DOS_ROPEN entry. The local and extracted original members emit the
same 0x36 zero-placeholder LEDATA and external symbol name/order.

TASM32 5.0 does not reproduce the historical OMF byte-for-byte: segment/type
index metadata and the equivalent FIXUPP frame representation differ. Cold
A/B objects also differ in dependency-time COMENT bytes. Excluding COMENT,
the local link-relevant OMF is deterministic with SHA-256
f1f2405a71273620bd5090b1f98a1dede77a40f7c01cf6f77b424c6b72d79bc6.
Acceptance therefore remains on raw TLINK output, MAP, and target bytes rather
than normalized or raw object identity.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_zun_file_ropen.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay keeps all previously localized support members and replaces
filropen at zero-based MASTER archive position 170. The accepted receipt is
.analysis/reconstruction/probes/v528-zun-file-ropen-001/receipt.json,
SHA-256
62ce7f297ac2a91af856895061758f1395fe6e291c3ca23848d187b7b27fbb73.

Both cold rounds retain the historical resident candidate MAP SHA-256
9798e11f400727f4c5b2a0e22d9fd72f5d202f48eb79ffb4b24f68e3bbb07053
and the 6360-byte candidate component SHA-256
a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab.
The linked FILE_ROPEN module is raw-equal to the complete target extent. The
resident target residual remains 4241 bytes.

## Acceptance boundary

units.csv records the complete 0x36 FILE_ROPEN extent as reviewed,
library-origin, source-present support. It does not change the authored ZUN
function count or grant packed/composite exactness.

Continue the file-helper family with FILE_WRITE, FILE_SEEK, FILE_APPEND, and
FILE_CLOSE using the same physical archive, OMF-integrity, MAP, and raw-linked
output gates.
