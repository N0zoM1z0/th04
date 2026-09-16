# TH04 Elly CIRCLE physical-producer split (v201)

## Scope

v201 resolves the integration blocker left by v200 for the natural
`elly_backdrop_colorfill()` callback in `MAIN.EXE`. The reviewed target extent is
`CIRCLE_TEXT 0AAF:13DC`, load `0xBECC..0xBED9`, file `0xD6CC..0xD6D9`, size
`0x0E / 14`, SHA-256
`6e1968ec26ed949a9659f9f56232985154f34111f607b4a0b8d51debb145688b`.
The target has no ordered MZ relocation inside this function. Fresh attested
Ghidra still creates no function at analysis address `0x1BECC`; exactness and
function admission therefore come from target raw bytes, TLINK public/layout,
OMF, cold replay, and the strict no-Ghidra review path rather than Ghidra body
construction.

v200 had already recovered maintainable natural source at
`src/main/boss/elly_backdrop.cpp`, SHA-256
`f31dad909a71fc89ecf3db7da549a1cbfc32efda53dc038a7aeb115583570159`.
Standalone TC86 Borland C++ 4.02 emitted exactly 14 CODE bytes with all 12 fixed
bytes equal to target and one normal near-call FIXUPP covering the remaining two
pre-link bytes. v200 deliberately withheld exact credit because the target body
was still physically supplied by monolithic `th04_main.asm`.

## Physical owner split

v201 makes the natural object the actual linked producer. Before the split, the
relevant final CIRCLE contribution was one `th04_main.asm` region at
`0AAF:11A4 +0x468`. It contained the exact point-number/shot prefix, the Elly
body, and five already accepted post-Elly symbolic assembly owners.

With the v201 unit selected, the cold linker MAP is instead:

- `th04_main.asm`: `CIRCLE_TEXT 0AAF:11A4 +0x238`;
- `th04/ellybd.cpp`: `CIRCLE_TEXT 0AAF:13DC +0x0E`;
- `th04\\cpost201.asm`: `CIRCLE_TEXT 0AAF:13EA +0x222`;
- `th04/itemsinv.cpp`: unchanged at `CIRCLE_TEXT 0AAF:160C +0x4B`.

The `0x222` post-Elly suffix is exactly the five maintained physical producers
already accepted in v198-v200:

1. `src/main/hardware/fillm64_56_256_256.asm`;
2. `src/main/tile/bb_mask.asm`;
3. `src/main/boss/yuuka5_backdrop.asm`;
4. `src/main/formats/z_super_put_16x16_mono.asm`;
5. `src/main/formats/bb_txt_put.asm`.

No target-derived executable body is copied into the suffix. The checked-in
`config/replay/th04_circle_post_elly_v201.asm.in` is an integration wrapper that
contains only segment declarations, external symbol declarations, and ordered
`include` directives for those maintained sources. Its SHA-256 is
`9ea9a2a7b66432ddb000e386eb4b0fc4363557c8c675c6981354cc75c5abbfa4`.

The replay driver materializes this wrapper through a fail-closed
`scaffold_extractions` input check. The extraction validates the single existing
maintained fill include line against scaffold SHA-256
`c872e7c1d94d571fc62e6b14e0960b89ef882f46df60a1d8467d117b9e0e549b`
and span SHA-256
`c504dec8fdc41e03aa4b45eaa96ac0e384dc6d548fd7e16fa471fc6757a8b76e`,
then replaces that extracted line with a comment in the wrapper template. It
therefore contributes no extracted target-derived body.

A late build replacement inserts `th04/ellybd.cpp` and `th04/cpost201.asm`
immediately after `th04_main.asm`. A final source transform removes the old
inline Elly body and the five historical include seams from the monolithic
scaffold. The transform accepts only the two observed focused/aggregate
pre-transform scaffold hashes and validates both removed spans by SHA-256.

## Preserving old exact-owner meaning

Five accepted suffix units historically compared contained extents of
`obj/th04/main.obj`. v201 does not silently rewrite that historical replay
meaning. Each unit retains `main.obj` as its normal producer and adds a
trigger-scoped `producer_override_when_unit = "th04-main-elly-backdrop-v200"`.
Only when the Elly split is selected do those units resolve to
`obj/th04/cpost201.obj` / `th04\\cpost201.asm`.

The migrated owners are:

- v200 fillm64 backdrop owner;
- v198 `.BB` tile-mask owner;
- v199 Yuuka backdrop owner;
- v199 monochrome z-super owner;
- v199 BB-text owner.

This makes both historical and split replay fail closed: old units retain their
original producer when v201 is absent, while the v201 dependency closure must
independently re-prove every migrated extent against the new producer.

## Focused replay

The authoritative focused run is
`gptweb-v201-elly-split-focused-candidate-003`:

