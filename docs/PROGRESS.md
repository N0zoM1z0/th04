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
| Reviewed authored byte units/regions | 58 |
| Reviewed authored bytes | 12,691 |
| Exact authored byte units/regions | 54 |
| **Exact authored bytes** | **12,687 / 12,708 (99.834750%)** |
| Tracked authored function candidates | 114 |
| Reviewed authored functions | 114 |
| Exact authored functions | 112 |
| **Exact authored functions** | **112 / 114 (98.245614%)** |
| Provisional function candidates excluded from the denominator | 0 |
| Exact original-style standalone ASM units | 9 / 1,489 bytes |

The current reviewed authored byte mismatch is only 21 bytes total. `snd_load`
now has 230 / 234 bytes exact: maintained natural C++ independently recovers its
8-byte DOS-open sequence, 26-byte driver-dispatch/read sequence, and 3-byte
`MOV AX,[BP+6]` reload. Only `PUSH DS` (1 byte), target `89 C3` `MOV BX,AX`
(2 bytes), and `POP DS` (1 byte) remain blocked there. `bullets_update` is also
fully boundary-reviewed, so its known 17-byte spark-call gap is now honestly
included in the byte denominator rather than excluded; natural C++ reproduces
all argument setup but lowers the call as `CALL FAR` instead of target `NOP;
PUSH CS; CALL near`. Neither gap is waived or filled with inline assembly.
`snd_pmd_resident` is fully exact from maintained pure C after expressing the
PMD IVT slot as a Borland `__es` segment-specific pointer. `dialog_init` is also exact after restoring its
original second C++ translation unit: the linked code bytes stay identical while
the Intel OMF FIXUPP batching and ordered MZ relocations return to target order.

Eleven former Ghidra non-contiguous-body candidates are manually reviewed exact.
The replayable exact-manual gate requires the same TLINK public and exact byte
owner, a configured Ghidra min/max span, gap-free raw `ndisasm` coverage through
a terminal return, and—for indirect switches—every table target to land on a
raw instruction boundary inside the function. A separate reviewed-nonexact gate
now proves complete boundaries without implying byte equality. `bullets_update`
is the first nonexact switch-data case: its code decodes through `RETF` at
`0x2CC27`, byte `0x2CC28` is switch metadata, the five words at `0x2CC29` all
target decoded instructions, and the next TLINK public begins exactly at
`0x2CC33`. No function candidate remains provisional in the current screen.

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
receipts remain useful, while the current pre-commit full-owner replay
`gptweb-producer-v9-precommit-001` independently repeated two isolated
`git archive` materializations of the pinned ReC98 revision, overlaid
repository-maintained source, restored the checked-in dialog TU split through
`Tupfile.lua`, and passed all 60 default-selected raw/map/ordered-relocation/
OMF/determinism checks.

Function accounting is independently conservative. The checked-in
`scripts/review_th04_main_functions.py` intersects target Ghidra entries,
locally rebuilt TLINK publics, and exact authored byte owners. It automatically
accepts contiguous Ghidra bodies, separately replays explicitly configured
manual raw/switch-table reviews for body-construction false negatives, and
validates complete reviewed-nonexact boundaries before placing them in the
denominator. See
`docs/reconstruction/TH04_MAIN_EXACT_BATCH.md` for the evidence and exclusions.
