# TH04 MAIN CIRCLE spark lifecycle v186

## Scope and recovery

This packet continues the target-first `MAIN.EXE` CIRCLE_TEXT review after the
v185 items-invalidation checkpoint. The private target remains
`candidate-local-attested`; it is never modified, relocated, published, or
committed. Ghidra observations remain provisional target-analysis evidence.

The conversation started from clean committed HEAD
`eb970d1cd955761ff3cae9330d8de91df55efcfa`. While the initial read-only cohort
inspection was in progress, the live worktree changed to six unstaged tracked
files plus untracked `src/main/spark/invalidate.cpp`. The complete diff,
untracked source, current `.analysis/gpt-web/th04-main-20260916-v186/` scratch,
replay receipts, and active-process list were inspected before any new edit.
There was no active TCC/TASM/TLINK/replay producer. The changes form one coherent
v186 packet bound to the same starting HEAD and current target, so they were
classified as recoverable current work and completed rather than reset or
ignored.

The stale prompt hypothesis around `sub_11DE6` was separately checked against
live ledgers. v143 already classifies the adjacent shot-velocity/shot-level seam
as an exact original-style symbolic-TASM owner, so this packet does not reopen
that closed route.

## Reviewed lifecycle cohort

The reviewed physical window is CIRCLE_TEXT `0AAF:168C..1873`, load
`0xC17C..0xC363`, file `0xD97C..0xDB63`, size `0x1E8 / 488`. Its target SHA-256
is `80f435f69d36768c441dd56c96952d520b9a4d953f085d04347e3e627fb01a36`.
The logical bodies are:

| Function | Load extent | Size | Target SHA-256 |
| --- | --- | ---: | --- |
| `ITEM_SPLASHES_RENDER` | `0xC17C..0xC1FE` | `0x83` | `d1a0dce276dcc8dadf49cedf2229c4ef2d4308e533fe674fad3ad9da99d59d87` |
| `@spark_render` | `0xC200..0xC264` | `0x65` | `b5e6cc168a07ac05aa5931c03e10d9e0b87a47d9511cced1a887e5fe100bf32e` |
| `_sparks_update` | `0xC266..0xC2B1` | `0x4C` | `97a59bc875d388aac6a017fbff050c6757c6949f537d147c5aa8f10fafe121f6` |
| `_sparks_render` | `0xC2B2..0xC2EC` | `0x3B` | `e83d1980d89cf5e35d236d42df2db372709757b9b0d67c7da5c7e5f8f6c8baa8` |
| `sparks_invalidate()` | `0xC2EE..0xC313` | `0x26` | `c276012d7f67a319ba2fe203deb3acbfe9522b6b5c07f58a562369a4c8722e3c` |
| `_sparks_init` | `0xC314..0xC331` | `0x1E` | `16384305e570f94bd3fef1189d3d0e103e6e8ef32c7361a57b73db90c908201f` |
| `@item_splash_dot_render` | `0xC332..0xC34D` | `0x1C` | `4898597cc5a5db17fa9565240b3a28784cb27361dc207996af2cafde6510b313` |
| `sub_C34E` | `0xC34E..0xC363` | `0x16` | `6ad88fa26720fcd93fcb85609d05930b846ff5a61dcaebe86198acf3215e58cd` |

The remaining three bytes in the physical window are source-owned layout bytes
at load `0xC1FF`, `0xC265`, and `0xC2ED`. Target MZ relocation overlap in the
window is only `0xC1AE` inside `ITEM_SPLASHES_RENDER` and `0xC31F` inside
`_sparks_init`.

Fresh target-bound Ghidra constructs complete contiguous bodies for the first
seven entries. `sub_C34E` still has no Ghidra function entry; its 0x16 body is
closed independently by target raw decode, the pinned TASM PROC, RET 4, and the
next entry at `0xC364`. The current function-review driver has no
`reviewed_nonexact_no_ghidra` policy: its ordinary nonexact path requires
Ghidra metadata, while no-Ghidra admission exists only for exact owners.
Therefore `sub_C34E` remains a reviewed boundary but is not forced into the
reviewed function denominator in this packet.

