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
