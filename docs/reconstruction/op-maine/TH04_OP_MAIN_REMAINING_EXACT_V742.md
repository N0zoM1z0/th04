# OP main-menu producer boundary correction and exact replay (v742)

This packet resolves the six remaining authored functions in the 0xD53-byte
th04/op_main.cpp OP_MAIN_TEXT producer. Five of the six had provisional Ghidra
auto-functions whose multi-range spans escaped their physical owner.

The pinned current TC86 4.02 source was recompiled with -S to obtain the
compiler's own PROC/ENDP and switch-table structure. The generated assembly is
used only as structural evidence: include-file debug records and private static
symbol names can vary when maintained bodies are included. Executable identity
is gated by the OMF CODE stream, linked target bytes, full program image, MAP,
and ordered relocations.

The target-reviewed layout is:

- start_demo at 0xA9C9: 0xE4 / 228-byte body, followed by an 0x08 four-word
  compiler switch table;
- main_unput_and_put at 0xAAB5: 0x115 / 277-byte body, followed by one pad
  byte and a six-word switch table (0x0D auxiliary bytes);
- option_unput_and_put at 0xABD7: 0x240 / 576-byte body, followed by one pad
  byte and an eight-word switch table (0x11 auxiliary bytes);
- main_update_and_render at 0xAE96: 0x1B0 / 432-byte body, followed by a
  six-word switch table (0x0C auxiliary bytes). TC86 -S emits an
  uninitialized pad directive here, but target file bytes show no extra
  file-backed pad;
- option_update_and_render at 0xB052: 0x30C / 780-byte body, followed by one
  pad byte and two six-word switch tables (0x19 auxiliary bytes);
- OP _main at 0xB377: 0x128 / 296-byte body, with no auxiliary table.

Maintained source:

- src/op/main/start_demo.inl
- src/op/main/main_unput_and_put.inl
- src/op/main/option_unput_and_put.inl
- src/op/main/main_update_and_render.inl
- src/op/main/option_update_and_render.inl
- src/op/main/main.inl

These bodies contain no keep_0, optimization_barrier, inline target assembly,
emitted opcodes, or pseudo-register forcing.

v742 performs two independent cold TC86/TLINK rounds. Both reproduce every
reviewed function body, every adjacent compiler table extent, the complete
0xD53 OP_MAIN_TEXT producer, the full OP program image, and all 804 ordered MZ
relocations. The OMF OP_MAIN_TEXT CODE stream is also identical to the pinned
current producer in both rounds.

Focused receipt:
.analysis/reconstruction/receipt-archive/v742-op-main-remaining-focused-receipt.json

Focused receipt SHA-256:
e1954c39f61ddad9c1cda94d10dc18b7721f5e84d01877a81a3acdd842a6558a

The in-memory v743 pre-acceptance aggregate passed 77/77 OP decoded slices.
After the six rows were written into the checked-in ledger, canonical v744
again passed 77/77.

Canonical aggregate receipt:
.analysis/reconstruction/receipt-archive/v744-op-main-remaining-canonical-receipt.json

Canonical aggregate receipt SHA-256:
e24181d3572c50ff6948e7db0fd761b867ff4a8251ae299d3ae0c204f16a3b7f

This establishes decoded-function exactness for the six bodies and physical
ownership of their adjacent compiler switch tables. It does not claim
packed-file or whole-OP exactness.
