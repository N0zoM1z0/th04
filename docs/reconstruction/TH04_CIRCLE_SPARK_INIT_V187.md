# TH04 MAIN CIRCLE spark initializer v187

## Scope

This packet continues the target-first `MAIN.EXE` CIRCLE_TEXT lifecycle review
from the v186 spark checkpoint. The private executable remains ignored operator
input with canonicality `candidate-local-attested`; it is never modified,
relocated, published, or committed. Ghidra observations remain provisional and
receive no exactness credit by themselves.

The session starts from clean committed HEAD
`4b90db0f1faceb8da25d2896ccc6227433c7a113`, branch `main`, upstream
`origin/main`, ahead 8 / behind 0. `.analysis/` measured **8,725,089,108 bytes**
at entry. Mandatory preflight/status/boundary gates passed. `th04-ghidra`
discovery again exposed ten operations and no `get_metadata`; provider `check {}`
passed for repository `th04`, target `target:th04-main`, SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
Repository-native Ghidra independently passed the 6,144-byte MZ header, entry,
1,136 ordered relocations, mapping, digest, and samples. Required
TC4J/TASM/TLINK surfaces passed; optional host `wine64` hash drift remains
informational.

The stale prompt route around `sub_11DE6` is not reopened. v143 already owns the
adjacent shot-velocity/shot-level physical seam as exact original-style symbolic
TASM.

## ABI ownership problem

The v186 natural-source probe had already reproduced the fixed instruction shape
of `_sparks_init`, but exact source promotion was blocked by the declaration
surface. Target/TLINK/TASM evidence shows that the TH04 spark API has **mixed
linkage**:

- `_sparks_init`, `_sparks_update`, and `_sparks_render` use C-linkage-style
  publics;
- `sparks_invalidate()` uses the C++-decorated public `@sparks_invalidate$qv`;
- `sparks_add_random()` and `sparks_add_circle()` also remain C++-decorated.

Therefore wrapping the entire upstream `spark.hpp` in `extern "C"`, renaming
symbols with a macro, or lying about the ABI would be incorrect. v187 adds the
maintained TH04-owned declaration surface `src/main/spark/spark.hpp`, SHA-256
`f560ad477bbd32801a9f408d665e420de867a6f89de0e307c16e398d5930a01f`.
Only init/update/render are declared with C linkage; invalidate and add routines
retain C++ linkage. `src/main/core/gameplay_loop.cpp` is corrected to use the
same C-linkage declarations for update/render. That caller remains independently
nonexact; this declaration correction does not grant it exactness credit.

The header preserves `spark_ring_offset` as **16-bit storage**. The original BSS
is `dw ?`, and the already-maintained exact `src/main/spark.asm` add/wrap path
uses the full word. The target initializer nevertheless performs
`mov byte ptr _spark_ring_offset, 0`. The natural source therefore expresses the
real low-byte-only operation instead of changing the global type to manufacture
code shape.

The same target quirk applies to the 16-bit `spark_t::angle` field: initialization
writes only its low byte from `IRand()`.

## Natural source and compiler shape

The maintained initializer is `src/main/spark/init.cpp`, SHA-256
`213f43e3073313dc986a6a68fb1f5ac7f3de6bbd9506c3100486f25a949a3fb3`.
It contains no inline assembly, target-derived byte arrays, `#pragma codestring`,
fake returns, inert padding, symbol aliases, target patches, or ABI lies.

Target extent:

- segment: CIRCLE_TEXT;
- map: `0AAF:1824..1841`;
- load: `0xC314..0xC331`;
- file: `0xDB14..0xDB31`;
- size: `0x1E / 30` bytes;
- target SHA-256:
  `16384305e570f94bd3fef1189d3d0e103e6e8ef32c7361a57b73db90c908201f`.

With the corrected selective-linkage header and explicit low-byte operations,
TC86 Borland C++ 4.02 emits exactly 30 CODE bytes and PUBDEF `_sparks_init`.
Every fixed instruction byte matches target. The only six pre-link byte
differences are three ordinary 16-bit link-resolved words for `sparks`, the
`IRand` FAR offset, and `spark_ring_offset`. The retained probe CODE SHA-256 is
`c1b76ed9ee7d9a5b3e0a6d823a700bad71873e207c817eced0550828813b4c31`;
probe object SHA-256 is
`6bdbec03f4345131c2e41c370ce43f0001497cfd8b58fd83c4012acfb511f663`.

## Physical producer split

