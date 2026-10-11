# TH04 current handoff

Development and the full reconstruction/native goal are active. The user is
using Windows: keep launches muted, use Linux headless/private Xvfb, and do
not open Windows GUI, change focus or inject host keys. Windows acceptance
remains open. Updated 2026-10-12.

## DOS installed-owner VSync wait (v1408)

Shared `vsync_wait.cpp` now chooses the original branch once at entry:
installed IRQ waits for any unsigned Count1 change; otherwise it waits for
the next GDC blank. Neither path clears Count1/Count2. The owner is a public
byte alias of START/END's existing saved PIC mask, with no additional storage.

Cold all-four-product producer 1425/d9383fa5 passes links, MZ/IRQ audits and
MAIN bullet tables. Complete original MAIN 0000:2462, decoded OP 0000:2648
and decoded MAINE 0000:2206 each have 38-byte waits; compiled contributions
are 49 bytes. Three-artifact comparisons pass 528 controls at loads 1000/3333,
including 72 real ISR/IRET injections and 24 midwait owner changes. Existing
START/IRQ/END retains 324 controls. The real polling-only predecessors each
reject 136 installed-owner cases while their 40 unowned cases still agree.

Fresh muted four-Demo runs pass all 15,988 original consumed-input/score/RNG
boundaries. This is a selected-state regression; earlier whole-pool/video
acceptance retains its own frozen producer. Raw register differences are
recorded, including different artifact DS layouts and incidental AX/DX/FLAGS;
no complete register, byte-exact or physical latency claim is made.

Replay index/products: `.analysis/reconstruction/probes/dos-vsync-wait-v1408/`.
`focused.json`, `negative-final.json` and `demo-regression.json` record commands;
`verify_retention.py --restore --prefix <owned path>` restores archived inputs.
Verified retirement reclaims 52.39 MiB from 3,584 owned paths/1,450 blobs.
Stopped observer diagnostic logs separately reclaim 346.77 MiB losslessly.
Final products/MAPs, wait OMFs, original/compiled transcripts and failure
readers remain. See [VSync recovery](reconstruction/product/TH04_NATIVE_VSYNC_V864.md).

CI passes 451 tests, targets/calibration, ledgers and catalog. Original MAIN,
OP and MAINE databases were attested in root before work; isolated private
Ghidra/JDK CI checks skip. Source-backed own caches reclaim another 8.49 MiB.
Frozen DOS 30-file and native 1,235-file parent closures retain their hashes.

Historical exact remains 661/663. Next source work includes DOS ordinary
text writers' mutable TextVramSeg references and other native scene waits;
physical timing, broader game routes and Windows acceptance remain open.

## Native ordinary text writers (v1409)

`TextPlane` now recovers the complete WORD character input and the original
Shift-JIS byte-stream conversion. It preserves mutable text bases, WORD
addresses, NUL handling, malformed pairs and glyph/attribute aliases. HUD,
Game Over and the real frontend use the recovered character writer.

All 65,536 WORD characters and 65,536 two-byte strings agree with original
MAIN 0000:229E/22F6 on both visible banks. A separate 840-case corpus agrees
on complete 80000h..DFFFFh memory at loads 1000/3333: 1,680 comparisons.
Cold GNU and optimized UBSan/bounds reproduce the results; prior Gaiji retains
all 2,656 comparisons. The frontend builds, six component contracts and
native CI 345 pass. No game campaign was needed for this function recovery.

Native `port/modern-64` is at 328585f, producer 526/3e7d5e33. Complete evidence
is in `port-motion-v1402/.analysis/port64/native-sjis-text-v1409/`.
Verified cache retirement reclaims 14.50 MiB net; the closure reader checks
all current proofs and 780 frozen parent files. See
[ordinary text recovery](reconstruction/product/TH04_NATIVE_TEXT_CHARACTER_V1409.md).

Original instructions read `TextVramSeg` at DGROUP 2134:0768. The two DOS ASM
owners still fix A000h; recover their mutable references with a cold affected
product and original-instruction comparison next. Historical authored exact
acceptance remains 661/663. The full reconstruction/native goal stays active.
The palette VSync review remains a separate frozen producer.
Root CI passes 451 tests and the updated ledgers; target preflight passes.

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

Retained native v1408 commit 8f7f7d5 has producer 524/6f214e8c. Proofs are in
`port-motion-v1402/.analysis/port64/native-text-address-v1408/`. Verified
archiving and source-backed cache cleanup reclaim 13.04 MiB net; current
source/program/transcript closure and frozen native/DOS parents pass.
See [text writer recovery](reconstruction/product/TH04_NATIVE_GAIJI_TEXT_V860.md).
The v1409 ordinary-text recovery above extends these address semantics.
Historical exact remains 661/663 and the full goal stays active.

The palette VSync recovery below remains a separate frozen review producer;
it has not been merged into the text-writer producer.

## Retained native OP palette VSync wait (v1407)

`review/native-gdc-poll-v1407` remains frozen at f2a51e2, producer524/d9edcdf5.
Palette waits preserve both counts and choose installed Count1 inequality or
the next GDC blank; frame_delay and Logo retain their distinct clear orders.
GNU77 programs/75 CTests and optimized UBSan13 programs/10 contracts pass.
Each compiler passes32 original controls and432 ideal vectors/1296 waits;
eight muted routes retain129 prior outputs and15988 selected-state boundaries.
The real48e05da startup predecessor rejects counter retention. This review
has not been integrated into the newer ordinary-text native producer.

Evidence and lossless recovery: `.analysis/reconstruction/probes/native-gdc-poll-v1407/`.
Its frozen source/program/transcript proofs and prior cleanup remain intact;
v1408 above is the separate DOS wait recovery. Other scene adapters and
CPU/loading/ISR costs remain open. See [VSync ownership](reconstruction/product/TH04_NATIVE_VSYNC_V864.md).

## Retained DOS text Gaiji recovery (v1407)

`gaiji_text.cpp` now restores the mutable text base, original store order,
wrapped attribute count and return ES for `GAIJI_PUTCA/PUTSA`. Original
MAIN and MAINE match all 2,656 complete memory/write/state controls at
load 1000/3333, including long strings whose glyphs alias attributes.
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

Shared DOS installed-owner VSYNC_WAIT now has the v1408 cold replay above.
Recover DOS ordinary-text mutable bases next; preserve the separate native review. Other native scene adapters
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
