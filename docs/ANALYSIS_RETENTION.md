# Private build and analysis retention

Native `port/modern-64` is at 48e05da, including GRCG, font and Gaiji
address recovery. The separate startup/motion integration on
`review/startup-motion-join-v1403` is frozen at 514 files / c2f8d689.
Its verified snapshot predates those renderer changes. Attest a combined
producer when integrating the two histories. The v1401 startup implementation
already reached `port/modern-64` through fffcc83.

## v1407 DOS text Gaiji

Replay index: `.analysis/reconstruction/probes/dos-text-gaiji-v1407/`.
The 1,425-file input freeze fb50205b, three selected products/MAPs/compiler
receipts, 2,656 complete text comparisons, 4,800 graphics Gaiji regressions and
old compiled control stay live. `verify_closure.py` also checks the frozen
v1406 source archive and unchanged proof identities independently of the new
live source.

Restored only journaled parent source/object caches needed for verified reuse.
Retired those restored files and the current producer's disposable source/OMF
caches: 7,143 paths / 1,449 blobs. The path/hash/size/mode/nsmtime journal
preceded archiving and deletion; CRC, every blob, temporary metadata readback
and 68 protected files pass. Net reclamation is 29.51 MiB after archive
and journal. 546 source-backed Python caches reclaim another
8.49 MiB, for 38.00 MiB total. Earlier archives and selected programs stay intact.

```sh
python3 .analysis/reconstruction/probes/dos-text-gaiji-v1407/verify_closure.py
python3 .analysis/reconstruction/probes/dos-text-gaiji-v1407/verify_retention.py
```

Add `--restore --prefix <owned producer subtree>` to the retention reader
when a compiler input is needed. Restore narrowly with verified metadata;
keep old acceptance receipts bound to their original producers.

## v1406 DOS Gaiji

The replay index `.analysis/reconstruction/probes/dos-gaiji-v1406/` binds
final products, MAPs and compiler receipts, and retains original comparisons,
first-candidate ES diagnostics and the v1400 negative control. Published
OP/MAINE products are in `.analysis/build/th04-gaiji-v1406-final/`.
The 1,425-file input profile is cfaa77bf; all 4,800 final controls and complete
transcript frames pass `verify_closure.py`.

Retired only this batch's cold and final OP/MAINE source/OMF caches, plus the
explicitly stopped unnecessary MAIN cache: 5,565 paths / 1,383 blobs.
The journal was persisted before archiving and deletion; gzip CRC, each blob,
restored size/hash/mode/nsmtime and 629 protected files pass. Net reclamation is
22.67 MiB after archive and journal. 545 source-backed Python caches
reclaim another 8.48 MiB; total 31.14 MiB. Earlier producers stay intact.

```sh
python3 .analysis/reconstruction/probes/dos-gaiji-v1406/verify_closure.py
python3 .analysis/reconstruction/probes/dos-gaiji-v1406/verify_retention.py
# Restore only a needed producer subtree:
python3 .analysis/reconstruction/probes/dos-gaiji-v1406/verify_retention.py --restore --prefix .analysis/reconstruction/probes/product-20261011-180052-085f918e-op/source
```

## v1403 combined native producer

3131 owned paths / 1463 blobs, 16.93MiB archive,
468.70MiB net cleanup before post-CI caches. Frozen514-file producer, selected
current executables, complete original vector comparisons, failure controls,
receipts and prior producers stay live. Full current path metadata is journaled
before archive/deletion, then CRC/all hashes and metadata readbacks pass.

```sh
python3 .analysis/reconstruction/probes/native-startup-motion-join-v1403/verify_retention.py
python3 .analysis/reconstruction/probes/native-startup-motion-join-v1403/verify_retention.py --restore --prefix .analysis/worktrees/port-modern-64/.analysis/port64/native-startup-motion-join-v1403/build-gnu
python3 .analysis/reconstruction/probes/native-startup-motion-join-v1403/check_frozen_parent.py
```

Strict current reader binds514/c2f8d689. Frozen v1401 remains512/60cf4491;
its strict current-source failure is expected, and the new parent reader checks
its frozen closure/CRC/blob union independently. Do not restamp old proofs.
The first v1401 journal caveat is unchanged; v1403 full metadata is available.

Final current-tree CI passes root451/native345, tracking and diff checks.
Root's actual private target/database/Oracle mutations pass; native private DB
checks skip absent projects. Additional post-CI source-backed caches reclaim
16.52MiB. v1403 total net cleanup is
485.22MiB; disjoint v1401+v1403 retirement/caches total 1318.54MiB
(1.29GiB), excluding temporary review-worktree removal.

## v1401 native startup waits

Only the owned current CMake intermediates, nonselected executables, verified
Demo capture duplicates, bulky frontend PCM/BMP and redundant source archives
were retired. Frozen512-file producer, selected current executables, original
raw evidence, failures, receipts and physical saves remain live. All prior
archives/producers stay unchanged. CRC/EOF, every blob and every temporary
restored SHA/size/mode/nsmtime passed before deletion; protected proofs passed
before and after. 2874 paths / 1467 blobs;
archive 26.28MiB and net reclamation 817.00MiB before post-CI caches.

Cleanup recovery caveat: the first deletion stopped at a missing compiler
object. All archive blobs had passed CRC/SHA and temporary readback, but the
full original path/mtime journal had not been persisted before deletion.
Receipt-pinned Demo/program contents were recovered; regenerated files have
new filesystem attributes. The final journal is written before deletion and
supports full current-path metadata recovery. 511 auxiliary blobs retain
content SHA/size without original path/mtime metadata. They remain in the final
content union; compiler intermediates can be cold-regenerated. Failed scripts
and logs, cleanup-recovery.json and the complete blob union are retained.
Concurrent source commits/motion work were observed during this interval;
causation of the object disappearance is unproved. Avoid overlapping writers.

```sh
python3 .analysis/reconstruction/probes/native-startup-waits-v1401/verify_retention.py
python3 .analysis/reconstruction/probes/native-startup-waits-v1401/verify_retention.py --restore --prefix .analysis/worktrees/port-modern-64/.analysis/port64/native-startup-waits-v1401/build-gnu
python3 .analysis/reconstruction/probes/native-startup-waits-v1401/check_parent.py
```

Commands run from DOS root. Recovery pins current native512/60cf4491 independently
from frozen v1399 512/5474b8e3 and v1400 DOS a34c1357. Old strict readers reject
the changed native source; never edit or restamp them. Use a fresh namespace for
a new experiment. Restore only needed owned paths and verify their metadata.

