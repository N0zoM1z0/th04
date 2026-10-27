# TH04 Portable 64-bit

See the [portable guide](../docs/PORTABLE.md) for Windows release setup,
controls, audio profiles, saves, Windows/Linux source builds and packaging.
The public source branch is `port/modern-64`.

```sh
cmake -S port64 -B build/windows-x64 -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_TOOLCHAIN_FILE="$PWD/port64/mingw64-toolchain.cmake" \
  -DCMAKE_CXX_FLAGS="--param=ggc-min-expand=5 --param=ggc-min-heapsize=4096"
cmake --build build/windows-x64 --target th04-port64 --parallel 1
```

On a Windows MinGW-w64 development CMD, use `port64\build-windows.bat`.
Game data is supplied separately at runtime. Launch `Play.bat` for ordinary
play with sound or the attested release's `Play-no-life-loss.bat` for seamless
invincibility. Both share one executable and keep separate saves.

Current status and limits: [handoff](../docs/RE_HANDOFF.md).
Earlier experiment reports: [portable history](../docs/port64/PORTABLE_HISTORY.md).
