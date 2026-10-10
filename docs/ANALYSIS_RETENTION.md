# Private build and analysis retention

v1369 retains complete raw video streams and their independent ordinary controls
under `.analysis/runtime/candidates/dos-demo-v1369-*/`. Every stream losslessly
stores3996 x279809 B per demo using XOR/gzip. Keep the full raw GDC diagnostic
bytes, invisible graphics tails, palette entries and first-difference blocks;
programmed-state comparison does not discard the excluded scan clocks.
Executed failed/corrected producers are frozen as `producer-source-v1/v2`, with
the final reader/source/test inputs separately frozen in `reader-source/` under
`.analysis/reconstruction/probes/demo-video-v1369/`. Host ABI, namespace failure,
full comparisons and bounded carpet data/ring witnesses stay replayable.

Initial sharing of104 immutable completed-capture paths reclaims87,281,664
allocated B; the next112-path pass reclaims36,651,008 B. All complete bytes,
sizes and modes agree before sharing and after readback;64/74 protected hashes
remain unchanged. Both journals and readbacks live in the v1369 directory.
Only completed immutable images/fonts/REC files/traces are shared, never live
execution images. The separate cold MAIN repair cache and existing11MiB cache
remain retained. Native x64 worktree/source and Windows packages are unchanged.

After complete repaired ordinary/video comparison, a142-path sharing pass
reclaims another37,371,904 allocated B;103 protected hashes recheck unchanged.
Sharing totals161,304,576 B (about153.8MiB) before journals. All twelve completed
video gzip files total503,789,277 B; none of the old/repaired candidate gzip
streams is byte-identical, so no stream is shared or discarded. The unchanged
Demo2/3/4 programmed-region hashes do not imply raw GDC clock equality. Keep
`repair-copies-before.json`/`repair-copies-readback.json` and every full stream.

After terminal final CI, `source-caches-before.json` and `source-caches-readback.json`
retire529 regenerable public Python caches/8,830,976 allocated B. Every source
and195 protected hashes recheck. `final-independent-readback.json` separately
checks all three sharing journals, cache absence,306 protected hashes and26
archived source inputs, final423-test CI and complete replay verdicts. Combined
copy/cache reclamation is170,135,552 B (about162.3MiB) before journal overhead.
Historical exact states/denominator remain unchanged; original source language
of the new DATA owner remains unknown. All build/game/comparison jobs are terminal.

v1368 reuses all immutable v1367 DGROUP streams; no new bulky capture or product
build. After terminal CI,522 regenerable public Python caches retire8,724,480
allocated B (about8.3MiB) before journal overhead. All522 retained source hashes
and49 protected input/product/trace/receipt hashes recheck unchanged; nine
frozen reader/test inputs and all four complete comparison verdicts also pass
separate readback. Journals and `final-independent-readback.json` live under
`.analysis/reconstruction/probes/demo-globals-v1368/`. Streams, prior negative
evidence and the11MiB cold product cache stay available; native worktree is unchanged.

v1367 retains eight complete DGROUP streams (3996 x65536 B each) using reversible
XOR/gzip storage, with full original/candidate scalar/caller traces and producer
source snapshots. All jobs are terminal. Sharing byte-identical immutable HDI/
font/demo copies across84 paths reclaims65,937,408 allocated B; all84 complete
hashes and37 protected artifact/trace/stream/receipt hashes recheck unchanged.
Journals: `.analysis/reconstruction/probes/demo-dgroup-v1367/immutable-copies-*`.
Completed capture trees are immutable; execute new captures only in fresh paths.

