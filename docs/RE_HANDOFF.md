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
| OP.EXE | 93 | 14 / 71 / 8 | 11 | 82 | Remaining shared sound owners; SCORE physical TU |
| MAIN.EXE | 495 | 495 / 0 / 0 | 492 | 0, plus 3 blocked | Evidence-triggered side lane only |
| MAINE.EXE | 72 | 14 / 51 / 7 | 11 | 61 | Remaining shared sound owners; SCORE physical TU |
| ZUN.COM | 13 | 3 / 4 / 6 | 0 | 13 | `cfg_init`, ZUNINIT boundary, component link |

The non-MAIN authored backlog is 156 pending acceptances, 21 provisional
boundaries, and 40 unresolved `target-derived-asm` candidate representations.
There is a separate 35-entry OP/MAINE/ZUN original-ASM attestation queue.
`target-derived-asm` does **not** prove original ASM ownership. Corroborated
boundaries still require target-local physical review before exact promotion.

OP and MAINE each have three decoded/link-exact BGIMAGE functions plus eight
artifact-local cold-relinked natural C/C++ shared functions: vram_planes_set(),
frame_delay(), pi_palette_apply(), pi_put_8(), pi_load(), and
snd_pmd_resident(), snd_mmd_resident(), and snd_kaja_interrupt(). Their units.csv
rows stay source-present: DIET-packed files have no honest raw
file offsets for those decoded function bodies. Neither artifact, nor ZUN, has
a file-backed authored-byte percentage yet. MAIN alone has 83,442 / 83,469
reviewed file-backed authored C/C++ bytes exact and 492 / 494 reviewed
authored functions exact. The 27-byte gap is checkerboard `LOOP` 2, Stage 4
carpet 23, and shared `snd_load` encoding 2. It is not the project-wide gate.

The artifact-local decoded-function acceptance plane is implemented and
cold-tested for OP/MAINE BGIMAGE, VRAM, frame-delay, PI, PMD, MMD, and KAJA source plus ZUN resident diagnostics. Run
`python3 scripts/decoded_function_acceptance.py` for its static ledger gate,
or add `--artifact th04-op`, `th04-maine`, or `th04-zun` for a fresh cold
comparison. See the [v508 acceptance contract](reconstruction/packed/TH04_DECODED_FUNCTION_ACCEPTANCE_V508.md).
The **next** source packet is the two remaining reviewed shared sound owners /
205 decoded bytes in each OP/MAINE artifact. Extend the cold backend to compile
their actual source, review each artifact-local extent, and record its own raw
function evidence; do not transfer another artifact's exact credit. Work in small
sound cohorts. Review provisional boundaries and source-origin
questions alongside mature TUs, not as a global gate.

## Replayed facility checks

- OP/MAINE v489 current-snapshot BGIMAGE replay and v494 Reduction #172
  BGM-BSS replay both pass two cold builds per artifact. Ordered target
  relocations remain 804/804 OP and 559/559 MAINE; each decoded program retains
  precisely the shared `snd_load` two-byte residual. `T`/minalloc is exact in
  the v494 control. These are overlay/relink Oracles, **not** standalone TH04
  product builds or whole-packed exactness. Commands, receipts, and limits:
  [non-MAIN replay handoff](reconstruction/packed/TH04_NONMAIN_REPLAY_HANDOFF_V507.md).
- v510 cold-compiles maintained `frame_delay.cpp` independently into OP and MAINE. Both complete 21-byte decoded functions are raw-zero in two rounds; all 804/559 ordered relocations remain exact, and both aggregate linked program images remain identical to v489. The combined decoded wrapper replays five accepted functions per artifact. See the [v510 frame-delay note](reconstruction/packed/TH04_SHARED_FRAME_DELAY_V510.md).
- v511 cold-compiles maintained pi_put.cpp and pi_load.cpp independently into OP and MAINE. Palette, put, and load are raw-zero in both artifacts, all 804/559 ordered relocations remain exact, and aggregate program images remain v489-identical. The combined wrapper now replays eight accepted functions per artifact. Its dispatcher was corrected to name PI backends explicitly and fail closed on unknown IDs; corrected -002 receipts supersede the old combined -001 receipts, while the focused PI evidence itself was unaffected. Borland dependency timestamps are normalized only for OMF determinism, never for raw function acceptance. See the [v511 PI note](reconstruction/packed/TH04_SHARED_PI_V511.md).
- v512 independently cold-compiles maintained pmd_resident.c into OP and MAINE. Both complete 46-byte functions are raw-zero in two rounds, the complete linked images remain v489-identical, and all 804/559 ordered relocations remain exact. See the [v512 PMD note](reconstruction/packed/TH04_SHARED_PMD_V512.md).
- v513 cold-compiles maintained mmd_resident.c plus the already attested zero-code SHARED alignment TU into OP and MAINE. Both complete 47-byte functions are raw-zero in two rounds and all 804/559 ordered relocations remain exact. The only aggregate linked-program difference per artifact is the explicitly excluded post-MMD padding byte (OP 0xDC73, MAINE 0xCF8B); the alignment object has zero LEDATA and does not emit or claim that byte. The fail-closed combined wrapper now executes seven explicit backends and keeps ten accepted functions per artifact raw-zero. See the [v513 MMD note](reconstruction/packed/TH04_SHARED_MMD_V513.md).
- v514 independently cold-compiles maintained kaja_interrupt.cpp into OP and MAINE. Both complete 30-byte functions are raw-zero in two rounds, both linked program images and EXEs remain v489-identical, and all 804/559 ordered relocations remain exact. The fail-closed combined wrapper now executes eight explicit backends and keeps eleven accepted functions per artifact raw-zero. See the [v514 KAJA note](reconstruction/packed/TH04_SHARED_KAJA_V514.md).
- The six BGIMAGE `units.csv` replay commands now use the retained v489 source
  snapshot via `--current-snapshot`; compacted v487/v488 input paths in the
  historical note are not the live command.
- `scripts/probes/replay_th04_zun_source_only.py` now captures transitive local
  headers. Both maintained ZUN C++ TUs compile twice identically: `cfg_init`
  152 CODE bytes, `_main` 246 versus the 252-byte target body. This is only
  source-only compilation. The separate resident component link has now been
  rebased from the deleted v214 inputs to the retained v489 library and seven
  transitive TH04 source/header files; two cold links agree. The linked
  `cfg_init` still has 13 byte differences and `_main` remains nonexact.
  Composite/packed product replay is still missing.
- The [v509 three-artifact cold smoke](reconstruction/packed/TH04_THREE_ARTIFACT_SMOKE_V509.md)
  independently compiles and links maintained VRAM source into OP and MAINE:
  each complete 41-byte decoded function is raw-zero in two rounds with all
  ordered relocations exact. The rebased ZUN `GRAPH_CLEAR` replay also raw-matches
  its complete 36-byte linked support slice, but this library-origin result is
  not an authored exact acceptance; ZUN's authored count remains zero.
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
