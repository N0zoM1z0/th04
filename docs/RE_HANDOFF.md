# TH04 native branch handoff

## Native MAIN pause, resume and Quit (v1431)

Ordinary MAIN Esc now enters its pause menu. Actors, stage, player resources,
score and RNG remain suspended while IRQ/audio/text blink service continues.
The original three gaiji labels at26:12/14/15 and their C1/E9 attributes are
retained. Up/Down toggles once per release/press; Esc selects Resume, Z/Enter
confirms, and Q returns Quit immediately without the three space erasures.
Other confirmations wait for final release and erase four ANK cells per row.
The completed pause returns latched keys and unused time. The caller resumes
its suspended frame once; Quit publishes run state and returns to fresh OP,
with released MAIN resources and a clean second MAIN. Pause Esc is consumed
by that menu and is not requeued as a new pause after Resume.

Original MAIN DEMO_TEXT0AAF:07DF..08FD (load0B2CF..0B3ED,287 bytes), full
input_wait130E:0133..0186, frame_delay130E:00D7..00EB and VSYNC_WAIT0000:2462..
2487 execute with legal MZ relocations/DGROUP2134 at loads1000/3333.
Initial/final busy reset-sense loops sample immediately then at explicitly
chosen counted-edge observation points, without clearing Count1. Those points
are keyboard/CPU cadence adapters, not measured polling costs. Menu waits
preserve actual Count1-only clearing and pre/post OR. Physical CPU, keyboard,
active-PMD timing and full-game paired acceptance remain open.

Cold554/31e6b3d7 GNU Release and optimized UBSan/bounds each build84 programs
and pass82 CTests. Each agrees with768 original controls and
384 coarse plus384 one-ms partitions on complete events/keys/
counters/time/selection/result/latch streams. Eight actual frontend routes per
compiler cover both characters and Esc/Z/menu-Quit/Q, actor/score/RNG freeze,
raw menu TRAM, resource release/fresh OP/second MAIN.16 original putsa/putca
controls at loads1000/2000 validate all12 occupied menu cells' code/attribute
words per compiler; other cells and full graphics are outside that check.
Each ordinary SDL/private TCP-disabled Linux Xvfb run additionally exercises
Esc/Z Resume, Q Quit and second MAIN, with read-only traces and zero audio
opens. No actor/hit/score/clock writes or Windows focus/input are used.
Four compiled mutations reject cancel-as-Quit, Q erasure, skipped release and
stale live key_det; unchanged compiled control passes.

Retained dev384-control failure differed only in live key_det during waits;
reset-sense and OR-sense now update that observable field before STOP. The
first actual fixture wrongly started from missing/setup CFG; a valid encoded
configuration fixes its own entry. A dummy-video window probe and later real
SDL Esc requeue failure remain distinct. Compiler namespace failures and all
source/program/trace evidence are retained. Prior UBSan Normal-clear acceptance
stays revoked:0x19 is an unplayed sentinel after a failed survival route; this
batch does not retry or promote that full-route claim.

Replay: `.analysis/reconstruction/probes/native-main-pause-v1431/`;
producer: `.analysis/worktrees/native-main-pause-v1431/.analysis/port64/native-main-pause-v1431-v5/`.
`verify_main_pause.py` owns original controls; `window.py` owns private SDL keys.
Content/CRC/mode/nsmtime/temp-restore retirement saves256.67 MiB net.
Source/all programs/fixtures/receipts/failures remain live or losslessly recover
with `verify_retention.py --restore --prefix`. Full goal stays active; broader
Boss/death/process parity, unowned score RAM, other waits, physical scanout and
Windows remain open. Historical exact stays661/663.

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
