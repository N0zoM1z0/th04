# TH04 reconstruction and native handoff

Updated2026-10-17. Both full development goals remain active. Work on one
bounded claim, keep code/docs English and publish frequent gpt-6.1-sol: commits.

## Current baselines

| Purpose | Identity | Location |
| --- | --- | --- |
| DOS tools | main b7fe3d8 plus cached-reader/final evidence commits | This checkout |
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

Original/reconstructed DOS complete3200 Stage2 updates, with Midboss activation
at actor2601 and600 battle updates. The NPC remainsactive at3200 withHP100,
phase1/frame39; defeat is not accepted. Comparable loop fields and7787 ordered
RNG calls (707 LCG/7080 ring), nine full pools,22 states and38 configured video
regions agree across9607 bridge/actor/score/loop snapshots. Own MZ/MAP/CPU/DS/
opcode, full DGROUP/video/resident and conventional-memory witnesses bind each
producer. Aggregate remainsfalse for248 post-reset input and9607 raw-GDC records.
Older v1457 18/1807 and v1456 302/312/9836 vectors remain independent failures.
These are MAIN-only replacements with original OP/MAINE/ZUN/assets.

Native code8cd826e adds direct22-byte Midboss/active telemetry and a16-bit
extent guard; no gameplay repair was needed in this span. Complete566-file
3747e671 closure, coldGNU87 programs/83CTests and optimizedUBSan2 match6403
selected bridge/init/actor-score records,3201 complete9-pool snapshots, consumed
inputs, homing, Boss/Midboss and continuous RNG. Full state/pool wires agree
across programs. Native116 volatile post-reset samples remain separately
measured. Both programs also reproduce the distinct9835 selected-update,
59 full640x400 RGB/TRAM elapsed pairs/177 observations, with real Continue,
physical saves,title/popup and actor gates. Stage2 native pictures and natural
OP/loader/UI/CPU clocks are not accepted by this component.

The initial reader created and disabled a new watchpoint per checkpoint;
standalone GDB confirms disabled objects remain registered. Its controlled
stop at1709 remainsincomplete. The replacement reuses seven own-file boundary
watchpoints; actual original/source maxima are10 including3 baseline across
all9607 snapshots. The public class survives3200 realGDB switches atseven
cached points. Six resource-data mutations,ten new capture-data mutations and
eight earlier extent/observation guards reject. Old600 semantic vectors remain
identical. Complete physical CFG/SCR bytes match; allten16-bit score checksums
validate and ranked Continue changes decoded section1.

Root-owned bundle: `.analysis/reconstruction/probes/dos-stage2-midboss-v1458/`,
privately linked in native. Use paired-final-{gnu,ubsan},native-final-result,
files,midboss-lifecycle,cached/captures and all actual negative/control receipts.
The initial original capture is intentionally incomplete;never restamp it.

## Next work

Continue through actual Midboss reset/defeat from the verified3200 frontier;
do not infer death from a fixed stop. Consider a recorded lifecycle stop with
an independently checked bound, preserving continuous raw inputs/RNG and each
own CS/DS/MAP. Add native Stage2 pictures only with actual original checkpoints
and elapsed ownership. Resolve reset/IRQ/read timing behind248 and older key
failures; equal consumed input does not waive GDC or physical timing.
Full original/source/native campaigns, four-product routes, NP2, native Windows,
every-frame/raw-plane rendering, audio/input clocks, pristine provenance and
historical exactness remain open. Do not reopen the two deferred MAIN cases.

The native diagnostic accepts16-bit extents;3200 is the verified extent,not
full-stage acceptance. Require both --require-midboss and
--require-bounded-watchpoints with --stage2-updates N for new paired claims.
The public th04_stage_boundary_gdb.py maintains a fixed cache; future captures
must freeze private copies before running. Preserve own-file address and
raw-frame/RNG ordering when extending the lifecycle or adding UI waits.

## Replay and retention

Archive311 owned generated files into125 content blobs,
releasing1288.430 MiB after archive, gzip and both journal files. All32386
protected hashes verify, including28575 parent identities, all51 prior
finish.late_protected entries and the old finish identity. Actual recovery
restores17 owned aliases (12 complete-capture aliases,4 incomplete-capture
aliases and the private executable), executes allthree pinned native programs
from fresh input-only fixtures, and replays frozen DOS/native consumers.
Both actual standalone GDB probes reproduce growth versus bounded caching;
the controlled original still rejects. Every restored alias verifies SHA,
size,mode and nsmtime before retirement. Earlier borrowed13 reader-control
aliases and4 elapsed-fixture aliases receive no cleanup credit. Keep current
final GNU/cache/UBSan cores and all compressed complete/incomplete evidence.

```sh
python3 .analysis/reconstruction/probes/dos-stage2-midboss-v1458/replay_restored.py \
  --output-dir .analysis/reconstruction/probes/NEW-midboss-recovery
```

Use fresh names. Keep complete compressed DGROUP/video/raw/CPU/memory/RNG and
current final GNU/cache/UBSan cores. Preserve the prior28575 plus51 late hashes,
the current journal and its finish.late_protected in subsequent retention.
Frozen recipes use private source snapshots;the legacy two public capture/
keyboard files retain their old hashes. Do not count borrowed/repeated aliases.

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
