# TH04 MAINE verdict C++ frontier (v471)

## Scope

v470 recovers the physical MAINE topology and reduces target-constrained
relocation-order differences to 178, but the split `MAINE_01_TEXT` owner still
contains 136 internal ordering mismatches. The maintained source tree already
contains a semantic shell in `th04/end/verdict.cpp` for several functions that
remain executable only in the reconstructed TASM monolith.

v471 starts with the smallest of these, `graph_3_digit_put()`.

## Natural C++ body

The target TASM body is a straightforward three-digit formatter:

- divide a 16-bit value by 100 and 10;
- suppress leading digits unless
  `graph_3_digit_put_as_fixed_2_digit` is enabled;
- build a four-byte gaiji string;
- call `graph_gaiji_puts(left, top, GAIJI_W, string, 14)`.

A direct C++ spelling using the existing `g_EMPTY`, `gb_0`, and
`graph_3_digit_put_as_fixed_2_digit` symbols causes pinned TC86 4.02 to emit the
exact target shape: `ENTER 6`, saved `SI`, the two unsigned divisions, four-byte
stack buffer, and `RET 6`.

Against the already-source-split v470 `MAINE_01_TEXT` owner, the compiler emits
**150 / 150 raw CODE bytes exactly**. Its OMF fixups are:

- kind-3 segment fixup at function offset `0x8D` (`graph_gaiji_puts`);
- kind-1 data-offset fixups at `0x59` and `0x24`.

## Linked owner replacement

The v470 MAINE_01 source has no private-control-flow references crossing this
function boundary. v471 therefore splits it naturally into:

- TASM prefix: `0x8B7` bytes;
- TC86 C++ `graph_3_digit_put`: `0x96` bytes;
- TASM suffix: `0x92C` bytes.

The six suffix calls to `graph_3_digit_put()` must remain `near`; declaring the
new cross-object symbol as a generic procedure would make TASM emit six far
calls and grow the segment by 12 bytes. Preserving the actual near ABI restores
the original total `MAINE_01_TEXT` size `0x1279` exactly.

The maintained C++ declaration uses `uint16_t`, which TC86 naturally mangles as
`@GRAPH_3_DIGIT_PUT$QIIUI`. The reconstructed TASM scaffold used
`@GRAPH_3_DIGIT_PUT$QIIU`; the replay changes only this source-level symbolic
interface in the suffix. Symbol spelling is not executable target data.

Both A/B cold builds produce:

- MAINE EXE SHA-256 unchanged from v470:
  `2e4b7bc9abf039a4a0d105cf141c1959f3e54ce5812066e9d409e69b42a72c3c`;
- MAP SHA-256
  `d15028081d0104843c53802d17c95747b6c7741bdc500ee94af93911e1eda720`;
- program-image SHA-256 unchanged:
  `0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1`;
- complete 559-entry relocation table byte-for-byte unchanged from v470;
- linked 150-byte function SHA-256
  `7149fdd7c6a73eca991d4fb22d3d25f50640228cc368fe64d10ad6ed8a07a85e`;
- ordered relocation residual still 178, as expected: this function contributes
  only one segment relocation, already at the same v470 table position.

Private receipt SHA-256:
`65f60f69038e9f9a4d003e6a463ae977cfbd043ab343f53c5a434d1a5a149828`.

## Next work

Continue with the adjacent verdict helpers already described by the maintained
C++ shell:

- `skill_apply_and_graph_percentage_put()`;
- `graph_fraction_of_million_put()`;

then expand toward `verdict_animate()`. The goal is to recover enough of the
MAINE_01 TASM owner as one TC86 producer to reproduce the target's internal
FIXUPP order naturally, never by permuting relocation records.

## v472 `skill_apply_and_graph_percentage_put()`

The next adjacent MAINE_01 helper spans load `0x1836..0x192A` (`0xF5` bytes).
The maintained verdict semantics already constrain a straightforward natural
C++ body:

