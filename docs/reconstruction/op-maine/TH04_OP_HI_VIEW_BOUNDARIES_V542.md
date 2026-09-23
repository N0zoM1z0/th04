# OP hi_view physical boundary correction (v542)

This packet reviews the five OP.EXE SCORE functions after `scores_put`, using
the pinned OP target and its decoded MZ load module. The v489 OP candidate and
MAP are corroboration, not the authority for target function extent or source
authenticity.

| Function | Target payload extent | Size | Segment:offset |
| --- | --- | ---: | --- |
| `stage_put` | `0xC8A5..0xC8F4` | `0x50` | `1A74:2165` |
| `place_put` | `0xC8F5..0xCA19` | `0x125` | `1A74:21B5` |
| `rank_render` | `0xCA1A..0xCA93` | `0x7A` | `1A74:22DA` |
| `regist_view_menu` | `0xCA94..0xCBE2` | `0x14F` | `1A74:2354` |
| `cleardata_and_regist_view_sprite` | `0xCBE3..0xCC96` | `0xB4` | `1A74:24A3` |

The important correction is `rank_render`. Ghidra's exported body ends at
`0xCA55` and reports only `0x3C` bytes. The target's instruction at `0xCA54`
is `JMP 0xCA5B`, into the supposedly unclaimed suffix. Its loop branches
back from `0xCA5E` to `0xCA56`, and the complete instruction stream ends at
`RET 0xCA93`; the next Ghidra/MAP entry begins at `0xCA94`. Thus the
`0xCA56..0xCA93` interval is reachable function code, not padding or data.
The other four Ghidra bodies already match their complete target extents.

The replay checks the target-restored MZ and OP-local candidate identities,
Ghidra inventory and analysis-image identities, all five target body hashes,
complete 16-bit instruction tiling, aligned internal direct branches, terminal
returns, next-entry adjacency, available candidate MAP publics, and raw-equal OP-local
v489 candidate slices. Pinned ReC98 history separately introduces all five
logical functions under explicit `[Decompilation]` subjects. Those source
files remain candidate material even though their linked bytes match.
The v489 candidate MAP lists `cleardata_and_regist_view_sprite()` at
`0A74:24A3`, and `main_cdg_load()` at the next `0A74:2557` entry. This
corroborates the target-reviewed physical extent, but not original naming or
source provenance. The earlier "no own MAP public" statement was incorrect.
The v489 MAP names the grouped physical SCORE producer `th04/scall.cpp`;
`hi_view.cpp` is a logical included component. The boundary ledger's older
`map_module=th04/hi_view.cpp` field describes its original candidate MAP
snapshot, not the v489 physical object. Neither candidate layout establishes
original authoring provenance.

Replay with a new output directory:

```bash
python3 scripts/probes/probe_th04_op_hi_view_boundaries.py \
  --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME
```

Accepted receipt: `.analysis/reconstruction/probes/v542-op-hi-view-boundaries-003/receipt.json`,
SHA-256 `f4540de96968d62068c2fae201a206506e24b38de858aece1b76691ef2cc80f9`.

Ledger effect: five OP boundary rows move from corroborated to reviewed;
`rank_render` expands from the provisional Ghidra `0x3C` body to its target
`0x7A` extent. All five retain `candidate-cpp` and `unreviewed` acceptance.
No source-present or exact claim is made, and no MAINE/ZUN claim is inferred.

## v545 maintained stage renderer acceptance

The first bounded OP-specific high-score source owner is now
`src/op/score/stage.cpp`, with an included semantic body in `stage_put.inl`.
The descriptive `stage_put` spelling is not an original-name claim. No target
byte array, fake return, or target-derived assembly is used.

Fresh OP target disassembly and the attested Ghidra inventory agree on
`1A74:2165`, payload `0xC8A5..0xC8F4`, 80 contiguous bytes ending `RET 6`.
Two direct branches stay inside the function, the next entry starts `0xC8F5`,
and the target encodes the expected shadow/stage gaiji calls and `0xFF`/`0xEF`
selection. The v489 candidate MAP and grouped SCORE_TEXT object corroborate
the physical placement, not source provenance.

Run `python3 scripts/probes/replay_th04_op_stage_put.py --output-dir
.analysis/reconstruction/probes/v545-op-stage-put-001`. Two cold rounds compile
the maintained TU independently to 80-byte CODE SHA-256
`aa1f738c16605d93e1022e3d6a31ee20c320d5c1762666ee3bb272fd1fe3ce3c`,
then compile the same bounded body inside the grouped OP SCORE_TEXT producer.
The complete linked function has zero target differences, SHA-256
`c082747d5014d29b84ada4662b93dc0a11b6b22a6ce7cb44e798429e2960b363`.
All 804 target-ordered relocations match; the whole candidate EXE and MAP
remain v489-identical. Focused receipt SHA-256:
`1cc99d5ef293f37c756481f6d81ee70ceacd861e37a7bc7e245ac616eede12e5`.
The full OP decoded-function wrapper passes all 14 registered slices; receipt
SHA-256 `a07221c7a72ff713c94cbff71cd3a28e0c26fc9f560170b5f71a1d54d8d8b132`.

