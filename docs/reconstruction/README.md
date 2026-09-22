# Reconstruction evidence notes

These notes explain bounded target observations, compiler experiments, replay
receipts, and unresolved producer questions. They support the ledgers; they do
not define current progress or exactness by themselves.

## Active frontiers

### MAIN.EXE

- [Checkerboard counted-LOOP blocker](main/TH04_MAIN_CHECKERBOARD_V396.md)
- [Stage 4 carpet low-level producer blocker](main/TH04_MAIN_KURUMI_CARPET_V174.md)
- [snd_load DS/MOV analysis](main/TH04_SND_LOAD_DS_V391.md)
- [Cross-cutting compiler/FIXUPP negatives](main/TH04_MAIN_FIXUP_CODEGEN_PROBES.md)

### OP / MAINE / packed artifacts

- [master.lib object-boundary frontier](packed/TH04_MASTER_OBJECT_BOUNDARIES_V397.md)
- [Decoded payload frontier](packed/TH04_PACKED_PAYLOAD_FRONTIER_V218.md)
- [BGIMAGE natural-source frontier](op-maine/TH04_BGIMAGE_NATURAL_V247.md)
- [BGIMAGE hybrid producer closure](op-maine/TH04_BGIMAGE_HYBRID_V489.md)
- [OP ZUNSOFT natural-C++ frontier](op-maine/TH04_OP_ZUNSOFT_CPP_V463.md)
- [OP historical SCORE_TEXT producer](op-maine/TH04_OP_SCORE_GROUP_V488.md)
- [MAINE verdict natural-C++ frontier](op-maine/TH04_MAINE_VERDICT_CPP_V471.md)
- [MAINE SCORE_TEXT natural-C++ frontier](op-maine/TH04_MAINE_SCORE_CPP_V479.md)

### ZUN.COM

- [ZUN resident main](zun/TH04_ZUN_MAIN_V241.md)
- [ZUN standalone component link](zun/TH04_ZUN_COMPONENT_LINK_V317.md)

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
addressable. Continue an existing subject note when an experiment advances the
same claim. Add a new note only for a distinct ownership decision, reusable
negative result, or replay boundary. Keep live priorities in
[`RE_HANDOFF.md`](../RE_HANDOFF.md) and live counts in the CSV ledgers and
generated progress reports. Notes not listed under active frontiers or recent
milestones are retained evidence; do not scan them during routine handoff.
