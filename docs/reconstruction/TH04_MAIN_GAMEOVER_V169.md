# TH04 MAIN game-over / GameExecl producer reconstruction (v169)

## Scope

This packet closes the `MAIN_TEXT` physical window immediately following
`thicklasers_render()` and immediately preceding the already exact
`yuuka5_fg_render()` owner in the attested local Japanese `MAIN.EXE` target.

Target identity remains:

- artifact: `th04-main / MAIN.EXE`;
- canonicality: `candidate-local-attested`;
- SHA-256: `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`;
- MZ relocation count: 1,136.

No claim in this note establishes pristine-release provenance, standalone TH04
product closure, runtime-storage identity, or runtime-scenario validation.

## Target-first boundary review

Pinned TASM, raw target decoding, target-bound Ghidra metadata, direct target
CALL anchors, and next-entry adjacency close the six contiguous authored
functions after the v168 thick-laser owner:

| Function | MAIN_TEXT | Load extent | File extent | Size |
| --- | --- | --- | --- | ---: |
| `gameover_fade_in()` | `0AAF:3971` | `0xE461..0xE4D0` | `0xFC61..0xFCD0` | `0x70` |
| `gameover_fade_out()` | `0AAF:39E1` | `0xE4D1..0xE540` | `0xFCD1..0xFD40` | `0x70` |
| `gameover_run()` | `0AAF:3A51` | `0xE541..0xE679` | `0xFD41..0xFE79` | `0x139` |
| `gameover_continue_menu()` | `0AAF:3B8A` | `0xE67A..0xE7DD` | `0xFE7A..0xFFDD` | `0x164` |
| `game_state_save_score()` | `0AAF:3CEE` | `0xE7DE..0xE7FC` | `0xFFDE..0xFFFC` | `0x1F` |
| FAR `GameExecl()` | `0AAF:3D0D` | `0xE7FD..0xE8A2` | `0xFFFD..0x100A2` | `0xA6` |

The five near functions total `0x39C` bytes. `GameExecl()` is the immediately
following `0xA6` FAR body. Together they cover exactly `0x442` bytes and end at
load `0xE8A2`; exact `yuuka5_fg_render()` begins at `0xE8A3`.

The target-bound Ghidra metadata constructs contiguous bodies of 112, 112, 313,
356, 31, and 166 bytes respectively. Ghidra remains provisional evidence with
zero exactness credit; the final exact result comes from the cold replay chain
below.

## Natural source and physical-producer split

A first natural TC4J diagnostic emitted the complete `0x442` CODE topology from
one translation unit, with function starts at relative offsets
`0x000/0x070/0x0E0/0x219/0x37D/0x39C`. That result was not promoted.

The target MZ relocation sequence supplies the missing physical-producer
information. The five near functions own one contiguous relocation run ending at
target relocation index 370, while `GameExecl()` begins the immediately following
run at indices 371 through 379. Preserving all six functions in one TC4J object
therefore loses the target FIXUPP/TLINK ordering even though its instruction
shape is correct.

The maintained source is consequently split into two semantic translation units:

- `src/main/core/gameover.cpp`: five near functions, `0x39C` CODE;
- `src/main/core/gameexecl.cpp`: FAR `GameExecl()`, `0xA6` CODE.

The preceding maintained `src/main/bullet/thicklaser_render.cpp` remains its own
`0x19E` TC4J producer. The resulting target-order contribution is therefore:

`tlr.cpp 0x19E -> gmov5.cpp 0x39C -> gmexe.cpp 0xA6 -> y5fg.cpp 0x1CC`.

The exact replay transform removes only the superseded historical
`sub_E2C3..MAIN_TEXT end` code producer, publishes the required symbolic aliases,
and keeps the existing data owners. `gameover_erase_in`, `gameover_erase_out`,
and `maine_binary` remain `extern` aliases to historical assembler-owned data.
No new data-ownership credit is granted by this packet.

The maintained C++ contains no inline assembly, target-derived byte arrays,
`#pragma codestring`, fake returns, inert padding, copied target bytes, or object
patching. Existing `#pragma samecodeseg` directives are source-level Borland
linker controls already independently accepted elsewhere in TH04.

## Focused cold replay

Focused replay:

`gptweb-v169-gameover-focused-candidate-003`

- dependency closure: 122 units;
- receipt SHA-256:
  `f2e566eec3187c16ba4d18440be1e2f8c8056e038737422095ae5303e7d71c7c`;
