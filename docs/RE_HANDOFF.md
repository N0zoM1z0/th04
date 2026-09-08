# TH04 reconstruction handoff

## Current phase

The headless reconstruction environment is operational. A whole-artifact
boundary/origin review has now been completed without starting another source
reconstruction batch. `config/th04_function_boundaries.csv` is the current
routing inventory and `docs/BOUNDARY_REVIEW.md` is its generated explanation.

The inventory contains 2,120 distinct function-like observations:

- 732 authored reconstruction candidates: OP 94, MAIN 553, MAINE 72, ZUN 13;
- 248 accepted exact MAIN functions and two reviewed blocked MAIN functions;
- 482 authored candidates otherwise unreviewed;
- 52 original-style ASM observations in a separate attestation queue;
- 1,336 compiler/runtime/library/data/switch observations explicitly excluded.

Within the accepted 136-owner MAIN cohort, the live reviewed totals are:

- authored C/C++ bytes: **38,041 / 38,072 exact (99.918575%)**;
- authored functions: **248 / 250 exact (99.200000%)**;
- original-style ASM: **9 units / 1,489 exact bytes**, tracked separately;
- reviewed nonexact authored bytes: **31 bytes** in two functions.

These percentages use only accepted reviewed MAIN ledger denominators. They
are not a claim that 99.92% of an executable or the game has been
reconstructed. Derive current numbers with `python3 scripts/status.py`;
`config/units.csv`, `config/th04_main_authored_functions.csv`, and
`config/th04_function_boundaries.csv` override prose.

`OP.EXE`, `MAINE.EXE`, and `ZUN.COM` still have no accepted reconstruction
units. No deterministic TH04 runtime-differential scenario has been authored.

## Target and analysis identity

The active `th04-main` target is `.analysis/targets/th04/main.exe`:

- size: 156,258 bytes;
- SHA-256: `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`;
- MZ header: 6,144 bytes;
- entry `CS:IP`: `0000:0000` (`1000:0000` at the Ghidra image base);
- relocations: 1,136;
- load-module SHA-256:
  `3a30221339626ce7608e3169063864b55d78881d64e90e56e1dd8e5a02ae140d`.

The target and read-only Ghidra database pass the configured MZ, entry-point,
relocation, mapping, and sampled-byte attestations. Target canonicality remains
`candidate-local-attested`; this is a known provenance gap, not proof of a
pristine official dump.

The other three on-disk targets are DIET-packed MZ containers. Their own
attested decompressor stubs were run at load segments `0x1000` and `0x2000`;
both runs produced identical unrelocated payloads and relocation streams:

- OP: 69,028 bytes, 804 relocations, SHA-256
  `13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`;
- MAINE: 62,414 bytes, 559 relocations, SHA-256
  `7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c`;
- ZUN: 13,422 bytes, no relocations, SHA-256
  `baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.

OP and MAINE Ghidra projects use private diagnostic hybrid MZ images: the load
module is target-observed, while the checked header and relocation table come
from the cold candidate. They are not original-unpacked-EXE claims. The flat
ZUN payload is raw exact to the cold candidate composition pipeline and is
split into configured selector/data/embedded-COM/stub regions.

## Latest accepted batch

v88 recovers public FAR `reimu_update()` at `0x2F3AB..0x2F8ED` as one
0x543-byte exact owner: 0x515 bytes of code plus two compiler switch-table
regions. Fresh Ghidra cross-links its body beyond the true owner; pinned TASM,
raw decoding, switch-target validation, and exact map ownership define the
accepted extent.

v89-v94 recover the first Gengetsu family at `0x2F8EE..0x2FEDE`: 1,521 bytes,
seven exact C++ owners, and twelve exact functions. v95-v98 then close the rest
of `MAIN_036_TEXT` from `0x2FEDF..0x306EB`: another 2,061 exact bytes in four
natural-C++ owners and seven exact functions. Important boundaries are:

- `0x2F8EE`, `0x2F903`, and `0x2F97A` are three functions in one physical
  TC86 producer. Splitting the producer loses the alignment byte before the
  middle function's sparse switch tables.
- Ghidra has no entry at `0x2F8EE`, `0x2F97A`, **or `0x30050`**. The last one
  is admitted only through the no-Ghidra reviewer after pinned TASM, raw RET,
  generated-public, and next-PROC validation.
- `gengetsu_columns_phase()` at `0x2FEDF` owns code through `RET` at `0x30047`
  plus a four-word compiler jump table through `0x3004F`.
- `gengetsu_cycle_phase()` at `0x2FD30` owns 0xC4 code bytes through `RET` plus
  a five-word jump table, for a complete 0xCE-byte extent through `0x2FDFD`.
- public FAR `gengetsu_update()` at `0x3026A` continues through `RETF` at
  `0x306D7` and owns the following ten-word phase jump table through `0x306EB`.
  Fresh Ghidra stops early; raw/TASM/table-target review defines the exact end.

The maintained sources are under `src/main/boss/` and contain no target-byte
emission, copied machine-code arrays, `#pragma codestring`, or inline assembly.

## Latest replay receipts

The current end-of-segment owners each pass focused two-cold replay, culminating
in `.analysis/reconstruction/exact-unit-replay/gptweb-v98-probe-003/receipt.json`.
The complete default cohort then passes at:

