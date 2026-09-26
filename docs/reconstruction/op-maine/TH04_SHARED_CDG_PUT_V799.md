# Shared CDG renderer ownership, v799

`src/shared/formats/cdg_put.asm` is the maintained original-ASM translation
unit for `CDG_PUT_8` in MAIN, OP, and MAINE. It retains the TH04 target's
self-modifying color-segment load and PC-98 GRCG/VRAM operations. The former
ReC98 `pc98.inc`, MASTER macro, and TH03 CDG includes are replaced by the
bounded TH04 values and definitions used by this unit. No portable semantic
rewrite is part of this claim.

| Artifact | Decoded target extent | TLINK `SHARED` start | Full module | Raw result |
| --- | --- | --- | ---: | --- |
| MAIN.EXE | `0x13580..0x1361D` (file `0x14D80..0x14E1D`) | `130E:04A0` | `0x9E` | MAIN accepted-unit cold replay |
| OP.EXE | `0xE00E..0xE0AB` | `0DA1:05FE` | `0x9E` | 0 differences in A/B cold links |
| MAINE.EXE | `0xD356..0xD3F3` | `0CC7:06E6` | `0x9E` | 0 differences in A/B cold links |

The complete module includes one final alignment byte after the 0x9D-byte
Ghidra `CDG_PUT_8` function body. These targets contain no relocation site
within the contribution. The OP/MAINE probe checks all ordered relocations
for each linked artifact and exact identity with the retained full candidate
program, while comparing the complete module to independent, hash-attested
decoded targets. The candidate build supplies link scaffolding only.
The v811 OP target-first boundary review confirms `0DA1:05FE..069A` ends
`RETF 6` and assigns the `069B` NOP to module alignment; OP's function
boundary is now reviewed.
The v815 MAINE review independently confirms its `0CC7:06E6..0782` FAR
body and separate `0783` alignment NOP; MAINE's boundary is now reviewed.

Focused replay:

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_th04_op_maine_cdg_load.py \
  --module cdg_put --output-dir .analysis/reconstruction/probes/NEW-CDG-PUT-REPLAY
taskset -c 0,1 nice -n 10 python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-module-th04-cdg-put-asm-13580 --run-id NEW-MAIN-CDG-PUT-REPLAY
```

The OP and MAINE rows remain decoded `source-present` units. Their DIET
packed-file offsets and complete TH04 standalone product builds are not
established, and this original-ASM module does not change the authored C/C++
function denominator.

The OP/MAINE A/B receipt is
`.analysis/reconstruction/probes/v799-op-maine-cdg-put-002/receipt.json`
(SHA-256 `735d59e171b1ab4e98e7c8351505c0e6c63bc4a60c0acd22dfabe73d80f3f6be`).
The MAIN v800 accepted-unit replay also passes with receipt SHA-256
`134599553ac15921071abd6b75a6ae950d2f0187beb5f6f6bce836fb3d9afe58`.
