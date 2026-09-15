# TH04 MAIN player invalidation recovery (v176)

## Scope

This packet reviews and reconstructs `player_invalidate()` at the tail of
`MAIN__TEXT` in the attested local `MAIN.EXE` target. The private target remains
ignored operator input with `candidate-local-attested` canonicality. It is not
modified, patched, relocated, copied into tracked source, or treated as an
independently proven pristine release.

The corrected target extent is:

- group address: `0AAF:5CF2..5DA7`;
- load-module range: `0x107E2..0x10897`;
- file range: `0x11FE2..0x12097`;
- size: `0xB6` bytes;
- target slice SHA-256:
  `13b2ea1657c35eefbd27fb1eaa66c637f48815877175dfbe541e162d0e7a218b`.

The next byte, load `0x10898`, begins exact `PLAYER_M_TEXT` and the existing
`player_move(unsigned int)` owner.

## Boundary correction

The live Ghidra-derived inventory had recorded `body_size=0x94`,
`body_span=0xB6`, two noncontiguous ranges, and no direct callers. v176 does not
promote the Ghidra body construction itself. Independent target evidence closes
the complete `0xB6` function instead:

- TLINK exposes public `player_invalidate()` at `0AAF:5CF2`.
- Pinned TASM begins `@player_invalidate$qv proc near` at the same entry.
- Linear 16-bit target decoding tiles every byte through the final `RET` at load
  `0x10897`.
- The next code segment `PLAYER_M_TEXT` begins exactly at load `0x10898`, so
  there is no post-return jump table, alignment byte, or data owner inside this
  function extent.
- A target `E8` at load `0xCB5E`, inside MAP-public `tiles_render()` at
  `0AAF:2068`, resolves directly to offset `0x5CF2`. This supplies a target call
  anchor even though Ghidra reports zero callers.
- The complete function contains one MZ relocation, at load `0x10837`.

The machine boundary ledger therefore records the complete `0xB6` reviewed
extent while preserving the original Ghidra facts (`ghidra_contiguous=false`,
two ranges, zero reported callers) as provisional observations rather than
rewriting them into something the analysis provider did not report.

## Natural-source reconstruction

Maintained source is `src/main/player/invalidate.cpp`, SHA-256
`23e0e6ed67f9c5929cb629018a2e3597936591d64c81b8f4acca58bca515d966`.
It is ordinary Turbo C++ source and uses no inline assembly, target-derived byte
arrays, `#pragma codestring`, fake returns, inert padding, target patching, or ABI
lies.

The cheap compiler loop identified two source-shape details before replay:

1. Writing the explosion radius update as subtraction naturally emitted
   `SUB AX,0070`, while the target encodes the equivalent expression as
   `ADD AX,FF90`. Expressing the source operation as addition of the negative
   velocity produces the target instruction.
2. Passing adjacent `drawpoint.y` and `drawpoint.x` fields directly caused TC4J
   to coalesce them into one 32-bit `PUSH`, shortening the function by three
   bytes. The target performs two word-sized pushes. Exposing the existing two
   words through separate linkage-visible field names preserves the target
   two-word argument-expression shape without adding storage.

With these natural source choices, TC86 Borland C++ 4.02 emits the complete
`0xB6` instruction skeleton.

## Drawpoint storage aliases

The current ReC98-overlay data owner allocates one `Point` named `_drawpoint`,
exactly four bytes. The replay-only source transform preserves that four-byte allocation while
publishing field-level linkage names:

```asm
public _drawpoint, _drawpoint_x, _drawpoint_y
_drawpoint label Point
_drawpoint_x dw ?
_drawpoint_y dw ?
```

Candidate aggregate MAP confirms:

- `_drawpoint` = `2134:539A`;
- `_drawpoint_x` = `2134:539A`;
- `_drawpoint_y` = `2134:539C`.

Thus the two field names are aliases into the pre-existing storage, not duplicate
runtime state. This bounded layout fact does not establish whole-program runtime
storage identity.

## Physical producer split

Before v176, the extracted TASM object `th04/m1rsuf.asm` contributed the tail of
`MAIN__TEXT`, including the old reconstructed invalidate assembly. v176 removes
only `include th04/main/player/invalidate.asm` and inserts the natural object
`th04/pinv.cpp` immediately after `m1rsuf.obj` in the link order.

