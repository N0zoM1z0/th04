# OP / MAINE SCORE high-score boundary and provenance review (v541)

This packet target-reviews four additional SCORE / high-score functions while
keeping the retained ReC98 C++ outside the accepted source plane.

## Reviewed target extents

OP:

| Function | Decoded extent | Size | Target SHA-256 |
| --- | --- | ---: | --- |
| hiscore_scoredat_load_both | 0xC733..0xC79D | 0x6B | 81cd0235b3e97394fab9168a5faeb316cf3590646ef4b71941c06d2a7dbe5e72 |
| scores_put | 0xC79E..0xC8A4 | 0x107 | f2d96c5f6893b598f652e03a82b3264267304b86b88e011286c946dc01695841 |

MAINE:

| Function | Decoded extent | Size | Target SHA-256 |
| --- | --- | ---: | --- |
| hiscore_scoredat_load_for | 0xC2AD..0xC315 | 0x69 | d7c242f31981b55c3dbdb0db4296e6bf59524f9d2d9bb6761d2fc8ea37e0d273 |
| hiscore_scoredat_save | 0xC316..0xC3B1 | 0x9C | 657805c7c6b0773da7bdcd1e6813507c1c3305fb75dd8ee695c3b6b75d9992b6 |

Each target Ghidra body is one contiguous range with an address count equal to
the listed size. Complete target disassembly closes exactly at the next
function entry with RET, and every direct branch stays inside its owner.
Each v489 artifact-local linked slice is raw-equal to its own target slice.

No OP bytes are used as MAINE evidence or vice versa.

## Function-level source provenance

The pinned ReC98 history directly contains these logical functions in commits
whose subjects are explicitly Decompilation:

- load_both and load_for:
  f761f8e313724e242d61bf979b36b45f15f14f60,
  High Score screen GENSOU.SCR loading;
- scores_put:
  9eef948b9380e9caf0b1019893858a9ae13ec3ef,
  High Score viewer score rendering;
- save:
  952ac1c042d2dcee0362e2491542a8b8d5a8ad4f,
  High Score menu GENSOU.SCR saving.

Later source moves and debloating place the logical loading code in
th04/hiscore/score_ld.cpp and saving in score_sv.cpp, but do not establish
independent original-source provenance.

Therefore the candidate C++ remains useful physical/codegen corroboration,
not accepted maintained source.

## Replay

Run:

    python3 scripts/probes/probe_th04_score_hiscore_boundaries.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The accepted v541 receipt is
.analysis/reconstruction/probes/v541-score-hiscore-boundaries-001/receipt.json,
SHA-256
85260ce08971a6972a59ace7263eb475c3a5fcbfbc01130e0bd5ea4005760b75.

## Ledger effect

Only physical boundary confidence changes. These four entries move from
corroborated to reviewed, while accepted_state remains unreviewed and
source_form remains candidate-cpp. No source-present or exact unit is added.

After v540/v541, all three MAINE hi_end candidate-C++ functions are physically
reviewed. OP hi_view still has five corroborated owners beginning with
stage_put and place_put; those should be handled as a separate target-first
packet rather than widening this claim.
