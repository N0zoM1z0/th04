# TH04 `MAIN.EXE` authored exact batch

## Scope

This note records the first large exact reconstruction batch after the initial
58-module routing screen. ReC98 revision
`b6ba5b0a529edbb31efdf8c0e939263804f8ee47` is used only as pinned clean-build
scaffolding and candidate provenance. Every accepted byte comes from maintained
repository source and is re-attested against the pinned Japanese TH04 target.

The current reviewed results are:

- authored C/C++ bytes: **12,699 / 12,708 = 99.929178% exact**;
- authored functions: **112 / 114 = 98.245614% exact**;
- exact standalone original-style ASM: 9 units / 1,489 bytes, tracked
  separately and excluded from the authored C/C++ percentage.

## Cold replay design

`config/th04_main_exact_units.toml` and
`scripts/replay_th04_main_exact_units.py` define the replay. Each acceptance
run:

1. attests the pinned TC4J/TASM/TLINK/MS-DOS Player toolchain;
2. materializes two independent source trees with `git archive` from the pinned
   ReC98 revision;
3. replaces complete translation units with maintained files from `src/`,
   uniquely substitutes an identity-preserving natural-source fragment, or
   applies a hash/offset-bound maintained source replacement inside the pinned
   scaffold when adjacent upstream low-level source is deliberately excluded;
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
`.analysis/reconstruction/exact-unit-replay/gptweb-bullet-v10-precommit-001/receipt.json`.
It passes all 64 current default-selected units in both isolated cold
materializations, including the full pure-C PMD owner and the restored natural
C++ dialog init/exit TU split after the stricter reviewed-nonexact function
accounting changes. `dialog_op` and `dialog_run` remain
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

### Pinned source replacement rule

`source_mode = "replace"` is for the narrow case where the maintained natural
source differs from a small low-level span inside a pinned scaffold file. It is
not a textual search-and-replace shortcut. Before touching the source, the
replay driver requires all of the following to match the manifest exactly:

- SHA-256 of the complete pinned scaffold file;
- byte offset and size of the old source span; and
- SHA-256 of that exact old source span.

Only then is the repository-maintained replacement inserted, while preserving
the scaffold source timestamp. The receipt records old/new identities and the
patched scaffold hash. Any upstream drift fails closed. Regression tests cover
both the positive replacement and scaffold-drift rejection. This mechanism is
used for the three-byte `snd_load` parameter reload so the repository can own
pure C++ without copying adjacent ReC98 inline assembly into maintained source.

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

The complete reviewed function is target file `0x14C96..0x14D7F` (234 bytes),
and **230 / 234 bytes are now exact**. The original 184-byte prefix and 9-byte
tail remain exact, and this batch recovers another 37 middle bytes from
maintained natural C++:

- `0x14D4F..0x14D56` (8 bytes): DOS open setup + `INT 21h`;
- `0x14D59..0x14D5B` (3 bytes): `MOV AX,[BP+6]`; and
- `0x14D5C..0x14D75` (26 bytes): driver dispatch and DOS read.

The DOS-open and dispatch/read regions are identity fragments that occur exactly
once in the pinned scaffold and pass independent two-cold replay. The parameter
reload required a genuinely different natural source shape. Direct `_AX = func`,
a cast, and an inline identity helper make TC4J promote `func` to DI, grow the
function from 234 to 237 bytes, and emit `MOV AX,DI`. This maintained expression
instead keeps the parameter memory-resident:

```cpp
_AX = *reinterpret_cast<snd_load_func_t near *>(&func);
```

TC4J then preserves the 234-byte layout and naturally emits target `8B 46 06`.
The checked-in replacement is applied only through the fail-closed pinned-source
replacement rule above; the surrounding upstream low-level source is not
imported or claimed as maintained source.

Only four authored bytes remain nonexact:

```text
file 0x14D4E: 1E       PUSH DS
file 0x14D57: 89 C3    MOV BX, AX
file 0x14D76: 1F       POP DS
```

The `89 C3` blocker remains strongly constrained. Ordinary TC4J `_BX = _AX`
and both pinned TASM 4.1/5.0 encode `MOV BX,AX` as `8B D8`; tested register
allocation, pseudo-register alias/reference, flag, and assembler-mode variants
do not produce `89 C3`. A segment-aware clean-C/C++ CODE survey found no
register-register `89 /r` compiler precedent in the current corpus.

The DS pair is independently constrained as well. `geninterrupt(i)` in the
attested TC4J `DOS.H` is only `__int__(i)` and carries no segment-register
clobber contract, so the compiler cannot infer that PMD/MMD returns the song
buffer through `DS:DX`. Ordinary locals, register locals, ES temporaries, and
new `void __seg *` / `unsigned __seg *` save probes lower to MOV-based saves and
restores. A CODE-segment-aware scan of 239 clean C/C++ objects found no isolated
mid-function compiler `PUSH DS ... POP DS`: genuine pairs are full
`__saveregs`/interrupt-style prologues, while apparent TH01 hits were far-pointer
argument pushes followed by switch-table data misdecoded as instructions.

These negative results do not prove the original source language or producer.
They do justify keeping the remaining four bytes blocked instead of manufacturing
them with inline assembly, `__emit__`, byte directives, hand-edited compiler
assembly, or patched OMF.

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

### `bullets_update` call-form blocker

The complete reviewed function is target file `0x1E0C8..0x1E432` (0x36B bytes).
Exact natural-source slices cover the code on both sides of a 17-byte low-level
call region. Replacing only that region with the natural C++ call
`sparks_add_random(...)` reproduces every argument push and surrounding byte but
TC4J emits a five-byte `CALL FAR`; target instead has `NOP; PUSH CS; CALL near`.

Focused compiler controls explain the boundary. TC4J naturally emits the
`PUSH CS; CALL near` far-call bridge only when the far callee definition is
already visible earlier in the same translation unit and the same logical code
segment. An extern declaration, a definition in another code segment of the
same group, first-declaration segment ownership, near/far function-pointer
casts, constant function pointers, and `#pragma samecodeseg` do not recover the
target form. `samecodeseg` is still meaningful: TDUMP shows that it changes the
Pointer16 FIXUPP frame from TARGET to the current group while leaving `CALL FAR`
LEDATA unchanged. No assembly stitching is used to close the gap.

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
tables sit immediately after their bodies.

Reviewed nonexact functions use a separate fail-closed path: they need the same
entry/public observations plus a complete raw code decode, and may explicitly
own trailing switch metadata/tables without claiming the bytes exact.
`bullets_update` is now reviewed this way. Its 0x360-byte code span decodes
through `RETF` at `0x2CC27`; byte `0x2CC28` is switch metadata; five words at
`0x2CC29` target `0x2CB71`, `0x2CB78` (three entries), and `0x2CB7F`, all raw
instruction starts; and the next TLINK public is exactly `0x2CC33`. The full
function extent is therefore 0x36B bytes even though its final five-byte
spark-call form remains nonexact; the preceding 12 argument bytes are exact.

The resulting denominator is 114 reviewed functions: 112 exact plus the two
explicit nonexact functions `snd_load` and `bullets_update`. `dialog_init` is a
newly tracked function admitted only by explicit `[[new_exact]]` policy after
its exact byte owner appeared. No current function candidate remains
provisional.

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
