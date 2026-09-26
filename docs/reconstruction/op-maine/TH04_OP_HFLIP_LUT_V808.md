# OP horizontal-flip lookup generator, v808

The attested OP target MAP assigns `th03/hfliplut.asm` a `0x1E`-byte `SHARED`
contribution at `0DA1:0134`, decoded payload `0xDB44`. Ghidra has no
function entry there. Raw 16-bit disassembly instead shows one contiguous
body from `PUSH DI` through `RETF` at `0DA1:0151`; the next MAP owner starts
at `0152`. The body writes a 256-entry bit-reversal lookup table and has no
separate data or alignment extent.

The maintained symbolic TASM source moved without content changes from
`src/main/hardware/hflip_lut.asm` to
`src/shared/hardware/hflip_lut.asm`. MAIN's file-backed exact unit was cold
replayed after the move: raw, MAP, relocation, and size checks passed. The
OP-only v808 probe assembled and linked the shared source in two isolated
worktrees. Both complete `0x1E`-byte OP contributions have zero raw
differences against the hash-attested v228 restore; all 804 ordered OP
relocations match and none overlaps this contribution. Receipt:
`.analysis/reconstruction/probes/v808-op-hfliplut-002/receipt.json`.

Replay:

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_th04_op_maine_shared_asm.py \
  --module hfliplut --output-dir .analysis/reconstruction/probes/NEW-OP-HFLIP
```

The OP decoded module is `source-present` with a reviewed function boundary.
Its original packed-file offset remains unknown. This does not change the
authored C/C++ function count of 85/93 exact.

## MAINE owner, v812

MAINE independently preserves a `0x1E`-byte `SHARED` contribution at
`0CC7:01EC`, decoded payload `0xCE5C`. Target disassembly ends `RETF` at
`0209`; the next owner begins at `020A`. The same maintained shared source
cold-links the complete MAINE contribution with zero raw differences in two
isolated rounds and all 559 ordered relocations preserved. Receipt:
`.analysis/reconstruction/probes/v812-maine-hfliplut-001/receipt.json`.
The MAINE packed-file offset and historical source spelling remain open.
