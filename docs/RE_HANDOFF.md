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
- MAIN has **482/491 reviewed authored C/C++ functions** and
  **81,333/83,441 reviewed authored C/C++ bytes** exact (97.473664%). Forty
  accepted original-style ASM units add 5,615 bytes. Whole MAIN.EXE is not yet
  exact.
- The latest complete native aggregate is
  `gpt-web-demo-session-v380-aggregate-final-001`: all 256 selected MAIN
  owners pass two cold builds, raw bytes, MAP, ordered relocations, and OMF.
  Receipt SHA-256:
  `c87c01b0152815d72eee36eb3d18106e312e854d82b883c1b47db782222183ad`.
- The remaining reviewed authored C/C++ gap is **2,108 bytes**: dialog
  op/run/render 1,545, scroll 295, checkerboard 174, Stage 4 carpet 90, and
  the final 4 `snd_load` bytes.
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

1. **Recover natural DIALOG_TEXT relocation order.** The complete 1,310-byte
   stage-session owner is now exact; its formerly isolated `0xB2DA` relocation
   is explained and reproduced by natural TC4J LEDATA/FIXUPP batching in the
   fused slowdown/DEMO producer. `dialog_op()` and `dialog_run()` already match
   raw bytes, MAP, and relocation sites, but the target has three descending MZ
   relocation runs while the current object produces two. Continue from the
   [dialog](reconstruction/main/TH04_MAIN_DIALOG_BOUNDARY_V180.md) and FIXUPP
   codegen notes.
2. **Close the remaining 563 non-dialog MAIN bytes.** The remaining blockers
   are scroll 295 bytes, checkerboard 174, Stage 4 carpet 90, and the final 4
   `snd_load` bytes. These are primarily compiler/code-shape or ownership
   problems rather than unexplained artifact layout.
3. **Continue the remaining artifacts.** The cold decoded-payload residual is
   7 OP bytes, 5 MAINE bytes, and 0 ZUN bytes; this is not packed-file equality.
   ZUN's 6,360-byte diagnostic component differs at 4,241 bytes and still uses
   external support code. Continue from the
   [packed frontier](reconstruction/packed/TH04_PACKED_PAYLOAD_FRONTIER_V218.md)
   and [ZUN component link](reconstruction/zun/TH04_ZUN_COMPONENT_LINK_V317.md).
4. **Add deterministic DOSBox-X runtime scenarios** after standalone build and
   link closure can produce the artifacts under test.

The live six-function MAIN review queue comes from `config/units.csv`,
`config/th04_main_authored_functions.csv`,
`config/th04_function_boundaries.csv`, and `python3 scripts/status.py`.

## Retained private evidence

Keep these ignored `.analysis/reconstruction/exact-unit-replay/` trees:

- `gpt-web-demo-session-v380-aggregate-final-001`
- `gpt-web-demo-session-v380-focused-008`
- `gptweb-v213-dialog-reloc-diagnostic-001`

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