- `.analysis/reconstruction/exact-unit-replay/gptweb-main036-complete-aggregate-004/receipt.json`
  — all 136 default owners, two isolated cold materializations.

The aggregate is the retained current private acceptance baseline. Superseded
replay materializations and raw probe matrices may be pruned after their
commands, outcomes, and digests enter the checked-in ledgers; historical
`.analysis` paths are provenance rather than a cache-retention guarantee.

The 2026-09-08 retention pass kept all 275 replay `receipt.json` files,
compacted 273 superseded receipt-bearing runs, removed 88 receiptless run
directories, and retained the then-current full trees. Obsolete probe,
warm-build, one-off function-review, and isolated DOS-workspace caches were
also removed. This reduced the private `.analysis` tree from about 27 GiB to
1.6 GiB without removing targets, installed toolchains, Ghidra state, runtime
state, current boundary inputs, or the cold reconstruction seed.

For every v89-v98 owner, the retained current replays report zero raw differences, exact map
placement, identical ordered overlapping MZ relocations, valid deterministic
TC86 OMF, and stable source snapshots. The aggregate candidate executable is
deterministic across A/B with SHA-256
`7e4759add3f7358898081805fc1eaba0eab2b5d3122607ecf0f8b24ccfeaaaa9`.

The current function review uses the same aggregate map, fresh attested Ghidra
metadata, pinned TASM boundaries, and raw 16-bit decoding. It reports 248/250
exact functions, 114 automatic acceptances, 134 manual reviewed acceptances,
and zero provisional strict rejections. The private report is
`.analysis/reconstruction/functions/function-review-v98-current.json`.

## Remaining reviewed nonexact work

Only two reviewed authored functions are nonexact:

1. `snd_load`: 4 bytes remain blocked by target-specific register/segment-save
   instruction encodings. Existing pure-C, TC4J flag, and TASM probes are
   recorded as negative results; do not repeat them without a new falsifiable
   source shape.
2. `enemy_bullet_template_push`: all 27 bytes remain blocked because natural
   TC4 struct-copy forms emit a different `REP MOVSW` setup order. ReC98's
   inline-assembly shortcut is not acceptable evidence.

`dialog_op` and `dialog_run` have maintained source and exact code bytes, but
remain outside the reviewed exact denominator because their ordered MZ
relocation sequences do not match. Restoring the lower historical TU split was
already tested and does not solve those two functions.

## Next target-first queue

Do not resume from the old prose-only MAIN frontier. Query
`config/th04_function_boundaries.csv` for `work_queue=reconstruct` and
`accepted_state=unreviewed`, then select one coherent artifact-local unit.
There are 482 such rows. Prefer `boundary_state=corroborated`; the 105
provisional rows need focused target control-flow, return/shared-tail,
jump-table, alignment, and adjacent ownership review before source work.

The largest remaining class is 289 MAIN entries currently represented by
target-derived assembly. That label means “likely authored game code awaiting
natural source,” not “original handwritten ASM.” OP has 94 unreviewed authored
candidates, MAINE 72, and ZUN 13. Cross-game source paths in MAP evidence are
corroboration only and must become TH04-local or proved `src/shared/` source.

Do not return to retired `exact/`, `partial/`, or `modules/` source layouts.
Product source follows `src/main/`, `src/op/`, `src/maine/`, `src/zun/`, and
proved `src/shared/` ownership with semantic subsystem directories.

## Build status

The accepted 136-owner cohort compiles and links reproducibly through the
pinned ReC98 cold-replay scaffold. This is a strict exactness Oracle, not a
standalone TH04 build.

The repository still lacks many TH04 translation units, a fully localized
ABI/header surface, and a complete TH04-owned link graph. Unlocalized
declarations are explicitly quarantined behind one-line
`compat/rec98/<upstream-path>` forwarders. Do not bulk-copy ReC98 or other game
trees to hide this gap. Recover declarations into the owning TH04 subsystem or
a proved `src/shared/` surface, attest affected owners, then remove the matching
forwarder.

## Reproduction commands

Run before target-dependent work:

```bash
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/boundary_review/validate_function_boundary_ledger.py
```

The complete private inventory refresh order and its DIET/Ghidra/MAP/TASM
limitations are in `docs/BOUNDARY_REVIEW.md`. Reusable scripts are grouped
under `scripts/boundary_review/`; generated payloads, listings, Ghidra exports,
and databases remain ignored.

Replay one owner or the complete accepted cohort:

```bash
python3 scripts/replay_th04_main_exact_units.py --unit UNIT_ID --run-id RUN_ID
python3 scripts/replay_th04_main_exact_units.py --run-id RUN_ID
```

Regenerate progress and finish a session with:

```bash
python3 scripts/progress.py
python3 scripts/ci.py
git diff --check
```

The compact acceptance contract and unresolved producer constraints remain in
`docs/reconstruction/TH04_MAIN_EXACT_BATCH.md`,
`docs/reconstruction/TH04_MAIN_FIXUP_CODEGEN_PROBES.md`, and
`config/knowledge.csv`. Whole-artifact boundary results are in
`docs/BOUNDARY_REVIEW.md` and `config/th04_function_boundaries.csv`.
