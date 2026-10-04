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

Current native scope: [Stage6 resources/waves/pre-battle dialogue](PORT64.md#stage6-resources-waves-and-pre-battle-dialogue).
Normal/Lunatic naturally traverse Stage1..5, then Stage6 waves and the complete
pre-battle scene at frame5198. Native releases STD/MAP streams at the original
speed0/back-page1 gate and invalidates CDG1..31 handles during dialogue. The
62 battle sprites128..189 are loaded; simulation holds before unported
Yuuka6's first update. Easy retains its separate Stage5 bad-dialogue/Ending
frontier. Semantic remains stopped except for concrete port ambiguities.

v1282 passes three incremental builds/23 CTests/24 products each. Independent
original CPU1,024 setups/42 gates/four dialogue traces (1,895 ordered requests)
agree GNU/Wine/optimizedUBSan; actualWindows consumes the retained references.
Independent archive217,744 portrait pixels pass16 captures. New16 Stage6
routes112BMP/128counters agree four hosts; full GUI preserves34 preceding
image/counter groups and actualWindows checks1,660 route images. Original
whole-route/physical-hardware/FPS/DOS exactness are separate, unproved claims.
Changed Stage5 contracts retain1,024 setup/1,820 star/504 pixel controls on
GNU/Wine/UBSan against v1277 independent references; original CPU not rerun.
Producer manifest68eda7fd; final08a9891b only corrects verifier.limit prose.
reporter-continuity proves the otherwise identical AST/all24 products per host
unchanged; producer receipts keep their original manifest.

Root Windows EXE c2542286/English launcher are now v1282, no GUI launched.
previous-v1281 is retained; all21 DOS/HDI/config/font/build root files unchanged.
Receipts:.analysis/port64/stage6-v1282/ (target-review,root-ghidra-attestation,
setup-{linux,wine,ubsan}-final,original-dialog-review,integration-final,
integration-review,native-windows-controls-receipt,reporter-continuity,
source-manifest-final,stage5-reference-replay,Windows export).5514 completed validation BMPs are
gzip-archived with SHA readback, reclaiming3.84GiB; current builds/fonts/saves
and original CPU references remain expanded. Restore private BMPs with gzip -d.
Next: Yuuka6 core/attack/animation/entity/foreground/checkerboard owners and
ordinary battle join; then Extra, player death/Continue/Bomb, remaining HUD,
audio, Ending and save I/O. The complete native game remains unfinished.

Historical v1281 acceptance:
The GUI runs title/options/character/shot and ordinary Stage1 through Stage5
waves/midbosses/bosses/dialogues. Yuuka now joins actual shot damage, seven
attacks, thick lasers, indexed foreground/background/palette, all eight32x32
factor3 death frames and route-specific post-dialogue. Sixteen Reimu/Marisa
Normal/Lunatic A/B-shot/idle routes request Stage6; both Easy A-shot routes
load the independent bad dialogue and hold before unported Bad Ending.
That batch published v1281 native EXE/English launcher without launching GUI. Previous
v1277 is retained in port64-preview/v1281-yuuka-battle/previous-v1277.

Final native source manifest c81d775741f2d836c456aa76bbab5c30c4de746d695f620639ab5083603e8ea6.
Three incremental builds each pass23CTests/24ELF64-staticPE products. Full
GNU/Wine/actualWindows1548 route images agree;32 preceding image/counter groups
remain unchanged. New698Yuuka BMPs/716counters also agree optimizedUBSan.
Fresh original128death-zoom screens compare32,768,000 pixels;96original Ending
branch invocations execute actual bad filenames/FE/type1 publication before
GameExecl. Native branch comparison is predicate-only; I/O/dialog/audio/palette
are CPU adapters. Retained independent9936graphics and7330core/69652checkpoint
references pass current GNU and actualWindows consumers; optimizedUBSan core
also passes. Original full-route/physical-hardware/FPS/DOS exactness remain
separate. All21 nonnative Windows root files are unchanged.

The initial ordinary route exposed missing laser initialize(): scratchflag0
created inactive beams. Stage initialization now arms LINE/radius/clock while
retaining other fields. Clear/bridge the bullet bool and laser BYTE contact
once per new simulation frame, including gather releases; blocking dialogue
and cached repaint preserve simulation/RNG/explosion/laser/star state. Player
death/Continue remains an unported consumer. The previous zoom-sheet comment
is corrected: entrance128 is64x64;phase254 uses MIKO32 patterns4..11,32x32.
v1280 zoom controls covered entrance/idle assets only; retain their scope.
Receipts:.analysis/port64/yuuka5-join-v1281/ (integration-accepted/receipt,
integration-review,native-windows-controls-receipt,death-zoom-final/receipt,
departure-final/receipt,target-review,source-manifest-final,Windows export).

The completed v1281 validation BMPs are losslessly gzip-archived after comparison:
media-archive-receipt and accepted-media-archive-receipt reclaim10.73GiB with
original/compressed hashes and readback. Three redundant native pixel outputs
are also archived; root .analysis/cleanup/port64-duplicate-pixels-20261004/receipt
confirms93.0MiB reclaimed and5,117 protected files unchanged. Original CPU pixel
buffers, current builds, DOS fast caches and Windows saves remain live. Restore
private archived outputs with gzip -d before replay; root/native CI pass.

Historical v1277 resource controls: Stage5 has no BMT or midboss callback; actual setup retains BOSS/midboss metadata
and null callbacks have start frame60000. Original setup1,024/star1,820/rolling
OR-plane504 controls pass;16 archive portrait checks compare197,728 pixels.
Linux/Wine/actualWindows21contracts/850BMP/926counters agree;optimizedUBSan
Stage5 routes and controls agree, all30preceding image/counter groups unchanged.
Receipts:`.analysis/port64/stage5-v1277/`; final native source manifest
581547d4f74da59a984ad83f6a247bdc38735b923820e9765b8621a31b9a2115.
CTest-only correction preserves all22product hashes; an explicit continuity
receipt bridges earlier source manifests without relabeling their receipts.

Fresh MAIN0AAF:419E..4280/4281..42F0 bits/body review preserves raw sprites,
color9 packed-center line chains, visible WORD damage reset and hidden-slot
retention. Only slots0..3 are Marisa-owned; private26 and slots4..31 stay intact.
13,606 original foreground/5,888 shared NPC backdrop controls agree GNU/Wine/
optimized UBSan/actual Windows.1,344 original body/bit normal-white SUPER/
rolling controls compare344,064,000 indexed pixels across all12BFNTimages,
eight alignments and signed Y edges. Hardware ports/visible VRAM use a bounded
shadow; physical alias/page/scroll/pacing remain separate.

Expansion can move line endpoints offscreen. Marisa uses original0000:079A..
080C clip and1562..16FE raster: actual stage32..415/16..383 inclusive, X before
Y, signed IDIV towardzero, then16.16 accumulator.1,522 original CPU write-mask
controls agree all four hosts; selected ordinary coordinate cases, not an
extreme16-bit/general physical-line equivalence claim. Clipping completed
raster changes boundary rounding; direct old in-screen-only ray reuse can fail.

7,759 Marisa core controls/87,031 full records and1,024 retained setups still
pass all hosts. Original draw/pixel producers and final native reference
consumers are separately frozen; final line controls reexecute the CPU, and
core consumers freshly execute four IDIV failures. Actual stage_state_init
0AAF:73DB..74A5 clears custom832 bytes but retains private26; initial loaded
private bytes are zero. Stage4 setup retains preceding Elly metadata. Private
defaults are first-encounter assumptions, not a generic reentry reset.

GUI alone enables an explicit portable flystep repair: attack1/2 durations12/
13 extend to14, avoiding the original zero divisor. Both policy callers have
separate native contracts; original-state comparisons keep the policy disabled.
No natural original-route divide fault reproduction claim.

Eight natural Reimu-player Normal/Lunatic A/B shot/idle routes162BMP/170counters
reach attacks/bit lifecycles/post-dialog/bonus/fade417/departure489/Stage5 request.
20contracts/738totalBMP/798counters agree Linux/Wine/actualWindows; optimized
UBSan contracts/routes/state/draw/line/pixels pass. All preceding576BMP/628
counters plus earlier menu/shooting captures are identical. Blocking dialogue
and pending Stage5 resources freeze simulation/RNG.21staticPE validation
products live in port64-preview/v1276; only GUI EXE/launcher are published,
21DOS/HDI/config/font/build root files stay unchanged. MinGW cross-build and
Windows execution are distinct. No GUI FPS/fullgame/physical hardware/DOS exact
claim. Root preflight/fresh Ghidra header/entry/relocations/bytes attestation pass;
DOS source/exact units/authored acceptance stay unchanged.

User-requested cleanup already reclaimed18.53GiB from obsolete CMake/Windows
native builds and losslessly archived historical BMP/large-text outputs.
Another2.83GiB is reclaimed from4,064 v1275 validation BMPs via verified gzip;
media-archive-receipt.json records every original/compressed SHA.
Archived data were read back against SHA-256. Current three native build dirs,
targets/database/toolchains/DOS images/fonts and live CPU references remain.
v1276 validation BMPs/redundant native pixel stream archive reclaims another3.66GiB;
media-archive-receipt.json stores readback hashes. Original CPU references stay live.
Restore historical private media with `gzip -d -- FILE.gz` before replay.
Follow-up cleanup reclaims 3.33 GiB: 4,353 obsolete validation files are archived
with verified readback and 59 superseded v1272-v1274 Windows executables removed.
`.analysis/port64/cleanup-20261004/receipt.json` records hashes and confirms
1,255 current build/Windows files unchanged. CI and diff checks pass.

Receipts: `.analysis/port64/marisa-render-v1276/` contains target-review.json,
stage-reset-controls.json, producer-source/manifest.json,
line-producer-source/manifest.json, render-linux-full/receipt.json,
pixels-linux-full/receipt.json, render-{linux,windows,ubsan}-accepted/receipt.json,
pixels-{linux,windows,ubsan}-final/receipt.json,
core-{linux,windows,ubsan}-accepted/receipt.json,
setup-{linux,windows,ubsan}-accepted/receipt.json,
native-windows-{core,setup,render,background,line,pixels,receipt}.json,
integration-review.json and windows-export-receipt.json.
Cross: `.analysis/port64/verification-marisa-render-v1276-accepted/receipt.json`.
Manifest:3adf253ed25e0a48be20efd71e94d70ad0de70864755b752b156cd0d003bc000.
Prior v1274/v1275 original references and focused PORT64 notes stay available.

v1277 validation media are archived after readback: 3,078 BMPs reclaim 2.15 GiB.
`stage5-v1277/media-archive-receipt.json` records hashes; original CPU references
and current builds remain expanded. Restore private BMPs with `gzip -d`.

User-requested build cleanup archives/removes 325 obsolete expanded builds,
compresses 173 historical generated HDIs and 32 duplicate consumer traces, and
removes 42 superseded v1275/v1276 Windows PEs. About 3.9 GiB of file allocation is
reclaimed; 112,131 retained files have identical pre/post hashes. All extant DOS
build inventories and their referenced object caches, three current native
builds, Windows root/saves and v1277 including previous-v1276 rollback remain.
Receipt: root `.analysis/cleanup/build-artifacts-20261004/receipt.json`.
Restore individual historical images/traces with `gzip -d -- FILE.gz`; complete
old source/object/result trees are recoverable from the SHA-verified
`expanded-builds-20261004-cleanup.tar.zst` in root receipt-archive.

Stage5 laser dependency is now portable: initialization/full 24-byte copy/
first-free allocation/lifecycle/collision plus ordered drawing requests.
8,464 original CPU cases/13,975 checkpoints agree Linux/Wine/UBSan/actualWindows;
22 contracts pass all three builds. Existing 22 Linux/UBSan products remain
raw-identical; MinGW differs only COFF timestamp/checksum. Root Windows stays
v1277; only new validation files are exported to v1278-laser-controls.
See [laser owner](PORT64.md#thick-laser-state-and-graphics-producer) and
`.analysis/port64/yuuka5-v1278/`. Graphics call equivalence excludes pixel
consumers/physical VRAM. Native source manifest 05e8bd69.

Stage5 Yuuka core/seven attacks/movement are now portable. Fresh original CPU
production passes7,330cases/69,652checkpoints including8retained win/timeout
controls spanning phases0..18/254/255 at four difficulties. Linux/Wine/UBSan/
actualWindows agree; three incremental builds pass23CTest/24products each.
The original circle entry is1BA6 and mirror special-motion tokenFF. Spawn and
laser contact now share the BYTE hit latch without treating its retained127 as1
until a new contact. VM is a null/retained token; the FAR address is not a host
pointer. All23 GNU predecessors are raw-identical; MinGW differences are only
COFF timestamp/checksum.14UBSan predecessors differ, so fresh16Stage5 routes
compare112BMP/128counters instead of claiming raw equality. Media are verified
and gzipped. At v1279 root Windows remainedv1277; only v1279-yuuka-controls diagnostics
exported. See [Yuuka core](PORT64.md#stage5-yuuka-core-and-seven-attacks) and
`.analysis/port64/yuuka5-v1279/`. Source manifest ce458897. These are boss-only
controls with injected shots/downstream consumers, not a GUI battle join.

Stage5 Yuuka foreground/background and sprite/laser/filler rasters now pass
9,936request controls and1,804full640x400 pixel controls across GNU/Wine/UBSan/
actualWindows. Normal/white SUPER preserves unsigned-X/WORD flat addresses;
zoom is3x, idle sheets48x96. Rectangle/vline clipping wraps before comparison.
Initial original972sprite screens were complete before native case864 failed;
final consumers replay those unchanged references with explicit producer AST/
helper-byte continuity. Final832primitive screens and allrequests reexecute
original CPU. The initial rejected consumer remains failed. Core7330/69652
regression passes GNU/actualWindows.23CTest/24products pass each build;23prior
GNU/UBSan products are raw-identical and23MinGW differ only header timestamps/
checksums. At v1280 only diagnostics were exported; GUI/rootWindows remainedv1277.
See [Yuuka graphics](PORT64.md#stage5-yuuka-foreground-and-raster-controls),
`.analysis/port64/yuuka5-render-v1280/`; final manifest7e410b8e. No whole-game/
physical-hardware/FPS/DOS-exact claim.

The latest requested cleanup additionally archives97historical files with
verified gzip readback, reclaiming1.21GiB while119,965retained files keep their
hashes. Root receipt:`.analysis/cleanup/historical-media-followup-20261004/`.

Next bounded work: actual Stage6 resource/setup/STD and Yuuka6 dialogue/battle.
Extra, player death/Continue/Bomb, remaining HUD, audio, Ending/save still need
native implementation. Semantic stays
stopped except concrete port ambiguities. Complete native gameplay is the port
stopping condition.

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
