# TH04 reconstruction and port64 handoff

Updated 2026-10-17. Both development goals remain active. Verify the current
machine and select one bounded task. Historical exact-function counts are not
whole-game completion metrics. Keep all new code and documentation in English.

## Published branches and local availability

| Purpose | Published baseline | Availability |
| --- | --- | --- |
| DOS reconstruction, comparison tools and ledgers | `main: 585392f` | Current checkout; later evidence commits follow this baseline |
| Native x64 source | `port/modern-64: 791203f` | Fresh writable `.analysis/native/port64-recovery-v1445/`; old frozen working directories remain missing |

The old `.analysis/worktrees/` directory was absent at the 2026-10-16 audit,
although Git retains its registrations. This includes `native-natural-clear-v1432`,
`native-main-pause-v1431` and `dos-smem-page-copy-v1423`. The reason is unknown;
do not count their absence as cleanup or claim their private files remain live.
Do not prune registrations to conceal the loss or overwrite frozen branches.

Root v1437/v1436 captures, compressed memory/video, reports and recovery archives
remain. Native v1432 root reports/archives remain, but all 94 protected files
listed under its missing trees are unreadable. Historical DOS v1437 receipts
also reference a missing candidate MAIN/MAP. Complete historical replay needs
those original sources of evidence. New builds/captures must have new identities;
never alter an old receipt or seal to accept different paths or hashes.

New v1438 root MAIN/MAP files and four captures are now available independently
of those trees. MAIN is `.analysis/build/dos-boss-video-v1438/MAIN.EXE`; its MAP
is `.analysis/reconstruction/probes/product-20261016-041217-299bcab8-main/source/obj/main-native.map`.
Their hashes reproduce the historical content identities below, with new
producer receipts. Initial cold compilation linked successfully but its wrapper
refused publication after comparison-tool changes altered the input fingerprint.
Subsequent verified cache publication reused 192 C++ objects and relinked. This
is not a cold deterministic exact replay. Both attempts remain retained.

```sh
git status --short
git ls-remote --heads origin main port/modern-64
git worktree list --porcelain
taskset -c 1 nice -n 19 python3 scripts/preflight.py
python3 scripts/status.py
```

Read `AGENTS.md`, [current state](RE_HANDOFF.md), [architecture](ARCHITECTURE.md),
[workflow](RE_WORKFLOW.md), [knowledge base](KNOWLEDGE_BASE.md) and relevant
`.agents/skills/`. Query `config/knowledge.csv` before repeating experiments.
Target preflight passes; provenance remains `candidate-local-attested`, not proof
of an official pristine dump. Before using target disassembly, also run
`python3 scripts/ghidra.py ARTIFACT check`.

The native source is now restored into a fresh namespace, without altering
old registrations or receipts. Use this writable checkout for native work:

```sh
git -C .analysis/native/port64-recovery-v1445 status --short
git -C .analysis/native/port64-recovery-v1445 log -n 3 --oneline
```

Avoid recreating a missing frozen directory. Main commits do not publish native changes;
commit and push each branch separately and verify its remote head.

## Boss defeat, post-Boss dialogue and bonus event integration (v1453)

Native `791203f` extends the actual original/native comparison to **9835
updates**, through Orange defeat, post-Boss dialogue, stage bonus and leave.
Both cold GNU and optimized UBSan programs pass selected state/RNG/input,
global homing, nine pools, four Boss blocks, Continue/save, popup/title rows
and 2665 actual BB calls over 9834 intervals. Source565/3cf3900b.
All59 active-TRAM samples pass; the complete-picture gate retains 4
whole RGB failures at frames 9284, 9349, 9600, 9700. Keep these failures.
Stage2 update9836, complete campaigns, raw graphics-plane identity, physical
scanout, NP2, Windows and historical exactness remain open.

See [the bounded evidence note](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md)
for target addresses, falsified approaches, replay and remaining picture gates.

v1453 recovery replays the archived missing-TRAM producer and both corrected
9835-update programs, preserving all177 picture observations and the retained
RGB failures. SHA/mode/nsmtime retirement totals 1481.680 MiB net over two disjoint
journals;all16595 protected hashes remain equal. Five owned restored aliases
and eight borrowed aliases verify and retire;borrowed bytes receive no new
cleanup credit. See the focused note for exact recovery selection and failures.

## Boss circle clipping and complete sampled pictures (v1452)

Native `a8e0165` fixes the seven remaining v1451 score-area graphics samples.
Actual private pixel-write traces identify the Orange entrance circle at
center (232,40), radius 326, color 9 as the writer of (557,64) at update 6740.
Both trace programs reproduce the frozen producer's selected 8000-update state
and all 38 complete BMP/index/TRAM observations before the repair.

