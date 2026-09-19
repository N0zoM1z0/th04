# TH04 B4M Stage 2 midboss producer (v150)

## Result

v150 target-reviews and exactly reconstructs the Stage 2 midboss pattern/update
cohort in `th04-main / MAIN.EXE` as one maintained natural-C++ logical owner.

The exact owner is:

- segment: `B4M_UPDATE_TEXT`;
- map: `13A9:1062..14E7`;
- load: `0x14AF2..0x14F77`;
- target file: `0x162F2..0x16777`;
- size: `0x486 / 1158` bytes;
- target slice SHA-256:
  `0b3b5d5ffa21dfe4fe0ca63b40b7d6a48952331a918064fbe7f0275fb25d4276`.

The selected private target remains read-only and only
`candidate-local-attested`.

## Boundary review

The owner contains four near pattern helpers followed by one FAR dispatcher:

| Entry | Reviewed extent | Result |
| --- | ---: | --- |
| `midboss2_pattern_cloud_spreads` load `0x14AF2` | `0x84` | Ghidra/TASM/raw agree; dispatcher switch supplies the target-local caller anchor. |
| `midboss2_pattern_ring` load `0x14B76` | `0x57` | Ghidra/TASM/raw agree; dispatcher switch supplies the target-local caller anchor. |
| `midboss2_pattern_quad` load `0x14BCD` | `0x78` | Ghidra/TASM/raw agree; dispatcher switch supplies the target-local caller anchor. |
| `midboss2_pattern_aimed_special` load `0x14C45` | `0xB8` | Ghidra/TASM/raw agree; dispatcher switch supplies the target-local caller anchor. |
| FAR `midboss2_update()` load `0x14CFD` | `0x27B` physical | Ghidra is sparse; target-first review closes the compiler tail. |

Fresh Ghidra constructs all four near entries, but reports zero callers for them.
It gives only 383 body bytes over two ranges for FAR `midboss2_update()` and
also reports zero callers for the dispatcher. Pinned TASM and target control
flow explain both omissions: the dispatcher's switch cases directly call the
near helpers, while Stage 2 setup installs the FAR entry through
`_midboss_update_func`.

The dispatcher executes through `RETF` at load `0x14F63`. Five compare values
`0, 1, 2, 3, 0xFF` and five jump words occupy `0x14F64..0x14F77`; every jump
word targets an instruction start. The exact v149 Stage 4 owner begins at the
next byte, load `0x14F78`.

The immediately preceding `gather_point_render()` is deliberately not absorbed
into this owner. It occupies load `0x14A98..0x14AF1`, appears as the separate
`include th04/main/gather_point_render.asm` in the pinned assembler source, and
has a target-local caller from the gather subsystem. The Stage 2 owner therefore
starts at `0x14AF2` rather than being expanded solely because of adjacency.

The seven ordered MZ relocation sites owned by the `0x486` slice are:

```text
0x14CB8 0x14C7C 0x14C66 0x14BE6 0x14B8F 0x14B0B 0x14F12
```

## Natural source and source-shape evidence

Maintained source is `src/main/midboss/m2_update.cpp`, SHA-256
`e4f5b402a12d2ff8d8d12252ddd175657f8d0bdc3b412e4d33dcd2fdccc08756`.
It preserves the historical large memory model, B4M/MAIN_03 ownership, the FAR
update ABI, near helper ABI, and Borland's ordinary
`#pragma samecodeseg midboss_reset` optimization. The three Stage 2 private state
bytes remain in their existing BSS owner and are exposed only through zero-byte
symbol aliases `_midboss2_pattern`, `_midboss2_direction`, and
`_midboss2_patterns_done`.

Three bounded compiler probes identify two source-shape details rather than
manufacturing bytes. The first direct `if`/`else if` spelling emitted 1157 CODE
bytes and also exposed an incorrect gather color-argument order and an incorrect
use of generic `PHASE_EXPLODE_BIG`. A second spelling used
`switch(midboss.phase_frame)` with source cases `1, 48, 52`; TC4J emitted 1156
bytes because it laid out the case bodies in source order. The final natural
source orders the case bodies `48, 52, 1`. TC4J still emits the comparison chain
in sorted value order `1, 48, 52`, but now produces the target physical body
order and the exact 1158-byte contribution. Stage 2's explosion state is the
target-local numeric phase `2`, distinct from the generic TH04 boss explosion
enum value.

