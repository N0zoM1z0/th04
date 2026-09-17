# TH04 END/MAI scroll and MPN reconstruction (v195)

## Scope

This packet reviews one structurally connected scroll/MPN cohort in the locally
attested TH04 `MAIN.EXE` target:

- `MAI_TEXT` `sub_CCD6`, load `0xCCD6..0xCD35`, size `0x60`;
- `END_TEXT` `sub_B835`, load `0xB835..0xB8FB`, size `0xC7`;
- `END_TEXT` `MPN_LOAD`, load `0xB8FC..0xB970`, size `0x75`.

The private target remains only `candidate-local-attested`; no target bytes are
checked in, patched, relocated, or used as source data.

The two END_TEXT functions exactly fill the physical residual between the
already exact v99 ending owner and v100 map owner. Before this packet, the cold
MAP attributed the complete `0x13C` residual at `0AAF:0D45..0E80` to the
monolithic `th04_main.asm` object. v195 splits only the `0x75` MPN uploader out
of that residual; `sub_B835` remains in the monolithic object with zero source
or exactness credit.

## Target-first boundaries

### `MPN_LOAD`

`MPN_LOAD` is a contiguous near Pascal function at END_TEXT map
`0AAF:0E0C`, load `0xB8FC..0xB970`, file `0xD0FC..0xD170`, size
`0x75 / 117`, target SHA-256
`746d80268b65200ceee3667bee747c3c235a4baa5813bf8197761021453bf976`.
Fresh Ghidra reports one contiguous 117-byte body through the target `RET 4`.
The exact `map_load()` owner begins immediately at load `0xB971`.

The function owns four ordered MZ relocation entries, corresponding to the
palette/file loader, the two FAR `sub_3680` calls, and `mpn_free()`. No trailing
compiler table or alignment byte is included in its logical or physical owner.

### `sub_B835`

`sub_B835` is now reviewed as the complete near function at END_TEXT load
`0xB835..0xB8FB`, file `0xD035..0xD0FB`, size `0xC7 / 199`, target SHA-256
`80f17b65eee2a5e9ce7338e727e4a00dcef4f641a8cdddfae03e08e2925922d8`.
Fresh Ghidra constructs the complete body and reports one caller, the MAI_TEXT
scroll driver at `0x1CCD6`. The body contains tile-ring bookkeeping, a 24-word
`REP MOVSW` path with DS/ES exchange, condition-flag shuffling, and EGC redraw
calls. One ordered MZ relocation belongs to the FAR `egc_off` call.

The boundary is reviewed, but its source form and origin remain deliberately
unresolved. It receives no natural-source exactness and no original-ASM
attestation credit in v195.

A later bounded compiler control tests the copy mechanism without assigning
origin to the whole function. Run
`python3 scripts/probes/probe_th04_end_scroll_copy.py --output-dir .analysis/reconstruction/probes/v257-end-scroll-copy`.
Pinned TC4J 4.02 compiles a small C++ `__memcpy__` from a far map-segment
pointer to a near tile-ring pointer with length 48. Its valid 33-byte OMF CODE
contains one 24-word `REP MOVSW` and DS/ES exchange, as does the target at
`END_TEXT 0AAF:0DDB` / load `0xB8CB`. The generated register and segment setup
order is different, so this is a compiler-observed plausible primitive, not
an exact body or a recovered source file. Private receipt SHA-256 is
`e03131c290771d6371f3998e0a440d6d49126b67a29c4a9bdc708a97c804aa37`.

### `sub_CCD6`

`sub_CCD6` is now reviewed as the complete near MAI_TEXT function at load
`0xCCD6..0xCD35`, file `0xE4D6..0xE535`, size `0x60 / 96`, target SHA-256
`0115bd70a1f2a3a1e637dfd111e6125e355934e3fdae7d654fa2f0f3171ccb9e`.
Fresh Ghidra reports `gameplay_loop()` as its sole caller and `sub_B835` as its
game-local callee, together with the FAR scroll call. Its only ordered MZ
relocation is the FAR `graph_scrollup()` segment word. `PLAYFLD_TEXT` starts
immediately at load `0xCD36`.

This boundary is also reviewed without assigning a source/origin verdict.

## Natural `MPN_LOAD` source

Maintained source is `src/main/formats/mpn_upload.cpp`, SHA-256
`5f252e25ce3cd491c82d3bf20ed1bd280de689bf1f23283c9f3dd51f0f165603`.
It is ordinary C++ under the historical TC4J profile. It contains no inline
assembly, codestring, target byte array, synthetic padding, or fake return.

The target-observed ABI is intentionally preserved as
`extern "C" int pascal near mpn_load(const char *fn)`. Turbo C++ warns that the
function reaches the end without returning a value. This warning is retained:
TH02/TH04 declarations historically use an `int` return type, while the TH04
target returns with `RET 4` without assigning AX. Adding an invented return
value would change target code generation rather than improve it.

The first truthful compiler probe produced 120 bytes and localized three ABI/
source-shape mistakes. After correcting function distance, the FAR Pascal
renderer ABI, and local declaration order, a bounded probe emitted the complete
117-byte target instruction skeleton. The final `extern "C"` form also exports
the target `MPN_LOAD` public. Before linking, masking only the four unresolved
FAR-call operands leaves zero fixed-byte differences against the target.

## OMF/link ownership

Splitting the C++ uploader requires the game-owned FAR renderer `sub_3680`,
which remains physically in `th04_main.asm`, to become externally linkable.
TASM `/mx` preserves the first spelling of a case-insensitive public. A first
focused attempt therefore failed at TLINK when the monolithic object exported
lowercase `sub_3680` while Pascal C++ requested uppercase `SUB_3680`.

