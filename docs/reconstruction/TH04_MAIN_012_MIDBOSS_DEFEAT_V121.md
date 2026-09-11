# TH04 `MAIN_012_TEXT` default midboss defeat renderer packet (v121)

## Scope and target identity

v121 reconstructs the default midboss defeat renderer immediately before the
v120 Yuuka6 entity-render owner. The active artifact is `th04-main` /
`MAIN.EXE`; the private target remains operator input with
`candidate-local-attested` canonicality and SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
No target bytes were modified, copied into product source, or used to patch a
candidate.

## Boundary and ownership

The complete function is `midboss_defeat_render()` at:

- TLINK `0AAF:6FAA`;
- load-module `0x11A9A..0x11B43`;
- Ghidra `2000:1A9A`, linear `0x21A9A..0x21B43`;
- target file `0x1329A..0x13343`;
- size `0xAA` / 170 bytes;
- target slice SHA-256
  `c2be6296115444300edcc861c867dacd4115cd14ab1a5ac2777e95cc01603af0`.

Fresh attested Ghidra constructs one contiguous 170-byte near body. Pinned TASM
and raw decode agree through the terminal `RET` at `0x21B43`; the next byte,
`0x21B44`, begins independently exact `yuuka6_entities_render()`. Ghidra shows
three unique direct callees: `polar()` (with two FAR call sites), the near
`scroll_subpixel_y_to_vram_seg1()` helper, and FAR `super_roll_put()`. It reports
no direct caller, while the maintained Stage 4 midboss rendering source invokes
this shared renderer from the explode-big phase; the missing direct xref is
therefore not treated as boundary or ownership evidence.

Three target MZ relocations overlap the extent at load addresses `0x11ADB`,
`0x11AF6`, and `0x11B2D`. They are the segment words for the two FAR `polar()`
calls and the FAR `super_roll_put()` call. The scroll helper is a same-group
near call.

## Persistent angle storage

The target routine mutates one byte historically named `angle_23212`. Target
TASM places that byte in the existing MAIN data contribution near the HUD data;
v121 does not move it into the new C++ object. The replay transform publishes
`_midboss_defeat_angle` as an alias at that exact storage address while leaving
`angle_23212 db 0` in place. This preserves storage ownership and link layout
while giving the maintained source a semantic identifier.

## Natural-source feedback loop

The maintained source is `src/main/midboss/defeat_render.cpp`. It uses the
TH04-local `midboss_stuff_t`, the existing large-model `polar()` declaration,
`SinTable8`/`CosTable8`, the near MAIN scroll helper, and `super_roll_put()`.
No ReC98 function body was copied; the reference assembly was used only to
bound and diagnose the target shape.

The first two compile attempts failed before object generation because the
minimal include set did not yet expose the trigonometric tables and then the
SUPER renderer declaration. Adding the current repository's normal
`master.hpp` plus `pc98_gfx.hpp` declaration surfaces solved only those header
issues and did not change the intended source semantics.

The first emitted object was 166 bytes versus the 170-byte target. The sole
structural cause was the capped-angle increment: plain
`midboss_defeat_angle++` let TC4J emit the shorter memory `INC`. Expressing the
same operation through the compiler's live AL register API:

```cpp
_AL = midboss_defeat_angle;
_AL++;
midboss_defeat_angle = _AL;
```

naturally emits the target `MOV AL,[mem]; INC AL; MOV [mem],AL` sequence.

That produced the correct 170-byte size. One final instruction-order mismatch
remained at the loop tail: the target increments the loop index before updating
the angle. Moving both updates into the natural `for` iteration expression,
with `i++` sequenced first, reproduces the target order without padding,
assembly, fake control flow, or byte emission.

The final isolated TC4J object emits exactly 170 code bytes. Candidate versus
target differs only in 16 unresolved link-time runs: 2-byte offsets or 4-byte
FAR pointers. Zeroing those unresolved words makes all 170 bytes identical with
SHA-256
`6c46f96aca7ffe2ed8bb63fa88cbe418af2b1603091e88f9c39ec68f895fc610`.
This object-shape observation was retained as compiler evidence only until the
cold link replays below passed.

