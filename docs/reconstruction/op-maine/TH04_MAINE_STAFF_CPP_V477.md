> **Historical packet.** This note records the v477 state. Its statements about
> functions that "remain" are superseded by the live ledgers and the v700/v702+
> exact replays. Use docs/RE_HANDOFF.md and docs/PROGRESS.md for the current
> queue.

# TH04 MAINE staff-roll C++ frontier (v477)

## Scope

After v476, MAINE has 140 target-constrained relocation-order differences. The
remaining `MAINE_01_TEXT` prefix contains seven reconstructed TASM helpers plus
`staffroll_animate()`. The maintained `th04/end/staff.cpp` already documents the
shared state and the `dissolve_put_func(base_left, base_top, distance)` ABI, but
contains no executable bodies.

v477 recovers the first four adjacent helpers as ordinary TC86 C++:

- the radial four-plane dissolve (`sub_AED0`, `0x15D` bytes);
- the first fixed-angle dissolve (`sub_B02D`, `0x117` bytes);
- the second fixed-angle dissolve (`sub_B144`, `0x117` bytes);
- the expanding background rectangle helper (`sub_B25B`, `0x36` bytes).

## Natural compiler shapes

All four functions use existing repository APIs and intrinsics only. No inline
assembly, codestrings, object patching, or relocation-table rewriting is used.

The radial helper's final GRCG disable is the one compiler-sensitive detail.
Calling `grcg_off()` adds a far call, while `_outportb_(0x7C, 0)` selects the
short immediate-port encoding. The target uses the normal DX-port form. The
repo-standard x86real spelling

```cpp
_DX = 0x7C;
_AL = 0;
outportb(_DX, _AL);
```

naturally emits the exact target six bytes `BA 7C 00 B0 00 EE`.

The rectangle helper likewise needs its source dataflow preserved:

```cpp
register int half = distance;
half /= 2;
```

rather than initializing `half` from `distance / 2` in one expression. The two
forms are semantically equal, but the former naturally yields the target
`MOV SI,[BP+4] / MOV AX,SI` register sequence.

## Exact owner

The four C++ bodies form one `MAINE_01_TEXT` contribution of `0x3C1` bytes.
Against the v476 TASM owner, **all 961 raw CODE bytes are exact**; SHA-256:

`1cbbcaa3153f1df6222707cc52fa1b56bb2fd81a2bec984615c3e3e4a38ff4f5`.

TC86 emits one kind-3 FIXUPP stream in high-address-first order. This produces
exactly the target's function-level ordering:

1. the single `sub_B25B` segment site;
2. all 14 `sub_B144` sites in reverse address order;
3. all 14 `sub_B02D` sites in reverse address order;
4. all 14 `sub_AED0` sites in reverse address order.

The TASM remainder begins at `sub_B291`. Existing calls and function-pointer
assignments are redirected only through near/public symbol names at the new
source-level object boundary.

Both A/B cold replays produce:

- MAINE SHA-256
  `dad219be755c32c27f9bb2db4563d64e2c2b1b390b5caeddff8d711756b9130b`;
- MAP SHA-256
  `a4fa9483717816a9efe2977801b3c5a47e5404956e1aefa43bd4d049289e9030`;
- unchanged program-image SHA-256
  `0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1`;
- target-equal 559-site relocation multiset.

Target relocation indices `152..194` are now fully exact. Ordered MAINE
residual drops from **140 to 98** (`461 / 559` same-index).

Private receipt SHA-256:
`c55765670daba54b6a3d006f67fbd9116651f21177fc7a25e8497f07e0dd9cd4`.

## Next work

The remaining MAINE_01 prefix consists of `sub_B291`, `sub_B31E`, `sub_B3AC`,
and `staffroll_animate()`. Target ordering shows another compiler-record
interleave across that contiguous run, so continue recovering those functions
as a natural TC86 owner rather than splitting or permuting relocation records.

## v478 complete staff-roll owner

v478 extends the v477 C++ owner through `sub_B291`, `sub_B31E`, `sub_B3AC`, and
`staffroll_animate()`. The three loop helpers are direct page-flip/dissolve loops
using the existing `graph_accesspage/showpage` macros and the typed
`dissolve_put_func` pointer. All seven helpers through `sub_B3AC` form a
`0x57D` raw-exact TC86 prefix.

`staffroll_animate()` then reproduces the remaining `0x33A` bytes. The only
source-level subtlety is restoring the actual coordinate-pair ordering at calls
to the Pascal helpers; once those pairs are written in their historical order,
the entire **0x8B7 / 2231-byte MAINE_01 staff owner is raw CODE exact**. Raw
SHA-256:
`d30e94167ce85eb5e38ecf6f9dce4f634a9088b7a3f8a9fcb238d5697a0da4d4`.

Existing `sff*.pi`, `sff*.cdg`, and `staff` filename bytes stay in the v470
rest/data owner. Zero-byte `_aSff*` / `_aStaff` aliases expose the same addresses
to TC86 without moving or duplicating data.

Both A/B replays produce MAINE SHA-256
`45aa099ecb29aee883c29ea37c7ad8493ed1871e8b3694a19b63b8e28c331989`,
MAP SHA-256
`4be00e3e72042ef0a2ee38a223f63dea39fbf763cd19232b7321adb416200ccc`,
and unchanged program-image SHA-256
`0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1`.
TC86's three FIXUPP records naturally make target indices `195..250` exact.
Ordered MAINE residual drops **98 -> 42** (`517 / 559` same-index), fully closing
MAINE_01 internal relocation order.

Private receipt SHA-256:
`2b9c51d7497ee2b443a563151c39a61087900e77b29c7d30d43a50066bffead1`.

Remaining MAINE relocation work is now only SCORE_TEXT internal direction (34)
and shared BGIMAGE direction (8).
