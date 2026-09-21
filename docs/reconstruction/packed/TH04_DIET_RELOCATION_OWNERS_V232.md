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
[v233 OMF and TASM control](../op-maine/TH04_BGIMAGE_FIXUP_PRODUCER_V233.md) ties the
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

## v425 MAINE master-object order follow-up

v232 measured the old monolithic candidate. After v400/v401 restored real
master CODE/DATA object boundaries, v425 revisits MAINE without editing source
bodies or relocation-table bytes. The only change is TLINK input order among
already-separated objects: `mainem.obj`, then the two master CODE tails, then
the historical `VS.OBJ` and maintained DATA tail.

Two copied v401 source trees build identically. Payload size stays `0xF3CE`; the
only payload difference remains the shared two-byte `snd_load` handle copy, and
the 559 relocation-site multiset stays target-equal. Relative to the v231 **restored-candidate inverse control** (not the DIET-restored target), the ordered difference collapses from 13 indices
`42..54` to exactly two indices, `48..49`: candidate `0x2F59, 0x2FE7` versus candidate-control `0x2FE7, 0x2F59`. 557/559 entries are now equal at the same table
index. Both A/B candidates have SHA-256
`9b14cad4fc3bbd079890cd15d64de03d3c7159fb2b4ae38dab111bdfc8a0df60`.

Private receipt SHA-256:
`8b0154c2c2a28e7877b2b1a94fe4831664ac29ec700ae929fde3c16c15fc6f6e`.

This is physical/link-topology evidence, not an ordered-relocation exactness
claim. The v231 reference SHA is `candidate_inverse_control.restored_candidate_sha256`; it is not the target-restored MZ. The historical pre-DIET TLINK table remains unobserved. The final two-entry swap must therefore
not be repaired by hand or promoted into a source requirement merely to make a
restored diagnostic view equal.

## v426 historical MASTER.LIB BGM members

v425 reduces MAINE's ordered difference against the v231 restored-candidate inverse control to a single two-entry swap. v426 asks whether independent historical support-library
evidence favors that swap or the candidate's natural read-before-timer order.

The locally pinned historical `masters.lib` is listed and extracted with the
pinned Borland TLIB 4.00. It stores the relevant routines as **separate OMF
members** and lists them in this order:

1. `b_r_sdat` — exports `BGM_READ_SDATA`; extracted object size 626 bytes,
   SHA-256 `4840e85e4dadc80791a2214ee02cde1edc8c60081f690b11b8aa2fafe98cbf58`;
   one `_TEXT` LEDATA of `0x130` bytes with its segment-word fixup at local
   `+0xB7`.
2. `b_timer` — exports `_BGM_TIMER_INIT` / `_BGM_TIMER_FINISH`; extracted
   object size 407 bytes, SHA-256
   `651bfe73ac4ef8fc5261513cde4e6ae82cc1cb30fdd166f8403663f1076c0c68`;
   one `_TEXT` LEDATA of `0x6A` bytes with its segment-word fixup at local
   `+0x13`.

This is independent historical library-object evidence for a read-before-timer
producer organization. It does **not** prove the original TH04 executable's
TLINK extraction order, but it provides no basis for reversing these two
routines merely to match DIET `-RA`'s final two restored relocation entries.
That restored order remains a diagnostic application/restoration view, not an
acceptance oracle for historical TLINK order.

Private receipt SHA-256:
`5192771073c57be2bbf9b80b0dc2ae4fe069fe6969c4bc7bc05152c8b71e60c6`.

## v427 OP_MUSIC_TEXT physical-object split

The post-v401/v402 OP relocation discrepancy has a structural cut that was not
visible in v232's old monolithic candidate. In the fused `th04_op.asm` object,
relocation indices 139..144 are all in `_TEXT`, while indices 145..179 are all
in the separate `OP_MUSIC_TEXT` segment. The v231 restored-candidate inverse control places the master mid/tail/data relocation blocks between those two segment groups.

v427 therefore changes **physical OMF ownership only**. The existing
`OP_MUSIC_TEXT` source span is removed from `th04_op.asm` and assembled as its
own TASM object with only the extern/type interface required by that source.
Master CODE objects are linked before historical `VS.OBJ` / DATA ownership, and
the new music object follows them. No function body, payload constant, or MZ
relocation-table byte is edited.

Two copied v402 trees build identically. The candidate payload stays `0x10DA4`
and still differs only at shared `snd_load` load `0xDE8B..0xDE8C`; all 804
relocation sites remain target-equal as a multiset. The baseline v402 candidate
differs from the v231 restored-candidate inverse control at indices `145..187` (43 entries). The v427 candidate MZ relocation table is **804/804 ordered equal** to that candidate-control table. Candidate SHA-256 is
`78468a2ae389ba9c97fb7b391355e4eda2cb750f84f3cc4abf3e34802bceafbd`;
MAP SHA-256 is
`cd2e0a35b1d1262dca398db0302ab68243179cf18edfac2e1ec0810acf2ef334`.

A subtle OMF detail is also pinned by the replay: the separate music object must
reproduce the fused file's minimal extern environment. Including the broader
`master.inc` changes TASM FIXUPP threading for four segment relocations and
leaves a 22-index candidate-control discrepancy even though the payload stays
unchanged. This is module-interface metadata, not source-code behavior.

Private receipt SHA-256:
`4dcb4c44ca64f4b32156e8ee9e608b740963802cab39ab7a18c34a6ffaf88808`.

