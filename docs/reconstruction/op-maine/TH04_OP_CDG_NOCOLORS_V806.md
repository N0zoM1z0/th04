# OP CDG alpha-only renderer, v806

The OP target has `CDG_PUT_NOCOLORS_8` at decoded payload `0xDC92`, map
`0DA1:0282`. Attested Ghidra reports one contiguous 0x51-byte FAR body. The
target ends it with `RETF 6` at `0xDCE0..0xDCE2`; a following `0x90` at
`0xDCE3` belongs to the 0x52-byte `SHARED` assembler contribution.

`src/op/formats/cdg_p_nc.asm` is a maintained original-style TASM candidate
with local TH04 CDG slot and PC-98 VRAM definitions. The starting algorithm
came from pinned ReC98 candidate material and retains its self-modifying width
load. Historical original-source provenance is open. The maintained source
contains symbolic instructions and alignment, without copied target bytes or
an inert code-generation barrier.

The OP-only v806 probe assembles this source in isolated A/B worktrees with
pinned TASM32 5.0 and links it against the retained OP scaffold. Both complete
linked program images and all 804 ordered MZ relocation entries agree with
their controls. Both 0x52-byte code contributions have zero raw differences
against the hash-attested v228 target restore. The module has no overlapping
relocation site. Receipt:
`.analysis/reconstruction/probes/v806-op-cdg-nocolors-001/receipt.json`
(SHA-256 `ff092076a2c018aeea49a0f4a7600b0eea7cf4fc658a14d09c4cc04cf4d83e48`).

Replay:

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_th04_op_maine_shared_asm.py \
  --module cdg_p_nc --output-dir .analysis/reconstruction/probes/NEW-OP-CDG-NOCOLORS
```

This is an OP decoded `source-present` original-ASM unit with a reviewed
function boundary. Its packed-file offset and historical source provenance
remain open, and it does not change the authored C/C++ function count.
