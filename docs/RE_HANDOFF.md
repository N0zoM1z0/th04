# TH04 current handoff

Development and the full reconstruction/native goal are active. The user is
using Windows: keep launches muted, use Linux headless/private Xvfb, and do
not open Windows GUI, change focus or inject host keys. Windows acceptance
remains open. Updated 2026-10-12.

## Joined native palette output and counter delays (v1419)

Published `port/modern-64`: `85fe1f30af27a1aee1a8822f2e950c95cafa2a11`.
Shared `pc98_palette::show()` restores the three complete 266-byte originals:
MAIN 0000:1F04, OP 0000:1DE0 and MAINE 0000:19EC. It keeps signed WORD
truncation, tone clamping, analog output and the notebook LCD branch with its
original masks, weighting, query polarity and port order. Startup's actual
DAC consumer and six other display consumers use this source.

Fresh joined producer 536/3ba0ba42 retains the published live WORD delay and
bulk IRQ owner. GNU Release and optimized UBSan/bounds each cold-build the
complete core/frontend and nine related programs, pass nine selected CTests,
and agree on 20,832 retained original palette I/O/DAC controls. Each also
passes 144 original delay consumers, 36 real ISR controls and 2,008 independent
integer/raster vectors. Native CI passes 345 tests. The actual prior startup
source rejects 288 of 1,368 analog controls. Historical exact stays 661/663.

Replay is under each owned tree's `.analysis/port64/`, in
`native-palette-show-v1418` and `native-palette-show-join-v1419`.
The original v1415/v1417 captures keep their own source identities. Current
source freezes, selected programs and 5,945 parent pins remain; verified
compiler/cache retirement releases 101.02 MiB net across both producers.
Continue shared elapsed scene-wait ownership. Physical LCD scanout, broader
paired routes and Windows remain open; this recovery ran no game campaign.

## Native IRQ counter and frame_delay primitive (v1417)

Producer 534/8a83575e adds live `vsync::Delay`: construction clears only
Count1 and truncates the argument to WORD; readiness polls the current
unsigned word. A different consumer can reset Count1 and extend the wait.
Positive delays remain pending without an IRQ owner, with no GDC fallback;
zero clears Count1 and returns immediately even when uninstalled.

Counter bulk advancement preserves the original carry-skip recurrence and
both wrapped words with full-width UINT64 arithmetic. It returns the full counted-IRQ
total without intermediate multiplication overflow. RasterClock's path with
no observers uses this recurrence and integer edge search; the callback
overload still emits every IRQ. Actual startup uses the path with no observer.
This enables large WORD delays/cadence inputs without billions of host loops.
Elapsed MAINE/registration Scene integration and physical CPU/IRQ latency
remain open; a new primitive is not full-scene acceptance.

Both cold GNU and optimized UBSan/bounds build all 82 programs and pass all
80 CTests. Complete original frame_delay bodies MAIN 130E:00D7,
OP 0DA1:002B and MAINE 0CC7:0033 (21 bytes each) pass 144 consumer controls
at loads 1000/3333. Separate 36 actual original ISR/IRET injections gate the
counter recurrence. Consumer word changes are explicit stimuli. Independent
Python big integers check 280 bulk and 1,728 delay/raster vectors, including
UINT64_MAX and the 4,294,901,760-IRQ wait boundary. No physical timing claim.

Three compiled mutations reject 25 overflow, 1,428 Count2-reset and 576
signed-threshold cases. Existing wait consumers retain 32 original controls,
432 native vectors and 1,296 waits per compiler. Eight muted actual
startup/four-Demo/fresh-OP routes retain all 129 prior hashes per profile and
15,988 original selected-state boundaries each; GNU/UBSan outputs agree.

