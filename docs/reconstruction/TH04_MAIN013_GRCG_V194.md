# TH04 MAIN_013 GRCG producer reconstruction (v194)

## Scope

This packet reviews the complete `MAIN_013_TEXT` contribution and the adjacent
`CHECKERB_TEXT` owner in the locally attested TH04 `MAIN.EXE` target.

The private target is still only `candidate-local-attested`; none of the target
bytes are checked in or used as generated source.

| Owner | MAP | Load-module extent | File extent | Size | Target SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| `MAIN_013_TEXT` | `0AAF:74D8..7585` | `0x11FC8..0x12075` | `0x137C8..0x13875` | `0xAE` | `82e90acf57d9fb1c8ef83ed1b0e91857cfba3dc98a3d3a8a27fda89cfe97ac85` |
| `CHECKERB_TEXT` | `0AAF:7586..7633` | `0x12076..0x12123` | `0x13876..0x13923` | `0xAE` | `a1ce86ff7d72218b6ea7c8ae3a4e2f94b64cd4c6c792c523d28e7be9f5732c60` |

`MAIN_013_TEXT` has no ordered MZ relocation overlap and consists of five
logical near entries plus two source-owned alignment NOPs:

| Entry | Load extent | Size | Boundary result |
| --- | --- | ---: | --- |
| `@grcg_tile_bb_put_8` | `0x11FC8..0x12009` | `0x42` | Reviewed original-style ASM; Ghidra has no function entry |
| `playfield_fillm_0_40_384_274` | `0x1200A..0x12022` | `0x19` | Reviewed original-style ASM; Ghidra body agrees |
| alignment | `0x12023` | `0x01` | Physical owner byte, not a function |
| `sub_12024` | `0x12024..0x12059` | `0x36` | Reviewed original-style ASM; Ghidra has no function entry |
| `playfield_fill` | `0x1205A..0x12067` | `0x0E` | Reviewed original-style ASM; Ghidra body agrees |
| `_grcg_fill_playfield_rows` | `0x12068..0x12074` | `0x0D` | Reviewed original-style ASM; Ghidra body agrees |
| alignment | `0x12075` | `0x01` | Physical owner byte, not a function |

The maintained producer is `src/main/hardware/playfield_grcg.asm`, SHA-256
`7840ea15852072823aed7569d98dcb1d5a20881a2e0d4868247573d9df6690e7`.
It is symbolic assembly, not target-derived byte data.

## Boundary and origin evidence

Fresh attested Ghidra still reports no containing function at analysis-linear
`0x21FC8` or `0x22024`. It constructs contiguous functions at `0x2200A`,
`0x2205A`, and `0x22068`. These are provisional semantic observations only.
Raw 16-bit decode, historical TASM PROC boundaries, the TLINK MAP, immediate
next-entry seams, and the exact linked physical owner close the complete extent.

Independent TH05 target evidence contains byte-identical complete tile-fill,
hardware-clear, and row-fill cores. ReC98 is useful for lineage and build
scaffolding but its reconstructed source is not treated as historical authority.
A bounded natural TC4J probe for `_grcg_fill_playfield_rows` emits 28 bytes
rather than the 13-byte target helper, expanding the write loop and flag reuse.
Together with the independent target lineage and symbolic TASM reproduction,
this supports the original-style ASM classification without converting a
failed C++ probe into proof by itself.

## OMF public ownership correction

Recovery found a link-only aggregate failure after the code bytes were already
focused-exact. The Pascal declaration used by `bomb.cpp` requires the uppercase
OMF public `PLAYFIELD_FILLM_0_40_384_274`, while the standalone producer had
listed the lowercase spelling first.

A pinned TASM32 5.0 probe demonstrates that `/mx` records the first spelling of
this case-insensitive public. Lowercase-first and uppercase-first probe objects
have identical LEDATA-record payload SHA-256
`26a338c181b9be70afa1790c3ae0fd2d3eef02142519b05235f52c3bc7675212`
and no FIXUPP records. Reordering the public declarations therefore changes OMF
symbol metadata only. The uppercase-first probe object SHA-256 is
`dbec06e4918fd2925e7a5dc0c5e317dc38cd96e58cb6cf5c90750704959d8fa9`.
The overlay scaffold now also declares the uppercase external spelling.

