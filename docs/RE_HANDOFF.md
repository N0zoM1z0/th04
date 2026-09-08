# TH04 reconstruction handoff

## Current phase

The headless reconstruction environment is operational. A whole-artifact
boundary/origin review has now been completed without starting another source
reconstruction batch. `config/th04_function_boundaries.csv` is the current
routing inventory and `docs/BOUNDARY_REVIEW.md` is its generated explanation.

The inventory contains 2,120 distinct function-like observations:

- 732 authored reconstruction candidates: OP 94, MAIN 553, MAINE 72, ZUN 13;
- 255 accepted exact MAIN functions and two reviewed blocked MAIN functions;
- 475 authored candidates otherwise unreviewed;
- 52 original-style ASM observations in a separate attestation queue;
- 1,336 compiler/runtime/library/data/switch observations explicitly excluded.

Within the accepted 140-owner MAIN cohort, the live reviewed totals are:

- authored C/C++ bytes: **38,809 / 38,840 exact (99.920185%)**;
- authored functions: **255 / 257 exact (99.221790%)**;
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

v99 expands the reviewed authored universe in `END_TEXT`: `end_game_good()`, `end_game_bad()`, and `end_extra()` at `0x1B7B9..0x1B834` are three contiguous FAR bodies (0x2B, 0x2B, 0x26) agreed by target Ghidra, pinned TASM, TLINK publics, and raw decode. One pure-C++ producer reproduces all 0x7C bytes; `#pragma samecodeseg GameExecl` selects the target TLINK `NOP; PUSH CS; CALL near` optimization and exact relocation order without byte emission.

v100 closes the `END_TEXT` suffix with target-first natural C++: `map_load()` at `0x1B971..0x1B9BA` (0x4A) and `map_free()` at `0x1B9BB..0x1B9D5` (0x1B) are full contiguous Ghidra/TASM/TLINK/raw bodies. No ReC98 C++ body exists. The exact link layout is `endmain.cpp` 0x7C + unchanged `th04_main.asm` middle 0x13C + `mapend.cpp` 0x65, preserving the complete segment length and ordered relocations without padding or ASM splitting.

v101 corrects a material authored-boundary error in `BOSS_FG_TEXT`: fresh Ghidra creates `gengetsu_fg_render()` at `0x22F5F` but includes only the first 5 bytes (`ENTER 2; PUSH SI`). Pinned TASM keeps the PROC open through segment end, and raw target decoding closes at `LEAVE; RET` on `0x230EB..0x230EC`, proving the full **0x18E / 398-byte** function. Target-first natural C++ reproduces all 398 bytes, exact map placement, and the complete ordered relocation overlap in focused and 139-owner aggregate cold replay.

v102 recovers the `BOSS_BG_TEXT` suffix `mugetsu_gengetsu_bg_render()` at `0x22979..0x22A09` as a full **0x91 / 145-byte** natural-C++ owner. Fresh Ghidra, pinned TASM, MAP ownership, and raw decoding agree on the boundary; focused and 140-owner aggregate cold replay are raw/map/ordered-relocation exact. Target packed Pascal arguments also disprove the initial `(16,32)` backdrop-coordinate hypothesis: both target calls require source arguments `(32,16)`.

The maintained v89-v98 sources are under `src/main/boss/`; v99 adds `src/main/end/ending.cpp`, and v100 adds `src/main/formats/map.cpp`, and v101 adds `src/main/boss/gengetsu6_fg_render.cpp`, and v102 adds `src/main/boss/mugetsu_gengetsu_bg_render.cpp`. These accepted sources contain no target-byte emission, copied machine-code arrays, `#pragma codestring`, or inline assembly.

## Latest replay receipts

The latest BOSS_BG_TEXT owner passes focused two-cold replay at
`.analysis/reconstruction/exact-unit-replay/gptweb-v102-probe-003/receipt.json`.
The complete default cohort then passes at:

- `.analysis/reconstruction/exact-unit-replay/gptweb-v102-aggregate-001/receipt.json`
  — all 140 default owners, two isolated cold materializations.

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

For every v89-v102 owner, the retained current replays report zero raw differences, exact map
placement, identical ordered overlapping MZ relocations, valid deterministic
TC86 OMF, and stable source snapshots. The aggregate candidate executable is
deterministic across A/B with SHA-256
`defc6f9b75ba4d1655cf0760405b7c1e29b51d4f96c708029a40a154668ae4a2`.

The current function review uses the same aggregate map, fresh attested Ghidra
metadata, pinned TASM boundaries, and raw 16-bit decoding. It reports 255/257
exact functions, 120 automatic acceptances, 135 manual reviewed acceptances,
and zero provisional strict rejections. The private report is
`.analysis/reconstruction/functions/function-review-v102-current.json`.

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
There are 475 such rows. Prefer `boundary_state=corroborated`; the 105
provisional rows need focused target control-flow, return/shared-tail,
jump-table, alignment, and adjacent ownership review before source work.

The largest remaining class is 282 MAIN entries currently represented by
target-derived assembly. That label means “likely authored game code awaiting
natural source,” not “original handwritten ASM.” OP has 94 unreviewed authored
candidates, MAINE 72, and ZUN 13. Cross-game source paths in MAP evidence are
corroboration only and must become TH04-local or proved `src/shared/` source.

Re-screening confirmed that several tempting ReC98 candidate-C++ paths are not acceptable drop-ins: checkerboard, TH03 vector, `item_splashes_init`, and `carpet_lighting_put_new` depend on inline ASM and/or `#pragma codestring` for instruction shape. Keep them as routing evidence until an allowed source form is proved. Ghidra also still misses CIRCLE_TEXT boundaries including `randring1_next16`, `randring1_next16_mod`, and the near/far null functions; MAP/TASM keeps those candidates visible.

Do not return to retired `exact/`, `partial/`, or `modules/` source layouts.
Product source follows `src/main/`, `src/op/`, `src/maine/`, `src/zun/`, and
proved `src/shared/` ownership with semantic subsystem directories.

## Build status

The accepted 140-owner cohort compiles and links reproducibly through the
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
