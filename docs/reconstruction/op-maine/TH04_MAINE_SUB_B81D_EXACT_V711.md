# MAINE sub_B81D exact replay (v711)

Target-first review closes MAINE payload 0xB81D..0xB885 as one contiguous
105-byte owner at loaded 1A05:17CD. Fresh Ghidra inventory reports one caller
and two callees; the terminal POP SI / LEAVE / RET ends exactly at the next
gv.cpp owner. The MAP public/TASM PROC and pinned gv.cpp candidate independently
corroborate the sub_B81D entry.

Maintained source is src/maine/end/sub_B81D.inl. It formats the resident
last-score digits into gaiji while suppressing leading zeroes, then emits the
score suffix. The focused replay replaces only this function inside pinned
gv.cpp and performs two independent TC86/TLINK cold rounds.

Both rounds reproduce all 105 function bytes, the complete 0x3FA-byte gv
MAINE_01_TEXT producer at payload 0xB787, the full linked MAINE program image,
and all 559 ordered relocations. No target-derived assembly or pseudo-register
forcing is used.

Focused receipt:
.analysis/reconstruction/receipt-archive/v711-maine-sub-b81d-focused-receipt.json

Focused receipt SHA-256:
18ee59fb94495d3a81aabbc34857f77d6ac3f64912d4671ee858d4c8bcba9d2b

The in-memory pre-acceptance aggregate v712 contains 53 raw-zero MAINE slices.
After the row was written to the checked-in acceptance ledger, canonical v713
replayed that ledger from disk and again produced 53/53 raw-zero slices.

Canonical aggregate receipt:
.analysis/reconstruction/receipt-archive/v713-maine-sub-b81d-canonical-receipt.json

Canonical aggregate receipt SHA-256:
18cbacfce79b25be869a9646158c8d966a1ad75a268fbb9e1a73d79233e8a357

This establishes decoded-function exactness for the 105-byte owner. It does not
claim packed-file exactness, whole-MAINE exactness, or literal historical-source
provenance. The adjacent sub_B9F2 remains a separate physical-ownership problem
because its automated Ghidra body is non-contiguous.
