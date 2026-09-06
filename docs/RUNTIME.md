# Headless PC-98 runtime setup and use

Runtime emulation is optional for static, raw-exact reconstruction. It becomes
necessary when a bounded claim depends on timing, input, self-modifying code,
VRAM/palette state, sound state, or another behavior that static and compiler
Oracles cannot settle. Runtime similarity never waives a byte mismatch.

The repository currently defines a **headless host smoke baseline**, not a
deterministic TH04 Runtime Oracle:

- primary: DOSBox-X 2024.03.01 from Ubuntu 24.04;
- mode: SDL dummy video and audio, no GUI/menu, isolated XDG state;
- machine: PC-98, 16 MiB, normal core, fixed 8,000 cycles;
- PC-9801-86-compatible FM board, 2.4576 MHz PIT, 2.5 MHz GDC;
- private input image: the same hash-attested Japanese `zun.hdi` used by the
  target importer;
- secondary cross-check: Neko Project II debug build, intentionally deferred.

DOSBox-X's [official PC-98 guide](https://github.com/joncampbell123/dosbox-x/wiki/Guide%3APC%E2%80%9098-emulation-in-DOSBox%E2%80%90X)
documents `machine=pc98`, PC-98 hard/floppy image mounting, and support for the
early Touhou games. Its [command-line reference](https://github.com/joncampbell123/dosbox-x/wiki/DOSBox%E2%80%90X%E2%80%99s-Command%E2%80%90Line-Options)
documents the headless, config, command, and time-limit switches used here.
The Ubuntu package is intentionally the locally calibrated baseline, not a
claim that it is the newest upstream release.

`config/runtime.toml` pins the calibrated package, executable digest, config,
image identity, and required startup markers. The actual profile is
`config/runtime/dosbox-x-headless.conf`.

## Install on Ubuntu 24.04

The package is convenient and has native PC-98 support:

```bash
source ~/clash.sh
proxy_on
sudo apt update
sudo apt install dosbox-x
```

The calibrated host has package `2024.03.01+dfsg-1build2` and `/usr/bin/dosbox-x`
SHA-256
`30a5fdf8fa95abaf7bae1a9e624ccfc9e26e5357a19cc567bf3a2ac659699258`.
`scripts/smoke_runtime.py` fails closed if either the executable or checked-in
configuration differs. A newer package is an uncalibrated environment until
its identity and scenarios are reviewed; do not update the hash merely to make
the check pass.

## Retain the private runtime image

The normal importer deletes its temporary HDI after extracting executables.
Ask it to retain the exact Japanese image under the ignored `.analysis/` tree:

```bash
python3 scripts/import_targets.py /path/to/legal-copy.rar \
  --include-all-games-smoke \
  --retain-runtime-image
```

The command verifies the HDI size, SHA-256, Anex86 geometry, FAT partition and
volume label before placing it at `.analysis/runtime/images/zun.hdi`. The image,
archive, executables, logs, and receipts are private and must never be committed.

## Headless checks

Check PC-98 startup without booting game media:

```bash
python3 scripts/smoke_runtime.py
```

Then check that the attested HDI can be mounted and enter its boot path:

```bash
python3 scripts/smoke_runtime.py --boot-image
```

Both commands force `SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy`, isolated
temporary XDG directories, `-nogui`, `-nomenu`, and a hard time limit. They
write ignored diagnostics to:

- `.analysis/runtime/smoke.log`;
- `.analysis/runtime/smoke-attestation.json`.

A passing result means only that the exact local DOSBox-X binary, checked-in
PC-98 profile, and (when requested) exact HDI reached the expected startup
path without a GUI. It does not prove a title screen, deterministic frame,
correct timing, or TH04 semantic behavior.

## When a real Runtime Oracle is needed

Create one bounded scenario rather than extending the smoke check. Pin and
record all of the following:

1. target/candidate digests and exact HDI or minimal DOS image;
2. emulator source/build digest and complete config;
3. reset/save-state origin, CPU cycles, PIT/GDC clocks, memory, FM board, and
   any fonts or ROMs;
4. tick/frame-based input events and checkpoint definitions;
5. raw memory ranges, events, VRAM, palette, and relevant audio state;
6. repeated original/candidate runs from the same state;
7. a one-variable metamorphic run and replay under a pinned Neko Project II
   debug build.

Store bulky traces below `.analysis/runtime/`; check in only scenario
definitions, compact digests, reducers, and replayable evidence rows. Follow
the Runtime skill and `docs/ORACLES.md` before treating such a run as evidence.

## Why Neko Project II is not installed yet

The available [NP2kai source tree](https://github.com/AZO234/NP2kai) has
additional SDL/wx build dependencies and requires its own build/config
attestation. Installing it now would not improve static exact matching. Add it
when the first concrete runtime claim needs cross-emulator falsification; at
that point, pin the exact source revision and build rather than accepting an
arbitrary host binary.
