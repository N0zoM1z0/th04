# TH04 current handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

v1397 independently verifies original OP wait ownership under 24,000 / 36,000
CPU budgets and a config-only BGM-off control. Active measure polling preserves
IRQ Count1; the first Logo wait inherits 104 / 100 and passes without another
counted interrupt. BGM-off frame_delay(0) clears Count1 even with zero wait.
Logo clears Count1 after each wait; Count2 continues. Native still samples
measure readiness once per admitted refresh and uses fixed Logo waits: these
ownership/phase differences are now demonstrated, not repaired.

Native v1397 documentation is committed at `19e5356`.
Product source remains at v1396 native 49b2fa5 / 510-file ea5c016d and DOS
fingerprint 6f5898dd. No fresh product build, full-picture or exact promotion is
claimed by v1397. DOS-root scripts/runtime/verify_op_wait_clock.py checks all
three complete original captures, full load/relocations/PIC/GDC and rejecting
mutations. Replay/retention index: .analysis/reconstruction/probes/native-vsync-waits-v1397/.

v1397 complete CI passes root 447 / native 345, with tracking/diff checks.
Lossless image/font cleanup recovers 218.40 MiB (18 files / 5 unique blobs);
post-CI source-backed caches recover another 16.38 MiB. Complete captures,
failed attempts and earlier producer proofs remain protected. Restore only
needed images from the DOS-root v1397 verify_retention.py --restore, optionally
--prefix; run new captures/readers under fresh namespaces.

v1396 (native commit `49b2fa5`) connects explicit loading/drawing/process work to the headless GDC
text clock as well as resident sound. Work retains sub-refresh time;
`MainAssets::display_elapsed_ns` supplies the independent display-to-PMD-install
epoch. External observation retains fractional origin and owns its elapsed
time, excluding double logical work/refresh admission. Default adapters/epoch
remain empty/zero; no fitted startup age or bus-delay constant is introduced.

Current native producer: 510 files,
ea5c016d0cd40bcb453bd9f6c27c6ec24c2513ec63342fa8be2fa8d6acc85d43.
v1396 changed only view.cpp/view.hpp; DOS source/headers/flags and fingerprint
6f5898dd remain unchanged. Cold GNU builds 71 programs / passes 69 CTests;
optimized UBSan builds seven selected targets / passes four sound contracts.
Earlier 55459 producer/receipts retain their identities.

Original OP load 10FC / DGROUP 2030; decoded Logo 0A74:14F5, PI-loaded
0A74:1523, PI-drawn 0A74:1534, second song-command 0DA1:0264 (PLAY) and
measure end 0DA1:039D remain the independently attested runtime hooks.
Independent original v1393 complete GDC/PIC observations determine initial
first-V-to-first-B age: 162,850,542 / 113,377,278 ns (24,000 / 36,000 CPU).
Initial display callbacks differ: 1.875 / 1.916666667 ms; do not fit one epoch.
Actual maintained FrontEnd with real PI/BFNT/music/effect/config and strict
ROM forwards the original work and matches all twelve loading/readiness
counter assertions per input. PLAY counts 24 / 17, READY 117 / 110; observed
counter fields are assertions only. Sixteen callers (two inputs, four modes,
GNU/UBSan) complete startup with identical compiler output tables.

Zero-work and graphics-only removal reject original sound/display gates.
A display-only frozen-observer control keeps every sound interval and the same
PLAY/READY sound state, yet rejects display counts. Completion, song measures
and wait counts cannot validate the display owner. An actual extra frontend
checks a one-nanosecond fractional-origin crossing, no duplicated logical
refresh and rollback rejection. Rounded cadence count agreement does not
establish exact sub-refresh/IRQ/chip/wait-edge/physical scanout equality.

Eight fresh default CLI routes cover none/pmd/pmdb2/pmd86, full startup,
four demos and fresh OP ready. All 129 files per run equal retained v1395
baseline pins; old receipts are not restamped. Prior raw RGB limits remain
31/40 none, 34/40 active. Muted private Linux Xvfb startup/selection/input/
focus/release/exit passes with zero audio device opens.

Replay: DOSroot .analysis/reconstruction/probes/native-gdc-work-v1396-v2/;
native .analysis/port64/native-gdc-work-v1396-v2/. Source freeze, compiler/caller/
comparison receipts and original parent pins stay protected. Restore retired
build/program/RGB/state inputs from the DOS root:

```sh
python3 .analysis/reconstruction/probes/native-gdc-work-v1396-v2/verify_retention.py --restore
```

Use --prefix for a required subtree and fresh namespaces for another execution.
Lossless retirement reclaims 472.69 MiB: 2697 logical build/program/video files
in 1407 unique blobs plus 16 complete state/item outputs in 2 blobs.
Complete gzip CRC/EOF, member SHA/size/mode/nsmtime and protected proof/frozen
source checks pass. Rejected V1 also retains its own frozen-source archive and negative receipts,
reclaiming 472.65 MiB separately; never attest current source with V1.
Both full CI gates pass (root 441 / native 345), with ledger and diff checks.
Post-CI source-backed caches reclaim 16.69 MiB separately.

Next measure counted-IRQ edge phase independently of GDC blink, then implement
the distinct PMD busy-service and counted-IRQ wait owners,
preserving unsigned counters, reset location and inherited phase. Use v1397
first-two-Logo and zero-fallback checks; do not substitute GDC blink counts or
fit observed durations. Default CPU/bus/resource/graphics inputs stay open.
Full pictures, broader combat/process,
physical/cross-emulator scanout, chip/IRQ/audio, Windows input/audio and MAIN
historical carpet/checkerboard exactness remain open; goal stays active.
Targets remain candidate-local-attested. Continue CPU0/nice19 serial muted
Linux work; Windows GUI/focus/host keys remain excluded.

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
