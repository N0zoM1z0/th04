# TH04 shared VRAM / PI front cohort (v210)

## Scope

v210 reviews the SHARED front cohort that follows the artifact-local menu/score
code in `OP.EXE` and `MAINE.EXE`. It deliberately keeps artifact-local exactness
separate from source ownership.

Reviewed target extents:

| Producer | OP payload | MAINE payload | MAIN load | Physical size |
| --- | --- | --- | --- | ---: |
| `vram_planes_set()` | `0xDA12..0xDA3A` | `0xCC7A..0xCCA2` | `0x130EE..0x13116` | `0x29` |
| `frame_delay(int)` | `0xDA3B..0xDA4F` | `0xCCA3..0xCCB7` | `0x131B7..0x131CB` | `0x15` |
| PI put producer | `0xDA50..0xDAFC` | `0xCCB8..0xCD64` | not linked | `0xAD` |
| `pi_load()` | `0xDAFD..0xDB42` | `0xCD65..0xCDAA` | not linked | `0x46` |

The frame-delay row was already reviewed in v209 and is included here only to
close the physical ordering. In MAINE, `pi_put_quarter_8()` begins exactly at
`0xCDAB`; in OP the next independent SHARED owner follows the PI load module.
No retained OP/MAINE payload relocation overlaps any v210 reviewed extent.

## Target-first producer identity

Candidate Intel OMF FIXUPP records independently identify all normal link fields.
No target-difference-derived mask is used.

- `vram_planes_set()`: FIXUPP locations in record order are
  `33, 24, 15, 6`. After masking those four 16-bit fields, MAIN, OP, and MAINE
  have common fixed SHA-256
  `b0fc08641718c8299d856d10a1c1856109ff18000dcea4f2490d20451bb17bb8`.
- PI put (`pi_palette_apply()` + `pi_put_8()`): FIXUPP locations in record
  order are `160, 115, 93, 90, 60, 56, 29, 21, 18, 13`. OP and MAINE have
  common fixed SHA-256
  `7b922462ebcfa345fb2a28538521ed19bccb6cd6bc6da0ac610e76da839703a2`.
- `pi_load()`: FIXUPP locations in record order are
  `58, 53, 43, 29, 26, 14`. OP and MAINE have common fixed SHA-256
  `71d800e1bbb8233c1b24f3d6bb91d3a170be98d8a00fcf5f7b854ba74562d21b`.

The current cold OP and MAINE candidates are already raw-identical to the target
for each complete producer extent. This is strong producer/source routing
evidence, but it is not an artifact-local OP/MAINE exactness Oracle.

Compact cross-artifact receipt:
`.analysis/gpt-web/th04-main-20260917-v210/front-shared-v210.json`, SHA-256
`2d6bae0aca20761208ec10dfce214b469e745ef3bef4762757b1a62d33c36290`.

## Maintained natural source

The already exact MAIN VRAM source moves content-identically to
`src/shared/hardware/vram_planes.cpp`, SHA-256
`b18d07a61c0aeb04d6c7a7eac00b62e0d6cb0b4d438fd516364c19bc8a61a6b2`.
Its historical ReC98 path is only scaffold provenance; v210 source ownership is
proved by the three TH04 targets and current cold replay.

The PI implementations are maintained as ordinary C++:

- `src/shared/formats/pi_put.cpp`, SHA-256
  `dc94dcb027e0f554d222deb0c6086cce603463c33370e3f506ce20324b3c649c`;
- `src/shared/formats/pi_load.cpp`, SHA-256
  `0305c2e99a9fc60e2952f9fcc20b8aa4f1da79286729da68129837db987f6dcd`.

The still-unlocalized declaration/data surface is quarantined through one-line
`compat/rec98/th02/formats/pi.h`, SHA-256
`ccc43c987eabcb9e52c8363ce4fda5bdc7b3621c38e42da32a4eef842b5eeb4a`.
Product source does not directly include the ReC98 tree.

