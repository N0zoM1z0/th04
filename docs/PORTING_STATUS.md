# Semantic and x64 port status

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

Updated 2026-10-12. The full native goal remains active on `port/modern-64`, in
`.analysis/worktrees/port-motion-v1402/`. Root `main` keeps the standalone DOS
product and indexes native findings. A root `git push` does not commit or push
native worktree changes.

## DOS ordinary text writers (v1410)

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
Continue source recovery, including the separate DOS installed-owner VSync
frontier, before long game campaigns. The full goal stays active.

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

`TextPlane` now uses the original WORD addresses and glyph/attribute sequence,
including row spills, mutable text bases and wrapped string attribute counts.
Sparse pages preserve writes outside the directly stored visible banks used
by HUD, Game Over and score registration.

All 664 native fixtures match 2,656 original MAIN/MAINE memory results at
loads 1000/3333. Optimized UBSan/bounds reproduces them. Cold core/five
programs, five related contracts and native CI 345 pass. The compiled
predecessor rejects edge and 2,049-character controls; the rejected string's
partial visible banks agree, so complete memory and failure status matter.

Native `port/modern-64` commit 8f7f7d5 has producer 524/6f214e8c. Proofs:
`port-motion-v1402/.analysis/port64/native-text-address-v1408/`. Verified
cleanup reclaims 13.04 MiB net, with complete proofs and frozen parents intact.
See [text writer recovery](reconstruction/product/TH04_NATIVE_GAIJI_TEXT_V860.md).
Next recover ANK/Shift-JIS addresses. Historical exact remains 661/663.
The palette VSync review below is a separate frozen producer, pending integration.

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

## Current products and acceptance

| Product | Accepted scope | Remaining boundary |
| --- | --- | --- |
| Historical reconstruction | OP 93/93, MAIN 493/495, MAINE 72/72, ZUN 3/3 authored functions | Function acceptance is not whole-file exactness; MAIN carpet/checkerboard deferred |
| Standalone PC-98 DOS | Four local-source products, repaired normal/invincible packages; user reports complete Normal routes/save | Automated natural dense Lunatic, timing/audio and second-emulator coverage remain separate |
| Semantic readable | Assets, heap, input/timing, scroll, bullets/VM/shots/items, RNG, score and process contracts clarified | Resume only for a concrete native blocker; old exact replay failures remain failed |
| Native x64 | Typed Linux/Windows gameplay, renderer, asset, lifecycle, persistence and sound owners with scoped Oracles | Full physical host/game-route acceptance remains open |

Target files pass local identity/format checks but remain
`candidate-local-attested`; external pristine-dump provenance is unresolved.
No native observation promotes a historical exact unit.

## Native progress

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

## Previous DOS Gaiji recovery (v1406)

`src/shared/hardware/graph_gaiji.cpp` now preserves continuous string byte
addresses, WORD/spill writes across FFFFh and return ES. Original OP and MAINE
entries agree with the final linked products on all 4,800 component controls
at load1000/3333. The compiled predecessor has 150 address-mask differences;
write-width and ES comparisons reject all 2,400 predecessor controls.

Both affected products were cold-built, then the ES correction freshly compiled
Gaiji with verified unchanged-object reuse. Final OP/MAINE links and IRQ audits
pass. Product inputs are 1,425 files / cfaa77bf; MAIN and ZUN keep their prior
frozen products. Historical exact remains 661/663. The full goal is active.

Replay: `.analysis/reconstruction/probes/dos-gaiji-v1406/`; final products:
`.analysis/build/th04-gaiji-v1406-final/`. The maintained
`scripts/runtime/verify_dos_gaiji.py` compares actual original/product
instructions. The phase's `verify_closure.py` checks source/program pins and
complete transcript carriers. See [Gaiji recovery](reconstruction/product/TH04_NATIVE_GRAPH_GAIJI_V861.md).
Continue function and native-owner recovery before long game campaigns.

Root CI passes 451 tests, ledgers, catalog and private target/database Oracles.
Lossless retirement removes 5,565 owned cache paths after archive and
metadata readback; 629 protected files and final closure still pass.
Source-backed Python caches add 8.48 MiB reclamation;
combined cleanup is 31.14 MiB net. Programs, MAPs and complete proofs remain.