Fresh provider caller/callee review connects the cohort rather than treating it
as isolated tiny functions. `_sparks_render` directly calls `@spark_render`;
`ITEM_SPLASHES_RENDER` calls `@item_splash_dot_render`; external lifecycle
callers reach `_sparks_update`, `_sparks_render`, `sparks_invalidate()`, and
`_sparks_init`. The independent TH05 source/cold-map path continues to build
`spark_render.asm`, `sparks.asm`, and `splash_dot_render.asm` from the same TH04
include family. This cross-game structure is corroboration only and does not
transfer source form or exactness.

## Natural-source probes and negative evidence

The selected exact source is `src/main/spark/invalidate.cpp`, SHA-256
`a515166caeb898f934a6563cb220cdf1c28f09987edbd0f2cef79e039f878a86`.
It is ordinary C++ and contains no inline assembly, target-derived byte arrays,
`#pragma codestring`, fake returns, inert padding, ABI lies, or target patches.
A production-profile TC86 contextual probe emits exactly 38 CODE bytes. The only
six pre-link byte differences are three OMF-resolved 16-bit words for
`tile_invalidate_box`, `sparks`, and the near call displacement. Every fixed
instruction, branch, stack operation, structure stride, and return byte is
identical to target.

Two neighboring natural-source probes are deliberately retained as nonexact:

- `_sparks_update`: legal natural TC4J emits 71 bytes versus the 76-byte target.
  It folds the bounds-removal and age-expiry `F_REMOVE` stores into one shared
  tail even when source labels preserve the target conceptual CFG. The target
  keeps a first store plus jump before the age block and a second expiry store.
  The retained negative object SHA-256 is
  `b946fe2db95e7e0860e875bf63507a50ba9093e30ceae6e97b8ef45ec2d48129`;
  its 71-byte code SHA-256 is
  `d88ff9de4135b034b25aa0cfe5d671418683333173c39ba019b336926314ca2c`.
- `_sparks_init`: natural TC4J emits exactly 30 bytes with all fixed instruction
  bytes target-identical and only link words unresolved. Exact promotion is
  withheld because the target public is C-linkage `_sparks_init` while the
  current upstream `spark.hpp` declaration has C++ linkage; Borland rejects an
  `extern "C"` definition after that declaration. The retained shape object
  SHA-256 is
  `c9da84d1674cd0e82f5f90e7e9324cdb3ec34bd23a56ab652c752baeb02c7af2`.
  No macro alias or ABI lie is used to bypass the declaration mismatch.

The remaining lifecycle functions stay reviewed/blocked with no forced source
or original-ASM classification. ReC98 assembler source and TH05 reuse remain
hypothesis/corroboration, not authority.

## Physical producer split

`src/main/spark/invalidate.cpp` is inserted into the zero-credit v185 CIRCLE
suffix without assigning source credit to its neighbors. Hash-bound scaffold
extractions preserve `_sparks_update` and `_sparks_render` in a zero-credit
prefix and preserve `_sparks_init`, `@item_splash_dot_render`, `sub_C34E`, and
the remainder in a zero-credit suffix.

The exact v186 map contribution is CIRCLE_TEXT `0AAF:17FE`, size `0x26`, module
`th04/spkinv.cpp`. The v185 suffix prefix contributes `0AAF:1658` size `0x1A6`;
the post-v186 suffix begins at `0AAF:1824` with historical `_sparks_init`.
No MZ relocation overlaps the maintained 38-byte function.

## Exact Oracles

Final focused replay:

- run: `gptweb-v186-sparks-invalidate-focused-004`;
- selected owners: 115;
- two isolated cold builds;
- receipt SHA-256:
  `99eb92590613b32991376884378150d2ce7bf8772708cb4eda21bbf3a75d4b15`;
