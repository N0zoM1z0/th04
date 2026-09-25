# MAINE sub_B9F2 physical ownership and exact replay (v714)

The old boundary ledger marked sub_B9F2 provisional because Ghidra exposed a
non-contiguous two-range body: 0x148 reachable addresses across a 0x182-byte
span. That auto-function shape was not sufficient evidence of physical
ownership.

Fresh review reconciles the target, expanded TASM listing, MAP adjacency, and
compiler output:

- sub_B9F2 PROC starts at TASM offset 0xB22 / MAINE payload 0xB9F2;
- LEAVE / RET occupies payload 0xBB72..0xBB73;
- sub_B9F2 ENDP is at TASM offset 0xCA4 / payload 0xBB74;
- payload 0xBB74 is one compiler alignment byte;
- payload 0xBB75..0xBB80 is a six-word CS-relative switch table for
  resident->credit_lives;
- the next PROC and MAP public, sub_BB81, begins exactly at payload 0xBB81.

Therefore the reviewed function body is the complete 0x182-byte interval
[0xB9F2, 0xBB74). The following 0x0D bytes are compiler-owned auxiliary data,
not function code and not part of the next function.

Maintained source is src/maine/end/sub_B9F2.inl. It is ordinary C++ using
32-bit bonus arithmetic, two switches, irand(), the item-collection penalty,
the million-fraction renderer, and no target-derived assembly or pseudo-register
forcing.

Focused v714 performs two independent TC86/TLINK cold rounds. Both reproduce:

- all 386 bytes of the reviewed function body;
- all 13 bytes of adjacent compiler alignment/switch-table ownership;
- the complete 0x3FA-byte gv MAINE_01_TEXT producer at payload 0xB787;
- the full linked MAINE program image;
- all 559 ordered MZ relocation entries.

Focused receipt:
.analysis/reconstruction/receipt-archive/v714-maine-sub-b9f2-focused-receipt.json

Focused receipt SHA-256:
0ab85b35d5b53c64021b0d99473ef337e720ebf8512b418bb3e39ca98d5628c2

The in-memory v715 pre-acceptance aggregate passed 54/54 raw-zero slices.
After the B9F2 row was written into the checked-in acceptance ledger, v716
replayed the canonical ledger from disk and again passed 54/54.

Canonical aggregate receipt:
.analysis/reconstruction/receipt-archive/v716-maine-sub-b9f2-canonical-receipt.json

Canonical aggregate receipt SHA-256:
e0ae500e71e305cd0d5b2fa902d09c884cf59afdc81dd3ce75874cb21a9bada3

This establishes decoded-function exactness and compiler auxiliary ownership. It
does not claim packed-file exactness, whole-MAINE exactness, or literal
historical-source provenance.
