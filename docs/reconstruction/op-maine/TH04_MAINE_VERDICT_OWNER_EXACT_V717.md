# MAINE verdict owner exact replay (v717)

This packet re-reviews and cold-replays the final MAINE_01 verdict producer
rather than trusting the older v475/v476 boundary wording.

## Physical ownership correction

Ghidra's auto-function at sub_BB81 is not a physical function boundary: it
merges seven disjoint ranges and reports a 0xA9CE span. Expanded TASM and MAP
evidence instead close the producer as follows:

- sub_BB81 starts at payload 0xBB81;
- POP SI / LEAVE / RET ends its code at 0xC0DE..0xC0E0;
- sub_BB81 ENDP is at payload 0xC0E1;
- therefore the function body is exactly 0x560 bytes;
- payload 0xC0E1..0xC0F7 is 0x17 bytes of compiler auxiliary ownership: one
  alignment byte and two switch tables;
- verdict_animate begins at 0xC0F8 and is exactly 0x51 bytes;
- SCORE_TEXT begins at 0xC149.

This corrects the old shorthand that treated the full 0x577 pre-animate region
as the BB81 function. The 0x577 region is one function plus compiler auxiliary
data, not one function body.

## Maintained source and replay

Maintained source is:

- src/maine/end/sub_BB81.inl
- src/maine/end/verdict_animate.inl

Both are injected into the pinned current v489 th04/vb.cpp translation-unit
environment. Two independent TC86/TLINK cold rounds reproduce:

- all 0x560 bytes of sub_BB81;
- all 0x17 compiler auxiliary bytes;
- all 0x51 bytes of verdict_animate;
- the complete 0x5C8 vb.cpp MAINE_01_TEXT producer;
- the full linked MAINE program image;
- all 559 ordered MZ relocation entries.

No target-derived assembly or pseudo-register forcing is used.

Focused receipt:
.analysis/reconstruction/receipt-archive/v717-maine-verdict-owner-focused-receipt.json

Focused receipt SHA-256:
ce644a7687132c35a61ff0c3d2eef8adfd67b047f0f3a0e7cec4b9c053e625a0

The v718 in-memory pre-acceptance aggregate passed 56/56 raw-zero slices.
After both rows were written to the checked-in acceptance ledger, v719 replayed
that ledger from disk and again passed 56/56.

Canonical aggregate receipt:
.analysis/reconstruction/receipt-archive/v719-maine-verdict-owner-canonical-receipt.json

Canonical aggregate receipt SHA-256:
6b877fd1b1512b12f0bfe72ea2d0a5d8dc193443fdb20ef6e933f67d355414f7

This establishes decoded-function exactness and compiler auxiliary ownership.
It does not establish packed-file exactness, whole-MAINE exactness, or literal
historical-source provenance.