Original MAIN far `0000:11EC` reads DGROUP clipping words 032C..033A.
All 38 captured after-score DGROUPs retain `(32,16)-(415,383)`, with zoom 0;
the native circle helper had assumed the default whole-screen rectangle.
The helper now accepts a clip rectangle,and the common Boss-circle call supplies
that observed stage rectangle. This preserves the target's clipped-bottom-row
asymmetry. Isolated original execution and both compiler profiles verify
900 render vectors and 1053 circle vectors,including 135 stage-clip cases.
Other Boss/disc/rectangle and actor rendering paths are outside this repair.

Both fresh GNU and optimized UBSan programs now match **all 38 complete 640x400
RGB pictures** at actual score return `0AAF:0207`:zero differing pixels,
including the seven previously failing frames6740,6741,6753,6765,6772,6773,6774.
The uncorrected real producer still reproduces 1377 differing pixels;changing
one complete-picture pixel independently fails the same comparator.
Both profiles preserve selected 21 scalar/RNG/input fields,nine complete pools,
four Boss blocks,Continue,CFG/SCR,popup state/rows and title state/three rows
over 8000 updates,plus 2665 actual BB calls over 7999 intervals. Repeat paints
preserve pools/RNG/input and full pixels. All 15988 native Demo state boundaries
stay equal. GNU 87 programs and 83 CTests pass;source closure 565/394e53f4.

Evidence: `.analysis/reconstruction/probes/native-score-pixels-v1452/`.
Original capture remains the immutable DOSBox-X v1451 score capture with live
font/video/DGROUP;the v1450 constructed-BB Oracle remains refuted. The correct
pre-scroll title phase from `a8a67af` is retained. Old negative reports and
retention journals remain unchanged. Restore the v1451 score capture's four
archived aliases before strict original readers,and verify/retire them afterward
without counting borrowed files as new cleanup.

Verified retention archives 640 owned aliases/intermediates in 255 blobs,
releasing 254.469 MiB after archive and new gzip recipes; all 13102 protected
hashes remain equal. Current GNU87/cache, UBSan game/Orange/cold cores, all38
GNU pictures, complete original compressed font/video/memory and the old failed
producer remain recoverable or live. `recover.py` verifies SHA/mode/nsmtime.
`replay_restored.py` restores one owned archived actual writer, borrows four
v1451 original aliases and reruns it plus both repaired8000-update programs.
Every selected state/entry/popup gate and all38 BMP identities reproduce;
the old writer still fails1377 pixels and both current profiles pass. All five
aliases verify and retire afterward. The four borrowed aliases receive no new
cleanup credit; previous journals and failed attempts remain unchanged.

Next extend the original/native comparison beyond 8000 toward Boss defeat and
process/campaign completion. These 38 samples establish programmed-display
agreement,not every frame or physical scanout. Other globals,full routes,NP2,
Windows,canonicality and historical exactness remain open. Both full goals
remain active.

## Historical title gates (v1450; BB phase inference withdrawn)

Clock/string/row and complete primitive observations remain valid. The old
constructed natural-BB interpretation and its source preview are refuted by
v1451 actual entries/pictures. The archived first "negative" uses the correct
pre-scroll phase. Old receipts/source/programs/journals remain immutable; use
the focused differential note for the correction and replay context.

## Retained popup result (v1449)

Native `da4ee5f` remains the replayable popup/score-tail producer. Its BGM334
aggregate failure, score-tail0/25000 counterexample, source closure and both
retention journals are preserved in the focused differential note. V1450
supersedes only the newly built title producer and its configured gates.

## Native Continue and full-power pickup repaired (v1448)

Native source `7bdcd60` now applies item collection's clear effect to the real
bullet owner. An actual ordinary Game Over/Continue reaches a full-power pickup
at update 7640. The old executable leaves bullets active; original MAIN instead
sets DGROUP2134:BCBA to20, then19 next update. Its first visible state/pool
failure is boundary 7642. The failed executable, source and reports remain.

A fresh original 8001 capture and complete cold GNU/optimized UBSan builds pass
8000 updates: 21 selected state/RNG fields, actual player input, nine complete
pools, four Boss blocks and complete CFG/SCR bytes. GNU 85 programs / 82 CTests pass.
Five original code-fetch/caller/memory checkpoints at frame7547 establish that
player0AAF:5FCF consumes20h before Game Over0AAF:3A51; the later menu2000h resumes
that same call through5FCA/00F4. Keep this distinct from STD dialogue before
player_update. The real ranked Continue changes only decoded score section 1;
all ten full 16-bit checksums and the complete encoded file agree.