Native `port/modern-64` is at 8f7f7d5, including GRCG, font and Gaiji
address recovery. The separate startup/motion integration on
`review/startup-motion-join-v1403` is frozen at 514 files / c2f8d689.
Its verified snapshot predates those renderer changes. Attest a combined
producer when integrating the two histories. The v1401 startup implementation
already reached `port/modern-64` through fffcc83.


v1403 integrates remote motion recovery a0b6149 with the independently
validated startup waits. Verified integration producer514/c2f8d689 is frozen;
CMake's new motion contract and its verifier are now both included in the
complete source manifest. Fresh GNU builds73 programs/71CTests; optimized
UBSan builds10 programs/7 contracts. Unchanged original MAIN0000:1DA8..1E13
and table2134:021E execute at load1000:184908 vectors per compiler agree,
including514 original DIV faults. Complete expanded comparison transcripts
match between GNU/UBSan. The compiled old blanket -32768 rejection fails.
This accepts the bounded corpus and explicit native fault surface; it is not
an exhaustive four-coordinate Cartesian product or historical byte exactness.

Eight fresh current startup/fourDemo/freshOP profiles each match original
selected state at15988 boundaries and every129 frozen v1401 output hashes.
Startup/IRQ code itself is unchanged. Physical timing, default resource/CPU
costs, full pictures and broader Boss/death/process remain open. Continue
bounded source recovery before long game campaigns. Windows GUI/focus/host
keys/audio opens remain excluded while the host is in use.

The original native push encountered a concurrent non-fast-forward remote
motion commit. Both histories were merged without force pushing. v1401 proofs
remain frozen at512/60cf4491, including its132 frontend fixture cases and
70GNU/6UBSan checks; their strict live-source reader correctly rejects current
source. A new reader verifies its archive/1150-file closure independently.
No old receipt was edited to claim the new producer. The frozen DOS parent
is a34c1357; current v1406 source is indexed above.
Historical exact counts/canonicality are unchanged.

Current replay index: .analysis/reconstruction/probes/native-startup-motion-join-v1403/
(DOS root); native .analysis/port64/native-startup-motion-join-v1403/.
Use build.py, validate.py and verify_retention.py in a fresh namespace;
check_frozen_parent.py reads old proofs and the expected strict-reader rejection.
All current source/program/vector/capture inputs are pinned. The read-only
original MZ target, complete1136 relocation topology and two separate compiler
outputs remain distinct evidence. Runs are CPU1/nice19, serial and muted.

Additional owned cleanup 468.70MiB after 16.93MiB archive. Full current
path/hash/size/mode/nsmtime journal is persisted before any archive/deletion.
CRC/EOF, all blobs, every temporary metadata restore and protected proofs pass.
No prior producer is retired. The v1401 initial auxiliary-metadata caveat remains
explicit in retention notes; current v1403 paths have full recovery metadata.

Retained v1401 native producer is512/60cf4491. OP startup now waits on the
independent unsigned IRQ owner and services PMD at timer deadlines within an
elapsed admission. It preserves inherited Logo counts and clears inactive zero
fallbacks. Cold70GNU/6UBSan contracts, three compiled negative controls,
132 frontend configuration/restart cases and eight full four-Demo routes pass.
Each route matches original selected state at15988 boundaries. Only startup
and text-clock traces change for PMD profiles; other127 outputs remain equal to
frozen v1399. No-driver retains all129. Current GNU/UBSan outputs match completely.
Default loading/graphics/CPU costs, physical timing and other scene adapters
remain open. Frozen v1400 DOS source is retained; its three-artifact108-case and
four cold product/Demo evidence remains separately pinned. See the handoff.

The v1362 GNU Reimu A / Lunatic / Turbo0 candidate is now terminal and
accepted by the independent `verify_natural_slowdown.py` reader: 88,249 route
refreshes plus 792 refreshes in a separate Scores process. It reaches all six
stages without Continue, exits registration by Esc, returns to fresh OP, and
stores real section3 clear mask1 at the physical rename and final file. The nine
other decoded score partitions and CFG stay unchanged; no pending file remains.
Final MAIN: stage5/frame13,649, lives7, misses6, score units5,597,294.

Natural density reaches439 bullets. At >=320 there are571 refreshes/287
slowdown2; at >=400 there are240/129. Complete deadlines/terminal counts pass.
At >=400, update P95/P99/max are6.61/8.50/13.37ms with no update exceeding its
own admission period. This is instrumented GNU/private-Xvfb/shared-WSL evidence;
uninstrumented physical FPS and original DOS parity remain unaccepted. Generic
traces do not expose every inner Ending phase. Audio opens remain zero.

