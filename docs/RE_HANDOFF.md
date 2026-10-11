# TH04 current handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

v1390 (native `e66bd39`) repairs the Demo validation entrance: `--demo-pictures` now runs full
visual OP startup. Actual muted routes record one Logo and five completed
titles, including ready OP after Demo4. Captures use `--pmd-driver none`;
original PMD measure waits remain unpaired. The 510-file native producer is
`bdc1fb56f80b1d5d987c89a1cfe63cea9da155eb6ef8eb662c10480dd02c4b5e`.
Only main.cpp and demo_picture_frontend_checks.inl change.

Cold GNU builds 71 programs and passes 69 CTests; optimized UBSan builds the
game, trace and shake programs. Their actual four-Demo captures produce 128
identical files. Selected state/RNG/draw counts match both fresh originals at
all 15,988 boundaries. State, palette, index, TRAM and shake outputs keep their
previous hashes. Full startup changes five RGB files, the logical clock trace
and adds startup-events.txt. Private Linux Xvfb input/focus/release/exit passes
with no audio device opened.

Two original runs use the same collector, ELF, config, reset and sample plan.
Only host waits after the first 128 recorded V callbacks differ: 0 versus 5 ms,
with 654,057,090 ns total measured delay. Both complete GDC event streams replay
independent archived advance bodies; all 15,988 boundaries, 15,984 thin rows and
40 full samples per capture pass their guards. Selected state and caller traces
agree. Refresh ordinals differ by 5 at 15,987 boundaries and by 6 at one boundary;
2,501 visible phases differ. Raw text, graphics, palettes, modes, FONT and CRT
agree in all 40 paired samples. Only GDC and raster-time spans differ. This
single pair does not attribute the shift specifically to sleep rather than
run-to-run jitter. Keep epochs distinct. Parameter-entry coverage remains zero.

Each original's complete FONT/CRT/VRAM/palette/GDC/time samples emit 120 full
RGB references. Separate actual FrontEnd fixtures use that capture's event
ordinals at 15,988 boundaries and 15,984 endpoints. Complete raw RGB equals
40/40 for each capture, 80/80 total, without normalization, crops, tolerance or
phase fitting. Whole canonical TRAM equals; whole-index inequalities remain
diagnostic. Default full-startup headless RGB equals 32/40 and 30/40 against
the separate originals. Earlier 37/40 covered compact headless entry and
retained V3. Fixture startup-prefix/final-OP clocks remain unpaired. The
zero-initial-callback control rejects. Existing DAC, initial count 1 and
17,723,227 ns period keep their independent proof identities.

MAIN SHA-256 starts 077440a3; seams are MAIN 0AAF:00B7/0975 with runtime load
10FC/DGROUP3230. Default boot/loading/process CPU-I/O clock ownership, raw PIC
fractional timing, physical/cross-emulator scanout, paired Boss/death/process
and Windows input/audio remain open. The full goal stays active. Targets are
candidate-local-attested; historical carpet/checkerboard exactness stays
deferred. Next separate original startup/loading clock owners from observer
effects with controlled event traces and repeated zero-delay controls.

Replay: DOS-root .analysis/reconstruction/probes/native-clock-owners-v1390/;
native .analysis/port64/native-clock-owners-v1390/. pipeline_v2.py runs original
readers/full cold builds/fullstartup captures/explicit per-capture clock fixtures
and private Xvfb serially onCPU0/nice19; compare_native.py reduces full raw RGB.
Use fresh output namespaces. All prior closed proofs keep immutable identities.
Final lossless cleanup reclaims587.84MiB after archive/journal. Current
game/trace/shake programs, frozen510 sources, original compressed streams,
all independent programs/receipts/logs stay live. Restore retired HDIs/rawscalar,
native captures, objects/libraries and helper programs before complete replay:

```sh
python3 .analysis/reconstruction/probes/native-clock-owners-v1390/verify_retention.py --restore
```

Without --restore, full gzipCRC/EOF/member SHA/mode/size/nsmtime and inherited
protected/frozen-source pins are checked. See the focused note for limits and
prior archived controls. Final CI/diff checks cover both worktrees.

See [the focused note](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md).

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
