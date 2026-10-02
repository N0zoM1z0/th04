# TH04 native 64-bit bring-up

This branch keeps the playable PC-98 DOS build intact and starts a separate
native port. The first working slice reads a user-supplied TH04 HDI (or loose
OP archive), decodes PAR and 16-color PI data, and writes a 24-bit BMP. It
builds and runs as Linux x86-64 ELF and Windows x64 PE32+. It does **not** run
gameplay yet. No original executables or game data are embedded in the binary.
Unlike the DOS reconstruction, this port makes no byte-exact claim.

The architecture follows the separation used by TH08's modern port: the
historic compiler/link path remains the reconstruction baseline, while CMake
builds a new host product. TH08's current modern product is still 32-bit;
TH04's 16-bit segmented ABI and PC-98 hardware need a wider runtime boundary
before gameplay sources can compile for x64.

Linux build and independently verified image smoke:

```sh
cmake -S port64 -B .analysis/port64/linux -DCMAKE_BUILD_TYPE=Release
cmake --build .analysis/port64/linux --parallel
python3 port64/smoke.py --exe .analysis/port64/linux/th04-port64 \
  --hdi .analysis/runtime/images/zun.hdi
```

Windows x64 cross-build from Linux:

```sh
cmake -S port64 -B .analysis/port64/windows \
  -DCMAKE_TOOLCHAIN_FILE="$PWD/port64/mingw64-toolchain.cmake" \
  -DCMAKE_BUILD_TYPE=Release
cmake --build .analysis/port64/windows --parallel
```

For native Windows development, use a 64-bit CMake generator and build the
same `port64` source directory. Example command on Windows:

```cmd
th04-port64.exe --hdi D:\path\to\your\th04.hdi --member CONG10.PI --output CONG10.bmp
```

The CLI prints a FNV32 hash of the 4-bit packed pixels. `CONG10.PI` and
`CONG14.PI` must yield `232AE649` and `EDFA0534` on the attested HDI; these
match the independent 16-bit DOS decoder probe. The generated BMP is an
inspection artifact and is never written into the HDI. This slice supports
PI images with embedded palettes, as used by these fixtures.

Next runtime boundaries are a portable PC-98 four-plane framebuffer/palette,
input/timing, audio, and replacement of DOS file/heap interfaces. Only then
can OP, MAIN, and MAINE gameplay/UI sources be migrated and tested against
the DOS build. A completed TH04 native game has not yet been demonstrated.
