# Reconstruction evidence notes

These notes explain bounded target observations, compiler experiments, replay
receipts, and unresolved producer questions. They support the ledgers; they do
not define current progress or exactness by themselves.

## Active frontiers

Only the links in this section and `docs/RE_HANDOFF.md` describe the current
frontier. Versioned notes outside this list are historical snapshots and may
contain residual counts that were correct only at that packet.

### MAIN.EXE

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
- [BGIMAGE hybrid producer / relocation closure](op-maine/TH04_BGIMAGE_HYBRID_V489.md)
- [OP historical SCORE_TEXT producer](op-maine/TH04_OP_SCORE_GROUP_V488.md)
- [OP/MAINE score codec boundary / provenance review](op-maine/TH04_SCORE_CODEC_BOUNDARIES_V540.md)
- [OP/MAINE SCORE high-score boundary / provenance review](op-maine/TH04_SCORE_HISCORE_BOUNDARIES_V541.md)
- [OP hi_view boundary correction and provenance](op-maine/TH04_OP_HI_VIEW_BOUNDARIES_V542.md)
- [MAINE SCORE insertion natural C++ and decoded acceptance](op-maine/TH04_MAINE_SCORE_CPP_V479.md#v543-maintained-score-insertion-acceptance)
- [DIET MZ partition / derived minalloc](packed/TH04_DIET145F_MZ_PARTITION_V231.md)
- [Packed BGM-BSS file-backing mechanism](packed/TH04_BGM_BSS_FILEBACK_V492.md)
- [ZUN-modified MASTER provenance](packed/TH04_ZUN_MASTER_VERSION_V493.md)
- [BGM BSS Reduction #172 provenance](packed/TH04_BGM_BSS_REDUCTION172_V494.md)

### ZUN.COM

- [ZUN resident main](zun/TH04_ZUN_MAIN_V241.md)
- [ZUN standalone component link](zun/TH04_ZUN_COMPONENT_LINK_V317.md)
- [ZUNINIT physical boundary review](zun/TH04_ZUNINIT_BOUNDARIES_V520.md)
- [MEMCHK physical boundary review](zun/TH04_MEMCHK_BOUNDARIES_V521.md)
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
