# TH04 native branch handoff

## Ordinary native dialogue and Boss prefix (v1446)

Source `13e6676` preserves Stage1's gameplay input across blocking dialogue
refreshes. Target MAIN `0AAF:00F1` calls player_update at `0AAF:5FCF` before the
Boss callback through `DGROUP 2134:432C` at `0AAF:0113`; load `10FC` is recorded.
The executed predecessor consumed 0 at update 6548 instead of original `20h`.
Its 21 selected fields and nine pools still matched: the held-shot interval
made this input error invisible to that earlier comparison. The fixed real
FrontEnd retains the selected gameplay key/Shift while dialogue owns its
separate release/Enter samples. It does not edit game state or original captures.

Fresh source closure of 557 files (d246f71f) builds 85 GNU programs, passes 82 CTests and
also builds an optimized UBSan core/game. The ordinary Normal/ReimuA seed64/lives6/bombs0 comparison
now covers 7,500 completed updates and 7,501 boundaries through real dialogue and
Boss phases 0/1/2: actual gameplay inputs, 21 fields/full RNG state and counts,
nine complete pools, and four complete Boss blocks (45 bytes, including spare
state bytes) agree with original DOS. Dialogue has 803 frozen admissions and
804 advances under declared component keys; these are not original timing.
Five natural losses end with one life. Native initialization uses an explicit
OP counter of 64 and menu API; natural startup/input delivery is not accepted.

Public replay: native port64/verify_ordinary_state.py --frontend --updates 7500
with --dos-root, --original, --exe and a fresh --output-dir. Canonical proof/source/recovery:
`.analysis/reconstruction/probes/native-ordinary-front-v1446/`. The writable
native tree remains `.analysis/native/port64-recovery-v1445/`.
Intermediate dialogue/player-prefix pictures, remaining globals/Game Over/
Continue, Boss defeat, whole routes, scanout/timing, Windows and historical
exactness remain open. Next extend the actual FrontEnd through Game Over and
Continue using original captured inputs and separate blocking-owner evidence.

Eight actual reader controls pass, including independent sampled-input/Boss
mutations and strict default/configured extents. Compiler dependencies cover 350
actual own files; fresh GNU core and ymfm archives equal v1445 byte for byte.
Verified archival retires 249 owned files in 244 blobs, releasing544.664 MiB net
after a 9.607 MiB archive. SHA/CRC/mode/nsmtime and 2,296 protected hashes pass.
Restored predecessor/fixed prototype and current GNU/UBSan FrontEnds reproduce
the complete 7,500-update outputs; only the predecessor repeats its actual-input
failure. Two restored executable aliases retire again; six borrowed original
aliases return to their older archive state without counting as new cleanup.
Current GNU cache/85 programs, selected UBSan game/libraries, all sources and
complete original/current compressed captures remain. Use recover.py and
replay_restored.py in this batch's namespace. The active retirement log is
explicitly excluded until the final closure; no journal/log receipt is restamped.
Missing old 94 files remain a separate historical gap.

Cold C++ producer13e6676 remains557/d246f71f. Current Python consumer48db31c
is557/7c4b8576: only verify_demo_pools.py restores the default Demo truncation
diagnostic after the first native CI found its message regression. All350
compiled own inputs and cold executables are unchanged. Fresh separate GNU/
UBSan consumer replays and eight current-reader controls reproduce all admitted
results. The first failed CI and every old producer/runtime receipt remain
unchanged; current-consumer.json and consumer-replay.json bind both identities.

Final gates pass: root CI573 with live MAIN database and Ghidra mutation
checks, native CI354, and both tracking/diff checks. Native private Ghidra is
skipped because this checkout has no project; the actual database replay is
in the DOS root. Keep the initial native message-regression CI as a negative.

## Ordinary MAIN collision-latch publication (v1445)

