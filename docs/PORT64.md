# TH04 native x64 port

`port/modern-64` is a separate product based on the semantic DOS source. The
DOS build remains the behavioral reference and keeps its own Borland/TASM
acceptance rules. The portable product uses fixed-width state, ordinary host
pointers and host backends; it does not claim byte equality with PC-98 code.

## Current executable slice

`port64/main.cpp` currently owns the read-only resource path: TH04 HDI FAT12,
PAR directory/decompression and 16-color PI decoding. `port64/view.cpp` owns
the first graphics boundary. It decodes mask-only, combined and opaque CD2 sheets,
composes the recovered OP main, Options and character/shot layouts at 640x400, writes
deterministic BMPs, and opens an SDL2/Linux or Win32/GDI window. The user
supplies the original HDI or loose OP archive at runtime.

`port64/menu_state.cpp` owns fixed-width host state for the six main commands
and eight option rows. It preserves the locked-Extra skip, main/options return
selection, rank/lives/bombs/BGM/SE wrap directions, Turbo toggle and reset
defaults. Host key events call this state instead of embedding transitions in
SDL or Win32 code. `port64/selection_state.cpp` implements the source-observed
two-stage character/shot choice, including per-combination Extra availability.
Game enters it, renders the original selection background and portraits, and
publishes a confirmed choice through the portable OP-to-MAIN contract. Scores,
Music Room, Extra unlock data, descriptions, idle demos, sound and configuration
persistence remain to be migrated.

`port64/application_state.cpp` now owns the first executable-handoff boundary.
It replaces DOS process/segment mechanics with one fixed-width resident object
and guarded `OP -> MAIN -> MAINE -> OP` state transitions. Normal and Extra
starts preserve their configurable/fixed resources; demos retain the original
four stage/character/shot contracts and the split live/resource stage fields.
MAIN publishes score and run counters before either returning to OP or entering
MAINE. MAINE classifies Good/Bad, Extra and score-only routes from the original
one-byte sentinel values, retaining the Good/Bad script selector, before
returning to OP. A generation counter marks each fresh executable-local
resource lifetime. No gameplay or score-file I/O is implied by this
control-plane slice.

The first gameplay contract is separated into
`src/main/bullet/group_types.hpp` and `port64/bullet_geometry.cpp`. Both DOS
and portable sources share the numeric group and 8-bit clockwise angle
definitions. Portable persistent group storage is explicitly one byte.
Deterministic tests cover odd/even spread order, accumulator wrapping, rings,
aim plus template rotation, directional sprite cels and rejection of a zero
ring count. Speed state remains outside this bounded slice.

`port64/random_lcg.cpp` owns the process-local 32-bit generator. Its unsigned
update reproduces TC4J's modulo arithmetic and 15-bit result without depending
on host `long` width or signed overflow. `application_state.cpp` separately
stores the resident OP menu-frame accumulator, resets local state to 1 for a
new modeled executable, copies the resident seed into MAIN, applies demo seed
318, and re-seeds MAINE only when verdict calculation begins. This retains the
Bad/Good versus Extra/score-only save-order distinction.

`port64/random_ring.cpp` owns the following random-state boundary. One
`SharedRandomRing` replaces both historical accessor copies and preserves
their shared call order. Its contract covers the descending 256-byte fill,
overlapping little-endian word samples, low-byte-only cursor increment,
AND/MOD reduction after consumption and the index-255 sample whose high byte
is the pre-increment cursor value `0xFF`. The implementation synthesizes that
boundary value without an out-of-bounds C++ load. A zero MOD divisor throws
after consuming the sample, providing a defined host failure at the same state
boundary as the original 8086 `DIV` exception. Its production fill now consumes
`Lcg32` directly. Connecting direct spark/item calls and the remaining gameplay
sites stays separate work.

`port64/item_system.cpp` is the first fixed-pool gameplay state built on those
random contracts. It preserves the byte automatic-drop counter, every-second
64-entry table lookup, first-free pool allocation, miss-drop spread selection,
the discarded distinct-slot draw, conditional per-item type draws and the
last-life override order. Its scorer uses explicit 8/16/32-bit state for power,
dream, point totals and performance accumulators. The full-power big-item path
branches before table access while retaining the historical final cap of 42,
2,560-point reward and yellow popup, so x64 never reproduces the DOS
pre-clamp out-of-range read. The pickup helper performs the historical wrapped
unsigned 16-bit rectangle test without host signed overflow. The live `item_pool` now connects that scorer to 32 entities, preserving
move-before-gravity, pull cancellation, previous positions, pre-clamp collision
coordinates and next-frame reclamation. Per-slot effects retain pickup order;
HUD/audio adapters remain separate.