Only this decoded function is accepted. The remaining v542 hi_view functions
still have decompilation provenance, and the DIET-packed OP.EXE has no honest
file offset for this body. No complete SCORE TU or whole OP product exactness
is asserted.

## v552 maintained two-column row renderer

The next OP SCORE_TEXT function is target-reviewed at `1A74:21B5`, decoded
payload `0xC8F5..0xCA19`, exactly `0x125` (293) bytes ending `RET 2` before
`rank_render` at `0xCA1A`. Fresh target disassembly tiles the attested
Ghidra extent with 117 instructions and two internal direct branches. Its
two score columns read names at `+4`, stages at `+176`, and sections spaced
196 bytes apart. The name `place_put` is descriptive, not original-source
proof; the earlier ReC98 candidate remains explicitly decompilation-derived.

Maintained natural C++ is in `src/op/score/place.cpp` and bounded
`place_put.inl`, with artifact-local, offset-checked score layout in
`scoredat.hpp`. A reusable OP SCORE harness pins the v489 candidate inputs,
source closure, target extent, standalone OMF, grouped SCORE_TEXT, MAP,
complete linked function, and ordered relocations. In the standalone object,
16 differing bytes lie exclusively within five near-call and five data-address
OMF FIXUPP words. The independent harness verifies every differing position,
the relevant instruction forms, and the presence of each fixup; it does not
normalize away any linked mismatch. Both grouped objects are identical to
v489 and both linked 293-byte functions are raw-zero against target SHA-256
`79322cc0563bb1c1753393eb704c5869f07563fc658da33c71c217e66b865c71`.
The full candidate EXE/MAP and all 804 ordered relocations remain unchanged.

Replay with `python3 scripts/probes/replay_th04_op_place_put.py --output-dir
.analysis/reconstruction/probes/<new-id>`; retained focused receipt
`.analysis/reconstruction/probes/v552-op-place-put-002/receipt.json` has SHA-256
`e5ce18c639239fe478f3b0b6c330ec655b78862e38271cb919553dd338246d39`.
The first scratch probe failed because it allowed near-call fixups only; its
four `ADD AX,imm16` and one indexed-load data fixups were subsequently
attested and whitelisted at exact locations. No packed-file, complete SCORE
TU, or whole OP exactness is asserted. The next `rank_render` owner retains
the v542 Ghidra-tail correction and requires that special boundary review
when reconstructed.
The full cold OP decoded-function wrapper passes all 15 registered slices;
retained aggregate receipt SHA-256 is
`7e796a3c2f833e6f8cb804d92687c0bf4a8b3c579db5d63b2edc9393a01969d8`.

## v553 maintained rank renderer with reachable Ghidra tail

The OP SCORE_TEXT function at `1A74:22DA` is decoded payload
`0xCA1A..0xCA93`, `0x7A` (122) bytes ending `RET` before `regist_view_menu`
at `0xCA94`. The live Ghidra inventory still reports only the 60-byte prefix
`0xCA1A..0xCA55`. Target bytes at `0xCA54` encode `JMP 0xCA5B`; the tail is
reachable, contains the loop and rank-glyph calls, and ends at `0xCA93`.
Fresh target disassembly tiles all 122 bytes with 47 instructions and two
internal direct branches. The new harness permits this prefix discrepancy
only for the pinned `rank_render` extent and explicitly checks the jump into
the tail. The name is descriptive, not original-source proof.

Maintained natural C++ is in `src/op/score/rank.cpp` and bounded
`rank_render.inl`. Two pinned TC86 4.02 standalone CODE bodies differ from
the grouped owner only at three near `place_put` call displacements and two
absolute rank-global loads; all five words have OMF FIXUPP entries. The
grouped SCORE_TEXT object, full candidate EXE/MAP, and 804 ordered
relocations remain v489-identical. Both complete linked functions are
raw-zero against target SHA-256
`42f01ff3f1a4f34d2f5b06cce22e05d6b617e3491f0dfa7b8ee6d72bc9be8a1e`.

Replay with `python3 scripts/probes/replay_th04_op_rank_render.py --output-dir
.analysis/reconstruction/probes/<new-id>`; retained focused receipt
`.analysis/reconstruction/probes/v553-op-rank-render-002/receipt.json` has
SHA-256 `3dcfc70275402a7590faf55a58c81a421b7c9c57d989e1e5d0935f25024518aa`.
The first scratch probe failed its strict standalone gate until the two
rank-global `MOV AL,[imm16]` fixups were independently located in OMF. This
accepts the whole target-reviewed function, not the packed file, complete
SCORE TU, or following registration menu.
The full cold OP decoded-function wrapper passes all 16 registered slices;
retained aggregate receipt SHA-256 is
`b29eb9a03e836c630ddc8b91d388c799de74b2eb27834e616db4962473321ff8`.

## v554 maintained clear-state and sprite initializer

