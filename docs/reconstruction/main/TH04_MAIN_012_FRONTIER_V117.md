# TH04 MAIN_012_TEXT v117 Frontier

This note records target-first boundary and natural-source work immediately
before the accepted `elly_fg_render()` owner. It does **not** promote any new
exact owner. The private target remains local operator input with
`candidate-local-attested` canonicality only.

## Address model

All target addresses below are qualified by `th04-main / MAIN.EXE` and
`MAIN_012_TEXT`. The executable has a 0x1800-byte MZ header. Ghidra is loaded at
segment `2000`, while the TLINK map places this code in segment `0AAF`.

| Function | Map address | Load-module extent | Ghidra linear extent | File extent | State |
| --- | --- | --- | --- | --- | --- |
| `shots_add()` | `0AAF:72A6` | `0x11D96..0x11DC9` | `0x21D96..0x21DC9` | `0x13596..0x135C9` | provisional boundary; source-present |
| `shot_velocity_set()` | `0AAF:72DA` | `0x11DCA..0x11DE5` | `0x21DCA..0x21DE5` | `0x135CA..0x135E5` | provisional boundary; natural-source exactness unresolved |
| `sub_11DE6` | `0AAF:72F6` | `0x11DE6..0x11E11` | `0x21DE6..0x21E11` | `0x135E6..0x13611` | target-reviewed FAR boundary; natural-source exactness blocked by current LOOP hypothesis |

Pinned TASM PROC starts, raw 16-bit decoding, and the immediately following
entries close all three extents without gaps. None of the three extents contains
an MZ relocation. Fresh attested Ghidra constructs the complete 44-byte
`sub_11DE6` body, but does not construct functions at the two preceding entries.
That absence is why the generated boundary ledger remains provisional for
`shots_add()` and `shot_velocity_set()`; it is not evidence that the entries are
data.

## `sub_11DE6`: bounded negative result

The 44-byte FAR target body scans nine `SHOT_LEVEL_TO_POWER` thresholds with
`CX = 9` and the x86 `LOOP` instruction, derives `shot_level` from the byte
index, selects `playchar_shot_func`, and calls `hud_power_put()` through the
same-segment `NOP; PUSH CS; CALL near` encoding before `RETF`.

The same-segment call is not the blocker. Existing repository evidence shows
that `#pragma samecodeseg` can make TC4J/TLINK choose that encoding naturally.
The blocker is the threshold loop. The current-session matrix tested ordinary
`int`, `unsigned int`, byte counters, `register` counters, `for`/`while`/`do`
forms, explicit Borland `_CX`, CPU levels `-1/-2/-3`, `-k-`, and `-G` under the
pinned Turbo C++ 4.02 profile. Ordinary counters are allocated to `SI` and use
`INC/CMP/Jcc` or `DEC/Jcc`; explicit `_CX` uses `DEC CX` plus a test/branch.
None emits the target `LOOP` instruction.

The closest allowed source shape also proves useful positive facts: `-k-` plus
Borland register pseudo-variables reproduces the target frameless AX/BX data
flow, direct threshold addressing, `shot_level` store, and callback selection.
No inline assembly, `#pragma codestring`, target-byte emission, or padding was
accepted to bridge the remaining loop mismatch. Do not retry this family
without a new falsifiable TC4J source/compiler hypothesis.

## `shot_velocity_set()`: ABI/origin seam

Raw target decoding closes a 28-byte Pascal near function ending in `RET 4`.
Its body begins with `MOV BX,SP; PUSH SI`, reads the near pointer and byte angle
through `SS:[BX+4]` and `SS:[BX+2]`, indexes a four-byte velocity table, copies
one dword to the caller-provided destination, restores SI, and returns.

A natural C++ stack-peek probe can match the 28-byte size and the table/copy
semantics, but TC4J emits `PUSH SI; MOV BX,SP` and uses `MOV BH,0` where the
target uses `MOV BX,SP; PUSH SI` and `XOR BH,BH`. The current ReC98 declaration
returns `SPPoint`, but ordinary struct-return probes introduce additional return
shaping while target callers observed in this packet ignore the result. The
return type and authored-vs-original-assembly origin therefore remain open.
Historical ReC98 history only establishes that this routine was reverse-
engineered into assembly; it does not establish original source language.

## `shots_add()`: maintainable source-present candidate

`src/main/player/shots_add.cpp` is a maintained natural-C++ candidate using the
real TH04 `Shot`, `PlayfieldMotion`, and subpixel types through the quarantined
ReC98 forwarding header. It uses Borland's existing register pseudo-variable
idiom (`_AX` for the returned pointer and `_BX` for the current shot), an
unsigned interpretation of the byte-sized `shot_last_id`, a packed flag/age
word initialization, ordinary current-position assignment, and
`SPPoint::set_long(0, TO_SP(-12))` for the initial velocity.

A bounded compiler probe copied only the transitive 24-header / 58,121-byte
include closure and compiled with the MAIN profile (`-O -b- -3 -Z -d
-DGAME=4 -ml -DBINARY='M'`). Turbo C++ 4.02 emitted a valid 52-byte OMF code
record. Mechanically zeroing only the five unresolved 16-bit external data-
symbol fixup words in the 52-byte target extent makes the object code identical
to the target instruction stream. The source SHA-256 is
`88b223e0ce8c52638fb2e9bac4378828a70625a9aa8a7082f371d92c347dc6fa`;
the dependency-timestamp-normalized object SHA-256 is
`97c6df88bbad260b7cdccb68bf5f39192e6ffe818f9858a1d7369407518bb68d`.

This result receives zero exactness credit. `shots_add()` physically precedes
the unresolved `shot_velocity_set()` and `sub_11DE6` bodies inside the remaining
monolithic `MAIN_012_TEXT` contribution. Simply removing `shots_add()` from the
assembler and appending its C++ object would move it after those bodies and
fail map/raw ownership. The existing replay split mechanism is not a license to
manufacture a target-derived assembler suffix solely to force placement.
Natural exact promotion therefore waits for a legitimate producer-order
closure of the intervening functions.

## Next evidence-connected work

Review `shot_velocity_set()` first as an ABI/origin seam. A useful next
hypothesis must explain the target's pre-save `MOV BX,SP`, `XOR BH,BH`, and
`RET 4` under the pinned compiler, or provide independent evidence that the
routine is genuine original-style assembly. If that remains unresolved, move
one function earlier in `MAIN_012_TEXT` while preserving the three proven
adjacent extents; do not sacrifice the `shots_add()` source shape merely to
obtain a convenient link order.
