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

The repository stores four independent kinds of durable state:

1. `targets.toml` pins private inputs and provenance.
2. `units.csv` records boundaries, ownership, source presence, and acceptance.
3. `hypotheses.csv` records falsifiable semantic/ABI claims.
4. `evidence.csv` records Oracle observations and replay information.

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

`blocked` and `excluded` are side states.  `blocked` keeps a documented missing
dependency; `excluded` requires an origin such as third-party library,
compiler-generated code, immutable asset, or proven undecompilable assembly.
Moving backward is allowed whenever stronger evidence invalidates an earlier
claim.  Exact is deliberately brittle.

## Source architecture

The `src/` tree starts empty.  Do not bulk-import ReC98.  Recover bounded TH04
units from the verified target, using ReC98 and adjacent games as corroboration.
When shared code is proved, keep target-specific build/link ownership explicit
rather than erasing it behind a modern abstraction.

Exact reconstruction and a future portable runtime are separate products.  A
portable branch may replace segmentation and hardware access only after the
exact branch has captured the behavior and a differential runtime Oracle can
guard the change.

## Private and generated state

`.tools/` contains the ignored pinned Ghidra/JDK downloads and versioned
installations. `ghidra-project/` contains ignored private headless databases,
following TH095's non-dot-prefixed project layout. `.analysis/` contains
targets, disk images, compiler installations, Ghidra XDG state and exports,
emulator images, probes, traces, and reports. None is committed. A durable
conclusion moves into source, a checked-in ledger, a focused evidence note, or
an executable test; private tool state never becomes the only copy of project
knowledge.

Ghidra 12.1.3's pinned `MzLoader` loads the program at segment `0x1000`,
applies the MZ relocation words, exposes the header through a `HEADER` overlay,
and creates entry `(0x1000 + CS):IP`. Its relocation-derived blocks and `RETF`
boundary adjustment are heuristic. `scripts/ghidra.py ARTIFACT check` therefore
attests full bytes, mappings, relocations, and entry while keeping every block
and auto-analysis function provisional. See `docs/GHIDRA.md`.
