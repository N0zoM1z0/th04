# TH04 CIRCLE_TEXT scroll and motion seam v183

## Scope

This packet continues the CIRCLE_TEXT authored-boundary audit at the dense
prefix immediately before the already exact v137 `randring1_next16()` owner.
The current replay scaffold previously represented load `0xB9D6..0xBC6F` as one
`0x29A` residual `cirpre.asm` contribution. That residual is a reconstruction
layout artifact, not evidence that all enclosed functions shared one historical
translation unit.

Target-first review separates two adjacent functions at the right edge of that
residual:

| Function | Map extent | Load extent | File extent | Size | Target SHA-256 | Classification |
| --- | --- | --- | --- | ---: | --- | --- |
| `SCROLL_SUBPIXEL_Y_TO_VRAM_SEG1` | `0AAF:1120..1147` | `0xBC10..0xBC37` | `0xD410..0xD437` | `0x28` | `4a4462bd241d2940c042943e2b1295aa1a139c91824d6ce158f5e6012797b686` | natural C++ exact |
| `PlayfieldMotion::update_seg1()` | `0AAF:1148..1167` | `0xBC38..0xBC57` | `0xD438..0xD457` | `0x20` | `77752519e9fe9e2974c43d2a8e29684bba67c63d2a9e1b326e9e22b49e7270f7` | original-style symbolic ASM exact |

`randring_fill()` remains zero-credit replay residual at load
`0xBC58..0xBC6F`; exact v137 `randring1_next16()` begins at load `0xBC70`.
Neither promoted function contains an MZ relocation site.

The private MAIN target remains only `candidate-local-attested`; this work does
not establish independent pristine-release provenance.

## Recovery and analysis attestation

The conversation began from clean `main` HEAD
`5c94877d88e8a871f5d2ec6224f9e1c4c07bd305`, ahead 4 / behind 0 versus
`origin/main`, with no staged, unstaged, untracked, conflicted, unrelated, or
unknown work. `.analysis/` measured `8,434,894,471` bytes at entry.

The repository preflight, live status, function-boundary validator,
repository-native `python3 scripts/ghidra.py th04-main check`, and pinned
TC4J/TASM/TLINK toolchain attestation all pass. The target remains the
156,258-byte Japanese-local MAIN MZ with SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`,
6,144-byte header, and 1,136 ordered relocations.

Provider discovery exposes ten allowlisted `th04-ghidra` operations and no
`get_metadata` operation. The explicit `check {}` provider call was blocked by
the platform before dispatch and therefore has no attestation result. Subsequent
bounded `function`, `callers`, and `callees` operations succeeded with
`attestation.status = passed-by-registered-bridge`, bound to repository `th04`,
target `target:th04-main`, and the expected target SHA-256. Ghidra observations
remain provisional semantic evidence with zero exactness credit.

## Physical residual seam

The final v183 link divides the old `0x29A` replay residual into the following
ordered CIRCLE_TEXT contributions:

- `th04\cirpre.asm`: `0AAF:0EE6`, size `0x23A`, retaining load
  `0xB9D6..0xBC0F` with zero new reconstruction credit;
- `th04/scroll1.cpp`: `0AAF:1120`, size `0x28`;
- `th04\motion1.asm`: `0AAF:1148`, size `0x20`;
- `th04\cirs183.asm`: `0AAF:1168`, size `0x18`, retaining only
  `randring_fill()` with zero reconstruction credit;
- exact v137 `th04/r1next.cpp`: `0AAF:1180`, size `0x0D`.

The still-unresolved pre-scroll residual is load `0xB9D6..0xBC0F`, size
`0x23A / 570`, SHA-256
`0442cf41e550709cead0b65ae590288af06b6e2b0fbd1b988d023cba591a8e88`.
It contains four target functions plus the one-byte alignment NOP at `0xBAED`:
`TILES_INVALIDATE_AROUND`, `TILES_FILL_INITIAL`, `sub_BAEE`, and
`tiles_redraw_invalidated()`. The only target relocation inside that residual is
at load `0xBC0B`.

The remaining `randring_fill()` residual is load `0xBC58..0xBC6F`, size
`0x18 / 24`, SHA-256
`42c2cd75d930070226e8d40f836ee38666b7a541ba6c472902ad8a594b12ae89`.
It contains the target relocation at load `0xBC5F` and receives no v183 source
or exact-function credit.

## Natural C++ scroll reconstruction

Maintained source is `src/main/scroll/scroll_subpixel_y.cpp`, SHA-256
`af33abbc26558bb0e2ee35d5268d81faf08a842468afe368225deacf799ab24a`.
A one-line compatibility forwarder at `compat/rec98/th01/math/subpixel.hpp`
keeps the product source within the repository's migration boundary instead of
including a TH01 path directly.

A bounded TC4J probe established the source shape before any exact replay. The
natural Pascal-near function reads the by-value subpixel argument through the
historical `_SP`/`_SS`/`peek` idiom, converts to pixels, applies active scroll,
and performs the target negative-first vertical wrap. TC86 Borland C++ 4.02
emits exactly `0x28` CODE bytes. Before linking, every fixed instruction byte
is target-identical; the only four differing bytes are the two unresolved
16-bit external words for `scroll_active` and `scroll_line`.

The final cold object is a valid TC86 OMF module with raw SHA-256
`b30cbdc5aedb621351c0551d289d8ee043918f912db34fad5f6b4b2a339306c6`.
It contains one CODE LEDATA, one public, and one FIXUPP record. Both focused cold
builds emit the identical object.

No inline assembly, copied target bytes, `#pragma codestring`, fake return,
inert padding, ABI lie, or target patch is used.

