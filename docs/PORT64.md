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
independent original-timing measurement. The scene now has a
movable, shooting player and real STD-scheduled enemies over the original Stage 1
scrolling background; enemy bullets, bosses, Bomb/death, later-stage visuals and
HUD remain absent.
`--main-screenshot` alone injects seven item types for a deterministic 60-frame
fixture, preserving an honest distinction from ordinary interactive gameplay.

`stage_background` owns the MPN planar tiles, MAP section rows and STD order/
speed streams. It expands MPN pixels once instead of re-reading four planes
per frame, translates the original image VRAM addresses into host tile IDs,
and owns the 25x24 visible ring. Initial STD sections are filled bottom-first;
the pre-advance display origin and byte fractional accumulator retain DOS
ordering, including the initial speed-chunk length and the zero terminator.
The host redraws this software background instead of emulating EGC copies.

`player_shots` adds all four routes and ten power levels using fixed 8/16-bit
state and a 68-slot pool. It retains trigger/release cadence, Reimu volley
cycle resets and homing, Marisa option-laser startup/ring order, descending
allocation, allocation-dependent shared-ring draws, delayed reclamation, hit
animation and the per-frame collision cache. Hit processing retains signed
velocity division, progressively reduced damage, Bomb/boss division before
laser damage, unsigned rectangle bounds and spark phase. Sparks are requests
to a future adapter, so this slice does not consume their random draws or
render them. Sound and spark effects remain absent.

MAIN now dispatches STD waves, then updates player/shots/enemies/items in original order. SDL and Win32 sample
held Z; rendering uses original MIKO16 shot/options/ring cels and laser masks,
with reverse pool drawing over the Stage 1 background. The explicit
`--shooting-screenshots DIR` fixture collects a full-power item before firing
66 frames on each route, then writes four BMPs to an existing directory.
Ordinary windows start at power 1 and do not inject items/enemies.

Independent relocated original MAIN CPU replay covers 4,072 checkpoints:
2,216 producer cases, 512 trigger decisions (every timer byte and both key
states), 64 lifecycle states, 640 hit tests and 640 repeated-hit tests against
the same cache. It executes the original math/random callees; only spark calls
are intercepted and their arguments compared. Scope is `main_01 0AAF`, load
segment 2000 with isolated initialized DGROUP at DS 8000. Trigger code spans
`6092..60D6` and stops before dispatch; update is `59C6`, hittest `5AC9`, shot
producers start at `2F5F` (Marisa) and `487C` (Reimu). The pinned target retains
its `candidate-local-attested` provenance gap. No new byte-exact claim follows.

A separate negative control observes reads beyond the original 68-slot pool
when the last free slot is followed by another allocation request. Host
allocation instead stops at capacity. All valid scoped controls agree on Linux,
Wine/Win32 and GNU UBSan/bounds; all four full-power BMP hashes agree across
hosts. Original BFNT pixel matching in both character windows confirms multiple
held-Z volleys and complete departure after release. Earlier UI/movement/item
fixtures retain their hashes. Native Windows host pacing remains untested.

`stage_program` parses all seven original STD script/wave chunks, replacing
near pointers with checked script handles. Waves dispatch only on their exact
16-bit frame; midboss suppression still advances the original cursor. Opaque
marker bytes vary between stages and are skipped without a magic-value check.
Zero-count and out-of-extent malformed records are rejected instead of
reproducing DOS underflow/out-of-range paths.

`enemy_system` implements the 52 valid opcodes with explicit names and widths,
same-frame setup chains, inclusive N+1 timed movement, loops, clipping,
performance-dependent autofire, shared-ring spawn randomness, the 32-slot pool,
shot/cache damage, kill scoring/drops, homing selection and collision requests.
Damage flash and animation advance once per simulation frame, independently
of host repaint messages. Original MIKO32 and ST00 BFNT cels draw before shots.
The scroll owner now publishes the preceding update's Q12.4 delta even when
its helper stops the stream in that call; enemy scroll movement consumes it.

Fire, sound, tile-ring and spark requests dispatch synchronously. Only item
drops are connected to the live pool in this slice. Bullet tuning/allocation,
spark random draws and sound are not modeled yet, so natural shared RNG will
change when those adapters are added. Player collision records a hit but
player death is still absent. This is a runnable Stage 1 enemy/shot slice,
not a complete or invulnerable patched version of the native game.

