# TH04 native VSync interrupt owner

2026-09-27 product-build investigation. `src/shared/hardware/vsync_irq.asm`
owns `VSYNC_START`, `VSYNC_END`, `_vsync_Count1`, `_vsync_Count2`, and
`_vsync_Proc` for the TH04 product build. Its far Pascal entry points install
INT 0Ah and INT 18h handlers through DOS, preserve the original vectors and
PIC mask, reset both frame counters on start, and restore vectors and the
original VSync mask bit on end. The IRQ handler uses DGROUP, updates the two
volatile counters, calls an optional far Pascal callback, acknowledges the
PIC, and retriggers PC-98 VSync. An INT 18h wrapper retriggers VSync after CRT
BIOS calls. PC-9821 mode query sets the 31 kHz carry-delay value; this
hardware path is reference-corroborated and untested at PC-98 runtime.

The bounded historical `vsync.asm` and the TH04 frame-counter call sites
corroborate the required mechanism and ABI. The maintained implementation is
a TH04-local owner; it is not a target byte claim. Its INT 0Ah handler and
INT 18h wrapper are in code memory so they can run with an arbitrary caller
DS. `_vsync_Count1` is a DGROUP word at calibration MAP `0E9B:04F0`.

`scripts/probes/probe_th04_native_vsync_runtime.py` assembles the TH04 owner,
compiles a small TC4J caller, links with pinned Borland system libraries, and
runs under pinned MS-DOS Player. The v2 receipt SHA-256 is
`d5ec4c50767d9504ad4f88643f81128ff0113409fc5a4a6e77345766a9f66aa4`.
It exits 0 with `VSYNC_PASS`: manually triggered INT 0Ah increments both
counters and invokes the far callback; repeated start resets counters without
stacking a second hook; end and repeated end restore both vectors. This is a
DOS vector-lifecycle observation. It does not exercise a real PC-98 VSync
signal, GDC frequency detection, or hardware interrupt timing.

Two cold no-archive MAINE builds compile 120 TH04 units (77 C++, 43 ASM),
leave 15 unresolved symbols, and report zero warnings. Their link-relevant
and timestamp-normalized OMF records agree; only BGIMAGE shows its known raw
timestamp drift. Receipt SHA-256 values are
`6d2b02015416820cc0ca2a80d0727c47d8288cdc47f680ba66937e6118f5fb22`
and `b108087801bd3cba10fe72fd077a86334e98b8ba26f0e51037a9a6dfa364f1c4`.
The source manifest SHA-256 is
`fa25d59bbac41d0a86b50682ac40335d790a1b05a22a39826afe2b71df9176ae`.

The historical-library calibration TLINK exits 0 (receipt
`e5502df7d7afcac04ba7ee07572050302cb946379990352ec06c483e071003ce`)
with the known archive-dictionary warning. Its MZ validates 604 relocation
sites at two DOS load segments (receipt
`2753088f52f2e609a5b29f83618dd84299d69dcd3be740fb71870fe9f77ef287`).
The call ABI audit checks 29 far returns, 110 relocated direct far calls,
and one same-CS `push cs; call` (receipt
`7d02903eb0be86bbe04d42e96fb213387bd7c389e37f56cf2cb41aeef36ebdb4`).
At calibration MAP `0957:43FE` and `0957:44CD`, `VSYNC_START` and `VSYNC_END`
both return with `RETF`; the calibration addresses are not target addresses.

The no-archive link still needs text gaiji (3), sprites (3), sound (4),
packed-file service (3), and packed graphics (2). The calibration MZ still
contains historical support and has not reached MAINE under PC-98 runtime.
Before treating VSYNC as runtime-accepted, use an actual PC-98 scenario that
checks counter cadence, optional callback behavior, BIOS INT 18h gaiji calls,
and vector/PIC restoration on exit.

## Semantic timing and joystick contracts

The semantic/readable input/timing batch names the existing PIC ports and mask
bits, DOS vector requests, PC-9821 mode selectors and the unsigned fractional
cadence accumulator. Repeated START resets both counters and cadence state
before checking whether it already owns the hooks. The saved mask stores the
original VSync bit with ones in other positions, so END's AND preserves the
current other mask bits; it also serves as a nonzero ownership sentinel.
An accumulator carry skips both logical counters and the callback but still
acknowledges and rearms the interrupt. A callback with segment zero is disabled
regardless of its offset. These explanations follow the maintained native
owner; the physical 31 kHz timing path remains separately unobserved.

frame_delay resets volatile unsigned Count1 and spins against a signed 16-bit
argument using the original DOS promotion rules. GDC polling instead finishes
an active blank and waits for the next blank, without resetting either IRQ
counter. The two services must stay distinct in a portable implementation.

