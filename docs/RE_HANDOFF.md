# TH04 current handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

v1399 corrects native repeated VSYNC_START: it clears Count1/Count2 and
selects the cadence increment while preserving the accumulator. v1398 wrongly
cleared that accumulator. Its zero-phase startup/Demo observations remain valid;
they do not validate repeated START with nonzero phase.

New independent Unicorn execution runs complete original OP START0000:2552–25BB,
GDC query0000:15C2–1617 and IRQ0000:25C6. Twelve cases vary load10FC/3333,
BIOS mode bits0/C and accumulator0/12345/65535. Installed ownership0xFB,
no IRQ inside START and BIOS AH31 responses are explicit diagnostic inputs;
all original instructions execute unchanged with proper far return/IRET frames.
START writes no accumulator. With phase65535/modeC, the next IRQ skips counting.
Current GNU/UBSan match12/12. Frozen v1398 matches only4 zero-phase cases;
8 nonzero-phase cases reject and2 gain a spurious counted IRQ. This is a seeded
CPU diagnostic, not a natural31kHz or physical timing claim.

Current native commit: `90a8596` (`port/modern-64`).
Current native producer:512 files,
5474b8e36c4f90908803a8a94e95f22dad4c131e3a435af921ca5aacb7587a74.
Only pc98_vsync.hpp / its contracts change. Fresh cold GNU builds72 programs /
passes70 CTests; optimized UBSan builds8 targets / passes5 selected contracts.
Fresh current-source probes also reproduce all208 original IRQ records and230
raster callbacks. Eight new full startup/four-Demo/fresh-OP routes retain all129
baseline output files per driver profile. Old producer/proofs keep their own
identities; no old receipt is restamped.

Important next ownership issue: src/shared/hardware/vsync_irq.asm in both DOS
source trees still explicitly clears cadence_skip_accumulator on START. Direct
original OP execution falsifies that reset under these controlled inputs.
DOS source/fingerprint6f5898dd remains unchanged in this native-only correction;
its current24kHz demo proofs remain scoped and cannot accept this31kHz/repeated-
START corner. Next fix and separately cold-replay the shared DOS assembly before
frontend integration. Also preserve query-before-increment-selection/count-clear
ordering: current source clears those fields before querying; test an IRQ
interleaved with the BIOS query in the next bounded unit. Historical exact units / MAIN deferred cases are not
promoted or rewritten by this observation.

Original full-clock IRQ evidence v1398 remains separately scoped: load10FC /
DGROUP2030,106/102 counted IRQs,143/139 scalar rows and119/111 GDC callbacks.
Raster geometry AW80/HS8/HFP10/HBP8, AL400/VS8/VFP7/VBP25 gives characterHz2631575,
horizontal106/vertical440/retrace407. Source-defined100ns emulator adjustment /
float delay is explicit. Counter service latency varies50–138 /64–142 cycles;
extra hooks perturb wait brackets. Do not fit an ISR duration or alias blink
with IRQ Count1. See the focused note for immutable captures and reader commands.

Replay indices from DOS root:
.analysis/reconstruction/probes/native-vsync-lifecycle-v1399/ and
.analysis/worktrees/port-modern-64/.analysis/port64/native-vsync-lifecycle-v1399/.
Public original reader:

```sh
python3 scripts/runtime/verify_op_vsync_lifecycle.py --output-dir .analysis/reconstruction/probes/NEW-vsync-lifecycle
```

It pins packed/decoded OP,804 diagnostic relocs, Unicorn binary, complete
instruction/memory-write traces and target frames. Current source, compiled
caller and parent target receipts are separately pinned. Current followup uses
one CPU/nice19 serial work on CPU1 because user processes occupy CPU0; original
v1398 timing captures retain their original CPU0 identity. No Windows GUI,
focus, host keys or audio device is used by this work.

Recovery uses the new v1399 verify_retention.py. It independently attests current
512/5474b8, frozen v1398 512/efea and older510/ea5c. Old strict readers reject
the changed current source; do not edit them.

```sh
python3 .analysis/reconstruction/probes/native-vsync-lifecycle-v1399/verify_retention.py
python3 .analysis/reconstruction/probes/native-vsync-lifecycle-v1399/verify_retention.py --parent v1398
```

Use --restore / a narrow --prefix for owned archived inputs; --parent v1397 or
v1396 routes earlier archives. Full source, original raw streams, failed/old
producers and compiled negatives remain protected. Full CI passes root451/native345;
current retirement/cache cleanup reclaims 484.68 MiB net. Full CRC/temporary
restore/688 protected proofs pass. Details are in the focused note/private
receipts. Prior v1398 cleanup remains separately indexed at544.95 MiB.