v186 left `_sparks_init` in the zero-credit CIRCLE suffix through the extracted
`include th04/sparkinit186.inc`. v187 removes exactly that include from the
hash-bound `cirsuf186.asm` scaffold and inserts natural `th04/spkinit.cpp`
between `spkinv.cpp` and the remaining suffix. No neighboring bytes receive
source credit.

The final natural contribution is exactly CIRCLE_TEXT `0AAF:1824`, size `0x1E`,
module `th04/spkinit.cpp`. `@item_splash_dot_render` still begins at
`0AAF:1842`. The target and candidate each have one ordered MZ relocation inside
the initializer, at load **`0xC31F`**; focused and aggregate replay prove that
relocation exactly.

## Header impact audit

The maintained `th04/main/spark.hpp` overlay participates in more translation
units than the initializer itself. In the v186 final aggregate, 57 logical exact
units map to 16 distinct physical objects whose dependency inventory includes
that header. Recompiling with the maintained v187 header changes both raw and
dependency-normalized OMF identities for all 16 prior objects. This is recorded
rather than hidden or described as object-identity stability.

The object-level identity change is **not** an accepted-byte regression. The v187
220-owner candidate aggregate recompiles the entire default exact cohort under
the new header and proves every accepted linked raw extent, MAP contribution,
and ordered relocation overlap again. The resulting candidate MAIN SHA-256 is
unchanged:
`205e42067b0eb3534dc83deba125ebf845c1c153f6515ebe60430d3a79f21bd9`.
The compact old/new object audit is retained as
`durable-final/spark-header-impact.json`, SHA-256
`f077e5274b9a40c417ce505c7311f7ef4edbb5878f5113d3793ee544f8dae9d5`.

## Exact Oracles

Final focused replay:

- run: `gptweb-v187-sparks-init-focused-current-001`;
- 116 selected owners, two isolated cold builds;
- receipt SHA-256:
  `045b3921f0cc228fd2ea2fdad9627af5b548055e2c26769755262342c2f91dbc`;
- A/B `spkinit.obj` SHA-256:
  `1cb16def69edbe1b41a6582fd7eb86d2ead322f4488d3124095c997cd535ed3e`;
- dependency-normalized object SHA-256:
  `942b016cad6db042ca5b57a28f411939deed69c14f11b99489d0b512b0f00fef`;
- A/B candidate MAIN SHA-256:
  `518811db1bf863343e7bf69fdad4613c537cd08113b8a40538e0519ee46512df`;
- initializer raw/MAP/ordered-relocation verdicts: all exact.

Candidate-state aggregate:

- run: `gptweb-v187-sparks-init-aggregate-candidate-001`;
- 220 owners, twice;
- receipt SHA-256:
  `e4c42e64768a6ea2bfebf2e7a94e555aa22094981280fa316bf00d38c8104d51`;
- A/B MAP SHA-256:
  `1a9ede117a5a1ceaeca956a1571197e163a54f00821bd74b159f9a9e8e2e9968`;
- A/B candidate MAIN SHA-256:
  `205e42067b0eb3534dc83deba125ebf845c1c153f6515ebe60430d3a79f21bd9`;
- all 220 current/candidate owners pass raw/MAP/ordered-relocation gates.

Post-promotion tracked aggregate:

- run: `gptweb-v187-sparks-init-aggregate-current-final-002`;
- 220 tracked default owners, twice;
- receipt SHA-256:
  `e6c5c4c4ca3cf1d20538f0fc091fa9b3d27fae310dc6ce7e1ab592eb0bab2778`;
- tracked manifest SHA-256:
  `7008d5e6398d0c996840166760647ed699bc2d3240e27f78c395391050848dc3`;
- A/B final MAP SHA-256:
  `1a9ede117a5a1ceaeca956a1571197e163a54f00821bd74b159f9a9e8e2e9968`;
- A/B candidate MAIN SHA-256 remains
  `205e42067b0eb3534dc83deba125ebf845c1c153f6515ebe60430d3a79f21bd9`.

## Recovery rebind to the final live manifest

Recovery audit found that the earlier focused/candidate/final receipts were real
PASS receipts but their recorded exact-manifest digests did not equal the final
live file after the interrupted packet was recovered. Rather than infer that the
difference was comment-only, the current live manifest was replayed again.

