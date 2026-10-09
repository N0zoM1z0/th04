# TH04 native branch handoff

Updated 2026-10-09. Current phase: finish audio ownership, then complete natural
Linux/Windows routes and timing/performance validation. Native code remains on
`port/modern-64`; DOS source and historical acceptance remain separate.

## Verified current frontier

v1332 repairs static MinGW runtime inheritance and binary configuration
failure captures. GNU/optimized UBSan and actual Windows each pass all 51
component contracts. Nine fresh muted frontends on current GNU and Windows
agree on 2,015 complete files: sound scenes, score routes, Music Room, Scores,
demos, configuration and first setup, including real physical saves and
separate-process restart. These remain bounded controls, not full natural
route or audio/timing acceptance. 395 maintained files bind 156 AMD64 products.
Git writes/push and Windows execution now work; source through v1331 and the
new repairs are committed/pushed. No new Windows GUI package is published.
Current replay/negative/retention receipts:
`.analysis/port64/windows-current-v1332/`; see
[Windows evidence](port64/evidence/windows-current.md).

v1331's PMD SSG owner remains validated against original effects and music
sharing: 79,488 effect rows, 3,942 sharing rows, 134,274 short sequence rows
and 49,164 longer rows per Linux host. FM/OPN state/synthesis, physical clocks,
real frontend measure waits and complete original startup remain unfinished.
All launches stay muted. General semantic expansion is paused; reopen only
an ambiguity blocking a concrete native owner. DOS acceptance is unchanged.
Current terminal cleanup reclaims about2.06GiB while retaining source,
current caches/programs, inputs, independent references and acceptance logs.

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

1. Implement PMD/OPN music/FM state/synthesis and real driver measure queries;
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
Current original/reference consumers and source/product manifests:
`.analysis/port64/windows-current-v1332/`; sound-scene original producers:
`.analysis/port64/sound-scenes-v1328/`; previous sound-control producer:
`.analysis/port64/audio-v1325/original-linux/`. Completed receipts retain their
own manifests and must never be restamped or overwritten. Detailed commands,
input hashes, adapter limits and negative controls live in the focused notes.

The last published Windows GUI is v1296, archived outside the DOS demo folder;
it is older than this retained source and reaches registration_pending.
Native source/evidence through v1331 and both v1332 fixes are committed and
pushed. Historical recovery patches remain private and contain public source
only, not assets/tools.

Preserve pinned targets/HDI/font, independent references, recovery archives and
all156 current programs. Periodically retire terminal duplicate captures and
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
