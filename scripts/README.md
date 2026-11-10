# TH04 script map

Use the grouped notes below to find current build, comparison and analysis
commands. Historical entries may need fresh inputs; inspect a command before
running it.

## Common tasks

| Task | Entry point | Guide |
| --- | --- | --- |
| Check local state/targets | `python3 scripts/preflight.py` | [Workflow](../docs/RE_WORKFLOW.md) |
| Build DOS products | `python3 scripts/build.py --help` | [DOS build](../docs/DOS_BUILD.md) |
| Build on Windows, English progress | `scripts/windows/build-th04.cmd` | [Windows options](windows/README-build.txt) |
| Prepare/play a disposable image | `scripts/prepare_product_hdi.py`, `scripts/export_windows_play.py` | [Runtime](../docs/RUNTIME.md) |
| Find a hardware fix/control | [Hardware tools](catalog/hardware.md) | [Hardware reuse](../docs/PC98_HARDWARE_REUSE.md) |
| Find a script by purpose | `rg -n 'palette' scripts/catalog` | Catalog below |
| Inspect a command before running | `python3 scripts/build.py --help` | Source/subject note |
| Check repository basics | `python3 scripts/ci.py` | [Knowledge policy](../docs/KNOWLEDGE_BASE.md) |

Run commands from the repository root. Only one Borland/Wine writer may run.
Use fresh probe paths; diagnostic images are not ordinary game packages.
A catalog entry is not proof that its historical private inputs remain expanded
or that an old replay currently passes. Consult its subject note and ledgers.

## Catalog by purpose

- [Setup and attestation](catalog/setup.md)
- [Tracking, CI and maintenance](catalog/tracking.md)
- [DOS builds and Windows packaging](catalog/build.md)
- [Historical matching/compiler controls](catalog/matching.md)
- [Boundaries and databases](catalog/boundaries.md)
- [Runtime scenarios and fault observation](catalog/runtime.md)
- [PC-98 hardware/ABI/performance](catalog/hardware.md)
- [Formats, memory and score services](catalog/formats.md)
- [Source ownership/provenance review](catalog/source-review.md)
- [Libraries, fixtures and tool-side support](catalog/support.md)

Physical ownership remains `windows/`, `boundary_review/`, `ghidra/`,
`runtime/fixtures/`, `lib/` and `probes/`. Categorized indexes are under
`catalog/`. Historical probe paths and imports are retained because manifests,
attested replay commands and evidence rows identify them; bulk moves would
change replay inputs. New generic utilities may use a subsystem folder after
its imports/root calculation and replay callers are reviewed.



Run `python3 scripts/ci.py` for basic checks without private inputs.
Run comparator, compiler and runtime checks only for the affected scope.
The grouped catalogs are navigation aids; ordinary script changes do not
require regenerating an inventory or hashing documentation.
