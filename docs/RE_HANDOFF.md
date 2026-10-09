# TH04 native branch handoff

Updated 2026-10-09. Current phase: finish audio ownership, then complete natural
Linux/Windows routes and timing/performance validation. Native code remains on
`port/modern-64`; DOS source and historical acceptance remain separate.

## Verified current frontier

v1334 adds musical FM state and ordered register requests above the native
sequence owner. GNU8, optimized UBSan and actual Windows each compare175,140
original-backed rows:134,274 supplied-song and40,866 dual-LFO/gate/delay rows.
All53 component contracts pass perhost.403 maintained source inputs bind162
AMD64 programs. Three source-only gain/TimerA/gate variants reject. Existing
short/long sequence, SSG, SSG-sharing and external FM effect controls regress.
Current receipts: native `.analysis/port64/pmd-music-v1334/`; detailed scope:
native `docs/port64/evidence/pmd-musical-fm.md`.

The musical owner covers six FM parts, embedded voices, gates, pitch/slide,
both LFOs, attenuation, delays and all owned mirror/write cells. Effects/music
handover, musical SSG/FM3 extras, ADPCM/rhythm, synthesis, physical clocks,
frontend PMD capability and complete startup remain unfinished. All launches
stay muted; no audio device/backend is opened. DOS acceptance and target
provenance remain unchanged. General semantic expansion resumes only for a
concrete port blocker.

Actual Windows executes90 CPU-only musical traces/87,570 unique rows, compared
against both original PSPs for175,140 rows; no frontend launches in this batch.
v1332's nine muted GNU/actual-Windows frontend controls retain their own
source/product identities and2,015 complete files, physical saves and restart.
Relative to v1333,52 GNU and51 UBSan programs remain unchanged; changed
components regress and all54 relinked Windows programs are freshly attested.
A current Windows GUI/full natural routes/timing remain required.

Cleanup verifies990 protected hashes and all complete compressed traces.
Two interim receipts measure272,588,800 allocated bytes reclaimed (about260MiB);
source-backed caches after both final CIs add17,059,840 bytes (total276.2MiB).
The terminal step's final accounting failed after cleanup; independent recovery
readback passes, and no terminal-step reclaimed-byte estimate is claimed.

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

1. Join running FM music/effects with attested mask/key/voice restoration;
   finish musical SSG/FM3 extras, ADPCM/rhythm, synthesis and real driver measures;
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
Current musical FM originals/consumers and source/product manifests:
`.analysis/port64/pmd-music-v1334/`; stopped external FM effects:
`.analysis/port64/pmd-fm-v1333/`; prior frontend acceptance:
`.analysis/port64/windows-current-v1332/`; sound-scene original producers:
`.analysis/port64/sound-scenes-v1328/`; previous sound-control producer:
`.analysis/port64/audio-v1325/original-linux/`. Completed receipts retain their
own manifests and must never be restamped or overwritten. Detailed commands,
input hashes, adapter limits and negative controls live in the focused notes.

The last published Windows GUI is v1296, archived outside the DOS demo folder;
it is older than this retained source and reaches registration_pending.
Native source/evidence through v1334 remain on the native branch with
separate original/consumer source identities and current replay receipts.
Historical recovery patches remain private and contain public source only,
not assets/tools.

Preserve pinned targets/HDI/font, independent references, recovery archives and
all162 current programs. Periodically retire terminal duplicate captures and
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
