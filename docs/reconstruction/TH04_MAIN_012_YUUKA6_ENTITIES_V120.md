# TH04 `MAIN_012_TEXT` Yuuka6 entity renderer packet (v120)

## Scope and target identity

v120 reconstructs the target-authored Yuuka6 chase-cross and safety-circle
renderer immediately before the v119 exact Yuuka6 foreground owner. The active
artifact is `th04-main` / `MAIN.EXE`; the private target remains operator input
with `candidate-local-attested` canonicality and SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
No target bytes were modified, copied into product source, or used to patch a
candidate.

## Boundary and owner

The complete near function is now published as `_yuuka6_entities_render` at:

- TLINK `0AAF:7054`;
- load-module `0x11B44..0x11C19`;
- Ghidra `2000:1B44`, linear `0x21B44..0x21C19`;
- target file `0x13344..0x13419`;
- size `0xD6` / 214 bytes;
- target SHA-256
  `ae05e203c6c8d6230efcd361ba416c41f6095f44acc3aa1010234e805dc4f69f`.

Fresh attested Ghidra constructs one contiguous 214-byte body. Pinned TASM and
raw target decoding agree through the terminal near `RET` at `0x21C19`, and the
next byte `0x21C1A` is independently exact `yuuka6_fg_render()`. The new owner
has one direct caller, that foreground renderer, and six callees:
`super_put`, `super_put_1plane`, `grcg_circlefill`, `grcg_circle`, and the two
near GRCG mode/color helpers.

Five target MZ relocations overlap the extent at load-module addresses
`0x11B8A`, `0x11BA9`, `0x11BC1`, `0x11BF1`, and `0x11C0E`. They are the five FAR
graphics calls; the two GRCG helpers are same-group near calls.

## TH04-local data layout

The source does not copy the stale ReC98 Yuuka6 structure definitions. The
maintained exact `src/main/boss/chasecrosses_add.cpp` already supplies the
TH04-local layout evidence:

- `CUSTOM_COUNT` is 32;
- the first 31 records are 0x1A-byte chase-cross entities;
- each chase-cross stores its center at +2/+4, age at +0x0E, and per-frame
  damage at +0x16;
- advancing the 0x1A-byte SI pointer 31 times lands on the final custom record;
- that final 0x1A-byte record is the corrected safety-circle layout, with
  radius fields at +0x10/+0x12 and ring color at +0x18.

This reconciles the two structures inside one routine without inventing a new
storage owner.

## Natural-source feedback loop

The maintained source is `src/main/boss/yuuka6_entities_render.cpp`.

The first compile attempt failed only because `V_RED` was not present on the
current TH04 header surface. `_AH = 2; grcg_setcolor_direct_raw()` expresses the
target color setup directly through the existing natural register API.

The next candidate was 212 bytes versus the 214-byte target. Every instruction
up to the final GRCG shutdown already matched. The sole source-shape mismatch
was `_outportb_(0x7C, 0)`. Inspection showed that helper is implemented through
`__emit__`, which is prohibited in maintained reconstruction source and also
selects the shorter immediate-port `OUT 7Ch,AL` encoding.

The allowed natural register-port form:

```cpp
_DX = 0x7C;
_AL = 0;
outportb(_DX, _AL);
```

naturally emits target `MOV DX,7Ch; MOV AL,0; OUT DX,AL`. With that change TC4J
emits exactly 214 code bytes. The isolated OMF differs from target only at nine
16-bit unresolved link-time words. Zeroing those nine OMF fixup words makes all
214 bytes identical, SHA-256
`9c5e59bb758e36ebeb683518070336caa3ff338fc1d3c22d05f78745828ef763`.

The final source contains no inline assembly, `__emit__`, `#pragma codestring`,
target-derived byte arrays, fake return, inert padding, object patching, or ABI
lie. TC4J naturally allocates the record pointer/index to SI/DI and preserves
the live Y value in AX for the no-damage `super_put` call.

## Focused replay

v120 removes the old TASM body only after the v119 frontier transforms and
inserts `th04/y6rend.cpp` immediately before `th04/y6fg.cpp`. The transform is
fail-closed against:

- v119-transformed scaffold SHA-256
  `aca6a0dae22a67b57ee3409e1572f109928c0326530650618b451a88a1ea7a9a`;
- removed CRLF source span SHA-256
  `c61b61710c74be926618008bff173bab514d1a1f74a157fb2697a02278a932cc`;
- patched scaffold SHA-256
  `137fef08ca99c78a30af0bd9e78872b53b21ebb062f031513b3ea7c3057e7b83`.

Focused two-cold replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-yuuka6-entities-render-v120 \
  --run-id gptweb-v120-yuuka-entities-focused-001
```

passes in both isolated builds: all 214 raw bytes, exact map contribution at
`0AAF:7054`, exact ordered five-relocation overlap, valid TC86 OMF, normalized
OMF SHA-256
`22caa366a1f0c52f923a91f2dd3633ce4bae9989ba507df04e75be57a4b72d10`,
and focused candidate MAIN SHA-256
`08d890be852e491867180d5d4e7e4be3623322f06c1eef6b858d64c3d2bc4eed`.

## Aggregate replay and function review

The required aggregate replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --run-id gptweb-v120-yuuka-entities-aggregate-001
```

passes all 156 default owners twice. Both candidate MAIN executables have
SHA-256
`db01824ab61ea9070b4b960e6a37781e4eea8ffcf77863acbf08c4d754633d99`.
No previously accepted owner regresses.

A fresh target-bound function review uses the v120 aggregate map plus a fresh
metadata block for the complete Ghidra body at `0x21B44`. It reports 273 exact
of 275 reviewed authored functions (99.272727%), automatic=132, manual=141,
strict rejections=0, reviewed nonexact=2. The private report SHA-256 is
`a411d7b5fcf14e305c3c3b207e01b21d4b2e40ee66114a44ea693190fc31b403`.
The new renderer is accepted through the ordinary complete-Ghidra/TLINK/exact-
owner gate rather than a manual boundary exception.

## Current state and continuation

v120 expands the reviewed byte denominator by 214 bytes and closes all of them
exactly. The live MAIN C/C++ byte total is 41,284 / 41,315 exact (99.924967%).
The only 31 reviewed nonexact bytes remain the two older blocked functions.

The nearby semantic seam is unchanged: `shot_velocity_set()` and `sub_11DE6`
still have no accepted natural source or independently proved original-assembly
origin. The v119 replay-only residual remains Oracle plumbing and gains no
reconstruction credit from v120.

The next concrete adjacent candidate is `midboss_defeat_render()` immediately
before the new exact owner: load `0x11A9A..0x11B43`, file
`0x1329A..0x13343`, size `0xAA` / 170 bytes. Its current boundary is
corroborated/authored/unreviewed, and fresh Ghidra constructs the complete near
body `0x21A9A..0x21B43`. The next session should reconcile its callers, three
callees, relocations, and semantic/data ownership before probing natural source.