Two actual ordinary X early-hit cancellations occur in Stage4, preserving miss
count while consuming stock, starting Bomb, clearing respawn and setting
invincibility255. The last-life proactive policy branch remains dry-controlled
only. Separate ordinary window probes pass early/closed cases (1,039/1,048
refreshes): early X cancels frame394 hit at395; closed-window X at401 remains
rejected at404 (stock2, Bomb inactive, miss1, respawn61). The first late probe
stays failed: its cleanup incorrectly expected MAIN Esc to return to OP, while
the host Escape handler exits MAIN directly. This is a probe cleanup failure,
not a demonstrated Bomb failure or original Escape-parity acceptance.

Retained GNU Reimu A routes:

| Route | Route + independent Scores refreshes | Scope |
| --- | --- | --- |
| Normal/Turbo1 | 89,008 +794 | Six stages/noContinue, physical clear/freshOP/restart |
| Lunatic/Turbo1 | 88,927 +790 | Physical clear; dense slowdown2 absent |
| Lunatic/Turbo0 | 88,249 +792 | Physical clear plus natural dense slowdown2 gates |
| Extra | 30,388 +790 | NoContinue, full eight A gaiji, physical clear/restart |

Prior UBSan Normal all-clear acceptance is revoked: mask0x19 is an unplayed
sentinel even though bit0 is set. The v1360 GNU Turbo0 attempt also stays failed
(88,267 refreshes, Final Stage miss13, masks0x19); its separate795-refresh
Scores reader and bounded dense slowdown observations remain valid. Require
mask<4 plus the selected shot bit, never bit0 alone. All these jobs are terminal;
do not poll or revive dated PID/tool handles from historical active-job files.

Registration, lifecycle/Continue/HUD, stage/Ending/Extra, score/config, demo,
MusicRoom/unlocks and muted sound owners have separate component/integration
evidence. Eight actual GNU/UBSan Continue cases and ten GNU setup/corrupt-file
cases are retained. Startup combinations cover27 GNU/UBSan and19 earlier
Windows cases. Broader character/shot/rank/Ending/Extra routes, actual Windows
display/input, physical audio and uninstrumented performance remain open.

No C++ rebuild: compiled producer485 inputs/`00af24f7…`, GNU game
`dbe17225…`, UBSan `029e7ba1…`, Windows `5b6cf2c3…` remain v1356. The completed
route uses frozen consumer491/`d25ba16e…`. Actual Bomb probes use archived
consumer492/`3135f76e…`; handoff formatting changes only that Python probe's
layout, preserves its AST, and freezes current492/`4ed57dab…` separately.
Do not restamp old runtime receipts with current source identities.

Primary native receipts: `.analysis/port64/bomb-input-v1362/` (completed route,
independent-natural-v1364.json, actual-rescues-v1364.json) and
`.analysis/port64/bomb-window-v1364/` (early/late/failed probes, independent
readback, both492-input source snapshots). All paths here are relative to the
native worktree. See its `docs/port64/evidence/host-window.md` for replay details.

## Comparison priority for the next agent

The user's primary comparison is **original Japanese DOS versus reconstructed
DOS**, both through the PC-98 game route. Native x64 must also preserve gameplay
state and effects. Native-host equality and successful native clears do not
replace either comparison. Start with the four bundled demos, then bounded
recorded ordinary play; compare score, consumed input, RNG and actor state at
the same logical boundary, followed by VRAM/palette/effects and process/save
transitions. See [DOS/native differential handoff](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md).

TH08 is a read-only workflow reference, not TH04 evidence. Its active worktree
is dirty; do not edit it, run its builds, change its database or launch its game.
Complete trace/end/input-consumption guards and first-divergence diagnostics
are the useful parts to adapt. Retained four-demo DOS traces pass their
full input/score/RNG schema, nine raw actor/effect pools and 22 Boss/Midboss/player
state blocks. Retained DGROUP streams cover3996 updates per demo; scalar traces
also retain each terminal decision. Boss state stays at setup throughout these
demos; death and respawn are not exercised. Other globals, Boss combat and
process teardown remain open.

