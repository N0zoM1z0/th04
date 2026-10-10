# TH04 current handoff

Updated 2026-10-10. Current focus: resumed x64 implementation on its separate
branch; DOS demo state is retained. This handoff
indexes verified state; detailed experiments belong in focused notes and CSV
ledgers. General semantic work has reached its stopping condition: resume it
only for an ambiguity that blocks a concrete native port owner.

## Products and claim boundaries

| Product | State | Authority |
| --- | --- | --- |
| Historical reconstruction | OP 93/93, MAIN 493/495, MAINE 72/72, ZUN 3/3 accepted authored functions | [Generated progress](PROGRESS.md), acceptance ledgers |
| Standalone DOS PC-98 game | Four products build from maintained local source without master.lib or ReC98 product includes; repaired normal and invincible variants | [DOS operation](DOS_BUILD.md), [hardware findings](PC98_HARDWARE_REUSE.md) |
| Semantic DOS source | Asset, memory, input/timing, scroll, bullet/VM/shot/item, RNG, score and process contracts clarified | [Semantic summary](SEMANTIC_READABILITY.md) |
| Linux/Windows x64 | Separate `port/modern-64` branch; component-tested normal stages and cutscenes; complete game still unfinished | [Port status and TODO](PORTING_STATUS.md) |

Function acceptance is not whole-file exactness. OP/MAINE/ZUN counts cover
recovered payload functions, not original packed-file extents. MAIN's carpet
and checkerboard cases remain deferred; no acceptance is promoted by the
native fixes or this documentation cleanup. Targets remain
`candidate-local-attested` (a provenance gap).

## DOS verification frontier

- The user reports complete Normal routes/Endings/save and earlier invincible
  Easy/Lunatic runs. These are manual Windows observations.
- Recorded ordinary controls cover startup, OP options/Music Room/config
  persistence, Orange clear, Stage 2 entry, the repaired Kurumi empty-ring
  failure and Stage 3 entry. Seeded Good Endings reach registration and save
  the expected section; their final black frames do not accept fresh OP.
- Upper-left pellet corruption is confirmed and repaired by full EAX clearing;
  seven ordinary checkpoints exclude the old mark. The Stage 6 stripe's
  connection to initial scroll state remains inferred, with user confirmation
  that the stripe disappeared.
- Scalar/CPU/I-O controls reject planar and bullet drawing regressions. A
  440-bullet Lunatic/Turbo fixture measures improvement, including the extreme
  all-cloud phase. It is not a natural full Lunatic route or Windows FPS test.
- Full natural dense Lunatic timing/audio, the optional Windows 36,000-cycle
  profile and a second PC-98 emulator remain validation TODOs. New DOS
  performance work is outside the current native batch.

See [reusable hardware contracts and limits](PC98_HARDWARE_REUSE.md) for each
repair, replay entrypoint and evidence/knowledge routing.

## Native x64 frontier

v1350 fixes final static-menu repaint in both GUI loops. Actual Linux SDL
dummy and Windows offscreen callbacks distinguish the old 24,214 stale pixels/
zero final updates from the fixed zero stale pixels/one update. Three-host
logical full/skip controls agree. All 195 programs rebuild; 64 contracts pass
per host. Four deferred controls enter the manifest after all frozen jobs close.
467 current source inputs bind
`e6911c41c7092c963b526f0494a1b8544b6cbfad675ce9f50fa1391ebacc2d9b`.
New products live in native sibling `port64-presentation-v1350/.analysis/product-v1350/`;
the current branch's source bytes match. Old program/source receipts remain.

Every-refresh drawing now agrees for all four prior ordinary logical prototype
routes on three hosts: 270,193 advances, 37 capture files and physical saves
per host. Complete stock music closes 138 original two-PSP cases; each host's
69 unique native runs compare against both loads, 1,654,542 configured rows.
Fresh current-product replays also pass; part9/PPS counters remain zero and
92 unowned sample-reset cases remain explicit. Native lifecycle/music notes
route the receipts and limits. All relevant jobs have terminal success.

Remaining: public route entry, full startup presentation across sound modes,
other ranks/shots/Continue, physical input/refresh/slowdown and dense Lunatic
performance, audio-device output and current GUI delivery. Stock control/CPU
sample validation does not implement audible playback. All tests stay muted;
candidate-local-attested provenance and DOS acceptance are unchanged.

Historical v1349 frontier:

v1349 verifies four ordinary key-only logical prototype routes on GNU8,
optimized UBSan and actual Windows: Reimu Easy, both Normal characters and
Reimu Extra.270193 route advances/37 capture files perhost and physical final
saves agree. Each host's Normal-earned save admits Extra in a new process.
Legal6life/2bomb settings retain real hits/deaths/Bombs; no Continue or state
injection occurs. GNU every-refresh Easy presentation also agrees.103core
objects per GNU/MinGW are raw-equal to recorded current195product objects.
These are prototype logical routes, not public CLI/GUI/hosttiming acceptance.
Scope/replay: native `docs/port64/evidence/stage-lifecycle.md`.

