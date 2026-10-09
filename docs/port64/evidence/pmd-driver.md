# Original resident PMD driver reference

v1329, 2026-10-09. `verify_pmd_driver.py` now executes the supplied HDI's
original resident music drivers and every M26/M86 music resource, without
opening an audio device. `verify_pmd_controls.py` executes their FM effects,
fade, stop and restart controls. This establishes the independent reference
needed to implement the native sequencer and synthesis. The native runtime
still reports PMD/MMD absent; no new native FM functionality is accepted.

## Inputs and execution boundary

The original HDI SHA-256 is
`0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd`.
Fresh root/native preflight and root OP database/header/entry/relocation/load
checks pass before target work. Target provenance remains
`candidate-local-attested`. Driver and music ownership is derived from the
attested FAT/PAR image, not a substitute download or emulator bundle.

| GENSO driver | Bytes | SHA-256 | Original type/version AX |
| --- | --- | --- | --- |
| PMD.COM | 20379 | `cbbe9bd610aedda586d8bd7f6dd13d21f037a089458a21ddda0b11a53b4b29e4` | `4800` |
| PMDB2.COM | 25730 | `dfebbfd6e82916dfc4d8d01f2fcd938e215cc16cbd5ce2f19bce37cdc3841437` | `4801` |
| PMD86.COM | 28871 | `34b7381d66400b89fca833e08fb30f315b9092eb3883f137538dcf18477fd77f` | `4802` |

These auxiliary files are flat COM programs: entry `PSP:0100`, INT60 service
entry `PSP:0103`; they are distinct from TH04's MZ ZUN.COM. Both PSP segments
1000 and 2000 execute unchanged driver bytes. Actual installation publishes
INT60 and the FM IRQ vector. The CLI tails come from the original GAME.BAT:
`/M8 /V0 /E2 /K /N /P` for PMD, and `/M8 /V0 /E2 /K /N- /P` for the other two.

DOS version, PSP/environment/SFT, prints, resident termination and vector
services are explicit guarded adapters. The SFT reports the actual COM name
and file size; the original installation can inspect its trailer. The board
adapter models presence/readback and Timer A/B flag acknowledgement; it does
not synthesize waveforms or emulate a complete board. PIT calibration uses
an explicit instruction-count IRQ adapter. Playback injects timer status
0/1/2/3 rather than claiming wall-clock hardware deadlines. Unknown interrupt,
I/O width/port, buffer overrun, missing ack and exhausted CPU budget fail closed.

Original INT60 dispatch, song/resource pointers, song and FM-SE parsing,
measure/volume/status queries and OPN writes execute. Nothing calculates
measure from the native game frame count. IRQ and service return frames are
explicit caller adapters. All original bytes remain private.

## Observed controls and limits

All 23 M26 resources execute with PMD; all 23 M86 resources execute with both
PMDB2 and PMD86. At two loads this is 138 cases, each recording 384 Timer B
states: 52,992 measure/volume/status snapshots, complete ordered OPN writes,
real resource addresses and buffer limits. Every per-song record agrees
between loads. Timer A alone leaves measure unchanged; after stop, injected
timers do not advance the stopped measure. This is a bounded driver execution
reference, not full song completion, physical PCM or natural game acceptance.

The supplied LOGO songs increase measure every 24 Timer B ticks, while OP
increases it every 96. LOGO changes Timer B register 26 at ticks 1, 169 and
175 in this profile; OP first writes 196. A fixed 96-tick counter would return
1 at tick96 for LOGO, while the original returns4. Therefore neither a fixed
game-frame delay nor a universal fixed driver-tick counter can replace the
actual measure query. Actual tempo/register changes must drive the backend.

17 FM SE numbers × three drivers × two loads = 102 controls execute the real
MIKO.EFC consumer. Six LOGO fade/stop/restart controls agree across loads.
Timer A fade changes the returned volume while retaining measure. Restart
resets measure and fade. Volume records preserve raw AX, including the
retained AH; only the documented low byte is the volume value.

Two adapter-only variants reject: a fixed96tick measure disagrees with the
immutable LOGO reference, and leaving timer flags latched despite ack writes
exhausts the bounded real interrupt handler. These are Oracle adapter tests,
not native product-source mutation or changed target bytes.

The all-music producer retains its own 385-file source manifest. Its consumer
has a separate 386-file manifest after adding the controls verifier; no receipt
is restamped. All 150 native C++ products and their build inputs remain those
verified in v1328; only verification Python and documentation change here.
Historical DOS unit/decoded-function acceptance is unchanged.

## Replay and next owner

From the native checkout, use fresh outputs:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_driver.py \
  --hdi ../../runtime/images/zun.hdi --output .analysis/port64/pmd-new/music
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_controls.py \
  --hdi ../../runtime/images/zun.hdi \
  --reference .analysis/port64/pmd-new/music \
  --output .analysis/port64/pmd-new/controls
```

Private source/input/engine identities, full driver traces, negative results,
cleanup and complete public pending-source recovery are under
`.analysis/port64/pmd-v1329/`. Both checkouts finish with CI and diff checks.
Keep completed references immutable after hardlink sharing; replay into a fresh
directory. The previous v1328 scene/frontend and PCM producer receipts retain
their own identities and bounded scope.

Terminal cleanup shares 72 identical driver trace files after full byte/hash
comparison, reclaiming 7,667,712 allocated bytes with 4,252 protected hashes
unchanged. After CI, 1,012 source-backed Python caches reclaim 16,986,112 bytes.
The earlier scratch FM-SE output is retired only after all 102 output streams
compare with the accepted controls; its digest remains in the cleanup receipt.
All current programs, source, inputs and independent references remain.

Next implement the native PMD sequencer and OPN/SSG/FM synthesis against these
references, including actual tempo changes, bar length, resource lifetime and
measure/volume queries. Then wire backend capability and real measure reports
through Ending/Staff waits, complete startup audio and driver lifecycle, and
verify complete natural Linux/Windows routes and dense Lunatic timing. The
current absent backend must remain absent until it can execute real music;
elapsed host time must not manufacture capability or progress.
