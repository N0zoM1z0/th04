# TH04 current handoff

Updated 2026-10-03. The active goal is a standalone PC-98 game: checked-in
TH04 source, successful builds, and normal gameplay. Native whole-build byte
equality is not required. The two remaining MAIN exactness cases are deferred
and retain their nonexact states. ReC98 implementations are adaptation inputs;
upstream exactness claims are not inherited. Current phase: runtime integration.

The `semantic/readable` branch now prepares the DOS source for the native
x64 port; it starts at current local `main` commit `8d20492`. The first bounded
batch clarifies the shared PI decoder's command names, units, history, DOS
allocation and ownership. Two cold isolated DOS builds remain raw-identical:
38,050 bytes, SHA-256 `9cc4e7ad…`, 254 relocation entries, zero differences.
Independent historical pixel hashes and slot load/free controls also pass.
This proves a source-to-source regression result for the service harness;
it is not original-target equality or a complete Good Ending visual replay.
See [semantic readability](SEMANTIC_READABILITY.md) for the remaining queue.
The PAR/CDG semantic batch also passes dependency-validated incremental builds:
complete MAIN/OP/MAINE files and ordered relocations equal their preceding
source builds (192,351/77,740/70,614 bytes; SHA-256 `dbbfa404…`,
`c8ac4d73…`, `0a2d3ce8…`). Nine real PAR-member controls pass. Historical
CDG replay could not complete: the old OP/MAINE private snapshot is absent,
and the current MAIN driver rejects a scaffold-transform digest before
building. No target acceptance or ledger state is promoted by this batch.
The BFNT semantic batch likewise preserves all three complete DOS files and
ordered relocations. Historical pattern/palette hashes and fake-VRAM screen
hash `0BE615EA` pass with lifecycle and clipped-placement controls; see the
[BFNT note](reconstruction/product/TH04_NATIVE_SUPER_SPRITE_V870.md).
Ending source repair and Windows deployment are deferred while the user plays.
Private CPU replay has reproduced MAINE CDG self-modifying CS writes into the
PI decoder (`.analysis/ending-analysis-20261003/ANALYSIS.md`); a complete
repaired ending-to-registration replay is still required. The newly reported
stage-4 top stripe disappears after Marisa's bomb; shared backdrop filling
matches its target body, while display-scroll transition state remains under
investigation. Do not interpret either report as completed runtime acceptance.


## Current state

| Artifact | Accepted authored functions | Native build/runtime |
| --- | ---: | --- |
| OP | 93/93 | Standalone build; normal options/Music Room/scores/DOS exit and saved config pass |
| MAIN | 493/495 | Standalone build; bounded ordinary route reaches stage 3; user completed the invincible Easy route through the ending |
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
`.analysis/reconstruction/probes/product-20261002-151920-831649d8-build.json`.
The latest OP cold build compiles 111 C/C++ and 53 ASM roots, links without
warnings, and equals the preceding dependency-validated cached native build.
The current normal MAIN cold build (`product-20261002-151920-831649d8-main`)
rebuilds all roots with the shared byte-sized sprite renderer: 191,823 bytes,
SHA-256 `cd9aedb58cd9e7fbbc16f590f5199fa918c815fad2183ff9d9a1de335f4d16cd`.

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

The explicit bullet-group repair passes ordinary Orange clear and stage 2
entry. Both old switch frames fail the static gate; the published and cold
repaired builds pass. Historical private fault layouts remain in the ledgers.

The ordinary v1203 `main_progression.json` run reaches Kurumi combat but
displays Divide error/DOS return by 575 seconds. The same-image v1208 repeat
still fights Kurumi at 605 and displays the same guest failure at 635. All four
executed product identities pass in both runs. Host exit 0 does not accept the
guest failure; the repeat's black final frame is also unaccepted.

The pinned-original v1204 control reaches third-stage Elly dialogue at 635;
its final 650 frame is black and is not an accepted checkpoint. The private
cpu-only v1207 MAIN also reaches stage 3, with a valid observer arm but no
exception. Neither result repairs the ordinary native failure. A private
source-built emulator likewise changes progression and does not reproduce it.

