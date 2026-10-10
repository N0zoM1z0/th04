# TH04 current handoff

Both final CIs pass, including root live Ghidra replay/mutations. Final readback
checks 8,640 retained hashes. Post-CI cleanup separately retires 1,014 public
source-backed Python caches and preserves their source hashes, reclaiming
16,433,152 allocated bytes net. Cache journal/receipt:
root `.analysis/cleanup/audio-output-post-ci-caches-v1353{,-before}.json`.

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

v1353 implements Linux/Windows host audio transport while every verification
stays muted and never opens a physical backend/device. Default output is muted;
interactive `--audio` is opt-in, and `--mute` dominates in either argument order.
One lazy application device accepts final mixed stereo or nonresident mono;
buffering/failure never clock the game. Production backend API tests use only
explicit fake tables, and frontend PCM uses explicit fake factories.

All 201 current AMD64 programs build cold from 475 maintained inputs; GNU8,
optimized UBSan and actual Windows pass 66 contracts each. Three profiles by
nine BGM/SE settings preserve 195 complete frontend files per host against the
preceding GNU producer. Two ordinary Continue regressions retain 16 captures
and physical final saves per host. The preceding 103 GNU and 103 MinGW core
objects are raw-equal. Three wrong transport variants/four early CLI controls
reject. Current source manifest:
`95ce37f3cfd2a17ec3547e38f5aae71226b2616623e0a79b6cada1772f66ec36`.
The failed MinGW test typedef and mutable-save Windows plan remain recorded;
corrected fresh runs pass. Native replay: `docs/port64/evidence/audio-output.md`;
private receipts: `.analysis/port64/audio-output-v1353/`.

The v1352 natural Continue acceptance remains separate: two 1,551-advance
scenarios per host, real deaths/Continue/resume/second Game Over/Esc,
registration/fresh OP. Ranked and unranked physical files distinguish old
520 units from default minimum 1,000; two-load original Game Over component
replays compare 58,424 requests under documented adapters.

Earlier complete four A routes/Hard B and supplied music keep their earlier
source identities: four routes compare 270,193 advances per host and
Normal-earned saves admit fresh Extra; music compares 138 two-load cases and
1,654,542 configured rows per host. These are not whole-original-route claims.

Remaining: full startup across sound modes, remaining rank/shot routes,
physical input/refresh/slowdown, dense Lunatic timing/performance, physical
sound-device validation and current GUI delivery. No device was opened;
last installed native GUI remains v1296. DOS acceptance/provenance are unchanged.

Scoped v1353 cleanup reports 1,494,827,008 allocated bytes reclaimed; three
recovery archives/all 1,915 members and 8,636 final protected hashes read back.
Sources/products/captures/failures remain recoverable; see
[retention](ANALYSIS_RETENTION.md). Final CI cache pruning is separate.

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