- derive a six-digit fraction from `share / total` in 32-bit arithmetic;
- add or subtract that fraction from global `skill`;
- render the integer percentage with `graph_3_digit_put()`;
- render the two fixed fractional digits;
- append the reconstructed fullwidth dot and percent strings through
  `graph_putsa_fx()`.

Pinned TC86 4.02 emits **all 245 raw CODE bytes exactly** from the checked replay
template. The function OMF carries 12 fixups; the two segment fixups are at
function offsets `0xEB` and `0xDB`, naturally emitted high-address first.

### Linked source-level split

v472 refines the v471 TASM suffix into:

- `0x69` bytes of TASM immediately preceding the helper;
- `0xF5` bytes of TC86 C++;
- `0x7CE` bytes of remaining TASM.

The existing private near helper `sub_B81D` crosses the new source-level object
boundary and is therefore made `public near` in the replay scaffold. The two
fullwidth string labels `aBd` and `aBu` live in the v470 rest/data owner; zero-byte
`_aBd` / `_aBu` aliases expose those same addresses to TC86. These are symbolic
boundary adapters only: they emit no new data and alter no linked address or
program byte.

Both A/B cold replays produce:

- MAINE SHA-256
  `db8d82aeb64407563a97a77ae285b477296c8f54cccd4ed743a6352d9e5bd418`;
- MAP SHA-256
  `22fab072431657e7d2ec33fb95fe79e1eb61605a5c985782535d25d0c403029a`;
- unchanged program-image SHA-256
  `0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1`;
- raw helper SHA-256
  `9d2f2eb5690a82e44ce8b6fb87aa573a0c25752a18f136f952879b435a6e61b7`;
- linked helper SHA-256
  `1a4143ca6004cfb50313ba830da1d1490eb15de5c0366ce4392403867c5daa79`;
- target-equal 559-site relocation multiset.

Only relocation indices `254` and `255` change relative to v471. They become
`0xB973, 0xB963`, exactly matching the target-constrained order. Ordered MAINE
residual therefore falls from **178 to 176** (`383 / 559` same-index).

Private receipt SHA-256:
`ebf14039d80a96c8328eb18647e9eadec5381cdfeecd396bcd072878d331cffb`.

## Updated next work

Continue directly with the adjacent `graph_fraction_of_million_put()` helper,
then expand the same TC86 owner toward `verdict_animate()`. Do not hand-reverse
FIXUPP records; the graph3 and skill packets now demonstrate that natural C++
producer recovery changes exactly the target-constrained entries while keeping
all linked program bytes exact.

## v473 `graph_fraction_of_million_put()`

The next helper begins immediately after v472 at load `0x192B` and spans
`0x77` bytes. Its source semantics are the formatting-only subset of the skill
helper:

1. divide a 32-bit value by 10,000 and render the integer part;
2. retain the remainder;
3. divide by 100 and render exactly two fractional digits;
4. append the second reconstructed fullwidth dot string (`aBd_0`).

A direct C++ spelling with `SI`/`DI` register copies of `left`/`top` causes
pinned TC86 4.02 to emit **119 / 119 raw CODE bytes exactly** on the first
bounded source shape. The function OMF fixups are:

- kind-3 segment fixup at `0x6D` for `graph_putsa_fx`;
- kind-1 offsets at `0x6A`, `0x5E`, `0x5A`, `0x4E`, and `0x23`.

v473 splits only the first function from the v472 TASM tail. The existing
`aBd_0` data remains in the v470 rest owner and receives a zero-byte `_aBd_0`
C-linkage alias. The remaining TASM tail declares the new C++ function as a
near external. Neither adapter emits executable or data bytes.

Both A/B cold replays produce:

- MAINE EXE SHA-256 unchanged from v472:
  `db8d82aeb64407563a97a77ae285b477296c8f54cccd4ed743a6352d9e5bd418`;
