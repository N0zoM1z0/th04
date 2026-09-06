# TH04 reconstruction progress

This is the current conservative snapshot derived from `config/units.csv` and
`config/th04_main_authored_functions.csv`. Percentages use only reviewed
boundaries. Provisional Ghidra entries, unresolved switch/shared-tail bodies,
and byte regions whose relocation ownership is not exact remain outside the
reviewed denominator until they are resolved.

## `MAIN.EXE` authored progress

| Measure | Current result |
| --- | ---: |
| Initial screened source-module contributions | 58 / 17,412 bytes |
| Initial Ghidra function entries in those contributions | 151 |
| Reviewed authored byte units/regions | 53 |
| Reviewed authored bytes | 12,494 |
| Exact authored byte units/regions | 51 |
| **Exact authored bytes** | **12,448 / 12,494 (99.631823%)** |
| Tracked authored function candidates | 113 |
| Reviewed authored functions | 101 |
| Exact authored functions | 99 |
| **Exact authored functions** | **99 / 101 (98.019802%)** |
| Provisional function candidates excluded from the denominator | 12 |
| Exact original-style standalone ASM units | 9 / 1,489 bytes |

The remaining reviewed authored byte mismatch is deliberately small and
explicit: a 5-byte `LES` region inside `snd_pmd_resident` and a 41-byte middle
region inside `snd_load`. Both complete functions remain reviewed but nonexact,
which is why the function denominator is 101 rather than 99.

The 12 provisional function candidates do not enter the function denominator.
Eleven have a non-contiguous Ghidra body even though their enclosing maintained
byte owner is exact; `bullets_update` crosses a deliberately excluded
handwritten-call region. Exact enclosing bytes never waive unresolved function
ownership.

Three additional `dialog` byte regions (`dialog_op`, `dialog_run`, and
`dialog_init`) are also kept provisional. Their raw bytes, map placement, and
OMF output reproduce, but the target and candidate MZ relocation tables order
the same relocation sites differently. The strict relocation-order Oracle
therefore blocks promotion.

Standalone source modules that were genuinely assembly translation units in
the build are tracked as `origin=original-asm`. Their 1,489 exact bytes are not
included in the authored C/C++ byte percentage.

## Replay basis

The current accepted byte cohort is reproduced by
`python3 scripts/replay_th04_main_exact_units.py`. The final development replay
`gptweb-accept60-002` used two isolated `git archive` materializations of the
pinned ReC98 revision only as build scaffolding, overlaid repository-maintained
source, and passed all 60 selected raw/map/ordered-relocation/OMF/determinism
checks.

Function accounting is independently conservative. The checked-in
`scripts/review_th04_main_functions.py` intersects target Ghidra entries,
locally rebuilt TLINK publics, and exact authored byte owners, then accepts only
contiguous bodies wholly contained by one exact owner. See
`docs/reconstruction/TH04_MAIN_EXACT_BATCH.md` for the evidence and exclusions.
