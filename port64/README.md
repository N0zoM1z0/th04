# TH04 native 64-bit bring-up

This branch keeps the playable PC-98 DOS build intact and develops a separate
native port. The current GUI reads a user-supplied TH04 HDI, decodes the original
assets and runs the title/options, character/shot selection, Stages1 through6.
Stages1 and2 include their actual STD waves, midboss, pre-dialog, ordinary boss,
post-dialog, clear bonus and departure. Stage3 continues its STD waves and
midboss, Elly battle, post-dialog, clear bonus and departure. Stage4 runs its
STD waves, carpet lighting, two midboss encounters and character-dependent
NPC dialogue. Both characters continue through their respective Reimu/Marisa
Boss battle, post-dialog, clear bonus and departure into Stage5 STD waves, scrolling stars and Yuuka pre-dialogue.
Stage5 has no midboss; it includes Yuuka's battle, post-dialogue and departure.
Normal/Lunatic continue through Stage6 waves, dialogue and Yuuka's final
battle, then all-clear, Good Ending, Staff Roll, assessment and congratulations.
Easy follows its Bad Ending through the same post-Ending owners.
On Linux the window uses SDL2; on Windows it uses Win32/GDI.
Arrow keys move, Z fires, Shift slows movement; release then press Enter or Z
to advance dialogue. After congratulations and the original100-refresh delay,
registration accepts arrows, Z/Enter, X to erase and Esc to save, then returns
to fresh OP. Player death and frozen Game Over/Continue are joined with bounded
frontend controls. Quit's score-only MAINE route, Bomb graphics/shared palette,
complete HUD/audio and Extra remain pending.
The native preview does not embed
original executables or assets and makes no DOS byte-exact claim.

All launches stay muted (`--mute` is also explicit in the Windows launcher).
Scores use a separate `GENSOU.SCR` under `$XDG_DATA_HOME/th04` or
`$HOME/.local/share/th04` on Linux, `%LOCALAPPDATA%\TH04` on Windows; override
with `--save-dir DIR`. Original writer closes commit through a temporary file
and atomic replacement. An I/O failure blocks the return to OP. Files shorter
than ten196-byte sections are recreated by an explicit host repair; score-core
short-read behavior remains unchanged. HDI inputs stay read-only.

