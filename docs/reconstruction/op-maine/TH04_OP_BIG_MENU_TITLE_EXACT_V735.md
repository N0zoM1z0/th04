# OP big menu/title exact replay (v735)

This packet starts formal OP work after the MAINE strict-source frontier was
recorded. It deliberately targets two large functions rather than only leaf
helpers.

## op_animate

The target body starts at OP payload 0xCCD2 / loaded 1A74:2592 and is exactly
0x28C / 652 bytes. Fresh Ghidra reports one contiguous body with one caller and
twelve callees. The body ends exactly at the end of the 0x2C7 OP_TITLE_TEXT
contribution from th04/op_title.cpp at payload 0xCC97.

Maintained source:
src/op/title/op_animate.inl

## playchar_menu

The target body starts at OP payload 0xD708 / loaded 1A74:2FC8 and is exactly
0x309 / 777 bytes. Fresh Ghidra reports one contiguous body with two callers and
sixteen callees. The body ends exactly at the end of the 0xAB3 OP_01_TEXT
contribution from th04/m_char.cpp at payload 0xCF5E.

Maintained source:
src/op/menu/playchar_menu.inl

## Cold replay

v735 injects only the two maintained function bodies into the pinned current
v489 OP translation units. Two independent TC86/TLINK rounds reproduce:

- all 652 bytes of op_animate;
- all 777 bytes of playchar_menu;
- both complete TLINK producer contributions;
- the complete linked OP program image;
- all 804 ordered MZ relocation entries.


The in-memory v736 pre-acceptance aggregate passed 66/66 OP decoded slices.
After both rows were written to the checked-in acceptance ledger, canonical
v737 replayed that ledger and again passed 66/66.


The known two-byte shared SND_LOAD mismatch lies outside both producers and is
unchanged. This establishes decoded-function exactness for these two functions;
it does not claim packed-file or whole-OP exactness.
