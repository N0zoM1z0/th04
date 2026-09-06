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
| Reviewed authored byte units/regions | 52 |
| Reviewed authored bytes | 12,691 |
| Exact authored byte units/regions | 51 |
| **Exact authored bytes** | **12,650 / 12,691 (99.676936%)** |
| Tracked authored function candidates | 114 |
| Reviewed authored functions | 113 |
| Exact authored functions | 112 |
| **Exact authored functions** | **112 / 113 (99.115044%)** |
| Provisional function candidates excluded from the denominator | 1 |
| Exact original-style standalone ASM units | 9 / 1,489 bytes |

The remaining reviewed authored byte mismatch is a single 41-byte middle
region inside `snd_load`; it is also the only reviewed nonexact function.
`snd_pmd_resident` is fully exact from maintained pure C after expressing the
PMD IVT slot as a Borland `__es` segment-specific pointer. `dialog_init` is now
also exact after restoring its original second C++ translation unit: the linked
code bytes stay identical while the Intel OMF FIXUPP batching and ordered MZ
relocations return to the target order.

Eleven former Ghidra non-contiguous-body candidates are now manually reviewed
exact. The replayable manual gate requires the same TLINK public and exact byte
owner, a configured Ghidra min/max span, gap-free raw `ndisasm` coverage through
a terminal return, and—for indirect switches—every table target to land on a
raw instruction boundary inside the function. `bullets_update` remains the one
provisional candidate because it crosses a deliberately excluded handwritten-
call region. Exact enclosing bytes never waive that nonexact gap.

Two `dialog` byte regions (`dialog_op` and `dialog_run`) remain provisional.
Their raw bytes and relocation-site sets reproduce, but the ordered relocation
lists still differ. The former `dialog_init` blocker was distinct: historical
and local replay show that it originally lived in a second C++ translation unit;
restoring that TU boundary fixes all six ordered relocations without changing
linked code bytes. The historical pre-merge first dialog object already has the
same `dialog_op`/`dialog_run` fixup order as the current candidate, so the same
split is explicitly ruled out as a fix for those two.

Standalone source modules that were genuinely assembly translation units in
the build are tracked as `origin=original-asm`. Their 1,489 exact bytes are not
included in the authored C/C++ byte percentage.

## Replay basis

The current accepted byte cohort is reproduced by
`python3 scripts/replay_th04_main_exact_units.py`. Historical acceptance
receipts remain useful, while the current full-owner replay
`gptweb-dialog-split-aggregate-001` independently repeated two isolated
`git archive` materializations of the pinned ReC98 revision, overlaid
repository-maintained source, restored the checked-in dialog TU split through
`Tupfile.lua`, and passed all 60 default-selected raw/map/ordered-relocation/
OMF/determinism checks.

Function accounting is independently conservative. The checked-in
`scripts/review_th04_main_functions.py` intersects target Ghidra entries,
locally rebuilt TLINK publics, and exact authored byte owners. It automatically
accepts contiguous Ghidra bodies and separately replays explicitly configured
manual raw/switch-table reviews for body-construction false negatives. See
`docs/reconstruction/TH04_MAIN_EXACT_BATCH.md` for the evidence and exclusions.
