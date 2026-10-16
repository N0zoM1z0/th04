# TH04 native branch handoff

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
