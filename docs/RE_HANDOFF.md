# TH04 current handoff

Development and the full reconstruction/native goal are active. The user is
using Windows: keep launches muted, use Linux headless/private Xvfb, and do
not open Windows GUI, change focus or inject host keys. Windows acceptance
remains open. Updated 2026-10-12.

## Native text Gaiji migration (v1408)

Native `TextPlane` now follows the original WORD coordinates, mutable text
base and glyph/attribute store sequence. Sparse pages retain spill and alias
writes while the existing visible arrays serve HUD, Game Over and registration.
Ordinary frame copies stay near 8 KiB.

All 664 native fixtures match original MAIN 0000:1B0C/1B50 and MAINE
0000:0FC4/1008 at loads 1000/3333: 2,656 full memory comparisons. Optimized
UBSan/bounds reproduces them. Cold core/five programs, five related contracts
and native CI345 pass. The compiled predecessor rejects both edge and long
string inputs; the string's partial visible banks agree despite its failure.

Native `port/modern-64` is at 8f7f7d5, producer 524/6f214e8c. Proofs are in
`port-motion-v1402/.analysis/port64/native-text-address-v1408/`. Verified
archiving and source-backed cache cleanup reclaim 13.04 MiB net; current
source/program/transcript closure and frozen native/DOS parents pass.
See [text writer recovery](reconstruction/product/TH04_NATIVE_GAIJI_TEXT_V860.md).
Next recover ANK/Shift-JIS writer addresses before long game campaigns.
Historical exact remains 661/663 and the full goal stays active.

The palette VSync recovery below remains a separate frozen review producer;
it has not been merged into the text-writer producer.

## Native OP palette VSync wait recovery (v1407)

Fixed native base48e05da now separates palette VSYNC_WAIT from frame_delay.
Original decoded OP0000:2648..266D (38 bytes) branches on DGROUP0856:
installed IRQ snapshots Count1 at1AC6 and waits for any change; otherwise it
finishes the current GDC blank and waits for the next rising blank. Neither
path clears Count1 or Count2 (1AC8). Native startup palette fades retain
both words; frame_delay and Logo retain their different clear orders.
Original fade helpers0000:0622..0664 and0666..06A3 call2648 before
the palette loop and once per speed-loop iteration (0632/0643/0676/0687).

Cold producer524/d9edcdf5 passes77 GNU programs/75 CTests and13 optimized
UBSan programs/10 focused contracts. Each compiler passes32 unchanged-original
controls at load1000/3333 and432 independent ideal raster/cadence vectors
(1296 waits), including FFFF-to-zero and status/IRQ edge separation.
Count1/GDC inputs are explicit consumer stimuli, not measured physical IRQs.
The real48e05da startup predecessor fails the new counter-retention contract.
Eight fresh muted startup/fourDemo/freshOP routes retain all129 output hashes
per profile from frozen v1404; each passes15988 original selected-state boundaries.

The first cold build failed the valid-final-edge overflow contract (74/75).
Its source/program/logs remain frozen; v2 repairs exhaustion and passes.
This batch changes native wait/startup source, with no new DOS product or
historical exact promotion. The older25-byte compiler-service observation describes only the polling
producer, not the complete original function. Shared DOS vsync_wait.cpp still implements only
port polling; recover its installed-owner branch in a separate cold replay.
Other native scene wait adapters, CPU/loading/ISR costs, complete pictures,
Boss/death/process, second-emulator and Windows acceptance remain open.

Review branch: review/native-gdc-poll-v1407. Replay index:
.analysis/reconstruction/probes/native-gdc-poll-v1407/; native receipts:
.analysis/port64/native-gdc-poll-v1407-v2/. Original extent SHA-256:
989ba1d57373892c48f460097161f08d5391388535059d007327fda0f4e45b20.
Focused commands are in validate.py/focused.json; original/native reader:
port64/verify_gdc_poll.py. Recovery reader: verify_retention.py
(--restore/--prefix for owned archived paths). Frozen v1404's736-file closure
and3179-path/1489-blob archive pass without modifying old receipts.

