# TH04 current handoff

Both final CIs pass, including root live Ghidra replay/mutations. Current
host-window/recovery receipts retain distinct producer/consumer identities.
All launches remain muted.

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

v1355 adds a read-only trace v2 score/life/statistics snapshot and an ordinary
X11 Continue/save/restart verifier. 204 AMD64 programs build cold from 481
producer inputs; GNU8, optimized UBSan and actual Windows pass 67 contracts each.
Among 105 GNU/MinGW core objects, only trace serialization changes; 104 remain
raw-equal to v1354. GNU/UBSan's 195 fake-audio frontend files per host also equal
v1354. No audio backend/device opens.

Eight real SDL/X11 processes under private Xvfb pass two stationary Lunatic
Reimu A Continue/Quit/registration/fresh OP cases and two physical-file Scores
restarts per GNU8/UBSan. MAIN freezes at frames 432/630 during Game Over and
resumes at 433; Continue resets score/power/lives/credit. Missing-score/unranked
and declared zero-score/ranked leaderboard fixtures are distinct. Ranked
writer-close/rename snapshots contain CONTINUE 500 units with credit 0 while
MAIN resets to credit 1/score 0. Nine other decoded partitions preserve checksum
and payload; encoding keys legitimately change. Restarts preserve file hashes.
All launches are muted. These are bounded OS-input trials, not complete clear
routes, original whole-route equivalence, physical devices or dense timing.

Producer manifest: `cce4f0fd683c5166f798303e2ebfb83a4fbbe8baef1ee56a862c024c25dbe3be`.
Final verifier: `d027a9701ce8c6168c408bd18a93b72806e60079e87cbf39b7ab8d0ef9267f5c`.
Only the route verifier differs; every compiled input is raw-identical.
Keep the first missing-verdict-key and key-header comparator failures failed.
Current evidence/recovery: native `.analysis/port64/host-route-v1355/`;
replay/limits: native `docs/port64/evidence/host-window.md`.

Actual Windows still rejects before SendInput. PID/class selection now excludes
an early ConsoleWindowClass handle. Same-session WinSta0/Default diagnostics
observe foreground-lock timeout 2147483647 ms; three owned-window activation
attempts fail. No desktop/global policy/input-queue workaround was used.
Passing Windows contracts do not accept Windows held input.

Remaining: actual Windows input, full startup/rank/shot/Normal/Extra/Ending/
Continue window routes, physical refresh/slowdown2 and dense Lunatic performance.
Physical audio remains untested under the user's mute instruction. Existing
v1354 experimental package/user DOS images and saves remain untouched.

v1355 scoped cleanup keeps all 204 programs, producer/consumer source archives,
compiler/CMake metadata, traces, physical files, captures and failed attempts.
It retires 1190 regenerable build files / 70 completed contract-stage files after
two full recovery archives / 144 members read back, net 596836352 allocated bytes.
An independent replay verifies 2847 protected hashes and all 1260 absent files.
The three earlier desktop stages retire 20 files, net 35110912 bytes; the terminal
GUI stage and archived failed consumer materialization retire 494 files,
net 22450176 bytes. Immutable capture sharing keeps 324 complete BMP/PCM paths
and hashes, net 210509824 bytes. Counts subtract their journals/archives but
exclude final receipt size. No original input, accepted program or save deleted.
Post-CI pruning retires 1020 source-backed Python caches, net 16822272 allocated
bytes; root `.analysis/cleanup/host-route-post-ci-caches-v1355.json` records
source/hash readback. Both CIs pass, including root live Ghidra replay/mutations.

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
