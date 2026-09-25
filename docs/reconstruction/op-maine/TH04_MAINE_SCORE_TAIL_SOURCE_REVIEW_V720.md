# MAINE SCORE tail boundary and source-admissibility review (v720-v724)

The SCORE tail contains three authored functions:

- regist_menu at payload 0xC814, reviewed body size 0x39C;
- the SCORE EGC-start helper at 0xCBB0, size 0x43;
- the rectangle-copy helper at 0xCBF3, size 0x86.

## Physical boundaries

Fresh target review corrects regist_menu's old Ghidra auto-function. Ghidra
merges five ranges across a 0xC392 span, but the expanded TASM PROC/ENDP closes
the real function at SCORE_TEXT local 0x7FE, yielding exactly 0x39C bytes.
The following 0x43 and 0x86 helpers are contiguous and independently closed by
both TASM and Ghidra. The complete pinned scoreall.cpp producer is 0xB30 bytes
at payload 0xC149.

## Why v720/v722 do not give three exact functions

Focused v720 can reproduce all three function byte ranges and the complete
producer raw-zero. An in-memory 59-slice aggregate (v721) and a checked-in
59-slice replay (v722) also compare raw-zero.

That byte equality is not sufficient for authored-source credit for two
functions. The pinned decomp.hpp explicitly documents both mechanisms as
compiler-optimization circumvention used to recreate binary layout:

- regist_menu calls optimization_barrier() solely to prevent TC86 from folding
  an otherwise-redundant jump. Without it, bounded v483 ordinary-source probes
  remain 920/924 bytes exact, with one CMP-vs-MOV/OR zero-test frontier.
- the EGC-start helper uses keep_0(0) solely to prevent TC86 from reducing
  MOV AX,0 to XOR AX,AX. The ordinary form remains 66/67 bytes.

Therefore v721/v722 are retained as diagnostic raw-equality receipts, not as
the current acceptance gate for these two functions. Their physical boundaries
remain reviewed and their maintained semantic source remains useful, but they
are not counted exact.

## Natural rectangle-copy acceptance

The 0x86-byte rectangle helper does not need either compiler-shape helper.
Historical v484 had already isolated it as natural C++. v723 repeats that claim
against the current pinned v489 producer and is stricter: only
src/maine/score/score_rect_copy.inl is substituted from maintained source.
regist_menu and EGC-start remain unchanged pinned scaffold and receive no credit.

Two v723 cold rounds reproduce the complete 134-byte rectangle body, the
0xB30 SCORE_TEXT producer, full linked program image, and all 559 ordered
relocations.

Focused receipt:
.analysis/reconstruction/receipt-archive/v723-maine-score-rect-natural-focused-receipt.json

Focused receipt SHA-256:
c0bfabec13b4009cf77409427f69f13d4ad34c6905c4e07fa2c62cdb72a06515

After the acceptance ledger was reduced to the strict-source set, v724 replayed
the checked-in ledger and passed 57/57 MAINE slices raw-zero.

Canonical receipt:
.analysis/reconstruction/receipt-archive/v724-maine-score-rect-canonical-receipt.json

Canonical receipt SHA-256:
6c5da132bf829cdb3207d987066381a3c82afb8b3fbdb06588c7a9f56972c995