Producer 557/8284f2cd freezes every maintained source before both cold builds.
Final consumer 557/3e985ee3 changes only the Python save-scope text/reporting;
all compiled inputs are unchanged. Five real negative reader controls pass.
Replay/source: `.analysis/reconstruction/probes/native-continue-v1448/`,
`result.json`, `cold_build.py`, `finalize_consumer.py`, `continue-witness.json`.
Public original reader: `scripts/probes/attest_th04_continue_checkpoints.py`.
Native save/UI controls are component stimuli; blocking timing, complete
pictures/TRAM/scanout, other globals, full process/campaign, Windows and exact
promotion remain open. Continue these comparisons; both development goals stay active.

Verified retention archives 243 owned aliases/intermediates into 243 content blobs:
21.612 MiB archive,54.297 MiB net released,2338 protected hashes checked. Restore/
CRC/SHA/mode/nsmtime checks pass. Restoring five original/prototype aliases and
rerunning three real 8000-update programs reproduces the old 7642 failure and both
current successes, including full selected output/save/GO traces. The five aliases
are checked and retired again. Current GNU programs/cache,UBSan game,both new
cold cores and complete compressed captures remain. Use recover.py to restore
capture aliases, or replay_restored.py for restore/run/retirement. The old 94
missing files are unrelated and no historical receipt is rebound.

## Original dialogue/player input boundary corrected (v1447)

The v1446 input interpretation and the `13e6676` latch are withdrawn. Actual
original MAIN code-fetch/caller checkpoints at load `10FC` show STD `0AAF:2454`,
dialog `0AAF:2BFB/2A7C`, then player `0AAF:5FCF`, all at frame 6548. Dialogue occurs
before player_update. The loop sample contains `20h` (Shot), but player entry
contains `2000h` (Enter). The old comparator confused these boundaries. Its state/
pool/Boss results remain; player-input acceptance is withdrawn. Old receipts
are unchanged and affected evidence/knowledge is explicitly reclassified.

Native `a7f9bea` removes that latch and keeps live dialogue keys. Public capture
--dialog-checkpoints and attest_th04_dialog_checkpoints.py bind target code,
CPU/stack, conventional/DGROUP memory, raw video and observer sources. Native
--frontend requires this witness for blocked frames. A fresh public original
capture of 7,501 updates supports GNU/UBSan 7,500-update comparisons: 21 state/RNG
fields, actual player input, nine full pools and four Boss blocks agree.
The real old executable fails only player input at 6548 (`20h` versus `2000h`).

One pre-script sample also matches player/RNG fields, all nine pools and all
141,312 pixels of the instantaneous programmed-GDC playfield graphics projection.
Box subregions overlap that playfield; they are not extra samples. Independent
emulator rendering source matches its pinned archive and corroborates GRB/DAC
conversion. TRAM, full pictures/scanout and physical timing remain open.
Eight real inner controls check PC/frame/code/caller/memory/input ownership.

Source closure557/f6c6e393 has fresh main/view/audio builds against unchanged attested
cold GNU/UBSan cores. Fresh dependencies cover 130 own files; 231 reused core
dependencies/library hashes and 82 unchanged core contracts pass. This is a
leaf rebuild, not a fresh complete cold-core build. Final root CI 573 with live
MAIN database/mutation checks and native CI 354 pass. Native private Ghidra
skips because its project is absent; the real database replay is in DOS root.

Verified archival retires 26 owned aliases in 17 blobs: 346.137 MiB net after a
39.959 MiB archive. SHA/CRC/mode/nsmtime and 258 protected hashes pass. Four
restored 7,500-update FrontEnds reproduce two old input failures and two current
passes, with complete selected state/pool/Boss/file/prefix outputs. Five aliases
are verified and retired again. Current GNU cache/programs, selected UBSan game/
cold cores and full compressed capture/RAM/video/source evidence remain. Failed
layout and 6549-stop captures stay distinct. Old missing 94 files are unrelated.

Replay/source/recovery: `.analysis/reconstruction/probes/native-dialog-prefix-v1447/`.
Original: `native-dialog-prefix-v1447-public-original`; use recover.py before
readers, or replay_restored.py for restore/replay/retirement. Native tree:
`.analysis/native/port64-recovery-v1445/`. The closed retirement log is pinned
only in a separate final closure; no old journal or receipt is rebound.
Continue Game Over/Continue input/resident/score ownership and complete pictures.
Broader process/campaign, Windows and historical exactness remain open.

## Historical v1446 state/pool result; player-input interpretation superseded

