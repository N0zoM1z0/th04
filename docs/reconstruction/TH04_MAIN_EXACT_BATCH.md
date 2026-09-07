# TH04 `MAIN.EXE` authored exact batch

## Scope

This note records the first large exact reconstruction batch after the initial
58-module routing screen. ReC98 revision
`b6ba5b0a529edbb31efdf8c0e939263804f8ee47` is used only as pinned clean-build
scaffolding and candidate provenance. Every accepted byte comes from maintained
repository source and is re-attested against the pinned Japanese TH04 target.

The current reviewed results are:

- authored C/C++ bytes: **12,932 / 12,983 = 99.607179% exact**;
- authored functions: **115 / 116 = 99.137931% exact**;
- exact standalone original-style ASM: 9 units / 1,489 bytes, tracked
  separately and excluded from the authored C/C++ percentage.

## Cold replay design

`config/th04_main_exact_units.toml` and
`scripts/replay_th04_main_exact_units.py` define the replay. Each acceptance
run:

1. attests the pinned TC4J/TASM/TLINK/MS-DOS Player toolchain;
2. materializes two independent source trees with `git archive` from the pinned
   ReC98 revision;
3. copies `compat/rec98/` into each tree and records every forwarding file's
   path, size, and SHA-256;
4. replaces complete translation units with maintained files from `src/`,
   uniquely substitutes an identity-preserving natural-source fragment, or
   applies a hash/offset-bound maintained source replacement inside the pinned
   scaffold when adjacent upstream low-level source is deliberately excluded;
5. preserves primary-source metadata because Turbo C++ records it in OMF
   COMENT class `E8`;
6. builds the complete corpus serially;
7. requires the accepted target slice to have zero raw differences in both
   cold builds;
8. checks that the TLINK contribution contains or exactly equals the accepted
   extent, as configured;
9. compares the ordered overlapping MZ relocation sites;
10. validates the generated Intel OMF module and requires its narrowly
   normalized identity to repeat across both cold builds; and
11. fails the aggregate cohort if any selected unit fails any dimension.

Historical checked-in acceptance evidence remains replayable. The current
full-owner pre-commit replay is private at
`.analysis/reconstruction/exact-unit-replay/gptweb-authored-expand-default-004/receipt.json`.
It passes all 64 current default-selected exact-replay units in both isolated
cold materializations, including the 0xD9-byte MB_DFT score-bonus prefix, the 11-byte pure-C
`snd_se_reset` owner,
the full pure-C PMD owner, and the restored natural C++ dialog init/exit TU split. `dialog_op` and `dialog_run` remain
`default_enabled = false`; they stay individually replayable with `--unit` and
are never silently accepted by the default aggregate.

### Fragment rule

Fragment replay is intentionally identity-preserving. A checked-in fragment
must occur **exactly once** in the pinned scaffold source. The driver rewrites
that occurrence with the same repository-maintained bytes, restores the
original source timestamp, and then compiles normally. This lets a natural
C/C++ region be independently owned without copying adjacent ReC98 inline
assembly into `src/`.

`source_mode = "forwarded-fragment"` is the same identity gate for fragments
whose include spelling now passes through `compat/rec98/`. Before comparison,
the driver resolves only include lines backed by an existing one-line
forwarder, verifies that the forwarder contains exactly the corresponding
upstream include, and requires the resolved fragment to occur exactly once in
the pinned scaffold. No declaration or executable source token is normalized.
The receipt retains the maintained and resolved sizes/digests plus the exact
forwarder list.

No accepted C/C++ source under `src/main/` contains `_asm`, an `asm { ... }`
block, `#pragma codestring`, or `__emit__`. The semantic source layout is
independent of this acceptance classification; exact state remains in the
ledgers.

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
both the positive replacement and scaffold-drift rejection. This mechanism is used for both the three-byte `snd_load` parameter reload and
the complete maintained `bullets_update` function. In the latter case, the
entire pinned low-level function source span is hash/offset-bound before being
replaced by natural C++ with one `#pragma samecodeseg`; adjacent upstream source
is not claimed as maintained source.

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