The focused exact object is 645 bytes with SHA-256
`b3eff3dd886711e66130bc261de3e69388a870db01dd52efc15a662278effb89`.
Both cold builds publish the uppercase Pascal symbol and produce identical OMF.

## Exact replay

Focused replay:

- run: `gptweb-v194-main013-grcg-focused-candidate-007`
- selected dependency closure: 128 owners
- failures: `[]`
- receipt SHA-256: `bb0bd95b8e718e776003771e0dfb5356fea8429b8b76194541abce032f8ee96d`

Candidate aggregate replay before promotion:

- run: `gptweb-v194-main013-grcg-aggregate-candidate-005`
- tracked/default candidate cohort: 232 owners
- failures: `[]`
- receipt SHA-256: `e5d84ffd60fc6451c247fd2eb79e016de7eb01366c554cdd5265cf2f166eae55`

Post-promotion aggregate replay:

- run: `gptweb-v194-main013-grcg-aggregate-final-001`
- tracked default exact cohort: 232 owners
- failures: `[]`
- receipt SHA-256: `2324133cdc691856bb502b404ec6d735319307326862f5bf6cccf3ab5cb4b899`
- manifest SHA-256: `ef03f9e7071efef57bc8c8e6204bfd7cf492b3284ddf9656deea13981b2093e4`
- A/B MAP SHA-256: `6d9caabc4e0a87eed403e246e164e1a78e9798576b3285c313f3cd0899c2b670`
- candidate `MAIN.EXE` SHA-256: `205e42067b0eb3534dc83deba125ebf845c1c153f6515ebe60430d3a79f21bd9`

The aggregate candidate image is an exactness-oracle product of the pinned
ReC98 overlay build. It is not a standalone TH04 production build and is not
claimed to be whole-image-identical to the private target.

## Adjacent checkerboard negative result

`playfield_checkerboard_grcg_tdw_update_and_render()` is now reviewed as the
complete `CHECKERB_TEXT` extent `0x12076..0x12123`, size `0xAE`. Fresh Ghidra
constructs only 46 sparse body bytes through analysis-linear `0x220BC` and
reports no callers, while target raw review finds two near-call anchors. The
next `MB_INV_TEXT` owner begins immediately at load `0x12124`.

Maintained natural source is `src/main/stage/checkerboard.cpp`, SHA-256
`647bb108f3ede67d98d09157dd305d41deaa4e34c47606cdc3090732af51679f`.
The historical reconstruction obtains the target `LOOP` through inline
assembly; that escape hatch is deliberately rejected. Natural TC4J instead
emits `DEC CX; MOV AX,CX; OR AX,AX; JNZ`, making the linked owner 179 bytes
(`0xB3`) instead of 174 (`0xAE`). Two-cold linked replay is deterministic but
nonexact. The function therefore remains source-present, reviewed, and blocked
with zero exactness credit.

## Accounting and next packet

This packet moves five `MAIN_013_TEXT` observations from the authored C/C++
reconstruction queue to the separate original-style ASM attestation queue and
adds the complete checkerboard function to the reviewed blocked C/C++
denominator. It does not inflate C/C++ exactness with ASM credit.

After regeneration, MAIN reports 56 ASM-attestation observations, 24 blocked
C/C++ observations, and 32 unreviewed C/C++ observations. Exact original-style
ASM physical ownership is 29 units / 4,370 bytes. Maintained C/C++ exactness is
75,209 / 80,868 reviewed bytes and 456 / 479 reviewed functions.

The next structurally meaningful MAIN candidate is `END_TEXT sub_B835` at load
`0xB835`, currently a corroborated 0xC7 TASM/Ghidra extent with no accepted
source verdict. Review its owner, adjacent entries/data, callers/callees,
relocations, and source lineage before choosing C/C++ versus original ASM.
`MAI_TEXT midboss2_render()` at load `0xCC3A`, size 0x9C, is the next sizeable
fallback. OP, MAINE, and ZUN remain independent artifact queues and receive no
MAIN exactness by transfer.
