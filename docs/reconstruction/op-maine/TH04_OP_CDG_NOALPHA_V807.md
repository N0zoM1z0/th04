# OP CDG no-alpha renderer, v807

The attested OP target has `CDG_PUT_NOALPHA_8` at decoded payload `0xE176`,
map `0DA1:0766`. Ghidra closes one contiguous `0x65`-byte FAR body; the
following `0x90` is the source-owned `EVEN` alignment byte. The complete
`SHARED` contribution is `0x66` bytes and has no overlapping MZ relocation.

The maintained symbolic source is
`src/shared/formats/cdg_put_noalpha_8.asm`. A MAIN file-backed exact replay
previously established the same source owner independently; that acceptance
does not transfer to OP. The assembler implementation is justified by the
target's segment-stack and `REP MOVSD` copy structure and the recorded legal
TC4J natural-source negative probe. Historical original-source spelling is
unknown.

The OP-only v807 probe assembled the source in two isolated worktrees with
pinned TASM32 5.0 and linked it with the retained OP scaffold. Both complete
linked program images equal their controls; all 804 ordered relocations agree.
Both complete `0x66`-byte contributions have zero raw differences against the
hash-attested v228 OP target restore. The `_cdg_slots` operand is resolved by
an OMF external fixup to the OP-local value. Receipt:
`.analysis/reconstruction/probes/v807-op-cdg-noalpha-001/receipt.json`.

Replay:

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_th04_op_maine_shared_asm.py \
  --module cdg_p_na --output-dir .analysis/reconstruction/probes/NEW-OP-CDG-NOALPHA
```

This is an OP decoded `source-present` original-ASM unit with a reviewed
function boundary. Its original packed-file offset is unknown, so this is
not a whole OP.EXE or packed-file exact claim. The authored C/C++ function
count remains 85/93 exact.