The completed first-load69stock song cases agree on three hosts:827271rows.
All46part9prefixes/zero observed note/PPS requests and unowned reset writes
are inventoried. Full138two-load producer remains live, not accepted. Current
195program/source identity remains v1348 below; four new note/route replay
files retain separate pins until guarded writers close. Receipts: native
`.analysis/port64/{route-exploration-v1349,game-audio-v1348}/`.
Next finish fullsong/audio usage, integrate public route CLI/fullstartup
presentation, then remaining ranks/shots/Continue and physical host
input/refresh/slowdown/Lunatic performance/new GUI. All launches stay muted;
candidate-local-attested provenance and DOS acceptance remain unchanged.

v1348 repairs shared FM/SSG note rotation after a supplied ST00B mismatch.
457728 original arithmetic calls and3600 legal FM/SSG/FM3 boundary rows agree
on GNU8, optimized UBSan and actual Windows; three source variants reject.
195programs rebuild;64contracts pass perhost. GNU/UBSan regress194238 prior
rows and21103632 resident PCM frames perhost. Current muted frontends produce
336 matching files perhost/equal physical saves; Windows additionally matches
two completed first-load ST00B cases/25626rows. Full138case song producer
`original-dev-v2` remains live; prefix results are not aggregate acceptance.
463 listed inputs bind product manifest
`ba2e588853f852fa5a02886b03383ea25d7664fb5f2eeb75a1d608cef000d845`.
Two note verifiers have separate pins during the producer's tool freeze;
register their manifest entries after guarded writers close. Receipts: native
`.analysis/port64/game-audio-v1348/`; ownership/replay: native
`docs/port64/evidence/pmd-musical-fm.md`. Finish complete song/audio-usage
closure, then startup/natural routes/host timing/new GUI. All runs stay muted;
DOS acceptance and candidate-local-attested provenance remain unchanged.

v1347 closes the recorded independent startup pixel corpus:15 cases/5,879
complete two-page/raw-palette/DAC/shown-RGB frames agree on GNU8, optimized
UBSan and actual Windows.94,400 original clipped SUPER executions and4,311
palette/page checkpoints constrain the adapters. Four renderer variants keep
all prior147,830control rows but fail pixels.461 verifier inputs have manifest
`3af8cef1ce57711a8291548646902831a665cc910fb124dcd4f3af82ea27fb4c`;
195 unchanged programs retain their459-input v1346 producer identity.
Receipts: native `.analysis/port64/startup-pixels-v1347/`; ownership/replay:
native `docs/port64/evidence/op-startup.md`. Full startup integration,
PPS/external ADPCM, natural routes, host timing and new GUI remain open.
All runs stay muted; no physical video/chip or DOS exactness is accepted.

v1346 joins original logo/fireworks/title control and muted frontend startup.
15 two-load cases/147,830 complete state/request rows agree on GNU8,
optimized UBSan and actual Windows; four wrong source variants reject.
Three driver profiles by11 settings and separate-process restarts produce336
matching files perhost; final physical saves agree. A declared finite STD
reaches ordinary Game Over, MAINE and fresh OP without forced lifecycle state.
459 inputs bind195 AMD64 programs;64 contracts pass perhost. Independent startup pixels are covered by v1347 above; full startup
integration, PPS/external ADPCM, natural routes,
host timing and new GUI delivery remain open. No DOS exactness is promoted.

Historical v1346 native source manifest:
`b62c3026fcfa814ccce48906485e6c191c51c760486455421b04fee3c2aaf61f`.
Receipts: native `.analysis/port64/startup-v1346/`; ownership and replay:
native `docs/port64/evidence/op-startup.md` on `port/modern-64`.

v1345 recovers FM3 C6 subtracks, CF slot/voice ownership, C7/C8 detunes,
special pitch and shared mode on all three drivers. FM26 aliases D-F and
restores all four shared tracks after effects;86/B2 append three tracks.
66 distinct two-PSP cases/55,836 complete rows agree on GNU8, optimized UBSan
and actual Windows. Nine wrong source variants reject; the initially
pitch-clipped LFO comparison remains inconclusive in its own receipt.
453 maintained inputs bind192 AMD64 programs;63 contracts pass per host.
GNU/UBSan regress783,936 earlier complete rows, resident services/PCM and
muted frontends; Windows regresses resident/three frontend profiles.
PPS/external ADPCM, full startup, natural routes and host timing remain.
No new GUI, physical chip accuracy or historical exactness is accepted.

v1345 native source manifest: `1689400f6154f6ef377d41357a802a1d6a75129e19449068c81a431e26ef50b0`.
Receipts: native `.analysis/port64/fm3-recovery-v1345/`; ownership, distinct
case accounting, failures and replay: native `docs/port64/evidence/pmd-fm3.md`.
Older producer/consumer identities remain unchanged.