Source13e6676's Stage1 latch was based on the wrong callback ordering. V1447
removes it and replaces the loop-sample comparison with actual player-entry
evidence. The old557/d246f71f producer and557/7c4b8576 Python consumer still
reproduce their7500-update selected state/full-pool/Boss results, but their
player-input acceptance is withdrawn. Failed/successful receipts and recovery
archives remain unchanged; the ledgers record this correction explicitly.

## Earlier native ordinary component and source repair (v1445)

Fresh native GNU85 programs/82 CTests and optimized UBSan entire-core/tracer
match original Normal/ReimuA seed64,6 lives/0 bombs at3997 boundaries/3996
complete updates:21 fields/LCG-ring state and counts plus nine full pools,
including inactive bytes. Two deaths/respawns end with4 lives/2 misses.
main_state.cpp now publishes pending collision hits before completed-frame
observers, fixing original MAIN DGROUP2134:4669 mismatches at3078/3284. The old
cold c0a1060 negative retains only those two field failures and equal pools.
GNU/UBSan state/pool outputs and15988 old/new native Demo regression boundaries
are byte-identical; the latter does not renew original Demo/picture acceptance.

Source closure556/49984d82, native CI354 and root CI573/live MAIN Ghidra
replay/mutations pass. Public native tool:
port64/verify_ordinary_state.py, requiring the current DOS checkout's readers
and a restored original capture. Canonical proof/source/recovery is
`.analysis/reconstruction/probes/native-recovery-v1445/` in this DOS checkout,
also symlinked under the fresh native tree. Do not inherit missing old producers.
The native start is an explicit component fixture. Continue actual FrontEnd
ordinary dialogue/Boss/Game Over and remaining globals/pictures; natural process
timing, broader campaigns, Windows and historical exactness remain open.

Current v1445 retention releases245.527 MiB net; recovery/re-execution and
3087 protected hashes pass. Use replay_restored_v2.py in the v1445 private
namespace for repeatable restore/replay/retirement. Old missing files are unchanged.

## Current OP input diagnosis (v1444)

Initial/fresh source OP misses its second Enter because rendering is still
black-in at1000ms/tone84 and its first character poll sees Enter held with
uninitialized input_prev2Eh. At1120ms key_det2000h and BIOS Return are set;
the real branch waits for INPUT_NONE to clear the latch. Original is already
character-ready/input_prev0 at1000 and shot-ready at2000. Preserve original
undefined stack behavior; an initializer or input_s.asm change would conceal
this mechanism. Measure initial-renderer subcall costs next if continuing DOS
timing work. Native development can resume in a newly attested checkout.

New read-only diagnostic nine-entry routes admit the same first7547/second600
state components but retain282/13 post-reset input differences (old270/10
unchanged). A separate delayed-second-Enter variation reaches MAIN at2343ms
versus source2751/original2341, with latch0 at both selection confirmations.
It has152 pre-change raw RAM differences, so it supports the diagnosis without
proving strict identical-state single-variable causality or timing parity.

Replay/producers/full key-event RAM: `.analysis/reconstruction/probes/dos-op-menu-input-v1444/`.
Use analyze.py and verify_result.py after selected retention/recover.py restores.
Four actual inner controls and the retained first-reader rejection replay pass.
No product source, exact unit or native branch changes follow from this probe.
Twenty-four aliases are recoverably retired in37 blobs (239.785 MiB net after
2.193 MiB archive);388 protected inputs and full temporary metadata restore pass.
replay_restored.py reproduces five analysis reports and the fresh route report
byte for byte, then verifies and retires aliases again. Full compressed RAM/
entry/DGROUP,1566-input source archive, products/MAPs and receipts remain live.

## Current four-source cold build and process route (v1443)

All four products cold-build serially from frozen3ca7b96 without requested
object caches. Fresh manifest is `.analysis/build/dos-four-products-v1443/build.json`:
MAIN778641ab, OP7ca38942, MAINE3b562840, ZUNd6043dce. MAIN reproduces the fixed
Continue product below; ZUN's two cold component/packing outputs agree. Own
MAPs/receipts live under product-20261016-065147-3427b48f-{main,op,maine,zun}.
These inputs exist independently of the missing historical worktrees.

New boundary original/source captures actually execute four ZUN4B00 entries,
initial OP4B00 and MAIN->MAINE->fresh OP->second MAIN4B03. Complete relocated
entry images/actual PCs, raw AX and full PSP/MCB/RAM agree with their own files.
OP's source counter hook comes from its own MAP0700:035B/DS0FF2, not original
0A74:0D2F/DS0F34. Parent PSP875/MCB874 anchors allocation walks.