The failed v1 Demo1 gzip (71,510,555 B) becomes a6,036,503-byte DG2 archive; a
separate full decoder regenerates the original gzip byte-for-byte, SHA-256
`28c053d7…`. Net65,478,656 allocated B reclaimed from the original gzip through
the intermediate zstd archive to the final delta archive. No failed receipt,
log, source or observed DGROUP byte is discarded. Final mapping is
`dos-demo-v1367-original-dgroup/failed-stream-delta-retention.json`.
Recovery/verification: run
`python3 .analysis/reconstruction/probes/demo-dgroup-v1367/restore_failed_stream.py`
without arguments to hash a full reconstructed gzip, or add `--output FRESH.gz`
to materialize it. Verify the saved expected size/SHA before use; do not run the
archived failed consumer as a current acceptance reader. The intermediate zstd
journal is historical; its replacement/restoration mapping is explicit above.
The8-stream current comparisons and old11MiB product cache remain available.
Final CI passes377 tests plus live Ghidra/mutation controls. Its explicit
compileall syntax gate regenerates caches even with PYTHONDONTWRITEBYTECODE;
final cleanup retires520 caches/8,695,808 allocated B. Full source and44
protected hashes read back unchanged. Four legitimate late observer/reader/test
edits have separately hash-verified old-source archives and current-source
bridges; the earlier522-cache journal remains historical. Copy/archive/final
cache reclamation totals140,111,872 allocated B (about134MiB) before journals,
excluding the earlier cache interval to avoid double counting. Independent
final receipt: `demo-dgroup-v1367/final-retention-post-ci.json`. All eight current
streams total35,534,216 stored B, losslessly preserving2,095,054,848 DGROUP B.

v1366 shares byte-identical immutable HDI/font/demo copies across seven
terminal v1365/v1366 DOS captures. All49 files retain their complete hashes;
unique allocated storage falls303,779,840 to193,323,008 B, reclaiming
110,456,832 B before journal overhead. Only identical copies become hard links.
Treat those completed capture directories as immutable; new executions require
fresh paths. Original inputs, executed products, maps, complete traces,
diagnostic DGROUP dumps and failed receipts remain.
The full journal and independent hash/storage readback are
`.analysis/reconstruction/probes/demo-angle-v1366/immutable-copies-before.json`
and `immutable-copies-readback.json`. This is storage deduplication, not new
runtime evidence or permission to reuse an old execution image.

After both new captures finish, `final-copies-before.json` and
`final-copies-readback.json` extend the same immutable sharing to63 files and
reclaim another22,540,288 allocated B. After final CI,514 regenerable public
`scripts/`/`tests/` Python caches retire8,605,696 allocated B; every corresponding
source and26 protected input/product/trace/receipt hashes recheck unchanged.
The cache journals are `source-caches-before.json`/`source-caches-readback.json`
under the same v1366 probe directory. `final-retention-independent.json`
independently rechecks all three journals. Combined reclamation is141,602,816
allocated B (about135MiB) before journal overhead. The new cold MAIN's11MiB
source/object/link cache remains available for validated incremental builds.

v1364 handoff cleanup retires1,019 regenerable Python caches under root/native
`scripts/`, `tests/` and native `port64/`, after both CIs finish. Net16,543,744
allocated B (about15.8MiB) reclaimed after the retention journal; final small
receipt overhead excluded. Every corresponding source hash and516 protected
source/archive/program/input/save/trace hashes recheck unchanged; a separate
post-retirement reader rechecks all hashes and absent paths. No compiler build,
game launch or deletion of user packages/saves/targets/toolchains.

Root `.analysis/cleanup/handoff-source-caches-v1364.json` is the full journal;
`handoff-source-caches-readback-v1364.json` and
`handoff-source-caches-independent-v1364.json` are the two readbacks.
Python recreates these caches from retained public source. Executed consumer491
and492 snapshots remain distinct from formatted current492 inputs; source
archives are retained in native `bomb-input-v1362/` and `bomb-window-v1364/`.

v1363 archives and retires the unused historical mutable native
`.analysis/port64/ubsan-live-v1251/` build materialization. All936 files, modes,
sizes and SHA-256 values read back from a complete recovery archive before
retirement; a separate reader rechecks every archive member after retirement.
No process executable/cwd/argv/mapping refers to the old tree. Net252,231,680
allocated B (about240.5MiB) reclaimed after retaining the105,898,956-byte archive
and journal; final receipt overhead excluded. This preserves the current bytes
of an old mutable build, not a cold historical replay or refreshed acceptance.

Recovery: root `.analysis/cleanup/ubsan-old-build-v1363/` holds
`ubsan-live-v1251.tar.gz`, `retention-before-v1.json` with all original paths/
modes/hashes, and the independent readback. Extract into a fresh scratch root
(`tar -xzf ARCHIVE -C FRESH_DIR`), then verify every member against the journal
before use. Active v1356 programs and pinned helper/HDI/font/source archive
hashes remain unchanged; current traces, saves, user packages and toolchains are
excluded. That muted private-Xvfb Turbo0 candidate is now terminal and its
independent route/dense readback passes; the v1363 live observations remain
historical. No Windows GUI, host keys, audio device or new build is involved.