## Motion origin correction

`PlayfieldMotion::update_seg1()` is not forced into C++. Its target body is the
frameless stack-peek update skeleton that copies `cur` to `prev`, adds
`velocity`, and returns with `RET 2` while AX/DX naturally contain the new
coordinates.

Three independent evidence classes support original-style shared assembly:

1. The complete 32-byte body occurs byte-identically twice in the TH04 MAIN
   load module, at `0xBC38` and `0x13D32`.
2. The same complete 32-byte body also occurs twice in the independent TH05 MAIN
   target, at load `0xBE1A` and `0x1527C`.
3. TH04 load `0x13D32` is already reproduced by accepted exact
   `src/main/math/motion.asm`, which invokes the symbolic `MOTION_UPDATE_DEF 3`
   TASM macro. The v183 source uses the same maintained macro mechanism for
   segment 1 rather than copying machine bytes.

A bounded natural TC4J counter-probe used a minimal same-layout
`PlayfieldMotion` class and a `void pascal near` member. TC4J emitted 34 bytes
with `PUSH BP; MOV BP,SP; PUSH SI` and an SI-based `this` pointer, not the
32-byte target frameless BX stack-peek ABI. Its CODE SHA-256 is
`cdfd139ab007f5d0cfae245c614358f322aaac166c54998b920ba1bb4d12cd71`.
This negative result is evidence against forcing an ordinary C++ member shape;
it is not byte-exactness evidence by itself.

Maintained symbolic source is `src/main/math/motion_seg1.asm`, SHA-256
`bf2493917afe20dabbe693af8654d9e39c1c93aec329724886cbbbc4748879df`.
It invokes `MOTION_UPDATE_DEF 1` inside explicit `CIRCLE_TEXT / main_01`
ownership. The final TASM OMF is valid and deterministic, raw SHA-256
`28b9a22941442050aec19cf37a2b88f4e679e2415189a923110f9670091319ed`,
with one `0x20` CODE LEDATA and no fixups.

The boundary therefore moves from the authored-C++ reconstruction queue to the
separate original-style ASM attestation queue. Its exact bytes do not enter the
authored-C++ function denominator.

## Replay interleaving

v137 had already hash-extracted the old CIRCLE prefix into `cirpre.asm` to place
exact `randring1_next16()` at its target position. v183 preserves that accepted
layout instead of appending new objects after the residual.

The v183 replay performs a second hash-bound transformation of the generated
`cirpre.asm`: the original generated scaffold SHA-256 is
`ee91d7afe09d9929e35e4c763d66575f96b0dbb327bafe0d89506d5797b9b1c8`;
the removed scroll/motion/randring span is 92 source bytes with SHA-256
`76eaa06c2fd5df03d640c95292d043a49384234c8552ac8befcc651ca8e0dcf9`;
the resulting prefix scaffold SHA-256 is
`7d454f0527abdc37520cbd797a9243c1d4bead4b02eaed1bf9ca65dacce8859e`.

Only the unchanged `randring_fill` include is independently extracted from the
pinned original scaffold into the zero-credit suffix object. The extracted line
has SHA-256
`915a73a65550a53893bb3e571a3b8aa712a0153734a6818657ebf6a78916e348`.
This keeps the accepted v137 randring owners at their original linked addresses.

Two exploratory control-plane failures carry no exactness meaning. An early
motion run used `circle.asm`, colliding with an existing `circle.cpp` object
name, so Tup refused to build. A later direct `--unit scroll` attempt failed
because the final physical split requires the separately selected `motion1.asm`
overlay. The reproducible focused closure therefore selects the motion unit,
which depends on the scroll unit and validates both producers together.

## Exact replay receipts

Final focused physical-producer closure:

- run `gptweb-v183-motion-seg1-focused-002`;
- 112-unit dependency closure, two isolated serial cold builds;
- receipt SHA-256
  `4bc9baeb2bd1b1470b12a4859d422b77d30692f1e2bbd9bc09d73a4dc44cc385`;
- scroll raw/MAP/relocations exact, target SHA-256
  `4a4462bd241d2940c042943e2b1295aa1a139c91824d6ce158f5e6012797b686`;
