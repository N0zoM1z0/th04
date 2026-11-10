# TH04 MAINE regist_menu current-v489 compiler frontier (v831)

> **Status:** Historical negative checkpoint, superseded by v835. The v831 split remains valid for the source forms tested, but current MAINE is 72/72 and `regist_menu()` is accepted from ordinary semantic C++.

## Result

`regist_menu()` remains blocked at payload `0xC814`, size `0x39C` / 924 bytes.

v831 revalidates the old v483/v730 compiler frontier against the current
retained v489 SCORE producer instead of relying on the pruned v478 worktree.
The target-exact `optimization_barrier()` form remains diagnostic only:
`decomp.hpp` explicitly defines it as an empty inline function used to prevent
jump optimizations.

## Four-byte residual

The target zero-test at function-relative `+0x345` uses direct-memory
`CMP [key_det],0`, followed by `JZ` and a redundant unconditional `JMP`.
Every other byte in the 924-byte function is already explained.

Two cold source-family controls now make the compiler split explicit:

- Natural single-case `switch(key_det)` preserves the 924-byte function size
  and target `JZ + JMP` topology, but emits `MOV AX,[key_det] / OR AX,AX`.
  Exactly four function bytes differ: `0x345`, `0x346`, `0x348`, `0x349`.
- Natural direct `if/goto` emits the target-style direct-memory `CMP`, but
  TC4.02 removes the redundant JMP. SCORE_TEXT shrinks from `0xB30` to
  `0xB2E`, shifting later code.

Additional current-v489 experiments with one-shot loop `break`/`continue`,
multiple named labels, double-goto forms, and ternary forms either collapse
the same JMP or expand the function.

TC4J `-B` output confirms this is a CFG block-preservation problem, not an
unknown opcode selection problem.

## Evidence

Replay:

```sh
python3 scripts/probes/probe_th04_maine_regist_frontier_v831.py \
  --output-dir .analysis/reconstruction/probes/v831-maine-regist-frontier-001
```

Archived


SHA-256:
`123633de7f6a3a9f6d222ca9bb739fa55e66cf3e8397733c065b94ae9045ae66`

No exact credit is granted. Resume this boss only with a materially new
source-origin or compiler mechanism; do not repeat the same switch/if/goto/
one-shot-loop matrix.
