# 東方幻想郷 ～ Lotus Land Story

<p align="center">
  <img
    src="resources/title-screen.png"
    width="640"
    alt="Original Japanese TH04 title screen">
</p>

<p align="center">
  <img src="resources/progress.svg" alt="TH04 four-artifact boundary and function acceptance progress">
</p>

This repository reconstructs the original Japanese PC-98 **Touhou 4:
Lotus Land Story**. The active goal is to build `MAIN.EXE`, `OP.EXE`,
`MAINE.EXE` and `ZUN.COM` from maintained TH04 source and run the full game.
Native builds need not reproduce the original executable bytes. MAIN's two
remaining historical exactness cases are deferred.

[Current state and remaining work](docs/RE_HANDOFF.md) is the working entrypoint.
Historical function acceptance is reported by `python3 scripts/status.py` and
[PROGRESS.md](docs/PROGRESS.md); it is separate from gameplay completion.

The v1475 actual source MAIN defeats Elly at 12792 and reaches Stage4 init/score1
with original OP/MAINE/ZUN/assets. All 13378 pool/state snapshots,13377 actual
words and 33609 raw/resident/RNG rows match the original. All 23 full live-font
RGB/TRAM/palette samples pass. Source strict aggregate retains 19 postactor keys
and 23 raw GDC differences. Native 12889 still differs by 407 blinking pixels;
1805 native keys remain separate. No emulator is live. See the current handoff.

The v1477 private physical-device experiment preserves all 52 keyboard edges,
including four tails after UI exit. Nine-pool/stable-state gates and all 22 full
Stage3 RGB samples pass, but two of four literal-player inputs fail. Actual
original/source RAM shows BIOS Enter released while key_det retains8192; the
native input-latch model remains unresolved. No game-code or campaign claim.

The prior v1473 repair propagates and consumes Elly's scythe hit through MAIN's player
latch. Cold GNU/UBSan reproduce original hit8046 and GameOver8085 with8082 complete
nine-pool/state snapshots and8086 raw score/state/resident/RNG-count rows. All79
old8000 outputs remain unchanged. Stage4 and campaigns stay open; see the
[current handoff](docs/RE_HANDOFF.md). Current closure is566/a7606e66.

The retained v1467 records a complete original 8000-update Stage3 route. Native
566/4787233c replays its literal inputs: both cold GNU/optimized UBSan programs
agree on all 79 files, 8001 nine-pool snapshots, 8010 stable-state records and
nine complete RGB/TRAM/DAC samples. Palette-bearing dialogue loads refresh the
player palette; enemy opcode8F tile writes preserve background-prefix order.
Fresh GNU 83 CTests and UBSan/session checks pass. One requested/readback input
mismatch and 712 volatile post-actor keys remain separate. Original/source-DOS
paired MAIN was then at completed Stage3 4000; current source 13377/Stage4 is documented
in the handoff. Continuous display, physical timing,
full campaigns and artifact exactness remain open. Completed products retire
after recovery checks; see the [current handoff](docs/RE_HANDOFF.md).

Native development is active. Historical frozen554/31e6b3d7 GNU and optimized
UBSan passed four strict natural headless routes: Easy ReimuA, Normal ReimuA,
Normal MarisaA and Extra ReimuA earned by the same-run Normal save. All four
complete captures/saves agree across compilers, with real clear mask1 and no
Continue. The new554/a79f199f reader rejects sentinel/high masks, wrong
partitions, Bad Ending, incomplete stages and full-checksum failures. Previous
failed window Normal acceptance stays revoked. Original full-game parity,
complete pictures, physical timing and Windows remain open; see the
[handoff](docs/RE_HANDOFF.md) for scope and recovery.


## Build and run

The retained v1463 repair covers a carried clear-bonus palette tone at stage-session
completion. Both cold programs match 14 complete original WORD/DAC samples;
all eight state wires, legacy routes and 177 prior display observations remain
unchanged. The later 14 sampled full RGB/TRAM comparisons above pass; raw graphics
indices and every-frame display remain open. See [current handoff](docs/RE_HANDOFF.md) for evidence and recovery.


Current v1462 completes actual original/source4000-update Stage3 routes after
real Stage1/Stage2 clears. Across43193 boundaries, configured fields/RNG,
nine pools,22 states,private3 and38 video regions agree. DOS aggregate remains
false for682 post-reset keys/31563 raw-GDC records plus12 auxiliary GDC records.
Current566/1ad0ea4c GNU/UBSan match28793 selected scalars/14396 nine-pool
snapshots and9836 current Stage1 pool snapshots. All8 wires and physical saves
agree;510 native volatile keys remain separate. Both roles68 full memories and
43193 full resident256 windows pass;12 UI full windows were not captured.
Frozen recovery executes both actual programs and the full GNU paired reader,
reproduces all vectors and retires21 restored aliases. The prior extent follows.