- selected owners: 138;
- two isolated cold builds;
- `failures=[]`;
- receipt SHA-256
  `b5bc020a8c620a5e0dc2e1628910a8622ece54daa61972f571dd4234ee4ef3bd`;
- A/B MAP SHA-256
  `f7f1cdc7e99ec2560ed5582639e0d6feda56199a500a915077adc3baf02da616`;
- A/B candidate MAIN SHA-256
  `9ca141da410323d87dbaa40379b1670d870b96005ec80c760acf9b20b794d353`.

The natural Elly object is raw-identical in A/B:
`9e64cc59bba8622f59d41aec2c9a48ef4170b19545edb4316b6db0308d472938`.
Its dependency-normalized OMF SHA-256 is
`5401837af5eebc20c2004cd3d9aabe76ba1cbc4518bfb9a7d6fe540be99f0dfe`.
It contains the 14-byte CIRCLE contribution, one public, and one near-call
FIXUPP.

The post-Elly TASM object has dependency-normalized A/B SHA-256
`921fe32bf9efc982ae20800dbcb6d9bcea6ca70db88360c874b0648728a004c7`.
Its raw object identity varies only through Borland dependency metadata. All five
migrated accepted suffix owners are `raw=True`, `map=True`, and `relocs=True`.
The exact shot owner remains in the shortened `main.obj`, and
`items_invalidate()` remains exactly at the following public.

## Candidate and post-promotion aggregate replay

Before ledger promotion, v201 temporarily enabled the Elly unit and ran
`gptweb-v201-elly-split-aggregate-candidate-001`. The 242-owner candidate cohort
passes twice with `failures=[]`; receipt SHA-256 is
`6ae9863abe8c16bfbdd541055edc3f1ee49ce33a3ca4cc403cc1af185cb5e726`.
The tracked manifest was restored to candidate-disabled state after this trial
before promotion.

After promotion, the permanent tracked manifest SHA-256 is
`715f3000edb6a444f5de1f07149cfa7a6d963fa1a97f9d0ff0db2e661cc575e5`.
The required no-unit post-promotion replay
`gptweb-v201-elly-split-aggregate-final-001` again passes all 242 tracked default
owners twice with `failures=[]`; receipt SHA-256 is
`aab1d6eab440cc8b7ba48428f6b65fd6e87b372ee60873d91d08c7a381ce0d83`.

Final A/B aggregate identities are:

- MAP SHA-256: `818e1681f3627b3216efe8c73848542b825b72ad318cc1266bcde25f6b022b85`;
- candidate MAIN SHA-256:
  `6e087e39ee8dbb04ac4215749ff796b6a35590cf2a1129375b1fb03da2ccc414`;
- natural `ellybd.obj` raw SHA-256:
  `9e64cc59bba8622f59d41aec2c9a48ef4170b19545edb4316b6db0308d472938`;
- `ellybd.obj` dependency-normalized SHA-256:
  `5401837af5eebc20c2004cd3d9aabe76ba1cbc4518bfb9a7d6fe540be99f0dfe`;
- split `main.obj` dependency-normalized SHA-256:
  `9d9f9ffff867fba5371d0fbaa0566e3da85963ba874f63bd327cb820719dd327`;
- `cpost201.obj` dependency-normalized SHA-256:
  `921fe32bf9efc982ae20800dbcb6d9bcea6ca70db88360c874b0648728a004c7`.

Elly itself and every affected prior exact owner are raw/MAP/ordered-relocation
exact in both final cold builds.

## Function review

Fresh v201 target-bound Ghidra still reports no function at `0x1BECC`. The
function therefore uses the repository's stricter no-Ghidra exact path rather
than inventing a database entry.

The trial reviewer uses the current candidate aggregate MAP, the pinned target,
and the retained complete v196 function/metadata exports from the same saved
Ghidra project. The project and target were freshly re-attested in v201 through
both the Factory provider and repository-native nonce-bound Ghidra check; the
v201 provider query independently confirms the Elly no-function result.

Review report SHA-256 is
`d5be583a79a4966d3bf2d5c629d30df9940c441ebeaa5c911ff9255ca261c64e`.
The trial ledger SHA-256 is
`81607eb77ea70b3dc8cdc2a737fdf6ae64111cf544fcdac608e48e88f1ded997`.
It adds exactly `th04-main-fn-1becc`, removes none, and proposes 42 unrelated
historical normalization changes. Only the validated Elly row is merged.

The accepted target function is a gap-free seven-instruction, 14-byte extent
through RET. Its next TLINK public is exactly `0x1BEDA`, the separately exact
post-Elly suffix start. No Ghidra boundary is synthesized.

## Other TH04 artifacts

A fresh DIET stub replay was attempted for `th04-op` first but failed closed
before emulation because the active host Python lacks the repository-pinned
`unicorn==1.0.2` dependency. Because the command stopped at that gate, fresh
MAINE/ZUN decompression was not run in v201. This limitation is retained
explicitly rather than treating old payload files as newly produced evidence.

