# TH04 native branch handoff

Updated 2026-10-09. Native development has resumed. General semantic work stops
unless an ambiguity blocks a concrete port owner. This branch retains the
unfinished x64 product; DOS work/organization merges separately into main.

## Verified frontier

- v1303 adds character Bomb pictures, BB tiles and retained48-star effects.
  Original MAIN at loads1000/2000 agrees with GNU/optimized UBSan/actual Windows:
  1,236 state cases/2,252 records and294 pixel cases/548 complete screens.
  105 AMD64 products bind263 source files; all34 contracts pass per host.
  This component still needs the live lifecycle/render dispatch. No GUI death,
  physical timing/audio or complete route acceptance follows.
- v1302 adds the blocking Game Over/menu and MAIN Continue score components.
  Original MAIN at loads1000/2000 agrees with GNU/optimized UBSan/actual Windows:
  2,003 menu cases, 64 full scenes, 2,985 file controls. All 34 contracts pass.
  These components have not joined live MAIN or its renderer/save consumer.
- v1301 adds the player/miss/Bomb CPU producer component. Original MAIN relative
  `0AAF:54C4..553A`, `571A..581D`, `5E98..610D` executes at loads1000/2000,
  DS8000. 8,235 isolated cases plus retained sequences produce 10,319 records
  agreeing GNU/optimized UBSan/actual Windows; each host passes 34 contracts.
  Fire/items/HUD/sound/game-over/character graphics are explicit adapters.
  The new component has not joined live MAIN; GUI death/Bomb remains pending.
- v1300 joins registration timing/input/rendering, ordered host score commits,
  fresh OP and a second MAIN launch. Missing/corrupt/short files, all ten sections,
  partial/full names, no-entry acknowledgement and failed writes have controls.
- GNU/optimized UBSan/actual Windows each pass 33 contracts and 30 seeded
  frontend fixtures; all 112 output files agree. 102 AMD64 products bind a
  245-file manifest. Prior 1,288 score/382 menu/158 graphics comparisons pass.
- Original MAINE decoded relative `0000:0622..06A3` fade bodies run at loads
  1000/2000: black-in(2) takes 35 refreshes, black-out(1) takes 18.
  VBlank/palette adapters are explicit; physical timing is unaccepted.
- Both GUI source backends consume registration. Actual Windows acceptance here
  is CLI/seeded child scenes. Published GUI remains v1296-congratulations.
- Normal Stages 1–6 and Ending/Staff/verdict/congratulations integration have
  bounded controls. Complete game/native route/audio acceptance is pending.
- DOS source/targets and historical unit/function acceptance are untouched.

## Next owners

1. Add Game Over TRAM rendering, then join the verified Bomb graphics and
   tested player lifecycle, scene and MAIN Continue save to live MAIN. Suspend
   at the last-life call and resume its suffix once; publish real counters.
2. Extra, full HUD, OP auxiliary flows, unlocks, audio/configuration.
3. Actual Linux/Windows complete routes, persistence/restart and dense Lunatic
   timing/performance. All runs stay muted; audio requests are retained only.

See [port overview and stable evidence anchors](PORT64.md), branch-local
`config/evidence.csv`/`config/knowledge.csv`, and main's
[overall status](https://github.com/N0zoM1z0/th04/blob/main/docs/PORTING_STATUS.md).
Detailed history no longer accumulates in this handoff.

## Commands and private state

```sh
python3 scripts/preflight.py
python3 scripts/ci.py
git diff --check
```

Fast caches: `.analysis/port64/{linux,windows,ubsan}-live-v1251`.
Current receipt root: `.analysis/port64/registration-join-v1300/`.
Its `platform-review.json`, source manifest, fade/reference consumers and actual
Windows receipts establish the scope above. Replay `review_results.py` there.
Root MAINE Ghidra attestation passes independently of this worktree's missing
`.tools`; target provenance remains `candidate-local-attested`.
Latest component root: `.analysis/port64/player-lifecycle-v1301/`;
`platform-review.json` binds 105 AMD64 products to 250 files. Root MAIN database
attestation passes. Reuse the checked-in player lifecycle Python/Windows probes.
Latest Game Over root: `.analysis/port64/gameover-v1302/`; `platform-review.json`
binds 105 AMD64 products to 257 files. MAIN saves one selection with one RNG word;
MAINE re-keys all ten sections with two RNG draws per key. Never interchange them.
One Windows temporary-score replacement failed; three isolated retries and the
full rerun pass. Cause remains unknown; preserve failure propagation.
Latest Bomb root: `.analysis/port64/bomb-v1303/`; `platform-review.json` binds
263 files to manifest `c0fbe950be3e6f7a4bf794ea357d0c92d6d1859e8c4684296e77137b47d11751`.
Use the checked-in Bomb Python/Windows probes with fresh output paths. A rejected
star-only fixture omitted caller GRCG setup; actual1666/1672 restores equality.
Final pixels are compressed, and Windows hashes binary stdout without a raw dump.
This batch retires8 superseded streams, reclaiming13,643,776 allocated bytes;
2,379 protected source/cache/input/final-reference files remain unchanged.

Completed captures share immutable hard-linked storage after independent
production/full readback. The early 90-snapshot development pair is archived;
`capture-storage-receipt.json` records restore paths/hashes and 2,385,702,912
net bytes reclaimed in v1299. Keep current 158-snapshot original input and all fast
caches. Use fresh output directories; never overwrite a shared capture inode.
Pinned originals/tools, Windows GUI/launchers/assets/saves and rollback remain.
Per the user's cleanup request, retire superseded/failed outputs each batch and
deduplicate completed captures only after hash readback. v1302 reclaimed
980,566,016 allocated bytes; current targets, source and build caches are intact.
`cleanup-receipt.json` and `final-capture-storage.json` record the operations.
