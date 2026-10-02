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
| MAIN | 493/495 | Standalone build; Orange clear and stage 2 entry pass; Divide error during Kurumi battle remains |
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
`.analysis/reconstruction/probes/product-20261002-110652-9ee543c1-build.json`.
The latest OP cold build compiles 111 C/C++ and 53 ASM roots, links without
warnings, and equals the preceding dependency-validated cached native build.
The current MAIN cold build (`product-20261002-110750-9ecf496d-main`) rebuilds
all 193 C/C++ roots and equals the published explicit-group repair.

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
- MAIN's native bullet TU explicitly declares BULLET_U_TEXT/main_03. The old
  link-only group made both dense switch tables segment-relative under group
  CS. All 14 linked destinations now pass the far-caller/frame audit, which
  runs before MAIN publication. Other program bytes remain unchanged; the MZ
  relocation table changes. Historical exact source branches remain unchanged.

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

The former first-stage STOP has a bounded repair: the same ordinary Easy/
six-life/two-Bomb v1199 scenario passes midboss defeat and reaches Orange dialogue
at 185/215 seconds. The uninstrumented v1201 extension reaches Orange combat
at 335/365/395/425 and post-boss dialogue at 450. Stage switching and later
gameplay are outside that receipt. Old private layouts showed
STOP/COPY/Divide error; the post-startup v1194 observer instead captured INT 6
at damaged CS:IP after `bullets_update()`. v1197 stopped at its entry before any
bullet iteration. Native static inspection rejects both old switch frames and
accepts the explicit-group build. Digit divisors remain 1000/100/10. The v1195
fixture changed byte 5 (Turbo), despite its misleading private SE label; it does
not exclude sound effects. Preserve the old diagnostics as observations.

The ordinary v1203 `main_progression.json` run finishes its 650-second host
capture with all four product hashes verified. Frequent shot-release gaps
advance dialogue: Orange combat at 215..305, stage clear/new background at
335/365, and Kurumi combat at 455/485/515/545. At 575 the guest displays Divide
error and returns to DOS with the battle screen behind it; 605/635/650 retain
the DOS prompt. Host exit 0 and successful input delivery do not accept this
guest failure. This advances the frontier to stage 2, without accepting its
completion, rendering equivalence, later stages or full gameplay. The fault's
CS:IP and initiating operation are not yet observed.

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
- `.analysis/runtime/candidates/native-bullet-group-v1199-20261002/run/receipt.json`
- `.analysis/runtime/candidates/native-bullet-group-v1199-20261002/run-long/receipt.json`
- `.analysis/runtime/candidates/native-bullet-group-v1199-20261002/run-progress/receipt.json`

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
two-Bomb options for the repaired first-stage regression (the pre-repair
`837b4b8` build stops on this route). Private MAIN `--fault-trace` emits gameplay,
bullet and decimal DIV checkpoints plus chained CPU exception frames;
`--debug-port-e9` captures them without losing boot-log smoke markers.
`main_progression.json` adds frequent shot-release gaps and balanced movement
for longer ordinary-game runs. It does not force stages or change product code.

## Next work

1. Localize the stage 2 Kurumi Divide error under the ordinary progression
   scenario, with an original control and private chained CPU frames. Then
   validate later stages, endings, Extra and character/rank variants.
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