This still does **not** prove the historical pre-DIET TLINK table or packed-file
exactness. `compare_diet_payloads.py` separately reports that DIET decompressor
application order differs from candidate MZ order beginning around this same
region. The restored MZ table and the stub application order remain distinct
diagnostic surfaces.

## v428 terminology correction

The original v425/v427 probe flags and notes called their comparison input
`target-restored`. That label was wrong. The referenced files are the v231
`candidate_inverse_control` outputs: DIET `-RA` applied to the **candidate**
packed files, with SHA-256 `7e6b7886...` for MAINE and `cb9b1c6c...` for OP.
The actual v228 DIET-restored target files have different SHA-256 values
(`670de6ba...` MAINE and `8fc3b67f...` OP).

Therefore v425/v427 establish candidate physical/link topology only. They do
not establish the target's historical pre-DIET relocation-table order. The
probe scripts retain `--target-restored` only as a deprecated CLI alias for
old command lines; new use should pass `--reference-candidate`.

## v429 current candidates versus the real v228 target restore

v425 and v427 intentionally established only candidate-to-candidate physical
link topology. v429 now rebases those current candidates onto the **actual v228
target-derived DIET restore**, without changing any source body, object, or
relocation-table byte. The checked-in
`scripts/probes/probe_th04_current_target_relocation_topology.py` verifies the
current candidate/MAP identities, the v228 restored identities, relocation-site
multisets, ordered indices, and candidate-MAP owner projection.

The result is deliberately different from the v425/v427 candidate-control
numbers:

| Artifact | Current candidate | v228 target-restored | Same-index relocations | Ordered differences |
| --- | --- | --- | ---: | ---: |
| OP | `78468a2a...` | `40a981a6...` | 581 / 804 | **223** (`146..465`) |
| MAINE | `9b14cad4...` | `6b454718...` | 260 / 559 | **299** (`48..346`) |

Both relocation-site **multisets remain equal**. The new differences are
therefore ordering/topology diagnostics, not missing relocation sites. Candidate
MAP projection localizes every module-local order change to a small set:

- OP: `th04/bgimage.cpp` (8, exact reverse), `th04/hi_view.cpp` (61),
  `th04_op_master_data_tail.asm` (4, exact reverse), and
  `th04_op_music_master.asm` (35).
- MAINE: `th04/bgimage.cpp` (8, exact reverse), `th04_maine.asm` (175), and
  `th04_maine_master_data_tail.asm` (4, exact reverse).

The target-restored owner blocks expose especially useful physical cuts. OP's
61 `hi_view.cpp` relocation sites appear as **23 + 38** target-restored blocks
with the two `score_e.cpp` relocations between them. MAINE's 175
`th04_maine.asm` relocations appear as **139 `MAINE_01_TEXT` + 36
`SCORE_TEXT`**, with `hi_end.cpp` and `score_e.cpp` between those blocks. These
are concrete object/segment hypotheses for the next non-patching link-topology
experiments.

The current candidates also retain the already-known MZ tail/header difference:
OP is 3,228 bytes shorter and MAINE 3,220 bytes shorter than the v228 restored
views, with the corresponding page-count/minalloc differences. v429 does not
alter or claim ownership of that surface.

Private receipt SHA-256:
`80f22afe0711fa905acc5d761f5c0731953cd16b4867db158ad78a4c382ea92a`.

The acceptance limit remains unchanged: DIET `-RA` starts from the target and
re-packs raw exact, but its restored MZ is not proven to be the historical
pre-DIET TLINK output. v429 therefore supplies a **target-derived routing
baseline**, not a relocation-order exactness oracle. Do not patch or permute the
MZ table to satisfy it.

## v441 active TLINK switch surface

The current packed frontier leaves only shared `snd_load` in program bytes and
an unresolved linker/packer `R/T` surface. v441 therefore tests the remaining
active TLINK 6.10 switches that could plausibly affect library extraction or
segment/link organization without editing OMF or MZ bytes.

The pinned linker binary itself exposes these help entries:

- `/e` — ignore extended dictionaries;
- `/E` — process extended dictionaries;
- `/f` — inhibit optimizing far calls to near;
- `/P[=dd]` — pack code segments.

Starting from the retained v429 current OP/MAINE source trees, the replay
changes only the response-file flags and relinks with the same objects and
libraries:

| Variant | OP result | MAINE result |
| --- | --- | --- |
| `/e` instead of `/E` | EXE/MAP/804 relocation order byte-identical | EXE/MAP/559 relocation order byte-identical |
| no `/e` or `/E` | byte-identical | byte-identical |
| `/P` | byte-identical | byte-identical |
| `/f` | 1,221 program bytes differ; relocations 804→1050 | 1,215 program bytes differ; relocations 559→804 |

Thus extended-library dictionaries and code-segment packing are inert for these
already-selected link inputs. Far-call optimization is active, but disabling it
changes a large amount of already target-equal code and changes the relocation
site multiset, so it cannot explain the isolated packed `R/T` frontier.

Private receipt SHA-256:
`19c09864c81e461b362c871b8f398fdedc9451f837bb96c4bbd0cd881f606133`.

This closes these **active TLINK 6.10** switch routes only. A different
independently attested linker version or a real historical OMF boundary remains
a separate hypothesis; v441 is not evidence for the lost original command
line.
