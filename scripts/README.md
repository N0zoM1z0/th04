# TH04 script map

Start here to choose a tool. The catalog covers every Python, shell, Windows,
Java, assembly and debugger file below `scripts/`; it records purpose and role
without executing probes. Python descriptions come from source docstrings or maintained entrypoint descriptions;
missing descriptions are explicitly marked filename-derived.

## Common tasks

| Task | Entry point | Guide |
| --- | --- | --- |
| Check local state/targets | `python3 scripts/preflight.py` | [Workflow](../docs/RE_WORKFLOW.md) |
| Build DOS products | `python3 scripts/build.py --help` | [DOS build](../docs/DOS_BUILD.md) |
| Build on Windows, English progress | `scripts/windows/build-th04.cmd` | [Windows options](windows/README-build.txt) |
| Prepare/play a disposable image | `scripts/prepare_product_hdi.py`, `scripts/export_windows_play.py` | [Runtime](../docs/RUNTIME.md) |
| Find a hardware fix/control | `python3 scripts/catalog/index.py list --category hardware` | [Hardware reuse](../docs/PC98_HARDWARE_REUSE.md) |
| Find a script by purpose | `python3 scripts/catalog/index.py list --query palette` | Catalog below |
| Inspect a command before running | `python3 scripts/catalog/index.py show build.py` | Source/subject note |
| Check ledgers and public tests | `python3 scripts/ci.py` | [Knowledge policy](../docs/KNOWLEDGE_BASE.md) |
| Review cleanup | `python3 scripts/prune_analysis.py --help` | [Retention](../docs/ANALYSIS_RETENTION.md) |

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

## Maintain the indexes

```sh
python3 scripts/catalog/index.py --write
python3 scripts/catalog/index.py --check
```

CI checks complete coverage and deterministic descriptions; add/edit a script,
regenerate the catalog and commit both. `catalog/catalog.json` is the searchable
machine-readable inventory. Native x64 build/control scripts live on the
separate `port/modern-64` branch under `port64/`, indexed by its `docs/PORT64.md`.