Final isolated-checkout CI passes root451/native345, plus tracking and diff
checks. Borrowed pinned targets pass identity/format checks; private Ghidra
project replay skips because those isolated checkouts have no project. Source
and runtime proof identities remain separately pinned. Source-backed review CI
caches reclaim 16.32MiB separately, for 833.32MiB net this batch;
review worktrees are temporary and their tracked document state is preserved.

## v1400 shared DOS lifecycle

Four current cold root DOS products, three artifact-local original/linked
108-case instruction comparisons and fresh15984+4 Demo boundaries are terminal.
Only this batch's duplicate materialized input trees, compiler intermediates,
two standalone src copies and disposable candidate HDIs/font are retired.
Net **56.03 MiB** after **15.55 MiB** archive/journal;
7264 logical files / 1481 unique blobs / 2351 protected proofs.
Full CRC/EOF and every temporary restored SHA/size/mode/nsmtime pass before
delete; an independent reader passes afterward. Current1425-file input freeze,
products/MAPs, original raw streams, new/old compiled controls and all failed
drafts remain. After terminal root451/native345 CI, 1054 source-backed Python
caches reclaim **16.44 MiB** net separately; current batch totals
**72.47 MiB** net. Repeated CI is unnecessary without another source change.

```sh
python3 .analysis/reconstruction/probes/dos-vsync-lifecycle-v1400/verify_retention.py
# Restore only the needed current owned inputs:
python3 .analysis/reconstruction/probes/dos-vsync-lifecycle-v1400/verify_retention.py --restore --prefix .analysis/runtime/candidates/dos-demo-v1400-vsync-candidate
python3 .analysis/reconstruction/probes/dos-vsync-lifecycle-v1400/check-parent.py
```

Parentv1399 stays512/5474b8 and DOS6f; current root DOS fingerprint is a34c1357.
Old strict readers reject changed live DOS source as expected. The new parent
reader verifies all frozen closure/source/CRC/blob identities separately, not
by restamping old proofs. Native x64 source is unchanged. Prior484.68MiB
(v1399) and544.95MiB(v1398) remain separate; do not count them again.


## v1399 corrected START cadence ownership

Current native producer512/5474b8 corrects accumulator retention; DOS source6f
remains unchanged. Original12-case Unicorn, newcold GNU/UBSan, rejected old
v1398 caller,208-IRQ/230-raster probes and all8 default129-file regressions are
terminal. Shared DOS assembly phase/query-order repair remains the next unit.
No old acceptance is upgraded by this cleanup.

Current owned CMake intermediates/unused binaries and duplicate complete CLI
captures retire losslessly: 3104 logical paths / 1447 blobs, **468.27 MiB net**
after a **16.88 MiB** archive/journal. Complete gzip CRC/EOF, every actual
temporary restored SHA/size/mode/nsmtime and 688 protected proofs pass before /
after deletion. No new original HDI exists in this diagnostic batch. Complete
original/source/negative traces, frozen old/new headers and selected programs
stay live. Parent v1398 source512/efea/archive/757 sealed proofs recheck without
restamping; older510/ea5c remains independently routed.

```sh
python3 .analysis/reconstruction/probes/native-vsync-lifecycle-v1399/verify_retention.py
python3 .analysis/reconstruction/probes/native-vsync-lifecycle-v1399/verify_retention.py --parent v1398
```

Add --restore and a narrow --prefix for required owned paths, using fresh
execution namespaces. Earlier strict readers reject changed current5474b8;
use the new reader. Full CI root451/native345 plus a separate 1053-file
post-CI cache journal recover another 16.41 MiB; current net **484.68 MiB**.
This does not include old v1398's544.95 MiB again. Target/host saves/sharedtools /
TH08 and frozen old proofs remain untouched. Current control/compiler/native
checks use oneCPU1/nice19 because CPU0 is occupied; originaltiming captures
keep their CPU0 identity.

## v1398 IRQ raster and native VSYNC primitive

Current native source is frozen at 512 files / `efea1700`; DOS fingerprint
`6f5898dd` is unchanged. Both original IRQ captures, independent full readers,
cold GNU / optimized UBSan builds, complete component comparisons, compiled
negative controls and all eight default startup/Demo regressions are terminal.
Frontend wait integration remains open; archive validation promotes no timing
or exactness claim.

Lossless retirement of **3,110 logical files / 1,451 unique blobs** reclaims
**528.63 MiB after archive and journal**, keeping a **39.20 MiB** recovery archive.
Complete gzip CRC/EOF, every content digest and temporary actual restored
SHA/size/mode/nsmtime pass before deletion. A separate full reader verifies all
694 protected proofs and current frozen source afterward. Complete original
raw/GDC streams, source freezes, selected current GNU/UBSan game/trace/shake /
VSYNC programs, compiled mutants and failed attempts stay live. Only current
owned disposable HDIs/fonts, CMake intermediates / unused programs and duplicate
complete native captures are retired. Previous producers/proofs remain unchanged.

The v1398 reader checks current 512/efea and previous frozen 510/ea5c producers
separately. Old strict v1396/v1397 recovery readers reject the changed current
manifest; use this new reader rather than editing old attestations:

```sh
python3 .analysis/reconstruction/probes/native-irq-clock-v1398/verify_retention.py
python3 .analysis/reconstruction/probes/native-irq-clock-v1398/verify_retention.py --restore --prefix .analysis/runtime/candidates/dos-op-v1398-irq-
python3 .analysis/reconstruction/probes/native-irq-clock-v1398/verify_retention.py --parent v1397
python3 .analysis/reconstruction/probes/native-irq-clock-v1398/verify_retention.py --parent v1396
```

Add --restore and a narrow --prefix for the required parent subtree. The old
v1396 primary archive and its separate complete state/item text archive are both
required; the new reader verifies their linked journals and all protected old
hashes. Its first single-archive attempt remains failed, with frozen source/logs;
it does not imply parent corruption. Both current archive and retention.json
are needed for owned-path recovery. Use fresh namespaces for new execution.


Both full CI gates pass (root 451 / native 345 tests), with tracking and diff
checks. Post-CI source-backed Python cache cleanup retires 1051 files,
recovering a separate 16.32 MiB after its journal. Total current net cleanup:
544.95 MiB. The cache journal is disjoint from lossless archive retirement;
retained source regenerates these caches. Goal remains active.

## v1393 original OP loading work

The original 24,000/36,000 CPU pair, complete strict readers, guest DOS return
checks and GNU/UBSan measured-age/zero-age service probes are terminal.
Native product source is unchanged at 510-file producer `9cfe100a`; its frozen
source and closed build/program proofs remain owned by v1392. No fresh native
cold build or Demo/window acceptance is claimed here.