The prior v1461 original/reconstructed DOS comparison completes 10394 Stage2
updates, Kurumi defeat/clear, Stage3 initialization and its first update. Nine
full pools, 22 states, 11636 ordered RNG calls and 38 configured video regions
agree over 31196 boundaries. The DOS aggregate retains
544 post-reset key/31196 raw-GDC differences and
12 additional UI raw-GDC differences. Older vectors remain separate.

This runtime pair replaces MAIN only; OP, MAINE, ZUN and game assets remain
the pinned originals. It does not establish a complete four-source campaign.

Closed 566/4c3c50cb cold GNU and optimized UBSan match 20795 selected scalar
records and 10397 full nine-pool snapshots, actual consumed inputs, homing and
Boss/Midboss/RNG. Physical CFG/SCR files and the legacy 3500/8000 plus 59 RGB/TRAM
fixtures pass. Native Stage2 pictures, natural clocks, complete campaigns, NP2,
Windows, pristine provenance and historical exactness remain open. Both full
goals stay active; see the [current handoff](docs/RE_HANDOFF.md).

With local inputs and the toolchain installed:

```sh
python3 scripts/preflight.py
python3 scripts/build.py
# Outputs: .analysis/build/th04/{MAIN.EXE,OP.EXE,MAINE.EXE,ZUN.COM}
python3 scripts/prepare_product_hdi.py \
  --output-dir .analysis/runtime/candidates/NEW-game
xvfb-run -a python3 scripts/probes/run_th04_maine_diagnostic_hdi.py \
  --prepared-dir .analysis/runtime/candidates/NEW-game \
  --output-dir .analysis/runtime/candidates/NEW-game/run \
  --frame-second 60 --time-limit 75
```

Run one Borland/Wine build at a time. `--only main` selects one product;
`--main-cpp-cache PATH` reuses objects only when their inputs match a prior MAIN
build. A fresh build is the final source-migration check. The build rejects
compiler/linker failures and publishes outputs after all requested products
succeed. Runtime validation remains separate.

Image preparation modifies a disposable copy of your supplied original-data
image. Original executables and game assets are never committed.

## Setup

The build uses pinned Turbo C++ 4.0J, TASM and TLINK under Wine. ReC98 supplies
the pinned MS-DOS Player and local sprite conversion inputs; product source
and headers live in this repository and do not use `masters.lib`.

```sh
mkdir -p _reference
git clone https://github.com/nmlgc/ReC98.git _reference/ReC98
git -C _reference/ReC98 checkout --detach b6ba5b0a529edbb31efdf8c0e939263804f8ee47
python3 scripts/import_targets.py /path/to/your/legal-copy.rar \
  --retain-runtime-image
bash scripts/bootstrap_toolchain.sh
python3 scripts/preflight.py
```

Host tools include Python 3, Wine, archive utilities and, for runtime checks,
the pinned DOSBox-X build plus Xvfb, xdotool and ImageMagick. See
[RUNTIME.md](docs/RUNTIME.md) for emulator setup. Analysis/database work also
uses `bootstrap_analysis_toolchain.sh` and `scripts/ghidra.py`.

## Local inputs

Supply your own legal copy.  The importer selects the Japanese `zun.hdi` and
requires these artifacts:

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| `OP.EXE` | 42,290 | `8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f` |
| `MAIN.EXE` | 156,258 | `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b` |
| `MAINE.EXE` | 38,035 | `670de6ba907a2edbc1592de810acd92e5b89541d3dc35b70210171166d1713f8` |
| `ZUN.COM` | 7,754 | `0a12e9a489d3b704a77cf04ca3062ee48f298a9df6d237dc7dad46986e2d116e` |

These hashes currently have `candidate-local-attested` provenance: they
identify the supplied Japanese image exactly, while independent pristine-dump
confirmation remains open.  That qualification is kept separate from whether
a candidate build exactly matches the pinned bytes.

## Source and validation

Source belongs under `src/main/`, `src/op/`, `src/maine/`, `src/zun/` and
`src/shared/`, organized by subsystem. See [SOURCE_LAYOUT.md](docs/SOURCE_LAYOUT.md)
and [ARCHITECTURE.md](docs/ARCHITECTURE.md). ReC98 implementations are migration
inputs; their progress and exactness claims do not transfer automatically.

Use [RE_WORKFLOW.md](docs/RE_WORKFLOW.md) for implementation work. Install public
validation dependencies with `python3 -m pip install -r requirements-ci.txt`;
CI also checks out the pinned ReC98 source-routing reference used by the manifest
audit; this is a validation input, not a product include dependency. Private
CPU/runtime Oracles additionally require their documented local tools. Finish with:

```sh
python3 scripts/ci.py
git diff --check
```

Historical evidence is routed through [the reconstruction index](docs/reconstruction/README.md),
`config/units.csv` and `config/evidence.csv`. [ORACLES.md](docs/ORACLES.md)
defines the separate byte-exact acceptance contract. Local tools, targets,
images, builds and reports remain in ignored directories.

## License

Repository-authored code and documentation are provided under the MIT License.
This does not grant rights to the original game, its assets, or referenced
third-party work.
