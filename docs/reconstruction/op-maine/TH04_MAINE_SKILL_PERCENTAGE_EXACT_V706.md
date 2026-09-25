# MAINE skill percentage exact replay (v706)

Target-first review closes MAINE payload 0xB886..0xB97A as one contiguous
245-byte owner at loaded 1A05:1836. Ghidra reports one caller and two callees;
the MAP public and pinned gv.cpp candidate corroborate the skill percentage
owner.

Maintained source is src/maine/end/skill_apply_and_graph_percentage_put.inl.
The focused replay replaces only this function inside the pinned gv.cpp
translation unit and performs two independent TC86/TLINK cold rounds.

Both rounds reproduce all 245 function bytes, the complete 0x3FA-byte gv
MAINE_01_TEXT producer at payload 0xB787, the full linked MAINE program image,
and all 559 ordered relocations.

Focused receipt:
.analysis/reconstruction/probes/v706-maine-skill-percentage-focused-001/receipt.json

Focused receipt SHA-256:
711e15f944777311e58ce38259f7e452efb7e3b341b3e08eb8546775ce63c39f

The pre-registration aggregate then passes 51/51 MAINE decoded slices
raw-zero.

Aggregate receipt:
.analysis/reconstruction/probes/v707-maine-skill-percentage-aggregate-preaccept-001/receipt.json

Aggregate receipt SHA-256:
77f82887ad5c17e118a7686ef813b034bc62136ceada4d47ff6f687c99afa54e

This establishes decoded-function exactness, not packed-file or whole-MAINE
exactness and not literal historical source provenance.
