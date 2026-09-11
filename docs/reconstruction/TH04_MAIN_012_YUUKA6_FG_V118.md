# TH04 `MAIN_012_TEXT` Yuuka6 foreground packet (v118)

## Scope and target identity

This packet reviews the `th04-main` / `MAIN.EXE` Yuuka6 foreground callback in
`MAIN_012_TEXT` and tests a maintainable natural Turbo C++ 4.02 source form. The
private target remains operator input with `candidate-local-attested`
canonicality. No target bytes were modified or copied into source.

The active target is SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The repository-native Ghidra check and the Factory provider attestation agree
on the MZ image, entry mapping, relocation stream, load-module digest, and
sampled bytes.

## Boundary and ownership

`yuuka6_fg_render()` is a near `MAIN_012_TEXT` function at:

- TLINK/TASM map address `0AAF:712A`;
- load-module extent `0x11C1A..0x11D95`;
- Ghidra `2000:1C1A`, linear `0x21C1A..0x21D95`;
- target file extent `0x1341A..0x13595`;
- size `0x17C` / 380 bytes;
- target-extent SHA-256
  `048438f24c87ea79c99a90311016ad0cfe020b0cfd1aadc5c1b1bb13adc7aeb9`.

Pinned TASM keeps one PROC over the full extent, Ghidra constructs one
contiguous 380-byte function, and raw 16-bit decode reaches `RET` at load
`0x11D95`. `shots_add()` starts immediately at `0x11D96`, so there is no
unowned post-return byte, shared tail, or hidden table between the two entries.
The extent owns ten target MZ relocation sites, all at FAR graphics calls.

Ghidra reports no direct caller/xref to `0x21C1A`. This is not evidence that the
entry is dead: maintained `boss.cpp` installs `yuuka6_fg_render` through
`boss_fg_render_func`, so the call is indirect by design.

The body renders the main Yuuka sprite pair, damage flashing, the mirror copy,
and the auxiliary center sprite, then calls the small/big explosion renderers,
`thicklasers_render()`, and the adjacent Yuuka6 entity renderer currently known
from the target as `sub_11B44`. The last semantic name is deliberately only a
source-facing near declaration until that neighboring owner is reconstructed.

## Natural-source probe

The maintained candidate is `src/main/boss/yuuka6_fg_render.cpp`. It uses only
natural C++ and the existing TH04 ABI/header surface. It contains no inline
assembly, target-derived byte arrays, `#pragma codestring`, fake returns,
padding, or target patching.

The first compilable candidate fixed screen coordinates directly to `_SI` and
`_DI`. Turbo C++ produced the correct control flow but 392 bytes rather than
the target 380: six `MOV AX,reg; ADD AX,imm` pairs were each two bytes longer
than the target `LEA AX,[reg+imm]`. This gave a precise source-shape hypothesis
rather than a reason to edit unrelated expressions.

Changing only those variables to natural `register int left` and
`register int top` lets TC4J allocate SI/DI itself. The compiler then emits the
target `LEA` forms and produces exactly 380 code bytes under the pinned MAIN
profile (`-O -b- -3 -Z -d -DGAME=4 -ml`).

The resulting object is stronger than an instruction-normalized near match:

- candidate LEDATA size: 380 bytes;
- candidate-versus-target mismatch runs: 45;
- every mismatch run is exactly two bytes;
- OMF FIXUPP subrecords: 45;
- the 45 mismatch-run starts exactly equal the 45 FIXUPP locations;
- all remaining 290 bytes are byte-identical to the target extent;
- the object is valid `TC86 Borland C++ 4.02` Intel OMF.

The bounded object/fixup comparison is recorded in evidence. It proves that
the compiler-selected instruction skeleton and every relocation/fixup site
have the target shape before link resolution. It does **not** prove linked
map placement, ordered MZ relocations, or final raw equality.

The object dependencies are exactly the expected graphics functions, `boss`,
`stage_frame_mod16`, Yuuka6 state/data aliases, the two explosion renderers,
`thicklasers_render()`, and the adjacent entity renderer. Existing exact-link
maps independently corroborate the already-maintained boss, stage, mirror,
auxiliary, and thick-laser symbol bindings.

