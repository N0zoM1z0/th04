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
  **83,375/83,469 reviewed authored C/C++ bytes** exact (99.887383%).
  Forty-three accepted original-style ASM units add 5,702 bytes.
- Latest complete native aggregate:
  `gpt-web-v410-carpet-frame-aggregate-final-001`, 281 MAIN owners,
  receipt SHA-256
  `d1c5af30fe7419391e48b60156b87b8d4ccb5202ca7e7ca216f18e1c877c2487`.
- Remaining reviewed MAIN C/C++ gap: **27 bytes** — checkerboard contributes only its two-byte `E2 F7` `LOOP`, Stage 4 carpet contributes 23 low-level residual bytes after v409/v410 recover 67/90 bytes, and `snd_load` retains the two-byte `89 C3` MOV BX,AX residual.
- v403 confirms TH03 joins TH02/TH05 at natural `8B D8` in homologous
  `snd_load`; the TH04-only `89 C3` therefore remains provenance-blocked.
- v404 verifies pinned TC4J `#pragma intrinsic` string-op codegen, but tested
  families emit no `LODSB`/`LOOP` and cannot preserve the strided carpet/checkerboard semantics.
- v405 expands carpet/checkerboard provenance scanning to all 20 registered TH01-TH05 artifact images (restoring 8 DIET containers first); both unusual signatures remain TH04-MAIN-only, so neither blocker gains hybrid-source provenance.
- v406 closes the same-media PC-98 IDE hidden-optimizer hypothesis: exhaustive TCALC.PRJ/PRJ2MAK scalar toggles expose only `-O`, and PC-98 `TC.EXE` still emits no `LOOP`/`LODSB` for the bounded blocker probes.
- v408 splits the 174-byte checkerboard owner into 172 exact natural-source bytes plus one two-byte blocked `LOOP`; focused A/B, 272-owner candidate aggregate, and 272-owner post-promotion aggregate all pass with zero failures. The complete checkerboard function remains blocked.
- v409 similarly partitions Stage 4 carpet: seven natural identity fragments totaling 56 bytes are exact, while eight low-level residual owners totaling 34 bytes remain blocked. Focused A/B plus 279-owner candidate and post-promotion aggregates all pass; the complete carpet function remains blocked.
- v410 further separates compiler-generated carpet entry/exit bytes from the adjacent historical PUSH DS/POP ES and LOOP: 11 more bytes become exact, leaving carpet at 67/90 exact and 23 blocked. Focused A/B plus 281-owner candidate/post-promotion aggregates pass; the function remains blocked.
- MAIN has **no provisional authored C/C++ boundaries**.
- OP, MAINE, and ZUN have no artifact-local exact cohort yet.
- OP/MAINE v400/v401 physical-object replay closes all six former master.lib CODE/DATA alignment residuals. v402 then closes the two OP-music XOR-direction bytes with a TH03/TH05-corroborated low-level copy core. OP and MAINE diagnostic payload candidates now each differ only at the shared two-byte `snd_load` `89 C3`; payload lengths and target-equal relocation multisets remain unchanged.
- `compat/rec98` migration is closed: 0 forwarders, 0 include sites,
  0 product files.

## Ordered work queue

1. **Close the remaining 27-byte MAIN gap.** Continue only the three live byte blockers: checkerboard `E2 F7` (2 bytes), the eight Stage 4 carpet residual owners (23 bytes total), and the final `snd_load` MOV BX,AX encoding (2 bytes).
2. **Keep provenance gates strict.** Current corpus/cross-game evidence does
   not justify target-derived inline assembly for any of the three blockers.
3. **Continue OP/MAINE packed closure from v402.** Master.lib CODE/DATA seams
   are closed by real historical object ownership and the OP-music XOR pair is
   closed by independent TH03/TH05 producer corroboration. Both decoded payload
   candidates now differ only at shared `snd_load` (2 bytes per artifact).
4. **Add deterministic DOSBox-X runtime scenarios** after standalone build/link
   closure can produce the artifacts under test.

The live MAIN review state comes from `config/units.csv`, `config/th04_main_authored_functions.csv`, `config/th04_function_boundaries.csv`, and `python3 scripts/status.py`.

## Retained private evidence

No expanded exact-unit replay tree is required for the current handoff. The
latest accepted MAIN replay is
`gpt-web-v410-carpet-frame-aggregate-final-001`; its receipt SHA-256 is
`d1c5af30fe7419391e48b60156b87b8d4ccb5202ca7e7ca216f18e1c877c2487` and is durable in the checked-in evidence ledger. Re-run it if the full receipt body is needed.

Keep the current small blocker/frontier probe cache while those topics remain
active:

- `.analysis/gpt-web/v391-snd-load-crossgame-001`
- `.analysis/gpt-web/v396-checkerboard-negative-001`
- `.analysis/gpt-web/v398-checker-loop-forms-001`
- `.analysis/gpt-web/v399-tcc-opt-surface-001`
- `.analysis/gpt-web/v396-final-opcode-corpus-001`
- `.analysis/gpt-web/v397-master-object-boundaries-001`
- `.analysis/gpt-web/v400-master-object-split-replay-001`
- `.analysis/gpt-web/v401-master-vs-object-replay-001`
- `.analysis/gpt-web/v402-opmusic-hybrid-replay-001`
- `.analysis/gpt-web/v403-snd-load-th03-001`
- `.analysis/gpt-web/v404-tc4-intrinsic-surface-001`
- `.analysis/gpt-web/v405-final-blocker-crossartifact-001`
- `.analysis/gpt-web/v406-tc4j-pc98-ide-optimizer-001`
- `.analysis/gpt-web/v400-master-object-split-baseline-001`

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
