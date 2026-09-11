# TH04 MAIN_032 point-number shared-tail boundary review (v135)

## Scope

This packet reviews the dual-entry point-number add PROC in `MAIN_032_TEXT`
without granting source or exactness credit. The selected target is the local
Japanese `MAIN.EXE`, SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
Its canonicality remains only `candidate-local-attested`.

The physical target PROC occupies load `0x13D90..0x13DF0`, file
`0x15590..0x155F0`, and Ghidra image `0x23D90..0x23DF0`, for `0x61` bytes.
Its SHA-256 is
`8af1558b889add6229f53be0a8d44f05c8548c1df89f00fdd2f38d52d83b515d`.
No MZ relocation overlaps this physical extent.

## Logical entries and shared tail

The target has two independent TLINK publics with the same Pascal-near
three-word argument ABI:

- `pointnums_add_yellow(int,int,unsigned int)` at `MAIN_032_TEXT 13A9:0300`,
  image `0x23D90`;
- `pointnums_add_white(int,int,unsigned int)` at `MAIN_032_TEXT 13A9:031A`,
  image `0x23DAA`.

Fresh Ghidra creates both entries, but its apparently closed yellow body is a
boundary false positive. Yellow executes the contiguous entry stub
`0x23D90..0x23DA9` (`0x1A` bytes), whose final instruction is `JMP 0x23DBE`.
The destination is a shared tail at `0x23DBE..0x23DF0` (`0x33` bytes), also
reached by the white entry. Yellow therefore has two logical execution ranges
containing `0x4D` bytes across a `0x61` span. It is not a continuous 0x61-byte
function and it is not a closed 0x1A-byte function.

White is contiguous from `0x23DAA..0x23DF0`, size `0x47`. Its normal fallthrough
enters the same tail. The shared tail converts the selected ring index in `BX`
into a `pointnum_t` pointer, marks the slot alive, then only at image `0x23DC9`
executes `PUSH BP; MOV BP,SP` before reading the three Pascal parameters. It
ends in `RET 6` at `0x23DEE`.

Provider callers resolve both entries to the item-collection function. Fresh
xrefs show target calls to white at `0x2CBCF` and `0x2DDBA`, and to yellow at
`0x2DDC6`. Thus the two publics are real ABI entry points, not symbol aliases.
Ghidra's body construction remains provisional and receives zero exactness
credit.

## Natural TC4J probes

v134 already falsified two ordinary source families. Two normal Pascal C++
functions duplicate the common body and emit `0xB6` code bytes. A white-only
Borland pseudo-register form can keep the ring index in `BX`, but emits `0x49`
bytes versus target `0x47`: it creates `PUSH BP; MOV BP,SP` at the public entry
rather than the shared tail and lowers the final digit pointer as
`MOV AX,BX; ADD AX,0xB` instead of target `LEA AX,[BX+0xB]`. `-O`, `-O-`, `-k`,
and `-k-` do not repair that shape.

v135 tested the remaining high-value compiler hypotheses rather than expanding
the flag matrix blindly. `#pragma option -G` and `-G-` both emit exactly the
same 73-byte white CODE stream as the v134 pseudo-register baseline, SHA-256
`6829d03a1cf40518a503f071b47562f8b139b64b399415165418125e65ef3516`.
Neither setting delays the BP frame.

A genuinely different natural source then modeled the target as two public
wrappers that end by calling one same-signature `static near` common helper.
If TC4J performed sibling-tail-call lowering, this could naturally explain the
yellow jump, white fallthrough, and delayed helper frame. TC4J instead emits
135 bytes: both wrappers build their own BP frames, repush all three Pascal
arguments, `CALL` the common helper, and then `RET 6`. An explicit
`return common(args)` spelling is rejected by TC++ 4.02 for the `void` Pascal
wrappers. No sibling-tail-call form was demonstrated.

These probes are diagnostic compiler evidence only and carry zero exactness
credit. They establish that the known ordinary TC4J source families do not
produce the target's two-public/one-shared-tail layout. They do not prove that
the historical source was assembly.

## Origin status

ReC98 represents this PROC as `th04/main/pointnum/add.asm`. Its file history
starts with the 2020-01-14 commit `[Reverse-engineering] [th04/th05] Point
number popup add functions`. That is useful source-shape evidence, not an
independent record of ZUN's original source language. Therefore
original-style/irreducible assembly remains an active hypothesis, but origin is
still `unknown` for reconstruction purposes.

The machine boundary ledger is corrected to mark both entries `reviewed` while
leaving `accepted_state=unreviewed`: yellow records logical body size `0x4D`
and span `0x61`; white records its contiguous `0x47` body. No maintained source,
exact unit, focused replay, aggregate replay, or Factory claim is created by
this packet.

## Continuation

The best evidence-connected continuation is the point-number lifecycle/render
cohort in `CIRCLE_TEXT`: `POINTNUMS_INIT`, `pointnums_invalidate()`,
`POINTNUMS_UPDATE`, `POINTNUMS_RENDER`, and `@pointnum_put`. Their current
boundaries are corroborated, they form a substantially larger semantic cohort,
and recovering their natural TC4J source may expose original register/layout
idioms that can falsify or support a future revisit of this dual-entry PROC.
