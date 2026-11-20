# Reference repository analysis

This analysis pins the inspected revisions so later agents can distinguish
historical observations from current upstream state.

| Reference | Revision inspected | Role here |
| --- | --- | --- |
| N0zoM1z0/th08 | `bd54d865ebbc9f7291b355d152b16cc4b7f5be59` | mature agent memory, exact ledgers, cold aggregate replay |
| N0zoM1z0/th095 | `8adeea57830d63ad320a6c85be51f9069506ec34` | conservative in-progress workflow and independent Oracle policy |
| N0zoM1z0/th105 | `fa8a4149eeba27e9a1c78ab3bb03d970ef4f8266` | origin/boundary uncertainty and non-contiguous ownership |
| nmlgc/ReC98 | `b6ba5b0a529edbb31efdf8c0e939263804f8ee47` | PC-98/Turbo C++ knowledge and untrusted build candidate |
| nmlgc/mzdiff | `02603e1b070a1cfe5f9c580d49b9eb28617aeb4a` | ReC98-linked MZ comparison implementation |
| tsdko/98imgtools | `6c7a82a68addc5be2d4291a4bc98046a647b6235` | HDI geometry and PC-98 FAT-partition corroboration |

The clones live under ignored `_reference/` and are not project source.

## What transfers from the N0zo repositories

- exact target hashes and fail-closed database attestation;
- separate ledgers for candidate boundary, origin, source presence, and exact
  acceptance;
- bounded tasks, explicit evidence classes, durable repository memory, and
  current handoff;
- reproducible per-unit manifests with relocation-aware comparison;
- smallest-first builds, cold aggregate replay after shared changes, and no
  rounded exactness;
- local task skills that route an agent to the right rules and commands;
- target-independent public CI separated from private target checks.

TH095's current Ghidra layout was also checked directly: official downloads
and versioned installations stay under ignored `.tools/`, stable
`.tools/ghidra` and `.tools/jdk` links hide versioned paths from wrappers, and
the private project stays in ignored root `ghidra-project/`. TH04 adopts that
layout and headless wrapper pattern. It does not copy TH095's PE attestation:
TH04 independently validates MZ header/load views, segment mappings,
relocations, and `CS:IP` as documented in `docs/GHIDRA.md`.

## What does not transfer

- flat PE virtual addresses and section/RVA assumptions;
- COFF `REL32`/`DIR32` logic as the only relocation model;
- MSVC 7/8 ABI, EH/RTTI/COMDAT/LTCG conclusions;
- Win32 runtime and DirectX Oracles;
- one function equals one contiguous compiler symbol;
- PE-centric reccmp/objdiff coverage as a complete PC-98 verdict.

## ReC98 TH04 progress

The public ReC98 status page labels its figures **as of 2026-01-19**:

| Artifact | Reverse-engineered | Finalized | Position-independent |
| --- | ---: | ---: | ---: |
| TH04 total | 46.62% | 39.30% | 100% |
| `OP.EXE` | 100% | 91.77% | 100% |
| `MAIN.EXE` | 34.07% | 25.56% | 100% |
| `MAINE.EXE` | 60.40% | 60.40% | 100% |

ReC98 defines reverse-engineered as clarified purpose/names, usually but not
necessarily C++; finalized means decompiled or proved undecompilable.  These
are not N0zo-style strict per-function byte-match percentages.  The difference
between reverse-engineered and finalized is explicitly technical debt.

The inspected TH04 build contains separate `OP`, `MAIN`, and `MAINE` link
lists, launcher subprograms, large ASM slices, shared earlier-game source,
`master.lib`, generated sprite data, and Borland runtime libraries.  Its
project documentation states that the master branch is kept buildable to
artifacts indistinguishable from the originals.  This repository has not yet
accepted that broader claim: it rebuilt the pinned commit three times and ran
all 20 selected TH01-TH05 outputs through the local Oracle vector.  Only three
flat COM candidates are raw-exact, and none of the four TH04 candidates pass.

## TH04 position independence

ReC98 reached 100% PI for TH04's `OP.EXE`, `MAIN.EXE`, and `MAINE.EXE`
in P0244. Its counter screens hexadecimal operands in selected assembly
dumps against each executable's ZUN data range. The authors resolve
addresses to symbols and distinguish constants from references. The FAQ
excludes structure resizing, and the counter disables address counting
for TH04 `ZUN.COM`. The exactness ledgers and portable play results
measure other properties. The maintained DOS executables pass a local
check of the same source criterion after two controlled relinks, a Stage 4
DOS replay, and review of register-carried literals.
[Local PI evidence](reconstruction/product/TH04_DOS_POSITION_INDEPENDENCE.md).