- manifest SHA-256:
  `4c9eb6bd6fefc43d75ab1cc9d59c44b8a274fc1b8c8d13688357c8f4465cf335`;
- A/B candidate MAIN SHA-256:
  `14fe983faadd7f9d46c788bb79b83c240e8e6212ac5dd2a5fd32ad69bf76e0ab`;
- `failures=[]`.

Owner results:

- `thicklasers_render`: `0x19E`, slice SHA-256
  `217a422e808e1d86bd6bd5ccd9439b1bb263ca8f829bb19074d04ae614849159`,
  exact MAP and all 13 ordered relocations;
- game-over UI owner: `0x39C`, slice SHA-256
  `660c501c75c5c245e6c671d0ce50f489952aa76defe6431ec646f22acf69c4bf`,
  exact MAP and all 29 ordered relocations;
- FAR `GameExecl`: `0xA6`, slice SHA-256
  `ae8fd5d23b3612c3555f9667b5f47ed1dd996d7590ce8e878ee9e317458dd8bf`,
  exact MAP and all 9 ordered relocations.

All three TC86 objects are valid and dependency-normalized deterministic across
A/B.

## Aggregate promotion gates

Candidate-state aggregate:

`gptweb-v169-gameover-aggregate-candidate-001`

- 201 default owners, two isolated cold builds;
- receipt SHA-256:
  `8599ce1fc392efcfbe318ec9152e3df47a87b8558dbec8be64cb2dbf3b394235`;
- A/B candidate MAIN SHA-256:
  `b98f80796da4bd0733a6d32e41b03a54e5ddeeb7471bfdbe67b247fa2b844e5d`;
- `failures=[]`.

Post-promotion aggregate:

`gptweb-v169-gameover-aggregate-final-001`

- 201 default owners, two isolated cold builds;
- receipt SHA-256:
  `2275a3a95f9bb3ce979ce2ef0a259afe298f825f0a69e5291e3122a5a9100b43`;
- manifest SHA-256:
  `316cc25584d87301483125c18242726c314b30831360730ab721b6302c1814f4`;
- A/B candidate MAIN SHA-256:
  `b98f80796da4bd0733a6d32e41b03a54e5ddeeb7471bfdbe67b247fa2b844e5d`;
- `failures=[]`.

## Fail-closed logical function review

The function reviewer uses target-bound Ghidra inventory/metadata, target bytes,
and the candidate aggregate MAP. The five near functions have no original target
TLINK public, so their reconstruction-only C++ publics are accepted only through
the existing `generated_public` + target CALL + next-entry gate. FAR
`GameExecl()` retains the independently observed original target public.

The trial report SHA-256 is
`f7144169df432c1a3b1cfe3aa7be66af36ff98ecfd9360e733fddfac803fb801`.
It changes the maintained reviewed-function set from 384 to exactly 390 IDs,
adds only the six expected v169 functions, removes none, promotes the previously
blocked v168 thick-laser function, and yields 377 exact / 13 blocked reviewed
functions.

## Accounting after promotion

Live MAIN accounting after v169 is:

- reviewed authored bytes: `64,552 / 68,056 exact` (`94.851299%`);
- reviewed authored functions: `377 / 390 exact` (`96.666667%`);
- boundary routing: 377 exact, 13 blocked, 147 unreviewed, 31 ASM-attestation.

These percentages apply only to the moving reviewed authored ledger. They are
not percentages of `MAIN.EXE`, TH04 as a product, or the whole game.

OP.EXE, MAINE.EXE, and ZUN.COM remain independent queues with no honest accepted
exact-function or exact-byte denominator. v169 grants them no credit.

## Retention and verification-plane limits

Receiptless interrupted v169 focused materializations 001 and 002 were deleted
only after confirming inactive producers and no tracked references. Focused 003
and the candidate aggregate were compacted to receipt-only; their receipts remain
hash-bound above. The candidate aggregate MAP used by function review was copied
to the v169 scratch root. The post-promotion aggregate remains a complete cold
baseline.

This packet establishes repository-native owned-extent exactness for the three
physical owners and logical exactness for the seven affected reviewed functions.
It does not establish standalone production-source/link closure, runtime-storage
identity, runtime-scenario validation, whole-image exactness, portable-runtime
validation, Factory Truth-Kernel acceptance for v169, or pristine-release
provenance.