Source8a2092b fixes an observable shared-hit latch: collision owners previously
fed Lifecycle only at the next player prefix, which immediately consumed the
flag. Original MAIN DGROUP2134:4669 (load10FC) was1 at before-update3078/3284,
while native life().hit was0. Publish pending collisions before completed-frame
observers/rendering. Existing next-prefix consumption remains; death timing and
all nine pool streams were already equal in the predecessor.

Fresh cold GNU85 programs/82 CTests and optimized UBSan entire-core/ordinary
tracer pass the original Normal/ReimuA seed64, lives6/bombs0 component:3996
complete updates,3997 before-update/prefix boundaries,21 fields including full
LCG/ring bytes and post-initialization draw counts, and nine complete pools.
Two natural deaths/respawns end at lives4. GNU/UBSan state and pool outputs are
byte-identical. Fresh cold c0a1060 is retained as a compiled negative: only the
two hit fields fail, with all nine pools equal. Seven actual reader controls
reject malformed prefixes, fake Demo terminal, wrong hit/resident/RNG data and
an inactive pool byte. Four-Demo old/new native regression is byte-identical
at15988 boundaries; this does not renew original Demo/picture acceptance.

Current source closure556/49984d82 and all new proof files are independent of
the missing old worktrees. The writable checkout is the DOS root's
`.analysis/native/port64-recovery-v1445/`; canonical proof lives at DOS-root
`.analysis/reconstruction/probes/native-recovery-v1445/`, also symlinked below
this checkout. Native CI354 passes with borrowed target files and the pinned
ReC98 Tupfile as a read-only CI Oracle; native compilation completed without
that reference directory. Root CI573/live MAIN Ghidra replay/mutations pass.
Historical native paths/94 protected files remain missing; do not restamp their
receipts or claim this new producer restores their complete replay.

Use port64/verify_ordinary_state.py with the current DOS checkout's original
route readers, a restored original capture and the newly built ordinary tracer.
The native start is an explicit typed component fixture, not a naturally timed
native OP route. Other globals, dialogue/Boss/Game Over, full pictures, broader
campaigns, physical timing, Windows and historical exactness remain open.
Continue the ordinary comparison through actual FrontEnd blocking owners.
See [the focused lifecycle evidence](port64/evidence/stage-lifecycle.md).

Verified retention retires742 owned files into619 content blobs, releasing
245.527 MiB net after a13.660 MiB archive. Full SHA/CRC/mode/nsmtime checks
and3087 protected hashes pass. Restored four ordinary component executables
and both native Demo executables reproduce complete retained outputs and
pool digests; nine owned aliases are verified and retired again. Six borrowed
original aliases return to their older archived state and are not counted as
new cleanup. Current GNU programs/cache and selected UBSan programs remain.
The first journal bound a still-empty redirected log and correctly rejects;
its bytes and reader remain unchanged. A distinct retention-final.json and
recover_final.py bind the closed terminal log. replay_restored_v2.py also
restores borrowed original aliases and requires the identical first replay
report, so the recovery is repeatable. Historical missing94 files remain open.

## Historical native natural routes and strict clear gate (v1432)

The route reader now requires the requested character/rank/shot partition's
actual physical clear mask below4 plus its shot bit, all ten full16-bit score
checksums, complete stage coverage, correct Ending and registration/fresh OP
without Continue.0x19 and high-bit masks remain unplayed even when bit0 is set.
Easy's five-stage Bad Ending and Extra's separate stage6 process are checked
against their own extents; Normal requires six stages and Good Ending.

Current unchanged cold554/31e6b3d7 GNU and optimized UBSan each pass
Easy ReimuA, Normal ReimuA, Normal MarisaA and earned Extra ReimuA. All use
ordinary key-only advice in Mode::ordinary, legal six-life/two-bomb setup,
physical configuration/scores and no actor/hit/life/score/stage/clock writes.
Extra starts from the same-run Normal-earned file in a new process. Each route
has clear mask1 and returns to fresh OP, with no Continue. GNU/UBSan complete
key/19-field MAIN-state/startup/menu/capture and save files agree for all four routes:
72434, 88914, 79214, 29611 admissions, 270,173 per compiler.
These are logical headless routes with render_every0 and retained checkpoints,
not complete pictures, original full-game parity, OS delivery or timing claims.