The remaining historical source pragma is not an escape hatch. TC4J documents
`-Z` as “Suppress register reloads”, while `snd_load.cpp` has carried `-Z-`
since its first C++ decompilation. Minimal `_BX=_AX` and block-scope DS-save
controls have identical instruction LEDATA under `-Z` and `-Z-`: `MOV BX,AX`
stays `8B D8`, and DS saves stay MOV-based. Flipping only the real function to
`-Z` also keeps `8B D8` and makes things worse by replacing two target-exact
`LES BX,[BX+8F8h]` reloads at function offsets `+0x96` and `+0xAC` with plain
`MOV BX,[BX+8F8h]`. Target differences grow from 2 to 4; do not repeat this
profile.

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

### `bullets_update` — solved in natural C++ + normal TLINK

The complete reviewed extent is target file `0x1E0C8..0x1E432` (0x36B = 875
bytes): 0x360 bytes of code through `RETF`, followed by one metadata byte and a
five-entry compiler near-jump table. It is now one exact authored byte owner.

The maintained source uses the ordinary call plus one Borland pragma:

```cpp
#pragma samecodeseg sparks_add_random
sparks_add_random(
    bullet->pos.cur.x, bullet->pos.cur.y, to_sp(2.0f), 2
);
```

The important distinction is **object code versus final linked code**. TC86
still emits a five-byte `CALL FAR` in `bullet_u.obj`; `samecodeseg` changes the
Pointer16 FIXUPP frame to `MAIN_03`. TLINK 6.10 documents `/f` as *inhibiting*
far-to-near call optimization, and TH04's normal response file does not specify
`/f`. Once the linker resolves `SPARK_A_TEXT` and `BULLET_U_TEXT` in the same
`MAIN_03` group, it replaces the five-byte far call with the same-length target
sequence:

```text
90 0E E8 85 73    NOP; PUSH CS; CALL near sparks_add_random
```

The segment relocation disappears at the same time. A `/P` code-packing relink
without `samecodeseg` leaves `CALL FAR`, so packing alone is not the mechanism.
The resulting full 875-byte target/candidate slice has SHA-256
`862908f44a5ade53c3148393f09bc0f76c02aac61488594e250aa8b91826673f`
and the ordered overlapping relocation list agrees. Two isolated cold builds in
`gptweb-bullets-full-v11-001` verify the full unit; the later default cohort
`source-layout-default-001` verifies it together with all other current
exact owners. No inline assembly, codestring, `__emit__`, raw byte directive, or
patched object/link output is used.

## Authored-boundary expansion: `MB_DFT_TEXT`, `snd_mmd_resident`, and `snd_se_reset`

The earlier module-routing ledger left the raw-identical 0x119-byte
`th04/mb_dft.cpp` contribution as `origin=unknown`. Raw identity was not enough
to classify the whole contribution as authored C/C++ because the candidate's
third function, `midboss_defeat_update`, contains inline assembly.

Fresh target review narrows a safe authored prefix instead of promoting the
whole module:

- TLINK public `13A9:64DE` / target linear `0x29F6E` starts
  `midboss_score_bonus`; Ghidra min/max end at `0x29FD7` (0x6A bytes).
- TLINK public `13A9:6548` / target linear `0x29FD8` starts
  `boss_score_bonus`; Ghidra min/max end at `0x2A046` (0x6F bytes).
- the next TLINK public `13A9:65B7`, `midboss_defeat_update`, starts exactly at
  `0x2A047`, immediately after the accepted 0xD9-byte prefix.

The maintained `src/main/midboss/score_bonus.inl` contains only the two natural
C/C++ functions and their required declarations/macros; it contains no inline
assembly or byte-emission escape hatch. Focused two-cold replay
`gptweb-mbscore-exact-002` reproduces all 217 accepted bytes, and
`gptweb-authored-expand-default-004` repeats the result inside the 64-unit
aggregate with matching TLINK placement, ordered overlapping relocations, and
normalized OMF identity.

