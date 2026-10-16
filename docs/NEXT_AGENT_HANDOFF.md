# TH04 reconstruction and port64 handoff

Updated 2026-10-16. Both development goals remain active. Verify the current
machine and select one bounded task. Historical exact-function counts are not
whole-game completion metrics. Keep all new code and documentation in English.

## Published branches and local availability

| Purpose | Published baseline | Availability |
| --- | --- | --- |
| DOS reconstruction, comparison tools and ledgers | `main: 88807717028184f6ab2c9a9241082f068ff8183c` | Current checkout; later evidence commits follow this baseline |
| Native x64 source | `port/modern-64: c0a1060371c5f8ba758ca8b10f6cbc99063ba3d6` | Remote and local Git objects exist; old working directories are missing |

The old `.analysis/worktrees/` directory was absent at the 2026-10-16 audit,
although Git retains its registrations. This includes `native-natural-clear-v1432`,
`native-main-pause-v1431` and `dos-smem-page-copy-v1423`. The reason is unknown;
do not count their absence as cleanup or claim their private files remain live.
Do not prune registrations to conceal the loss or overwrite frozen branches.

Root v1437/v1436 captures, compressed memory/video, reports and recovery archives
remain. Native v1432 root reports/archives remain, but all 94 protected files
listed under its missing trees are unreadable. Historical DOS v1437 receipts
also reference a missing candidate MAIN/MAP. Complete historical replay needs
those original sources of evidence. New builds/captures must have new identities;
never alter an old receipt or seal to accept different paths or hashes.

New v1438 root MAIN/MAP files and four captures are now available independently
of those trees. MAIN is `.analysis/build/dos-boss-video-v1438/MAIN.EXE`; its MAP
is `.analysis/reconstruction/probes/product-20261016-041217-299bcab8-main/source/obj/main-native.map`.
Their hashes reproduce the historical content identities below, with new
producer receipts. Initial cold compilation linked successfully but its wrapper
refused publication after comparison-tool changes altered the input fingerprint.
Subsequent verified cache publication reused 192 C++ objects and relinked. This
is not a cold deterministic exact replay. Both attempts remain retained.

```sh
git status --short
git ls-remote --heads origin main port/modern-64
git worktree list --porcelain
taskset -c 1 nice -n 19 python3 scripts/preflight.py
python3 scripts/status.py
```

Read `AGENTS.md`, [current state](RE_HANDOFF.md), [architecture](ARCHITECTURE.md),
[workflow](RE_WORKFLOW.md), [knowledge base](KNOWLEDGE_BASE.md) and relevant
`.agents/skills/`. Query `config/knowledge.csv` before repeating experiments.
Target preflight passes; provenance remains `candidate-local-attested`, not proof
of an official pristine dump. Before using target disassembly, also run
`python3 scripts/ghidra.py ARTIFACT check`.

After verifying no competing writer, restore native development into a fresh
branch/directory rather than reusing a missing frozen tree. For example:

```sh
git worktree add -b work/port64-next .analysis/worktrees/port64-next origin/port/modern-64
git -C .analysis/worktrees/port64-next status --short
```

Choose another name if it exists. Main commits do not publish native changes;
commit and push each branch separately and verify its remote head.

## Recorded results and open requirements

The following rows describe historical producers. They are not fresh replay
claims. Commands, evidence IDs and ownership are in the
[DOS differential note](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md),
[native status](PORTING_STATUS.md), `config/evidence.csv` and `config/knowledge.csv`.

| Extent | Recorded agreement | Open or failed requirements |
| --- | --- | --- |
| Four bundled Demos, 3,996 updates each | Consumed input, score/RNG, nine complete pools, 22 state blocks and every configured video region; Demo 1 divergence fixed | Physical scanout and full ordinary game |
| Ordinary Normal ReimuA, 3,996 updates, v1434-v1436 | Two independent pairs, 36 fields, 1,369 ordered RNG calls, natural deaths/respawns; all 38 v1436 video regions agree | Raw GDC timing differs every frame; v1436 companion aggregate fails for 155 post-reset input samples |
| Ordinary Boss prefix, 7,500 updates, v1437 | Consumed input, 36 fields, 2,837 ordered RNG calls, nine pools and 22 state blocks; Boss phases 0/1/2 and five natural losses | Aggregate fails for 258 post-reset input samples; no complete Boss pictures, defeat or campaign acceptance |
| Fresh ordinary Boss video, 7,500 updates, v1438 | All 38 full video regions, consumed input/36 fields/2,837 RNG calls, nine pools and 22 state blocks; independent no-video scalar controls | Raw GDC differs every frame; video companion aggregate fails for 253 post-reset samples, separate controls for 259; no defeat, natural exit or campaign |
| Native v1432 GNU / optimized UBSan | Easy ReimuA, Normal ReimuA, Normal MarisaA and Extra ReimuA unlocked by the same Normal save; complete logic/save agreement, mask=1, no Continue | Headless `render_every=0`; no complete original-picture, Windows input/audio, physical timing or original full-game acceptance |

