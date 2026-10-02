# Reconstruction evidence notes

These notes explain bounded target observations, compiler experiments, replay
receipts, and unresolved producer questions. They support the ledgers; they do
not define current progress or exactness by themselves.

Versioned notes are historical snapshots unless a current-state document
explicitly reaffirms a claim.
Historical .analysis/reconstruction/probes/... paths record where evidence was
produced; the expanded worktree may have been pruned after its receipt and
digests were archived. Re-run the checked-in command or restore the private
receipt archive rather than treating a missing probe directory as missing
source evidence.

## Current open questions

Native product-build investigation is active. Use the live ledgers and
[`RE_HANDOFF.md`](../RE_HANDOFF.md) for current counts and acceptance. These
notes explain the remaining source and container gaps:

- [Native DOS product build readiness and source-graph gaps](product/TH04_NATIVE_BUILD_READINESS_V1.md)
- [Native MAINE far-call ABI trap and repair](product/TH04_NATIVE_FAR_CALL_ABI_V856.md)
- [Native PC-98 scroll and GRCG rectangle owners](product/TH04_NATIVE_SCROLL_BOX_V858.md)
- [Native PI cleanup owner and segment-pointer compiler probe](product/TH04_NATIVE_PI_FREE_V859.md)
- [Standalone PI slot lifetime after the ending](product/TH04_NATIVE_PI_SLOT_LIFETIME_V1224.md)
- [Native text VRAM gaiji writers](product/TH04_NATIVE_GAIJI_TEXT_V860.md)
- [Native graphics gaiji writers](product/TH04_NATIVE_GRAPH_GAIJI_V861.md)
- [Native graphics page copy and TC4J loop scope](product/TH04_NATIVE_GRAPH_COPY_V862.md)
- [Native segmented heap and TC4J merged-return counterexample](product/TH04_NATIVE_HEAP_V863.md)
- [Native VSync interrupt and DOS vector lifecycle](product/TH04_NATIVE_VSYNC_V864.md)
- [Native gaiji backup, restore, and BFNT loader](product/TH04_NATIVE_GAIJI_STORAGE_V865.md)
- [Native packed-row renderer and PI decoder handoff](product/TH04_NATIVE_PACK_PUT_V866.md)
- [Native PAR archive fixtures and DOS file service](product/TH04_NATIVE_PF_ARCHIVE_V867.md)
- [Native packed PI decoder and historical ABI/source divergence](product/TH04_NATIVE_PI_DECODE_V869.md)
- [Native BFNT sprite storage and planar renderer](product/TH04_NATIVE_SUPER_SPRITE_V870.md)
- [Native BGM beeper service, standalone MAINE link, and IRQ far-call fixup](product/TH04_NATIVE_BGM_V871.md)
- [Native OP source graph, segment grouping, and link frontier](product/TH04_NATIVE_OP_LINK_V875.md)
- [Native MAIN local header and composite-source closure](product/TH04_NATIVE_MAIN_SOURCE_CLOSURE_V882.md)
- [Native MAIN product-source and DATA/BSS compiler frontier](product/TH04_NATIVE_MAIN_PRODUCT_FRONTIER_V1025.md)
- [Native MAIN normal-route runtime differential and input-layout lead](product/TH04_NATIVE_MAIN_STARTUP_V1074.md)
- [Native MAIN large-model far-runtime owners and v1131 frontier](product/TH04_NATIVE_MAIN_FAR_RUNTIME_V1131.md)
- [Native ZUN resident and source-composed launcher](zun/TH04_ZUN_NATIVE_SOURCE_BUILD_V880.md)
- [OP strict source blockers](op-maine/TH04_OP_STRICT_FRONTIER_V766.md)
- [MAINE strict source blockers](op-maine/TH04_MAINE_STRICT_FRONTIER_V732.md)
- [ZUN resident `_main` and `cfg_init` blockers](zun/TH04_ZUN_MAIN_V241.md)
- [ZUN mixed flat build and source limits](zun/TH04_ZUN_MIXED_COMPOSITE_V788.md)
- [DIET MZ partition and packing limits](packed/TH04_DIET145F_MZ_PARTITION_V231.md)

## Evidence catalog

The links below route to historical proofs and experiments. Their per-packet
counts, file paths, and proposals do not supersede the current ledgers.

### MAIN.EXE

- [Checkerboard counted-LOOP blocker](main/TH04_MAIN_CHECKERBOARD_V396.md)
- [Stage 4 carpet low-level producer blocker](main/TH04_MAIN_KURUMI_CARPET_V174.md)
- [snd_load DS/MOV analysis (historical; superseded by v836)](main/TH04_SND_LOAD_DS_V391.md)
- [Cross-cutting compiler/FIXUPP negatives (historical routing)](main/TH04_MAIN_FIXUP_CODEGEN_PROBES.md)
- [Public trial provenance intake](main/TH04_TRIAL_PROVENANCE_V500.md)

### OP / MAINE / packed artifacts

