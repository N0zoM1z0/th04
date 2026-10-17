# TH04 reconstruction and native handoff

Updated2026-10-17. Both full development goals remain active. Work on one
bounded claim, keep code/docs English and publish frequent gpt-6.1-sol: commits.

## Current baselines

DOS tools:main0223bc1 plus current wait-owner/evidence commits.
Native:port/modern-64 8b55013 plus correctedcustom-wire/evidence commits.

Native checkout: `.analysis/native/port64-recovery-v1445/`; current programs/cache:
`.analysis/port64/stage2-boss-v1460-wire-final/{gnu,ubsan}` inside it.
Full 566-file closure:
`bcd114bb581588aaaf1fc0de804c04f182ea97ee5439b34027736caec895dab4`.
Prior 3747 cold programs/cache remain live; superseded 6a is recoverable.
DOS source/compat is unchanged since 07f69d3. Cohort:
`.analysis/build/dos-four-products-v1443/MAIN.EXE`,200279 bytes/1183 relocations,
SHA778641ab...; own MAP42d7d2c7... at
`.analysis/reconstruction/probes/product-20261016-065147-3427b48f-main/source/obj/main-native.map`.
Original MAIN 156258 bytes/SHA077440a3...,header 6144/1136 relocations,entry 0000:0000.
Targets stay candidate-local-attested; pristine provenance remains open.

## Startup

Read AGENTS.md,RE_HANDOFF,ARCHITECTURE,RE_WORKFLOW,ORACLES,KNOWLEDGE_BASE and
relevant skills; query the knowledge ledger before new experiments.

```sh
git status --short
git ls-remote --heads origin main port/modern-64
git -C .analysis/native/port64-recovery-v1445 status --short
taskset -c 1 nice -n 19 python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/ghidra.py th04-main check
```

Use one low-priority CPU and one Borland/Wine writer. Keep launches muted/
headless; no Windows GUI, focus changes or host keys. Keyboard stimuli stay
inside the private recorded emulator. Never inject expected state/RNG/phase.

## Active clear observation (v1461)

The v1461 batch follows Stage2 defeat/clear. Fresh target/source own-MZ CFG
proves nonzero quit returns after score, without a following Stage2 loop
(original0AAF:0207, source0708:07BD). The first new loop-exit collector was
controlled-stopped during its unfinished Stage1 prefix and remains failed.
A distinct score-exit capsule now observes actual quit2/return/free/Stage3 init
and one full update under a11000 budget. Twelve host-only dispatch mutations
reject; actual original/source clear acceptance is pending. Native-only scouts
forecast Continue8132, defeat9809, postdialog9905 and departure10394; these do
not widen the accepted8000 frontier. Current bundle:
`.analysis/reconstruction/probes/dos-kurumi-clear-v1461/`, score-captures.log and
capture-score/. Keep the stopped capsule/data and all parent38121+22 late hashes.

## Verified frontier

Original and reconstructed DOS complete 8000 Stage2 updates after the same
Stage1 return at 9837. Comparable fields, 10161 ordered RNG calls (708 LCG/9453 ring),
nine full pools, 22 states and 38 configured video regions agree across 24007
bridge/actor/score/loop snapshots; 17838 independent raw loops bind the route.
The aggregate remains false: 422 post-reset key and 24007 raw-GDC records differ.
Six additional own-file blocking CPU/stack/full-memory observations have equal
fields, full pools/states and configured video, with six raw-GDC differences.
These are MAIN replacements with original OP/MAINE/ZUN/assets; older failed
vectors remain independent.

Continue at 5363 and pre-Boss dialogue at 6982 are independently observed on both
DOS files. Own player entries establish 5364 input 32 and 6983 input 8192, although
the preceding 6982 loop input is 32. The native adapter uses real FrontEnd keys;
189 Continue and 400 dialogue polls suspend gameplay and resume one update each.
All other loop-to-player input checks stay strict. Five fixed auxiliary watches
plus seven cached boundary points keep each debugger at 15 registered objects.
Fourteen target-record and 12 native-record mutations reject; 11 earlier actual
CLI plan negatives and 21014 old/new reader records remain valid.

Current complete 566/bcd114bb cold GNU 87 programs/83 CTests and optimized UBSan 2
match 16003 selected scalar records and 8001 complete nine-pool snapshots, actual
consumed input, homing, Boss/Midboss and continuous RNG. 278 volatile native
post-reset key samples remain separately measured. Both actual programs also
reproduce the legacy 3500 wires and the separate 9835 selected updates/59 full
RGB-TRAM pairs/177 observations with recorded elapsed inputs.

