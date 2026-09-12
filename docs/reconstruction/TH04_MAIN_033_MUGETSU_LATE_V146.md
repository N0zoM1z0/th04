# TH04 MAIN_033_TEXT Mugetsu late callbacks and physical producer (v146)

## Scope

Artifact: `th04-main / MAIN.EXE` (`candidate-local-attested`). Target SHA-256:
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The ignored private executable was read only and was not patched, replaced,
relocated, staged, committed, or published.

v146 reviews the eight Mugetsu functions immediately after the v145 callback
pair and tests the stronger physical-producer hypothesis suggested by v145's
ordered-relocation failure.

The reviewed late owner is MAIN_033_TEXT `13A9:49CE..4F5D`, load
`0x1845E..0x189ED`, file `0x19C5E..0x1A1ED`, size `0x590`. Its target SHA-256 is
`4c4f4e9df4710e98898785b19490f7bdeb57400d72081eb68cba64eb41f21b4d`.
`POINTNUM_DIGITS_SET` begins independently at load `0x189EE`; its post-ENDP NOP
is at `0x18A13`, followed by the existing Kurumi owner at `0x18A14`. Those bytes
are not assigned to Mugetsu.

## Boundary review

| Function | Load | File | Reviewed physical size | Fresh Ghidra |
| --- | --- | --- | ---: | --- |
| `mugetsu_1845E` | `0x1845E` | `0x19C5E` | `0x4E` | contiguous |
| `mugetsu_184AC` | `0x184AC` | `0x19CAC` | `0xAA` | sparse two-range body |
| `mugetsu_18556` | `0x18556` | `0x19D56` | `0x8E` | sparse two-range body |
| `mugetsu_185E4` | `0x185E4` | `0x19DE4` | `0x71` | contiguous |
| `mugetsu_18655` | `0x18655` | `0x19E55` | `0x2F` | contiguous |
| `MUGETSU_PHASE2_NEXT` | `0x18684` | `0x19E84` | `0x35` | contiguous |
| `mugetsu_186B9` | `0x186B9` | `0x19EB9` | `0x32` | contiguous |
| `mugetsu_update()` | `0x186EB` | `0x19EEB` | `0x303` | severely cross-linked |

Pinned TASM, gap-free target decode, next-PROC adjacency, and direct call sites
inside `mugetsu_update()` close all seven near helper extents. The sparse Ghidra
bodies at `0x284AC` and `0x28556` are explicitly rejected in favor of the full
`0xAA` and `0x8E` target extents.

Fresh Ghidra is unusable as an extent oracle for the FAR dispatcher: its body is
cross-linked across seven ranges far outside the Mugetsu region. Target/TASM
review instead closes `mugetsu_update()` as `0x303` physical bytes. The first
`0x2CE` bytes are executable through the common-tail `RETF` at load `0x189B8`.
The trailing `0x35` bytes contain one zero compiler metadata byte, the nine
values `0..7, 255`, a nine-word mode jump table, and an eight-word phase jump
table. Every jump-table word resolves to an instruction start inside the reviewed
executable body. The independent point-number owner starts immediately afterward
at `0x189EE`.

`boss_update_func` installs the FAR `mugetsu_update()` entry. The dispatcher, in
turn, directly calls each reviewed near helper, providing target-local caller
ownership despite Ghidra reporting zero callers.

## Maintained natural source

`src/main/boss/mugetsu_late.cpp` is the maintained natural C++ source for the
complete `0x590` late owner. SHA-256 is
`52847829bf0715b4571b47bd95d2b64f8de3dc1751e51f69e68945acde98c103`.
It uses existing TH04 boss, bullet, player, frame, RNG, sound, and callback
surfaces, with only the existing one-line `compat/rec98` forwarding layer for
unlocalized upstream declarations. It contains no inline assembly, target-derived
byte arrays, `#pragma codestring`, copied target bytes, fake returns, inert
padding, ABI lies, or target patching.

The actual tracked text was forwarder-resolved into the pinned ReC98 probe tree
and compiled with the production TC4J profile. It produces valid TC86 Borland
C++ 4.02 OMF; dependency-normalized object SHA-256 is
`39a53ebad9744211d9d097a5eb0406a88b85c7d3ca8c4b875742a5841a00e412`.
This proves source presence and compiler viability only.

