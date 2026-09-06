---
name: th04-matching
description: Build and validate strict TH04 PC-98 reconstruction units with an attested Borland/TASM/TLINK toolchain, segment and relocation manifests, and raw zero-difference acceptance. Use for code generation, link layout, unit matching, or exact-state promotion.
---

# TH04 strict matching

Read `AGENTS.md`, `docs/BUILD_MATCHING.md`, `docs/ORACLES.md`, and the selected
unit/evidence rows.

## Gate the work

Require a verified target, reviewed complete extent, explicit ownership,
natural source, and attested tool binaries.  Do not begin exact promotion from
an unattested dump or cached object.
An upstream matching/finalized claim supplies no required evidence.  Rebuild
the candidate locally and rerun the entire required Oracle vector.

## Canonical loop

1. State the memory model, flags, segment/group declarations, TU order, and
   link inputs as a falsifiable toolchain hypothesis.
2. Cold-build the smallest truthful unit or artifact serially.
3. Compare object/map structure, complete extent, relocations, instruction/CFG
   shape, stack/register/segment behavior, x87, and raw bytes.
4. Classify the mismatch before editing: boundary, origin, source semantics,
   ABI, compiler profile, TU ownership, segment layout, link order, relocation,
   padding, library/runtime, or overlay.
5. Record a reproducible evidence receipt with all tool/input/output digests.
6. Promote `exact` only for zero raw differences and all required Oracles.
7. After shared changes, cold-replay every affected accepted unit.

`python3 scripts/compare_artifacts.py` exits zero only for raw identity.
Relocation-normalized equality is never eligible for exact promotion.
