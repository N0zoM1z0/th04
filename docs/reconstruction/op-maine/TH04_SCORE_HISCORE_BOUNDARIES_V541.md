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

## v558 maintained OP two-column high-score loader

Fresh target review closes `hiscore_scoredat_load_both` at `1A74:1FF3`,
payload `0xC733..0xC79D` (107 bytes). The complete stream has 39 instructions,
two internal direct branches, and a terminal `RET`; `scores_put` begins at the
adjacent payload `0xC79E`. The target slice SHA-256 is
`81cd0235b3e97394fab9168a5faeb316cf3590646ef4b71941c06d2a7dbe5e72`.

Target bytes at payload `0x10682` contain `GENSOU.SCR\0`, matching the
loader's direct `DS:1342` filename reference under the attested MZ load map.
The target stream observes a `rank * 0xC4` seek, a `0xC4`-byte read into
`hi`, a `0x310` relative seek, then a second `0xC4`-byte read into `hi2`.
After close it calls the score decoder; the target returns true after
recreation and false after a successful load/decode. The maintained natural
owner is `src/op/score/loadboth.cpp` with body
`src/op/score/load_both.inl`, using `sizeof(hi)` so the shared body compiles
in both its standalone TU and the candidate's grouped SCORE scaffold.

TC86 standalone CODE differs from the grouped owner only at two OMF FIXUPP
words for DGROUP addresses (`0x1A`, `0x4A`) and two near-call displacements
(`0x5A`, `0x61`). Both cold rounds agree on the standalone and grouped
link-relevant OMF, complete candidate EXE/MAP, full function slice, and all
804 ordered MZ relocation sites. The focused receipt is
`.analysis/reconstruction/probes/v558-op-score-load-both-probe-004/receipt.json`
(SHA-256 `12df8a2551d03452a3ec6327ac4b34eb16867ad9c036729d732649515e1e1305`);
the OP aggregate receipt is
`.analysis/reconstruction/probes/v558-op-cold-aggregate-001/receipt.json`
(SHA-256 `8d2a1958cf0da1bd9a6d969161b9b1fe7b4e44328a9e594558ad2988bd44c177`).
All 19 registered OP slices compare raw-zero. The candidate program image is
69,028 bytes versus the target-restored 72,256 bytes, so neither packed OP nor
the whole executable is exact. The `units.csv` owner remains `source-present`
because its DIET-packed file offset is unknown; decoded exactness is recorded
separately. The MAP label and retained ReC98 source remain candidate evidence,
not proof of original-source provenance.

## v559 maintained OP score renderer

Fresh target boundary replay and the earlier v541 review agree that
`scores_put` owns payload `0xC79E..0xC8A4` (263 bytes) at `1A74:205E`. The
target stream has 102 instructions and four internal branches, terminates at
`0xC8A2` with `RET 4`, and is followed by `stage_put` at `0xC8A5`. Its target
slice SHA-256 is
`f2d96c5f6893b598f652e03a82b3264267304b86b88e011286c946dc01695841`.

Target operands read the final encoded score digits at `BX+0x3E17` and
`BX+0x3EDB`, then the preceding digits from `BX+0x3E10` and `BX+0x3ED4`.
The source implements both score columns with natural `super_put()` calls,
suppresses an extra leading decimal digit below ten, and advances the remaining
seven digit columns by 16 pixels. MAP names and ReC98's decompilation are
candidate evidence only; the original source spelling is not asserted.

The maintained owner is `src/op/score/scoreput.cpp` plus
`src/op/score/scores_put.inl`. Focused cold replay verified four standalone
data-address differences at CODE offsets `0x49`, `0x60`, `0x9C`, and `0xE7`;
each is an actual OMF FIXUPP site. Both grouped `SCORE_TEXT` cold links
reproduce the complete function raw-zero, the candidate EXE/MAP hashes remain
stable, and all 804 ordered MZ relocation sites match. Focused receipt SHA-256:
`5811b7cf58ae83bca0c04b90da3529e9142debf191b7b55d78818a25157c40fd`.

The v559 OP aggregate checks all 20 registered decoded slices raw-zero in two
cold rounds. Its receipt SHA-256 is
`c28d6bf2f998a0670fcc7398f7250dcab95a1ed03e88aef9c8b30f9a033e99ae`; the
retained directory is about 1.6 MiB, with generated A/B source trees removed.
`scores_put` is `decoded-exact`, while its `units.csv` row remains
`source-present` because the packed-file offset is unknown. The aggregate
candidate image is still 69,028 bytes against the 72,256-byte target-restored
program; OP.EXE is not exact. The adjacent SCORE codec owner
`scoredat_recreate` was accepted in v561 below. Continue target-first with
`scoredat_encode` at payload `0xC627`, followed by `scoredat_decode` at `0xC57A`.

## v561 maintained OP score-file regeneration

Fresh target review closes `scoredat_recreate` at `1A74:1F4C`, payload
`0xC68C..0xC732` (167 bytes, SHA-256
`b5f25d0f2b5b7b1448d75000b98578cd8710ae419e2c8c079d717a014c796909`). The
contiguous body tiles 66 instructions, has ten direct internal branches, ends
in `RET`, and is followed at `0xC733` by the separately accepted high-score
loader. The target initializes ten records in `hi`: score digits to `0xA0`,
place zero's digit slot 5 to `0xA1`, later slot 4 values from `0xA9` down to
`0xA1`, cleared byte `0x19`, stage `0xA5 - floor(place / 2)`, eight `0xC4`
name cells, and a zero terminator. It then creates `GENSOU.SCR`, writes ten
`0xC4`-byte encoded `hi` sections, and decodes each section after writing.

The target instruction stream passes `DS:1342` to the file-create routine,
and target bytes at MZ load-module payload `0x10682` contain `GENSOU.SCR\0`.
The pinned candidate MAP's DGROUP entry `0F34:1342` corroborates the segment
mapping; it is not independent target or original-source provenance.

Maintained source is `src/op/score/scoregen.cpp` plus
`src/op/score/scoregen.inl`. Standalone TC86 CODE differs only at the two
near-call displacement words `0x87` and `0x96`, both verified as OMF FIXUPP
sites for the internal encode/decode calls. Both grouped cold links reproduce
the complete 167-byte target function raw-zero, the candidate EXE/MAP, and all
804 ordered MZ relocation sites. Focused receipt SHA-256:
`50546d64fcc7869a9826d05c9d4c5df2c8fe1c1f8caf26c12198693f3540d702`.

The v561 OP aggregate checks all 21 registered decoded slices raw-zero in two
cold rounds. Its receipt SHA-256 is
`4b83f9b0a05f0697e2e1b170e869c509a8b89deef95871307ab6148ebb464a36`; A/B source
trees were removed, leaving a 1.7 MiB receipt/log directory. The unit remains
`source-present` because the DIET-packed file offset is unknown; decoded
function state is `decoded-exact`. The candidate image remains 69,028 bytes
versus the 72,256-byte target-restored image, so packed OP and whole-EXE exactness
remain unclaimed. Next target-first owners are `scoredat_encode` at `0xC627`
and `scoredat_decode` at `0xC57A`.
