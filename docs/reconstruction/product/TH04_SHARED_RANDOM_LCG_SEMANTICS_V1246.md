# TH04 shared process-local LCG semantics (v1246)

## Scope

This batch documents the 32-bit linear congruential generator implemented by
`src/shared/runtime/random.cpp` and the seed transfers that connect ZUN.COM,
OP.EXE, MAIN.EXE and MAINE.EXE. The source edit renames one local value and
adds comments at the transfer sites. It does not change a public symbol,
resident layout, translation-unit boundary, calling convention, instruction
order or accepted unit extent.

This generator feeds the shared random ring documented in
[`TH04_MAIN_RANDRING_SEMANTICS_V1244.md`](../main/TH04_MAIN_RANDRING_SEMANTICS_V1244.md),
but the two pieces have different lifetimes: the LCG lives for one executable
process, while MAIN refills the byte ring once per stage session from that
continuing process state.

## Generator contract

TC4J gives `long` and `unsigned long` a width of 32 bits. The maintained source
stores the state in a signed `long`, but explicitly converts the old state to
`unsigned long` before the update:

```text
next_state = (uint32(old_state) * 0x015A4E35 + 1) mod 2^32
random_seed = bit_pattern_as_signed_long(next_state)
result = (next_state >> 16) & 0x7FFF
```

The unsigned conversion and arithmetic are part of the contract. They retain
the low 32 bits even when the stored signed value crosses `LONG_MAX`. `irand()`
returns bits 16 through 30 of the new state as a nonnegative 15-bit value; it
discards both the low 16 state bits and bit 31.

Calculated vectors for a portable contract test are:

| Initial state | Step | New state | Return value |
| --- | ---: | ---: | ---: |
| `1` | 1 | `0x015A4E36` | 346 |
| `1` | 2 | `0x8082A52F` | 130 |
| `1` | 3 | `0xAAE684BC` | 10,982 |
| `318` | 1 | `0xAE2D25D7` | 11,821 |
| `318` | 2 | `0xF5765784` | 30,070 |
| `318` | 3 | `0x28925655` | 10,386 |

These vectors are direct calculations from the maintained expression. They are
useful regression inputs, not an independent target or runtime Oracle.

## Process and seed lifecycle

`random_seed` is ordinary initialized data in each executable. Loading a new
OP, MAIN or MAINE process therefore creates a separate state whose default is
1. The resident block contains another signed 32-bit value named `rand`; it is
a persistent seed source and is not an alias for any process's live LCG state.

| Owner | Seed behavior |
| --- | --- |
| ZUN.COM | Clears the resident bytes when it creates the 256-byte block, so `resident->rand` initially starts at zero. |
| OP.EXE | Increments `resident->rand` once per title-menu frame. OP's own Music Room, logo, and score-codec `irand()` calls advance OP's separate process-local state, initially 1. |
| MAIN.EXE | Copies `resident->rand` to `random_seed` once after startup. Ordinary Stage transitions remain in the same process and do not copy it again. Every ring fill and direct gameplay `IRand()` call shares and advances this state. |
| MAIN demo | Replaces the MAIN state with 318 before the first demo Stage runtime initialization, making the recorded sequence independent of title-menu wait time. |
| MAINE.EXE | Begins with its own default state 1. `sub_B9F2()` re-seeds it from `resident->rand` while calculating the verdict bonus. MAIN never publishes its advanced state back to the resident block. |

Route order is observable in MAINE. Bad and Good Ending routes render the
verdict before score registration, so the later ten-section score-file re-key
continues from the resident-derived MAINE state. Extra and score-only routes
register first; their score-file keys start from MAINE's default state 1, and
the verdict re-seed occurs afterward. Within `sub_B9F2()`, the random bonus draw
is conditional, but the assignment to `random_seed` is unconditional.

MAIN's calls must remain in one stream. `randring_fill()` consumes 256 results
at every Stage runtime initialization. Spark initialization and item-drop-cycle
selection also call `IRand()` directly during play, so their call counts affect
later direct results and the next Stage's ring contents. Splitting these users
into subsystem-specific generators would change gameplay even if each local
generator used the same formula.

## Portable contract

The native x64 port should represent both the resident accumulator and each
process-local generator with explicit `uint32_t` storage. A portable step is:

```cpp
state = (state * UINT32_C(0x015A4E35)) + UINT32_C(1);
return static_cast<uint16_t>((state >> 16) & UINT32_C(0x7FFF));
```

This avoids signed overflow and avoids the platform-dependent width of `long`
(64 bits on common Linux x64 ABIs and 32 bits on Windows x64). Process
replacement should explicitly construct a new local state at 1, then perform
the same product-specific seed transfer. The port must not substitute the host
C library `rand()`, reset MAIN at every Stage, automatically publish MAIN state
to the resident object, or merge OP's menu-frame accumulator with OP's own LCG.

## Evidence and validation

The lifecycle description is source-derived from the maintained product graph:

- ZUN.COM clears the resident block before `cfg_init()`.
- OP increments the resident seed in its frame loop.
- MAIN copies the seed once, applies the demo override, and calls the generator
  through the ring fill and direct gameplay consumers.
- MAINE's route order places `sub_B9F2()` before or after registration as
  described above.

The compiler regression uses the immediately preceding semantic source as its
baseline. Three objects per product cover the changed source and each builder's
fresh dependency control. All nine pairs have identical narrowly
dependency-timestamp-normalized OMF streams and identical non-`COMENT`,
link-relevant record streams.

The complete products also equal the pre-edit baseline:

| Artifact | Size | SHA-256 | Ordered relocations |
| --- | ---: | --- | ---: |
| MAIN.EXE | 199,455 | `cb4c5b667f9a2d5a5c3ef62865fdc926a74a100155068c63e5dfbd019362b70c` | 1,181 |
| OP.EXE | 79,372 | `ef37e6e890c4bfcbb65eb57a7087e4298382b7ccb4082b4092e2ced8129318d5` | 817 |
| MAINE.EXE | 72,246 | `7bfd7fd594377d03c070c4be8335feb9d3451f2b8dcb8bfbe9dafa95915b542f` | 663 |

Final native receipts:

- `.analysis/reconstruction/probes/product-20261003-142054-88ea1305-main/receipt.json`
- `.analysis/reconstruction/probes/product-20261003-120224-bfbb4b93-op/receipt.json`
- `.analysis/reconstruction/probes/product-20261003-141828-f31d4087-maine/receipt.json`

Comparison reports:

- `.analysis/build/semantic-lcg-readable-v1246/omf-compare-baseline.json`
  (`1ce0cb86f7353242a74ea97ec55d3fb5df102cc66083fe014c11a7ba89503dc4`)
- `.analysis/build/semantic-lcg-readable-v1246/main-compare.json`
  (`acfbcc6b08313047c862115f94007c73a8b475a63e5999a1c9e0000b76dbd723`)
- `.analysis/build/semantic-lcg-readable-v1246/op-compare.json`
  (`f9628ccba50fc13aceac749a436f8beef35c1b5cf1b3790c599974fcebf6ea77`)
- `.analysis/build/semantic-lcg-readable-v1246/maine-compare.json`
  (`0f341bbe9766d784beb298a136d6f0bfe78caa55c389e99d5d7cb5784518a0c5`)

This is dependency-validated source-to-source preservation. It does not add a
fresh cold target replay, independently observe runtime randomness, or change
any historical exact state.