Raw video comparison retains every graphics/text/palette byte on both pages
at all3996 updates per demo. Text, palettes, page selectors and selected programmed GDC fields
agree. Complete v1372 replay accepts all 38 compared video regions in all four
demos, with 3996 updates and zero differing updates each. The missing Stage 4
lighting-animation cell shifted later cels; the corrected symbolic table
removes all 1032 remaining Demo 1 graphics differences. Cold MAIN changes only
17 animation DATA bytes. Point-number multiplier indices 10/11, packed bullet
boxes and carpet image columns remain verified. Raw scanout timing and process
teardown stay open. Historical
focused point-number replay remains blocked before comparison by an incompatible
bullet/add.cpp header in the old scaffold; it grants no fresh exact credit.

v1373 implements the native point-number pool and event/render joins that were
missing at06922ce. Item pickups select white/yellow and retain base-point/pull
multiplier semantics; bullet zaps insert white numbers. Original CPU controls
at two loads agree on830 complete state/list/request rows and494 full indexed
screens on GNU/UBSan, with two additional full400-slot render cases. Five source
mutants reject. The69 GNU products pass68 CTests; two focused UBSan products
and five headless frontend pictures perhost pass. These are component and
integration-smoke claims, not complete natural original-DOS/native picture
parity. Earlier full-route and Windows receipts retain their own producers.
The same read-only audit finds the native Stage 4 lighting formula already
preserves the original cel 5/column 2 exception. Its component Oracle excludes
original dirty-page transients replaced by full host redraw; paired presentation
acceptance remains separate from the data formula.
Later four-demo observations pair selected input/score/player/RNG state and
nine complete actor/effect pools with original DOS. Broader ordinary gameplay,
complete pictures and process transitions remain unpaired.

## TODO, in order

1. Extend accepted four-demo original/reconstructed DOS comparison to other
   global owners, full scanout timing and process teardown, then
   recorded ordinary play covering Boss combat and death/respawn.
   Preserve identical data/config/saves,
   logical input, complete-trace gates and first-divergence diagnostics.
2. Extend the same comparison to native x64. Attest input mapping, RNG ring and
   process state, score units, update order and dialogue boundaries; then compare
   rendering/effects, VRAM/palette and save/process transitions.
3. Expand native full routes across characters/shots/ranks/Endings/Continue and
   Extra. Current accepted GNU Reimu A routes do not cover every combination.
4. Verify uninstrumented natural dense Lunatic performance and broader host
   pacing. The completed Turbo0 instrumented route closes its scoped dense gate.
5. Actual Windows display/input and physical audio remain unavailable under the
   user's no-host-GUI/no-device constraint. Do not launch or work around it.

Historical exactness remains a separate ledger. The two deferred MAIN cases
are not prerequisites for this behavioral comparison.

## Delivery and storage

The previously delivered experimental GUI package is retained at
`/mnt/d/Entertainment/Game/Touhou/th04-reconstruct/native-port64-v1354/`.
`start-muted.bat` and `start-linux-muted.sh` explicitly mute; independent host
saves and Normal/3-life/2-Bomb defaults preserve all 21 preceding DOS/package
files. Source archives/profiles accompany the binaries. Windows input automation
remains rejected; physical audio, dense timing and full-goal acceptance remain.

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

Follow [retention](ANALYSIS_RETENTION.md); never blanket-delete `.analysis/`.

Detailed historical batch evidence remains in ledgers, subject notes and Git.
Use [handoff](RE_HANDOFF.md), [semantic contracts](SEMANTIC_READABILITY.md) and
`python3 scripts/status.py` for current authority instead of old progress labels.

Native v1374 additionally accepts four complete original/native MAIN demos on
23 selected before-update/terminal fields and exact RNG counts (15,988 boundaries
per GNU/UBSan host). The Stage 1 midboss now receives the fractional scroll
accumulator. Native v1375 also accepts all nine complete actor/effect pools at 15,984
pre-score updates after restoring Midboss yellow bonus popups. Paired pictures,
other globals, scanout and ordinary Boss/death/process routes remain open.
See the current handoff.

Native v1376 additionally exercises the actual idle OP→four demos→OP FrontEnd,
retaining all15988 selected state/count matches. Raw TRAM revealed a missing
DEMO PLAY label; original timer72/gaiji/position/C3 attributes constrain its
renderer repair. GNU/optimized UBSan compare40 complete label spans including
frames72/73/74.
v1377 aligns the presentation seam after the complete update. All40 sampled
complete8000-byte canonical TRAM planes agree on GNU and optimized UBSan,
including score/HUD; all15988 selected state/count boundaries still pass.
Full graphics/RGB, physical blink/scanout and whole-picture acceptance remain
open. New consumers retain the immutable v1376 compiled producer; see the
current handoff and differential note.