The adjacent joystick owner now names register selection, busy polling,
controller action bits and the bounded 256-attempt board detection. JS_SENSE
returns a fresh active-low sample in AX; it neither tests js_bexist nor stores
js_stat. The input sampler owns the presence check and action merge. JS_END
flushes DOS keyboard input and leaves the presence word unchanged.

Baseline and two fresh assemblies preserve complete link-relevant OMF records
for input_s.asm, joystick.asm and vsync_irq.asm. Control:
`.analysis/reconstruction/probes/semantic-input-default-v1234/receipt.json`.
This is compiler preservation; its COMENT exclusion is not raw object equality
or a new target-exact claim. The existing DOS VSync lifecycle probe is the
bounded callback/counter/vector control, separate from PC-98 cadence.

A rejected TC4J control replaced the GDC status literals with function-local
enum constants. It omitted two `mov ah,0` instructions, reducing VSYNC_WAIT
from 25 to 21 bytes and shifting later CS/relocation layout in all three native
products. Naming those values with literal macros retains the preceding
expression form. Do not assume an enum substitution is byte-neutral just
because its numeric value and C++ behavior agree. Reports:
`.analysis/semantic-input-v1234/enum-negative-control.json` and the three
`ARTIFACT.EXE-compare.json` files. This rejection does not promote normalized
or semantic equivalence to raw equality.

The final existing DOS lifecycle replay passes at
`.analysis/reconstruction/probes/semantic-vsync-runtime-v1234/receipt.json`.
The literal-macro build preserves all three complete native MZs and their
ordered relocations; see the [input/timing result](../packed/TH04_SHARED_INPUT_WAIT_V565.md).

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

## Native MAINE delay and black-fade boundaries (v1413)

Isolated native producer 530/96e2008a restores shared Animation's logical
WORD parameter boundaries. A zero frame_delay continues on the same call;
negative arguments become unsigned WORD waits. Black fades align once, then
use signed WORD speed: nonpositive values skip all per-group waits. The
optional PaletteSink reports every fade-generated palette_show, including
all 18 updates on one admission for zero speed. Explicit tone requests stay
in RequestSink. This is a logical refresh projection, with no shared Count1
owner, CPU execution cost or elapsed raster/IRQ timing claim.

Both cold GNU and optimized UBSan/bounds build all 80 programs and pass all
78 CTests. Complete original MAINE 0CC7:0033..0047 frame_delay and
0000:0622..06A3 black fades pass 72 cases at loads 1000/3333; the actual
0000:2206..222B wait executes inside each fade. Count1 pulses are explicit
stimuli and palette_show is a guarded tone observer. All 36 native vectors
match, including WORD truncation, zero and 7FFFh/8000h boundaries.

The actual 9a7f380 Animation predecessor differs in all seven complete
boundary traces. Current Congratulations retains 32 original branches,
50 original fade/key clocks and 20 complete PI-page comparisons per compiler;
verdict retains 916 state/request cases and 10 clock/key controls. Their
pixel references retain their earlier native decoder producer. Eight muted
startup/four-Demo/fresh-OP routes retain all 129 prior hashes per profile and
15,988 original selected-state boundaries each. No exact/full-game promotion.

Replay: `.analysis/reconstruction/probes/native-maine-animation-v1413/`;
producer: `.analysis/worktrees/native-maine-animation-v1413/.analysis/port64/native-maine-animation-v1413/`.
`focused-gnu.json`, `focused-ubsan.json` and `focused.json` record commands.
Use `th04-port64-cutscene-contracts` for Congratulations/verdict helpers;
frozen port readers need read-only `PYTHONPATH=ROOT` for the HDI parser.
Failed missing-parser/wrong-program recipes remain. Verified retirement
reclaims 505.69 MiB net; full source/projections, selected programs and
predecessor remain. Continue actual elapsed scene wait ownership; physical
timing, complete pictures, broader Boss/death/process and Windows stay open.

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
broader Boss/death/process, native LCD mapping and Windows remain open.

## Native elapsed MAINE consumers (v1423)

Development remains active. Verdict and Congratulations in normal Ending,
Score and Extra now share the live raster/IRQ counter owner. Their black
fades, WORD frame delays and signed input waits consume elapsed time rather
than host repaint counts. Initial fade alignment keeps Count1; delay clears
only Count1. Input release combines samples before and after the wait;
negative timeouts still release first, while zero and 9999 repeat the press
wait. A completed child returns unused time to its parent. The registration
entry delay 100 starts at the actual child completion. New MAINE/OP processes
reset counter BSS while retaining raster phase; clock and audio advance once.

