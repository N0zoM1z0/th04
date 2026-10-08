# TH04 native x64 port

Tracking issue: [#1](https://github.com/N0zoM1z0/th04/issues/1).

Updated 2026-10-09. Development has resumed. `port/modern-64` remains separate
from the DOS branch; portable code does not claim PC-98 executable exactness.

## Current state

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

v1305 joins lifecycle/Game Over suspension, Bomb dispatch, miss pickup suppression
and real MAIN Continue host commits into the core. GNU/optimized UBSan/actual
Windows each pass34 contracts; native checkpoint traces/files agree. A finite
STD/contact/real-store probe verifies one resumed suffix on all three hosts;
a repeated-prefix mutant is rejected. Original10,319 lifecycle records/2,003
menus/64 scenes/2,985 file controls re-agree.105 products bind267 listed files
and two additional verifier digests.87,998,464 allocatedbytes are reclaimed
with2,845 protected files unchanged. GUI Game Over freeze/TRAM and keyboard,
death/Bomb rendering and score-only registration→verdict→fresh OP still need
joining. Long actor fixtures explicitly disable hit consumption; ordinary GUI
constructors do not. No GUI publication or complete ordinary route is accepted.
See [bounded lifecycle evidence](port64/evidence/stage-lifecycle.md#live-main-lifecycle-suspension-and-continue-persistence).

## Remaining owners

- [x] Ordered registration wait/fade/input/rendering, retained pre-save sections,
  separate host score commits and fresh OP. Audio requests retained; backend pending.
- [ ] Bomb, hit/death/lives, game-over and Continue.
- [ ] Extra gameplay/boss and complete HUD.
- [ ] OP score/Music Room/demo/unlocks, audio/configuration and pacing.
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
