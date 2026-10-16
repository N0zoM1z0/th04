# TH04 reconstruction and native handoff

Updated2026-10-17. Both full development goals remain active. Work on one
bounded claim, keep code/docs English and publish frequent gpt-6.1-sol: commits.

## Current baselines

| Purpose | Identity | Location |
| --- | --- | --- |
| DOS tools | main 4f75f49 plus verified lifecycle evidence commits | This checkout |
| Native telemetry | port/modern-64 8cd826e plus final evidence commits | `.analysis/native/port64-recovery-v1445/` |
| Normal DOS cohort | MAIN778641ab/MAP42d7d2c7 | `.analysis/build/dos-four-products-v1443/` |
| Native cold GNU/cache/UBSan | 566/3747e671 | Native `.analysis/port64/stage2-midboss-v1458-final/{gnu,ubsan}` |

Full native closure:3747e67195391032e6f8a1bbd0eea2ef68fdcc4f59be01adb344b47af8b76c72.
Source/compat DOS code stays unchanged since07f69d3. MAIN200279 bytes/1183relocs;
original MAIN156258/1136,header6144,entry0000:0000. Candidate MAP:
`.analysis/reconstruction/probes/product-20261016-065147-3427b48f-main/source/obj/main-native.map`.
Use config/targets.toml for full hashes and candidate-local-attested provenance.

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

## Verified frontier

Original and reconstructed DOS now complete 3500 Stage2 updates in the same
process. The observed Midboss activates at 2601, enters defeat at 3349,
reaches phase3/HP0 at 3413 and resets at 3414; 86 further updates retain
its inactive raw state. All comparable loop fields, 7861 ordered RNG calls
(707 LCG/7154 ring), nine complete pools, 22 states and 38 configured video
regions agree across 10507 bridge/actor/score/loop snapshots. Each side binds its
own MZ/MAP/CS/DS, opcode, DGROUP, video and full conventional-memory witnesses.
Aggregate remains false for 174 post-reset key and 10507 raw-GDC records.
Older v1458 248/9607, v1457 18/1807 and v1456 302/312/9836 failures remain separate.
These are MAIN replacements with original OP/MAINE/ZUN/assets.

Retained native 8cd826e telemetry and complete 566-file/3747e671 cold programs
match 7003 selected records and 3501 full nine-pool snapshots in both GNU and
optimized UBSan. Consumed inputs, homing, Boss/Midboss state and continuous RNG
agree; 144 volatile post-reset key samples are measured separately. No gameplay
repair was needed. Existing cold GNU 87 programs/83 CTests and UBSan2 remain the
producers. The separate v1458 replay of 9835 selected updates and 59 full RGB/TRAM
elapsed pairs remains valid for these unchanged programs. This new component
accepts the observed Midboss lifecycle, not native Stage2 pictures or natural
OP/loader/UI/CPU clocks.

The lifecycle gate requires actual activation, attack, nonpositive HP, defeat,
exit, reset and at least 64 post-reset updates. Original reset13A9:642C and
source reset157C:661B each have independently decoded callback/active/HP stores
and their own far relocation. Full-memory witnesses immediately around each
transition verify the near invalidate/render and far update null callbacks;
addresses are never normalized across executables. Thirteen lifecycle/MZ and
ten actual original/source callback mutations reject. The bounded debugger
still uses seven cached points, with ten total registered objects on each side.
Complete initial/final CFG/SCR bytes match, all ten full 16-bit score checksums
validate, and Continue changes decoded section1.

Current root-owned bundle: `.analysis/reconstruction/probes/dos-midboss-reset-v1459/`.
Use paired-{gnu,ubsan}, lifecycle-{gnu,ubsan}, result.json, files.json and
reset-callback-controls.json. Programs stay in native
`.analysis/port64/stage2-midboss-v1458-final/{gnu,ubsan}`.

## Next work

Extend the verified 3500 frontier toward Stage2 Boss/clear, preserving actual
inputs/RNG and each executable's own segment/layout ownership. Add native
Stage2 pictures only with independent original elapsed checkpoints. Resolve
the 174 post-reset key and raw-GDC failures; equal consumed inputs do not
accept IRQ/CPU/display timing. Full original/source/native campaigns, four-product
routes, NP2, native Windows, every-frame/raw-plane rendering, audio/input clocks,
pristine provenance and historical exactness remain open. Keep both full goals
active and leave the two deferred MAIN exactness cases alone.

Require --stage2-updates N --require-midboss --require-bounded-watchpoints on
compare_th04_stage_boundary.py. Then run compare_th04_midboss_reset.py with the
same captures, paired native report, frontend and producer receipt. A fixed stop
alone cannot accept defeat. Freeze private collector copies before each run.
The new extra_memory_frames profile adds witnesses without removing baseline
frames. Recovery uses private frozen readers; never mutate old backing paths.

## Replay and retention

Verified retention archives 52 owned generated files into 13 content blobs,
releasing 1136.781 MiB after archive, gzip and both journal files. All 33549
protected hashes verify, including all 32386 parent identities, all 44 prior
finish.late_protected entries and that finish identity. Actual recovery restores
12 owned capture aliases, executes both retained cold GNU/optimized UBSan
programs with fresh original-input-only 3500 fixtures, and replays frozen
DOS/native and callback/lifecycle consumers. Full state/pool vectors and the
failed DOS key/raw-GDC aggregate reproduce. SHA, size, mode and nsmtime verify
before every restored alias retires. The one earlier borrowed v1458 HDI was
verified and retired separately, with no cleanup credit. Keep both current
cold programs/cache and all complete compressed CPU/DGROUP/video/full-memory/
raw/RNG evidence. New backing files are private immutable snapshots.
Run comparison commands from the main checkout; the native checkout links
this root-owned bundle for recovery.

```sh
python3 .analysis/reconstruction/probes/dos-midboss-reset-v1459/replay_restored.py \
  --output-dir .analysis/reconstruction/probes/NEW-reset-recovery
```

This executes native programs and replays recorded DOS consumers; it does not
rerun the emulator. Use fresh outputs. Manual recovery supports recover.py
--restore --path EXACT. Subsequent journals must merge all 33549 protected
identities, every finish.json late_protected entry and that finish identity.
Old journals and the incomplete v1458 reader observation remain unchanged.
The two old public capture/keyboard files remain frozen backing inputs.

Old missing worktrees,native v1432's94 protected files and v1437 MAIN/MAP remain
missing. Never repopulate frozen paths,substitute producers,prune to hide loss
or count absence as cleanup.

## Check and publish

```sh
python3 scripts/build.py --output-dir .analysis/build/NEW-products
python3 scripts/ci.py
git diff --check
```

Run focused comparisons first. Native push: git push origin HEAD:port/modern-64.
Root/native commits publish separately;verify remote heads and clean trees.
Do not mark either full goal complete after this bounded batch. Continue actual
Midboss termination and the remaining original/source/native requirements.
