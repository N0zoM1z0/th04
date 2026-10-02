# TH04 current handoff

Updated 2026-10-02. The active goal is a standalone PC-98 game build:
checked-in TH04 source, successful builds, and normal gameplay. Whole-build
byte equality is not required. The two remaining MAIN function exactness
cases are intentionally deferred and retain their nonexact ledger states.
ReC98 public implementations may be adapted into the owning TH04 subsystem;
no upstream exactness claim is inherited.

## Current state

| Artifact | Accepted authored functions | Native build/runtime |
| --- | ---: | --- |
| OP | 93/93 | Complete TH04-only link; rebuilt OP now enters rebuilt MAIN demo |
| MAIN | 493/495 | Complete TH04-only link; stage-0 background plane check passes |
| MAINE | 72/72 | Complete TH04-only link; score/ending runtime pending |
| ZUN | 3/3 | Source-only cold packed build; rebuilt GAME.BAT startup reaches OP and MAIN |

These function counts describe the historical reconstruction acceptance plane,
not whole executable or native runtime completion. Live counts:
`python3 scripts/status.py`. Targets remain `candidate-local-attested`.

MAIN now compiles all 193 C/C++ roots, 154 ASM roots, eight state owners
and four generated sprite owners without `masters.lib`. The v1147 cached link
and v1148 fresh link both have zero compiler/assembler failures, linker errors
or warnings. Twelve bounded ASM owners use local declaration contexts;
no build-time Git-history extraction remains.

Stage-0 graphics checks now pass: the source MPN cache was correct, but EGC
mode 2300h broadcast its blue plane. The pinned original uses 3100h at
MAIN MAI_TEXT 0AAF:212C (file E41Ch). Using 3100h makes all 600 rendered tiles
match their complete four-plane source images, with zero blue-plane broadcasts.
Native HUD data also needs four rank strings and a NUL-terminated blank HP bar.
All four uninstrumented products now build through `scripts/build.py`. ZUN
parts no longer depend on an old decoded target directory or `masters.lib`.
The combined startup replay reaches a progressing MAIN demo. Before the native
OP palette block was freed, `execl` returned ENOMEM (8): after cleanup the
largest free DOS block was 31,100 paragraphs, but a four-paragraph OP-owned
block immediately followed its program block. Freeing that temporary palette
block before overlay allows the complete MAIN to start. This is runtime-observed
for demo startup, not full-game acceptance; menu glyphs and complete gameplay
rendering still need comparison.

Current replay surfaces:
- `.analysis/reconstruction/probes/product-20261002-073408-1aa3cf62-build.json`
- `.analysis/runtime/candidates/native-op-memory-v1161-20261002/run/op_handoff_memory.json`
- `.analysis/runtime/candidates/native-all-products-v1162-review-20261002/run-demo/receipt.json`
- `.analysis/runtime/candidates/native-main-graphics-v1152-20261002/run-demo/graphics.json`
- `.analysis/runtime/candidates/original-product-baseline-20261002/run-input/receipt.json`

## Build and validation

```sh
python3 scripts/preflight.py
python3 scripts/build.py
python3 scripts/prepare_product_hdi.py \
  --output-dir .analysis/runtime/candidates/NEW-game
xvfb-run -a python3 scripts/probes/run_th04_maine_diagnostic_hdi.py \
  --prepared-dir .analysis/runtime/candidates/NEW-game \
  --output-dir .analysis/runtime/candidates/NEW-game/run \
  --frame-second 95 --time-limit 1000 --stop-after-frame
python3 scripts/ci.py
git diff --check
```

Only one Borland/Wine build may run at a time. `--only main` selects one product;
`--main-cpp-cache PATH`, `--op-cache PATH`, and `--maine-cache PATH` reuse
objects only after input/dependency/toolchain identity checks. `prepare_product_hdi.py
--original` creates an original-executable baseline. Runtime checkpoints use
`--checkpoint-second SECOND`; held keys use `--input-event down:z@SECOND` and
`--input-event up:z@SECOND`. Private MAIN `--graphics-trace` writes MPN and VRAM
checkpoints. `--audio` enables the mixer; F12+w events toggle WAV capture on Linux.
Always use new disposable output paths and preserve original data.

## Next work

1. Validate playable input through the rebuilt menu and normal-game handoff.
2. Compare menu/HUD rendering, shots, bombs, stages, sound and exit.
3. Run all four rebuilt artifacts together, including MAINE and score/config
   persistence. Test actual input and state progression, not one screenshot.
4. Keep the simple build/run entrypoints and concise current handoff up to date.

## Navigation

- [Architecture](ARCHITECTURE.md): artifact/ABI and source ownership.
- [Runtime](RUNTIME.md): pinned emulator and image setup.
- [Progress](PROGRESS.md): generated historical function acceptance.
- [Evidence index](reconstruction/README.md): focused historical investigations.
- `config/evidence.csv` / `config/knowledge.csv`: durable receipts and findings.

Historical checkpoints remain in Git and the evidence ledgers. Do not use an
old note's missing-header count or blocker as a current work queue. The product
include audit currently has zero compatibility forwarders and forbidden edges.