The first MAIN7547 completed updates (plus unfinished final sample) and second
MAIN600 updates agree on consumed input/36 fields/ordered RNG, nine pools and
22 state blocks. Six resident256 samples and physical CFG/SCR agree. Aggregate
passed=false retains270/10 post-reset input differences. Candidate fresh menu
requires four confirmations/3345 emulated ticks versus original three/2338,
despite equal seed65. The earlier fixed three-pulse candidate never enters
second MAIN and remains rejected with its own278 first-MAIN input differences.
Do not call that earlier capture complete or diagnose a product bug from it.

Replay/source/recovery: `.analysis/reconstruction/probes/dos-four-product-route-v1443/`.
Boundary names: `dos-four-product-route-v1443-boundary-{original,candidate}`.
CI573,22 public tests,81 boot/cohort mutants and12 boundary mutants pass.
Thirty owned aliases are recoverably retired (304.902 MiB net,41 blobs).
Use retention/recover.py --restore --prefix for a specific capture, or
replay_restored.py for boundary restore/comparison/retirement. The restored
comparison reproduces the identical report digest and expected exit1. Full
compressed evidence, diagnostics, cold/current source, products/MAPs and
receipts stay live; missing old native trees are outside this cleanup.
The v1444 section above isolates the held-confirmation mechanism. Continue with
renderer costs, new-producer Demo pool/video comparisons, or native work in a
fresh attested checkout. Avoid
expanding control-plane tests as a substitute for source/runtime progress.
Full campaign, pixels, timing, native and exact acceptance remain open.

## Current Continue repair (v1439)

The natural Continue route exposed a real defect in the old f21a5c7c MAIN:
`_continues_used` occupied a separate byte before `_score`. Original target
MAIN0AAF:3CDA increments the score base at DGROUP(2134):4349. Actual admitted
routes first differed at frame 7548: original score0100000000000000 versus
candidate0000000000000000, despite both restoring lives/power. The refused
producer and complete negative are preserved; the new strict gate rejects it.

`src/main/score/state.asm` now aliases both publics. New MAIN is 200,279 bytes,
SHA-256 `778641ab845bcd67c6888bacc049e2cfa20fddda844681d3d2fd164f8386abc9`,
in `.analysis/build/dos-continue-alias-v1439/`. MAP/compiler receipt belongs to
`product-20261016-043629-1b1b2afa-main`. Verified unchanged objects plus fresh
changed ASM/link pass OMF/MZ/IRQ/switch gates. This is not a cold deterministic
exact replay. Historical exact MAIN's complete 438-input closure excludes this
product-only BSS owner, so accepted historical inputs/ledgers are unchanged.

New original/fixed candidate captures agree through 8,000 updates on consumed
inputs, all 36 fields/3,042 ordered RNG calls, nine full pools and 22 state blocks.
Natural Game Over/Continue at 7547/7548 restores lives 1->6, bombs 0, power 1 and
score counter 0->1; gameplay resumes and a seventh loss occurs. The no-video
companion retains 263 post-reset input differences. Fresh video also agrees
on all 38 regions at 8,000 actor-update checkpoints; its companion retains 281
input differences and raw GDC differs every frame. Intermediate Game
Over UI/wait frames are outside that boundary. All four Demo scalar/RNG
regressions pass 15,984 updates/four terminals. New-producer full Demo pool/video
acceptance remains pending; do not inherit older producer acceptance.
Replay and frozen sources: `.analysis/reconstruction/probes/dos-gameover-continue-v1439/`.
Root CI506/private gates passed for v1439. The later bounded Quit route is
below; complete resident lifecycle, full reconstructed process routes and
native/cross-emulator/Windows acceptance remain open.

## Admitted second-MAIN update comparison (v1442)

New `dos-second-main-updates-v1442-boundary-{original,candidate}` captures agree
through 600 second-MAIN actor updates on consumed input,36 fields/ordered RNG,
nine pools, 22 state blocks, terminal fields, six full resident samples and
physical CFG/SCR. Twelve complete RAM allocation checkpoints per side retain
resident MCB 9FEE/data 9FEF/owner FFFF. The first MAIN has 7,547 complete updates and
one unfinished pre-update sample. New Shot uses the actual first actor-update
boundary, not an entry-relative delay. The aggregate preserves291/24 post-reset
input differences. The earlier timed pair is not admitted (initial Shot 2000/0000,
post-reset292/17); its later pool differences are not a confirmed product defect.

Replay/source/recovery: `.analysis/reconstruction/probes/dos-second-main-updates-v1442/`.
CI 551, twelve public controls and 32 actual boundary controls pass; the earlier
reader failure and 27 timed controls remain. Two journals release 229.992 MiB net
from 24 owned aliases; full compressed streams, source/producers and MAIN/MAP
remain. The MAIN producer remains778641ab; supporting executables remain original.
No complete campaign, pixel, native, exact or physical timing claim follows.

