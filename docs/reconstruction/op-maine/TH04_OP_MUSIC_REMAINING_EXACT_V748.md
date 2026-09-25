# OP Music Room remaining exact replay (v748)

This packet resolves the two remaining natural C++ functions selected from the
0x6A5-byte th04/op_music.cpp OP_MUSIC_TEXT producer.

## polygons_update_and_render

The target entry is payload 0xC04E / loaded 1A74:190E. Ghidra exposes 397
reachable bytes across a 0x1F6-byte span in two ranges. That auto-body is not a
valid physical ownership boundary.

Target bytes, MAP ownership, TC86-generated PROC/ENDP structure, terminal RET,
and cold replay close the complete 0x1F6 / 502-byte physical function body.
There is no adjacent compiler switch table.

Maintained source:
src/op/music/polygons_update_and_render.inl

## musicroom_menu

The target entry is payload 0xC3B7 / loaded 1A74:1C77. Ghidra reports one
contiguous 0x1C3 / 451-byte body. TC86-generated PROC/ENDP and MAP ownership
agree, and the function ends at the OP_MUSIC_TEXT producer boundary.

Maintained source:
src/op/music/musicroom_menu.inl

Neither maintained body uses target-derived assembly, emitted opcodes,
optimization_barrier/keep_0 helpers, or pseudo-register forcing.

v748 injects only these two maintained bodies into the pinned current Music
Room translation unit. Two independent TC86/TLINK rounds reproduce both
complete function bodies, the complete 0x6A5 OP_MUSIC_TEXT producer, the full
linked OP program image, and all 804 ordered MZ relocation entries.

Focused receipt:
.analysis/reconstruction/receipt-archive/v748-op-music-remaining-focused-receipt.json

Focused receipt SHA-256:
d995791398bb93f6d6779311fc8086d7d393c70912b3a3cb55906b150c80e6c0

The in-memory v749 pre-acceptance aggregate passed 81/81 OP decoded slices.
An initial v750 canonical attempt stopped when an older shared-VRAM backend's
internal preflight returned nonzero during a transient dirty-state window; it
produced no canonical receipt. Top-level preflight then passed, and v751
replayed the current checked-in acceptance ledger successfully at 81/81.

Canonical aggregate receipt:
.analysis/reconstruction/receipt-archive/v751-op-music-remaining-canonical-receipt.json

Canonical aggregate receipt SHA-256:
47cd2eb24d5318e826f65ed2ad971c257bf4935f160e4fb89417a659f1bda448

This establishes decoded-function exactness for both Music Room functions. It
does not claim packed-file or whole-OP exactness.
