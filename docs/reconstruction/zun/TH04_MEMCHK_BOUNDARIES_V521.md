# MEMCHK physical boundary review (v521)

This packet closes the three game-authored function boundaries inside the
MEMCHK component of decoded TH04 ZUN.COM. It does not accept the retained
candidate assembly as original source and grants no authored exactness.

## Target component and authored contribution

MEMCHK occupies decoded payload 0x2440..0x3421, size 0x0FE2 / 4066 bytes,
SHA-256 2531795670b5cafb65bf261f499d5d77b71aeaf26015f8481000cdbb96272dfc.

The candidate MAP attributes only runtime COM _TEXT 0x367..0x3C9,
0x63 / 99 bytes, to th04_memchk.asm. In payload coordinates this is
0x26A7..0x2709. Target-first decoding partitions that contribution exactly:

| Entry / gap | Payload extent | Size | Terminal / value |
| --- | --- | ---: | --- |
| _main | 0x26A7..0x26CC | 0x26 | RET |
| padding | 0x26CD | 1 | 0x00 |
| sub_38E | 0x26CE..0x26F4 | 0x27 | RET 2 |
| padding | 0x26F5 | 1 | 0x90 |
| sub_3B6 | 0x26F6..0x2709 | 0x14 | RET |

No target control-flow edge enters either padding byte. The two gaps are
therefore outside all accepted authored function extents.

## Replay and source authority

Run:

    python3 scripts/probes/probe_th04_memchk_boundaries.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The probe attests the target, retained candidate source, MAP, linked MEMCHK
component, and a fresh TASM32 5.0 expanded listing. The listing must expose
exactly _main, sub_38E, and sub_3B6 at the expected entries. Those PROC entries
are corroboration only.

Each body is independently decoded from hash-attested target bytes with
ndisasm. Its complete branch/call vector and terminal instruction are checked.
The three function extents plus the two one-byte gaps must tile the full
candidate-authored 0x63-byte CODE contribution.

The retained linked memchk.com is raw-equal to the target MEMCHK component.
However, the candidate source header explicitly states that it was generated
by IDA. Its SHA-256 is
37738cdf77006976928c78b9da207ecb4c35a5b155e5c28f3d62f4f9deaf57fa.
Raw equality therefore corroborates offsets and linked behavior only; it does
not establish original-ASM provenance or maintained source ownership.

The v521 receipt
.analysis/reconstruction/probes/v521-memchk-boundaries-001/receipt.json
has SHA-256
69e3c95197ce8a5197d03cb0de7a8c8d05e4a59b4d6dbb118dad74a9ebabf31a.

## Ledger effect

All three MEMCHK authored entries move from corroborated to boundary-reviewed,
while retaining target-derived-asm source form and unreviewed acceptance.
No units.csv source owner is added and no function becomes exact.

Together with v520 ZUNINIT, every current ZUN authored candidate now has a
reviewed physical boundary: 13 reviewed / 0 corroborated / 0 provisional.
The eleven unresolved target-derived-asm source/origin questions remain open,
as do the blocked natural _main and cfg_init link contexts.