The primary VM86 observer confirms vector 0 at `24FB:9780`, MAIN load `10FC`,
MAIN_03 `13FF:9780`: all 64 relocated code bytes match the ring-count IDIV in
`bullet_velocity_and_angle_set()`. DS `334F` has Easy rank, performance/min/max
4/4/16, ring-aimed group 2Ch and count zero. The BP chain and actual near-call
instructions identify Kurumi dual spawnrays, fixed regular generation and the
Easy wrapper. Pinned target file `1E612h` has the same cumulative reductions:
six shots minus two minus four becomes zero, then Easy halves zero.
The native `TH04P` clip branch now skips empty rings; the original replay branch
retains its bytes. The isolated x86 Oracle rejects the old native build and
accepts both empty-ring cases plus nonempty-ring/single negative controls.
The ordinary repaired v1217 run clears Kurumi and explicitly enters STAGE 3 at
635 seconds. All four executed product identities pass; the black final frame
is unaccepted. Native cold-build equality and the generated-code Oracle pass.
Two default-branch cold replays preserve the complete 2,139-byte bullet owner:
raw bytes, MAP and relocations pass (`empty-ring-v1219/receipt.json`).
The read-only observer passes real-mode and DOS/EMM386 VM86 DIV fixtures,
including 27 instruction bytes and complete RAM snapshots. Calibration:
`.analysis/runtime/emulators/primary-observer-v1215b/calibration-vm86/receipt.json`.

For interactive testing, the separate `--invincible-main` build clears pending
player hits before miss processing in a private staged source overlay. Its four
products build and pass MZ/link audits; the normal published MAIN is unchanged.
`scripts/export_windows_play.py` packages the four verified products, saved HDI,
Windows DOSBox-X and `start-th04.bat` at
`D:\Entertainment\Game\Touhou\th04-reconstruct`. The Windows 2023.05.01
emulator reached OP with the user's dynamic/Pentium/15000/32 MB profile; Z/X
worked after switching Windows input to English. The user completed the
invincible Easy route through the ending, with slow OP fireworks, boss defeat
explosions and some stage-5 Yuuka barrages but no other reported faults. Their
saved Easy config has turbo mode enabled, so the explicit bullet-count slow-
down branch is inactive. This is user runtime observation, not an instrumented
ordinary-build acceptance. The shared `SUPER_PUT` now uses masked byte-sized
planar writes. Fake-VRAM output and 45 randomized placements match the prior
renderer. Under pinned Linux DOSBox-X, the old OP was still in fireworks at
30 seconds; the changed OP reached the title menu at 30 seconds. Receipts:
`.analysis/runtime/candidates/super-perf-{before,after}-20261002/run-logo/receipt.json`.
Windows-host and stage-5 performance need fresh playtest. The Windows builder
is `build-th04.cmd`: it shows English progress, hashes, and uses validated
incremental object reuse by default; `-Cold` forces a four-product source build.
The complete invincible Windows run
`product-20261002-155156-92d1f35a` passed all four source/link audits and
refreshed the saved package. The following default Windows CLI run
`product-20261002-162226-4cebef25` passed in 98.8 seconds: MAIN reused 192
C++ objects, OP 163 objects, MAINE 137 objects, and ZUN passed unchanged-input
fingerprint and package/product hash checks. All four final product hashes
equaled the cold build. The saved `MIKO.CFG` and `GENSOU.SCR` SHA-256 values
were unchanged across both exports. The Windows package is ready for a new
playtest; these build checks do not establish its frame rate.
Shared `SUPER_PUT` composes each destination byte once, directly overwrites
fully opaque bytes, and clips row/byte intervals before drawing. DOS fake-VRAM
screen hash remains `0BE615EA`; randomized planar and clipping controls pass.
The user completed the invincible Lunatic route and reported that Good Ending
score registration showed background/remnants without the menu or text and
turned black after Esc. Their copied HDI is preserved at
`.analysis/runtime/candidates/lunatic-ending-user-20261003/` (SHA-256
`91cafe8a…`). The saved Lunatic configuration has turbo enabled; the
bullet-count intentional slowdown branch is inactive, so Yuuka spell lag is
inferred to be render/CPU load pending a phase-specific trace.