Ordinary DOS pairs replace MAIN only; OP/MAINE/ZUN/assets/reset files remain
original. They do not validate a complete route through four reconstructed
executables. Post-reset differences 156/155/258 belong to v1435/v1436/v1437
respectively and must not be interchanged. Equal consumed inputs do not erase
intermediate input differences. New v1438 counts 253/259 belong to separate
video/control captures. Three pools staying empty in shorter prefixes
does not cover their active paths.

The Demo 1 frame-3343 divergence in old handoff `55cf73e` is resolved. Midboss
toggle, carpet columns, bullet invalidation dimensions, point-number glyph and
lighting-animation-cell fixes have separate cold-build evidence in the focused
note. Historical authored exact is 661/663: OP 93/93, MAIN 493/495, MAINE 72/72,
ZUN 3/3. MAIN's separate function-ledger denominator 494 is a different measure.
The two deferred carpet/checkerboard exact cases remain deferred.

## Next tasks

1. Drive real Game Over/Continue/process routes from the newly paired Boss
   prefix. The original naturally reaches
   Game Over at frame 7,547. Release held Shot before operating its release-first
   wait. Do not change lives/RNG/clock or diagnose an IRQ failure from a single
   Count1=0 sample. Record Continue, Quit, MAINE, fresh OP/second MAIN and resident
   lifetimes separately; the current single-MAIN observer does not imply
   multi-process support.
2. Recover native development and historical replay inputs. Search for the
   original missing storage; otherwise build published source under a new
   namespace and collect independent new evidence. The new root MAIN/MAP does
   not restore the native producer, old trees or a fresh four-product build.
3. Extend past the paired 7,500-update Boss prefix toward defeat and complete
   process routes with independent input/RNG/pool controls and full video.
   v1438 now passes all configured video regions over that prefix, with terminal,
   metadata and 38 actual-frame counterexamples. The 3,996 default remains strict.
   Preserve all post-reset/raw-GDC failures when extending the acceptance extent.
4. Align native state/effects using identical consumed inputs and explicit
   state boundaries: original DOS, reconstructed DOS, then native. Expand game
   area checks to HUD/page changes/text/palettes/full pictures. GNU/UBSan equality
   and old 40-area samples do not prove original full-picture agreement. Modify
   source for reproduced differences or a concrete ownership requirement.

The observed original Game Over stack is relative MAIN `0AAF:3B1E` to
`130E:0149` input_wait release loop to `130E:00E3` frame_delay(1). The actual
far wait call is `0AAF:3B19`. Historical v1437 bounded terminal is relative MAIN
`0AAF:01B3` at load `10FC`; GDB flushes and kills that capture. Its
`natural_game_exit=false` is intentional and must not become a natural-exit claim.

Native save admission requires all ten complete 16-bit section checksums,
character/rank/shot partitions, `mask < 4` and the selected shot bit, plus Ending,
stage coverage, registration/fresh OP. The older window/UBSan Normal claim with
sentinel `0x19` remains revoked; newer headless results do not restore it.

## Historical replay identities

| Evidence | Root-relative location |
| --- | --- |
| v1437 reports/controls/recovery | `.analysis/reconstruction/probes/dos-ordinary-boss-v1437/` |
| v1437 final captures | `.analysis/runtime/candidates/dos-ordinary-boss-v1437-{original,candidate}-7500/` |
| v1436 video | `.analysis/runtime/candidates/dos-ordinary-video-v1436-{original,candidate}/` |
| v1434 independent plain baselines | `.analysis/runtime/candidates/dos-clock-input-v1434-v8-{original,candidate}/` |
| Pinned observer receipt | `.analysis/runtime/emulators/demo-observer-build-v1365/receipt.json` |
| Native v1432 root reports | `.analysis/reconstruction/probes/native-natural-clear-v1432/` |
| New v1438 work | `.analysis/reconstruction/probes/dos-boss-video-v1438/` |

