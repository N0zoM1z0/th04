# Multi-dimensional Oracle policy

## Principle

No single comparator answers every reconstruction question.  The framework
uses independent Oracles that fail for different reasons and publishes a
verdict vector instead of hiding evidence behind one similarity percentage.

`config/oracles.toml` is the machine-readable policy.  A supporting Oracle can
increase semantic confidence or localize a mismatch, but it cannot override a
failed exact requirement.

Exact evidence is artifact-scoped by default.  A passing row for another
artifact—or a generic row with no artifact—cannot satisfy a unit's required
gate.  Only `toolchain-identity` and `ledger-consistency` are deliberately
global; compilation replay, OMF, layout, raw bytes, and cold replay must be
attached to the same artifact as the exact unit.

## Layer 0: provenance and target identity

Record the outer archive only in a private import receipt.  Public identity
pins the Japanese HDI, HDI geometry, FAT partition offset and label, DOS path,
artifact size, MD5, SHA-256, and detected format.  An active
IDA/Ghidra database must additionally agree on MZ fields, `CS:IP`, relocation
count, load-module digest, and sampled mapped bytes.

The current target is `candidate-local-attested`: it is exactly the user's
supplied legal copy.  External canonicality remains a separate claim until an
independently sourced pristine dump agrees.  A local ReC98 rebuild is useful
toolchain calibration, but its upstream status is not independent provenance.

The operational Ghidra check is deliberately two-sided. A headless Java script
exports the database's original and modified `FileBytes`, header and load
memory snapshots, source mappings, relocation records, entry points, and
analysis state. `scripts/attest_ghidra_database.py` then derives the expected
views independently from the pinned target with `scripts/lib/pc98.py`. It
requires exact full digests and mapping/relocation equality plus deterministic
samples. A per-run nonce prevents stale exports from passing when a Ghidra
post-script fails but the outer headless process returns zero.

This is a database-consistency Oracle, not an independent semantics Oracle.
It proves which target the database represents and how the pinned MZ loader
mapped it; it does not validate Ghidra's inferred functions or decompiler.
Installation, commands, and calibrated dimensions are in `docs/GHIDRA.md`.

## Layer 1: container and format integrity

For MZ artifacts, parse and report:

- declared file size versus physical size;
- header paragraphs and relocation-table bounds;
- initial `CS:IP`, `SS:SP`, allocation bounds, checksum, and overlay number;
- relocation order and set;
- bytes before the load module, program image, and trailing overlay.

For flat COM files, record the complete byte extent and digest.  TH04's
`ZUN.COM` is MZ and must not be treated as a flat COM solely by extension.

## Layer 2: layout and relocation

Compare these dimensions separately:

- complete raw artifact;
- MZ header fields and uninterpreted header bytes;
- ordered relocation table and order-insensitive relocation set;
- relocation-entry multiplicity and words stored at shared relocation sites;
- program image as linked;
- program image with words at valid MZ relocation sites normalized;
- overlay/trailing bytes;
- linker map segment/group order, sizes, classes, alignment, and public symbols.

Relocation-normalized equality is a diagnostic: it can reveal a link/load
layout issue while proving that most non-relocated content is identical.  It
never qualifies as exact.

## Layer 3: bounded static semantics

A reviewed unit comparison should eventually emit:

- exact byte spans and first/count of differences;
- bounded mismatch runs and a count partitioned inside/outside relocation-site
  bytes;
- 16-bit instruction stream with operand widths;
- CFG edges, switch/jump-table ownership, near/far calls and returns;
- stack frame, calling convention, register and segment-register effects;
- referenced strings, globals, ports, interrupts, and relocation sites;
- x87 stack/dataflow fingerprints;
- compiler-owned, library-owned, padding, and shared-tail exclusions.

Instruction normalization helps diagnosis, not acceptance.  A decompiler and
the disassembly it was derived from are one evidence class.

## Layer 4: compiler and ABI

Use minimal, falsifiable Turbo C++ 4.0J/TASM/TLINK probes for memory model,
near/far distance, calling convention, scalar width, packing, inline behavior,
local allocation, segment/group pragmas, jump tables, x87 emission, fixups, and
link order.  Record source digest, exact commands, tool binary digests, object
and map digests, and observed output.

A probe is independent only when it tests a hypothesis; target bytes pasted
into source or assembly are circular evidence.

Compiler output is checked one layer earlier than final MZ comparison.  The
strict Intel OMF parser validates every record length and checksum, requires a
single THEADR-to-MODEND module boundary with no trailing bytes, and extracts
COMENT producer and dependency records.  The attestation probe must observe
`TC86 Borland C++ 4.02`, `Turbo Assembler  Version 5.0`, and the pinned
`dos.h` path.  These facts catch wrong-tool and wrong-include contamination;
they do not prove that a source reconstruction or ABI hypothesis is correct.

OMF reports keep raw and Borland-dependency-timestamp-normalized identities.
Only the two 16-bit DOS time/date words in COMENT class `E9` are normalized,
then the record checksum is recomputed and the stream reparsed.  Code, data,
fixups, paths, producers, record order, and build-time strings remain exact.
This lets an agent distinguish harmless file-metadata churn from genuine
object changes without discarding either observation.

