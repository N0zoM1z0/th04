# Architecture

## Scope

The exact branch reconstructs four TH04 artifacts independently:

| Artifact | Responsibility | Target format |
| --- | --- | --- |
| `OP.EXE` | menus, setup, Music Room, title flow | DOS MZ |
| `MAIN.EXE` | stages, player, enemies, bosses, HUD | DOS MZ |
| `MAINE.EXE` | endings, staff roll, score flow | DOS MZ |
| `ZUN.COM` | launcher and embedded resident programs | MZ container despite its `.COM` name |

Shared code is not assumed identical merely because ReC98 builds one source
file into several artifacts.  Each artifact keeps its own target identity,
link context, relocation surface, and accepted units.

The locally attested MZ topology is intentionally asymmetric: `MAIN.EXE` has a
6,144-byte header with 1,136 relocation entries and a 150,114-byte load module;
the other three artifacts have 32-byte headers and zero relocation entries.
All four declare relative entry `0000:0000`.  These are observed container
facts, not proof of source boundaries or compiler ownership.

## Why PE-era workflows do not transfer directly

TH08/TH095/TH105 have a flat 32-bit virtual-address model, PE sections, COFF
objects, REL32/DIR32 relocations, and MSVC-specific class/EH behavior.  TH04 is
16-bit real-mode DOS code with:

- `segment:offset` addressing and a runtime-selected load segment;
- near/far code and data pointers whose types affect both ABI and bytes;
- multiple memory models, DGROUP, named code groups, and 64 KiB limits;
- MZ relocation entries that patch words inside the load module;
- 8086 plus selected 80386 instructions and x87 floating-point code;
- Borland/TASM/TLINK ordering, padding, fixup, and translation-unit effects;
- PC-98 VRAM planes, GDC/GRCG/EGC, interrupts, EMS, PMD/MMD, and timing;
- launcher containers and code that may be handwritten, self-modifying, or
  deliberately left in assembly.

Therefore no bare linear address is a durable identity.  A unit is identified
by artifact, segment/group (once known), offset, file extent, and ownership.
Emulator linear addresses are observations that also record the load segment.

## Control plane

The repository stores five independent kinds of durable state:

1. `targets.toml` pins private inputs and provenance.
2. `units.csv` records boundaries, ownership, source presence, and acceptance.
3. `hypotheses.csv` records falsifiable semantic/ABI claims.
4. `evidence.csv` records Oracle observations and replay information.
5. `th04_function_boundaries.csv` records all-artifact function-like
   observations, origin classification, boundary confidence, and work routing;
   it is not an exactness ledger.

Exact-required evidence has an explicit scope: global, artifact, or
unit-plus-file-extent as declared in `config/oracles.toml`. This keeps the
ledger strict without tying disposable tool caches or databases to one host.

This separation prevents common false equivalences:

- a decompiler function is not a reviewed compiler unit;
- a ReC98 name is not a TH04 target observation;
- source presence is not semantic confidence;
- semantic equivalence is not code-generation equivalence;
- normalized equality is not raw equality;
- one exact function is not an exact translation unit or executable.

## Reconstruction state machine

`config/units.csv` permits these monotonic states:

```text
candidate
  -> boundary-reviewed
  -> source-present
  -> structural
  -> exact
```

`blocked` and `excluded` are side states. `blocked` keeps a documented missing
dependency. `excluded` requires an explicit reason such as third-party
ownership, compiler-generated code, an immutable asset, proven undecompilable
assembly, or a superseded overlapping bookkeeping owner retained only to keep
old evidence addressable. Excluded rows are not current work. Moving backward
is allowed whenever stronger evidence invalidates an earlier claim. Exact is
deliberately brittle.

## Source architecture

The `src/` tree is the TH04 product source tree. Like TH08, it is organized by
executable and engine responsibility, never by reconstruction status:

```text
src/
  main/       MAIN.EXE gameplay, hardware, formats, and UI subsystems
  op/         OP.EXE source when reconstructed
  maine/      MAINE.EXE source when reconstructed
  zun/        ZUN.COM source when reconstructed
  shared/     declarations or implementations proved shared by TH04 artifacts
```

