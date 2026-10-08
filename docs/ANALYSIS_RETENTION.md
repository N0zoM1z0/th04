# Private build and analysis retention

`.analysis/` is ignored private state. A historical evidence path is provenance,
not a guarantee that its expanded directory remains present. Durable commands,
hashes, conclusions and negative results belong in checked-in notes/ledgers.
A verified private archive supplies recovery where the input cannot be rebuilt.

## Keep live

| Surface | Reason |
| --- | --- |
| `.analysis/targets/`, runtime source HDI/font/assets | Pinned original inputs; never commit or replace silently |
| `.analysis/toolchain/`, `.tools/`, emulator sources/binaries | Attested Borland/Wine, Ghidra/JDK, CPU observer and PC-98 runtime tools |
| `ghidra-project/`, active database attestations/exports | Target-dependent analysis and boundary evidence |
| `.analysis/build/th04-normal`, `th04-invincible` and their validated cache dependencies | Current DOS products; preserve fast builds |
| `port-modern-64/.analysis/port64/{linux,windows,ubsan}-live-v1251` | Current native incremental caches; deleting them makes the next build cold |
| Current original CPU references and component inputs | Independent Oracle provenance, not disposable duplicates |
| `.analysis/reconstruction/receipt-archive/` and manifests | Recovery of archived captures/snapshots |
| Installed Windows DOS package, two launchers, assets and independent save images | Current demo state; x64 previews are archived |

Worktree paths in the table are below `.analysis/worktrees/`. Keep native work
on its independent branch. Never use blanket `git clean -fdx`, `rm -rf .analysis`
or a global Wine kill as cleanup.

## Completed archive routing

| Subject | Receipt location (relative to repository unless stated) |
| --- | --- |
| Retired expanded product source/build snapshots | `.analysis/cleanup/old-product-snapshots-20261005/receipt.json` |
| Historical generated fixture buffers | `.analysis/cleanup/historical-fixtures-20261005/receipt.json` |
| Old runtime image/screenshot/Windows preview trees | `.analysis/cleanup/superseded-artifacts-20261005/receipt.json` |
| Earlier x64 traces and Windows executables | `.analysis/cleanup/historical-port-builds-20261005/receipt.json` |
| Deduplicated historical gzip and preview packages | `.analysis/cleanup/build-followup-20261005/receipt.json` |
| Development media | `.analysis/cleanup/development-media-20261005/receipt.json` |
| Verdict/congratulations captures | Native `.analysis/port64/{verdict-v1295,post-verdict-v1296}/media-archive-receipt.json` |
| Latest registration capture sharing and early 90-snapshot archive | Native `.analysis/port64/registration-render-v1299/capture-storage-receipt.json` |
| This organization batch | `.analysis/cleanup/organization-20261005/receipt.json` |

Native locations are relative to `.analysis/worktrees/port-modern-64`.
Receipts contain archive/member hashes and restore commands. Historical v1293/
v1295 Windows previews are archived; installed GUI is v1296 with v1295 rollback.
Old handoff retention claims described their time boundary, not today's active
package. Do not sum historical reclamation figures without checking overlap.

## Organization batch, 2026-10-05

51 retired DOS build output directories and 11 inactive large protection hash
lists are archived with full readback (205 files). The clean detached semantic
checkout at `853d446` is removed; that commit remains in both retained branches.
Its `.analysis`, tool, reference and database roots were symlinks, not deleted
inputs. The receipt records 55,144 unchanged protected hashes and approximately
122 MiB net allocated space reclaimed after archive/manifest overhead.

Current DOS products and cache dependencies, three native caches, tools,
original inputs, databases and Windows files remain live. Restore archived
`protected-before.json` lists before re-running an older private cleanup script;
its original path is still recorded in the older receipt. Restore commands are
in the organization receipt above.

## Windows DOS demo cleanup, 2026-10-08

User-authorized cleanup retains only the normal/invincible DOS versions and
necessary runtime/build files at `D:\Entertainment\Game\Touhou\th04-reconstruct`.
53 removed/modified files pass archive-member hash/size readback before deletion.
The archive includes x64 v1296/rollback, optional profile launchers/configs and
prior package metadata/README. All 18 protected files remain byte-identical,
including both complete save images and all eight product binaries.

About 112 MiB of file contents are removed from Windows; a 31 MiB recovery
archive remains under `.analysis/reconstruction/receipt-archive/`.
Receipt, member manifest and restore command:
`.analysis/cleanup/windows-dos-demo-20261008/receipt.json`.
Only README/package metadata is updated; removed optional profile fields no
longer advertise absent files. Export reconstructs a missing reference budget
from the verified standard profile. Native source/tools/caches stay retained.

## Safe cleanup procedure

1. Inspect git/worktree state and active writers; classify generated outputs,
   required tools, immutable inputs and currently referenced Oracle dependencies.
2. Inventory candidate paths, size/digest and allocated blocks. Protect current
   products/cache closures, source, tools and Windows saves with before hashes.
3. For non-rebuildable historical evidence, create a lossless archive, check
   every member's size/digest and retain restore instructions before removing
   expanded files. Keep small result/receipt logs where useful.
4. Share byte-identical completed captures only after independent producer and
   full readback. **Hard-linked paths are immutable**: use a new output directory
   or atomic replacement. Re-running a writer in place can corrupt all aliases.
5. Recheck protected hashes, sources, ledger/CI and actual net allocated space;
   record the scoped result. Do not imply a new runtime or exact acceptance.

`python3 scripts/prune_analysis.py` defaults to dry run and uses
`config/analysis_retention.toml`. Its generic policy predates later native
caches; review its explicit keep/archive coverage before selecting `--apply`,
`--prune-probes`, `--prune-exact-replays` or `--prune-caches`. It is not a
permission to remove arbitrary worktrees, unique CPU traces or current caches.
Native registration verifiers reject existing output directories. Restore tar
members first, then decompress older `.gz` paths if the receipt requires it.