v1378 repairs the missing native Midboss shake event consumer. Original CPU
MAIN_01_TEXT0AAF:2246..2315 agrees on3262 state/movement controls. All15984
complete demo shake globals/requests and prior scalar/nine-pool controls agree.
Demo1 frame3379 diagnostic game-area differences drop55357→430, confined to
top rows16/17; full graphics/RGB and physical scanout remain unaccepted.
Final immutable509-input producer9346e951… is cold-built on GNU; details and
replay are in the differential note and native docs/port64/evidence/demo.md.

v1379 paints the full ordinary400-row background ring before motion, removing
Demo1frame3379 remaining430 game-area differences on GNU/optimized UBSan.
Allselected scalar/shake/text checks remain equal; nine other nonzero samples
are unchanged. Onlyview.cpp is cold-built/relinked against attested unchanged
v1378 dependencies; no new whole-current cold/CTest or fullpicture claim.

v1380 corrects Marisa laser color to the original pre-update modulo, removing
11,384 color differences in four Demo 2 samples; all ten sampled Demo 2 game
areas now agree on GNU/optimized UBSan. Five other nonzero samples remain.
All selected scalar/shake/text checks pass, all 125 captures agree between
variants, and parent state/shake traces remain byte-identical. Only view.cpp
changes among 509 inputs; previous whole cold/CTest/pool evidence retains its
producer. Whole graphics/RGB/scanout and broader pairing remain open.


v1381 restores whole-pool white/purple pellet passes from the original caller
and actual leaf execution. All 40 overlap color differences disappear:
Demo 1 frame3996 32→0, frame1952 34→26. Other 38 complete index/RGB samples
remain unchanged. All scalar/shake/text checks pass on GNU/optimized UBSan;
parent state/shake traces remain byte-identical. Ordinary circles are excluded
at all five former remaining samples. Four nonzero samples and full pictures/
scanout/broader pairing remain open; the bounded view build retains prior core
and whole cold/CTest/full-pool producer identities.

v1382 adds the missing eight-slot item-spawn splash owner and white foreground
dots. GNU/optimized UBSan pass311 originalCPU component cases each and all15984
complete81-byte natural splash records. All103 late-sample pixels disappear;
39 of40 sampled game areas now agree, with initialDemo1 still different. Other37
entire index/RGB samples remain unchanged. Fresh cold GNU71 programs/69CTest
and optimizedUBSan3 core/game/trace/shake products pass all nine full pools,
selected scalars,shake and complete text checks. Old products retain separate
producer identities. Drawing-relative CPU geometry does not accept programmed
GDC/physicalscanout; complete pictures/cache/margins/RGB/broader routes remain.

v1383 preserves Stage4 background draw inputs before the carpet callback and
applies the tail's current/previous row copies from the updated ring. Actual
original CPU controls explain the first 124,439 game-area discrepancies;
48 tail-copy controls cover tile and 400-row wrap. All 40 standard sampled
game areas now agree on GNU/UBSan; all 133,251 first/second-picture changes
equal original indices and 38 entire samples stay unchanged. Ten separate GNU
lighting fields/full text samples agree, repairing 7,498 frame1666 pixels.
Complete scalar/shake/splash/text traces remain unchanged. View-only cold builds
retain separate v1382 whole-cold/69CTest/nine-pool producers. Snapshot-only
edge failure stays unaccepted; full pictures/cache/margins/RGB/scanout/broader
routes remain open.

## Complete RGB diagnostic frontier (v1384)

Native now selects the final MPN stage palette after BMT/BFT setup, including
MarisaST10. Actual GNU/optimized UBSan126 captures match; all40 entire indices/
TRAM and parent state/shake/splash/display/save traces stay unchanged. The fix
changes720358 sampleRGB pixels;40 game-area index diagnostics remain zero.
Independent attested emulator composition retains full rawRGB:12 curtain
samples zero,28 unequal. Explicit DAC projection isolates5×556 Demo-label
blink pixels, not whole-picture acceptance. Recover blink refreshes/liveCG/
textscroll/CRT/scanout before broader picture and ordinary route pairing.
Current509 manifestba6eff48 changes only view.cpp; bounded TU builds reuse
attested v1382 objects. Old cold/CTest/pool/proof identities remain separate.
See the current handoff and focused differential note for replay commands.

## MAIN text blink and independent display clock (v1385)