Final union retains analog/LCD palette output, indexed Demo entry and the
original WORD Demo blackout with all18 palette publications and19 tone stores.
Cold producer 540/bc9bb404 builds all 84 programs and passes all 82 CTests
under GNU Release and optimized UBSan/bounds. Each compiler agrees with 576
complete original MAINE fade/delay/input controls at loads 1000/3333 and 288
coarse plus 288 one-millisecond partition vectors. The original key and
palette calls use guarded adapters, with independent ideal IRQ stimuli;
physical CPU/I/O/ISR latency is not measured.

The attested original entries are MAINE 0000:0622/0666 (black fades),
0CC7:0033..0047 (frame_delay), 0CC7:020A..025F (input_wait), and
0000:2206..222B (the full wait inside each fade). These are runtime-observed
instruction controls; the pinned targets remain candidate-local-attested.
`run.py` records the serial cold commands and `focused.py` the exact original
and actual-route commands. New replay needs a fresh producer directory.

Actual Score (24 routes plus four write failures), Extra (16 actor-control
routes with hit consumption disabled), and 24 Ending routes exercise the new
consumers and phase publication. Ending/Staff/verdict/Congratulations keep complete page
and palette checks; display RGB is projected from original MAINE palette I/O
through the retained analog DAC model. The historical RGB8 formula remains
separate. Shared palette and actual eighteen-frame Demo-entry controls are
replayed against the final producer. Compiled one-variable mutations cover
fade counter clearing, post-only key samples, the 9999 sentinel and discarded
handoff time. The first stopped-entry mutation rejects no configured vectors
and remains an inconclusive wrong-site probe; the completion-site mutation
is independently compiled and rejects160 complete traces. Eight muted default
routes retain all129 prior hashes, selected original states and GNU/UBSan
parity. This regression does not promote complete original pictures.

Registration proper, Cutscene/Ending script, Staff and MAIN fade still have
legacy wait owners. Their full elapsed counter history, physical timing,
broader Boss/death/process routes and Windows acceptance remain open.
Historical exact remains 661/663. This is scoped runtime agreement.

Replay: `.analysis/reconstruction/probes/native-maine-demo-word-join-v1423/`;
producer: `.analysis/worktrees/native-maine-demo-word-join-v1423/.analysis/port64/native-maine-demo-word-join-v1423/`.
The preliminary v1418/v1420/v1422 cold producers and failed recipes retain their
own identities. Stage retirement saves 1,254.54 MiB net and keeps all 8,420
paths in a fully verified content archive. The superseded539 producer keeps
both complete build graphs and its completed GNU route/image proof; its UBSan
Extra job was deliberately stopped after remote WORD Demo source advanced. The stage retention reader accepts
`--restore --prefix` for owned original paths. Final retirement and publication
receipts record the remaining checks and current commit.

Stage archive readers are under `.analysis/reconstruction/probes/native-maine-stage-retention-v1422/`
and `.analysis/reconstruction/probes/native-maine-indexed-stage-retention-v1423/`.
The latter saves another 984.19 MiB net across 4,538 owned paths, including
the deliberately interrupted UBSan campaign; its logs and source identity remain.

Final verified retirement releases 1961.42 MiB net. Both complete program graphs, source freeze and original controls remain.

## Native elapsed Staff Roll (v1424)

Staff's actual scene and Ending caller now use the shared raster/IRQ owner.
The three dissolve loops poll the inherited unsigned Count1 against2, then
clear only Count1 after success. They do not use frame_delay's entry reset.
MAINE 0A05:1298,1325,13C6 each has CMP/JB then MOV Count1,0; the complete
0A05:0E80..1736 Staff extent remains pinned. Shared black fades align once,
preserve Count1 and publish all eighteen palette updates. Inactive measure
waits execute a live WORD frame_delay; active waits query after load/start,
preserve counters and service supplied measure deadlines. The actual audio
bridge uses the resident PMD timer deadline. Keys do not skip Staff.

Whole original Staff, black fades, wait and snd_delay_until_measure
0CC7:03D6..0407 instructions execute at loads1000/3333. Graphics/files and
measure replies are guarded adapters; ideal IRQ and one-second measure
stimuli remain separate from physical CPU/I/O/audio costs. Both cold GNU and
optimized UBSan/bounds producer541/83933826 build84 programs and pass82 CTests.
Each passes48 original controls,24 coarse and24 one-ms partitions, covering
inactive BGM, progressing measure and no measure progress. Existing576
MAINE controls/288 partitions also pass on the same frozen producer.

