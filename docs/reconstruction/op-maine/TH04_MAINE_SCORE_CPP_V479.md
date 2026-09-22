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

## v483 `regist_menu()` compiler frontier

The next SCORE_TEXT function is the `0x39C`-byte registration menu at load
`0xC814`. Cross-game TH02 source supplies the high-level registration state
machine; TH04 target code fixes the game-specific PI background, dual-character
score loading, slow-mode warning, clear-bit update, input handling, and alphabet
layout.

A natural TC86 source reproduces the target function shape extremely closely:

- exact `ENTER 0xA` frame and SI/DI allocation;
- exact PI/sound/rank/playchar setup;
- exact 3x17 alphabet initialization;
- exact four-direction cursor movement and wrapping;
- exact 9-entry character switch table;
- exact name editing, bomb/cancel handling, save/wait/cleanup flow;
- exact total function size `0x39C`.

The A/B replay fixes the compiler frontier at **920 / 924 raw CODE bytes**.
Candidate SHA-256 is
`d9481b34f6872fc507a9053549ad1e05a2a0dbecbab40a5809358d5693becb02`;
the v478 reference function SHA-256 is
`e8fdf2245ad5a741ff86603daf612ecdd36625e724f34b6f2d807ed9ae943340`.

Only four raw bytes remain different, all at function offsets
`0x345, 0x346, 0x348, 0x349`. They are one zero-test instruction:

```text
candidate: A1 ?? ?? 0B C0    MOV AX,[key_det] / OR AX,AX
reference: 83 3E ?? ?? 00    CMP word ptr [key_det],0
```

The following `JZ` and otherwise-redundant `JMP` are already exact in the best
source shape. Structured `if(key_det == 0)` produces the direct-memory `CMP` but
TC86's `-O` jump optimizer removes the `JMP`; a one-case `switch(key_det)` keeps
the target double jump but selects `MOV/OR`.

### Bounded negative compiler surface

Local probes intentionally kept the remaining 920 exact bytes fixed while
checking only plausible compiler/source mechanisms. None closes the four-byte
site without perturbing already-exact code:

- ordinary `if` / goto / do / while / for / tail-merge spellings;
- signed, unsigned, union, struct, bitfield, lvalue, and volatile switch forms;
- empty and meaningful repeated-scope variable declarations;
- whole-function `-O-`, `-O- -y`, and global `-Z-`;
- normal `-O -y` and local `#pragma option -Z-`.

This matches the repo-local TC86 research: `-O` performs jump merging, while
`-O- -y` provides only a different partial optimizer surface. Neither matches
this function as a whole.

The complete natural C++ prefix now spans `0x7FE` bytes. Relative to the v478
TASM owner it has only six raw differences: the four bytes above plus the known
`0x2F5..0x2F6` same-segment near-call addend that TLINK already resolves exact.
The remaining assembly tail is `0xCA` bytes: `_egc_start_copy_inlined` plus the
private EGC rectangle-copy helper.

Private receipt SHA-256:
`ea6867099f1ecdb24a40e701132fb9be8470d96679854257c0f8826965f21558`.

**No exact or packed-file credit is granted by v483.** Continue the EGC tail and
SCORE record-ownership analysis independently; do not hand-encode the remaining
zero-test instruction.

## v484 `score_rect_copy()`

The final SCORE_TEXT function at load `0xCBF3` is a `0x86`-byte EGC-assisted
rectangle copy helper. Its preceding `0x43` EGC-start routine remains assembly-
owned in this packet; only the rectangle loop moves to natural C++.

The checked source computes the VRAM byte offset, converts width to 16-dot
words, walks rows/words, toggles the transfer port around a VRAM read, writes the
captured word back, and finally disables EGC. No inline assembly or emitted
opcode bytes are used in the recovered function itself.

