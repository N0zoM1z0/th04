# TH04 Portable 64-bit

A native C++17 port of the Japanese PC-98 **Touhou 4: Lotus Land Story**.
Windows uses Win32/GDI and WinMM; Linux uses SDL2. The portable program runs
without a DOS emulator. Original game data remains external and read-only.

## Download and play on Windows

Follow the numbered [README quick start](../README.md#play-on-windows):
download the release, extract your Japanese full-version game files, then run
`prepare_assets.py` to make `th04.hdi` and prepare the font/rhythm data.
[Data preparation](PREPARE_DATA.md) covers original media, supported file
identities, existing HDIs and offline use.

Double-click **Play.bat** for ordinary play with sound. **Play-no-life-loss.bat**
starts the same executable with seamless invincibility: hits do not trigger a
death animation or respawn. It patches only the process it creates. The two
launchers use separate `save-normal` and `save-no-life-loss` folders.
The default profile is **PMD86/OPNA**, with FM, SSG and rhythm enabled.

Update an existing installation by replacing the executable and launchers while
keeping both save folders and the external data files. Close your game before
replacing its executable. The release contains only one `th04-port64.exe`.

### Controls

| Key | Action |
| --- | --- |
| Arrow keys | Move / navigate |
| Z or Enter | Confirm / advance dialogue; Z fires in gameplay |
| X | Bomb; cancel/back in menus; erase in name entry |
| Shift | Slow movement |
| Esc | Pause; back in menus; finish/save name entry |

The first connected gamepad can also supply its first two axes/hat and first
two buttons for movement, Shot/confirm and Bomb/cancel. Keyboard remains
available. Physical gamepad mappings can vary.

### Game data and sound

Manual Windows command, from the executable/data folder:

```bat
th04-port64.exe --hdi th04.hdi --font-bmp FREECG98.BMP --save-dir save-normal --title --audio --pmd-driver pmd86 --opna-rom ym2608_adpcm_rom.bin
```

`--audio` enables output; `--mute` runs synthesis silently for diagnostics.
For the three-FM-channel 26K arrangement, use `--pmd-driver pmd` and omit
`--opna-rom`. Its `.M26` arrangements can sound different from `.M86`.
For no synthesis use `--pmd-driver none --mute`. Set FM86 in the game's BGM
options when using the default PMD86 launcher; an explicitly saved FM26 setting
still requests the 26K arrangement.

Scores/configuration are stored outside the HDI. Without `--save-dir`, the
program uses `%LOCALAPPDATA%\TH04` on Windows or `$XDG_DATA_HOME/th04`
(default `$HOME/.local/share/th04`) on Linux. The BATs override this with their
separate local save directories. Keep `MIKO.CFG` and `GENSOU.SCR` together.

## Build from source

The portable source is on **port/modern-64**. The default **main** branch is
the DOS reconstruction; select the portable branch explicitly:

```sh
git clone --branch port/modern-64 https://github.com/N0zoM1z0/th04.git th04-portable
cd th04-portable
```

The portable build requires CMake 3.16+, a 64-bit C++17 compiler and a build
tool. The portable target builds from this checkout with its vendored ymfm
library. The Linux frontend additionally requires SDL2 and pkg-config.
Data is needed to play.

### Windows x64 with MinGW-w64

Provide 64-bit MinGW-w64 GCC, CMake and Ninja on `PATH` (for example a MINGW64
development environment). Run from a CMD prompt in the source checkout:

```bat
port64\build-windows.bat
```

This configures a Release build in `build\portable-win64` and builds only
`th04-port64` with one compiler process. The result is
`build\portable-win64\th04-port64.exe`. Copy it into your data folder and use
`Play.bat`, or run the manual command above. MinGW runtime libraries are linked
statically; no separate MinGW DLL installation is needed for the release ZIP.

The optional invincibility launcher accepts only attested release hashes and
patch addresses. Self-built executables can use ordinary `Play.bat`; the
invincibility mapping must be re-attested for a different executable.

### Cross-build Windows x64 from Linux

Install CMake, Ninja and the `x86_64-w64-mingw32` C++ toolchain. From the checkout:

```sh
cmake -S port64 -B build/windows-x64 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_TOOLCHAIN_FILE="$PWD/port64/mingw64-toolchain.cmake" \
  -DCMAKE_CXX_FLAGS="--param=ggc-min-expand=5 --param=ggc-min-heapsize=4096"
cmake --build build/windows-x64 --target th04-port64 --parallel 1
```

The executable is `build/windows-x64/th04-port64.exe`. This is the toolchain
family used by the tested Windows release. Low compiler concurrency and GCC
GC settings bound memory use, especially for the large frontend source file.

### Linux x86-64

Install a C++17 compiler, CMake, Ninja, pkg-config and SDL2 development headers:

```sh
cmake -S port64 -B build/linux-x64 -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_FLAGS="--param=ggc-min-expand=5 --param=ggc-min-heapsize=4096"
cmake --build build/linux-x64 --target th04-port64 --parallel 1
./build/linux-x64/th04-port64 --hdi /path/to/th04.hdi \
  --font-bmp /path/to/FREECG98.BMP --save-dir ./save-linux --title --audio \
  --pmd-driver pmd86 --opna-rom /path/to/ym2608_adpcm_rom.bin
```

The GCC GC flags above apply to GCC. Omit them when selecting another compiler.
The published binary is Windows x64; Linux uses the source build.

### Focused checks and packaging

Build and run only the checks you need. Example Linux audio checks:

```sh
cmake --build build/linux-x64 --target th04-port64-pmd-pcm-contracts th04-port64-audio-device-contracts --parallel 1
ctest --test-dir build/linux-x64 --output-on-failure -R '^(pmd-pcm-contracts|audio-device-contracts)$'
```

The audio-device contracts use a fake backend; they do not play through the
host speakers. Asset-driven Windows tests additionally use private inactive
desktops and explicit mute. Do not run the complete default CMake target just
to build the game: it also builds many reconstruction/test executables.

An attested Windows executable can be packaged from a clean committed checkout:

```sh
python3 port64/package_release.py --exe /path/to/th04-port64.exe \
  --version 2026.10.27 --output-dir dist
```

The packager uses an explicit file allowlist, checks AMD64 PE32+ and the
invincibility launcher's supported hash, and writes ZIP/checksum/build metadata.
The manifest identifies the source commit and binary digest.

## Development notes

The [current handoff](RE_HANDOFF.md) records release checks and remaining work.
Focused notes cover [audio fidelity](reconstruction/product/TH04_PORTABLE_AUDIO_FIDELITY.md),
[rendering](reconstruction/product/TH04_PORTABLE_RENDER_PERFORMANCE.md), and
[UI/save/invincibility](reconstruction/product/TH04_PORTABLE_UI_AND_INVINCIBILITY.md).

Repository-authored code/documentation is MIT licensed. The vendored ymfm
engine is BSD-3-Clause with a recorded local opt-in key-state API extension.
The package includes both notices. Original Touhou content remains the work
of its respective rightsholders and is not included in the public package.