- A/B `spkinv.obj` SHA-256:
  `9178b8cea141e03ad28011855df5499116886a8788d10c07acc2f3ac59e64b2a`;
- dependency-normalized object SHA-256:
  `32062a7f467c5824c874b0d287b72ade23c623cf0963972568957a1209eed80c`;
- A/B candidate MAIN SHA-256:
  `518811db1bf863343e7bf69fdad4613c537cd08113b8a40538e0519ee46512df`;
- v186 raw/MAP/relocation checks: all pass.

Candidate-state aggregate:

- run: `gptweb-v186-sparks-invalidate-aggregate-candidate-001`;
- 219 owners, twice;
- receipt SHA-256:
  `e0f4b11e3f535c9a179fd80ee679d2514b188cb2c95a754ad1f685301dd9f9b8`;
- A/B MAP SHA-256:
  `c773c137239e69c599b05209790a5d7cf126e7203088400d09d0e6177311c2ff`;
- A/B candidate MAIN SHA-256:
  `205e42067b0eb3534dc83deba125ebf845c1c153f6515ebe60430d3a79f21bd9`.

Post-promotion aggregate:

- run: `gptweb-v186-sparks-invalidate-aggregate-final-001`;
- 219 tracked default owners, twice;
- receipt SHA-256:
  `731efc53560be3146f6405cd1fbf30b56f134606cc69599c57bddd71114f0fea`;
- manifest SHA-256:
  `545c0602988c82c5b56315040fe60a5733a391bb1bb7548cde7c9d5c4a52b0d0`;
- the v186 raw/MAP/relocation/object identities remain identical to the
  candidate aggregate.

The exact function-review report SHA-256 is
`9e5a1209b37bed0c72aecd7a39ff379a602bfc05bba9b504eb07a98d27bace1c`.
It adds exactly seven lifecycle rows and removes none: one exact
`sparks_invalidate()` plus six reviewed blocked functions. The generic writer
would change 40 unrelated historical rows, so those changes are not adopted.

## Accounting and verification planes

After this packet, live MAIN accounting is:

- exact reviewed authored bytes: **75,034 / 80,519 = 93.187943%**;
- exact reviewed authored functions: **453 / 482 = 93.983402%**;
- blocked functions: 29;
- unreviewed authored candidates: 50;
- original-style ASM attestation observations: 36.

The function percentage drops because six previously corroborated candidates
are now honestly admitted as reviewed blockers while one lifecycle function is
admitted exact. This is denominator expansion, not an accepted exact regression.
The byte accounting grows only by the newly maintained 38-byte owner; reviewed
function boundaries without maintained unit ownership do not fabricate an
accepted byte denominator.

OP.EXE, MAINE.EXE, and ZUN.COM remain separate active queues with 94, 72, and 13
unreviewed authored candidates. No MAIN credit transfers to them. ZUN.COM
remains treated as an MZ executable despite its extension.

This packet proves exact natural-C++ ownership only for `sparks_invalidate()`.
It does not establish standalone TH04 product compile/link closure, whole-image
exactness, runtime-storage identity, runtime-scenario validation, portable
runtime validation, independent pristine-release provenance, or Factory
Truth-Kernel acceptance.

## Next structural packet

The best immediate continuation is not another spelling matrix. First resolve
the TH04-owned spark declaration/linkage seam around `_sparks_init`: its natural
30-byte compiler shape is already closed, but exact C-linkage currently conflicts
with the upstream header declaration. Treat this as a header/ABI ownership
problem, not a request for a macro alias. Review every affected spark caller and
header consumer before changing the declaration, then cold-replay affected exact
owners.

Couple that ABI work with the neighboring unresolved lifecycle producers rather
than taking only a tiny win: re-test `_sparks_render` and
`@item_splash_dot_render` under the corrected local declaration surface, retain
the `_sparks_update` 71-vs-76 negative unless a genuinely new compiler-IR
hypothesis appears, and keep `sub_C34E` as the Ghidra-missed raw/TASM boundary
that still lacks a legal nonexact no-Ghidra function-review path.
