# TH04 B4M Stage 3 midboss producer (v152)

## Result

v152 target-reviews and exactly reconstructs the Stage 3 midboss pattern/update
cohort in `th04-main / MAIN.EXE` as one maintained natural-C++ logical owner.

The exact owner is:

- segment: `B4M_UPDATE_TEXT`;
- map: `13A9:0861..0C1E`;
- load: `0x142F1..0x146AE`;
- target file: `0x15AF1..0x15EAE`;
- size: `0x3BE / 958` bytes;
- target/candidate slice SHA-256:
  `9d39b653e75a26bd64d9683e34d75bc88f025ddd52f881665c26c1066d03c997`.

The selected private target remains read-only and only
`candidate-local-attested`.

## Target-first boundary review

The owner contains four near attack-pattern helpers followed by one FAR
midboss dispatcher:

| Entry | Reviewed physical extent | Boundary result |
| --- | ---: | --- |
| `midboss3_pattern_aimed_spreads` load `0x142F1` | `0x92` | Fresh Ghidra, TASM, raw decode, and the next PROC agree. |
| `midboss3_pattern_cloud_ring` load `0x14383` | `0x44` | Fresh Ghidra, TASM, raw decode, and the next PROC agree. |
| `midboss3_pattern_spread_rotate` load `0x143C7` | `0x5E` | Fresh Ghidra, TASM, raw decode, and the next PROC agree. |
| `midboss3_pattern_random_ring` load `0x14425` | `0x66` | Fresh Ghidra, TASM, raw decode, and the next PROC agree. |
| FAR `midboss3_update()` load `0x1448B` | `0x224` | Ghidra is cross-linked; target/TASM/raw define the accepted extent. |

Fresh target-attested Ghidra gives contiguous complete bodies for the four near
helpers. It does not provide a usable boundary for the FAR dispatcher: its body
is cross-linked far outside `B4M_UPDATE_TEXT`, into unrelated target code. The
accepted FAR boundary therefore does not inherit the database extent.

Pinned TASM and gap-free target decoding show that the FAR dispatcher executes
through `RETF` at load `0x14699`. Load `0x1469A` is one compiler metadata zero;
five compare values followed by five jump words occupy `0x1469B..0x146AE`.
Every jump word targets an instruction start inside the dispatcher. The exact
v151 Stage X owner begins at the next byte, load `0x146AF`, which supplies a
hard right-hand ownership seam. Stage 3 setup independently publishes the FAR
entry through `_midboss_update_func`.

The complete owner contains seven target MZ relocation entries, in target table
order:

```text
0x14679 0x145D9 0x1446D 0x1440F 0x143C3 0x1436D 0x1430E
```

Focused and aggregate replay reproduce this exact ordered sequence.

## Natural source recovery

Maintained source is `src/main/midboss/m3_update.cpp`, SHA-256
`01e10963aea10c01ba4bf79553f3ad525cf36dd32c7d7e1a225035c0a3569719`.
The small historical ReC98 `th04/main/midboss/m3.cpp` file contains constants
and declarations but no function bodies, so it is useful ABI corroboration only
and contributes no exactness credit.

The source uses the normal TH04 large-model declarations for midboss state,
player homing, bullet templates, gathers, items, scroll conversion, vector
motion, HUD rendering, and sound. Two private Stage 3 bytes remain in their
existing BSS owner and are exposed during replay only through zero-byte aliases:
`_midboss3_pattern` over `byte_25598` and `_midboss3_mirror` over
`byte_25599`. Existing `_midboss3_patterns_done` and
`_MIDBOSS3_FLY_ANGLES` symbols remain in their established owners.

No inline assembly, `#pragma codestring`, copied target-byte array, inert
padding, fake return, object patch, target patch, or ABI lie is used.

## Compiler-shape diagnosis

The first useful natural candidate was intentionally diagnosed through the
smallest compiler loop before exact replay.

A probe command that accidentally omitted the production `-b-` flag made
Borland store enum-valued `bullet_template.group` fields as words. That was a
probe-profile error, not source evidence. Recompiling the unchanged source with
the production `-b-` profile immediately made all four near-function boundaries
match target exactly.

Two remaining source-shape experiments localized the FAR-dispatcher difference:

1. With the `phase_frame == 1` flight initialization outside the pattern
   `switch`, TC4J emits `0x3B8` total CODE. The four near helper seams are exact,
   but five case/default exits stay one byte shorter than target.
2. Replacing only the `phase_frame == 64 / 68` chain with a two-case `switch`
   emits `0x3B9`; this does not explain the missing target branch distance.

The corresponding dependency-normalized OMF identities are
`dd29aa8ef5de110acc08d3021b863c13b9a4fb75974eeb24c6f02a9827a3b668`
for the `0x3B8` probe and
`497e2dfd0574514375b2d397304006bd11fa87866dc9a8cf652db0c3c1da4b89`
for the `0x3B9` probe.

