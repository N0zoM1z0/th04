# Reconstruction evidence notes

These notes explain bounded target observations, compiler experiments, replay
receipts, and unresolved producer questions. They support the ledgers; they do
not define current progress or exactness by themselves.

## Active frontiers

### MAIN.EXE

- [Gameplay loop compiler candidate](main/TH04_DEMO_GAMEPLAY_TERNARY_V248.md)
- [Dialog ownership and relocation order](main/TH04_MAIN_DIALOG_BOUNDARY_V180.md)
- [Stage-session split diagnostic](main/TH04_DEMO_PAUSE_SPLIT_V282.md)
- [DEMO link-order diagnostic](main/TH04_DEMO_LINK_ORDER_V291.md)
- [Remaining FIXUPP and compiler negatives](main/TH04_MAIN_FIXUP_CODEGEN_PROBES.md)
- [END/MAI scroll and MPN source gap](op-maine/TH04_END_SCROLL_MPN_V195.md)

### Packed artifacts and ZUN.COM

- [Decoded payload frontier](packed/TH04_PACKED_PAYLOAD_FRONTIER_V218.md)
- [BGIMAGE natural-source frontier](op-maine/TH04_BGIMAGE_NATURAL_V247.md)
- [ZUN resident main](zun/TH04_ZUN_MAIN_V241.md)
- [ZUN standalone component link](zun/TH04_ZUN_COMPONENT_LINK_V317.md)

### Standalone source closure

- [Compatibility dependency migration and handoff template](shared/TH04_COMPAT_MIGRATION.md)

## Recent MAIN milestones

- [Accepted MAIN cohort](main/TH04_MAIN_EXACT_BATCH.md)
- [Enemy helpers](main/TH04_MAIN_ENEMY_HELPERS_V328.md)
- [Enemy script dispatcher](main/TH04_MAIN_ENEMY_SCRIPT_NATURAL_V330.md)
- [Item producer](main/TH04_MAIN035_ITEMS_V154.md)
- [Thick-laser producer](main/TH04_MAIN_THICKLASER_UPDATE_V181.md)
- [Gather-point renderer](main/TH04_MAIN_GATHER_POINT_RENDER_V326.md)

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
generated progress reports.
