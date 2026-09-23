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
not accepted maintained source by itself. A separate target-first maintained
reconstruction of MAINE `hiscore_scoredat_load_for` is recorded below; it does
not change the provenance of the candidate source or the other three owners.

## Replay

Run:

    python3 scripts/probes/probe_th04_score_hiscore_boundaries.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The accepted v541 receipt is
.analysis/reconstruction/probes/v541-score-hiscore-boundaries-001/receipt.json,
SHA-256
85260ce08971a6972a59ace7263eb475c3a5fcbfbc01130e0bd5ea4005760b75.

## Ledger effect

At the v541 checkpoint only physical boundary confidence changed: these four
entries moved from corroborated to reviewed while accepted_state remained
unreviewed and source_form remained candidate-cpp. The later v557 section
records a separate maintained reconstruction for MAINE `load_for` only.

After v540/v541, all three MAINE hi_end candidate-C++ functions are physically
reviewed. OP hi_view still has five corroborated owners beginning with
stage_put and place_put; those should be handled as a separate target-first
packet rather than widening this claim.

## v557 maintained MAINE high-score loader

Target-first reinspection closes the complete loader at `1A05:225D`, payload
`0xC2AD..0xC315` (105 bytes), ending `RET 2`; the next target entry is
`0xC316`. The fresh boundary probe decoded 37 instructions and three internal
conditional branches, with every direct branch remaining inside the extent.
The complete target slice SHA-256 is
`d7c242f31981b55c3dbdb0db4296e6bf59524f9d2d9bb6761d2fc8ea37e0d273`.

Maintained natural C++ lives in `src/maine/score/load_for.cpp` with its bounded
body in `load_for.inl`. The two standalone OMF CODE differences are exactly
the near-call displacement words at offsets `0x54` and `0x5B`, each covered by
an OMF FIXUPP record. The grouped SCORE_TEXT link reproduces the full 105-byte
target function raw-zero in both focused cold rounds; all 559 ordered
relocations remain target-equal. The complete candidate EXE SHA-256 is
`d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c`, and its
MAP SHA-256 is
`014d8dfdf31a2c42c39e76288f23842cff7bd84fb6534f6d46479ba5d8b0838e`.
The MAINE cold aggregate now passes all 21 registered decoded slices.

Replay with:

    python3 scripts/probes/replay_th04_maine_score_load_for.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME
    python3 scripts/decoded_function_acceptance.py --artifact th04-maine --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The focused receipt is
`.analysis/reconstruction/probes/v557-maine-score-load-for-probe-003/receipt.json`
(SHA-256 `5619926ba48c4654cc158552155179f85a74bc11b37daf08c4241d92077d3d43`);
the aggregate receipt is
`.analysis/reconstruction/probes/v557-maine-cold-aggregate-001/receipt.json`
(SHA-256 `d9c4f971d7e6baa0dff03c253e1d6edc459b6aed3064ee65abe5ad2780a6c4f4`).
Both rounds match at the function extent. The packed-file offset is unknown;
candidate program size is 62,414 bytes versus the target's 65,634, so neither
the DIET-packed MAINE file nor the whole executable is exact. The candidate
function name remains a MAP/candidate-derived label, not target-attested
original-source provenance.

The boundary and decoded-function ledgers mark this one function exact on the
decoded plane only. The corresponding `units.csv` row remains
`source-present`, because no honest packed-file offset exists.
