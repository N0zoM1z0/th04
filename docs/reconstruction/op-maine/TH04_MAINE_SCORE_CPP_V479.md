# TH04 MAINE SCORE_TEXT natural C++ frontier (v479)

## Scope

v478 fully closes MAINE_01 internal relocation order. MAINE then has only 42
target-constrained relocation-order differences:

- 34 inside the reconstructed `SCORE_TEXT` owner;
- 8 in shared BGIMAGE.

The residual SCORE owner begins at load `0xC3B2`. Its first private function is
`0x154` bytes long. Although its original symbol name is not target-attested,
its semantics are unambiguous from target code and the maintained scoredat
structures: insert `resident->score_last` into `hi`, shift lower entries, fill
the new name with `gs_DOT`, copy the score digits, and write either `gs_ALL` or
the current stage.

The replay calls this helper `score_insert()` descriptively. That name is not a
historical-source claim.

## Natural C++

The checked template uses ordinary C++ only:

- nested descending score-digit comparisons;
- the same signed integer-promotion behavior present in the target;
- explicit place/name/score shift loops;
- direct `resident` and `hi` field accesses;
- ordinary stage/end-sequence selection.

Pinned TC86 4.02 emits **340 / 340 raw CODE bytes exactly**. Raw SHA-256:

`978e0eb303d2875ed00983f0ea3fc9d48136949afbcd677190a7447eeba2d09c`.

The function has only data-offset fixups; it contributes no segment relocation
whose order can change the 42-entry packed frontier by itself.

## Linked replacement

`probe_th04_maine_score_insert_cpp_v479.py` starts from the retained v478 source
snapshot only after checking its EXE, MAP, response-file owner token, and SCORE
owner identities. Two independent copies then:

1. compile the `0x154` C++ prefix;
2. assemble the unmodified TASM remainder as a separate SCORE_TEXT owner;
3. bridge the later `regist_menu()` call through a same-segment near external;
4. relink TH04 MAINE.

The TASM remainder keeps its exact size `0x774`. Its raw OMF addends are allowed
to differ at normal SCORE_TEXT fixup fields after the physical split; final
linked bytes and the entire relocation table are the fail-closed acceptance
surface.

Both A/B builds produce:

- MAINE SHA-256 unchanged from v478:
  `45aa099ecb29aee883c29ea37c7ad8493ed1871e8b3694a19b63b8e28c331989`;
- MAP SHA-256
  `8bef805e5d3d83081860375d50b5120d978da1486aa632741d14b51f1dc21a2a`;
- unchanged program-image SHA-256
  `0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1`;
- linked helper SHA-256
  `ed7880a5a1cd7aa721c2a95bafb819da15768fd660cf6dd96dbccc9fdc30c093`;
- complete 559-entry relocation table byte-for-byte unchanged from v478;
- ordered residual still **42** (`517 / 559` same-index).

Private receipt SHA-256:
`a4b9e232547cea85c09be6316c1c05a83ff502e2b570366486ad4ce53e07c400`.

## Next work

Continue forward through the adjacent SCORE_TEXT helpers (`sub_C506`,
`sub_C5EC`, `sub_C665`, `sub_C711`, `sub_C7C9`, `sub_C7E3`, registration menu,
and the final EGC helper pair). The goal is to grow one natural TC86 SCORE_TEXT
producer until its internal segment-FIXUPP order matches the remaining 34 target
indices. Do not permute MZ relocation entries.

## v480 score/stage rendering prefix

Two adjacent helpers immediately follow the v479 insertion routine.

### Score renderer (`sub_C506`)

Cross-game comparison with TH05 `sub_B899` reveals the same score-digit renderer
with TH04's two-character layout. The target ABI is naturally expressed as
`pascal (place, unsigned char playchar)`: Borland pushes `place` first and the
byte playchar second, producing the observed `[bp+6]` / `[bp+4]` slots and
`RET 4`.

The exact source-shape controls are ordinary C++ semantics:

- ternary expressions for y/x/pattern-base selection produce the target
  branch-merge stores;
- the rendered playchar is byte-sized, matching the target zero-extension;
- digit arithmetic is written before addition of the pattern base, selecting
  the target AX/DX evaluation order.

TC86 emits **230 / 230 raw CODE bytes exactly**.

### Stage renderer (`sub_C5EC`)

The next helper selects highlight color, derives x/y from `(place, playchar)`,
and draws a two-pixel color-14 shadow plus the actual gaiji. Its natural source
uses a word-sized playchar argument but explicitly compares it to the byte-sized
global `playchar`, matching the target `mov al / mov ah,0 / cmp ax,di` sequence.
TC86 emits **121 / 121 raw CODE bytes exactly**.

### One natural SCORE_TEXT producer

v480 compiles `score_insert + score_put + stage_put` as one TC86 TU. The complete
prefix is **`0x2B3` / 691 raw bytes exact**, SHA-256
`33c15523010ce54850087504a918a1b0a681ba5009470fdc3ffb0b450c006b1b`.

The five segment FIXUPPs are emitted high-address first at local offsets:

`0x2A9, 0x295, 0x224, 0x1FB, 0x1D3`.

After linking, their physical sites are:

`0xC65D, 0xC649, 0xC5D8, 0xC5AF, 0xC587`.

That sequence exactly equals target indices `327..331`. At the current partial
source split the C++ prefix appears before the higher-address TASM remainder,
so the same sequence occupies candidate indices `311..315`; ordered residual
therefore remains **42**. This is expected and demonstrates the producer
direction needed when the rest of the first SCORE FIXUPP record is recovered.

