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
