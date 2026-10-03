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
`Lcg32` directly. Direct spark initialization and live spark draws now use these same owners;
remaining boss/player-transition sites are still separate work.

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
scrolling background, including enemy bullets. Bosses, Bomb/death, later-stage
visuals and HUD remain absent.
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
laser damage, unsigned rectangle bounds and spark phase. The shot owner emits spark requests; the live MAIN adapter now allocates them
synchronously using the shared ring. Sound remains absent. The earlier isolated
shot CPU oracle below deliberately intercepts spark callees.

MAIN now dispatches STD waves, then updates player/shots/bullets/enemies/items
in original order. SDL and Win32 sample
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

Fire, sound, tile-ring and spark requests dispatch synchronously. Item drops
and enemy bullet tuning/allocation are connected to their live pools. Spark allocation and its random draws now run synchronously as well; audio
and remaining boss/player-transition adapters stay separate. Player collision records a hit but
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

## Enemy bullets

`enemy_bullets` connects script FIRE and enemy autofire synchronously to the
same random ring, preserving the partially assigned process-wide scratch
versus full-template transfer. It models separate descending 240-pellet and
200-large pools, rank/performance tuning, all 14 groups, cloud phases and nine
special motions. Explicit byte stores retain wrapped count/speed arithmetic,
initial deceleration, velocity-before-speed changes, signed angle division
and double corner bounces. Graze precedes collision on a fresh bullet;
invincibility blocks both. Clear/zap contracts retain their timers, pattern
changes, age rewards and capped ordered bonuses. Death/Bomb owners have not
yet been connected to the exposed hit/clear/zap state.

The original count policy sets delay 2 on even frames when Turbo is disabled
and the active count reaches `24 + performance + rank * 8`. Both host timers
apply that flag to their chosen simulation cadence. This is original deliberate
slowdown policy, not a measurement of original frame timing or host performance.
Extra forces Turbo, as in the original launch contract.

Normal pellets use a procedural 8x8 white/purple glyph; large bullets, clouds
and decay use the original MIKO16/MIKO32 BFNT assets. Independent original
`main_01 0AAF:1EAC/1F3E` CPU execution with a GRCG write-mask shadow compares
all 64 glyph pixels across 72 alignment/Y-roll controls. The lower pass starts
at Y+3 after six white rows and repeats its first row. A Y+4/nine-row reading
was rejected by these controls. Indexed-pixel SHA-256:
`a46af7a156407770ad1074cfd03659acc4efc2f3bb7129812f766c8dae478c35`.
This checks the glyph, not full host edge clipping or every cloud sprite.

Original relocated MAIN CPU replay agrees on 36,216 checkpoints (18,900 tuning,
10,160 allocation and 7,156 update cases) for Linux, Wine/Win32 and GNU
UBSan/bounds. It compares the template, FNV32 fingerprints of all 440 packed
26-byte records, scalars, ring cursor and ordered intercepted requests. Joint
STD/enemy/bullet replay also agrees on 1,200 Normal and 1,200 Lunatic frames.
Scope: `MAIN.EXE main_03 13A9`, tune `9435/9440/9448/9453`, regular wrappers
`945E/9486/94A2`, special wrappers `94BE/94DA/94F6`, group `9538`, special
motion `8CA6`, update `8E38`; load `2000`, DS `8000`, pool DS:5A22.
Spark, HUD graze, point-number and gather callees are intercepted. Their effects,
spark random draws, gather lifecycle, complete routes and natural timing are
excluded; these are bounded semantic comparisons, not byte-exact acceptance.

Separate count-zero ring controls reach original `IDIV BX` exceptions at
loaded CS:IP `33A9:9648` and `33A9:9669`. The port retains the already repaired
playable DOS product's skip guard; undefined original zero-count behavior is
excluded from the agreement claim.

`--combat-screenshots DIR` additionally selects Lunatic through OP and advances
900 real Stage 1 frames without firing for each character. Each scene has five
live enemy bullets; no entities or score are injected. Both bullet BMPs and the
previous held-Z combat fixtures agree across Linux, Wine/Win32 and UBSan. This
is a drawing/integration fixture, not a dense-barrage performance benchmark.
All five x64 contract executables and prior resource/UI/player-shot fixtures
pass. Cross-host receipt:
`.analysis/port64/verification-bullets-v1255/receipt.json`; CPU receipts:
`.analysis/port64/bullets-v1255/cpu-{linux-final3,windows-final,ubsan-final}/receipt.json`.