The replay transform now publishes the existing symbol as `SUB_3680` before its
unchanged PROC. This is a symbol-metadata ownership change, not a replacement
body. Focused and aggregate replay keep every pre-existing selected owner exact,
including the monolithic bytes surrounding that helper.

The successful linked END_TEXT layout is:

- `th04/endmain.cpp`: `0AAF:0CC9`, size `0x7C`;
- remaining `th04_main.asm`: `0AAF:0D45`, size `0xC7` (`sub_B835` only);
- `th04/mpnend.cpp`: `0AAF:0E0C`, size `0x75` (`MPN_LOAD`);
- `th04/mapend.cpp`: `0AAF:0E81`, size `0x65`.

## Exact replay

Focused replay:

- run: `gptweb-v195-mpn-focused-candidate-003`;
- selected dependency closure: 129 owners;
- failures: `[]`;
- receipt SHA-256:
  `33d0e628621049b03e0217d0bf77dd004aae7ced631f949f8c7588029ba78a86`;
- A/B `mpnend.obj` SHA-256:
  `e6a414002536e265b1f3cd52b51d590ca8497e32aa7d915807e112f160312a9f`.

Candidate aggregate before promotion:

- run: `gptweb-v195-mpn-aggregate-candidate-001`;
- 233 candidate-state default owners, twice;
- failures: `[]`;
- receipt SHA-256:
  `7d074441962dc66eb73b4e7adc5debc6f4049615ecab99046826f5dca520b3c4`.

Post-promotion aggregate:

- run: `gptweb-v195-mpn-aggregate-final-001`;
- 233 tracked default exact owners, twice;
- failures: `[]`;
- receipt SHA-256:
  `e8cf7c951e3a0bd54172a3ce756e2c537860931892ad483610e017faa0f386b9`;
- tracked manifest SHA-256:
  `281dfc31b0d59a60d4ae5da835b80c729c5143538777a8f8ee1fe7c9507f3000`;
- A/B MAP SHA-256:
  `0e3b868a7f0eedd4f60eef1463be7915fe3e1e2bac54980f3b307f68a7120f7d`;
- A/B `mpnend.obj` SHA-256:
  `e6a414002536e265b1f3cd52b51d590ca8497e32aa7d915807e112f160312a9f`;
- candidate overlay `MAIN.EXE` SHA-256:
  `27ac9d000382410e0dcee7358a978fb52aad940232450d44248410825f494422`.

The overlay executable is an exactness Oracle for declared owners, not a
standalone TH04 product build and not a whole-image exact claim.

## Function review

`scripts/review_th04_main_functions.py` validates `MPN_LOAD` through its strict
automatic path: the target Ghidra body is contiguous, starts at the matching
TLINK public, and lies wholly inside the exact natural-C++ owner. The trial
report SHA-256 is
`c9d463ce28f7c5a9b1368bf0a7fe2c3c50d4a841ee955056c2785caa8fb48b7c`.

The reviewer trial also rewrites historical rows into address order, producing a
large textual diff unrelated to v195. Only the newly validated `0x1B8FC` row was
therefore extracted and inserted into the existing ledger; all pre-existing
479 authored-function rows were preserved byte-for-byte in their existing
relative order.

## Scroll-source negative evidence

Three bounded TC4J driver hypotheses were tested under the production profile.
An ordinary local `delta` emits 109 bytes versus the target 96 and reloads the
subpixel value into wider temporaries. An explicit `_AL/_AX` form reaches 105
bytes but `scroll_line -= _AX` causes Borland to reload `scroll_line` into AX,
collapsing the intended subtraction into `SUB AX,AX`. A register unsigned
`delta` form emits 110 bytes and keeps the value in DX rather than preserving
the target AX lifetime.

These are durable mechanism negatives, not proof of original assembly. No
source-spelling matrix is continued without a genuinely new compiler/source
hypothesis.

Independent TH05 target-derived bodies preserve the same broad scroll-helper
architecture: BP/local-byte state, tile-ring `REP MOVSW` with DS/ES swap, flag
shuffle, EGC redraw flow, and a homologous driver. TH05 also has stage-specific
conditions and different STD map indexing. This corroborates lineage but does
not establish TH04 source form or exactness.

## Other TH04 artifacts

The attested unpacked payloads were also screened so MAIN ownership would not be
silently generalized:

- OP: 69,028 bytes, SHA-256
  `13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`;
- MAINE: 62,414 bytes, SHA-256
  `7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c`;
- ZUN: 13,422 bytes, SHA-256
  `baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.

Longest contiguous exact matches against the MAIN bodies are only 6/6/4 bytes
for `sub_B835`, 8/8/5 for `MPN_LOAD`, and 5/5/3 for `sub_CCD6` across
OP/MAINE/ZUN respectively. This is bounded negative routing evidence only. The
three artifacts keep their independent authored queues and receive no MAIN
source or exactness credit.

## Accounting and continuation

Live MAIN accounting after v195 is **75,326 / 80,985 exact reviewed C/C++
bytes (93.012286%)** and **457 / 480 exact reviewed C/C++ functions
(95.208333%)**. Generated progress separately reports 75,326 exact bytes and
91.83% of its conservative confirmed authored-byte denominator. Original-style
ASM remains a separate **29 units / 4,370 bytes** track.

`sub_B835` and `sub_CCD6` are boundary-reviewed but remain source/origin
unknown. The next structural packet should continue immediately leftward in
MAI_TEXT with `midboss2_render()` at load `0xCC3A`, size `0x9C`, and explicitly
reconcile its owner/seam with the now-reviewed scroll driver at `0xCCD6` before
choosing natural C++ versus original-style assembly.