The superseded 6a cold program failed 602 custom-pool records at 7399..8000. Its
exporter always used the Yuuka6 view and omitted six existing Kurumi rays.
Pinned original MAIN 13A9:4F84 independently observes a byte flag, word members,
26-byte stride and six entries at DGROUP 2134:B204; source own MAP locates the
allocator 157C:335C and pool 242E:4544. The corrected exporter writes all six
actual records into the first 156/832 bytes and preserves the full tail and
inactive coordinates. All other exported bytes stay identical. Gameplay logic
was unchanged; keep the failed program/report as a counterexample.

Boss initialization is observed at 6983 with 4800 HP; phase 1 starts at 7303 and phase 2
starts at 7334. All 1018 battle actor updates through 8000 match; the final Boss is
phase 2/3811 HP. Defeat and clear remain open. The prior Midboss defeat at 3349 and
reset at 3414 remain accepted under their separate callback/lifecycle gate. Complete
initial/final physical CFG/SCR files agree and all ten 16-bit score checksums pass.

## Next work

Advance the actual Stage2 Boss toward defeat/clear using own-file inputs,
RNG and segment/layout evidence. Add native Stage2 pictures only with independent
original elapsed checkpoints. Resolve the 422 post-reset key and raw-GDC
failures; equal consumed inputs do not accept IRQ/CPU/display timing. Full
original/source/native campaigns, four-product routes, NP2, native Windows,
every-frame/raw-plane rendering, audio/input clocks, pristine provenance and
historical exactness remain open. Keep both full goals active and leave the
two deferred MAIN exactness cases alone.

Use --stage2-updates N --require-midboss --require-bounded-watchpoints
--require-stage2-waits on compare_th04_stage_boundary.py for this route.
A fixed stop cannot accept Boss defeat. Freeze producer/readers before new
captures; never modify closed capsules or their live backing inputs.

Root-owned evidence: `.analysis/reconstruction/probes/dos-stage2-boss-v1460/`. Run private recovery from the main checkout.

## Verified recovery

Verified retention archives 3095 owned generated files into 1678 content blobs,
releasing 5238.078 MiB after archive, gzip, both journal files and new frozen replay snapshots. All 38121
protected identities verify, including 33549 parents, all 38 previous late
identities and that finish identity. Current 566/bcd114bb GNU 87/cache/UBSan 2 and
prior 3747 programs/cache stay live. Complete compressed original/source CPU,
DGROUP, video, conventional memory, raw/RNG/keyboard/UI data remain preserved.
The superseded 6a 602-record failure and its exact program are recoverable.

Actual recovery restores 12 owned capture aliases and the exact old 6a GNU program.
It executes that program and both current cold GNU/optimized UBSan programs with
fresh original-input-only 8000 fixtures. All four output wires reproduce: old 602
custom failures and current zero differences. Frozen paired DOS/native/UI
reducers execute for before and current GNU; UBSan's four wires equal GNU and its
original full paired report. No second restored UBSan reducer is claimed. Both
actual reductions retain 422 key/24007 main-GDC/6 auxiliary-GDC failures. All 13 aliases
verify SHA, size, mode and nsmtime before retirement. The earlier borrowed one HDI
plus four legacy aliases retire separately with no new cleanup credit.

```sh
python3 .analysis/reconstruction/probes/dos-stage2-boss-v1460/replay_restored.py \
  --output-dir .analysis/reconstruction/probes/NEW-stage2-boss-recovery
```

Run from the main checkout. This reexecutes native programs and recorded DOS
consumers, not the emulator. Use fresh outputs; recover.py --restore --path EXACT
supports manual recovery. Subsequent journals must merge all 38121 protected
identities, every finish.json late_protected entry and that finish identity.
The two old public capture/keyboard files remain frozen live backing inputs.
Historical missing worktrees, native v1432's 94 files and v1437 MAIN/MAP remain explicit
gaps; never recreate frozen paths, rebind receipts or count missing files as cleanup.
Actual current GNU/UBSan final MIKO.CFG and GENSOU.SCR bytes also match the
attested original DOS8000 files exactly, including the second Continue update.
The separate native-physical-files-attested.json binds both producer receipts.
Both full goals stay active; Stage2 Boss defeat/clear, native pictures, timing,
campaigns, NP2, Windows, pristine provenance and historical exactness remain open.
