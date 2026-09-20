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
- MAIN has **487/493 reviewed authored C/C++ functions** and
  **82,758/83,443 reviewed authored C/C++ bytes** exact (99.179080%). Forty
  accepted original-style ASM units add 5,615 bytes. Whole MAIN.EXE is not yet
  exact. The denominator grew by two because v387 formally reviewed and
  accepted the previously provisional NULLFUNC_NEAR / NULLFUNC_FAR bytes.
- The latest complete native aggregate is
  `gpt-web-nullfunc-v387-aggregate-final-001`: all 261 selected MAIN
  owners pass two cold builds, raw bytes, MAP, ordered relocations, and OMF.
  Receipt SHA-256: `5450ddca56533691f2963d7518d143ad90099888578c75200d4121c38aff0ab2`.
- The remaining reviewed authored C/C++ gap is **685 bytes**: dialog render
  218, `sub_B835` 199, checkerboard 174, Stage 4 carpet 90, and the final 4
  `snd_load` bytes.
- Four small provisional boundaries totaling **113 bytes** remain outside the
  reviewed denominator: `randring1_next16_mod()` 25,
  `randring2_next16_mod()` 25, `item_splashes_init()` 26, and
  `POINTNUM_DIGITS_SET` 37.
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

1. **Close the remaining 199-byte scroll helper `sub_B835`.** A bounded
   pure-C++ TC4J variant now reaches the exact 199-byte size and target CFG.
   TC4J built-in symbolic inline assembly explains the remaining register
   encoding/copy-order shape, and an independent TH05 target preserves the same
   low-level producer. Historical source provenance and linked END_TEXT ownership
   are still open, so do not promote or add tracked inline assembly yet.
2. **Close checkerboard 174, Stage 4 carpet 90, and the final 4 `snd_load`
   bytes.** These are primarily compiler/code-shape or ownership problems.
3. **Keep the 218 DIALOG_TEXT render bytes as a bounded compiler blocker.**
   Independent TH05 target bytes preserve the same compact `REP STOSW`/`LOOP`
   and register-direction shape, but pinned TC4J rejects both command-line and
   pragma `-Ol`; ReC98's matching inline assembly is explicitly decompilation
   provenance, not recovered original ASM. Do not convert these functions to
   standalone TASM solely to gain exactness.
4. **Continue the remaining artifacts and deterministic runtime scenarios**
   after standalone build/link closure can produce the artifacts under test.

The live six-function MAIN review queue comes from `config/units.csv`,
`config/th04_main_authored_functions.csv`,
`config/th04_function_boundaries.csv`, and `python3 scripts/status.py`.

## Retained private evidence

Keep these ignored `.analysis/reconstruction/exact-unit-replay/` trees:

- `gpt-web-nullfunc-v387-aggregate-final-001`
- `gpt-web-nullfunc-v387-focused-005`
- `gpt-web-scroll-driver-v383-aggregate-final-001`

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
