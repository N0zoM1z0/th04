# TH04 native x64 port

Tracking issue: [#1](https://github.com/N0zoM1z0/th04/issues/1).

Updated 2026-10-05. Development is paused. `port/modern-64` remains separate
from the DOS branch; portable code does not claim PC-98 executable exactness.

## Current state

- Normal Stages 1–6 waves/bosses/dialogues/departures and MAINE Ending/Staff/
  verdict/congratulations are implemented with bounded original CPU and native
  integration controls. Complete natural route validation remains pending.
- Latest source component: v1299 registration graphics/text; 158 full snapshots
  agree GNU/Wine/optimized UBSan/actual Windows under explicit hardware/ROM/PI/
  far-return adapters. Score core (1,288 cases) and logical menu (382) are retained.
- Three fast builds have 33 AMD64 products and 32 passing contracts each. Source
  manifest `e4c55fe9b3c8b02f426349cecac47c976d4a26276d3821cdc7712aba92f6177b`
  binds 238 implementation/verifier files; documentation moves do not change it.
- Published Windows GUI/launcher remain **v1296-congratulations**, ending at
  `registration_pending`; v1297–v1299 are tested components awaiting integration.
- No physical PC-98, complete native persistence/audio or whole-game acceptance.

## Next owners when resumed

- [ ] Ordered registration scene: wait/fade/audio boundaries, explicit host input,
  retained pre-save decoded sections, separate host score persistence, fresh OP.
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
Current readback: `.analysis/port64/registration-render-v1299/platform-review.json`.
Use fresh outputs. Keep DOS images/saves, pinned inputs, tools and cache closures.

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
