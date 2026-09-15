# TH04 MAIN HUD / score producer v172

## Scope

This packet reviews and reconstructs the contiguous HUD / score producer in
`th04-main / MAIN.EXE / MAIN__TEXT`, immediately before the exact v171 Reimu
shot producer. It replaces only the historical assembler code contribution for
this physical extent. Existing data storage remains in its original owners and
is exposed to the new C++ object only through zero-byte symbolic publication.

The private target remains read-only operator input with canonicality
`candidate-local-attested`. No result in this packet proves independently
pristine release provenance.

## Target, analysis, and toolchain identity

Factory provider `th04-ghidra` is attested to repository `th04` and
`target:th04-main`, size 156,258, SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
`python3 scripts/ghidra.py th04-main check` independently passes the 6,144-byte
MZ header/load mapping, entry point, all 1,136 MZ relocations, load-module
identity, and sampled bytes. Ghidra boundaries, names, xrefs, decompilation, and
types remain provisional target observations with zero exactness credit.

The pinned TC86 Borland C++ 4.02 / TASM32 5.0 / TLINK 6.10 toolchain is READY.
The optional host-only `wine64` file hash remains informational under the
existing policy; the required identity surfaces and execution probes pass.

## Physical ownership

The reconstructed physical producer is:

- target segment/group: `MAIN__TEXT / MAIN_01`;
- target MAP start: `0AAF:4316`;
- MZ load-module extent: `0xEE06..0xF33B`;
- target file extent: `0x10606..0x10B3B`;
- size: `0x536 / 1,334` bytes;
- target slice SHA-256:
  `a2d39c1f44d69d626a7c961d61cc3a824c0a18b05831b34b79170f6f9dd3d751`.

The next byte, load `0xF33C`, is the already exact v171 Reimu shot producer.
The v172 object naturally emits two Borland CODE LEDATA payloads, `0x400` and
`0x136`. The target has 27 overlapping MZ relocations in the exact final order:
18 sites associated with the first object fixup group followed by nine sites in
the second. Focused and both aggregate replays preserve that complete order.

## Logical function boundaries

The physical producer contains eleven reviewed authored functions:

| Function ledger name | Analysis start | Load start | Logical size |
| --- | ---: | ---: | ---: |
| `SCORE_EXTEND_UPDATE_AND_RENDER` | `0x1EE06` | `0xEE06` | `0x9F` |
| `score_reset()` | `0x1EEB0` | `0xEEB0` | `0x38` |
| `hud_lives_put()` | `0x1EEE8` | `0xEEE8` | `0xB9` |
| `hud_bombs_put()` | `0x1EFA1` | `0xEFA1` | `0xC3` |
| `HUD_POINT_ITEMS_PUT` | `0x1F064` | `0xF064` | `0x16` |
| `HUD_DREAM_PUT` | `0x1F07A` | `0xF07A` | `0x17` |
| `hud_graze_put()` | `0x1F091` | `0xF091` | `0x14` |
| `HUD_POWER_PUT` | `0x1F0A5` | `0xF0A5` | `0x38` |
| `hud_hp_put(int)` | `0x1F0DD` | `0xF0DD` | `0x9A` |
| `HUD_BAR_PUT` | `0x1F177` | `0xF177` | `0x8D` |
| `hud_put()` | `0x1F204` | `0xF204` | `0x138` |

Ten entries have contiguous target-bound Ghidra bodies at the exact generated
TC4J MAP public. `SCORE_EXTEND_UPDATE_AND_RENDER` requires a stricter manual
extent review because the switch makes Ghidra's body-address set noncontiguous.
Raw 16-bit decode closes its executable body with `RET` at `0x1EEA4`. The
following physical bytes are compiler data, not function-body credit:

- metadata byte at `0x1EEA5`: `0x00`;
- five switch words at `0x1EEA6..0x1EEAF`:
  `0x4333, 0x433C, 0x4345, 0x4355, 0x4365`;
