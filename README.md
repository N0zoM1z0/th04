# 東方幻想郷 ～ Lotus Land Story

> [!NOTE]
> The [Windows x64 portable preview](https://github.com/N0zoM1z0/th04/releases) supports Normal, Extra, Music Room, endings and saves, with sound.
> Portable source is on [`port/modern-64`](https://github.com/N0zoM1z0/th04/tree/port/modern-64); the PC-98 DOS reconstruction is on [`main`](https://github.com/N0zoM1z0/th04/tree/main).

A reconstruction of the Japanese PC-98 **Touhou 4: Lotus Land Story**, with
a C++17 port for Windows and Linux. The portable version runs without a DOS emulator.

<a href="https://www.youtube.com/watch?v=ryCOOMZ5PBI">
  <img src="https://i.ytimg.com/vi/ryCOOMZ5PBI/maxresdefault.jpg" width="640" alt="Watch TH04 portable gameplay on YouTube">
</a>

[▶ Watch on YouTube](https://www.youtube.com/watch?v=ryCOOMZ5PBI) · Stages 1–3 · Lunatic · Invincibility enabled

<p align="center">
  <img src="resources/progress.svg" alt="TH04 four-artifact boundary and function acceptance progress">
</p>

## Play on Windows

### 1. Download the portable release and preparation script

Extract the Windows x64 ZIP from [Releases](https://github.com/N0zoM1z0/th04/releases)
into a writable folder, such as `C:\Games\th04-portable`.
Install [Python 3.9 or newer](https://www.python.org/downloads/windows/) for the
one-time data preparation. Open CMD in that folder and download the script:

```bat
curl.exe --fail -L -o prepare_assets.py https://raw.githubusercontent.com/N0zoM1z0/th04/refs/heads/port/modern-64/port64/prepare_assets.py
```

If you already cloned `port/modern-64`, the script is in `port64\prepare_assets.py`.

### 2. Extract your Japanese full-version game files

The original game used two installation floppies. Its installer writes loose
game files to a hard disk; `th04.hdi` is the portable program's container name.
The original [installation manual, transcribed at THBWiki](https://thwiki.cc/附带文档:东方幻想乡/1st),
describes running `INSTALL A:` under PC-98 DOS or running both disks' self-extractors.

Use your installed game folder, or extract both original installer archives
into one folder, for example `C:\Games\TH04-original`. It must contain:

| File | Size in bytes |
| --- | ---: |
| `MAIN.EXE` | 156,258 |
| `幻想郷ED.DAT` | 1,120,284 |
| `東方幻想.郷` | 1,053,177 |

The script finds these files by content even if an extractor garbled their
Japanese names. It checks the supported Japanese full-version hashes; trial
or translated files need a separate compatibility path.
See [original media and extraction](docs/PREPARE_DATA.md#original-media-and-extraction)
for installer archives and existing disk images.

### 3. Prepare the HDI, font and sound data

From the portable release folder:

```bat
py -3 prepare_assets.py --game-dir "C:\Games\TH04-original" --output-dir . --fetch-support
```

This creates `th04.hdi`, `FREECG98.BMP` and `ym2608_adpcm_rom.bin` beside the EXE.
The HDI contains your three game files unchanged. `--fetch-support` downloads a
pinned DOSBox-X font bitmap and extracts the rhythm data from a pinned
libOPNMIDI header. It does not download the game.
[Offline preparation, supported inputs and checksums](docs/PREPARE_DATA.md)
are documented separately. The script uses Python's standard library; no pip
packages are needed. If `py` is unavailable, use your Python 3 executable instead.

### 4. Start the game

Run **Play.bat** for normal play, or **Play-no-life-loss.bat** for invincibility
without the death animation. Both enable sound. Use the arrow keys to move,
Z to shoot/confirm, X to bomb/cancel, Shift to move slowly and Esc to pause/back.

The launchers keep scores/settings in `save-normal` and `save-no-life-loss`.
Keep those folders when updating. The [portable guide](docs/PORTABLE.md)
covers gamepads, audio options and troubleshooting.

## Build the portable version

Compiling requires CMake 3.16+, a 64-bit C++17 compiler and a build tool.
Game data is needed when running the game. Install [Git](https://git-scm.com/),
then get the portable branch explicitly:

```sh
git clone --branch port/modern-64 https://github.com/N0zoM1z0/th04.git th04-portable
cd th04-portable
```

### Windows x64

Install MinGW-w64 GCC, CMake and Ninja. One setup is [MSYS2](https://www.msys2.org/):
run this in its **UCRT64** terminal:

```sh
pacman -S --needed mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-cmake mingw-w64-ucrt-x86_64-ninja
```

Then open **CMD**, enter your checkout and run the following. Adjust the MSYS2
path if you installed it elsewhere:

```bat
set "PATH=C:\msys64\ucrt64\bin;%PATH%"
port64\build-windows.bat
mkdir run
copy build\portable-win64\th04-port64.exe run\
copy port64\Play.bat run\
py -3 port64\prepare_assets.py --game-dir "C:\Games\TH04-original" --output-dir run --fetch-support
run\Play.bat
```

The invincibility launcher supports the published executable; self-built
executables use `Play.bat` until their patch offsets are registered.

### Linux x86-64

On Debian/Ubuntu, install `build-essential cmake ninja-build pkg-config libsdl2-dev python3`.
From the checkout:

```sh
cmake -S port64 -B build/linux-x64 -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build/linux-x64 --target th04-port64 --parallel 1
python3 port64/prepare_assets.py --game-dir /path/to/TH04-original --output-dir run --fetch-support
./build/linux-x64/th04-port64 --hdi run/th04.hdi --font-bmp run/FREECG98.BMP \
  --save-dir run/save-normal --title --audio --pmd-driver pmd86 \
  --opna-rom run/ym2608_adpcm_rom.bin
```

[Build details and Linux-to-Windows cross-compilation](docs/PORTABLE.md#build-from-source).

## Development

- [DOS setup and build](https://github.com/N0zoM1z0/th04/blob/main/docs/DOS_BUILD.md)
- [Current work and progress](docs/RE_HANDOFF.md)
- [Documentation index](docs/README.md)

## Credits

**ZUN** ([上海アリス幻樂団 / Team Shanghai Alice](https://www16.big.or.jp/~zun/))
created Touhou Project and the original TH04 game, characters, artwork and music.

Thanks to the authors and contributors of:

- **[ReC98](https://github.com/nmlgc/ReC98)** — **nmlgc and contributors**, for
  PC-98 reverse engineering, recovered source, hardware definitions and DOS
  build infrastructure used throughout this reconstruction.
- **[master.lib](https://github.com/nmlgc/ReC98/tree/master/libs/master.lib)** —
  the PC-98 graphics and system library used by TH04 and the DOS reconstruction.
- **KAJA / PMD** — the original PC-98 music driver and formats reconstructed
  by the portable audio layer.
- **[ymfm](https://github.com/aaronsgiles/ymfm)** — **Aaron Giles and contributors**,
  for the Yamaha FM, SSG and ADPCM synthesis used by the portable version.
- **[SDL2](https://wiki.libsdl.org/SDL2/FrontPage)** — Linux windowing, input and audio.
- **[DOSBox-X](https://github.com/joncampbell123/dosbox-x)** and the **FREECG98 contributors** — PC-98 execution tests and the external font bitmap used by
  setup, including [font corrections by hdk1983](https://github.com/joncampbell123/dosbox-x/issues/4123).
- **[libOPNMIDI](https://github.com/Wohlstand/libOPNMIDI)**,
  **[MAME](https://github.com/mamedev/mame)** and
  **[98fmplayer/libopna](https://github.com/myon98/98fmplayer/tree/master/libopna)** —
  rhythm-data preparation and audio reference implementations used for validation.
- **[Unicorn](https://www.unicorn-engine.org/)**,
  **[Capstone](https://www.capstone-engine.org/)** and
  **[Ghidra](https://github.com/NationalSecurityAgency/ghidra)** — original-code
  execution, disassembly and reconstruction checks.
- **[Wine](https://www.winehq.org/)** and **[mtools](https://www.gnu.org/software/mtools/)** —
  DOS-toolchain execution and disk-image preparation.

Project-authored code and documentation use the [MIT License](LICENSE).
ymfm retains its [BSD-3-Clause license](https://github.com/N0zoM1z0/th04/blob/port/modern-64/port64/vendor/ymfm/LICENSE);
SDL2 uses the [zlib license](https://www.libsdl.org/license.php).
