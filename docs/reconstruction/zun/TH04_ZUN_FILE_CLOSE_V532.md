# ZUN FILE_FLUSH / FILE_CLOSE library replacement (v532)

This packet replaces the external MASTER filclose member with maintained
symbolic TASM source. It completes the immediate file-helper support family;
neither function counts as authored ZUN exactness.

## Target-first module partition

The decoded target filclose module occupies payload 0x10FA..0x1173, exactly
0x7A / 122 bytes, SHA-256
90029ad4fbf09f328e31116ad1618037ef39a6866b05f661842142fba3f438ac.

Target-first disassembly partitions it as:

| Owner | Payload extent | Size | Terminal / value |
| --- | --- | ---: | --- |
| FILE_FLUSH | 0x10FA..0x1164 | 0x6B | RET |
| alignment | 0x1165 | 1 | 0x90 |
| FILE_CLOSE | 0x1166..0x1173 | 0x0E | RET |

FILE_FLUSH SHA-256 is
d1d0993554f298bde55a09b8e79a49e7f3819db9ec869c903937347af8e495da.
FILE_CLOSE SHA-256 is
9af8f01eaf9db22dbf91343f0fcdfa1d579951320cfdd11181622cccb6bc21ca.
The 0x90 belongs to neither function.

## Maintained source and OMF

src/shared/dos/file_close.asm retains both functions in their historical
physical TU. FILE_FLUSH handles buffered writes and read-buffer position
reconciliation; FILE_CLOSE calls it, closes the DOS handle, and invalidates
the MASTER file state.

Two isolated TASM32 5.0 rounds emit deterministic 0x7A zero-placeholder
LEDATA SHA-256
f7aea53ef369cf41b32b3167382f3f5aa60e1c0b139b767af1b1c03869a30a15
and deterministic link-relevant OMF SHA-256
327f736eb0c0b24d9159c63993414d375331b97b7ac64d90ef02c2dca4a8c69b.
The extracted historical member has identical LEDATA; final linked bytes
remain the acceptance gate.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_zun_file_close.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay preserves all earlier localized support and replaces filclose at
zero-based MASTER archive position 167. The accepted v532 receipt is
.analysis/reconstruction/probes/v532-zun-file-close-001/receipt.json,
SHA-256
9dc01780a34f012e648ed13b9afbd7b48507b679373da7c50bab017d83d10914.

Both cold rounds retain candidate MAP SHA-256
9798e11f400727f4c5b2a0e22d9fd72f5d202f48eb79ffb4b24f68e3bbb07053
and 6360-byte resident component SHA-256
a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab.
Both functions and the complete physical module raw-match target. The
resident target residual remains 4241 bytes.

## Acceptance boundary

units.csv records FILE_FLUSH and FILE_CLOSE as two reviewed, library-origin,
source-present units sharing one maintained TU. The 0x90 between them is
function-external module alignment.

With v325 and v527-v532, the immediate MASTER file-helper family used by the
resident path is now maintained source: FILE_READ, FILE_FLUSH, FILE_CLOSE,
FILE_ROPEN, FILE_WRITE, FILE_CREATE, FILE_SEEK, FILE_TELL, and FILE_APPEND.
Further support work should move to VERSION/GRP/FONTOPEN or another
target-reviewed dependency; authored ZUN blockers stay evidence-triggered.
