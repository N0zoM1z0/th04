# MAINE verdict owner exact replay and BB81 boundary correction (v717)

The old v475 reconstruction note treated payload 0xBB81..0xC0F7, size 0x577,
as the sub_BB81 function. Fresh physical ownership review shows that was too
wide.

The current target evidence closes the layout as follows:

- sub_BB81 starts at payload 0xBB81 / loaded 1A05:1B31;
- expanded TASM ends the PROC at local 0x1211, so the function body is exactly
  payload 0xBB81..0xC0E0, size 0x560;
- payload 0xC0E1 is one compiler alignment byte;
- payload 0xC0E2..0xC0F7 contains two compiler-generated switch tables;
- verdict_animate starts at payload 0xC0F8 and is exactly 0x51 bytes;
- the 0x5C8 th04/vb.cpp MAP contribution ends exactly at SCORE_TEXT payload
  0xC149.

This explicitly rejects the Ghidra auto-function for sub_BB81 as a physical
boundary. Ghidra merges seven ranges across an unrelated 0xA9CE span. That
remains useful control-flow evidence, but it does not own those distant bytes.

Maintained source is split into:

- src/maine/end/sub_BB81.inl
- src/maine/end/verdict_animate.inl

The replay injects only these two maintained bodies into the pinned current
th04/vb.cpp translation unit. Two independent TC86/TLINK cold rounds reproduce:

- all 0x560 bytes of sub_BB81;
- all 0x17 bytes of the adjacent compiler alignment/switch-table extent;
- all 0x51 bytes of verdict_animate;
- the complete 0x5C8 vb.cpp MAINE_01_TEXT producer;
- the full linked MAINE program image;
- all 559 ordered MZ relocation entries.

Focused receipt:
.analysis/reconstruction/receipt-archive/v717-maine-verdict-owner-focused-receipt.json

Focused receipt SHA-256:
ce644a7687132c35a61ff0c3d2eef8adfd67b047f0f3a0e7cec4b9c053e625a0

The in-memory v718 pre-acceptance aggregate passed 56/56 raw-zero slices.
After both functions were entered into the checked-in acceptance ledger, v719
replayed the canonical ledger and again passed 56/56.

Canonical aggregate receipt:
.analysis/reconstruction/receipt-archive/v719-maine-verdict-owner-canonical-receipt.json

Canonical aggregate receipt SHA-256:
6b877fd1b1512b12f0bfe72ea2d0a5d8dc193443fdb20ef6e933f67d355414f7

This establishes decoded-function exactness for both functions and compiler
auxiliary ownership for the 0x17 bytes between them. It does not claim
packed-file exactness, whole-MAINE exactness, or literal historical-source
provenance.
