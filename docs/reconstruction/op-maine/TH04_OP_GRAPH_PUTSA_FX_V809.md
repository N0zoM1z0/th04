# OP font-effects renderer, v809

The attested OP target MAP assigns `th04/grppsafx.asm` two contributions:
`SHARED` code at `0DA1:04A4` (decoded payload `0xDEB4`, `0x15A` bytes) and
`DGROUP:_DATA` at `0F34:0A00` (decoded payload `0xFD40`, `0x40` bytes).
Neither contribution overlaps an MZ relocation site. The function and its
tables must be compared together because the renderer patches its own call
displacements and spacing/mask operands from those tables.

Target disassembly confirms `GRAPH_PUTSA_FX` from `04A4..05CE` (`0x12B`
bytes). Its `RETF 0Ah` at `0599` is followed by a reachable halfwidth path
through `05CE`, so that branch is still part of the function. The `05CF`
NOP is source-owned alignment. Internal glyph-weight helpers occupy
`05D0..05FD`; the Ghidra entry at `05DD..05ED` is a near bold-weight helper
with a `RETN`, reached by two calls and by fallthrough from the black-weight
helper. It is a label inside the assembler owner, not an independent source
translation unit.

The maintained `src/shared/hardware/graph_putsa_fx.asm` is a bounded
original-style TASM candidate. Its starting algorithm came from pinned
ReC98 material, then its PC-98/GRCG constants and macros were localized so
product source has no other-game or library include path. Historical
original-source spelling remains open. The v809 OP-only probe assembled
this source in two isolated worktrees with pinned TASM32 5.0 and linked it
against the retained OP scaffold. Both complete linked program images agree
with the scaffold controls; all 804 ordered relocations agree. Both code
contributions and both data contributions have zero raw differences against
the hash-attested v228 OP restore. Receipt:
`.analysis/reconstruction/probes/v809-op-grppsafx-001/receipt.json`.

Replay:

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_th04_op_maine_shared_asm.py \
  --module grppsafx --output-dir .analysis/reconstruction/probes/NEW-OP-GRPP-SAFX
```

The decoded code and data owners are `source-present`; both listed function
boundaries are reviewed. Their original packed-file offsets are unknown, so
the result does not claim whole OP.EXE exactness or add authored C/C++
function credit.

## MAINE owner and shared source, v813

The unchanged source moved from `src/op/hardware/` to `src/shared/hardware/`
after MAINE target review. MAINE independently owns `0x15A` bytes of
`SHARED` code at `0CC7:058C` (decoded `0xD1FC`) and `0x40` bytes of
`DGROUP:_DATA` at `0E53:05C0` (decoded `0xEAF0`). Its FAR renderer body is
`058C..06B6`; `06B7` is alignment. The internal bold-weight helper is
`06C5..06D5` and ends `RETN`.

The v813 replay assembled the shared source and linked both OP and MAINE in
isolated A/B rounds. Both artifacts retain zero raw differences for their
complete code and data contributions and preserve their own ordered
relocations (804 OP, 559 MAINE). This also revalidates OP after the path
move. Receipt:
`.analysis/reconstruction/probes/v813-op-maine-grppsafx-001/receipt.json`.
MAINE's two listed function boundaries are reviewed; both decoded module
extents are `source-present`. Their packed-file offsets remain unknown.
