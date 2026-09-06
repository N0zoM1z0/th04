# Agent reconstruction workflow

## 1. Preflight

```bash
git status --short --branch
python3 scripts/preflight.py
```

If target verification or database attestation fails, target-dependent RE is
blocked.  Public tooling/documentation work may continue without inventing
target claims.

When a Ghidra database will be used, also run its fresh headless read-only
attestation in the same session:

```bash
python3 scripts/ghidra.py th04-main check
```

This verifies the pinned `.tools/` installation and the saved
`ghidra-project/` database before exporting a nonce-bound private receipt.
Ghidra auto-analysis results remain provisional even when this check passes.

## 2. Select one bounded problem

Run `python3 scripts/status.py --json` and select one artifact plus one bounded
unit.  Prefer a unit whose entry, exits, callers, and adjacent ownership can be
reviewed in one session.  Large dispatchers and shared segment changes need an
explicit sub-plan.

Create the `candidate` row in `config/units.csv` only after recording how the
candidate was found.  Use artifact plus segment:offset; never rely on a naked
linear address.

## 3. Reconcile ownership before semantics

Inspect raw bytes, MZ relocations, disassembly, all control-flow exits, callers,
callees, shared tails, jump tables, alignment, embedded data, and adjacent
entries.  Classify authored, compiler, library, asset, padding, or original ASM
ownership.  A disassembler's function extent is only a proposal.

Promote to `boundary-reviewed` when the compared extent is complete and does
not steal or omit bytes.

## 4. State a falsifiable hypothesis

Add a row to `config/hypotheses.csv` for an uncertain name, type, width,
calling convention, field offset, branch meaning, or source shape.  Link each
claim to independent evidence rows.  Keep unresolved contradictions explicit.

Evidence priority when claims conflict:

1. hash-attested target bytes and target-local control/data flow;
2. pinned Borland/TASM/TLINK probes;
3. target-local deterministic runtime observations;
4. multiple target-local callers/callees/xrefs;
5. ReC98, adjacent Touhou games, hardware docs, and historical material;
6. database names, decompiler syntax, and intuition.

## 5. Implement natural source

Recover behavior, ABI, segmentation, and ownership before tuning code shape.
Do not mechanically translate pseudocode.  Keep unknown meaning neutral.
Promote to `source-present` only when the body and its material side effects are
implemented, not when a stub compiles.

## 6. Probe and compare smallest-first

Compile the smallest truthful unit with explicit flags and immutable tool/input
digests.  Compare object/map structure, relocations, instructions, CFG, stack,
registers, segments, x87, and then raw bytes.  Diagnose mismatches by Oracle
dimension before changing source.

Use:

```bash
python3 scripts/compare_artifacts.py TARGET CANDIDATE --json
```

For a locally cold-built pinned ReC98 control, run
`scripts/survey_rec98_outputs.py SOURCE` first.  Its default exact gate rejects
any raw mismatch; `--gate calibration` only proves that the known 20-output
failure/pass vector, per-game OMF identities, and source/build receipts were
reproduced.  The compact vector exposes objective size, header, relocation,
program, and overlay counts so the next experiment can be routed without
mistaking similarity for acceptance.  Add `--compact` for the normal agent
view; omit it only when the verbose per-byte comparison receipt is needed.

The current comparator covers whole MZ/COM artifacts; the OMF adapter validates
record integrity and exposes producer/dependency metadata plus raw and narrowly
timestamp-normalized identities.  Unit-level code/data/fixup adapters still
require a reviewed TH04 map/address and ownership model.

## 7. Validate semantics independently

Use a compiler probe for ABI-visible claims.  When runtime infrastructure is
available, add a deterministic scenario with state/VRAM/palette/event
checkpoints.  Use cross-game source only as corroboration and confirm it
against TH04.

Upstream reconstructions follow the same path as any other hypothesis.  Record
their provenance with an `upstream` evidence row, re-review boundaries against
the selected artifact, and rerun every required local Oracle.  Never import an
upstream `exact` or `finalized` state into `config/units.csv`.

## 8. Promote without rounding

`structural` records strong non-byte evidence.  `exact` requires raw zero
differences, replay metadata, required evidence, and cold affected-unit replay.
Near matches remain non-exact regardless of their percentage.

## 9. Preserve durable memory

Update source, ledgers, focused notes, reusable probes, and the handoff.  Put
failed experiments in a concise durable note when they eliminate a plausible
path.  Delete or retain bulky raw output only below `.analysis/`.

Finish with:

```bash
python3 scripts/ci.py
git diff --check
```
