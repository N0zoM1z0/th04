# TH04 source layout

Product source is organized first by output artifact and then by gameplay or
platform subsystem. Source paths describe ownership; exactness lives in the
ledgers.

| Path | Purpose | Current state |
| --- | --- | --- |
| `src/main/` | MAIN.EXE gameplay and engine translation units | Active |
| `src/op/` | OP.EXE-owned translation units | Populated; shared owners live under `src/shared/` |
| `src/maine/` | MAINE.EXE-owned translation units | Populated; shared owners live under `src/shared/` |
| `src/zun/` | ZUN.COM launcher and resident code | Active |
| `src/shared/` | Code or declarations proved to be shared by TH04 artifacts | Active |

Within an artifact, place new files in the closest semantic subsystem. Keep a
file at the artifact root only when it represents an established historical
translation unit spanning several subsystems. The current root-level MAIN
files preserve already reviewed source owners and object boundaries; their
paths are referenced by exact replay manifests, function ledgers, and receipts.
They are not a template for new files.

Changing the path, split, merge, or include composition of an accepted
translation unit changes its replay input surface. Update every manifest and
ledger reference, then rerun the affected focused comparison and complete cold
aggregate before accepting such a change.

Product source may include repository-owned TH04 headers directly. Remaining
ReC98 declarations go through `compat/rec98/` until they are recovered under an
artifact or proved shared. Do not add progress-state directories such as
`exact/`, `partials/`, or `modules/`.
