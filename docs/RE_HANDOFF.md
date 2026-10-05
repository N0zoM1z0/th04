# TH04 native branch handoff

Updated 2026-10-05. Native development is paused. General semantic work stops
unless an ambiguity blocks a concrete port owner. This branch retains the
unfinished x64 product; DOS work/organization merges separately into main.

## Verified frontier

- Latest retained source: v1299 registration graphics and separate text plane.
  Original MAINE drawing helpers, SUPER/font kernels and raw TRAM stores execute
  under explicit hardware/ROM/BFNT/PI/RETF adapters at two load segments.
- 158 full two-page/palette/TRAM/RGB snapshots agree GNU/Wine/optimized UBSan/
  actual Windows. All 99 AMD64 products bind the 238-file source manifest;
  each build's 32 contracts pass. Prior 382 menu and 1,288 score cases pass.
- v1299 is a component, not an integrated saving scene. Published Windows GUI
  remains v1296-congratulations, reaching `registration_pending`.
- Normal Stages 1–6 and Ending/Staff/verdict/congratulations integration have
  bounded controls. Complete game/native route/audio acceptance is pending.
- DOS source/targets and historical unit/function acceptance are untouched.

## Next when resumed

1. Consume registration requests in ordered scene time (waits/fades/explicit
   input/audio), retaining decoded render sections before save mutates HI.
2. Commit a separate host score file at its boundary and return to fresh OP.
3. Complete Bomb/death/lives/Continue, Extra, full HUD, OP auxiliary flows,
   audio/configuration, and actual Linux/Windows complete route/persistence tests.

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
Current receipt root: `.analysis/port64/registration-render-v1299/`.
Its `platform-review.json`, `build-products-bound.json`, actual Windows receipt
and source manifest establish the scope above; final CI passes in `ci-closure.log`.

Completed captures share immutable hard-linked storage after independent
production/full readback. The early 90-snapshot development pair is archived;
`capture-storage-receipt.json` records restore paths/hashes and 2,385,702,912
net bytes reclaimed. Keep current 158-snapshot original input and all fast
caches. Use fresh output directories; never overwrite a shared capture inode.
Pinned originals/tools, Windows GUI/launchers/assets/saves and rollback remain.