The product PI slot free path now clears its owner pointer before the next
load. A bounded DOS load/free/load/free probe passes and the product far-call,
vector and MZ audits pass; this fixes a verified stale-pointer hazard, but a
complete Good Ending-to-registration visual replay is still open. See
[`TH04_NATIVE_PI_SLOT_LIFETIME_V1224.md`](reconstruction/product/TH04_NATIVE_PI_SLOT_LIFETIME_V1224.md).
The current Windows fast-build package is
`product-20261002-183722-150a02ad` at
`D:\Entertainment\Game\Touhou\th04-reconstruct`. `start-th04.bat` uses
24,000 DOSBox-X cycles for heavy scenes; `start-th04-reference.bat` uses the
collection's original 15,000-cycle setting for comparison. The saved
`MIKO.CFG` and `GENSOU.SCR` hashes `64d6b41f…` and `d4037728…` were preserved
byte-for-byte during export. Windows playtesting must establish whether the
registration page and Yuuka frame pacing improved; a successful build cannot
make that runtime claim. The latest user Reimu/Lunatic playtest reports that
Yuuka is now smooth, but the full Ending route still shows damaged graphics
and never reaches registration; sound continues and Esc has no visible effect.
This rejects treating the PI slot fix as a complete Ending repair. The second
provided image is a PC-98 STOP pause notice, not registration.
The Linux emulator aborts after PC-98 reset with dynamic core, so its
private launcher uses normal/Pentium/15000/32 MB. Neither playable profile is
normal-game acceptance evidence. A long native v1220 route reached Game Over
after Continues and was stopped at 1250 seconds; a
pinned-original v1221 control showed a guest interrupt/reset screen at 455.
Neither provides a later-stage acceptance checkpoint.

Current runtime receipts:
- `.analysis/runtime/candidates/native-four-cs-v1178-20261002/run/receipt.json`
- `.analysis/runtime/candidates/native-four-cs-v1178-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/native-op-menu-v1181-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/original-op-menu-v1181-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/native-op-reload-v1182-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/native-bullet-group-v1199-20261002/run-progress/receipt.json`
- `.analysis/runtime/candidates/native-bullet-group-v1199-20261002/run-repeat-v1208/receipt.json`
- `.analysis/runtime/candidates/original-progression-v1204-20261002/run/receipt.json`
- `.analysis/runtime/candidates/native-cpu-state-v1207-20261002/run/cpu-fault.json`
- `.analysis/runtime/candidates/native-bullet-group-v1199-20261002/run-primary-gdb-v1214/emulator-cpu-fault.json`
- `.analysis/runtime/candidates/native-bullet-group-v1199-20261002/run-primary-vm86-v1216/emulator-cpu-fault.json`
- `.analysis/runtime/candidates/native-empty-ring-v1217-20261002/run/handoff-state.json`

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
`--cpu-debugger-receipt .analysis/runtime/emulators/primary-observer-v1215b/receipt.json`
uses the calibrated primary-emulator exception observer. After the completed
run, `inspect_th04_emulator_cpu_fault.py --run-dir RUN --require-fault` verifies
all executed products and locates captured code against the relocated MAIN/MAP.

## Next work

1. Have the user replay OP fireworks, boss defeat and Yuuka stage 5 with the
   updated Windows package. Profile any remaining slowdown under that host.
2. Inspect the completed ordinary sweep at
   `.analysis/runtime/candidates/native-empty-ring-v1217-20261002/run-sweep-v1222`.
   Validate later stages, endings, Extra and character/rank variants; the
   independent playable invincible image can expose additional integration bugs.
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