The v1361 Turbo0 candidate is now terminal failed-clear; its separate bad-save
Scores reader and final CIs pass. Final terminal-CI cache pruning retires962
source-backed caches/net15,650,816 allocated B, including now-unused port64
helpers. Receipt: `.analysis/cleanup/slowdown-terminal-caches-readback-v1361.json`.
Together with the earlier reader-CI interval (955 entries/net15,478,784 B), this
turn's two distinct cleanup intervals reclaim31,129,600 allocated B (about29.7MiB).
Programs, current failed trace/actions, saves, source archives and all negative
receipts remain for ordinary input-policy review; no new build is produced.

v1361 both final CIs pass (root includes live Ghidra/mutation replay). The
independent reader and eight controls create no build/game output. Source-backed
public-script caches retire955 files after source/protected hash readback,
net15,478,784 allocated B (about14.8MiB), subtracting the journal. Active port64
helper caches, program, trace, saves and frozen consumer snapshots are preserved.
Root receipt: `.analysis/cleanup/slowdown-reader-caches-readback-v1361.json`.

v1360 CIs pass on both branches, including root live Ghidra/mutation replay.
Scoped post-CI pruning retires955 source-backed public-script caches after full
source/protected hash readback, net15,478,784 allocated bytes (about14.8MiB),
subtracting the journal. Active port64 helper caches, program, source archive,
trace and physical saves are excluded. No new build intermediates are created.
Root receipt: `.analysis/cleanup/slowdown-source-caches-readback-v1360.json`.

v1359 final CIs pass on both branches, including root live Ghidra replay and
mutation controls. No new build intermediates are created. Post-CI cleanup
retires961 source-backed Python caches after all source and protected-input
hashes read back; net15,634,432 allocated bytes (about14.9MiB), subtracting the
journal. Programs, source archives, traces, physical saves and negative readers
remain. Root receipt: `.analysis/cleanup/host-storage-source-caches-readback-v1359.json`.

Post-final-CI pruning retires 1,018 source-backed public Python caches,
net 16,633,856 allocated bytes after the persisted journal and full source
hash readback. Root receipts: `.analysis/cleanup/full-window-post-ci-caches-v1356*.json`.

v1356 also archives and retires 1,190 terminal build intermediates after
complete member/hash readback, net 398,848,000 allocated bytes. A second
full archive retires 201 completed contract program materializations,
net 393,736,192 allocated bytes. All 204 current program bytes and
identities remain recoverable: three game programs stay live; restore
`contract-programs-recovery-v2.tar.gz` into `.analysis/product-v1356/`
before running CTest. The complete 485-input producer source vector,
CMake/link/compiler metadata, preceding 204 programs, failed recipes,
physical files and active private-Xvfb route remain intact. Independent
replay checks 3,254 hashes; package readback confirms 21 DOS / 13 native
v1354 installed files unchanged. Both CIs pass. Final receipt overhead
is excluded. Recovery journals: native `.analysis/port64/full-window-v1356/`.

v1356 retires only two terminal owned Windows startup staging directories.
All 155 files are preserved in a complete recovery archive and every member
was read back before deletion. Net logical bytes reclaimed: 36,333,457
(archive retained; final receipt overhead excluded). Original inputs,
current/preceding programs and user saves are untouched. Native receipts:
`.analysis/port64/full-window-v1356/windows-gui-stop-cleanup-v1.json` and
`windows-startup-stage-recovery-v1.tar.gz`. No new build was needed for that Windows stage cleanup.

v1355 scoped cleanup keeps all 204 programs, producer/consumer source archives,
compiler/CMake metadata, traces, physical files, captures and failed attempts.
It retires 1190 regenerable build files / 70 completed contract-stage files after
two full recovery archives / 144 members read back, net 596836352 allocated bytes.
An independent replay verifies 2847 protected hashes and all 1260 absent files.
The three earlier desktop stages retire 20 files, net 35110912 bytes; the terminal
GUI stage and archived failed consumer materialization retire 494 files,
net 22450176 bytes. Immutable capture sharing keeps 324 complete BMP/PCM paths
and hashes, net 210509824 bytes. Counts subtract their journals/archives but
exclude final receipt size. No original input, accepted program or save deleted.
Post-CI pruning retires 1020 source-backed Python caches, net 16822272 allocated
bytes; root `.analysis/cleanup/host-route-post-ci-caches-v1355.json` records
source/hash readback. Both CIs pass, including root live Ghidra replay/mutations.