Retirement reclaims **103.23 MiB after archive/journal**, retaining a **60.40 MiB**
archive with 22 complete files, including eight disposable HDIs. Full gzip
CRC/EOF, member SHA/size/mode/nsmtime, all 33,284 inherited/current protected
hashes and 510 unchanged producer pins pass before and after deletion. Unique
complete clock streams/raw loads, source, receipts and the first interrupted
capture remain live. Its incomplete inner gzip remains failed; verified outer
archiving cannot upgrade it. A further compression experiment saved only
0.42 MiB; the generated duplicate was dropped and the simple source archive
kept unchanged. Its recipe and bit-exact readback receipt remain available.
Both full CI gates pass (441 / 345 tests), followed by 16.66 MiB of source-backed
post-CI cache cleanup under a separate journal.

From DOS root:

```sh
python3 .analysis/reconstruction/probes/native-op-loading-v1393/verify_retention.py
```

Add `--restore` before full reader/probe replay to restore exact retired paths.
Use fresh output namespaces; never overwrite earlier closed producers. The
original reader also requires actual menu completion and rejects the real
zero-exit incomplete attempt. Both archive and journal are required for recovery.


## v1392 cold PMD application installation

Closed original OP startup/timer, GNU/optimized UBSan build, eight actual
native profile, constructor controls, service probe, raw RGB and private Xvfb
receipts precede retirement. CPU0/nice19 serial work reclaims **620.75 MiB**
after the **66.02 MiB archive and journal**. All 3,253 complete archive members
pass full gzip CRC/EOF and SHA/size/mode/nsmtime checks before and after deletion;
33,158 inherited/current protected hashes and all 510 frozen source pins pass.
Current producer starts `9cfe100a`; DOS fingerprint remains `6f5898dd`.
Both complete CI gates pass (441 / 345 tests), followed by another 16.64 MiB
source-backed cache cleanup. That journal is separate from archive recovery.

Current GNU/UBSan game, trace and shake executables, frozen source, closed
receipts/logs, read-only original runtime load observations and compressed
original clock streams remain live. Objects/static libraries, unused contract
programs, borrowed old libraries, expanded events, duplicate native captures,
new full RGB references and four disposable original HDIs/copied fonts are
losslessly archived. Old producers and proofs are unchanged.

From DOS root, check the archive and protected state with:

```sh
python3 .analysis/reconstruction/probes/native-pmd-startup-v1392/verify_retention.py
```

Add `--restore` before complete replay, CTest or the public original reader's
HDI checks. Use fresh output directories for new runs; never rerun a closed
producer or retirement controller into its old path. Both archive and journal
are required for exact owned-file recovery. This retirement does not accept
original default CPU/loading clocks, physical audio/scanout or full processes.


## v1388 original boot clock

All jobs are terminal. Current509/f2b03ebb has fresh GNU71/69CTest and optimized
UBSan3 cold-build receipts; actual four-Demo127 files and privateXvfb deadline/
input checks pass. Main441/liveGhidra andnative345/target CI pass. Original
boot/GDC event ownership, common-clock positive/zero-only negative and cadence
controls stay separately pinned. Default native process CPU-I/O timing remains open.

Lossless retirement archives 3,213 complete files and deletes
1,051 source-backed caches. Full temporary restored SHA/size/mode/nsmtime
and complete gzip CRC/footer/EOF pass before and after deletion. All
29,115 earlier/current protected hashes,509 source pins and the
unchanged DOS fingerprint pass. Net allocated recovery is
855,470,080 B (815.8 MiB) after the 102.1 MiB archive,
before the 7.2 MiB journal allocation. Both archive and
journal are required for exact file recovery. V1 partial clock gzip remains
incomplete; the outer archive recovery never upgrades its inner stream to a pass.

Current game/trace/shake executables, independent timing/counter/clock programs,
frozen sources, logs, receipts and original reference streams remain live.
The archive holds CMake intermediates/static libraries, unused CTest helper
executables, duplicate captures/references, expanded event/phase data and both
attempts' disposable HDIs/copied assets. Original compressed streams stay live;
all unique V1 failure bytes and distinct V2/V3 complete proof identities remain
retained. V3 same-capture compressed40 fullvideo samples stay live.
Earlier a47f0496 and font/raster proofs keep their original scopes; the old
protected inventory is checked without relabeling it as currentf2b03ebb.

From DOS root, use
`python3 .analysis/reconstruction/probes/native-epoch-v1388/verify_retention.py`
for complete temporary recovery or add `--restore` to restore exact owned paths.
Restore before CTest or readers needing expanded inputs. Run one-shot probe
recipes in fresh output namespaces; never overwrite terminal evidence or rerun
the retirement controller. The V1 host guard failure and distinct complete V2/V3 boot/video observer source/logs
remain retained. Current event-clock fixture is separate from default process timing.


## v1387 calibrated native cadence

All jobs are terminal. Current509/03351541 has fresh GNU71/69CTest and optimized
UBSan3 cold-build receipts; actual four-Demo127 files and privateXvfb deadline/
input checks pass. Main441/liveGhidra andnative345/target CI pass. Original
GDC/time ownership and independent old-rate rejection stay separately pinned.

Lossless retirement archives 2,577 complete files and deletes
1,044 source-backed caches. Full temporary restored SHA/size/mode/nsmtime
and complete gzip CRC/footer/EOF pass before and after deletion. All
28,262 earlier/current protected hashes,509 source pins and the
unchanged DOS fingerprint pass. Net allocated recovery is
364,519,424 B (347.6 MiB) after the 28.4 MiB archive,
before the 6.8 MiB journal allocation. Both archive and
journal are required for exact file recovery.

Current game/trace/shake executables, independent timing/counter/clock programs,
frozen sources, logs, receipts and original reference streams remain live.
The archive holds CMake intermediates/static libraries, unused CTest helper
executables, complete duplicate capture files and freshly emitted references.
Earlier a47f0496 and font/raster proofs keep their original scopes; the old
protected inventory is checked without relabeling it as current03351541.

From DOS root, use
`python3 .analysis/reconstruction/probes/native-cadence-v1387/verify_retention.py`
for complete temporary recovery or add `--restore` to restore exact owned paths.
Restore before CTest or readers needing expanded inputs. Run one-shot probe
recipes in fresh output namespaces; never overwrite terminal evidence or rerun
the retirement controller. The initial archive-reader guard failure and separate
corrected v2 source/logs remain retained.


## v1377 aligned presentation consumer