The residual `m1rsuf` contribution is exactly `0x8AE` bytes at `0AAF:5444` and is
still byte-identical to the target. Its target/candidate residual slice SHA-256 is
`c0958ca18d9268a00f477311230ffb9166661f52a2ce5540a615ef9e5b59d0d9`.
`pinv.cpp` then occupies `0AAF:5CF2..5DA7`, immediately before
`PLAYER_M_TEXT` at `0AAF:5DA8`, with no padding.

A deliberately broad auxiliary gate in focused candidate002 also required the
legacy residual `m1rsuf` object to reproduce historical relocation ordering over
its entire `0x8AE` extent. That gate failed even though the residual raw bytes and
MAP were exact. This is a pre-existing property of the target-derived residual
object, not a v176 source mismatch. The overbroad gate was removed and retained
as negative evidence. The new `pinv.cpp` owner independently reproduces its sole
target relocation exactly at load `0x10837`.

## Exact replay

Focused replay
`gptweb-v176-player-invalidate-focused-candidate-003` closes a 130-owner
dependency cohort twice with `failures=[]`. Receipt SHA-256 is
`9c035ee0083f251a5a4555b55483c23b725a4ac9e3ebad4cb63894190f2dd1c6`.

For both cold builds:

- MAP: `0AAF:5CF2 00B6 C=CODE S=MAIN__TEXT G=MAIN_01 M=th04/pinv.cpp`;
- raw slice: exact, SHA-256
  `13b2ea1657c35eefbd27fb1eaa66c637f48815877175dfbe541e162d0e7a218b`;
- target/candidate ordered relocation overlap: `[0x10837]`;
- raw object SHA-256:
  `b6f10fd0aa260b2e68e24070fbeec7f9920ce43f6bdbf205d02fec8c793e3b15`;
- dependency-normalized OMF SHA-256:
  `bcc0d8628214b4873921dbd6ff16a22cde54954b0a450d1901e80bf7e1e9c2b7`;
- translator: `TC86 Borland C++ 4.02`.

Candidate-state aggregate
`gptweb-v176-player-invalidate-aggregate-candidate-001` passes all 209 selected
default owners twice before ledger promotion. Receipt SHA-256 is
`99a1c1606ce7e30591bf38c012999e7a549f472a4de14cc9afb93898af083749`.

Post-promotion aggregate
`gptweb-v176-player-invalidate-aggregate-final-001` again passes all 209 default
owners twice with `failures=[]`. Receipt SHA-256 is
`7c5adbf291d878ee212744ca7fa0a4f436479ddd3a9798a61711b5f45cff48ee`.

All authoritative v176 exact runs bind replay manifest SHA-256
`e5736907b146b1a3005608e1947b2aeaba0cbca63b5b68bf6842761f1c15de86`.

## Accounting and verification planes

After v176 promotion, the non-overlapping MAIN ledger reports:

- `70,495 / 74,089` exact reviewed authored bytes (`95.149077%`);
- `415 / 429` exact reviewed authored functions (`96.736597%`);
- 14 reviewed blocked MAIN functions;
- 108 unreviewed MAIN authored candidates;
- 31 original-ASM attestation observations.

Repository-native owned-extent/function exactness is PASS for the complete
`player_invalidate()` owner and the 209-owner post-promotion cohort. Standalone
TH04 product compile/link closure is not established. Whole-program runtime
storage identity is not established. No runtime scenario was executed. Whole-
image exactness and portable-runtime validation are not established. No Factory
Truth-Kernel acceptance is submitted or claimed.

OP.EXE, MAINE.EXE, and ZUN.COM remain independent active authored-boundary queues
and receive no v176 MAIN credit. `ZUN.COM` remains an MZ executable despite its
extension.

## Continuation

The next packet should audit the connected `MAIN__TEXT` shot cohort rather than
harvest an isolated easy function. Start at provisional `shots_invalidate()` at
load `0x10444`: Ghidra reports `body_size=0x6C`, `body_span=0x72`, two ranges, so
it has the same class of boundary-construction risk just corrected here. Reconcile
it together with adjacent `sub_1042A`, `sub_104B6`, public `shots_render()`, FAR
`shots_hittest()` (eight reported callers), and the seam into `ENEMIES_RENDER` at
load `0x10713`. This connected window can expose shared tails, hidden compiler
data, near/far ABI shape, and physical producer/relocation ownership in one
coherent review.
