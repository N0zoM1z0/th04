# TH04 reconstruction handoff

Updated 2026-09-23. This is the current-state index, not an experiment log.
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

All four targets and OP/MAINE/ZUN databases passed the 2026-09-23 preflight
and fresh read-only attestation. Target canonicality remains
`candidate-local-attested`, not independently pristine.

## Live state and next action

| Artifact | Authored candidates | Reviewed / corroborated / provisional boundary | Function exact | Pending acceptance | Next surface |
| --- | ---: | ---: | ---: | ---: | --- |
| OP.EXE | 93 | 24 / 61 / 8 | 15 | 78 | hi_view stage and row renderers accepted; rank tail needs special review |
| MAIN.EXE | 495 | 495 / 0 / 0 | 492 | 0, plus 3 blocked | Evidence-triggered side lane only |
| MAINE.EXE | 72 | 26 / 39 / 7 | 20 | 52 | Seven SCORE_TEXT owners accepted; review registration menu or pivot subsystem |
| ZUN.COM | 13 | 13 / 0 / 0 | 0 | 11, plus 2 blocked | `_main` natural CALL shape; ZUNINIT/MEMCHK source authority |

The non-MAIN authored backlog is 143 pending acceptances, 15 provisional
boundaries, and 36 unresolved `target-derived-asm` candidate representations.
There is a separate 35-entry OP/MAINE/ZUN original-ASM attestation queue.
`target-derived-asm` does **not** prove original ASM ownership. Corroborated
boundaries still require target-local physical review before exact promotion.

