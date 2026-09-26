# Shared PC-98 input sensing, v802

The maintained `src/shared/hardware/input_s.asm` provides the same input
sensing TASM unit for MAIN, OP, and MAINE. This unit reads PC-98 BIOS key
bitmap addresses, calls joystick sensing when present, and writes the TH04
input flags. It uses local TH04 definitions for the exact values it needs;
the earlier `platform/` and ReC98 include paths are gone.

| Artifact | Load-module start | TLINK `SHARED` start | Full contribution |
| --- | --- | --- | ---: |
| MAIN.EXE | `0x1379C` (file `0x14F9C`) | `130E:06BC` | `0x10A` |
| OP.EXE | `0xE1DC` | `0DA1:07CC` | `0x10A` |
| MAINE.EXE | `0xD48A` | `0CC7:081A` | `0x10A` |

The contribution contains `input_reset_sense` (8 bytes), `input_sense`
(0x101 bytes), and one final function-external alignment byte. OP and MAINE
each pass independent A/B TASM/TLINK cold links against their own
hash-attested decoded target: the entire 0x10A-byte contribution has zero
raw differences, all ordered artifact relocations agree, and the single
module-overlapping relocation is preserved. MAIN passes the accepted-unit
complete cold replay after the source move. These are three artifact-local
claims; source identity in one artifact does not transfer raw equality to
another.

The packed OP/MAINE original-file offsets and standalone product builds
remain open. Their ledger state is decoded `source-present`, not file-backed
`exact`, and this original-ASM work does not alter authored C/C++ function
counts.

The OP/MAINE A/B receipt is
`.analysis/reconstruction/probes/v804-op-maine-input-s-shared-001/receipt.json`
(SHA-256 `e83afdfe6634f94d121ef15d683375b03b492d5ead6567705031bbbfaf999c17`).
The MAIN v803 accepted-unit replay passes with receipt SHA-256
`61a3a4616adb60bdb05f8a2d00e61671b63f034ff33bd30247122ad09a7547c0`.

Replay:

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_th04_op_maine_shared_asm.py \
  --module input_s --output-dir .analysis/reconstruction/probes/NEW-INPUT-S-REPLAY
taskset -c 0,1 nice -n 10 python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-module-th04-input-s-asm-1379c --run-id NEW-MAIN-INPUT-S-REPLAY
```