Gather/spark allocation and random-call boundaries are now connected below.
The Stage 1 midboss boundary is connected below. Next port bosses, stage
transitions/visuals, player death/Bomb, HUD/audio and Ending/save screens. Semantic work remains paused until a concrete
ambiguity blocks these tasks. The native game is still incomplete; the DOS
product and its exact acceptance remain unchanged.

## Sparks and gather circles

`effects` owns a 96-slot spark attempt ring and 16 first-free gather slots.
MAIN initializes the low byte of each spark angle with 96 direct process-LCG
calls after ring fill and item-drop initialization. Initialization preserves
high angle/offset bytes; stage clearing normally makes them zero. Spark
requests advance the attempt offset even over occupied slots, consuming one
shared sample only on an actual free slot. Circular bursts retain the wrapped
16-bit premultiplied numerator, including counts above 255. Spark updates run
before player movement, retain move-before-gravity and byte age wrapping, and
reclaim removed slots on the following frame.

Gather requests capture the already tuned full 18-byte bullet template and
reset the gather shape to the original defaults. Ascending updates move the
center, save/subtract signed radius, advance byte angle, and release when the
radius becomes smaller than 2 pixels. Release restores the full process-wide
bullet scratch and calls the regular wrapper without retuning. Gather-only
allocation changes just the saved spawn byte. Gather updates run after items;
fresh enemy-created circles therefore shrink in the same frame. Immediate
shot-hit, enemy-kill and bullet-graze spark requests retain their shared-ring
ordering.

The host paints gathers and eight spark cels procedurally from disks/lines,
in original foreground order: player, gathers, sparks, items, then bullets.
No original bitmap arrays are embedded. Original renderer GRCG-mask shadows
agree on 648 glyph controls (nine masks, eight alignments, nine Y/roll positions),
SHA-256 `d5c8419022abe60572035dc8285014f950ae164eac11c8bcfd238e27221fb3a3`.
Original render-coordinate/cel/color controls additionally cover 120 spark
and 216 gather states, including signed-word point-angle multiplication.
Glyph checks exclude full host edge clipping.

The independent CPU oracle agrees on 3,075 cases: 54 initialization, 497 random
spark adds, 496 circular adds, 1,080 spark updates, 120 spark draws, 54 gather
adds, 54 gather-only adds, 504 gather updates and 216 gather draws. It compares
complete serialized 96x16-byte spark or 16x42-byte gather records, process
LCG/ring/attempt cursors, and full restored release templates. Entries:
`MAIN main_01 0AAF:1824/1776/17C2/1710` (spark init/update/render/glyph),
`main_03 13A9:039A/03FC` (random/circle), `0027/0091/013E/01CC/1008`
(gather add/only/update/render/glyph); load `2000`, DS `8000`. Storage:
DS:53E2 sparks, DS:41F4 attempt byte offset, DS:9292 gathers, DS:9586 template.
The isolated gather-update oracle intercepts the regular wrapper to compare
its complete input; the joint oracle executes that wrapper.

Normal/Lunatic joint controls agree on 2,400 frames while executing original
STD/enemy, spark, gather, bullet and shot-hit callees. These private controls
inject one targeted shot-cache entry per frame and a gather producer every
96 frames. They compare canonical wire fingerprints for all four pools, ring
and spark cursors, graze, hit/kill/score state and scratch template. This is a
controlled integration test, not ordinary gameplay or complete routes.
Drops, HUD, audio and graphics effects outside these glyphs are intercepted.

Separate negative controls reproduce original zero-count spark-circle `DIV`
at loaded `33A9:043A`; the host throws a defined exception. Random spark count
zero retains its 65,536-attempt word decrement behavior. Corrupted spark offsets
are rejected before host array access. These out-of-domain cases must not be
conflated with normal boss burst counts or universal original equality.