OP and MAINE each have three decoded/link-exact BGIMAGE functions plus ten
artifact-local cold-relinked natural C/C++ shared functions: vram_planes_set(),
frame_delay(), pi_palette_apply(), pi_put_8(), pi_load(), and
snd_pmd_resident(), snd_mmd_resident(), snd_kaja_interrupt(),
snd_determine_modes(), and snd_delay_until_measure(). Their units.csv
rows stay source-present: DIET-packed files have no honest raw
file offsets for those decoded function bodies. MAINE additionally has the
340-byte SCORE insertion, 230-byte score renderer, 121-byte stage renderer,
172-byte name cursor renderer, 184-byte score-entry row renderer,
26-byte places dispatcher, and 49-byte alphabet cursor renderer;
OP additionally has an 80-byte local stage renderer and a 293-byte
two-column row renderer. Neither artifact, nor ZUN, has
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
Seven MAINE SCORE functions bring MAINE to 20 / 1,962; two OP SCORE renderers
bring OP to 15 / 1,213. Continue adjacent SCORE
owners from target-first boundaries; corroborated/provisional entries
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
- v538 closes the remaining legitimate jump-optimization pragma route for _main. Pinned 4.0J already rejects BCC-style -Od/-O suboptions (v399); file-level pragma option -O- reproduces the known 248-byte -O- build, while an inner disable/restore pair stays at the 246-byte baseline and an unrestored inner pragma again yields 248. None changes bad-option/already-resident from merged JMPs to the target CALLs. _main remains blocked/source-present, not exact. See the ZUN main note.
- v519 closes cfg_init source/codegen locally without weakening the raw gate: the 152-byte natural object has 15 two-byte OMF FIXUPP fields, and all 30 target/object differences are exactly those fields; every non-fixup byte matches. The current natural resident link still has 13 raw cfg_init differences, all inside those same fixup words because downstream symbols remain six bytes early under the blocked _main layout. cfg_init and _main are now function-level blocked but remain source-present units. Move routine ZUN work to ZUNINIT/MEMCHK ownership and external component inputs. See the cfg_init and ZUN main notes.
- v539 revalidates cfg_init on the current compact-MASTER reduced-runtime link. Of the same 15 FIXUPP words, three already equal target and every other one is exactly target minus 6; those 12 shifted words account for all 13 raw byte differences. This proves the present cfg_init residual is fully downstream layout from the six-byte _main blocker, not an independent cfg_init source mismatch. Raw exactness still fails, so cfg_init remains blocked/source-present. See the cfg_init note.
- v520 target-reviews the complete ZUNINIT physical partition: eight code extents plus two data islands tile payload 0x6F3..0xB67 exactly. Fresh target disassembly closes every function at JMP/IRET/RET/DOS-exit boundaries and no control-flow edge enters either data island. Candidate TASM PROC entries and the raw-equal target-derived linked component are corroboration only; all ZUNINIT rows remain `target-derived-asm` with no exact credit. ZUN now has 10 reviewed / 3 corroborated / 0 provisional authored boundaries. See the [v520 ZUNINIT note](reconstruction/zun/TH04_ZUNINIT_BOUNDARIES_V520.md).
- v521 target-reviews the three MEMCHK authored functions and keeps payload 0x26CD=00 and 0x26F5=90 as function-external padding. The complete MEMCHK component is raw-equal to the retained candidate link, but the candidate source explicitly identifies itself as IDA-generated; that equality is corroboration only and grants no source or exact credit. All 13 current ZUN authored candidates now have reviewed physical boundaries with 11 target-derived-asm provenance questions still open. See the [v521 MEMCHK note](reconstruction/zun/TH04_MEMCHK_BOUNDARIES_V521.md).
- v522 closes the pinned ReC98 assembly-provenance route for ZUNINIT/MEMCHK: both files enter history as IDA-generated Initial state imports, and MEMCHK's only later path change is the 0FFh-to-255 PI false-positive spelling fix. Therefore the raw-equal candidate-linked components cannot be promoted as original ASM source. The 11 target-derived-asm entries remain unresolved and require independent provenance or natural reconstruction. See the [v522 provenance note](reconstruction/zun/TH04_ZUN_GENERATED_ASM_PROVENANCE_V522.md).
- v523 restores the maintained ZUN support replay chain after the source-only compiler moved from a fixed HEADERS list to transitive source_closure(). Fresh RESDATA and combined GRAPH_CLEAR+RESDATA+FILE_READ cold replays reproduce the historical resident component SHA and 4241 raw target differences, so the support acceptance claims are unchanged. The combined FILE_READ replay is now the live route for shrinking the remaining masters.lib surface.
- v524 localizes the 16-byte library-origin DOS_FREE/MEM_FREE support body as maintained symbolic TASM. Preserving the historical zero-byte _DATA SEGDEF is required for identical MAP topology; it emits no target data. Replacing MASTER archive member index 211 together with GRAPH_CLEAR, RESDATA, and FILE_READ leaves the full resident candidate MAP/component unchanged, while the target DOS_FREE slice is raw-equal. This is library support only and leaves ZUN authored exact=0. See the [v524 DOS_FREE note](reconstruction/zun/TH04_ZUN_DOS_FREE_V524.md).
- v525 localizes library-origin DOS_AXDX. The target function is 0x15 bytes ending RET 4; the containing dosc module is 0x16 bytes because EVEN emits a function-external 0x90 at payload 0x1343. Maintained symbolic TASM reproduces both body and module, keeps MASTER archive index 216, and leaves the full resident candidate MAP/component unchanged. Only the 0x15-byte function is source-present support; ZUN authored exact remains zero. See the [v525 DOS_AXDX note](reconstruction/zun/TH04_ZUN_DOS_AXDX_V525.md).
- v526 localizes library-origin DOS_PUTS2. The target function is 0x27 bytes; the containing module is 0x28 because EVEN emits a function-external 0x90 at payload 0x136B. Two cold TASM objects differ only in a dependency-time COMENT record, while all non-COMENT OMF records, raw module bytes, MAP, archive index 221, and resident component agree. This remains support-only; ZUN authored exact stays zero. See the [v526 DOS_PUTS2 note](reconstruction/zun/TH04_ZUN_DOS_PUTS2_V526.md).
- v527 localizes library-origin FILE_CREATE at MASTER archive index 172. Putting its globals in _DATA/DGROUP recovers the historical 0x3C LEDATA; TASM5 still uses a different equivalent FIXUPP frame encoding, but final TLINK module bytes, MAP, and full resident candidate are raw-identical. Only the 0x3B function is source-present; trailing payload 0x128B=90 is module alignment. ZUN authored exact remains zero. See the [v527 FILE_CREATE note](reconstruction/zun/TH04_ZUN_FILE_CREATE_V527.md).
- v528 localizes library-origin FILE_ROPEN at MASTER archive index 170. The complete target owner is 0x36 bytes ending RET 2 with no external padding. Local and historical objects share the same zero-placeholder LEDATA and extern ordering; TASM5 differs only in OMF metadata/FIXUPP representation, while final TLINK module bytes, MAP, and resident candidate remain raw-identical. This is support-only and ZUN authored exact remains zero. See the [v528 FILE_ROPEN note](reconstruction/zun/TH04_ZUN_FILE_ROPEN_V528.md).
- v529 localizes library-origin FILE_WRITE at MASTER archive index 171. Target-first decoding corrects the old noncontiguous Ghidra view: the full 0xA6 module is the function owner, and the 0x90 before the direct-write path is internal EVEN alignment rather than trailing padding. Local TASM preserves the target extent, MAP, and resident candidate exactly; ZUN authored exact remains zero. See the [v529 FILE_WRITE note](reconstruction/zun/TH04_ZUN_FILE_WRITE_V529.md).
- v530 localizes the physical filseek member at MASTER archive index 177 as two support functions: FILE_SEEK is 0x33 bytes, payload 0x12BF=90 is function-external alignment, and the previously Ghidra-missed FILE_TELL is a target-reviewed 0x0E-byte function at 0x12C0. One maintained TU reproduces both raw linked functions, the gap, MAP, and resident candidate. ZUN authored exact remains zero. See the [v530 FILE_SEEK/TELL note](reconstruction/zun/TH04_ZUN_FILE_SEEK_V530.md).
- v531 localizes library-origin FILE_APPEND at MASTER archive index 182. The full 0x50 target module is a single function ending RET 2 immediately before DOS_FREE, with no external padding. Local symbolic TASM preserves target bytes, MAP, and the resident candidate exactly; ZUN authored exact remains zero. See the [v531 FILE_APPEND note](reconstruction/zun/TH04_ZUN_FILE_APPEND_V531.md).
- v532 completes the immediate MASTER file-helper support family by localizing the physical filclose member at archive index 167: FILE_FLUSH is 0x6B bytes, payload 0x1165=90 is function-external alignment, and FILE_CLOSE is 0x0E bytes. Together with v325/v527-v531, FILE_READ/FLUSH/CLOSE/ROPEN/WRITE/CREATE/SEEK/TELL/APPEND now have maintained support source and unchanged raw resident MAP/component. ZUN authored exact remains zero. See the [v532 FILE_FLUSH/CLOSE note](reconstruction/zun/TH04_ZUN_FILE_CLOSE_V532.md).
- v533 localizes the fontopen MASTER member at archive index 337: DOS_ROPEN/FONTFILE_OPEN are one 0x18-byte aliased code owner, and the same physical member owns the two-byte file_sharingmode data word. Both final linked sections, MAP, and resident candidate remain raw-identical. This is library support only; ZUN authored exact remains zero. See the [v533 FONTOPEN note](reconstruction/zun/TH04_ZUN_FONTOPEN_V533.md).
- v534 localizes the pure-data VERSION and GRP MASTER members at archive indices 0 and 91. VERSION owns 0x5D target DATA bytes and GRP owns 0x0B; the following zero bytes at payload 0x21F7 and 0x2203 are TLINK alignment outside the owners. GRP preserves its single _Master_Version EXTDEF so VERSION is still pulled by a real dependency. MAP and the full resident candidate remain raw-identical; this is support-only and ZUN authored exact remains zero. See the [v534 VERSION/GRP note](reconstruction/zun/TH04_ZUN_VERSION_GRP_V534.md).
- v535 localizes the physical FIL state member at archive index 163: four initialized target DATA bytes plus 0x14 bytes of uninitialized BSS. BSS receives no invented target-byte extent; it is accepted only through OMF/MAP/link layout. TASM5 reverses the same-address file_BufferPos alias display order, and the replay permits only that exact two-line MAP swap while requiring every other line and the complete resident component to match. ZUN authored exact remains zero. See the [v535 FIL note](reconstruction/zun/TH04_ZUN_FILE_STATE_V535.md).
- v536 closes the external MASTER archive dependency for the ZUN resident. Fifteen already-localized support members are rebuilt into a deterministic 8192-byte compact archive, while GRAPH_CLEAR remains a standalone local object; the external 640-member masters.lib is not read or linked. The same 6360-byte candidate resident is reproduced with 4241 target differences. Remaining external link inputs are c0t.obj, emu.lib, maths.lib, and ct.lib. This is dependency closure only; ZUN authored exact remains zero. See the [v536 compact MASTER note](reconstruction/zun/TH04_ZUN_COMPACT_MASTER_V536.md).
- v537 proves emu.lib and maths.lib are unused by the resident: removing both from the link response changes zero COM or MAP bytes. c0t.obj contributes c0.ASM, while fresh TLIB/MAP classification reduces CT.LIB to exactly 26 pulled runtime members. The remaining external runtime surface is therefore c0t.obj plus CT.LIB; this is compiler/runtime inventory only and ZUN authored exact remains zero. See the [v537 runtime inventory note](reconstruction/zun/TH04_ZUN_RUNTIME_INVENTORY_V537.md).
- v546 replays that reduced-runtime link on current sources and probes the 4,241 ZUN resident same-position byte differences without modifying either binary. The two missing 3-byte `_main` calls and one candidate-only six-zero interval give 6,354 aligned positions: 6,308 equal and 46 still different, all with `±6`, `+3`, or one carry-byte delta. This supports a six-byte layout-cascade hypothesis, not an exact claim or proof of every remaining field's ownership. See the [v546 resident shift note](reconstruction/zun/TH04_ZUN_RESIDENT_SHIFT_V546.md).
- v547 accepts MAINE SCORE_TEXT's adjacent stage renderer at `1A05:259C`, payload `0xC5EC..0xC664`, 121 bytes ending `RET 6`. A reusable bounded SCORE harness independently compiles the maintained TU and overlays only its body into the grouped SCORE producer. Two cold links reproduce the full candidate EXE/MAP, all 559 ordered relocations, and the complete target function. Packed MAINE and surrounding candidate source remain unaccepted. See the [SCORE note](reconstruction/op-maine/TH04_MAINE_SCORE_CPP_V479.md#v547-maintained-stage-renderer-and-reusable-replay).
- v548 accepts the next MAINE SCORE_TEXT cursor renderer at `1A05:2615`, payload `0xC665..0xC710`, 172 bytes ending `RET 6`. The standalone object differs only in the two-byte near-call displacement with an attested OMF fixup; grouped SCORE_TEXT and both cold-linked functions are raw-zero. The full candidate EXE/MAP and 559 ordered relocations remain stable; packed-file and whole-TU exactness remain open. See the [SCORE note](reconstruction/op-maine/TH04_MAINE_SCORE_CPP_V479.md#v548-maintained-name-cursor-renderer).
- v549 accepts MAINE SCORE_TEXT's score-entry row renderer at `1A05:26C1`, payload `0xC711..0xC7C8`, 184 bytes ending `RET 4`. Its two standalone near-call displacement words carry OMF fixups; all other CODE bytes, grouped SCORE_TEXT, and both linked target functions match. Candidate EXE/MAP and 559 ordered relocations remain stable; packed-file and whole-TU exactness remain open. See the [SCORE note](reconstruction/op-maine/TH04_MAINE_SCORE_CPP_V479.md#v549-maintained-score-entry-row-renderer).
- v550 accepts the 26-byte MAINE SCORE_TEXT row dispatcher at `1A05:2779`, payload `0xC7C9..0xC7E2`, ending `RET 2`. Its standalone near-call displacement has an OMF fixup; grouped SCORE_TEXT and both linked target functions are raw-zero. Candidate EXE/MAP and 559 ordered relocations remain stable; packed-file and whole-TU exactness remain open. See the [SCORE note](reconstruction/op-maine/TH04_MAINE_SCORE_CPP_V479.md#v550-maintained-score-entry-row-dispatcher).
- v551 accepts MAINE's 49-byte alphabet cursor renderer at `1A05:2793`, payload `0xC7E3..0xC813`, ending `RET 6`. Standalone TC86 CODE itself equals the grouped owner without fixup exceptions; two cold links reproduce the target function, candidate EXE/MAP, and 559 ordered relocations. The decoded wrapper now covers 20 MAINE slices. The following registration menu is unaccepted, as are the packed file and whole SCORE TU. See the [SCORE note](reconstruction/op-maine/TH04_MAINE_SCORE_CPP_V479.md#v551-maintained-alphabet-cursor-renderer).
- v552 accepts OP's 293-byte two-column row renderer at `1A74:21B5`, payload `0xC8F5..0xCA19`, ending `RET 2`. Standalone natural C++ differs only at five near-call and five data-address OMF fixup words; the complete grouped SCORE_TEXT and both linked target functions are raw-zero. The candidate EXE/MAP and 804 ordered relocations stay stable. The decoded OP wrapper now covers 15 slices; packed-file and whole-TU exactness remain open. The next `rank_render` owner needs the v542 tail-boundary correction. See the [OP hi_view note](reconstruction/op-maine/TH04_OP_HI_VIEW_BOUNDARIES_V542.md#v552-maintained-two-column-row-renderer).
- v540 target-reviews the OP and MAINE scoredat_decode / scoredat_encode / scoredat_recreate physical boundaries independently. Target Ghidra spans, complete disassembly, internal jump closure, adjacent entries, and each artifact's v489 linked bytes all agree. Pinned ReC98 history introduces the logical codec implementations explicitly as Decompilation, so all six rows remain candidate-cpp / unreviewed with no source-present or exact credit. See the [v540 SCORE codec note](reconstruction/op-maine/TH04_SCORE_CODEC_BOUNDARIES_V540.md).
- v541 target-reviews four additional SCORE/high-score owners: OP hiscore_scoredat_load_both and scores_put, plus MAINE hiscore_scoredat_load_for and hiscore_scoredat_save. Target Ghidra spans, complete disassembly, internal branch closure, adjacent entries, and artifact-local v489 linked bytes all agree. Each logical function is directly present in an explicitly Decompilation-labeled ReC98 commit, so all four remain candidate-cpp / unreviewed with no source-present or exact credit. MAINE hi_end physical C++ owners are now reviewed. See the [v541 SCORE high-score note](reconstruction/op-maine/TH04_SCORE_HISCORE_BOUNDARIES_V541.md).
- v542 independently target-reviews OP's five remaining hi_view owners. In `1A74:22DA`, `rank_render` is `0x7A` bytes, not Ghidra's truncated `0x3C`: a target JMP enters the omitted `0x3E`-byte reachable tail and the RET is at payload `0xCA93`. OP boundary counts become 24/61/8; source and exact counts do not change because all five ReC98 logical implementations have explicit decompilation introductions. See the [v542 OP hi_view note](reconstruction/op-maine/TH04_OP_HI_VIEW_BOUNDARIES_V542.md).
- v543 accepts MAINE's first local SCORE source owner: target-reviewed `1A05:2362`, payload `0xC3B2..0xC505`, 340 bytes. Two cold compilations and grouped SCORE_TEXT relinks are raw-zero for this complete function; all 559 ordered relocations and the v489 candidate EXE/MAP remain unchanged. The full MAINE acceptance wrapper passes 14 slices. The packed file, other SCORE owners, and surrounding ReC98 scaffold are not accepted. See the [SCORE insertion note](reconstruction/op-maine/TH04_MAINE_SCORE_CPP_V479.md#v543-maintained-score-insertion-acceptance).
- v544 accepts the next bounded MAINE SCORE renderer at `1A05:24B6`, payload `0xC506..0xC5EB`, 230 bytes ending `RET 4`. Two cold natural-source compilations and grouped relinks match the complete decoded function, leave all 559 ordered relocations and the v489 candidate EXE/MAP unchanged. The full MAINE wrapper passes 15 slices; the surrounding candidate scaffold remains unaccepted. See the [SCORE note](reconstruction/op-maine/TH04_MAINE_SCORE_CPP_V479.md#v544-maintained-score-renderer-acceptance).
- v545 accepts OP's bounded high-score stage renderer at `1A74:2165`, payload `0xC8A5..0xC8F4`, 80 bytes ending `RET 6`. Two cold natural-source compilations and grouped SCORE_TEXT relinks match the whole decoded function, keep all 804 ordered relocations and the v489 candidate EXE/MAP unchanged. The full OP wrapper passes 14 slices; other hi_view candidate source stays unaccepted. See the [OP hi_view note](reconstruction/op-maine/TH04_OP_HI_VIEW_BOUNDARIES_V542.md#v545-maintained-stage-renderer-acceptance).
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
