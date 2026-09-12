# TH04 MAIN_033 Mugetsu PC-98 IDE physical producer (v147)

## Result

The maintained Mugetsu MAIN_033 source is now exact for the complete reviewed
physical producer from `13A9:459F..4F5D`, load `0x1802F..0x189ED`, target file
`0x1982F..0x1A1ED`, size `0x9BF / 2495` bytes. The target slice SHA-256 is
`465de67f247a69bdf95a6953de924c88f011f52943e794e945207b75bc6b55e9`.

Exactness is split into the existing non-overlapping logical owners rather than
creating a new overlapping byte-credit unit:

- v107 gather prefix: `0x8C`;
- v108 transition callback: `0x6F`;
- v144 dense transition pair: `0x1EA`;
- v145 phase-2 callbacks: `0x14A`;
- v146 late callbacks and FAR update: `0x590`.

`POINTNUM_DIGITS_SET` remains an independent owner beginning at load `0x189EE`.
The private target remains read-only and only `candidate-local-attested`.

## New compiler mechanism

The command-line TC4J path was the wrong producer for the v144 dense pair. The
original PC-98 IDE integrated compiler, `TC.EXE` from the same pinned TC4J media,
uses a distinct code-generation path. It is run headlessly under the pinned
DOSBox-X PC-98 profile by `scripts/compile_tc4j_pc98_ide.py`. The generated OMF
still identifies its translator as `TC86 Borland C++ 4.02`.

This is not a relaxation of the Oracle. The exact replay freezes
`src/main/boss/mugetsu_main033.cpp` as an explicit prebuild `repo_source` plus
the driver, PC-98 probe helper, toolchain attestor, OMF/MZ parsers, runtime
configuration, DOSBox configuration, and toolchain manifest. The compiler
prebuild produces `obj/th04/m5all.obj`; normal TASM/TLINK replay then compares
the linked artifact exactly as for every other accepted owner.

The focused A/B object has raw SHA-256
`3e1dcf9544a2cac3f4fea66cc39f0098609eacf958e6e78f456f34e746893bd4`
and dependency-normalized SHA-256
`db39c571beaf13e3293aab6f6ff589176cbe7a91cd78c6df0e8190feddfe3e82`.
It contains three CODE LEDATA payloads of 1024, 1023, and 448 bytes, for exactly
`0x9BF` bytes total, and 15 publics at the target offsets. TLINK maps it as:

```text
13A9:459F 09BF C=CODE S=MAIN_033_TEXT G=MAIN_03 M=M5A.CPP ACBP=28
```

The target's fourteen MZ relocations are reproduced in exact order.

## Maintained source ownership

The physical producer does not duplicate five independent copies of the
function bodies. `src/main/boss/mugetsu_main033.cpp` is a composition TU similar
to the already exact Kurumi fused producer. It defines
`TH04_MUGETSU_MAIN033_COMBINED`, establishes the integrated-compiler profile, and
includes the five logical source fragments. Each logical source keeps its
standalone includes/pragmas behind a combined-mode guard, while the function
implementation itself has one checked-in source of truth.

The final v144 dense control flow is ordinary C++ but differs from the earlier
command-line-TCC hypothesis. The integrated compiler needs the target-shaped
shared `ret0` control flow: the final switch case falls through, the `<48` test
jumps to the shared return, and the `stage_frame_mod2 != 0` branch sets sprite
130 then immediately jumps to that return while the false path falls through to
sprite 129. This mechanism was not established by the earlier v109/v144
command-line spelling or optimizer probes, so those failures remain valid
negative evidence for that producer path.

The v146 FAR update also retains the target ABI explicitly: `boss_explode_big`
is called through the same unsigned-int overload used by the exact same-game
boss update sources.

No inline assembly, `#pragma codestring`, target-derived byte array, copied target
bytes, inert padding, fake return, object patch, target patch, or ABI lie is used.

## Cold replay receipts

Current-source focused replay:

- run `gptweb-v147-mugetsu-main033-focused-candidate-007`;
- 114-unit dependency closure;
- receipt SHA-256
  `d50065f7778bda176c0d9c1efe33baa14fd02ff60af5c26a8b6932b972be595e`;
- two isolated cold builds; `failures=[]`;
- all five Mugetsu logical slices pass raw bytes, map, ordered relocations, OMF,
  and determinism.

Candidate-state aggregate replay:

- run `gptweb-v147-mugetsu-main033-aggregate-candidate-002`;
- all 181 default exact owners;
- receipt SHA-256
  `aec4b7e36d88159b51e4628bab04abffd38066b58d9f7e3c4e40e6001741d0b2`;
- two isolated cold builds; `failures=[]`.

Post-promotion aggregate replay:

- run `gptweb-v147-mugetsu-main033-aggregate-final-001`;
- all 181 default exact owners;
- receipt SHA-256
  `a50851ef415b3a84e31ca024b57b0c2cfe5f9cdf023e518f2b7e0b3f0f22859e`;
- two isolated cold builds; `failures=[]`;
- both candidate MAIN images have SHA-256
  `c7905c812815fe02d7d40a7e7bb880a2404e124336df043e742cf69db17c2d84`.

## Recovered-session negative evidence

The interrupted v147 work contained useful failed routes and they remain
recorded rather than being rewritten as successes. An early integrated-compiler
run failed normalized-object determinism before source timestamps were frozen.
During recovery, selecting v144 directly omitted the required v145 split anchor;
a first deduplicated design failed because the physical producer source displaced
the logical overlay fragments; and one linked run exposed an incorrect
`boss_explode_big(explosion_type_t)` overload. A deterministic focused replay
then produced a `0x9C1` object, proving that the pre-v147 dense control-flow shape
was two bytes too large in the fused producer. These are routing failures, not
target rejections.

## Accounting and verification planes

Promotion adds no new reviewed denominator. It converts the already reviewed
2244 Mugetsu bytes and twelve functions from blocked/source-present to exact.
The live MAIN ledger becomes 49,808 / 49,812 exact reviewed authored bytes
(99.991970%) and 312 / 313 exact reviewed authored functions (99.680511%). The
only reviewed blocked function is the four-byte `snd_load` remainder.

The focused and both aggregate receipts establish repository-native exactness for
the declared logical owners only. They do not establish a standalone TH04
production-source/link closure, runtime-storage identity, or any runtime scenario.
No claim is made that the maintained source text is byte-for-byte historical
source, and target provenance remains `candidate-local-attested`. Factory Truth
Kernel acceptance, if submitted, is a separate verification plane.
