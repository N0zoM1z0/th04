# TH04 current handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

v1395 (native commit `955de04`) adds resident elapsed work across installation, OP resource/drawing
consumers and process gaps. Typed `Timeline::advance_work` progresses the same
Timer/PCM owner without a local process, or the local beeper/mix with a process.
Pending refresh wait is flushed once before completed work; retained guards
cannot charge it again. Unknown kinds and >1-second intervals reject before
clock mutation. `MainAssets` exposes installation, OP-entry and startup-event
adapters. Default inputs are empty; no fitted offset/bus cost/wait is added.

Current native producer: 510 files,
55459c6f487e25ce39e0b8499b89f52936e0273c536905e94b8a7764426fdb7e.
Six maintained native files change; DOS source/flags/headers do not change and
fingerprint 6f5898dd stays fixed. Cold GNU builds 71 programs / passes 69 CTests;
optimized UBSan builds seven selected targets / passes four sound contracts.
Earlier 9cfe producer and proof receipts retain their identities.

A separate caller compiles frozen maintained view.cpp, links cold product
core/chip archives and executes actual FrontEnd with real PI/BFNT/music/effects,
strict ROM and physical config. It forwards independent v1393 original 24,000 /
36,000 CPU loading epochs through the new adapters. PLAY equals the source
255,036,542 / 178,822,806 ns exactly. Both reach measure readiness at 93 refreshes;
sample errors 3.648611 / 8.074889 ms are below one 17.723227 ms frontend refresh.
Twelve complete GNU/UBSan callers (two inputs, three modes) have identical
output tables. Allzero controls complete 97 refreshes but reject PLAY epoch;
graphics-only removal also rejects even while aliasing 93 refreshes. Counts and
program completion are insufficient. This conditional diagnostic is coarser
than the retained standalone 1 ms probe; no physical chip/IRQ/GDC claim follows.

Eight fresh default CLI captures cover none/pmd/pmdb2/pmd86, full startup,
four natural demos and fresh OP ready. Every compiler pair reproduces all 129
files from its retained v1392 baseline. This is current source-bound regression,
not restamping old receipts or default original clock/full-picture acceptance.
Prior RGB limits remain 31/40 none, 34/40 active. Muted private Linux Xvfb
startup/selection/input/focus/release/exit passes; audio device opens 0.

Replay: DOSroot .analysis/reconstruction/probes/native-elapsed-work-v1395/;
native .analysis/port64/native-elapsed-work-v1395/. Current source freeze,
compiler/caller/run/comparison receipts and original-parent pins remain live.
Restore archived programs/build/RGB/state inputs from the DOS root:

```sh
python3 .analysis/reconstruction/probes/native-elapsed-work-v1395/verify_retention.py --restore
```

Use --prefix to restore only a required relative subtree, and fresh namespaces
for another execution. Lossless retirement reclaims about 472.70 MiB of
build intermediates/programs, RGB/indexed samples and duplicate state/item
outputs. Full gzip CRC/EOF, content hashes, logical size/mode/nsmtime and
protected proof/source pins are checked. First archive has 2697 logical files /
1407 unique blobs; additional text archive retains 16 logical files /
2 unique blobs. Failed first caller compilation remains failed;
V2 fixes only its frozen root include path. Both full CI gates pass (root 441 /
native 345), with ledger and diff checks. Post-CI source-backed caches reclaim
16.85 MiB separately; proof inputs remain protected.

Next establish deterministic default resource/graphics work inputs and connect
the distinct GDC/application epoch; do not substitute host wall time or a fitted
startup age for original CPU/bus work. Goal remains active. Full pictures,
broader paired combat/process, physical/cross-emulator, Windows input/audio and
MAIN historical carpet/checkerboard exactness remain open. Targets remain
candidate-local-attested. Continue CPU0/nice19 serial muted Linux work;
Windows GUI/focus/host keys remain excluded.

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
