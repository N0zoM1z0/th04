# TH04 current handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

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

v1360 adds legal Turbo0 selection and an explicit dense-slowdown route gate.
`--adaptive --rank 3 --turbo 0 --require-dense-slowdown --key-driver xtest`
requires the existing complete six-stage/clear/physical-save/Scores-restart gates,
then complete deadline reduction and actual>=320/>=400 slowdown2 samples. Default
Turbo1/fixed Normal inputs retain their previous behavior. Four unsupported
argument combinations reject before display/game/save creation. Consumer490
inputs (`a07fda7a…`) archive/read back; only route Python differs from v1359,
all485 compiled inputs/program identities remain unchanged. No new build.

One GNU natural ReimuA/Turbo0 trial is live on private Xvfb (tool17095,
controller404173/game404187). Its initial physical CFG is0306020201000000000E;
early Stage0 has35 slowdown2 records/zeroaudio, but max100 bullets is below dense
acceptance. No terminal clear/dense verdict yet. Before polling/restarting,
inspect native `.analysis/port64/slowdown-window-v1360/active-job-v1.json` and
match /proc start ticks/argv; leave pinned route/input/reducer sources unchanged.
Windows GUI/foreground/host input/audio opens remain prohibited.


v1359 accepts GNU natural Lunatic ReimuA on private Xvfb: six stages/noContinue,
88,927 route+790 Scores restart refreshes; section3 real mask1 at physical
rename/final file, registration Esc/freshOP, unchanged CFG/nineother partitions.
Final MAIN frame13,633 has lives2/misses11, score5,179,856. Natural density max440;
>=400 has369 samples/update P95=5.07ms, but Turbo1 yields no dense slowdown2.
Observer/shared-host timing is separate from uninstrumented performance.

Ten actual muted storage/setup processes pass6,305 refreshes/20 physical renames:
WMclose unfinished setup preserves rankFF/noSCR; ordinary setup keys precede
score creation; corrupt CFG/first-last SCR recover; valid tails/ranges/metadata
and two physical restarts pass. GNU scope only; Windows GUI/input stays closed.

The v1358/v1359 jobs are terminal. Independent receipts/frozen490-input consumer
0cd137fd: native `.analysis/port64/host-storage-v1359/`. Actual Lunatic trace:
`.analysis/port64/lunatic-window-v1358/gnu-lunatic-reimu-a-v1/`. Compiled485 inputs
remain unchanged; no new build/Windows/audio opens. Source-backed final caches
retire961 files/net15,634,432 allocated B; [retention](ANALYSIS_RETENTION.md).

v1358 corrects the v1357 UBSan all-clear/admission claim. Unplayed flag0x19
also has bit0; original native OP normalizes masks>3 to0. The old bit-only
comparator accepted that sentinel incorrectly. GNU Normal stores real mask1;
GNU Extra also stores mask1 and retains its accepted no-Continue/full-name route.
UBSan reaches all six stages, then transitions from Final Stage miss13/respawn33
to MAINE without a Game Over scene. Its final physical Normal mask remains0x19,
so good-clear/admission acceptance is revoked. This is consistent with the
compiled Final Stage death-to-Bad-Ending path. Its physical save/Esc/freshOP/
Scores restart, unchanged CFG/nineother partitions and zeroaudio observations
remain valid. Raw old receipts remain historical comparator outputs.

Five corrected checksum-valid mask/snapshot mutants reject, including0x19 with
bit0. Both retained GNU positive routes pass the stronger mask<4+shot-bit gate.
The six-stage verifier now supports ranks1..3/characters0..1/shots0..1 through
ordinary OP selection and optional persistent private XTest keys. Easy's five-
stage ending gate stays separate. The v1358 natural Lunatic ReimuA trial
subsequently completed on unchanged v1356 GNU; the v1359 terminal verdict above
supersedes its pending state. Dense rank3 reductions separate>=320/>=400 and exclude
Normal/Extra/dialog rows; full observer cost remains outside uninstrumented
performance acceptance. Current receipts: native `.analysis/port64/lunatic-window-v1358/`.

The schedule reducer verifies every deadline against preceding after-update
slowdown or recorded resync, plus v1/v2/v3 widths and terminal counts. Native
MAIN includes 3,245/2,765 slowdown2 records; GNU/UBSan observe 2/505 resyncs.
Instrumented CPU/presentation/advice/trace cost remains separate from acceptance
of uninstrumented performance. Five consumer mutants reject wrong deadlines,
wrong row versions, missing termination/stage and checksum-valid lost admission.

GNU Extra v2 completes no-Continue Reimu A with persistent ordinary XTest
keys: 30,388 route refreshes plus 790 independent Scores restart refreshes.
The physical renamed rank4 file contains all eight A gaiji, credit0 and clear
flag; nine other decoded partitions (including earned Normal admission) and CFG
are unchanged. Final MAIN frame27,832 has lives5/misses3. This is GNU private-
Xvfb acceptance; other Extra characters/shots/hosts and Windows remain open.
Extra v1's Game Over at frame25,595 stays failed. Server keymap/request-cost
controls do not prove a causal explanation for that failure. Current receipts: native
`.analysis/port64/window-route-v1357/`; GNU Normal is retained under
`.analysis/port64/full-window-v1356/linux-normal-adaptive-v5/`.

All 27 muted driver/BGM/SE startup combinations pass on GNU/UBSan (32,147
refreshes) on v1355 programs. Windows retains 19 cases only. No Windows GUI,
foreground or host-key retries while the user uses the host. Earlier wrong-map
and corrected fixed/path Game Over failures remain failed. Live advice is const
output; OS input still owns the keys. No game/clock/score/life injection.
All v1357/v1358 jobs are terminal. v1358 active-job receipts retain historical
PID/start/source identity; v1359 records the terminal readback. Do not reuse
stale handles or restart a completed route.

Cold v1356 products retain 485 inputs (`00af24f7…`) and 204 program
identities. GNU/UBSan pass 67 contracts each plus manual held-input
regressions with advice disabled. Windows is cross-compiled only; its
new execution remains unverified. 104/105 GNU/MinGW core objects equal
v1355; only trace serialization changes. Both control-plane CIs pass
(root includes live Ghidra replay/mutations). Historical acceptance
and target provenance are unchanged.

The extracted policy preserves the complete 88,934-tick logical Normal
Reimu A input/state/startup/menu/Ending streams and physical saves.
The v1357 route checks above are independent; no uninstrumented timing follows.

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

Remaining: actual Windows input/startup, other ranks/shots/Endings/Continue,
other Extra characters/shots/hosts, physical refresh/slowdown2 and dense Lunatic performance.
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
