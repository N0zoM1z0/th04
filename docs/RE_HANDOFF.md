# TH04 current handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

v1369 repairs the Stage4 carpet table's special right-hand columns18/20
(original DGROUP2134:190C,144 B; old source19/21). Cold MAIN199455 B is
07d4d640…; MAP stays2ee564c3… and the complete old/new MZ differs only24 DATA
bytes.193 C++/155 ASM/8 state/4 sprite producers pass with zero reused C++ roots.
The package `.analysis/build/th04-demo-carpet-v1369/` retains old unchanged
OP/MAINE/ZUN; installed Windows packages and native x64 worktree are unchanged.

All four repaired ordinary demos pass15988 input/score/RNG/caller/resident
boundaries. Complete raw video captures compare3996 updates per demo,279809 B
per update: both pages/all four planes, TRAM, full palettes, selectors and
selected programmed GDC fields. The carpet repair removes Demo1's old frame2
blue-band difference; all compared regions now match through490, first remaining
491. Other demos retain identical region hashes/first1729/658/1349. Text/palettes/
selectors/selected GDC fields pass throughout. Full raw GDC scan/raster/FIFO/clock
internals remain diagnostic; this does not accept complete scanout timing.
All four demos still reject full raw graphics parity. Diagnose the remaining
renderer/effect owner from retained streams; no cause is yet proved.

Retained v1367/v1368 DGROUP observations belong to older16132526… MAIN: nine
raw pools24952 B/update plus22 pointer-free states104 B/update pass15984 updates.
All other new MAIN bytes/MAP stay unchanged, but no fresh complete DGROUP capture
is claimed. Boss stays at setup; hit/death/respawn and callback/other globals,
process teardown, ordinary Boss play, native x64 and cross-emulator parity stay
open. Historical exact states are unchanged; new carpet DATA owner is only
source-present. Canonicality remains candidate-local-attested.

Final CI passes423 tests,20-target calibration and live Ghidra/mutation controls.
Post-CI retirement removes529 source-backed caches/8,830,976 allocated B.
Whole-byte-identical copy sharing reclaims161,304,576 B; combined170,135,552 B
(about162.3MiB) before journals.306 protected hashes and26 archived source inputs
recheck. All12 full video streams/earlier states/negative evidence and cold caches
remain; all jobs are terminal. No native worktree or Windows GUI/audio write.
Replay commands, producer/reader archives and coverage are in the focused note.
Current commit identities are obtained with `git log -1` in each worktree.

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

- v1369 complete repaired demo scalar/RNG comparison passes all15988 boundaries.
  Complete video first remaining writes491/1729/658/1349; text/palettes/modes and
  selected GDC fields pass. Old video failure and all raw diagnostics remain.
  Carpet table144 B agrees target; cold source/raw-MZ-only24-byte causal gate
  removes frame2 blue band. ABI compiler/archive/ELF controls plus34 new public
  test groups gate the new surface. Package/recipe and remaining drawings:
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

## Native x64 frontier

The v1362 GNU Reimu A / Lunatic / Turbo0 candidate is now terminal and
accepted by the independent `verify_natural_slowdown.py` reader: 88,249 route
refreshes plus 792 refreshes in a separate Scores process. It reaches all six
stages without Continue, exits registration by Esc, returns to fresh OP, and
stores real section3 clear mask1 at the physical rename and final file. The nine
other decoded score partitions and CFG stay unchanged; no pending file remains.
Final MAIN: stage5/frame13,649, lives7, misses6, score units5,597,294.

Natural density reaches439 bullets. At >=320 there are571 refreshes/287
slowdown2; at >=400 there are240/129. Complete deadlines/terminal counts pass.
At >=400, update P95/P99/max are6.61/8.50/13.37ms with no update exceeding its
own admission period. This is instrumented GNU/private-Xvfb/shared-WSL evidence;
uninstrumented physical FPS and original DOS parity remain unaccepted. Generic
traces do not expose every inner Ending phase. Audio opens remain zero.

Two actual ordinary X early-hit cancellations occur in Stage4, preserving miss
count while consuming stock, starting Bomb, clearing respawn and setting
invincibility255. The last-life proactive policy branch remains dry-controlled
only. Separate ordinary window probes pass early/closed cases (1,039/1,048
refreshes): early X cancels frame394 hit at395; closed-window X at401 remains
rejected at404 (stock2, Bomb inactive, miss1, respawn61). The first late probe
stays failed: its cleanup incorrectly expected MAIN Esc to return to OP, while
the host Escape handler exits MAIN directly. This is a probe cleanup failure,
not a demonstrated Bomb failure or original Escape-parity acceptance.

Retained GNU Reimu A routes:

| Route | Route + independent Scores refreshes | Scope |
| --- | --- | --- |
| Normal/Turbo1 | 89,008 +794 | Six stages/noContinue, physical clear/freshOP/restart |
| Lunatic/Turbo1 | 88,927 +790 | Physical clear; dense slowdown2 absent |
| Lunatic/Turbo0 | 88,249 +792 | Physical clear plus natural dense slowdown2 gates |
| Extra | 30,388 +790 | NoContinue, full eight A gaiji, physical clear/restart |

Prior UBSan Normal all-clear acceptance is revoked: mask0x19 is an unplayed
sentinel even though bit0 is set. The v1360 GNU Turbo0 attempt also stays failed
(88,267 refreshes, Final Stage miss13, masks0x19); its separate795-refresh
Scores reader and bounded dense slowdown observations remain valid. Require
mask<4 plus the selected shot bit, never bit0 alone. All these jobs are terminal;
do not poll or revive dated PID/tool handles from historical active-job files.

Registration, lifecycle/Continue/HUD, stage/Ending/Extra, score/config, demo,
MusicRoom/unlocks and muted sound owners have separate component/integration
evidence. Eight actual GNU/UBSan Continue cases and ten GNU setup/corrupt-file
cases are retained. Startup combinations cover27 GNU/UBSan and19 earlier
Windows cases. Broader character/shot/rank/Ending/Extra routes, actual Windows
display/input, physical audio and uninstrumented performance remain open.

No C++ rebuild: compiled producer485 inputs/`00af24f7…`, GNU game
`dbe17225…`, UBSan `029e7ba1…`, Windows `5b6cf2c3…` remain v1356. The completed
route uses frozen consumer491/`d25ba16e…`. Actual Bomb probes use archived
consumer492/`3135f76e…`; handoff formatting changes only that Python probe's
layout, preserves its AST, and freezes current492/`4ed57dab…` separately.
Do not restamp old runtime receipts with current source identities.

Primary native receipts: `.analysis/port64/bomb-input-v1362/` (completed route,
independent-natural-v1364.json, actual-rescues-v1364.json) and
`.analysis/port64/bomb-window-v1364/` (early/late/failed probes, independent
readback, both492-input source snapshots). All paths here are relative to the
native worktree. See its `docs/port64/evidence/host-window.md` for replay details.

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
are the useful parts to adapt. Complete DOS demo captures now exist, with a
repaired Demo1 frontier. Full actor/presentation/process parity and
native RNG seed/ring/call-count observations remain open.

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