- with CS base `0x1AAF0`, these resolve to decoded instruction starts
  `0x1EE23, 0x1EE2C, 0x1EE35, 0x1EE45, 0x1EE55`;
- exact generated `score_reset()` begins at `0x1EEB0`.

Therefore logical function bodies total `0x52B`, while the exact physical owner
is `0x536`; the `0x0B` difference is explicitly reviewed compiler metadata/table
data and is never counted as executable function credit.

Fresh caller/callee review also closes the central topology. `hud_put()` has ten
direct Ghidra-observed callees covering the subordinate HUD helpers; point,
dream, and graze helpers share the stage-bonus count renderer. External calls
from the game-over/session/item paths agree with the semantic source names used
by the maintained callers. These semantic observations do not themselves grant
exactness.

## Natural source and source-shape diagnosis

Maintained source is `src/main/hud/hud.cpp`, SHA-256
`4744765113ee2456af66a3741dcea33f9788c5e8670157baa91fa7f4b4e501ef`,
with local declarations in `src/main/hud/hud.hpp`, SHA-256
`823438968ad03713977796f28755ab522b7c9633ae2557695009d2b006c64fa9`.
The producer preserves large-model far pointers, near/far function distance,
Pascal entry points, `MAIN__TEXT / MAIN_01`, and the source-level `-a2` structure
needed for the switch/table layout.

No inline assembly, target-derived byte arrays, `#pragma codestring`, `__emit__`,
fake returns, inert padding, copied target bytes, target/object patching, or ABI
lies are used.

The final two source-shape mechanisms are ordinary Borland semantics:

1. `#pragma samecodeseg playperf_raise` causes TLINK to produce the target
   same-group `NOP; PUSH CS; CALL near` sequence at load `0xEE68` and removes an
   otherwise extra segment relocation at `0xEE6B`. The repository already has
   independently accepted positive examples of this Borland control.
2. Passing the rank-label expression as a direct `const char near *` from DGROUP
   to master.lib's large-model far-pointer parameter makes TC4J emit the target
   `PUSH DS` before rank offset arithmetic. Flat, two-dimensional, `char`, and
   explicit far-cast probes all preserved the wrong push order; a local far
   pointer also enlarged the producer by `0x0B`. The direct near expression
   keeps the complete producer at `0x536` and matches the target order naturally.

A cross-game TH05 target-derived assembler observation shows the same rank-label
`PUSH DS; rank*8; ADD glEASY` instruction shape. It is useful source-shape
corroboration only and receives zero TH04 exactness credit.

The replay also publishes existing assembler-owned data/code labels with
zero-byte aliases so the new C++ object can resolve HUD gaiji strings, the lives
and bombs suffix strings, and the existing stage-bonus renderer. No storage is
copied or re-owned.

## Durable negative evidence

Focused `gptweb-v172-hud-score-focused-candidate-003` is retained as a bounded
negative. Receipt SHA-256 is
`ddba90e0dc90a83f52667e261e48810973cee162336e4ea9714d1fe52b13e069`.
It already had the exact `0x536` MAP contribution and deterministic valid OMF,
but failed raw and relocation exactness in exactly two locations:

- a true FAR `playperf_raise` call produced five mismatching bytes and one extra
  relocation at load `0xEE6B`;
- the rank-label far-pointer argument pushed DS after offset arithmetic rather
  than before it.

The final source changes address only those mechanisms. Candidate-001/002 and
the first aggregate attempt were build/link plumbing failures with zero
exactness credit; their receiptless current-session trees were deleted after
confirming no tracked references and no active producers.

## Exact replay

Focused replay:

`gptweb-v172-hud-score-focused-candidate-004`

- 124-owner dependency closure, two isolated cold builds;
- `pass=true`, `failures=[]`;
- receipt SHA-256:
  `be232c61bad68838ebd97825f8c112086bdf9637650cf59405cdac09ebdc42f5`;
- A/B candidate MAIN SHA-256:
  `76cfa74e6a2085436ec305f353a02832246823b572259465a5bf81af7ce9f148`;
