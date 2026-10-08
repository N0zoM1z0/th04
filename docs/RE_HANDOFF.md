# TH04 current handoff

Updated 2026-10-09. Current focus: resumed x64 implementation on its separate
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

The last Windows x64 GUI was v1296 (now archived outside the DOS demo folder): normal stage flow proceeds through Ending,
Staff Roll, verdict and congratulations to `registration_pending`. Later
v1300 source now joins the ordered registration scene, separate host score
commits, fresh OP and second MAIN. GNU/optimized UBSan/actual Windows each
pass 33 contracts and 30 seeded child scenes; 112 output files agree. Prior
1,288 score/382 menu/158 full graphics comparisons pass; original MAINE fades
at decoded-relative `0000:0622..06A3` agree at two loads (35/18 refreshes).
This does not accept full natural routes, physical timing or audio. Native
commits `43946c3`/`6c90c1a` are pushed on `port/modern-64`; its ledgers and
handoff own the detailed evidence.

v1301 player lifecycle and v1302 Game Over/Continue file components now pass
bounded original CPU/GNU/UBSan/actual Windows comparisons. Current builds have
35 AMD64 products and 34 contracts each; native code commit `1610726` is pushed.
v1303 character Bomb graphics now agree on1,236 original CPU state cases/
2,252 records and294 pixel cases/548 screens at two loads, GNU/optimized UBSan/
actual Windows.105 current products bind263 files;34 contracts pass per host.
The source remains a component awaiting live dispatch; no GUI death or full-route
claim follows. Code commit `9a50588` is saved on the native branch.
v1304 Game Over TRAM now agrees on200 complete indexed/text/RGB snapshots at
two original loads and GNU/optimized UBSan/actual Windows. All158 registration
snapshots still agree;34 contracts pass per host.105 products bind267 files.
Text stores and FAR returns execute original instructions; graphics, CGROM and
video-policy adapters remain explicit. This is still a component.
Native code/evidence commits `a789b80`/`5ca7995` are pushed; v1304 cleanup
reclaims398,381,056 allocated bytes. Windows raw retirement is reported
separately as203,511,584 logical bytes; final references/caches remain.
v1305 now joins the native MAIN lifecycle, real last-life suspension, character
Bomb dispatch and Continue host-save callback. GNU/optimized UBSan/actual
Windows each pass34 contracts; checkpoint traces/files and a finite STD/contact
probe agree. Continue resumes one suffix; a repeated-prefix mutation is rejected.
Original10,319 player records/2,003 menus/64 scenes/2,985 file controls re-agree.
105 products bind267 listed files plus two verifier digests.87,998,464 allocated
bytes are reclaimed with2,845 protected files unchanged. Native GUI Game Over
freeze/TRAM/keyboard, death/Bomb graphics and score-only registration followed
by verdict/fresh OP remain pending; long actor probes explicitly disable hit
consumption. No new published GUI or complete ordinary route follows.
Native code/evidence commits `a7c096d`/`6945f69` are pushed on `port/modern-64`.
Next finish these frontend owners, then Extra, full HUD/OP/audio/config and
full-route validation.
Keep native source separate and every launch muted. MAIN database attestation
passes before the next target-dependent batch.
Per the user's request, clean superseded build/capture outputs periodically;
v1302 reclaimed 980,566,016 allocated bytes with hash readback. Preserve pinned
inputs, final receipts and active caches; replay into fresh output directories.

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
