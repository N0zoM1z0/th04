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
- MAIN has **484/491 reviewed authored C/C++ functions** and
  **82,660/83,441 reviewed authored C/C++ bytes** exact (99.064009%). Forty
  accepted original-style ASM units add 5,615 bytes. Whole MAIN.EXE is not yet
  exact.
- The latest complete native aggregate is
  `gpt-web-dialog-v381-aggregate-final-001`: all 258 selected MAIN owners
  pass two cold builds, raw bytes, MAP, ordered relocations, and OMF. Receipt
  SHA-256: `507bc4ab4bb70f23088deb83d82360274656d6e360bcb3d0bff3eae3f60b2f76`.
- The remaining reviewed authored C/C++ gap is **781 bytes**: dialog render
  218, scroll 295, checkerboard 174, Stage 4 carpet 90, and the final 4 `snd_load` bytes.
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

1. **Close the remaining 218 DIALOG_TEXT render bytes.** `dialog_op()` and
   `dialog_run()` are now exact after restoring the fused
   f_dialog/shared-dialog TC4J producer. The remaining dialog blockers are
   `dialog_box_put()` (88), `playfield_copy_front_to_back()` (56),
   and `dialog_face_unput_8()` (74); these are instruction-shape/codegen
   problems rather than unresolved relocation topology. Continue from the
   dialog-render notes and compiler codegen probes.
2. **Close the remaining 563 non-dialog MAIN bytes.** The remaining blockers
   are scroll 295 bytes, checkerboard 174, Stage 4 carpet 90, and the final 4
   `snd_load` bytes. These are primarily compiler/code-shape or ownership
   problems rather than unexplained artifact layout.
3. **Continue the remaining artifacts.** The cold decoded-payload residual is
   7 OP bytes, 5 MAINE bytes, and 0 ZUN bytes; this is not packed-file equality.
   ZUN's 6,360-byte diagnostic component differs at 4,241 bytes and still uses
   external support code. Continue from the packed-frontier and ZUN component
   link notes.
4. **Add deterministic DOSBox-X runtime scenarios** after standalone build and
   link closure can produce the artifacts under test.

The live six-function MAIN review queue comes from `config/units.csv`,
`config/th04_main_authored_functions.csv`,
`config/th04_function_boundaries.csv`, and `python3 scripts/status.py`.

## Retained private evidence

Keep these ignored .analysis/reconstruction/exact-unit-replay/ trees:

- `gpt-web-dialog-v381-aggregate-final-001`
- `gpt-web-dialog-v381-focused-003`
- `gpt-web-demo-session-v380-aggregate-final-001`

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
