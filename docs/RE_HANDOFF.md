# TH04 current handoff

Updated 2026-10-02. The active goal is a standalone PC-98 game: checked-in
TH04 source, successful builds, and normal gameplay. Native whole-build byte
equality is not required. The two remaining MAIN exactness cases are deferred
and retain their nonexact states. ReC98 implementations are adaptation inputs;
upstream exactness claims are not inherited. Current phase: runtime integration.

## Current state

| Artifact | Accepted authored functions | Native build/runtime |
| --- | ---: | --- |
| OP | 93/93 | Complete standalone build; enters MAIN and receives MAINE return; menu labels still differ from original |
| MAIN | 493/495 | Complete standalone build; stage-0 graphics, audio and private movement/shot/Bomb/death checks pass |
| MAINE | 72/72 | Complete standalone build; uninstrumented score/name registration saves 39,300 and returns to OP |
| ZUN | 3/3 | Source-only cold packed build; four-product GAME.BAT startup passes |

These counts describe historical function acceptance, not whole executable or
normal-game completion. `python3 scripts/status.py` reports the live ledgers.
Targets remain `candidate-local-attested`. Product include checks have zero
compatibility forwarders and forbidden ReC98 edges.

The full native build compiles 193 MAIN C/C++ roots, 154 ASM roots, eight state
owners and four generated sprite owners without `masters.lib`. All four products
build through `scripts/build.py`. A fresh four-product build and subsequent
source/dependency-validated MAIN/OP/MAINE relink pass; the final MAINE matches its
fresh build. ZUN is cold-deterministic. Current inventory:
`.analysis/reconstruction/probes/product-20261002-090618-400c84b6-build.json`.

Verified integration fixes:
- MAIN EGC tile copy uses 3100h, observed at MAI_TEXT 0AAF:212C (file E41Ch).
  All 600 initial tiles match their four-plane source images. HUD data includes
  four rank strings and a NUL-terminated blank HP bar.
- OP frees its temporary palette DOS block before overlay. The former four-
  paragraph block split free memory and made `execl` return ENOMEM=8.
- MAINE's C++ code group changed the CS frame for SHARED assembly. Independent
  native IRQ/PAR and self-modifying renderer segments repair four vectors and
  38 CS-relative operands. The build now checks these destinations, including
  observed direct-call CS frames. The default renderer branch retains its
  previous complete link-relevant OMF output in cold compiler comparisons.

The uninstrumented v1178 normal route reaches stage 0, Game Over, Continue,
MAINE name entry, score persistence and the OP title menu. Ten saved-score
section checksums and digit ranges pass. Private v1176 separately records all
MAINE initialization call completions. Pinned originals under the same emulator
also show pale score colors and previous CONTINUE/stage-image remnants; do not
attribute these to reconstruction without another control. Native OP menu labels
separately differ from original. Candidate `src/op/main/menu.cpp` uses colored
`cdg_put_8` for labels where the upstream composition uses `cdg_put_nocolors_8`;
OP target attestation is required before correcting that native composition.

Current runtime receipts:
- `.analysis/runtime/candidates/native-four-cs-v1178-20261002/run/receipt.json`
- `.analysis/runtime/candidates/native-four-cs-v1178-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/native-maine-render-v1176-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/original-score-baseline-v1177-20261002/run/receipt.json`
- `.analysis/runtime/candidates/native-actions-v1170-20261002/run/play-state.json`

## Build and validation

```sh
python3 scripts/preflight.py
python3 scripts/build.py
python3 scripts/prepare_product_hdi.py --output-dir .analysis/runtime/candidates/NEW-game
xvfb-run -a python3 scripts/probes/run_th04_maine_diagnostic_hdi.py \
  --prepared-dir .analysis/runtime/candidates/NEW-game \
  --output-dir .analysis/runtime/candidates/NEW-game/run \
  --frame-second 95 --time-limit 1000 --stop-after-frame
python3 scripts/ci.py
git diff --check
```

Only one Borland/Wine build may run at a time. `--only main` selects one product;
`--main-cpp-cache`, `--op-cache` and `--maine-cache` reuse only verified inputs.
`prepare_product_hdi.py --original` creates an attested original baseline;
`--lives 1 --bombs 0` sets an ordinary configuration fixture in the disposable
image. Runtime `--checkpoint-second` captures intermediate frames; held keys use
`--input-event down:z@SECOND` / `up:z@SECOND`. `--key-delay-ms 300` gives menu taps
adequate duration. Always use new output paths. Private state probes do not
replace uninstrumented runs. `inspect_th04_handoff_trace.py --require-score-saved`
checks executed-image identity and changed decoded score sections.

## Next work

1. Attest and correct the OP menu label call composition; verify options,
   Music Room, score viewing and config persistence.
2. Validate bosses, later stages, endings, Extra and character/rank variants.
3. Compare rendering/audio under another PC-98 emulator before assigning
   original-and-native shared display artifacts to source bugs.

## Navigation

- [Architecture](ARCHITECTURE.md): artifact/ABI and source ownership.
- [Runtime](RUNTIME.md): pinned emulator and image setup.
- [Progress](PROGRESS.md): historical function acceptance.
- [Evidence index](reconstruction/README.md): focused historical investigations.
- `config/evidence.csv` / `config/knowledge.csv`: durable receipts and findings.

Historical checkpoints remain in Git and the ledgers. Old missing-header counts
and blockers are not the current work queue.
