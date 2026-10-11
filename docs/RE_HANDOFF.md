# TH04 current handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

v1393 (native evidence `7416a91`) separates original OP loading work from explicit waits. Two complete
original GAME.BAT/PMD86 captures change only fixed CPU budget 24,000→36,000;
initial HDI/reset/assets/profile/emulator are identical. Both full decoded OP
loads (69,028 bytes, 804 ordered relocations) agree; load 10FC / DGROUP 2030,
startup relative CS 0A74, sound 0DA1. Thirty attested points yield 41 scalar
boundaries plus decoded entry, complete GDC model replay and rejecting load,
counter, DOS-return and fractional-time controls. Stop is host-controlled
before ordinary menu execution, not DOS process completion.

Logo 0A74:14F5→1523 (PI load return) takes 66.984250 / 44.623833 ms;
0A74:152A→1534 (palette return to PI put return) takes 61.656000 / 41.043750 ms.
The PI phases approximately scale with inverse CPU budget. Gaiji 0A74:0C6B→0C79
is 40.258875 / 34.996528 ms, so a global startup CPU factor is unsupported.
First B installation schedule to Logo play is 255.036542 / 178.822806 ms.
All finer intervals telescope to that age. Each capture has 62 identical file
requests and 61 matched IRET returns before measure entry; parent child-exec OP
has not returned. Both new measure waits span 93 events versus prior 92;
keep each epoch distinct and never hardcode a wait or installation offset.

Native product source is unchanged at 510-file producer
`9cfe100a84ac0a325d498b9b81602298009e462643b2cfa453947fe85bc1b049`.
The v1392 cold GNU/UBSan build, four-profile Demo and private Xvfb proofs retain
their identities; none is rerun or restamped as new acceptance. Current typed
service diagnostics reuse attested closed GNU/UBSan programs and real assets.
Measured ages give measure 2 at 1,645 / 1,641 ms, within 0.388500 / 0.814778 ms
of original play-to-last-callback, below 1 ms sampling. Complete compiler-pair
tables agree. Only changing age to zero completes at 1,707 ms but rejects as
62.388500 / 66.814778 ms late. No age is fitted into the product; default
loading, complete PIC/IRQ and physical chip/audio remain unpaired.

The first broad interrupt observer was terminated during high-frequency PMD
polling. GDB exited zero and its wrapper said passed, but actual completion was
absent. The strict reader rejects that real counterexample. V2 requires actual
41-row menu completion/hash/terminal log; file hooks stop at measure entry and
GDC/timer observations continue. Failed source/log/wrapper/partial gzip stay
immutable. The outer archive cannot upgrade an incomplete inner capture.

Next isolate gaiji hardware/IO waits and define explicit elapsed-work ownership
through startup resource/draw/process transitions. Goal remains active;
MAIN historical exactness stays deferred and targets candidate-local-attested.
No DOS product source/flags/headers change; fingerprint 6f5898dd is unchanged.
Broader paired combat/process, default pictures, physical/cross-emulator scanout
and Windows input/audio remain open. Continue CPU0/nice19 serial muted Linux
work; Windows GUI/focus/host keys remain excluded.

Replay: DOSroot .analysis/reconstruction/probes/native-op-loading-v1393/;
native .analysis/port64/native-op-loading-v1393/. Public reader:
scripts/runtime/verify_op_loading_clock.py. Restore retired HDIs/programs/
expanded inputs before full replay:

```sh
python3 .analysis/reconstruction/probes/native-op-loading-v1393/verify_retention.py --restore
```

Lossless retirement reclaims 103.23 MiB after archive/journal; 22 files
(including eight disposable HDIs) are archived in 60.40 MiB. Full gzip
CRC/EOF/member SHA/mode/size/nsmtime, 33,284 protected proof hashes and all
510 unchanged frozen-source pins pass before and after deletion. Current
compressed clock streams, raw loads, complete/failed observations and proof
receipts remain live. The incomplete first capture remains failed. Earlier
proofs are unchanged. Both full CI gates pass (root 441 / native 345 tests), together with ledger and
diff checks. Another 16.66 MiB of source-backed post-CI caches is removed.

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
