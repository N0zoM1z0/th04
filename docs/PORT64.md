# TH04 native x64 port

`port/modern-64` is a separate product based on the semantic DOS source. The
DOS build remains the behavioral reference and keeps its own Borland/TASM
acceptance rules. The portable product uses fixed-width state, ordinary host
pointers and host backends; it does not claim byte equality with PC-98 code.

The current preview runs Stages1 through6 including their waves, bosses,
dialogues and departures. Stage4 has both character-dependent NPC battles;
Stage5 joins Yuuka's seven attacks and thick lasers. Normal/Lunatic continue
through Stage6 waves, the complete pre-battle dialogue and Yuuka's final
battle, then all-clear and the appropriate Good Ending. Easy runs its separate
bad dialogue and Bad Ending. The native frontend now joins MAIN's score/run
statistics, mandatory fade, resource release and fresh MAINE lifecycle to all
eight Ending script/graphics routes. Staff Roll now completes its two backgrounds
and three dissolve families, with the preview holding at verdict entry. The
verdict calculation/request/clock component now passes original CPU controls;
its graphics and GUI integration, congratulations and score registration/save
remain next. See [verdict component](#verdict-calculation-and-clock),
[Staff Roll](#staff-roll-integration) and
[MAIN-to-MAINE integration](#main-to-maine-ending-integration) for the current
acceptance scope. Earlier slices below retain their historical boundaries.
The final-boss [animation/motion helpers](#yuuka6-animation-and-motion-helpers)
and [cross/safety-circle entities](#yuuka6-cross-and-safety-circle-entities)
plus [gathering/attack helpers](#yuuka6-gathering-and-attack-helpers) and
[mirror/core dispatch](#yuuka6-mirror-and-core-dispatch) are
independently ported and now joined to the ordinary game loop.

## Current executable slice

`port64/main.cpp` currently owns the read-only resource path: TH04 HDI FAT12,
PAR directory/decompression. `port64/pi_image.cpp` shares the unchanged
16-color PI decoder with the MAINE cutscene owner. `port64/view.cpp` owns
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

## Stage-clear and all-clear bonus

`port64/stage_bonus.*` now owns both original reward calculations, the ordered
text/gaiji/performance/HUD requests, Bomb increment and all-clear extend-disable
side effect. Ordinary native Stage1 consumes this owner exactly once after its
post-boss dialog and shows a colored bonus TRAM layer over graphics tone60.
This advances the v1260 frontier above: the preview now stops on the actual
bonus screen. Score drain, leave overlay, persistent resident statistics and
next-stage resource handoff remain the next integration work; freezing there
does not establish a complete stage transition.

Independent original MAIN CPU controls execute main03 13A9:9C31 (ordinary),
9E06 (all clear),99FE/9A89 formatters,9AFF/9B59 multiplier helpers and actual
main01 0AAF:1874/188E performance arithmetic. At load2000, CS33A9/2AAF,
DS8000 copied from relocated DATA, all1,837 cases agree on complete score delta,
Bomb count, performance, extends and palette tone, plus ordered text/gaiji
bytes/coordinates/colors and performance/HUD calls. There are986 ordinary and
851 all-clear controls, including the complete modifier matrix, five ranks,
Extra, unhandled byte values, word component wrapping, byte Bomb/performance
wrapping, life underflow, pre-modifier threshold neighbors and score-delta
overflow. Linux ELF64, Wine/MinGW PE32+ and optimized GNU UBSan/bounds all
execute the same original CPU producer independently. Video consumers are
intercepted; these controls prove math/state/requests, not complete rendering.

Preserve these original details:

- Reward units are ten points; value gaiji append the final zero. Component
  values first wrap as unsigned16-bit values, then widen. This includes
  graze×5 and `(remaining_lives-1)×1000/3000`; zero lives is not clamped.
- Life-credit, Continue and rank multipliers each perform their own unsigned
  multiply/divide-by10 and truncate. Extra has no rank multiplier. A zero final
  defeat-bonus byte applies a zero multiplier and skips the other descriptions.
- Ordinary performance thresholds use the unmodified subtotal, even when
  timeout zeros the award. The Bomb byte increments on every ordinary clear,
  including timeout/zero point items; then no-miss/low-Bomb performance raises
  run in order. All clear sets extends10 and does not grant a Bomb or change
  performance.
- Raise performs wrapped byte addition plus unsigned upper clipping; lower
  performs wrapped byte subtraction plus signed lower comparison. The target
  arithmetic executes, rather than being replaced by an Oracle adapter.

`bonus_text.hpp` localizes the maintained MAIN DATA strings with readable
Japanese comments. The CPU Oracle found the candidate timeout description at
`src/main/stage/bonus_state.asm` has eight full-width spaces before ×; pinned
MAIN DATA2134:1F79 has seven. The portable table corrects this one character.
The DOS owner is unchanged because changing its data extent would require
separate layout/build validation. Candidate DATA observations are not inherited
as original facts. Negative receipt: `bonus-v1261/candidate-text-mismatch.json`.

Native fixtures still start eight natural Stage1 routes from the OP handoff
with real gameplay and no injected reward or Boss start. Their final snapshot
now includes the actual bonus; the first four images/counters and all prior
shot/combat/midboss/diagnostic Orange images remain unchanged. Three extra ticks
leave delta/Bomb unchanged, proving the front end does not award repeatedly.
The current native prototype has no death/Bomb/Continue consumers, so those
live counters remain zero; only the isolated original CPU cases cover their
nonzero reward effects. Colored TRAM uses actual font/game gaiji and cell
replacement, including blank glyphs. Blink and complete original color/page
composition are not established by the snapshot controls.

Ten contracts and40 natural checkpoints agree Linux/Wine/UBSan. Native Windows
headless replay also passes ten contracts and the40 BMPs/48 counters. The
Windows root native executable and English launcher are refreshed with a
versioned backup under `port64-preview/v1261`; DOS files/launchers/assets are
unchanged. No native Windows GUI pacing or original full-route claim.

```bash
python3 port64/verify_bonus.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-bonus-contracts \
  --output-dir .analysis/port64/bonus-v1261/cpu-linux-attested
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-bonus-v1261-final/receipt.json
```

Receipts: `bonus-v1261/cpu-{linux,windows,ubsan}-attested/receipt.json`,
`integration-review.json`, `native-windows-receipt.json` and
`verification-bonus-v1261-final/receipt.json`. The same independent rejecting
adapter control checks that a Unicorn callback exception cannot silently pass.
Semantic remains stopped; next implement score drain and actual stage leave /
resource transition, not additional naming work.

## Score drain and extends

The current native MAIN ends each ordinary simulation frame with the original
score owner, after its frame counter and periodic performance raise. Actor/item
awards enter one pending accumulator. Score update transfers that amount into
eight little-endian decimal bytes, preserves continues in digit0, compares the
complete high score and dispatches extends. Life/performance changes and the
20-frame bullet-clear minimum feed the actual simulation; sound, life-HUD and
popup remain requests pending their consumers. HUD score rows56:4/6 now use
the original game gaiji and remain bright over dimmed graphics.

Pinned MAIN main01 0AAF:6BD4..6CA2 (update),6BA2..6BD3 (HUD),4316..43B5
(extend) and actual1874 performance raise are independently executed at load2000,
CS2AAF, isolated DS8000 copied from target DATA2134, resident9000:0000.
All4,690 transitions agree Linux GCC8.4, MinGW13 PE32+ under Wine and optimized
UBSan/bounds:3,759 isolated controls plus five retained-state sequences926 steps
and their five initial calls. Subsequent awards are injected into each owner's
retained state; target outputs are not reseeded into native after each tick.
Complete decimal/high-score/temp/HUD bytes, pending/frame dwords, life/clear/
performance/extend/popup state and ordered requests agree. The rejection control
also proves a failed Unicorn callback cannot silently pass. Identity remains
candidate-local-attested; no DOS exact claim follows from portable equality.

Keep the target's low-word-only frame-delta assignment even when a fixture's
high word is nonzero. Preserve the five temporary-digit writes and six AAA
iterations, including nondecimal AF/two-byte carry controls. The highest score
byte remains unnormalized. Extend predicates compare digit6/7 directly rather
than a total integer threshold, then raise performance/increment extends before
the life-cap check. Granting a life from99 produces100; the next grant is
suppressed. Continue and score digit0 share target DATA2134:4349 (confirmed by
0AAF:3CDA increment and43C0 reset skipping digit0). Maintained DOS storage
places a separate `_continues_used` byte before `_score`; that candidate layout
cannot establish the native ownership contract. DOS source is unchanged.

The live900-frame pickup/drain control conserves all awards, grants two extends
once, emits SE7 requests and publishes a20-frame clear timer. Eleven contracts
pass Linux/UBSan/Wine/native Windows. Forty natural Normal/Lunatic character/
shot-idle snapshots and counters agree Linux/Wine/UBSan/native Windows. The
old60-frame BMP is independently recreated with the saved v1261 PE; exactly960
pixels change inside the two new HUD rows, with every other pixel retained.
This pixel mask justifies the new MAIN fixture hash; other fixture changes may
also reflect real extends/performance changes, not just HUD.

At the end of the score batch this Stage1 preview still froze at the bonus;
the following departure batch connects its same-frame continuation and clocks.
Saved high-score loading, life-HUD, popup/audio, death/Bomb/Continue lifecycle,
resident publication and later resources/Ending/save remain separate work.
Current source/build receipts and English native launcher are packaged under
Windows `port64-preview/v1262`; the root native executable is refreshed only
after delivered hash checks. DOS products/launchers/assets are unchanged.
No full-route, original TRAM/palette composition or GUI frame-pacing claim.

```bash
python3 port64/verify_score.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-score-contracts \
  --output-dir .analysis/port64/score-v1262/cpu-linux-attested
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-score-v1262-attested/receipt.json
```

Receipts: `score-v1262/cpu-{linux,windows,ubsan}-attested/receipt.json`,
`target-owners.json`, `render-review/receipt.json`, `integration-review.json`,
`native-windows-receipt.json`, and `verification-score-v1262-attested/receipt.json`.
Stop naming work here; next resume the actual boss-update frame after blocking
dialog, then port the416/488 leave/next-stage handoff without skipping it.

## Stage enter and departure

Ordinary Stage1 now enters through the original black TRAM gaiji mask, completes
its blocked post-boss dialog inside the same actor frame, awards/drains its
bonus, and executes the416/488 leave sequence. The actor prefix runs once;
paused dialog ticks do not move actors or consume RNG. On continuation the
saved contexts feed items/gathers/render, overlay, frame/periodic performance
and score. Deferred tone60 is applied when that frame completes; the dialog
snapshot retains the palette previously displayed. Removing the former extra
front-end dim prevents the bonus scene from being dimmed twice.

Observed pinned MAIN owners at load2000: main01 CS2AAF, unloaded0AAF:
enter62B3..6348, leave6349..63B4, black6287..62B2; main03 CS33A9,
unloaded13A9: common defeatACB3..AE86. Isolated DS8000 is copied from
relocated DATA2134; resident9000:0000. Gameplay-loop0AAF:0098..0212/fileC388
places player/shots/bullets/enemies before the far boss callback at0105,
items/gathers after it, overlay0148 before clock01A8 and score0204. Database
attestation is the root `.analysis/ghidra/database-attestations/th04-main.json`.
These are target/runtime observations, not a new DOS exact promotion; pinned
target provenance remains candidate-local-attested.

Enter/leave share DATA2134:1B62. Enter draws at nonzero multiples of8 using
byte gaiji64-time/8 and retains72 when it changes callback to titles. Leave
decrements first; at416 it starts72→71, at488 zero-time black fill clears the
callback. TRAM is replaced across24×23 gaiji cells, not blended over retained
bonus letters; the score rows outside the playfield remain bright. Actual
GAMEFT gaiji57 independently explains all8,726 changed pixels in the60-frame
fixture relative to the saved v1262 PE; all other pixels remain identical.
Title/BGM/demo overlay consumers and original complete video timing are separate.

Common defeat adds wrapped stage graze before dialog, then calls bonus exactly
once. At416 it requests sound fade10; at488 it increments resident stage/ascii,
sets quit2 and requests one delay frame before finishing the ordinary frame.
TH04 ordinary leave does not flush pending score; remaining score carries into
the next session. The live application publishes graze/lives/Bombs/stage/ascii
without replacing MAIN, reseeding its LCG or falsely loading Stage2 resources.
Further input is held at that unloaded request. The current preview ends with
black playfield and bright score, pending the actual Stage2 loader and actors.

Independent original CPU controls cover all256 timer bytes, interval/wrap
boundaries and1,929 departure cases. Original machine context pauses at the
far dialog callee and resumes at its actual return address; held ticks preserve
the caller state. Three retained489-tick original departure→leave→score sequences
exercise pending1,20,000,000 and2,000,000,000, including nonzero pending at
stage advance. In total4,331 input commands/7,265 complete state and ordered
request records match GCC8.4 Linux, MinGW13 PE32+ under Wine, optimized
UBSan/bounds and actual Windows PE execution. A rejecting callback remains a
required negative control. Forty focused original Orange phase255 snapshots
also preserve the prior serialized boss/pool/global/RNG contract.

The first fixture was rejected at frame1 because Python native-aligned Bh
inserted a padding byte, writing256 to target53DA. Explicit packed little-endian
<Bh restores the intended phase/frame bytes. Keep the rejecting observation;
an adapter packing error is not permission to change target semantics.

Twelve contracts pass Linux/UBSan/Wine/native Windows. Eight natural Normal/
Lunatic character/shot-idle Stage1 routes produce64 identical BMPs and72
counters across all hosts, through bonus,416 fade, late mask and488 request.
Controls check actors/RNG do not repeat on dialog resume, bonus/fade/next-stage
requests occur once, and the unloaded Stage2 request freezes further updates.
These are headless behavior/picture controls, not measured GUI frame pacing.
Windows package `port64-preview/v1263` and root native launcher are refreshed
after delivered hashes; DOS products/assets and normal/invincible launchers
are unchanged.

Stage2 session/resource initialization, midboss/Kurumi, final/Extra Ending
dispatch, saved high score/life HUD/popup/audio/death/Bomb/Continue/Ending/save
remain outside this slice. Later run initialization must reset accumulated
resident graze at its actual owner; these scenarios start a fresh application.
When loading Stage2, preserve global pending score while resetting only the
proved stage-owned counters/pools, then activate the correct resources/boss.
Do not merely relabel Stage1 or reuse Orange as a placeholder.

```bash
python3 port64/verify_transition.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-transition-contracts \
  --output-dir .analysis/port64/leave-v1263/cpu-linux-attested-final
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-leave-v1263-final/receipt.json
```

Receipts: `leave-v1263/cpu-linux-attested-final/receipt.json`,
`cpu-{windows,ubsan}-attested-final/receipt.json`, `target-owners.json`,
`gameplay-loop-owner.json`, `render-review/receipt.json`,
`orange-departure-cpu-linux/receipt.json`, `integration-review.json`,
`native-windows-cpu.json`, `native-windows-receipt.json`, and
`verification-leave-v1263-final/receipt.json`. Semantic remains stopped;
next port the actual Stage2 session/resource/actor boundary.

## Stage actor-session preparation

This section records the v1264 preparation frontier. The following Stage2
midboss section advances that actor integration beyond2600 to the Kurumi gate.

The next-stage actor API now operates on the existing MAIN owners instead of
creating a new gameplay session. It clears the seven implemented entity pools,
resets player current/previous position, firing time/style, stage point/dream
counts, graze/zap and gather/circle setup. It preserves process-wide score/
pending score, power/overflow/performance, input latch/velocity, shot volley and
hit-spark cycles, bullet clear timer/template/counters, gather center and spark
ring-offset high byte. Score HUD refresh does not drain pending awards.

The original random call order is ring256 → item drop1 → spark angles96,
all from the existing process LCG. Twenty-four double resets retain the same
original machine and native owners between calls:706 draws, with no reseeding
from target output. Stage2 preparation validates its STD before mutating owners
or consuming RNG. The actual departure request is required; MAIN generation,
resident statistics and score remain in the same application.

Observed pinned MAIN load2000/isolated DS8000 owners: main01 unloaded0AAF
runtime06E0..07AD, stage-state73DB..74A5, shots-reset593A..5953,
ring1168..117F and sparks1824..1841; main03 unloaded13A9
items9F8B..9FA7, midboss-reset642C..6453 and Stage2 setupA623..A6F5.
Actual library IRand2000:2172 and score HUD6BA2 execute. Original stage-state
clears nine complete physical extents, checked independently with upper EAX0
on entry to the register-ABI REP STOSD helper. Native custom-entity/point-popup
owners are absent; these target clear checks do not claim their implementation.
Clipping/hardware, shot-level dispatch, item splashes, Bomb, thick lasers,
point numbers and remaining HUD callees use explicit adapters.

The Stage2 midboss seed changes start2600, HP750, sprite0, current/previous
position3072,-512 and velocity0,16; inactive phase/frame/damage metadata stays.
All256 phase-byte controls execute actual original midboss_reset and stage2_setup
and compare the22-byte midboss state plus active flag. Boss/Kurumi callbacks,
rank-dependent boss fields and resource consumers are not ported by this seed.
Native MAIN holds before frame2600 so it cannot invoke the Stage1 callback
under a Stage2 identity.

All928 selected original CPU controls agree Linux GCC8.4, Wine-hosted MinGW13
PE32+, optimized UBSan/bounds and actual Windows x64. There are648 isolated
actor resets,24 retained double resets and256 midboss seeds. The checkpoints
include selected persistent metadata, all96 spark angles, all256 ring samples,
post-clear actor flag/position emptiness and score/HUD bytes. Rejected callback
control remains mandatory; these are bounded state claims, not whole-session
or DOS exactness claims. Identity remains candidate-local-attested.

Four controlled native Normal/Lunatic character routes finish natural Stage1,
retain its actual awards and then load original ST01.STD/ST01.MAP. They execute
10,400 total Stage2 frames, reject invalid STD before mutation and stop at2600
with midboss2 pending. Their counters agree Linux/Wine/UBSan/native Windows.
This is actor/STD/background-state integration without Stage2 visual resources,
full original gameplay or GUI pacing comparison. Thirteen contracts and the
previous64 Stage1 BMPs/72 counters agree all hosts and remain identical to v1263.

The GUI still ends at the unloaded Stage2 request. The new actor API is used
only by controlled integration until its caller replaces stage-owned sprites,
MAP/MPN/palette/portraits/dialog state and joins midboss2/Kurumi. Shared player
resources remain resident. Test package `port64-preview/v1264` contains current
x64 executables, native Windows verification and private stage fixtures; the
root GUI executable remains v1263. DOS source/assets/launchers are unchanged.
Do not advertise full Stage2 gameplay based on this preparation API.

```bash
python3 port64/verify_session.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-session-contracts \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --output-dir .analysis/port64/session-v1264/cpu-linux-final
```

Receipts: `session-v1264/target-owners.json`,
`cpu-{linux,windows,ubsan}-final/receipt.json`, `native-windows-session.json`,
`native-windows-receipt.json`, `integration-review.json`, and
`verification-session-v1264-final/receipt.json`. Initial invalid-style fixtures
were rejected by the existing shot-checkpoint guard; valid styles are now seeded
explicitly. The target/native actor code was not weakened to accept corruption.
Semantic remains stopped. Next implement Stage2 resources and midboss2.

## Stage2 midboss and actor integration

The native Stage2 owner now implements all four attack patterns, the96-frame
entry, three direction bytes,52-frame movement/gather gaps, damage rewards,
timeout and upward retreat. It retains the same shared bullet scratch and
random ring. The four quad directions tune only the first producer; later
shots inherit the adjusted group/count. The hit wrapper's10 argument is a
sound ID, not a damage cap. Entry consumes colliding shots but remains
invulnerable. Timeout after17 patterns branches before collision/rewards;
actual defeat adds the unsigned16 bonus product, point requests, a Bomb,
zap/shake and48 sparks. Retreat uses private phase2 and16-frame spark requests.

Rendering follows original0AAF:214A: Y<=0 or phase>2 produces no sprite;
otherwise idle146..149, left150..151 or right152..153 is drawn at the
actual signed/rolled position. Damage flash is consumed only when the sprite
call runs. Invalid sprite>2 leaves the target's SI undefined; native rejects
that state explicitly and excludes it from gameplay equivalence claims.
The Stage2 BFNT bank still needs to join the GUI.

Pinned MAIN13A9:1062..14E7 owns four patterns, the far126D dispatcher and
compiler switch data. Actual original tuning/regular-special producers,
gather3stack/only, shot-hit wrapper, score bonus/random, HP, activation/reset
and sprite geometry execute in the CPU comparator. There are9,282 controls
and13,512 records:2,542 updates,6,720 render cases,16 activation/reset cases,
and four retained Normal/Lunatic timeout/defeat update+render sequences.
These retained sequences preserve all midboss/bullet/gather owners and ring
between steps; ordinary other-actor updates are deliberately omitted.
Full22-byte state, three private bytes,440 bullet records,16 gather records,
both templates, RNG cursor, pending awards and ordered requests/draws compare.
Shot damage is injected at the real collision boundary. Spark requests,
point popups, Bomb requests, audio, HP pixels and sprite pixels are adapters.
No full original Stage2 route, GUI timing or DOS exactness claim follows.
The callback-rejection control prevents ctypes exceptions from being swallowed:
store the error, stop Unicorn and rethrow after the emulation call.

MAIN now chooses the actual Stage2 callback at2600. STD pauses scheduled waves
while that midboss is active. Shot collisions, gathers, sparks, items, score
drain and native drawing requests join the existing owners in frame order.
Four native Reimu/Marisa Normal/Lunatic routes continue natural Stage1 into
real ST01.STD/MAP, defeat the Stage2 midboss and reach the pre-Kurumi dialog
gate at6982. They hold there until dialog/Kurumi join. These are native actor
routes, separate from the selected original CPU comparisons.

The GUI remains Stage1 because stage sprites/map/palette/portrait/dialog
resources have not been replaced yet. `port64-preview/v1265` is the build/
verification package; the root GUI remains v1263 and DOS launchers/assets stay
unchanged. General semantic work remains stopped. Next connect Stage2 resource
ownership and dialog, then Kurumi; do not call this full Stage2 gameplay yet.

```bash
python3 port64/verify_midboss2.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-midboss2-contracts \
  --output-dir .analysis/port64/midboss2-v1265/cpu-linux-final
```

Receipts: `.analysis/port64/midboss2-v1265/target-owners.json`,
`cpu-{linux,windows,ubsan}-final/receipt.json`,
`session-{linux,windows,ubsan}-final/receipt.json`, `native-windows-midboss2.json`,
`native-windows-receipt.json`, `integration-review.json`, and
`.analysis/port64/verification-midboss2-v1265-final/receipt.json`.

## Stage2 visual resources and dialog

This advances the preceding backend-only slice. Both SDL and Win32 windows now
consume the actual Stage1 departure request, validate Stage2 assets before actor
mutation and continue through real Stage2 STD/MAP, its midboss and pre-Kurumi
dialog. The preview holds after that dialog; Kurumi battle remains unported.
Semantic readability stays paused at the user's stopping condition.

Pinned target observations: MAIN main01 `0AAF:055B..0580` is the second case in
the seven-word switch at `0AAF:06D2`. It requests `BSS1.CD2` at slot8,
`ST01.BFT`, actual `13A9:A623` setup and `ST01.MPN` without a character-dependent
map branch. The setup requests `ST01.BMT`, `ST01BK.CDG` image0/slot16 and
`ST01.BB`; five rank seeds execute these original requests through adapters.
`0AAF:07AE..07DE` frees stage sprites128..255 and CDG slots8..30. These are
selected relocated target observations with load2000/isolated DS8000, not new
whole-function exactness claims. Asset headers establish18 32x32 BFT images,
16 64x64 BMT images,75 MPN tiles and four128x128 boss portraits. Thus native
stage slots128..145 belong to BFT and146..161 to BMT. The Stage2 BMT palette
replaces the Stage1 palette without its color-zero override.

The native stage resource object owns its byte vectors on the heap. CDG views
reference these vectors and sprite slots reference its sheets; disable whole
object copying and move only the owning pointer. Clear every dynamic stage slot
before destroying Stage1 dialog sheets. Common player/items/enemy sheets remain
owned. Allocate and validate the next background/script before preparing actors,
then publish resident resource_stage1 only after installing the resource bank.
The same MAIN generation continues and initialization consumes353 LCG draws.

Four native character/Normal-Lunatic routes run natural Stage1, enter Stage2,
render its map/midboss/retreat and reach the pre-Kurumi gate at6982. Dialog holds
gameplay frames, player/shot actors and shared RNG; its completion holds the
unported battle frontier without restarting the script. Script offsets end at
566 for Reimu and585 for Marisa. Eight checkpoints per route give32 BMPs and36
counters, identical on Linux GCC8.4, MinGW13 PE32+ under Wine, actual Windows
and optimized GNU UBSan/bounds. Fourteen contracts pass; the previous64 natural
Stage1 BMPs/72 counters remain identical to v1265 across Linux/Wine/Windows.
The Windows verification script includes both stage suites and reports96 images.

Independent checks execute all48 existing original dialog controls/76 scenes /
18,768 events on Linux and Wine, including both Stage2 scripts with held and
released input. Font decoding uses the supplied FREECG98 bitmap. Original
graphics/file/audio/wait consumers remain intercepted; the native frame pacing
is not an original-game timing claim. A separate Python FAT/PAR/CDG/BFNT path
checks57,188 opaque Kurumi portrait pixels against the native screenshots and
Stage2 palette. It rejects a disposable BMP with one opaque pixel changed at
(298,112); transparent background lies outside this portrait-only comparator.
Original hook rejection also has an explicit negative control. These checks do
not compare complete original VRAM or establish full Stage2 gameplay/FPS.

```sh
cmake --build .analysis/port64/linux-live-v1251 --parallel 4
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-stage2-v1266/receipt.json
python3 port64/verify_stage2_resources.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --frames .analysis/port64/verification-stage2-v1266/stage2-linux \
  --output .analysis/port64/stage2-v1266/resources-final.json
```

Source manifest:
`3e229f60bb2e8095508ee7da56b469b39f67908b035aabfda30f3124fabcd7f3`.
Receipts: `.analysis/port64/stage2-v1266/target-resources.json`,
`resources-final.json`, `negative-pixel.json`, `dialog-cpu-{linux,windows}/receipt.json`,
`native-windows-receipt.json`, `integration-review.json`, `windows-export-receipt.json`,
and `.analysis/port64/verification-stage2-v1266/receipt.json`.
Windows package `port64-preview/v1266` and root native launcher use this preview,
with a versioned backup. DOS executables, normal/invincible launchers, assets and
saved files are retained. Next implement Kurumi state/attacks/render and connect
the post-dialog continuation before expanding later-stage gameplay.

## Kurumi state and attack core

The Stage2 Kurumi logic is now a portable owner in `port64/kurumi.cpp` and
`kurumi.hpp`. Original MAIN main03 `13A9:4F84..56CC` owns the spawnray,
orbit and attack helpers; `56CD..5B32` owns the far update. Byte `5B33`
precedes three switch-word tables at `5B34..5B53`; these are data, not more
instructions. Selected relocated slices, setup `A623..A6F5`, boss reset
`A4D1..A517` and shared defeat `ACB3..AE86` are recorded separately from
runtime comparisons. Provenance remains candidate-local-attested.

Kurumi uses six 26-byte records at original DATA2134:B204. The byte flag owns
allocation; the other byte and twelve-byte tail survive reuse. Phase0 clears
only flags. The ray updater counts free entries before updating, so a newly
freed ray delays the all-free result until the next call. It writes SPEEDUP
into the bullet template but invokes the regular fixed-speed producer; preserve
that original call and its retained group. Orbit writes current coordinates
without moving previous coordinates or velocity. Seeking retains velocity
inside its dead band. Phase0 tests the old clock before invulnerable hit advances
it. Later hit damage is truncated to a byte after the clock increments.

The process-local turning toggle at46B0, unknown byte at46B1 and bullet special
controls BCB7/BCB8 remain explicit state. The final stack periods are255,128,32,8
for Easy,Normal,Hard,Lunatic. Extra does not load this ordinary boss; the native
fresh constructor rejects rank4. A zero period reaches original signed division
at13A9:5695; native code throws after the preceding cloud producers instead of
executing host undefined behavior. The zero-period guard is a native contract
and static target observation, not an original CPU exception replay.

Boss defeat is shared with Orange, but Orange's unconditional gather-center
write is specific to its update and must not leak into Kurumi. The extracted
helper preserves that distinction. Boss reset retains HP, angle, end HP and
additional state. Four fresh-DS setup controls compare only the24-byte boss,
hitbox384/384 and rank period; preceding-stage retained metadata remains an
integration requirement.

Original CPU execution supplies3,436 boundary controls and eight retained
boss-only sequences. Each difficulty has an8,323-frame timeout and1,190-frame
damage19 sequence, both reaching departure. All41,488 records agree on Linux
GCC8.4, MinGW13 PE32+ under Wine, optimized GNU UBSan/bounds and actual Windows.
Comparisons include the24-byte boss,16 additional bytes, every ray including
padding, all440 bullets/16 gathers/96 sparks,48 explosion bytes, templates,
global special controls, shared RNG cursor and ordered requests. Actual original
bullet/effect/bonus/departure callees execute; shots inject damage and
graphics/audio/HUD/item/point/dialog/delay consumers remain adapters. Retained
sequences advance only this owner and retain pool occupancy. They do not replay
ordinary actor motion, GUI rendering or frame pacing.

The comparator rejects a disposable first-checkpoint BOSS byte mutation and
propagates an injected original hook rejection. Fifteen contracts pass on all
build variants and actual Windows. Orange's prior34,040-record state trace
including ten retained sequences remains identical on Linux/Wine/UBSan after
the shared-helper extraction. The previous64 Stage1 and32 Stage2 BMPs and
108 counters remain unchanged across Linux/Wine/UBSan/actual Windows.

```sh
python3 port64/verify_kurumi.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-kurumi-contracts \
  --output-dir .analysis/port64/kurumi-v1267/cpu-linux-complete
```

Source manifest:
`803e9fbbab64f3b3edd1ac30043aa9b475dfb52c277eef44f4a47afdfeeb0c76`.
Receipts: `.analysis/port64/kurumi-v1267/target-state.json`,
`cpu-linux-complete/receipt.json`, `cpu-{windows,ubsan}-final/receipt.json`,
`native-windows-kurumi.json`, `negative-trace.json`, `integration-review.json`
and `.analysis/port64/verification-kurumi-v1267/receipt.json`.
Windows package `port64-preview/v1267` contains the checked core and15 contract
executables. Root Windows files remain byte-for-byte on v1266. Kurumi foreground,
backdrop, GUI battle and post-dialog continuation are the next bounded slice;
the live preview still holds after the pre-Kurumi dialog. No new DOS exactness
or complete original Stage2/gameplay claim follows. Semantic remains stopped.

## Kurumi foreground and ray raster

`port64/kurumi_render.cpp` now implements the original foreground at MAIN
main01 `0AAF:6CA3..6E7A` and the backdrop request plan at `76FB..7756`.
The next byte starts Orange's foreground. Shared explosion rendering is
extracted into `orange::prepare_explosions`; both bosses retain their own
foreground, sprite bank and circle geometry.

Boss sprite coordinates use signed arithmetic shifts, while ray coordinates
truncate signed division by16 before adding playfield32/16. Flag0 suppresses
a ray; every other flag draws, including values the updater does not advance.
Sprites0/12 animate with frame-mod16; sprites4/6 use frame-mod8; other sprites
remain fixed. Damage selects white rendering and is retained. The phase254
register expression pushes the calculated top before loading the sprite byte,
so its Y is defined. Phase0 circles begin only after clock128, with color7
and two color6 rings.

The native ray raster orders endpoints byX and accumulates a slope quantized
to16 fractional bits from8000h. Actual ray endpoints stay within the default
640x400 screen clip; generalized clipped endpoints are outside this helper's
scope and are rejected. Independent original CPU line controls execute
`0000:1562..16FE` with in-screen endpoints and compare all32,000 mask bytes.
Memory writes model RMW masks, not physical GRCG color/page/scroll state.
Only this default-clip path is selected; adjacent alignment at16FF, the next
function at1700 and the clipping helper are separate ownership.

Background phase0/254 and early departure request all tiles. Phase1 requests
the picture at32/96 with fill color0, copies the actual BB segment and requests
mask cel from the arithmetic phase-clock shift. Later battle phases request
the picture; later departure requests dirty tiles. The original colorfill
`0AAF:3F80..3F98` and row kernel `7578..7584` write384x192 pixels from32/208
and384x80 from32/16, covering104,448 pixels. This is a TDW address-footprint
observation: that mode ignores CPU value bits. Using the RMW mask collector
for this fill was rejected by the footprint comparison. Host background
composition has not yet consumed this geometry.

Across Linux GCC8.4, MinGW13 PE32+ under Wine, optimized GNU UBSan/bounds and
actual Windows,7,204 foreground controls,2,816 backdrop request controls and
620 line masks agree with the original. Compare complete48-byte explosions,
156 ray bytes including retained padding, flash/aging/tone clocks and ordered
sprite/circle/ray geometry. Original BOSS/additional-byte invariance is also
asserted; native comparisons cover damage and the listed render state.
Sprite/CDG/tile/color consumers remain adapters. A disposable one-bit change
in a native ray mask fails immediately, and original hook rejection propagates.
The shared extraction also passes900 original Orange foreground controls.
Kurumi's41,488-record prior state trace replays on current Linux. Fifteen
contracts and the previous96 BMPs/108 counters remain identical across hosts.

```sh
python3 port64/verify_kurumi_render.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-kurumi-contracts \
  --output-dir .analysis/port64/kurumi-render-v1268/cpu-linux-full
```

Source manifest:
`e0bf7972efdead82ba50d555011c9c873f47afc7ea75c690cfb2b97bd6ef0a02`.
Receipts: `.analysis/port64/kurumi-render-v1268/target-render.json`,
`cpu-{linux,windows,ubsan}-full/receipt.json`, `native-windows-render.json`,
`negative-line.json`, `orange-render-linux/receipt.json`, `integration-review.json`
and `.analysis/port64/verification-kurumi-render-v1268/receipt.json`.
Windows package `port64-preview/v1268` contains the checked core. Root Windows
files remain on v1266. Next account for preceding-stage retained Boss metadata,
compose the Stage2 backdrop and connect Kurumi battle/post-dialog/departure.
No new DOS exactness, physical GRCG or full Stage2/gameplay/FPS claim follows.
Semantic remains stopped; the existing DOS source was sufficient for this slice.

## Migration order

Semantic work stops when the current subsystem is clear enough to port and
verify. Motion/items/background/shots/enemies required no further DOS-source edits.
For each next module, stop readability work once state ownership, arithmetic,
control flow and hardware boundaries support an independently checked native
implementation. Resume only for a concrete ambiguity exposed by integration.
Enemy bullets, gathers, sparks and the Stage 1 midboss now use that synchronous boundary.
Orange state/attacks/foreground and pre/post-boss dialog now run in ordinary Stage1.
Ordinary Stage1 now also consumes the actual clear bonus and displays its tally.
Ordinary frame score drain and extends now join MAIN.
Post-dialog frame continuation and stage-leave overlay now reach the next-stage
request. Actor-session preparation and Stage2 midboss/STD/MAP integration through the
pre-Kurumi dialog gate are checked separately. Stage2 visual resources and its
pre-battle dialog now join the live window. Kurumi state/attacks have independent
CPU controls. Foreground/explosion/ray raster and backdrop requests now have
independent controls and now join the live battle/post-dialog/departure. Stage3
resources/STD/midboss, Elly battle, post-dialog and departure also run in the live window.
Next connect Stage4 and the remaining stages,
HUD, death/Bomb transitions and audio. Add saved
configuration and route-level gameplay/Ending/score checkpoints as those
systems become runnable. Full gameplay is the completion condition, not an
exhaustive source-renaming pass.


## Kurumi battle and departure integration

The native GUI now continues from the actual Stage2 pre-dialog gate through
Kurumi battle, post-dialog, clear bonus and departure. Previously it held after
the pre-dialog despite the separately verified boss and renderer. The next held
frontier is Stage3 resource loading. This is a native integration slice; player
death/Bomb, full HUD/audio, later stages, Ending and saving remain incomplete.
Semantic stays paused unless a specific port ambiguity needs clarification.

Original MAIN13A9:A4D1..A517 `boss_reset` clears phase/mode/pattern/frame,
velocity, damage and the two small explosion alive flags. HP/angle/endHP,
other additional bytes and all remaining explosion metadata survive, including
the big alive flag. Stage2 setupA623..A6F5 installs current/previous3072,1296,
sprite0, hitbox384,384 and rank periods255,128,32,8. The portable factory retains
these owners from Orange, while the separately observed stage runtime resets
slowdown1, shake0, bombing-disabled0 and invincibility64. Common stage0675
stores palette tone100 after loading. The new BFNT palette replaces color0
before Kurumi activates; at clock320 Kurumi itself sets96,0,0 as the existing
independent core controls attest. Copying all preceding globals would retain
Orange's defeat slowdown/invincibility/palette rather than the new stage values.

1,024 original CPU retained-marker setup controls compare complete24-byte Boss,
16 additional and48 explosion bytes plus hitbox/timeout.256 controls execute
only the original player countdown prefix0AAF:5FD4..5FDE, ending before hit/death
handling. They agree Linux/Wine/UBSan/actual Windows. A separate predecessor
control actually executes stage_runtime06E0 from speed3/shake17,-19/Bomb255/
invincibility255 and observes1,0,0,0,64. File/BFNT/CDG/hardware requests remain
adapters. A private source-built driver also checks the new retained metadata
and reset globals after four natural Stage1 departures; it is an integration
check, not another independent original Oracle.

The gameplay owner now dispatches the active ordinary boss, uses real shots,
bullets/gathers/sparks/items/score and prepares the foreground exactly once per
simulation frame. Player invincibility decrements once in the frame prefix and
is shared with boss/bullet owners; a suspended post-dialog frame does not repeat
that prefix. Rendering composes Stage2's opaque picture at32,96, its own BB mask,
the TDW color0 rectangles through physical row399, actual stage sprites and the
fixed-point ray pixels already checked in the previous slice. Full host redraw
continues to replace PC-98 dirty-tile/VRAM hardware operations.

Eight natural Reimu/Marisa Normal/Lunatic routes vary held shooting during the
Kurumi battle, exercising both defeat and timeout. Neither phase/RNG/actor pools
are forced. Each records nine checkpoints and asserts frozen dialog actors/RNG/
invincibility, post-dialog continuation, exactly one bonus/fade/next request,
416/488 departure and three inert advances at the Stage3 frontier. Resident
stage/ascii become2 but resource stage remains1; MAIN generation remains2.
Timeout receives no timely-clear award. Rendering and counters agree across
Linux GNU8.4, cross-built MinGW13 PE32+ under Wine, optimized GNU UBSan/bounds
and native Windows. All15 contracts pass. Total168 BMPs/188 counters include
72 new Kurumi images/80 counters; prior96 BMPs/108 counters are unchanged.

Independent Python FAT/PAR decoding verifies57,188 opaque portrait pixels and
86,016 selected unobstructed opaque-CDG/colorfill pixels across the new battle
checkpoints. The latter uses the original phase2 red color0, lower picture side
bands, bottom physical rows384..399 and idle-route upper rows. Shooting can
cover upper rows, so those are excluded from shot controls. This checks selected
asset/palette composition, not full original VRAM. A disposable BOSS output byte
mutation and one selected backdrop pixel mutation both fail their comparators;
injected original-hook failures also propagate.

Current Linux reexecutes all7,204 foreground/2,816 backdrop/620 complete line
mask controls, matching v1268. Three current builds replay the41,488 independently
recorded original core states with identical digests; that regression does not
reexecute original updates. Actual Windows additionally runs the new setup/
countdown controls and every native visual scenario. No original full Stage2,
physical GRCG, GUI frame pacing, native Windows compiler or DOS exact claim.

```sh
python3 port64/verify_kurumi_setup.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-kurumi-contracts \
  --output-dir .analysis/port64/kurumi-live-v1269/setup-linux-final
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-kurumi-live-v1269-final/receipt.json
```

Source manifest:
`1fcba424ea85e628b7f7df71e3183bd861f0a5e920645fabccf0cc60d0df52d1`.
Receipts: `.analysis/port64/kurumi-live-v1269/{target-live,integration-review,resources-live,negative-live,native-windows-receipt,native-windows-setup,windows-export-receipt}.json`,
`setup-{linux,windows,ubsan}-final/receipt.json`,
`core-{linux,windows,ubsan}-final/receipt.json`, `render-linux/receipt.json`,
and `.analysis/port64/verification-kurumi-live-v1269-final/receipt.json`.
Windows root `start-th04-port64.bat` and native EXE now use this v1269 preview;
21 other existing files remain unchanged. No window launched. Native builds
use incremental CMake; the DOS product did not require rebuilding. Next connect
Stage3 resources/actors/midboss, then Elly and its dialogs.

## Stage3 midboss and pre-Elly integration

The native window now continues from Kurumi's actual departure into Stage3,
runs its real STD/MAP and midboss, and finishes the Elly pre-dialog. Elly's
battle is held at the genuine frame9202 gate. No placeholder boss update runs.
Stage3 setup is derived from MAIN13A9:A6F6..A7B4, which installs the midboss
callbacks09FB/1D95, start frame1600, HP850, current/previous3072,-512 and
velocity0,64. Reset clears active/HP before setup; phase, phase clock, damaged
flag, unused angle, shared HP-bar and defeat angle survive until their real
owners change them.1,280 CPU controls seed all22 actor bytes across256 markers
and five ranks, and compare those retained fields on three builds and actual
Windows. Elly's own retained Boss setup is deferred to the next batch.

Four attack helpers occupy13A9:0861..09FA; the dispatcher ends at0C09. The
zero byte0C0A and switch table0C0B..0C1E have separate static ownership.
Renderer0AAF:1D95..1E59 preserves signed division for the flying animation,
strict playfield bounds, one scroll wrap, damage-flash consumption and the
shared defeat-angle updates. Original update controls execute actual aim,
rank/performance tune, ordinary/fixed-speed bullet allocation, gather3stack,
collision wrapper, score bonus, HP bar, activation/reset and render helpers.
Audio, point popup/item/spark consumers and hardware drawing remain adapters;
shot damage is injected at the real collision boundary.

Entry lasts20 ticks. Four attacks alternate with pauses and twelve mirrored
flight directions observed at DATA:1790. After dash12, the original keeps
moving until a boundary exit rather than selecting another attack. Boundary
exit still performs shot collision; a lethal shot on that frame takes the
original defeat/reward path. Defeat clears only horizontal velocity. The native
core throws for a corrupt new-dash index>=12 instead of reading adjacent host
memory. Ordinary retained Normal/Lunatic controls at both ring-cursor seeds
complete without that exception; corrupt-state equivalence is excluded.

The actual target produces15,886 complete state/event/draw records from9,792
input controls:2,568 updates,7,200 renders, eight activation/reset controls each
and eight retained shot/timeout sequences. State comparisons include all22
actor bytes, three private bytes, shared defeat angle, score, RNG cursor, full
bullet/gather templates,440 bullet records,16 gather records and ordered events/
draw geometry. Current Linux/Wine/optimized UBSan/actual Windows replay the same
independent trace. The original was reexecuted before the new contract target's
static-link repair; the current Linux contract executable remains identical.
Reference replay verifies target/fixture/trace identities and record counts;
it does not claim to reexecute original code. Hook rejection propagates, and
a disposable output-byte mutation fails the comparator.

Stage loading validates resources/STD before actor mutation, consumes353 next
process LCG draws, keeps MAIN generation2 and publishes resident/resource2.
Stage slots initially append16 BFT and four BMT images, replacing the preceding
bank. Pre-dialog cleanup installs ST02.BB1's six32x32 images and ST02.BB2's
twelve64x64 images. BB2 supplies the new active palette. Independent Python
FAT/PAR/CDG decoding checks106,880 opaque Elly portrait pixels across eight
Normal/Lunatic Reimu/Marisa shot/idle routes. A disposable checked-pixel mutation
fails the comparator. File loaders are request adapters in the original CPU
setup; these asset controls are not complete original VRAM comparisons.

Sixteen contracts and240 BMPs/268 counters agree Linux, Wine, optimized UBSan
and actual Windows. Prior168 BMPs/188 counters stay identical to v1269. Dialog
freezes actors/invincibility/RNG and the completed Elly frontier remains held.
Windows test-target DLL loading initially failed because its declaration came
after the static-link/warning loops; it now participates in both loops. All17
package PE executables import only Windows-provided DLLs. Windows builds use
MinGW13 cross-compilation; actual Windows execution is separately observed,
not a native Windows compiler claim. GNU8.4 builds Linux and optimized UBSan.

```sh
python3 port64/verify_midboss3.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-midboss3-contracts \
  --output-dir .analysis/port64/midboss3-control
python3 port64/verify_stage3_resources.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --exe .analysis/port64/linux-live-v1251/th04-port64-midboss3-contracts \
  --frames .analysis/port64/verification-stage3-v1270-final/stage3-linux \
  --output .analysis/port64/stage3-resource-control/receipt.json
```

Runtime batch manifest:
`416e8079931e7754318f7abc2176762951a3d22212a2590fd965518b9de922e7`.
Current manifest after a CTest-only registration correction: `322e213a739262231351902ee294c0bdd582b84f6abd1f88d93cb3dafb0c0a2e`.
`control-review.json` confirms all51 executable bytes are unchanged and the
16 CTest contracts pass Linux/UBSan; the runtime receipts keep their original
batch manifest above. No gameplay source changed in that correction.

Receipts: `.analysis/port64/midboss3-v1270/{target-live,integration-review,negative-live,native-windows-receipt,native-windows-setup,native-windows-core,windows-export-receipt}.json`,
`core-linux-final/receipt.json`, `core-{linux,windows,ubsan}-replay-final/receipt.json`,
`setup-{linux,windows,ubsan}-replay-final/receipt.json`, and
`.analysis/port64/verification-stage3-v1270-final/receipt.json`.
Windows root native EXE/launcher use the v1270 preview;21 other existing files
remain identical. No GUI was launched. Elly battle/later stages, player death/
Bomb, complete HUD/audio, Ending and persistence remain unported. The DOS source
and exact acceptance states are untouched. Semantic remains stopped; next port
Elly's retained setup, foreground, backdrop/tile ownership and battle.


## Elly battle and departure integration

The v1271 native window continues through Stage3's genuine pre-dialog at frame
9202, Elly's entrance, scythe/orbit and all attack groups, defeat, post-dialog,
clear bonus and the 416/488-frame departure. It holds at the actual Stage4
resource request. Semantic readability stays stopped once sufficient for the
next native slice; clarify only a concrete ambiguity. DOS source and exact
acceptance are unchanged.

Observed pinned MAIN ownership is13A9:7ECC..8C3D (scythe/helpers/dispatcher),
0AAF:7322..73DA (foreground),7757..777E (previous-position invalidation),
777F..77E6 (background), and13A9:A6F6..A7B4 (Stage3 setup).
The background generator's1154:0D2F alias has the same file extent; the executed
identity above is used in runtime records. Separate scythe jump destinations
819C..81AB, gather alignment83A2/table83A3..83B2 and dispatcher tables8C02..8C3D
are data ownership, not executable instructions. Original08F6:2F6C..2F79 executes
its unrolled fill;12,288 CPU write addresses independently establish the
32,128,384,256 rectangle. This does not prove physical GRCG color/VRAM behavior.

The original scythe has an unsigned16-bit clock, byte angle/speed and signed
turn. It runs before the Boss phase dispatcher and uses raw shot damage with
against-boss=false to reduce only vertical velocity; Boss body hits use true
and truncate returned damage to a byte. Native integration supplies separate
callbacks with the shared shot-score/spark consumers in their original order.
Entrance advances the Boss clock twice; the orbit uses previous.x as radius.
Phase0 sets the blue component of palette0, and phase2 clears it. Attack gather
calls use gather-only allocation, retaining the entity's bullet-template fields.
These details were resolved by target CPU controls rather than DOS refactoring.

256 retained setup controls compare the complete24-byte Boss,16 additional and
48 explosion bytes, hitbox and timeout. Original setup leaves all19 private
scythe bytes, orbit clock and pattern group untouched. The native first Stage3
load uses fresh MAIN BSS for those private fields; this is not a claim that
Stage3 setup resets them. Preceding Kurumi HP/endHP/angle and other untouched
Boss/explosion metadata are retained; stage-common globals have separate reset
ownership. The pre-dialog already installs six32x32 and twelve64x64 battle
sprites and the BB2 palette.

Independent original CPU expectations cover9,329 controls/39,297 complete
state/event records:2,958 scythe,288 orbit,6,075 dispatcher controls and eight
retained sequences across all four ordinary ranks with injected damage0/19.
Each no-shot Boss-only sequence departs after6,523 ticks; damage19 after971.
These sequences omit ordinary pool updates/rendering; native full-stage
integration is checked separately. Native foreground compares5,316 controls
and background compares11,264, including signed clock boundaries, scythe bounds,
explosion/flash metadata,64x64 invalidations and copied BB pointer.

The first comparison exposed gather allocation copying a bullet template.
After correcting gather-only ownership, the final builds replay the independently
recorded original expectations. `full-cpu-linux/original-reference.json` is a
target-only receipt, distinct from native candidate passes and the retained
initial mismatch. Native replay validates target/fixture/trace identity; it
reports original_cpu_reexecuted=false. Foreground/background and retained setup
execute the original again for each of Linux, Wine and optimized UBSan.

17 native contracts and336 BMPs/372 counters agree Linux, Wine, optimized
UBSan/bounds and actual Windows. The preceding240 BMPs/268 counters remain
identical to v1270. Eight Normal/Lunatic Reimu/Marisa shot/idle scenarios each
capture twelve new checkpoints: entrance/scythe assembly, BB transition, orbital
attack/scythe flight, two group transitions, defeat, post-dialog, bonus, fade and
Stage4 request. Post-dialog freezes actor/invincibility/RNG ownership; MAIN
generation2 survives and resident stage advances to3 while resource stage stays2.
Three additional advances at the pending request do not simulate again.

A disposable modified output token is rejected at checkpoint0/field0. Each
original callback rejection is propagated. An attempted background-only
asset/screenshot comparison is deliberately not accepted: retained shots,
sparks and items can overdraw even the top rows. Shared native asset decoding
and prior portrait checks still pass, but no new full-screen original VRAM or
unobstructed-background pixel assertion is made.

Replay from the native worktree:

```sh
python3 port64/verify_elly.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-elly-contracts \
  --output-dir .analysis/port64/elly-cold/core
python3 port64/verify_elly_setup.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-elly-contracts \
  --output-dir .analysis/port64/elly-cold/setup
python3 port64/verify_elly_render.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-elly-contracts \
  --output-dir .analysis/port64/elly-cold/render
```

Use the Windows `.exe` with `--runner wine`, or the optimized UBSan build for
same-source controls. `port64/verify.py` includes all five natural scenario
suites; `port64/verify_windows.ps1` executes the17 contracts and all336 checkpoints
on actual Windows. Receipts live below `.analysis/port64/elly-v1271/`:
`target-live.json`, `core-{linux,windows,ubsan}-final/receipt.json`,
`setup-{linux,windows,ubsan}-final/receipt.json`,
`render-{linux,windows,ubsan}-final/receipt.json`, `negative-live.json`,
`native-windows-{receipt,core,setup,render,background}.json`,
`integration-review.json` and `windows-export-receipt.json`.
Cross-build receipt: `.analysis/port64/verification-elly-v1271/receipt.json`.
Source manifest: `464f6e89661d8adf112ef12645b6c5ae01d1d00f8f7141d686e828853bd7641b`.

Windows root native EXE/launcher use v1271; the versioned package contains18
checked static x64 PE executables.21 other existing DOS/HDI/config/font/build
files remain identical and no GUI was launched. Linux uses SDL2; Windows uses
Win32/GDI. No native Windows compiler or GUI frame-pacing claim is made.
Stage4 onward, player death/Bomb, complete HUD/audio and Ending/save remain
unported. Next bounded work is Stage4 resources/actor reset/midboss and its
character-dependent pre-boss gate.

## Stage4 resources, midboss and NPC dialogue

The v1272 native batch advances the preceding Elly frontier. Stage4 loads only
after the actual Stage3 departure request, preserves MAIN generation2, consumes
the common353 process draws, installs ST03's28x32x32 plus8x64x64 sprites,89 MPN
tiles and STD/MAP streams, and runs to the genuine pre-boss dialog at frame12808.
The first route uses KAO3/Marisa and ST03BK2; the second KAO2/Reimu and ST03BK.
The dialog clears the stage sprite bank, loads the character-dependent BBT
sheets/palette and holds after completion. Reimu/Marisa Boss battles remain the
next owner; the port does not manufacture a replacement fight or completion.

Observed MAIN ownership is13A9:14E8..1ABE (four pattern helpers and dispatcher),
0AAF:2316..23A2 (foreground) and13A9:A7B5..A931 (retained setup). The dispatcher
ends with RETF at1AA9;1AAA is alignment and1AAB..1ABE is its phase table. Stage4
midboss starts2800 at144,-32 with4,2 pixel velocity and1200HP. Entrance takes48
updates and clears only its selected private counters. Fresh DATA2134:185E has
an aim-toggle value1; setup does not reset it. The shared HP bar, flash, angle
and other untouched22-byte actor fields retain preceding-stage state.

First termination, whether defeat or timeout, re-arms the same actor for5600 at
240,-32 with-4,2 velocity,1200HP and frame0. Second termination clears active/HP
without rearming. Defeat rewards30 minus completed patterns, emits shake before
explosion setup, and dropsBomb first/one-up second. All four pattern helpers
preserve signed clock IDIV, byte wrap, tune-before-fixed-shot overrides,
retained aim state and separate shot requests. Homing precedes movement; a
lethal hit after a bounds exit still wins. Foreground preserves small-point
clipping,64x64 append slots156..163 and read/clear flash ownership.

Carpet0AAF:3F9A..3FF3 is a near RET4 helper; its last two bytes are the RET
operand, not alignment. Callback3FF4..40FD owns ring corrections, lighting
columns/dirty flags, initial full invalidation and final callback disable.
Target DATA2134:190C..199B supplies image offsets and199C..1A5B the8x24 mask.
The lower seams use columns18/20, unlike the quarantined DOS source candidate's
19/21. Cel5 leaves only left column2 already lit; right column21 stays2. Native
source derives the meaningful tile IDs/masks with explicit asymmetry, and an
independent full-table comparison checks every entry before CPU controls.
This batch does not change or reopen the deferred DOS carpet exactness unit.
Native full redraw consumes the same25x24 ring; physical dirty-page transients
remain outside the accepted rendering scope.

12,362 independent original CPU controls produce31,410 complete actor/private/
HP/RNG/score/template/440-bullet/16-gather state and ordered event/draw records.
16 retained sequences cover Normal/Lunatic, injected damage0/10, ring cursors
0/255 and first/second encounter starts. Original expectations are preserved
before native reference replay; each replay explicitly reports no original
reexecution. Each of the three builds independently reexecutes436 carpet
controls/4,012 records and256 retained setup controls. Original callback
rejections propagate. Independent archive pixels verify NPC portrait0 and the
active character-dependent palette in all eight native routes.

The initial carpet checkpoint0 mismatch disproved regularized seam columns.
A separate core control588 failure exposed an observer counting9512 and its
inner regular wrapper twice; the native pool/template was already correct.
Only the observer was corrected, retaining the failed comparison. Neither
failure is relabeled a pass. These findings stay separate from the selected
original CPU and native integration results.

18 contracts and432 BMPs/476 counters agree Linux, Wine, optimized UBSan/bounds
and actual Windows. All preceding336 BMPs/372 counters stay identical to v1271.
Eight natural Normal/Lunatic Reimu/Marisa shot/idle routes exercise actual STD
waves, both activations and two defeats or timeouts, carpet disable, NPC resource
selection and dialog freeze. Recorded player keys track the midboss on shooting
routes; no hit, phase, score or spawn is injected there. Dialog and final hold
do not repeat simulation. Native screenshots are independently guarded by
assets/state, not treated as complete original-game VRAM equivalence.

Replay with `port64/verify_midboss4.py`, `port64/verify_carpet.py` and
`port64/verify_stage4_resources.py`; each accepts the pinned `--target` and
`--exe`, plus `--runner wine` for the Windows cross-build. Resource checks also
need `--hdi` and `--frames` from `--stage4-screenshots`. The midboss reference
replay uses `--reference-dir` only after a complete original run passes.
`port64/verify.py` and `port64/verify_windows.ps1` include all six natural suites.
Receipts live below `.analysis/port64/midboss4-v1272/` and
`.analysis/port64/verification-stage4-v1272/receipt.json`.
Manifest: `0bae5caad45928c0ca67c3420ee9fff3dcd2c34b8a411dc8a7a992b83ab55888`.

Windows root native EXE/launcher use v1272. The versioned package contains19
checked static x64 PE executables;21 other root DOS/HDI/config/font/build files
remain identical. No GUI launched. Windows executes a MinGW cross-build;
Windows-host compilation, physical hardware and GUI pacing are not claimed.
Stage4 NPC Bosses onward, player death/Bomb, complete HUD/audio, Ending and
persistence remain unported. Semantic stays stopped unless a concrete ambiguity
requires a bounded clarification. Next implement the actual NPC Boss owners.


## Stage4 Reimu state and orb core

v1273 ports MAIN Reimu dispatcher13A9:B91B..BE2F, ten attack producers,
AE87/AF21 movement, AFBB gather intro, B0A1/B0FC orb allocation, B163 orb
update and B8E8 palette pulse. It adds a native core owner; GUI rendering and
activation remain the next batch. The GUI still holds after Stage4 pre-dialog
at frame12808, and the Marisa Boss owner remains unported.

Fresh target review separates AFBB..B077 code, B078 alignment, B079..B0A0
case keys/destinations, and B91B..BE2F code from BE30..BE43 mode tables and
BE44..BE5D phase destinations. DATA2134:BCFA is signed angle delta, BCFB orb
pattern and BCFC the single trail flag aliased by both old visibility names.
BCFD is alignment; BCFE..BD17 is the26-byte template. B204..B543 holds32
records. DATA24B6/24B7 start at0 and hold the alternate angle/pulse direction.

Native records use explicit fixed widths, wrap and signed shifts. Moving
allocation retains spin time, angle speed and padding; spinning allocation
retains velocity and padding. Released or unknown nonzero orb flags still run
raw shot/player collision that update. The raw shot adapter is independent of
against-Boss damage. Unsigned wrapped rectangles preserve boundary behavior.
The entrance has a double clock increment; hit wrappers own ordinary phase
increments, while defeat staging advances separately. Score/drop/clear and
shared RNG consumption order remain guarded, including discarded angle draws.

6,678 original CPU controls produce62,514 complete state/event records.
Eight retained sequences cover four ranks with injected damage0/19, visit
phases0..12/254/255 and reach departure in12,716/1,245 updates respectively.
Native GNU, Wine, optimized nonrecovering UBSan/bounds and actual Windows PE
execution compare every recorded field against those independently generated
expectations. Reference replay explicitly reports no original reexecution.
Original shot/video/audio/item/point consumers are bounded adapters; retained
sequences advance this Boss only and exclude complete stage/render/pacing.

1,024 retained Stage4 setups independently execute the original across four
ranks and256 markers for each of the three builds. Complete BOSS24/additional16/
explosions48/hitbox/timeout and private3/template26/pool832/initialized2-byte
retention are checked; callback fields are BCD8 update, BCDA segment and BCDC
foreground. Native preparation currently assumes the first fresh MAIN Reimu
encounter; it does not promise repeated-setup private-state retention.

The first native short comparison fails at2402 field24: candidate blue ball76
and special129 differ from original57/128. Original also supplies red ball61
and no-special255. The repaired full comparison passes; the original failure
remains failed. An initial scratch setup used wrong character/rank addresses,
then a candidate pointer check confused segment and offset fields; only those
observers changed. An original zero-divisor control confirms flag/spinTime and
other selected writes precede IDIV; native throws after those writes and retains
the angle. A full pool does not execute the division. The initial aggregate
comparison also rejects source drift while candidates are repaired; its
separate target-only reference remains valid. Final frozen-source replays pass.

19 contracts and432 existing BMPs/476 counters agree Linux/Wine/actual Windows;
all preceding checkpoints remain identical to v1272. A versioned20-static-PE
validation package lives in `port64-preview/v1273`; all23 recorded root files,
including existing native EXE/launcher and21 DOS/HDI/config/font/build files,
remain unchanged. No GUI launched. Windows executes a MinGW cross-build;
Windows-host compilation, physical hardware, full game and DOS exactness are
not claimed.

Replay `port64/verify_reimu.py --target TARGET --exe CONTRACT --output-dir NEW`
and `port64/verify_reimu_setup.py` with the same options. Use `--runner wine`
for the PE build. A full original run produces `original-reference.json`; only
then use `--reference-dir` for a hash-checked complete native replay. Receipts
live below `.analysis/port64/reimu-v1273/`: `target-live.json`,
`core-full-first/original-reference.json`, `core-{linux,windows,ubsan}-final/receipt.json`,
`setup-{linux,windows,ubsan}-frozen/receipt.json`, `zero-div-original.json`,
`native-windows-{core,setup,receipt}.json` and `integration-review.json`.
Cross receipt: `.analysis/port64/verification-reimu-v1273/receipt.json`.
Manifest: `38e0289f882c6867b0f4849b32cf84091fa6236481318892009a99db92d24abe`.

Next connect Reimu foreground/trail/rolling-orb rendering, the shared NPC
backdrop and actual Marisa-player battle gate; then port the Marisa Boss and
later stages. Semantic remains stopped unless a concrete ambiguity arises.


## Stage4 Reimu battle and rendering

v1274 connects the verified Reimu core to the actual Stage4 Marisa-player
pre-dialog handoff. Boss setup consumes the retained Elly metadata and four
rank parameters; there is no substituted Marisa Boss. The GUI's other character
stays at its real pre-battle gate. Main state owns body shots with
against-Boss=true and orb shots with against-Boss=false. Orb damage is discarded
while ordinary shot consumption/score/sparks still execute. Shared frame prefix,
gathers, explosions and score drain run once per simulated frame. A repaint
reads cached draw requests and cannot age explosions or clear damage twice.

Observed MAIN0AAF:8347..83A2 draws32 orb slots in ascending order, accepting
nonzero flags and signed centerY>-256. Absolute screen coordinates are
SAR(centerX,4)+16 and SAR(centerY,4); sprite base plus
`((stage_frame+slot)&7)>>1` uses the original rolling call. Foreground
83A3..846E draws the previous raw Boss sprite in B/I planes with flagsFFC6,
then the current sprite.136 alone animates with frameMod16/4. Damage selects
the white FFC0 draw and is consumed below phase254; phase254 uses the large
sprite and255 has no body/orb draw. Shared small/big explosions follow.

The B/I trail writes alpha-covered pixels as destination index OR9, retaining
R/G. Reversing RGB loses plane identity when palette colors duplicate, so the
Reimu frame keeps palette indices through composition and post-dialog capture.
Actual original SUPER1PLANE0000:2838 and rolling0000:2D3E execute against
all12 64x64 Reimu and eight32x32 orb BFNT images, eight X alignments, retained
16-color backgrounds and seven negative/top/bottom Y positions.640 controls
compare complete640x400 indexed surfaces:163,840,000 pixels. The shadow models
GRCG output ports and visible A800:0000..7CFF writes; it does not emulate physical
page/scroll timing or aliasing outside that visible plane. Negative rows are
outside visible VRAM; only bottom overflow rolls to row0. Invalid extreme
coordinates remain outside this pixel claim.

Observed shared NPC backdrop0AAF:77E7..7873 divides signed phase clock by8,
truncates toward zero and stores AL as the BB cel. Phase1 cels0..7 use stage
tiles plus BB, later cels use the256x256 CDG at(96,72), color1 filler and BB.
Phases2..253 use the picture and filler. The BB consumer paints one bits with
color15 instead of invalidating zero-bit tiles. Filler13EA..1424 writes top and
bottom384x56 borders and left/right64x256 borders; actual CPU write addresses
match75,776 pixels. Phase0/255 signed clocks and254 retain their tile behavior.
Host full redraw replaces the original dirty-copy hardware.

9,188 original foreground controls compare ordered body/trail/orb/explosion
requests, damage consumption, complete private/template/pool retention and
explosion aging/flash clocks.5,888 original backdrop controls compare call
order, signed clocks, byte cels and BB pointer copies. GNU, Wine, optimized
UBSan and actual Windows native builds reproduce the full original expectations.
Original production and hash-guarded native-only reference replay are labeled
separately. Earlier6,678 Reimu core controls/62,514 records still pass all four
hosts;1,024 retained setups pass Linux and actual Windows.

Eight natural Normal/Lunatic Marisa-player A/B shot/idle scenarios enter through
title selection and the complete preceding stages. They capture phases0..12,
defeat, post-dialog, clear bonus, fade417 and next-stage489 without injecting
damage/phases/spawns/RNG. Idle routes visit every attack. Post-dialog freezes
simulation and RNG, bonus/fade/departure occur once, resident stage advances to4
while loaded resource stage remains3, and the Stage5 request freezes pending
actors/RNG/score until its resource owner exists.144 new BMPs/152 counters agree
Linux/Wine/optimized UBSan/actual Windows.19 contracts and576 total BMPs/628
counters agree Linux/Wine/actual Windows; all old432 BMPs/476 counters remain
identical. This is headless deterministic coverage, not GUI pacing or an
original ordinary-route equivalence claim.

The versioned20-static-PE package is `port64-preview/v1274`. Root Windows
`th04-port64.exe` and `start-th04-port64.bat` are refreshed after comparison,
with21 DOS/HDI/config/font/build file hashes unchanged. No GUI is launched;
MinGW cross-building and actual Windows execution are distinct observations.
Death/Bomb/full HUD/audio/Ending/save and later stages remain unported.

Replay foreground/background using `port64/verify_reimu_render.py --target
TARGET --exe CONTRACT --output-dir NEW`; only after an original run succeeds,
use `--reference-dir ORIGINAL_DIR` for a complete hash-checked native replay.
Use `port64/verify_reimu_pixels.py` with the same three options plus `--hdi HDI`;
`--runner wine` selects PE execution. `--reimu-screenshots DIR` runs the eight
natural routes. `port64/verify.py` and `verify_windows.ps1` include those routes.
Receipts are under `.analysis/port64/reimu-render-v1274/`; the cross-platform
receipt is `.analysis/port64/verification-reimu-render-v1274/receipt.json`.
Native source manifest: 10c0073624a213552cdf27bf6ee58ac663f27a8f7a77646232cdf63a4fe35127.

The user-requested cleanup removes superseded CMake and native Windows build
outputs and archives old BMP/large text with verified lossless gzip.18.53 GiB
was reclaimed before this batch's final validation. Original and compressed
hashes and removed build identities are in `cleanup-receipt.json`; current
builds, original targets, databases, toolchains, fonts, DOS products/images and
v1273 CPU references are retained. Before reusing a compressed historical
private file, restore it with `gzip -d -- FILE.gz`. Native changes do not promote
or invalidate DOS exact acceptance. Semantic stays stopped; next port slice is
the distinct Stage4 Marisa Boss.

## Stage4 Marisa core

v1275 ports the Reimu-player Stage4 Marisa Boss core, four auxiliary bits,
all ten attacks, movement, body/bit collision, HP rewards and defeat/departure.
It is a separate native owner; the GUI still holds at the pre-dialog frontier
until its foreground and backdrop are connected. The root Windows playable
EXE/launcher remain v1274. Broad semantic work stays stopped.

Fresh hash-attested MAIN review covers segment13A9:2F8A..422E, including
20 code extents and three dispatcher tables, and DATA:1A5E..1A65 HP values
220,400,280,450.32 retained26-byte custom records are explicit; Marisa owns
only the first four. Private DATA:432E..4347 fields and retained templates
are separate from common BOSS state. Code addresses become explicit dispatch
tokens, with an unknown active callback rejected instead of cast to a host
pointer. Pinned target SHA-256 is
077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b;
provenance remains candidate-local-attested.

Body damage truncates to BYTE before division by the previous update's
alive-bit count plus one. Bit damage retains WORD signed-wrap behavior and
uses the raw against-Boss=false consumer. Body hits, pattern selection and
firing occur before current bit destruction/movement and packed center writes.
Dead bit records still receive the original all-four distance/angle mutations.
Mode7 calls the phase-entry helper twice, including duplicate clock64 sounds.
Once-tuned templates retain the original angle/origin mutation order.

The original flystep13A9:30F5..3174 has IDIV divide-by-zero and quotient
overflow cases. Four independent original CPU failures and native contracts
cover both axes and sequential writes: a Y failure can leave the X velocity
committed. Controlled attack1/2 states with last-alive clock148 and current
clock152 reach duration12 and IDIV at3117. This is a controlled-state hazard,
not a reproduced natural player route. The core reports that original failure;
GUI integration must choose and test an explicit portable runtime policy.

7,759 original CPU cases compare87,031 complete state/event records across
four ranks, empty/full/sparse pools, retained bytes, signed boundaries, all
ten seeded attacks, and eight complete boss-only sequences. Without damage,
each rank reaches departure after15,411 updates; damage19 uses1,080 updates.
The traces include full440-bullet/16-gather/96-spark pools, templates, RNG,
common BOSS/explosions and private bit state. Actual original shared helpers
execute; damage/audio/video/item/point consumers are bounded adapters.
Initial CPU production is archived separately from final hash-guarded native
reference replay. Each final replay also executes the four original divide
controls afresh. GNU, MinGW under Wine, optimized UBSan and actual Windows
agree on every record.1,024 original retained setup controls per build verify
common BOSS, callbacks and retained private26/template26/pool832/initializer
bytes. Setup itself does not reset those records; native private defaults
require a first encounter or explicit caller seeding.

20 contracts pass, and576 existing natural BMPs/628 counters agree across
Linux, Wine and actual Windows with every v1274 checkpoint unchanged.
The Linux GUI binary is unchanged; all23 Windows root files are unchanged.
21 static PE validation products live in `port64-preview/v1275`. Windows
execution is observed; Windows-host compilation and GUI pacing are not claimed.
No DOS source, exact acceptance, physical hardware or complete game claim changes.

Replay `port64/verify_marisa.py --target TARGET --exe CONTRACT --output-dir
NEW` for original CPU production. Only after that succeeds, use
`--reference-dir ORIGINAL_DIR` for a complete identity-checked native replay.
`port64/verify_marisa_setup.py` uses the same three required options.
`--runner wine` selects PE execution. Default Marisa contracts additionally
exercise callback rejection and original divide failure behavior.

Receipts under `.analysis/port64/marisa-v1275/`: `boundary-review.json`,
`original-divide-failures.json`, `original-caller-divide-failures.json`,
`producer-attestation.json`, `core-linux-full/original-reference.json`,
`core-{linux,windows,ubsan}-accepted/receipt.json`,
`setup-{linux,windows,ubsan}-accepted/receipt.json`,
`native-windows-{core,setup,receipt}.json`, and `integration-review.json`.
Cross receipt: `.analysis/port64/verification-marisa-v1275-accepted/receipt.json`.
Native source manifest:
c7619d2c5e51200ff508ebd6057bea44b2e8c309462f668da931594a6c43cb91.
Next connect Marisa rendering and actual pre/post-dialog gates, then Stage5.
Player death/Bomb/full HUD/audio/Ending/save remain pending.

After recording the final comparisons,4,064 v1275 validation BMPs are archived
with verified gzip readback, reclaiming another2.83 GiB. Receipts and CPU
fixtures remain live; `media-archive-receipt.json` records every original and
compressed SHA. Restore a private BMP path with `gzip -d -- FILE.bmp.gz`.

## Stage4 Marisa battle and rendering

v1276 connects the Marisa owner to the actual Reimu-player Stage4 pre-dialog
handoff. Both characters now play their respective NPC battle, post-dialog,
clear bonus and departure, then hold at the Stage5 pending-resource request.
Main state owns raw bit shots with against-Boss=false and body hits with true.
Shared gathers, score, frame prefix and explosion updates run once per simulated
frame; repainting consumes cached requests and cannot clear damage or age
explosions again. The native preview still lacks player death, Bomb, complete
HUD/audio, later stages, Ending and save.

Fresh MAIN0AAF:419E..4280/4281..42F0 review and original CPU controls prove the
ordered body, line, four bit and shared explosion requests. The body uses the
raw sprite without an animation offset; damage selects white FFC0/alpha plane0
and is consumed only below phase254. The packed alive centers form an open
chain for two bits and close for three/four, color9, before drawing the slots.
Bits require nonzero flag and signed centerX>-256,<6144 and centerY>-256,<5888.
Visible nonzero WORD damage selects rolling white and resets that WORD; hidden
slots retain damage. Slots4..31 and all private26 bytes stay untouched.

Expansion can move line endpoints outside the viewport. The shared older ray
consumer required in-screen endpoints, so direct reuse could fail during an
ordinary GUI repaint. Marisa now follows original0000:079A..080C clipping and
1562..16FE line rasterization: the actual stage rectangle is32..415/16..383,
inclusive. Clip X before Y, signed IDIV toward zero, then draw the existing
16.16 accumulator line from the clipped endpoints. Clipping the finished raster
instead changes boundary rounding.1,522 original CPU write-mask controls cover
both directions, corners, edge points and wholly rejected lines. These are
selected controls within ordinary coordinate bounds, not a general extreme
16-bit coordinate or physical GRCG color/aliasing claim.

13,606 original foreground controls compare ordered requests, complete
private26/pool832 retention, visible damage consumption and shared explosion/
flash clocks;5,888 shared NPC backdrop controls verify signed eight-frame cels,
BB pointer copies and call order. All eight64x64 Marisa BFNT images from
ST03B21.BBT and four32x32 bit images from ST03B22.BBT execute original normal
and white SUPER/rolling put routines0000:2F54/2838/2D3E/2B78.1,344 controls
compare344,064,000 complete indexed pixels across eight X alignments, retained
16-color backgrounds and seven signed top/bottom positions. Normal body does
not roll; bit puts do, with white coming from alpha plane0. Negative rows are
outside visible VRAM and only bottom overflow rolls. GRCG ports and visible
A800 plane writes use a bounded software shadow; page/scroll/timing and aliases
outside the visible surface are excluded.

Independent original producers are frozen separately from final native-only
reference replays. Linux GNU, MinGW under Wine, optimized UBSan and actual
Windows agree on all state/draw/background/line/pixel expectations. Final render
replays also regenerate all1,522 original line controls; final core replays
regenerate four original divide failures.7,759 Marisa core controls/87,031
records and1,024 retained setup controls still pass on every host.

Four fresh stage_state_init0AAF:73DB..74A5 controls execute actual REP STOSD:
all832 custom bytes clear while private DATA432E..4347 is retained. Initial
loaded private26 bytes are zero. Stage4 setup remains a separate common BOSS
reset, retaining Elly metadata. Native first encounter uses those initial
private defaults; do not generalize this to later reentry without explicit
retained owner state. Gameplay enables an explicit portable policy for attack1/
2 flystep durations12/13: extend them to14 to avoid the original zero divisor.
Default core comparisons leave this disabled, and native policy contracts
verify both callers separately. Every other duration and strict flystep error
behavior stays unchanged; no natural original-route fault reproduction claim.

Eight natural Normal/Lunatic Reimu-player A/B shot/idle routes start from title
selection and traverse all preceding stages, actual Marisa attacks/bit pool,
post-dialog, bonus, fade417 and next-stage489 without injecting damage, phases,
spawns or RNG.162 new BMPs/170 counters agree across Linux/Wine/UBSan/actual
Windows.20 contracts and738 total natural BMPs/798 counters agree across hosts;
all preceding576 BMPs/628 counters and earlier menu/shooting captures remain
identical. Dialog and the Stage5 frontier freeze simulation/RNG. This headless
coverage is separate from GUI frame pacing and original ordinary-route equality.

21 static PE validation products are in `port64-preview/v1276`. After complete
readback, the native GUI EXE/English launcher alone replace the root Windows
preview;21 DOS/HDI/config/font/build files remain identical. No GUI is launched.
Windows execution and MinGW cross-compilation are separate observations.
DOS source and exact acceptance are untouched. Semantic remains stopped.

Replay `port64/verify_marisa_render.py --target TARGET --exe CONTRACT
--output-dir NEW` for original foreground/backdrop/line controls; only after
that succeeds use `--reference-dir ORIGINAL_DIR` for complete guarded draw/
backdrop replay (line controls still execute the original CPU).
`port64/verify_marisa_pixels.py` takes the same options plus `--hdi HDI`.
`--runner wine` selects PE execution. GUI natural routes use
`--marisa-screenshots DIR`; aggregate drivers include both NPC routes.

Receipts under `.analysis/port64/marisa-render-v1276/`: target-review.json,
stage-reset-controls.json, producer-source/manifest.json,
line-producer-source/manifest.json, render-linux-full/receipt.json,
pixels-linux-full/receipt.json, render-{linux,windows,ubsan}-accepted/receipt.json,
pixels-{linux,windows,ubsan}-final/receipt.json,
core-{linux,windows,ubsan}-accepted/receipt.json,
setup-{linux,windows,ubsan}-accepted/receipt.json,
native-windows-{core,setup,render,background,line,pixels,receipt}.json,
integration-review.json and windows-export-receipt.json.
Cross receipt: `.analysis/port64/verification-marisa-render-v1276-accepted/receipt.json`.
Native manifest:3adf253ed25e0a48be20efd71e94d70ad0de70864755b752b156cd0d003bc000.
Next port Stage5 resources/midboss/boss; reopen semantic only for concrete
ambiguities needed by that implementation.

Final validation media (4,785 files: BMPs and the redundant native pixel stream)
are losslessly archived after hash/counter readback, reclaiming3.66 GiB.
`media-archive-receipt.json` records all original/compressed SHA-256 values;
original CPU pixel references, fixtures and current builds remain live.
Restore private media with `gzip -d -- FILE.gz` before an old-path replay.


## Stage5 resources, stars and Yuuka pre-dialogue

The native GUI now consumes the actual Stage4 departure request and continues
through Stage5 STD waves, the scrolling star layer and both characters' Yuuka
pre-dialogue. Sixteen Normal/Lunatic, Reimu/Marisa, A/B-shot, shooting/idle
routes run 6,080 Stage5 simulation frames each. The GUI then holds at the
ordinary Yuuka battle boundary; that Boss owner is the next implementation.
Semantic work remains limited to concrete port ambiguities.

MAIN `13A9:A932..A9EB` disables the midboss callbacks and sets start frame 60000.
Its `boss_reset` retains HP/endHP/angle, additional bytes 1..15 and explosion
metadata; setup overwrites only position/sprite/hitbox, interval byte0 and
three star centers. Actual `midboss_reset` also clears HP and active; it retains
other actor metadata. 1,024 original CPU controls compare complete 24-byte boss storage,
16 additional bytes, 48 explosion bytes and 22-byte midboss storage. Five separate original
activation controls confirm the null callback set still becomes active at 60000;
this is a metadata probe, not a natural route reaching that frame.

The bounded original session case4 arm `0AAF:05E4..0653` independently confirms
BSS4.CD2, ST04.BFT, ST04BK.CDG, ST04.BB, ST04.CDG and ST04.MPN request order.
There is no BMT append. Stage5 initially owns 12 sprites at 128..139 and its BFT
palette; dialogue replaces them with ST04.BB1's one 64x64 sprite and BB2's
eight 48x96 sprites, ending at 137. Sixteen independent archive portrait/palette
checks compare 197,728 opaque pixels after the dialogue resource replacement.
File and hardware consumers are bounded adapters; the session arm is entered
after bootstrap, not a complete original session execution claim.

Stars start at Q12.4 centers at 320/40/190 pixels, move 4 pixels per completed frame,
and wrap once at 400. `0AAF:40FE..4168` skips updates during phases 1..253.
Signed WORD addition/SAR and one-row correction preserve malformed-state edge
requests; the physical raster accepts ordinary placements only. The invalidator
`4169..419D` records 96x80 boxes at the preceding center. 1,820 actual CPU star/
invalidation controls include signed edges and 800 trajectory checkpoints.

Original `130E:063A..06BB` ORs CDG source plane B into destination plane I/E000,
with bottom-up rows and physical 400-row wrapping. It preserves other colors;
a four-plane opaque sprite replacement is wrong. 504 actual CPU controls compare
16,128,000 complete plane bytes across aligned left edges, wrap points, display
origins and retained color backgrounds. Native lower-color/OR invariants also
pass. This flat visible VRAM model does not prove physical aliases/pages/scroll
hardware or frame pacing. Host redraw replaces the original dirty rectangles.
Cached star requests make repaint and blocking dialogue side-effect free.

Linux/Wine/actual Windows pass 21 contracts, 850 total natural BMP checkpoints and
926 counters. The 112 new Stage5 BMPs / 128 counters also agree under optimized
UBSan/bounds; all 30 preceding image/counter groups remain identical. Dialogue
and the pending Boss boundary freeze simulation, both RNG owners, score and
star centers. This is a bounded native frontier, not full-game or DOS exactness.

Receipts are under `.analysis/port64/stage5-v1277/`; `final-linux/receipt.json`
contains the fresh original producer and independent portrait checks.
`session-arm.json`, `null-midboss-activation.json`, `target-review.json`,
`integration-review.json`, and native reference-consumer receipts retain their
scopes. `test-config-continuity.json` records a final CTest-only argument fix:
all 22 products stayed byte-identical after three incremental rebuilds, and the
proper 21 test invocations passed. Earlier scenario/reference receipts keep their
original source manifest; the explicit continuity receipt bridges to the final
manifest 581547d4f74da59a984ad83f6a247bdc38735b923820e9765b8621a31b9a2115.
No historical receipt is relabeled as a new run.

Replay the component claim with:

```sh
python3 port64/verify_stage5.py --target /path/to/pinned/MAIN.EXE \
  --hdi /path/to/legal/zun.hdi --exe /path/to/th04-port64-stage5-contracts \
  --output-dir .analysis/port64/stage5-controls
```

Optional `--frames` names the 112 Stage5 BMP directory and enables independent
portrait checks. `--stage5-screenshots DIR` on the main executable generates
sixteen natural routes from the title; no injected phase/damage/spawn/RNG.
Windows v1277 exports only the GUI/English launcher and retains v1276 backup;
21 root DOS/HDI/config/font/build files stay unchanged. The native preview
still lacks player death, Bomb, complete HUD/audio, subsequent Bosses/stages,
Ending and save. DOS exact ledgers and maintained DOS source stay unchanged.

After final readback, 3,078 private validation BMPs are losslessly archived,
reclaiming 2.15 GiB. `media-archive-receipt.json` records every original and
compressed hash; restore the historical image paths with `gzip -d -- FILE.gz`
before replaying image comparisons. Original CPU references remain live.

## Thick-laser state and graphics producer

The v1278 dependency batch ports the complete two-slot laser owner into
`port64/thick_lasers.{hpp,cpp}`. MAIN 13A9:22E4..243D supplies initialization,
24-byte template transfer, first-free allocation, lifecycle and collision;
0AAF:37D3..3970 supplies the ordered graphics producer. Original target identity,
fresh database attestation and raw instruction review precede the CPU controls.
The DOS sources and accepted exact extents are unchanged. Target provenance
remains `candidate-local-attested`.

The native record explicitly names Q12.4 origins, pixel radii, signed WORD
clocks and all retained bytes. Initialization clears only the two actor flags
and scratch flag/clock/radius/speed. Template transfer retains the four bytes
after the origin and all other metadata. A full pool makes no allocation or
sound request. Transitions reset the clock and then increment it; the final
shrinking frame also increments after becoming free. Unknown nonzero BYTE
states preserve the original unsigned collision gate. The hit latch is retained
until the owning game frame clears it, and invincibility is consumed elsewhere.
Each shift/add/sub wraps before signed comparisons. Collision is narrower than
the displayed radius and begins below half the rounded cap.

The graphics producer preserves SAR4 coordinate flooring, signed IDIV width
rounding, upper-only quarter-width clamp, original outer/middle/white layer
ordering and unconditional GRCG disable. The outline successor is a WORD;
color 255 requests 256. Draw commands record the original FAR callee arguments,
including signed edge requests. This establishes command equivalence, not
circle/box/vline pixel equivalence, physical VRAM or frame pacing. Pixel
consumers and Yuuka foreground/background require separate controls when the
battle is joined.

Independent original CPU execution passes 8,464 cases and 13,975 checkpoints:
64 retained initializations, 64 full template copies, 144 allocations, 4,851
state/collision controls, 3,332 draw controls and nine retained lifecycle
sequences. Each checkpoint compares all 72 storage bytes, hit latch and ordered
sound/graphics requests. GNU Linux, static MinGW under Wine, optimized
UBSan/bounds and an actual PowerShell Windows process agree. Original callback
rejection and independent fixture-identity/trace-byte/extra-record negatives
are required and pass. The final source manifest is
`05e8bd69c1dc36bee294f661affce9e49db3ed5fbfa02c78c1d833dddea060be`.

All three incremental builds pass 22 CTests. Their 22 preceding Linux and UBSan
executables are raw-identical; all 22 preceding MinGW executables differ only
at their COFF timestamp and associated checksum. No previous GUI scenario is
relabelled as a new run, and no byte-exact DOS claim is made. Aggregate Linux/
Windows verification now requires the 23rd product and new laser contracts.
Root Windows game/launcher/saves/HDIs remain v1277. Only the new laser validation
program, fixtures, frozen manifest and verifier are exported under
`port64-preview/v1278-laser-controls`; no GUI launched.

Replay from the native worktree root:

```sh
cmake --build .analysis/port64/linux-live-v1251 --parallel 4
cmake --build .analysis/port64/windows-live-v1251 --parallel 4
python3 port64/verify_lasers.py \
  --target ../../targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-laser-contracts \
  --output-dir .analysis/port64/yuuka5-v1278/laser-linux-final
```

Receipts live under `.analysis/port64/yuuka5-v1278/`: `target-review.json`,
`producer-source/manifest.json`, `laser-{linux,windows,ubsan}-final/receipt.json`,
`native-windows-receipt.json`, `oracle-negative-controls.json`,
`windows-link-continuity.json`, `previous-binary-continuity.json`,
`integration-review.json` and `windows-test-export.json`. The raw continuity
receipt deliberately reports Windows differences; the separate full-file
comparison proves their exact header-only locations. Original references and
current builds remain expanded. Next: Yuuka's phase/attack dispatch, then its
rendering and ordinary Stage5 battle join. The GUI still stops after pre-dialog.

## Stage5 Yuuka core and seven attacks

The native `yuuka5` owner now implements MAIN13A9:243E..2F89: the movement
transition, sweep/cloud/gather/speedup-ring/aimed-spread/laser-burst/mirrored
attacks and ordinary boss phase dispatch. The original extent includes two
alignment bytes, four gather cases, twenty laser cases, two mode tables and
nineteen phase destinations. Target/header/relocations and a fresh root Ghidra
attestation precede execution. DOS product source and exact acceptance remain
unchanged; provenance stays `candidate-local-attested`.

Named attack/state fields expose retained ownership. Movement wraps the WORD
coordinate difference before signed division by64; its caller advances the
clock and skips shot damage during movement. Entry refreshes only bullet
origin before motion. Early pair exits subtract800 from the next threshold;
late pairs retain it. Gather timeout bypasses the hit wrapper, whereas the
final phase advances/hits before evaluating its1000-frame bonus cutoff.
Default defeat dispatch omits the laser/HUD tail. The VM callback is represented
as a null/retained dispatch token, without treating a16-bit FAR pointer as a
native address. Phase0 writes that token and clears the midboss countdown.

Original shrinking-circle calls use0AAF:1BA6, not the adjacent growing entry;
mirrored-stream setup writes special-motionFF. Cloud counters and private tone
wrap as BYTEs; published palette tone remains a WORD. Bullet spawn contact and
laser contact share a player-hit BYTE: new contact writes1 even over a retained
127. The native join preserves that write while retaining the bullet owner's
separate bool. The game frame must clear both representations at its boundary.

Fresh original CPU production and GNU Linux comparison pass7,330 fixtures and
69,652 checkpoints:1,620 isolated moves,2,408 helper edges,3,259 dispatcher
edges,35 complete attack sequences across five rank settings and eight retained
whole-boss controls. Each Easy/Normal/Hard/Lunatic win/timeout control visits
phases0..18/254/255 and reaches the departure request. Timeout controls traverse
both pair attacks and all four mode tokens. These controls retain all boss,
additional/private, template, bullet/gather/spark/explosion/laser storage,
shared counters, VM classification and ordered requests. Injected shot damage
and downstream circle/HUD/item/point/dialog/audio/delay consumers are explicit
adapters; ordinary actor updates, render and actual stage loading are absent.
This is not a completed native Stage5 gameplay claim.

Static MinGW under Wine, optimized UBSan/bounds and an actual PowerShell Windows
process match the independently produced records. Three comparator mutation
controls, callback rejection and invalid native argument checks pass. All three
incremental builds pass23 CTests and validate24 ELF64/staticPE products each.
All23 GNU predecessors remain raw-identical. All23 preceding MinGW programs
differ only in COFF timestamp/checksum. Nine UBSan predecessors are identical;
fourteen differ after recompilation, so no raw continuity is claimed for those.
Fresh UBSan execution of sixteen preceding Stage5 routes preserves112 image
hashes and128 counters; their media are losslessly gzipped with readback checks.

The final source manifest is
`ce458897179e6fb05588a575119e651d07ca067d3bdcfaee7cbf3468fdef523a`.
Root Windows game/launcher/saves/HDIs remain v1277. Only validation PE, fixtures,
manifest and PowerShell/results are exported under
`port64-preview/v1279-yuuka-controls`; no GUI launched. Next is Yuuka foreground,
backdrop and laser raster validation followed by the ordinary Stage5 battle
join. Semantic work remains stopped except a concrete port ambiguity.

Replay from the native worktree root:

```sh
cmake --build .analysis/port64/linux-live-v1251 --parallel 4
cmake --build .analysis/port64/windows-live-v1251 --parallel 4
python3 port64/verify_yuuka5.py \
  --target ../../targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-yuuka5-contracts \
  --output-dir .analysis/port64/yuuka5-v1279/yuuka-linux-final
```

Use a new output path when repeating a producer. Receipts under
`.analysis/port64/yuuka5-v1279/` include `target-review.json`, frozen
`producer-source/manifest.json`, `yuuka-{linux,windows,ubsan}-final/receipt.json`,
`native-windows-receipt.json`, `oracle-negative-controls.json`,
`previous-nonwindows-continuity.json`, `windows-link-continuity.json`,
`preceding-stage5-ubsan-review.json`, `integration-review.json` and
`windows-test-export.json`. The non-Windows raw comparison deliberately records
UBSan differences; its fresh scenario receipt is separate evidence. No physical
PC-98 timing/pixels, GUI FPS, full-game or DOS exact claim is made here.

## Stage5 Yuuka foreground and raster controls

`yuuka5_render.cpp` now owns MAIN0AAF:3DB3..3F7E foreground requests and
0AAF:7874..7900 backdrop decisions. Target review records11 complete physical
spans/1,535 bytes, including the rectangle's separate1076 shared return and
zoom31A2's self-modified immediates. Root preflight and fresh root Ghidra
header/entry/relocation/full-byte checks pass. Targets retain the local provenance
gap; portable results do not promote DOS source or exact acceptance.

Idle Yuuka draws two48x96 images separated by48 pixels. The64x64 entrance image
is also used during the three movement-disc transitions. Phase254 requests
factor3 zoom, distinct from the earlier shared large-sprite path. Damage resets
only in the visible entrance/idle white branches. Shared explosions advance
once after body requests; lasers draw afterward only below phase255. Cached
requests separate simulation/render ownership from subsequent repaints.

Backdrop phase1 divides the signed clock by4, then tests only unsigned AL.
Its picture branch clears the uncovered regions before CDG; stable phases use
common7667, which puts CDG before calling the retained filler. Filler1508/7578
covers X32..127/Y128..383 plus X32..415/Y16..127. The288x256 CDG at128,128
occupies the remaining region. BB/CDG/tile consumers remain their existing
separate owners; this batch compares their ordered requests and filler pixels.

An initial original CPU comparison rejects native sprite case864: normal SUPER
uses unsigned X SHR3 and a WORD row address. Negative X can produce a different
flat visible VRAM location, whereas host coordinate clipping drops those stores.
The corrected Yuuka normal/white raster preserves that address arithmetic.
Zoom reads the four color planes, skips color0 and paints clipped inclusive3x3
rectangles. Rectangle/vline endpoints are signed-sorted, then clip-origin
subtraction wraps as WORD; an ordinary host min/max clamp differs on extreme
inputs. Filled circles use the original midpoint horizontal spans and actual
stage clip32..415/16..383. Native disc raster rejects radii above512; pixel
controls cover0..180, while arbitrary WORD radii remain request-only evidence.

Final comparison passes9,936 request controls:4,446 foreground,5,120 backdrop,
370 original disc write masks. Another1,804 controls compare461,824,000 indexed
pixels:972 normal/white/factor3 sprite cases across all nine real BFNT images,
eight alignments, signed Y edges and selected negative X;832 rectangle/vline/
disc/filler cases retain16-color backgrounds and WORD color256. GRCG ports and
visible A800 writes use an explicit software shadow. General physical page/
alias/scroll/timing, GUI rendering and full Stage5 gameplay remain separate.

The initial frozen Oracle completed all972 original sprite screens before its
native mismatch. `original-pixel-production.json` records that production only;
it does not pass the rejected initial consumer. Final native consumers replay
those unchanged screens after the address fix. `producer-continuity.json`
proves identical ASTs for Original/Shadow/input/expected producer components and
identical bytes for five base/staging helpers. Final832 primitive screens and
all9,936 requests freshly execute original code. Each receipt records per-control
fresh-production/reference provenance; no old native pass is relabelled.

GNU Linux, static MinGW under Wine, optimized UBSan/bounds and an actual
PowerShell/native Windows process agree. The unchanged preceding Yuuka core
also replays7,330 fixtures/69,652 independent original checkpoints on final GNU
and actual Windows. Seven reference/output/native rejection controls plus
fresh callback rejection pass. Three incremental builds each pass23 CTests and
validate24 ELF64/staticPE products. All23 preceding GNU and23 UBSan programs
remain raw-identical;23 preceding MinGW files differ only at timestamp/checksum.
No prior GUI screenshot run is relabelled as a new run.

Final source manifest:
`7e410b8eff20d4f912f2c9e895a5c25e9e80e4c95ef18e388794d97810d91778`.
The root Windows GUI/launcher/saves/HDIs stay at v1277. Only diagnostic executable,
fixtures, assets, manifest and PowerShell/results are exported under
`port64-preview/v1280-yuuka-render-controls`; no GUI launched. Next is the ordinary
Stage5 battle join, including hit-latch clearing, palette/background phase
ownership and post-dialog/bonus/departure. Player death/Bomb/HUD/audio/Stage6/
Extra/Ending/save are still pending native work. Semantic work stays stopped
unless a concrete ambiguity prevents that implementation.

Replay from the native worktree root, using new output directories:

```sh
cmake --build .analysis/port64/linux-live-v1251 --parallel 4
cmake --build .analysis/port64/windows-live-v1251 --parallel 4
python3 port64/verify_yuuka5_render.py \
  --target ../../targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-yuuka5-contracts \
  --output-dir .analysis/port64/yuuka5-render-v1280/NEW-render
python3 port64/verify_yuuka5_pixels.py \
  --target ../../targets/th04/main.exe --hdi ../../runtime/images/zun.hdi \
  --exe .analysis/port64/linux-live-v1251/th04-port64-yuuka5-contracts \
  --output-dir .analysis/port64/yuuka5-render-v1280/NEW-pixels
```

Receipts under `.analysis/port64/yuuka5-render-v1280/` include target-review.json,
producer-source-initial/manifest.json, producer-source/manifest.json,
original-pixel-production.json, producer-continuity.json,
render-{linux,windows,ubsan}-accepted/receipt.json,
pixels-{linux,windows,ubsan}-accepted/receipt.json,
core-linux-accepted/receipt.json, native-windows-receipt.json,
oracle-negative-controls.json, previous-nonwindows-continuity.json,
windows-link-continuity.json, integration-review.json and windows-test-export.json.
`pixels-linux-final/pixel-mismatch.json` retains the rejecting initial observation.
Large redundant native outputs are gzip-archived with complete readback; current
original pixel/reference buffers stay live. Restore archived private output paths
with `gzip -d -- FILE.gz` before replay.


## Stage5 Yuuka ordinary battle and route-specific departure

The v1281 join activates the existing Yuuka owner only after the actual Stage5
pre-dialogue has installed the nine battle sprites. MAIN now owns its retained
boss metadata, two thick-laser records, shared bullet/laser contact latch,
shot damage, gather releases, homing, explosions and cached draw requests.
Background selection uses the pre-update phase/clock; palette0 and deferred
WORD tone come from the live Yuuka snapshot rather than the setup copy.
Phase1 uses signed clock/4 BB cels, white one-bit cells and the original
filler/CDG order. Ordinary battle freezes the stage star centers. Host full
redraw remains the replacement for dirty tile/EGC copies.

The first ordinary Easy route exposed a missing integration call: a default
laser scratch record has flag0, so add() copied inactive records and no laser
was drawn. Calling the original-shaped initialize() at stage initialization
arms LINE/radius/clock while retaining the other beam/scratch fields. The
rejected capture/log remains under development-routes; later routes observe
both line and wide lasers and transient contact writes. At each new simulation
frame, clear both representations of the shared player-hit latch; preserve it
through boss update and post-boss gather releases. Blocking dialogue resumes
the existing frame suffix, and repaint cannot clear the latch or age effects.
Player death remains a separate unimplemented consumer.

A correction to the preceding graphics discussion: phase254 actually resolves
patterns4..11 to MIKO32.BFT's eight32x32 death images. The64x64 entrance image128
is used in entrance/movement, not as the ordinary defeat zoom source. The v1280
factor3 pixel controls used the nine entrance/idle assets and therefore did
not independently cover this real death sheet. New --defeat-zoom-only controls
execute original31A2 with the eight32x32 images at16 edge/offset combinations,
comparing128 retained640x400 screens (32,768,000 indexed pixels). Historical
v1280 evidence remains scoped to its original asset set.

Original MAIN13A9:AD4D..AD6C tests stage_id4, continues-used BYTE DS4349 and
rank BYTE DS4348. Easy or any nonzero continues-used loads a separate bad
script, animates it and calls end_game_bad before normal clear bonus. Actual
0AAF:2411..242D mutates character offset3 of _DM04B.txt;0AAF:0CF4..0D1E writes
resident sequenceFE/type ASCII1, fades sound/palette and transfers to MAINE.
The independent stage/rank/continues/character matrix (96 invocations) executes these branches,
filename writes and resident publication; I/O/dialog/audio/video consumers are
explicit adapters and the transfer stops at GameExecl. Native comparison is
of the branch predicate. The natural Easy routes separately check the loaded
character-specific script, no normal bonus and no Stage6 request. Continue
statistics and actual native MAINE/Ending rendering have not joined yet, so the
GUI deliberately holds before that Ending call instead of inventing a result.

--yuuka5-screenshots traverses Stage1..4 naturally, then records18 Stage5
routes: sixteen Reimu/Marisa Normal/Lunatic A/B-shot/idle runs, plus both Easy
A-shot routes. It checks phases0..18/254/255, movement states, laser lifecycle,
all eight death frames, post-dialogue, bonus, fade417 and departure489, plus
simulation/RNG/resource/star invariants. The18 routes produce698 BMPs and716
counter lines; the16 ordinary routes request Stage6 while retaining resource
stage4 until that owner joins. Easy stops before Bad Ending. These are native
host scenarios, not independent original full-game or FPS evidence.

Receipts and source manifests live in .analysis/port64/yuuka5-join-v1281.
The Windows launcher remains English and describes the Stage6/Ending frontier.
DOS source, exact units and authored acceptance do not change. Semantic
readability remains stopped except for specific port ambiguities; Stage6 and
Extra, player death/Continue/Bomb, remaining HUD, audio, Ending and saved-data
I/O are still required for a complete native game.

## Stage6 resources, waves and pre-battle dialogue

The v1282 join carries a normal Stage5 departure into ST05.MPN/MAP/STD/BFT,
BSS5.CD2 and the character-specific _DM05/_DM15 script, without restarting
MAIN or replacing its process LCG. Stage6 has16 initial32x32 BFT images and14
MPN tiles. Actual MAIN13A9:A9EC..AA87 loads only ST05.BB: there is no BMT,
new CDG picture or stage/midboss callback. CDG16 and the colorfill pointer
retain their preceding Stage5 ownership. Boss HP/endHP/angle, most additional
bytes, big explosion and midboss motion/phase metadata survive reset; the
new position is192x80 and hitbox radii24x48. Rank0..3 replace additional[0/1]
with48/64/80/96 and1/1/2/4. Native rejects rank4 here; Extra uses stagex_setup.
The original18A6 rank selector indexes stack arguments unchecked, and rank4
reads the far return CS instead of providing a Normal fallback. The rejected
initial assumption is retained in setup-linux.log; it does not describe the
final executable.

Before dialogue, actual0AAF:2454..24CD releases CDG31, STD and MAP for stage5/6
only when speed0/back-page1. Native frees the STD actor program and MAP/order/
speed streams, retaining the displayed tile ring and MPN bank. A released
background stream rejects updates; a pending Yuuka6 owner freezes simulation.
The original complete scene consumes cursor1044/910, rather than stopping at
the first inner '#'. Both scripts load BB1/2/3, close boxes, release CDG1..31,
load BB4/5/6/7/9 and request ST05B music before the final outer '#'. Native
invalidates live CDG handles and guards future portrait/backdrop use; cached
read-only archive bytes are not treated as live handles. The final sprite bank
is128..189: seven48x96 sheets plus eight32x32 BB9 images. No inert free callback
or prematurely activated boss substitutes for these requests.

Independent original CPU controls cover1,024 retained setups,42 resource gate
cases and four complete dialogue traces (two characters x held/released,
1,895 ordered events). Linux/Wine/optimized UBSan agree; actual Windows consumes
the retained setup/four dialogue references. Independent archive pixels check
217,744 opaque portrait pixels in16 native captures. File, video, waits, audio
and free consumers are explicit original-CPU adapters. These controls do not
prove original whole-route video or physical PC-98 timing.

--stage6-screenshots traverses Stage1..5 naturally and then16 Stage6 routes
(two characters x Normal/Lunatic x A/B x shot/idle). All reach frame5198's
stopped scroll/dialog gate and complete the pre-battle scene.112BMP/128counter
records agree GNU/Wine/actualWindows/optimizedUBSan, including353 LCG reset
draws, resource generation, callback ownership and dialogue/repaint/frontier
freeze. The full cross-host GUI passes with all34 preceding image/counter
groups unchanged; actual Windows checks23 contracts/1,660 route BMPs. Three
incremental builds each pass23 CTests/24 products. This is native integration
evidence, not an original full-route or FPS claim.
The changed Stage5-contract consumer also replays the retained v1277 original
reference:1,024 setups/1,820 stars/504 rolling-plane cases pass GNU/Wine/UBSan.
Only CRT CRLF is normalized in text;16,128,000 pixel bytes compare raw per
host. This reuses the independent reference without reexecuting original CPU.

Receipts are under .analysis/port64/stage6-v1282. Producer manifest68eda7fd;
final manifest08a9891b differs only in verify.py receipt.limit prose. The
reporter-continuity receipt verifies the otherwise identical AST and all24
complete products per host unchanged; completed producer receipts keep their
original manifest. Windows publishes native EXE c2542286 and the English
launcher, retains previous-v1281 and leaves21 DOS/HDI/config/font/build files
unchanged. No GUI is launched. Completed validation BMPs are losslessly gzip
archived after readback; restore private images with gzip -d before replay.

Next: port Yuuka6's actual core, attack helpers, animation/entities and
checkerboard/background/foreground, then join the ordinary battle. Extra,
player death/Continue/Bomb, remaining HUD, audio, Ending and save I/O also
remain required. Semantic work stays bounded to ambiguities needed by those
owners; the complete native game is not finished.

## Yuuka6 animation and motion helpers

v1283 recovers the eight animation entries and four movement entries at
MAIN13A9:6933..6E76 into port64/yuuka6.hpp/.cpp. This is the next dependency
for the final boss; the ordinary GUI still stops before its first update.
No DOS source or accepted extent changes. Semantic work only clarifies the
specific state ownership needed by this native slice.

All animation entries share the signed16-bit animation_frame. They increment
before testing cels and retain the incoming sprite on a terminal frame;
close/open stamp flags1/2 on every call, while the other six only replace the
flag on completion. A switch of animation does not implicitly reset its clock.
The caller separately owns phase_frame. Teleport animation executes before
clock64's position/mirror publication and clock128's completion. Mirror X is
wrapped6144-X, enabled for any nonzero mirror state, then the state becomes2.
Flight uses two actual five-node BYTE angle paths; every sixth patterns residue
returns to the center through the teleport helper. The112 completion does not
also move. Only legitimate paths0/1 are accepted when the table is accessed;
malformed native snapshots reject instead of reading adjacent original DATA.

Horizontal motion adds wrapped velocity before inclusive48/336-pixel reversal,
never clamps, evaluates the actual integer sine/polar displacement and advances
its BYTE angle by2. Centering accepts the subpixel interval[3072,3088); entering
that interval by a step still returns false. A just-completed appearance also
returns false and retains aux_flag until the following call. Source comments
explain these timing and retention boundaries for the later battle owner.

Three fresh original-CPU producers each pass20,463 fixtures/36,045 full state
records against GNU, Wine and optimizedUBSan. The comparator includes all24
boss bytes,10 contiguous animation/mirror bytes, the mirror-state BYTE and
return BYTE. Every patterns BYTE, both valid flight tables, all256 wave angles,
animation cels/negative/overflow clocks, mirror modes and retained helper
sequences are covered. Actual vector/polar callees execute; no downstream
file/video/shot/audio/timing consumer is invoked. DS writes outside these
owners fail closed. Callback exceptions and a one-variable return mutation
are rejected. Actual Windows consumes the independent reference and matches
all36,045 records; it does not execute the original CPU producer.

The three incremental builds each provide25 products and pass24 CTests.
All24 preceding GNU and optimizedUBSan executables are raw-identical to v1282.
All24 preceding MinGW products differ only in COFF timestamp/PE checksum
bytes; the complete remaining bytes agree. The no-font GNU/Wine integration
smoke passes the updated verifier, including the new contract. This does not
repeat the previously accepted full dialogue/route image matrix or prove
whole-battle rendering, physical PC-98 timing, FPS or DOS exactness.

Receipts live in .analysis/port64/yuuka6-motion-v1283; final source manifest
269abf2dc769c274edd4b4c847b0f52700ea67653ddf44729789d14634823134.
accepted-{linux,windows,ubsan} retains original fixtures/compressed traces;
native-windows-review,product-continuity,build-receipt and integration-smoke
record the distinct checks. The initial CTest configuration mistakenly passed
the new executable name to the old Yuuka5 contract; ctest-linux.log retains
the failure, and all three accepted CTest replays pass after fixing that
registration. Initial producer9479b49b is retained without relabeling it.
The Windows v1283-yuuka6-motion package contains only the new private contract,
fixtures, manifest and control script, avoiding25 duplicate full executables.
The published GUI/launcher and protected DOS/config/saves remain untouched.

Next: chase-cross/safety-circle entity ownership, gathering and attack helpers,
then the dispatcher and foreground/checkerboard join. Extra, player death,
Continue, Bomb, HUD, audio, native Ending and score save remain unfinished.

## Yuuka6 cross and safety-circle entities

v1284 ports four bounded owners at MAIN13A9:65F7..6932 and
MAIN0AAF:7054..7129 into `port64/yuuka6_entities.hpp/.cpp`: cross allocation,
safety-circle initialization, update and drawing requests. The final-boss
dispatcher has not yet joined these owners to the ordinary GUI. DOS source,
acceptance and the published v1282 preview remain unchanged.

The original DATA:B204 pool contains32 records of26 bytes. Cross allocation
scans all32, but update and render scan31 and reinterpret the last record as
the circle. Allocation retains spare words, previous-position bytes and
padding; a last-slot cross must not acquire a separate native lifetime.
Circle centers use screen pixels, while cross centers use subpixels. Its
polar position subtracts literal32/16 from the pixel intermediate before
scaling by16. Converting those offsets into2/1 pixels changes the attack.

Cross motion precedes its inclusive offscreen flag clear. The iteration still
executes contact, homing and ordinary-shot damage after that clear; a kill
can replace flag0 with death flag16. Age below56 turns one BYTE step toward
the player, including+1 when already aimed exactly. WORD damage and signed
HP subtraction wrap, score accumulation wraps as DWORD, and kill requests
consume the actual shared spark/RNG owners before a BigPower item request.
These are ordinary shots, with against-boss=false; a boss damage callback
would incorrectly add Bomb damage. The raw player-hit BYTE is retained until
new cross or spawned-bullet contact writes1. The eventual live caller must
bridge that shared process state with the bullet/boss owners each frame.

Circle growth reaches136 before a separate frame switches to shrink, retaining
the shrink clock. Shrink emits the original paired stack/spread pellets and
tuned aimed rings, including rank/performance, pool saturation and clear/zap
branches. Death flags advance during rendering, so `prepare_render()` runs
once per simulated frame and `draws()` can serve cached repaints. The growth
draw deliberately leaves GRCG enabled; the ring draw disables it. The native
API publishes ordered graphics requests here, rather than claiming actual
sprite/circle pixels or physical video timing.

One fresh original-CPU producer passes6,089 fixtures/9,031 checkpoints against
GNU. Wine and optimizedUBSan consume its independently produced reference;
all three also execute a fresh five-rank MAIN0AAF:0312..03D1 switch-tail
probe. This verifies the actual indirect add/tune callbacks, including the
shared Normal/Extra tail, without running the preceding resident/file/score
initialization. Actual Windows consumes the same fixtures and agrees on all
9,031 full state/request records. It does not execute the original CPU.
Checks include832 custom bytes, complete440-bullet/96-spark pools, scratch
template, RNG/score/hit globals, ordered events and draws. Allocation793,
circle initialization112, update2,131, render3,041 and12 retained224-frame
sequences cover dense pools, signed/unsigned wrap and all raw flag BYTEs.
Actual polar/atan, spark/RNG, tune and bullet-spawn callees execute; ordinary
shot damage, graphics, item and sound consumers are explicit request adapters.
Callback exceptions and a one-variable comparator mutation reject. Existing
atan excludes INT16_MIN displacement; extreme movement fixtures use age>=56.
These controls do not establish whole-battle behavior, frame pacing or exactness.

Two rejecting runs are retained. The initial reference used Normal callbacks
for an Easy fixture; its checkpoint2393 bullet-count mismatch was an Oracle
context error, not evidence of a native gameplay bug. After fixing the context,
checkpoint2830 found a native shared-state defect: spawned-bullet contact
left an incoming hit BYTE127 instead of writing1. The repaired bridge detects
each spawn's new contact before restoring the bullet bool. The rejected
f40959a5 source closure and GNU product are retained together in
`contact-negative-source-and-product.tar.gz`, with their hashes recorded in
`contact-negative-identity.json`; the passing product has a distinct identity.

All three incremental builds provide26 x64 products and pass25 CTests each.
All25 preceding GNU/optimizedUBSan products are raw-identical. For all25
preceding PEs, restoring only the retained eight COFF timestamp/checksum bytes
recovers the complete previous SHA-256; no other byte changes. GNU/Wine
no-font integration smoke passes; the full preceding font/route image matrix
is not repeated. The actual-Windows private package contains only the new
entity contract, fixtures, manifest and streaming gzip control, avoiding
duplicated old executables or expanded250MB state traces. The published GUI,
launcher and21 protected DOS/config/save files remain unchanged; no GUI launched.
Root and native `scripts/ci.py`, tracking validation and `git diff --check`
pass. Native CI skips its absent private Ghidra project; the fresh root MAIN
database attestation is retained separately. The304 completed no-font BMPs
are losslessly gzip-archived with SHA-256 readback, reclaiming218MiB; current
builds, caches, original CPU references and user saves remain available.

Receipts: `.analysis/port64/yuuka6-entities-v1284/`, including `target-review`,
`root-ghidra-attestation`, `accepted-{linux,windows,ubsan}`, `native-windows-review`,
`build-receipt`, `product-continuity` and `integration-smoke`. Source manifest:
dce4e3835be08c885c02b928fe21831183c069f3b18fcda62c4f0fa5c0c517f6.
Replay with `python3 port64/verify_yuuka6_entities.py --target TARGET --exe EXE
--output-dir NEW`; add `--runner wine` for MinGW or `--reference-dir REFERENCE`
to consume the independently produced fixtures/trace.

Next: gather and attack helpers, then final-boss core and foreground/checkerboard
integration. Extra, player death/Continue/Bomb, HUD, audio, Ending and save I/O
remain required. Reopen semantic only for a concrete port ambiguity.

## Yuuka6 gathering and attack helpers

v1285 ports17 bounded entries at MAIN13A9:6E77..7951: five gathering entries
and twelve attack entries, including four sparse compare/jump tables. The
existing `yuuka6::System` owns the methods in `port64/yuuka6_attacks.cpp`;
`Gathering` and `Attack` select explicit behaviors without changing its stored
layout. DOS source and acceptance remain unchanged. The ordinary preview still
holds before Yuuka6's first update; this dependency batch does not publish a
new playable battle or launch a GUI.

The same gather and bullet scratch templates persist across calls. Gather-only
allocation retains the saved bullet fields except spawn_type0, and retained
velocity/spare bytes survive even on a full pool. Side gathering ends at the
left center; dual gathering ends at the mirror center. Later circles use the
original shrinking entry0AAF:1BA6, with ordered requests and color publication.
The helpers do not advance the attack clock or update allocated entities.
Animation executes before later branch/gather tests; a terminal attack may
reset phase_frame before the final gather call. Cached repaints cannot replay
these calls.

Attack comments explain special/fixed-speed spawning, distinct mirrored origin
and heading, two laser origins, retained speed growth, random consumption even
when cross allocation is full, and the BYTE rotation's outward/return ordering.
The rotating-ring initializer aims boss-minus-player, opposite ordinary aim,
before its16-unit rotation. The spin attack changes the second origin angle
without replacing the retained template heading. BYTE count/speed/angle and
signed WORD quotients preserve their original widths. New spawn contact writes
the shared player-hit BYTE1, including over an incoming127; the future core
must bridge it with the entity/laser/frame owners.

One independent original-CPU producer passes5,305 fixtures/39,757 checkpoints:
375 gather fixtures,4,822 isolated attacks and108 retained320-frame sequences.
The comparator includes35 boss/animation/mirror bytes,16 additional bytes,
circle color, hit/RNG/special globals, both templates, complete440-bullet,
16-gather, two-laser plus scratch and32-custom pools, and ordered requests.
Actual animations, vector/atan, RNG/tune/regular/special spawn, gather and
laser/cross/safety-circle allocation execute. Circle and sound consumers are
request adapters; spark/ordinary-shot ownership is also checked unchanged.
Sequences do not advance ordinary actors, pool updates, pixels or the battle
dispatcher. Five ranks, density, performance, clear/zap, raw flag/angle and
signed clock/coordinate boundaries are covered within the recorded domain.

The first control omitted BCC2, the special producer callback, despite setting
regular BCC0 and tune BCC4. Guarded execution rejected the resulting unrelated
code path at fixture388; this was an Oracle context defect. The corrected
five-rank switch-tail probe executes MAIN0AAF:0312..03D1 and checks all three
callbacks. A one-field BCC2 mutation reproduces the rejection. A separate zero
dual-spread-range control reaches original MAIN13A9:02F6 DIV WORD SS:[BX+2]
after two random samples; GNU/Wine/UBSan explicitly reject the zero divisor.
Native partial state is not exposed or compared on that exception. Existing
INT16_MIN atan and count-zero ring fault/portable-repair limits remain separate.

The fresh full CPU producer retains manifest8b4343e0. Final685c4c37 names
pattern constants, explains reverse aim and splits a terminal return to remove
a warning; its final header comment distinguishes attack completion from
`animate()` alone. All27 GNU/UBSan products match the already-passing ff96
files raw, and all27 PEs preserve every nonmetadata byte. The no-font smoke
keeps its ff96 producer identity, linked through `comment-continuity`; the
complete new GNU contract remains raw-identical to the8b43 producer. Final GNU,
Wine and optimizedUBSan consume the independently produced reference, each
also executing a fresh three-callback rank probe. Actual Windows consumes the
fixtures and agrees on all39,757 records. Original CPU is not executed on
Windows; do not relabel the retained producer as three fresh full replays.

Three incremental builds provide27 x64 products and pass26 CTests each.
All26 preceding GNU products are raw-identical; all26 preceding PEs retain
every byte outside the eight timestamp/checksum bytes. Of26 preceding UBSan
products,25 are raw-identical; the rebuilt motion contract differs and passes
the full retained independent20,463-case/36,045-record motion control. No
raw or debug-only equality is claimed for that changed file. The initial
all-products raw assertion rejects and remains retained. GNU/Wine no-font
integration smoke passes; the published v1282 GUI/launcher and21 protected
DOS/config/save files remain unchanged. The actual-Windows private package
copies only the new attack contract, fixtures and streaming gzip control.
Root and native CI pass; the root also freshly attests the MAIN Ghidra database.
All304 completed smoke BMPs are losslessly gzip-compressed after receipt-hash
and decompressed SHA-256 checks, reclaiming229,971,858 bytes. Current builds,
CPU references and protected files remain available; see `bmp-compression.json`.
No whole-battle, original pixels, physical timing, FPS or DOS exact claim.

Receipts: `.analysis/port64/yuuka6-attacks-v1285/`, including `target-review`,
`root-ghidra-attestation`, `development-linux-full`, `accepted-{linux,windows,ubsan}`,
`producer-continuity`, `native-windows-review`, `missing-special-context`,
`zero-angle-range`, `build-receipt`, `product-continuity`,
`motion-ubsan-regression` and `integration-smoke`. Source manifest:
685c4c37b677e42dfe0ae5105ac4c1e28437730bf38c4c47b1ac7536fae772c3.
Replay with `python3 port64/verify_yuuka6_attacks.py --target TARGET --exe EXE
--output-dir NEW`; use `--runner wine` or `--reference-dir REFERENCE` as needed.

Next: mirror hit-test and final-boss core/phase dispatch, then foreground and
checkerboard integration. Extra, player death/Continue/Bomb, HUD, audio, Ending
and save I/O remain required. Semantic stays bounded to concrete port ambiguities.

## Yuuka6 mirror and core dispatch

v1286 ports MAIN13A9:7952..799E mirror hit-test,799F..79EB phase transition,
and79EE..7ECB FAR dispatcher. The latter owns executable code through7E77,
three sparse four-case tables and one18-entry phase table;79EC..79ED is
alignment. `port64/yuuka6_core.cpp` calls the existing twelve attacks,
animations, movement, shared explosion/defeat, lasers and custom entities.
Ordinary GUI still holds before Yuuka6 update; no new GUI is published.

Mirror state2 uses ordinary shots with384x768-subpixel half-radii, stores the
returned AL as a BYTE and tests HP<0. Main-body AB48 checks the whole shot WORD
for audio, then ABBE truncates before damage/HP. Thus WORD256 sounds on the
main body but subtracts zero HP, while the mirror does not sound. A retained
wrong BYTE-conditioned native variant rejects against the actual original
complete record; corrected native matches. Shot/Bomb and ordinary callbacks
are separate. Neither callback's injected damage proves real shot consumption.

The dispatcher has no shared clock increment. Hit wrappers, hidden branches
and explicit transition arms each advance their own clock; an attack can
reset it before a hit. Random movement destinations are sampled on every call,
including frames without teleport. Dual-mode selection rejects repeats with
the same RNG. Phase transitions clamp bullet clear to20, restore the preceding
end HP and reset attack/animation state. Entity tail bridges raw player-hit,
pending-score DWORD and shot scratch around the existing owner; shared defeat
returns before laser/custom/HUD tail. Drawing and death-flag aging remain
separate and must occur once per simulated frame in the future join.

One fresh independent original producer matches3,137fixtures/90,702records:
252 mirror,960 phase transitions,1,917 isolated core and eight retained
Easy/Normal/Hard/Lunatic win/timeout sequences. Each traverses phases0..17
and stops on entry to254; zero-damage sequences take19,654/19,639/19,664/19,800
frames, damage19 sequences2,204. Checkpoints include35 boss/animation/mirror
bytes,16 additional bytes, complete bullet/gather/laser/custom/spark pools,
templates, explosions48, shot scratch, homing, VM/background tokens, HP,
palette/score/hit/RNG globals and ordered requests. Actual callees execute;
shots and sound/circle/HUD/point/item consumers are adapters. `stage_id=0`
is the recorded owner-only fixture context; short default255 clocks stop at63,
before the stage-dependent Ending branch. No whole-route or Ending I/O claim.

Initial Original adapter inheritance rejected a `super()` type check; the
correct MRO includes both attack and boss adapters. This is a control-context
failure, distinct from the native sound bug. Final verifier adds a one-byte
comparator rejection. Exact AST checks preserve Original/fixture/fixtures/seed/
execute from producer fcf45d46, and all28 products per host remain raw-identical.
Final GNU/Wine/optimizedUBSan consume that independent reference and freshly
check five-rank regular/special/tune callbacks. Actual Windows agrees all90,702
records under the retained fcf producer identity. Final source manifest:
2d4df41ae2fbe6c094723e8c0491291de7acf9f0271999ee69abdc343e6e0b54.

Three incremental builds pass27CTests/28x64 products each.25 preceding GNU/
UBSan products are raw-identical;25 preceding PEs preserve all nonmetadata
bytes. Two changed animation/motion and attack contracts pass their independent
36,045 and39,757 retained records on all three hosts. Those receipts keep the
fcf manifest, linked by verifier-only continuity. GUI/launcher remainv1282;
21 protected Windows DOS/config/save files remain unchanged. No pixel, physical
hardware/pacing/FPS, original whole-route or DOS byte-exactness claim.
Root/native CI pass. Two verified duplicate native outputs are removed,
reclaiming185,082,796 bytes; the original reference and WSL actual-Windows
records remain. `duplicate-cleanup.json` records hashes and the Windows restore
path. `build-review-final.json` checks all28 product architectures and hashes.

Receipts:.analysis/port64/yuuka6-core-v1286, including target-review,
root-ghidra-attestation,development-linux-full-callbacks,accepted-{linux,windows,ubsan},
native-windows-review,verifier-continuity,sound-word-negative,
build-review-producer and motion/attacks-{linux,windows,ubsan}.
Replay `python3 port64/verify_yuuka6_core.py --target TARGET --exe EXE
--output-dir NEW`; add `--runner wine` or `--reference-dir REFERENCE` as needed.
Next: foreground/checkerboard and ordinary final-battle join, then remaining
Extra/death/Continue/Bomb/HUD/audio/Ending/save owners. Semantic stays bounded.

## Yuuka6 foreground dispatch

v1287 ports MAIN0AAF:712A..72A5 (380 bytes) as a separate `Foreground`
owner. The original DATA46C3/46C4 flash counters are independent of the core
update dispatcher. A visible hit uses red on even parity, normal on odd parity,
then increments its BYTE counter and clears that body's damage. A frame without
hits retains parity. Hidden sprite0 preserves both damage bytes and both
counters, even with an active mirror. The optional auxiliary sprite precedes
the two body halves and the mirror. Sprite255's second half remains WORD256;
negative subpixel positions use signed SAR4 rounding rather than host division.
Red requests attest the original erase-mask0/planeFFCD arguments, distinct
from the custom crosses' white planeFFC0. Actual plane pixels remain separate.

Phase255 returns immediately. Phase254 emits only zoom factor3 and returns;
neither branch ages common explosions or dying crosses. Ordinary phases retain
small-explosion2D9C, big-explosion2E65, thick-laser37D3, custom7054 order.
`prepare_render()` consumes hit bytes and advances those render-owned states
once per simulation frame; cached `draws()` repaints do not advance them again.
Safety-circle GROW's mode/color/disc requests deliberately omit disable, while
its ring path includes disable. A separate render owner preserves the existing
core Snapshot layout and update ABI. These comments name original ownership
and widths without reopening general semantic work or changing DOS source.

One fresh original CPU producer matches3,522fixtures/4,458 complete records,
covering phase/hidden/aux/mirror combinations, flash BYTE parity/wrap, signed WORD
positions, original explosion controls, laser modes, all31 simultaneous custom
slots and24 retained40-frame sequences. Records include boss35/additional16,
explosion48, laser72, custom832 bytes, flash/damage/palette/hit globals and the
ordered8-field graphics requests. Original foreground and all four rendering
owners execute; sprite/zoom/circle/color callees are explicit request adapters.
Fresh callback rejection, one-byte comparator rejection and an actual two-input
body-parity control distinguish red from normal while mirror parity stays red.
The original reference is produced before native comparison and retains its
source manifest. Wine, optimized GNU UBSan/bounds and actual Windows consume
and match that independent reference. Windows does not claim original CPU
execution. Full raster pixels, physical PC98 page/alias/VRAM, frame pacing,
ordinary final battle and Ending remain separate requirements.

The three incremental builds pass28CTests/29products each. All28 preceding GNU
products remain raw-identical. Restoring eight retained timestamp/checksum
bytes recovers all28 preceding PE hashes.25 oldUBSan products are raw-identical;
the three changed motion/attack/core contracts pass36,045/39,757/90,702 retained
independent records. No debug-only or raw equality is claimed for those changed
products. All product architectures and compiler/cache identities are checked.
The no-font Linux resource smoke also passes. No DOS exact acceptance changes.
Source manifest: `0b47d197a1899f132dc4e2594b56c16670674d5493d629095df0419b07d6d2eb`.
Receipts: `.analysis/port64/yuuka6-render-v1287/`. Replay with
`port64/verify_yuuka6_render.py --target MAIN --exe CONTRACT --output-dir OUT`;
add `--reference-dir ORIGINAL_DIR` for a hash-checked consumer or `--runner wine`
for PE execution. Actual Windows uses the private
`port64-preview/v1287-yuuka6-foreground/verify-foreground.ps1` streaming gzip
control. GUI staysv1282; all23 published root game/config/save/script files
remain hash-identical. Next: actual foreground pixels, checkerboard/particle
background and ordinary final-battle join, followed by remaining complete-game
owners. Semantic remains stopped except for a concrete port ambiguity.

## Yuuka6 checkerboard and particle background

v1288 ports MAIN0AAF:7586..7632 checkerboard, 7901..7934 center clip,
7937..7970 wrap clip, 7971..7D8B particles and 7DC9..7E88 background prefix.
7D8D..7DC8 is jump-table data; adjacent alignment bytes remain separate.
No DOS source, authored-unit ledger or exact acceptance changes. The original
Japanese target remains candidate-local-attested.

`Background` owns 56 active Q12.4 shapes and a retained sentinel, BYTE state,
fade and palette latch, WORD pattern/flyout speed, symbolic clip callback and
opaque 16-bit BB resource tokens. It receives the existing shared random ring;
a private RNG would change subsequent combat. Initialization only occurs at
phase0 clock2 and consumes112 samples. Entry fade0 selects wrap for states0/8/12
and center for6/10; a same-frame transition retains that entry callback.
Transition arms may increment fade before their threshold and again in the
common tail. Incoming255 wraps before the comparison, while transition reset255
becomes0 at the tail. Palette-zero parity retains untouched components; the
late-state latch retains the previous palette after it sets.

The checkerboard preserves paragraph arithmetic, WORD offsets, BYTE pass count,
partial top rows and alternating dark columns. Its numeric store addresses never
become host pointers. Original flat visible writes include row384 below the
playfield: host playfield clipping would reject the independent pixel controls.
The mono16 kernel preserves unsigned X shift, WORD row offsets and visible-byte
filtering rather than host XY clipping. Every background update advances once;
cached requests and checker stores can repaint without consuming RNG or state.

One fresh original CPU producer passes2,220fixtures/5,711 complete state/request
records. These include two retained1,571-step caller-driven phase sequences,
clip boundaries, fade parity/threshold/wrap, palette latch, initialization,
negative entrance clocks, RNG cursor wrap and retained sentinel/resource tokens.
Actual RNG, atan/vector, clip and checker owners execute; state fixtures adapt
fill, BB and mono calls into ordered requests. Separately114 pixel fixtures
execute actual checker/mono/color kernels through an independent GRCG shadow:
80 retained checker frames and107 mono frames, including the eight actual
MIKO16 particle masks, all eight X alignments and selected signed WORD edges.
All187 full640x400 screen buffers agree byte-for-byte (47,872,000 pixel bytes
plus640 checker descriptor bytes). GNU, Wine PE, optimized UBSan/bounds and
actual Windows consume the same independent original reference. Each Python
control rechecks callback rejection; a one-byte comparator mutation rejects.
A fresh two-input incoming fade0/1 control changes the selected clip callback;
correct native records agree and swapping them rejects.

These controls do not prove combined BB/fill/particle composition, physical
PC98 VRAM alias/page/palette hardware, frame pacing, whole combat or DOS exactness.
Checker inputs are bounded to visible-layout paragraphs A850..AF6C; stored pass0
means256 passes in the implementation but is outside this pixel matrix. Existing
atan INT16_MIN displacement remains an explicit excluded/rejected input.

Three incremental builds pass29CTests/30 AMD64 products each. All29 previous
GNU and UBSan products remain raw-identical; restoring eight retained PE
metadata bytes recovers all29 previous PE full hashes. No cold DOS exact claim.
GUI/launcher stayv1282 and all23 published Windows root files are unchanged.
Only the private background contract package is added. Source manifest:
`aea4d05ef79705449c5883fe582861003528177a6cee6784b8a98c8ea8d0bf8f`.
Receipts: `.analysis/port64/yuuka6-background-v1288/`. Replay:
`python3 port64/verify_yuuka6_background.py --target MAIN --hdi HDI --exe CONTRACT
--output-dir OUT`; add `--reference-dir ORIGINAL_DIR` for a hash-checked consumer
or `--runner wine` for PE. Actual Windows uses private
`port64-preview/v1288-yuuka6-background/verify-background.ps1` with binary-stream
gzip capture. Root fresh Ghidra is READY; native private database replay skips.
Root/native CI and diff-check pass.
Next: actual foreground red/white/zoom pixels and ordinary final-battle join,
then remaining complete-game owners. Semantic stays stopped except for a
concrete native ambiguity; this dependency batch does not complete the port.

## Yuuka6 foreground sprite pixels

v1289 supplies `yuuka6::raster_sprite()` for the foreground requests accepted
in v1287. Normal, white and phase254 factor3 use the already controlled Yuuka5
kernel. Red reuses its alpha/WORD-offset walk and merges only destination bit1.
Observed MAIN0000:2838 takes planeWORD FFCD and emits GRCG modeCD/tileFF;
PC98 plane order B/R/G/I therefore enables red while retaining blue, green and
intensity. Filling indexed color2 would erase those three bits. The new source
comments make this ownership explicit; no DOS source or exact ledger changes.
Resolve each pattern to its actual sheet before drawing: all62 Stage6 body,
auxiliary and cross patterns128..189 come from ST05.BB1/2/3/4/5/6/7/9, while
phase254 death4..11 uses32x32 MIKO32 instead of the48x96 body sheet.

One fresh original CPU producer matches2,405 complete640x400 indexed screens,
615,680,000 compared pixel bytes. Controls cover all62 Stage6 images in normal,
white and red modes at all eight X alignments, selected vertical and signed
WORD edges, all eight actual death images at16 selected factor3 positions,
96 ordered six-sprite body/mirror/aux/cross overlap frames and62 retained
normal-then-red frames. Each screen retains destination pixels across its
ordered draw sequence; the original SUPER/ONEPLANE/ZOOM and downstream
color/rectangle kernels execute. BFNT alpha/four-plane staging is an explicit
input adapter; an independent GRCG shadow produces the reference, never the
portable raster. A target-only red/white pair proves destination color5 becomes
7 for red versus15 for white, and rejects a swapped screen. Fresh guarded
callback and one-byte comparator rejection also pass. GNU, Wine PE, optimized
UBSan/bounds and actual Windows consume the same independent reference.

The changed foreground contract also replays the existing3,522fixtures/4,458
complete state/request records on GNU/Wine/UBSan and actual Windows; the v1287
producer manifest remains attached to that reference. All three builds pass
29CTests/30 AMD64 products each. The other29 GNU/UBSan products are raw-identical;
restoring eight retained PE metadata bytes recovers all29 previous PE hashes.
No debug-only equality or cold DOS exactness claim. GUI remainsv1282 and all23
published Windows root game/config/save/script files remain hash-identical.
Only a private pixel-contract package is added.

Screens attest bounded visible kernel composition, not ordinary boss update/
foreground dispatch integration, safety-circle pixels, BB/background composition,
physical VRAM page/alias/scroll/palette hardware or host pacing/FPS. Selected
negative-X WORD offsets remain flat visible writes; factor3 uses original stage
clipping. Historical library exclusion/provisional zoom-boundary states remain
unchanged; a fresh raw view reaches zoom RETF8 at327A..327C inclusive.
Target provenance stays candidate-local-attested.

Source manifest: `81b816fd7b8c096832d304d615c50729fb096e037986c9f57569adcc1ff3ca9c`.
Receipts: `.analysis/port64/yuuka6-pixels-v1289/`, including original-linux,
accepted-{windows,ubsan},foreground-{linux,windows,ubsan},native-windows-review,
target-review,build-review and root-ghidra-attestation. Replay:
`python3 port64/verify_yuuka6_pixels.py --target MAIN --hdi HDI --exe CONTRACT
--output-dir OUT`; add `--reference-dir ORIGINAL_DIR` for a hash-checked consumer
or `--runner wine` for PE. Actual Windows uses private
`port64-preview/v1289-yuuka6-pixels/verify-pixels.ps1` and captures binary stdout
through streaming gzip. Root/native CI and diff-check pass; fresh root Ghidra
READY, native private database replay skips. Next: ordinary final-battle join
with the accepted core, entities, foreground and background owners, then the
remaining complete-game owners. Semantic remains limited to concrete ambiguity.

## Yuuka6 ordinary battle and Final Stage departure

v1290 connects the already controlled motion, attacks, entities, core,
foreground and background to the normal Stage6 dialogue completion. No stage
skip, seeded boss phase, forced HP or synthetic damage is used by the live
route matrix. The common Stage6 boss metadata and the same process/random
ring continue into combat; dialogue does not refill the ring or reset lasers.

The observed MAIN loop0AAF:0098..0212 calls the background before player,
shots, bullets and boss, with foreground after items/gather. The native join
keeps that order: background initialization/scatter draws from the shared
ring in the frame prefix; foreground consumes body/mirror hit flashes and
ages dying crosses once in the suffix. Host repaints consume cached draws.
The byte contact latch is bridged across bullet, laser and cross owners;
body hits use boss shots and mirror/cross hits use ordinary shots.

The host consumes the actual62-image battle bank, MIKO16 mono masks,
checkerboard stores and BB transition. BB0AAF:1426..14A2 uses DATA:BA8A color
and one-bit cells, not a freed CDG16 image. Normal/white/red/death zoom use
accepted sprite kernels; circle/disc and common explosion requests reuse the
existing native primitives. Complete physical PC98 page/alias/scroll/palette
composition is not independently proved by this live join.

The first natural run rejected `released MAP/STD streams updated`: dialogue
had freed those streams, but the frontend still advanced the map after the
first boss update. Keeping the release guard and skipping the released owner
repairs the real path. Every live matrix route now reaches the actual final
battle, including checker/particle updates, safety circles, crosses, mirrored
attacks, thick lasers and both death phases.

`update_final_departure()` owns the stage_id5 arm of13A9:ACB3..AE86. Tone60
precedes clock0 graze publication and all-clear9E06. All-clear disables score
extends; no post-dialogue is opened. At416 the original calls0AAF:0CC9
`end_game()` before the actor-frame suffix, leave fade and clock/homing
increment. The native frontend exposes a Good Ending request and holds there
until MAINE is ported; it does not flush pending score early or synthesize
MAINE statistics. The independent departure controls stop at that original
nonreturning call. A preliminary injected488 fixture followed the generic
next-stage arm, which is unreachable after that call; it is outside this
Final Stage natural-path contract, not accepted native equality.

Validation:

- Three incremental builds pass29CTest/30AMD64 products each. GNU retains19
  complete previous products; restoring only eight recorded PE metadata bytes
  recovers19 previous PE hashes. UBSan retains15 raw products; changed core and
  foreground consumers also replay their independent references below.
- Sixteen Normal/Lunatic, Reimu/Marisa, A/B, idle/real-shot routes cover
  phases0..17,254,255, the attacks and all-clear. The512 Stage6 images and528
  complete counters agree GNU, Wine, optimizedUBSan and actualWindows.
  Repaint controls guard frame/RNG, background particles/checker/palette,
  body/mirror flash, custom death ages and laser clocks.
- The public GNU/Wine verifier preserves all28 earlier v1282 image/counter
  groups. ActualWindows executes29 contracts and2,060 ordinary route images;
  its22 image/counter groups agree with the public replay.
- Fresh hash-attested original departure execution passes2,052 bounded calls
  on GNU, Wine and UBSan; actualWindows consumes those original records.
  Callback rejection and Ending-versus-fade mutation fail closed. All-clear
  math, full MAINE and original whole-route comparisons remain separate.
- Changed GNU/UBSan core products pass3,137 fixtures/90,702 complete retained
  original records; the original v1286 producer identity remains distinct.
  Changed UBSan foreground passes3,522 fixtures/4,458 retained v1287 records.

Manifest: `bbe0e09ba94269e1d659d25a83aa261f0e8130fc3903230cec82fc7ad4eba7a3`.
Receipts: `.analysis/port64/yuuka6-join-v1290/`, including target-review,
source-freeze, integration-final, previous-route-review, native-windows-review,
departure-{linux,wine,ubsan}, departure-native-windows-review, core-{linux,ubsan},
render-ubsan, build-review and deploy-receipt. Reusable CPU replay:

```sh
python3 port64/verify_yuuka6_departure.py --target MAIN --exe TRANSITION_CONTRACT \
  --output-dir NEW
```

Add `--runner wine` for PE. `--stage6-screenshots DIR` exercises the whole live
route through the Ending request; supplied HDI/font and recorded binary hashes
are required. Completed generated BMPs are archived losslessly with SHA
readback to keep the earlier cleanup effective. No FPS, complete-game, original
whole-route or DOS exact claim is made. Next owners are native Ending/save,
Extra, death/Continue/Bomb, remaining HUD/audio/config persistence. Semantic
work remains limited to an ambiguity that blocks one of those owners.

## MAINE Ending script and graphics owner

v1291 adds `cutscene::Script` and `cutscene::Scene` as native C++ owners.
`Script` preserves the three-digit/default parser, twelve-byte filenames,
WORD cursor wrap, mask order, Escape sampling and graphics/page/palette/audio
requests. Its clock separates release/press waits, explicit frame delays,
non-skippable palette fades and song-measure waits. A sound owner must explicitly
complete a measure wait; key input cannot stand in for song progress.
`Scene` owns both640x400 indexed graphics pages, the saved480x64 text-box
background, palette and current PI slot. It decodes supplied resources at
runtime and performs quarter selection, EGC mask copies, graphics-font effects
and gaiji drawing. The asset collection must outlive the Scene: its loaded PI
slot borrows a stable picture-map entry. No original font, picture, script or
executable is embedded.

Fresh execution of the pinned MAINE DIET wrapper at load1000/2000 recovers the
same62,414-byte payload and559 relocation sites. Packed SHA is670de6ba;
payload SHA is7495ae43. The active Ghidra database attests the packed wrapper;
the decoded function observations below use the hash-bound raw payload, not an
invented decoded-database attestation. Provenance remains
`candidate-local-attested`. Original0A05:07F7 dispatcher and0A05:0DAC animation
execute their own instructions in the control oracle. External consumers are
intercepted; original0CC7:058C font/effect kernels additionally execute against
an explicit supplied CGROM adapter in the pixel oracle.

Important target-specific behavior:

- The picture rectangle is160,64,320,200. The standalone DOS dispatcher
  candidate's left-zero constant cannot supply this native owner; a source name
  or historical acceptance is insufficient to attest its include context.
- MAINE samples key_det bit0010 for Escape. Frontend MAIN action masks require
  explicit translation. Ending text uses graphics page1, with no per-character
  delay; the interval controls the text-box mask passes.
- `k` waits without publishing the box; `@` clears both pages without replacing
  the saved background. Preserve both quirks when composing later flows.
- `_ED000.TXT` supplies the two-byte string ",4" too. Original halfwidth font
  effects operate on AL with WORD weights and a little-endian rotated store;
  aligned heavy/bold/black spill dots differ from fullwidth text. Native keeps
  these dots rather than correcting the original renderer.

Validation at `.analysis/port64/maine-ending-v1291/`:

- Eight actual scripts and ten synthetic controls at four held-input states
  produce72cases/86,614 complete ordered records, invariant across two original
  load segments and identical GNU, Wine and optimizedUBSan consumers.
- An independent NumPy raster consumes original requests and target mask words.
  Eight routes have twelve checkpoints each:192 complete indexed pages and96
  palettes/page-selection/scroll/tone states match on all three builds.
-264 full-frame font controls cover six fullwidth/ANK/space/kana strings,
  four weights, eight alignments and additional positions/colors. Both original
  relocation loads agree with each native consumer. The route gallery executes
  another1,025 per-route string/weight/align controls.
- Three incremental builds pass30CTest each and produce31AMD64 executables.
 28 prior GNU products are raw-identical;28 prior PE products differ only in
  timestamp/checksum.26 prior UBSan products remain raw-identical. The changed
  dialogue owner passes its independent original script/activation/font oracle;
  eight existing PI/UI/MAIN smoke fixtures retain their prior hashes.

`verify_cutscene_windows.ps1` executes the same binaries on actual Windows,
including all30 contracts,72 script streams,17 PI decodes,264 font controls
and192 pages/96 palettes. It compares complete bytes against the attested GNU
references and preserves the original producer receipts separately.

Replay from the native worktree:

```sh
python3 port64/verify_cutscene.py --target ../../targets/th04/maine.exe \
  --decoded-dir ../../port64/maine-ending-v1291/decoded-original \
  --hdi ../../runtime/images/zun.hdi \
  --exe .analysis/port64/linux-live-v1251/th04-port64-cutscene-contracts \
  --output-dir NEW-control
python3 port64/verify_cutscene_pixels.py --target ../../targets/th04/maine.exe \
  --decoded-dir ../../port64/maine-ending-v1291/decoded-original \
  --hdi ../../runtime/images/zun.hdi --font-bmp SUPPLIED-FONT \
  --exe .analysis/port64/linux-live-v1251/th04-port64-cutscene-contracts \
  --reference-dir NEW-control --output-dir NEW-gallery
```

PI decode is a separately regressed dependency: the complete decoder body is
unchanged except for external ownership. This gallery is not independent
validation of the original PI decoder or a physical PC-98 video capture.
Mask/font acceptance covers actual Ending inputs and the stated font matrix;
arbitrary hardware clipping, all unused font effects and real audio timing are
separate. No DOS source, exact/unit/function ledger or published Windows GUI is
changed. Next join MAIN's score/run counters and MAINE resource lifetime to this
owner, then implement Staff Roll, verdict and registration. The ordinary native
preview still holds at the Ending transfer; component success is not full-game
completion. Semantic work stays limited to concrete port ambiguities.

Final source manifest: `df9ce765c305847b34fd3eb3e0dd8bcfe9029d0a923d4ea8937d3f6cd3125262`
(196 files). `source-freeze.json` and `build-review.json` bind current sources,
all31 executables per build and the actual-Windows reference identities.
After verification,1,368 completed Wine/UBSan/Windows pixel/font files are
losslessly gzip-archived, reclaiming320.3MiB;116 active executable/Windows-root
hashes are unchanged. The current GNU reference gallery remains expanded.
`output-archive-receipt.json` records every member and readback. Restore an
archived output with `gzip -d -- PATH.bin.gz` before direct historical comparison.

## MAIN-to-MAINE Ending integration

The v1292 frontend continues ordinary MAIN into all eight Good/Bad Ending
scripts. The preceding v1291 component supplies the script/page/font owner;
this batch supplies the executable lifetime, resident publication and host
presentation. Staff Roll, verdict and registration are subsequent owners.

`run_statistics` copies the eight displayed HUD digits and cumulative run
counters. It deliberately excludes pending score, as MAIN0AAF:3CEE saves those
existing bytes before GameExecl0AAF:3D0D. Completed-frame statistics increment
at the actual tail, so the nonreturning Ending call excludes that suffix. STD
counts stop at the boss callback and survive Stage replacement. Stage reset now
clears item entities while retaining items_spawned; the target's complete nine
clear regions do not own MAIN DATA:2398. Headless checks use no host clock;
interactive slow-frame statistics sample host work in17,730,496ns periods.
That host sample is a backend approximation, not measured original PC-98 timing.

`maine::Ending` writes GOOD/FF/type0 or BAD/FE/type1 before song fade4 and the
mandatory MAIN blackout. The observed0000:0666 loop makes eighteen palette
calls over273 VSync waits; Escape cannot bypass it. Publication precedes the
native resource-release callback, which runs while the old MAIN generation and
LCG still exist. Entering MAINE then creates a fresh process-local LCG at1.
The original additionally frees an optional EMS handle after score publication
and before its other counters; native EMS storage is absent. Original release
order and execl's explicit failure return/stack path are checked separately;
those adapters do not execute a full DOS replacement.

MAIN host actions translate cancellation explicitly to MAINE key_det0010;
other held actions become a wait key. MAINE's unsigned song-measure comparison
requires actual reported progress when audio is active. The current inactive
backend executes the original minimum-frame fallback instead. Story graphics
use their shown/access pages, palette tone and scroll; old MAIN/TRAM resources
are gone. Window and headless frontends use the same owner.

Validation at `.analysis/port64/maine-join-v1292` includes:

- Original MAIN72 Good/Bad/EMS publication and cleanup-order controls;
 378 frame-counter wrap/unsigned-threshold vectors; the full fade loop.
- At decoded MAINE loads1000/2000,120 sound-mode/fallback/measure controls and
 24 palette-output controls. Palette bytes are RGB: redAC, greenAA, blueAE.
- Three fast incremental builds,31 AMD64 products and30CTest per host.
 Linux, Wine and optimizedUBSan each traverse24 natural menu/STD/dialogue/boss
 routes, covering two characters, actual A/B choices, Easy/Normal/Lunatic and
 idle/shot final battles. Each compares576 complete pages,288 palette/state
 checkpoints and288 RGB frames against the independently checked v1291 gallery.
 Actual Windows consumes the same resident/counter/fade and route references.
-442 original stage-reset/midboss seed controls and four native Stage1-to-Stage2
 routes. The reset consumer's executable bytes remain identical through the
 final GUI-only diagnostic-log edit. The complete9 original clear regions,
 retained353 process draws and cumulative item-spawn sentinel are checked.

The old fixture drivers pressed Right on the shot screen, which only responds
to Up/Down. Their B-labelled Stage4/5/6 paths were actually A; retain their
pixel/phase evidence with that narrowed input scope. This batch fixes all four
such drivers and asserts the real resident character/shot selection for the
new matrix. A separate negative finding corrects the v1291 PNG-only RGB
swizzle; its indexed pages/palette bytes and original font controls are intact.
The original indexed references and the new CPU palette controls drive current
RGB comparisons directly. Windows state streams useCRLF; compare their integer
records, while complete page/palette/BMP hashes remain strict. A source-snapshot
mutation guard also rejected development checks that spanned adding verifier
files; accepted frozen controls are stored separately.

No DOS source or exact ledger changes. Original targets remain
candidate-local-attested; decoded MAINE binds payload7495ae43, while its active
Ghidra database attests the packed wrapper. The reference PI decoder is a
separately regressed dependency. No physical PC-98 capture, full original-game
route, music synthesis, player-death/Bomb/Continue/Extra behavior, host FPS or
saved-score completion is claimed by this Ending batch.

The validated v1292 Windows preview is published under
`D:\Entertainment\Game\Touhou\th04-reconstruct\port64-preview\v1292-ending-join`;
root `start-th04-port64.bat` uses the new GUI. The versioned launcher uses its
own original HDI/font, while the root launcher retains the user's normal image.
Both English launchers state the Staff Roll frontier. Previousv1290 GUI/launcher
are retained and2,169 pre-existing Windows files outside the two authorized
native replacements keep their hashes. DOS launchers/products/config/saves are
unchanged; publication does not auto-launch the GUI.
After full readback,8,640 completed render buffers/BMPs are gzip-archived,
reclaiming3.21GiB;553 protected original-reference/active-binary/Windows-root
hashes stay unchanged. Original CPU traces and v1291 raw indexed references
remain expanded. Restore v1292 media using `gzip -d -- PATH.bin.gz` or
`PATH.bmp.gz` before direct historical consumers; the archive receipt records
every original/compressed digest.96 derived v1291 PNGs have correctedRGB
presentation with original indexed/palette hashes retained in a separate receipt.


## Staff Roll integration

The v1293 native MAINE owner runs the complete `staffroll_animate` sequence
for both Good and Bad Ending. `staff_roll` separates the ordered graphics/file/
sound requests from their host consumers; both the GUI and deterministic route
runner use the same owner. The preceding Ending graphics pages transfer once,
then its script/PI/text-box owner releases. MAINE generation, resident counters
and process RNG remain unchanged. Staff Roll releases its background snapshot
and six CDG slots, completes the final blackout and holds at verdict entry.

The dissolve producer preserves radial, diagonal and axis displacements,
unsigned angle wrapping, signed polar/SAR rounding and the original 63-frame
alternation. Fade and music waits remain blocking. Keys never skip Staff Roll;
active music requires a real reported measure, while the inactive backend uses
64/160-frame fallbacks. The resulting deterministic inactive-audio run contains
10,396 requests and 3,967 ticks. These are native scheduling counters, not
measured physical PC-98 timing or synthesized audio.

Two hardware details matter: `graph_copy_page(destination)` copies the opposite
page and leaves access on the destination; `BGIMAGER` restores WORD-aligned
rectangles with TH04's inclusive `h+1` row loop. The last SFF7 expansion touches
row400, so full-page comparisons cover visible rows0..399 and do not claim the
heap/offscreen allocation tail. CDG opaque draws clear the mask then OR color
planes, while the displaced plane helper uses white GRCG masks. The shared
read-only `cdg_image.hpp` replaces the GUI's private CDG/CD2 parser without
embedding original files or turning DOS segment fields into host pointers.

Verification at `.analysis/port64/staff-roll-v1293` binds the 208-file source
manifest `830f7c96cca70b471124d408cbad3ece832d94f7964d62a18604338d7cc487b9`:

- Eight original CPU request controls execute all eight bodies at decoded
  MAINE_01 `0A05:0E80..1736`, using loads1000/2000 and initial angles0/7/64/255.
  The complete producer digest is independently checked against the recovered
  payload; original polar at `0CC7:0260` executes its signed multiply/SAR.
  File, sound, graphics and VSync consumers are explicit adapters.
- 268 direct original CPU graphics controls execute `0CC7:0408` plane drawing,
  `0CC7:06E6` opaque CDG and `0CC7:0A86` background restore. They cover all18
  CDG assets, four color planes, alignments0/7/15, varying seeded backgrounds,
  zero-height inclusive copies and the visible portion of the row400 write.
  A supplied GRCG adapter applies masks; ordinary target OR/copy instructions
  execute. Unsupported requests fail closed.
- An independent original-request-driven raster compares332 complete indexed
  pages and166 palette/page/lifetime checkpoints. CDG planes are independently
  unpacked; the two PI backgrounds use a recorded v1292 decoder regression
  dependency, not an original-CPU PI decoding claim. A whole-page byte mutation
  is rejected. GNU, Wine and optimized UBSan pass all controls.
- Three fast incremental builds each produce31 AMD64 executables and pass all
  30 CTests.29 GNU and29 UBSan executables remain raw-identical to v1292. The
  changed GUI and cutscene consumer pass full original-controlled regressions;
  there is no PE body equality claim from the prior hash-only snapshot.
- Each host runs24 natural menu/STD/dialogue/boss/Good-or-Bad-Ending routes,
  then the entire Staff Roll to verdict entry. The preceding576 Ending pages,
  288 palette/state and288 RGB checks remain intact;48 final Staff Roll pages
  and24 palettes agree with the independently controlled component gallery.
  Resident publication, resource release and fresh MAINE lifetime stay checked.

The actual-Windows consumer is `verify_maine_join_windows.ps1 -StaffDirectory
CONTROLS`; it also checks the original handoff/counter/fade controls and all30
contracts. Its original/reference producer scope stays separate from Windows
execution. Source snapshots and original CPU streams remain immutable; only
completed derived media may be archived after full SHA-256 readback.

Target provenance remains candidate-local-attested, including the recovered
MAINE payload7495ae43. The Ghidra MAINE database attests its packed wrapper,
not a distinct recovered-payload semantics Oracle. No DOS source or acceptance
ledger changes. Verdict, congratulations, score persistence, Extra/death/Bomb/
Continue/full HUD/audio/config and a complete original-game video comparison
remain outside this batch. General semantic work stays stopped.

Actual Windows passes all30 contracts, eight original request streams,268
kernel controls,332 complete component pages and24 natural Ending/Staff Roll
routes. The route consumer compares1,248 binary/state files; independent Python
readback checks the original Ending/RGB reference and final Staff Roll pages.
Native and root CI pass. The validated preview is published at
`D:\Entertainment\Game\Touhou\th04-reconstruct\port64-preview\v1293-staff-roll`;
root `start-th04-port64.bat` is updated and previousv1292 is backed up. All2,206
pre-existing Windows files outside the two authorized native replacements keep
their hashes. The versioned launcher uses its own verified original HDI/font;
publication does not launch the GUI or change DOS products/scripts/config/saves.

A focused follow-up reads all eight original Ending request streams: every
copy0 has access1 beforehand and an explicit access0 immediately afterward.
Their visible-page regressions remain valid under the existing request-adapter
state convention. Do not reuse that convention as generic graph_copy_page
semantics for new owners; Staff Roll uses the independently reviewed destination
semantics. `ending-copy-caller-review.json` preserves this narrowed caller proof.

After all consumers finish,6,977 completed v1293 render buffers/BMPs are losslessly
gzip-archived, releasing1.98GiB. Seven explicit inputs retain hashes; supplementary
post-archive verification checks93 current native executables and456 expanded
original-controlled Ending/font reference buffers against accepted pre-archive
receipts. Two final GNU Staff Roll pages, original request/fixture streams,
PI decoder baseline, current build caches and Windows inputs remain available.
Restore archived direct-consumer paths with `gzip -d -- PATH.bin.gz` or
`PATH.bmp.gz`; `media-archive-receipt.json` and `archive-readback.json` retain
member/readback and protected-product/reference digests.

## Verdict calculation and clock

v1294 ports the complete recovered MAINE0A05:1737..20F8 owner to
`port64/verdict.cpp`. `Plan` computes the assessment and owns the ordered
graphics/file/palette/wait requests. `Script` consumes them with explicit
refresh and key waits. These are native components; the GUI still holds at
the v1293 verdict-entry frontier. No synthetic cutscene script, copied
instruction array, DOS pointer alias or host floating-point rate is used.

Source comments retain the operations affecting results: percentages divide
before multiplying, accumulation wraps as DWORD, signed division truncates
toward zero, frame rates narrow to WORD after division by10, and graze doubling
wraps AX before zero extension. Completion overrides STD to44000 for Good
and12000 for completed Extra. Chance bonus re-seeds MAINE LCG from resident
menu-time rand and draws once only if item penalty is nonzero. Result exposes
the continued LCG and changed STD for later publication at calculation time;
it does not itself mutate application resident state or replace a process.

Original DATA0E53:071A is the initialized-zero subtraction flag. The separate
BSS0E53:3F9C completion toggle does not feed that helper: fresh percentages
all add, including completion and slowdown. Fixed-two-digit mode is initialized
DATA0743. Skill/rank are3F9E/3FA2. The30-byte commentary buffer starts3FA3;
its byte28 terminator is3FBF. CP932 file records retain30-byte stride. Assessment
is hidden if `(frames>>1)<=slow_frames`, without opening commentary. Valid
scores cover26 rows, including line0/no seek for skill at least1500000.

`verify_verdict.py` executes all original bodies/switch tables and
irand0000:1C5A..1C83.916 fixtures at both load1000/2000 compare complete
consumer requests, CP932/gaiji strings, skill/cap/rank, resident STD, RNG,
independent subtraction/fixed/toggle globals and file lifetime. Coverage includes
legal rank/life/bomb/end/Turbo combinations, all26 commentary records, miss15
and Bomb30 edges, BCD thresholds, invalid slowdown, WORD/DWORD wrap, equal/zero
denominators and wrapped hundreds glyphs terminating a gaiji string.

Ten further controls execute original black-in0000:0622, black-out0666,
frame_delay0CC7:0033 and input_wait0CC7:020A. Only VSync, keyboard samples
and palette-display consumers are adapted. Ordered request refresh times,
changed palette tones and completion times match native scheduling at both
loads. Release combines previous/current samples; a fresh press resumes requests
in the same scheduler call. Zero wait budget never expires. Profiles include
initially-held Enter, one-refresh release, a press during release and a
one-refresh fresh press. These are bounded modeled-refresh controls, not
physical PC-98 pacing, audio synthesis or rendered-pixel evidence.

GNU8.4Release, MinGW13-posix AMD64 and optimized GNU UBSan/bounds fast builds
each produce31 products and pass30CTests. Three native consumers match916
cases and10 clocks. `verify_verdict_windows.ps1` also runs30 contracts and
the same comparisons on actual Windows; independent Python output readback
checks original hashes.213-file manifest:
6c846b7fb01bfa03c11a2a9d5f7c0e896d7da3c69c5c8b6c98a77dcffd707268.
Receipts:.analysis/port64/verdict-v1294.30GNU/30UBSan products, including
the game executable, are raw-identical to v1293. PE metadata changes on relink;
no preceding PE body equality is claimed. Native/root CI pass.

Next join a graphics canvas, full-string text/gaiji drawing and UDE.PI, compare
complete pages with original font kernels, then attach verdict to Staff Roll
and publish resident STD/RNG in the correct phase. Preserve the independently
reviewed destination/opposite-page copy semantics. Congratulations and score
registration/save follow. Windows preview, DOS source, original targets and
exact acceptance remain unchanged. General semantic expansion stays stopped.
