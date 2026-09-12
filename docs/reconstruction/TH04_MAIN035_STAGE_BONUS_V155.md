# TH04 MAIN_035 Stage bonus producer (v155)

## Result

v155 target-reviews and exactly reconstructs the contiguous Stage bonus producer
in `th04-main / MAIN.EXE` as maintained natural C++.

The physical owner is:

- segment: `MAIN_035_TEXT`;
- map: `13A9:99FE..9F8A`;
- load: `0x1D48E..0x1DA1A`;
- target file: `0x1EC8E..0x1F21A`;
- size: `0x58D / 1421` bytes;
- target/candidate slice SHA-256:
  `9d34b803f8675921e44088a82add869aa55c3fc4f337ad0d31c3e2289b24adda`.

The private target remains read-only and only `candidate-local-attested`.

## Authored-boundary correction

Six real authored functions tile the owner without gaps:

| Function | Load extent | Size |
| --- | --- | ---: |
| `stage_bonus_value_put` | `0x1D48E..0x1D518` | `0x8B` |
| FAR `stage_bonus_count_put` | `0x1D519..0x1D58E` | `0x76` |
| `stage_bonus_factor_apply` | `0x1D58F..0x1D5E8` | `0x5A` |
| `stage_bonus_apply_modifiers` | `0x1D5E9..0x1D6C0` | `0xD8` |
| `stage_clear_bonus()` | `0x1D6C1..0x1D895` | `0x1D5` |
| `stage_allclear_bonus()` | `0x1D896..0x1DA1A` | `0x185` |

Ghidra is materially wrong in three places. `stage_bonus_apply_modifiers` is
cross-linked into unrelated code. `stage_clear_bonus()` is truncated at load
`0x1D88B`, after which Ghidra invents a function at `0x1D88C`. Likewise,
`stage_allclear_bonus()` is truncated at `0x1D954`, followed by another invented
function at `0x1D955`. Pinned TASM and gap-free target decoding prove those two
entries are ordinary internal tails of the enclosing functions. They remain
excluded boundary observations and do not enter the authored-function denominator.

`stage_bonus_apply_modifiers` owns its four-word compiler jump table at load
`0x1D6B9..0x1D6C0`; all four words resolve to decoded instruction starts inside
the function. The blocked v154 `items_init()` owner begins at the next byte after
`stage_allclear_bonus()`, load `0x1DA1B`, supplying the right ownership seam.

The owner has 26 overlapping target MZ relocation entries. Focused and aggregate
replay reproduce the complete ordered sequence exactly.

## Natural source

Maintained source is `src/main/stage/bonus.cpp`, SHA-256
`4ebfd8b5cdf22c6dbed8946021f5cbec62094d85bfd9d0fc4ef532e0068dc70c`.

The source preserves the large memory model, near/far function distances, Pascal
callee-clean argument order, byte-sized resident/rank state, 32-bit score
arithmetic, existing stage-bonus strings/data ownership, and the historical
`MAIN_03 / MAIN_035_TEXT` code placement. Existing strings and the bombs HUD
routine remain in their original assembler owners; replay only adds zero-byte
public aliases. No data is copied or relocated.

One helper, `stage_bonus_count_put`, also has three callers in the residual
assembler outside this producer. It is therefore exported as a normal FAR Pascal
C function and those exact residual call sites are retargeted to its public
symbol. The two calls inside this producer remain ordinary C++ calls.

No inline assembly, `#pragma codestring`, copied target-byte array, inert padding,
fake return, target/object patch, or ABI lie is used.

## Cheapest compiler feedback

The first successful natural-source probe produced a `0x597` contribution, only
10 bytes longer than target. Correcting the historical Pascal parameter shape and
splitting the factor multiply/divide yielded probe 002 with exact `0x58D` size
and all six function/table seams.

Focused candidate 002 then gave a high-quality linked negative: map placement,
all 26 ordered relocations, OMF validity, total size, and determinism already
passed, while 50 raw bytes differed. During diagnosis, two intermediate diff
scripts accidentally used the wrong executable/file-offset domains; those
results were explicitly rejected and did not drive source changes. The valid
load-module comparison localized the 50 bytes to normal source-shape choices:

- stack-local declaration order in the two formatting helpers;
- Pascal declaration order for `(left, y, value)`;
- source case-body order for the credit-lives switch;
- keeping the non-Extra all-clear path as the natural fallthrough.

Applying only those natural-C++ changes produced candidate 003, which is linked
byte-exact.

The exact cold-replay `sbonus.obj` is valid TC86 Borland C++ 4.02 OMF:

- raw SHA-256:
  `7daf23c48249d4d909c2be13eea6685de2f8a2f80ff83898e0314c09d02a213c`;
- dependency-normalized SHA-256:
  `32c1b74441d96965891928b2d36ea288324f6f03b8503556fd660a62977b2e3d`;
- exact map contribution:
  `13A9:99FE 058D C=CODE S=MAIN_035_TEXT G=MAIN_03 M=th04/sbonus.cpp ACBP=28`.

## Exact replay

Focused replay:

- run: `gptweb-v155-stage-bonus-focused-candidate-003`;
- 96-owner dependency closure;
- receipt SHA-256:
  `4379fd989aadc0d273ce29c5478eba546e5f6953b3cf5e0dc4d96425728c33c7`;
- two isolated cold builds;
- `failures=[]`;
- exact owner bytes, map, all 26 ordered relocations, valid deterministic OMF,
  and dependency closure;
- both focused candidate MAIN images:
  `369ca4dd1899a15eb4dc538810707caf6f87f1415408b48570ffcd82d1005944`.

Candidate-state aggregate:

- run: `gptweb-v155-stage-bonus-aggregate-candidate-001`;
- all 188 default owners twice;
- receipt SHA-256:
  `d3cb2ad5b16f9b8d29ce7d7282fb3806ab1e9f881893bcb64a1812f4a2f82310`;
- `failures=[]`;
- both candidate MAIN images:
  `6698eecf35baa37d31180693491276701d908e80a6f4dd8bd85a3ea0e21f0517`.

Post-promotion aggregate:

- run: `gptweb-v155-stage-bonus-aggregate-final-001`;
- all 188 default owners twice;
- receipt SHA-256:
  `e7457f9e35c77ec9aeff40b5ebbb12273fa4e4830ca365237d3b0ce24f0bc600`;
- `failures=[]`;
- both candidate MAIN images remain:
  `6698eecf35baa37d31180693491276701d908e80a6f4dd8bd85a3ea0e21f0517`.

## Accounting and verification planes

v155 adds 1421 reviewed authored bytes and six reviewed authored functions, all
exact. It also corrects two Ghidra-only observations as internal function tails
rather than function starts. The live MAIN ledger after promotion is:

- `58,523 / 59,877` exact reviewed authored bytes (`97.738698%`);
- `352 / 359` exact reviewed authored functions (`98.050139%`);
- `188` default exact replay owners.

The reduced percentages are not exact-owner regressions. v154 previously added
six source-present blocked item functions and `snd_load` remains independently
blocked by four bytes, so seven reviewed functions and 1354 reviewed bytes remain
nonexact. Boundary discovery also remains active.

v155 establishes repository-native owner/function extent exactness for this
six-function producer. It does not establish standalone TH04 production-source
or link closure, runtime-storage identity, a runtime scenario, whole-image
exactness, independently pristine release provenance, or Factory Truth Kernel
acceptance.
