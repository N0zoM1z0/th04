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

v1352 closes ordinary Continue on GNU8, optimized UBSan and actual Windows.
The maintained route plan accepts optional `pilot=1`: stationary held shot,
with ordinary dialog/menu keys and no actor, hit or life-state writes. Physical
Lunatic configuration uses lives option 1/Bombs 0. Each of two scenarios runs
1,551 advances: real deaths, first Game Over/Continue, resumed gameplay, second
Game Over/Esc, registration and fresh OP. Sixteen complete capture files and
physical saves agree per host. Original Game Over at two loads also reproduces
58,424 component requests from the recorded key sequences; unrecorded state
fields remain explicit adapters, not an original whole-route comparison.

The first score is 520 internal units (5,200 displayed points), below the
default leaderboard minimum of 1,000 units. Continue correctly makes no ranked
write. A separately declared
zero-score selected-section fixture accepts and physically saves `CONTINUE`
with the old 520 units before reset. GNU/UBSan observe complete writer-close
snapshots; Windows final files and all recorded states/captures agree. MAIN
frame 432 stays frozen for 189 refreshes, then resumes at 433 once. Second
Game Over freezes frame 630 for 222 refreshes before the quit route.

All 195 current programs build cold and 64 contracts pass per host. GNU and
MinGW each retain 103 raw-equal core objects from v1351. Default pilot B-entry
compatibility passes seven complete files/physical saves on all three hosts;
invalid pilot/trailing plan fields reject before output/save writes. Final
467-input source manifest:
`f0d72042b3f75b2e6305f7afc44454e175d7d28b9181d5517a6b83b40d3f3454`.

Remaining: startup across sound modes, other rank/shot/Continue routes,
physical input/refresh/slowdown, dense Lunatic performance, audio-device output
and current GUI delivery. All runs stay muted. Complete four-route/Hard B and
stock music corpora retain their distinct earlier producer identities; no new
whole original-route, DOS exactness or full-goal acceptance follows.

The v1351 complete four ordinary shot A routes pass on all three hosts:
270,193 advances, 2,504 startup advances, 49 full capture files and equal
physical saves per host. Normal-earned files admit Extra in a new process.
GNU Hard/Reimu B additionally completes 89,114 advances, Ending/registration/
fresh OP; both scopes bind prior source `e3448a63...`. Old wrong-shot/pre-entry
failures remain. New v1352 changes only the route control; retain old accepted
source/program vectors and replay into fresh directories.

Complete supplied music remains accepted in its v1350 scope: 138 original
two-PSP cases, 69 unique native runs per host, 1,654,542 compared rows. Control
and CPU samples do not implement audio-device output. Last installed native
GUI remains v1296; no new package is delivered.

Native replay/ownership: `docs/port64/evidence/stage-lifecycle.md`,
`pmd-musical-fm.md`, `op-startup.md`; private receipts under
`.analysis/port64/natural-continue-v1352/`. Earlier v1351 cleanup reclaims
1,158,561,792 allocated bytes plus 16,347,136 post-CI cache bytes net. New v1352
cleanup separately reclaims 591,622,144 allocated bytes after two full recovery
archive readbacks (3,165 protected hashes, 315 members). Accepted inputs,
captures, physical saves and source vectors remain recoverable. Both final CIs
pass; post-CI source-backed cache pruning separately reclaims 16,347,136 bytes
net. Final readback checks unchanged source/product/corpus/recovery hashes.
Candidate-local-attested provenance and DOS acceptance are unchanged.

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
