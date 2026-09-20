# MAIN stage-session split diagnostic (v282)

The pinned local MAIN.EXE is SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`
and has `candidate-local-attested` provenance. This probe uses its MZ bytes and
relocation table directly; it does not use a disassembler database.

The reviewed session owner is `DEMO_TEXT 0AAF:03E0`, MZ load
`0xAED0..0xB3ED`, target file `0xC6D0..0xCBED`, `0x51E` bytes. The v214
monolithic C++ source already reproduces every owner byte and relocation site,
but puts the relocation at `0xB2DA` last where the target puts it first.

Run the checked-in bounded probe:

```sh
python3 scripts/probes/probe_th04_demo_pause_split.py \
  --output-dir .analysis/reconstruction/probes/v282-demo-pause-split-replay
```

It attests the target, retained v214 inputs, and pinned TC4J/TASM32/TLINK;
then copies those inputs into a temporary private tree. It compiles the first
three functions from `sess.cpp` separately from `pause()`, places `pause()`
in a synthetic byte-aligned `PAUSE_TEXT` segment, and places the following
demo producer in synthetic byte-aligned `DEMO_TAIL_TEXT`. It assembles the
corresponding zero-code segment anchors and links with `pause.obj` before
`sess.obj`. The temporary tree is deleted; logs and a JSON receipt remain
below the output directory.

Pinned TC4J emits `0x3FF` core bytes and `0x11F` pause bytes. Their
concatenation is **byte-identical** to the original `0x51E` monolithic
`sess.obj` CODE; the `0x9A` demo-tail CODE is also unchanged. The trial MAP
places them at `0AAF:03E0`, `0AAF:07DF`, and `0AAF:08FE` respectively. The
linked owner SHA-256 is the target's
`1c409149015a161d36078c7297e9e5fee04bb2dc4ef1b088c72ec81ed1f71e34`,
and all 52 relocation sites agree as an unordered set.

**Ordered relocation equality fails.** The target's owner sites occupy MZ
table indices `22..62` and `89..99`: `0xB2DA` first, then 40 core sites,
then 11 later pause sites. This trial places all 52 owner sites at indices
`506..557`, with the 12 pause sites before the 40 core sites. Thus a plain
function-level split can preserve code and address layout but cannot explain
the target's isolated early `0xB2DA` fixup. The target OMF and its original
segment identities are unavailable; the synthetic segments do not establish
historical ownership. No exact unit or artifact state changes.

Candidate image SHA-256:
`ce0fb6d3ce61aa922ef2411492c048cfc28d1c93081622ab0fa4b515515a0c0a`.
Private receipt SHA-256:
`ef6335bfac23cdc1f389a2ffea984aed73ec67604c438d20becfd16f4a0a0a7d`.
The next producer hypothesis must predict the **global** MZ table placement
as well as owner-local FIXUPP order while preserving the `0x51E` bytes and
verified source semantics.

## Mid-function segment control (v337)

The target order can be described as one `pause()` relocation at load
`0xB2DA`, then the 40 session-core relocations, then the remaining 11
`pause()` relocations. This suggests a three-part object topology, so the
bounded follow-up tested whether TC4J can switch code segments after the first
`input_reset_sense()` call without changing the function body:

```sh
python3 scripts/probes/probe_th04_demo_midfunction_segment.py \
  --output-dir .analysis/reconstruction/probes/v337-demo-midfunction-segment-001
```

The probe attests MAIN, the retained v214 session object, and the pinned TC4J
binary. `#pragma option -zCPAUSE_TAIL_TEXT` inside `pause()` is rejected with
an incorrect-directive diagnostic. `#pragma codeseg PAUSE_TAIL_TEXT main_01`
at the same position compiles, but all `0x11F` bytes remain in one
`PAUSE_HEAD_TEXT` LEDATA range and `PAUSE_TAIL_TEXT` receives no CODE.

Thus the source-level pragma mechanisms cannot produce the proposed
one/core/eleven FIXUPP partition inside this function. The historical object
producer remains unknown, and the unit stays blocked on ordered relocations.
Private receipt SHA-256:
`069ee4f7fc6ccbad0b6dc5f63b83eb299d5f31b49bac97c26df9a9c057c7b850`.

## Pause-only `-B` producer and TH05 control (v378)

The whole-session v236 `-B` diagnostic changed the 0x51E CODE extent and
therefore could not answer whether only `pause()` had a different historical
producer. A bounded follow-up isolates the 0x11F-byte `pause()` body from the
retained v214 source and compiles that source twice. Direct TC86 emits 287
DEMO_TEXT bytes with SHA-256
`fa82e39b2363c970eb3fec366a04c4f15678562e3030cb4c7b45f69210cbdf92`.
TCC `-B` emits assembly; after adding only the same empty `MAI_TEXT` segment
declaration required by the earlier diagnostic, pinned TASM32 emits the
**identical 287 CODE bytes**.

The producer switch changes only OMF fixup ordering. Direct TC86 records the
twelve far-call FIXUPP locations in descending order:

`0x116, 0x104, 0xF2, 0xD9, 0xAB, 0x99, 0x78, 0x4D, 0x46, 0x34, 0x22, 0x09`.

