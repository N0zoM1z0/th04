# Shared BGIMAGE FIXUPP direction control (v233)

## Observed candidate and target-restored order

The pinned v214 candidate `th04/bgimage.obj` is valid Intel OMF. Its
`SHARED` LEDATA is object offsets `0x000..0x0CF`, followed by one FIXUPP
record with 27 LOCAT offsets in strictly **descending** order. Eight of
those fixups become MZ relocation entries, at object offsets
`0xC5, 0xBC, 0xB3, 0xAA, 0x2E, 0x23, 0x18, 0x0D` in candidate order.
The candidate MZ relocation order agrees exactly with this OMF subsequence
in both OP and MAINE. Their target-restored MZ views contain the same eight
sites in exactly **reverse** order. The absolute MZ load-module site ranges
are OP `0xE437..0xE4EF` and MAINE `0xD635..0xD6ED`.

The [v232 owner projection](TH04_DIET_RELOCATION_OWNERS_V232.md) records the
full ordered tables, candidate MAP ownership, and attested target-restored
input hashes. The target OMF and historical pre-DIET MZ remain unavailable.

## Bounded symbolic assembler control

To test whether a different normal object producer could emit ascending
locations, the checked-in
`config/replay/th04_bgimage_fixup_direction_v233.asm.in` declares eight
external FAR symbols and emits `DW SEG F1` through `DW SEG F8` in
source order. Pinned TASM32 5.0 assembled it under the recorded Wine prefix
with `/m /mx /kh32768 /t`. Its valid OMF has one `SHARED` LEDATA and
FIXUPP LOCAT offsets `0, 2, 4, 6, 8, 10, 12, 14`: strictly
**ascending**. The source SHA-256 is
`90129f58a781ee197ab3c6436386a9482484d58e2fc50101e7d9c9b26dd3f2a8`;
object SHA-256 is
`d788ce1cbaf28fd08b3cf4c82e40f1513975c236b46b3489c4449838f16d7133`.
The private probe receipt is
`.analysis/reconstruction/probes/v233-bgimage-fixup/receipt.json`,
SHA-256
`4bb8847949d0dc1f916304f2a44f1319eb4499208008be6a7aaa523f0a8f1475`.

This control proves that the attested TASM producer can emit ascending
symbolic segment fixups. It does **not** reproduce BGIMAGE code, prove its
historical source form, or justify replacing its C++ with target-derived
assembly. The subsequent
[v234 assembly-output probe](TH04_BGIMAGE_B_MODE_V234.md) preserves all
BGIMAGE CODE bytes while reversing FIXUPP order in a diagnostic relink; its
upstream source still fails maintained-source acceptance.