Verified archive retirement reclaims502.05 MiB net from this batch's
successful/failed build intermediates, nonselected programs and duplicate
capture outputs. Full path/hash/size/mode/nsmtime, CRC, every blob and protected
proof are checked before deletion. Source freezes, selected programs, complete
original controls/native vectors and failure evidence remain live.
Both isolated full CI gates pass (root451/native345), with ledgers and diff checks.
Pinned private targets/calibration pass; isolated private Ghidra/JDK checks skip,
while original OP database was actually attested in root before recovery.
Source-backed owned post-CI caches reclaim another16.35 MiB; this batch
reclaims518.40 MiB net, disjoint from prior frozen cleanup.

Goal active; CPU1/nice19 serial and muted; no Windows GUI/focus/keys/audio.

## Current DOS text Gaiji recovery (v1407)

`gaiji_text.cpp` now restores the mutable text base, original store order,
wrapped attribute count and return ES for `GAIJI_PUTCA/PUTSA`. Original
MAIN and MAINE match all 2,656 complete memory/write/state controls at
load1000/3333, including long strings whose glyphs alias attributes.
The compiled predecessor has 40 final memory differences and 426 ES differences.
The previous graphics Gaiji functions retain all 4,800 controls with the new
OP/MAINE products.

Three affected products were rebuilt with freshly compiled changed source
and verified unchanged-object reuse. Links, IRQ audits and MAIN bullet tables
pass. Product inputs are 1,425 files / fb50205b; ZUN keeps its prior product.
Historical exact remains 661/663. The full goal stays active.

Replay index: `.analysis/reconstruction/probes/dos-text-gaiji-v1407/`;
products: `.analysis/build/th04-text-gaiji-v1407/`. See
[text Gaiji recovery](reconstruction/product/TH04_NATIVE_GAIJI_TEXT_V860.md).
The native `TextPlane` migration is indexed in v1408 above.
Continue function recovery before long game campaigns.

Root CI passes 451 tests, ledgers, catalog and private target/database checks.
Verified archiving retires 7,143 owned cache paths; source-backed Python
caches bring cleanup to 38.00 MiB net. Complete original/compiled memory
transcripts, selected products and frozen parent proofs remain.

## Retained acceptance and next work

Historical authored acceptance remains 661/663: OP 93/93, MAIN 493/495,
MAINE 72/72 and ZUN 3/3. MAIN carpet/checkerboard are deferred. Function
acceptance does not imply whole-file exactness. Targets remain
candidate-local-attested; pristine-dump provenance is unresolved.

Retained original/reconstructed DOS bundled demos agree on consumed input,
score/RNG, nine complete pools, 22 state blocks and every configured video
region at 3996 updates each. These paths exercise Midboss; Boss combat,
death/respawn and complete process transitions still need paired checks.
Native selected-state/pool/shake/splash and sampled game-area results retain
their original frozen producers; default route hash equality here is scoped
regression, not new complete-picture acceptance.

Frozen v1404 combined 520/774cc800 already passes original motion/GRCG/font
corpora plus eight routes; v1407 starts from newer Gaiji native base48e05da.
Older review/native-integrated-v1404 and review/startup-motion-join-v1403
remain immutable. Earlier GNU Reimu A Normal/Lunatic/Extra/save/restart
routes retain v1356 Linux scope; the previous UBSan Normal clear claim
remains revoked (mask0x19 is a sentinel; require mask<4 plus selected shot bit).

Next recover shared DOS installed-owner VSYNC_WAIT with owner/ABI guards,
cold affected products and original/Demo replays. Other native scene adapters
and default elapsed-work models still need source recovery. Serialize actual
builds. Preserve the active Windows host, shared writer worktrees, private
original inputs, saves and frozen evidence. TH08 stays read-only.

## Commands and navigation

Run python3 scripts/preflight.py before target-dependent work, then the
focused comparison, python3 scripts/ci.py and git diff --check. Use fresh
probe namespaces, CPU1/nice19, one Borland/Wine writer and muted headless runs.
See [differential evidence](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md),
[VSync ownership](reconstruction/product/TH04_NATIVE_VSYNC_V864.md),
[retention recovery](ANALYSIS_RETENTION.md), [workflow](RE_WORKFLOW.md)
and [subject index](reconstruction/README.md). Earlier chronological handoff
material remains in Git and the focused notes; it is not the live work queue.