The TASM object records the exact reverse ascending order. Thus whole-pause
`-B` cannot explain the TH04 target sequence, which needs only the first
pause relocation (`0xB2DA`, local pointer-fixup location `0x09`) before the
40 session-core relocations while retaining the other eleven in descending
order.

An independent TH05 target control further narrows the hypothesis. Its
`pause()` is also 0x11F bytes at load `0xB638..0xB756`; the twelve target MZ
relocations are contiguous and descend by local address
`0x117, 0x105, 0xF3, 0xDA, 0xAC, 0x9A, 0x79, 0x4E, 0x47, 0x35, 0x23, 0x0A`.
The first input-call relocation is therefore last, not first. TH04's isolated
`0xB2DA` relocation is not a generic cross-game pause producer property.

Private diagnostic receipt:
`.analysis/gpt-web/demo-pause-B-only-001/receipt.json`, SHA-256
`0046c2f9a60af035bee7732b6144f5cc64e0dd957fe26abf1bac48bcebfd8a8e`.
No maintained source, accepted unit, or exactness denominator changes in v378.

## DEMO producer LEDATA batching (v379)

The v378 pause-only producer experiments showed that changing only the pause
compiler path cannot produce the target one/core/eleven relocation order.
The next diagnostic instead changes the **translation-unit prefix** while
keeping the stage-session source itself unchanged.

A single pinned-TC4J producer containing the 0x1A-byte
`slowdown_frame_delay()` body, the already accepted v377 demo prefix, and the
0x51E-byte stage-session source emits three DEMO_TEXT LEDATA chunks:
`0x000..0x3FA`, `0x3FB..0x7F8`, and `0x7F9..0x8FB`.
`stage_session_init()` begins at object offset `0x3DE`. Parsing FIXUPP
subrecords according to the OMF Location field and selecting only Location=3
(16:16 long-pointer) entries yields exactly 56 stage-session fixups in the
target owner-local order: the first pause pointer at `+0x408`, all forty core
pointers descending, then the remaining eleven pause pointers descending.

The causal control omits only the slowdown prefix. The same TC4J source then
places `stage_session_init()` at `+0x3C4`, uses LEDATA boundaries at `0x400`
and `0x800`, and fails the target order. Separate `-v`, `-y`, `-v -y`,
`-v-`, and `-y-` probes preserve the 1310-byte session CODE and the baseline
FIXUPP order; adding LINNUM metadata therefore does not explain the target.

Private semantic receipt:
`.analysis/gpt-web/demo-fixupp-batching-v379/receipt.json`, SHA-256
`60095c49bb1239b820f28b9e0c8423edd939ea523526db963632eb155694e066`.
This establishes a natural TC86 producer mechanism for the previously
unexplained relocation order, but grants no exact credit until a linked
candidate passes raw bytes, MAP placement, ordered MZ relocations, OMF, and
the complete aggregate.

## Exact fused DEMO producer closure (v380)

The v379 batching mechanism is now reproduced by maintained product source and
accepted by the normal exact replay path. The selected v380 producer compiles
the exact 0x1A-byte `slowdown_frame_delay()` body, the already accepted DEMO
prefix, and `src/main/stage/session_init.cpp` as one natural TC4J `DEMO_TEXT`
object. No relocation-table patch, target-derived byte array, or synthetic
pause producer is involved.

Focused run `gpt-web-demo-session-v380-focused-008` passes two isolated cold
builds with `failures=[]`. Both builds emit the same fused `demopre.obj`
(SHA-256
`92e41ff285ed0696722cb28f447d11196c2ed8d7ab8b943bffcf3e202e628c09`).
The logical stage-session owner remains at `0AAF:03E0`, and all `0x51E`
linked bytes match the target slice SHA-256
`1c409149015a161d36078c7297e9e5fee04bb2dc4ef1b088c72ec81ed1f71e34`.
All 52 overlapping MZ relocations now match in target order, including
`0xB2DA` first, followed by the 40 core sites and the remaining 11 pause
sites. Focused receipt SHA-256:
`1b724362896b55837be39b3c42de61b7e2b04b761891099707f963b215f3bb9d`.

The candidate-state 256-owner aggregate
`gpt-web-demo-session-v380-aggregate-candidate-001` also passes twice. A fresh
attested 920-function Ghidra inventory plus the fail-closed function reviewer
then promotes exactly the four logical functions in this owner:
`stage_session_init()`, `stage_runtime_init()`, `stage_session_free()`, and
`pause()`. Unrelated historical ledger-note normalizations from the trial
writer were deliberately not merged.

After promotion, `gpt-web-demo-session-v380-aggregate-final-001` again passes
all 256 default MAIN owners twice with `failures=[]`; both candidate MAIN
images remain SHA-256
`3512f20edf5bbff733fba23ce55e78b016d2ba39c691df5668e5cde2b2e5eeb5`.
Final receipt SHA-256:
`c87c01b0152815d72eee36eb3d18106e312e854d82b883c1b47db782222183ad`.

This closes the complete 1,310-byte reviewed stage-session gap and four
reviewed authored functions. MAIN now has 81,333 / 83,441 reviewed authored
C/C++ bytes and 482 / 491 reviewed authored C/C++ functions exact. The next
OMF-order target is DIALOG_TEXT.