Linux ELF64, Wine-hosted PE32+ and GNU UBSan/bounds pass all six contracts,
resource/UI/player-shot regression fixtures and the scoped CPU controls. Real
1200-frame Stage 1 held-Z scenes now yield 24 kills, score delta 5,720 and power
6 per character; the 900-frame Lunatic scenes have six live bullets. Their four
BMPs/counters agree across hosts and sanitizers. Earlier enemy-only 26-kill
results above remain historical: adding real spark random consumption changes
the shared sequence. Cross-host receipt:
`.analysis/port64/verification-effects-v1256-final2/receipt.json`; CPU receipts:
`.analysis/port64/effects-v1256/cpu-{linux,windows,ubsan}-final/receipt.json`.
The DOS source and acceptance ledgers are unchanged. Native player death,
Bomb, bosses, progression, HUD/audio and Ending/save remain incomplete; native
Windows pacing still needs an actual Windows host observation.

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

## Stage 1 midboss

`midboss` owns fixed-width Stage 1 state, activation at frame3100, the four
emergence-tile writes, the two invulnerable unfolding phases, the paired
special-bullet pattern, shot damage, five-unit score bonus, scroll timeout and
the common defeat lifecycle. It preserves HP800 versus displayed HP maximum620,
signed frame/HP wrap, retained damage bytes, and the second bullet's reuse of
the once-tuned shared template. The phase-zero Y compensation adds the prior
frame's subpixel scroll delta, not the physical scroll origin. STD dispatch
uses the previous active flag before activation, matching the original loop.
Enemy homing selection is overridden by the midboss after enemy updates;
next-frame shots consume that result. Hit sparks consume one shared sample
per free attempt with radius128/count1 at the original call boundary.

`prepare_render` caches normal/white split sprites and the 16-sprite expanding
defeat ring once per simulation frame. Refreshing the host window does not
clear damage twice or advance the defeat angle. `stage1_setup` appends twelve
64x32 `ST00.BMT` patterns at global140 after twelve 32x32 `ST00.BFT` patterns
at128. The host now loads both sheets. Original setup installs BMT's palette
and overrides color zero's R/G to FF; native RGB is FF/FF/70 before DAC
quantization. Earlier MAIN fixture `a6341ebd...` becomes `4cbbe895...` for this
specific correction. Four earlier combat BMPs change only their80/85 color-zero
pixels; their geometry and counters are unchanged. OP/selection/handoff hashes
remain unchanged. This supersedes the earlier incomplete Stage 1 palette.

The prior-image delta probe is replayable from the private v1256 baseline
and the new cross-host receipt's `combat-linux` directory:

```python
import hashlib, json
from pathlib import Path
old = Path('.analysis/port64/verification-effects-v1256-final2/combat-linux')
new = Path('.analysis/port64/verification-midboss-v1257-final/combat-linux')
baseline = json.loads((old.parent / 'receipt.json').read_text())
for path in sorted(old.glob('*.bmp')):
    before, after = path.read_bytes(), (new / path.name).read_bytes()
    assert hashlib.sha256(before).hexdigest() == baseline['combat_fixture_bmp_sha256'][path.stem]
    expected = bytearray(before)
    for at in range(54, len(before), 3):
        if before[at:at+3] == bytes((170, 204, 170)):
            expected[at:at+3] = bytes((119, 255, 255))
    assert expected == after, path.name
```

The new independent CPU oracle executes pinned original MAIN at load2000,
DS8000, checking699 isolated update/activation/reset/render cases, including
all440 packed26-byte bullet records, the22-byte midboss state, full scratch,
HP/animation globals, random cursor and ordered effects/draw coordinates.
An additional450 controls execute original tile initialization, scroll driver
and the actual tile setter at six checkpoints, comparing the complete25x24
ring. A separate original `stage1_setup` call verifies initial state, the BMT
filename and palette overrides with an explicit file-palette adapter. Scope:
main_03 13A9:0522/0587/642C/6454/6486/64DE/65B7/A55F;
main_01 0AAF:1C88/6FAA/0B92/0FB2/21E6. Ghidra database attestation and
target identity pass; canonicality remains candidate-local-attested.

Midboss CPU controls inject damage at the hittest boundary and intercept
tile/circle/point-number/audio/HP-pixel calls. Tune/add/bonus and defeat
geometry execute; independent tile controls execute the setter itself.
These are bounded runtime observations, not byte equality or full-route
original video comparison. MAIN retains pending sound, point, HP and shake
requests in `midboss_events`; audio, point-number rendering, HUD and screen
shake remain to be connected. Host redraw does not yet emulate the exact
PC-98 page/dirty-tile publication schedule or every edge-roll case.

