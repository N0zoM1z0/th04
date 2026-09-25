# OP remaining m_char.cpp functions exact replay (v738)

The current v489 OP snapshot already proved the complete m_char.cpp OP_01_TEXT
producer at payload 0xCF5E, size 0xAB3. v738 re-tests the five still-unaccepted
functions in that producer by replacing only their maintained natural-C++ bodies.

Accepted functions:

- raise_bg_allocate_and_snap at 0xCF5E: 0x1A1 / 417 bytes;
- raise_bg_put at 0xD0FF: 0xF4 / 244 bytes;
- pic_put at 0xD3A2: 0xC3 / 195 bytes;
- shottype_titles_put at 0xD465: 0x130 / 304 bytes;
- shottype_title_box_put at 0xD595: 0xBB / 187 bytes.

All five target bodies are contiguous Ghidra ranges and each MAP public remains
inside the same th04/m_char.cpp contribution. The maintained source uses
ordinary C++ and normal far-memory VRAM lvalue macros; it does not introduce
optimization_barrier, keep_0, codestring bytes, inline assembly, or explicit
pseudo-register forcing.

Two independent v738 TC86/TLINK cold rounds reproduce:

- all five complete function bodies;
- the complete 0xAB3 m_char.cpp producer;
- the full linked OP program image;
- all 804 ordered MZ relocation entries.

Focused receipt:
.analysis/reconstruction/receipt-archive/v738-op-mchar-remaining-focused-receipt.json

Focused receipt SHA-256:
9c9aa2898dd34851158e363fbd1f68e5c466b1b96a8a930e4416e10d1ec38ddd

The in-memory v739 pre-acceptance aggregate passed 71/71 OP decoded slices.
After the five rows were written to the checked-in acceptance ledger, canonical
v740 replayed that ledger and again passed 71/71.

Canonical aggregate receipt:
.analysis/reconstruction/receipt-archive/v740-op-mchar-remaining-canonical-receipt.json

Canonical aggregate receipt SHA-256:
61f06b7a708ad3f205d844a50effc3c3d4d0fbc8b9378453b3aaf7735afdb05b

This establishes decoded-function exactness for these five functions. It does
not claim packed-file or whole-OP exactness.
