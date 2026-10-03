# TH04 native 64-bit bring-up

This branch keeps the playable PC-98 DOS build intact and develops a separate
native port. The current slice reads a user-supplied TH04 HDI (or loose OP
archive), decodes PAR, PI and CD2 data, writes inspection BMPs, and presents
the resource-derived OP main menu through SDL2 on Linux or Win32/GDI on
Windows. Game now enters the two-step character/shot menu rendered from
`SLB1.PI` and `SL.CD2`; a completed choice updates the portable resident
contract and starts a live MAIN player scene. The portable state machine skips locked Extra, enters the complete
Options list, wraps every stored option in the original direction, restores
the original defaults, and returns to the Option command on Cancel/Option
Quit. Other main commands whose screens are not ported yet print their index and
leave the window open; main Quit/Esc closes it. In that scene, arrow keys move the original character sprite and Shift halves
speed. The fixed 32-slot item pool handles drops, motion, attraction and scoring;
its seven-type scene fixture is headless-only. The interactive scene currently
has a black playfield without stage scripts, shots, enemies, bombs or death. No original executables or game data are embedded in the binary. Unlike
the DOS reconstruction, this port makes no byte-exact claim.

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
with seven explicitly injected item types (`0fe4fac7...`); these fixture items
are not injected into ordinary interactive sessions.
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

The next gameplay slice is stage VM/entity integration, followed by shots,
enemy bullets, scrolling/tile maps, HUD, death/Bomb transitions and audio.
Saved configuration and Ending/score persistence also remain. Semantic work
is paused unless a concrete ambiguity blocks one of these slices; a completed
TH04 native game has not yet been demonstrated.
