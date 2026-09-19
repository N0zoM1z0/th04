# TH04 B4M Stage 1 midboss producer (v153)

## Result

v153 target-reviews and exactly reconstructs the complete remaining Stage 1
`B4M_UPDATE_TEXT` prefix in `th04-main / MAIN.EXE` as one maintained natural-C++
logical owner.

The exact owner is:

- segment: `B4M_UPDATE_TEXT`;
- map: `13A9:0522..0860`;
- load: `0x13FB2..0x142F0`;
- target file: `0x157B2..0x15AF0`;
- size: `0x33F / 831` bytes;
- target/candidate slice SHA-256:
  `715fd10888b236ed8401f9821edb3f1af99e10279b02948b18363aca42f7fb57`.

The selected private target remains read-only and only
`candidate-local-attested`.

## Target-first boundary review

The physical owner contains exactly two authored functions:

| Entry | Reviewed physical extent | Boundary result |
| --- | ---: | --- |
| `midboss1_pattern_special_pair` load `0x13FB2` | `0x65` | Fresh Ghidra, TASM, raw decode, target caller, and next entry agree. |
| FAR `midboss1_update()` load `0x14017` | `0x2DA` | Ghidra truncates after four bytes; target/TASM/raw close the full dispatcher through `RETF`. |

Fresh Ghidra constructs the near helper as one contiguous `0x65` body and also
reports the direct call from load `0x14286` inside the dispatcher. At the FAR
entry, however, Ghidra constructs only the four-byte prologue and misses the
remaining control flow and callees. The accepted FAR boundary therefore does not
inherit that truncated database extent.

Pinned TASM and gap-free target decoding continue the FAR dispatcher through
`RETF` at load `0x142F0`. There is no post-return compiler table or padding in
this owner. Exact v152 Stage 3 begins at the next byte, load `0x142F1`, supplying
a hard right ownership seam. Stage 1 setup independently installs
`@MIDBOSS1_UPDATE$QV` through `_midboss_update_func`.

The complete owner contains fourteen target MZ relocation entries in target
order:

```text
0x142D8 0x1426E 0x14220 0x141B5 0x14198 0x1411A 0x140E5
0x140D5 0x140C2 0x140AF 0x1407A 0x1406A 0x14057 0x14044
```

Focused and aggregate replay reproduce this exact ordered sequence.

## Natural source recovery

Maintained source is `src/main/midboss/m1_update.cpp`, SHA-256
`d54824b032a92fd8f1c35b8c5304e2aecd554d76c35592cdd9e4fcd41857d8c5`.
The source preserves the historical large memory model, FAR update ABI, B4M /
`MAIN_03` code ownership, byte-sized bullet enums, Q4.4 scroll storage, direct
shot-hitbox globals, and the original tile-ring calls.

Two existing BSS objects remain in their original assembler data owner and are
exposed during replay only through zero-byte aliases:

- `_midboss1_angle` over `byte_25594`;
- `_midboss1_vram_y` over `word_25596`.

No storage is moved and no new runtime state is introduced. The latter word is
write-only in the current target inventory; the maintained name intentionally
describes the stored value without inventing a consumer.

No inline assembly, `#pragma codestring`, copied target-byte array, inert
padding, fake return, object patch, target patch, or ABI lie is used.

## Cheapest compiler feedback

Before editing the repository, v153 calibrated its standalone probe command by
recompiling the already-exact v152 `m3u.cpp` from one reused short-path cold
source tree. With the exact Tup profile and a forward-slash relative source path,
the calibration object reproduced both the raw and dependency-normalized v152
OMF identities. An earlier invocation without `GAME=4` failed at preprocessing
and is only probe-driver history, not codegen evidence.

The first Stage 1 natural-source candidate then compiled successfully with no
source-shape iteration. TC86 Borland C++ 4.02 emitted:

- exactly `0x33F` CODE bytes;
- FAR public `@MIDBOSS1_UPDATE$QV` at relative `0x65`;
- therefore the target `0x65` near-helper / `0x2DA` FAR-dispatcher seam.

The standalone probe is supporting compiler evidence only. Linked exactness is
established by cold replay below.

The final cold-replay `m1u.obj` is valid TC86 Borland C++ 4.02 OMF:

