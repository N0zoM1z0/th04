# TH04 current handoff

Updated 2026-10-04. The standalone PC-98 reconstruction remains the behavioral
reference; native x64 has a separate nonexact branch. Target provenance remains
`candidate-local-attested`, not proof of an official pristine dump. The two
remaining MAIN exactness cases stay deferred. Portable changes do not alter DOS
source or exact acceptance. Root `semantic/readable` stays at `ce68815`;
`port/modern-64` is the active native worktree.

Semantic readability is paused at the user's stopping condition: enough clarity
for the next port slice. Reopen only a concrete native ambiguity, then return to
implementation. Historical semantic results and bounded replay limits are in
[SEMANTIC_READABILITY.md](SEMANTIC_READABILITY.md).

Current native scope: [Kurumi battle and departure integration](PORT64.md#kurumi-battle-and-departure-integration).
The GUI runs title/options/character/shot selection, ordinary Stage1 through
Orange and Stage2 through its midboss, pre-dialog, Kurumi, post-dialog, clear
bonus and the416/488 departure. Stage3 resources are the held frontier. Player
death/Bomb, complete HUD/audio, later stages, Ending/save remain unported.

MAIN13A9:A4D1..A517/A623..A6F5 reset/setup retains HP/angle/endHP,
additional1..15 and explosion metadata; only two small alive flags clear,
including retention of the big alive flag.1,024 original CPU setup controls and
256 countdown controls0AAF:5FD4..5FDE agree Linux/Wine/UBSan/actual Windows.
Stage runtime06E0 independently resets slowdown1/shake0/Bomb-disabled0/invincibility64;
common stage0675 ends palette tone100. Loaded Stage2 palette color0 joins the
boss at pre-dialog completion; Kurumi later sets its observed red color0 itself.

Eight natural Normal/Lunatic Reimu/Marisa shot/timeout routes reach Stage3's
request. Dialog suspends actors/invincibility/RNG; post-dialog resumes the
already-entered frame without repeating the prefix. Bonus/fade/next each execute
once. Main generation2 and the process seed persist. Departure489 completes
frame488; resident stage/ascii become2 while resource stage stays1 until load.
Fifteen contracts,168 BMPs/188 counters agree Linux/Wine/optimized UBSan/actual
Windows. Previous96 BMPs/108 counters remain identical to v1268. Current Linux
reexecutes10,640 original render controls;41,488 original state records replay
on Linux/Wine/UBSan. Independent archive decode checks57,188 portrait and86,016
selected unobstructed battle-background/colorfill pixels. Native host agreement
is not original full-route VRAM, physical hardware, frame pacing or DOS exactness.

Windows `D:\Entertainment\Game\Touhou\th04-reconstruct\start-th04-port64.bat`
now uses v1269 through Kurumi clear; no GUI was launched. Package
`port64-preview/v1269` contains16 checked x64 PE executables. Only root native
EXE/launcher changed;21 existing DOS/HDI/config/font/build files remain identical.

Receipts: `.analysis/port64/kurumi-live-v1269/{target-live,integration-review,resources-live,negative-live,native-windows-receipt,native-windows-setup,windows-export-receipt}.json`,
`setup-{linux,windows,ubsan}-final/receipt.json`,
`core-{linux,windows,ubsan}-final/receipt.json`, `render-linux/receipt.json`, and
`.analysis/port64/verification-kurumi-live-v1269-final/receipt.json`.
Source manifest: `1fcba424ea85e628b7f7df71e3183bd861f0a5e920645fabccf0cc60d0df52d1`.

Next bounded native work: establish Stage3 resource/STD/MAP/midboss ownership,
then Elly render/battle/dialog. Continue stage coverage and later player-death/
Bomb, complete HUD/audio/Ending/persistence work. Keep semantic stopped.

## Current state

| Artifact | Accepted authored functions | Native build/runtime |
| --- | ---: | --- |
| OP | 93/93 | Standalone build; normal options/Music Room/scores/DOS exit and saved config pass |
| MAIN | 493/495 | Standalone build; user completed invincible Easy/Lunatic and all normal Windows Normal routes; optimized bounded ordinary replay passes |
| MAINE | 72/72 | Standalone build; seeded Good Endings register/save; user confirms full Normal Windows Ending/save before the planar batch |
| ZUN | 3/3 | Source-only cold packed build; four-product GAME.BAT startup passes |

These counts describe historical function acceptance, not whole executable or
normal-game completion. `python3 scripts/status.py` reports the live ledgers.
Targets remain `candidate-local-attested`. Product include checks have zero
compatibility forwarders and forbidden ReC98 edges.

The full native build compiles 193 MAIN C/C++ roots, 155 ASM roots, eight state
owners and four generated sprite owners without `masters.lib`. All four products
build through `scripts/build.py`. The bullet batch uses dependency-validated
fast MAIN/OP/MAINE builds and rechecks the preceding cold ZUN source/packing
receipts and 37 unchanged component-source/build-driver hashes. Current
normal/invincible inventories are `.analysis/build/th04-{normal,invincible}/build.json`.
Normal products are MAIN 199,455 bytes (`cb4c5b66…`), OP 79,372 (`ef37e6e8…`),
MAINE 72,246 (`7bfd7fd5…`) and ZUN 7,723 (`d6043dce…`). Invincible MAIN is
also 199,455 bytes (`0d99bc5a…`); the other three products are identical.

Verified integration fixes:
- MAIN EGC tile copy uses 3100h, observed at MAI_TEXT 0AAF:212C (file E41Ch).
  All 600 initial tiles match their four-plane source images. HUD data includes
  four rank strings and a NUL-terminated blank HP bar.
- OP frees its temporary palette DOS block before overlay. The former four-
  paragraph block split free memory and made `execl` return ENOMEM=8.
- MAINE's C++ code group changed the CS frame for SHARED assembly. Independent
  native IRQ/PAR and self-modifying renderer segments repair four vectors and
  42 MAINE CS-relative operands (40 for OP, 39 for MAIN, including their CDG entries).
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
ordinary gameplay-to-Good-Ending handoff remains separate from seeded replays. See
[`TH04_NATIVE_PI_SLOT_LIFETIME_V1224.md`](reconstruction/product/TH04_NATIVE_PI_SLOT_LIFETIME_V1224.md).
The Windows package at `D:\Entertainment\Game\Touhou\th04-reconstruct`
contains optimized normal `product-20261003-082645-59909a08` and invincible
`product-20261003-083233-dcc0bfe1` variants. `start-th04-normal.bat` mounts ordinary
collision damage in `play-normal.hdi`; `start-th04.bat` mounts the separately
source-compiled invincible MAIN in `play.hdi`. Invincibility remains a private
staged source overlay, not a maintained player change or launcher memory patch.
OP/MAINE/ZUN are identical between variants. Both launchers use 24,000 cycles;
reference launchers use 15,000. Optional `start-th04-normal-highcpu.bat` and
`start-th04-highcpu.bat` set only 36,000 cycles for those same respective images.
The latest serial fast builds and Windows readback pass; only MAIN.EXE changed
in either saved image, with every nonproduct GENSO file retained byte-for-byte.
Control: `.analysis/bullet-v1235/windows-export-receipt.json`. Windows CLI builds
retain their English progress and validated object reuse; actual Windows CLI
controls for the preceding batch remain at
`.analysis/render-corner-20261003/windows-fast-control.json`.

The user confirms normal death-to-registration/save and subsequently full
Normal routes/Endings before the planar batch, then improved title/cross/Ending
performance and little Extra slowdown. Optimized bounded ordinary and seeded
Ending/save replays pass; full Lunatic and the optional Windows 36,000-cycle
profile still need a user test. The Linux emulator aborts after PC-98 reset
with dynamic core; Linux runtime controls use normal/Pentium. Old damaged
Ending and Divide-error reports are superseded by the bounded repairs above;
private fault layouts remain replay evidence in the ledgers.

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

1. Retest dense Lunatic/Extra and the optional 36,000-cycle Windows profile;
   separate natural-route timing/audio from the completed synthetic pool control.
2. Inspect the completed ordinary sweep at
   `.analysis/runtime/candidates/native-empty-ring-v1217-20261002/run-sweep-v1222`.
   Validate later stages, endings, Extra and character/rank variants; the
   independent playable invincible image can expose additional integration bugs.
3. Compare rendering/audio under another PC-98 emulator before assigning
   original-and-native shared display artifacts to source bugs.
4. Keep semantic work paused unless a native ambiguity requires a bounded
   clarification; continue the native gameplay queue above. Repair the historical
   scaffold digest/replay surface separately before a new cold exact claim.

## Navigation

- [Architecture](ARCHITECTURE.md): artifact/ABI and source ownership.
- [Runtime](RUNTIME.md): pinned emulator and image setup.
- [Progress](PROGRESS.md): historical function acceptance.
- [Evidence index](reconstruction/README.md): focused historical investigations.
- `config/evidence.csv` / `config/knowledge.csv`: durable receipts and findings.

Historical checkpoints remain in Git and the ledgers. Old missing-header counts
and blockers are not the current work queue.