Both A/B runs preserve the full linked program image and target-equal 559-site
relocation multiset. Private receipt SHA-256:
`ff298d52b99f5d020b79239b539889bb830613aea1e03fd6de9d13b5749cf30a`.

Continue with `sub_C665` and the following rendering helpers, extending this
same TC86 owner rather than creating independent final objects.

## v481 name/cursor renderer and four-function prefix

The next SCORE helper (`sub_C665`, `0xAC` bytes) redraws one registration row and
its current-name cursor. Its ABI is target-constrained by the call site:

```cpp
void pascal near name_cursor_put(
    int place, unsigned char rendered_playchar, unsigned char cursor
);
```

The function derives the TH04 left column (`2` / `40`) and row (`6` /
`place + 7`), copies a `128x16` rectangle from page 1 to page 0 through the
private near EGC helper, draws the shadowed name, and reverse-highlights the
current character.

A cross-game source clue resolves the only non-obvious pointer expression:
TH02's preserved `scoredat_name_puts()` uses

```cpp
reinterpret_cast<const char*>(hi.score.g_name[place])
```

for the same gaiji string. Using that spelling in TH04 causes TC86 to generate
the target sequence "compute row offset, then push DS:offset" for both string
calls. The isolated function then matches **170 / 172 raw bytes**; the remaining
two raw bytes are only the relative displacement of its call to the still-later
private copy helper. When split into separate objects the C++ owner carries a
zero addend plus same-segment FIXUPP, and TLINK resolves the exact target call.

Fusing this helper with the v480 prefix yields one `0x35F` / 863-byte natural
TC86 owner. Its raw SHA-256 is
`20e21f50d69da87e08ae964f400c547fdf1df7d4d1338126d8b14766b05d6e80`;
raw differences from the original same-object TASM prefix are only offsets
`0x2F5..0x2F6` (the near-call addend). The linked slice is target exact with
SHA-256
`37e3e6e243f8ec56c7be9f6420d1d70dac54db46e41a4afd409ac9f95ad59e40`.

TC86 emits eight segment FIXUPPs in descending code-address order:

`0x355, 0x32E, 0x319, 0x2A9, 0x295, 0x224, 0x1FB, 0x1D3`.

Their linked sites are
`0xC709, 0xC6E2, 0xC6CD, 0xC65D, 0xC649, 0xC5D8, 0xC5AF, 0xC587`, exactly the
sequence required at target indices `324..331`. Under the partial source split
they currently occupy candidate indices `311..318`, so the global ordered
residual intentionally remains **42**.

Both A/B builds preserve the complete linked program image and target-equal
559-site relocation multiset. Private receipt SHA-256:
`3ee59d7ea4c2c1dfe2dd67607ea04040e5a62ec52fc7e2984c6e180d26e9aa52`.

Continue with `sub_C711` and following higher-address SCORE helpers, extending
this same TC86 owner until the complete first SCORE FIXUPP record is recovered.

## v482 row/table/cursor helpers

v482 extends the natural SCORE_TEXT producer through the three helpers directly
preceding `regist_menu()`:

- the `0xB8` place-row renderer (`sub_C711`);
- the `0x1A` ten-row wrapper (`sub_C7C9`);
- the `0x31` alphabet cursor renderer (`sub_C7E3`).

All three are ordinary TC86 C++ and **raw CODE exact**. The only source-shape
adjustment needed by the largest helper is branch orientation: the target lays
out the ordinary-name path first and jumps to the highlighted path only when
both `entered_place` and playchar match. Spelling the condition as the negative
case followed by `else` reproduces that physical branch order exactly.

Together with v479-v481, the natural C++ prefix now spans `0xC3B2..0xC813`,
exactly **`0x462` / 1122 bytes**. Raw SHA-256:

`836b450754b7c9a7db562235d2858e77afe7c369594db3614749dde81afd81da`.

As in v481, the only raw differences from the original monolithic TASM prefix
are offsets `0x2F5..0x2F6`, the zero addend for the same-segment near call from
the name/cursor helper to the still-later private copy helper. TLINK resolves the
full `0x462` linked slice target-exact; linked SHA-256:

`11bc4d06b392a9ce4ad9b71f791e3f6ff5ca859f041f68c15809718773b7e49a`.

### Producer-order projection

The prefix now emits 12 segment fixups. In the temporary split replay they
occupy candidate indices `311..322` in this site order:

`C7A9, C783, C75A, C709, C6E2, C6CD, C65D, C649, C5D8, C5AF, C587, C80C`.

Those exact sites occur in the target at indices:

`321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 320`.

That is the expected TC86 single-TU shape: the higher-address registration/EGC
code still lives in the following TASM object, so the partial C++ owner is
emitted too early in relocation-table order. Consequently the temporary split
has **43** ordered mismatches rather than v478's 42. This is intentionally not
claimed as packed-frontier improvement; the complete linked program image is
still byte-identical and the relocation multiset is still exact.

Both A/B replays produce candidate SHA-256
`2dac1a8a1cf6ee10d41946c82933112e496cd19f3df354fed11cbc49e50f597b`
and MAP SHA-256
`a3cc85e0d705a96c539f71ba0803d062bf035f9b886004eb2d6c5604ea869c64`.

Private receipt SHA-256:
`39ad6614b958b275de7b5f630a44383e5f2f99045e2ded6c19c78fcca7b53a0b`.

## Updated next work after v482

Recover `regist_menu()` and the final EGC copy helper pair into the **same**
TC86 SCORE_TEXT translation unit. Do not preserve the v482 physical split as a
final topology and do not permute relocation entries. Once the high-address
functions join this prefix, TC86 should be able to emit the complete SCORE_TEXT
segment-fixup stream in target order.