Replay: `.analysis/reconstruction/probes/native-counter-delay-v1417/`;
producer: `.analysis/worktrees/native-counter-delay-v1417/.analysis/port64/native-counter-delay-v1417/`.
`focused.json`, build receipts and `verify_counter_delay.py` record the gates.
`verify_retention.py --restore --prefix` restores owned archived paths.
Verified retirement reclaims 506.12 MiB net. Source freeze, full original/
integer projections, selected programs and compiled mutations remain.
Historical exact remains 661/663; actual elapsed consumers, complete pictures,
broader Boss/death/process, physical LCD scanout and Windows remain open.

Published native head: `dcbe8f73c0a5e36b93fc2117252ffe71055e7c71`.

## DOS analog and LCD palette output (v1415)

`palette_show.cpp` now restores the original `PaletteNote` branch in
MAIN, OP and MAINE. Nonzero selects eight LCD shades, with the original
component masks, weighted conversion, polarity query and port order.
Default zero keeps analog RGB output. Each complete original function is
266 bytes: MAIN 0000:1F04, OP 0000:1DE0, MAINE 0000:19EC.

Three cold DOS products from producer 1425/491e4afa link and pass IRQ audits;
MAIN also passes its bullet tables. All 20,832 original/compiled instruction
controls agree at loads 1000/3333. The actual old MAIN rejects 6,488 LCD
controls and retains 456 analog matches. The added state WORD also passes
528 VSync wait and 324 lifecycle controls across the three rebuilt products.
These results establish ordered I/O and far-return state; historical exact
counts stay unchanged.

Replay: `.analysis/worktrees/dos-palette-note-v1415/.analysis/reconstruction/probes/dos-palette-note-v1415/`.
Full original functions/transcripts, fresh EXEs/MAPs, six palette/state OMFs,
complete source freeze and 1,744 parent proof files remain. Verified archive
retirement and source-backed cache cleanup release 22.07 MiB net.
CI passes all 451 tests and tracking gates. See the palette section in
[build readiness](reconstruction/product/TH04_NATIVE_BUILD_READINESS_V1.md)
and [retention instructions](ANALYSIS_RETENTION.md). Continue hardware/caller
recovery; no game campaign was run for this change.

## Joined native MAINE wait consumers (v1416)

Joined native producer 532/037b0f2e restores shared Animation's logical
WORD parameter boundaries. A zero frame_delay continues on the same call;
negative arguments become unsigned WORD waits. Black fades align once, then
use signed WORD speed: nonpositive values skip all per-group waits. The
optional PaletteSink reports every fade-generated palette_show, including
all 18 updates on one admission for zero speed. Explicit tone requests stay
in RequestSink. This is a logical refresh projection, with no shared Count1
owner, CPU execution cost or elapsed raster/IRQ timing claim.

Both cold GNU and optimized UBSan/bounds build all 81 programs and pass all
79 CTests. Complete original MAINE 0CC7:0033..0047 frame_delay and
0000:0622..06A3 black fades pass 72 cases at loads 1000/3333; the actual
0000:2206..222B wait executes inside each fade. Count1 pulses are explicit
stimuli and palette_show is a guarded tone observer. All 36 native vectors
match, including WORD truncation, zero and 7FFFh/8000h boundaries.

Both compilers also retain 96 OP/MAINE original fade controls and 24 native
timelines from the independent palette producer. Both target identities,
complete fade extents and all 96 retained wait streams are re-attested.

The actual latest 6b0e1ba Animation predecessor differs in three complete
delay traces; its four fade traces already agree. Current Congratulations retains 32 original branches,
50 original fade/key clocks and 20 complete PI-page comparisons per compiler;
verdict retains 916 state/request cases and 10 clock/key controls. Their
pixel references retain their earlier native decoder producer. Eight muted
startup/four-Demo/fresh-OP routes retain all 129 prior hashes per profile and
15,988 original selected-state boundaries each. No exact/full-game promotion.