[FAQ and scope](https://github.com/nmlgc/rec98.nmlgc.net/blob/master/faq.html#L185),
[counter configuration](https://github.com/nmlgc/rec98.nmlgc.net/blob/master/rec98repo.go#L179),
[TH04 milestone](https://rec98.nmlgc.net/blog/2023-06-13).

- **MAINE.** ReC98's last TH04 PI patch changed the `CONG00.pi` address
  from a literal DGROUP offset `00A8h` to `offset _CongFN`. Local C++
  obtains the pointer directly from the string literal. The current DOS
  build also checks IRQ-vector and self-modifying renderer destinations
  in the linked executable. [Upstream patch](https://github.com/nmlgc/ReC98/commit/97f0c3b4f53a60caed48ffba1a7fa0817fd1dd0e),
  [local entry](../src/maine/end/main.inl#L4),
  [link audit](../scripts/probes/audit_th04_native_irq_vectors.py).
- **OP.** The EGC setup write to `0000:0495h` updates PC-98 BIOS state.
  A scan of direct literal memory operands in maintained source found
  hardware and DOS accesses of this kind. Register-carried addresses and
  relative assumptions still need review. [EGC setup](../src/op/hardware/egc_start_copy.inl#L11).
- **MAIN.** The carpet code looks up its tables through symbols.
  `HUD_SCORE_PUT` resolves `_hiscore` symbolically and reaches `_score` by
  decrementing through the end of the adjacent array. Pinned TASM/TLINK
  and a CPU fixture at load segment `2000h` ran the source routine with a
  stub that captured both gaiji rows. A 16-byte insertion before the
  routine and another before the pair moved all three symbols and kept
  the rows `99999999` and `87654321`. Inserting two bytes containing
  `02h 03h` between the arrays instead changed the second row to
  `32876543`. ReC98 preserves the same adjacency in its 100% source.
  Treat the two arrays as one layout owner when moving them, as with
  the random ring and cursor.
  [Carpet lookup](../src/main/stage/carpet_anim_row_level.inl),
  [score routine](../src/main/score/update.asm#L72),
  [upstream score routine](https://github.com/nmlgc/ReC98/blob/b6ba5b0a529edbb31efdf8c0e939263804f8ee47/th04/main/scoreupd.asm#L68),
  [random ring](reconstruction/main/TH04_MAIN_RANDRING_SEMANTICS_V1244.md).
- **ZUN.** The composite builder adjusts the directory when an embedded
  COM changes size. An unreachable one-byte insertion before the
  selector's directory assembled and linked, but the builder rejected
  the resulting 224-byte stub. The maintained launcher contract pins
  three stub lengths and reads the COMCSTM header fields at fixed offsets.
  [Composite builder](../scripts/build_zun_composite.py#L22),
  [selector](../src/zun/launcher/selector.asm#L127),
  [header consumer](../src/zun/launcher/customization_stub.asm#L18).

The bounded receipts are indexed as `ev-th04-main-pi-score-adjacency`
and `ev-th04-zun-pi-selector-length`.

## ReC98 Oracle assessment

ReC98's reported strongest Oracle is the final linked artifact under its
documented
[`Rule #1`](https://github.com/nmlgc/ReC98/blob/b6ba5b0a529edbb31efdf8c0e939263804f8ee47/CONTRIBUTING.md#rule-1):
the decompressed program image and unordered set of
relocations must not change.  It explicitly permits alternate encodings of
identical x86 instructions and trailing zero padding.  The linked `mzdiff`
tool reports several MZ dimensions but intentionally follows that policy; it
is not equivalent to this repository's raw whole-file verdict.  COM/container
outputs use complete byte equality.

The local attested cold build demonstrates the distinction.  ReC98's
`OP.EXE` and `REIIDEN.EXE` have exact program images and relocation multisets
but different relocation order/header bytes; `FUUIN.EXE` has an exact program
image and ordered relocations but a 1,504-byte larger header.  Our gate rejects
all three.  `ZUNSOFT.COM` is raw-exact.  Repeating the cold build produced the
same candidate vector, so these are stable comparator-policy observations
rather than a transient build failure.

The all-game survey provides a second kind of calibration.  All three cold
builds produce the same 20-file candidate identity, and the five game-specific
OMF sets reproduce after narrowly normalizing Borland dependency timestamps.
However, strict TH04 comparison reports broad program/relocation differences
for `OP.EXE` and `MAINE.EXE`, 3,326 outside-relocation-site program-byte
differences for `MAIN.EXE`, and an MZ-versus-flat-COM format mismatch for
`ZUN.COM`.  These measurements are useful routing evidence and directly reject
any interpretation of ReC98's editorial progress figures as local exactness.

The gaps for an autonomous agent are control-plane gaps, not a criticism of
the reconstruction result:

- target hashes and canonicality are not repository-local manifests;
- no checked-in per-unit accepted ledger or replay command binds each progress
  claim to a target/tool/output digest;
- progress dimensions (RE/finalized/PI) are editorial metrics, not raw exact
  unit states;
- mzdiff is a helpful policy-specific display tool but has no JSON schema,
  strict ordered-relocation/full-header gate, mismatch taxonomy,
  unit ownership, instruction/CFG/ABI analysis, or runtime differential layer;
- build success and whole-image equality do not independently test semantic
  hypotheses, undefined behavior, or emulator/hardware variance.

## Our design response

This repository keeps raw identity as the final non-negotiable gate while
adding provenance, structural MZ, relocation-normalized diagnostic, reviewed
ownership, compiler probes, static semantics, runtime state/VRAM/event traces,
cross-emulator runs, metamorphic tests, and ledger/reproducibility Oracles.
Results remain a vector.  The framework does not average away a failure.
No ReC98 unit or status is pre-approved: acceptance begins only after local
boundary review, attested cold rebuild, and our complete Oracle gate.