All jobs are terminal. Main441/live Ghidra and native345/target CI pass; native
private tool/Ghidra gates explicitly skip where unavailable. Immutable502-file
v1376 compiled programs remain separate from frozen505-file consumer8b0f702a.
Complete original/reconstructed VP3 streams, frozen replay, full graphics
diagnostics, failed attempts and prior programs remain pinned.

Lossless retirement reclaims153010176 allocated B (145.9 MiB) before journals:
128 complete files (eight duplicate capture HDIs plus120 selected raw snapshots)
and1044 public source-backed caches. Full restored SHA/size/mode/nsmtime and
complete gzip CRC/footer/EOF pass, as do9692 protected hashes,505 current source
pins and the unchanged DOS input fingerprint. The prior v1376 archive is intact.

From the DOS root, use
`python3 .analysis/reconstruction/probes/native-presentation-v1377/verify_retention.py`
for full temporary restored readback, or add `--restore` to recover exact paths.
Restore before re-reading the new capture HDIs or old selected snapshot paths.
The new native reader reads its v1376 native captures directly from their archive.
Do not rerun one-shot retirement controllers or reuse terminal output directories.

## v1376 actual FrontEnd display and text evidence

All jobs are terminal. Four new GNU/optimized UBSan programs,502-source
producer/reader snapshots, original references, pre-repair missing-label
captures and corrected target witnesses remain pinned. DOS/Windows products
and all71 previous native programs are unchanged.

Retention fully restores671 raw display/state files, compiler intermediates
and the exploratory v2 ELF from one archive, with exact SHA/size/mode/nsmtime.
Complete gzip CRC/footer/EOF also passes.1043 public source-backed caches are
retired. This reclaims291966976 allocated B (about278.4 MiB) before journals.
All8904 older protected hashes,502 current source pins,4 new/71 prior programs
and the unchanged DOS source fingerprint pass. No pixel/text byte is masked.

Recovery lives in native `.analysis/port64/native-pictures-v1376/`.
Run `python3 .analysis/port64/native-pictures-v1376/verify_retention.py` from the
native worktree for complete temporary restores and protected readback.
`--restore` reinstates exact owned paths, refusing different existing bytes.
Restore before reusing `frozen_readback.py`, `verify_initial_label.py` or old
object inputs. Public `verify_demo_pictures.py` executes retained programs into
fresh outputs without restoring old captures. Do not rerun the one-shot cleanup
controller or reuse terminal output directories. Whole pictures remain
qualified diagnostics; scalar/label acceptance has its own receipts.


## v1375 complete native actor/effect pool evidence

All jobs are terminal. Current GNU70/focused cold UBSan1 products, build objects,
500-source producer/reader snapshots and original references remain available.
The failed8-pool initial producer and missing-Midboss source/program control are
retained independently. Old DOS/Windows/natural-route products are unchanged.

Lossless retention reclaims2038489088 allocated file B (about1.90 GiB) before
journals: five complete native pool streams, ten complete raw text streams and
1042 source-backed public Python caches. Complete restored file readback and
all15984 pool frame headers/EOF pass for each stream. All8904 prior protected
hashes,500 current source pins,71 current programs and the unchanged DOS product
fingerprint pass. Current build objects and all failures/commands remain.

Journals/recovery are in native `.analysis/port64/native-pools-v1375/`.
Run `python3 .analysis/port64/native-pools-v1375/verify_retention.py` from the native
worktree to restore/read every stream into disposable files and check protected
producers. `--restore` recreates the ten old text paths with exact modes/nsmtimes;
different existing bytes are refused. Pool archives retain their complete raw
SHA/size and can be restored into fresh paths. Public replay creates fresh files;
do not reuse terminal output directories or rerun old cleanup controllers.

## v1374 complete native Demo state evidence

All jobs are terminal. Current GNU 70/focused UBSan 3 products and cold build
objects stay available, along with both final 498-file producer/reader snapshots,
complete original references, wrong-distance source/binary and failed scratch
adapters. Existing DOS and Windows products remain unchanged.

Lossless retention reclaims 166055936 allocated file B (about 158.4 MiB) before
journals: 26 complete raw/text/old-probe streams and 1041 source-backed caches.
Every archived stream restores with exact bytes, file modes and nsmtimes.
Independent readback validates 8904 protected hashes, all 26 complete restores,
current 498 source pins and the unchanged DOS input fingerprint. No state or
pixel data is normalized to obtain archive equality. Sources/logs remain.

Journals/recovery live in native `.analysis/port64/native-demo-v1374/`.
Run from this root worktree:

```sh
nice -n 15 taskset -c 0 env PYTHONDONTWRITEBYTECODE=1 \
  python3 .analysis/worktrees/port-modern-64/.analysis/port64/native-demo-v1374/restore_streams.py
```

Add `--restore` before reading retired original/native raw text or earlier probe
binaries. Different existing outputs are refused. Fresh public paired replays
create their own input/output files; use a fresh output directory. Do not rerun
old mutation/cleanup controllers against their terminal directories.

## v1373 native point-number evidence

All build/game/reader/CI/retention handles are terminal. Native v1373 keeps the
new GNU 69 products, focused UBSan contracts/frontend, all sources, full original
CPU state/pixel references, failed source variants and their build commands.
Old DOS v1372 and native v1356/Windows product identities remain unchanged.

Lossless retention reclaims 502460416 allocated file B (about 479.2 MiB) before
journals. 23 complete native raw-pixel/text/mutant streams restore byte-exactly
with file modes and nsmtimes. Raw native screens reuse independently equal
original gzip streams; text and retired mutant programs have exact gzip copies.
No row, glyph, pool byte or pixel is normalized to obtain archive equality.
Independent readback validates 3093 protected hashes and 496 current source pins.
Both complete 830/494 original component reports and full 400-slot controls stay
available. The first 766-case executed sources keep their own identity.

CI explicitly generates source caches despite PYTHONDONTWRITEBYTECODE. The
initial cleanup's absence assertion rejects after all 23 archives succeed; its
source/log and partial journal remain. A separate v2 tail verifies the old
journal, retires 1040 source-backed caches and completes all recovery/hash gates.
Do not rerun the first deletion controller against already retired inputs.

Journals and recovery are in native
`.analysis/port64/pointnum-v1373/`. Verify recovery from the root worktree:

```sh
nice -n 15 taskset -c 0 env PYTHONDONTWRITEBYTECODE=1 \
  python3 .analysis/worktrees/port-modern-64/.analysis/port64/pointnum-v1373/restore_streams.py
```

