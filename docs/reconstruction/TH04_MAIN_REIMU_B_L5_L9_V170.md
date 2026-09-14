# TH04 MAIN Reimu B-shot level 5-9 reconstruction (v170)

## Scope and target binding

This packet reviews and reconstructs the contiguous Reimu B-shot level 5-9
producer in `th04-main / MAIN.EXE / MAIN__TEXT`. The private target remains the
ignored operator input `.analysis/targets/th04/main.exe`, size 156,258 bytes,
SHA-256 `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`,
with canonicality only `candidate-local-attested`.

Factory `th04-ghidra` and repository-native `scripts/ghidra.py th04-main check`
independently attest the current database/target mapping, MZ header, entry,
1,136 relocations, load mapping, and sampled bytes. Ghidra observations remain
provisional and receive zero exactness credit.

## Boundary correction

The old ledger was materially incomplete at this frontier. Fresh Ghidra creates
one function at linear `0x1FB22`, but its body is grossly cross-linked backward
to `0x13D5B` and spans three ranges. It constructs no functions at the next four
TASM entries. Pinned TASM plus target raw decoding instead establish:

| Function | MAIN__TEXT | Load / linear | Executable body | Post-RET table | Physical span |
| --- | ---: | --- | ---: | ---: | ---: |
| `shot_reimu_b_l5()` | `0AAF:5032` | `0xFB22 / 0x1FB22` | `0xC6` | `0x08` | `0xCE` |
| `shot_reimu_b_l6()` | `0AAF:5100` | `0xFBF0 / 0x1FBF0` | `0xC6` | `0x08` | `0xCE` |
| `shot_reimu_b_l7()` | `0AAF:51CE` | `0xFCBE / 0x1FCBE` | `0xC6` | `0x08` | `0xCE` |
| `shot_reimu_b_l8()` | `0AAF:529C` | `0xFD8C / 0x1FD8C` | `0xC6` | `0x08` | `0xCE` |
| `shot_reimu_b_l9()` | `0AAF:536A` | `0xFE5A / 0x1FE5A` | `0xCE` | `0x0C` | `0xDA` |

The physical producer is therefore file `0x11322..0x11733`, load
`0xFB22..0xFF33`, size `0x412`. Its target SHA-256 is
`dd0f0ababdaf3909c9d2d9091cb3e9b9a03b97a1bba4ee975813e5caf0168387`.
There is no overlapping MZ relocation.

Every executable body ends in `RET`. The trailing tables are contiguous and
fill the gap to the next function entry. All twenty target table words resolve,
with CS base `0x1AAF0`, to decoded instruction starts inside their own body.
The final six-word level-9 table ends at `0x1FF33`; the following historical
`bb_playchar` contribution starts at `0x1FF34`.

The function ledger intentionally counts only the executable bodies
(`0xC6/0xC6/0xC6/0xC6/0xCE`). The 0x2C total switch-table bytes are exact
compiler-owned physical data in the 0x412 owner and are not function-body credit.

## Natural source and compiler shape

Maintained natural source is `src/main/player/reimu_shot_b.cpp`. It uses the
existing TH04 shot structures and ordinary C++ control flow. It contains no
inline assembly, copied target bytes, `#pragma codestring`, fake returns, inert
padding, object patching, or ABI lies.

TC86 naturally emits one `0x412` CODE contribution with public offsets
`0`, `0xCE`, `0x19C`, `0x26A`, and `0x338`. One source-shape detail is material:
TC86 emits switch case blocks in source order. The target physically orders the
level 5-8 case blocks from the highest case down and similarly orders the level-9
blocks from the shared 10/11 case downward. Writing the natural switch cases in
that target physical order reproduces both the basic-block sequence and the
compiler jump-table words without target-derived byte emission.

The final source SHA-256 is
`1ba040bddb3e62a5bb9090587eda3aec020ae1c058d04938af88939b0aa04a94`.
The exact focused object has raw SHA-256
`243dcaeafb75698ff9230dcfb677edb9c8a93961df104bc42e4a877bd2ef5ac1`
and dependency-normalized SHA-256
`35bf7c65460cfa4d84b93a291768372334872253c699d4076dbb91c610c3a3ac`.

## Physical split and negative evidence

The target position lies inside the historical monolithic `main__TEXT`
assembler contribution. v170 therefore hash-splits the replay scaffold into:

1. the retained assembler prefix;
2. natural `th04/rshb.cpp`, size `0x412`;
3. replay-only extracted `th04/m1rsuf.asm`, beginning with the original
   `bb_playchar` contribution and receiving zero reconstruction credit.

