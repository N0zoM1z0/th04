# Portable data preparation

## Scope

The public Windows preview consumes `MAIN.EXE`, `幻想郷ED.DAT` and `東方幻想.郷`
from a `GENSO` directory. The original three file identities are listed in
[PREPARE_DATA.md](../../PREPARE_DATA.md). `MAIN.EXE` is hash-attested against
`config/targets.toml`; the archive hashes were read from the same retained HDI.
Target provenance remains `candidate-local-attested`.

The original installation manual describes two floppies and loose-file hard
disk installation (external corroboration, via the linked transcription).
The reader workflow therefore starts with installed/extracted files rather
than the development collection archive required by `scripts/import_targets.py`.

## Container contract

`port64/main.cpp` currently fixes its FAT12 reader to partition offset 38912,
1024-byte sectors, eight sectors per cluster, one reserved sector, two
four-sector FATs and 1536 root entries. Merely naming another disk `th04.hdi`
does not give it that geometry.

`port64/prepare_assets.py` writes a deterministic 21,415,936-byte data container
with that geometry. Its boot/header/directory bytes are authored metadata;
only the three hash-checked user payloads are copied, unchanged. The generated
container is not a bootable DOS disk or an original disk dump. It contains no
source configuration or score files. Its SHA-256 is:

`23e7b0298d1256db92c1336988c83be0a60d656ab3dee3f84360dd74d5904633`

This differs from the retained development image
`0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd`;
the three runtime payload hashes agree. The existing image reader is explicitly
limited to this layout and rejects other BPBs/FAT mirror disagreements/chains.
Other images must first export their installed game files.

## Replays and results (2026-10-28)

- Five checked-in Python tests use authored synthetic multi-cluster files.
  They cover deterministic round trips, identification despite garbled names,
  payload/BPB corruption, FAT mirror mismatch/cycles, and all-output validation
  before existing files can be replaced. Command on the portable branch:
  `python3 -m unittest discover -s tests -p test_prepare_portable_assets.py -v`.
- The public `--game-dir ... --fetch-support` command was run using the private,
  attested three-file fixture. The pinned font/header downloads passed their
  hashes; extracted rhythm data equals the existing 8192-byte reference ROM.
- Independent `mcopy -i prepared/th04.hdi@@38912 ::GENSO/* OUTPUT` recovers all
  three byte-identical payloads. Feeding those garbled-name exports back to
  `--game-dir` gives the same container hash. `--hdi` also reads the retained
  original geometry and recovers the same payloads.
- Actual Windows release EXE
  `8257fbf8e952690ab8963844ba92f810399f9f67ca74db463ca006aaf3fbe750`
  ran `--resident-sound-checks` on the generated image. With the preceding
  font, all 65 outputs equal the retained original-image run: nine settings,
  27 BMPs, nine mixed PCM files, state/configuration/score boundaries and live
  Ending/Staff measure consumers. Repeating with the newly fetched upstream
  font also leaves all 65 outputs equal for this corpus.

Runtime cases use the maintained `verify_windows_background.ps1` controller,
fresh private inactive desktops, `--mute`, owned process/input adapters and
bounded jobs. They do not use physical input or the active desktop. No game
C++ source or executable changed, so the prior public-source cold build stays
the binary build evidence; this batch exercises its data-container boundary.
Font glyph coverage beyond these scenes is separate from the container-byte
comparison.

Private replay inputs/receipts live under `.analysis/readme-20261028/` and
`C:\Users\21992\AppData\Local\Temp\TH04-readme-20261028`. Retain hashes and
receipts; duplicate images/component captures are regenerable. No original
payloads, bitmap or ROM are added to Git or the public release.
