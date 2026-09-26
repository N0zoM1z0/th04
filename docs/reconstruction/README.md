# Reconstruction evidence notes

These notes explain bounded target observations, compiler experiments, replay
receipts, and unresolved producer questions. They support the ledgers; they do
not define current progress or exactness by themselves.

Versioned notes are historical snapshots unless explicitly listed as active.
Historical .analysis/reconstruction/probes/... paths record where evidence was
produced; the expanded worktree may have been pruned after its receipt and
digests were archived. Re-run the checked-in command or restore the private
receipt archive rather than treating a missing probe directory as missing
source evidence.

## Active frontiers

Only the links in this section and `docs/RE_HANDOFF.md` describe the current
frontier. Versioned notes outside this list are historical snapshots and may
contain residual counts that were correct only at that packet.

### MAIN.EXE (reference only; not current campaign)

- [Checkerboard counted-LOOP blocker](main/TH04_MAIN_CHECKERBOARD_V396.md)
- [Stage 4 carpet low-level producer blocker](main/TH04_MAIN_KURUMI_CARPET_V174.md)
- [snd_load DS/MOV analysis](main/TH04_SND_LOAD_DS_V391.md)
- [Cross-cutting compiler/FIXUPP negatives](main/TH04_MAIN_FIXUP_CODEGEN_PROBES.md)
- [Public trial provenance intake](main/TH04_TRIAL_PROVENANCE_V500.md)

### OP / MAINE / packed artifacts

