# TH04 `MAIN.EXE` authored exact batch

## Scope

This note records the first large exact reconstruction batch after the initial
58-module routing screen. ReC98 revision
`b6ba5b0a529edbb31efdf8c0e939263804f8ee47` is used only as pinned clean-build
scaffolding and candidate provenance. Every accepted byte comes from maintained
repository source and is re-attested against the pinned Japanese TH04 target.

The current reviewed results are:

- authored C/C++ bytes: **12,650 / 12,691 = 99.676936% exact**;
- authored functions: **112 / 113 = 99.115044% exact**;
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

Historical checked-in acceptance evidence remains replayable. The current
full-owner pre-commit replay is private at
`.analysis/reconstruction/exact-unit-replay/gptweb-dialog-split-aggregate-001/receipt.json`.
It passes all 60 current default-selected units in both isolated cold
materializations, including the full pure-C PMD owner and the restored natural
C++ dialog init/exit TU split. `dialog_op` and `dialog_run` remain
`default_enabled = false`; they stay individually replayable with `--unit` and
are never silently accepted by the default aggregate.

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

### Translation-unit split rule

`[[splits]]` entries in the exact-unit manifest can restore an original C/C++
TU boundary without importing old objects. A split is activated only by named
units and must remove one checked-in fragment that occurs exactly once in the
pinned scaffold; `suffix` mode additionally requires that fragment to reach
EOF. The same maintained bytes and a checked-in current-header wrapper are then
materialized as a second TU, and one unique build-graph anchor is patched so
normal `build.bat`/Tup/TC4J/TLINK compile and link it in the declared order.
The receipt records all scaffold, fragment, wrapper, and build-graph hashes.

The TH04 dialog split is the first use: `dialog_init` + `dialog_exit` are the
unique 2,063-byte suffix of the pinned merged implementation. Moving that
suffix to `th04/dialog_i.cpp` preserves every linked code byte but changes OMF
FIXUPP batching back to the target order.

## Explicit nonexact byte gaps

### `snd_pmd_resident` — solved in pure C

The complete reviewed function is target file `0x14B7E..0x14BAB` (46 bytes).
Earlier generic far-pointer probes failed to reproduce the five-byte IVT load
without repeated loads or spills. The missing source shape is Borland's
segment-specific pointer type:

```c
_ES = _AX; // _AX is 0 here
if(kaja_isr_magic_matches(
    *(void far * __es *)(PMD * 4), 'P', 'M', 'D'
)) {
    _AX++;
}
```

TC4J naturally compiles the IVT dereference to the exact target instruction:

```text
26 C4 1E 80 01    LES BX, ES:[0180h]
```

No inline assembly, `__emit__`, codestring, or target-derived byte directive is
used. `gptweb-pmd-full-001` verifies the unit independently, and
`gptweb-pmd-aggregate-001` verifies it together with the complete default exact
cohort. Both isolated builds produce the same valid TC86 OMF, exact TLINK
contribution, identical empty overlapping-relocation list, and zero differing
bytes across all 46 bytes.

The older generic-pointer negative probes remain useful: `MK_FP`, typed or
`register` far locals, and separate `_BX`/`_ES` assignments are still known
wrong source shapes. They must not be generalized into a claim that TC4J cannot
express this `LES`; the `__es` pointer is the exact counterexample.

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
  reconstruction strategy;
- declaring the DOS handle as a pure-C `register int` does not recover the
  target encoding. TC4J allocates it to DX in small probes, DI once the real
  `_DX`/`_CX`/SI pressure is represented, and spills it when DI is also
  unavailable. The resulting moves are `8B /r`, never target `89 C3`; and
- pure-C DS preservation also fails to reproduce the middle block's
  `PUSH DS ... POP DS`. A normal saved local emits `MOV [bp-2],DS` / `MOV
  DS,[bp-2]`, a register local uses AX, and an ES temporary uses two `MOV`
  pairs. `__saveregs` saves all registers rather than just DS, while
  `__loadds` does not create the required mid-function pair.

Additional FIXUPP/code-generation work is recorded in
`docs/reconstruction/TH04_MAIN_FIXUP_CODEGEN_PROBES.md`. In particular, the
pinned TASM media contains a DOS TASM 4.1 that TCC can invoke through `-B`; it
still assembles ordinary `mov bx, ax` as `8B D8`. A corrected segment-aware OMF
survey also finds no clean TC86 C/C++ CODE precedent for register-register
`89 /r` in the current cold corpus. Pure-C++ reference/template/comma/conditional
lvalue probes further show that `_BX` is not addressable and cannot be routed
through a generic store-lvalue backend. Raw OMF byte searches are not accepted
as instruction evidence.

These observations do not prove what the original ZUN source looked like.
They do rule out several cheap compiler-profile explanations and make future
work focus on source/IR recovery rather than repeating the same flag or TASM
mode experiments. The project does not use `db 89h, 0C3h`, `__emit__`, inline
assembly, or any equivalent byte injection to manufacture equality.