The final focused object is a valid single TC86 Borland C++ 4.02 OMF module:

- raw SHA-256:
  `8a27abcbebecc9f44b541e3e710bb44e037844ebf51f4e44c3c716d3731f15bc`;
- dependency-normalized SHA-256:
  `5398d18629c24f308bfe8f7be3c14638df6622f941e487438eeaa0a6201aa5e1`;
- exact map contribution:
  `13A9:1062 0486 C=CODE S=B4M_UPDATE_TEXT G=MAIN_03 M=th04/m2u.cpp ACBP=28`.

There is no inline assembly, `#pragma codestring`, copied target-byte array,
inert padding, fake return, object patch, target patch, or ABI lie.

## Physical layout and zero-credit plumbing

v149 already generated `th04/b4mpre.asm` from a hash-bound prefix of the original
assembler contribution. v150 does not create a second copy. Only when the Stage 2
owner is selected, a hash-bound source transform removes the original Stage 2
PROC/table suffix from that generated file. TASM then naturally emits a `0xB40`
B4M prefix ending immediately before the new source. Replay inserts `m2u.cpp`
between this prefix and the existing exact v149 `m4u.cpp`:

```text
13A9:0522 0B40 B4M_UPDATE_TEXT th04\b4mpre.asm   # replay-only, zero credit
13A9:1062 0486 B4M_UPDATE_TEXT th04/m2u.cpp     # maintained natural C++
13A9:14E8 05D7 B4M_UPDATE_TEXT th04/m4u.cpp     # exact v149 natural C++
13A9:1ABF 1636 B4M_UPDATE_TEXT th04_main.asm     # residual assembler suffix
```

The prefix and residual suffix remain layout plumbing and receive no authored
source-reconstruction credit. Focused and aggregate v150 replay also revalidate
the complete v149 Stage 4 owner after this split.

## Replay

Current-source focused replay:

- `gptweb-v150-midboss2-focused-candidate-001`;
- 92-owner dependency closure;
- receipt SHA-256
  `43dfa598c69bc45a0af49a17f73e556257c8b1c2a5d8c6b422b091c6ca5d628c`;
- two isolated cold builds, `failures=[]`;
- owner raw bytes, map placement, all seven ordered relocations, OMF validity,
  auxiliary TASM validity, and determinism pass;
- the dependent v149 Stage 4 owner also passes all exact checks.

Candidate-state aggregate replay:

- `gptweb-v150-midboss2-aggregate-candidate-001`;
- all 184 default owners twice;
- receipt SHA-256
  `e6ee276011856bdbd31e7de738a0d964ac25bc8c28f5aa23b9a0692549162625`;
- `failures=[]`.

Post-promotion aggregate replay:

- `gptweb-v150-midboss2-aggregate-final-001`;
- all 184 default owners twice;
- receipt SHA-256
  `315a0f3ca0748ec3a674588a4b5a8ce093a655a49d29efdff8dbefb435645afc`;
- `failures=[]`;
- both candidate MAIN images have SHA-256
  `e9cd686b3c435a5aaa630490606aa13fea19ce1c3b1fa12754daa892c3f56cfb`.

## Accounting and verification planes

v150 adds 1,158 reviewed authored bytes and five reviewed functions, all exact
under the complete repository-native promotion chain. The live MAIN ledger is
therefore 54,312 / 54,316 exact reviewed authored bytes (99.992636%) and
331 / 332 exact reviewed functions (99.698795%). The only reviewed blocked
function remains the four-byte `snd_load` remainder. Boundary discovery remains
open, so these percentages are not a completion claim.

The focused and aggregate receipts establish repository-native function/extent
exactness only. They do not establish standalone TH04 production-source/link
closure, runtime-storage identity, a runtime scenario, whole-image exactness,
independently pristine target provenance, or Factory Truth Kernel acceptance.
