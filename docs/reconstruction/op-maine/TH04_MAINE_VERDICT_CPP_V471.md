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
