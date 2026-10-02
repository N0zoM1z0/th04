# TH04 current handoff

Updated 2026-10-02. The active goal is a standalone PC-98 game: checked-in
TH04 source, successful builds, and normal gameplay. Native whole-build byte
equality is not required. The two remaining MAIN exactness cases are deferred
and retain their nonexact states. ReC98 implementations are adaptation inputs;
upstream exactness claims are not inherited. Current phase: runtime integration.

## Current state

| Artifact | Accepted authored functions | Native build/runtime |
| --- | ---: | --- |
| OP | 93/93 | Standalone build; normal options/Music Room/scores/DOS exit and saved config pass |
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
`.analysis/reconstruction/probes/product-20261002-092346-adc55999-build.json`.
The latest OP cold build compiles 111 C/C++ and 53 ASM roots, links without
warnings, and equals the preceding dependency-validated cached native build.

Verified integration fixes:
- MAIN EGC tile copy uses 3100h, observed at MAI_TEXT 0AAF:212C (file E41Ch).
  All 600 initial tiles match their four-plane source images. HUD data includes
  four rank strings and a NUL-terminated blank HP bar.
- OP frees its temporary palette DOS block before overlay. The former four-
  paragraph block split free memory and made `execl` return ENOMEM=8.
- MAINE's C++ code group changed the CS frame for SHARED assembly. Independent
  native IRQ/PAR and self-modifying renderer segments repair four vectors and
  38 CS-relative operands (39 for OP, including its monochrome CDG helper).
  The build checks these destinations, including
  observed direct-call CS frames. The default renderer branch retains its
  previous complete link-relevant OMF output in cold compiler comparisons.
- OP labels use monochrome CDG masks and description color 15, observed in
  OP_MAIN_TEXT 0A74:0375/0497. Native call composition and FAR Pascal RETF6
  checks pass; historical accepted inline bodies remain unchanged.

The uninstrumented v1178 normal route reaches stage 0, Game Over, Continue,
MAINE name entry, score persistence and the OP title menu. Ten saved-score
section checksums and digit ranges pass. Private v1176 separately records all
MAINE initialization call completions. Pinned originals under the same emulator
also show pale score colors and previous CONTINUE/stage-image remnants; do not
attribute these to reconstruction without another control.

The uninstrumented v1181 normal-menu scenario passes on native and original
products. Options frames 75/95 and returned-menu frame 165 are raw-identical.
Both enter Music Room, emit non-silent stereo audio, view scores, exit to DOS
and save the same valid configuration `0304010201010000000c` (Lunatic, four
lives, one Bomb). Startup/loading and polygon-animation phases differ;
waveform or general timing equality is not claimed.
The native v1182 reboot loads those saved options into the menu and exits to
DOS with the complete ten-byte configuration unchanged.

The first-stage regression is currently failing. With ordinary Easy/six-life/
two-Bomb options and recorded shots, uninstrumented native v1183 stops in ZUN's
STOP modal by checkpoint 155; originals continue to Orange's dialogue and fight.
Removing only host WAV-capture chords still reproduces the native stop (v1184).
Private call checkpoints reach `bullets_update()` at stage_frame 3996 before a
Divide error (v1188); adding decimal checkpoints changes the last frame to 3958
but again exits there. The observed digit divisors remain 1000/100/10. Extra
observer layouts can instead reach COPY/STOP modals. The initial damaged call
or memory write is unresolved; do not equate these secondary symptoms with a
confirmed arithmetic bug or accept first-boss gameplay.

Current runtime receipts:
- `.analysis/runtime/candidates/native-four-cs-v1178-20261002/run/receipt.json`
- `.analysis/runtime/candidates/native-four-cs-v1178-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/native-maine-render-v1176-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/original-score-baseline-v1177-20261002/run/receipt.json`
- `.analysis/runtime/candidates/native-actions-v1170-20261002/run/play-state.json`
- `.analysis/runtime/candidates/native-op-menu-v1181-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/original-op-menu-v1181-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/native-op-reload-v1182-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/native-first-boss-nochord-v1184-20261002/run/receipt.json`
- `.analysis/runtime/candidates/native-fault-calls-v1188-20261002/fault6.log`

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
image; `--rank 0` selects Easy. Runtime `--checkpoint-second` captures
intermediate frames; held keys use
`--input-event down:z@SECOND` / `up:z@SECOND`. `--key-delay-ms 300` gives menu taps
adequate duration. Always use new output paths. Private state probes do not
replace uninstrumented runs. `inspect_th04_handoff_trace.py --require-score-saved`
checks executed-image identity and changed decoded score sections.
Use `--scenario config/runtime/scenarios/op_menu.json` for the normal menu
regression and `inspect_th04_handoff_trace.py --require-config-options
030401020101` to check persistence. `prepare_product_hdi.py --config-from-run
RUN_DIR` seeds a fresh disposable image with a verified saved configuration.
Use `--scenario config/runtime/scenarios/main_stage1.json` with Easy/six-life/
two-Bomb options to reproduce the current first-stage failure. Private MAIN
`--fault-trace` emits gameplay call and decimal DIV checkpoints; the runtime
runner's `--debug-port-e9` captures them without losing boot-log smoke markers.

## Next work

1. Fix the first-stage `bullets_update()` failure, then validate bosses, later
   stages, endings, Extra and character/rank variants.
2. Compare rendering/audio under another PC-98 emulator before assigning
   original-and-native shared display artifacts to source bugs.

## Navigation

- [Architecture](ARCHITECTURE.md): artifact/ABI and source ownership.
- [Runtime](RUNTIME.md): pinned emulator and image setup.
- [Progress](PROGRESS.md): historical function acceptance.
- [Evidence index](reconstruction/README.md): focused historical investigations.
- `config/evidence.csv` / `config/knowledge.csv`: durable receipts and findings.

Historical checkpoints remain in Git and the ledgers. Old missing-header counts
and blockers are not the current work queue.
