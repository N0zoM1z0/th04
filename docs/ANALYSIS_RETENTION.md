# Private build and analysis retention

## Current policy

On 2026-10-19 the user authorized permanent retirement of unnecessary historical
experiments and asked to avoid rebuilding large historical cohorts. Keep the
current handoff dependencies and selected independent evidence. The previous
cumulative promise to preserve every inherited provider and replay every phase
is superseded. Historical receipts are unchanged; some named payloads are now
intentionally retired and those receipts are not current replay guarantees.
Earlier versions of this document remain in Git history.

The current private checkpoint is DOS-root:
`.analysis/cleanup/retire-history-20261019/`.
Its `keep.json` records physical identities, `aliases.json` is a flat selected
alias index, and `recover.py` has no dependency on old recovery modules.

```sh
# Run inside the normal serial CPU/memory-limited job.
python3 -B .analysis/cleanup/retire-history-20261019/recover.py
python3 -B .analysis/cleanup/retire-history-20261019/recover.py --restore --path REPO_RELATIVE_PATH
```

Default verification checks the scoped retained handoff. A path absent from the
flat alias index has no recovery promise. Old v1497/storage full-history recovery
commands are obsolete after retirement; do not run or repair them by rebuilding
all their missing experiments. Historical direct readers need their selected
raw inputs restored before use. Remove temporary restored copies after use.

## Keep

- Canonical targets, current game HDI/font/assets, user saves, active Borland/Wine
  and Ghidra environments/databases, active emulator source and binary.
- Maintained root/native source, current source capsules, current 105 program
  paths and 12 object identities, required reused link/compiler inputs, current
  commands/responses and the selected semantic controls. The corrected capsule
  belongs to `host-joystick-v1497-final` despite its wrapper failure; keep it.
- Selected independent capture baselines: the initial original demo, the
  original clock baseline, original-versus-original clock controls, Stage 3
  original/candidate route, source-DOS latch failure and Stage 3 boss original.
  Later original scenarios and recent input/IRQ captures also remain selected.
  `keep.json` records the named capture/probe groups; remaining providers support
  only aliases in the flat index.
- Source capsules, compact experiment scripts/commands/receipts and useful
  negative conclusions. The pinned emulator source archive plus 69 recorded
  source/configuration changes replace two superseded expanded source trees.
- Archives carrying original runtime images, exact-unit replay provenance,
  final reference media, original DOS delivery/save state and old product
  source snapshots. They are distinct from retired development media/previews.

## Retired

The private `plan.json.gz` and `removed.jsonl.gz` enumerate intentionally deleted
paths. `result.json`/`finish.json` record actual allocation and verification.
Retired surfaces include superseded native executables/objects/generated Make
metadata, two old emulator source/build expansions, obsolete Windows preview
packages and development media, redundant early runtime captures and older
probe outputs. Current receipt dependencies and selected alias providers are
excluded before deletion.

This is permanent retirement, not another lossless archive. Full replay of all
old experiments is no longer supported. Historical exactness evidence archives,
canonical targets and active source are retained; this cleanup makes no new
exactness or full-game acceptance claim. Historical observations with retired
payloads must not be reused as freshly replayed evidence.

## Build and verification scope

Build affected translation units/programs only, in fresh output directories.
Run the relevant component comparisons and current frontend smoke checks.
Do not automatically relink every test program, replay all old phases or copy
whole source/build histories into new archives. Expand checks when actual
shared ABI/layout dependencies change; exact promotion still needs all its gates.
The regular `scripts/ci.py` checks the control plane and private target/database
identity when available; it does not build a native product cohort.

Heavy work stays serial: CPUQuota35%, CPU1/Nice19, MemoryHigh256M, MemoryMax768M,
no swap, TasksMax64/LimitCORE0, muted/headless. Use documented compiler exceptions
only when an affected translation unit actually needs rebuilding. Never run
incremental CMake/CTest inside retained/partially retired cohorts.

After an experiment, discard regenerable intermediates, superseded programs and
redundant search captures. Keep concise results and the smallest independent
baseline/counterexample set needed for its maintained claim.

## Cleanup result (2026-10-19)

The retirement removes 65202 files. Whole-directory allocation changes from
16439222272 to 8509648896 bytes before final verification logs: 15.31 to
7.93 GiB, a net reduction of 7.38 GiB in this retirement pass. This excludes
the earlier 2.94 GiB compression savings. The scoped checkpoint contains
4084 physical identities and 4439 selected aliases; 7427 historical aliases
are retired. Current 105 program paths remain physical. No product build or
relink is performed. Final validation and publication are recorded privately
under the checkpoint directory.

Scoped identity verification, six actual SHA/size/mode/nsmtime restorations,
existing GNU/UBSan joystick component programs, root CI (593 tests), native CI
(354 tests) and both diff checks pass. Verification peaks at 269197312 bytes
with no OOM events. Its scoped identity check takes about eight seconds; no
historical aggregate replay or product compilation is invoked.
