# TH04 current handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

v1398 adds a native unsigned VSYNC counter and explicit rational raster clock.
The components preserve START/END, carry skips, 16-bit wrap, Count1-only wait
reset and an independent display phase. Frontend integration is the next step:
active PMD readiness still uses admitted-refresh sampling and Logo still uses
fixed logical waits. No wait-scheduler repair is claimed yet.

Original OP load 10FC / DGROUP 2030 is independently verified at decoded
0000:25D6, immediately before Count1 increments. Two complete muted Linux
GAME.BAT captures at CPU 24000/36000 record all 106/102 counted IRQs, 143/139
scalar boundaries and 119/111 GDC callbacks. IRQ deadlines derive from master
AW 80 / HS 8 / HFP 10 / HBP 8, AL 400 / VS 8 / VFP 7 / VBP 25, character clock
2631575 Hz and the pinned emulator's explicit 100 ns adjustment / float delay. IRQ and GDC blink
have distinct phases. Callback-to-target-increment latency varies 50–138 /
64–142 CPU cycles; do not encode a fixed service delay or fit wait durations.
The extra IRQ observer changes measured wait brackets relative to v1397;
retain each capture's own producer and times.

Native v1398 implementation is committed at `dd916ff` on
`port/modern-64`. Current native producer: 512 files,
efea1700368644b07a03040b9b60bd12335413d3b842c9a76aa72046f4475dea.
New port64/pc98_vsync.hpp and its contracts are registered in CMake / explicit
source manifest. DOS product source, flags and fingerprint 6f5898dd are
unchanged. Cold GNU builds 72 programs / passes 70 CTests; optimized UBSan
builds 8 selected targets / passes 5 sound/VSYNC contracts. Native Counter and
RasterClock separately reproduce 208 target IRQ records and 230 host raster
callbacks under both builds. Wrong Count2 reset, blink-phase substitution and
carry removal reject; the 31-kHz carry test is synthetic, not original runtime
acceptance. Four public IRQ-reader mutation tests also pass.

Eight fresh default native CLI routes (none/pmd/pmdb2/pmd86 × GNU/UBSan)
complete startup, all four demos and fresh OP. Every 129-file output set equals
its immutable v1396 profile baseline. This is current-source regression,
not whole-picture or combined frontend IRQ timing acceptance. Earlier window,
original/DOS Demo and physical evidence keeps its own frozen identity.

Replay indices from DOS root:
.analysis/reconstruction/probes/native-irq-clock-v1398/ and
.analysis/worktrees/port-modern-64/.analysis/port64/native-irq-clock-v1398/.
Original reader original-reader-v1/receipt.json SHA 334d6fde92b5c797163ae6bdcd9d60e88f285782a3864c0ba0abe837650d2342;
native probe-v3/receipt.json SHA 00084b0e54e6d9a750a0547718c593c6e8411139c2c8e6af71fd7eed4a16cbf6.
The first probe's unsupported C++20 option and second probe's early-rounded
PIC admission remain failed. V3 uses supported C++17 and upward integer-ns
admission, preserving the rational phase formula and original floating times.

Cleanup recovery uses the new v1398 reader, which attests current 512/efea and
old frozen 510/ea5c producers separately. Old v1396/v1397 strict readers now
reject the changed current manifest; do not edit or restamp those proofs.

```sh
python3 .analysis/reconstruction/probes/native-irq-clock-v1398/verify_retention.py
# Restore only needed owned files before complete replay:
python3 .analysis/reconstruction/probes/native-irq-clock-v1398/verify_retention.py --restore --prefix .analysis/runtime/candidates/dos-op-v1398-irq-
# Previous complete archives / frozen producers:
python3 .analysis/reconstruction/probes/native-irq-clock-v1398/verify_retention.py --parent v1397
python3 .analysis/reconstruction/probes/native-irq-clock-v1398/verify_retention.py --parent v1396
```

Add --restore and a narrow --prefix for archived parent inputs. Lossless
retirement of 3,110 files / 1,451 blobs reclaims 528.63 MiB after its 39.20 MiB
archive and journal. Full CRC/EOF, member/temporary-restore metadata and
694 protected proof hashes pass. Full CI passes root 451 / native 345 tests;
post-CI source-backed caches reclaim another 16.32 MiB (1,051 files).
Total current net cleanup is 544.95 MiB. Tracking/diff checks pass.
Complete source freezes, original scalar/GDC streams, selected current
programs, compiled negative controls, failed attempts and old proofs remain
protected. Use fresh namespaces for another capture, build or reader.

Next connect PMD busy service and inherited unsigned IRQ waits to FrontEnd,
preserving clear-before-frame_delay versus clear-after-Logo and global raster
phase. Resource/CPU/bus/graphics elapsed inputs need a defensible model; do not
fit startup ages or use GDC blink as the IRQ counter. v1397 BGM-off zero-wait
and active inherited-count controls remain mandatory, alongside v1398 full
IRQ progression. Physical/second-emulator timing, full pictures, broader
combat/process, chip/audio and Windows input/audio remain open. MAIN historical
carpet/checkerboard exactness stays deferred. Goal remains active; targets
remain candidate-local-attested. Continue CPU0/nice19 serial muted Linux work.

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
