# Original DOS, reconstructed DOS and native fidelity

The two comparison goals remain original Japanese DOS versus reconstructed
DOS, and native x64 state/effect fidelity. Native host agreement and successful
logical routes do not establish original timing or full-game byte identity.
Exact acceptance remains in the configured ledgers and complete comparators.

## Useful verified findings

- The original MAIN byte sampler reads eight BIOS bytes, then Shift, then
  optional active-low joystick pins. Reset clears the latch; Sense retains
  existing actions. Joystick actions OR into it and use only the low six bits.
  Original ISA controls cover all byte and pin values, disabled reads and both
  incoming IF states. Checking only the final action word misses read-order
  and disabled-bus defects.
- With the recorded scratch load segment 0000, the sampler is MAIN
  130E:06BC/06C4..07C4. Shift is queried at 07AB..07B1, before the enable test
  at 07B4 and far call at 07BB. Helper 0000:366A..3675 brackets only the OPNA
  transaction with PUSHF/CLI/POPF. It does not mask the whole keyboard sample.
- BIOS reads and PIC EOI are different owners. In the pinned DOSBox-X normal
  boot, CPU acceptance enters a protected monitor, then the V86 BIOS path.
  F000:E96E returns with ISR1 still set; OUT 00h,20h at F000:E971 clears it,
  and IRET at F000:E974 restores the interrupted context. Captured elapsed
  intervals varied; they are not a fixed hardware IRQ-delay constant.
- The native frontend owns persistent device state across menu generations.
  Keep physical key identities before action aliases, preserve host delivery
  order and require neutral state after joystick connection/focus regain.
  The first two axes/first hat and buttons 0/1 are a portable host policy.
- Stage transitions must reset carried palette tone at completed stage
  initialization. Palette-bearing dialogue loads refresh the player palette;
  enemy opcode 8F tile writes preserve background-prefix order.
- Original Boss circles use the stage clipping rectangle (32,16)-(415,383),
  not the whole screen. Whole-picture comparisons caught differences that
  scalar state, selected rows and constructed render calls had missed.

These are retained target/runtime findings at their recorded scenarios and
source revisions. Re-run the relevant comparison before extending their scope.
The knowledge ledger links the bounded compiler and semantic conclusions.

## Remaining timing and input problem

Original-versus-original retained 30 tail/23 raw-GDC differences. The source
DOS input scenario retained 19 key/23 GDC differences; the native physical-input
scenario retained 40 tail/7837 boundary differences. Their clocks, inputs and
checkpoints differ, so do not combine these counts into one verdict.

The missing owners are original CPU/OPNA service, common boot epoch and other
IRQ producers. A host timestamp does not establish UART arrival, CPU acceptance
or BIOS completion. Preserve physical requests, UART, PIC, BIOS reads, Shift and
the game latch separately when choosing the next small experiment.

Useful failed approaches:

- Fitting 58/82/87-cycle delays or searching another whole route for old75's
  inferred phase does not explain device/CPU scheduling.
- Equal scalar state does not establish equal full pictures or raw GDC timing.
- A successful compile, an exit-zero mutated consumer, or agreement between
  GNU and UBSan does not prove the original sampler contract.
- Dependency timestamps/source locations may change object metadata without
  preserving whole object identity. Compare the actual bytes before reusing
  an object; use fresh output for the next build.

## Current replay tools

Use `scripts/capture_th04_dos_demos.py` and
`scripts/compare_th04_dos_demos.py` for fresh bounded original/source captures.
`scripts/probes/verify_pc98_input_bytes.py` tests the original byte sampler;
its functional inputs are separate from physical V86 timing. The native
frontend and component sources live on `port/modern-64` under `port64/`.

Build only affected targets. Exact source changes require complete configured
extents and relocations. Use [the current handoff](../../RE_HANDOFF.md) for the
product priority and [retention](../../ANALYSIS_RETENTION.md) for disposable
output. Historical captures, build cohorts and recovery aliases are retired;
they are not prerequisites for a new comparison.

Unique GDB hook sources for the unresolved CPU/IRQ experiment remain under
`.analysis/runtime/candidates/dos-irq-service-v1495-v2/source/`. They contain
original-ISR, PIC, epoch and timer observers absent from maintained source.
The old capture output and executable cohorts are retired.
