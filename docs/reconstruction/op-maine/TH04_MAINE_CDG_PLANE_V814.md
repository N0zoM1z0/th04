# MAINE CDG plane renderer, v814

The attested MAINE target MAP assigns `CDG_PUT_PLANE` one `0x9A`-byte
`SHARED` contribution at `0CC7:0408`, decoded payload `0xD078`. Target
disassembly closes a single FAR body at `0CC7:04A1` with `RETF 8`; the next
MAP owner begins at `04A2`. No MZ relocation overlaps the contribution.

`src/maine/formats/cdg_put_plane.asm` is a maintained original-style TASM
candidate for this bounded renderer. Its starting algorithm came from pinned
ReC98 material; the CDG slot layout and PC-98 VRAM constants are declared
locally. Historical source spelling remains unknown. The renderer shifts
CDG plane words across unaligned VRAM word boundaries and patches the first
mask and width operands in its own code.

The MAINE-only v814 probe assembled this source in isolated A/B worktrees
with pinned TASM32 5.0 and linked it against the retained MAINE scaffold.
Both complete linked program images agree with the scaffold controls; all
559 ordered relocations agree. Both complete `0x9A`-byte contributions have
zero raw differences against the hash-attested v228 MAINE restore. Receipt:
`.analysis/reconstruction/probes/v814-maine-cdg-plane-001/receipt.json`.

Replay:

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_th04_op_maine_shared_asm.py \
  --module cdg_p_pl --artifact maine \
  --output-dir .analysis/reconstruction/probes/NEW-MAINE-CDG-PLANE
```

This is a decoded `source-present` original-ASM unit with a reviewed
function boundary. Its original packed-file offset is unknown, so it does
not change the authored C/C++ function count or claim whole MAINE.EXE
exactness.