Original relocated MAIN CPU comparison covers 9,414 VM vectors, 896 enemy
hit/lifecycle/render cases, all seven STD schedules (1,188 waves, with explicit
midboss skip controls), and 12,600 Stage 1 enemy update/render frames across
Easy, Normal and Lunatic. It executes VM/motion/RNG, spawn, scheduler, enemy
update, shot hittest and enemy renderer code. Near script pointers are
normalized to handles; ordered intercepted requests and draw coordinates/cels
are compared. Graphics pixels, intercepted callees' effects/RNG, route-level
boss behavior and natural host timing are excluded. Entries: `MAIN.EXE
main_03 13A9:1B4D` VM, `4263` spawn, `4341` STD, `43C9` update, and
`main_01 0AAF:5C23` renderer; load segment `2000`, DS `8000`, ES `9000`.

`--combat-screenshots DIR` runs 1,200 actual Stage 1 frames with held Z and
normal initial power for each character. It injects no enemies/items/score;
each run kills 26 enemies, accumulates score delta 5,761 and reaches power 7.
Linux and Wine-hosted Windows BMPs/counters agree. The prior fixtures retain
their hashes; GNU UBSan/bounds also passes. The background CPU oracle now
compares the published scroll delta across all 6,715 frames, including stopping.
Cross-host receipt: `.analysis/port64/verification-enemies-v1254/receipt.json`.
Scoped CPU receipts: `.analysis/port64/enemies-v1254/cpu-{linux,windows,ubsan}-final/receipt.json`.
No DOS source, exact acceptance state or target bytes changed.

The oracle derives hook offsets from `address - CS*16`. A Unicorn 1.0.2
negative control executes one NOP at load address `33B90` with CS `33A9`:
inside the hook, `UC_X86_REG_IP` reports `3B90`, while the CS-relative offset
is `0100`; after execution IP is `0101`. Dispatching a callee hook by that
raw register silently misses it. Receipt:
`.analysis/port64/enemies-v1254/hook-ip-negative.json`. This is an emulator API
observation, not evidence of a TH04 VM defect. The corrected CPU comparisons
above run the original callees and record the actual intercepted boundaries.

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
`a6341ebde93ab5424a263f3b9393e6654bbada0e215dc119e324529e4f7a3524`.
A separate GNU x86-64 build passes both contracts and the full resource smoke
with undefined-behavior and array-bounds instrumentation enabled.

An independent Unicorn replay of original MAIN `main_01 0AAF:5DA8`
(load segment 2000, file 0x12098, 131 bytes) agrees with both native products
for all 256 direction masks. This is target CPU evidence for isolated
`player_move`, with initially zero velocity, not full `player_update`.
The 321 independently generated trig constants separately agree with the
maintained DOS source tables. Actual SDL and Wine/Win32 window probes check
held Right, Shift slowdown and Esc; they do not measure native Windows FPS.
Both characters also pass window
checks over the scrolling background using independent original BFNT pixel
matching. The separate background oracle executes original initial fill
`main_01 0AAF:0FB2` (load 0xBAA2), scroll driver `21E6` (load 0xCCD6) and
helper `0D45` (load 0xB835): all 6,715 software-state/ring frames agree,
including termination and 64 stopped frames. It intercepts graphics/EGC calls.
The original `_TEXT 0000:3680` MPN renderer independently agrees on 32,768
indexed pixels across all 128 character-specific tiles. This is bounded
original CPU evidence, not full gameplay or Windows pacing.

The earlier background verification receipt is
`.analysis/port64/verification-background-v1252/receipt.json` (SHA-256
`b672ceef52c024b9fd5ddd5e6b5b3d756980ccc953a91964c473abce201a669c`), with source manifest
`7da5c6540a1e28c07886ec5c3db9cf37bc46fa93903f1a4fc7158fcc7a87267e`.
Original CPU, native-window and sanitizer receipts for the background slice
are under `.analysis/port64/background-v1252/`. The earlier movement-only
receipts remain under `.analysis/port64/live-v1251/`. Each records product
hashes and scope limits; `verify.py` records the source manifest.
Earlier shooting receipt:
`.analysis/port64/verification-shots-v1253-final/receipt.json`. Original CPU
receipts are `.analysis/port64/shots-v1253/cpu-{linux,windows,ubsan}-final/receipt.json`;
window receipts use `window-{linux,windows}` and `window-marisa-{linux,windows}`.

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
verify. Motion/items/background/shots/enemies required no further DOS-source edits.
For each next module, stop readability work once state ownership, arithmetic,
control flow and hardware boundaries support an independently checked native
implementation. Resume only for a concrete ambiguity exposed by integration.
Next, connect enemy bullet tune/add/update to the synchronous event boundary,
then midboss/bosses, later-stage scrolling/tile maps, HUD, death/Bomb transitions
and audio. Add saved
configuration and route-level gameplay/Ending/score checkpoints as those
systems become runnable. Full gameplay is the completion condition, not an
exhaustive source-renaming pass.