`--registration-checks DIR` runs30 seeded child-scene fixtures, including all
ten sections, both name exits, save/reload, fresh OP and second MAIN. This
does not exercise a complete natural gameplay route. See the
[registration evidence](../docs/port64/evidence/score-registration.md#registration-scene-and-host-save).

The two Stage4 Boss owners have independent original CPU state/event,
foreground/backdrop and indexed-pixel controls. Marisa additionally owns four
bits, ten attacks and the target's signed line clipping rules. Gameplay uses
an explicit native repair for the original variable-duration flystep zero
divisor; original-state controls keep that repair disabled. See the bounded
[Stage4 render evidence](../docs/PORT64.md#stage4-marisa-battle-and-rendering).

Semantic readability work stays paused once sufficient for the next port slice;
only a concrete ambiguity reopens a bounded clarification. Current evidence
and limitations live in [PORT64.md](../docs/PORT64.md), while the older subsystem
sections below retain their bounded historical scope.

The portable core also models the DOS executable chain as guarded in-process
states over one fixed-width resident object. Contracts cover normal, Extra and
the four demo launches; MAIN statistics publication; Good/Bad, Extra and
score-only MAINE routing; direct MAIN-to-OP return; and MAINE-to-OP retention.
This state is ready to connect to future gameplay/Ending implementations; the
current menu still reports those destinations as unported.

`Lcg32` is the fixed-width process-local generator underneath portable random
state. It reproduces the unsigned modulo-2^32 update and 15-bit result on both
Linux and Windows, including signed-boundary vectors. The application state
keeps OP's menu-frame accumulator in the resident object, resets local state to
1 at each modeled executable transition, copies the resident seed on MAIN
entry, applies the demo seed 318, and exposes MAINE's verdict re-seed as an
explicit event so route ordering stays visible.

`SharedRandomRing` preserves
the single stream shared by both historical accessor families, the descending
256-call fill, overlapping little-endian samples, byte-sized cursor advance,
AND/MOD reduction order and the layout-defined `0xFF00` boundary sample. The
boundary is synthesized explicitly, so the x64 implementation never reads
outside its array. A zero MOD divisor becomes a defined host exception after
the sample has advanced, matching the original state order around 8086 `DIV`.

`item_system` builds the first MAIN gameplay contract on that stream. It
models the 32-slot fixed pool's miss-drop allocation, three velocity fields,
big-item slot, unused distinct draw, per-item power/point draw and one-life
full-power override. Fixed-width score state covers the point/dream tables,
Bomb multiplier, power overflow, collection/miss performance carries and the
wrapped unsigned pickup rectangle. The big-power cap is evaluated before the
portable table lookup, yielding the same cap/reward without the DOS source's
transient out-of-range access.

The architecture follows the separation used by TH08's modern port: the
historic compiler/link path remains the reconstruction baseline, while CMake
builds a new host product. TH08's current modern product is still 32-bit;
TH04's 16-bit segmented ABI and PC-98 hardware need a wider runtime boundary
before gameplay sources can compile for x64.

Linux build and independently verified image smoke:

```sh
cmake -S port64 -B .analysis/port64/linux -DCMAKE_BUILD_TYPE=Release
cmake --build .analysis/port64/linux --parallel
ctest --test-dir .analysis/port64/linux --output-on-failure
python3 port64/smoke.py --exe .analysis/port64/linux/th04-port64 \
  --hdi .analysis/runtime/images/zun.hdi
```

Windows x64 cross-build from Linux:

```sh
cmake -S port64 -B .analysis/port64/windows \
  -DCMAKE_TOOLCHAIN_FILE="$PWD/port64/mingw64-toolchain.cmake" \
  -DCMAKE_BUILD_TYPE=Release
cmake --build .analysis/port64/windows --parallel
WINEDEBUG=-all python3 port64/smoke.py --runner wine \
  --exe .analysis/port64/windows/th04-port64.exe \
  --hdi .analysis/runtime/images/zun.hdi
```

For native Windows development, use a 64-bit CMake generator and build the
same `port64` source directory. Example command on Windows:

```cmd
th04-port64.exe --hdi D:\path\to\your\th04.hdi --title
```

The resource CLI prints a FNV32 hash of the 4-bit packed pixels. `CONG10.PI` and
`CONG14.PI` must yield `232AE649` and `EDFA0534` on the attested HDI; these
match the independent 16-bit DOS decoder probe. The generated BMP is an
inspection artifact and is never written into the HDI. This slice supports
PI images with embedded palettes, as used by these fixtures.

`--title-screenshot FILE.bmp` performs the complete OP1.PI + SFT2.CD2 +
CAR.CD2 main-menu composition without opening a window.
`--options-screenshot FILE.bmp` adds the SFT1.CD2 numerals and renders the
default Options state. Linux and Windows x64 produce the same 640x400 BMPs
with SHA-256 `b52ea861...` and `a064338b...`.
`--character-screenshot` and `--shot-screenshot` render the two selection
stages; their shared cross-host hashes are `c1a795a3...` and `12aa7616...`.
`--handoff-screenshot` retains the static handoff fixture (`0b2c0f8c...`).
`--main-screenshot` requires an HDI and drives a 60-frame movement/item scene
with seven explicitly injected item types (`4cbbe895...`); these fixture items
are not injected into ordinary interactive sessions.
`--shooting-screenshots DIR` writes all four full-power shooting fixtures to
an existing directory. Each fixture collects an explicitly injected full-power
item and holds Z for 66 frames; ordinary windows start at power 1.
`--midboss-screenshots DIR` runs four 4500-frame Stage 1 fixtures (both
characters, held Z or no shot) and saves six checkpoints each. They use actual
STD waves, background, shots and effects; player death is still unported.
Independent original-CPU state/render/tile/setup controls:

```sh
python3 port64/verify_midboss.py --target .analysis/targets/th04/main.exe \
  --hdi .analysis/runtime/images/zun.hdi \
  --exe .analysis/port64/linux/th04-port64-midboss-contracts \
  --output-dir .analysis/port64/midboss-control
```

The portable contract target
also consumes `src/main/bullet/group_types.hpp` and checks 64-bit pointer
width, byte-sized angles/group codes, spread/ring geometry, aim and template
rotation wrapping, half-turn directional-sprite reuse, and OP menu/config
transitions. It additionally checks the complete portable process-handoff
contract and rejects invalid cross-phase transitions. The contract output also
reports `randring=SHARED_OVERLAP lcg=PROCESS_LOCAL32` after checking LCG
vectors, executable/resident seed lifetimes, an LCG-backed 256-call fill, all
256 cursor positions and the consuming zero-divisor failure path. It also
reports `items=FIXED_WIDTH_SAFE` after checking enemy-drop cadence, shared-ring
consumption, full/sparse pool allocation, one-life override, scoring caps,
performance carries and pickup boundaries.

A GNU x86-64 debug build also passes these contracts with
`-fsanitize=undefined,bounds`, including unsigned wrap, process resets, the
full LCG-backed random-ring fill and the above-cap big-power scoring case.

The live MAIN contracts additionally cover Q12.4 wrapping, negative arithmetic
shifts, angle/polar motion, conflicting input priority, Shift speed, clamping,
item gravity, attraction, deferred release, pickup/miss ordering and BFNT
palette/row decoding. `verify_movement.py` independently executes the pinned
original MAIN player-move body under Unicorn for all 256 direction masks and
compares the native vectors. This validates the isolated primitive; it does
not establish full player update or original frame timing.

Optional window integration replay (requires Xvfb, xdotool, ImageMagick and Pillow):

```sh
xvfb-run -a -s '-screen 0 1600x1000x24' python3 port64/verify_window.py \
  --exe .analysis/port64/linux/th04-port64 \
  --hdi .analysis/runtime/images/zun.hdi \
  --output-dir .analysis/port64/window-linux
```

For Wine/Win32 use `--runner wine` and the Windows executable. This checks
actual held keys, visible movement, slower Shift movement and Esc exit with
loose time bounds; native Windows pacing remains a separate observation.

`stage_background` decodes the MPN last-image index and B/R/G/I planes once,
translates MAP VRAM addresses into portable tile IDs, initializes the 25-row
ring in STD order, and preserves the byte scroll accumulator, initial chunk
length speed and pre-advance display origin. The host redraws the playfield
from this ring while retaining the original Stage 1 scroll state sequence.
The independent original-CPU oracle covers initial fill and 6,715 frames
through termination, including 64 stopped frames. Original MPN renderer calls
also match all 32,768 indexed pixels of both character tile sets.

```sh
python3 port64/verify_background.py --target .analysis/targets/th04/main.exe \
  --hdi .analysis/runtime/images/zun.hdi \
  --exe .analysis/port64/linux/th04-port64-live-contracts \
  --output-dir .analysis/port64/background-cpu
```

Use `--runner wine` for the PE32+ contract executable. Scroll EGC copies and
graphics calls are intercepted in this oracle; it proves bounded software
state and MPN pixels rather than complete PC-98 video or gameplay.
`verify_window.py --playchar marisa` covers the other character. Its visible
movement check now matches nontransparent original BFNT sprite pixels against
the scrolling window, rather than assuming a black background.

`player_shots` preserves descending volley allocation order, all four routes
and ten power levels, cycle resets, allocation-dependent random consumption,
old option coordinates at laser startup, hit-animation countdown and the
frame collision cache. Releasing Z finishes the remaining volleys of the
18-frame cycle. Hit tests retain diminishing damage, Bomb/boss division order,
odd-frame laser damage and spark phase. Spark requests now dispatch through the live effect adapter; the isolated
shot CPU oracle still intercepts them. Sound remains separate. The host stops
at 68 slots rather than importing the original allocator's observed overrun.

```sh
python3 port64/verify_shots.py --target .analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux/th04-port64-shot-contracts \
  --output-dir .analysis/port64/shots-cpu
```

The relocated original CPU agrees on 4,072 trigger/producer/update/hit
checkpoints, including all timer bytes, both characters/shot types, all levels,
homing targets, sparse/full pools, laser phases, hit edges and repeated calls.
Spark calls are recorded and intercepted. A separate negative control observes
the original allocation overrun; the host boundary is tested with sanitizers.
Both character windows pass held-Z firing and release against original sprite
pixels. Windows validation runs under Wine; native Windows pacing is untested.

Stages1..6 now connect their ordinary waves, bosses and clear transitions.
Remaining gameplay owners include Extra, HUD, death/Bomb transitions and audio.
Saved configuration and Ending/score persistence also remain. Semantic work
is paused unless a concrete ambiguity blocks one of these slices; a completed
TH04 native game has not yet been demonstrated.

`stage_program` dispatches original STD waves without catch-up; midboss skips
consume the wave. `enemy_system` preserves inclusive timed movement, immediate
setup chains, script loops, clipping, Lunatic autofire, performance intervals,
shot damage, homing, kill/drop scoring and animation. Render-state mutations
occur once per simulation frame. Synchronous fire/sound/tile/spark requests
retain the original call boundaries; item drops and bullet tune/add are
connected synchronously now. Spark RNG/effects now dispatch synchronously too; player death remains absent.

```sh
python3 port64/verify_enemy.py --target .analysis/targets/th04/main.exe \
  --hdi .analysis/runtime/images/zun.hdi \
  --exe .analysis/port64/linux/th04-port64-enemy-contracts \
  --output-dir .analysis/port64/enemies-cpu
mkdir -p .analysis/port64/combat
.analysis/port64/linux/th04-port64 --hdi .analysis/runtime/images/zun.hdi \
  --combat-screenshots .analysis/port64/combat
```

Use `--runner wine` with the PE32+ contract executable. The CPU oracle compares
9,414 VM vectors, 896 hit/lifecycle cases, all seven schedules and 12,600 actual
Stage 1 enemy update/render frames. It records ordered intercepted requests
and renderer coordinates/cels, not complete graphics pixels or gameplay.
The combat fixture holds Z for 1,200 original Stage 1 frames per character,
with normal initial power and no injected entities/items/score. Both host
products kill 26 enemies and reach power 7; their images and counters agree.


`enemy_bullets` retains rank/performance byte arithmetic, descending separate
pools, cloud timing, first-close-frame graze, collision, clear decay, zap
bonuses and the original optional count-based slowdown. Enemy firing and spark requests consume
the same ring immediately; gather requests capture templates for later release.
The host draws small pellets procedurally and other bullets from original BFNT.

```sh
python3 port64/verify_bullets.py --target .analysis/targets/th04/main.exe \
  --hdi .analysis/runtime/images/zun.hdi \
  --exe .analysis/port64/linux/th04-port64-bullet-contracts \
  --output-dir .analysis/port64/bullets-cpu
```

Use `--runner wine` for the PE32+ contract executable. Scoped original CPU
comparison covers 36,216 tune/add/update checkpoints and 2,400 joint
STD/enemy/bullet frames. A separate 72-case original GRCG shadow checks the
procedural 8x8 pellet glyph, including the repeated lower row and Y roll.
Two negative controls retain original zero-count ring IDIV exceptions; the
native product skips those rings as the playable DOS repair does.
`--combat-screenshots DIR` now also writes `reimu-bullets.bmp` and
`marisa-bullets.bmp`: OP-selected Lunatic, 900 frames without Z, five live
bullets per image. These are natural Stage 1 fixtures without injected
entities. They are not dense-barrage timing measurements. Five contracts,
cross-host BMPs/counters and UBSan/bounds pass. This earlier bullet-only oracle
excludes gather/spark callees; their next integration is covered below. Full
routes and player death remain incomplete.


`effects` initializes spark angles with the same process generator after the
256-call ring fill and item initialization. Only free spark attempts consume
random samples; occupied attempts still advance the offset. Circular bursts
preserve word numerator wrapping. Gather circles move/shrink after items and
restore the already tuned full bullet scratch on release without retuning.
Both effects render from procedural geometry, without embedded original sprites.

```sh
python3 port64/verify_effects.py --target .analysis/targets/th04/main.exe \
  --hdi .analysis/runtime/images/zun.hdi \
  --exe .analysis/port64/linux/th04-port64-effect-contracts \
  --bullet-exe .analysis/port64/linux/th04-port64-bullet-contracts \
  --output-dir .analysis/port64/effects-cpu
```

Use `--runner wine` with both PE32+ executables. The independent original CPU
oracle compares 3,075 complete-state/render controls, 648 spark/gather glyph
controls and 2,400 controlled Normal/Lunatic integration frames. The latter
inject targeted shot-cache/gather inputs to exercise real original callee
chains; ordinary windows do not inject these. Six contracts, cross-host
fixtures and GNU UBSan/bounds pass. The original zero-count circle division
fault is a separate negative control; the host throws a defined exception.
The real 1200-frame Stage 1 shooting scenes now yield 24 kills/score5,720/power6,
and the Lunatic 900-frame scenes contain six live bullets per character. Spark
RNG integration changes the earlier partial fixture's sequence. Full routes,
bosses, death/Bomb, HUD/audio and Ending/save remain to be migrated.
