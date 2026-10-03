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