v1344 recovers primary FM B6 feedback and B8 operator total-level commands,
including byte rotation/wrap, masked software state and disabled FM26 parts.
Three original drivers at PSP1000/2000 yield84 cases/101,448 complete rows;
GNU8, optimized UBSan and actual Windows agree. Five source-only variants reject;
two initially inconclusive controls become discriminating with corner inputs.
451 maintained inputs bind189 AMD64 products;62 contracts pass per host.
GNU/UBSan regress602,448 earlier musical/effect rows, resident services and
bounded muted frontend captures. FM3 extra subtracks/slot ownership/special
pitch, PPS/external ADPCM, full startup, natural routes and host timing remain.
All runs remain muted; no new GUI or historical exactness is accepted.

v1344 native source manifest: `81260aeae14b62a1f175844a52a00bb25f122fa938f45524a19b103fb718912b`.
Receipts: native `.analysis/port64/pmd-fm3-v1344/`; ownership and replay:
native `docs/port64/evidence/pmd-musical-fm.md`.
Earlier producer/consumer identities remain unchanged.

v1343 joins CPU-only resident PMD to the actual native frontend. One driver
survives OP/MAIN/MAINE/fresh OP; controls and beeper remain process-local.
Actual capability selects M26/M86, and Ending/Staff waits query the new song's
real measure. All launches stay muted without an audio device/backend.

Original OP controls coupled to the three original COM drivers cover 72 cases
at PSP1000/2000. GNU8, optimized UBSan and actual Windows compare 9,204 complete
records and 21,103,632 FM-mode stereo PCM frames per host; each executes 36
unique service streams. SE2 mixed PCM is host-consistency evidence only.
Three profiles by nine BGM/SE choices each produce 65 equal frontend files on
all hosts, including live Music Room/MAIN and a declared registration child.
Six source-only variants reject; an earlier stale-query variant is inconclusive.
451 maintained inputs bind 189 AMD64 products; 62 contracts pass per host.
Independent control/driver engines share typed buffers, not a physical DOS
address space; PCM arithmetic shares pinned ymfm. No physical chip accuracy,
natural full-route or historical exactness acceptance follows.

v1343 source manifest:
`fded844658566dd8bb32f1298a68664a0f45e55d22676f2e979efe5380cf9964`.
Receipts: native `.analysis/port64/pmd-resident-v1343/`; detailed ownership,
failures and replay: native `docs/port64/evidence/pmd-resident.md`.
Earlier PCM/clock corpora retain their own identities. FM3/PPS/external ADPCM,
full original logo/startup, natural Linux/Windows routes and host
refresh/input/slowdown/Lunatic performance remain unfinished. No new GUI is
published; the last delivered native package remains v1296.
DOS acceptance and candidate-local-attested provenance are unchanged.


Normal six-stage/MAINE, registration/host score/fresh OP,
death/Bomb/Game Over/Continue, Extra actor routes, HUD/unlocks/Scores,
Music Room, demos and configuration/setup are joined under bounded controls.
Extra and the long Ending actor controls disable hit consumption; complete
natural survival remains separate. The last published native GUI remains the
archived v1296 package. See [port status](PORTING_STATUS.md) and the native
branch handoff for the current queue.

Next finish full startup integration and remaining audio ownership
while muted, then full ordinary/Extra routes on
Linux/Windows, saves/restarts, refresh/input/slowdown and dense Lunatic timing.
MAIN's two deferred exactness cases do not gate native functionality.

## Windows DOS demo package

The demo directory retains `start-th04-normal.bat` (ordinary damage) and
`start-th04.bat` (separately compiled invincible MAIN), plus their two unchanged
images/products, standard 24,000-cycle profiles, emulator/font and English
source builder. Independent saves are preserved by full-image hash readback.
Native previews and optional launchers are archived outside that directory.
Windows `Build-TH04.ps1 -CheckOnly -Normal` passes; no rebuild or game launch
was performed. See [retention](ANALYSIS_RETENTION.md) for recovery.

## Working commands

```sh
git status --short
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/build.py --help
python3 scripts/catalog/index.py list --category hardware
python3 scripts/ci.py
git diff --check
```

Only one Borland/Wine writer at a time. Use fresh probe output paths. Follow
[DOS build and testing](DOS_BUILD.md) for publication and Windows fast builds;
[script catalog](../scripts/README.md) for the full command map;
[analysis retention](ANALYSIS_RETENTION.md) before deleting private state.

## Navigation

- [Documentation map](README.md), [architecture](ARCHITECTURE.md),
  [workflow](RE_WORKFLOW.md), [source layout](SOURCE_LAYOUT.md).
- [Evidence index](reconstruction/README.md), [knowledge policy](KNOWLEDGE_BASE.md).
- `config/units.csv`, authored/decoded function ledgers: accepted ownership.
- `config/evidence.csv`, `config/knowledge.csv`: observations and reusable findings.

Historical handoff detail is retained in Git (pre-cleanup `a4f7991`) and the
subject notes. Old build/package names and private receipt paths are provenance,
not the current work queue or a promise of expanded artifact retention.
