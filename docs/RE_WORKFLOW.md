# Working on TH04

Development is paused; see [current handoff](RE_HANDOFF.md) and
[porting TODO](PORTING_STATUS.md). The DOS goal is standalone builds and normal
PC-98 gameplay. Native builds
need not match original executable bytes. Do not reopen MAIN's carpet or
checkerboard exactness cases. Adapt necessary ReC98 shared implementation into
local TH04 source; preserve functional ABI and hardware behavior.

## Start

```sh
git status --short
python3 scripts/preflight.py
python3 scripts/status.py
```

Read [RE_HANDOFF.md](RE_HANDOFF.md) for current blockers and build commands.
For raw target/database work, run `python3 scripts/ghidra.py ARTIFACT check`
before using its observations. Pinned targets identify the supplied Japanese
copy; provenance remains `candidate-local-attested`.

## Implement and build

- Work on one coherent runtime or build problem. Prefer code and executable
  checks to additional narrative documents.
- Keep source under `src/main`, `src/op`, `src/maine`, `src/zun` or shared TH04
  subsystems. Eliminate external source/header dependencies as they migrate.
- Respect near/far calls, Pascal stack cleanup, DGROUP, register ABIs, segment
  groups and 64 KiB bounds. Successful TLINK output alone does not verify them.
- Run only one Borland/Wine build at a time. Worktrees and generated code/data
  belong below ignored `.analysis/`; never change pinned executable bytes.
- `python3 scripts/build.py` builds the four products without historical
  master.lib and publishes them only after every requested build succeeds.
  Build success and runtime acceptance remain separate.
- Use `--only main` and the verified C++ cache for bounded MAIN ASM iterations.
  Finish a source migration with a fresh build before calling it complete.

## Run

`prepare_product_hdi.py` installs build outputs into a copy of the pinned
original-data image. The normal route is GAME.BAT, through ZUN and OP into
MAIN and later MAINE. Directly launching MAINE omits resident setup.

Use recorded input and state checkpoints to validate gameplay progression,
resources, sound and saves. Instrumentation changes timing/layout, so compare
with an uninstrumented build. A screenshot or one marker is a bounded result.
Keep original data and the prepared source image unchanged.

## Historical exact acceptance

The CSV ledgers and [ORACLES.md](ORACLES.md) retain the exact reconstruction
contract. Upstream source, native build success and runtime observations never
promote a historical unit to exact. Only invoke the strict matching workflow
when an exact claim is explicitly in scope; preserve deferred nonexact states.

## Finish

```sh
python3 scripts/ci.py
git diff --check
```

Update the concise handoff when the verified runtime frontier changes. Reusable
findings belong in the evidence/knowledge ledgers; chronological detail is in
Git and private receipts. Commit messages use `gpt-6.1-sol: ...`.