Historical v1437 ordinary MAIN is 200,279 bytes,
SHA-256 `f21a5c7ca38ebaee0e0ae544540ed2c36b4429cd846c3a12d8a5ccb887728cd8`.
Its missing build directory is
`.analysis/worktrees/dos-smem-page-copy-v1423/.analysis/build/smem-page-copy-v1423/`.
Its MAP was that tree's
`.analysis/reconstruction/probes/product-20261012-005819-ac6f4873-main/source/obj/main-native.map`,
SHA-256 `2b6a74a073f98a2b53ab9583ad1bfee5775886b8954240b1efab2c5d089bdf59`.
Old root `.analysis/build/th04` or `th04-normal` is not this producer.

Native frozen C++ producer is `554/31e6b3d7...`, reader consumer
`554/a79f199f...`; full digests and the 553 unchanged-input contract are in
[the route note](reconstruction/product/TH04_NATIVE_NATURAL_ROUTES_V1432.md).
GNU/UBSan executables were in the missing `native-main-pause-v1431` tree under
`.analysis/port64/native-main-pause-v1431-v5/`.

Only after finding and verifying the original MAIN/MAP and restoring required
raw/image aliases may the historical complete comparison run:

```sh
taskset -c 1 nice -n 19 python3 scripts/probes/compare_th04_bounded_ordinary.py \
  .analysis/runtime/candidates/dos-ordinary-boss-v1437-original-7500 \
  .analysis/runtime/candidates/dos-ordinary-boss-v1437-candidate-7500 \
  --original-main .analysis/targets/th04/main.exe --output /tmp/th04-boss-prefix.json
```

Expected exit 1 means scalar/pools/states agree but 258 post-reset samples differ.
A missing-file error is not that expected result. Use a receipt-verified frozen
source snapshot if old source hashes differ; never re-sign the historical producer.

## Resource, cleanup and finish rules

Use CPU 1 / nice 19 for heavy work and serialize Borland/Wine builds. Keep runs
muted and headless or on private Linux Xvfb. Do not open Windows GUI, take focus
or inject host keys. The initial root analysis footprint was about 6.3 GiB;
missing worktrees do not count as verified reclaimed space.

Keep scratch/generated files in fresh `.analysis/` namespaces and retain failed
producers. Clean only this session's explicitly owned, recoverable intermediates.
Before deletion verify archive SHA/CRC, complete reconstructed contents,
restored mode/nsmtime and protected files. Never delete all analysis, old trees
or all builds. Keep complete compressed streams, inputs, compilers, receipts,
source snapshots and required MAPs.

Use each v1437/v1436 `recover.py --restore --prefix PATH` selectively. v1434 has
its own `recover.py`; its old `verify_retention.py` points at a superseded full
archive. Native v1432's protected-file check currently fails for 94 files; its
archive cannot restore the entire tree. Return temporary aliases to archived
state after use and do not count that as new cleanup. The prior audit checked
24/8 v1437/v1436 archived paths without expanding large files.

v1438's own `recover.py` checks/restores 16 image/font/raw paths in 24 blobs.
Verified full content/CRC/temporary mode/nsmtime and protected-file checks release
194.625 MiB net with a 1.069 MiB archive. Complete compressed streams, new
MAIN/MAP, receipts, source and failed publication evidence remain live. Its
video comparison exits 0; its companion comparison exits 1 for 253 input samples.
The initial post-extension CI passes 495 public tests plus private target,
database and Oracle gates. Native CI was not rerun in the missing trees.

After shared headers/flags/segments/link order/layout changes, invalidate and
cold-replay affected accepted units. Source recovery, runtime agreement and
historical exactness are separate claims. Finish with the focused comparison,
`taskset -c 1 nice -n 19 python3 scripts/ci.py` and `git diff --check`. Update
README, RE_HANDOFF and the existing focused note when evidence changes. Verify
no original programs/assets/private archives/credentials are staged. Commit
messages require the `gpt-6.1-sol: ` prefix; commit/push each changed branch and
verify remote heads. Keep the full goal active while required work remains.

## Ready-to-use agent instruction

Continue TH04 reconstruction and port64. Read this handoff and AGENTS.md; verify
both remote branches, pinned targets and actual local files. Recover missing
producer inputs or create new attested builds without rewriting historical
receipts. Complete a bounded Boss-picture or Game Over/Continue differential
against original DOS, reconstructed DOS and eventually native state/effects.
Preserve input/GDC failures and the two deferred exact cases. Use one low
priority CPU, muted Linux headless runs and explicit recovery-verified cleanup.
Update evidence/status, run CI/diff checks, commit with `gpt-6.1-sol: ` and push.