Restore from native `.analysis/port64/host-route-v1355/` recovery archives and
member journals; retain distinct 481-input producer and consumer vectors.

## Previous v1354 recovery


v1354 retains all 204 current programs, complete producer/consumer source
archives, compiler/CMake metadata, Linux window and fake-audio captures,
physical saves, controller failures, pinned inputs and preceding products.
Current intermediates and both terminal owned Windows stages are recoverable
through three archives under native `.analysis/port64/host-window-v1354/`.
All 299 members read back before deletion. The scoped pass retires 1,190
regenerable build files and 225 stage files, reporting 628,129,792 allocated
bytes net reclaimed; accounting excludes its final receipt. A separate
pre-build pass prunes 12 source-backed Python caches (278,528 allocated bytes).

Sources have two distinct identities: the frozen cold producer and the final
consumer with two corrected verifier scripts. All compiled inputs are raw-equal.
Cleanup protection is scoped to its interval; later authorized source edits
must keep the earlier producer/archive identity instead of restamping receipts.

Keep pinned assets/targets/tools, active caches/databases, complete current and
preceding source/program vectors, recorded inputs, physical saves and failures.
Prune only terminal owned stages and regenerable intermediates after recovery
and hash readback. Restore archives into fresh directories; use the persisted
`retention-before-v1.json` journal for original paths/member hashes. Never
blanket-delete `.analysis/`, run git clean over private state, or remove user saves.

Prior v1353 recovery and its failed attempts remain indexed by the prior
receipts and Git; their archives are preserved. Both final CIs pass. Additional terminal capture sharing retains all 324
BMP/PCM paths and complete byte hashes while reclaiming 210,509,824 allocated
bytes net after its journal. Source-backed post-CI cache pruning retires 957
files with 15,585,280 allocated bytes net after its journal. Receipt overhead
is excluded. Main build cleanup, capture sharing and cache accounting remain
separate. The first follow-up helper had a str/Path readback typo; corrected
full journal readbacks verify all captures/sources before acceptance.

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

Native musical commands/fade-stop v1338 retains418 source inputs/174 current
products, full original/native/Windows traces, separate producer/consumer
archives and failed/inconclusive probes under native
`.analysis/port64/pmd-commands-v1338/`. Full archive/trace readback verifies
2954 protected hashes; a closed terminal snapshot checks 2277.
Persisted pre-mutation journals reclaim 676,278,272 allocated bytes
(644.9 MiB), including owned NTFS staging, raw trace copies,
negative binaries, native.o/.a and Windows.obj/link archives. Current
executables, source/compiler/cache/link identities and independent references
remain; CMake rebuilds absent intermediates and replay requires fresh paths.

Post-CI cleanup retires 1,012 source-backed generated Python cache files,
reclaiming 16,986,112 additional allocated bytes; receipt:
root `.analysis/cleanup/pmd-commands-post-ci-caches-20261010.json`.

Native hardware rhythm v1339 retains 422 source inputs/177 products, complete
primary and long-command/byte-wrap supplemental original/native/Windows rows,
separate producer/consumer archives and failed/inconclusive observations under
native `.analysis/port64/pmd-rhythm-v1339/`. Full archive/trace readback verifies
3915 protected hashes. Persisted journals measure 850,616,320 allocated bytes
reclaimed (811.2 MiB). Retired raw copies, counterfactual executables,
two owned Windows stages and 557 CMake intermediates have verified compressed
successors or source recovery. The first Windows stage accounting multiplier
is corrected from persisted per-file records in `cleanup-windows-stage-accounting.json`;
its original receipt remains unchanged. Current products, source/compiler/cache/
link profiles and independent references remain. Use fresh replay paths;
CMake rebuilds missing intermediates.


