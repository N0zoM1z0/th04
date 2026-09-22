# ZUN DOS_PUTS2 library replacement (v526)

This packet replaces the external MASTER dosputs2 member in the ZUN resident
diagnostic link with maintained symbolic TASM source. It is library support,
not authored ZUN exactness.

## Function versus module layout

The decoded target DOS_PUTS2 function occupies payload 0x1344..0x136A,
size 0x27 / 39 bytes, SHA-256
90259993539788eb6cc440e98400c1551f6502aa42c64d1fe8d5860539b9c981.

The historical dosputs2 module contributes 0x28 CODE bytes. The final byte at
payload 0x136B is 0x90 from word alignment after the function. It is outside
the DOS_PUTS2 function owner. The complete 40-byte module SHA-256 is
c346fe75402242d9b1348e634244efb9e94ba1b8dc637602d8767f0c6c5fb3d9.

Maintained source src/shared/dos/dos_puts2.asm prints a near NUL-terminated
string through DOS AH=02h, expands LF to CR/LF, preserves SI, and uses EVEN
only for module alignment. It also preserves the historical zero-byte _DATA /
DGROUP topology. No codestring, object patch, or target byte array is used.

## Cold archive replacement

Run:

    python3 scripts/probes/replay_th04_zun_dos_puts2.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay keeps the previously localized support members and replaces
dosputs2 at zero-based MASTER archive position 221. The two cold TASM objects
may differ in a Borland/TASM dependency-time COMENT record; every non-COMENT
OMF record must instead match the pinned link-relevant digest
7106e7fd80b01134a9fbc76229f8dd09a62945bc67da0547d0ff237bff1e7a4d.
Raw function/module bytes, MAP, and final resident component are never
normalized.

The accepted v526 receipt
.analysis/reconstruction/probes/v526-zun-dos-puts2-001/receipt.json
has SHA-256
dd4ab8c5bd31e659685067f2332aafb56bf8011d01660c30aec5ad78e3b65145.

The complete 6360-byte candidate resident and MAP remain unchanged at
component SHA-256
a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab.
The resident still differs from target at 4241 raw bytes.

## Acceptance boundary

units.csv records only the 0x27-byte DOS_PUTS2 function as reviewed,
library-origin, source-present support. The trailing 0x90 remains module
alignment outside that owner. No ZUN authored function becomes exact.

The next external surface is the file-helper family plus VERSION/GRP/FONTOPEN.