Add `--restore` before replaying unchanged old commands that name retired
fixtures/raw text or native-pixel files. Restoration refuses different existing
files. The public original/native verifier generates fresh inputs/reports;
use a fresh output directory. Mutable orchestration stdout stays outside the
protected probe trees.


v1372 retains the new complete scalar/DGROUP captures and accepted four-demo
video reports under `dos-demo-v1372-animation-candidate*`. The only source repair
changes 17 animation DATA bytes. Successful cold MAIN objects and original/
prior-candidate bounded watchpoint snapshots remain; all import/reader/MAP
assertion negatives keep their original sources and logs.

78 terminal immutable paths share identical bytes/modes, reclaiming 139792384 B;
128 protected file hashes verify this pass. Four complete new video gzip files
are retained as `demo-writer-v1372/video-delta/demo-N-xor.bin.gz` against the
unchanged full original v1369 baselines. Every candidate gzip byte, encoded
record header, raw GDC clock and invisible tail restores exactly before retiring
163233792 B. A one-bit archive mutation rejects before decode. Verify or restore:

```sh
nice -n 15 taskset -c 0 env PYTHONDONTWRITEBYTECODE=1 python3 \
  .analysis/reconstruction/probes/demo-writer-v1372/restore_video_stream.py
# Add this option to recover all files before the unchanged complete reader:
# --output-directory .analysis/runtime/candidates/dos-demo-v1372-animation-candidate-video
```

Existing files are never overwritten. Keep all four original baselines, deltas,
`video-stream-retention.json` and the recovery source; use a disposable copy of
execution images for any later game run. Final CI passes 441 tests. Afterwards
535 source-backed caches retire 8892416 B. The final independent reader checks
270 protected hashes, 26 frozen inputs, all four full gzip recoveries, original/
new comparison results and the current product fingerprint. Total reclamation
is 311918592 allocated file B (about 297.5 MiB) before journals. Cleanup stdout
and mutable phase files stay outside the protected probe tree. All jobs are
terminal; native06922ce and Windows packages remain unchanged.

v1371 retains complete ordinary/DGROUP captures and controls under
`.analysis/runtime/candidates/dos-demo-v1371-pointnum-candidate*`. Full video
comparison is `dos-demo-v1371-pointnum-video-comparison-v2.json`; the initial
missing-consumer report/source/log stay retained separately.57 terminal immutable
paths share identical bytes/modes, reclaiming73,854,976 allocated B.

The four new video gzip files are retained losslessly against the complete
original v1369 baselines as `demo-render-v1371/video-delta/demo-N-xor.bin.gz`.
Full byte/SHA/size recovery validates every encoded record, raw GDC clock and
invisible tail before retiring162,910,208 B. Keep all four baselines/deltas,
`video-stream-retention.json` and the restoration script. Verify without writing:

```sh
nice -n 15 taskset -c 0 env PYTHONDONTWRITEBYTECODE=1 python3 \
  .analysis/reconstruction/probes/demo-render-v1371/restore_video_stream.py
```

Add `--output-directory
.analysis/runtime/candidates/dos-demo-v1371-pointnum-candidate-video` to restore
all four exact original files before unchanged-reader replay. Existing files
are never overwritten; completed execution images remain immutable.

The failed historical122-owner replay remains failed before byte comparison.
Its A `source/` is retained in `demo-render-v1371/failed-focused-source.tar.gz`:
2784 PAX entries,16,350,880 file-payload B, complete bytes/modes/ns mtimes checked.
Reclamation18,526,208 B; restore with `tar -xzf ARCHIVE -C FRESH-directory` before
source/object inspection. Original root:
`.analysis/reconstruction/exact-unit-replay/gpt61-v1371-pointnum-symbol-focused/a/`.
Its generated raw `source.tar` is separately retained byte-for-byte as
`failed-scaffold-input.tar.gz`, reclaiming8,040,448 B; recover with `gzip -dc
ARCHIVE > FRESH-source.tar`, verifying the digest/size in
`failed-scaffold-input-retention.json`. That journal also retains original mode
and ns mtime. Frozen maintained `repo-inputs/`, all failure logs and the successful
cold MAIN cache remain live. Native06922ce source-only inspection freezes four
complete files separately; it grants no runtime acceptance and changes no native file.

After final434-test CI,533 source-backed Python caches retire8,876,032 B.
Total v1371 reclamation is272,207,872 allocated file B/about259.6MiB before journals.
Independent readback verifies199 protected hashes,20 frozen inputs, all four
full gzip restores,2784 PAX entries/raw tar recovery, four native source files
and cache absence. Every game/build/reader/CI/cleanup job is terminal. Restore
only to fresh paths for inspection; preserve the initial failed consumer report,
receipt-pinned late GDB freeze and corrected full v2 reader as separate evidence.

v1370 keeps the fresh ordinary and full DGROUP captures under
`.analysis/runtime/candidates/dos-demo-v1370-invalidate-candidate*` with their
independent controls and complete comparisons.178 terminal immutable-copy
paths reclaim74,018,816 allocated B, with159 protected hashes unchanged.

The four new video gzip files are retained losslessly as sparse XOR archives
under `.analysis/reconstruction/probes/demo-render-v1370/video-delta/`, against
the four complete original v1369 video streams. Every candidate gzip byte,
including all raw GDC clocks, invisible tails and header fields, restores to
its original full SHA-256 and size before the large copies retire. The journal
is `video-stream-retention.json` in the v1370 probe and capture directories.
Reclamation is162,811,904 B; this is storage encoding, not semantic normalization.
Keep the baseline streams, all four delta archives and the restoration script.

Verify all four original gzip digests without materializing large files:

```sh
nice -n 15 taskset -c 0 env PYTHONDONTWRITEBYTECODE=1 python3 \
  .analysis/reconstruction/probes/demo-render-v1370/restore_video_stream.py
```

Before using the unchanged complete video reader, add
`--output-directory .analysis/runtime/candidates/dos-demo-v1370-invalidate-candidate-video`
to restore all four exact original files. The tool uses exclusive creation and
restores modes/timestamps; existing files are never overwritten. Restore only
for inspection/replay, never reuse completed execution images. A one-bit delta
mutation is rejected before decode; its exact recipe/digest is retained, and
its temporary copy is retired.

The first cold source cache whose publication failed the input-change guard is
fully retained in `demo-render-v1370/rejected-cold-source.tar.gz`:1769 PAX entries,
3,356,051 file-payload B, verified complete bytes/modes/nanosecond timestamps.
Its original source copy retires6,684,672 allocated B; logs/receipt remain.
Restore `source/` with `tar -xzf ARCHIVE -C FRESH-directory` before inspecting its
old object/map/product paths. The successfully published cold MAIN cache stays
live. Source/producer archives and all earlier failed/accepted evidence remain.

