# OP setup submenu exact replay (v745)

This packet promotes the two remaining natural setup submenus inside the
0x5A6-byte th04/op_setup.cpp OP_SETUP_TEXT producer.

- setup_bgm_menu starts at payload 0xB794 / loaded 1A74:1054 and is exactly
  0x11D / 285 bytes.
- setup_se_menu starts at payload 0xB8B1 / loaded 1A74:1171 and is exactly
  0x11D / 285 bytes.

Fresh target Ghidra reports both as contiguous single-range functions. MAP
ownership places both in the same current OP_SETUP_TEXT producer.

Maintained source:

- src/op/setup/setup_bgm_menu.inl
- src/op/setup/setup_se_menu.inl

Neither maintained body uses target-derived assembly, emitted opcodes,
optimization_barrier/keep_0 helpers, or pseudo-register forcing.

v745 injects only these two maintained bodies into the pinned current setup
translation unit. Two independent TC86/TLINK rounds reproduce both complete
285-byte bodies, the complete 0x5A6 producer, the full linked OP program image,
and all 804 ordered MZ relocation entries.

Focused receipt:
.analysis/reconstruction/receipt-archive/v745-op-setup-submenus-focused-receipt.json

Focused receipt SHA-256:
5724e2310acbc03fbc111f0c546cea658493e97c82d91dbaee5f7aae113c7a10

The in-memory v746 pre-acceptance aggregate passed 79/79 OP decoded slices.
After both rows were written into the checked-in acceptance ledger, canonical
v747 again passed 79/79.

Canonical aggregate receipt:
.analysis/reconstruction/receipt-archive/v747-op-setup-submenus-canonical-receipt.json

Canonical aggregate receipt SHA-256:
30294667ce38d0a1aef1871ffd0b36128dfcea4858fbe5553e5b399e022ec910

This establishes decoded-function exactness for the two setup submenus. It does
not claim packed-file or whole-OP exactness.
