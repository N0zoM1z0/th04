# Preparing TH04 portable game data

The [README](../README.md#play-on-windows) gives the complete quick start.
This guide covers original media, the data preparation script and offline use.

## Original media and extraction

TH04's full version was installed from two floppies onto a PC-98 hard disk.
The original installation instructions describe `INSTALL A:` and a manual
alternative that runs both disks' self-extracting archives. See the
[original manual transcription at THBWiki](https://thwiki.cc/附带文档:东方幻想乡/1st).
`th04.hdi` is the filename used by our launcher for its prepared data container;
it is not the name of an original downloadable full-game release.

Choose the path matching the files you already have:

1. **Installed game folder:** use that folder directly with `--game-dir`.
2. **Both original installer archives:** extract both into the same folder.
   [7-Zip](https://www.7-zip.org/) supports LZH archives. Try opening the EXEs
   as archives, rather than launching the 16-bit programs on Windows x64.
   For a pair named `GENSO1.EXE` and `GENSO2.EXE`, the CMD commands are:

   ```bat
   "C:\Program Files\7-Zip\7z.exe" x "C:\TH04-media\GENSO1.EXE" -oC:\Games\TH04-original
   "C:\Program Files\7-Zip\7z.exe" x "C:\TH04-media\GENSO2.EXE" -oC:\Games\TH04-original
   ```

   Use the names on your own disks. If the archiver cannot open their
   self-extracting format, run the original installer in a PC-98 DOS environment
   and export its installed game folder. The preparation script takes the
   extracted files, not the installer EXEs themselves.
3. **Floppy images (`.fdi`, `.d88`, `.hdm`, etc.):** access both disks through a
   disk-image tool or a PC-98 DOS emulator. Export their installer archives and
   follow step 2, or run `INSTALL A:` in the emulator and export the installed
   folder. Renaming a floppy image to `.hdi` does not convert it.
4. **Existing hard-disk image:** if it already uses the supported layout, use
   `--hdi` below. For another layout, export the installed game folder with
   your disk-image tool and use `--game-dir`.

The current importer requires these three files from the supported Japanese
full version. The first supplies point-number graphics; the two archives
supply the remaining graphics, scripts, sound effects and music.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `MAIN.EXE` | 156258 | `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b` |
| `幻想郷ED.DAT` | 1120284 | `ca787b8ff66f7b3f10c97b3ecc77cd466772767e3e9e8cf5a0c71dd612b1c8d7` |
| `東方幻想.郷` | 1053177 | `4d975850a66b4ec2ca5fd4fba7f3166dd9293d220ba8ab6c1be87ed98b1399be` |

The script searches subfolders by size and SHA-256, so Japanese filename
encoding errors do not require manual renaming. The trial version, translated
executables and other revisions have different identities. A mismatch stops
preparation and reports the missing supported file.

## Run the preparation script

Use Python 3.9+; there are no pip dependencies. The script is on the
[`port/modern-64` branch](https://github.com/N0zoM1z0/th04/blob/port/modern-64/port64/prepare_assets.py).
From a `port/modern-64` source checkout, run:

```bat
py -3 port64\prepare_assets.py --game-dir "C:\Games\TH04-original" --output-dir "C:\Games\th04-portable" --fetch-support
```

For a downloaded release, save the script beside the executable and omit
`port64\` from the command. On Linux use `python3`, forward slashes and your
local folder paths. Put the output beside the executable used by `Play.bat`.

The script creates:

```text
th04-portable/
  th04-port64.exe          # from the release or your build
  Play.bat                # from the release or port64/
  Play-no-life-loss.bat    # optional; published EXE only
  run_no_life_loss.ps1     # used by the optional launcher
  th04.hdi                # generated from your three game files
  FREECG98.BMP            # font bitmap
  ym2608_adpcm_rom.bin     # 8192-byte rhythm sample data
  prepared-assets.json    # input/output hashes and support reference URLs
```

The generated HDI is a deterministic FAT12 **data container**, not a bootable
DOS installation. It copies the three payloads unchanged into `GENSO` using the
layout expected by the published executable. It omits DOS system files,
unrelated games and the source installation's scores/settings. Scores created
by the portable game live in the launchers' separate save folders.

For an existing compatible image:

```bat
py -3 port64\prepare_assets.py --hdi "C:\Games\existing-th04.hdi" --output-dir "C:\Games\th04-portable" --fetch-support
```

This validates and repacks the three supported files. It accepts the current
1024-byte-sector FAT12 layout at byte offset 38912. An arbitrary HDI may have
a different partition offset or filesystem: export its game folder instead.
The script refuses to replace differing existing output files. Choose a fresh
output folder when converting an older installation, then move the prepared
data files into your play folder while keeping your save directories.

## Font and sound data

`--fetch-support` downloads two pinned resources over HTTPS and checks their
SHA-256 identities before writing any output:

- [DOSBox-X `FREECG98.BMP`](https://github.com/joncampbell123/dosbox-x/blob/997f616e0886a835fc3660f2b935688f17f20d42/contrib/fonts/FREECG98.BMP):
  the 2048×2048 monochrome PC-98 font bitmap used by the text renderer.
- [libOPNMIDI `fmopn_2608rom.h`](https://github.com/Wohlstand/libOPNMIDI/blob/43b6bee61c943ebf91f50dbea649da04aa87fca2/src/chips/mamefm/fmopn_2608rom.h):
  the script extracts only the 8192-byte `YM2608_ADPCM_ROM` array into
  `ym2608_adpcm_rom.bin`. It does not compile or run the downloaded header.

| Prepared support file | SHA-256 |
| --- | --- |
| Downloaded `FREECG98.BMP` | `91d75314ac4f940ab13b3c33fb260ef1713865d025a94f09f6814a72e47dfa87` |
| `ym2608_adpcm_rom.bin` | `53afd0fa9c62eda3e2be939e23f3adf48a2af8ad37bb1640261726c5d5adeba8` |

The earlier tested font bitmap with SHA-256
`41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6`
is also accepted for offline preparation.

For an offline machine, supply those files locally:

```bat
py -3 port64\prepare_assets.py --game-dir "C:\Games\TH04-original" --output-dir "C:\Games\th04-portable" --font "C:\Resources\FREECG98.BMP" --rhythm-rom "C:\Resources\ym2608_adpcm_rom.bin"
```

Alternatively, prepare the files on a connected machine and copy the three
outputs to your play folder. The public release contains the program and
launchers; game data and these support files are prepared locally.

## Common preparation errors

| Error | Next step |
| --- | --- |
| `missing full-version Japanese files` | Extract both full-version installers into one folder. Check the sizes/hashes above; another revision needs explicit compatibility work. |
| `unsupported HDI layout` / `image is too short` | Export the image's installed game files; use `--game-dir`. |
| `download checksum differs` | Check connectivity/proxy responses; use the pinned files through the offline options. |
| `existing file differs` | Prepare in a fresh output folder. Existing data and scores are left in place. |
| Python command not found | Install Python 3.9+ and use `py -3` on Windows, or your Python 3 executable. |

`scripts/import_targets.py` serves reconstruction research: it expects a
specific locally attested collection archive. Use `port64/prepare_assets.py`
for the portable player's setup described here.
