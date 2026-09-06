# TH04 `MAIN.EXE` authored exact batch

## Scope

This note records the first large exact reconstruction batch after the initial
58-module routing screen. ReC98 revision
`b6ba5b0a529edbb31efdf8c0e939263804f8ee47` is used only as pinned clean-build
scaffolding and candidate provenance. Every accepted byte comes from maintained
repository source and is re-attested against the pinned Japanese TH04 target.

The current reviewed results are:

- authored C/C++ bytes: **12,448 / 12,494 = 99.631823% exact**;
- authored functions: **99 / 101 = 98.019802% exact**;
- exact standalone original-style ASM: 9 units / 1,489 bytes, tracked
  separately and excluded from the authored C/C++ percentage.

## Cold replay design

`config/th04_main_exact_units.toml` and
`scripts/replay_th04_main_exact_units.py` define the replay. Each acceptance
run:

1. attests the pinned TC4J/TASM/TLINK/MS-DOS Player toolchain;
2. materializes two independent source trees with `git archive` from the pinned
   ReC98 revision;
3. replaces complete translation units with maintained files from `src/`, or
   uniquely substitutes a maintained natural-source fragment into the pinned
   scaffold when the surrounding upstream function contains excluded inline
   assembly;
4. preserves primary-source metadata because Turbo C++ records it in OMF
   COMENT class `E8`;
5. builds the complete corpus serially;
6. requires the accepted target slice to have zero raw differences in both
   cold builds;
7. checks that the TLINK contribution contains or exactly equals the accepted
   extent, as configured;
8. compares the ordered overlapping MZ relocation sites;
9. validates the generated Intel OMF module and requires its narrowly
   normalized identity to repeat across both cold builds; and
10. fails the aggregate cohort if any selected unit fails any dimension.

The development acceptance receipt is private at
`.analysis/reconstruction/exact-unit-replay/gptweb-accept60-002/receipt.json`.
It contains 60 default-selected units and passes in both cold materializations.
Three known `dialog` relocation-order investigations are marked
`default_enabled = false`; they remain individually replayable with `--unit`
and are never silently accepted by the default aggregate.

### Fragment rule

Fragment replay is intentionally identity-preserving. A checked-in fragment
must occur **exactly once** in the pinned scaffold source. The driver rewrites
that occurrence with the same repository-maintained bytes, restores the
original source timestamp, and then compiles normally. This lets a natural
C/C++ region be independently owned without copying adjacent ReC98 inline
assembly into `src/`.

No accepted C/C++ source under `src/th04/main/exact/`,
`src/th04/main/modules/`, or `src/th04/main/partials/` contains `_asm`, an
`asm { ... }` block, `#pragma codestring`, or `__emit__`.

## Explicit nonexact byte gaps

### `snd_pmd_resident`

The complete reviewed function is target file `0x14B7E..0x14BAB` (46 bytes).
The natural prefix (18 bytes) and suffix (23 bytes) are exact. The five bytes at
file `0x14B90` remain nonexact:

```text
26 C4 1E 80 01    LES BX, ES:[0180h]
```

Pure C89 probes established useful negative results. A direct IVT dereference
can make TC4J emit `LES`, but repeated macro use reloads the pointer. Typed and
`register` far pointers spill, and assigning `_BX`/`_ES` separately emits two
loads rather than the target single instruction. No TC4J header intrinsic for
`LES` was found. The project therefore leaves these five bytes nonexact rather
than importing ReC98's inline assembly.

### `snd_load`

The complete reviewed function is target file `0x14C96..0x14D7F` (234 bytes).
The natural 184-byte prefix and 9-byte tail are exact. The 41-byte middle region
at file `0x14D4E` remains nonexact. One localized compiler/source-shape
mismatch is:

```text
target:    89 C3    MOV BX, AX
candidate: 8B D8    MOV BX, AX
```

A standalone TASM 5.0 probe also naturally emits `8B D8` for `mov bx, ax`.
Follow-up compiler/assembler probes narrow this further without weakening the
claim:

