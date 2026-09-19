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
- MAIN has **476/491 reviewed authored C/C++ functions** and
  **79,183/83,441 reviewed authored C/C++ bytes** exact (94.896993%). Forty
  accepted original-style ASM units add 5,615 bytes. Whole MAIN.EXE is not yet
  exact.
- The latest complete native aggregate is
  `gpt-web-scroll-state-aggregate-001`: all 253 selected MAIN owners pass two
  cold builds, raw bytes, MAP, ordered relocations, and OMF. Receipt SHA-256:
  `7ccf4a2233d7761ccea5c540fd2ccda0fb1d5de87999dd18ecbc25eae1becef2`.
- OP, MAINE, and ZUN have no artifact-local exact cohort yet. Their current
  ledger exact count is zero.
- The TH04 product tree now uses local runtime, graphics, platform, GRCG,
  randring, CDG, resident, overlap, sound, player-shot, palette, playchar, rank,
  PI, tile-format, BB, enemy-size, maintained sprite-pattern, polar, subpixel, bullet-add implementation, HUD
  geometry, item-overflow, midboss-state, and scroll-state interfaces. The
  remaining compatibility boundary is **8 forwarders, 9 include sites, and 9
  product files**, with no missing, unused, invalid, or
  direct forbidden includes.

## Ordered work queue

1. **Finish standalone source closure.** Follow the
   [compatibility migration recipe](reconstruction/shared/TH04_COMPAT_MIGRATION.md).
   The only remaining multi-site forwarder is
   `th05/main/boss/boss.hpp`. Its two uses sit in GAME5 calibration
   branches and currently consume no TH05-exclusive boss symbol, so close it
   together with the TH04 boss-base ownership rather than inventing a mirror
   interface. In parallel, continue the one-site families in audit order,
   beginning with `th02/snd/impl.hpp` and
   `th02/snd/measure.hpp`. Run a complete default aggregate after each
   shared-header or ABI batch.
2. **Close the MAIN gameplay loop candidate.** Retained run
   `gpt-5-6-sol-v346-gameplay-symbolic-focused-004` emits the target-positioned
   379-byte object. Bind the final case-sensitive `SHOTS_RENDER()` external
   without changing that object, then run focused A/B and the complete default
   aggregate. This remains compiler evidence until linked raw/MAP/ordered-reloc
   checks pass. See the
   [gameplay note](reconstruction/main/TH04_DEMO_GAMEPLAY_TERNARY_V248.md).
3. **Recover natural OMF relocation order.** Dialog raw bytes, MAP, and sites
   match, but its target has three descending MZ relocation runs while the
   current object produces two. Stage-session raw bytes, MAP, and sites also
   match, but ordered relocations differ. Continue from the
   [dialog](reconstruction/main/TH04_MAIN_DIALOG_BOUNDARY_V180.md) and
   [stage-session](reconstruction/main/TH04_DEMO_PAUSE_SPLIT_V282.md) notes.
4. **Continue the remaining artifacts.** The cold decoded-payload residual is
   7 OP bytes, 5 MAINE bytes, and 0 ZUN bytes; this is not packed-file equality.
   ZUN's 6,360-byte diagnostic component differs at 4,241 bytes and still uses
   external support code. Continue from the
   [packed frontier](reconstruction/packed/TH04_PACKED_PAYLOAD_FRONTIER_V218.md)
   and [ZUN component link](reconstruction/zun/TH04_ZUN_COMPONENT_LINK_V317.md).
5. **Add deterministic DOSBox-X runtime scenarios** after standalone build and
   link closure can produce the artifacts under test.

The live six-function MAIN review queue comes from `config/units.csv`,
`config/th04_main_authored_functions.csv`,
`config/th04_function_boundaries.csv`, and `python3 scripts/status.py`.

## Retained private evidence

Keep these ignored `.analysis/reconstruction/exact-unit-replay/` trees:

- `gpt-web-scroll-state-aggregate-001`
- `gpt-5-6-sol-v346-gameplay-symbolic-focused-004`
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
