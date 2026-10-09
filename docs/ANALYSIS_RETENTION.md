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

Current native FM batch v1333 retains original/consumer source archives,
independent FM/SSG/music references, actual Windows component trace receipts
and negative logs below native `.analysis/port64/pmd-fm-v1333/`. Its terminal
readback shares235 full-byte-identical outputs, compresses failed traces with
verified decompression and retires private mutant programs/owned NTFS staging,
reclaiming325,083,136 allocated bytes (about310MiB). All730 protected hashes
remain unchanged, including399 sources and159 current programs. Retained
shared paths are immutable; subsequent producers must use fresh directories.

After both final CIs pass, the source-backed cache receipt
`.analysis/cleanup/pmd-fm-source-backed-caches-20261009.json` records retirement
of1,015 public-script/test/port64 CPython caches in the two worktrees, reclaiming
another17,125,376 allocated bytes. All1,130 mapped Python sources retain their
hashes. Combined terminal reclamation is342,208,512 bytes (about326MiB).

Native musical FM v1334 retains independent supplied-song/constructed producer
archives, the final consumer archive, full compressed reference/native/Windows
traces, regressions and negative source/log receipts under native
`.analysis/port64/pmd-music-v1334/`. Recovery readback verifies990 protected
hashes including403 sources,162 programs, active cache/link/compiler inputs,
original HDI/drivers and independent references. Two interim receipts measure
272,588,800 allocated bytes reclaimed (about260MiB). Terminal duplicates are
shared after full equality; failed/Windows traces are losslessly compressed,
private probes/variants and owned NTFS staging retired. Final terminal space
accounting failed on a missing interim-receipt key; failed script/log retained,
independent complete readback passes, and no terminal byte estimate is claimed.
After both final CIs, a persisted pre-deletion journal retires1,013 source-backed
CPython caches below public scripts/tests/port64, adding17,059,840 measured
allocated bytes;1,131 Python source hashes remain unchanged. Measured total
for this batch is289,648,640 bytes (about276.2MiB). Cache receipt:
root `.analysis/cleanup/pmd-musical-source-backed-caches-20261009.json`.
Use fresh output directories; retained hardlinks are immutable.

Native FM music/effects handover v1335 retains separate original and final
consumer source archives, rejected candidates/invalid fixture observations,
complete compressed original/GNU/UBSan/Windows traces and replay receipts under
native `.analysis/port64/pmd-fm-join-v1335/`. Whole readback verifies1569
protected hashes including407sources/165current products and compiler/cache/link
inputs. Persisted pre-mutation journals measure1,401,487,360allocated bytes reclaimed
(1336.6MiB). Terminal duplicates share only after complete equality; raw
negative/Windows traces, experimental binaries and owned NTFS staging retire
only after exact decompression/archive readback. All independent references,
source identities and current products remain. Future replay uses fresh paths.

Native musical SSG v1336 retains412sources/168current products, complete
original/native/Windows traces, failed candidates and independent producer/
consumer archives under native `.analysis/port64/pmd-musical-ssg-v1336/`.
Full readback verifies1855protected hashes; pre-mutation journals measure
1,311,682,560allocated bytes reclaimed (1.22GiB). Completed native `.o`/`.a`
files retire along with raw Windows/negative outputs and owned NTFS staging.
Current executables/cache/link identities and all independent reference/source
archives remain. CMake rebuilds the absent intermediates; use fresh trace paths.

Native combined FM/SSG v1337 retains 416 source inputs/171 current products,
full independent original/native/Windows traces and separate producer/consumer
archives under native `.analysis/port64/pmd-combined-v1337/`. The Windows
first-load snapshot is independently bound; final readback compares all 66
original cases. Full readback verifies 2111 protected hashes and measured
pre-mutation journals reclaim 1,112,240,128 allocated bytes (1.04 GiB).
Terminal negative binaries/raw traces, owned NTFS stage and native `.o`/`.a`
files retire; current programs, independent references, inconclusive/failed
probes and source/cache/link/compiler identities remain. Use fresh replay paths.
Post-CI cleanup separately retires 1,013 generated Python cache files after
checking their source hashes, reclaiming 17,059,840 allocated bytes; receipt:
`.analysis/cleanup/pmd-combined-post-ci-caches-20261010.json`.

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
