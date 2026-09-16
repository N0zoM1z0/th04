# TH04 CIRCLE_TEXT .BB tile-mask assembly reconstruction (v198)

## Scope

v198 reviews and exactly reconstructs one low-level `CIRCLE_TEXT` physical owner
in the locally attested TH04 `MAIN.EXE` target as evidence-backed symbolic
original-style / irreducible assembly:

- artifact: `th04-main / MAIN.EXE`;
- group / segment: `MAIN_01 / CIRCLE_TEXT`;
- target MAP start: `0AAF:1426`;
- load-module extent: `0xBF16..0xBFF7`;
- file extent: `0xD716..0xD7F7`;
- physical size: `0xE2 / 226` bytes;
- target/candidate owner SHA-256:
  `655dfe2664c04ed3d529409ffba3689c5f28a7aa24d8793941f1d07efe577e86`.

The owner contains two logical functions and one source-owned alignment byte:

- `tiles_bb_put_raw(int)`: load `0xBF16..0xBF92`, `0x7D / 125` bytes;
- TASM `EVEN` NOP: load `0xBF93`, one byte, outside either function body;
- `tiles_bb_invalidate_raw(int)`: load `0xBF94..0xBFF7`, `0x64 / 100` bytes.

The NOP at load `0xBF15` belongs to the preceding backdrop producer and is not
absorbed by v198. `yuuka5_backdrop_colorfill()` begins at the immediate next
byte, load `0xBFF8`.

The private target remains ignored operator input with only
`candidate-local-attested` canonicality. v198 does not patch, replace, relocate,
commit, or publish it.

## Boundary and relocation review

Fresh target-bound Ghidra constructs a contiguous 125-byte body at analysis
`0x1BF16..0x1BF92` and a contiguous 100-byte body at
`0x1BF94..0x1BFF7`. It currently reports no direct callers for either entry.
Those observations are provisional navigation evidence only and grant no
exactness credit.

Pinned TASM/TLINK and gap-free raw decode independently close the same logical
bodies. The complete physical owner has exactly one overlapping target MZ
relocation: load `0xBF27`, `MAIN_01:CIRCLE_TEXT 0AAF:1437`, the segment word of
the FAR `grcg_setcolor` call. Exact replay reproduces the same ordered overlap.

The post-promotion replay result is bound to the promoted ledger extent and
reports `raw_exact=true`, `map_exact=true`, `relocations_exact=true`, size 226,
and identical target/candidate slice hashes. The existing monolithic
`th04_main.asm` `CIRCLE_TEXT` contribution remains in place; v198 replaces only
the maintained include text for this bounded owner rather than moving physical
neighbors.

## Origin and natural-source feasibility

ReC98 is used only as reconstruction provenance. Its source shape is not treated
as historical author text or exactness authority.

Independent TH05 target evidence preserves the same low-level producer family:

- the put routine keeps the same BP-local, FS mask-reader, and bit-walk
  architecture, with the TH05 body five bytes longer because of its GAME 5
  `scroll_active` path;
- the 100-byte invalidator preserves the same architecture, differing from TH04
  only in six linked operand/displacement bytes.

Legal TC86 Borland C++ 4.02 probes provide an independent negative producer
result rather than a spelling matrix. Direct and register `__seg` pointer forms
dereference through ES, not the target FS mask reader, and no inspected pinned
TC4J header exposes a natural `_FS` pseudo-variable surface. A complete semantic
C++ owner emits 258 CODE bytes versus the target 226, adding stack-stored segment
pointers, ES-based accesses, additional saves/temporaries, and expanded byte
countdowns. No prohibited inline assembly, `__emit__`, codestring, copied target
bytes, inert padding, or ABI fabrication is used to cross that gap.

Together, the independent target and compiler evidence supports classifying this
producer as evidence-backed original-style / irreducible assembly. This does not
claim recovery of the historical source text.

## Maintained symbolic source

Maintained source is `src/main/tile/bb_mask.asm`, SHA-256
`1ec9c305cee7076778ef72fb468c87236c25d8a8a727e6181d3ac77c00fde740`.
It uses semantic symbols, ordinary TASM instructions, the target calling
conventions, and a source-level `EVEN`. It contains no target-derived byte array,
C/C++ inline assembly, `__emit__`, `#pragma codestring`, target patching, fake
return, or hand-authored inert byte padding.

The source remains in the historical include position
`th04/main/tile/bb_put_a.asm` inside the cold scaffold. The exact-unit manifest
therefore gates the reviewed subextent through the containing `th04_main.asm`
object and exact CIRCLE_TEXT MAP placement rather than pretending it is an
independent historical object.

