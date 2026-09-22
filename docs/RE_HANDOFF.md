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
| OP.EXE | 93 | 14 / 71 / 8 | 13 | 80 | Shared maintained cohort complete; SCORE physical TU |
| MAIN.EXE | 495 | 495 / 0 / 0 | 492 | 0, plus 3 blocked | Evidence-triggered side lane only |
| MAINE.EXE | 72 | 14 / 51 / 7 | 13 | 59 | Shared maintained cohort complete; SCORE physical TU |
| ZUN.COM | 13 | 13 / 0 / 0 | 0 | 11, plus 2 blocked | ZUNINIT/MEMCHK provenance; external component inputs |

The non-MAIN authored backlog is 152 pending acceptances, 15 provisional
boundaries, and 40 unresolved `target-derived-asm` candidate representations.
There is a separate 35-entry OP/MAINE/ZUN original-ASM attestation queue.
`target-derived-asm` does **not** prove original ASM ownership. Corroborated
boundaries still require target-local physical review before exact promotion.

OP and MAINE each have three decoded/link-exact BGIMAGE functions plus ten
artifact-local cold-relinked natural C/C++ shared functions: vram_planes_set(),
frame_delay(), pi_palette_apply(), pi_put_8(), pi_load(), and
snd_pmd_resident(), snd_mmd_resident(), snd_kaja_interrupt(),
snd_determine_modes(), and snd_delay_until_measure(). Their units.csv
rows stay source-present: DIET-packed files have no honest raw
file offsets for those decoded function bodies. Neither artifact, nor ZUN, has
a file-backed authored-byte percentage yet. MAIN alone has 83,442 / 83,469
reviewed file-backed authored C/C++ bytes exact and 492 / 494 reviewed
authored functions exact. The 27-byte gap is checkerboard `LOOP` 2, Stage 4
carpet 23, and shared `snd_load` encoding 2. It is not the project-wide gate.