## Paired resident ownership checkpoints and second MAIN (v1441)

The new original/candidate route executes MAIN Quit -> original MAINE -> fresh
original OP -> second MAIN. Four full load images are attested to their own
pinned files at actual 10FC:0000, retaining PSP 10EC. Ten complete conventional
RAM checkpoints per side verify resident MCB 9FEE, data 9FEF, 256 bytes, owner word
FFFF. This raw DOS field does not attest a live PSP FFFF or continuous lifetime.
Both actual second MAIN entries retain counter 70 after observed fresh menu 65.
The second MAIN has no admitted gameplay updates yet; supporting products remain
original and the MAIN producer remains 778641ab.

The first MAIN's7,547 complete updates plus unfinished final pre-update sample
agree on consumed input/scalar/RNG/pools/states. All 256 resident bytes agree at
five checkpoints. Physical CFG/SCR and all ten complete 16-bit checksums agree.
The new aggregate fails for 286 post-reset input samples, distinct from v1440's 284.
CI 539, thirteen public controls and 45 actual counterexamples pass. Replay and
frozen source: `.analysis/reconstruction/probes/dos-process-restart-v1441/`.
Restore route-retention aliases before the process-route comparator. Its verified
archive releases 96.895 MiB net from eight owned paths. Existing missing native
worktrees and94 protected files remain outside this cleanup.

## Actual bounded DOS Quit route (v1440)

Real original/candidate MAIN Quit -> original MAINE -> fresh original OP menu
now has three full-image/actual-entry observations with retained PSP10EC.
MAIN778641ab agrees on 7,547 completed updates, 7,548 pre-update samples,
consumed input/scalar/RNG, nine pools and 22 state blocks. The unfinished final
update is retained explicitly. The aggregate fails for 284 post-reset input
samples. All 256 resident bytes agree at four handoff/entry/menu checkpoints;
physical CFG and SCR agree, including all ten complete 16-bit checksums and
only decoded score section1 changed. Fresh OP's counter64->65 proves real use.

Replay and source archive: `.analysis/reconstruction/probes/dos-process-route-v1440/`.
Use `compare_th04_dos_process_route.py`; restore selected route-retention images
first. Root CI526 and 24 actual counterexamples pass. Supporting products remain
original, `natural_game_exit=false`, and resident allocation-owner MCB is not
sampled. Intermediate UI pictures, second MAIN and full reconstructed chain
remain separate requirements. Probe/route retention verifies 31 aliases and
releases 345.461 MiB net; missing old worktrees are untouched.

## Recorded results and open requirements

The following rows describe historical producers. They are not fresh replay
claims. Commands, evidence IDs and ownership are in the
[DOS differential note](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md),
[native status](PORTING_STATUS.md), `config/evidence.csv` and `config/knowledge.csv`.

| Extent | Recorded agreement | Open or failed requirements |
| --- | --- | --- |
| Four bundled Demos, 3,996 updates each | Consumed input, score/RNG, nine complete pools, 22 state blocks and every configured video region; Demo 1 divergence fixed | Physical scanout and full ordinary game |
| Ordinary Normal ReimuA, 3,996 updates, v1434-v1436 | Two independent pairs, 36 fields, 1,369 ordered RNG calls, natural deaths/respawns; all 38 v1436 video regions agree | Raw GDC timing differs every frame; v1436 companion aggregate fails for 155 post-reset input samples |
| Ordinary Boss prefix, 7,500 updates, v1437 | Consumed input, 36 fields, 2,837 ordered RNG calls, nine pools and 22 state blocks; Boss phases 0/1/2 and five natural losses | Aggregate fails for 258 post-reset input samples; no complete Boss pictures, defeat or campaign acceptance |
| Fresh ordinary Boss video, 7,500 updates, v1438 | All 38 full video regions, consumed input/36 fields/2,837 RNG calls, nine pools and 22 state blocks; independent no-video scalar controls | Raw GDC differs every frame; video companion aggregate fails for 253 post-reset samples, separate controls for 259; no defeat, natural exit or campaign |
| Native v1432 GNU / optimized UBSan | Easy ReimuA, Normal ReimuA, Normal MarisaA and Extra ReimuA unlocked by the same Normal save; complete logic/save agreement, mask=1, no Continue | Headless `render_every=0`; no complete original-picture, Windows input/audio, physical timing or original full-game acceptance |

Ordinary DOS pairs replace MAIN only; OP/MAINE/ZUN/assets/reset files remain
original. They do not validate a complete route through four reconstructed
executables. Post-reset differences 156/155/258 belong to v1435/v1436/v1437
respectively and must not be interchanged. Equal consumed inputs do not erase
intermediate input differences. New v1438 counts 253/259 belong to separate
video/control captures. Three pools staying empty in shorter prefixes
does not cover their active paths.

