# MAINE million-fraction renderer exact replay (v708)

Target-first review closes MAINE payload 0xB97B..0xB9F1 as one contiguous
119-byte owner at loaded 1A05:192B. Ghidra reports two callers and two callees;
the MAP public and pinned gv.cpp candidate corroborate the
graph_fraction_of_million_put label.

Maintained source is src/maine/end/graph_fraction_of_million_put.inl. The
focused replay replaces only this function inside the pinned gv.cpp translation
unit and performs two independent TC86/TLINK cold rounds.

Both rounds reproduce all 119 function bytes, the complete 0x3FA-byte gv
MAINE_01_TEXT producer at payload 0xB787, the full linked MAINE program image,
and all 559 ordered relocations.


The final current-ledger aggregate is v710. It is driven by the checked-in
acceptance ledger with no in-memory candidate injection and contains 52 unique
MAINE slices; all 52 compare raw-zero.


The earlier v709 pre-acceptance output was later overwritten by a duplicate-row
diagnostic and is deliberately not cited as canonical evidence.

This establishes decoded-function exactness, not packed-file or whole-MAINE
exactness and not literal historical source provenance.