Native now preserves blink-before-reverse and supplies a persistent display
clock to MAIN text. All15988 native rows replay unchanged GDC source;
80 complete controlled text layers plus8 attribute cases match independent
DOSBox-X output. Original15984 triples expose zero/two-refresh residues;
original absoluteepoch is uncalibrated. FreshGNU71/69CTest and UBSan3cold
produce127 equal ordinary captures with40 unchanged entire indices/TRAM
and6 parent trace/save hashes. Priorfullpool identity stays separate.
LiveCG/textCRT/absolutephase/scanout and broader routes remain open.

## Complete FONT/register and original time observations (v1386)

All 15,984 new original VP4 records carry the complete 516 KiB FONT memory,
eleven text/CRT fields and actual PIC/raster times. FONT is stable. The old
direct asset model fails at 32 ANK V/W bytes; the actual A9 write-port guard
model matches all 528,384 bytes. All 38 old programmed regions match, while
25 complete raw GDC records retain raster differences.

Rendering with the actual FONT/register inputs reproduces the earlier 40
samples. The original period is 17.72322658483988 ms versus native's
17.730496 ms approximation; cadence calibration is the next bounded task.
The 509 product source inputs (a47f0496…) and retained v1385 build/capture
identities are unchanged. Physical scanout, full raw RGB, original phase,
broader routes and historical exact acceptance remain open. See the current
handoff for replay recipes and evidence scopes.

## Calibrated native cadence (v1387)

All 15,984 original GDC/time records reproduce the archived timing model;
native now uses the nearest period, 17,723,227 ns. Fresh GNU69 CTests,
optimized UBSan3 targets and127 identical ordinary Demo files pass. Independent
20,000 scheduling and1,000,000 frontend-refresh controls reject the old cadence;
an actual private Linux window/input route also passes. Producer03351541 has
two changed inputs. Full-font/register references and original selected-state
checks remain retained. RawRGB12/40, DAC diagnostics32/40 and eight phase cases
remain; original common boot/process epoch is the next owner. Physical scanout,
broader paired routes, Windows and historical exact acceptance remain open.

## Original common boot clock (v1388)

Fresh boot/four-Demo capture observes GDC constructors0/0/32 and an immediate
first callback0→1. Blind display-event counts and unchanged counter
body reproduce all15,988 original phases without offsets. Native producer
f2b03ebb admits this initial event; onlyview.cpp changes. FreshGNU69CTest,
UBSan3 and actualfour-Demo127 files pass;126 hashes match the033 parent.

A separate actual FrontEnd recorded-event-clock experiment reproduces all
15,988 count/blink rows, selected state, 40 complete text planes and game-area index diagnostics; whole
index differences remain; explicitDAC
RGBdiagnostics match 40/40, raw RGB 12/40. Oldzero negativecontrol rejects.
Defaultboot/loading/process CPU-I/Oelapsed owners,rawpalette/RGB,physicalscanout,
broaderpairedBoss/death/process andWindows remainopen. The full goal staysactive.

## Native raw RGB palette owner (v1389)

Seven display consumers now use the recorded PC-98 DAC4→6→8 expansion.
FreshGNU69CTest, optimizedUBSan3, actualfourDemo127 identicalvariant files,
privateLinuxXvfb and two-load GameOver/MAINEregistration consumer checks pass.
Only28 fullRGB files differ fromf2; all87 non-RGB files keep old hashes.
Explicitoriginal-clock samples now match40/40 whole rawRGB without projection;
defaultphase matches37/40. Oldlinear sameclock rejects28/40. These are scoped
programmed-frame samples, not physicalscanout/defaultboot/wholepicture acceptance.
Default elapsed-time owners, physical/liveDAC/cross-emulator output, broader
paired routes and Windows remain open. The goal stays active. See the handoff.

## Full OP startup and observer control (v1390)

Native demo validation now runs the Logo and title startup before four natural
demos, then completes a fresh OP title. Cold GNU passes 69 CTests; muted GNU
and optimized UBSan produce 128 identical capture files. Selected state, RNG
and draw counts match both fresh original captures at all 15,988 boundaries.
The analog 4→6→8-bit DAC and 17.723227 ms refresh period retain their prior proofs.

With each original capture's supplied display-event clock, all 40 complete raw
RGB samples match the independent renderer: 80/80 across the fresh pair, without
normalization, crops or fitted offsets. Default full-startup headless captures
match 32/40 and 30/40 against the separate originals. The earlier 37/40 result
applied to compact headless entry against retained V3.

