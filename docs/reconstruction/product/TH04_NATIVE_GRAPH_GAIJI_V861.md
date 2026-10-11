# TH04 native graphics gaiji writers

## Complete DOS address and return-state recovery (v1406)

The maintained `graph_gaiji.cpp` now carries the string's byte offset between
characters. Each glyph adds `cursor >> 3` to the existing WORD offset, keeps
the residual bit shift, and adds the WORD step for the next character. This
recovers the original negative and large-step recurrence. Each row writes a
WORD followed by the separately wrapped spill byte. A WORD starting at FFFFh
writes its second byte at the next physical address; splitting that store into
two byte pointers had wrapped the second byte to offset zero. Both entries
also return with ES selecting `graph_VramSeg`, including an empty string.

The original OP entries are 0000:3E34 / 0000:3D8A; MAINE uses
0000:3760 / 0000:36B6. `scripts/runtime/verify_dos_gaiji.py` executes the
attested decoded originals and actual linked products at load segments 1000
and 3333. All 4,800 controls agree on the complete 65,537-byte write mask,
ordered write addresses, widths and values, CG/GRCG port order and interrupt
state. Far Pascal stack cleanup, DS/SI/DI/BP preservation and return ES pass.
The corpus covers all byte glyph codes, all shifts, additional WORD codes,
coordinate boundaries, twelve steps, NUL termination, empty strings and long
strings. CG input is an explicit deterministic fixture selected by actual
port writes; this comparison does not model physical display timing.

The compiled v1400 MAINE predecessor fails all 2,400 controls on write width
or return ES; 150 controls also differ in their final address masks. At
X120/Y819 a glyph's WORD crosses FFFFh. At X-8/Y32, negative string steps
expose the old coordinate-recalculation error. Port sequences remain equal.
The first v1406 candidate passed writes but retained 880 ES differences per
artifact; its source, transcripts and receipt remain separate from the final
accepted candidate.

OP and MAINE were cold-built without historical support libraries. The ES
correction then freshly compiled Gaiji and the builder's BGIMAGE unit in each
product, reusing only verified unchanged objects (163/165 OP, 137/139 MAINE).
Both final links and IRQ vector audits pass with zero warnings or unresolved
symbols. Final producer `product-20261011-180052-085f918e` uses input
fingerprint `cfaa77bf8548cb224c5cc57c23d31baa7f5b9f2ec49f92fbc9a37e1e1e734622`.
OP is 79,420 bytes; MAINE is 72,294 bytes. MAIN and ZUN were unaffected.

Private replay inputs and complete comparisons are under
`.analysis/reconstruction/probes/dos-gaiji-v1406/`. `verify_closure.py` checks
the 1,425-file source freeze, products, MAPs and every transcript frame.
Use the maintained verifier with `--artifact`, `--exe`, `--map` and a fresh
`--output` directory. Historical exact acceptance remains 661/663.

## Initial DOS source migration (v861)

2026-09-27 product-build investigation. The TH04-local
`src/shared/hardware/graph_gaiji.cpp` owns far Pascal `GRAPH_GAIJI_PUTC` and
`GRAPH_GAIJI_PUTS`. The code selects GRCG RMW mode and four color tiles,
switches the character generator to dot access, reads both halves of each
of 16 glyph rows from ports `0xA5`/`0xA9`, and writes three shifted bytes per
row into the current `graph_VramSeg` graphics plane. It restores CG code
access and turns GRCG off. The interrupt flag is preserved around the GRCG
mode port write. Drawing has no clipping, as in the bounded reference.

The glyph code uses `(c + 0x5680) & 0xFF7F`. This ordinary addition is also
observed at the local opcode sites of the four independently restored
TH04/TH05 OP/MAINE targets in the
[v493 MASTER version note](../packed/TH04_ZUN_MASTER_VERSION_V493.md);
the generic historical library still has the older carry-dependent variant.
All 524,288 combinations of two CG bytes and eight bit shifts agreed with
the bounded reference's three output bytes in a local algebra check.
MAINE's six maintained `GRAPH_GAIJI_PUTS` calls use `GAIJI_W == 16` as their
step. Other steps and interrupt/display timing remain unobserved; the
historical string routine has an unusual 16-bit byte-offset recurrence for
negative steps that this C++ product candidate does not reproduce.

Two cold no-archive MAINE builds compile 117 TH04 units (75 C++, 42 ASM).
They leave 23 unresolved names and zero warnings, two fewer than the text
gaiji checkpoint. Link-relevant and timestamp-normalized OMF records agree;
BGIMAGE alone has its known raw timestamp drift. The two private receipt
SHA-256 values are
`c9caa0e92b3829d5c7349c718b2bbd7ba9919bbae30dec984c13afd80a3aad7d`
and `e59a67d5302e5a4552ba6b89959020d3f9e5132076270a3fb9824f15d0ec9f6e`.
The manifest SHA-256 is
`c9b5552e1d6547aac0a3c5f9b55a8008850123c3f8f094c7c18c7e9e44dcdf56`.

The historical-library calibration TLINK link exits 0 (receipt
`b3006658a1349ec1402e8c663efff528f6d0c3d1dc25828fc7041bc7515af098`).
The MZ audit validates 597 relocation sites and two DOS load segments
(receipt `cc76f5c7e9cd97ed408207c55a139f1361911448db401f37b00b61ee034e03a7`).
The call ABI audit checks 19 far entries, 75 relocated direct far calls and
one same-CS `push cs; call rel16` (receipt
`02e2a1aa2fa2066151d562f16b093bd00d82b4e2d390efcf13a49912bffcf65c`).
The calibration MAP locates `GRAPH_GAIJI_PUTC` at `0993:3191` with `RETF 8`
and `GRAPH_GAIJI_PUTS` at `0993:31B3` with `RETF 12`; these are linked
calibration addresses, not original target addresses. This MZ still contains
historical-library support, and no MAINE runtime scenario has exercised the
PC-98 display path.

For TH05, keep target glyph-code opcodes, far Pascal cleanup, CG/GRCG port
order, VRAM output bytes, and actual screen timing as separate gates.
