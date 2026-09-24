# TH04 reconstruction handoff

Updated 2026-09-24. This is the concise resume index; live counts come from
`config/units.csv`, `config/th04_main_authored_functions.csv`,
`config/th04_function_boundaries.csv`,
`config/th04_decoded_function_acceptance.csv`, and `python3 scripts/status.py`.
The roadmap is [RE_ROADMAP.md](RE_ROADMAP.md); bounded evidence notes are
routed by [reconstruction/README.md](reconstruction/README.md).

## Resume checks

```sh
git status --short
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/compat_audit.py
```

Current target identity is `candidate-local-attested`: size, SHA-256, MZ
structure, tracking, function-boundary ledgers, and decoded acceptance validate,
but this is not proof of an official pristine release. Re-attest the active
disassembler database to target/header/entry/relocations/load digest/sampled
bytes before any new target observation. Keep one writable Borland session.

## Current non-MAIN state

| Artifact | Candidate boundaries: reviewed / corroborated / provisional | Function exact | Pending / blocked | Decoded source-owner bytes |
| --- | ---: | ---: | ---: | ---: |
| OP.EXE | 27 / 58 / 8 | 24 | 69 / 0 | 2,841 |
| MAINE.EXE | 29 / 36 / 7 | 24 | 48 / 0 | 2,247 |
| ZUN.COM | 13 / 0 / 0 | 0 | 11 / 2 | 404 |

OP's 2,841 source-owner bytes include two source-present but nonexact SCORE
codec candidates (274 bytes); 2,567 bytes are in the 24 accepted exact
functions. MAINE's 24 functions (2,247 bytes) are exact. These are decoded-function extents,
not packed-file byte totals. No honest packed-file denominator exists yet for
OP, MAINE, or ZUN. MAIN is not on the active reconstruction path: its 492/495
accepted authored functions and 27 file-backed authored bytes remain an
evidence-triggered side lane.

## Latest verified cohort: OP/MAINE shared vector math

Maintained source is `src/shared/math/vector.cpp` and its local declarations.
It naturally compiles a contiguous `0x5E`-byte OP/MAINE `SHARED` producer:
`polar` (`0x1C`) followed immediately by `VECTOR2_AT` (`0x42`). OP loaded
addresses are `1DA1:01A8` and `1DA1:01C4` (payload `0xDBB8` and `0xDBD4`);
MAINE addresses are `1CC7:0260` and `1CC7:027C` (payload `0xCED0` and
`0xCEEC`). Complete function bodies match raw-zero; independent tiling closes
them with `RETF 6` and `RETF 0xA`. The `vector2_at` declaration is only a
target-observed near reference to two 16-bit output words, not a full `SPPoint`
API claim.

Full decoded aggregate replay passes 24/24 functions in each artifact:

- OP receipt: `.analysis/reconstruction/probes/v570-op-vector-exact-aggregate-001/receipt.json`, SHA-256 `c68fd2ef401e95ec1135a2577aaa0a5f0a6b05838b6d7296ab8349a713e73c99`; all 804 ordered target relocations preserved.
- MAINE receipt: `.analysis/reconstruction/probes/v570-maine-vector-exact-aggregate-002/receipt.json`, SHA-256 `6539b07824f74d88146dbded2dda2f87b1e127a109e9e376458cbb219a48a22e`; all 559 ordered target relocations preserved.

Both candidate linked program images remain equal to the retained target-local
v489 baselines. This verifies the accepted decoded extents and aggregate replay,
not a packed EXE byte-for-byte reconstruction. The prior input-wait cohort
remains documented in
[TH04_SHARED_INPUT_WAIT_V565.md](reconstruction/packed/TH04_SHARED_INPUT_WAIT_V565.md);
the vector/math evidence is in
[TH04_SHARED_VECTOR_MATH_V570.md](reconstruction/op-maine/TH04_SHARED_VECTOR_MATH_V570.md).

## Replay footprint and next work

The replay helper now materializes compiler-facing C/C++ source and include
files plus only response-file-linked objects, while keeping independent
writable A/B trees. OP snapshots contain 2,549,948 source/include bytes,
171,255 root support-object/archive bytes, and 101,922 response-linked object
bytes; MAINE contains 2,583,609, 171,255, and 90,749 bytes respectively. The
previous source-tree copy was about 27 MiB per artifact/round. The helper is
TCC-only (do not apply its source filter to TASM). Focused worktrees and logs
are disposable; current private acceptance directories retain only their small
receipts. Delete experiment intermediates immediately after recording their
receipt, and preserve only artifacts covered by `config/analysis_retention.toml`.

Continue OP/MAINE from a fresh physical-boundary review and select one adjacent
menu or other small owner whose source and producer can be truthfully tested;
do not assume the next address-ordered function is the next good unit.
Preserve OP and MAINE SCORE TU composition, target restore provenance, v489
BGIMAGE, and v494 relocation/layout Oracles. Keep the two OP SCORE codec units
source-present/nonexact unless a natural-source cold build reaches raw zero;
never transcribe target rotates into inline assembly. For ZUN, all 13 authored
boundaries are reviewed, but 11 remain pending and two C++ units are blocked;
resolve source authority and component/runtime ownership before claiming
authored exactness. The ZUN library-origin graph-clear slice is support-only.

Historical MAIN residuals, ZUN runtime inventories, and per-version experiment
logs belong in their bounded notes, not this current-state handoff. After each
coherent change, run the focused replay, affected cold aggregate, full CI, and
`git diff --check`; update the ledgers and this handoff only from verified
results.
