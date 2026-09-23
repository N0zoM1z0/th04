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
returns, next-entry adjacency, candidate MAP publics, and raw-equal OP-local
v489 candidate slices. Pinned ReC98 history separately introduces all five
logical functions under explicit `[Decompilation]` subjects. Those source
files remain candidate material even though their linked bytes match.
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