The artifact-local decoded-function acceptance plane is implemented and
cold-tested for OP/MAINE BGIMAGE, VRAM, frame-delay, PI, PMD, MMD, KAJA, sound-mode, and delay source plus ZUN resident diagnostics. Run
`python3 scripts/decoded_function_acceptance.py` for its static ledger gate,
or add `--artifact th04-op`, `th04-maine`, or `th04-zun` for a fresh cold
comparison. See the [v508 acceptance contract](reconstruction/packed/TH04_DECODED_FUNCTION_ACCEPTANCE_V508.md).
The maintained reviewed shared hardware/PI/sound cohort is now complete: 13
decoded-exact functions / 840 source-owner bytes in each OP/MAINE artifact.
The next bounded OP/MAINE packet should move to a physically coherent TU such
as SCORE, or to another mature reviewed owner; corroborated/provisional entries
still need target-local physical review before promotion. Do not transfer exact
credit between artifacts.

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
- v515 independently cold-compiles maintained determine_modes.cpp into OP and MAINE. Both complete 156-byte functions are raw-zero in two rounds, both complete linked programs and EXEs remain v489-identical, and all 804/559 ordered relocations remain exact. The fail-closed combined wrapper now executes nine explicit backends and keeps twelve accepted functions per artifact raw-zero. See the [v515 sound-mode note](reconstruction/packed/TH04_SHARED_MODE_V515.md).
- v516 independently cold-compiles maintained delay_until_measure.cpp into OP and MAINE. Both complete 49-byte functions are raw-zero in two rounds, both complete linked programs and EXEs remain v489-identical, and all 804/559 ordered relocations remain exact. MAINE 0xD077 remains function-external linker fill before CDG_PUT_PLANE and receives no delay-owner credit. The fail-closed combined wrapper now executes ten explicit backends and keeps thirteen accepted functions per artifact raw-zero. See the [v516 delay note](reconstruction/packed/TH04_SHARED_DELAY_V516.md).
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
- v518 localizes the resident _main six-byte gap to two missing three-byte dos_puts2 calls: the target selectively preserves bad-option and already-resident calls while sharing only the /R-not-resident path with the no-space call. A two-round supported TC4J profile matrix closes baseline, -O-, -Z-, -G, -v, -y, and -y/-O- as producer explanations. Pinned ReC98 history independently classifies its self-assignment barriers as decompilation no-op workarounds and only speculates about original provenance, so they remain quarantined. _main stays 246/252 source-present; proceed with cfg_init function-local validation and other ZUN ownership work. See the ZUN main note.
- v519 closes cfg_init source/codegen locally without weakening the raw gate: the 152-byte natural object has 15 two-byte OMF FIXUPP fields, and all 30 target/object differences are exactly those fields; every non-fixup byte matches. The current natural resident link still has 13 raw cfg_init differences, all inside those same fixup words because downstream symbols remain six bytes early under the blocked _main layout. cfg_init and _main are now function-level blocked but remain source-present units. Move routine ZUN work to ZUNINIT/MEMCHK ownership and external component inputs. See the cfg_init and ZUN main notes.
- v520 target-reviews the complete ZUNINIT physical partition: eight code extents plus two data islands tile payload 0x6F3..0xB67 exactly. Fresh target disassembly closes every function at JMP/IRET/RET/DOS-exit boundaries and no control-flow edge enters either data island. Candidate TASM PROC entries and the raw-equal target-derived linked component are corroboration only; all ZUNINIT rows remain `target-derived-asm` with no exact credit. ZUN now has 10 reviewed / 3 corroborated / 0 provisional authored boundaries. See the [v520 ZUNINIT note](reconstruction/zun/TH04_ZUNINIT_BOUNDARIES_V520.md).
- v521 target-reviews the three MEMCHK authored functions and keeps payload 0x26CD=00 and 0x26F5=90 as function-external padding. The complete MEMCHK component is raw-equal to the retained candidate link, but the candidate source explicitly identifies itself as IDA-generated; that equality is corroboration only and grants no source or exact credit. All 13 current ZUN authored candidates now have reviewed physical boundaries with 11 target-derived-asm provenance questions still open. See the [v521 MEMCHK note](reconstruction/zun/TH04_MEMCHK_BOUNDARIES_V521.md).
- v522 closes the pinned ReC98 assembly-provenance route for ZUNINIT/MEMCHK: both files enter history as IDA-generated Initial state imports, and MEMCHK's only later path change is the 0FFh-to-255 PI false-positive spelling fix. Therefore the raw-equal candidate-linked components cannot be promoted as original ASM source. The 11 target-derived-asm entries remain unresolved and require independent provenance or natural reconstruction. See the [v522 provenance note](reconstruction/zun/TH04_ZUN_GENERATED_ASM_PROVENANCE_V522.md).
- v523 restores the maintained ZUN support replay chain after the source-only compiler moved from a fixed HEADERS list to transitive source_closure(). Fresh RESDATA and combined GRAPH_CLEAR+RESDATA+FILE_READ cold replays reproduce the historical resident component SHA and 4241 raw target differences, so the support acceptance claims are unchanged. The combined FILE_READ replay is now the live route for shrinking the remaining masters.lib surface.
- v524 localizes the 16-byte library-origin DOS_FREE/MEM_FREE support body as maintained symbolic TASM. Preserving the historical zero-byte _DATA SEGDEF is required for identical MAP topology; it emits no target data. Replacing MASTER archive member index 211 together with GRAPH_CLEAR, RESDATA, and FILE_READ leaves the full resident candidate MAP/component unchanged, while the target DOS_FREE slice is raw-equal. This is library support only and leaves ZUN authored exact=0. See the [v524 DOS_FREE note](reconstruction/zun/TH04_ZUN_DOS_FREE_V524.md).
- v525 localizes library-origin DOS_AXDX. The target function is 0x15 bytes ending RET 4; the containing dosc module is 0x16 bytes because EVEN emits a function-external 0x90 at payload 0x1343. Maintained symbolic TASM reproduces both body and module, keeps MASTER archive index 216, and leaves the full resident candidate MAP/component unchanged. Only the 0x15-byte function is source-present support; ZUN authored exact remains zero. See the [v525 DOS_AXDX note](reconstruction/zun/TH04_ZUN_DOS_AXDX_V525.md).
- v526 localizes library-origin DOS_PUTS2. The target function is 0x27 bytes; the containing module is 0x28 because EVEN emits a function-external 0x90 at payload 0x136B. Two cold TASM objects differ only in a dependency-time COMENT record, while all non-COMENT OMF records, raw module bytes, MAP, archive index 221, and resident component agree. This remains support-only; ZUN authored exact stays zero. See the [v526 DOS_PUTS2 note](reconstruction/zun/TH04_ZUN_DOS_PUTS2_V526.md).
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
