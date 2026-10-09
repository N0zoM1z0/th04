# TH04 native x64 port

v1340 joins resident timer-register dispatch to the FM/SSG/effect/rhythm
player. GNU8, optimized UBSan and actual Windows each match 80,040 complete
original rows (174 cases, two PSPs); Windows executes 87 unique traces/40,020
rows and compares both loads. All 59 contracts pass per host. 426 maintained
inputs bind 180 AMD64 products. Acknowledge precedes parsing; tempo commits
between Timer B music and Timer A effects; FM26 effect release restores mode.
Four source-only variants reject. Prior owner corpora replay on GNU/UBSan.
Receipts: native `.analysis/port64/pmd-clock-v1340/`; details: native
`docs/port64/evidence/pmd-timer-player.md`.

Physical clocks, synthesis, FM3 extras/PPS/ADPCM, frontend capability/real
measures and full logo/startup remain unfinished. An independently executed
chip model corroborates default timer dividers; the translated manual's
factor-two conflict remains documented. All launches stay muted with no audio
device/backend. Linux GUI hashes remain unchanged; Windows bounded CPU
products are attested. No new GUI or full natural-route acceptance occurs.
DOS acceptance and candidate-local-attested provenance remain unchanged.


Tracking issue: [#1](https://github.com/N0zoM1z0/th04/issues/1).

Updated 2026-10-10. Development has resumed. `port/modern-64` remains separate
from the DOS branch; portable code does not claim PC-98 executable exactness.

## Current state

v1331 adds native PMD SSG effects with 40 semantic instruments, signed sweeps,
priority admission, stop/restart and ordered register writes. GNU/optimized
UBSan each compare 79,488 original effect rows and 3,942 constructed music/drum
sharing rows. The sequence now compares all selected mask bits: 134,274 short
and 49,164 longer rows per host pass without v1330's SSG exclusion.
394 sources bind 156 AMD64 products; 51 CTests pass per Linux host. Musical
OPN/FM effects, synthesis, physical clocks and frontend PMD capability remain
unfinished; all runs stay muted. Current evidence/recovery is native
`.analysis/port64/pmd-v1331/`; see native `docs/port64/evidence/pmd-ssg.md`.
Cleanup preserves 1,046 protected hashes and reclaims about 195 MiB. Current
Windows execution and Git commit/push remain pending. DOS acceptance is unchanged.

v1330 adds a native PMD bytecode/timer-state owner: musical part/rhythm
parsing, note lengths, mutable loops, tempo/bar commands, fade and stop/restart.
GNU/optimized UBSan each compare134274 original control rows in138 cases;
12 longer cases compare49164 rows perhost. SSG drum/SE mask bit1 remains an
explicitly excluded ownership surface, with raw original rows retained.
390sources bind153AMD64products;50CTests pass perLinuxhost. Native OPN/FM/SSG
synthesis, physical timers and frontend PMD capability remain absent. All runs
stay muted; full natural routes/currentWindows/Lunatic timing remain. Evidence
and recovery: native `.analysis/port64/pmd-v1330/`; details: native
`docs/port64/evidence/pmd-sequence.md`. DOS acceptance is unchanged.

v1329 establishes an independent original PMD driver reference: all three
HDI-resident drivers execute 138 M26/M86 cases at two PSP segments, recording
52,992 Timer B states and complete OPN writes.102 FM SE and six fade/restart
controls pass; fixed96tick measure and missing-ack adapters reject. LOGO uses
24ticks permeasure while OP uses96; actual driver state must supply measures.
This changes verification source only: native PMD/FM remains absent and all
150 C++ products retain v1328 identities. Reference/consumer manifests remain
separate. Current private references/recovery: native
`.analysis/port64/pmd-v1329/`; details: native
`docs/port64/evidence/pmd-driver.md`.

v1328 joins process-owned sound timelines across post-logo OP, MAIN and
MAINE: actual options, Scores, Music Room, cutscenes, Staff Roll and
registration. Fresh MAINE keeps an empty EFS; BGM option restart applies
pending SE mode without reloading effects. GNU/optimized UBSan each execute
216 original OP option cases, 32 MAINE entries and 8,834 control snapshots at
two loads; all 1,150 frontend output files agree. MAIN's 3,574,464 PCM samples
per host regress. All outputs of 24 Ending and eight Extra actor controls
agree; these disable hit consumption. An MAINE EFS-reload mutant rejects.
384 sources bind 150 AMD64 products; 49 CTests pass per Linux host. All launches
stay muted. PMD/OPN synthesis/real measures, complete startup audio, full
natural routes, actual Windows and Lunatic timing/performance remain. DOS
acceptance is unchanged. Current evidence/full pending-source recovery:
native `.analysis/port64/sound-scenes-v1328/`; details:
native `docs/port64/evidence/sound-scenes.md`.

Owned terminal cleanup reclaims 1,508,634,624 allocated bytes (about 1.40 GiB)
from 6,357 duplicate files and one retired mutant executable. 13,175 protected
hashes remain unchanged at that boundary; sources, inputs, references and all
current programs remain. Windows interop and shared Git metadata still reject;
no current Windows execution/commit/push is claimed.

See [beeper evidence](port64/evidence/beeper.md). Older milestones below retain
their historical bounded scope; the remaining-owner list is current.

v1325 adds a bounded sound-control owner: original OP resident probes, mode
selection, command dispatch, SE priority/duration and resource-load requests.
13198cases/73751records agree at loads1000/2000 and on optimized UBSan; a
source-only equal-priority mutant rejects.370sources bind141AMD64products;
46CTests pass perLinuxhost.92 priorLinuxproducts are byte-identical; MinGW
relinks have new identities and current build checks only. Real setup/config
frontend regress unchanged. This component is not yet joined to frontend audio
and does not synthesize PMD/FM samples. Next actual sound timeline, EFSbeeper,
PMD/OPN synthesis/measure waits, complete natural routes, actualWindows and
Lunatic timing/performance. All launches stay muted. BGM2 text is corrected to
stereoFM86; numeric setup/config/pixel evidence is unchanged. DOS acceptance
is unchanged. Windows/Git still reject; private evidence and fullv1308..v1325
recovery: native `.analysis/port64/audio-v1325/`. Details:
native `docs/port64/evidence/sound-control.md`.

The v1325 cleanup shares94terminalduplicates after complete bytes/hashes,
retiresone experimental executable and reclaims58671104allocatedbytes
(about56MiB), with4320protectedfilehashes unchanged.

v1324 joins the original two-menu first audio setup before score reads and
ordinary menus.84 original cases/303829 requests agree at loads1000/2000;
780 complete two-page/palette/RGB frames compare998437440bytes against original
font/SUPER kernels. GNU/optimized UBSan pass all9 BGM/SE choices, interrupted
restart, failed save and fresh OP through two muted application processes.
Missing/bad host config requests rankFF using observed ZUN six-byte defaults;
the host checksum is explicit policy. Completing setup defers physical save
until an existing boundary.2112 config controls and16 menu cases/Extra/4failed
writers regress.366sources bind138AMD64products;45CTests pass perLinuxhost.
Original full startup/audio, complete natural ordinary/Extra routes, actual
Windows save/restart and dense Lunatic timing/performance remain. All launches
stay muted. Windows interop and read-only Git metadata reject; commit/push
remain pending. Private evidence/full v1308..v1324 recovery: native
`.analysis/port64/setup-v1324/`. DOS acceptance is unchanged. Details:
native `docs/port64/evidence/setup.md`.

The v1324 cleanup shares907 terminal duplicate files after full-byte and hash
comparison, retiresone experimental executable and reclaims628629504allocated
bytes (about599.5MiB).5793protectedfilehashes remain unchanged; sources,
private inputs, replay/failure references andall138currentprograms remain.

v1322 recorded-demo references remain in `docs/port64/evidence/demo.md` and
`.analysis/port64/demo-v1322/`; original producers keep their own manifests.
Completed captures stay immutable; future replays use fresh directories.

The v1323 cleanup shares651 terminal duplicate outputs after complete byte/hash
comparison, retires8 regenerable Python caches andtwo experimental mutant
binaries, and reclaims412155904 allocated bytes (about393MiB).5233 protected
files are unchanged at that boundary. Current three caches,135 programs,
sources, private inputs and replay/failure references remain.

- v1320 joins OP Scores to ordered fades, held-key paging/release, original
  row/rank graphics and physical dual-column reads in the retained OP process.
  135 original caller cases at loads1000/2000 pass; GNU/optimized UBSan each
  consume the same independent reference. Actual OP font/SUPER kernels agree on
  640 complete two-page/palette/RGB displays (819230720bytes).12 actual
  options/Scores/menu/MAIN routes per Linux host agree on179 files/131BMPs;
  GNU independently compares107 sampled BMPs. Configured difficulty survives
  browsing, parent resident RNG waits for the child, redraw consumes no RNG and
  ordinary MAIN starts after return. A source-only omitted retained RIGHT test
  is rejected.339sources bind126AMD64products;41CTests pass per Linux host.
  556 prior OP reader cases,34 physical startup/restart+6 registration children,
  5926HUD/75RGB+ARGB and24GameOver/386full-display references regress on both
  Linux hosts. Producer/current consumer manifests remain separate; no receipt
  is restamped. Initial native title pages, PI decode, CGROM/GRCG, files/input/
  waits/audio are explicit adapters. Arbitrary bad ciphertext can cause original
  names to cross DS globals; the native consumer rejects unbounded section names
  and undefined SUPER patterns, with the failed probe retained. Full natural
  ordinary/Extra routes, physical timing/audio and current Windows execution
  remain unaccepted. Next Music Room/demo/audio/config and complete-route checks.
  All launches stay muted; DOS acceptance is unchanged. Windows interop/Git
  metadata still reject, so commit/push remain pending. Current receipts and
  full v1308..v1320 source/evidence recovery: native
  `.analysis/port64/op-ranking-v1320/`. Lossless640-display compaction reclaims
  792883200allocatedbytes (about756MiB); decompressed SHA-256 agrees.


- v1317 joins physical saved-score reading at startup and every fresh OP.
  GNU and optimized UBSan each pass 39 contracts, 556 original OP instruction
  cases at two relocated loads, 34 physical startup/restart cases, and 6 seeded
  registration child scenes that save, reopen in fresh OP and enter Extra.
  The original first checksum WORD is strict; the second uses its low byte.
  Global Extra includes the Extra rank, while character/shot availability excludes
  it. The original all-locked Marisa/B fallback is preserved. A source mutant
  that includes Extra in combination availability is independently rejected.
  Both hosts agree on 280 OP files/80 BMPs, 24 Quit routes/4 failed writers
  (220 files/134 BMPs), and 8 Extra MAINE tails (336 files/312 BMPs, including
  physical saves). 304 previous Extra BMPs are unchanged; 8 fresh OP title
  captures now display the saved unlock. Long Extra hit/unlock controls remain.
  120 AMD64 products bind 327 sources. GNU producer manifests precede only the
  corrected empty-mask contract; 117 other products are identical. Original
  outgoing MAIN/MAINE caller order replays retain explicit child/resource adapters.
  Next: full HUD and OP score display, Music Room/demo/audio/config persistence,
  complete natural routes, and actual Linux/Windows save/restart/Lunatic timing.
  All launches stay muted. Windows interop and Git metadata still reject;
  current Windows execution, commit/push and DOS exact acceptance remain pending.
  Full v1308..v1317 recovery: native `.analysis/port64/op-unlock-v1317/recovery/`.
  Own cleanup reclaims 638,742,528 allocated bytes;
  10,020 protected files pass hash readback.
  Details: native `docs/port64/evidence/op-score.md`.

- v1312 joins actual OP Extra/STD, the first retained `_DM06` dialog and
  Mugetsu battle through the frozen Gengetsu-dialog gate. Corrected real character
  selection covers both characters/shots: 16 actor controls per GNU/optimized
  UBSan, with 208 files/192 BMPs agreeing. Actual dialog/resource requests match
  two-load original execution; core/render and 12-scene Bomb regressions pass.
  Each executed host passes 36 contracts; 111 AMD64 products bind 301 source files.
  Actor controls disable player-hit consumption and adapt the unlock bit;
  graphics/input/wait/file/sound consumers are explicit adapters, EMS is untested.
  Full Extra, original complete pixels/MAIN, audio/timing and Windows runtime are
  unaccepted. Gengetsu, unlocks/HUD/OP/audio/config and full routes remain.
  Windows interop and Git writes still reject. All runs are muted. Detailed
  receipts and complete recovery: native `.analysis/port64/mugetsu-join-v1312/`;
  [Extra evidence](port64/evidence/extra.md). Own cleanup reclaims 593,711,104
  allocated bytes with 4,625 protected files passing hash readback.

Coverage correction: v1310 and early v1312 long controls labelled Marisa used
`down` in the character menu, so they actually duplicated Reimu. Their original
component claims remain scoped; their frontend results establish Reimu only.
Retained negative traces and v1312 corrected `right` input/resident/resource
assertions supersede the prior two-character claim; old receipts are unchanged.

- v1310 working tree joins real OP Extra selection, ST06 resources/STD and
  the complete timed midboss. GNU/optimized UBSan each pass35 contracts,
  1466 original actor cases/6652 records,256 setup cases and138 raw tiny
  screens at two loads. Eight long actor-control scenes plus two ordinary
  startup smokes agree per host;82 outputs/74 BMPs agree. Actor scenes disable
  hit consumption and use an explicit unlock-bit adapter; they stop at genuine
  Mugetsu dialog frame11196. The radius field is not hit points. Completed
  bullet clear/zap render state precedes score-tail extends; raw tiny headers
  preserve legitimate no-write calls. Bomb original join re-agrees.108 AMD64
  products bind291 files. Mugetsu/Gengetsu/full Extra remain; Windows builds
  but execution and Git writes remain environment-blocked. Cleanup reclaims
  119386112 allocated bytes with6197 protected files unchanged. See
  [Extra evidence](port64/evidence/extra.md).

- v1309 working tree joins BB tiles, cached character Bomb graphics, shared
  palette14/tone and explicit display scroll to live MAIN. Two physical pages
  retain49..176; foreground actors render after Bomb. Actual OP/finite-STD/X
  drive12 scenes and2,724 Bomb frames per GNU/optimized UBSan. Two-load original
  Bomb bodies agree on state/RNG and252 Bomb-layer indexed captures; complete
  native capture/RGB and repaint pairs agree.34 contracts per host;105 AMD64
  products bind284 files. Game Over322 displays and score-route28 routes regress
  on GNU. Captured pre-Bomb state/page/resources and hardware/audio adapters
  limit the claim: full ordinary routes/whole MAIN are unaccepted. Windows
  builds; actual Windows and Git commits remain environment-blocked.

- v1308 working tree consumes actual Game Over Quit into score-only MAINE,
  preserving delay100 -> registration -> verdict -> song fade4 -> fresh OP.
  GNU/optimized UBSan34 contracts and24 OP/finite-STD combat/contact routes
  plus4 real failed writers pass;224 complete files/136 BMPs agree. Two-load
  original MAINE dispatch/delay uses explicit child-duration/init/sound/exec
  adapters; prior322 Game Over displays re-agree on GNU. Windows AMD64 builds,
  but actual execution is pending under the current WSL socket restriction.
  Git metadata is read-only: changes remain uncommitted. See
  [score-route evidence](port64/evidence/score-registration.md#score-only-maine-quit-route).

- v1307 joins frozen Game Over indexed/TRAM rendering, held keyboard ownership
  and independent refresh pacing to ordinary MAIN. Actual OP selection and
  authored finite STD contact drive20 scenes per GNU/optimized UBSan/actual
  Windows. Two-load original requests/TRAM/score-HUD agree on322 complete
  displays;151 host files agree and34 contracts pass per host.105 AMD64 products
  bind277 files. Quit score-only MAINE, Bomb pixels/shared palette and full HUD
  remain. See [frontend evidence](port64/evidence/stage-lifecycle.md#live-game-over-frontend).
- Normal Stages 1–6 waves/bosses/dialogues/departures and MAINE Ending/Staff/
  verdict/congratulations are implemented with bounded original CPU and native
  integration controls. Complete natural route validation remains pending.
- Live source frontier: v1300 ordered registration scene and separate host score save,
  fresh OP/second MAIN. 30 seeded frontend fixtures on GNU/optimized UBSan/actual
  Windows produce 112 identical files. Each host passes 33 contracts.
- v1300 acceptance had 34 AMD64 products per fast build. Source manifest
  `635698a758e590316b03ebd4d4e45ee222bff3b90cb649e651a2df2af1aa1f58`
  binds 245 implementation/verifier/launcher files. Original score (1,288), menu
  (382), graphics (158 full snapshots) and fade (35+18 refreshes) controls pass.
- Published Windows GUI/launcher remain **v1296-congratulations**, ending at
  `registration_pending`; current GUI source integrates registration, while this
  batch's actual Windows controls use headless child-scene fixtures.
- No physical PC-98, full-route persistence/audio or whole-game acceptance.
- v1301 next-owner component: original player/miss/Bomb producers agree on
  10,319 state/request records at two loads; GNU/optimized UBSan/actual Windows
  pass 34 contracts each. 105 AMD64 products bind 250 source files, manifest
  `dc88a3e9e12c79f7f64b1b8561a7c2455af4dbe12f6e177dbf49ddf1a7b13496`.
  Live death/Bomb and blocking Game Over/Continue are still pending.
- v1302 adds Game Over/menu clocks and MAIN Continue file components: 2,003
  menus, 64 full scenes and 2,985 file controls agree at two original loads and
  GNU/optimized UBSan/actual Windows. Current builds have 35 AMD64 products and
  34 contracts each; 257 files bind manifest
  `85bfb562d43d6328cf738530a13c9320a90ffb2ab21fb0ffb3dda05aa29f3a7c`.
  Live suspension, TRAM graphics and actual Continue host-save integration remain.
- v1303 adds both character Bomb pictures, physical-scroll BB tiles and retained
  star/circle producers. 1,236 original state cases/2,252 records plus294 pixel
  cases/548 complete indexed screens agree at two loads and GNU/optimized UBSan/
  actual Windows. Current105 products bind263 files, manifest
  `c0fbe950be3e6f7a4bf794ea357d0c92d6d1859e8c4684296e77137b47d11751`.
  Live MAIN still needs lifecycle/Bomb/Game Over/Continue integration.
- v1304 adds the Game Over text renderer:200 complete indexed/TRAM/RGB
  snapshots agree against actual original TRAM instructions at two loads;
  GNU/optimized UBSan/actual Windows retain all158 registration captures and
  pass34 contracts each.105 current products bind267 files, manifest
  `7a25a243535773ce3a5bd9eb22cf898511e87cb3daafec96ace8deaae8ab6345`.
  Live MAIN suspension, lifecycle/Bomb dispatch and Continue saving remain.

v1306 adds original player death/invincibility rendering and a retained MAIN
render cache consumed by frontend source. Two-load original caller/helpers and
rolling kernels agree with GNU/optimized UBSan/actual Windows on6,637 requests
and259 complete screens;34 contracts pass per host.105 AMD64 products bind274
listed files. Continue save files remain identical, and cached draws freeze
with Game Over. A changed blink phase is rejected in269 original controls.
2,662,400 allocatedbytes are reclaimed with2,795 protected files unchanged.
GUI Game Over TRAM/keyboard, Bomb graphics and shared lifecycle palette and Quit registration→verdict
remain pending; no published GUI/full natural-route acceptance follows.
See [player rendering evidence](port64/evidence/stage-lifecycle.md#player-death-and-invincibility-rendering).

v1305 joins lifecycle/Game Over suspension, Bomb dispatch, miss pickup suppression
and real MAIN Continue host commits into the core. GNU/optimized UBSan/actual
Windows each pass34 contracts; native checkpoint traces/files agree. A finite
STD/contact/real-store probe verifies one resumed suffix on all three hosts;
a repeated-prefix mutant is rejected. Original10,319 lifecycle records/2,003
menus/64 scenes/2,985 file controls re-agree.105 products bind267 listed files
and two additional verifier digests.87,998,464 allocatedbytes are reclaimed
with2,845 protected files unchanged. GUI Game Over freeze/TRAM and keyboard,
Bomb graphics and score-only registration→verdict→fresh OP still need
joining. Long actor fixtures explicitly disable hit consumption; ordinary GUI
constructors do not. No GUI publication or complete ordinary route is accepted.
See [bounded lifecycle evidence](port64/evidence/stage-lifecycle.md#live-main-lifecycle-suspension-and-continue-persistence).

## Remaining owners

- [x] Ordered registration wait/fade/input/rendering, retained pre-save sections,
  separate host score commits and fresh OP. Audio requests retained; backend pending.
- [x] Join Bomb, hit/death/lives, Game Over and Continue under bounded controls.
  Core lifecycle, frozen Game Over frontend and Bomb graphics/shared
  palette are joined with bounded controls; Quit registration→verdict→fresh OP has bounded GNU/optimized
  UBSan coverage in v1308 and current v1332 Windows score-route controls.
- [ ] Complete ordinary Extra survival and full displays. Both battles/all three
  dialogues, MAINE save and fresh OP/second MAIN are joined under actor controls.
- [x] OP ranking display, held paging/release and retained OP/menu/MAIN return.
- [x] Physical saved-score OP unlock scan and restricted Extra character/shot selection.
- [x] Retained MAIN HUD/resource events and physical highest-score loading,
  with original caller and frozen Game Over/Continue controls.
- [x] Join Music Room, recorded demo, configuration and first audio setup under bounded controls.
- [x] Join OP/MAIN/MAINE sound requests/resources and process lifetimes under bounded controls.
- [ ] Join musical/effect chip ownership, PMD/OPN synthesis, physical clocks,
  real measure waits and full startup audio.
  Beeper offline PCM passes; original OP controller remains a representative Oracle.
- [ ] Validate HUD through ordinary boss routes and host refresh/input/slowdown.
- [ ] Actual Linux/Windows full-route/save/config tests across characters/ranks;
  dense Lunatic timing and independently scoped original comparisons.

General semantic expansion has stopped; clarify only a blocking port contract.

## Build and verification navigation

Use the existing [build commands](../port64/README.md), `port64/CMakeLists.txt`,
`port64/verify.py` and
component `verify_*.py` / `verify_*_windows.ps1` scripts. Detailed invocation
and private-input hashes remain in the component evidence below; do not execute
a historical writer against an existing hard-linked capture directory.
Current caches: `.analysis/port64/{linux,windows,ubsan}-live-v1251`.
Current readback: `.analysis/port64/registration-join-v1300/platform-review.json`.
Latest component readback: `.analysis/port64/gameover-v1302/platform-review.json`.
Latest Bomb readback: `.analysis/port64/bomb-v1303/platform-review.json`.
Latest Game Over graphics: `.analysis/port64/gameover-render-v1304/platform-review.json`.
Use fresh outputs. Keep DOS images/saves, pinned inputs, tools and cache closures.
Periodic cleanup now retires failed/superseded streams and deduplicates verified
immutable captures. v1302 reclaimed 980,566,016 allocated bytes with full hash
readback; final inputs/receipts and three current build caches remain available.

## Evidence index

Each former heading remains here as a stable anchor for ledger/source links.
The linked subject files preserve the detailed claims, negatives, commands and
receipts. Historical version boundaries do not supersede the current state.

[Historical introduction](port64/evidence/core-overview.md).

## Current executable slice

[Detailed evidence](port64/evidence/core.md#current-executable-slice).

## Enemy bullets

[Detailed evidence](port64/evidence/core.md#enemy-bullets).

## Sparks and gather circles

[Detailed evidence](port64/evidence/core.md#sparks-and-gather-circles).

## Verified builds

[Detailed evidence](port64/evidence/core.md#verified-builds).

## Stage 1 midboss

[Detailed evidence](port64/evidence/stage-1.md#stage-1-midboss).

## Stage 1 Orange state and attacks

[Detailed evidence](port64/evidence/stage-1.md#stage-1-orange-state-and-attacks).

## Stage 1 Orange foreground and native integration

[Detailed evidence](port64/evidence/stage-1.md#stage-1-orange-foreground-and-native-integration).

## Dialog VM and natural Stage 1 Boss flow

[Detailed evidence](port64/evidence/stage-1.md#dialog-vm-and-natural-stage-1-boss-flow).

## Stage-clear and all-clear bonus

[Detailed evidence](port64/evidence/stage-lifecycle.md#stage-clear-and-all-clear-bonus).

## Score drain and extends

[Detailed evidence](port64/evidence/stage-lifecycle.md#score-drain-and-extends).

## Player hit, death and Bomb state producer

[Detailed evidence](port64/evidence/stage-lifecycle.md#player-hit-death-and-bomb-state-producer).

## Character Bomb state and graphics

[Detailed evidence](port64/evidence/stage-lifecycle.md#character-bomb-state-and-graphics).

## Stage enter and departure

[Detailed evidence](port64/evidence/stage-lifecycle.md#stage-enter-and-departure).

## Stage actor-session preparation

[Detailed evidence](port64/evidence/stage-lifecycle.md#stage-actor-session-preparation).

## Stage2 midboss and actor integration

[Detailed evidence](port64/evidence/stage-2.md#stage2-midboss-and-actor-integration).

## Stage2 visual resources and dialog

[Detailed evidence](port64/evidence/stage-2.md#stage2-visual-resources-and-dialog).

## Kurumi state and attack core

[Detailed evidence](port64/evidence/stage-2.md#kurumi-state-and-attack-core).

## Kurumi foreground and ray raster

[Detailed evidence](port64/evidence/stage-2.md#kurumi-foreground-and-ray-raster).

## Migration order

[Detailed evidence](port64/evidence/stage-2.md#migration-order).

## Kurumi battle and departure integration

[Detailed evidence](port64/evidence/stage-2.md#kurumi-battle-and-departure-integration).

## Stage3 midboss and pre-Elly integration

[Detailed evidence](port64/evidence/stage-3.md#stage3-midboss-and-pre-elly-integration).

## Elly battle and departure integration

[Detailed evidence](port64/evidence/stage-3.md#elly-battle-and-departure-integration).

## Stage4 resources, midboss and NPC dialogue

[Detailed evidence](port64/evidence/stage-4.md#stage4-resources-midboss-and-npc-dialogue).

## Stage4 Reimu state and orb core

[Detailed evidence](port64/evidence/stage-4.md#stage4-reimu-state-and-orb-core).

## Stage4 Reimu battle and rendering

[Detailed evidence](port64/evidence/stage-4.md#stage4-reimu-battle-and-rendering).

## Stage4 Marisa core

[Detailed evidence](port64/evidence/stage-4.md#stage4-marisa-core).

## Stage4 Marisa battle and rendering

[Detailed evidence](port64/evidence/stage-4.md#stage4-marisa-battle-and-rendering).

## Stage5 resources, stars and Yuuka pre-dialogue

[Detailed evidence](port64/evidence/stage-5.md#stage5-resources-stars-and-yuuka-pre-dialogue).

## Thick-laser state and graphics producer

[Detailed evidence](port64/evidence/stage-5.md#thick-laser-state-and-graphics-producer).

## Stage5 Yuuka core and seven attacks

[Detailed evidence](port64/evidence/stage-5.md#stage5-yuuka-core-and-seven-attacks).

## Stage5 Yuuka foreground and raster controls

[Detailed evidence](port64/evidence/stage-5.md#stage5-yuuka-foreground-and-raster-controls).

## Stage5 Yuuka ordinary battle and route-specific departure

[Detailed evidence](port64/evidence/stage-5.md#stage5-yuuka-ordinary-battle-and-route-specific-departure).

## Stage6 resources, waves and pre-battle dialogue

[Detailed evidence](port64/evidence/stage-6-core.md#stage6-resources-waves-and-pre-battle-dialogue).

## Yuuka6 animation and motion helpers

[Detailed evidence](port64/evidence/stage-6-core.md#yuuka6-animation-and-motion-helpers).

## Yuuka6 cross and safety-circle entities

[Detailed evidence](port64/evidence/stage-6-core.md#yuuka6-cross-and-safety-circle-entities).

## Yuuka6 gathering and attack helpers

[Detailed evidence](port64/evidence/stage-6-core.md#yuuka6-gathering-and-attack-helpers).

## Yuuka6 mirror and core dispatch

[Detailed evidence](port64/evidence/stage-6-core.md#yuuka6-mirror-and-core-dispatch).

## Yuuka6 foreground dispatch

[Detailed evidence](port64/evidence/stage-6-render-flow.md#yuuka6-foreground-dispatch).

## Yuuka6 checkerboard and particle background

[Detailed evidence](port64/evidence/stage-6-render-flow.md#yuuka6-checkerboard-and-particle-background).

## Yuuka6 foreground sprite pixels

[Detailed evidence](port64/evidence/stage-6-render-flow.md#yuuka6-foreground-sprite-pixels).

## Yuuka6 ordinary battle and Final Stage departure

[Detailed evidence](port64/evidence/stage-6-render-flow.md#yuuka6-ordinary-battle-and-final-stage-departure).

## MAINE Ending script and graphics owner

[Detailed evidence](port64/evidence/ending.md#maine-ending-script-and-graphics-owner).

## MAIN-to-MAINE Ending integration

[Detailed evidence](port64/evidence/ending.md#main-to-maine-ending-integration).

## Staff Roll integration

[Detailed evidence](port64/evidence/postgame.md#staff-roll-integration).

## Verdict calculation and clock

[Detailed evidence](port64/evidence/postgame.md#verdict-calculation-and-clock).

## Verdict graphics and integration

[Detailed evidence](port64/evidence/postgame.md#verdict-graphics-and-integration).

## Congratulations and registration entry

[Detailed evidence](port64/evidence/postgame.md#congratulations-and-registration-entry).

## Score-file engine

[Detailed evidence](port64/evidence/score-registration.md#score-file-engine).

## Registration menu control owner

[Detailed evidence](port64/evidence/score-registration.md#registration-menu-control-owner).

## Registration graphics and text plane

[Detailed evidence](port64/evidence/score-registration.md#registration-graphics-and-text-plane).

Latest player-render evidence: `.analysis/port64/player-render-v1306/`;
`platform-review.json` / `readback.py` bind274 files to105 products.
Use `verify_player_render.py` / `verify_player_render_windows.ps1` with fresh
outputs. Player death graphics source is joined; GUI Game Over/Bomb and
score-only MAINE routing still require completion.
