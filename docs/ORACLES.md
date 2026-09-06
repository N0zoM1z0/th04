# Multi-dimensional Oracle policy

## Principle

No single comparator answers every reconstruction question.  The framework
uses independent Oracles that fail for different reasons and publishes a
verdict vector instead of hiding evidence behind one similarity percentage.

`config/oracles.toml` is the machine-readable policy.  A supporting Oracle can
increase semantic confidence or localize a mismatch, but it cannot override a
failed exact requirement.

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
data.  ReC98 build validation remains blocked until the exact toolchain is
attested.

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