- raw SHA-256:
  `69599fbc61ab55ffe8473a78b3ada2e5ec945eda2f2d65c68f1b88e49cae1fd6`;
- dependency-normalized SHA-256:
  `cf4b8fae031fd36f15763692635ec9bb7b9195a2e262ce89e69290967c006886`;
- exact map contribution:
  `13A9:0522 033F C=CODE S=B4M_UPDATE_TEXT G=MAIN_03 M=th04/m1u.cpp ACBP=28`.

## Retiring the code-bearing B4M prefix

Before v153, the v152 replay-only `th04/b4mpre.asm` contributed exactly these
same `0x33F` linked bytes. Its bytes and map were target-identical, but splitting
that historical assembler prefix from later natural producers caused its fourteen
MZ relocation entries to appear in ascending rather than target descending
order. v152 retained this as explicit negative evidence and granted the prefix
no authored/function exactness credit.

v153 supplies a genuinely new producer mechanism rather than weakening that
gate. The exact Stage 1 C++ owner naturally emits all fourteen relocations in
target order. Replay hash-removes the final Stage 1 source span from
`b4mpre.asm`; the resulting object contains zero LEDATA and 21 SEGDEF records.
Its dependency-normalized OMF SHA-256 is
`eb6bb210db91f026b8ac44c4cc3c99d821b5808ad8eafd424f2c46b82afe7130`.
It remains only as a zero-code structural/segment-order anchor and receives zero
reconstruction credit.

The v152 prefix source is bound by SHA-256
`f878e10fbc96180f03e23f4a5174a3b802f49578c6507bb8708e577df656935d`.
The exact removed Stage 1 textual span is bound by SHA-256
`c26b5824b66ff609d0fc500f47d93b61aafdf1465905938c92dd4615efa3946a`;
the zero-code generated prefix source is bound by SHA-256
`cb73fb2b70b44f2d35a7acf1f86373dffee696e71e00e55b1ff50017ce5acb04`.

## Exact replay

Current-source focused replay:

- run: `gptweb-v153-midboss1-focused-candidate-001`;
- 95-owner dependency closure;
- receipt SHA-256:
  `c0683b0f8bf48ac7402e697f097d6871735b99258a6c428b91bd79217aca1d14`;
- two isolated cold builds;
- `failures=[]`;
- owner raw bytes, map, all fourteen ordered relocations, valid OMF, zero-code
  prefix status, and determinism all pass;
- exact Stage 3, Stage X, Stage 2, and Stage 4 dependencies remain passing.

Candidate-state aggregate replay:

- run: `gptweb-v153-midboss1-aggregate-candidate-001`;
- all 187 default owners twice;
- receipt SHA-256:
  `586ccec96e31d7ebd5214ad3f5556e65bb66585dfac2ea08279b4f062151fa59`;
- `failures=[]`;
- both candidate MAIN images have SHA-256
  `49118749258855f0c6b51f73ffeee76697274f353b6176b7898775c695cafc32`.

Post-promotion aggregate replay:

- run: `gptweb-v153-midboss1-aggregate-final-001`;
- all 187 default owners twice;
- receipt SHA-256:
  `4db4654fe46e2524b1be3bcb95c2bb9fe988e3462fda724be169fbd88f32e8d2`;
- `failures=[]`;
- both candidate MAIN images retain SHA-256
  `49118749258855f0c6b51f73ffeee76697274f353b6176b7898775c695cafc32`.

## Accounting and verification planes

v153 adds 831 reviewed authored bytes and two reviewed authored functions, all
exact under the complete repository-native promotion chain. The current MAIN
ledger is therefore:

- `57,102 / 57,106` exact reviewed authored bytes (`99.992995%`);
- `346 / 347` exact reviewed authored functions (`99.711816%`);
- `187` default exact replay owners.

The only reviewed blocked authored function remains the four-byte `snd_load`
remainder. Boundary discovery remains active, so these percentages are not a
completion claim.

The replay receipts establish repository-native function/extent exactness only.
They do not establish standalone TH04 production-source/link closure,
runtime-storage identity, a runtime scenario, whole-image exactness,
independently pristine target provenance, or Factory Truth Kernel acceptance.