The Demo 1 frame-3343 divergence in old handoff `55cf73e` is resolved. Midboss
toggle, carpet columns, bullet invalidation dimensions, point-number glyph and
lighting-animation-cell fixes have separate cold-build evidence in the focused
note. Historical authored exact is 661/663: OP 93/93, MAIN 493/495, MAINE 72/72,
ZUN 3/3. MAIN's separate function-ledger denominator 494 is a different measure.
The two deferred carpet/checkerboard exact cases remain deferred.

## Next tasks

1. Resolve v1453 complete RGB failures at9284,9349,9600,9700. All59 active
   TRAM samples and selected9835 ordinary updates pass. The first two failures
   include substantial graphics differences;the last two differ407 pixels,
   matching the independently measured blink footprint. Record the actual native
   clock/writers and compare captured original GDC phase without fitting it.
   The former seven v1451 failures are repaired in v1452;do not restart that
   finished circle investigation or revive the refuted constructed BB Oracle.
2. The v1443 four-source nine-entry/second-MAIN extension and fresh native
   recovery are completed bounded steps. Continue DOS OP renderer/readiness
   diagnosis or new-producer Demo pool/video checks; retain post-reset/raw-GDC
   failures and the unfinished first-MAIN sample. Missing old native94 files
   and old candidate MAPs remain historical gaps. Use the new attested native
   producer; never re-sign old receipts or recreate missing frozen directories.
3. Extend the primary original/reconstructed DOS comparison beyond8000
   updates and route native beyond the newly accepted9835 selected updates only
   after addressing the retained pictures. Use each candidate's own MAP/CS/DS
   and explicit STD/Continue/post-Boss waits. Native Stage2 update9836 is outside
   the current comparison. Preserve raw-GDC/process failures and missing old
   producer gaps;do not re-sign original addresses onto a reconstructed MZ.
4. Align native state/effects using identical consumed inputs and explicit
   state boundaries: original DOS, reconstructed DOS, then native. Expand game
   area checks to HUD/page changes/text/palettes/full pictures. GNU/UBSan equality
   and old 40-area samples do not prove original full-picture agreement. Modify
   source for reproduced differences or a concrete ownership requirement.

The observed original Game Over stack is relative MAIN `0AAF:3B1E` to
`130E:0149` input_wait release loop to `130E:00E3` frame_delay(1). The actual
far wait call is `0AAF:3B19`. Historical v1437 bounded terminal is relative MAIN
`0AAF:01B3` at load `10FC`; GDB flushes and kills that capture. Its
`natural_game_exit=false` is intentional and must not become a natural-exit claim.

Native save admission requires all ten complete 16-bit section checksums,
character/rank/shot partitions, `mask < 4` and the selected shot bit, plus Ending,
stage coverage, registration/fresh OP. The older window/UBSan Normal claim with
sentinel `0x19` remains revoked; newer headless results do not restore it.

## Historical replay identities

| Evidence | Root-relative location |
| --- | --- |
| v1437 reports/controls/recovery | `.analysis/reconstruction/probes/dos-ordinary-boss-v1437/` |
| v1437 final captures | `.analysis/runtime/candidates/dos-ordinary-boss-v1437-{original,candidate}-7500/` |
| v1436 video | `.analysis/runtime/candidates/dos-ordinary-video-v1436-{original,candidate}/` |
| v1434 independent plain baselines | `.analysis/runtime/candidates/dos-clock-input-v1434-v8-{original,candidate}/` |
| Pinned observer receipt | `.analysis/runtime/emulators/demo-observer-build-v1365/receipt.json` |
| Native v1432 root reports | `.analysis/reconstruction/probes/native-natural-clear-v1432/` |
| New v1438 work | `.analysis/reconstruction/probes/dos-boss-video-v1438/` |
| Current Continue repair/regressions | `.analysis/reconstruction/probes/dos-gameover-continue-v1439/` |

Historical v1437 ordinary MAIN is 200,279 bytes,
SHA-256 `f21a5c7ca38ebaee0e0ae544540ed2c36b4429cd846c3a12d8a5ccb887728cd8`.
Its missing build directory is
`.analysis/worktrees/dos-smem-page-copy-v1423/.analysis/build/smem-page-copy-v1423/`.
Its MAP was that tree's
`.analysis/reconstruction/probes/product-20261012-005819-ac6f4873-main/source/obj/main-native.map`,
SHA-256 `2b6a74a073f98a2b53ab9583ad1bfee5775886b8954240b1efab2c5d089bdf59`.
Old root `.analysis/build/th04` or `th04-normal` is not this producer.

