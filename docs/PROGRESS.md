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
| Reviewed authored byte units/regions | 56 |
| Reviewed authored bytes | 12,708 |
| Exact authored byte units/regions | 53 |
| **Exact authored bytes** | **12,704 / 12,708 (99.968524%)** |
| Tracked authored function candidates | 114 |
| Reviewed authored functions | 114 |
| Exact authored functions | 113 |
| **Exact authored functions** | **113 / 114 (99.122807%)** |
| Provisional function candidates excluded from the denominator | 0 |
| Exact original-style standalone ASM units | 9 / 1,489 bytes |

The current reviewed authored byte mismatch is only **4 bytes total**, all inside
`snd_load`. That 234-byte function now has 230 exact bytes; only `PUSH DS`
(1 byte), target `89 C3` `MOV BX,AX` (2 bytes), and `POP DS` (1 byte) remain
blocked. `bullets_update` is fully exact across its complete 0x36B reviewed
extent. Its maintained natural C++ uses `#pragma samecodeseg sparks_add_random`;
TC86 still emits a five-byte far call in the object, but the group-frame FIXUPP
lets normal TLINK 6.10 far-call optimization produce the target `NOP; PUSH CS;
CALL near` in the final MZ and remove the segment relocation. No inline assembly,
codestring, `__emit__`, or byte injection is used. `snd_pmd_resident` remains
fully exact from maintained pure C through Borland `__es` pointer semantics, and
`dialog_init` remains exact after restoring its natural second C++ translation
unit.

Eleven former Ghidra non-contiguous-body candidates are manually reviewed exact.
A twelfth exact manual case, `bullets_update`, uses the stricter exact-extent
path because Ghidra's body ranges are unusable. The gate requires the same TLINK
public and one exact authored byte owner, gap-free raw decoding through `RETF`,
the exact next-public boundary, and—for its trailing compiler switch data—every
jump-table target to be a decoded instruction start. Thus the complete 0x36B
extent (0x360 bytes of code plus 11 bytes of switch metadata/table) is independently
reviewed exact without trusting Ghidra's body construction. `snd_load` is now the
sole reviewed nonexact function. No function candidate remains provisional in
the current screen.

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
`gptweb-sndload-z-v12-precommit-001` independently repeated two isolated
`git archive` materializations of the pinned ReC98 revision, overlaid
repository-maintained source, restored the checked-in dialog TU split through
`Tupfile.lua`, and passed all 62 default-selected raw/map/ordered-relocation/
OMF/determinism checks.

Function accounting is independently conservative. The checked-in
`scripts/review_th04_main_functions.py` intersects target Ghidra entries,
locally rebuilt TLINK publics, and exact authored byte owners. It automatically
accepts contiguous Ghidra bodies, separately replays explicitly configured
manual raw/switch-table reviews for body-construction false negatives, and
validates complete reviewed-nonexact boundaries before placing them in the
denominator. See
`docs/reconstruction/TH04_MAIN_EXACT_BATCH.md` for the evidence and exclusions.