## Relocation-order blockers

`dialog_op`, `dialog_run`, and `dialog_init` initially reproduced raw bytes,
map placement, deterministic OMF, and relocation *sets* while failing the
required ordered-relocation Oracle. Decoding `dialog.obj` showed why ordering is
sensitive: MZ segment relocations are emitted in Intel OMF FIXUPP subrecord
order, and linked code equality does not force identical LEDATA/FIXUPP record
partitioning.

`dialog_init` is now solved. ReC98 history identified a later maintenance merge
of two lower dialog translation units. At the parent revision, `dialog_f.cpp`
contains shared/op/run/animate while a separate `dialog.cpp` contains
init/exit. Recompiling that historical natural C++ split with the same pinned
TC4J showed that the 355-byte init/exit code payload is byte-identical to the
current merged suffix, but its single-object FIXUPP sequence yields exactly the
six target `dialog_init` relocations. A diagnostic relink confirmed:

- `dialog_init`: raw exact and ordered relocations exact after the split;
- `dialog_exit`: remains raw/relocation exact;
- `dialog_op` and `dialog_run`: remain raw exact but relocation-order mismatched.

The checked-in solution does **not** use the historical object. A minimal
current-header pure-C++ second TU compiles to the same 355-byte code payload and
FIXUPP shape. The cold replay driver restores this split through the build graph
and `gptweb-dialog-split-aggregate-001` passes all 60 default units twice.

This also falsifies the obvious next guess for the remaining blockers: the
historical pre-merge `dialog_f.obj` already has the same `dialog_op` and
`dialog_run` pointer-fixup order as the current candidate. Their relocation
order needs a different source/OMF-emission explanation. Follow-up natural TU
boundary, source-shape, TC86-option, and TCC-via-TASM probes are tabulated in
`TH04_MAIN_FIXUP_CODEGEN_PROBES.md`; none repairs `dialog_op` or `dialog_run`
without changing another required dimension.

## Function accounting

`config/th04_main_authored_functions.csv` is a separate function ledger. It
prevents module byte exactness from automatically becoming a function-boundary
claim.

`scripts/review_th04_main_functions.py` conservatively intersects:

- a function entry from the hash-attested target Ghidra database;
- a public symbol at the same start in the locally rebuilt TLINK map; and
- one exact authored byte owner from `config/units.csv`.

Automatic promotion still requires Ghidra's complete body to be contiguous
and wholly contained inside that exact byte owner; this now accepts 101
functions, including the exact `snd_pmd_resident` and newly owned 197-byte
`dialog_init`.
A second, explicit manual-review path handles analysis false negatives without
trusting Ghidra's body set. Each `[[reviewed_exact]]` entry in
`config/th04_main_function_review.toml` must agree with the same TLINK public and
exact owner, Ghidra's body min/max span, and a raw `ndisasm -b16` pass that tiles
every byte through the terminal RET/RETF. For indirect switches the checked-in
reviewer additionally parses the target jump table and requires every target to
be a decoded instruction start inside the function span. Two regression tests
force this switch gate to fail closed on a target that lands between
instructions.

This manual gate promotes 11 Ghidra body-construction false negatives: four
straight-line/overlap cases (`player_pos_update_and_clamp`, both large title/BGM
overlay functions, and `overlay_popup_update_and_render`), `boss_items_drop`,
`bullet_velocity_and_angle_set`, and five compiler-switch functions whose jump
tables sit immediately after their bodies. `bullets_update` remains provisional
because it crosses the excluded 17-byte handwritten-call gap; an exact owner on
both sides cannot prove the missing middle.

The resulting denominator is therefore 113 reviewed functions: 112 exact plus
the single explicit nonexact `snd_load`. `dialog_init` is a newly tracked
function admitted only by explicit `[[new_exact]]` policy after its exact byte
owner appeared. One additional candidate, `bullets_update`, remains
provisional and outside the denominator.

## Reusable Borland lessons

- Translation-unit boundaries are binary inputs even when linked code bytes are
  unchanged. They can alter Borland LEDATA/FIXUPP batching and therefore the
  ordered DOS MZ relocation table. Restore natural C/C++ TU ownership before
  trying source-semantic changes when raw bytes and relocation sets already
  match but relocation order does not.
- Borland segment-specific pointers are code-generation relevant. When `_ES`
  already contains the IVT segment, dereferencing `void far * __es *` can emit a
  single `LES` with an ES override; generic far pointers or `MK_FP` are not
  interchangeable source shapes for exact reconstruction.
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
- Exact module bytes do not prove Ghidra's internal function bodies. Ghidra can
  create overlapping decodes or stop at an indirect switch even when the raw
  target has a complete function. Override such cases only with the checked-in
  manual gate: exact owner + TLINK public + matching min/max + gap-free raw
  decode; switch tables additionally require every target to be an instruction
  start inside the span. Shared tails and nonexact gaps remain provisional.