These muted captures use `--pmd-driver none`; PMD measure waits and original
audio timing remain unpaired. Boot/loading/process clock ownership, physical
and cross-emulator scanout, broader paired routes and Windows input/audio remain
open. Development stays active; see the handoff for evidence and cleanup recovery.

Producer: `bdc1fb56f80b1d5d987c89a1cfe63cea9da155eb6ef8eb662c10480dd02c4b5e`. See the differential note and current handoff.

## Retained physical configuration and startup clocks (v1391)

Native development is active. Demo validation now loads the physical
configuration before running one Logo, four natural demos and a fresh OP title.
Nine observed OP/MAIN configuration requests match the incoming file; complete
CFG and score files stay unchanged. Cold GNU passes 69 CTests. Each of four
muted driver profiles (`none`, `pmd`, `pmdb2`, `pmd86`) produces 129 identical
GNU / optimized UBSan capture files, with selected state, RNG and draw counts
matching all 15,988 original boundaries.

The active PMD profiles spend 94 native refreshes between the measure request
and first SUPER_load; `none` spends zero. Original PMD measure/audio timing
remains unpaired. A one-call configuration bypass keeps all previous 128 files
identical but uses the wrong rank at every configuration point; the new
independent option check rejects it.

A same-source original zero-delay repeat shifts refresh ordinals by 8 relative
to the prior baseline. The prior delayed pair shifted by 5 or 6. That shift
cannot uniquely diagnose inserted sleep; keep each capture's clock separate.
With the fresh original's supplied clock, all 40 complete raw RGB samples match
an independent renderer without normalization, crops or fitted offsets.
Default native counts are 31/40 for `none` and 34/40 for the active profiles;
these are timing diagnostics. Prior 80/80 supplied-clock evidence retains its
original producer identity. Boot/loading/process clock ownership, physical
and cross-emulator scanout, broader paired routes and Windows input/audio
remain open. See the handoff for scoped evidence and cleanup recovery.

Retained producer: `c6a90f57e662cbbe85cec9b55047f0ffce5df818067725f687b548f4d2579010`. Native commit: `927ce48`.
See the handoff and focused differential note for evidence and recovery.

## Cold PMD installation and original OP timers (v1392)

Native development is active. The application PMD driver now installs from cold
chip state and applies installation writes to both logical timers and PCM.
Read-only original OP captures show the first Timer B period is **73.728 ms**;
the previous native state incorrectly began at 16.128 ms. Two independent
installation controls reject the old state and the PCM-only update.

Cold GNU passes 69 CTests; optimized UBSan passes three PMD contracts. Four
muted driver profiles each produce 129 identical GNU / UBSan capture files.
Demo state, RNG, draws, shake and physical configuration/save files remain
identical to the retained original-paired captures at all 15,988 selected seams.
One Logo and five completed titles include the final fresh OP ready.

Default active-PMD waiting now spans 97 native refreshes; the bounded original
OP captures span 92. This is not full startup-clock acceptance: original CPU
and file-loading time still need paired owners. Complete default RGB matches
remain 31/40 for none and 34/40 for active profiles; own-counter-phase 40/40 is
diagnostic. Earlier supplied-original-clock matches retain their original
producer identity. Broader paired gameplay/process routes, physical scanout
and Windows input/audio remain open. See the handoff for evidence and cleanup.

v1392 producer (unchanged in v1393): `9cfe100a84ac0a325d498b9b81602298009e462643b2cfa453947fe85bc1b049`. Native commit: `28b3f95`.
See the current handoff and focused differential note for complete scoped evidence.

## Original OP loading work and clock owners (v1393)

Native development is active. The repaired PMD application still installs from
cold state with the original observed 73.728 ms first Timer B period. New
read-only OP captures separate startup loading and drawing work: changing only
CPU budget from 24,000 to 36,000 reduces the Logo PI load phase from 66.98 to
44.62 ms and its drawing phase from 61.66 to 41.04 ms. Gaiji work scales
differently; there is no universal startup-delay constant.

The unchanged native producer retains its cold GNU 69 CTests, three optimized
UBSan PMD contracts and four driver-profile Demo comparisons. New GNU / UBSan
service probes with each original's measured installation age agree within
1 ms sampling; zero-age controls complete but fail the same timing check.
These diagnostics do not pair default native loading clocks. A real interrupted
GDB capture exited zero without completion; the new reader rejects it.

