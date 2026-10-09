# Native continuous PMD clock: first closed corpus

v1341 adds `OpnTimers` and `ClockedPlayer`. GNU8, optimized UBSan and
actual Windows each compare **72,391 complete rows in 46 closed first-load
scenarios**, with all 60 component contracts passing per host. 430 maintained
inputs bind 183 AMD64 products, 61 per cache. This is the first closed batch;
the original two-PSP/three-driver aggregate producer is still running. Do not
claim its 174-case acceptance until its terminal receipt and full consumers
pass. Every run is muted and opens no audio device/backend.

## Clock ownership

The installed default prescaler gives a 72-master-cycle FM clock on FM26
and 144 on the OPNA boards. A reload uses `1024-A` such clocks; B uses
`16*(256-B)`. Starting a stopped B timer compensates its free-running
modulo-16 divider. Acknowledge and changes to A/B reload registers preserve
an already scheduled deadline. Expiration reloads before CPU dispatch, so a
tempo command inside that dispatch affects the following reload. Music stop
leaves resident timers running; start/restart preserves the resident epoch.

Nanoseconds convert to master cycles with a retained rational remainder.
Frequency is an explicit host input. Recorded scenarios use 4 MHz/8 MHz;
these are adapter settings, not measured physical board frequencies. The
first FM clock is at one full quantum after epoch zero. Coincident timer
expirations latch together before one zero-latency IRQ. No CPU instruction,
bus write latency, interrupt masking interval, prescaler change or CSM audio
behavior is accepted by this owner. `OpnTimers` is the bounded timer surface,
not a complete OPN chip emulator.

`ClockedPlayer` routes live primary timer writes from the maintained player
into these deadlines. IRQs call the actual musical/effect owner. It supplies
real musical progress from timer dispatch rather than fixed frame-derived
measure replies. It remains separate from the frontend resident-process and
PCM owners, and does not yet advertise a frontend driver capability.

## Independent comparisons

The original COM identities and guarded Unicorn/DOS adapters remain those in
[pmd-driver.md](pmd-driver.md#target-and-observer-contract). Targets are
flat COM, `PSP:0100` entry/`PSP:0103` service, without MZ relocations. This
batch uses direct original execution; no disassembler database or target
mutation is involved.

A standalone CPU-only Oracle executes pinned BSD3
[ymfm](https://github.com/aaronsgiles/ymfm/tree/81aec25ccbb98f4873a255f7551ac4dadac59b4a).
The original producer forwards its own timer writes to this independent chip
model. Model callbacks schedule expirations; original COM handles their status
and forwards acknowledge/tempo writes back to the model. The native consumer
uses its own scheduler and parser, without the chip-model source or generated
original events. Complete configured musical/FM/SSG/effect/fade/rhythm state,
chronological owned writes, cycles, timer status, both deadlines and IRQ counts
compare. Original service calls independently crosscheck the fast state view.

The model generates three minimum-fidelity outputs per FM clock, first at one
quantum, to advance its real internal FM counter. Calling only timer callbacks
would freeze that counter and miss initial B divider phase. This model adapter
accepts neither audio samples nor physical initial bus phase. Source hashes,
compiler, model revision and the adapter source remain under the private scope.
The previous die-model/manual factor-two conflict remains recorded in
[pmd-timer-player.md](pmd-timer-player.md#clock-routing-and-limits).

Three boards × 16 initial B phases compare **2,448 complete cold-chip rows**.
A whole END1 timeline divided into three unequal parts per nanosecond step
retains all **1,285 complete IRQ rows** and its final checkpoint. Zero-time
steps do not advance timers. Source-only variants reject acknowledge reloads
(row 2), dropped time remainder (row 6), immediate tempo reloads (row 2),
half periods (row 0), and omitted initial B phase (cold-chip row 57).

One attempted counterproof applied the free-running phase at every B reload.
Its complete END1 stream equals the reference: the installed B deadlines
already have FM count modulo 16 zero. The harness assumption that it must
reject was false. Preserve this inconclusive observation; it is not a
comparator reject control. The first producer attempt also rejected a wrong
model-source argument index before original execution; its log remains.

GNU/UBSan additionally replay all **80,040 v1340 timer-register rows per host**
against the unchanged terminal original reference. Their 60 legacy products
have unchanged hashes. Linux GUI hashes remain unchanged; current Windows
relinks have fresh identities and only bounded CPU execution is accepted.
No new GUI launch, distribution or natural-route acceptance occurs.

## Replay and outstanding aggregate

Private scope: `.analysis/port64/pmd-time-v1341/`.

- `model-profile.json`, `ymfm-timers.cpp`: pinned independent chip and adapter.
- `windows-first/closed-reference.json`: the exact 46 complete first-load files,
  source archive identity and explicit still-running producer limit.
- `native-first/receipt.json`, `windows-first/readback.json`: complete first
  batch consumers, including actual Windows stage readback.
- `generic-receipt.json`, `partition-current/receipt.json`,
  `counterfactuals-v2/receipt.json`, `initial-phase-counterproof/receipt.json`:
  phase, time partition and falsifying controls. The earlier partition receipt
  retains its prior binary/archive identity; the fresh current partition binds
  the final current program.
- `product-profile.json`, `source-profile-current.json`,
  `consumer-source.tar.gz`: current 430 inputs/183 products, full archive readback.
- `original-v2/`: live aggregate original producer. Observe the existing
  handle/PID; never restart solely after a polling timeout.

After the original producer closes its complete receipt, use fresh outputs:

```sh
python3 port64/verify_pmd_clock.py --reference .analysis/port64/pmd-time-v1341/original-v2 --binary .analysis/port64/linux-live-v1251/th04-port64-pmd-clock-contracts --binary .analysis/port64/ubsan-live-v1251/th04-port64-pmd-clock-contracts --output .analysis/port64/NEW-clock-native
```

Original replay additionally supplies `--hdi`, `--model` and `--model-profile`;
the profile attests both private source and all pinned external inputs.
Actual Windows uses a fresh typed `pmd-clock` plan. Read back all streams
against both PSPs, preserve the first closed receipts and producer archive,
and recheck every current product. Do not restamp old receipts.

Journaled cleanup preserves all 183 programs and 430 source hashes and
reclaims **413,282,304 allocated bytes (394.1 MiB)**. Raw/probe streams have
verified lossless successors. Objects/static libraries regenerate from the
current source archive and retained CMake/link profiles. Live original/chip
processes and the Windows stage are excluded from that cleanup. A separate
terminal-stage archive/readback journal subsequently reclaims 195,694,592
allocated bytes. Total 608,976,896 bytes (580.8 MiB) across disjoint journals;
the stage restores from `windows-first/stage.tar.gz`.

PCM FM/SSG/rhythm synthesis, other required driver owners, actual resident
frontend lifetime, startup/measure waits and complete natural Linux/Windows
routes remain unfinished. Historical DOS acceptance and
`candidate-local-attested` provenance remain unchanged.