The final source contains no inline assembly, `__emit__`, `#pragma codestring`,
target-derived byte arrays, fake return, inert padding, object patching, or ABI
lie.

## Focused replay

v121 applies only after the v120 transforms. The transform is fail-closed over:

- v120-transformed scaffold SHA-256
  `137fef08ca99c78a30af0bd9e78872b53b21ebb062f031513b3ea7c3057e7b83`;
- removed target-derived TASM PROC span SHA-256
  `6d6ac6ed4014be974a9b714c65b5604dd4de1551811a244260fb36049743cc5d`;
- patched scaffold SHA-256
  `6d8d48624dac2693a32962fee8790f32a72d81260f113da2cb745a0ddcd4c0a9`.

The new `th04/mbdrend.cpp` producer is inserted immediately before
`th04/y6rend.cpp`, and the original angle byte remains in the assembler data
producer through the alias described above.

Focused two-cold replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-midboss-defeat-render-v121 \
  --run-id gptweb-v121-midboss-defeat-focused-001
```

passes both isolated builds. Each reports:

- all 170 target bytes exact;
- exact map contribution `0AAF:6FAA 00AA ... M=th04/mbdrend.cpp`;
- exact ordered relocation overlap at the three target sites;
- valid TC86 Borland C++ OMF;
- normalized object SHA-256
  `541d16af3fbc53d2dbdb8a19ec852f43afeba0b5bb020766c57d5c0bfad4b678`;
- deterministic candidate MAIN SHA-256
  `ebd573d2c7d1d17e7d056d74fe1af838179873024ca4c19cb5807dd3d62b5ef4`.

## Aggregate replay and function review

The required aggregate replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --run-id gptweb-v121-midboss-defeat-aggregate-001
```

passes all 157 default owners twice. Both candidate MAIN executables have
SHA-256
`60b1fa74e43dcf20a1e9558ca7b5e414dc9113f23a8e34c985708a9d7db1656f`.
No previously accepted owner regresses.

A fresh target-bound function review uses the v121 aggregate map and the fresh
complete Ghidra metadata block for `0x21A9A`. It reports:

- reviewed authored functions: 276;
- exact functions: 274 (99.275362%);
- automatic exact acceptances: 133;
- manual exact acceptances: 141;
- strict provisional rejections: 0;
- reviewed nonexact functions: 2.

The private report SHA-256 is
`e60e61af6093f4fd25d91195ae81b4de07fe3265332cf1e853a5bb7589e77a37`.
The new renderer is accepted through the ordinary contiguous-Ghidra/TLINK/
exact-owner path, not a manual boundary exception.

## Current state and continuation

v121 expands the reviewed byte denominator by 170 bytes and closes all of them
exactly. The live MAIN C/C++ byte total is 41,454 / 41,485 exact (99.925274%).
The only 31 reviewed nonexact bytes remain the two older blocked functions.

The unresolved `shot_velocity_set()` / `sub_11DE6` source-origin seam is
unchanged. Fresh v121 analysis reconfirmed `sub_11DE6` as the complete 44-byte
FAR `CX=9`/`LOOP` threshold scan with the same-segment `NOP; PUSH CS; CALL near`
tail. No new source-shape hypothesis emerged, so the already-negative ordinary
loop matrix was not repeated.

The next structurally connected target-first candidate is the immediately
preceding `orange_fg_render()` at load `0x1196B..0x11A99`, file
`0x1316B..0x13299`, size `0x12F` / 303 bytes. Fresh attested Ghidra constructs
the complete near body `0x2196B..0x21A99`, ending exactly at the v121 owner,
and reports eight callees. Its callers, relocation/data ownership, and source
shape should be reconciled before reconstruction.