Native frozen C++ producer is `554/31e6b3d7...`, reader consumer
`554/a79f199f...`; full digests and the 553 unchanged-input contract are in
[the route note](reconstruction/product/TH04_NATIVE_NATURAL_ROUTES_V1432.md).
GNU/UBSan executables were in the missing `native-main-pause-v1431` tree under
`.analysis/port64/native-main-pause-v1431-v5/`.

Only after finding and verifying the original MAIN/MAP and restoring required
raw/image aliases may the historical complete comparison run:

```sh
taskset -c 1 nice -n 19 python3 scripts/probes/compare_th04_bounded_ordinary.py \
  .analysis/runtime/candidates/dos-ordinary-boss-v1437-original-7500 \
  .analysis/runtime/candidates/dos-ordinary-boss-v1437-candidate-7500 \
  --original-main .analysis/targets/th04/main.exe --output /tmp/th04-boss-prefix.json
```

Expected exit 1 means scalar/pools/states agree but 258 post-reset samples differ.
A missing-file error is not that expected result. Use a receipt-verified frozen
source snapshot if old source hashes differ; never re-sign the historical producer.

## Resource, cleanup and finish rules

Use CPU 1 / nice 19 for heavy work and serialize Borland/Wine builds. Keep runs
muted and headless or on private Linux Xvfb. Do not open Windows GUI, take focus
or inject host keys. The initial root analysis footprint was about 6.3 GiB;
missing worktrees do not count as verified reclaimed space.

Keep scratch/generated files in fresh `.analysis/` namespaces and retain failed
producers. Clean only this session's explicitly owned, recoverable intermediates.
Before deletion verify archive SHA/CRC, complete reconstructed contents,
restored mode/nsmtime and protected files. Never delete all analysis, old trees
or all builds. Keep complete compressed streams, inputs, compilers, receipts,
source snapshots and required MAPs.

Use each v1437/v1436 `recover.py --restore --prefix PATH` selectively. v1434 has
its own `recover.py`; its old `verify_retention.py` points at a superseded full
archive. Native v1432's protected-file check currently fails for 94 files; its
archive cannot restore the entire tree. Return temporary aliases to archived
state after use and do not count that as new cleanup. The prior audit checked
24/8 v1437/v1436 archived paths without expanding large files.

v1438's own `recover.py` checks/restores 16 image/font/raw paths in 24 blobs.
Verified full content/CRC/temporary mode/nsmtime and protected-file checks release
194.625 MiB net with a 1.069 MiB archive. Complete compressed streams, new
MAIN/MAP, receipts, source and failed publication evidence remain live. Its
video comparison exits 0; its companion comparison exits 1 for 253 input samples.
The initial post-extension CI passes 495 public tests plus private target,
database and Oracle gates. Native CI was not rerun in the missing trees.

v1439 archives 24 image/font/raw aliases in 37 blobs, releasing 300.207 MiB net
with a 2.229 MiB archive after complete content/CRC/temporary mode/nsmtime and
protected checks. Complete compressed 8,000-record DGROUP/video, refused/fixed
MAIN/MAP, compiler/source and all failures remain. Use its own `recover.py`
selectively; its full video comparison exits 0, video companion exits 1 for 281
input samples, no-video companion exits 1 for 263, and Demo scalar comparison
exits 0. Root CI 506/private gates pass. Historical exact inputs/ledgers stay
unchanged; both development goals remain active.

After shared headers/flags/segments/link order/layout changes, invalidate and
cold-replay affected accepted units. Source recovery, runtime agreement and
historical exactness are separate claims. Finish with the focused comparison,
`taskset -c 1 nice -n 19 python3 scripts/ci.py` and `git diff --check`. Update
README, RE_HANDOFF and the existing focused note when evidence changes. Verify
no original programs/assets/private archives/credentials are staged. Commit
messages require the `gpt-6.1-sol: ` prefix; commit/push each changed branch and
verify remote heads. Keep the full goal active while required work remains.

## Ready-to-use agent instruction

Continue TH04 reconstruction and port64. Read this handoff and AGENTS.md; verify
both remote branches, pinned targets and actual local files. Recover missing
producer inputs or create new attested builds without rewriting historical
receipts. Complete a bounded Boss-picture or Game Over/Continue differential
against original DOS, reconstructed DOS and eventually native state/effects.
Preserve input/GDC failures and the two deferred exact cases. Use one low
priority CPU, muted Linux headless runs and explicit recovery-verified cleanup.
Update evidence/status, run CI/diff checks, commit with `gpt-6.1-sol: ` and push.