After final428-test CI,533 source-backed caches retire8,871,936 allocated B.
Total v1370 copy/archive/cache reclamation is252,387,328 allocated file B
(about240.7MiB) before journals. `final-independent-readback.json` verifies367
protected hashes,17 frozen source inputs, all4 complete gzip restores and the
1769-entry rejected-source archive, plus source-backed cache absence.
The first reader catches the cleanup writer completing its own initially empty
stdout log; the old source/log stay retained. Reader v2 checks only that explicit
log's terminal JSON against its receipt and exact before/after hashes, with all
other source/data checks unchanged. All jobs are terminal; accepted states,
native worktree and Windows packages stay unchanged.

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

## v1378 terminal validation and recovery

All v1378 jobs are terminal. Main441/liveGhidra and native345/target CI pass;
unavailable private native gates skip. Initial unregistered Oracle label and
cleanup log-lifetime failures stay retained: archive restoration passed before
retirement; final gate rejected its own writing log, then a distinctv2 journal
pinned that log after terminal. No archive/program/source bytes were repaired.
Lossless retirement reclaims324722688 allocated B (309.7MiB) before journal
cost:1390 full raw/sample/build-intermediate files and1044 source-backed caches.
Full restored SHA/size/mode/nsmtime/gzip EOF,15620 protected hashes,509 source
pins and unchanged DOS fingerprint pass. All71GNU/3UBSan/newmutant programs,
complete frozen sources, original references and failure receipts stay live.
Recovery from DOS root: python3 .analysis/reconstruction/probes/native-pages-v1378/verify_retention.py --restore before old raw-capture/graphics/frozen-reader paths.
Use no options for full temporary readback. v1377 restore proof retained its
then-current505 scope; its live-source check must not be restamped to509.

## v1379 terminal validation and recovery

All v1379 jobs are terminal. Main441/live Ghidra and native345/target CI pass;
private unavailable native gates skip. Frozen full-reader replay reproduces
both complete shake receipts, apart from its separately pinned source hash.
Lossless retirement reclaims153083904 allocated B (146.0MiB) before journalcost:
342 complete sample/capture/build files and1044 source-backed caches. All16713
protected hashes,509 source pins, full restoration/SHA/size/mode/nsmtime/gzip
EOF and unchanged DOS fingerprint pass before and after deletion. The active
cleanup producer log is explicitly excluded until terminal; old proofs remain
immutable. Two new FrontEnd programs and all older programs/sources stay live.
From DOS root, use python3 .analysis/reconstruction/probes/native-ring-v1379/verify_retention.py --restore before reading retired captures, fulltile pixels or relink objects;
without --restore it performs temporary complete readback. Old v1378 proof
retains its then-current509/9346e951 scope and cannot attest live8e77830c source.

## v1380 terminal validation and recovery

All v1380 jobs are terminal. Main 441/live Ghidra and native 345/target CI pass;
unavailable private native gates skip. Full parent/current sample hashes show
36 complete index/RGB samples unchanged. All 11,384 pixel changes in the other
four complete index pictures equal the actual original CPU beam and original
pixels on both variants. This further bounds the repair; whole pictures stay open.

Lossless retirement reclaims 156,069,888 allocated bytes (148.8 MiB) before
journal cost: 354 complete sample/capture/build files and 1,044 source-backed
caches. Full restoration/SHA/size/mode/nsmtime/gzip EOF, 17,815 protected
hashes, 509 source pins and unchanged DOS fingerprint pass before and after
deletion. The cleanup log is excluded while writing. Two new FrontEnd programs,
all old programs, frozen sources, original references and failures stay live.
From DOS root, restore retired inputs before CPU/graphics/reader/relink replay:

```sh
python3 .analysis/reconstruction/probes/native-shot-render-v1380/verify_retention.py --restore
```

Without --restore, it performs temporary complete readback. Old v1379 proof
retains its then-current 8e77830c scope and cannot attest live f5791751 sources.

## v1381 terminal validation and recovery

All v1381 jobs are terminal. Main 441/live Ghidra and native 345/target CI pass;
unavailable private native gates skip. Full parent/current sample hashes show
38 complete index/RGB samples unchanged. All 40 pixel changes in the other
two complete index pictures equal the actual original CPU pellet passes and original
pixels on both variants. This further bounds the repair; whole pictures stay open.

Lossless retirement reclaims 156,139,520 allocated bytes (148.9 MiB) before
journal cost: 354 complete sample/capture/build files and 1,044 source-backed
caches. Full restoration/SHA/size/mode/nsmtime/gzip EOF, 18,924 protected
hashes, 509 source pins and unchanged DOS fingerprint pass before and after
deletion. The cleanup log is excluded while writing. Two new FrontEnd programs,
all old programs, frozen sources, original references and failures stay live.
From DOS root, restore retired inputs before CPU/graphics/reader/relink replay:

```sh
python3 .analysis/reconstruction/probes/native-circle-v1381/verify_retention.py --restore
```

Without --restore, it performs temporary complete readback. Old v1380 proof
retains its then-current f5791751 scope and cannot attest live fb26d509 sources.

## v1382 terminal validation and recovery

All jobs are terminal. Main441/live Ghidra and native345/target CI pass;
unavailable private native gates skip. GNU cold71 programs/69CTest and UBSan
cold3 targets remain pinned; full81-byte splash/nine-pool/scalar/shake/text,
five malformed-trace rejection and frozen-reader controls pass. No Windows,
physical scanout, full pictures or historical exact promotion is accepted.

Lossless retirement reclaims 193,658,880 allocated bytes (184.7 MiB) before
journal cost: 975 complete sample/capture/build files and 1,044 source-backed
caches. Complete restoration/SHA/size/mode/nsmtime/gzip EOF, 22,622 protected
hashes, 509 source pins and unchanged DOS fingerprint pass before and after
deletion. Two complete native-pool streams already reclaimed 774,946,816
allocated bytes after full gzip restore/SHA/length/EOF verification. Combined
net allocated recovery is 968,605,696 bytes (923.7 MiB) before journal
cost. All71 GNU/3 UBSan programs, both component probes, old programs, frozen
sources, original references, full pool archives and failed attempts stay live.
The cleanup log is excluded while writing; previous proofs remain immutable.

