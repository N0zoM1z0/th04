# ZUN DOS_AXDX library replacement (v525)

This packet replaces the external MASTER dosc member in the ZUN resident
diagnostic link with maintained symbolic TASM source. It is library support,
not authored ZUN exactness.

## Function versus module layout

The decoded target DOS_AXDX function occupies payload 0x132E..0x1342,
size 0x15 / 21 bytes, SHA-256
ccf3bedd3a955505f0d5111f13dea7907ceb8d536d024bb9d69a21c8f2a35dd3.

The historical dosc module contributes 0x16 CODE bytes. The final byte at
payload 0x1343 is 0x90, emitted by word alignment after the function.
It is not part of the DOS_AXDX function owner. The complete 22-byte module
SHA-256 is
2653d1bfa735f07b9c6ec5f03aef2e0af2f64efdab15850ff42252cd6d9fc4db.

Maintained source src/shared/dos/dos_axdx.asm expresses the DOS call and
return-value normalization symbolically, then uses EVEN only to preserve
module layout. It also keeps the historical zero-byte _DATA / DGROUP
topology. No target byte array, codestring, object patch, or padding ownership
claim is used.

## Cold archive replacement

Run:

    python3 scripts/probes/replay_th04_zun_dos_axdx.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay keeps the already localized GRAPH_CLEAR, RESDATA, FILE_READ, and
DOS_FREE support, then replaces dosc at zero-based MASTER archive position
216. Local TASM output must match both the extracted original member and the
target module, while the function-scoped raw gate compares only the first
0x15 bytes.

The accepted v525 receipt
.analysis/reconstruction/probes/v525-zun-dos-axdx-001/receipt.json
has SHA-256
8e0debfa9c4b07e10e2cb9e5168e83454c7be1c7031710d2a9f96d93e3eb6f36.

The complete 6360-byte candidate resident and MAP remain unchanged at component
SHA-256
a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab.
The resident still differs from target at 4241 raw bytes.

## Acceptance boundary

units.csv records only the 0x15-byte DOS_AXDX function as reviewed,
library-origin, source-present support. The trailing 0x90 is module
alignment outside that owner. No ZUN authored function becomes exact.

The next smallest stable MASTER support member is DOS_PUTS2.
