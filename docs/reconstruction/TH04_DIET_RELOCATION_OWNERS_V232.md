# OP/MAINE target-restored relocation owner order (v232)

## Scope

`scripts/probes/analyze_diet_relocation_owners.py` compares the ordered MZ
relocation tables of the v226 cold ReC98-overlay candidate and the v228
DIET-restored target view. Each relocation site is projected onto exactly one
contribution in the **candidate** TLINK MAP. All 804 OP and 559 MAINE sites
are unique, their multisets agree, and every site has exactly one MAP owner.
The first ordered mismatch is index 146 in OP and 48 in MAINE.

The private v232 reports are
`.analysis/reconstruction/diet-replay/v232-{op,maine}-reloc-owners.json`,
SHA-256
`10d882deb939e571616d73ffb96a9afc574e1d54260d2358c75b2ac05c5a42cb`
and `fdd84c199e3e116dbfd588dd25219ade36ed3cb3d1403b4df5f2562f7a198ddf`.
The target itself remains `candidate-local-attested`. DIET `-RA` exactly
inverts our own candidate packs, but the historical target pre-DIET MZ and OMF
objects are unobserved. The target-restored order is a diagnostic view.

## Candidate MAP projection

| Artifact | Candidate owner blocks | Target-restored owner blocks | Candidate module whose sites are interleaved |
| --- | ---: | ---: | --- |
| OP | 33 | 37 | `th04_op.asm`: candidate 49 contiguous sites; target-restored 7 + 3 + 4 + 35 |
| MAINE | 30 | 33 | `th04_maine_master.asm`: candidate 14 contiguous sites; target-restored 7 + 3 + 4 |
| MAINE | 30 | 33 | `th04_maine.asm`: candidate 175 contiguous sites; target-restored 139 + 36 |

In both artifacts, the target-restored sequence leaves the current master ASM
group after its first seven relocations, includes `pi_put` and `pi_load`
contributions, and later returns to the master group. This shared placement
pattern is evidence for investigating physical object/segment grouping. It
does not prove the names or number of original source files.

Within candidate-MAP modules, OP has three changed projections:
`th04_op.asm` (49 sites), `th04/hi_view.cpp` (61), and
`th04/bgimage.cpp` (8). MAINE also has three:
`th04_maine_master.asm` (14), `th04_maine.asm` (175), and
`th04/bgimage.cpp` (8). The eight `bgimage.cpp` sites are in
**exact reverse order** in the candidate and target-restored views for both
artifacts. The other changed module-local sequences are more complex. The
[v233 OMF and TASM control](TH04_BGIMAGE_FIXUP_PRODUCER_V233.md) ties the
candidate eight-site order to its FIXUPP record and tests a symbolic ascending
producer without assigning historical source form.

The report records each owner block's table index and first/last MZ
program-image relocation site. For example, OP's candidate master block
starts at index 139 with 49 sites; the target-restored view starts at index
139 with seven sites, then resumes at indices 151, 158, and 271. MAINE's
first master block starts at index 41 with 14 candidate sites; its
target-restored pieces start at 41, 54, and 58.

## Reconstruction consequence

The packed mismatch cannot be repaired by the seven/five payload bytes alone.
The [v231 partition](TH04_DIET145F_MZ_PARTITION_V231.md) also requires the
ordered relocation and header/tail surfaces for the target-restored preimage.
For OP/MAINE, inspect the ASM master and `bgimage.cpp` OMF FIXUPP ownership,
segment contributions, and natural link input order before changing the
source layout. A final table permutation or target-derived hybrid would only
manufacture packed equality; neither is a reconstruction solution.
