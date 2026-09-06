# TH04 reconstruction agent rules

This repository targets the original Japanese PC-98 TH04 executables described
in `config/targets.toml`.  Local files from a translation, modified disk image,
different press, or emulator bundle must not silently replace them.

## Session preflight

Before target-dependent work:

1. Read `docs/RE_HANDOFF.md`, `docs/ARCHITECTURE.md`, `docs/RE_WORKFLOW.md`,
   and the relevant local skill.
2. Inspect `git status` and run `python3 scripts/preflight.py`.
3. Require every used target to pass size, SHA-256, format, and MZ-structure
   checks.  Treat `canonicality = "candidate-local-attested"` as a known
   provenance gap, not as proof of an official pristine dump.
4. Attest the active disassembler database against the target file, MZ header,
   entry `CS:IP`, relocation count, load-module digest, and sampled bytes.
5. Work on one bounded unit or one coherent control-plane batch.

## Evidence and state

- Keep target observations, compiler observations, runtime observations,
  cross-game corroboration, external documentation, and inference distinct.
- A disassembler database and its decompiler are views of target evidence, not
  independent Oracles.
- A name, source file, successful build, normalized instruction match, screen
  similarity, or ReC98 implementation is not an exact-match claim.
- Upstream source, comments, progress labels, and exactness statements enter as
  untrusted candidate material.  They must be re-attested against our pinned
  target with our clean build and complete required Oracle set; upstream or
  cross-game evidence cannot satisfy an exact requirement by itself.
- `config/units.csv` tracks boundary, origin, source presence, and accepted
  state separately.  `config/evidence.csv` records replayable observations.
- Exact-required evidence must name the same artifact as the unit unless
  `config/oracles.toml` explicitly permits that Oracle to be global.
- Only a cold build plus raw zero-difference comparison of the complete
  accepted extent may set a unit or artifact to `exact`.
- Never manufacture equality with copied target byte arrays, fake returns,
  inert padding, ABI lies, or target-derived inline assembly.  Genuine
  handwritten/undecompilable assembly must be classified and justified.

Use these claim words precisely:

- `observed`: read directly from a hash-attested target;
- `compiler-observed`: reproduced by a pinned toolchain probe;
- `runtime-observed`: reproduced under a recorded emulator scenario;
- `corroborated`: supported by a separate game or external source;
- `inferred`: falsifiable best explanation;
- `source-present`: maintained source exists;
- `structural`: configured non-byte structural checks pass;
- `exact`: complete configured bytes and relocations are identical.

## PC-98 and 16-bit ABI rules

- Preserve Turbo C++ 4.0J/TASM/TLINK behavior until direct evidence proves a
  different tool or flag for a bounded unit.
- Preserve memory model, near/far distance, calling convention, segment/group
  ownership, DGROUP assumptions, structure packing, enum and integer widths,
  x87 behavior, translation-unit order, and linker input order.
- Record addresses as artifact plus segment identity plus offset.  A linear
  emulator address is incomplete unless the load segment is also recorded.
- Treat MZ relocation sites, relocation entries, code/data segment layout,
  overlays, embedded COM payloads, and self-modifying code as first-class
  ownership surfaces.
- Ghidra/IDA function boundaries are provisional.  Reconcile shared tails,
  jump tables, alignment, interleaved data, far entry points, and ASM slices.
- Do not modernize undefined behavior or PC-98 hardware timing in the exact
  branch.  Record it, test it, and isolate portable work from reconstruction.

## Database and target safety

- Never patch target bytes or use a disassembler write as evidence until it is
  read back and mirrored into a checked-in ledger or note.
- Keep Ghidra projects below the ignored `ghidra-project/` directory. Keep IDA
  projects, exports, executable dumps, disk images, compiler installations, and
  generated reports below `.analysis/` or outside the repo. Ghidra rejects a
  project path containing the dot-prefixed `.analysis` component.
- Never commit original executables, game assets, archives, credentials, or
  private keys.

## Oracle discipline

Choose the smallest independent Oracle set that can falsify the claim, then
run the stronger gates before promotion.  Exact promotion requires target
identity, format integrity, boundary review, current toolchain identity,
toolchain replay, OMF integrity, cold-build determinism, relocation/layout
agreement, raw bytes, ledger validation, and cold aggregate replay.
Runtime, cross-emulator, trace, VRAM/palette, and invariant Oracles strengthen
semantic confidence but cannot waive a byte mismatch.

After shared headers, compiler flags, segment declarations, link order, or
global layouts change, invalidate and cold-replay every affected accepted unit.

## Session and handoff discipline

- One writable reconstruction session at a time; do not run concurrent
  Borland/Wine builds against shared outputs.
- Store scratch experiments under `.analysis/`; turn reusable experiments into
  deterministic scripts or documented probes.
- Finish with the focused comparison, `python3 scripts/ci.py`, and
  `git diff --check`.
- Update `docs/RE_HANDOFF.md` when the phase, verified facts, or blockers
  change.  Report artifact, segment:offset, evidence classes, commands, exact
  result, and remaining unknowns.
