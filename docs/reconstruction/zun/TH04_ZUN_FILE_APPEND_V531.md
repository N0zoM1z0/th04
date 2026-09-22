# ZUN FILE_APPEND library replacement (v531)

This packet replaces the external MASTER filapend member with maintained
symbolic TASM source. It is library support, not authored ZUN exactness.

## Target owner

The decoded target FILE_APPEND function occupies payload 0x12CE..0x131D,
exactly 0x50 / 80 bytes, SHA-256
ae7738e040ed138bb1e8b0d6a29e589d163c9e579f1584431db598f3b5825df5.
The final instruction is RET 2, and DOS_FREE begins immediately at 0x131E.
There is no function-external module padding.

Maintained source src/shared/dos/file_append.asm preserves the near Pascal
filename ABI, opens read/write through DOS_AXDX, clears MASTER file state,
and seeks to end with INT 21h/AH=42h.

Two isolated TASM32 5.0 rounds emit deterministic 0x50 zero-placeholder
LEDATA SHA-256
d696c040bb4e1a86f4028d0777fa6ef9af1c56ecd2a8dc8372e718a29de7cec5
and deterministic link-relevant OMF SHA-256
d258612419a3b108b3da62949d10264564281df0551d32b15bbf957bda00de68.
The extracted historical member has identical LEDATA; final linked bytes are
the acceptance gate.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_zun_file_append.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay preserves all previously localized support members and replaces
filapend at zero-based MASTER archive position 182. The accepted receipt is
.analysis/reconstruction/probes/v531-zun-file-append-001/receipt.json,
SHA-256
fcb0f2c1a8c6571c6243632939a23765fd8686a7afd9c4c65bbd307f7077c6b6.

Both cold rounds retain candidate MAP SHA-256
9798e11f400727f4c5b2a0e22d9fd72f5d202f48eb79ffb4b24f68e3bbb07053
and 6360-byte resident component SHA-256
a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab.
The complete FILE_APPEND module raw-matches target. The resident target
residual remains 4241 bytes.

## Acceptance boundary

units.csv records the complete 0x50 FILE_APPEND extent as reviewed,
library-origin, source-present support. It does not change authored ZUN
exactness.

FILE_CLOSE is the final remaining member in this immediate MASTER file-helper
family before moving to VERSION/GRP/FONTOPEN and other support.
