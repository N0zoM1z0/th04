# TH04 MAIN item lifecycle and scoring semantics (v1248)

## Scope

This batch makes the accepted item-management source readable without changing
its public ABI, translation-unit composition or instruction order. The physical
owner remains `th04-main-items-update-v154`:

- artifact and segment: `th04-main / MAIN_035_TEXT`;
- target file extent: `0x1F21B..0x1F760`;
- size: `0x546 / 1,350` bytes;
- functions: `items_init`, `items_add`, `items_miss_add`, `item_collect`,
  `item_lower_playperf`, and `items_update`;
- accepted target slice SHA-256:
  `a0949b541b517ba4be1cb7afd1094b60017235eefd777630b20c038a030f6531`.

The maintained source still contains the two symbolic `SUB` instructions whose
low-level ownership was accepted in v344. This batch does not reinterpret or
replace them.

## Stage seed and ordinary drops

Stage initialization first fills the 256-byte random ring and then calls
`items_init()`. The item initializer therefore consumes the next direct
process-LCG result, masks it to four bits, and stores it as the initial enemy
drop counter. This draw affects the continuing process LCG and consequently
later Stage fills.

An enemy that requests `IT_ENEMY_DROP_NEXT` advances the byte counter once.
Odd counter values return without allocating an item. Even values select
`ENEMY_DROPS[(counter / 2) % 64]`, so the 64-entry table covers 128 automatic
drop requests before the index repeats. Concrete item types bypass this
counter. Allocation scans the fixed pool from its first entry and uses the
first free slot; a full pool silently discards the requested item.

## Miss drops and shared-ring consumption

`items_miss_add()` attempts to fill five free pool slots. It first chooses the
one big-power position from the shared random ring. It then repeatedly draws a
second position until it differs, but never uses that result. The discarded
draw is still part of the global ring-consumption sequence.

The player's horizontal third selects one of three five-vector spreads. Each
free slot advances the spawn index. Every non-big slot consumes another ring
sample and uses bit 0 to choose power or point. When one life remains, the code
still performs those draws before overriding every spawned type with full
power. If fewer than five slots are free, the function keeps the items it did
spawn and stops at the end of the pool.

## Collection and scoring

The item collector calculates a 16-bit base value and adds a 32-bit value to
`score_delta`. While a Bomb's item-pull latch is active, it doubles the score
delta and stores the same latch with the point-number popup. Maximum point
items and saturated power bonuses select the yellow popup ring; other rewards
use the white ring.

- A point item at or above the 52-pixel line is worth 5,120 before the Bomb
  multiplier. Lower items use `3300 - (subpixel_y / 2)`. Both add the current
  dream score.
- Dream-item count saturates at 7, the last of eight score-table entries.
- Ordinary power at full power increments and clamps the overflow index before
  reading its inclusive 0..42 table.
- Big power at full power adds five, reads the table, and only then clamps.
  Values reaching or crossing index 42 finish with the explicit 2,560-point
  reward and a yellow popup.
- Bomb, 1-up and full-power items update their resident/HUD or shot state and
  use their fixed base rewards.

The big-power statement order matters to reconstruction. If adding five goes
above 42, historical DOS code can form a table address beyond the declared
reward entries before the result is overwritten with 2,560. The portable port
must produce the same final state and reward without performing an
out-of-bounds C++ access.

Collection and missed-item performance are separate byte accumulators.
Collection spends 32 units for one `playperf_raise(1)` call. A missed item
crossing 64 subtracts 48 and calls `playperf_lower(1)`, leaving a 16-unit carry
when it reaches the threshold exactly. Bomb and 1-up misses also apply their
direct larger penalties.

## Motion, removal and pickup

The item-pull latch points every live item's velocity toward the player and
marks that item as pulled. When the latch ends, the next update clears the
stored attraction velocity. Normal item arcs lose horizontal velocity once
vertical velocity becomes nonnegative, then gain one subpixel unit of downward
velocity per frame.

Items outside the horizontal bounds or below the playfield become `F_REMOVE`
and apply the missed-item penalty. Collected items also become `F_REMOVE`.
They are changed to `F_FREE` on the next item update, leaving the invalidation
pass one frame in which to erase the old sprite.

Collection is disabled while `miss_time` is nonzero. Otherwise, two unsigned
16-bit subtractions implement the pickup rectangle. For each axis the code
computes `player + half_extent - item`; an item outside either side produces a
value above the accepted unsigned width, including wraparound on the far side.
The target-supported inline `sub bx,ax` and `sub bx,dx` spellings preserve the
historical instruction encodings.

## Evidence and validation

The semantic baseline is the immediately preceding DOS source, not the target
artifact. The dependency-validated build recompiled 20 C++ roots affected by
the item header plus the item state ASM object. All 21 object pairs have
identical narrowly dependency-timestamp-normalized OMF streams and identical
non-`COMENT` link-relevant records.

The complete products also match:

| Artifact | Size | SHA-256 | Ordered relocations |
| --- | ---: | --- | ---: |
| baseline MAIN.EXE | 199,455 | `cb4c5b667f9a2d5a5c3ef62865fdc926a74a100155068c63e5dfbd019362b70c` | 1,181 |
| semantic MAIN.EXE | 199,455 | `cb4c5b667f9a2d5a5c3ef62865fdc926a74a100155068c63e5dfbd019362b70c` | 1,181 |

Receipts and reports:

- baseline: `.analysis/reconstruction/probes/product-20261003-143850-6a4b1d8d-main/receipt.json`;
- candidate: `.analysis/reconstruction/probes/product-20261003-144214-96dccfe4-main/receipt.json`;
- OMF comparison:
  `.analysis/build/semantic-items-readable-v1248/omf-compare-baseline.json`
  (`8cec7b7b3507b7a5a90157e66de316686e464777ecac510744b6c4ca9c32a478`);
- artifact comparison:
  `.analysis/build/semantic-items-readable-v1248/main-compare.json`
  (`e51b27c76d56729d521571ea86fc01229ae882b2409743a2ade45993a18366a4`).

This is dependency-validated source-to-source preservation. It does not add a
fresh cold target replay, a runtime item trace or a new exactness promotion.
