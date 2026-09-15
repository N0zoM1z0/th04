# TH04 MAIN player MAIN_0_TEXT recovery (v175)

## Scope

This packet reviews and reconstructs the complete `MAIN_0_TEXT` player cohort in
the attested local `MAIN.EXE` target. The private target remains ignored operator
input with `candidate-local-attested` canonicality; it is not modified, copied
into the repository, or treated as independently proven pristine media.

The reviewed target window is contiguous:

| Load range | File range | Size | Logical owner |
| --- | --- | ---: | --- |
| `0x10988..0x10ABE` | `0x12188..0x122BE` | `0x137` | `player_miss_update()` |
| `0x10ABF..0x10BFC` | `0x122BF..0x123FC` | `0x13E` | `player_update()` |
| `0x10BFD..0x10D4A` | `0x123FD..0x1254A` | `0x14E` | `player_render()` |

The first two functions form one natural TC4J physical producer of `0x275`
bytes. The renderer is an independent natural TC4J producer of `0x14E` bytes.
Together they exactly cover the historical `MAIN_0_TEXT` contribution before the
already-exact `HUD_OVRL_TEXT` owner at load `0x10D4B`.

## Target-first boundary review

All three entries were already present as provisional/corroborated target
observations, but no exact function credit was accepted before v175. The live
attested boundary inventory reports one contiguous Ghidra range for each entry.
Pinned TASM and raw target decoding independently close the same boundaries:

- `player_miss_update()` ends at the RET at load `0x10ABE`; the next function
  begins at `0x10ABF`.
- `player_update()` ends at the RET at load `0x10BFC`; `player_render()` begins
  at the next byte.
- `player_render()` ends at the RET at load `0x10D4A`; exact `HUD_OVRL_TEXT`
  begins at the next byte.

There is no post-RET jump table or compiler data inside any of the three logical
function extents. The gameplay loop directly calls the target entries of
`player_update()` and `player_render()`. The update routine directly calls the
miss helper. These call anchors are target observations and do not depend on the
reconstruction symbol names.

The analysis provider identity check passed for repository `th04` and target
`target:th04-main`. During v175, the provider's address-taking `disassemble` and
`function` operations rejected schema-valid address arrays before execution.
No semantic conclusion is derived from those transport/argument-layer failures;
the target-bound boundary inventory, raw bytes, TASM, MAP, and cold replay are
used instead. Repository-native `scripts/ghidra.py th04-main check` independently
passed MZ/header/load mapping, entry point, all 1,136 relocation records,
load-module identity, and sampled bytes.

## Natural-source recovery

Maintained source is:

- `src/main/player/update.cpp`, current SHA-256
  `8b55e7869128050f6fc9d7e14cd9984f8e21b054cb84de21f49791adc86ff2a6`;
- `src/main/player/render.cpp`, SHA-256
  `1438369bca78b7054a19ad411c8ac07d410dea1a339bbb9fb0b8cb6778761fe1`.

No inline assembly, target-derived byte arrays, `#pragma codestring`, fake
returns, inert padding, target patching, or ABI lies are used.

The compiler-only feedback loop exposed a small set of ordinary source-shape
mechanisms before any exact replay claim:

- an initial renderer probe was three bytes short because a temporary height
  constant used 32 instead of the real `PLAYER_H == 48`; replacing it with the
  established source constant produces the exact `0x14E` CODE extent;
- the initial update/miss producer was six bytes short because TC4J combined an
  angle update into a memory ADD and merged the two palette-tone stores;
- an explicit byte-valued `_AL` expression lifetime and branch-local palette
  stores produce the target instruction shape;
- local declaration order recovers the target `ENTER 2` frame; and
- one shared source-level `fire_shot` tail recovers the target shared call block.

After these natural source changes, production-profile TC4J emits exactly
`0x275` CODE bytes for the update/miss source and exactly `0x14E` CODE bytes for
the renderer before linking.

Historical ReC98 assembly is treated only as a reconstruction hypothesis. Its
TH04/TH05 player assembly history is reverse-engineering/decompilation history,
not independent original-source evidence. Exact natural TC4J output is therefore
the stronger origin evidence for these extents.

## Physical producer and relocation order

Target ordered MZ relocation overlap is:

- update/miss producer: `[0x10BB9, 0x10A08, 0x109BD]`;
- renderer: `[0x10D34, 0x10CF5, 0x10C6D, 0x10C61]`.

A structurally important neighboring relocation at load `0x10837` belongs to the
still-unreviewed `player_invalidate()` function in the preceding `MAIN__TEXT`
segment. This prevents inferring TLINK object order from ascending code address.

Focused candidate003 deliberately tested the wrong physical order
`pupdate.cpp -> residual th04_main.asm -> prender.cpp`. The update producer itself
had exact MAP and relocations, but the odd `0x275` CODE contribution was followed
by a zero-length word-aligned residual `MAIN_0_TEXT` declaration. TLINK therefore
inserted one alignment byte, moving the renderer, HUD, and later segments by one
byte and invalidating many previously exact owners. This is retained as negative
linker evidence, not reconstruction credit.