Pinned TC86 emits exactly `0x86` bytes. Relative to the old same-object TASM
body, raw offsets `0x0A..0x0B` differ only because the call to the preceding EGC
start helper is now an external same-segment near call with a zero addend plus
FIXUPP. The retained TASM SCORE head similarly differs at only offsets
`0x2F5..0x2F6`, where the earlier name/cursor helper now calls the C++ rectangle
copy through an external same-segment symbol. TLINK resolves both forms to the
same final machine code.

Both A/B replays produce:

- MAINE SHA-256 unchanged from v478:
  `45aa099ecb29aee883c29ea37c7ad8493ed1871e8b3694a19b63b8e28c331989`;
- MAP SHA-256
  `162d50edd4600047c1cb922a49c842a5ba40adedd091c56395bc0781b70654a3`;
- unchanged program-image SHA-256
  `0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1`;
- natural C++ raw helper SHA-256
  `d0b6cdfac6dbbf9f4ac811380e98d216bec149b7c8536b3a8a4831bfdf9e50c4`;
- target-exact linked helper SHA-256
  `86b8046d73b79655f913d1b7f62c34db3a3f6d43ffc168b9a4c855e78b7d7d2f`;
- all 559 relocation entries byte-for-byte unchanged from v478;
- ordered residual still **42** by design.

Private receipt SHA-256:
`cef7d44132d366839f13d267ba1838e9e8527014fbdc5e53787355ad637feea4`.

### Remaining SCORE tail

Only two source frontiers remain inside the reconstructed SCORE owner:

1. `regist_menu()`, already narrowed by v483 to one 4-byte zero-test peephole;
2. the preceding `0x43` EGC-start helper, where the current natural C++/intrinsic
   form is 66/67 bytes because TC86 emits `XOR AX,AX` instead of target
   `MOV AX,0`.

Neither is credited as exact yet. Once both join the same TC86 producer as the
v482 prefix, re-measure the 34 SCORE relocation entries; do not permute MZ
records.

## v485 complete EGC tail

v484 left the preceding `0x43` EGC-start helper one byte short: ordinary
`_AX = 0` is strength-reduced by TC86 to `XOR AX,AX`, while the target contains
`MOV AX,0`.

The repository already contains the intended legal source-level mechanism in
`decomp.hpp::keep_0()`. Its comment explicitly names pseudoregister zero
assignments as the use case, and TH05 independently uses

```cpp
outport(EGC_ADDRRESSREG, keep_0(0));
```

inside `th05/formats/pi_cpp_2.cpp` for the same EGC register. This is therefore
cross-game producer evidence, not a target-specific emitted-opcode workaround.

Replacing only the zero write with `keep_0(0)` makes the EGC-start helper
**67 / 67 raw CODE bytes exact**. Compiling it in the same TC86 TU as the v484
rectangle-copy helper yields the complete final SCORE code tail, `0xC9` bytes,
byte-for-byte identical to the original owner:

- raw/linked tail SHA-256
  `6b55b254101a12f91c53798f8e8838896de7b12b7591b4d9368f3bdd5a0d314d`
  at object level;
- linked target slice SHA-256
  `c97000dbc25f0ea6e58724b0f3b32739ec66e5bb9d181b687433c4a0b8b988b9`.

The v485 A/B replay keeps the original one-byte segment pad as a separate
assembly contribution. The retained SCORE head differs raw only at offsets
`0x2F5..0x2F6`, the expected same-segment near-call addend from the earlier name
renderer to the now-external C++ copy helper. TLINK resolves the full MAINE image
byte-identically and preserves all 559 relocation entries in the same order.

Both runs produce:

- MAINE SHA-256 unchanged from v478:
  `45aa099ecb29aee883c29ea37c7ad8493ed1871e8b3694a19b63b8e28c331989`;
- MAP SHA-256
  `5c882d63dfe20686e566a9fd3def7b4a4c5b914d4d1108b3dfd227c0da00c682`;
- unchanged ordered residual **42** (`517 / 559` same-index).