- [OP/MAINE/ZUN decoded-function acceptance plane](packed/TH04_DECODED_FUNCTION_ACCEPTANCE_V508.md)
- [Three-artifact cold function smoke and acceptance limits](packed/TH04_THREE_ARTIFACT_SMOKE_V509.md)
- [OP/MAINE shared frame-delay decoded acceptance](packed/TH04_SHARED_FRAME_DELAY_V510.md)
- [OP/MAINE shared PI decoded acceptance](packed/TH04_SHARED_PI_V511.md)
- [OP/MAINE shared PMD resident decoded acceptance](packed/TH04_SHARED_PMD_V512.md)
- [OP/MAINE shared MMD resident decoded acceptance](packed/TH04_SHARED_MMD_V513.md)
- [OP/MAINE shared KAJA interrupt decoded acceptance](packed/TH04_SHARED_KAJA_V514.md)
- [OP/MAINE shared sound-mode decoded acceptance](packed/TH04_SHARED_MODE_V515.md)
- [OP/MAINE shared delay-until-measure decoded acceptance](packed/TH04_SHARED_DELAY_V516.md)
- [OP/MAINE shared input-wait decoded acceptance and compact replay snapshots](packed/TH04_SHARED_INPUT_WAIT_V565.md)
- [OP/MAINE shared polar / vector2_at decoded acceptance](op-maine/TH04_SHARED_VECTOR_MATH_V570.md)
- [MAINE 50-byte cutscene helper boundary at payload 0xA815](op-maine/TH04_MAINE_BOX_ANIMATE_BOUNDARY_V572.md)
- [MAINE indirect-dispatch function boundary at payload 0xA847](op-maine/TH04_MAINE_SCRIPT_OP_BOUNDARY_V571.md)
- [MAINE script dispatcher natural-C++ exact replay](op-maine/TH04_MAINE_SCRIPT_OP_EXACT_V685.md)
- [MAINE cutscene animation natural-C++ exact replay](op-maine/TH04_MAINE_CUTSCENE_ANIMATE_EXACT_V687.md)
- [MAINE sound-effect function boundaries](op-maine/TH04_MAINE_SND_SE_BOUNDARIES_V699.md)
- [MAINE staff background expansion helper natural-C++ exact replay](op-maine/TH04_MAINE_STAFF_BG_HELPER_EXACT_V700.md)
- [MAINE staffroll animation exact replay](op-maine/TH04_MAINE_STAFFROLL_ANIMATE_EXACT_V702.md)
- [MAINE skill percentage exact replay](op-maine/TH04_MAINE_SKILL_PERCENTAGE_EXACT_V706.md)
- [MAINE million-fraction renderer exact replay](op-maine/TH04_MAINE_MILLION_FRACTION_EXACT_V708.md)
- [MAINE sub_B81D exact replay](op-maine/TH04_MAINE_SUB_B81D_EXACT_V711.md)
- [MAINE sub_B9F2 physical ownership and exact replay](op-maine/TH04_MAINE_SUB_B9F2_EXACT_V714.md)
- [MAINE verdict owner exact replay and BB81 boundary correction](op-maine/TH04_MAINE_VERDICT_OWNER_EXACT_V717.md)
- [MAINE SCORE tail boundary/source-admissibility review](op-maine/TH04_MAINE_SCORE_TAIL_SOURCE_REVIEW_V720.md)
- [MAINE strict-source frontier after v730-v732](op-maine/TH04_MAINE_STRICT_FRONTIER_V732.md)
- [TC4.02 SCORE rotate-intrinsic negative surface](op-maine/TH04_SCORE_ROTATE_INTRINSICS_V760.md)
- [BGIMAGE hybrid producer / relocation closure](op-maine/TH04_BGIMAGE_HYBRID_V489.md)
- [OP big menu/title exact replay](op-maine/TH04_OP_BIG_MENU_TITLE_EXACT_V735.md)
- [OP main-menu producer boundary correction and exact replay](op-maine/TH04_OP_MAIN_REMAINING_EXACT_V742.md)
- [OP setup submenu exact replay](op-maine/TH04_OP_SETUP_SUBMENUS_EXACT_V745.md)
- [OP Music Room remaining exact replay](op-maine/TH04_OP_MUSIC_REMAINING_EXACT_V748.md)
- [OP ZUNSOFT current natural-C++ owner exact replay](op-maine/TH04_OP_ZUNSOFT_NATURAL_EXACT_V753.md)
- [OP strict natural-source frontier](op-maine/TH04_OP_STRICT_FRONTIER_V766.md)
- [OP egcrect physical-boundary closure](op-maine/TH04_OP_EGCRECT_BOUNDARIES_V757.md)
- [OP op_main.cpp remaining functions exact replay](op-maine/TH04_OP_MAIN_REMAINING_EXACT_V742.md)
- [OP remaining m_char.cpp exact replay](op-maine/TH04_OP_MCHAR_REMAINING_EXACT_V738.md)
- [OP historical SCORE_TEXT producer](op-maine/TH04_OP_SCORE_GROUP_V488.md)
- [OP/MAINE score codec boundary / provenance review](op-maine/TH04_SCORE_CODEC_BOUNDARIES_V540.md)
- [OP/MAINE SCORE high-score boundary / provenance review](op-maine/TH04_SCORE_HISCORE_BOUNDARIES_V541.md)
- [OP hi_view boundary correction, provenance, and accepted stage renderer](op-maine/TH04_OP_HI_VIEW_BOUNDARIES_V542.md)
- [MAINE SCORE natural C++ and decoded acceptance](op-maine/TH04_MAINE_SCORE_CPP_V479.md#v543-maintained-score-insertion-acceptance)
- [DIET MZ partition / derived minalloc](packed/TH04_DIET145F_MZ_PARTITION_V231.md)
- [Packed BGM-BSS file-backing mechanism](packed/TH04_BGM_BSS_FILEBACK_V492.md)
- [ZUN-modified MASTER provenance](packed/TH04_ZUN_MASTER_VERSION_V493.md)
- [BGM BSS Reduction #172 provenance](packed/TH04_BGM_BSS_REDUCTION172_V494.md)

### ZUN.COM

- [ZUN resident main](zun/TH04_ZUN_MAIN_V241.md)
- [ZUN standalone component link](zun/TH04_ZUN_COMPONENT_LINK_V317.md)
- [ZUNINIT physical boundary review](zun/TH04_ZUNINIT_BOUNDARIES_V520.md)
- [ZUNINIT Shift-JIS converter semantic Oracle](zun/TH04_ZUNINIT_SJIS_V777.md)
- [ZUNINIT text VRAM writer runtime Oracle](zun/TH04_ZUNINIT_TEXT_VRAM_V778.md)
- [ZUNINIT text support symbolic ASM owner](zun/TH04_ZUNINIT_TEXT_SUPPORT_ASM_V779.md)
- [MEMCHK physical boundary review](zun/TH04_MEMCHK_BOUNDARIES_V521.md)
- [ZUN MEMCHK DOS_PUTS2 source-owner correction](zun/TH04_ZUN_MEMCHK_DOS_PUTS2_OWNER_V769.md)
- [ZUN MEMCHK natural source ownership and first authored exact function](zun/TH04_ZUN_MEMCHK_NATURAL_EXACT_V773.md)
- [ZUNINIT/MEMCHK generated-assembly provenance](zun/TH04_ZUN_GENERATED_ASM_PROVENANCE_V522.md)
- [ZUN DOS_FREE library replacement](zun/TH04_ZUN_DOS_FREE_V524.md)
- [ZUN DOS_AXDX library replacement](zun/TH04_ZUN_DOS_AXDX_V525.md)
- [ZUN DOS_PUTS2 library replacement](zun/TH04_ZUN_DOS_PUTS2_V526.md)
- [ZUN FILE_CREATE library replacement](zun/TH04_ZUN_FILE_CREATE_V527.md)
- [ZUN FILE_ROPEN library replacement](zun/TH04_ZUN_FILE_ROPEN_V528.md)
- [ZUN FILE_WRITE library replacement](zun/TH04_ZUN_FILE_WRITE_V529.md)
- [ZUN FILE_SEEK / FILE_TELL library replacement](zun/TH04_ZUN_FILE_SEEK_V530.md)
- [ZUN FILE_APPEND library replacement](zun/TH04_ZUN_FILE_APPEND_V531.md)
- [ZUN FILE_FLUSH / FILE_CLOSE library replacement](zun/TH04_ZUN_FILE_CLOSE_V532.md)
- [ZUN DOS_ROPEN / FONTFILE_OPEN library replacement](zun/TH04_ZUN_FONTOPEN_V533.md)
- [ZUN VERSION / GRP pure-data library replacement](zun/TH04_ZUN_VERSION_GRP_V534.md)
- [ZUN FIL file-state DATA / BSS library replacement](zun/TH04_ZUN_FILE_STATE_V535.md)
- [ZUN compact local MASTER archive](zun/TH04_ZUN_COMPACT_MASTER_V536.md)
- [ZUN Borland runtime inventory / EMU-MATHS removal](zun/TH04_ZUN_RUNTIME_INVENTORY_V537.md)
- [ZUN resident six-byte layout cascade diagnostic](zun/TH04_ZUN_RESIDENT_SHIFT_V546.md)
## Recent MAIN milestones

- [Accepted MAIN cohort and durable exact summary](main/TH04_MAIN_EXACT_BATCH.md)
- [Dialog ownership / relocation history](main/TH04_MAIN_DIALOG_BOUNDARY_V180.md)
- [Dialog render producer evidence](main/TH04_MAIN_DIALOG_RENDER_V182.md)
- [Thick-laser producer](main/TH04_MAIN_THICKLASER_UPDATE_V181.md)
- [Gather-point renderer](main/TH04_MAIN_GATHER_POINT_RENDER_V326.md)

Resolved one-off packet notes are folded into the exact summary, CSV ledgers,
and Git history instead of remaining in the routine documentation surface.

## Directory map

| Directory | Scope |
| --- | --- |
| [`main/`](main/) | MAIN code, layout, compiler, and boundary evidence |
| [`op-maine/`](op-maine/) | OP/MAINE source shared by those artifacts |
| [`packed/`](packed/) | DIET container, payload, header, and relocation work |
| [`shared/`](shared/) | Evidence for code or declarations shared across artifacts |
| [`zun/`](zun/) | ZUN.COM resident, configuration, and support code |

Version suffixes remain in filenames so old evidence and Git history stay
addressable. Treat every versioned note as state-at-that-packet unless it is
listed under Active frontiers above. Continue an existing subject note when an experiment advances the
same claim. Add a new note only for a distinct ownership decision, reusable
negative result, or replay boundary. Keep live priorities in
[`RE_HANDOFF.md`](../RE_HANDOFF.md) and live counts in the CSV ledgers and
generated progress reports. Notes not listed under active frontiers or recent
milestones are retained evidence; do not scan them during routine handoff.