Function review remains stricter than byte review. For both score-bonus
functions Ghidra's min/max spans are correct, but its body sets are
noncontiguous (66/106 and 71/111 bytes). The automatic gate therefore rejects
both. Two configured `[[reviewed_exact]]` entries use the existing fail-closed
manual path instead: same target Ghidra min/max, same local TLINK public, exact
owner containment, and independent `ndisasm -b16` coverage through terminal
`RET 2`. This adds two reviewed exact functions without weakening the automatic
contiguous-body rule.

`snd_mmd_resident` is also no longer left as an unreviewed whole-module
candidate. Target Ghidra and TLINK bind a 47-byte function at file `0x14BAC`;
the 48th module byte is trailing padding. A TH04-wrapper natural-C candidate
using `void far * __es *` reproduces the target `LES`, all three `MMD` magic
comparisons, and both global stores. It is intentionally **not** exact yet:
ordinary C `return true` / `return false` makes TC4J tail-merge the true return
into `JMP` plus one shared `RETF`, adding one byte and shifting three conditional
branch displacements. The two-cold candidate is deterministic but differs at
seven byte positions. Explicit `goto`, `_AX = _AX`, and whole-function `-O-`
probes did not restore the target early `RETF`.

A separate failed full-corpus probe established an ownership rule worth
preserving: replacing shared `th02/snd/mmd_res.c` with TH04-only source makes
the GAME=2 compilation consume TH04 declarations and fail with five
redeclaration/type errors. The replay manifest therefore overlays only the TH04
wrapper `th04/snd_mmdr.c` and keeps this candidate `default_enabled = false`.
Do not solve the remaining early-return mismatch by restoring the upstream
inline `RETF` assembly.

The 12-byte `th02/snd_se_r.cpp` umbrella candidate has a different boundary
shape. TLINK puts `_snd_se_reset` at the contribution start (`130E:07C6`), and
raw 16-bit target decode gives exactly two byte stores followed by `RETF` in
0x0B bytes. The twelfth byte is a standalone `NOP`, matching the candidate's
trailing `#pragma codestring "\x90"`. Therefore only the 11-byte function body
is reviewed as authored C/C++; the NOP stays outside the denominator. The
maintained `src/main/sound/se_reset.inl` contains no codestring or inline ASM,
uses checked-in `compat/rec98` one-line adapters for the two TH02 headers, and
replays through `source_mode = "forwarded-fragment"`. Focused receipt
`gptweb-snd-se-reset-003` and aggregate receipt
`gptweb-authored-expand-default-004` both reproduce all 11 bytes with stable
map placement, zero overlapping relocations, and deterministic normalized OMF.
Ghidra currently reports no function at target `0x238A6`; that blocks a
function-ledger promotion but does not invalidate the independently bounded
byte owner.

The remaining nonexact 0x5A-byte prefix of `th04/stages.cpp` was also screened
rather than blindly promoted. TLINK shows that the whole prefix is
`carpet_lighting_put_new()` from `0x3F9A` up to the already-exact
`stage4_render()` public at `0x3FF4`. Its candidate source depends on inline ASM
for DS→ES setup, `MUL`, `LODSB`, `SHL`, and `LOOP`, so the prefix is not a
maintained authored-C/C++ denominator candidate under the current rules. The
following 0x1AA-byte pure-C/C++ render suffix remains exact.

### Candidate umbrella retirement and `item_splashes_init` probe

