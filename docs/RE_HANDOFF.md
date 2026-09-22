# TH04 reconstruction handoff

Updated 2026-09-22. This is the current-state index, not an experiment log.
The ledgers and generated [progress](PROGRESS.md) are authoritative; old
versioned notes describe their historical packet. The active work plan is
in [RE_ROADMAP.md](RE_ROADMAP.md).

## Resume

Read `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/RE_WORKFLOW.md`, and the
relevant TH04 skill. Then run:

```bash
git status --short --branch
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/audit_compat_dependencies.py --check
python3 scripts/ghidra.py th04-op check  # substitute artifact under review
```

All four targets and OP/MAINE/ZUN databases passed the 2026-09-22 preflight
and fresh read-only attestation. Target canonicality remains
`candidate-local-attested`, not independently pristine.

## Live state and next action

| Artifact | Authored candidates | Reviewed / corroborated / provisional boundary | Function exact | Pending acceptance | Next surface |
| --- | ---: | ---: | ---: | ---: | --- |
| OP.EXE | 93 | 14 / 71 / 8 | 3 | 90 | Shared hardware/PI and sound owners; SCORE physical TU |
| MAIN.EXE | 495 | 495 / 0 / 0 | 492 | 0, plus 3 blocked | Evidence-triggered side lane only |
| MAINE.EXE | 72 | 14 / 51 / 7 | 3 | 69 | Shared owners; SCORE physical TU |
| ZUN.COM | 13 | 3 / 4 / 6 | 0 | 13 | `cfg_init`, ZUNINIT boundary, component link |

The non-MAIN authored backlog is 172 pending acceptances, 21 provisional
boundaries, and 40 unresolved `target-derived-asm` candidate representations.
There is a separate 35-entry OP/MAINE/ZUN original-ASM attestation queue.
`target-derived-asm` does **not** prove original ASM ownership. Corroborated
boundaries still require target-local physical review before exact promotion.

OP and MAINE each have three decoded/link-exact BGIMAGE functions. Their
`units.csv` rows stay `source-present`: DIET-packed files have no honest raw
file offsets for those decoded function bodies. Neither artifact, nor ZUN, has
a file-backed authored-byte percentage yet. MAIN alone has 83,442 / 83,469
reviewed file-backed authored C/C++ bytes exact and 492 / 494 reviewed
authored functions exact. The 27-byte gap is checkerboard `LOOP` 2, Stage 4
carpet 23, and shared `snd_load` encoding 2. It is not the project-wide gate.

The next control-plane packet is an **artifact-local acceptance plane** for
already maintained `src/shared/` functions in OP and MAINE: ten reviewed
owners / 633 decoded bytes in each artifact. Do not transfer MAIN's exact
credit. Review OP/MAINE physical boundaries and create cold replay with
artifact-local bytes, relocation/layout checks, source identity, and durable
function evidence. Work in small hardware/PI and sound cohorts. In parallel,
review provisional boundaries and source-origin questions by related physical
owner; do not halt every mature TU behind a global clearance phase.

## Replayed facility checks

- OP/MAINE v489 current-snapshot BGIMAGE replay and v494 Reduction #172
  BGM-BSS replay both pass two cold builds per artifact. Ordered target
  relocations remain 804/804 OP and 559/559 MAINE; each decoded program retains
  precisely the shared `snd_load` two-byte residual. `T`/minalloc is exact in
  the v494 control. These are overlay/relink Oracles, **not** standalone TH04
  product builds or whole-packed exactness. Commands, receipts, and limits:
  [non-MAIN replay handoff](reconstruction/packed/TH04_NONMAIN_REPLAY_HANDOFF_V507.md).
- The six BGIMAGE `units.csv` replay commands now use the retained v489 source
  snapshot via `--current-snapshot`; compacted v487/v488 input paths in the
  historical note are not the live command.
- `scripts/probes/replay_th04_zun_source_only.py` now captures transitive local
  headers. Both maintained ZUN C++ TUs compile twice identically: `cfg_init`
  152 CODE bytes, `_main` 246 versus the 252-byte target body. This is only
  source-only compilation. The old v214-snapshot ZUN component driver is not
  currently replayable without rebasing its inputs; a maintained-source
  component/packed replay is still needed.
- Same-media DOS/V TC4J backend intake is structurally attested as distinct
  from the PC-98 `TC.EXE`; no dynamic OMF/codegen has been attested, and it
  grants zero MAIN exact credit. See the compiler blocker note.

## Producer constraints and MAIN side lane

Use the v228 **target-derived** DIET restores as OP/MAINE target preimages;
never substitute the v231 restored-candidate inverse control. OP's SCORE
`score_db + score_e + hi_view` and MAINE's SCORE
`score_d + score_hi + complete score` must retain their proved physical TU
composition. The v489 BGIMAGE producer and v494 0xC6 MASTER BGM-BSS
file-backing mechanism close relocation order and load extent in the replay.
The generic `masters.lib` is not ZUN's exact modified MASTER object set.
Do not reopen SCORE order, BGIMAGE FIXUPP order, minalloc, or DIET relocation
sorting without materially new evidence. Private raw-patch controls have no
source acceptance credit.

MAIN's three residuals are documented in the
[checkerboard](reconstruction/main/TH04_MAIN_CHECKERBOARD_V396.md),
[carpet](reconstruction/main/TH04_MAIN_KURUMI_CARPET_V174.md), and
[snd_load / compiler](reconstruction/main/TH04_MAIN_FIXUP_CODEGEN_PROBES.md)
notes. Do not inject target-derived inline assembly to select the missing
instruction forms. Reopen only for independent provenance or a new compiler
mechanism. The public trial has a fail-closed intake gate but no attested
candidate bytes.

## Private state and finish

Keep `.analysis/targets/`, toolchain, retained runtime image, active Ghidra
projects/inputs, receipt archive, and current DIET observations. Keep the
v401, v402, and v489 expanded source snapshots listed in
`config/analysis_retention.toml`. Other `.analysis/gpt-web` runs are disposable
or receipt-only after evidence is durable; old private paths in evidence are
provenance, not a cache-retention promise. Review the dry run before applying:

```bash
python3 scripts/prune_analysis.py --compact-referenced
python3 scripts/prune_analysis.py --apply --compact-referenced
```

For every bounded packet, record artifact, segment:offset, evidence class,
replay command/receipt, exact result, and unknowns in a focused note and
ledger. Finish with focused replay, affected cold aggregate when needed,
`python3 scripts/ci.py`, and `git diff --check`. Do not promote a decoded,
normalized, or target-derived-control match as raw packed-file exactness.