Replay: `.analysis/reconstruction/probes/native-maine-wait-join-v1416/`;
producer: `.analysis/worktrees/native-maine-wait-join-v1416/.analysis/port64/native-maine-wait-join-v1416/`.
`focused-gnu.json`, `focused-ubsan.json` and `focused.json` record commands.
Use `th04-port64-cutscene-contracts` for Congratulations/verdict helpers;
frozen port readers need read-only `PYTHONPATH=ROOT` for the HDI parser.
Failed missing-parser/wrong-program recipes remain. Verified retirement
reclaims 505.93 MiB net; full source/projections, selected programs and
predecessor remain. Continue actual elapsed scene wait ownership; physical
timing, complete pictures, broader Boss/death/process and Windows stay open.

Published native head: `c2d8363606d73090f2ad47062788a5b497622647`.

## Native signed WORD palette fades (v1414)

Published `port/modern-64` is at `6b0e1ba`, combining the recovered palette
fade with the native wait/text owners. `maine::Animation` now truncates speed
to the original WORD and uses its signed condition. Zero and negative WORD
speeds finish after one initial refresh; positive speeds keep `1 + 17 * speed`
waits. Original OP/MAINE 0000:0622 and 0000:0666 pass 96 instruction controls
at loads 1000/3333. Both fresh compilers agree on 24 native timelines; the
actual old source rejects 14 boundary vectors.

Joined producer 530/4dc27bde freshly builds the complete core, actual frontend
and four selected contract programs in GNU Release and optimized UBSan/bounds.
Each passes four related CTests; native CI passes 345 tests. The prior v1412
79-program/77-CTest graph keeps its own frozen producer and receipts.

Complete evidence is in `native-palette-zero-v1413` and
`native-palette-join-v1414`, under each tree's `.analysis/port64/` directory.
The join's `verify_closure.py` checks its source archive, programs, comparisons
and 1,635 frozen parent files. Retirement and source-backed cache cleanup
release 41.48 MiB net across this recovery; complete originals and programs
remain. `verify_retention.py --restore --prefix build-gnu/` restores one
compiler's archived caches. Continue native hardware and scene-owner recovery
before longer game validation. Historical authored exact stays 661/663.

## Joined native palette waits and text writers (v1412)

The native merge retains both parents: ordinary WORD/Shift-JIS and Gaiji text
producer `328585f`, and palette wait producer `f2a51e2`. Cold producer
528/768091dc builds all 79 programs and passes all 77 CTests under both GNU
Release and optimized UBSan/bounds. The earlier selected UBSan subset is
historical evidence; this producer checks the complete graph.

Both compilers pass 32 original OP 0000:2648 wait controls at loads 1000/3333,
432 raster/cadence vectors (1,296 waits), 2,656 MAIN/MAINE Gaiji comparisons,
all 65,536 WORD characters and 65,536 two-byte inputs, and 1,680 complete
ordinary-text memory controls. Original Gaiji entries are MAIN 0000:1B0C/1B50
and MAINE 0000:0FC4/1008; ordinary entries are MAIN 0000:229E/22F6.
Retained original transcripts keep their target/helper pins and are read in
full; their receipts are not reassigned to the new native source.

Actual old `328585f` startup source fails the Count1-clear check (expected
exit 1). Eight muted SDL dummy routes (GNU/UBSan × none/pmd/pmdb2/pmd86)
complete startup, four demos and fresh OP. Each retains all 129 prior output
hashes and passes 15,988 original selected-state boundaries. GNU/UBSan output
sets agree. This remains scoped runtime agreement, with no exact, complete
picture, physical CPU/IRQ timing or Windows acceptance claim.

Private replay: `.analysis/reconstruction/probes/native-wait-text-v1412/`;
producer: `.analysis/worktrees/native-wait-text-v1412/.analysis/port64/native-wait-text-v1412/`.
`focused.json` records commands. `verify_retention.py --restore --prefix`
restores owned archived paths; retirement reclaims 508.31 MiB net.
Source, selected programs, full comparison streams, receipts and the real
predecessor remain. Continue bounded native scene wait/hardware recovery;
broader Boss/death/process routes, complete pictures and Windows remain open.