Splitting an original single OMF exposed module-local symbol ownership. The
replay plumbing publishes or imports only symbolic cross-seam references. TASM
`/mx` name case is significant: the original suffix public for `shots_render()`
is uppercase in OMF, while several prefix GRCG publics are lowercase. The final
plumbing uses the actual OMF spellings rather than changing natural source.

`ReC98.inc` normally publishes absolute `_address_0` when `BINARY` is defined.
Including it independently in both split TASM objects duplicates that public.
The replay-only suffix therefore inlines the same small dependency surface while
omitting only that duplicate absolute-public block. A bounded TASM probe proved
this form emits a valid OMF object.

The most useful negative linked diagnostic is
`gptweb-v170-reimu-b-split-005`, receipt SHA-256
`55dbf79c1683f089f067e34307a906da3272ccdd771af74e011184b99c1bf629`.
It linked successfully but failed broad raw-owner replay. MAP comparison showed
why: zero-length replay suffix declarations for word-aligned `MAIN_0_TEXT` and
`MAIN_01_TEXT` each imposed one byte of TLINK alignment despite contributing no
bytes, shifting `MAIN_012_TEXT` and later segments by two bytes; later empty
word-aligned declarations caused further layout disturbance. Empty replay-only
segment declarations are now byte-aligned, while the byte-bearing `MAIN__TEXT`
contribution retains its real alignment. This removes layout side effects rather
than compensating with padding.

## Exact replay

Focused replay:

- run: `gptweb-v170-reimu-b-split-006`;
- selected dependency owners: 123;
- receipt SHA-256:
  `8e28ab1c7cd338dbe1a5778a6313d9945c93bd489617ec02fc284bb9692cfc08`;
- both candidate MAIN images:
  `23095a8571d66c653f13c0625582f6b8a23bee4dcda9df98fed6fafeaeb6b4bf`;
- complete 0x412 target/candidate slice SHA-256:
  `dd0f0ababdaf3909c9d2d9091cb3e9b9a03b97a1bba4ee975813e5caf0168387`;
- raw, MAP, empty ordered-relocation overlap, OMF validity, auxiliary OMF, and
  A/B determinism all pass.

Candidate-state aggregate:

- run: `gptweb-v170-reimu-b-aggregate-candidate-001`;
- 202 default owners twice;
- receipt SHA-256:
  `c55e5c89bf745a474cd7252f6f46a4c958bb092fe913385f2b01378c906c45ec`;
- both candidate MAIN images:
  `e18f426cd5075d3e41f0d216de327c3a6a98286197c4f10eff42f15fe2d80aed`.

After physical-owner and function-ledger promotion, post-promotion aggregate:

- run: `gptweb-v170-reimu-b-aggregate-final-001`;
- 202 default owners twice;
- receipt SHA-256:
  `a3a1da4fb4472b10b3964d18ef6a229b1999695708b89476e05b825b9a75e9a3`;
- both candidate MAIN images remain
  `e18f426cd5075d3e41f0d216de327c3a6a98286197c4f10eff42f15fe2d80aed`;
- `failures=[]`.

## Fail-closed logical function review

The function reviewer now supports optional `physical_size` on exact extent and
no-Ghidra policies. `size` remains logical executable-function credit;
`physical_size` is used only to validate exact-owner containment, next-public
seams, and trailing compiler switch data. Existing policies default
`physical_size=size`, so prior behavior is unchanged. Focused regression tests
and the complete function-review test module pass.

Level 5 is admitted through the cross-linked exact-extent route. Levels 6-9 use
the no-Ghidra exact route. Each review requires the exact physical owner,
generated MAP public, raw terminal `RET`, target table validation, and the next
public or physical-owner end. Trial review SHA-256 is
`825414cfb7f6b9310dd2144a1e5bce77088c4bc74716aeb2b0defdd16790c365`.
It changes the maintained reviewed set from 390 to exactly 395 IDs, adds only
these five entries, removes none, changes no previous function state/size, and
produces 382 exact plus 13 blocked reviewed functions.

## Verification planes and remaining scope

v170 establishes repository-native exact physical ownership of the 0x412
producer and exact logical boundaries for the five executable functions. It does
not establish standalone TH04 production compile/link closure, whole-image
identity, runtime-storage identity, runtime scenario validation, portable
runtime validation, pristine-release provenance, or exactness of OP/MAINE/ZUN.
Those artifacts remain independent queues and receive no MAIN-derived credit.
