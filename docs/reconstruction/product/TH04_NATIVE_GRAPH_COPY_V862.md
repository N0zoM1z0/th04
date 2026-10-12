# TH04 native graphics page copy

2026-09-27 product-build investigation. `src/shared/hardware/graph_copy_page.cpp`
owns the far Pascal `GRAPH_COPY_PAGE(to_page)` entry. It allocates one plane's
temporary word buffer, turns GRCG off, and copies the blue, red, green, and
extra graphics planes from the opposite page to `to_page & 1`. For each
plane, port `0xA6` selects the source page before reading and the destination
page before writing. Success leaves the destination page selected and returns
1; an allocation failure changes neither GRCG mode nor access page and
returns 0. `graph_VramWords` supplies the live plane length.

The bounded historical routine uses `SMEM_WGET`/`SMEM_RELEASE`, while the v862
TH04 product candidate borrowed a 32,000-byte block at the current 400-line
setting through `HMEM_ALLOCBYTE`/`HMEM_FREE`. Those two heap entries were still
unresolved in that no-archive build. The different buffer pool can change
allocation success under memory pressure; no MAINE runtime page-copy
checkpoint exists yet. The four-plane copy and page-selection behavior are
the supported semantic claim, not target bytes or timing.

TC4J 4.02J treats the loop variable from `for(unsigned i = ...)` as in scope
throughout the function. Repeating that declaration in the second copy loop
failed compilation (`compile-054.log` SHA-256
`f77acebfe6005226d7169b8ccae74c7c8b9b5d602d655704a62323ba33b8715b`).
Declaring `i` once before both loops compiled. This is a portable lesson for
TH05 code written for the same compiler.

Two cold no-archive MAINE builds compile 118 TH04 units (76 C++, 42 ASM),
leave 22 unresolved names and zero warnings. Their link-relevant and
timestamp-normalized OMF records agree; BGIMAGE alone has known raw timestamp
drift. Receipt SHA-256 values are
`c8a6165649f8f61400ee9d8c745ad631a76c892607a7df253477631017d5d4c4`
and `6eb1d284fbf8ae917ca0cd51f02ace8d10c6fcb7d68df5431f0c447acdc0241c`.
The explicit manifest SHA-256 is
`70cbceac771bc0f4a8105e43f9da0b446eb7b50cef6171c4529e169fa4bc8e89`.

The historical-library calibration TLINK link exits 0 (receipt
`b217c84e7268f81a7e7699fb69912e8539ce0ca8180826d03d721111f0ecd8b5`).
The MZ audit validates 599 relocation sites and two DOS load segments
(receipt `1fad510500cffd2c7ef87ad90cff95b4065da19090414d8986891c4ba047ac34`).
The call ABI audit checks 20 far entries, 85 relocated direct far calls and
one same-CS `push cs; call rel16` (receipt
`0c0cad8c484f15e60e8f35ff37136dcd6290ae5599d4c723eccf01f027c9ebc7`).
The calibration MAP locates `GRAPH_COPY_PAGE` at `098C:3105` with `RETF 2`;
this is a calibration address, not the original target address. The MZ still
contains historical-library support and has not reached MAINE in a runtime
scenario.


## DOS SMEM recovery (v1423)

The maintained page-copy owner now uses the shared SMEM cursor rather than
allocating an HMEM block. Attested original OP 0000:156C..15C1 and MAINE
0000:11C2..1217 allocate the wrapped WORD byte count, disable GRCG only after
success, select the opposite/access pages for B/R/G/I, then release the
workspace. Failure returns AX=0 without port writes; success returns AX=1
and leaves the destination page selected.

The original helper at OP 0000:1556..156B / MAINE 0000:11AC..11C1 recomputes
CX as the wrapped DI shifted right after each REP MOVSW. The typed owner
keeps that rule: after the first read, the count is `words & 0x7FFF`. Zero
words still perform allocation, eight page selections and release. The
callee executes real relocated instructions in the component comparison;
its explicit two-bank RAM model uses DF=0 and does not represent physical
GDC timing. Complete memory results are retained as deduplicated gzip blobs.

All 160 original/compiled OP and MAINE controls agree at load segments 1000
and 3333: full retained memory, scratch results, page/GRCG port order, return
AX and cursor release. The actual v1415 compiled predecessor rejects eight
zero-length or exactly fitting workspace controls; its eight ordinary-copy
controls still agree on pixels, ports and AX. No game campaign was run.

The first 1,426-input cold donor is 466389e9. The final profile e60c079f changes
only the ABI assembly; unchanged objects are checked before reuse and all
three products are reassembled/relinked and audited. Evidence, both source
profiles, original/current memory blobs, failed products and the real old
programs are indexed in the shared SMEM note below. Historical authored exact
acceptance remains 661/663.
