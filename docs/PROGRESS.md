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
| Reviewed authored byte units/regions | 51 |
| Reviewed authored bytes | 12,494 |
| Exact authored byte units/regions | 50 |
| **Exact authored bytes** | **12,453 / 12,494 (99.671842%)** |
| Tracked authored function candidates | 113 |
| Reviewed authored functions | 112 |
| Exact authored functions | 111 |
| **Exact authored functions** | **111 / 112 (99.107143%)** |
| Provisional function candidates excluded from the denominator | 1 |
| Exact original-style standalone ASM units | 9 / 1,489 bytes |

The remaining reviewed authored byte mismatch is now a single 41-byte middle
region inside `snd_load`; it is also the only reviewed nonexact function.
`snd_pmd_resident` is fully exact from maintained pure C after expressing the
PMD IVT slot as a Borland `__es` segment-specific pointer, which makes TC4J
naturally emit the target `LES BX, ES:[0180h]` without inline assembly.

Eleven former Ghidra non-contiguous-body candidates are now manually reviewed
exact. The replayable manual gate requires the same TLINK public and exact byte
owner, a configured Ghidra min/max span, gap-free raw `ndisasm` coverage through
a terminal return, and—for indirect switches—every table target to land on a
raw instruction boundary inside the function. `bullets_update` remains the one
provisional candidate because it crosses a deliberately excluded handwritten-
call region. Exact enclosing bytes never waive that nonexact gap.

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
`python3 scripts/replay_th04_main_exact_units.py`. Historical acceptance
receipts remain useful, while the current full-owner replay
`gptweb-pmd-aggregate-001` independently repeated two isolated `git archive`
materializations of the pinned ReC98 revision, overlaid repository-maintained
source, and passed all 59 default-selected raw/map/ordered-relocation/OMF/
determinism checks after replacing the two PMD partial owners with one exact
46-byte function owner.

Function accounting is independently conservative. The checked-in
`scripts/review_th04_main_functions.py` intersects target Ghidra entries,
locally rebuilt TLINK publics, and exact authored byte owners. It automatically
accepts contiguous Ghidra bodies and separately replays explicitly configured
manual raw/switch-table reviews for body-construction false negatives. See
`docs/reconstruction/TH04_MAIN_EXACT_BATCH.md` for the evidence and exclusions.
