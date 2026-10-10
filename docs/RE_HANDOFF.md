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

v1351 adds maintained `--natural-route-checks` without private frontend hooks.
Four ordinary shot A routes pass on GNU8, optimized UBSan and actual Windows:
270,193 route advances, 2,504 startup advances, 49 complete capture files
and equal physical saves per host. Every startup/route refresh requests paint;
each host's Normal-earned files admit a new Extra process. This is logical
native consistency, not physical input/clock or an original whole-route claim.

The new Hard/Reimu B check rejects an incorrect horizontal shot-selection key.
The corrected owner uses down and asserts actual character/shot. Independent
GNU corrected-source Hard B completes 89,114 advances, Ending, registration
and fresh OP, with zero Game Over visits; it does not validate real Continue.
The final source has 195 cold programs and 64 passing contracts per host.
Current GNU is byte-identical to the tested Hard B program; all three hosts
verify B entry/16 advances. Final-source four-route replays pass on all three
hosts; all 49 files and physical saves equal the preceding public generation.
Preserve both producer identities and all negative receipts. Final 467-input
source manifest:
`e3448a63fbc299f22c3bffd6e94f4ee3d73e67fa0607c25f49942b910f52b633`.

Remaining: full startup across sound modes,
remaining rank/shot/Continue routes, physical input/refresh/slowdown, dense
Lunatic performance, audio-device output and current GUI delivery. All runs
stay muted. Prior stock music closure and DOS acceptance remain separate.

V1 source `6fdd2b98...` binds 195 cold programs and 64 passing contracts per
host. Its complete four-route corpus is archived separately from final
`e3448a63...` source and the corrected GNU Hard B program. GNU/MinGW each have
103 portable-core objects equal to the preceding v1350 cold build. Source
registration is frozen during each guarded batch; do not modify final listed
source files until new writers/readers close. Old comparisons replay from
archived source snapshots rather than current source.

Complete supplied music remains accepted in the v1350 scope: 138 original
two-PSP cases, 69 unique native runs per host, 1,654,542 compared configured
rows. Music control and CPU samples do not implement audible device output.
The last installed native GUI remains v1296; no new package is delivered.

Replay and ownership: native `docs/port64/evidence/stage-lifecycle.md`,
`pmd-musical-fm.md`, `op-startup.md`; current private receipts under native
`.analysis/port64/public-routes-v1351/`. Two cleanup passes reclaim 1,158,561,792 allocated bytes after four full
archive readbacks. Post-CI source-backed cache cleanup separately reclaims
16,347,136 bytes net; all route inputs/outputs remain.
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