After shared DOS lifecycle correction, connect independent PMD busy service and
inherited unsigned IRQ waits to FrontEnd, preserving clear-before-frame_delay /
clear-after-Logo, accumulator and global raster phase. Scene still samples once
per admitted refresh and uses fixed Logo waits. Default CPU/resource/graphics
elapsed work needs a model. Full pictures, broader combat/process,
physical/second-emulator scanout, chip/audio and Windows input/audio remain open.
Goal stays active; targets remain candidate-local-attested. Next heavy work
remains single-core/low-priority/serial and muted.

Earlier native shake, background-ring, laser, pellet, item-splash and MPN
palette repairs retain their frozen producer/proof identities. The
[focused differential note](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md)
indexes their results and archive recovery; they cannot attest the current
source without a fresh scoped replay.

Updated 2026-10-11. Current focus: complete DOS actor/presentation/process
comparison, followed by separate x64 state/effect fidelity. DOS demo state is
retained. This handoff indexes verified state; detailed experiments belong in focused notes and CSV
ledgers. The next behavioral validation focus is original DOS versus reconstructed
DOS, with native x64 fidelity checked separately. Reopen semantic work for a
reproduced differential or a concrete portable owner, not a general rename pass.

## Products and claim boundaries

| Product | State | Authority |
| --- | --- | --- |
| Historical reconstruction | OP 93/93, MAIN 493/495, MAINE 72/72, ZUN 3/3 accepted authored functions | [Generated progress](PROGRESS.md), acceptance ledgers |
| Standalone DOS PC-98 game | Four products build from maintained local source without master.lib or ReC98 product includes; repaired normal and invincible variants | [DOS operation](DOS_BUILD.md), [hardware findings](PC98_HARDWARE_REUSE.md) |
| Semantic DOS source | Asset, memory, input/timing, scroll, bullet/VM/shot/item, RNG, score and process contracts clarified | [Semantic summary](SEMANTIC_READABILITY.md) |
| Linux/Windows x64 | Separate `port/modern-64` branch; scoped GNU Reimu A Normal/Lunatic/Extra clear/save/restart routes plus component Oracles; full fidelity still open | [Port status and TODO](PORTING_STATUS.md) |

Function acceptance is not whole-file exactness. OP/MAINE/ZUN counts cover
recovered payload functions, not original packed-file extents. MAIN's carpet
and checkerboard cases remain deferred; no acceptance is promoted by the
native fixes or this runtime batch. Targets remain
`candidate-local-attested` (a provenance gap).

## DOS verification frontier

- v1372 fresh scalar/RNG and full nine-pool/22-state comparisons pass. Complete
  video accepts all four demos, all 3996 updates and 38 compared regions each.
  Correcting the short lighting-mask row removes all remaining Demo 1 graphics
  differences; the cold artifact changes only 17 DATA bytes. Previous carpet
  image, packed-box and point-number repairs stay verified. Complete old/new
  raw evidence and source/ABI controls stay
  available, with lossless gzip recovery before archived-stream replay:
  [paired evidence](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md).
- v1368 accepts22 raw global-state blocks across all15984 demo updates, with
  instruction witnesses and distinct-value/nonzero coverage. Complete24-byte
  Boss and22-byte Midboss,12-byte player motion, options and timers match.
  Boss combat/death/respawn are unexercised; callback addresses are excluded,
  never masked. Replay adds `--global-states` to the v1367 reader recipe;
  receipt `dos-demo-v1368-globals-comparison-final.json` retains all raw hashes.
- v1367 full raw pool reader accepts all15984 updates across four original/
  ordinary demos. Shots/enemies/sparks/bullets/custom_entities/circles/items/
  pointnums/gather pools cover24952 B per update, plus graze and post-reset
  input/Shift. No byte normalization. Complete DGROUP streams and ordinary
  controls are pinned in `dos-demo-v1367-dgroup-comparison-final.json`; executed
  producer v2/v3 differs from the current independent reader. Rendering and
  input reset precede this seam; score update follows it. Reuse the streams to
  recover remaining global state owners; v1369 captures video separately.
- v1366 original/ordinary DOS naturally rotates all four demos through GAME.BAT.
  Each has 3996 updates plus terminal condition3996; all 15,988 boundaries match
  consumed input/raw shift, score/deltas, LCG/ring/cursor/helper counts/arguments
  and sampled player/resident state. New cold MAIN SHA-256 `16132526…`, MAP
  `2ee564c3…`; package `.analysis/build/th04-demo-angle-v1366/` retains old
  unchanged OP/MAINE/ZUN. Original MAIN load10FC/DGROUP3230; candidate
  load10FC/DGROUP34F7. Full readback retains v1365's failed comparison separately.
  The bounded cause is initialized midboss aim toggle1 versus old BSS0, reversing
  the stack pattern's fixed/aimed order. At stage-frame writes3282/3299/3315/3331,
  all 440*26 bullet bytes, toggle1/1/2/2, template angle and graze59 agree.
  Original/candidate pools are DGROUP5A22/4974. These four snapshots are scoped
  diagnostics, not a complete actor/effects trace. See
  [paired evidence and replay commands](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md).
