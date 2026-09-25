# MAINE staffroll animation exact replay (v702)

Target-first review closes MAINE payload 0xB44D..0xB786 as one contiguous
826-byte owner at loaded 1A05:13FD. Ghidra reports one caller and 20 callees;
the MAP public and pinned candidate source corroborate the staffroll_animate
label.

Maintained source is src/maine/end/staffroll_animate.inl. The focused replay
replaces only this function inside the pinned staffall translation unit and
performs two independent TC86/TLINK cold rounds.

Both rounds reproduce all 826 function bytes, the complete 0x8B7-byte
MAINE_01_TEXT producer at payload 0xAED0, the full linked MAINE program image,
and all 559 ordered relocations.

Focused receipt:
.analysis/reconstruction/probes/v702-maine-staffroll-animate-focused-001/receipt.json

Focused receipt SHA-256:
297c0314a90837fc97685c3242c3f3c029d6705bf534923f24c01f33444f760e

The pre-registration aggregate then passes 49/49 MAINE decoded slices
raw-zero.

Aggregate receipt:
.analysis/reconstruction/probes/v703-maine-staffroll-animate-aggregate-preaccept-001/receipt.json

Aggregate receipt SHA-256:
7ebdbf33b2198cf5b94bce4db63e299dd6ee8cbf229c167cfcd72d135d693a1e

This establishes decoded-function exactness, not packed-file or whole-MAINE
exactness and not literal historical source provenance.