- motion raw/MAP/relocations exact, target SHA-256
  `77752519e9fe9e2974c43d2a8e29684bba67c63d2a9e1b326e9e22b49e7270f7`;
- A/B MAP SHA-256
  `205a8839a6c1f67556b10e073dddf4b9bd61b21421d75f809252e5fd5ccf7e5c`;
- A/B candidate MAIN SHA-256
  `0b082f90365a96b5a0ca907df4c832b4d062b2792f67a69e60a51003869ca2f9`.

Candidate-state aggregate:

- run `gptweb-v183-circle-aggregate-candidate-001`;
- 216 selected owners, two isolated cold builds, `failures=[]`;
- receipt SHA-256
  `5482d8a3d3dbce9c26c16ab86571209e9ef40fb7e104e1179f3a9c4d4cbeb8aa`;
- the temporary manifest was restored byte-for-byte after the run;
- final-shape MAP SHA-256
  `d35f21ada45f6a26586224ee75cf2333344c9e3cb072ca374277a653dd31d4c9`;
- candidate MAIN SHA-256
  `6685687e0f7554e4f84395e71cabac1f2e3babccaa76abaa86877846108145a4`.

Post-promotion aggregate:

- run `gptweb-v183-circle-aggregate-final-002`;
- all 216 tracked default exact owners pass twice with `failures=[]`;
- receipt SHA-256
  `85d22b45df4113f03103662b72f13ba18fcfabc54ecb76a9a8a19dbd27d877cc`;
- A/B final MAP SHA-256
  `d35f21ada45f6a26586224ee75cf2333344c9e3cb072ca374277a653dd31d4c9`;
- both final candidate MAIN images have SHA-256
  `6685687e0f7554e4f84395e71cabac1f2e3babccaa76abaa86877846108145a4`.

A pre-final complete-diff audit found one unrelated manifest edit introduced by an
overbroad path replacement: the existing exact `th04-main-module-th04-circle-cpp-c64a`
object path had temporarily changed from `obj/th04/circle.obj` to
`obj/th04/motion1.obj`. The tracked manifest was restored before checkpointing.
No source or linked v183 byte changed. Because the earlier aggregate receipts were
bound to the pre-correction manifest identity, the authoritative post-promotion
baseline was rerun as `gptweb-v183-circle-aggregate-final-002`; it passes all 216
default owners twice and is the final receipt cited here.

## Function review and accounting

The fail-closed function-review trial uses the final candidate MAP, the pinned
target-bound metadata snapshot, and the private target. It adds exactly
`th04-main-fn-1bc10`, removes none, and proposes 39 unrelated historical
normalization changes that are deliberately not adopted. Report SHA-256 is
`b8e6989021a6874c1391726dd86f0f7a0d28f078e42519a74bdcbe42d53303d0`.

Live authored-C++ accounting after promotion is:

- exact reviewed authored bytes: **74,921 / 80,406 (93.178370%)**;
- exact reviewed authored functions: **451 / 474 (95.147679%)**;
- routing: 451 exact, 23 reviewed blocked, 62 unreviewed authored candidates;
- original-style ASM attestation observations: 32.

The motion function moves out of the authored-C++ queue, so its 32 exact bytes
are tracked only on the separate ASM unit surface. These percentages remain a
moving reviewed denominator and are not a percentage of MAIN.EXE or TH04 as a
whole.

OP.EXE, MAINE.EXE, and ZUN.COM remain independent queues and receive no MAIN
credit. Their current authored queues remain 94, 72, and 13 unreviewed
candidates respectively; ZUN.COM remains an MZ artifact despite its extension.

## Verification planes and continuation

v183 establishes repository-native exact reconstruction for the natural C++
scroll helper and exact symbolic original-style assembly for motion seg1. It
does not establish standalone TH04 production compile/link closure, whole-image
exactness, runtime-storage identity, runtime-scenario validation, portable
runtime validation, independent pristine-release provenance, or Factory
Truth-Kernel acceptance. No v183 Factory replay claim was submitted.

The next evidence-connected packet should stay on the same structural seam and
consume the remaining pre-scroll CIRCLE residual `0xB9D6..0xBC0F` as a coherent
four-function owner/origin review:

- `TILES_INVALIDATE_AROUND`, `0xB9D6..0xBAA1`, `0xCC`;
- `TILES_FILL_INITIAL`, `0xBAA2..0xBAEC`, `0x4B`;
- alignment NOP at `0xBAED`, outside function ownership;
- `sub_BAEE`, `0xBAEE..0xBBA3`, `0xB6`;
- `tiles_redraw_invalidated()`, `0xBBA4..0xBC0F`, `0x6C`.

Do not assume the replay residual is one historical producer. First close its
original include/TU seams, the relocation at `0xBC0B`, caller/callee ownership,
and any cross-game or original-style-assembly evidence. `randring_fill()` at
`0xBC58..0xBC6F` remains a smaller independent residual behind the exact motion
owner.