After both final CIs pass, a source-backed cache journal retires 1015
generated Python caches, reclaims another 17,125,376 allocated bytes,
and verifies 1015 unchanged Python source hashes. Measured batch
total is 867,741,696 bytes (827.5 MiB). Receipt:
root `.analysis/cleanup/pmd-rhythm-post-ci-caches-20261010.json`.

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

Native resident timer ownership v1340 retains426inputs/180current products,
full independent original/GNU/UBSan/actualWindows traces, producer/consumer
source archives and rejected pre-start/timer-order/Windows dispatch captures
under native `.analysis/port64/pmd-clock-v1340/`. Full readback verifies
2426protected hashes. Persisted pre-mutation inventory measures
646,873,088net allocated bytes reclaimed (616.9MiB).
779completed raw/probe/native intermediate files andtwoownedWindows stages
retire after verified lossless successors or source recovery. All original
references/currentprograms/source/tool/cache-link profiles remain. Windows
stage archives andrestore commands arein `cleanup-before.json`; replay requires
freshpaths andCMake regeneratesmissing objects/static archives. The earlier
review's Python-cache cleanup is separate and notincluded inthis figure.

After both terminal CIs, the v1340 post-CI journal retires 1025
source-backed Python caches and verifies 1025 unchanged source
hashes, reclaiming another 17,358,848 allocated bytes.
Receipt: native `.analysis/port64/pmd-clock-v1340/post-ci-caches-receipt.json`.
Measured v1340 total is 664,231,936 bytes; the prior review cleanup is separate.


v1341 continuous-clock cleanup: 413,282,304 allocated bytes from terminal
raw/probe successors and regenerable native objects/libraries; 195,694,592
more from the fully archived terminal Windows-first stage. Total 608,976,896
bytes (580.8 MiB), disjoint journals under native
`.analysis/port64/pmd-time-v1341/cleanup-before.json` and
`windows-first/cleanup-before.json`. Retain 183 current programs/430 inputs,
source archives, original references and failures. Live original aggregate and
chip model are explicitly excluded. Full aggregate acceptance remains pending.

Post-CI v1341 cache cleanup separately retires 1,021 mapped Python caches
with unchanged backing source, reclaiming 17,092,608 allocated bytes. The live
original observer cache is excluded. Current 430-input/183-program hashes
are checked again after cleanup.

Final v1341 aggregate closure additionally archives/readbacks the terminal
full Windows stage and completed model/probes. `final-retention.json` sums
the disjoint journals: 1,018,875,904 allocated bytes (971.7 MiB), with all
430 maintained inputs, 183 current program hashes and original outputs checked
after cleanup. Every producer/consumer is terminal zero. Historical first
closed-batch receipts remain separate; no source or evidence is restamped.

Native PCM v1342 preserves445maintained inputs/186programs, original timed
register/PCM references, separate source archives and all rejected adapters
under native `.analysis/port64/pmd-pcm-v1342/`. Terminal readback validates
1243 protected hashes. Two disjoint pre-mutation journals reclaim
1,074,380,800allocated bytes (1024.6MiB): regenerable native objects/static
libraries, verified lossless failed outputs and full archived Windows stage,
plus841full-byte-equal compressed paths shared immutable. Current programs and
inputs remain; CMake rebuilds missing intermediates. `final-retention.json`
indexes journals and restore surfaces; future replay uses fresh directories.

Native resident frontend v1343 preserves 451 inputs/189 programs, independent
OP/COM references, final GNU/UBSan and actual Windows readback under native
`.analysis/port64/pmd-resident-v1343/`. Independent terminal readback verifies
2012 protected hashes and every member/size/mode of three lossless archives.
Disjoint persisted journals retire 5141 stage/control/intermediate files, share
648 full-byte-equal compressed paths and reclaim 1514315776 net allocated bytes
(1444.2 MiB), after archive/inventory overhead. Initial cleanup included its own
active log in the final guard and failed; that observation remains and separate
terminal readback passes. `final-retention.json` gives restore commands for
`windows/stage.tar.gz`, `windows-v2/stage.tar.gz` and
`retired-control-outputs.tar.gz`. Current programs/source/compiler/cache-link
identities, original inputs and references remain; CMake regenerates 597 objects
and libraries. Shared files are immutable; future writers use fresh paths.


