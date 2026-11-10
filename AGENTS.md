# TH04 reconstruction agent rules

## Highest priority: lightweight exact reconstruction and useful knowledge

These are the user's current workflow requirements. They override older
instructions that mandate broad CI, repeated preflights, document/source-pin
refreshes, per-checkpoint audits or extra workflow machinery. Preserve the
actual exactness, target identity, natural-source and state-isolation rules.

- Prioritize exact reconstruction and reusable knowledge. Use the shortest
  useful loop: inspect relevant state, analyze/edit, compile and compare the
  affected scope, retain useful learning, and create a coherent checkpoint.
- Use existing repository scripts and composable Bash. Add only the smallest
  change needed for an observed problem. Do not introduce a framework, schema,
  registry, state machine, generalized validator, test family or reporting
  process merely to make a local reconstruction task look more engineered.
- Documentation, knowledge and handoff edits require no compiler, analyzer,
  full CI, cold replay or receipt refresh. Inspect the diff. Check syntax only
  for machine-readable inputs actually changed.
- Source changes need the complete affected exact comparison, including its
  owned extents and relocations. Recheck known consumers of changed shared
  inputs. Tool changes need relevant positive/negative cases and a bounded
  real smoke. Run a broad suite only for an explicit request or a demonstrated
  impact that cannot be narrowed; state that reason first.
- Do not add tests or live freshness gates for prose hashes, prompt wording,
  progress totals, handoff source-SHA tables or ordinary source spelling.
  Bind exact evidence to executable inputs and relevant verification settings.
  Keep Git metadata as provenance. A document genuinely consumed by a build
  remains a build input. Never edit historical receipts to manufacture a pass.
- Plain Markdown is sufficient for knowledge: record the finding, applicable
  target/compiler/scope, evidence links, useful failed attempts and open
  questions. No mandatory JSON conversion, promotion workflow or test per note.
  Search relevant sections; do not read an entire large knowledge journal.
- Write documentation and knowledge in natural, fluent English. Lead with the
  concrete finding and connect the evidence and next action clearly. Remove
  filler, circular restatements, repeated conclusions and unnecessary jargon.
  Do not add defensive-claim boilerplate. State a real uncertainty or scope
  limit once when it changes a decision; do not repeat disclaimers about what
  a note does not prove, certify or authorize. Prefer a small useful note over
  an exhaustive report that is difficult to read.
- Keep handoff focused on current work, evidence references, blockers and the
  next useful action. Generate progress from canonical ledgers; avoid manual
  duplicate counts, recurring full reports and unrelated documentation chores.
- Preserve dirty/untracked work, targets, useful evidence, game-specific Wine
  prefixes and analyzer projects. Exactness still requires a complete strict
  comparison; knowledge and successful commands alone confer no exact credit.


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

## Source tree discipline

- Follow the TH08-style product layout: `src/main/`, `src/op/`, `src/maine/`,
  `src/zun/`, and proved `src/shared/` code, with subsystem directories below
  each artifact.
- Never classify source by directory. Do not create `exact/`, `partial(s)/`,
  or `module(s)/`; exactness and source presence live in the ledgers.
- Treat `.cpp`, `.c`, and `.asm` as translation units. Use `.inl` only for a
  bounded body that a semantic translation unit includes.
- TH04 product source must not directly include `libs/`, `platform/`, `th01/`,
  `th02/`, `th03/`, or `th05/` paths. Existing unlocalized dependencies go
  through checked-in `compat/rec98/<upstream-path>` forwarding headers. Only
  that compatibility directory may name direct ReC98 paths.
- `compat/rec98/` is a reusable, attested migration boundary, not product
  source or authored progress. Do not copy declarations into it. Recover and
  attest required common declarations under the owning artifact or
  `src/shared/`, then remove the corresponding forwarder.
- Derive the current work queue and progress from `config/units.csv`,
  `config/th04_main_authored_functions.csv`, `docs/PROGRESS.md`, and
  `python3 scripts/status.py`. Historical evidence and stable unit IDs may
  retain words such as `module` or `partial`; they are replay provenance, not
  source-layout examples. Never recreate their former directory structure.
- The product build must ultimately use checked-in TH04 source and headers.
  Overlaying maintained source into pinned ReC98 is an Oracle, not a standalone
  build and not permission to bulk-import its source tree.
- Use `docs/SOURCE_LAYOUT.md` for new source placement. Treat an accepted
  translation unit's path, split, and include composition as replay inputs
  rather than cosmetic layout choices.

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
  result, and remaining unknowns. Keep it a concise current-state index;
  put chronological experiment details in bounded reconstruction notes and
  evidence/knowledge ledgers instead of appending session logs.
- Use `docs/reconstruction/README.md` to route focused notes. Continue an
  existing subject note when the same claim advances; create a new note only
  for a distinct ownership decision, reusable negative result, or replay
  surface.

## Minimal retention and checks

Keep necessary original inputs, active analyzer projects, current source,
exact-match ledgers and complete rebuild/comparison scripts. Keep locked tool
binaries and the headers, libraries and runtime dependencies actually in use.
Retain useful conclusions, current blockers and failed ideas briefly. Keep an
unresolved compiler context only if recreating it would be genuinely difficult.
A file's age, historical reference or old successful test is no retention reason.

Delete superseded builds, duplicate evidence, historical archives, unused
prefixes and cleanup reports. Remove obsolete document references too. Do not
add a cleanup framework, permanent inventory, audit report or another archive.
Do not overwrite canonical objects or existing receipts while experimenting.

Share matching Factory tools, isolate writable state, and distinguish host
from target architecture. Temporarily move uncertain components aside, test
only the affected compile/link/runtime/resource paths, and delete the temporary
copy after success. Restore on failure and compare against the original
environment. Moving the only installation does not free disk space.

Default CI must be fast and work in a clean checkout without private programs,
toolchains or reference checkouts. Check machine syntax, ledger consistency,
build source paths and accidental private files over the complete current tree.
Use the full PR/push range for whitespace checks. Select comparator and other
specialist tests by the change. Never regenerate prose or progress in CI.
Exact source changes still require complete owned bytes and relocations and
all affected consumers; cleanup and prose do not require a whole-history replay.
See docs/ANALYSIS_RETENTION.md for the concise policy.

## Shared Factory runtime

Follow [the shared tools instructions](docs/SHARED_TOOLS.md). Ghidra/JDK and
Wine executables are shared through Factory; repository scripts also work
without MCP. Use `scripts/shared_runtime.py` and the existing compiler/analysis
frontends. Keep this game's prefix, analyzer project, Java home/cache, target
and compiler profile isolated. Do not install duplicate tools or inherit
another game's `WINEPREFIX`. This shared-runtime procedure supersedes older
per-repository installation instructions; pinned versions/hashes still apply.
