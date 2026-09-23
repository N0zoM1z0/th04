# OP / MAINE score codec boundary and provenance review (v540)

This packet target-reviews six SCORE codec function boundaries in OP.EXE and
MAINE.EXE. It deliberately does not accept the retained ReC98 C++ as
independent original source.

## Reviewed target extents

OP:

| Function | Decoded extent | Size | Target SHA-256 |
| --- | --- | ---: | --- |
| scoredat_decode | 0xC57A..0xC626 | 0xAD | 5efe0d5065947fa7bc698dba06267ca16d3b34b3e90369907e14451fc9d0e2a5 |
| scoredat_encode | 0xC627..0xC68B | 0x65 | 737bdcca37820fb3848004e60f12b6e8121470668ea058fb233be1bac7e3b69f |
| scoredat_recreate | 0xC68C..0xC732 | 0xA7 | b5f25d0f2b5b7b1448d75000b98578cd8710ae419e2c8c079d717a014c796909 |

MAINE:

| Function | Decoded extent | Size | Target SHA-256 |
| --- | --- | ---: | --- |
| scoredat_decode | 0xC149..0xC1A0 | 0x58 | 31ea6a61abea7712e7ddd2ef8d9ee446b5947b514611252cba2d70c3930aff99 |
| scoredat_encode | 0xC1A1..0xC205 | 0x65 | c5c56e733842e6ba9b2d0448109939b2e04c8536b8495057425c4e787437c497 |
| scoredat_recreate | 0xC206..0xC2AC | 0xA7 | 7bc9464f7f09359087fb329a0c829021a834415aba27383f717d38cd1ba98094 |

For every function, the target Ghidra body is one contiguous range whose
address count and span equal the listed extent. Complete target ndisasm closes
exactly at the next function entry with RET, and every direct jump stays inside
the function. The retained v489 linked candidate slice is independently
raw-equal to the corresponding target slice in each artifact.

OP and MAINE are checked separately. Their linked bytes differ at normal
artifact-local address/fixup operands; no raw equality is transferred between
the two programs.

## Candidate-source provenance

Pinned ReC98 revision b6ba5b0a529edbb31efdf8c0e939263804f8ee47
introduces the three logical implementation files in commits whose subjects
explicitly start with Decompilation:

- decode.cpp: commit 36ecd3c7a9c7d988d0d0c1432c0d510d76b958a4,
  GENSOU.SCR decryption;
- encode.cpp: commit 01684c4a1dfd3f5855a5798e17658b3d4bccab87,
  GENSOU.SCR encryption;
- recreate.cpp: commit 09dc7318edebfeae6e53647cf70d6731a8abf743,
  GENSOU.SCR default data.

Later debloating and refactoring do not create independent original-source
provenance. The v487/v488 grouped-TU work remains useful physical producer
evidence, and the linked candidate functions remain useful codegen controls,
but neither fact turns these decompiled C++ files into accepted maintained
source for this reconstruction.

## Replay

Run:

    python3 scripts/probes/probe_th04_score_codec_boundaries.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The v540 receipt
.analysis/reconstruction/probes/v540-score-codec-boundaries-001/receipt.json
has SHA-256
7685eba0ba98e09ca33a222bc36d6e4a5c9935e65eea99402bae804e00b34a83.

## Ledger effect

Only boundary confidence changes:

- OP: three SCORE codec entries move from corroborated to reviewed.
- MAINE: three SCORE codec entries move from corroborated to reviewed.

All six remain accepted_state=unreviewed and source_form=candidate-cpp.
No units.csv source-present row is added and no function becomes exact.

The boundary generator now permits a target-reviewed non-ASM function only
when a review override has target evidence and an exact expected Ghidra body
span. target-derived-asm reviewed overrides still require a TASM PROC. This
keeps C++ target review durable without weakening assembly provenance rules.

The next SCORE boundary packet should review the remaining four hiscore
view/end functions. Source reconstruction remains a separate task and must
not copy the decompiled candidate merely because its linked bytes match.

## v562 OP encoder source-present result

Fresh OP review retains the 101-byte `scoredat_encode` target extent at
`1A74:1EE7`, payload `0xC627..0xC68B`, SHA-256
`737bdcca37820fb3848004e60f12b6e8121470668ea058fb233be1bac7e3b69f`.
It clears and accumulates the checksum over bytes `+4..+195`, calls the target
far helper at payload `0x204E` twice for the low-byte keys, then walks the score
payload backward. Each byte is reduced by `key1 + feedback`; the new feedback
is that byte rotated right three bits and XORed with `key2`. The pinned
candidate MAP labels the helper `IRAND`; that name is corroboration, not a
target-discovered symbol.

Maintained natural source is `src/op/score/scoreenc.cpp` plus
`src/op/score/scoreenc.inl`. The bounded pinned-TC86 probe at
`scripts/probes/probe_th04_op_scoredat_encode_codegen.py` is deliberately a
negative exactness diagnostic: it produces a valid 111-byte standalone OMF
CODE segment, not the target's 101 bytes. In particular, `_crotr` generates a
helper call rather than target `ROR byte [BP-1],3`; the size and raw comparison
fail before grouped acceptance. Its retained receipt
`.analysis/reconstruction/probes/v562-op-scoredat-encode-codegen-002/receipt.json`
has SHA-256
`9dda17426fd7c6f35bcebcbd2ab500333a141b7fec65410fb608843dcd6ff2b7`; its
generated A source tree was pruned, leaving only the receipt and compile log
(about 12 KiB). The encoder unit is `source-present`, not `decoded-exact`; OP
remains at 21 exact / 72 pending and no packed-file offset is inferred. Do not
copy the decompilation candidate's inline assembly or change compiler flags to
force equality. Next target-first codec owner is `scoredat_decode` at payload
`0xC57A`.
