# TH04 native branch handoff

Updated 2026-10-09. Current phase: finish audio ownership, then complete natural
Linux/Windows routes and timing/performance validation. Native code remains on
`port/modern-64`; DOS source and historical acceptance remain separate.

## Verified current frontier

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
3. Validate host refresh/input/slowdown and Windows runtime behavior. Current
   MinGW builds pass; the Windows exit0 probe fails WSL UtilBindVsockAnyPort
   before PowerShell executes. Earlier actualWindows batches do not accept
   current source. Commit/push progress when Git metadata is writable; the
   shared read-only index rejects staging in this environment.

All application launches must stay muted. Do not substitute fictional audio
measure advancement for the original driver's state. General semantic work
resumes only for a specific blocking port contract. No exact promotion follows.

## Replay, private state and delivery

Fast caches: `.analysis/port64/{linux,windows,ubsan}-live-v1251`.
Current original/reference consumers and source/product manifests:
`.analysis/port64/sound-scenes-v1328/`; previous sound-control producer:
`.analysis/port64/audio-v1325/original-linux/`. Completed receipts retain their
own manifests and must never be restamped or overwritten. Detailed commands,
input hashes, adapter limits and negative controls live in the focused notes.

The last published Windows GUI is v1296, archived outside the DOS demo folder;
it is older than this retained source and reaches registration_pending.
Full pending native source/evidence and root-doc recovery is recorded under the
current batch. Recovery patches contain public source only, not assets/tools.

Preserve pinned targets/HDI/font, independent references, recovery archives and
all150 current programs. Periodically retire terminal duplicate captures and
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
