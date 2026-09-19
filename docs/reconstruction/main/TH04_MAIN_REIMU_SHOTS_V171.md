# TH04 MAIN Reimu shot producer v171

## Scope

This packet reviews and reconstructs the contiguous Reimu shot-control producer
in `th04-main / MAIN.EXE / MAIN__TEXT`. It supersedes the v170 B-shot level 5-9
range only as the **current physical byte owner**; all v170 target/source/replay
evidence remains valid historical subextent evidence.

The selected private target remains `candidate-local-attested`. It was read only
and was never patched, relocated, staged, or published.

## Target and tool identity

Fresh Factory `th04-ghidra` attestation binds repository `th04` to
`target:th04-main`, size 156,258 and SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
Repository-native `python3 scripts/ghidra.py th04-main check` independently passes
the 6,144-byte MZ header/load mapping, entry point, all 1,136 relocation records,
load-module identity, and sampled bytes. Ghidra function/decompiler results are
used only as provisional target observations.

The pinned TC86 Borland C++ 4.02 / TASM32 5.0 / TLINK 6.10 toolchain attestation
passes. The host-only `wine64` file hash remains informational under the existing
policy; required portable surfaces and execution probes pass.

## Physical ownership

The reviewed physical producer is:

- target segment: `MAIN__TEXT`;
- target MAP start: `0AAF:484C`;
- MZ load-module extent: `0xF33C..0xFF33`;
- target file extent: `0x10B3C..0x11733`;
- size: `0xBF8 / 3,064` bytes;
- target slice SHA-256:
  `2e121568889d69062af53517dff1e75100a91437c4bf0b0b9633496746c45f96`.

The preceding FAR `hud_put` closes with `RETF` at load `0xF33B`. The following
`BB_PLAYCHAR_LOAD` begins exactly at load `0xFF34`. Raw MZ parsing finds one and
only one relocation inside the complete producer: relocation-table index 468 at
load `0xF355`. Focused and aggregate candidates preserve that ordered overlap.

The first `0x7E6 / 2,022` bytes are fourteen newly reviewed logical functions:

| Function | Load start | Executable size |
| --- | ---: | ---: |
| `reimu_homing_set(Shot near *, unsigned char)` | `0xF33C` | `0x30` |
| `shot_reimu_l0()` | `0xF36C` | `0x24` |
| `shot_reimu_l1()` | `0xF390` | `0x33` |
| `shot_reimu_a_l2()` | `0xF3C3` | `0x90` |
| `shot_reimu_a_l3()` | `0xF453` | `0x96` |
| `shot_reimu_a_l4()` | `0xF4E9` | `0x9C` |
| `shot_reimu_a_l5()` | `0xF585` | `0x9C` |
| `shot_reimu_a_l6()` | `0xF621` | `0x9C` |
| `shot_reimu_a_l7()` | `0xF6BD` | `0xD2` |
| `shot_reimu_a_l8()` | `0xF78F` | `0xB3` |
| `shot_reimu_a_l9()` | `0xF842` | `0x115` |
| `shot_reimu_b_l2()` | `0xF957` | `0x8F` |
| `shot_reimu_b_l3()` | `0xF9E6` | `0x97` |
| `shot_reimu_b_l4()` | `0xFA7D` | `0xA5` |

Fresh target-bound Ghidra constructs each of those fourteen bodies contiguously
at exactly the target/TASM seams. The static homing helper has no original TLINK
public and is therefore admitted only through the fail-closed internal-call gate:
raw `RET 4`, next entry `0x1F36C`, exact owner containment, and target near call
at analysis address `0x1F437` resolving to `0x1F33C`.

The existing v170 functions then complete the physical producer:

| Function | Load start | Executable | Compiler table | Physical span |
| --- | ---: | ---: | ---: | ---: |
| `shot_reimu_b_l5()` | `0xFB22` | `0xC6` | `0x08` | `0xCE` |
| `shot_reimu_b_l6()` | `0xFBF0` | `0xC6` | `0x08` | `0xCE` |
| `shot_reimu_b_l7()` | `0xFCBE` | `0xC6` | `0x08` | `0xCE` |
| `shot_reimu_b_l8()` | `0xFD8C` | `0xC6` | `0x08` | `0xCE` |
| `shot_reimu_b_l9()` | `0xFE5A` | `0xCE` | `0x0C` | `0xDA` |

The `0x2C` total post-RET table bytes are compiler-owned physical data and are
not counted as executable function-body credit. Their twenty words remain the
instruction-aligned tables validated in v170.

## Natural source and compiler result