## Primary FM operator controls, v1344

Native `.analysis/port64/pmd-fm3-v1344/` retains separate original/consumer
source archives, full compressed driver/native row references, counterproof
sources/commands and current451-input/189-product/compiler/cache/link profiles.
Root `.analysis/review/semantic-port-review-lwruzqw5/cleanup-current.json`
retires1,610 rebuildable CMake/Python intermediates after3,305 protected hashes
pass, reclaiming424,996,864 allocated bytes net of journal/script overhead.
Native `retention.json`/`retention-journal.json` then retire987 closed Windows/
frontend files after complete archive member/size/mode/hash readback; two
archives reclaim323,452,928 additional allocated bytes net. Combined measured
reclamation is748449792 bytes (713.8 MiB). Source/program identities
and all independent original references remain. CMake regenerates absent
objects/archives; subsequent replay uses fresh output directories.

Restore `windows/stage.tar.gz` under the original owned NTFS directory from
`windows/stage.json`, and `frontend-regression-captures.tar.gz` under native
`.analysis/port64/pmd-fm3-v1344/frontend-regression/`. Archive members are
relative to those roots; original receipts retain their original hashes and
paths. No game assets, ROM data or original executables enter Git.

## FM3 v1345 retention index

The native branch retires3,189 terminal files with15 verified archives and
1,391 protected hashes unchanged; net764,350,464 allocated bytes (728.94 MiB)
are reclaimed. Current sources/programs/compilers/cache/link inputs and
original references stay retained. Native `docs/port64/evidence/pmd-fm3.md` and
`.analysis/port64/fm3-recovery-v1345/retention.json`/`retention-journal.json`
record member hashes, archive roots and recovery. Restore relative paths before
old candidate/Windows/frontend replay. Root scripts/tests Python caches are
separately retired in `.analysis/review/semantic-port-review-lwruzqw5/cleanup-v1345.json`;
all tracked root file bytes were unchanged at that cleanup boundary.

Native OP startup v1346 archives the owned Windows stage, developmental frontend
outputs and four source variants with full member readback under native
`.analysis/port64/startup-v1346/recovery/`. The persisted inventory retires
2575 files, shares 886 immutable full-byte-identical captures, verifies
11 archives and 2121 protected hashes, and reclaims
1447223296 net allocated bytes. All 459 maintained inputs/195 current
programs, frozen decoder/original references, tools and compiler/cache/link
profiles remain. Native objects/static archives and source-backed Python caches
are regenerable. Recovery roots/member hashes/restore commands are in
`retention-before-final-v1.json`; future producers use fresh destinations.

## Recorded startup pixels (v1347)

Native `.analysis/port64/startup-pixels-v1347/` retains the original producer,
three-host consumer receipts, source archives and full5,879-frame streams.
`source-bridge-v1.json` separates461 verifier inputs from the unchanged
459-input/195-program v1346 producer; no executable receipt is restamped.

`retention-before-v1.json` and `retention-receipt-v1.json` verify710 protected
hashes and reclaim503,971,840net allocated bytes (about480.6MiB). Two native
captures compare every decompressed byte before sharing the unchanged reference
gzip; timestamp-distinct gzip representations are losslessly replaced. All
frame-content receipts remain unchanged. The .NET compressed stream remains
separate as `windows-frames-v1.bin.gz`, preserving its receipt's compressed hash.
The other27 owned Windows-stage files recover from
`windows-stage-recovery-v1.tar.gz`; four retired mutant executables recover from
`counterproofs-recovery-v1.tar.gz`, whose members were fully read back. Original
references/assets, current programs, sources and build profiles remain live.
Future replay uses fresh output/stage paths; retained hardlinks are immutable.

A separate periodic cache journal at
root `.analysis/review/startup-pixels-cache-cleanup-v1/` retires1,035
source-backed CPython caches, reclaiming17,690,624allocated bytes and checking
4,235 protected hashes, including all195 programs. This is measured cache
retirement, not an additional end-to-end storage estimate across later CI runs.

After both final CIs, root
`.analysis/review/startup-pixels-cache-cleanup-final-v1/` retires1,034
regenerated source-backed caches/17,657,856allocated bytes and verifies4,235
protected hashes, including all195 current programs. The earlier periodic
cache retirement and this regenerated-cache retirement are not added together
as a net end-to-end reduction.

