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

v1354 fixes SDL keypad Enter held input and catchup resync losing slowdown.
GNU8, optimized UBSan and actual Windows pass 67 contracts each; 204 AMD64
programs build cold from 480 producer inputs. Preceding 104 GNU/MinGW core
objects remain raw-equal; GNU/UBSan's 195 fake-audio frontend files equal v1353.

GNU8/UBSan real SDL/X11 callbacks under private Xvfb pass ordinary Marisa B
entry, Return/keypad Enter, movement/Shift, shots/release and focus gating.
Normal/Shift movement is 64/32 Q12.4 units per frame. Both traces record zero
audio-device opens. Windows foreground acquisition rejects before sending
keys; passing Windows contracts do not accept Windows held-input behavior.

Producer manifest: `e2974686f86f22d2a2a7caaf736b664dd33aac3eae4703aeefbf93a7e9e6ac75`.
Final verifier: `04ec21c37c2039c549b4130b8432693940c9bf53109e1765174204f8dfe4c4c7`.
Only two verifier scripts differ; every compiled input is raw-identical.
Producer receipts and corrected consumer archives retain distinct identities.
Native replay/limits: `docs/port64/evidence/host-window.md`; private current
receipts: `.analysis/port64/host-window-v1354/` in the native worktree.

Earlier scopes remain: four complete A logical routes/Normal-earned Extra,
bounded real Continue/physical host saves/fresh OP, ten-section registration,
Extra/HUD/Scores/Music Room/demo/configuration, supplied PMD music and production
SDL/WinMM transport tested through explicit fake APIs. These do not establish
an original whole route, physical audio, or host timing. No backend/device opens.

Remaining: actual Windows input, startup across sound modes, other rank/shot/
Continue routes, physical refresh/slowdown2, dense Lunatic performance and
physical audio output. The full native goal stays active. A new experimental
muted GUI is delivered in `native-port64-v1354/` under the private demo folder;
all 21 preceding files/saves are unchanged. It is not final GUI acceptance.

Scoped cleanup retires 1,190 build intermediates and 225 terminal owned stage
files after three full archives/299 members read back, reporting 628,129,792
allocated bytes net reclaimed. Current programs/source vectors/captures,
failures, inputs and saves remain. Additional immutable capture sharing keeps
324 paths/hashes and reclaims 210,509,824 allocated bytes net. Post-CI cache
pruning retires 957 files with 15,585,280 allocated bytes net. Both subtract
their journals; final receipt overhead is excluded.

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
