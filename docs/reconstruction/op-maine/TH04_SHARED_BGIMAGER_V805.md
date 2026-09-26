# Shared BGIMAGE rectangle renderer, v805

`src/shared/hardware/bgimager.asm` is a maintained original-style TASM
candidate for `BGIMAGE_PUT_RECT_16`. It is distinct from the already
maintained C++ `bgimage_snap`, `bgimage_put`, and `bgimage_free` source. The
starting assembly came from the pinned ReC98 candidate; its historical
authorship remains unproved. This replay reattests the complete locally
maintained source against each TH04 target independently.

| Artifact | Decoded load-module extent | TLINK `SHARED` start | Result |
| --- | --- | --- | --- |
| OP.EXE | `0xE4F8..0xE579` | `0DA1:0AE8`, `0x82` | A/B raw zero |
| MAINE.EXE | `0xD6F6..0xD777` | `0CC7:0A86`, `0x82` | A/B raw zero |

The Ghidra function body is 0x81 bytes; one final byte belongs to assembler
alignment. The complete 0x82-byte module has no overlapping relocation site.
The probe cold-assembles the checked-in source with pinned TASM32 5.0 and
links independent OP/MAINE worktrees. Both full program images remain
identical to the retained link scaffolds, all ordered relocations match the
hash-attested v228 target restores, and every module byte matches each
target. The local PC-98 plane constants replace a ReC98 include; no copied
target byte array, object patch, or forced padding is used.

Receipt:
`.analysis/reconstruction/probes/v805-op-maine-bgimager-001/receipt.json`
(SHA-256 `f8f556243bc8546a1c54c166921f33ae83fd07619603e82bb88b914b0a4638c0`).

Replay:

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_th04_op_maine_shared_asm.py \
  --module bgimager --output-dir .analysis/reconstruction/probes/NEW-BGIMAGER-REPLAY
```

The ledger records decoded `source-present` module units. The packed-file
offsets and standalone TH04 product build are still open; this ASM module
does not affect the authored C/C++ function denominator.