## Why this is source-present, not exact

The target order in `MAIN_012_TEXT` is:

1. `yuuka6_fg_render()`;
2. `shots_add()`;
3. `shot_velocity_set()`;
4. `sub_11DE6`;
5. `elly_fg_render()`;
6. `stage_state_init()`.

The last two functions already have exact C++ owners, and `shots_add()` has a
v117 source-present C++ candidate. `shot_velocity_set()` and `sub_11DE6` still
remain inside the monolithic `th04_main.asm` producer with unresolved original
source language/code-generation questions. TLINK cannot interleave a new C++
object into the middle of that residual assembler contribution.

Moving `yuuka6_fg_render()` after the residual would change its address and raw
layout. Extracting the two unresolved followers as copied target assembly merely
to permit a link would manufacture equality and violate the reconstruction
rules. Therefore v118 intentionally runs no focused exact-unit cold replay and
no new aggregate exact replay for this candidate. It receives zero exactness
credit until the producer seam is legitimately resolved.

This reviewed/source-present owner deliberately expands the current confirmed
authored-byte denominator by 380 bytes. `scripts/status.py` therefore reports
40,638 / 41,049 exact authored C/C++ bytes (98.998758%) after v118, down from
the smaller v117 denominator. The accepted function ledger remains 270 / 272
exact because source-present is not an accepted exact/blocked function state.

## Corrected `sub_11DE6` compiler evidence

An intermediate v118 corpus scan initially overreached because it parsed the
wrong `ndisasm` field and incorrectly suggested that accepted natural C/C++
never contained `LOOP`. That claim was discarded before ledger promotion and
the scan was rerun correctly.

The corrected current corpus contains 123 accepted exact MAIN C/C++ owner
units. Thirteen units contain 25 `LOOP` instructions. All 25 belong to the same
TC4J compiler-generated switch-dispatch shape: a CS-resident case-value table
is scanned and followed by an indirect CS jump table. There are zero observed
`LOOP` instructions outside that switch-table pattern in the accepted natural
source corpus.

This is compatible with, but much narrower than, the v117 negative result.
TC4J clearly can emit `LOOP`; however, there is still no accepted natural-source
precedent for a source-level loop over a named DS-resident threshold table
compiling to the `sub_11DE6` form. The v117 `for`/`while`/`do`, register-counter,
explicit `_CX`, optimization, and CPU-level matrix remains negative for that
actual shape. This evidence does not prove that `sub_11DE6` was handwritten
assembly.

## `shot_velocity_set()` origin cross-check

All seven v117 natural probes already used `#pragma option -k-`, so stack-frame
suppression is not a missing experiment. The same target contains eleven
`MOV BX,SP; PUSH SI/DI` byte-shape occurrences including this function. Their
reviewed peers cluster in compiler/runtime/library code, the already
original-assembly `CDG_FREE` owner, or still-unreviewed target-derived assembly
candidates. There is no accepted natural C++ counterexample yet.

Borland/ReC98 compiler research also explains the v117 mismatch: a `-k-` C++
function that actually uses SI/DI saves those registers before ordinary body
statements, while the target captures `SP` in `BX` before saving `SI`.
Cross-game TH05 also reuses the same shot-velocity assembly source. Together
these observations strengthen an original-style assembly hypothesis but do not
meet the evidence bar for changing origin. The 28-byte boundary remains closed
and the source language remains unresolved.

## Continuation

The first structurally connected source candidate is the immediately preceding
`sub_11B44` / Yuuka6 entity renderer at load `0x11B44..0x11C19`, file
`0x13344..0x13419`, size `0xD6` / 214 bytes. `yuuka6_fg_render()` calls it at
its tail. ReC98 target assembly shows chase-cross and safety-circle rendering,
but the source form and exact owner still require TH04-local review.

Separately, exact promotion of the new foreground source still depends on a
legitimate resolution of the `shots_add` / `shot_velocity_set` / `sub_11DE6`
producer seam. Do not relabel either unresolved function as original assembly
solely to unblock linker order.
