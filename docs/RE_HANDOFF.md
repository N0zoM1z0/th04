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
| OP.EXE | 25 / 60 / 8 | 22 | 71 / 0 | 2,747 |
| MAINE.EXE | 27 / 38 / 7 | 22 | 50 / 0 | 2,153 |
| ZUN.COM | 13 / 0 / 0 | 0 | 11 / 2 | 404 |

OP's 2,747 source-owner bytes include two source-present but nonexact SCORE
codec candidates (274 bytes); 2,473 bytes are in the 22 accepted exact
functions. MAINE's 22 functions are exact. These are decoded-function extents,
not packed-file byte totals. No honest packed-file denominator exists yet for
OP, MAINE, or ZUN. MAIN is not on the active reconstruction path: its 492/495
accepted authored functions and 27 file-backed authored bytes remain an
evidence-triggered side lane.

## Latest verified cohort: OP/MAINE shared input wait

Maintained source is `src/shared/hardware/input_wait.cpp` plus
`src/shared/hardware/input.hpp` and `frame_delay.hpp`. The reviewed complete
function is 0x56 bytes in each artifact: OP load `1DA1:0152` (payload `0xDB62`,
MAP `0DA1:0152`), MAINE load `1CC7:020A` (payload `0xCE7A`, MAP `0CC7:020A`).
Independent A/B cold builds produce
raw-zero matches and preserve each target's relocations. The target slices were
also checked as contiguous disassembly tiles; that is boundary evidence, not a
second semantic runtime Oracle.

Full decoded aggregate replay passed 22/22 functions in each artifact:

- OP receipt: `.analysis/reconstruction/probes/v567-op-aggregate-001/receipt.json`, SHA-256 `f53b5a697f71c855cdcdbc319be74e941097feaf47ca41d3ce39d5b5b896ae2d`; all 804 ordered target relocations preserved.
- MAINE receipt: `.analysis/reconstruction/probes/v567-maine-aggregate-002/receipt.json`, SHA-256 `a382530b4448445662e2cbe1daafe7b2466bde7cdd5a86c693d0cff7baeea661`; all 559 ordered target relocations preserved.

Both candidate linked program images remain equal to the retained target-local
v489 baselines. This verifies the accepted decoded extents and aggregate replay,
not a packed EXE byte-for-byte reconstruction. Focused evidence and the snapshot
size experiment are documented in
[TH04_SHARED_INPUT_WAIT_V565.md](reconstruction/packed/TH04_SHARED_INPUT_WAIT_V565.md).

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
input/vector/menu owner whose source and producer can be truthfully tested.
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
