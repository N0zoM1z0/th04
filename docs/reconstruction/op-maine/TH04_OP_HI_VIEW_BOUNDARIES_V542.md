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