OP SCORE_TEXT at `1A74:24A3`, decoded payload `0xCBE3..0xCC96`, is a
180-byte function ending `RET` before OP_TITLE_TEXT begins at `0xCC97`.
The pinned target and Ghidra inventory agree on the complete extent. Fresh
16-bit disassembly tiles 60 instructions with six aligned internal branches.
The function loops over the five ranks, normalizes both play-character clear
flags to values at most three, accumulates extra-unlock state, then restores
the resident rank and loads two BFNT sprite resources. These are target
observations; the descriptive function name is not original-source proof.

Maintained natural C++ is `src/op/score/clear.cpp` with a bounded
`clear_sprites_load.inl`. Two pinned TC86 4.02 standalone compilations emit
the same 180-byte CODE shape as the grouped SCORE_TEXT owner outside one
near-call and 25 data-address words. Every differing word has an OMF FIXUPP
entry; no other CODE byte differs. The grouped object, full linked OP
EXE/MAP, and all 804 ordered relocations stay v489-identical. Both complete
linked functions are raw-zero against target SHA-256
`2093f45b6f1e8fda9ef6004999ba3dedbf24c6ec12134c11262ad8dd455b633c`.

Replay with `python3 scripts/probes/replay_th04_op_clear_sprites.py
--output-dir .analysis/reconstruction/probes/<new-id>`. Retained corrected
focused receipt
`.analysis/reconstruction/probes/v555-op-clear-sprites-map-public-002/receipt.json`
has SHA-256
`cffa9fcd2bf2ef051880a3f27e3d5f09c2d577907016983166f8215787cb3da1`.
The first strict probe rejected standalone relocation differences as designed;
the later probe records only explicitly located OMF fixup words. This accepts
the reviewed decoded function, not the packed file, complete SCORE TU, or
the preceding registration menu.
The full cold OP decoded-function wrapper passes all 17 registered slices;
retained aggregate receipt SHA-256 is
`444800e04108ec7cba997b589cf8c3f194022cd14ecfd97844c27d7ce83a6c60`.

## v555 candidate-MAP public correction

The earlier v554 prose incorrectly called this function MAP-private. The
attested v489 candidate MAP lists its public at `0A74:24A3`, followed by
`main_cdg_load()` at `0A74:2557`; the older v542 boundary probe already
required both entries. The focused harness now checks those exact address/name
strings and records them separately from the target boundary in its receipt.
The corrected two-round focused replay leaves the 180-byte raw-zero function,
grouped SCORE_TEXT, full candidate EXE/MAP, and 804 ordered relocations
unchanged. Candidate MAP symbols corroborate layout only; they do not prove
original names or source authenticity.
The corrected full OP wrapper rechecks all 17 accepted decoded slices with
zero raw differences. Its retained receipt is
`.analysis/reconstruction/probes/v555-op-map-correction-aggregate-001/receipt.json`
(SHA-256 `f5808754a501d658ef4ebf3b9dfdb07f24c88a79e2a2c52c165868898cf38f7b`);
the candidate-image and function-slice hashes are unchanged from the v554
compact replay.

## v556 maintained registration-view menu

OP SCORE_TEXT at `1A74:2354`, decoded payload `0xCA94..0xCBE2`, is a
335-byte function ending `RET` immediately before the v554 clear-state owner
at `0xCBE3`. The pinned target and Ghidra inventory agree on its full extent;
99 target instructions tile it with ten aligned internal direct branches.
The target tests OK twice in its exit condition, checks left/right against
rank bounds, then fades and redraws the main-menu background. These oddities
are preserved as observed behavior, not cleaned up in the exact source.

Maintained natural C++ is `src/op/score/menu.cpp` with bounded
`regist_view_menu.inl`. Two pinned TC86 4.02 standalone compilations emit a
335-byte SCORE_TEXT body. All 24 bytes differing from the grouped owner lie
within five near-call and nine data-address OMF FIXUPP words; no non-fixup
CODE byte differs. The grouped SCORE_TEXT object, complete linked OP EXE/MAP,
and all 804 ordered relocations remain v489-identical. Both complete linked
functions are raw-zero against target SHA-256
`907bc127317f2fb9e5fc10d14030f13051b9cee40a9d7fd66a90cd9dc6c16355`.
The v489 candidate MAP publics at `0A74:2354` and `0A74:24A3` corroborate
placement only, not original names or source provenance.

Replay with `python3 scripts/probes/replay_th04_op_regist_view_menu.py
--output-dir .analysis/reconstruction/probes/<new-id>`. The retained focused
receipt is
`.analysis/reconstruction/probes/v556-op-regist-view-menu-003/receipt.json`
(SHA-256 `d7fdb2a1bdae98d7ab653591b40f6ba510b4571d9f4cf277fd1ce0b72b618114`).
This accepts the reviewed decoded function only; the packed OP file and
complete SCORE translation unit are not exact.
The full cold OP decoded-function wrapper passes all 18 registered slices
with zero raw differences in two rounds; the prior 14 backend candidate-image
hash sets are unchanged. Its retained receipt is
`.analysis/reconstruction/probes/v556-op-regist-aggregate-001/receipt.json`
(SHA-256 `130b4252f471accf0175dfd37e818d18f41afe10f6945b4e3ed2a2134fb4777a`).
