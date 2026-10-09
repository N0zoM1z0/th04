# TH04 native branch handoff

Updated 2026-10-10. Current phase: finish audio ownership, then complete natural
Linux/Windows routes and timing/performance validation. Native code remains on
`port/modern-64`; DOS source and historical acceptance remain separate.

## Verified current frontier

v1338 recovers musical D4/D3 effect commands, D2 fade requests and the
next-Timer-B fade-stop boundary in the combined FM/SSG owner. GNU8, optimized
UBSan and actual Windows each match 101,082 complete original rows in 102 cases
at two PSP segments; 51 native traces contain 50,541 unique rows. All 57 component
contracts pass per host. 418 maintained inputs bind 174 AMD64 products. C0 parse
continuation, FM mask silence/restore and repeated effect TL writes during
music fades are recovered. Six source-only counterfactuals reject. Current
receipts: native `.analysis/port64/pmd-commands-v1338/`; detailed scope:
native `docs/port64/evidence/pmd-combined.md`.

The comparison retains all prior FM/SSG fields and chronological owned writes,
including banks and duplicates, plus fade speed/marker/whole request byte/
playing/default fade-stop policy. 17 authored resources per format exercise
masked/unmasked musical effects, zero stops and signed fade boundaries. FM3
extras, PPS, ADPCM/hardware rhythm, synthesis, physical clocks, frontend PMD
capability and complete startup remain unfinished. All launches stay muted;
no audio backend/device opens. DOS acceptance and candidate-local-attested
provenance remain unchanged. General semantic expansion resumes only for a
concrete native blocker.

Actual Windows executes 51 CPU-only traces and 57 contracts; 58 PE products and
inputs are checked before/after. Full readback compares both original PSPs.
GNU/UBsan replay prior 489,390 combined rows and all prior SSG, FM handover/music,
short/long sequence and effect corpora without changing receipt identities.
No GUI launches occur in this batch. v1332's bounded frontend/storage/restart
receipts retain their own identities; full natural ordinary/Extra survival,
current GUI and dense Lunatic timing remain.

Full archive/trace readback verifies 2954 protected hashes; a terminal
snapshot verifies 2277 source/product/cache/compiler/evidence hashes.
Persisted pre-mutation journals measure 676,278,272 allocated bytes reclaimed
(644.9 MiB). Raw copies, negative binaries, Windows staging and
native objects/static archives retire; current 174 products and independent
references remain. CMake rebuilds missing intermediates; fresh replay paths
are required.

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

1. Finish FM3 extras and PPS;
   recover ADPCM/rhythm, synthesis and physical clocks;
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
Current command originals/consumers and source/product manifests:
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
Native source/evidence through v1338 remain on the native branch with
separate original/consumer source identities and current replay receipts.
Historical recovery patches remain private and contain public source only,
not assets/tools.

Preserve pinned targets/HDI/font, independent references, recovery archives and
all 171 current programs. Periodically retire terminal duplicate captures and
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
