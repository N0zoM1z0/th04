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