A fresh coverage pass also reconciled several historical module-routing rows
against the current exact owners. Six modules had exactly one target byte left
outside maintained authored source: `tile.cpp` (`0xE341 = 90`), `initmain.cpp`
(`0x14EB3 = 00`), `snd_se_r.cpp` (`0x150B1 = 90`), `snd_se.cpp`
(`0x150EB = 90`), `scrolly3.cpp` (`0x15531 = 90`), and `grcg_3.cpp`
(`0x15715 = 90`). Each byte sits between or immediately after reviewed exact
owners. The pinned ReC98 candidate independently contains a matching
`#pragma codestring` at each location, so these are now explicit
`origin=padding` excluded owners rather than unresolved authored bytes.

The historical `bullet_u.cpp` module umbrella is also retired: its entire
0x565-byte contribution is covered by the exact 0x1FA-byte natural prefix plus
the exact 0x36B-byte `bullets_update`. Together these boundary decisions reduce
the live generic candidate-module queue from 16 rows to 9 without changing
either authored denominator or exact numerator. The remaining rows still have
real unresolved mixed/low-level or relocation-order work and are not excluded.

`item_splashes_init()` remains one such real gap. TLINK and target Ghidra bind
a complete 26-byte function at target `0x23F16` / file `0x15716`. The current
candidate matches 25/26 bytes; the sole difference is target `31 C0` versus
TC4J `33 C0` for `XOR AX,AX`, while the following `REP STOSW` and all other
bytes already match. Natural-source probes deliberately avoided inline ASM and
byte emission: regular `memset()` emits a runtime far call, Borland's official
`__memset__()` compiler intrinsic reorders ES/DI/AX/CX setup and still emits
`33 C0`, and `_AX ^= _AX` canonicalizes to the same `33 C0`. No natural exact
source is accepted yet; the negative receipt is retained under
`.analysis/reconstruction/probes/it-spl-u-natural/receipt.json`.

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

The regular manual gate now promotes 13 Ghidra body-construction false negatives:
the original four straight-line/overlap cases, `boss_items_drop`,
`bullet_velocity_and_angle_set`, five compiler-switch functions, and the two
new MB_DFT score-bonus functions. A separate
`[[reviewed_exact_extent]]` path handles `bullets_update`, whose Ghidra body
ranges are unusable. It reuses the complete-boundary checks from reviewed
nonexact accounting but additionally requires the entire configured extent to
stay inside one named exact authored owner. The gate validates the 0x360-byte
raw code through `RETF`, byte `0x2CC28` metadata, five near-jump words at
`0x2CC29`, all five decoded instruction targets, and exact next public
`0x2CC33`.

Reviewed nonexact functions still use the same fail-closed boundary path without
requiring exact bytes. `snd_load` is now the only such function.

The resulting denominator is 116 reviewed functions: **115 exact plus one
explicit nonexact `snd_load`**. No current function candidate remains
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
- Cross-game include ownership is part of exact replay. If a TH04 wrapper
  includes a lower-game source also built by TH02/TH03, overlaying TH04-only
  code onto that shared lower-game path can corrupt other corpus builds even
  when the TH04 object would compile. Prefer a TH04 wrapper overlay when the
  accepted object/module identity belongs to that wrapper.
- `__es` pointer syntax can solve Borland segment-load codegen without inline
  assembly, but it does not imply the rest of a function is naturally exact.
  In `snd_mmd_resident`, the `LES` and dataflow match while C-mode return
  tail-merging still changes final control-flow bytes. Treat compiler-control
  flow as a separate exactness dimension and keep negative source shapes in the
  knowledge ledger.
- A raw-identical module ending in a candidate `#pragma codestring` should be
  split at an independently decoded function return rather than promoted
  wholesale. `snd_se_reset` is the control: 11 pure-C bytes end at `RETF`, then
  one NOP padding byte remains excluded. A missing Ghidra function can block
  function accounting while byte ownership still proceeds from TLINK + raw
  decode + cold replay; keep those two denominators separate.
- Maintained cross-game fragments should use `compat/rec98` headers together
  with replay `source_mode=forwarded-fragment`. Do not weaken the include policy
  merely because the direct ReC98 fragment is byte-identical; the replay layer
  can attest the one-line adapters and resolve them back to the pinned scaffold.
