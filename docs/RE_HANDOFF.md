# TH04 native branch handoff

Updated 2026-10-10. Current phase: finish audio ownership, then complete natural
Linux/Windows routes and timing/performance validation. Native code remains on
`port/modern-64`; DOS source and historical acceptance remain separate.

## Verified current frontier

v1339 joins hardware rhythm to musical FM/SSG/effect ownership. GNU8,
optimized UBSan and actual Windows each match 199,266 complete original rows:
174 primary cases/172,434 rows and 24 supplemental cases/26,832 rows at two
PSP segments. All 58 component contracts pass per host. 422 maintained inputs
bind 177 AMD64 products. Drum/retrigger order, explicit key counters, stored
pan/levels, attenuation and byte-wrap arithmetic are recovered. Negative fade
underflow restores rhythm total before Timer A effect work. Seven source-only
counterfactuals reject. Receipts: native `.analysis/port64/pmd-rhythm-v1339/`;
scope: native `docs/port64/evidence/pmd-rhythm.md`.

The complete comparison preserves previous FM/SSG/fade fields and chronological
writes, plus rhythm track/globals/counters and primary mirrors 10..1F. Longer
512-tick command controls reach tails skipped by the primary restart timeline;
explicit overflow fixtures reject widened additions. The wrong initial music
base/map views and nondiscriminating short mutants remain inconclusive.
FM3 extras, PPS, ADPCM, synthesis, physical clocks, frontend driver capability/
real measure waits and complete logo/startup remain unfinished. All runs stay
muted; no audio backend/device opens. DOS acceptance and candidate-local-attested
provenance remain unchanged.

Actual Windows executes 99 unique CPU-only traces/99,633 rows; full readback
compares both original PSPs. 59 PE products and inputs are checked before/after.
GNU/UBSan replay prior command/combined/SSG/FM/sequence/effect corpora against
unchanged reference identities. Linux frontends keep their preceding binary
hashes; MinGW relinks have new identities and bounded CPU controls. No GUI
launch or new complete-route acceptance occurs. Natural ordinary/Extra survival,
host timing/slowdown, dense Lunatic performance and current GUI remain.

Full archive/trace readback verifies 3915 protected hashes. Persisted journals
measure 850,616,320 allocated bytes reclaimed (811.2 MiB), including
terminal raw copies, counterfactual programs, owned Windows stages and native
objects/static archives. Space accounting uses corrected 512-byte block units;
the earlier helper/receipt remains. All 177 current products, source identities
and independent references remain. Use fresh replay paths; CMake regenerates
missing intermediates.

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
   recover ADPCM, synthesis and physical clocks;
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
Current rhythm originals/consumers and source/product manifests:
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
Native source/evidence through v1339 remain on the native branch with
separate original/consumer source identities and current replay receipts.
Historical recovery patches remain private and contain public source only,
not assets/tools.

Preserve pinned targets/HDI/font, independent references, recovery archives and
all 177 current programs. Periodically retire terminal duplicate captures and
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