- [Shared CDG loader source and complete module replay across MAIN, OP, and MAINE](op-maine/TH04_SHARED_CDG_LOAD_V797.md)
- [Shared CDG renderer source and complete module replay across MAIN, OP, and MAINE](op-maine/TH04_SHARED_CDG_PUT_V799.md)
- [Shared PC-98 input sensing source across MAIN, OP, and MAINE](op-maine/TH04_SHARED_INPUT_V802.md)
- [Shared BGIMAGE rectangle ASM module in OP and MAINE](op-maine/TH04_SHARED_BGIMAGER_V805.md)
- [OP CDG alpha-only renderer reviewed boundary and cold module replay](op-maine/TH04_OP_CDG_NOCOLORS_V806.md)
- [OP CDG no-alpha renderer shared source and cold module replay](op-maine/TH04_OP_CDG_NOALPHA_V807.md)
- [OP horizontal-flip lookup generator boundary and shared source replay](op-maine/TH04_OP_HFLIP_LUT_V808.md)
- [OP font-effects renderer code/data and internal boundaries](op-maine/TH04_OP_GRAPH_PUTSA_FX_V809.md)
- [MAINE CDG plane renderer complete source module](op-maine/TH04_MAINE_CDG_PLANE_V814.md)
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
- [MAINE SND_LOAD artifact-local hybrid closure](op-maine/TH04_MAINE_SND_LOAD_HYBRID_V829.md)
- [MAINE shared-sound artifact-local closure](op-maine/TH04_MAINE_SND_SE_CROSSGAME_V830.md)
- [MAINE regist_menu compiler frontier (historical; superseded by v835)](op-maine/TH04_MAINE_REGIST_FRONTIER_V831.md)
- [MAINE SCORE codec artifact-local hybrid closure](op-maine/TH04_MAINE_SCORE_CODECS_HYBRID_V832.md)
- [MAINE cutscene EGC artifact-local hybrid closure (historical checkpoint)](op-maine/TH04_MAINE_CUTSCENE_EGC_HYBRID_V833.md)
- [MAINE SCORE EGC helper closure](op-maine/TH04_MAINE_SCORE_EGC_HYBRID_V834.md)
- [MAINE regist_menu ordinary-C++ closure](op-maine/TH04_MAINE_REGIST_TERNARY_V835.md)
- [TC4.02 SCORE rotate-intrinsic negative surface](op-maine/TH04_SCORE_ROTATE_INTRINSICS_V760.md)
- [BGIMAGE hybrid producer / relocation closure](op-maine/TH04_BGIMAGE_HYBRID_V489.md)
- [OP big menu/title exact replay](op-maine/TH04_OP_BIG_MENU_TITLE_EXACT_V735.md)
- [OP main-menu producer boundary correction and exact replay](op-maine/TH04_OP_MAIN_REMAINING_EXACT_V742.md)
- [OP setup submenu exact replay](op-maine/TH04_OP_SETUP_SUBMENUS_EXACT_V745.md)
- [OP Music Room remaining exact replay](op-maine/TH04_OP_MUSIC_REMAINING_EXACT_V748.md)
- [OP ZUNSOFT current natural-C++ owner exact replay](op-maine/TH04_OP_ZUNSOFT_NATURAL_EXACT_V753.md)
- [OP SCORE codec cross-game hybrid closure](op-maine/TH04_OP_SCORE_CODECS_HYBRID_V821.md)
- [OP shared-sound producer provenance bound (superseded by v827)](op-maine/TH04_OP_SND_SE_SHARED_V822.md)
- [OP shared-sound cross-game hybrid closure](op-maine/TH04_OP_SND_SE_CROSSGAME_V827.md)
- [OP internal EGC-start hybrid closure](op-maine/TH04_OP_EGC_START_HYBRID_V824.md)
- [OP EGC rectangle-copy hybrid closure](op-maine/TH04_OP_EGC_COPY_HYBRID_V825.md)
- [OP nopoly_B_put cross-game hybrid closure](op-maine/TH04_OP_NOPOLY_HYBRID_V826.md)
- [OP SND_LOAD complete-producer provenance bound (superseded by v828)](op-maine/TH04_OP_SND_LOAD_PROVENANCE_V823.md)
- [OP SND_LOAD maintained-hybrid closure](op-maine/TH04_OP_SND_LOAD_HYBRID_V828.md)
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

- [ZUN launcher selector symbolic source and boundary](zun/TH04_ZUN_SELECTOR_V786.md)
- [ZUN launcher mover and customization tail sources](zun/TH04_ZUN_LAUNCHER_TAILS_V787.md)
- [ZUN generated directory and mixed-input flat build](zun/TH04_ZUN_MIXED_COMPOSITE_V788.md)
- [ZUN resident main](zun/TH04_ZUN_MAIN_V241.md)
- [ZUN standalone component link](zun/TH04_ZUN_COMPONENT_LINK_V317.md)
- [ZUNINIT physical boundary review](zun/TH04_ZUNINIT_BOUNDARIES_V520.md)
- [ZUNINIT Shift-JIS converter semantic Oracle](zun/TH04_ZUNINIT_SJIS_V777.md)
- [ZUNINIT text VRAM writer runtime Oracle](zun/TH04_ZUNINIT_TEXT_VRAM_V778.md)
- [ZUNINIT text support symbolic ASM owner](zun/TH04_ZUNINIT_TEXT_SUPPORT_ASM_V779.md)
- [ZUNINIT complete symbolic component cold link](zun/TH04_ZUNINIT_SYMBOLIC_COMPONENT_V785.md)
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
- [Native MAIN EMS-stage startup differential](product/TH04_NATIVE_MAIN_EMS_STARTUP_V1080.md)

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
addressable. Treat every versioned note as state-at-that-packet. Continue an
existing subject note when an experiment advances the same claim. Add a new
note only for a distinct ownership decision, reusable negative result, or
replay boundary. Keep live priorities in
[`RE_HANDOFF.md`](../RE_HANDOFF.md) and live counts in the CSV ledgers and
generated progress reports. Notes outside current open questions are retained
evidence; do not scan them during routine handoff.