Maintained source is `src/main/player/reimu_shot.cpp`, SHA-256
`902c6c38c1fbc6bd8ce0724bb2b88240ffcefcd15f45ff22276c9e926ade1cad`.
The source uses the one-line compatibility forwarder
`compat/rec98/th04/main/homing.hpp` until the TH04 homing declaration surface is
localized. It contains no inline assembly, `__emit__`, target-derived byte arrays,
`#pragma codestring`, inert padding, fake returns, object/target patching, or ABI
lies.

TC4J naturally emits one `0xBF8` `MAIN__TEXT` contribution with all eighteen
public callback starts at the target offsets and the static helper at producer
offset zero. Final A/B `rshot.obj` raw SHA-256 is
`2904cf0728c5717a6015511e8a3d7aa7387828e94ec56554341c55dbcd89cb43`;
dependency-timestamp-normalized SHA-256 is
`577fb6111377be17255c414384c8a55516f056bd57eaeacefe421c76cf2aaf7a`.

The exact replay control plane now permits an **unaddressed candidate** to be
inspected against a hash-bound manifest extent before promotion. That route does
not grant byte ownership: only `state=candidate` with a blank ledger file offset
may use the manifest extent, and all non-candidates fail closed. After promotion,
the final aggregate reads the same extent from the ledger. Focused tests cover
ledger precedence, candidate-only use, non-candidate rejection, and size mismatch.

The superseded v170 row is retained with `state=excluded`, blank physical address
fields, and `default_enabled=false`. This preserves historical exact subextent
receipts while preventing the same `0x412` bytes from entering the current
reviewed authored-byte denominator twice.

## Exact replay

All required repository-native promotion replays are complete:

- focused `gptweb-v171-reimu-shots-focused-002`: 123-owner dependency closure,
  `pass=true`, `failures=[]`, receipt SHA-256
  `1271c124b24b51f3a0dccc2b03075f7c7871eb08c8eccce89de8f036c7aa4026`;
  the v171 extent is intentionally reported as `manifest-candidate`;
- candidate-state aggregate `gptweb-v171-reimu-shots-aggregate-candidate-001`:
  all 202 default owners pass twice, receipt SHA-256
  `cd443b56ba3b063f0770022b86c559081b89be8233043b413925aae7161968c6`;
- post-promotion aggregate `gptweb-v171-reimu-shots-aggregate-final-001`:
  all 202 owners pass twice again with `failures=[]`, receipt SHA-256
  `bd841c7dc07fa2387ab9d50ba86748c3002b5a182b60ffc10f39300996967235`;
  the v171 extent now comes from the maintained ledger.

Both aggregate A/B candidate MAIN images have SHA-256
`dbbcd91955aec312e2796456b8d1b1121b88d1c6d07bccf8a9b4cf35cd4e9d3c`.
The current replay manifest SHA-256 is
`4a9d5905fc5743416e31996df3fd4e678a59892cc6359b2d5ff55c8fd7382ce6`.
Every successful build is raw exact, MAP exact, single-relocation-order exact,
valid deterministic OMF, and dependency-closure exact for the declared owner.
The receiptless focused-001 experiment has zero exactness credit.

## Function review and accounting

The fail-closed function reviewer was rerun against the post-promotion aggregate
MAP. Its report SHA-256 is
`7356d1897018e234a9995aeff9a5524cee6b413e65f775c4dbacb54388a2cf16`,
identical to the earlier candidate-state trial. The reviewer directly traverses
360 target candidates (353 exact and seven reviewed nonexact) while its emitted
ledger preserves the complete maintained projection of 409 reviewed rows: 396
exact and 13 blocked. Exactly fourteen new v171 function IDs enter that maintained
ledger. Generic writer normalization would rewrite unrelated historical metadata,
so those 26 field-only changes are deliberately not adopted.

After replacing the current v170 physical owner rather than double-counting it,
live MAIN reviewed authored C/C++ accounting is:

- exact bytes: **67,616 / 71,120 (95.073116%)**;
- exact functions: **396 / 409 (96.821516%)**;
- reviewed blockers: **13**;
- unreviewed MAIN authored candidates: **128**.

These are moving reviewed denominators, not percentages of `MAIN.EXE` or TH04 as
a product.

## Verification planes

Repository-native function/owned-extent exactness is established for the unified
v171 producer and the complete 202-owner post-promotion cohort. Standalone TH04
production-source/link closure is not established. Runtime-storage identity is
not established. No runtime scenario was executed. Whole-image exactness and
portable-runtime validation are not established. No v171 Factory Truth-Kernel
acceptance is claimed here. Independent pristine-release provenance remains open.

`OP.EXE`, `MAINE.EXE`, and `ZUN.COM` remain separate artifact queues. v171 grants
no MAIN-derived source or exactness credit to them; `ZUN.COM` remains an MZ
artifact despite its extension.
