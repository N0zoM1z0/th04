# TC4.02 SCORE rotate-intrinsic negative surface (v760)

The remaining OP and MAINE SCORE codec candidates share the same codegen
frontier: the target performs an in-place ROR byte ptr [BP-1],3, while the
maintained natural C++ candidates either expand shift/OR expressions or call a
byte-rotate runtime helper.

v760 checks a compiler mechanism that had not been closed by the older source
spelling probes: Turbo C++ 4.02's own rotate declarations and intrinsics.

Pinned STDLIB.H distinguishes three surfaces:

- _crotr(unsigned char, int) is a runtime-library function;
- _rotr(unsigned, int) is a runtime-library function under the pinned flags;
- __rotr__(unsigned, int) is the actual compiler intrinsic.

Two isolated TC4.02 -S rounds produce the same structural observations:

- _crotr(feedback, 3) lowers to a FAR call to __crotr, including when feedback
  is a byte local;
- _rotr(feedback, 3) lowers to a FAR call to __rotr;
- direct __rotr__(feedback, 3) zero-extends the byte and emits ROR AX,3, a
  16-bit rotate, not the target byte-memory operation;
- no tested surface emits ROR byte ptr [BP-1],3;
- in a control source that includes mem.h, the repository's known pragma
  intrinsic memcpy form is accepted, while pragma intrinsic _crotr and pragma
  intrinsic _rotr each produce an Ill-formed pragma warning and leave the RTL
  calls unchanged.

Receipt:
.analysis/reconstruction/receipt-archive/v760-tc4-score-rotate-intrinsics-receipt.json

Receipt SHA-256:
e80a367d760da8dffd0a7118490ddcaf7da31d371c2a2fee4e8510e52b2bb9ec

This is negative compiler-mechanism evidence, not exactness evidence. It closes
the rotate-intrinsic route for OP scoredat_decode / scoredat_encode and the
corresponding MAINE codec blockers. Further progress on these functions now
requires a materially different source/provenance mechanism, not another
TC4.02 rotate spelling.
