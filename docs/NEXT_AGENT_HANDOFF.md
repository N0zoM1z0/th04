# TH04 reconstruction and native handoff

Updated2026-10-17. Both full development goals remain active. Work on one
bounded claim, keep all code/docs English and use frequent `gpt-6.1-sol: ...`
commits/pushes. Historical function acceptance is not whole-game completion.

## Current baselines

| Purpose | Identity | Location |
| --- | --- | --- |
| DOS tools/boundary evidence | main cb34388 plus final evidence commits | This checkout |
| Native semantic repair | port/modern-64 3340389 plus final evidence commits | `.analysis/native/port64-recovery-v1445/` |
| Normal DOS cohort | MAIN778641ab/MAP42d7d2c7 | `.analysis/build/dos-four-products-v1443/` |
| Current native cold programs/cache | 566/187b574f | Native `.analysis/port64/stage-epoch-v1457-final/{gnu,ubsan}` |

The native full closure is187b574fe1e099d3344f9150d6a30b879772545d9219521f6cae4dcb011a74c4.
DOS MAIN200279 bytes/1183 relocations; original MAIN156258/1136, header6144,
entry0000:0000. Own candidate MAP:
`.analysis/reconstruction/probes/product-20261016-065147-3427b48f-main/source/obj/main-native.map`.
Full target hashes/provenance are in `config/targets.toml`; canonicality stays
candidate-local-attested. Old `.analysis/build/th04/` is not the current cohort.

## Startup and limits

Read AGENTS.md, RE_HANDOFF, ARCHITECTURE, RE_WORKFLOW, ORACLES, KNOWLEDGE_BASE and
relevant skills. Query the knowledge ledger before new experiments.

```sh
git status --short
git ls-remote --heads origin main port/modern-64
git -C .analysis/native/port64-recovery-v1445 status --short
taskset -c 1 nice -n 19 python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/ghidra.py th04-main check
```

Use one low-priority CPU, one Borland/Wine writer and muted headless launches.
No Windows GUI, focus changes or host keys. Emulator keyboard stimuli remain
inside the recorded private scenario. Never patch target bytes or inject
expected native gameplay/RNG/phase state. Historical exactness remains separate.

## Verified frontier

Original and reconstructed DOS actually return from Stage1 at9837, after
the old actor9836 stop, then initialize Stage2 in the same process.600 complete
Stage2 updates agree on comparable loop fields and5656 ordered RNG events,
nine complete pools,22 state blocks and38 configured video regions across1807
bridge/Stage2 records. Actual CPU/CS:IP/DS/opcode, full DGROUP/video/resident,
28 full conventional-memory witnesses and601 Stage2 raw-loop contexts bind the
observations to each artifact's own MZ/MAP. Absolute LCG calls rise354 to707
in Stage2 initialization; its353 draws continue the existing process state.

Aggregate DOS acceptance remains false:18 post-reset input and1807 full raw-GDC
snapshots differ. The independent older v1456 control/video pairs retain302/312
post-reset input differences and9836 raw-GDC differences, despite equal nine
pools,22 states,38 configured regions and complete CFG/SCR bytes. These are
MAIN-only replacements with original OP/MAINE/ZUN/assets, not full four-product
campaign parity. Target provenance remains candidate-local-attested.

Native code3340389 fixes the omitted400-record point-number clear and the
query that returned old Orange before prepared Kurumi became active. It does
not change a guessed frame boundary. Complete source closure566/187b574f,
fresh GNU87 programs/83CTests and optimized UBSan2 pass. Both actual programs
match1203 selected bridge/init/actor-score records and all nine complete pools
at Stage2init+600updates, consumed inputs, homing, Boss fields and continuous
RNG. Their Stage2 state/pool wires are identical. Sixteen volatile post-reset
key snapshots remain separately measured against native consumed input.

Both current programs also reproduce the separate v1455 elapsed fixture:
9835 selected updates,59 complete640x400 RGB/TRAM pairs and177 full native
observations, with real input/homing/pools/Boss/Continue/save/title/popup gates.
Historical default-logical failures and natural OP/loader/UI/CPU clocks remain
unresolved. No Stage2 picture or autonomous timing acceptance follows.
Initial565-file diagnostic build omitted the new include from PORT_FILES and
is retained as diagnostic only; final builds use the complete566-file closure.

Evidence route: [bounded differential](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md)
and native `docs/port64/evidence/stage-lifecycle.md`. Current bundle:
`.analysis/reconstruction/probes/dos-stage2-boundary-v1457/`.
Use `native-final-result.json`, `public-final-{gnu,ubsan}`, legacy-regressions,
original/candidate attestations, target-init owners, actual negatives and captures.
The initial565-file build and earlier failed vectors stay immutable.

## Next bounded work

1. Extend actual Stage2 frame600 toward the Midboss; use each file's own code/
   data segments and STD. Original stage loop returns at9837, not the old9836
   actor stop. Native already naturally matched that boundary; do not invent
   a frame correction. Preserve inactive bytes and setup/reset ownership.
2. Measure rendering and elapsed ownership before accepting new Stage2 pictures.
   Resolve reset/IRQ/read timing behind old302/312 and new18 key differences;
   raw GDC, physical timing and native raw-plane identity remain separate gates.
3. Continue full four-product process/campaign and independent emulator work.
   Older nine-entry/second-MAIN components do not accept OP confirmation/timing,
   full endings/routes, NP2, native original-campaign parity or physical scanout.

## Replay and cleanup

Verified retention archives2732 owned generated files into1676 content blobs,
releasing1385.176 MiB after archive, gzip and both journal files. All28575
protected hashes verify, including all24890 parent identities. Actual recovery
restores12 owned capture aliases and the pre-fix executable, executes it and
both retained repaired GNU/UBSan programs from fresh input-only fixtures, then
replays the frozen DOS/native consumers. The old native failure remains false;
both repaired vectors remain true. All13 restored aliases verify SHA, size,
mode and nsmtime before retirement. Four borrowed v1455 aliases were separately
verified and retired without cleanup credit. Current final GNU/cache/UBSan
cores and all complete compressed original evidence remain live. New backing
paths are immutable private files; older journals and missing-file gaps remain.

```sh
python3 .analysis/reconstruction/probes/dos-stage2-boundary-v1457/replay_restored.py \
  --output-dir .analysis/reconstruction/probes/NEW-stage-epoch-recovery
```

Use fresh names. It restores13 owned aliases, actually executes all three native
programs, replays captured DOS comparisons and retires verified aliases again.
Manual readers need the exact image/font/raw aliases restored via `recover.py`.
Keep complete compressed CPU/DGROUP/video/memory/raw/RNG evidence and current
final GNU/cache/UBSan cores. New recipes use private immutable sources, not
mutable maintained paths. The legacy two public capture/keyboard paths remain
frozen; use separate new tools or private snapshots for future captures.

Old missing worktrees, native v1432's94 protected files and v1437 MAIN/MAP remain
missing. Do not repopulate frozen paths, conceal loss with pruning, substitute
producers or count absence as cleanup. Older journals remain valid separately.

## Build, check and publish

```sh
python3 scripts/build.py --output-dir .analysis/build/NEW-products
python3 scripts/ci.py
git diff --check
```

Run focused comparisons first. Native push: `git push origin HEAD:port/modern-64`.
Root and native commits publish separately; verify both remote heads and clean
trees. Do not mark either full goal complete after this bounded batch. Continue
from current ledgers/receipts, preserve failed gates and publish concrete progress.
