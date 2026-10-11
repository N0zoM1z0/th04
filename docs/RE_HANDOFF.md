# TH04 current handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

v1380 (native `f6e71fa`) repairs Marisa laser presentation color. Observed MAIN_01_TEXT
0AAF:3704..37C7 (file F9F4..FAB7, 196 bytes), especially 3786, reads
DGROUP 2134:538C before the update tail. Actual original caller/raw blitter
0AAF:1378..13DA runs on four complete original Demo 2 states; the GRCG adapter
explains all 11,384 former color 8↔9 differences with unchanged beam geometry.
Native rendering needs the modulo from before the update tail. GNU and
optimized UBSan now have zero game-area differences in all ten Demo 2 samples.
Five other nonzero samples remain unchanged (Demo 1 frames 1/1952/3996;
Demo 3 frames 3379/3709). Full graphics/RGB and scanout remain open.

All 40 complete text planes, 15,988 selected scalar/count boundaries and
15,984 complete shake states/requests pass. All 125 new capture files agree
between variants; every parent state/shake trace byte remains identical.
Frozen imported readers reproduce both shake receipts except pinned source
hashes. Only view.cpp differs among 509 inputs (manifest f5791751…). Cold view
TUs relink unchanged attested dependencies; there is no new whole-current
cold/CTest claim. Older complete-pool/69-CTest receipts retain their producers.
Recipes: DOS-root .analysis/reconstruction/probes/native-shot-render-v1380/;
receipts: native .analysis/port64/native-shot-render-v1380/.

All jobs are terminal. Main 441/live Ghidra and native 345/target CI pass;
unavailable private native gates skip. Complete parent/current hashes bound
changes to the original CPU beam's 11,384 pixels in four samples; the other
36 index/RGB samples are unchanged. Lossless retirement reclaims 148.8 MiB
before journal cost (354 complete files, 1,044 source-backed caches).
Full restoration/SHA/size/mode/nsmtime/gzip EOF, 17,815 protected hashes,
509 source pins and unchanged DOS fingerprint pass. New/old programs, source
snapshots and failure receipts stay retained. Recovery from DOS root:

```sh
python3 .analysis/reconstruction/probes/native-shot-render-v1380/verify_retention.py --restore
```

Without --restore it performs full temporary readback. Previous v1379 proof
retains its own source scope; do not use it to attest current sources.

Next localize the remaining circle samples and initial background against
actual original draw owners. Broader Boss/death/process/Windows pairing stays open.

Retained v1379 restores the full ordinary 400-row background ring before shake;
its original CPU/MPN observation explains the 430 Demo 1 frame3379 differences,
which remain zero. Its producer and recovery proof retain the 8e77830c source
scope; that old live-source check cannot attest current f5791751 inputs.

Retained v1378 (native `617d65f`) restores MAIN's missing Midboss shake event consumer.
Target-observed MAIN_01_TEXT 0AAF:2246..2315 (file E536..E605, 208 bytes) and
DGROUP 2134:427E/4280/4282/:185C identify x/y/timer/redraw and EGC requests.
GNU and optimized UBSan pass 3,262 original CPU state/request cases and 36
complete labelled-page movement/scroll checks. The cold producer pins 509
inputs, manifest9346e951…: GNU has 71 programs and 69 passing CTests; UBSan
cold-builds the game, trace and shake targets, without a full CTest claim.

Actual muted SDL-dummy idle OP→four demos→OP agrees with original at all
15,984 complete shake globals/movement requests, 15,988 selected scalar/count
boundaries, all nine complete actor/effect pools, and 40 complete 8,000-byte
canonical text-plane samples. All 125 GNU/UBSan capture files are identical.
Removing only the timer event consumer rejects 13 updates per demo, first at
3379/3710/1953/3059, while score/RNG controls still pass. Six malformed/state
trace controls reject. Frozen native and imported DOS readers reproduce both
complete shake receipts, apart from their separately pinned own-source hash.

All 40 samples agree on current/pending pages, zero pending wait and GDC scroll.
Both physical MPN cache banks match every asset image (Marisa Demo2 uses ST10).
Demo1 frame3379 diagnostic game-area differences fall from 55,357 to 430,
confined to y16/17. Investigate the background ring and clipping before vertical
movement next. Initial carpet, laser/circle pixels, full graphics/RGB/font/blink/
scanout, Boss direct offsets, Bomb interactions and broader routes remain open.
Physical edge movement remains an inferred model; CPU controls adapt EGC leaves.
No cropped/masked picture acceptance or historical exact promotion occurs.

Fresh preflight/live Ghidra and main441/native345 CI pass; unavailable private
native tool/Ghidra gates skip. DOS source fingerprint6f5898dd… and DOS products
are unchanged. Provenance remains candidate-local-attested. Private recipes:
root .analysis/reconstruction/probes/native-pages-v1378/; native receipts:
.analysis/port64/native-pages-v1378/. Public Oracle: port64/verify_playfield_shake.py.
Import actual DOS-root scripts/probes first; pass old DGROUP sources only for
attestation. Historical producer502/v1376 and consumer505/v1377 remain immutable.

All jobs are terminal. Lossless retirement reclaims 324,722,688 allocated bytes
(309.7 MiB), before journal cost: 1,390 complete raw/build files and 1,044
source-backed caches. Full restore/SHA/size/mode/nsmtime/gzip EOF, 15,620
protected hashes and 509 source pins pass. Programs, original references,
frozen sources and failed attempts remain retained. The initial ledger Oracle
label was rejected and corrected. Cleanup's first final gate rejected its own
writing log; a separate v2 journal pins the closed log, preserving the failure.
The complete archive had already passed restored readback before retirement.

From DOS root, restore retired raw captures/build intermediates before old
reader replay:

```sh
python3 .analysis/reconstruction/probes/native-pages-v1378/verify_retention.py --restore
```

Without --restore, it checks all recoveries temporarily. The old v1377 proof
keeps its then-current 505-source scope; its live-source check must not be
restamped to 509. Details are in the differential/demo and retention notes.

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