Linux ELF64, Wine-hosted Windows PE32+ and GNU UBSan/bounds pass seven
contract targets. The four4500-frame scenarios reach phases0/1/2/3 and leave
the scene; shooting kills the midboss while idle runs exercise timeout.
All24 BMPs and gameplay counters agree across hosts. Original CPU receipts:
`.analysis/port64/midboss-v1257/cpu-{linux,windows,ubsan}-final/receipt.json`.
Cross-host receipt:
`.analysis/port64/verification-midboss-v1257-final/receipt.json`.
No original executable/assets are embedded, and no DOS source or acceptance
state changes. Native Windows pacing and a complete game remain unverified.

## Stage 1 Orange state and attacks

`orange` now owns the fixed-width Stage 1 main Boss state: entrance,
four random movement/attack modes, horizontal bounce attacks, escalating
multi-direction bursts, HP thresholds, timeout, small/big explosion creation,
the final explosion animation clock, and Stage 1 clear/next-stage requests.
It uses the existing bullet, gather, spark and shared random-ring owners
synchronously. The scratch templates retain unused bytes and the second shot
of a paired producer uses the first shot's tuning. The regular random rings
intentionally do not tune. Multi-bursts use the verified fixed-speed wrapper.

This is a verified logic owner, **not yet connected to ordinary live MAIN**.
Foreground, explosion aging, circles and host background composition now
connect through the explicit diagnostic entry described below. Ordinary
pre/post-boss dialog, HUD/audio and the stage-clear consumer remain to connect.
The current live window still ends at the previous Stage 1 frontier. Original
`MAIN main_01 0AAF:2454` activates Boss callbacks only after scroll speed is
zero, the back page is 1 and the blocking pre-boss dialog has returned;
exhausting the STD wave program is insufficient. Keep that barrier when
connecting this owner. Post-boss dialog/bonus/next-stage events are ordered
requests: the progression consumer must account for resident graze before
dialog, complete the dialog before stage bonus and honor the quit/delay
boundary. These unported consumers are explicit adapters in the CPU controls.

The independent original-CPU comparator executes `MAIN main_03
13A9:6013` (complete 0x403-byte Orange update, followed by two switch tables),
its attack callees at `5B54..6012`, common hit/phase/defeat helpers
`AB48/ABBE/AC02/AC63/ACB3`, bonus `6548`, typed explosion adds `21EC/226C`,
and actual bullet/gather/spark callees. Load segment 2000, DS 8000 is recorded;
loaded code is 33A9. The local target remains candidate-local-attested,
MAIN SHA `077440a3...`, header 6144, 1136 relocations. Current Ghidra attestation
is checked separately; the database is not an independent behavioral oracle.

Two receipts supply 36,600 complete state checkpoints: 2,805 isolated controls,
ten whole-Boss sequences (five ranks, zero/19 injected damage,5,117/1,130
frames), and twenty 128-frame complete pattern controls (all four modes on
five ranks). Every sequence reaches phases 0/1/2/3/4/5/254/255 and the next-stage
request. The fixed ring does not choose aimed-cloud mode 2 in the whole-Boss
sequences; the separate full-pattern controls cover that gap explicitly.
These sequences advance Boss only; bullet/gather/spark pools deliberately
retain occupancy, so they are not natural gameplay or renderer tests.

Each checkpoint compares the full 24-byte Boss, 16 additional state bytes,
440x26-byte bullet pool,16x42-byte gather pool,96x16-byte spark pool, both
scratch templates, 48 explosion bytes, scalar globals, shared RNG cursor and
ordered hit/sound/circle/item/point/HP/progression requests. Full fields are
compared before hashing; gzip is only private trace storage. Target controls
inject damage at the actual hittest boundary and check that the against-Boss
flag is set then restored. They intercept circle geometry, item/point
allocation, HP pixels, audio, dialog/bonus and host delay, without claiming
those adapters have been migrated.

Preserved target details include damage-word-to-byte truncation before HP
subtraction (even 256 damage can play a hit sound but remove zero HP),
wrapped 16-bit target subtraction before movement division, retained velocity
inside the center dead band, phase 4's second 600-frame test **after** hittest
increments the clock, and assigning the final bonus byte directly to zap
(including zero). `Subpixel::None()` is `-15984` (−999 pixels), not INT16_MIN.
Small explosion creation selects slot 1 whenever slot 0 is alive, overwriting
slot 1 if necessary; its unused byte survives. State updates do not age these
explosions; the separate `prepare_render()` step below owns render-side aging.