Target control flow shows that the flight-initialization block belongs only to
pattern `case 0xFF`. Moving that ordinary C++ block inside the case makes the
five other switch exits naturally widen to the target encodings. The final
production-profile object then has exactly `0x3BE` CODE, the four target helper
seams, FAR public `@MIDBOSS3_UPDATE$QV` at relative `0x19A`, and the target
`RETF` / trailing-switch position.

The final cold-replay object is valid TC86 Borland C++ 4.02 OMF:

- raw SHA-256:
  `7127b99442237eecc69fd6b1f0ead2315586c795fa6ee8a1f1512fa04a44844e`;
- dependency-normalized SHA-256:
  `f257612ae47e3f741d171e2f5b3364304d2e9f4020904d90d8eed48d798f0f49`;
- exact map contribution:
  `13A9:0861 03BE C=CODE S=B4M_UPDATE_TEXT G=MAIN_03 M=th04/m3u.cpp ACBP=28`.

## Physical layout and zero-credit prefix evidence

v151 already leaves the Stage 3 code inside its hash-bound replay-only
`th04/b4mpre.asm`. v152 removes exactly the Stage 3 source span from that
materialized prefix and inserts `m3u.cpp` immediately before exact v151
`mxu.cpp`.

The v151 prefix source is bound by SHA-256
`7a551a24a2ddc77529cf16eb6187f41bbfaba60922c5dd5b25de2ef5a68f2b57`.
The exact removed textual span is bound by SHA-256
`5550308586824570d89f541743cd859f4d469bab796b5dc7de0cf5ec119ddf1a`;
the shortened generated prefix is bound by SHA-256
`f878e10fbc96180f03e23f4a5174a3b802f49578c6507bb8708e577df656935d`.
It contributes `0x33F` bytes immediately before the natural Stage 3 owner.

A diagnostic focused replay deliberately tested this zero-credit prefix as a
linked auxiliary extent. The result is useful negative evidence rather than an
acceptance gate:

- its `0x33F` linked raw bytes are target-identical, SHA-256
  `715fd10888b236ed8401f9821edb3f1af99e10279b02948b18363aca42f7fb57`;
- its map placement is exact at `13A9:0522`, size `0x33F`;
- its TASM object is valid and deterministic after dependency timestamp
  normalization;
- but its fourteen MZ relocation entries appear in ascending order after the
  physical TASM split, while the target table stores the same sites in descending
  order.

The failed diagnostic receipt is
`2cff535f5f7a2563591029277def108e9af4604b2f1f26efe7f44e507bed7aa7`.
The prefix is replay-only layout plumbing and receives no authored source or
function exactness credit. v152 therefore does not pretend that prefix to be an
exact reconstructed owner. The natural `m3u.cpp` owner independently passes its
own complete seven-entry ordered-relocation gate.

## Exact replay

Current-source focused replay:

- run: `gptweb-v152-midboss3-focused-candidate-003`;
- 94-owner dependency closure;
- receipt SHA-256:
  `89e3adf127e14736a061ba0af5359731a64e658336b68f8e02075f87962d7a99`;
- two isolated cold builds;
- `failures=[]`;
- owner raw bytes, map, all seven ordered relocations, valid OMF, and
  determinism all pass;
- exact Stage X, Stage 2, and Stage 4 dependencies remain passing.

Candidate-state aggregate replay:

- run: `gptweb-v152-midboss3-aggregate-candidate-001`;
- all 186 default owners twice;
- receipt SHA-256:
  `885fbc773f73f5400f9914186a05463353f0b4c41ce58e488893a9a097c27ea5`;
- `failures=[]`;
- both candidate MAIN images have SHA-256
  `2d2a030bf3d894fd465bed8f0fec9000efcd82670ee692c6fb3ab1bee5929534`.

Post-promotion aggregate replay:

- run: `gptweb-v152-midboss3-aggregate-final-001`;
- all 186 default owners twice;
- receipt SHA-256:
  `26d4aa1da00b69b45430d7e4bbd19ec36399d83826fdc9068f56ebb9a064d079`;
- `failures=[]`;
- both candidate MAIN images retain SHA-256
  `2d2a030bf3d894fd465bed8f0fec9000efcd82670ee692c6fb3ab1bee5929534`.

## Accounting and verification planes

v152 adds 958 reviewed authored bytes and five reviewed authored functions, all
exact under the complete repository-native promotion chain. The current MAIN
ledger is therefore:

- `56,271 / 56,275` exact reviewed authored bytes (`99.992892%`);
- `344 / 345` exact reviewed authored functions (`99.710145%`);
- `186` default exact replay owners.

The only reviewed blocked authored function remains the four-byte `snd_load`
remainder. Boundary discovery remains active, so these percentages are not a
completion claim.

The replay receipts establish repository-native function/extent exactness only.
They do not establish standalone TH04 production-source/link closure,
runtime-storage identity, a runtime scenario, whole-image exactness,
independently pristine target provenance, or Factory Truth Kernel acceptance.
