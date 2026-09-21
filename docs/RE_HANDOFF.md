# TH04 reconstruction handoff

Updated 2026-09-21. This file contains only live state and the next work queue.
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
- MAIN has **492/494 reviewed authored C/C++ functions** and
  **83,203/83,469 reviewed authored C/C++ bytes** exact (99.681319%).
  Forty-three accepted original-style ASM units add 5,702 bytes.
- Latest complete native aggregate:
  `gpt-web-item-splashes-init-v395-aggregate-final-001`, 269 MAIN owners,
  receipt SHA-256
  `b5810190e492ea0a7bb5403c61d9b0f5f8d6f53bf657ccfdcbbac7a4d2fed57c`.
- Remaining reviewed MAIN C/C++ gap: **266 bytes** — checkerboard 174,
  Stage 4 carpet 90, and the two-byte `89 C3` MOV BX,AX residual in
  `snd_load`.
- MAIN has **no provisional authored C/C++ boundaries**.
- OP, MAINE, and ZUN have no artifact-local exact cohort yet.
- `compat/rec98` migration is closed: 0 forwarders, 0 include sites,
  0 product files.

## Ordered work queue

1. **Close the remaining 266-byte MAIN gap.** Continue only the three live
   blockers: checkerboard, Stage 4 carpet, and the final `snd_load`
   MOV BX,AX encoding.
2. **Keep provenance gates strict.** Current corpus/cross-game evidence does
   not justify target-derived inline assembly for any of the three blockers.
3. **Continue OP/MAINE packed-object topology** from the v397 master.lib
   object-boundary note.
4. **Add deterministic DOSBox-X runtime scenarios** after standalone build/link
   closure can produce the artifacts under test.

The live six-function MAIN review queue comes from `config/units.csv`,
`config/th04_main_authored_functions.csv`,
`config/th04_function_boundaries.csv`, and `python3 scripts/status.py`.

## Retained private evidence

No expanded exact-unit replay tree is required for the current handoff. The
latest accepted MAIN replay remains
`gpt-web-item-splashes-init-v395-aggregate-final-001`; its run ID and
receipt SHA-256 are durable in the checked-in evidence ledger. Re-run it if the
full receipt body is needed.

Keep the current small blocker/frontier probe cache while those topics remain
active:

- `.analysis/gpt-web/v391-snd-load-crossgame-001`
- `.analysis/gpt-web/v396-checkerboard-negative-001`
- `.analysis/gpt-web/v398-checker-loop-forms-001`
- `.analysis/gpt-web/v399-tcc-opt-surface-001`
- `.analysis/gpt-web/v396-final-opcode-corpus-001`
- `.analysis/gpt-web/v397-master-object-boundaries-001`

Other current v397 object/listing controls may remain expanded because they are
small and directly support the active OP/MAINE frontier. Superseded probe
receipts are archived under `.analysis/reconstruction/receipt-archive/`.

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