Reproduce the complete current control set from this worktree:

```bash
cmake --build .analysis/port64/linux-live-v1251 --parallel 4
python3 port64/verify_orange.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-orange-contracts \
  --output-dir .analysis/port64/orange-v1258/regenerated
```

Historical original traces are under `orange-v1258/cpu-linux` (34,040
checkpoints) and `pattern-linux` (2,560). The final Linux, Wine/Windows PE32+
and optimized GNU UBSan/bounds executables replay both original traces with
`--native-only --reference-dir`; these host replays do not reexecute the CPU.
Receipts are`orange-v1258/replay-{linux,windows,ubsan}/receipt.json` and
`pattern-{linux,windows,ubsan}-final/receipt.json`. Both trace digests agree
on every host: `ebfb2fd4...` and `6e80f57d...`. Native product formats and
the existing OP/resource/player/shot/enemy/midboss image regressions are
independently replayed by `port64/verify.py`; eight contract targets pass.
The current cross-product receipt is
`.analysis/port64/verification-orange-v1258-final/receipt.json`, source
manifest`717f96b9...`.
No DOS source or exact-acceptance state changes. Native Windows pacing,
complete original-scene video equality and game routes remain unverified.

## Stage 1 Orange foreground and native integration

`orange_render.cpp` adds the cached foreground plan and two small/one big
explosion lifecycles. `circles` owns the sixteen ten-byte logical records and
the default PC-98 midpoint circle outline. `State::update()` advances these
once per simulation frame; host repaints only read cached draws. Circle updates
precede sparks/player updates, Boss shot hits and immediate effects precede
items/gathers, and Boss foreground precedes midboss/enemies. Outline circles
render after enemy bullets. Background selection uses the **pre-update** Boss
phase/frame, matching the original loop order.

Independent original CPU execution compares 900 foreground/explosion controls
and 918 circle controls on GNU Linux, MinGW PE32+ under Wine and optimized GNU
UBSan/bounds. Scope is `MAIN main_01 0AAF:6E7B` foreground, `2D9C/2E65`
explosion render, `1B5A/1BA6` circle add, `1BF2` update and `1C28` render;
load2000 gives CS2AAF, DS8000. Draw adapters capture ordered sprite/circle
geometry, white-plane arguments and scale requests. All 48 explosion bytes,
160 circle bytes, damage retention, palette tone/change flag and big-explosion
clock are compared. Of the circle controls, 150 execute the actual library
`0000:11EC` GRCG circle routine and compare its 32,000-byte write mask, including
default-rectangle edges, zero radius and row399. This is independent pixel-mask
evidence; it is not a hardware color/page/timing claim.

Preserve these observed quirks:

- Circle center division uses signed IDIV (negative fractions truncate toward
  zero), while sprite coordinates use SAR (floor). Age17 sets flag2 and is
  absent from rendering, despite an older DOS source comment suggesting it draws.
- Small explosions use 64 points at angle increments4 and strict screen
  bounds; the big explosion uses16 points/increments16 and inclusive bounds.
  MIKOD is actually48x48 although the target clips/transforms it as64x64.
- The final Boss explosion sprite uses the library's real twofold enlargement;
  it is distinct from the48x48 MIKOD sheet. Damage flashing does not clear the
  Boss damage byte. White-plane arguments are FFC0/mask0.
- Big-explosion flash advances its retained signed clock only while alive,
  resets the clock on an inactive render, and preserves tone until another
  palette action. Repainting does not age explosions or change this clock.

Native MAIN now consumes real shot hits, homing, bullet/gather/spark effects,
item allocations, circle requests and Boss bonus deltas. Private MIKOD.BFT,
ST00BK.CDG and ST00.BB are decoded with explicit geometry checks. The host
composes entrance masks, backdrop/color-zero changes, white damage sprites,
explosions and palette tone. Background BB/palette composition follows the
maintained DOS owners; this batch does not independently compare complete
original background/color VRAM or PC-98 dirty-page behavior. It uses full host
redraw rather than EGC copies and invalidated tiles.

