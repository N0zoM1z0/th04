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