From DOS root, restore retired samples/build inputs before CPU/graphics/reader
replay with python3 .analysis/reconstruction/probes/native-white-v1382/verify_retention.py --restore.
Without --restore it performs temporary complete readback. Old v1381 proof
retains its fb26d509 source scope and cannot attest current add39f3c inputs.
Native full pool gzip archives are already complete and require no new capture.

## v1383 terminal validation and recovery

All jobs are terminal. Main 441/live Ghidra and native 345/target CI pass;
unavailable private native gates skip. Final ordinary GNU/optimized UBSan and
separate extra GNU lighting controls, fixed-page full changed-pixel checks,
48 actual tail-copy controls and frozen reader replay pass. Only view.cpp
changes; v1382 whole-cold/69CTest/full-nine-pool producers stay separate.

Lossless retirement reclaims 455,786,496 allocated
bytes (434.7 MiB) before journal cost:
1,073 complete sample/capture/build/restored-image files and
1,044 source-backed caches. Full temporary restoration,
SHA/size/mode/nsmtime/gzip EOF, 24,916 protected hashes,
509 source pins and unchanged DOS fingerprint pass before and after deletion.
All seven new ordinary/diagnostic programs, old programs, frozen sources,
failures, complete original references and full pools remain retained. The
snapshot-only intermediate and reader failures are not restamped or promoted.

From DOS root, restore archived sample/build/image inputs before replay:

```sh
python3 .analysis/reconstruction/probes/native-initial-v1383-v2/verify_retention.py --restore
```

Without --restore it performs complete temporary readback. Old v1382 proof
keeps its add39f3c source scope and cannot attest current 50ca49c6 inputs.
Whole native pictures/cache/margins/RGB/scanout/broader gameplay remain open.

## Full RGB composition probe retirement (v1384)

All jobs are terminal. The native MPN-palette producer retains 509 inputs,
manifest ba6eff48; both programs, independent pinned emitter and failed owner
probe remain live. No DOS product input changes. Main441/native345 CI pass.
583 complete raw/reference/native capture and build-intermediate files and
1,044 source-backed caches retire only after complete SHA/size/mode/nsmtime,
gzip EOF and temporary-restoration checks. 25,495 protected hashes include
old proofs and the previously unlisted closed v1383 terminal-appender failure
and v3 script. Before/after deletion checks pass. Net allocated reclamation is
289,800,192 bytes (276.4 MiB) after archive cost, before journal cost.
The complete archive is approximately11 MiB.

From DOS root, restore before diagnostic reader replay:

```sh
python3 .analysis/reconstruction/probes/native-composite-v1384/verify_retention.py --restore
```

Without --restore it temporarily verifies every recovery. Journal SHA-256:
45d856ca61d328bbe4c88b94be6e5abdc35913e83a0e58dfc05d0d68771304d6.
The older50ca49c6 proof cannot attest current ba6eff48 inputs. This journal
preserves those frozen sources without restamping them. Current protected
inventory excludes its writing retirement log; this terminal appender was
created afterward and is separately retained. See focused demo evidence for
full rawRGB, explicit DAC diagnostics and open blink/CG/scanout boundaries.

The separately retained replay_compositor.py verifies all 120 entire RGB hashes
using only 41 temporary recovered inputs, then removes them. Its analog-nibble
and blink controls reject equality. No permanent re-expansion is needed for
this focused replay; it does not restamp the earlier 25,495-file inventory.

## Independent text-clock probe retirement (v1385)

All jobs are terminal. Current native producer pins 509 inputs, manifest
a47f0496c18261ff4650515b1c2cd6413451a44d8879b6b3b21fc032aec89c6f. Fresh whole cold GNU71/69CTest,
optimized UBSan3 cold targets, both programs, independent line/counter probes
and separate instrumented observer remain retained. Main441/native345 CI pass.
DOS product fingerprint6f5898dd is unchanged. Both private receipt-write and
missing-header failures remain separately retained; corrected v2 probes pass.

1,280 complete recovered references, actual/instrumented captures and build
intermediates and 1,044 source-backed caches retire after full temporary
restoration/SHA/size/mode/nsmtime/gzip EOF checks. Before/after deletion,
27,535 protected hashes and 509 source pins pass. The inventory inherits
v1384's 25,495 protected hashes and separately includes its later terminal
appender, closed logs, compositor replay, seal and final recovery output.
Net allocated reclamation is 350,756,864 bytes (334.5 MiB), after the
15.6 MiB lossless archive and before journal cost. Programs,
frozen inputs, original references, old proofs and failed attempts stay live.

Restore from DOS root before current reader replay:

```sh
python3 .analysis/reconstruction/probes/native-blink-v1385/verify_retention.py --restore
```

Without --restore it checks every recovery temporarily. Journal SHA-256:
4e22bc1edc74086a10d29a0035fc6e7b38e1e30934d61e02b82b4067b6760e4d. Old ba6eff48 proofs cannot attest
current a47f0496 source; they retain their original scope. This inventory
excludes its writing retirement log; a later terminal seal separately pins
closed outputs without restamping that proof. See focused differential/demo
notes for text-only adapter, explicit DAC diagnostics and open original
absolutephase/liveCG/CRT/scanout/ordinary-route limits.

## Live FONT/register/time probe retirement (v1386)

All jobs are terminal. Current native producer pins 509 inputs, manifest
a47f0496c18261ff4650515b1c2cd6413451a44d8879b6b3b21fc032aec89c6f. Retained v1385 whole cold GNU71/69CTest,
optimized UBSan3 cold targets, reference programs, independent line/font/raster probes
and old separately instrumented observer remain retained. Main441/native345 CI pass.
DOS product fingerprint6f5898dd is unchanged. The rejected direct FONT model and both passed ANK counting recipes remain
retained. The v2 counting recipe fixes repeated reads without restamping v1.

299 complete recovered references, fullFONT/VRAM samples, original temporaryimages and build
intermediates and 1,044 source-backed caches retire after full temporary
restoration/SHA/size/mode/nsmtime/gzip EOF checks. Before/after deletion,
27,637 protected hashes and 509 source pins pass. The inventory inherits
v1385's 27,535 protected hashes and separately includes its later terminal
appender, closed logs, final checks and seal.
Net allocated reclamation is 228,438,016 bytes (217.9 MiB), after the
26.3 MiB lossless archive and before journal cost. Programs,
frozen inputs, original references, old proofs and failed attempts stay live.

Restore from DOS root before current reader replay:

```sh
python3 .analysis/reconstruction/probes/native-cg-v1386/verify_retention.py --restore
```