Subdirectories below an artifact are semantic (`boss/`, `bullet/`, `sound/`,
and so on). Do not create `exact/`, `partial/`, `partials/`, `module/`, or
`modules/` source directories. Exactness, origin, reviewed boundaries, and
source presence belong only in `config/units.csv`, the authored-function
ledgers, and their evidence rows. The all-artifact inventory and its generation
policy are documented in `docs/BOUNDARY_REVIEW.md` and
`config/th04_boundary_review.toml`.

Some stable ledger and evidence IDs still contain historical `module` or
`partial` wording. They remain unchanged so old receipts stay addressable and
must not be interpreted as source paths, current work-queue priority, or a
template for new identifiers. Live state comes from the ledgers and generated
progress, while product ownership comes from the semantic `src/` tree.

A `.cpp`, `.c`, or `.asm` file represents a buildable translation unit or a
standalone source owner. A `.inl` file is a bounded body that is included by a
semantic translation unit; the extension records source composition, not a
weaker acceptance state. Replay-only overlay and fragment mechanics belong in
`config/th04_main_exact_units.toml` and must not determine the product layout.

The intended end state is a clean checkout whose TH04 source builds with the
pinned compiler, assembler, linker, and documented external libraries without
using `_reference/ReC98` as a source or header search path. Product source must
not directly include `libs/`, `platform/`, `th01/`, `th02/`, `th03/`, or
`th05/` paths. The current unlocalized dependencies are routed through
`compat/rec98/<upstream-path>`, a repository-owned forwarding boundary that is
materialized and attested by exact replay. Direct upstream paths are permitted
only inside that compatibility directory.

`compat/rec98/` contains no copied declarations and is not reconstructed source
or authored progress. It makes the dependency visible and gives the PC-98
repositories a reusable migration contract; it does not make the build
standalone. Recover required declarations into the appropriate TH04 artifact
or a proved `src/shared/` ownership surface, attest them, and remove the
corresponding forwarder. Historical ReC98 paths may remain in replay manifests,
linker-map evidence, and focused notes because those fields describe the pinned
calibration scaffold rather than the TH04 product layout. See
`compat/rec98/README.md`.

The current tree is not yet a complete standalone game build: only bounded
`MAIN.EXE` source owners have been reconstructed, and several still compile in
the exact Oracle through pinned ReC98 scaffolding. Do not conceal that gap with
copied declarations or a bulk import. Recover bounded TH04 units from the
verified target, using ReC98 and adjacent games as corroboration. When shared
code is proved, keep target-specific build/link ownership explicit rather than
erasing it behind a modern abstraction.

Exact reconstruction and a future portable runtime are separate products.  A
portable branch may replace segmentation and hardware access only after the
exact branch has captured the behavior and a differential runtime Oracle can
guard the change.

## Private and generated state

`.tools/` contains the ignored pinned Ghidra/JDK downloads and versioned
installations. `ghidra-project/` contains ignored private headless databases,
following TH095's non-dot-prefixed project layout. `.analysis/` contains
targets, disk images, compiler installations, Ghidra XDG state and exports,
emulator images, DIET payload observations, TASM listings, probes, traces, and
reports. None is committed. It is a working cache, not an archive: keep pinned
inputs/toolchains, active databases, current boundary-review inputs, and the
latest focused/aggregate replay receipts; prune superseded A/B source trees,
old probe matrices, and stale disassemblies after their commands, outcomes, and
digests are durable. A historical `.analysis` path in `config/evidence.csv` is
provenance, not a promise that the cache still exists.

Reusable boundary tooling is grouped under `scripts/boundary_review/`; only
its private outputs stay ignored. A durable conclusion moves into source, a
checked-in ledger, a focused evidence note, or an executable test; private tool
state never becomes the only copy of project knowledge.

Ghidra 12.1.3's pinned `MzLoader` loads the program at segment `0x1000`,
applies the MZ relocation words, exposes the header through a `HEADER` overlay,
and creates entry `(0x1000 + CS):IP`. Its relocation-derived blocks and `RETF`
boundary adjustment are heuristic. `scripts/ghidra.py ARTIFACT check` therefore
attests full bytes, mappings, relocations, and entry while keeping every block
and auto-analysis function provisional. See `docs/GHIDRA.md`.
