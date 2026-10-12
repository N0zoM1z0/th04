# TH04 native MAIN pause ownership

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

Published native head: `853e012509849ae2f218972594e67eb6fd591ceb`.