- The user reports complete Normal routes/Endings/save and earlier invincible
  Easy/Lunatic runs. These are manual Windows observations.
- Recorded ordinary controls cover startup, OP options/Music Room/config
  persistence, Orange clear, Stage 2 entry, the repaired Kurumi empty-ring
  failure and Stage 3 entry. Seeded Good Endings reach registration and save
  the expected section; their final black frames do not accept fresh OP.
- Upper-left pellet corruption is confirmed and repaired by full EAX clearing;
  seven ordinary checkpoints exclude the old mark. The Stage 6 stripe's
  connection to initial scroll state remains inferred, with user confirmation
  that the stripe disappeared.
- Scalar/CPU/I-O controls reject planar and bullet drawing regressions. A
  440-bullet Lunatic/Turbo fixture measures improvement, including the extreme
  all-cloud phase. It is not a natural full Lunatic route or Windows FPS test.
- Full natural dense Lunatic timing/audio, the optional Windows 36,000-cycle
  profile and a second PC-98 emulator remain validation TODOs. New DOS
  performance work is outside the current native batch.

See [reusable hardware contracts and limits](PC98_HARDWARE_REUSE.md) for each
repair, replay entrypoint and evidence/knowledge routing.

## Retained ordinary native routes

Earlier GNU Reimu A Normal/Lunatic/Extra clear/save/restart and bounded dense
slowdown receipts retain their v1356 compiled producer and separate readers.
These are scoped Linux/private-Xvfb runs; they do not accept full original
DOS parity, uninstrumented FPS, Windows or every inner Ending phase. The prior
UBSan Normal clear claim remains revoked because mask0x19 is a sentinel.
Require mask<4 plus the selected shot bit. The failed v1360 route and initial
late Bomb probe remain failed, with their bounded valid observations preserved.
See [port status](PORTING_STATUS.md), the differential note, and native
`docs/port64/evidence/host-window.md` for exact receipts and coverage.

## Comparison priority for the next agent

The user's primary comparison is **original Japanese DOS versus reconstructed
DOS**, both through the PC-98 game route. Native x64 must also preserve gameplay
state and effects. Native-host equality and successful native clears do not
replace either comparison. Start with the four bundled demos, then bounded
recorded ordinary play; compare score, consumed input, RNG and actor state at
the same logical boundary, followed by VRAM/palette/effects and process/save
transitions. See [DOS/native differential handoff](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md).

TH08 is a read-only workflow reference, not TH04 evidence. Its active worktree
is dirty; do not edit it, run its builds, change its database or launch its game.
Complete trace/end/input-consumption guards and first-divergence diagnostics
are the useful parts to adapt. Complete DOS demo captures pass their configured state/video scopes. Native
selected state/RNG/counts and nine full actor pools now also agree across all
four demos. Whole native presentation and broader process/gameplay pairing
remain open.

## Windows DOS demo package

The demo directory retains `start-th04-normal.bat` (ordinary damage) and
`start-th04.bat` (separately compiled invincible MAIN), plus their two unchanged
images/products, standard 24,000-cycle profiles, emulator/font and English
source builder. Independent saves are preserved by full-image hash readback.
Native previews and optional launchers are archived outside that directory.
Windows `Build-TH04.ps1 -CheckOnly -Normal` passes; no rebuild or game launch
was performed. See [retention](ANALYSIS_RETENTION.md) for recovery.

## Working commands

```sh
git status --short
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/build.py --help
python3 scripts/catalog/index.py list --category hardware
python3 scripts/ci.py
git diff --check
```

Only one Borland/Wine writer at a time. Use fresh probe output paths. Follow
[DOS build and testing](DOS_BUILD.md) for publication and Windows fast builds;
[script catalog](../scripts/README.md) for the full command map;
[analysis retention](ANALYSIS_RETENTION.md) before deleting private state.

## Navigation

- [Documentation map](README.md), [architecture](ARCHITECTURE.md),
  [workflow](RE_WORKFLOW.md), [source layout](SOURCE_LAYOUT.md).
- [Evidence index](reconstruction/README.md), [knowledge policy](KNOWLEDGE_BASE.md).
- `config/units.csv`, authored/decoded function ledgers: accepted ownership.
- `config/evidence.csv`, `config/knowledge.csv`: observations and reusable findings.

Historical handoff detail is retained in Git (pre-cleanup `a4f7991`) and the
subject notes. Old build/package names and private receipt paths are provenance,
not the current work queue or a promise of expanded artifact retention.
