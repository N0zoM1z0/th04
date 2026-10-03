# TH04 native 64-bit bring-up

This branch keeps the playable PC-98 DOS build intact and develops a separate
native port. The current slice reads a user-supplied TH04 HDI (or loose OP
archive), decodes PAR, PI and CD2 data, writes inspection BMPs, and presents
the resource-derived OP main menu through SDL2 on Linux or Win32/GDI on
Windows. The portable state machine skips locked Extra, enters the complete
Options list, wraps every stored option in the original direction, restores
the original defaults, and returns to the Option command on Cancel/Option
Quit. Main commands whose screens are not ported yet print their index and
leave the window open; main Quit/Esc closes it. It does **not** start gameplay
yet. No original executables or game data are embedded in the binary. Unlike
the DOS reconstruction, this port makes no byte-exact claim.

The portable core also models the DOS executable chain as guarded in-process
states over one fixed-width resident object. Contracts cover normal, Extra and
the four demo launches; MAIN statistics publication; Good/Bad, Extra and
score-only MAINE routing; direct MAIN-to-OP return; and MAINE-to-OP retention.
This state is ready to connect to future gameplay/Ending implementations; the
current menu still reports those destinations as unported.

`SharedRandomRing` is the first portable gameplay-state owner. It preserves
the single stream shared by both historical accessor families, the descending
256-call fill, overlapping little-endian samples, byte-sized cursor advance,
AND/MOD reduction order and the layout-defined `0xFF00` boundary sample. The
boundary is synthesized explicitly, so the x64 implementation never reads
outside its array. A zero MOD divisor becomes a defined host exception after
the sample has advanced, matching the original state order around 8086 `DIV`.

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
with SHA-256 `b52ea861...` and `a064338b...`. The portable contract target
also consumes `src/main/bullet/group_types.hpp` and checks 64-bit pointer
width, byte-sized angles/group codes, spread/ring geometry, aim and template
rotation wrapping, half-turn directional-sprite reuse, and OP menu/config
transitions. It additionally checks the complete portable process-handoff
contract and rejects invalid cross-phase transitions. The contract output also
reports `randring=SHARED_OVERLAP` after checking all 256 cursor positions and
the consuming zero-divisor failure path.

A GNU x86-64 debug build also passes these contracts with
`-fsanitize=undefined,bounds`.

Next runtime boundaries are description text, character selection, input
timing, audio, configuration persistence, and replacement of DOS file/heap
interfaces. UI destinations can then enter the portable handoff state while
MAIN bullet entity and rendering state build on the shared angle/group
contract. A completed TH04 native game has not yet been demonstrated.
