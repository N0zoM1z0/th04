# TH04 reconstruction handoff

## Current phase

The headless reconstruction environment is operational and the current work is
target-first `MAIN.EXE` recovery. The accepted exact cohort now contains 132
default owners. The live reviewed totals are:

- authored C/C++ bytes: **35,980 / 36,011 exact (99.913915%)**;
- authored functions: **241 / 243 exact (99.176955%)**;
- original-style ASM: **9 units / 1,489 exact bytes**, tracked separately;
- reviewed nonexact authored bytes: **31 bytes** in two functions.

These percentages use only reviewed ledger denominators. They are not a claim
that 99.91% of the executable or game has been reconstructed. Derive current
numbers with `python3 scripts/status.py`; `config/units.csv` and
`config/th04_main_authored_functions.csv` override prose.

`OP.EXE`, `MAINE.EXE`, and `ZUN.COM` still have no reviewed reconstruction
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

## Latest accepted batch

v88 recovers public FAR `reimu_update()` at `0x2F3AB..0x2F8ED` as one
0x543-byte exact owner: 0x515 bytes of code plus two compiler switch-table
regions. Fresh Ghidra cross-links its body beyond the true owner; pinned TASM,
raw decoding, switch-target validation, and exact map ownership define the
accepted extent.

v89-v94 recover the first Gengetsu family at `0x2F8EE..0x2FEDE`: 1,521 bytes,
seven exact C++ owners, and twelve exact functions. Important boundaries are:

- `0x2F8EE`, `0x2F903`, and `0x2F97A` are three functions in one physical
  TC86 producer. Splitting the producer loses the alignment byte before the
  middle function's sparse switch tables.
- Ghidra has no entry at `0x2F8EE` or `0x2F97A`, and sparsely constructs
  several later bodies. The function ledger uses raw/TASM/next-PROC evidence.
- `gengetsu_cycle_phase()` at `0x2FD30` owns 0xC4 code bytes through `RET` plus
  a five-word jump table, for a complete 0xCE-byte extent through `0x2FDFD`.

The maintained sources are under `src/main/boss/` and contain no target-byte
emission, copied machine-code arrays, `#pragma codestring`, or inline assembly.

## Latest replay receipts

Two independent current-tree runs pass:

- focused dependency closure:
  `.analysis/reconstruction/exact-unit-replay/codex-final-v94-focused-001/receipt.json`
  — 67 selected owners, two isolated cold materializations;
- complete default cohort:
  `.analysis/reconstruction/exact-unit-replay/codex-final-v94-aggregate-001/receipt.json`
  — all 132 default owners, two isolated cold materializations.

For every v89-v94 owner, both runs report zero raw differences, exact map
placement, identical ordered overlapping MZ relocations, valid deterministic
TC86 OMF, and stable source snapshots. The aggregate candidate executable is
deterministic across A/B with SHA-256
`99e7f9c100a8ff42bef1c97412d30c135f7aaff45fdc8ab3b63bfaea1a017b40`.

The current function review uses the same aggregate map, fresh attested Ghidra
metadata, pinned TASM boundaries, and raw 16-bit decoding. It reports 241/243
exact functions, 114 automatic acceptances, 127 manual reviewed acceptances,
and zero provisional strict rejections. The private report is
`.analysis/reconstruction/functions/function-review-v94-current.json`.

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

Continue `MAIN_036_TEXT` at local Gengetsu procedure `0x2FEDF`. Pinned TASM
shows subsequent procedure starts at `0x30050`, `0x300B6`, `0x30195`,
`0x30202`, and `0x3023B`, followed by public FAR `gengetsu_update()` at
`0x3026A`. Keep Ghidra boundaries provisional and account for trailing compiler
tables before setting any extent.

Do not return to retired `exact/`, `partial/`, or `modules/` source layouts.
Product source follows `src/main/`, `src/op/`, `src/maine/`, `src/zun/`, and
proved `src/shared/` ownership with semantic subsystem directories.

## Build status

The accepted 132-owner cohort compiles and links reproducibly through the
pinned ReC98 cold-replay scaffold. This is a strict exactness Oracle, not a
standalone TH04 build.

The repository still lacks every TH04 translation unit, a fully localized
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
```

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

Detailed historical acceptance and compiler-probe notes remain in
`docs/reconstruction/TH04_MAIN_EXACT_BATCH.md`,
`docs/reconstruction/TH04_MAIN_FIXUP_CODEGEN_PROBES.md`, and
`config/knowledge.csv`.
