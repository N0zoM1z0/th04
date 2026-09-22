# ZUN FILE_CREATE library replacement (v527)

This packet replaces the external MASTER filcreat member in the ZUN resident
diagnostic link with maintained symbolic TASM source. It is library support,
not authored ZUN exactness.

## Function and module

The decoded target FILE_CREATE function occupies payload 0x1250..0x128A,
size 0x3B / 59 bytes, SHA-256
afff204a724a02973d7a5ccaad7a755d86a3d466baf2d2554ea62bb86fd0f5b1.

The filcreat module contributes 0x3C CODE bytes. Payload 0x128B is a trailing
0x90 emitted by EVEN after the function and remains outside the function
owner. The linked target module SHA-256 is
935b2c0a3b3c7fab8c5dc101d9067fc7cbf47178d5647cb476203e7cb3269143.

Maintained source src/shared/dos/file_create.asm uses symbolic file globals
owned by _DATA/DGROUP and calls DOS_AXDX. Keeping the globals in their data
segment is required: declaring them in _TEXT makes TASM emit CS overrides and
changes code shape.

The local and extracted original objects have identical 0x3C zero-placeholder
LEDATA. TASM5 differs from the historical object in EXTDEF type-index metadata
and one equivalent FIXUPP frame encoding. v527 therefore does not claim raw
OMF identity. The acceptance gate is the final TLINK result: linked module,
MAP, and complete resident candidate must remain raw-identical.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_zun_file_create.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay replaces filcreat at zero-based MASTER archive position 172 while
keeping all previously localized support members. The accepted receipt
.analysis/reconstruction/probes/v527-zun-file-create-002/receipt.json
has SHA-256
6a2425f8f2896b79fe6284814260951da709d77cca59884d8074a96014625753.

Local link-relevant OMF SHA-256 is
81dc1ba9da568ea7b113af23815d6c70089218f9f9fe7b33213d4920e1d593da.
The final 6360-byte resident candidate and MAP remain unchanged at component
SHA-256
a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab.
The target residual remains 4241 raw bytes.

## Acceptance boundary

units.csv records only the 0x3B FILE_CREATE function as reviewed,
library-origin, source-present support. The final 0x90 remains module alignment
outside that owner. No authored ZUN function becomes exact.

Continue the remaining file-helper family with the same physical-module and
raw-linked-output gates.