- the target `MAIN.EXE` has only three `89 C3` encodings, at load offsets
  `0xD058`, `0xEAA9`, and `0x13557`; they fall in `dialog`, `stages`, and
  `snd_load`, respectively, while the cold ReC98 candidate has no `89 C3`;
- the other differences in `dialog` and `stages`, plus the one-byte
  `it_spl_u` difference, are the same register-register direction-bit family
  (`01 /r` versus `03 /r`, `89 /r` versus `8B /r`, and `31 /r` versus
  `33 /r`) rather than different arithmetic semantics;
- TH02's 112-byte `snd_load` is raw-identical between the pinned target and the
  same cold TC4J candidate and uses `8B D8`, so `89 C3` is not a general
  requirement of the shared `_BX = _AX` source shape;
- compiling the real TH04 `snd_load.cpp` with `-G`, `-O-`, `-k-`, 80186/286
  CPU modes, and tested combinations still produced `8B D8`;
- TASM 5.0 in MASM, IDEAL, 386, `MASM51`, `QUIRKS`, `SMART`/`NOSMART`, and
  operand-qualified forms also produced `8B D8`; and
- scanning the complete cold OMF corpus found one TC86 object containing
  `89 C3` (`th02/player_b.obj`), but that occurrence routes to an upstream
  inline-assembly `mov bx, ax`, which is specifically excluded from this
  reconstruction strategy.

These observations do not prove what the original ZUN source looked like.
They do rule out several cheap compiler-profile explanations and make future
work focus on source/IR recovery rather than repeating the same flag or TASM
mode experiments. The project does not use `db 89h, 0C3h`, `__emit__`, inline
assembly, or any equivalent byte injection to manufacture equality.

## Relocation-order blockers

`dialog_op`, `dialog_run`, and `dialog_init` were replayed in two isolated
builds. Each has exact raw bytes, exact containing TLINK placement, valid and
deterministic OMF, and the same set of overlapping relocation sites as the
target. The **ordered** relocation site list is a cyclically different order.
Because ordered MZ relocations are a required Oracle, all three byte regions are
`blocked` with provisional ownership and are excluded from the reviewed byte
denominator.

This distinction is important: raw equality and relocation-set equality are
not enough for this repository's exact policy.

## Function accounting

`config/th04_main_authored_functions.csv` is a separate function ledger. It
prevents module byte exactness from automatically becoming a function-boundary
claim.

`scripts/review_th04_main_functions.py` conservatively intersects:

- a function entry from the hash-attested target Ghidra database;
- a public symbol at the same start in the locally rebuilt TLINK map; and
- one exact authored byte owner from `config/units.csv`.

Promotion additionally requires Ghidra's complete body to be contiguous and
wholly contained inside that exact byte owner. This strict rule accepts 99
functions and rejects 13 candidate starts in the current screen; two of those
13 are the already reviewed nonexact `snd_pmd_resident` and `snd_load`.
`bullets_update` is kept provisional before the strict screen because it crosses
the excluded 17-byte handwritten-call gap. Eleven other non-contiguous target
bodies remain provisional rather than being inferred from next-function
addresses.

The resulting denominator is therefore 101 reviewed functions: 99 exact plus
the two explicit nonexact sound functions. Twelve additional candidates remain
visible in the ledger but do not enter the reviewed denominator.

## Reusable Borland lessons

- Turbo C++ records the primary source timestamp in OMF COMENT class `E8`.
  Copying maintained source with `copyfile()` manufactured per-cold-run object
  differences. Preserve identical source metadata (`copy2`) instead of
  weakening OMF normalization.
- `#pragma option -zC...` is a translation-unit-start option, while
  `#pragma codeseg` can switch later code. More importantly, a function's first
  declaration influences Borland segment/group fixups.
- Combining `midboss_reset` and `midboss_defeat_update` into one C++ source
  without inline assembly can reproduce most bytes, but a direct cross-code
  segment call still naturally becomes a 5-byte `CALLF` rather than the
  target's `PUSH CS` plus near `CALL`. Do not replace that negative result with
  byte-oriented assembly.
- Exact module bytes do not prove Ghidra's internal function bodies. Keep
  switch tables, shared tails, and non-contiguous bodies provisional until
  independently reviewed.