- MAP SHA-256
  `5edcd404826e00950979ba8194a09b01e75544ce84cd3145fd41cddedd596409`;
- unchanged program-image SHA-256
  `0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1`;
- raw helper SHA-256
  `c375f560be88e44c832501be3d83fc628ebc71a86badcf1a1e933185292610b4`;
- linked helper SHA-256
  `fc3bf1fc7fb56d0130390936ea4562bdc324920a60fec5b2336a9e5a855a4260`;
- complete 559-entry relocation table byte-for-byte unchanged from v472.

The single segment relocation was already in its target-constrained v472
position, so ordered residual remains **176** (`383 / 559` same-index).

Private receipt SHA-256:
`446b292ffda60a758fba5cca5e93c128fefd8d650d55af9768761110972347f8`.

## Updated next work after v473

The three adjacent helpers (`graph_3_digit_put`, skill percentage, and fraction
formatting) are now natural TC86 C++ and linked exact. Continue into the larger
following verdict logic beginning at `sub_B9F2`; that code carries enough
segment fixups that converting it into the same TC86 producer can further
reduce the MAINE_01 relocation residual.

## v474 combined verdict TC86 owner

The next private helpers expose the historical compiler-unit boundary more
strongly than isolated function recovery alone.

### `sub_B81D()`

The `0x69` helper formats `resident->score_last` as an eight-digit gaiji string
with leading-zero suppression, then appends the reconstructed `点` string. A
natural C++ loop is **105 / 105 raw CODE exact** once locals are declared in the
stack order implied by TC86:

1. `digit` (`BP-1`);
2. `past_leading_zeroes` (`BP-2`);
3. the 9-byte gaiji buffer (`BP-0x0C..BP-4`).

No low-level source form is needed.

### `sub_B9F2()`

The `sub_B9F2` calculation is ordinary C++ over `resident`:

- score bonus from starting lives, bombs, turbo mode, and graze;
- item-collection penalty derived in 32-bit arithmetic;
- an `irand()` remainder contribution;
- `×100`, clamp to 1,000,000, then `skill = skill + bonus`;
- render through the v473 fraction helper and append `%`.

The source form `skill = (skill + bonus)` matters: `skill += bonus` lets TC86
shorten the target load/add/store sequence to a memory add. The six-case lives
switch is generated normally by the compiler.

Compiled by itself, the B9 switch table is one byte earlier than the target.
This is **not** a padding-byte reconstruction problem. In the historical owner,
the preceding exact functions have sizes:

- `sub_B81D`: `0x69`;
- skill helper: `0xF5`;
- fraction helper: `0x77`.

Their `0x1D5` subtotal places the B9 table at an odd owner offset. Repo-standard
`#pragma option -a2` then naturally inserts the one target pad before the table.

### First-declaration code-segment rule

A bounded TC86 experiment found one additional compiler rule needed to recover
the physical owner. If `graph_3_digit_put()` is prototyped **before** the
`#pragma codeseg MAINE_01_TEXT`, TC86 binds that function to the default module
segment at its first declaration; its later definition does not move it. The
object then contains two different SEGDEFs and two FIXUPP records.

Removing that pre-pragma prototype and letting the definition be the function's
first declaration produces one single `MAINE_01_TEXT` SEGDEF/LEDATA/FIXUPP
owner containing, in physical code order:

1. `graph_3_digit_put()`;
2. `sub_B81D()`;
3. `skill_apply_and_graph_percentage_put()`;
4. `graph_fraction_of_million_put()`;
5. `sub_B9F2()` plus its aligned switch table.

The resulting CODE contribution is exactly **`0x3FA` bytes**.

### Linked result

`probe_th04_maine_verdict_cpp_v474.py` reconstructs v473 twice, substitutes
that single TC86 owner, keeps the remaining tail in TASM, and relinks MAINE.
Both runs produce:

- MAINE SHA-256
  `9436f51a66156cfda240296ae43972669ec76a952f04276c597081c992324c6a`;
- MAP SHA-256
  `2bfad457813561e365c3c9ef56f5c590eeb36e079865caa45623b0a601761488`;
- unchanged program-image SHA-256
  `0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1`;
- one `0x3FA` `MAINE_01_TEXT` LEDATA/FIXUPP contribution;
- kind-3 LOCAT order
  `3E7, 392, 261, 1EA, 1DA, F8, E3, 8D`;
- target-equal 559-site relocation multiset.

Those eight segment fixups become MZ relocation indices `251..258`, all
**target-index exact**:

`BB70, BB1B, B9EA, B973, B963, B881, B86C, B816`.

Ordered MAINE residual therefore drops from **176 to 170** (`389 / 559`
same-index) while every linked program byte remains unchanged.

Private receipt SHA-256:
`129537a6142cd2c85d2b40085b145f5a140ee750d79f2d00cd2a5458c10476e0`.

## Updated next work after v474

Continue immediately with the following `sub_BB81` verdict routine. Its target
segment relocations at indices `259..273` already form a high-address-first
run, so recovering that function as a natural TC86 owner should be the next
bounded producer test. Do not alter the MZ table or insert switch padding by
hand.

## v475 `sub_BB81()`

The next MAINE_01 verdict function is substantially larger: load
`0xBB81..0xC0F7`, exactly `0x577` bytes. It includes the full verdict page setup,
percentage application, skill normalization, rank/lives/bombs switches, score
clamping, text-file lookup, and final fade/input wait.

A natural TC86 source recovers the complete function **1399 / 1399 raw CODE
bytes exactly**, including both compiler-generated switch tables. Several source
shape details are compiler-observed rather than hand-coded byte controls:

- ternary assignment to `verdict_rank` keeps the value in `AL` across the global
  store and immediate `grEASY` lookup;
- `reinterpret_cast<long &>(skill) /= N` selects the target signed compound
  division load order while preserving the maintained `uint32_t` global ABI;
- `credit_bombs` is naturally a `switch`;
- the end-sequence condition is written in target control-flow order;
- `#pragma option -a2` preserves the target table/alignment surface.

The v475 source split replaces only this function and leaves the final
`verdict_animate()` body as an `0x51`-byte TASM tail. Existing strings and data
labels remain physically owned by the v470 rest/data object and are exposed to
TC86 through zero-byte aliases; the near `sub_BB81` public name similarly only
bridges the new object boundary.

Both A/B cold replays produce:

- MAINE SHA-256
  `10633c16550b1f82cbe15b9ec92abd92aad68649d4ce4257e8b1b7a0c695c161`;
- MAP SHA-256
  `9d831202195630aeeb07842da439c01e81debdb5c8548c8adb12f194fc989332`;
- unchanged program-image SHA-256
  `0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1`;
- raw BB81 SHA-256
  `303a7c12d21ab36596070997e0ed6040c5c1f4cead6a8e873ceb9a3355bcb672`;
- linked BB81 SHA-256
  `8db6709abadd107aca1437a89d4c050af7b6f4a76d325490b5e86f171e9ecc00`;
- target-equal 559-site relocation multiset.

The first TC86 FIXUPP record contributes 15 segment relocations in descending
code-address order, making target indices `259..273` exact. Ordered MAINE
residual drops from **170 to 157** (`402 / 559` same-index). The remaining
`0x51` verdict_animate TASM owner still perturbs indices `274..283`.

Private receipt SHA-256:
`28080aaf0d06e4fc7101ac7e380b118c4beac50e36514d4aad5bdcf1caba412a`.

## Updated next work after v475

Recover the adjacent `verdict_animate()` function into the same TC86 verdict
owner. Once that final `0x51` tail is natural C++, re-measure the remaining
MAINE_01 internal FIXUPP residual before moving on to SCORE_TEXT and BGIMAGE.