A bounded TC86 Borland C++ 4.02 probe compiled the maintained PI source without
inline assembly, `__emit__`, `#pragma codestring`, copied target bytes, fake
returns, inert padding, target patching, or ABI lies. The PI put object SHA-256 is
`05cdf00c5209bf7fb5dfbc44fc08911a97fe714dc4843e27eac89ccd7b422d17`;
the PI load object SHA-256 is
`483049ddec115e3807e943a5f2685ab6f3d5027d97ed5c23a974a64101426957`.
For each object, LEDATA, FIXUPP, PUBDEF, EXTDEF, and SEGDEF records are byte-
identical to the historical cold `th03/pi_put.obj` / `th03/pi_load.obj`.
ReC98's decompilation history therefore remains provenance, not acceptance
authority.

## MAIN exact replay after source migration

The MAIN VRAM owner was already exact before v210. Because its repository source
path moved, v210 replays it from current source rather than inheriting old
receipts.

Focused `gptweb-v210-vram-shared-focused-001` passes two isolated cold builds,
receipt SHA-256
`af13d01ba896c62883714f6fb04f349526d1a3eb7a6deb2c162f477ffd57d548`.
The 41-byte owner is `raw/map/relocs=true`; A/B `vplanset.obj` SHA-256 is
`65f7d0bd86cf0e321b04f8fd56f70cd421dca0e1c80eb48fbfe70ea7bc3da3ca`.

Mandatory no-unit aggregate `gptweb-v210-shared-front-aggregate-001` passes all
246 default exact MAIN owners twice with `failures=[]`, receipt SHA-256
`de3705cfeaf696017aa3c639c3bed224472de1f7ad23e69a11ab1c3ac5509987`.
It binds exact-manifest SHA-256
`461619ad069dc6666388d512c6b3bca55111ab16bc116a24e4600c9857ab15b8`.
A/B MAP SHA-256 remains
`4bea5732094f5f08b2c37365d7cae466f063e54f7cb22cad115c973810cf59cc`
and A/B candidate MAIN SHA-256 remains
`1932b7feb681e3fa198d24a10cd93a70ce2cb6d400d1ecab39545cafa26b9f9b`.

This is an already-exact source-ownership migration, not a new exact promotion.
No second post-promotion aggregate exists.

## Accounting and limits

OP and MAINE each gain four reviewed natural-source boundaries in this packet.
Their `accepted_state` remains `unreviewed` because the repository has no
artifact-local exact replay/denominator for either executable. MAIN accounting
is intentionally unchanged.

Standalone TH04 product compile/link closure, whole-image exactness,
runtime-storage identity, runtime-scenario validation, portable-runtime
validation, independent pristine provenance, and v210 Factory Truth-Kernel
acceptance are not established.

## Validation and analysis disposition

Full repository `python3 scripts/ci.py` passes after the v210 source, ledger,
and documentation changes. `git diff --check` also passes. The CI includes
tracking and boundary validation, generated-report checks, all four private TH04
target identities, cross-game Oracle calibration, Ghidra/JDK identity, fresh
read-only MAIN database replay, and Ghidra mutation smoke.

The v210 manifest entered at **4,565,529,847 bytes** under `.analysis/`. After
the focused replay, 246-owner aggregate replay, compiler probes, and full CI, the
workspace measures **4,688,710,840 bytes**, net **123,180,993 bytes**. The
focused tree (**58,555,001 bytes**) and aggregate tree (**64,576,905 bytes**) are
retained complete because total session growth remains below the 256 MiB soft
budget; the aggregate is the current cold baseline. The compact v210 scratch was
**8,396 bytes** at that inventory. The tiny **28,271-byte** V210PI short-path
subworkspace is left in shared Wine state rather than using campaign cleanup
authority on the provider prefix. Older baselines, targets, toolchains, Ghidra
state, and legacy/unknown analysis content are untouched.