Without --restore it checks every recovery temporarily. Journal SHA-256:
8af16fa8ebdccda54ccde6ac815f7b8c08b437dfac731c0ed3a3ff3a9e33dbf8. Old a47f0496 proofs retain their unchanged source scope; they do not attest
these new original VP4/font/register observations. This inventory
excludes its writing retirement log; a later terminal seal separately pins
closed outputs without restamping that proof. See focused differential/demo
notes for text-only adapter, explicit DAC diagnostics and open original
cadence, absolute phase, scanout and ordinary-route limits.

## Native DAC batch v1389

Final archive journal is .analysis/reconstruction/probes/native-dac-v1389/retention.json.
Net603.7 MiB reclaimed after the archive; another24.3 MiB of explicitly
aborted source-rebuildable products was cleared earlier. Frozen initial/final
producers, game/trace/shake, independent probes, original compressed40samples,
receipts and logs remain live. The journal inherits the unchangedv1388 protected
inventory and separately seals closedpost-retirement files. Archive/member SHA,
size/mode/nsmtime and completeoutergzipCRC/EOF pass before deletion and after it.

Restore from DOS root before CTest/retired-output replay:

```sh
python3 .analysis/reconstruction/probes/native-dac-v1389/verify_retention.py --restore
```

Without --restore this verifies the complete archive and live protected sources.
Oldlinear RGB controls retain f2 producer identity in the v1388 archive; current
whole rawRGB40/40 uses retainedoriginalV3 samples under supplied originalclock.
The initialstopped build has no accepted receipt; its rebuild journal is distinct.

## Full OP startup and controlled clock pair (v1390)

Lossless retirement journal and archive are in DOS-root
.analysis/reconstruction/probes/native-clock-owners-v1390/. Archive SHA-256:
`6f2c32ab93e9e81ecf9756af671d1c6ee8b47636ef04cca51ebc328cc22320dd`.
2887 files retired;587.84MiB net after archive/journal.
Original compressed full80/clock/thin streams and current game/trace/shake,
independent models, recipes,510-file source freeze and all proof receipts/logs
stay live. Retired rawscalar/HDIs and native expanded captures/reference RGB,
CMake objects/libraries and helper programs require --restore for full replay.
The verifier reads complete gzipCRC/EOF and pins every member SHA/mode/size/
nsmtime plus31536 inherited protected hashes. Prior
journals, closed proofs and source freezes retain their original identities.

```sh
python3 .analysis/reconstruction/probes/native-clock-owners-v1390/verify_retention.py
python3 .analysis/reconstruction/probes/native-clock-owners-v1390/verify_retention.py --restore
```

### Original Gaiji I/O clocks (v1394)

CPU0/nice19 serial original captures generated no builds. Lossless deduplication
retains 49 logical HDI/verifier-stream files in 15 content-addressed blobs and
reclaims 604.43 MiB. Complete and failed inner captures keep their identities.
Full gzip CRC/EOF/member SHA/size/mode/nsmtime and protected proof readback use
`.analysis/reconstruction/probes/native-gaiji-clock-v1394/verify_retention.py`
from the DOS root; `--restore` recovers logical files. The previous temporary
container is retired after its extracted members verify; its compressed bytes
are not claimed as live replay input. The separate cleanup-close receipt seals
the cleanup writer's actual terminal stdout after process exit.

Post-CI source-backed cache cleanup reclaims another 16.69 MiB; the full
CI gates pass (root 441 / native 345), with ledger and diff checks.

### Native elapsed work (v1395)

Cold builds, separate actual FrontEnd callers and eight default profile
captures close new source-bound proofs. Lossless content retirement reclaims
about 472.70 MiB: 2697 build/program/video logical files in1407 unique blobs,
plus 16 complete state/item text outputs in 2 blobs.
Complete CRC/EOF/member SHA and logical size/mode/nsmtime are validated; all
source freezes and closed receipts/logs retain their identities. Restore from
the DOS root with
`.analysis/reconstruction/probes/native-elapsed-work-v1395/verify_retention.py
--restore`; `--prefix` limits restoration to a needed relative subtree. Parent
protected state hashes resolve through the additional verified text archive.

Both full CI gates pass (root 441 / native 345). Source-backed post-CI caches
reclaim another 16.85 MiB; closed proof files remain protected.

### GDC elapsed work (v1396)

Current cold builds, sixteen actual callers, eight default captures and private
Xvfb close source-bound proofs. Lossless retirement reclaims 472.69 MiB:
2697 logical build/program/video files in 1407 unique blobs plus
16 complete state/item text outputs in 2 blobs. Full CRC/EOF/SHA,
logical mode/nsmtime and protected proof/frozen source pins are checked.
Restore from the DOS root with
`.analysis/reconstruction/probes/native-gdc-work-v1396-v2/verify_retention.py --restore`;
`--prefix` limits restoration. Supplemental mode-3 physical reset input
readback stays separate; old three-mode preparation/source/receipt unchanged.

Rejected V1 has its own verified archive/reader under
`.analysis/reconstruction/probes/native-gdc-work-v1396/`, reclaiming
472.65 MiB separately. Its 8657d4a2 freeze is not current-source acceptance.
Both full CI gates pass (root 441 / native 345). Post-CI source-backed caches reclaim 16.69 MiB separately.

### Original OP wait captures (v1397)

All three accepted originals, first33hook failure, unexecuted preparations and
readers are terminal. Product source stays510/ea5c016d; DOS6f5898dd unchanged.
Full root447/native345 CI, current and inherited v1396 retention readbacks,
tracking and diff pass. No fresh product build is claimed in this Oracle batch.

Only eighteen owned disposable HDIs / duplicate fonts are losslessly retired:
12 images and6 fonts,5 unique complete blobs. Net allocated reclamation after
archive/journal is218.40 MiB; post-CI source-backed caches recover16.38 MiB
separately (1050 files). Full gzip CRC/EOF, member digests, actual temporary
restored SHA/size/mode/nsmtime and116 current protected hashes pass before and
after delete. Full scalar loads/clocks, sources, receipts/logs and all failed
attempts remain live. Original targets/assets, host packages and saves are
untouched. The final raw images retain normal guest diagnostic-file writes;
restoration preserves them rather than reconstructing only an initial image.

From the DOS root:

```sh
python3 .analysis/reconstruction/probes/native-vsync-waits-v1397/verify_retention.py
```

Add --restore and optional --prefix before full wait-reader replay. Both the
content-addressed retired-content.tar.gz and retention.json journal are needed
for exact owned-path recovery; use fresh output/source names for new runs.
The failed33hook capture and import/reader failures are not upgraded by archive
CRC/restore success. The terminal seal separately closes writer stdout and
final checks/publication receipts.
