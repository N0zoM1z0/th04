# OP/MAINE packed input partition (v231)

## Controlled question

The [v228 round trip](TH04_DIET145F_ROUNDTRIP_V228.md) identifies DIET 1.45f
and a target-restored MZ view that repacks raw equal to each packed target.
`scripts/probes/partition_diet_mz_residual.py` compares that view with the
v214 cold ReC98-overlay candidate MZ. It checks that `-RA` restores our own
candidate packed files **byte-for-byte** to their prepack MZs, then builds
eight private diagnostic hybrids. This supports DIET invertibility for these
candidate inputs; it still does not prove that a restored target view is the
historical TLINK output.

The entire candidate-versus-restored-target MZ difference is covered by three
surfaces:

| Surface | OP.EXE | MAINE.EXE |
| --- | ---: | ---: |
| `P`: program-image bytes | 7 differing bytes | 5 differing bytes |
| `R`: ordered relocation table | 657 differing table bytes; first entry mismatch 146 | 769 differing table bytes; first entry mismatch 48 |
| `T`: coupled MZ file length, minimum allocation, trailing zero bytes | 3,228 zero bytes; minimum allocation 612→410 paragraphs | 3,220 zero bytes; minimum allocation 817→615 paragraphs |

The candidate and restored target have the same header paragraph count,
relocation count, and relocation-site multiset. All other header bytes match.
`T` is kept coupled because applying the smaller minimum allocation alone
makes the candidate MZ invalid: its initial `SS:SP` would exceed the minimum
allocated memory. The seven OP load-module offsets are `0x2D59`, `0x34AF`,
`0xBFB7`, `0xBFB9`, `0xDE8B`, `0xDE8C`, `0xFB97`; the five MAINE offsets are
`0x0CBD`, `0x2D11`, `0xD1D3`, `0xD1D4`, `0xE933`. These are physical MZ
program-image offsets, not standalone source function identities.

## Eight-way pack result

Each diagnostic MZ is valid and packed through the same pinned DIET 1.45f
and DOSBox-X profile. `P`, `R`, and `T` denote replacing only the named
candidate surface with bytes from the **target-restored** view. Empty means
the untouched candidate.

| Surfaces | OP packed bytes | MAINE packed bytes | Raw target equality |
| --- | ---: | ---: | --- |
| none | 42,251 | 37,985 | neither |
| P | 42,257 | 37,991 | neither |
| R | 42,239 | 37,932 | neither |
| PR | 42,243 | 37,936 | neither |
| T | 42,298 | 38,084 | neither |
| PT | 42,304 | 38,088 | neither |
| RT | 42,284 | 38,029 | neither |
| PRT | **42,290** | **38,035** | both raw equal |

The `PRT` hybrid equals the full target-restored MZ byte-for-byte. Only that
combination packed raw equal in this bounded factorial test; lengths are
nonadditive because compression depends on the whole stream. The OP and MAINE
v231 receipt SHA-256 values are
`4ab66c108ad73a4c5d2cf8cb48650c183021c5486f2a6bc23c558cedad5fe394`
and `1aaa9174653ed0dd084d57d874e1210e6998f59a3f3c862e98dc9ffa4e16df38`.
The private receipts and all hybrid inputs are under
`.analysis/reconstruction/diet-replay/v231-{op,maine}-mz-partition/`.
Superseded v229/v230 scratch copies were removed after the v231 inverse
controls and receipts passed.

This is a **diagnostic localization**. The hybrids copy target-derived bytes
and are forbidden as product source or exact-match evidence. Next resolve
the seven/five natural payload bytes and recover the compiler/linker cause of
relocation order and `T` topology. The original pre-DIET target MZ remains
unobserved; alternate preimages of the packed target are not excluded.