Retained Demo state/RNG/draw/shake/configuration/save evidence covers 15,988
selected seams. Complete default RGB counts remain scoped diagnostics, with
broader gameplay/process, physical scanout and Windows input/audio still open.
See the handoff for current evidence, limits and cleanup recovery.

Unchanged native producer: `9cfe100a84ac0a325d498b9b81602298009e462643b2cfa453947fe85bc1b049`. Native evidence commit: `7416a91`.

## Original Gaiji I/O elapsed work (v1394)

Development remains active. Four fresh original OP captures isolate the
emulator I/O owner: default Gaiji loading is 40.235458 / 34.996667 ms at fixed
24,000 / 36,000 cycles; only changing 8-bit I/O delay to zero gives 17.134000 /
11.404611 ms. Actual 8,192 read / 25,604 write accesses and pinned integer debit
rules account for 22.829167 / 23.412333 ms of Gaiji work. Complete loaded target,
GDC replay, raw PIC clocks and negative controls pass. This is DOSBox-X timing,
not a physical bus or fitted native wait.

Native source remains the 510-file `9cfe100a` producer; this batch changes only
evidence/docs and adds the ROOT Gaiji verifier. Next establish elapsed-work
handoffs across native asset loading, drawing and process entry. Previous
GNU/UBSan/Demo/window proofs keep their old producer identities; default clocks
and broader fidelity remain open. See the handoff and focused differential note.
Native evidence commit: de21a71.

## Resident elapsed work through OP (v1395)

Explicit resource/graphics/process intervals now advance resident Timer/PCM
across process gaps and local mix during a process, flushing pending wait once.
Actual maintained OP frontend callers using independent original v1393 work
inputs pass in GNU/UBSan. PLAY epochs of 255.036542 / 178.822806 ms and
93-refresh readiness have sample errors of 3.648611 / 8.074889 ms, within one
frontend refresh. Zero and graphics-only controls complete but fail the same
epoch gate; removing graphics can still alias 93 refreshes. Default work
adapters remain empty.

Current cold GNU builds 71 programs and passes 69 CTests; optimized UBSan
builds seven targets and passes four sound contracts. Eight default captures
across four driver profiles reproduce all 129 retained outputs each. Private
muted Linux Xvfb passes with zero audio device opens. Default resource/GDC
pairing, full pictures and broader routes remain open.
Native manifest: 55459c6f487e25ce39e0b8499b89f52936e0273c536905e94b8a7764426fdb7e.
Native commit: 955de04.

## Display time through OP loading work (v1396)

Explicit work now advances both resident sound and headless GDC text time,
retaining fractional refresh time. Independently observed first-display-to-PMD
epochs plus original work reproduce all twelve OP loading/readiness counter
assertions per CPU input in actual maintained frontend GNU/UBSan executions.
A display-only control preserves sound timing but rejects display counters.
External observation retains fractional origin and excludes double admission.

Cold GNU 71 programs / 69 CTests, optimized UBSan seven selected targets / four
sound contracts, sixteen actual callers, eight default four-profile captures
and private muted Linux Xvfb pass. All 129 default outputs per run retain their
v1395 identities. Default CPU/bus/resource/graphics costs and wait-edge
semantics, full pictures and broader routes remain open.
Native manifest: ea5c016d0cd40bcb453bd9f6c27c6ec24c2513ec63342fa8be2fa8d6acc85d43. Native commit: 49b2fa5.

## Distinct original OP waits (v1397)

Three complete original routes (FM86 CPU24000/36000 plus BGM-off CPU24000)
show active measure polling preserves Count1, so the first Logo wait inherits
104/100 and returns with zero new counted interrupts. BGM-off frame_delay(0)
clears Count1 and returns immediately; loading leaves Count1=1 before Logo.
Count1 clears after Logo waits while Count2 continues. Two counted IRQs can
cross one GDC observer seam; preserve their distinct phases.

Independent public wait reader and counter/PIC/GDC mutation controls pass;
product source remains v1396 native49b2fa5/ea5c016d and DOS6f5898dd. Native
refresh-sampled measures and fixed two-tick Logo waits still need replacement
by the proved busy-service / IRQ-count owners. No new build/full-picture or
exactness claim. See current handoff, focused differential note and retention.

Native documentation commit: `19e5356`; the product source producer stays
`49b2fa5` / 510-file `ea5c016d`.
