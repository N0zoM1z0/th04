---
name: th04-re
description: Reconstruct one bounded code or data unit from the locally attested Japanese TH04 PC-98 artifacts with segment-aware target evidence and conservative ledgers. Use for disassembly, decompilation, naming, boundary review, ABI recovery, or source implementation.
---

# TH04 bounded reconstruction

Read `AGENTS.md`, `docs/RE_HANDOFF.md`, `docs/ARCHITECTURE.md`,
`docs/RE_WORKFLOW.md`, and `docs/ORACLES.md` completely before changing state.

## Preflight

Run `python3 scripts/preflight.py`.  Attest the analysis database against the
selected manifest target, including MZ `CS:IP`, relocation count, load-module
digest, and sampled bytes.  Stop target-dependent work if attestation fails.

## Recover one unit

1. Identify artifact plus segment:offset and record a bounded candidate.
2. Reconcile entries, exits, shared tails, far/near edges, jump tables,
   interleaved data, relocation sites, padding, and adjacent ownership.
3. Inspect target-local callers, callees, xrefs, strings, ports, interrupts,
   globals, and disassembly before accepting a semantic name.
4. Separate observed facts, compiler evidence, runtime evidence, ReC98 or
   adjacent-game corroboration, and inference.
   Quarantine all upstream source and statuses as candidates; never inherit an
   upstream exact/finalized claim.
5. Recover memory model, calling convention, widths, packing, segment/group,
   side effects, and x87 behavior before selecting C/C++ shape.
6. Implement natural source; no pseudocode paste, target-byte arrays, fake
   returns, inert padding, ABI lies, or unexplained assembly.
7. Update source presence and evidence without claiming exactness.
8. Hand byte work to `$th04-matching`; use `$th04-oracle` for ambiguous claims
   and `$th04-runtime` for behavioral validation.

Keep databases and raw decompiler output under `.analysis/`.  Durable facts
belong in source, ledgers, focused notes, or reproducible probes.