`gptweb-v187-sparks-init-focused-current-001` passes the 116-owner dependency
closure twice with receipt SHA-256
`045b3921f0cc228fd2ea2fdad9627af5b548055e2c26769755262342c2f91dbc`.
`gptweb-v187-sparks-init-aggregate-current-final-002` passes all 220 tracked
default owners twice with receipt SHA-256
`e6c5c4c4ca3cf1d20538f0fc091fa9b3d27fae310dc6ce7e1ab592eb0bab2778`.
Both receipts bind exact-manifest SHA-256
`7008d5e6398d0c996840166760647ed699bc2d3240e27f78c395391050848dc3`,
which is the live file byte hash at checkpoint time. The aggregate MAP remains
`1a9ede117a5a1ceaeca956a1571197e163a54f00821bd74b159f9a9e8e2e9968`,
A/B `spkinit.obj` remains
`1cb16def69edbe1b41a6582fd7eb86d2ead322f4488d3124095c997cd535ed3e`,
and candidate MAIN remains
`205e42067b0eb3534dc83deba125ebf845c1c153f6515ebe60430d3a79f21bd9`.
The pre-rebind receipts remain historical promotion evidence but are not used as
the final live-manifest binding.

## Function review

The existing v186 reviewed function boundary at Ghidra linear `0x1C314` is not
changed. For promotion, v187 refreshed all later policy-relevant Ghidra metadata
that was missing from the older v128 review file using the attested provider
`function` operation in bounded batches. Five queried policy addresses returned
no Ghidra function, consistent with their no-Ghidra review routes; no synthetic
function metadata was created for them.

The canonical review trial uses the v187 candidate aggregate MAP, the refreshed
metadata surface, and the pinned target. Report SHA-256 is
`11b86623bd7d05a109debba3b3d89547b6b90c1fe73e9362ede65d612607d28c`.
The target row `th04-main-fn-1c314` changes from blocked to exact with unchanged
extent, exact owner, and source. The trial adds zero rows and removes zero rows.
Its generic writer would change 46 unrelated historical rows, so only the target
promotion is manually merged into the maintained ledger.

## Accounting and verification planes

After v187 promotion, live MAIN accounting is:

- exact reviewed authored bytes: **75,064 / 80,549 = 93.190480%**;
- exact reviewed authored functions: **454 / 482 = 94.190871%**;
- blocked functions: 28;
- unreviewed authored candidates: 50;
- original-style ASM attestation observations: 36.

OP.EXE, MAINE.EXE, and ZUN.COM remain independent active queues with 94, 72, and
13 unreviewed authored candidates respectively. No MAIN credit transfers to
those artifacts. ZUN.COM remains treated as an MZ executable despite its
extension.

v187 proves exact natural-C++ ownership only for `_sparks_init` and revalidates
the current exact cohort under the maintained spark declaration surface. It does
not establish standalone TH04 product compile/link closure, whole-image
exactness, runtime-storage identity, runtime-scenario validation, portable
runtime validation, independent pristine-release provenance, or Factory
Truth-Kernel acceptance.

## Analysis retention

After promotion, compact evidence retains the focused/candidate/final receipts,
final object and MAP, canonical function-review report and fresh metadata, the
successful compiler probe, target slice, and the header-impact audit. Only the
current-session reproducible focused/candidate full replay trees and superseded
top-level probe copies are removed after confirming there is no active producer.
The complete post-promotion aggregate remains as the current cold baseline.

After final CI, before checkpoint commit:

- `.analysis/`: **8,806,476,774 bytes**;
- net growth from v187 entry: **81,387,666 bytes**;
- v187 compact scratch: **12,967,337 bytes**;
- retained post-promotion aggregate baseline: **63,889,513 bytes**.

v186/v185 and older baselines, private targets, toolchains, Wine/Ghidra state,
and legacy or unknown analysis content are untouched.

## Next structural packet

Do not return to the `_sparks_update` spelling matrix without a genuinely new
compiler-IR hypothesis; the v186 71-versus-76-byte duplicate-removal-store
negative remains active.

The next evidence-connected packet is the **render side of the same CIRCLE
lifecycle cohort**: `ITEM_SPLASHES_RENDER` at load `0xC17C`, low-level
`@spark_render` at `0xC200`, `_sparks_render` at `0xC2B2`, and
`@item_splash_dot_render` at `0xC332`. Re-test those functions under the now
correct TH04-owned spark declaration surface, preserving source-owned layout
bytes at `0xC1FF`, `0xC265`, and `0xC2ED`. Keep adjacent Ghidra-missed
`sub_C34E` as a separate source/origin question rather than forcing it into the
current nonexact review policy.
