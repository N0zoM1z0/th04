# TH04 reconstruction handoff

Updated 2026-09-20. This file contains only live state and the next work queue.
Use the linked focused notes for experiment history. The CSV ledgers and fresh
script output remain authoritative.

## Resume here

Read [AGENTS.md](../AGENTS.md), [architecture](ARCHITECTURE.md),
[workflow](RE_WORKFLOW.md), and the relevant TH04 skill. Then run:

```bash
git status --short
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/audit_compat_dependencies.py --check
```

The goal is approximately 99% exact authored TH04 reconstruction, a standalone
rebuild from checked-in source, and playable DOSBox-X execution. Exact still
means a complete cold build with raw zero-difference bytes and relocations for
the accepted extent.

## Current verified state

- Target canonicality is `candidate-local-attested`. The pinned Japanese
  MAIN.EXE is 156,258 bytes, SHA-256
  `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
- MAIN has **491/494 reviewed authored C/C++ functions** and
  **83,177/83,469 reviewed authored C/C++ bytes** exact (99.650170%).
  Forty-three accepted original-style ASM units add 5,702 bytes. Whole MAIN.EXE
  is not yet exact. v394 closes all three remaining dialog-render helpers as
  authored hybrid C++ after independent TH05 producer corroboration.
- The latest complete native aggregate is
  `gpt-web-dialog-render-v394-aggregate-final-001`: all 268 selected MAIN
  owners pass two cold builds, raw bytes, MAP, ordered relocations, and OMF.
  Receipt SHA-256: `2c6b8b699f13c0b90aac3dcac6139ac13bdca3257b2de430241797cd988c2293`.
- The remaining reviewed authored C/C++ gap is **292 bytes**: checkerboard
  174, Stage 4 carpet 90, `item_splashes_init()` 26, and the final 2
  `snd_load` bytes (`89 C3`).
- MAIN now has **no provisional authored C/C++ boundaries**. v390 reviews the
  final provisional `item_splashes_init()` boundary as blocked, while
  `POINTNUM_DIGITS_SET` remains on the original-ASM plane from v389.
- OP, MAINE, and ZUN have no artifact-local exact cohort yet. Their current
  ledger exact count is zero.
- The TH04 product tree now uses local runtime, graphics, platform, GRCG,
  randring, CDG, resident, overlap, sound, player-shot, palette, playchar, rank,
  PI, tile-format, BB, enemy-size, maintained sprite-pattern, polar, subpixel,
  bullet-add implementation, HUD geometry, item-overflow, midboss-state,
  scroll-state, sound-implementation, sound-measure, config-loader, MAP-format,
  target-verified thicklaser, homing-state, faceset-filename, and boss-base
  interfaces. The `compat/rec98` forwarding boundary is now **0 forwarders, 0
  include sites, and 0 product files**; `audit_compat_dependencies.py
  --require-zero` passes. This closes the compatibility include migration, not
  complete source coverage or whole-artifact standalone rebuilds for every
  TH04 executable.

## Ordered work queue

1. **Close the remaining reviewed 292-byte C/C++ gap.** Checkerboard is 174
   bytes, Stage 4 carpet 90, `item_splashes_init()` is 26, and `snd_load` has
   the two-byte `89 C3` residual. Dialog render is exact as of v394.
2. **Keep provenance gates strict.** Checkerboard still lacks an independent
   non-switch counted-LOOP producer; carpet is TH04-only; item_splashes and the
   remaining `snd_load` MOV encoding have explicit compiler/provenance negative
   evidence. Do not replace them with target-derived inline assembly.
3. **Continue the remaining artifacts and deterministic runtime scenarios**
   after standalone build/link closure can produce the artifacts under test.

The live six-function MAIN review queue comes from `config/units.csv`,
`config/th04_main_authored_functions.csv`,
`config/th04_function_boundaries.csv`, and `python3 scripts/status.py`.

## Retained private evidence

Keep these ignored `.analysis/reconstruction/exact-unit-replay/` trees:

- `gpt-web-dialog-render-v394-aggregate-final-001`
- `gpt-web-dialog-render-v394-focused-004`
- `gpt-web-sub-b835-v393-aggregate-final-001`

Targets, toolchains, generated builds, database projects, and receipts stay
ignored. Never commit original executables or game assets.

## Finish every packet

Run the focused two-cold comparison and a complete cold aggregate for affected
accepted owners, then:

```bash
python3 scripts/preflight.py
python3 scripts/ci.py
git diff --check
```

Record the artifact, segment:offset, evidence class, exact command or receipt,
result, and remaining unknowns in the focused note and ledgers. Update this file
only when the live state, next queue, or blocker changes.