The executed consumer is554/a79f199f. All553 other maintained inputs,
including every compiled source/header/CMake input and the C++ route helper,
match the frozen producer. Only verify_natural_routes.py changed; no C++ build
or parent producer restamp. The reader explicitly records both identities and
rejects compiled-input differences. Nine public tests and a real complete
Normal trace/file control plus six full-checksum-valid counterexamples reject
missing/wrong-shot/sentinel/high masks, Bad Ending and omitted stages.

Prior failed UBSan/window Normal acceptance stays revoked in its own producer
scope. Current headless GNU/UBSan clear evidence is new and separate. Broader
shots/ranks/death/Continue, original/reconstructed DOS/native campaign parity,
full pictures, physical CPU/I/O/scanout, active-PMD timing and Windows remain
open. Historical exact stays661/663; full reconstruction/migration is active.

Replay: `.analysis/reconstruction/probes/native-natural-clear-v1432/`;
results: `.analysis/worktrees/native-natural-clear-v1432/.analysis/port64/native-natural-clear-v1432/`.
The frozen programs remain under `native-main-pause-v1431-v5`. `comparison.py`
verifies all complete captures and saves; `mutations.py` owns actual-file
counterexamples. Verified content/CRC/mode/nsmtime/temp-restore retirement
saves81.78 MiB net; route/state/input captures recover with
`verify_retention.py --restore --prefix`. All source, programs, saves, plans,
receipts and archive remain retained. Continue paired ordinary-game behavior.

## Native elapsed registration and all three callers (v1428)

Actual registration now uses shared elapsed Animation for black-in2,
input_wait0 and black-out1, and live Count1-only frame_delay1 for editing.
Alphabet/cursor and accepted command drawing precede keyboard reset. Sense
ORs the pre-wait and post-wait samples; BYTE repeat keeps its30/even/wrap rule.
File operations are consumed one at a time, with writer-close before free/
clear/fade. A failed host operation freezes the scene and Score/Extra parent;
later admissions neither retry I/O nor advance registration ticks/RNG/route.
The outer clock can continue. Successful completion returns unused time.

Normal Ending begins registration on its delay100 completion admission;
Score and Extra pass time directly to registration and then verdict or
Congratulations. Clock/audio service occurs once, and new process counter BSS
keeps raster phase. Legacy no-clock helpers remain separate logical models.

Pinned MAINE decoded0A05:27C4..2B5F menu, score0A05:20F9..24B5 and process
RNG0000:1C5A..1C83 execute unchanged. Fades0000:0622..06A3, frame_delay
0CC7:0033..0047, input_wait0CC7:020A..025F and full0000:2206..222B wait execute
with DGROUP0E53/live0EFA/0EFC/0F02 and ideal IRQ at loads1000/3333.
The62414-byte decompressor payload/559 relocation observations retain their
candidate-derived container topology gap; target canonicality remains
candidate-local-attested. Graphics, keyboard, successful file/sound have
guarded ABI seams; CPU/I/O/audio/loader costs and physical scanout are unmeasured.

Cold545/b4519b50 GNU Release and optimized UBSan/bounds each build84 programs
and pass82 CTests. Each agrees with544 original controls and272 coarse plus
272 one-ms partitions: full E/K/palette/edit-loop/file/RNG/counter/time streams,
ranked/unranked/Extra, WORD wrap/carry skips, held-repeat BYTE wrap, chords,
missing/partial/corrupt file recreation and blocked input. Each actual frontend
passes24 score-return routes/four writer failures,30 seeded saves/restarts,
8 Extra actor-control routes and24 Ending-to-registration/fresh OP/second MAIN
routes. Independent checks retain576 Ending pages/288 original-DAC RGB frames
and48 pages each for Staff/verdict/Congratulations. Existing432 Game Over and
576 MAINE controls pass. Eight default Demo profiles preserve129 prior hashes
each, original selected states and GNU/UBSan parity. No general-game or exact
promotion follows; historical exact stays661/663.

