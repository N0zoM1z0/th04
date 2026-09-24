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

## v563 OP decoder source-present result

The target `scoredat_decode` extent is 173 bytes at `1A74:1E3A`, payload
`0xC57A..0xC626`, SHA-256
`5efe0d5065947fa7bc698dba06267ca16d3b34b3e90369907e14451fc9d0e2a5`.
Direct target decoding shows two forward passes over the 196-byte `hi` and
`hi2` sections: for each byte from `+4` through `+194`, feedback comes from the
next encoded byte rotated right three bits and XORed with `key2`; the current
encoded byte is increased by `key1 + feedback`. Byte `+195` is increased by
`key1`, then the 16-bit sum over `+4..+195` is checked. A failed first section
returns 1; after the second section, the routine returns the low-byte difference
between its stored checksum and computed sum.

Maintained natural source is `src/op/score/scoredec.cpp` plus
`src/op/score/scoredec.inl`. The bounded TC86 probe at
`scripts/probes/probe_th04_op_scoredat_decode_codegen.py` produces 197 standalone
bytes against the target's 173. The two ordinary shift/OR feedback rotations
each compile to a longer sequence than the target's in-place `ROR byte
[BP-1],3`; the candidate's inline assembly was not imported. Its retained
receipt `.analysis/reconstruction/probes/v563-op-scoredat-decode-codegen-005/receipt.json`
has SHA-256
`06e516fa190d5ac8462ed3b2a65728a7cfae39dde86570fb3f783b9546e25afa`, and the
small generated listing is kept beside it for diagnosis. The unit remains
source-present/nonexact and its packed-file offset is unknown. OP remains at
21 exact / 72 pending. At that checkpoint the next target-first surface was
`input_wait_for_change` at payload `0xDB62`.

## v574 MAINE decoder source-present result

The reviewed MAINE `scoredat_decode` extent is 88 bytes at `1A05:20F9`, payload
`0xC149..0xC1A0`, target SHA-256
`31ea6a61abea7712e7ddd2ef8d9ee446b5947b514611252cba2d70c3930aff99`. The
freshly attested target body is one contiguous Ghidra range with 33 instructions
and four internal aligned direct branches, ending in `RET`.

Target interpretation (inferred from those instructions): the loop advances
from record offset `+4` through `+194`; each current score byte receives
`key1 + (ROR(next_encoded_byte, 3) XOR key2)`. The final score byte at `+195`
receives `key1`. The routine sums the 192 decoded score bytes and returns the
low-byte difference between the stored sum and computed sum. The label
`scoredat_decode` is a candidate symbol, not an independently observed name.

Maintained natural source is `src/maine/score/scoredec.cpp` plus
`src/maine/score/scoredec.inl`. It uses a near view of `hi`, ordinary shift/OR
rotation, and a register checksum accumulator. The focused TC86 4.02 replay
produces a valid 97-byte standalone `SCORE_TEXT` OMF segment, nine bytes longer
than the reviewed target. Its rotation compiles to shifts and OR rather than the
target's in-place `ROR byte [BP-1],3`, so this is source-present/nonexact only;
no target-derived assembly, packed-file offset, or full-MAINE exactness is
claimed. The probe stops at this standalone size mismatch before grouped link
acceptance.

The retained diagnostic receipt is
`.analysis/reconstruction/probes/v574-maine-scoredat-decode-005/receipt.json`,
SHA-256
`b56860ffa421eeac5307e6a5125c1036bfa2abe875b14d2bf352bf55ea6455bd`. It keeps
the target and natural-source disassemblies; the generated A build tree and
compile log were moved to trash, leaving only the 5.3 KiB receipt. MAINE remains
at 25 decoded-function exact slices / 2,297 exact bytes, plus this 88-byte
source-present candidate (2,385 total decoded source-owner bytes). Next codec
owner at that checkpoint was the separately reviewed `scoredat_encode` at
payload `0xC1A1`.

## v577 MAINE encoder source-present result

The reviewed MAINE `scoredat_encode` extent is 101 bytes at `1A05:2151`,
payload `0xC1A1..0xC205`, target SHA-256
`c5c56e733842e6ba9b2d0448109939b2e04c8536b8495057425c4e787437c497`. Fresh
target disassembly closes one contiguous Ghidra body with 34 instructions, four
internal aligned direct branches, and `RET` at the final byte.

Target observation: the body clears the 16-bit sum word, accumulates the bytes
at `+4..+195`, calls far `0000:1C5A` twice and stores each return's low byte into
the two key fields, then walks backward from `+195` to `+4`. Each current byte
is reduced by key1 plus feedback; feedback becomes that newly encoded byte
rotated right three bits and XORed with key2. The interpretation as an encoder
is inferred from those effects. `scoredat_encode` and `irand` are candidate/MAP
names, not target-attested symbols.

Maintained natural C++ is `src/maine/score/scoreenc.cpp` plus
`src/maine/score/scoreenc.inl`. Direct near-byte accesses reproduce the
target-like loop structure and two far calls in TC86 output, but the standalone
`SCORE_TEXT` segment is 113 bytes, 12 bytes over target. The target's four-byte
in-place `ROR byte [BP-1],3` is one instruction; natural shift/OR expands to a
16-byte sequence. The codegen diagnostic therefore stops before grouped/raw
acceptance. No target-derived assembly or packed-file offset is claimed.

The receipt
`.analysis/reconstruction/probes/v577-maine-scoredat-encode-002/receipt.json`
has SHA-256
`cacd9942ab10700798df036caad7c717b9cd6770ec8d386db390e4b4b7015e5c` and
contains both target and natural-source disassemblies, source digests, and the
valid TC86 OMF identity. The generated 8 MiB A worktree and compile log were
moved to trash immediately, leaving only the 12 KiB receipt. v580 supersedes
the then-pending adjacent `scoredat_recreate` work described below.

## v580 MAINE score-file recreation decoded-function exact

The reviewed `scoredat_recreate` candidate extent is payload `[0xC206,0xC2AD)`
(167 bytes) at `1A05:21B6`. Target disassembly observes it initialize the
high-score cleared flag and ten rows, then create the score-data file, encode
each row, write 0xC4 bytes, decode the row, and close the file. The source-level
symbol identity remains candidate/MAP-derived rather than target-attested.

Maintained natural C++ is `src/maine/score/scoregen.cpp` plus
`src/maine/score/scoregen.inl`. Two cold focused builds reproduce the complete
decoded slice raw-zero. A standalone-TU diagnostic differs at two near-call
FIXUPP displacement words (CODE offsets `0x87` and `0x96`); the grouped
`SCORE_TEXT` producer, candidate MZ/MAP baseline, and all 559 ordered MAINE
relocations remain stable. The subsequent 26-slice MAINE aggregate checks the
same complete function raw-zero. This promotes only the decoded function:
MAINE's candidate program is still shorter than the target, the packed-file
offset is unknown, and no whole-artifact exactness follows.

The v579 diagnostic isolated a TU-composition hazard: the candidate header
macro-expands `SCOREDAT_FN` into a filename literal. In the replacement owner,
undefine that macro before declaring the existing external filename array;
otherwise a `GENSOU.SCR` DGROUP literal appeared and grew the linked program by
12 bytes. The v580 source retains the external symbol and restores baseline
MZ/MAP bytes. Do not interpret this macro behavior as proof of the historical
symbol name. The focused receipt is
`.analysis/reconstruction/probes/v580-maine-scoredat-recreate-002/receipt.json`
(SHA-256 `0ddc5503997680017bad2989749a55b069ac7e787b811a8fc26d89b9c02567f1`);
the final exact-state aggregate receipt is
`.analysis/reconstruction/probes/v580-maine-score-exact-aggregate-final-001/receipt.json`
(SHA-256 `1782fc9ff8ff003485b3dca84fff8c0d5c431ae09e33d97584394c7984bb7b83`).

MAINE now has 26 decoded-function exact slices / 2,464 exact bytes, plus the
two source-present/nonexact codec candidates `scoredat_decode` (88 bytes) and
`scoredat_encode` (101 bytes), for 2,653 decoded source-owner bytes total.