- A/B `hud.obj` raw SHA-256:
  `3a83552d792624c5cf261b041d1d8f98e70747e05f5b4a5eaf8c8c8f311809b8`;
- dependency-timestamp-normalized OMF SHA-256:
  `ca2e3cc0fcb4acb0e355bd8ec05646555313841303ee514052f108896b27124f`.

Candidate-state aggregate:

`gptweb-v172-hud-score-aggregate-candidate-002`

- 203 default owners, two isolated cold builds;
- `pass=true`, `failures=[]`;
- receipt SHA-256:
  `c6bcfe9cb875cbf95699fa54cd57033a7f6e54c9314f2b686b3e71a863dde8e4`;
- A/B candidate MAIN SHA-256:
  `07ca518915a708a8337c90329ce3167b5000e5987f509163a0390865a0d8f92e`.

This aggregate also replays the current v155 stage-bonus source after its
`hud_bombs_put()` declaration is corrected from obsolete C linkage to the real
C++ FAR public. Its complete `0x58D` owner remains raw/MAP exact with all 26
ordered relocations exact in both cold builds.

Post-promotion aggregate:

`gptweb-v172-hud-score-aggregate-final-001`

- 203 default owners, two isolated cold builds;
- `pass=true`, `failures=[]`;
- receipt SHA-256:
  `cd4449b638c3924456c888fdcd5ec8b4e930eaef8913e7e30044ddda30724858`;
- replay manifest SHA-256:
  `4bc3bc77a7bda60d0b1be5b13023d53849bd077f33192506babdf26818e2e3df`;
- A/B candidate MAIN SHA-256 remains
  `07ca518915a708a8337c90329ce3167b5000e5987f509163a0390865a0d8f92e`;
- the v172 extent is read from the promoted ledger and remains raw/MAP/27-order
  relocation exact with deterministic valid OMF.

## Function review and accounting

The fail-closed function reviewer was rerun against the post-promotion aggregate
MAP. Final report SHA-256 is
`50dcbd861918a44760b8f33f9f484182bd478a144b4358d8fe2b1b6527f20e17`,
byte-identical to the pre-promotion trial report. The maintained function ledger
preserves all historical rows and adds exactly the eleven v172 functions; the
reviewer's unrelated historical normalization is intentionally not adopted.

Live MAIN reviewed accounting after v172 is:

- exact authored bytes: **68,950 / 72,454 (95.163828%)**;
- exact authored functions: **407 / 420 (96.904762%)**;
- reviewed blocked functions: **13**;
- unreviewed MAIN authored candidates: **117**;
- MAIN ASM-attestation candidates: **31**.

These are moving reviewed denominators, not percentages of `MAIN.EXE` or TH04 as
a product. They remain below the campaign pressure target and do not imply
completion.

## Verification planes

Repository-native owned-extent/function exactness is established for this v172
producer and the complete 203-owner post-promotion cohort. Standalone TH04
production-source/link closure is not established. Runtime-storage identity is
not established. No runtime scenario was executed. Whole-image exactness is not
established. No Factory Truth-Kernel acceptance was submitted or accepted for
v172. Independent pristine-release provenance remains open.

`OP.EXE`, `MAINE.EXE`, and `ZUN.COM` remain separate artifact queues with no
MAIN-derived exactness credit. `ZUN.COM` remains an MZ artifact despite its
extension.

## Next boundary-connected packet

The immediate left neighbor is structurally meaningful and should be reviewed as
one producer/seam question rather than as isolated easy functions:

- `sub_EC8E`, load `0xEC8E`, current span `0xE3`;
- `@marisa_fg_render$qv`, load `0xED71`, span `0x70`;
- the one-byte post-return zero at load `0xEDE1`;
- `orange_backdrop_colorfill()`, load `0xEDE2`, ending immediately before v172
  at `0xEE06` if the current TASM seam is correct.

The next session should determine physical producer/TU ownership, whether the
one-byte seam is compiler alignment or another owner, and whether the GRCG-heavy
backdrop path is authored C++, original-style assembly, or a mixed producer.
