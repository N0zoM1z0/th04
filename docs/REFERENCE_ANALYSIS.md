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
accepted that broader claim: it has now rebuilt the pinned commit locally and
found a concrete policy differential in the TH01 outputs.

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