`main_state` joins player-before-item updates to the existing process LCG and
shared ring. Q12.4 motion uses explicit signed wrap and arithmetic floor shift;
`player_motion` preserves aligned/diagonal speed, Shift division, the opposing
chord retry latch and playfield bounds. BFNT decoding loads MIKO/MARI player
cels and item cels from MIKO16, using the ST00 stage palette. The sprite base
is 16 within MIKO16, because the preceding MIKO32 sheet owns 24 patterns.
A completed HDI-backed Game selection now starts a timed SDL/Win32 MAIN scene
with held-key input. Host timers update at a nominal 17,730,496 ns step and
limit catch-up to four frames; this is a chosen bring-up cadence, not an
independent original-timing measurement. The scene is a black playfield with a
movable player; stage VM, shots, enemies, Bomb/death, tiles and HUD remain absent.
`--main-screenshot` alone injects seven item types for a deterministic 60-frame
fixture, preserving an honest distinction from ordinary interactive gameplay.

## Verified builds

The same source builds and runs as Linux ELF64 x86-64 and Windows PE32+
x86-64. Both decode the attested HDI fixtures with packed-pixel FNV32 values
`232AE649` and `EDFA0534`. Both produce the same title BMP, SHA-256
`b52ea8615865bfc11945fbe23828b7c391d8424c998062a8abfb5d62b4b31d2a`.
Both also produce the same default Options BMP, SHA-256
`a064338b0cfb89f7e418a85ab6bc84a7ea5ef835e4ca995b68772e0aef368185`.
The character and shot-stage BMPs are respectively
`c1a795a36c2603004fed9309200af833ff8718434b4ba8de2c0977eb2acda199`
and `12aa7616f49283462bb7c9dd41c3198fd66865a758da79ad24cf63de817ee438`.
The automated Game/character/shot path then produces the MAIN handoff frame
`0b2c0f8cebb9e1c0e600de3bee29feb8f225efb5b798cb3a387b6c5538bb55c5`.
Both portable contract executables report `pointer_bits=64`, `angle_bits=8`,
`menu_state=OP`, `handoff_state=OP_MAIN_MAINE`, `selection=OP` and
`randring=SHARED_OVERLAP`, `lcg=PROCESS_LOCAL32` and
`items=FIXED_WIDTH_SAFE`.
Both live contracts also report `motion=Q12.4 player=HELD_KEYS items=32
sprites=BFNT pointer_bits=64`. Their live fixture agrees across both products:
`0fe4fac7633580ec1efb85ad3a72f1f7dc6d5d9e0e34703083c21d6ba9076351`.
A separate GNU x86-64 build passes both contracts and the full resource smoke
with undefined-behavior and array-bounds instrumentation enabled.

An independent Unicorn replay of original MAIN `main_01 0AAF:5DA8`
(load segment 2000, file 0x12098, 131 bytes) agrees with both native products
for all 256 direction masks. This is target CPU evidence for isolated
`player_move`, with initially zero velocity, not full `player_update`.
The 321 independently generated trig constants separately agree with the
maintained DOS source tables. Actual SDL and Wine/Win32 window probes check
held Right, Shift slowdown and Esc; they do not measure native Windows FPS.

The current verification receipt is
`.analysis/port64/verification-live-v1251/receipt.json` (SHA-256
`efab4b04f99dbd71e2a80070bb531fd3b053edfd40643f51acb65b8a967337a6`),
with source manifest
`94739f8afd56f471b0435f4134d3860dafbff9b992482d830520ff3ebc1f90b5`.
Bounded target-movement receipts and window observations are under
`.analysis/port64/live-v1251/`; sanitizer evidence is under
`.analysis/port64/ubsan-live-v1251/`. These private receipts record their own
product hashes and scope limits. The source manifest is recorded by `verify.py`.

Replay the complete cross-build check with:

```sh
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux \
  --windows-dir .analysis/port64/windows \
  --hdi .analysis/runtime/images/zun.hdi \
  --output .analysis/port64/verification/receipt.json
```

The private receipt records executable format and hashes, the source manifest,
resource outputs and the HDI digest. It never copies game assets into the
repository.

## Migration order

Semantic work stops when the current subsystem is clear enough to port and
verify. The completed motion/item slice required no further DOS-source edits.
Next, connect stage VM and enemy entities to the frame loop, then port shots,
bullets, scrolling/tile maps, HUD, death/Bomb transitions and audio. Add saved
configuration and route-level gameplay/Ending/score checkpoints as those
systems become runnable. Full gameplay is the completion condition, not an
exhaustive source-renaming pass.