Two source-shape observations are material. The random bullet origins in
`mugetsu_184AC` and `mugetsu_18556` must preserve the RNG result in AX while the
boss coordinate is formed in DX. Ordinary compound expressions let TC4J fold
that into `ADD AX,[boss]; SUB AX,imm` and shorten the functions. Legal Borland
pseudo-register dataflow through `_DX` and `_AX` naturally emits the target
`MOV DX,[boss]; ADD DX,imm; ADD AX,DX` sequence and restores both exact target
lengths. In `mugetsu_update()`, direct `switch(boss.mode)`, one shared case label,
and explicit `_AL/_AX` lifetime for the random phase selector naturally recover
the target `ENTER 4,0`, switch scan, trampoline order, and two distinct shift
instructions.

## Physical-producer evidence

The target region from the already maintained Mugetsu gather prefix through the
end of `mugetsu_update()` is one contiguous candidate:

- MAIN_033_TEXT `13A9:459F..4F5D`;
- load `0x1802F..0x189ED`;
- file `0x1982F..0x1A1ED`;
- size `0x9BF / 2495` bytes;
- SHA-256
  `465de67f247a69bdf95a6953de924c88f011f52943e794e945207b75bc6b55e9`.

The target's fourteen MZ relocations in this region form three ordered runs with
cardinality `7 / 6 / 1`. A private unified natural-source compiler probe combines
the maintained v107, v108, v144, v145 semantics with the new v146 late source.
TC4J naturally emits three CODE LEDATA/FIXUPP groups. The latest probe's
relocation-producing OMF topology is also `7 / 6 / 1`: seven Pointer32 fixups,
then five Pointer32 plus the Segment16 fixup for
`stage_vm = nullfunc_far`, then one Pointer32. A DOS MZ relocation for Pointer32
lands on the segment word at fixup offset `+2`. This independently explains the
v145 relocation-order failure as a physical translation-unit split problem.

The unified probe does **not** establish exactness or historical translation-unit
identity. Its current CODE contribution is `0x9B9`, six bytes short of the
`0x9BF` target candidate. The maintained v144 dense-transition source remains
nonexact and is still the upstream blocker. After masking only standard OMF link
fields, however, all seven v146 helper bodies have zero fixed-byte differences
from target, and the `mugetsu_update()` executable body also has zero fixed-byte
differences. Candidate and target reach their two dispatcher `RETF` instructions
at identical function-relative offsets. In the current nonexact fused layout,
the only dispatcher-owned size difference is the target's one-byte compiler
switch metadata before the value table.

This is strong, falsifiable compiler/target routing evidence that the Mugetsu
region should be reconstructed as a larger physical producer. It is deliberately
retained as an open question rather than a historical-source fact.

## Accounting and verification planes

v146 adds `0x590 / 1424` reviewed authored bytes and eight reviewed authored
functions without adding exact numerator credit. Live MAIN accounting becomes:

- reviewed authored bytes: **47,564 / 49,812 exact (95.487031%)**;
- reviewed authored functions: **300 / 313 exact (95.846645%)**;
- reviewed blocked functions: **13**;
- MAIN authored candidates still unreviewed: **230**.

The lower percentages are a deliberate denominator correction, not an exact-owner
regression.

No v146 focused or aggregate exact replay is run because the fused physical
producer is already known nonexact at the v144 prefix. Running promotion gates
would not convert the compiler diagnostics into exactness. The retained exact
baseline remains the v143 178-owner final aggregate.

Boundary ownership and maintained late-source presence are established.
Independent function/extent byte exactness is **not** established for the new
late owner. Standalone TH04 production-source/link closure remains unestablished.
Runtime-storage identity is unestablished. No runtime scenario is validated. No
v146 Factory acceptance claim is submitted or implied. Target provenance remains
`candidate-local-attested`.

## Continuation

Do not split the new late helpers into artificial exact standalone owners merely
because their fixed code bytes match. The next useful hypothesis is the remaining
v144 dense-transition producer mechanism inside the now strongly corroborated
larger physical-TU context. Existing v109/v144 branch-spelling and `-O` negatives
must be preserved; a new attempt should require a genuinely new compiler or
source-ownership mechanism. If that blocker is solved, fuse the maintained
v107/v108/v144/v145/v146 source and run the complete focused and aggregate Oracle
sequence against the `0x9BF` physical producer.
