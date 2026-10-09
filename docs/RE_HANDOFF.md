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

Current source manifest:
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

Next finish audio ownership while muted, then full ordinary/Extra routes on
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