Each actual muted no-driver frontend completes24 Ending/Staff/verdict/
Congratulations routes. Independent checks cover576 Ending pages/288 RGB
frames,48 Staff pages,48 verdict pages and48 Congratulations pages. Current
RGB uses complete original palette I/O with the retained DAC projection.
These are component images and route invariants, not physical full scanout.
Real active-PMD paired scene timing, other scene wait owners, broader gameplay
and Windows remain open. Historical exact stays661/663.

Compiled whole-scene clear-before and clear-both mutations reject complete
original traces. A relative-threshold mutant passes coarse input but fails
one-ms input. The first development build had that same API misuse; its
program, source, failed partial trace and corrected replay remain separately
identified. until_count requires the absolute threshold2. Native CI345 passes.

Replay: `.analysis/reconstruction/probes/native-staff-elapsed-v1424/`;
producer: `.analysis/worktrees/native-staff-elapsed-v1424/.analysis/port64/native-staff-elapsed-v1424/`.
`verify_staff_elapsed.py` supplies original controls and full time/counter/
request comparisons; `focused.py` records actual route/page commands.
Verified content/SHA/CRC/metadata/temp-restore retirement releases908.95 MiB
net. Sourcefreeze, all programs, full control transcripts and failures remain.
`verify_retention.py --restore --prefix` restores owned archived paths. The
source target remains candidate-local-attested; this is scoped runtime agreement.

## Native elapsed Cutscene/Ending script (v1425)

Actual Ending scripts now share the raster/IRQ owner through Script, Canvas
and Ending. Parsing and queued graphics requests remain shared with the
logical helper. Zero frame_delay clears Count1 and resumes on the same
admission; input_wait preserves release-first, pre/post OR and signed WORD
budgets. Shared Animation now handles both white fades as well as black,
including initial VSync, signed WORD speed and eighteen palette updates.
MAINE white bodies0000:222C..22AB are pinned alongside black00622/0666,
frame_delay0CC7:0033..0047, input_wait020A..025F and measure03D6..0407.
The two complete original parser/helper bodies0A05:07F7..0D6B and0DAC..0E7F
execute unchanged. File/font/graphics, palette I/O and keyboard consumers
remain explicit adapters, with ideal IRQ and one-second measure stimuli.

Original cutscene checks high-byte key_det bit0x10 (word0x1000); portable
cutscene bit0x10 is a projection. The Oracle maps this explicitly. Escape is
sampled only at the next outer iteration; releasing it during a queued mask
cannot change that command. A completed owner returns unused elapsed time;
actual Ending forwards audio once and retains the Staff/verdict lifecycle.
Active measures query after load/start and use supplied service deadlines;
inactive measures use live WORD frame_delay. This is not physical timing.

Cold producer542/59d19121 builds all84 programs and passes82 CTests under
GNU Release and optimized UBSan/bounds. Each passes ten complete scripts
(eight original Ending plus two mixed/measure controls),960 original cases
at loads1000/3333,480 coarse and480 one-ms partitions. Same-source Staff
48 original/24 partitions and MAINE576 original/288 partitions also pass.
Each actual muted inactive-BGM frontend passes24 Ending/Staff/verdict/
Congratulations routes and independent component images:576 Ending pages,
288 original-DAC-projected RGB frames and48 pages each for the later owners.
The retained PI/font/kernel galleries keep their independent source identity.

Compiled zero-to-one delay rejects36 mixed cases; discarded completion time
rejects28 mixed and24 real-script cases; wrong full-word Escape rejects12 in
each subject. Unmodified compiled control passes. Native CI345 and tracking
pass. The initial malformed vector schema/configuration attempts are retained;
they were setup failures, not source/runtime acceptance.

Remaining MAIN fade, registration and other wait owners, real active-PMD
paired scene timing, physical CPU/I/O/scanout, broader gameplay and Windows
remain open. Historical exact stays661/663; targets are candidate-local-attested.
Replay: `.analysis/reconstruction/probes/native-cutscene-elapsed-v1425/`;
producer: `.analysis/worktrees/native-cutscene-elapsed-v1425/.analysis/port64/native-cutscene-elapsed-v1425/`.
`verify_cutscene_elapsed.py` records full original/native time/request/key/
counter streams; `focused.py` records actual routes and image comparisons.
Verified path/hash/size/mode/nsmtime/content/CRC/temp-restore retirement saves
1619.52 MiB net. Full transcript aliases and captures are recoverable via
`verify_retention.py --restore --prefix`; source, programs, vectors and summaries
remain live. The goal stays active.
