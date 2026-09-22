# ZUN FILE_SEEK / FILE_TELL library replacement (v530)

This packet replaces the external MASTER filseek member with maintained
symbolic TASM source. The physical module contains two library-support
functions; neither counts as authored ZUN exactness.

## Target-first module partition

The decoded target filseek module occupies payload 0x128C..0x12CD, exactly
0x42 / 66 bytes, SHA-256
97d28f9689f230c9d01bb0a1006619bb489bac5672d6c43fa1392279e141df01.

Target-first disassembly and the candidate MAP split it as:

| Owner | Payload extent | Size | Terminal / value |
| --- | --- | ---: | --- |
| FILE_SEEK | 0x128C..0x12BE | 0x33 | RET 6 |
| alignment | 0x12BF | 1 | 0x90 |
| FILE_TELL | 0x12C0..0x12CD | 0x0E | RET |

FILE_SEEK SHA-256 is
349277df795d98cd8cbca8f33bd67d2f28823948cbd173101008fbe4ff571575.
FILE_TELL SHA-256 is
1b1850b8e4c09cf4a123667471565abb6b30ed80b4e646ef89a18efd4324b897.

This closes a boundary inventory gap: Ghidra had no FILE_TELL function at the
candidate MAP public. The target bytes independently decode a complete
14-byte function there. The intervening 0x90 belongs to neither function.

## Maintained source and OMF

src/shared/dos/file_seek.asm keeps both functions in one physical TU, matching
the historical MASTER organization. FILE_SEEK calls FILE_FLUSH, performs the
DOS 42h seek, then re-reads the current position and updates MASTER state.
FILE_TELL adds the current buffer offset to that stored position.

Two isolated TASM32 5.0 rounds emit deterministic 0x42 zero-placeholder
LEDATA SHA-256
d28bd048ef86f5b1a8ef5d70c2945e36d93938cf0f614f6bc794034be7040cc2
and deterministic link-relevant OMF SHA-256
c8d1da245194db17e821ec1ed1e58022a24b29897ae787d976dcd8c1e63879bd.
The extracted historical member has identical LEDATA; final linked bytes
remain the acceptance gate.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_zun_file_seek.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay preserves all earlier localized support and replaces filseek at
zero-based MASTER archive position 177. The accepted v530 receipt is
.analysis/reconstruction/probes/v530-zun-file-seek-001/receipt.json,
SHA-256
8d2d594964c4b4c5421b2c497a21cea8e2f3ff26a65eb302703c072a939c3b8c.

Both cold rounds retain candidate MAP SHA-256
9798e11f400727f4c5b2a0e22d9fd72f5d202f48eb79ffb4b24f68e3bbb07053
and 6360-byte resident component SHA-256
a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab.
Both functions and the complete module raw-match target. The resident target
residual remains 4241 bytes.

## Acceptance boundary

units.csv records FILE_SEEK and FILE_TELL as two reviewed, library-origin,
source-present units sharing one maintained TU. The 0x90 between them is
function-external module alignment and receives no function credit.

Continue with FILE_APPEND and FILE_CLOSE under the same physical archive,
OMF-integrity, MAP, and raw-linked gates.
