# TH04 reconstruction handoff

Updated 2026-09-19. This file contains only live state and the next work queue.
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
- MAIN has **478/491 reviewed authored C/C++ functions** and
  **80,023/83,441 reviewed authored C/C++ bytes** exact (95.903692%). Forty
  accepted original-style ASM units add 5,615 bytes. Whole MAIN.EXE is not yet
  exact.
- The latest complete native aggregate is
  `gpt-web-session-v377-aggregate-final-001`: all 255 selected MAIN owners
  pass two cold builds, raw bytes, MAP, ordered relocations, and OMF. Receipt
  SHA-256: `20a23766aa1963d93907179709fa55030a1ff26d4a0018aa489f0aa638a86b5f`.
- The remaining reviewed authored C/C++ gap is **3,418 bytes**: stage
  session 1,310, dialog op/run/render 1,545, scroll 295, checkerboard 174,
  Stage 4 carpet 90, and the final 4 `snd_load` bytes.
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

1. **Recover natural OMF relocation order.** `gameplay_loop()` and
   `gameplay_session_init()` are now exact; the latter closes its historical
   one-byte gap through the compiler's natural word-aligned switch-table
   producer. Stage-session raw bytes, MAP, and relocation sites match while
   ordered relocations differ. Dialog raw bytes, MAP, and sites match but its
   target has three descending MZ relocation runs while the current object
   produces two. Continue from the
   [session](reconstruction/main/TH04_DEMO_GAMEPLAY_SESSION_V377.md),
   [stage-session](reconstruction/main/TH04_DEMO_PAUSE_SPLIT_V282.md), and
   [dialog](reconstruction/main/TH04_MAIN_DIALOG_BOUNDARY_V180.md) notes.
2. **Continue the remaining artifacts.** The cold decoded-payload residual is
   7 OP bytes, 5 MAINE bytes, and 0 ZUN bytes; this is not packed-file equality.
   ZUN's 6,360-byte diagnostic component differs at 4,241 bytes and still uses
   external support code. Continue from the
   [packed frontier](reconstruction/packed/TH04_PACKED_PAYLOAD_FRONTIER_V218.md)
   and [ZUN component link](reconstruction/zun/TH04_ZUN_COMPONENT_LINK_V317.md).
3. **Add deterministic DOSBox-X runtime scenarios** after standalone build and
   link closure can produce the artifacts under test.

The live six-function MAIN review queue comes from `config/units.csv`,
`config/th04_main_authored_functions.csv`,
`config/th04_function_boundaries.csv`, and `python3 scripts/status.py`.

## Retained private evidence

Keep these ignored `.analysis/reconstruction/exact-unit-replay/` trees:

- `gpt-web-session-v377-aggregate-final-001`
- `gpt-web-session-v377-focused-003`
- `gptweb-v213-dialog-reloc-diagnostic-001`
- `gptweb-v214-demo-fixupp-diagnostic-001`

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