`--orange-screenshots DIR` is an **explicit diagnostic start**, bypassing the
unported blocking pre-boss dialog with stopped scrolling. It retains normal
initial power1, actual shots/items and the shared RNG. Eight scenarios cover
Normal/Lunatic, Reimu/Marisa and shot/idle. Fifteen screenshots per scenario
include all eight phases, entrance circles/mask, active attack snapshots and
explosion frames8/16. Linux/Wine/UBSan agree on all120 BMPs and gameplay
counters. Idle reaches the pending dialog at frame4628 with Boss bonus0;
shots reach it at4225 Normal/4231 Lunatic with bonus12800. Repaint and three
additional pending-dialog ticks leave simulation clocks unchanged.

Ordinary STD still does not activate Orange: its original stopped-scroll,
back-page and completed-dialog contract must be implemented first. The native
diagnostic stops at phase255/frame0 before the post-boss dialog instead of
silently skipping it. Resident graze, dialog, clear bonus, stage progression,
audio/HUD/point numbers and player death/Bomb remain unported. Invincibility
requests reach the bullet context but the player countdown consumer is still
absent. These fixtures establish native integration, not a complete playable
Stage1 or original full-scene equality. Windows execution is via Wine, not
native Windows pacing validation. Semantic remains paused.

Reproduce from this worktree (create the screenshot directory first):

```bash
cmake --build .analysis/port64/linux-live-v1251 --parallel 4
python3 port64/verify_orange_render.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-orange-contracts \
  --output-dir .analysis/port64/orange-render-v1259/cpu-linux-final
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --output .analysis/port64/verification-orange-render-v1259/receipt.json
```

CPU receipts: `orange-render-v1259/cpu-{linux,windows,ubsan}-final/receipt.json`.
Render trace SHA`bb6b250a...`; circle trace SHA`d46f3ed2...`. The current
executables also retain all36,600 earlier Boss state/pattern checkpoints:
`regression-{state,pattern}-{linux,windows,ubsan}/receipt.json` under that
directory. Cross-product receipt: `verification-orange-render-v1259/receipt.json`,
source manifest`1e1e0fbe...`. `integration-review.json` records unchanged prior
shot/combat/midboss images/counters, UBSan image agreement and a negative
control that deliberately rejects an original-CPU hook. The callback wrapper
stops Unicorn explicitly and rethrows; callback errors cannot silently pass.

## Dialog VM and natural Stage 1 Boss flow

Native Stage 1 now reaches Orange through the real stopped-scroll/back-page
activation gate, blocking pre-boss dialog and resource reload. Defeat/timeout
then resumes the same script cursor for the post-boss dialog. This replaces
the v1259 ordinary-flow limitation above. The stage-clear bonus/transition
consumer is still absent, so simulation stays frozen after the post-dialog.

`port64/dialog.*` owns the immutable script buffer, retained consumed offset,
16-bit cursor/side/default parameter, command events and asynchronous waits.
An inner `#` exits a text box; the outer `#` ends the scene. `$` waits for key
release followed by a new press before stopping its current command level.
Held input speeds text but cannot dismiss a wait. Three-digit optional numbers
and inherited second-argument defaults preserve original consumption. Filenames
consume their separator and are limited to12 bytes. Fades retain six-unit tone
steps; palette TRAM text remains a separate white layer. Full host fade/input
latency is not inferred from the intercepted CPU wait/fade controls.

An independent original CPU Oracle executes pinned MAIN at load2000, DS8000,
CS2AAF (unloaded main01 0AAF), including2A7C dialog parse,26CC commands,
25DA/26A3 parameters and2454 activation. All16 actual dialog files and8
synthetic controls are tested with held/released input:48 cases,76 complete
scenes and18,768 ordered events agree, including final consumed offsets and
cursor/side/default state. Another768 speed/page controls compare the actual
dialog call and STD counter side effect, including invalid/nonactivating page2.
Input, rendering, file/CDG, audio, waits and fades are explicit boundary adapters;
this is command/state equivalence, not original complete-video equality.
The receipt attests both target and Unicorn engine. Hook failures explicitly
stop/reject the CPU; the native consumer does not generate expected traces.

This uncovered an integration error in the v1259 diagnostic. Actual `_DM00`
pre-boss commands clean slots128..255, loadST00.BB1 thenST00.BB2 and draw128.
The old diagnostic incorrectly retained midboss sprites (ST00.BFT/BMT). Native
ordinary flow now executes these commands and the diagnostic explicitly
installs the same battle bank. The BFNT headers describe four32x48 sprites
at128..131 and eight64x80 at132..139. Each file updates the active palette;
BB2 color0 is black. Previous geometry/state proofs remain valid, but the old
120 images did not establish original battle-sprite/palette correctness.