The existing independently attested packed targets, DIET receipts, and retained
payloads were then rebound read-only by SHA-256. All still match their prior
receipts exactly:

- OP packed SHA-256
  `8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f`,
  retained payload 69,028 bytes, SHA-256
  `13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`;
- MAINE packed SHA-256
  `670de6ba907a2edbc1592de810acd92e5b89541d3dc35b70210171166d1713f8`,
  retained payload 62,414 bytes, SHA-256
  `7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c`;
- ZUN packed SHA-256
  `0a12e9a489d3b704a77cf04ca3062ee48f298a9df6d237dc7dad46986e2d116e`,
  retained payload 13,422 bytes, SHA-256
  `baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.

The packed `ZUN.COM` still begins with `MZ`; its extension does not make it a
flat COM. A bounded exact-run scan of the 14-byte MAIN Elly body finds only a
two-byte maximum run in each OP/MAINE/ZUN payload. The compact routing receipt
SHA-256 is
`13fbad2534efc898fc9d720d336ee8af5462d93fd633cb27696fc99235ee4b2e`.
This is negative routing evidence only. Those artifacts retain their independent
94 / 72 / 13 authored reconstruction queues and receive no MAIN source,
boundary, or exactness credit.

## Recovery and negative controls

Two early focused attempts failed for producer-integration reasons and receive
zero codegen/exactness credit:

- focused-001 inserted the new build files too early, before historical
  fail-closed build replacements, and invalidated an old Tup anchor before any
  compiler/linker work began;
- focused-002 reached the real build. Natural Elly C++ compiled, but the split
  exposed missing cross-object declarations: `_grcg_fill_playfield_rows` in the
  wrapper and the moved suffix publics in the shortened monolithic object.
  Adding only those truthful OMF declarations resolved the failure.

A later promotion script also failed closed after using a nonexistent
`units.csv` field name; the CSV writer had truncated the final two rows. Recovery
review established current-session ownership, restored only `config/units.csv`
from the committed HEAD, and reapplied the Elly edit with the real
`replay_command` field. A subsequent evidence-schema validation failure caught
misplaced Oracle/result fields in the new v201 evidence rows; those fields were
corrected against the actual ledger schema before promotion gates passed.

The first function-review invocation omitted `--metadata`, so it performed only
candidate discovery. The proper metadata-bound trial was rerun before function
credit was admitted. These are control-plane recovery observations, not source
or target mismatches.

## Accounting and verification planes

After v201, repository status reports:

- exact reviewed C/C++ bytes: `75,496 / 81,155` (`93.026924%`);
- exact reviewed functions: `459 / 482` (`95.228216%`);
- MAIN reconstruction routing: 503 authored candidates, 459 exact, 24 blocked,
  20 unreviewed, and 65 ASM-attestation observations;
- generated original-style ASM exact ownership remains 36 physical units /
  5,146 bytes.

Generated progress uses its separate conservative denominator and reports
75,496 exact authored bytes at 91.85%.

Repository-native exact physical/function ownership is established for the
natural Elly callback. Standalone TH04 production compile/link closure,
whole-image exactness, runtime-storage identity, runtime scenario validation,
portable-runtime validation, independent pristine-release provenance, and v201
Factory Truth-Kernel acceptance remain unestablished.

## Analysis lifecycle and continuation

`.analysis/` started v201 at 3,883,288,072 bytes and peaked at 4,124,363,145
bytes after failed controls plus focused/candidate/final cold replays. After
confirming no active TCC/TASM/TLINK/replay producer, only explicit v201 failed
runs were removed; focused-003 and candidate aggregate were compacted to
receipt-only state. The complete 242-owner post-promotion aggregate remains the
current cold baseline. Pre-final-CI `.analysis/` is 3,963,107,794 bytes. Full final `python3 scripts/ci.py` returns `CI: PASS`; after its live Ghidra replay, `.analysis/` is **3,963,120,072 bytes**, net growth **79,832,000 bytes** from entry. Older
baselines, private targets, toolchains, Wine/Ghidra state, unrelated ignored
objects, and legacy/unknown analysis content remain untouched.

The next structurally meaningful MAIN candidate should be `_main` at
`DEMO_TEXT 0AAF:001C`, load `0xAB0C..0xAB87`, size `0x7C`. Fresh Ghidra sees one
contiguous FAR body called directly from the MZ entry and twelve callees,
including reviewed gameplay/session lifecycle functions. Six ordered MZ
relocation sites fall inside the extent. The next conversation should reconcile
startup/entry ownership, all twelve calls, the six relocation words, return/exit
behavior, adjacent DEMO ownership, candidate TASM provenance, and natural TC4J
source feasibility before assigning source or origin. `sub_B835` / `sub_CCD6`
remain reviewed difficult scroll helpers with existing compiler negatives and
should not be resumed by blind spelling search without a genuinely new
mechanism.
