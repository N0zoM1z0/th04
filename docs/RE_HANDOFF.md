# TH04 native branch handoff

Updated 2026-10-10. Current phase: finish audio ownership, then complete natural
Linux/Windows routes and timing/performance validation. Native code remains on
`port/modern-64`; DOS source and historical acceptance remain separate.

## Verified current frontier

v1341 adds resident master-cycle scheduling and rational nanosecond time.
GNU8, optimized UBSan and actual Windows each match 283,494 complete original
rows in 174 scenarios across two PSPs and three drivers. Windows executes 87
unique traces/141,747 rows and compares both original loads. All 60 component
contracts pass per host. 430 inputs bind 183 AMD64 products. Independent
pinned ymfm also matches 2,448 cold-chip rows across three boards/16 initial B
phases; time partitions retain 1,285 complete IRQ rows. Five source-only
variants reject; an equivalent variant is retained as inconclusive. Prior
timer-register 80,040 rows replay per GNU/UBSan. All producer/consumer handles
are terminal zero. Disjoint cleanup reclaims 1,018,875,904 allocated bytes
(971.7 MiB) while preserving current products and replay evidence.
Receipts: native `.analysis/port64/pmd-time-v1341/`; details: native
`docs/port64/evidence/pmd-clock.md`.

Current source manifest:
`e5f6d215587b8fe1258b62443a9cbfac3f710fe7db4d9f6d21cc3d0d2fd7440a`.
Acknowledge and tempo writes preserve live deadlines; overflow reloads before
IRQ work; music stop/restart retains resident phase. Nanoseconds retain their
rational remainder. Frequency, initial FM epoch and coincident zero-latency
IRQ remain explicit adapters, not physical board timing acceptance.
Synthesis, other required driver owners, actual resident frontend lifetime,
capability/measure waits and full startup remain unfinished. All runs stay
muted with no audio device/backend. Linux GUI hashes are unchanged; Windows
relinks have bounded CPU controls only. No new GUI or natural-route acceptance
occurs. DOS acceptance and candidate-local-attested provenance are unchanged.

See [OP/MAINE scene evidence](port64/evidence/sound-scenes.md), [MAIN sound evidence](port64/evidence/sound-main.md), [beeper evidence](port64/evidence/beeper.md) and
[sound-control evidence](port64/evidence/sound-control.md).

| Joined native owner | Verified scope | Evidence |
| --- | --- | --- |
| Registration and host scores | Ordered waits/fades/input/render, ten sections, Esc/full name, failed writers, physical save/fresh OP | [Registration](port64/evidence/score-registration.md) |
| Death/Bomb/Game Over/Continue | Core lifecycle, frozen display/input, actual Continue saving, Bomb foreground/palette; bounded controls | [Lifecycle](port64/evidence/stage-lifecycle.md) |
| Normal stages and MAINE | Six stages/bosses, both Stage4 character battles, eight Ending routes, Staff Roll/verdict/congratulations; bounded controls | [Port overview](PORT64.md) |
| Extra | Actual STD/resources, midboss, Mugetsu/Gengetsu, three dialogues, MAINE/save/fresh OP under actor controls | [Extra](port64/evidence/extra.md) |
| HUD/unlocks/Scores | Retained HUD, physical selected high score, OP rank/combination unlocks and paging | [HUD](port64/evidence/hud.md), [OP scores](port64/evidence/op-score.md) |
| Music Room/demo | Retained menu/playing state; four original recorded demos, physical-key/frame3996 exits | [Music Room](port64/evidence/op-music.md), [Demo](port64/evidence/demo.md) |
| Configuration/first setup | Original load/save boundaries, atomic host storage, interrupted/failed setup and separate process restart | [Configuration](port64/evidence/configuration.md), [Setup](port64/evidence/setup.md) |

These are bounded component/integration results, not complete natural game
acceptance. Extra actor controls disable hit consumption; physical OP score
controls separately establish real unlocks. The v1310/earlyv1312 character
selection negative remains recorded; corrected RIGHT input supersedes the
old claimed two-character frontend coverage.

## Remaining owners, in order

1. Join real clock scheduling to the recovered resident timer writes;
   recover synthesis and the remaining FM3/PPS/ADPCM owners;
   join original driver measures to frontend capability;
   complete original logo/startup audio and attest driver initialization/finish.
   OP/MAIN/MAINE scene requests, process lifetimes and muted beeper are joined
   under bounded controls; absent drivers supply no fictional measures.
2. Verify complete natural Linux/Windows routes for both characters and ranks,
   good/bad Ending, Extra survival/clear, Continue, saves/config and restart.
   Ordinary boss/HUD/lifecycle coverage and dense Lunatic performance remain.
3. Validate host refresh/input/slowdown, dense Lunatic performance and deliver
   an updated Windows GUI after the required complete-route acceptance.
   v1332 accepts current Windows bounded controls; it does not accept full
   ordinary/Extra survival or physical clock equivalence. Git is writable.

All application launches must stay muted. Do not substitute fictional audio
measure advancement for the original driver's state. General semantic work
resumes only for a specific blocking port contract. No exact promotion follows.

## Replay, private state and delivery

Fast caches: `.analysis/port64/{linux,windows,ubsan}-live-v1251`.
Current timer originals/consumers and source/product manifests:
`.analysis/port64/pmd-clock-v1340/`; prior rhythm owner:
`.analysis/port64/pmd-rhythm-v1339/`; prior command owner:
`.analysis/port64/pmd-commands-v1338/`; prior combined owner:
`.analysis/port64/pmd-combined-v1337/`; prior musical SSG owner:
`.analysis/port64/pmd-musical-ssg-v1336/`; prior joined FM owner:
`.analysis/port64/pmd-fm-join-v1335/`; musical FM component:
`.analysis/port64/pmd-music-v1334/`; stopped external FM effects:
`.analysis/port64/pmd-fm-v1333/`; prior frontend acceptance:
`.analysis/port64/windows-current-v1332/`; sound-scene original producers:
`.analysis/port64/sound-scenes-v1328/`; previous sound-control producer:
`.analysis/port64/audio-v1325/original-linux/`. Completed receipts retain their
own manifests and must never be restamped or overwritten. Detailed commands,
input hashes, adapter limits and negative controls live in the focused notes.

The last published Windows GUI is v1296, archived outside the DOS demo folder;
it is older than this retained source and reaches registration_pending.
Native source/evidence through v1340 remain on the native branch with
separate original/consumer source identities and current replay receipts.
Historical recovery patches remain private and contain public source only,
not assets/tools.

Preserve pinned targets/HDI/font, independent references, recovery archives and
all 180 current programs. Periodically retire terminal duplicate captures and
regenerable caches only after hashes and full byte comparison; shared hardlinks
are immutable. Restore or use a fresh output directory before replaying.

```sh
python3 scripts/preflight.py
python3 scripts/ci.py
git diff --check
```

Use [README](../port64/README.md), [port overview](PORT64.md) and the focused
notes for build/verification commands. Run target database checks in the root
checkout, which owns the attested Ghidra/JDK tools. Target canonicality remains
candidate-local-attested. Historical unit/decoded-function ledgers are unchanged.
