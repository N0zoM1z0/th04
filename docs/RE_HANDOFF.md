# TH04 current handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

v1391 (native `927ce48`) loads physical configuration in the actual Demo validation route.
The old capture copied MIKO.CFG but did not enable its owner: incoming rank 2
became native default rank 1. Demo-local Hard hid this from old state/pixel
checks. Only demo_picture_frontend_checks.inl changes: enable configuration,
observe actual configure requests and compare the complete saved CFG. Current
frozen 510-file producer: `c6a90f57e662cbbe85cec9b55047f0ffce5df818067725f687b548f4d2579010`.

Cold GNU builds 71 programs and passes 69 CTests; optimized UBSan builds the
game, trace and shake programs. Eight actual muted full-startup runs cover
none/pmd/pmdb2/pmd86 separately under GNU and UBSan. Each pair produces 129
byte-identical files. All nine OP/MAIN configure requests equal incoming options
2/3/2/2/1/1; all 10 CFG and 1,960 score bytes stay unchanged and equal independent
FAT readback of the fresh original's final disk. Each profile matches selected
state/RNG/draw counts at all 15,988 original seams. One resident Logo and five
completed titles include final fresh OP ready. Private Linux Xvfb input/focus/
release/exit passes with zero audio opens. Configuration requests are observed
native options, not original resolved board/driver/audio acceptance.

Native measure request to first SUPER_load is 0 refreshes for none and 94 for
pmd/pmdb2/pmd86. First MAIN is refresh 1,193 versus 1,287. These observed provider
spans are not target constants or original PMD measure timing. Strict PMDB2 ROM
identity rejected an LLE-format choice before launch; corrected -v2 runs use
the attested MAME ROM. No identity guard was relaxed. A one-call configuration
bypass completes successfully and preserves every old 128 output file, but all
nine configure points use rank 1; the independent option reader rejects it.

A fresh original zero-delay run uses the exact retained collector projection,
ELF, reset, input and sample plan. C2/E2/V21113/F15988 events replay independent
archived original GDC bodies at every 15,988 seam and 15,984 thin row. Parameter-
entry coverage stays zero. Fresh scalar/caller digests equal both retained
closed v1390 readers, without replaying or restamping old identities. All 120
original samples are freshly CRC/EOF/hash/clock-guarded; non-GDC/raster raw
regions agree across three captures. Baseline to zero-repeat event ordinals
shift by 8 at every seam with 3,999 visible phase changes, versus the old sleep
pair's 5/6 shift and 2,501 phase changes. Five events cannot uniquely diagnose
inserted sleep; this is not a causal estimate. Keep capture epochs distinct.

Current supplied-original-clock None fixture admits all seams/endpoints before
paint. Complete raw RGB is zero 40/40 against independent full FONT/CRT/VRAM/
palette/GDC/time rendering, without normalization, crop, tolerance or phase
fitting; whole canonical TRAM agrees. Zero-initial-callback control rejects.
Default headless RGB counts against this fresh original are 31/40 for none and
34/40 for active profiles. All profiles match 40/40 references evaluated at
their own counter phase; that remains diagnostic. Whole-index inequalities,
fixture startup-prefix/final-OP and original PMD/audio clocks remain unpaired.
Prior 80/80 and earlier compact-entry 37/40 keep their old scoped identities.
DAC, initial count 1 and 17,723,227 ns period proofs retain their identities.

MAIN SHA starts 077440a3; locations MAIN 0AAF:00B7/0975, runtime load10FC/
DGROUP3230. Default startup/loading/process clock owners, raw PIC fractional
timing, physical/cross-emulator scanout, paired Boss/death/process and Windows
input/audio remain open. Next identify original startup/loading and resolved
PMD clock owners from independent event evidence. The goal stays active;
candidate-local-attested provenance and deferred historical exactness remain.

Replay: root .analysis/reconstruction/probes/native-startup-clock-v1391/;
native .analysis/port64/native-startup-clock-v1391/. Original reader, cold
builds, eight captures, negative controls, private Xvfb and comparisons are
serial CPU0/nice19. pipeline_v3.py closes corrected RGB/profile reductions.
Earlier rejected freeze-parent, ROM and missing-import setup attempts retain
sources/logs/negative receipts; none is acceptance. All prior proofs keep their
immutable producer identities. Both complete CI/diff checks close this batch.

Lossless cleanup reclaims 725.04 MiB after archive/journal. Current game/trace/shake
programs, frozen sources, compressed originals and replay receipts/logs stay
live. Duplicate native captures, disposable HDIs, expanded references, objects,
libraries and helper programs are archived. Before full replay restore them:

```sh
python3 .analysis/reconstruction/probes/native-startup-clock-v1391/verify_retention.py --restore
```

Without --restore, checks include full gzip CRC/EOF, member SHA/mode/size/nsmtime,
inherited protected proof hashes and all frozen producer pins.

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
