# DOS build and Windows testing

This is the standalone **16-bit PC-98** product, called "native" in historical
`TH04_NATIVE_*` notes. It is distinct from the host x64 `port64/` product.
The standalone game need not reproduce whole original executable bytes;
historical exact reconstruction retains its separate acceptance contract.

## Build and launch

```sh
python3 scripts/preflight.py
python3 scripts/build.py --help
python3 scripts/build.py
python3 scripts/prepare_product_hdi.py --output-dir .analysis/runtime/candidates/NEW-game
python3 scripts/ci.py
```

`build.py` publishes the requested products after all builds/audits succeed.
Run only one Borland/Wine build at a time. `--only main` selects one product;
`--main-cpp-cache`, `--op-cache`, `--maine-cache` reuse verified input closures.
A successful incremental build is not a cold target/aggregate exact replay.

The English Windows entrypoint is
[`build-th04.cmd`](../scripts/windows/build-th04.cmd), with
[usage and progress display](../scripts/windows/README-build.txt).
The installed command at `D:\Entertainment\Game\Touhou\th04-reconstruct`
uses the Windows-to-WSL toolchain bridge and validated object/ZUN reuse by
default; `-Cold` requests a full source build, `-Normal` selects ordinary damage.
This is not a native Windows Borland compiler migration.

| Installed launcher | Product/image | Guest cycle budget |
| --- | --- | ---: |
| `start-th04-normal.bat` | Ordinary collision damage, `play-normal.hdi` | 24,000 |
| `start-th04.bat` | Separately built invincible MAIN, `play.hdi` | 24,000 |
| `start-th04-normal-highcpu.bat` | Same ordinary image | 36,000 |
| `start-th04-highcpu.bat` | Same invincible image | 36,000 |

For the 2026-10-08 demo, only the two standard launchers/profiles remain in the
Windows folder. Optional highcpu/reference launchers and x64 previews are
archived outside it. The installed English README covers demo commands. A
standard later export recreates optional profiles; missing reference settings
are derived from the verified standard profile, preserving its 24,000-cycle
runtime config. Current products/images/saves were not rebuilt or modified.

Invincibility is compiled through a private staged source overlay that clears
pending player hits; it is not a launcher-time memory patch or a maintained
player source change. OP/MAINE/ZUN agree between the two variants. Export
preserves the saved image's nonproduct files, configuration and scores.
Use English Windows input for Z/X gameplay keys.

## Retained product identities

Current inventories: `.analysis/build/th04-{normal,invincible}/build.json`.

| Normal product | Bytes | SHA-256 prefix | Relocations |
| --- | ---: | --- | ---: |
| MAIN.EXE | 199,455 | `cb4c5b667f9a2d5a` | 1,181 |
| OP.EXE | 79,372 | `ef37e6e890c4bfcbb` | 817 |
| MAINE.EXE | 72,246 | `7bfd7fd594377d03` | 663 |
| ZUN.COM | 7,723 | `d6043dce` | See build receipt |

Invincible MAIN is also 199,455 bytes (`0d99bc5a…`). These are product
identities, not hashes of the pinned original targets. Verify complete digests
from the build/package receipts before a replay; addresses must come from the
corresponding MAP, never an older note.

## Runtime controls

Use GAME.BAT through ZUN/OP/MAIN/MAINE; direct MAINE skips resident setup.
`prepare_product_hdi.py --original` supplies an attested original baseline.
`--config-from-run RUN_DIR` seeds a disposable image with saved configuration.
Original data and prepared source images remain immutable.

```sh
xvfb-run -a python3 scripts/probes/run_th04_maine_diagnostic_hdi.py \
  --prepared-dir .analysis/runtime/candidates/NEW-game \
  --output-dir .analysis/runtime/candidates/NEW-game/run \
  --frame-second 95 --time-limit 1000 --stop-after-frame
python3 scripts/probes/inspect_th04_handoff_trace.py --help
```

Scenarios in `config/runtime/scenarios/` include `op_menu.json`,
`main_stage1.json`, `main_progression.json`, `main_bullet_load.json`.
Record executed product, configuration, input, emulator and checkpoint hashes.
`--checkpoint-second` takes intermediate frames; held inputs use
`--input-event down:z@SECOND` / `up:z@SECOND`. `--key-delay-ms 300` gives menu
taps time to register. Private state/fault/load fixtures must not be exported
as ordinary playable products. Linux controls use normal/Pentium because the
recorded Linux dynamic-core setup aborted after PC-98 reset.

See [hardware reuse](PC98_HARDWARE_REUSE.md), [runtime setup](RUNTIME.md), and
[handoff](RE_HANDOFF.md) for coverage and pending natural-route tests.