Compiled actual Scene fade-counter clear, pre-draw reset and lost-remainder
mutations reject whole original streams; unchanged compiled control passes.
Native CI345 passes. First probe omitted constructor tone0 palette-show; its
short137 input also let zero HI pass checksum after an empty read, producing
invalid numeral indices rejected by the native renderer. Original core/control
continued with drawing as an adapter; actual unsafe drawing is unmeasured.
This remains an explicit renderer/input boundary, not accepted equivalence.
Valid partial and corrupt selected sections separately recreate and pass.
Second development passed272 controls but the failed Score owner threw on its
next elapsed admission; the new frozen failure matches the retained native
no-retry policy. All failed source/program/trace/journals remain distinct.

Replay: `.analysis/reconstruction/probes/native-registration-elapsed-v1428/`;
producer: `.analysis/worktrees/native-registration-elapsed-v1428/.analysis/port64/native-registration-elapsed-v1428/`.
`verify_registration_elapsed.py` owns full original/candidate streams;
`focused.py` owns actual parent routes and image commands. Verified journal/
SHA/CRC/content/mode/nsmtime/temp-restore retirement saves2435.09 MiB net,
plus42.04 MiB from three preliminary caches. Source/all programs/
fixtures/receipts/failures remain live; archived raw aliases/captures restore
with `verify_retention.py --restore --prefix`. Stage reader is under
`native-registration-stage-retention-v1428`. Only owned intermediates retired.

Other wait owners, malformed-score unsafe graphics, real active-PMD paired
timing, physical CPU/I/O/scanout, broader gameplay and Windows remain open.
Continue source recovery and migration; the full goal stays active.

## Retained native producer routing

Earlier Cutscene, Staff, MAINE, Demo, palette, IRQ and text producers
retain their original source/evidence identities. See the [VSync note](reconstruction/product/TH04_NATIVE_VSYNC_V864.md), [porting status](PORT64.md), and the subject index. Prior handoff detail remains in Git;
current open owners are listed above. Archives restore into fresh paths.

## Comparison priority for the next agent

The user's primary comparison is **original Japanese DOS versus reconstructed
DOS**, both through the PC-98 game route. Native x64 must also preserve gameplay
state and effects. Native-host equality and successful native clears do not
replace either comparison. Start with the four bundled demos, then bounded
recorded ordinary play; compare score, consumed input, RNG and actor state at
the same logical boundary, followed by VRAM/palette/effects and process/save
transitions. See [paired demo evidence](port64/evidence/demo.md).

TH08 is a read-only workflow reference, not TH04 evidence. Its active worktree
is dirty; do not edit it, run its builds, change its database or launch its game.
Complete trace/end/input-consumption guards and first-divergence diagnostics
are the useful parts to adapt. Retained DOS demos accept complete selected scalar/pool/video comparisons.
Retained native producers accept selected scalar/RNG/count fields and nine
complete pools. v1385 preserves the six parent trace/save hashes and 40 entire
index/TRAM samples; whole pictures, original display epoch and broader
gameplay/process routes remain open.

## Replay and finish

```sh
python3 scripts/preflight.py
python3 scripts/ci.py
git diff --check
```

Use [status](PORT64.md), [host-window evidence](port64/evidence/host-window.md)
and [retention](ANALYSIS_RETENTION.md). Source/program/profile archives retain
producer identities; restore into fresh paths. One Borland/Wine writer at a
time. Never open an audio backend/device in these validations.