The exact physical order is:

`residual th04_main.asm -> pupdate.cpp -> prender.cpp`

The residual assembler owns no bytes in the recovered `MAIN_0_TEXT` region.
Zero-byte aliases expose pre-existing data/function storage to the new C++
objects without creating duplicate runtime state. The two new objects then occupy
exact MAP ranges `0AAF:5E98` and `0AAF:610D` with no intervening padding.

## Exact replay

Current-source focused replay is
`gptweb-v175-player-main0-focused-final-002`. It closes a 129-owner dependency
cohort twice with `failures=[]`; receipt SHA-256 is
`86d9c16ddc7e37d4c0c71900763be94a93174a8739e88a2f9e0ef5dd1d00a43a`.

For `pupdate.cpp`:

- map: `MAIN_0_TEXT 0AAF:5E98`, size `0x275`;
- linked slice SHA-256:
  `961208da263bee64965de2153b1d51175e8d1d2c2c157647f30506815aa9f6f7`;
- target/candidate ordered relocation overlap:
  `[0x10BB9,0x10A08,0x109BD]`;
- raw object SHA-256:
  `39156aea8cf118d6afaddcbee7cf0a8b456918a6135d4b5c1ec2475fb019f22c`;
- dependency-normalized OMF SHA-256:
  `ddce04e6af7d5ff26a4d85b15d8aef679ccfb73cb941442be39c21f744710e0d`.

For `prender.cpp`:

- map: `MAIN_0_TEXT 0AAF:610D`, size `0x14E`;
- linked slice SHA-256:
  `e7c0acc2bdb6ba25f03676501368f6efe0cc5dde23ab1308f80f0150af49cadf`;
- target/candidate ordered relocation overlap:
  `[0x10D34,0x10CF5,0x10C6D,0x10C61]`;
- raw object SHA-256:
  `7312b0f424988926fa8e5c9ab31418df39c1d8fb72f0fbdbc00b9884b17ee731`;
- dependency-normalized OMF SHA-256:
  `791fbe1f8fe86385278ec6fa817fb3be7ed4bcc0585518654269f1392680538f`.

Post-promotion aggregate replay
`gptweb-v175-player-main0-aggregate-final-002` closes all 208 default owners twice
with `failures=[]`; receipt SHA-256 is
`c75c75114966bdd1a1ce70279ee975c1daa2fd72db5b9c20791b1401b3cd6dd4`.
Both player owners remain raw/MAP/ordered-relocation exact with deterministic
valid OMF. Both final runs bind replay manifest SHA-256
`d27105cd1560b4f4e1435c113fde6991c9a510ddc7da505553356843a55cbae5`.

Earlier successful candidate004 and candidate-state aggregate receipts are kept
as historical source/linker evidence. Current exactness claims are bound to the
compat-forwarded maintained source through the focused-final and aggregate-final
runs above.

## Carpet origin follow-up

v175 also closes the specific origin question left by v174 without changing the
Carpet exactness state. A SHA-bound scan of registered TH01-TH05 MAIN targets
searched for the distinctive TH04 `PUSH DS; POP ES; BX=24` prologue and
`CX=24; LODSB; CMP AL,1` loop motifs. Only TH04 MAIN contains either motif, at
load `0xEA8A` / `0xEAAB`. ReC98 history shows the Carpet inline assembly was
introduced by 2023 decompilation commit
`2aae476a855101c2d86fb192a71b2e74d34feaca`.

Therefore no independent evidence currently supports reclassifying
`carpet_lighting_put_new()` as original-style assembly. It remains
reviewed/source-present/blocked with the v174 raw codegen mismatch intact.

## Accounting and verification planes

After v175 promotion, the live non-overlapping MAIN ledger reports 70,313 exact
reviewed authored bytes out of 73,907 (95.137132%) and 414 exact functions out of
428 reviewed authored functions (96.728972%). The denominator grows by the
complete 963-byte player cohort and three exact logical functions.

Repository-native owned-extent/function exactness is PASS for both v175 physical
owners and all three logical functions. Standalone TH04 product compile/link
closure is not established. Runtime-storage identity is not established. No
runtime scenario is executed. Whole-image exactness and portable-runtime
validation are not established. No Factory Truth-Kernel acceptance is submitted
or claimed.

OP.EXE, MAINE.EXE, and ZUN.COM remain independent active authored-boundary queues
and receive no MAIN v175 credit. `ZUN.COM` remains an MZ executable despite its
extension.

## Continuation

The first evidence-connected continuation is `player_invalidate()` at
`MAIN__TEXT` load `0x107E2..0x10875`, current provisional size `0x94`. Its target
relocation at load `0x10837` is the exact relocation that interleaves the v175
update and renderer relocation groups. Review its true boundary, physical owner,
callers/callees, and source language before attempting another MAIN_0-adjacent
reconstruction. This is a structural relocation/owner seam, not an invitation to
harvest a small function in isolation.