## Layer 5: runtime differential

Once a deterministic harness exists, compare original and candidate with the
same initial disk state and input timeline:

- checkpointed conventional/EMS memory ranges;
- interrupt, I/O port, file access, and allocation event traces;
- raw PC-98 planar VRAM and palette state before screenshot rendering;
- frame/tick counters, RNG state, entity summaries, score, and replay output;
- PMD/MMD command/state events before waveform comparison.

Use at least DOSBox-X and a debug Neko Project II build.  A result seen in both
reduces emulator-model risk.  Runtime equality proves behavior only for the
recorded scenario, not byte identity.

## Layer 6: metamorphic and invariant checks

Vary one dimension while holding the semantic expectation fixed: load segment,
available conventional/EMS memory, CPU timing, GDC rate where supported, sound
mode, input batching, and archive-versus-loose data paths.  Check explicit
invariants rather than screenshots alone.  These tests expose hidden absolute
addresses, uninitialized state, timing assumptions, and accidental emulator
dependencies.

## Exact acceptance

A unit is exact only when all required conditions hold:

1. Target identity and canonicality policy are satisfied.
2. Its full code/data/relocation ownership is reviewed.
3. Natural source or justified original-style assembly is present.
4. The pinned toolchain and complete build inputs are attested.
5. The configured cold build is replayable.
6. Layout and relocation manifests agree.
7. Every raw byte in the accepted extent agrees.
8. Ledger validation passes.
9. Every affected previously accepted unit replays from a cold build.

Artifact-level exactness additionally requires the whole physical file,
including header, relocation table, padding, library/runtime code, and overlay,
to have the target SHA-256.  There is no rounded `99.99% exact` state.

## Comparator self-tests

`scripts/smoke_oracles.py` uses private targets from all five PC-98 games as
real-world format inputs.  It verifies self-equality, then injects independent
header, relocation-table, relocated-word, program-byte, overlay, and COM-byte
mutations into one representative of each available format/game.  Each
mutation must fail raw exactness and trip its intended dimension.  This proves
comparator behavior over the originals, not compiler/build reproduction.
Public CI also uses synthetic MZ/COM fixtures so regression tests need no game
data.

`scripts/smoke_ghidra_oracle.py` independently mutates a fresh private database
export's loaded byte, relocation result, source mapping, and run nonce. Every
case must fail its intended dimension. The real-corpus loader controls are TH04
`OP.EXE` with zero relocations, TH01 `OP.EXE` with 625 relocations, and analyzed
TH04 `MAIN.EXE` with 1,136 relocations. These controls validate the Oracle and
loader contract without promoting any inferred boundary or reconstruction.

The compiler/build calibration is now live.  Three cold source
materializations of pinned ReC98 revision
`b6ba5b0a529edbb31efdf8c0e939263804f8ee47` produced the same 20 selected
TH01-TH05 outputs, and all 416 generated OMF objects passed strict framing and
checksum validation.  Only three candidates are raw-exact.  All four TH04
outputs are rejected, with measured format, size, header, relocation, program,
and overlay dimensions retained for routing.  The five game-specific OMF sets
also agree after normalizing only Borland dependency timestamps; build-time
strings in the separate Research/Pipeline objects remain visible differences.
`config/rec98_pc98_calibration.toml` pins this all-game vector, while
`config/rec98_th01_calibration.toml` retains the focused policy differential.
Neither can turn a known rejection into an exact pass.

## Upstream quarantine and revalidation

ReC98 source, labels, comments, progress figures, and claimed matching outputs
are candidate inputs.  The same rule applies to every other reconstruction,
including repositories owned by this account.  Upstream evidence must use the
`upstream` evidence class and can never satisfy an exact-required Oracle.

To accept imported work, first reconcile its byte ownership against the pinned
TH04 target.  Then rebuild it locally from a clean tree with attested tools and
inputs, compare the full configured extent and relocation/layout surfaces, and
replay every affected accepted unit.  A local exact result is our evidence; the
upstream claim is only provenance for where the candidate came from.

The `upstream-policy-differential` Oracle explicitly records cases where an
upstream comparator and this repository answer different questions.  ReC98's
documented MZ rule accepts equal decompressed program images and unordered
relocation sets; our full-file gate additionally preserves header bytes,
ordered relocation entries, padding, overlays, and every raw byte.  A policy
differential explains a result and guides tooling.  It is diagnostic-only and
can never lower a required gate.

## Analysis accelerators are not acceptance Oracles

`scripts/export_analysis_bundle.py` emits hash-verified load-module bytes,
relocation-normalized bytes, a hypothetical relocated image, address metadata,
and relocation CSV below private `.analysis/`.  These are deterministic views
of target facts for disassemblers and loaders.

`scripts/mine_shared_blocks.py` finds byte-verified runs across the five games
after zeroing MZ relocation words.  It labels every output `candidate_only`:
shared bytes can route searches toward stable libraries, compiler helpers, or
reused game code, but do not establish source identity, semantics, boundaries,
or exact reconstruction.