The scene composes blue stipple boxes, CDG portraits, actual script sprite
commands and Japanese text from a user-supplied2048x2048 monochrome PC-98 font
BMP. The supplied emulator font stays private. Six independent Python
SJIS-to-ISO2022JP/PIL pixel controls compare1,536 glyph pixels with the native
lookup. The Stage1 scene supports its actual resources; other routes' parsed
CDG-free/scroll/audio requests still need consumers when those routes are ported.

Eight natural scenarios start from the real OP/menu handoff at frame0:
Normal/Lunatic × Reimu/Marisa × shooting/idle. They inject no enemies, damage,
scroll stop or Boss entry. Five snapshots each cover the pre-dialog first wait,
correct battle bank, attack, post-dialog first wait and final scene. Gameplay
frames and RNG freeze throughout dialog; key release/press is explicit.
Pre-dialog starts at6652 idle or6548 shooting, both back-page1. Reimu/Marisa
retained pre/post offsets are1081/1257 and707/857. Three additional ticks after
post-dialog keep the pending stage-clear state frozen. Linux/Wine/optimized
UBSan agree40 BMPs/counters. Earlier shot/combat/midboss images are unchanged;
120 diagnostic Boss images now use the corrected battle bank. The current
Windows Orange binary was relinked, so it independently reruns1,818 original
render/circle controls and36,600 retained original state/pattern checkpoints
rather than inheriting a stale executable SHA. UBSan also reruns these gates;
Linux's unchanged Orange contract SHA permits its prior bounded CPU evidence.

Actual Windows PowerShell execution now passes all nine contracts and the40
natural BMPs/48 counters, equal to Linux/Wine. This is headless execution and
does not measure GUI pacing or Windows compiler availability. The PE32+ product
was cross-built with MinGW. No DOS source, executable, launcher or exact ledger
state changed. A versioned native package is installed at
`D:\Entertainment\Game\Touhou\th04-reconstruct\port64-preview\v1260`,
and the root `start-th04-port64.bat` opens the Stage1 preview with explicit
private font/HDI paths. The previous root native executable is backed up in
that package. No game/font assets are checked in.

Reproduce the focused original CPU and cross-product checks:

```bash
python3 port64/verify_dialog.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --exe .analysis/port64/linux-live-v1251/th04-port64-dialog-contracts \
  --output-dir .analysis/port64/dialog-v1260/cpu-linux-final
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-dialog-v1260-final/receipt.json
```

Native Windows replay (requires a fresh output directory):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File port64/verify_windows.ps1 `
  -ExecutableDirectory .analysis/port64/windows-live-v1251 `
  -Hdi D:\Entertainment\Game\Touhou\th04-reconstruct\play-normal.hdi `
  -FontBitmap D:\Entertainment\Game\Touhou\th04-reconstruct\FREECG98.bmp `
  -OutputDirectory .analysis/port64/windows-dialog-check
```

Receipts are `dialog-v1260/cpu-{linux,windows,ubsan}-final/receipt.json`,
`integration-review.json`, `native-windows-receipt.json` and
`verification-dialog-v1260-final/receipt.json`. Whole-game progression,
resident graze/clear bonus, later stages, death/Bomb/HUD/audio and Ending/save
remain unported. Stop general semantic work; port the next actual consumer.

## Migration order

Semantic work stops when the current subsystem is clear enough to port and
verify. Motion/items/background/shots/enemies required no further DOS-source edits.
For each next module, stop readability work once state ownership, arithmetic,
control flow and hardware boundaries support an independently checked native
implementation. Resume only for a concrete ambiguity exposed by integration.
Enemy bullets, gathers, sparks and the Stage 1 midboss now use that synchronous boundary.
Orange state/attacks/foreground and pre/post-boss dialog now run in ordinary Stage1.
Next connect the actual stage-clear bonus/progression consumer, then later bosses/midbosses,
later-stage scrolling/tile maps, HUD, death/Bomb transitions
and audio. Add saved
configuration and route-level gameplay/Ending/score checkpoints as those
systems become runnable. Full gameplay is the completion condition, not an
exhaustive source-renaming pass.