Published native head: `9a7f380a2ef7d947dec2207f0552effcf01d032b`.

## Combined DOS text and VSync recovery (v1411)

Current MAIN/OP/MAINE include both mutable `TextVramSeg` reads and the
installed-owner VSync wait. Serial rebuilding compiles changed source freshly
and validates reused objects; links, IRQ audits and MAIN bullet tables pass.
Producer 1,425/82ade790 passes 3,156 ordinary-text, 2,656 Gaiji, 528 VSync wait
and 324 lifecycle comparisons. All four complete ordinary-text bodies retain
the original MAIN match after mapping the text-variable data operand.

The isolated `dos-text-vsync-join-v1411` tree retains source, products/MAPs,
wait OMFs, full transcripts and replay/retention readers. Its closure also
checks 776 frozen text-only and 858 frozen wait-only files independently.
See [text recovery](reconstruction/product/TH04_NATIVE_TEXT_CHARACTER_V1409.md)
and [VSync recovery](reconstruction/product/TH04_NATIVE_VSYNC_V864.md).
Historical authored exact remains 661/663; its prior native text producer is frozen at 328585f.
Verified retirement reclaims 33.45 MiB from the combined compiler/cache
copies; temporary v1410 restores return to their existing archive.
Continue native scene waits and hardware owners before long game campaigns.

## Frozen DOS installed-owner VSync wait (v1408)

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

Both isolated and published-main CI pass 451 tests, targets/calibration,
ledgers and catalog. Live-main Ghidra/JDK, MAIN database and mutation gates
also pass; all three original databases were attested before work.
Source-backed own/main caches reclaim another 8.49/8.52 MiB, bringing this
batch to 416.18 MiB net. Frozen DOS 30-file and native 1,235-file parent
closures retain their hashes. All 1,425 live-main input files match the cold
producer byte for byte after four pre-existing EOL representations are journaled and
normalized to Git/attributes LF; logical Git source is unchanged by that step.

Historical exact remains 661/663. The text-variable gap is closed in v1411
above; native scene waits, physical timing, broader routes and Windows
acceptance remain open.

## Frozen DOS ordinary text writers (v1410)

Both text ASM owners now read the maintained `TextVramSeg` instead of adding
a fixed A000h. The character writer keeps its full WORD ANK/JIS/Shift-JIS
conversion; the string writer keeps its lead-byte handling, store order,
wrapped attribute count and far Pascal ABI.

Cold MAIN/OP/MAINE builds pass links, IRQ audits and MAIN bullet tables.
The complete 87-byte character body in all three products and the 114-byte
MAIN string body agree with original MAIN after mapping only the text
variable's data offset. MAIN passes 1,680 full memory/write/ABI comparisons
at loads 1000/3333; OP/MAINE each pass 738 against the shared MAIN character
contract. The prior Gaiji owners retain 2,656 original comparisons.
The compiled v1407 MAIN predecessor differs in all 80 alternate-base controls,
including return ES. Far strings use independent RAM outside the loaded image.

Producer 1,425/451a46f7 and selected products are in the isolated
`dos-text-character-v1410` tree. Complete records and readers are under
`.analysis/reconstruction/probes/dos-text-character-v1410/` there. See
[text writer recovery](reconstruction/product/TH04_NATIVE_TEXT_CHARACTER_V1409.md).
Historical authored exact remains 661/663; native remains at 328585f.
CI passes 451 tests. Verified retirement reclaims 21.14 MiB net; complete
current records and 30 frozen DOS parent files retain their hashes.
Join these writers with the recovered DOS VSync owner above and verify
the combined producer before long game campaigns. The full goal stays active.

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

Original instructions read `TextVramSeg` at DGROUP 2134:0768. The DOS ASM
references are recovered by v1410 above. Historical authored exact acceptance
remains 661/663. The full reconstruction/native goal stays active.
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
DOS ordinary-text mutable bases are recovered above. Preserve the separate
native VSync review; other native scene adapters
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
