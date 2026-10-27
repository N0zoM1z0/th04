# TH04 Portable 64-bit

A native C++17 port of the Japanese PC-98 **Touhou 4: Lotus Land Story**.
Windows uses Win32/GDI and WinMM; Linux uses SDL2. The portable program runs
without a DOS emulator. Original game data remains external and read-only.

## Download and play on Windows

Download the Windows x64 ZIP from [Releases](https://github.com/N0zoM1z0/th04/releases).
Extract it into a writable folder. Add these separately supplied files beside
`th04-port64.exe`:

```text
th04-portable64/
  th04-port64.exe
  Play.bat
  Play-no-life-loss.bat
  run_no_life_loss.ps1
  th04.hdi                  # your original Japanese TH04 image
  FREECG98.BMP               # compatible external PC-98 font bitmap
  ym2608_adpcm_rom.bin       # external 8192-byte YM2608 rhythm ROM
```

The public ZIP contains the executable, launchers, instructions and licenses.
It contains no original HDI, game executable/data, font bitmap, sound ROM or
user save files. Obtain the required data from your own installation/resources.
A translation or modified image is not covered by the pinned Japanese-data checks.

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

The tested external inputs have these SHA-256 identities:

| File | SHA-256 |
| --- | --- |
| `th04.hdi` | `0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd` |
| `FREECG98.BMP` | `41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6` |
| `ym2608_adpcm_rom.bin` | `53afd0fa9c62eda3e2be939e23f3adf48a2af8ad37bb1640261726c5d5adeba8` |

The ROM identity is checked by the invincibility launcher. The image provenance
is `candidate-local-attested`; these identities describe tested local inputs,
not independent confirmation of an official pristine dump.

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
tool. No Borland, Wine, private `.analysis` directory, original game data or
ReC98 checkout is required to compile the portable program. The native Linux
frontend additionally requires SDL2 and pkg-config. Data is needed to play.

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
No sanitizer is enabled in these Release commands.

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
It never collects local game data or saves. The manifest identifies the source
commit and binary digest; it does not claim byte-identical cold builds.

## Validation and limits

The Windows release was cold-built from a public-source snapshot with no
private cache or game-data inputs, building only the game and two focused
audio checks. Actual Windows PCM/register/IRQ output retains the prior
validated values. The 2026-10-27 preview has background window/input/Bomb/pause
checks, Music Room track switching, complete protected Normal and earned Extra
logical routes through endings/name entry/save/fresh OP, two 23-song start
corpora, Stage3/boss two-loop audio controls and silent real-WinMM transport
checks. Current audio is independently compared with libopna and historical
MAME FM, using original-driver register events. The user also reports improved
manual playback after the audio fixes.

This is a functional preview. Full original DOS timing/pixel identity,
physical PC-98 analogue sound and exhaustive difficulty/controller coverage
are not claimed. Protected clears validate flow rather than ordinary balance.
See [current handoff](RE_HANDOFF.md),
[audio fidelity](reconstruction/product/TH04_PORTABLE_AUDIO_FIDELITY.md),
[rendering](reconstruction/product/TH04_PORTABLE_RENDER_PERFORMANCE.md), and
[UI/save/invincibility](reconstruction/product/TH04_PORTABLE_UI_AND_INVINCIBILITY.md).
Historical experiments are indexed in [portable history](port64/PORTABLE_HISTORY.md).

Repository-authored code/documentation is MIT licensed. The vendored ymfm
engine is BSD-3-Clause with a recorded local opt-in key-state API extension.
The package includes both notices. Original Touhou content remains the work
of its respective rightsholders and is not included in the public package.