Borland dependency records make raw `th04_main.obj` metadata differ between
cold builds. This is retained rather than hidden. Focused A/B raw object hashes
differ only in dependency `E9` timestamp metadata and normalize to
`e9822d015d24ae75700cf12856e94f7d5daa8888b94689bebf5fef340feffc6f`.
The aggregate A/B objects likewise normalize to
`9610b416ad2feb6173c8577457bd03a790a90e2836ae9fd614e8fda2afd73212`.
Linked bytes, MAP placement, and ordered relocations remain deterministic.

## Exact replay

Focused two-cold replay:

- run: `gptweb-v198-bb-mask-focused-candidate-001`;
- selected dependency closure: 132 units;
- `pass=true`, `failures=[]`;
- receipt SHA-256:
  `ad17e5767f71d39a67653fd0a50d98237bcfc4722932b7b9401a2ffce0120888`;
- both overlay source bindings use maintained source SHA-256
  `1ec9c305cee7076778ef72fb468c87236c25d8a8a727e6181d3ac77c00fde740`;
- A/B MAP SHA-256:
  `5c2b238885dfebe63b33d3d6b1e64b2f3b46137aa6aab202e70ca6e9cc9c86f4`;
- A/B candidate MAIN SHA-256:
  `b6dbff73b689d21f313f2a492a563d72272291b902967996017e033b1ba8d458`.

Candidate no-unit aggregate before promotion:

- run: `gptweb-v198-bb-mask-aggregate-candidate-001`;
- 236 candidate-state default owners, twice;
- `pass=true`, `failures=[]`;
- receipt SHA-256:
  `ce992c2d20b36100c834ad6baddff175a10b4b7e7f2170b7ce2e90d438dd6f74`;
- manifest SHA-256:
  `12b53db3bad2759ef1868a91a9d5256913a1630231163f2e3d17d0b7764c40dd`;
- A/B MAP SHA-256:
  `0465b4e10041a2c2dd718e89c8432a97a7668a53af171f2c52285e191676c375`;
- A/B candidate MAIN SHA-256:
  `a07df1577dae48c3513627f5fd5c593f037bc1a4d103e8e7a010386024e8b759`.

Post-promotion no-unit aggregate:

- run: `gptweb-v198-bb-mask-aggregate-final-001`;
- 236 tracked default exact owners, twice;
- `pass=true`, `failures=[]`;
- receipt SHA-256:
  `ec43a7a89de24e7b84a0b6b9764a0a82145acd9cdc075ac2140aa103eb550aef`;
- manifest SHA-256:
  `12b53db3bad2759ef1868a91a9d5256913a1630231163f2e3d17d0b7764c40dd`;
- v198 result comes from the promoted ledger and reports exact raw bytes, MAP,
  and ordered relocation overlap.

The current tracked manifest has the same SHA-256 as both aggregate receipts.
The current private target parser independently reproduces the 226-byte owner
slice SHA and the sole relocation at load `0xBF27`.

## Other TH04 artifacts

The independently attested unpacked TH04 payloads were checked rather than
receiving MAIN-derived assumptions:

- OP payload SHA-256
  `13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`;
- MAINE payload SHA-256
  `7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c`;
- ZUN payload SHA-256
  `baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.

Longest exact contiguous matches are only 7/7/3 bytes for the MAIN put body and
4/4/4 bytes for the MAIN invalidator across OP/MAINE/ZUN respectively. This is
bounded negative routing evidence only. No MAIN source, boundary, or exactness
credit transfers to those artifacts.

## Ledger plane and continuation

The two logical functions move from the authored C/C++ reconstruction queue to
the independent `attest-asm` queue. They are deliberately not inserted into the
authored C/C++ function ledger. Therefore MAIN reviewed C/C++ accounting remains
**75,482 / 81,141 exact bytes (93.025721%)** and **458 / 481 exact functions
(95.218295%)**. The independent original-style ASM plane rises to **31 exact
physical units / 4,726 bytes**.

Repository-native exact physical ownership is established for the bounded
0xE2 producer. This packet does not establish standalone TH04 production
compile/link closure, whole-image exactness, runtime-storage identity, runtime
scenario validation, portable-runtime validation, Factory Truth-Kernel
acceptance, or independent pristine-release provenance.

The next structurally connected CIRCLE packet should review the complete
`0xBFF8..0xC0FB` residual rather than harvesting one leaf: the 0x22
`yuuka5_backdrop_colorfill()`, the 0x7F `z_super_put_16x16_mono_raw(int)`, its
layout NOP at `0xC099`, the 0x61 `bb_txt_put_8_raw(unsigned int,unsigned int)`,
and the layout NOP at `0xC0FB`. Exact `items_invalidate()` starts at `0xC0FC`.
Reconcile physical producer/include seams, callers/callees, source language,
relocations, and cross-target lineage before choosing natural C++ versus
symbolic assembly.