## Shared PMD note rotation, v1348

Native `.analysis/port64/game-audio-v1348/` retains the closed three-host note
matrix/boundary corpus, old failure/cancelled terminal-predicate logs, current
463-input/195-program profiles and separately pinned note verifiers. The full
`original-dev-v2` song producer and `watch-linux-v2` remain live and excluded.
Do not modify their frozen public Python/PowerShell tools or accepted captures.

`retention-note-before-v1.json` and `retention-note-receipt-v1.json` verify4652
protected files, retire1320 terminal stage/mutant/native intermediate files and
share679 whole-byte-identical completed outputs. Three archives pass full
member/size/mode/hash readback. This cleanup scope reclaims1237872640 allocated
bytes net of archive/journal overhead (about1180.5MiB), while current programs,
sources, compilers/cache-link identities and original references remain.
This is a scoped cleanup measurement, not whole-turn disk usage while the
excluded original producer continues writing.

`note-windows-stage-recovery-v1.tar.gz` and
`frontend-windows-stage-recovery-v1.tar.gz` recover the two owned NTFS roots
recorded in their stage JSON files. Restore only into absent owned roots or
generate fresh plans/stages. `note-counterproof-programs-recovery-v1.tar.gz`
recovers the six private mutant programs; sources/commands/matrices remain.
The previous195v1346 programs separately recover from
`retired-v1346-products-v1.tar.gz`, whose complete members were checked before
the rebuild. CMake regenerates removed.o/.obj/.a from the current source
archive/profile. Shared captures are immutable; future writers use fresh paths.

Fresh `note-terminal-readback-v1.json` rechecks current product/source/compiler
identities, closed original/native/Windows note captures and all four recovery
archives (907 members including the old195programs) after cleanup. Both root
and native final CI pass; root Ghidra database replay/mutation smoke passes.
`root-cache-retention-before-v1.json`/`root-cache-retention-receipt-v1.json`
then retire507 regenerated source-backed root CI caches (8503296 allocated
bytes). This cache observation is separate from the native scoped net figure;
live native writers/toolchain caches remain excluded.

## Ordinary key-only routes and first-load songs, v1349

Native `route-exploration-v1349/retention-before-v5.json` and
`retention-receipt-v5.json` verify5358protected files before/after mutation,
retire993terminal/generated files and fully read back two recovery archives.
The scope reclaims410439680allocated bytes net of archive/journal overhead
(about391.4MiB). Current195products, six stable private v4/v5 programs,
source/compiler/cache-link identities, raw native captures/saves, old recovery
archives and original references remain. Entire live `original-dev-v2`,
`watch-linux-v2` and `watch-ubsan-v1` writers are excluded; this is not a
whole-turn disk-use estimate.

`game-audio-v1348/firstload-windows-stage-recovery-v1.tar.gz` restores the owned
69-case Windows stock-song stage. `route-exploration-v1349/windows-stage-recovery-v5.tar.gz`
restores both Windows normal/Extra plans, their real same-host earned/final
saves and all closed captures. Exact roots/members/modes/hashes are in the
before journal. Restore only into absent owned roots or generate fresh plans.
Private CMake objects/libraries/dependency files regenerate from canonical
`source-v1.tar.gz`, the applicable `private-source-v*.tar.gz` and retained
source/compiler/cache-link profiles. Deleted cached prototype executables
recover byte-identically from their retained stable v5 copies. The earlier
unaccepted v2 pilot's superseded scratch executable has no raw recovery claim.

Accepted native/public route and Windows receipts retain their original bytes;
the first-load aggregate does not restamp the still-live138original producer.
The two note verifiers and two new route replay files have independent pins
until existing Python/PowerShell manifest guards close. Subsequent authored
documentation/ledger changes are not mutations to the compiled/source inputs.

Fresh `terminal-readback-v5.json` validates current195products, prototype/
native/public capture identities, both Windows recovery archives and frozen
original tool inputs after cleanup. Both final CI runs pass, including root
live Ghidra replay/mutation smoke. `root-cache-retention-before-v5.json`/
`root-cache-retention-receipt-v5.json` then retire507 regenerated source-backed
root CI caches (8503296 allocated bytes), a separate cache observation.