Private receipt SHA-256:
`5a0eb9865656ea3315dcd3b2cfc7c7a9f9a16c0ee10af041a75680eff5f8db33`.

### SCORE frontier after v485

Every SCORE_TEXT helper except `regist_menu()` now has a linked-exact natural
C++ reconstruction. v483 has already narrowed `regist_menu()` to one four-byte
zero-test peephole (`MOV AX,[key_det] / OR AX,AX` versus target
`CMP word ptr [key_det],0`). Because `keep_0()` is also documented for
zero-comparison peepholes, test that mechanism next before reopening broader
optimizer/source-shape searches.

## v486 complete SCORE_TEXT C++ producer

The final `regist_menu()` four-byte compiler frontier is closed with the
repository's existing `optimization_barrier()` mechanism. The target repeat-key
branch contains a direct memory zero comparison followed by both `JZ` and an
otherwise-redundant `JMP`. Ordinary structured C++ lets TC86 fold that jump;
placing `optimization_barrier()` only in the nonzero arm preserves the original
control-flow shape without emitting any machine-code bytes. `regist_menu()` then
compiles **924 / 924 raw bytes exactly**.

Together with v479-v482 and the v485 EGC tail, the complete executable
`SCORE_TEXT` body is now one natural TC86 translation unit:

- code size: `0x8C7` / **2247 bytes**;
- raw SCORE CODE SHA-256:
  `99b6809c3ccac9d8f4257609132ec19fd0625fe12be0a95b54b1e6b5df718f17`;
- linked SCORE slice SHA-256:
  `491222d0f3c105e253ea4d6daf8546ec338b35ff9ad617abf76020bd60c2bda3`;
- linked MAINE program-image SHA-256 remains
  `0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1`.

Five existing SCORE strings remain physically owned by the v470 rest/data
object and are exposed to TC86 only through zero-byte C aliases. The historical
one-byte SCORE segment pad remains a separate assembly contribution. Neither
changes any executable or data address.

### OMF record frontier

This packet intentionally **does not grant packed relocation-order credit**.
The exact C++ object emits three target-relevant kind-3 FIXUPP records:

1. `R1` — 11 sites from the first `0x400` LEDATA;
2. `R2` — 24 sites from the second `0x400` LEDATA;
3. `R3` — 1 site from the final `0xC7` LEDATA.

Current TLINK order is:

`R1(11) -> R2-prefix(14) -> R2-suffix(10) -> R3(1)`.

The packed target requires:

`R2-suffix(10) -> R1(11) -> R3(1) -> R2-prefix(14)`.

Thus the full-source candidate has 44 ordered differences: all 36 SCORE entries
plus the independent 8-entry BGIMAGE block. The relocation-site multiset remains
559/559 exact.

Two natural surfaces are already closed:

- moving the complete SCORE contribution to several response-file positions
  leaves its **relative 36-site SCORE order unchanged** (while globally moving
  the whole block, as expected);
- TC86 `-y` line-number metadata keeps the exact same LEDATA/FIXUPP record
  topology while preserving code; `-v` changes code and is therefore not a
  candidate metadata-only explanation.

The remaining SCORE problem is therefore not source code. It is recovery of the
historical OMF/library record topology that caused TLINK to produce the target
cross-record interleave. Do not split functions at relocation offsets or edit MZ
entries to manufacture this sequence.

Both v486 A/B replays produce:

- EXE SHA-256
  `eba75be94f3e43776b5206a10ab3b9818eefc0308d9d87b7c148eca8f6b83397`;
- MAP SHA-256
  `57286cfe662899fd1889c3caca5d7e0cb38f89072fc40d462ad3ad3a6b01eaac`;
- 515 / 559 same-index relocations;
- ordered residual **44**, explicitly non-promoted.

Private receipt SHA-256:
`7b5e5863dc6f1310de87fe38967a55e09f1529324c39f999d904fca398c16af9`.
