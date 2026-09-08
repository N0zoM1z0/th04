# TH04 `MAIN.EXE` authored exact batch

## Scope

This note records the first large exact reconstruction batch after the initial
58-module routing screen. ReC98 revision
`b6ba5b0a529edbb31efdf8c0e939263804f8ee47` is used only as pinned clean-build
scaffolding and candidate provenance. Every accepted byte comes from maintained
repository source and is re-attested against the pinned Japanese TH04 target.

The current reviewed results are:

- authored C/C++ bytes: **29,603 / 29,607 = 99.986490% exact**;
- authored functions: **208 / 209 = 99.521531% exact**;
- exact standalone original-style ASM: 9 units / 1,489 bytes, tracked
  separately and excluded from the authored C/C++ percentage.

## Cold replay design

`config/th04_main_exact_units.toml` and
`scripts/replay_th04_main_exact_units.py` define the replay. Each acceptance
run:

1. attests the pinned TC4J/TASM/TLINK/MS-DOS Player toolchain;
2. materializes two independent source trees with `git archive` from the pinned
   ReC98 revision, after first freezing every live repo-owned replay input to one
   path/size/SHA snapshot shared by both cold builds; the run fails if those live
   inputs mutate before completion;
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
`.analysis/reconstruction/exact-unit-replay/gptweb-marisa-main033-v66-precommit-web-009/receipt.json`.
It passes all 104 current default-selected exact-replay owners in both isolated
cold materializations, including the 0x9B6-byte contiguous MAIN_035/BOSS TU,
the 0x1CB-byte contiguous midboss/HUD/defeat TU, and the 11-byte pure-C
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

## v21 authored-boundary expansion: contiguous `MAIN_035` / boss TU

A whole-target rescreen found an unowned `0x2DF61..0x2E5D7` suffix at the end
of reconstructed `MAIN_035_TEXT`. This was not a Ghidra-only discovery. The
target raw bytes, final TLINK map, and a pinned TASM listing of the already
raw-exact scaffold identify ten true functions that tile the full 0x677 bytes:
`boss_reset`, `bb_boss_load`, `bb_boss_free`, and `stage1_setup` through
`stagex_setup`. Ghidra finds many starts but under-sizes `stage3_setup` and
`stagex_setup` and creates an internal false split inside `stage4_setup`.
Therefore target Ghidra body size is not used as the sole boundary oracle.

The next historical `BOSS_TEXT` contribution is 0x33F bytes and is flat-adjacent
to this suffix. Target `boss_defeat_update` contains a four-byte `PUSH CS; CALL
near` back to `bb_boss_free`, even though the reconstruction placed the callee
in `MAIN_035_TEXT` and the caller in `BOSS_TEXT`. Rebuilding the 0x677 suffix
plus the 0x33F boss contribution in target order as one maintained natural-C++
TU resolves this exactly. `src/main/boss/boss.cpp` emits one 0x9B6
`MAIN_035_TEXT` contribution; historical `BOSS_TEXT` becomes zero-length and the
following `MAIN_036_TEXT` start is unchanged. Ordinary `bb_boss_free();`
naturally compiles to target `0E E8 54 F7` inside the 468-byte defeat function.

Focused two-cold replay `gptweb-boss-tu-v21-003` reproduces all 2,486 bytes with
target SHA-256 `14ac3390b67ec8ee06b25669e9f8a62b9da07a9a82d96e100864a9fbe24cad1f`.
All 60 MZ relocation entries overlapping this extent match the target in their
original order. The 65-unit aggregate `gptweb-boss-tu-v21-default-001` also
passes raw/map/ordered-relocation/OMF/determinism for every selected owner.

The replay does not patch object bytes. A fail-closed `source_transforms` gate
is bound to the pinned `th04_main.asm` scaffold SHA, each unique text anchor,
the removed source-span SHA, and final patched scaffold SHA. It removes only
the now-maintained old ASM definitions, redirects stage-setup references to the
C++ publics, and exposes existing callback/string labels as cross-object symbols
without emitting data or instructions. This is build/source ownership metadata,
not target-byte injection.

ReC98 was explicitly not treated as the semantic oracle. Its TH04 stage2/stage3
candidate values and control flow are materially wrong. Target raw/decompile
shows stage2 with one `select_for_rank(255, 128, 32, 8)`, `frames_until=2600`,
HP 750, boss Y=81, and sprite 0; the maintained source follows the target and
TC4J codegen rather than copying the reference candidate.

Function review adds eleven exact functions over v20. Strict review can accept
`boss_reset`, `bb_boss_load/free`, stage1, stage2, stage5 and stage6 directly.
`stage3`, `stage4`, `stagex`, and `boss_defeat_update` use configured manual
exact-extent review because Ghidra's constructed bodies are incomplete. The
manual extent requires exact-owner containment, final TLINK public placement,
gap-free target raw decode through terminal `RET`/`RETF`, and the next public or
owner end. Same-address manual reviews shadow automatic Ghidra claims before
counting, and the ledger writer separately rejects any residual overlap. The
result is **140/141 exact functions** with 141 unique addresses; `snd_load`
remains the sole reviewed nonexact function.

## Authored-boundary expansion: contiguous midboss TU, `snd_mmd_resident`, and `snd_se_reset`

The earlier ledger treated `MIDBOSS_TEXT` (0x5A), `HUD_HP_TEXT` (0x58), and
`MB_DFT_TEXT` (0x119) as separate authored/codegen boundaries and therefore
stopped at the 0xD9 score-bonus prefix before `midboss_defeat_update`. That was
a useful conservative intermediate result, but v20 target/producer review
shows that the split itself was wrong.

The three ranges are perfectly contiguous in the target, totaling 0x1CB bytes.
Their six publics are `midboss_reset`, the activation helper,
`hud_hp_update_and_render`, the two score-bonus functions, and the final
64-byte `midboss_defeat_update`. Fresh nonce-attested Ghidra reports
`midboss_defeat_update` as one contiguous `0x2A047..0x2A086` body. Its target
tail calls `midboss_reset` with the four-byte `0E E8` form.

A private producer control first proved that TC4J can emit this four-byte form
when the callee definition is visible in the same logical segment. Applying
`#pragma samecodeseg` while preserving the reconstructed segment split was
**not** acceptable: it rebound the symbol/frame and linked the call to the wrong
flat target. The successful reconstruction instead removes the false split.
`src/main/midboss/midboss.cpp` emits all six functions in target flat order as
one natural-C++ TU. The ordinary `midboss_reset();` call then naturally becomes
the target `PUSH CS; CALL near` without inline assembly, codestrings, `__emit__`,
or object patching.

Focused two-cold replay `gptweb-midboss-tu-v20-002` reproduces all 0x1CB bytes
with target SHA-256 `a108783b4f393a9e1a35bdcf1730b9063442bf249a34567f5623c53b57ff903a`.
The fail-closed `[[build_replacements]]` gate changes only the unique TH04 MAIN
source-list triple from `midboss.cpp + hud_hp.cpp + mb_dft.cpp` to the combined
`midboss.cpp`; other games keep their original source graph. TLINK reports one
0x1CB `MIDBOSS_TEXT` contribution, zero-length historical `HUD_HP_TEXT` /
`MB_DFT_TEXT` labels, and an unchanged following `MAIN_034_TEXT` start. The
65-unit aggregate `gptweb-midboss-tu-v20-default-001` passes every raw/map/
ordered-relocation/OMF/determinism check.

Function review remains strict. The two score-bonus Ghidra body sets are still
noncontiguous and continue through the existing manual raw-decode gate. Three
previous automatic rows migrate from their historical owners only through
explicit address/from-owner/to-owner policy, and `midboss_defeat_update` is a
new automatic exact function after fresh Ghidra/TLINK review. The resulting
v20 function baseline was 129/130 exact; v21 supersedes it below. `snd_load` remains the sole reviewed
nonexact function.

`snd_mmd_resident` is now exact. Fresh target Ghidra/raw/TLINK review binds a
47-byte far function at file `0x14BAC` / linear `0x233AC`, ending in `RETF` at
`0x233DA`. The decisive source correction is removing `-WX`: the same pure-C
`__es` pointer expression still emits the target `LES` and magic checks, while
TC4J now keeps the target's distinct true/false `RETF` paths. This directly
falsifies the older candidate comment that `-WX` was required for the early
return; the extensive return-shape/barrier probes under `-WX` were solving the
wrong problem.

Dropping `-WX` changes the MMD contribution from 0x30/ACBP=48 to the exact
47-byte 0x2F/ACBP=28 function, which would shift the following KAJA/MODE/LOAD
contributions by one byte. `src/main/sound/mmd_align.c` solves **layout only**:
it is a zero-code C translation unit compiled with `-WX -zCSHARED -k-`, so TC4J
emits a word-aligned `SHARED` SEGDEF and no LEDATA. The fail-closed
`[[build_inserts]]` replay gate copies this checked-in source to 8.3-safe
`th04/mmdaln.c` and inserts it at one unique TH04 MAIN Tupfile context; anchor
drift is unit-tested and rejected. This restores the next contribution to
`130E:02FC` without object/byte patching. Target `0x233DB = 0x90` remains a
separate excluded padding owner and is neither emitted nor claimed by the layout
TU. Focused `gptweb-snd-mmd-no-wx-align-002` and 67-unit aggregate
`gptweb-snd-mmd-no-wx-align-default-001` both pass all required exactness gates.

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
`gptweb-script-params-internal-precommit-002` both reproduce all 11 bytes with stable
map placement, zero overlapping relocations, and deterministic normalized OMF.
Ghidra reports no function at target `0x238A6`; the later no-Ghidra
TLINK-public/raw-boundary gate now promotes `_snd_se_reset` in the function
ledger without inventing Ghidra metadata.

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

## No-Ghidra function recovery and natural `dialog_animate`

A second boundary audit deliberately starts from TLINK publics rather than the
Ghidra function list. Comparing every TLINK public inside every exact authored
byte owner against `config/th04_main_authored_functions.csv` initially found
eight missing function starts. Seven had no Ghidra function entry at all;
`bullet_turn_y` was absorbed into an unrelated oversized Ghidra body.

The checked-in `[[reviewed_exact_no_ghidra]]` path does not turn missing analysis
into positive evidence. It requires the public to lie in one exact authored
owner, rejects any start that actually has a Ghidra entry, raw-decodes the
configured code gap-free through a terminal `RET`/`RETF`, and requires the end
to equal either the exact owner end or an explicit next TLINK public. For
`tune_for_easy`, the gate additionally accounts for all trailing compiler data:
0x58 bytes of code through `RET`, metadata byte `00` at `0x2CC8B`, and 22 near
jump words at `0x2CC8C`; every decoded target is an instruction start and the
table ends exactly at the next public `0x2CCB8`. Regression tests make the gate
fail on an existing Ghidra entry, a bad boundary, a non-instruction table
target, or unexplained trailing bytes. Re-running the TLINK-public audit after
promotion reports zero missing publics inside current exact authored owners.

This adds eight exact functions without changing any byte owner:
`midboss_invalidate_func`, `boss_backdrop_render`, `_snd_se_reset`,
`grcg_setmode_rmw_seg3`, `bullet_turn_x`, `bullet_turn_y`, `tune_for_easy`, and
`BULLET_TEMPLATE_TUNE_EASY`.

`dialog_animate` then adds both byte and function coverage. Target Ghidra and
TLINK bind a contiguous 62-byte far function at file `0xEEEB` / linear
`0x1D6EB`, immediately before `dialog_init`. The target contains the five-byte
bridge `90 0E E8 ...` after pushing `PAGE_COUNT`. The maintained
`src/main/dialog/animate.inl` uses an ordinary
`tiles_activate_and_render_all_for_next_N_frames(PAGE_COUNT)` call annotated
with `#pragma samecodeseg`; normal TLINK 6.10 far-call optimization reproduces
the target `NOP; PUSH CS; CALL near` and ordered relocation sites. No inline
assembly, codestring, byte emission, or patched object is used. Focused receipt
`gptweb-dialog-animate-001` and later 66-unit aggregate
`gptweb-script-params-internal-precommit-002` both pass.


## Shared script helpers and internal/static function audit

The next expansion deliberately ignored the historical module queue and scanned
**every C/C++ TLINK public interval** in the current 66-unit candidate. Two pure
C++ helpers from shared `th03/formats/script.hpp` had never been assigned an
authored owner even though they sit inside `th04/dialog.cpp`'s linked
`DIALOG_TEXT` contribution:

- `script_param_read_number_first(int far&)`: target `0x1D0CA..0x1D192`,
  201 bytes, TLINK public `0AAF:25DA`;
- `script_param_read_number_second(int far&)`: target `0x1D193..0x1D1BB`,
  41 bytes, TLINK public `0AAF:26A3`.

The next public, `dialog_op`, begins exactly at `0x1D1BC` / `0AAF:26CC`.
Fresh nonce-attested Ghidra reports contiguous 201/201 and 41/41 bodies, and raw
16-bit decoding tiles both functions through `RET 4`. Maintained
`src/main/dialog/script_params.inl` is a pure-C++ identity fragment of the
shared header and contains no inline ASM, codestring, `__emit__`, or byte
patching. Focused replay `gptweb-dialog-script-params-002` and 66-unit aggregate
`gptweb-script-params-internal-precommit-002` reproduce all 242 bytes with matching
map placement, ordered relocation surfaces, and deterministic normalized OMF.
Both functions therefore enter through the normal automatic Ghidra+TLINK+exact
owner gate.

A second audit searched **all Ghidra entries inside exact authored byte owners**
without requiring a linker public. Most leftovers were analysis noise: one
switch case label and three basic-block false splits inside the already-reviewed
`bullets_update`. One entry was a real static function:
`tiles_render_all_timed()` at `0x1CB80..0x1CB98` (25 bytes). Since Borland does
not emit a TLINK public for it, the new `[[reviewed_exact_internal]]` gate is
stricter than automatic review. It requires:

1. a contiguous, non-thunk/non-external target Ghidra body inside one exact
   authored owner;
2. gap-free raw decode through terminal `RET`/`RETF`;
3. the configured function end to equal an existing next TLINK public; and
4. an independent target word inside the same exact owner to encode the near
   function offset under a configured CS base.

For `tiles_render_all_timed`, the next public is `tiles_activate` at `0x1CB99`.
A later exact-owner instruction in
`tiles_activate_and_render_all_for_next_N_frames` stores near offset `0x2090` at
target word `0x1CBB1`; `0x1AAF0 + 0x2090 = 0x1CB80`. A regression test mutates
this pointer word and requires the internal gate to fail closed.

After these promotions, an exhaustive linker-public screen leaves 14 C/C++
public intervals outside the reviewed function ledger. Ten are raw-identical in
the current candidate, but they remain unpromoted because their available source
shape is low-level/inline-ASM or a required Oracle still fails (for example,
`dialog_op` and `dialog_run` remain blocked on ordered MZ relocation order).
Four retain raw differences. The exact-owner internal Ghidra audit has no
remaining credible independent function entries. These 14 intervals are the
current boundary/exactness work queue rather than the older ReC98 module list.

## Function accounting

`config/th04_main_authored_functions.csv` is a separate function ledger. It
prevents module byte exactness from automatically becoming a function-boundary
claim.

`scripts/review_th04_main_functions.py` conservatively intersects:

- a function entry from the hash-attested target Ghidra database;
- a public symbol at the same start in the locally rebuilt TLINK map; and
- one exact authored byte owner from `config/units.csv`.

Automatic promotion still requires Ghidra's complete body to be contiguous
and wholly contained inside that exact byte owner; this now accepts 104
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

The regular Ghidra-min/max manual gate promotes 13 body-construction false
negatives: the original four straight-line/overlap cases, `boss_items_drop`,
`bullet_velocity_and_angle_set`, five compiler-switch functions, and the two
MB_DFT score-bonus functions. Eight further exact functions use the stricter
no-Ghidra public/raw-boundary path described above. One internal static function
uses `[[reviewed_exact_internal]]`: it has no TLINK public, so the gate requires
a contiguous target Ghidra body, exact authored owner, gap-free raw terminal
decode, exact next-public boundary, and an independent target function-pointer
word that resolves to the same entry. A separate `[[reviewed_exact_extent]]`
path handles `bullets_update`, whose Ghidra body
ranges are unusable. It reuses the complete-boundary checks from reviewed
nonexact accounting but additionally requires the entire configured extent to
stay inside one named exact authored owner. The gate validates the 0x360-byte
raw code through `RETF`, byte `0x2CC28` metadata, five near-jump words at
`0x2CC29`, all five decoded instruction targets, and exact next public
`0x2CC33`.

Reviewed nonexact functions still use the same fail-closed boundary path without
requiring exact bytes. `snd_load` is now the only such function.

The resulting denominator is 129 reviewed functions: **128 exact plus one
explicit nonexact `snd_load`**. No current function candidate remains
provisional.

## Reusable Borland lessons

- `-WX` affects both control-flow codegen and SEGDEF alignment. `snd_mmd_resident` needs no `-WX` for exact code; when only the following word boundary must be restored, a zero-code C translation unit can contribute only a word-aligned SEGDEF with no LEDATA. Keep that layout input separate from target padding ownership.

- Linker publics are not a complete function universe. After exhausting public
  starts, scan target Ghidra entries inside exact authored owners for credible
  internal/static functions, but do not promote an unlabelled entry on Ghidra
  alone. `reviewed_exact_internal` requires a raw terminal boundary, exact next
  public, and an independent target function-pointer word; `tiles_render_all_timed`
  is the accepted control.
- Shared source headers can contribute authored game code even when the wrapper
  module is already familiar. A whole-linker-public sweep found the 242-byte
  script-parameter pair in `th03/formats/script.hpp`; boundary discovery should
  therefore index the final TLINK map rather than only ReC98 translation-unit
  filenames or previously reconstructed modules.

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
- The old “combined midboss source still CALLF” result only held while preserving
  the reconstructed logical segment split. v20 proves the stronger rule: when
  contiguous target code and a four-byte near bridge contradict reconstructed
  segment ownership, test whether the **segment/TU boundary itself is false**.
  One logical TU/segment recovers the complete 0x1CB region naturally.
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


## v22: target-driven `MAIN_034` prefix recovery

The old ReC98 module-routing screen was not the complete authored-C++ candidate
universe. `MAIN_034_TEXT` begins with target public
`chasecrosses_add(unsigned char,unsigned char)` at `13A9:65F7` / linear
`0x2A087`, yet the function had no authored byte owner and ReC98 only retained
its structure/prototype. Fresh target Ghidra reports one contiguous 74-byte body,
and raw 16-bit decode gives a simple structure scan/store loop ending in
`RET 4`. Reconstructing that behavior from the target plus the independently
checked `chasecross_t` layout yields `src/main/boss/chasecrosses_add.cpp`; TC86
emits an exact 0x4A-byte `MAIN_034_TEXT` contribution. Focused
`gptweb-chasecross-v22-001` and 66-unit aggregate
`gptweb-chasecross-v22-precommit-003` reproduce all 74 bytes, map placement,
ordered overlapping relocations, and deterministic OMF identity.

Incrementally migrating a **prefix** out of monolithic `th04_main.asm` exposed a
separate TLINK layout problem. Simply placing `chase.obj` before `main.obj`
causes `MAIN_03` ordering/size failure, and a MAIN_03-only zero-byte anchor moves
that group ahead of MAIN_01. The accepted replay therefore materializes
`src/main/layout/main_code_order_anchor.asm`, which declares the original
MAIN_01 code segments, `SHARED`, and MAIN_03 code segments/groups in target
order. Its OMF has 50 SEGDEF, 2 GRPDEF, and **zero LEDATA**; the replay driver
hard-checks that property and deterministic normalized identity. The anchor
owns no authored bytes and emits no target program/data bytes. With the anchor,
TLINK places a zero-byte metadata contribution at `13A9:65F7`, the natural
`th04/chase.cpp` contribution at `13A9:65F7` size `0x4A`, and residual
`th04_main.asm` at `13A9:6641` size `0x25FD`, while all program CODE segment
start/length tuples stay unchanged.

This established the historical v22 baseline at **15,544 / 15,548 authored bytes exact
(99.974273%)** and **141 / 142 reviewed functions exact (99.295775%)**. It also
provides a reusable, fail-closed route for continuing into the large still
unowned compiler-like regions embedded in `MAIN_033_TEXT`, `MAIN_034_TEXT`, and
`MAIN_036_TEXT` without treating ReC98's reconstructed files as the boundary of
the search space. `snd_load` remains the sole reviewed nonexact function.

## v23: extend `MAIN_034` through the internal safety-circle initializer

The next true TASM `PROC` after `chasecrosses_add` starts at target `0x2A0D1`
and ends immediately before the next true entry at `0x2A110`, giving a 0x3F-byte
function. This function has no original TLINK public. Fresh Ghidra correctly
creates an entry at `0x2A0D1` but constructs only 25 of its 63 bytes, so Ghidra
body size is not used as the extent oracle. Instead, target raw decode tiles all
63 bytes through `RET`, target near call `0x2ADD6` resolves exactly to the entry,
and pinned TASM plus fresh Ghidra both place the next true entry at `0x2A110`.

Target field accesses also falsify the ReC98 structure layout. ReC98's
`safetycircle_t` uses `unused_3[8]`, placing `col_ring` at +0x1C. The target
instruction is `C6 44 18 08`, so `col_ring` is at +0x18; natural TC4J source
with `unused_3[4]` emits the exact 63-byte instruction skeleton. With this
correction, `src/main/boss/chasecrosses_add.cpp` emits one 0x89-byte
`MAIN_034_TEXT` prefix containing the 0x4A chase function followed by the 0x3F
safety-circle initializer. Residual `th04_main.asm` resumes at `13A9:6680`.

Focused replay `gptweb-safetycircle-v23-002` and aggregate
`gptweb-safetycircle-v23-precommit-004` reproduce all 137 bytes, exact map extent,
ordered overlapping relocation list, deterministic TC86 OMF, and the unchanged
zero-LEDATA code-order anchor. The function ledger uses the fail-closed
`reviewed_exact_internal_call` path: exact owner + target Ghidra entry + raw
terminal + next internal entry + target near-call anchor. A generated TLINK
public used only for cross-object reconstruction is explicitly named but is not
treated as target boundary evidence.

The v23 reviewed baseline is **15,607 / 15,611 authored C/C++ bytes exact
(99.974377%)** and **142 / 143 reviewed functions exact (99.300699%)**.
`snd_load` remains the sole reviewed nonexact function, with four blocked bytes.

## v24: recover the 691-byte target-only Yuuka6 update

The next true TASM `PROC` after the v23 safety-circle initializer starts at
`0x2A110` / file `0x1B910`. Pinned TASM local offsets put the following true
function at `0x2A3C3`, so this routine occupies exactly **0x2B3 = 691 bytes**.
ReC98 does not contain a decompiled implementation. Raw target code has no
`REP`/`LOOP`/segment-register/port-I/O fingerprint: it is ordinary gameplay
logic over chase crosses, the safety circle, shots, sparks, items, score, and
bullet templates. Existing typed APIs plus target-observed constants are
sufficient to express it as natural C++.

Compiler archaeology converged tightly. TC86 immediately emitted the exact
0x2B3 size and full instruction sequence apart from two source-shape details.
First, `sparks_add_random` remained `CALL FAR` in OMF; adding the already-proven
`samecodeseg` frame hint lets normal TLINK rewrite that five-byte call to the
target `NOP; PUSH CS; CALL near`. Second, the linked artifact differed at only
16 bytes, all BP-relative local displacements. TC86 allocates these locals in
declaration order. Reordering the four declarations to `length, top, angle,
angle_delta` produced target BP-2/-4/-5/-6 slots and removed every remaining
byte difference without low-level code.

With the v24 source transform removing the old `yuuka6_1A110` ASM `PROC` and
retargeting its single residual caller, `src/main/boss/chasecrosses_add.cpp` now
contributes exactly **0x33C bytes** at `13A9:65F7`; residual `th04_main.asm`
resumes at `13A9:6933`. Final-source focused replay
`gptweb-yuuka6-update-v24-002` and 66-unit aggregate
`gptweb-yuuka6-v24-precommit-001` reproduce the full prefix, seven ordered
overlapping relocations, deterministic TC86 OMF, and the unchanged zero-code
layout anchor. The maintained master.lib dependency goes through the checked-in
`compat/rec98` forwarding layer.

Function review remains independent of generated symbols. Ghidra creates the
entry at `0x2A110` but reports only 372 body addresses and stops at `0x2A3C0`,
two bytes before the target `RET`. Ghidra also has no entry at the true next
TASM function `0x2A3C3`. Target near call `0x2B8F9` resolves to `0x2A110`, raw
decode tiles through `RET@0x2A3C2`, and the first eight target bytes at the next
entry hash to `7af4982d...`. `reviewed_exact_internal_call` now supports this
fail-closed target-attested next-boundary mode. Generated publics are marked
provisional and excluded from automatic public-based review.

The v24 reviewed baseline is **16,298 / 16,302 authored C/C++ bytes exact
(99.975463%)** and **143 / 144 reviewed functions exact (99.305556%)**.
`snd_load` remains the sole reviewed nonexact function with four blocked bytes.

## v25: recover the no-Ghidra 118-byte Yuuka6 phase-2 fly helper

Pinned TASM local symbols place `@yuuka6_phase2_fly$qv` at target `0x2A3C3`
and the next true helper at `0x2A439`, giving exactly 0x76 bytes. Target Ghidra
contains no current function at all, while the next helper is a complete 111-byte
Ghidra body. Target near call `0x2B563` resolves to `0x2A3C3`, and raw decode
ends in `RET` at `0x2A438`. The function is therefore admitted only through the
new fail-closed `reviewed_exact_no_ghidra_internal_call` path; the v25 TLINK
public is generated reconstruction plumbing and is excluded from automatic
public-based review.

The source is ordinary C++ integer/control-flow code. An initial equivalent
`if/else if` form compiled to 0x72 bytes. The target loads `boss.phase_frame`
into AX once, compares against 1 and 112, and uses a shared default path. Writing
that source as `switch(boss.phase_frame)` makes TC86 emit exactly that sequence,
restores the missing four bytes, and produces an exact 0x76 function with the
same 49 instruction mnemonics as the target. The final case returns the result
of the still-ASM `yuuka6_1A439` helper through a zero-code public alias at its
unchanged target address; no byte payload is inserted.

Focused `gptweb-yuuka6-phase2-v25-001` and 66-unit aggregate
`gptweb-yuuka6-phase2-v25-precommit-001` reproduce the entire **0x3B2-byte**
`MAIN_034_TEXT` prefix, exact map placement, all seven ordered overlapping MZ
relocations, deterministic TC86 OMF, and the zero-LEDATA code-order anchor.
The v25 reviewed baseline is **16,416 / 16,420 authored C/C++ bytes exact
(99.975639%)** and **144 / 145 reviewed functions exact (99.310345%)**.


## v26: recover the 111-byte Yuuka6 move helper

Pinned TASM places `yuuka6_1A439` immediately after the v25 prefix at target
`0x2A439`, with the next true entry at `0x2A4A8`; the resulting extent is exactly
0x6F bytes. Fresh nonce-attested Ghidra independently reports a contiguous
111/111-byte function at the same entry and a complete next function. Target raw
near call `E8 86 EE` at `0x2B5B0` resolves exactly to `0x2A439`, so the boundary
does not depend on the reconstruction-generated TLINK public.

The source is ordinary C++. TC86 naturally assigns the two arguments to SI/DI,
loads `boss.phase_frame` once into AX for the 64/128 sparse cases, emits the target
animation-call branches, and ends with the target Pascal-style `RET 4`. Two
private monolithic-ASM data labels are needed by the function; replay exposes them
with zero-byte `PUBLIC`/`LABEL` aliases at their existing storage instead of
copying or re-emitting the data. The old 111-byte ASM PROC is hash-bound and
removed, exactly three residual ASM calls are retargeted, and all transforms fail
closed on count/hash drift.

Focused `gptweb-yuuka6-move-v26-001` and aggregate
`gptweb-yuuka6-move-v26-default-001` reproduce the complete **0x421-byte**
`MAIN_034_TEXT` natural-C++ prefix with zero raw differences and identical seven
ordered MZ relocation entries. The reviewed baseline is now **16,527 / 16,531
authored C/C++ bytes exact (99.975803%)** and **145 / 146 reviewed functions exact
(99.315068%)**; `snd_load` remains the sole reviewed nonexact function with four
blocked bytes.


## v27: recover the 91-byte Yuuka6 horizontal-wave helper

The next target/TASM function at `0x2A4A8` is a complete 0x5B-byte Ghidra body
ending in `RET`; the next true entry is `0x2A503`, and raw target call `0x2B659`
resolves exactly to the helper. Natural C++ reproduces the target motion logic: X
velocity initialization/bounce, sine-driven Y motion through the existing exact
`polar()` API, and `boss.angle += 2`.

The first full-link prototype differed at only two non-relocation bytes while
function size and all relocations already matched. Those bytes were the two
packed Pascal argument words for `polar()`: writing `center=48px,radius=80px`
produced the reversed packed immediate. The target encodes `center=80px,
radius=48px`; correcting only that natural source semantics removes both bytes.
Focused `gptweb-yuuka6-wave-v27-001` and aggregate
`gptweb-yuuka6-wave-v27-default-001` reproduce the complete **0x47C-byte**
`MAIN_034_TEXT` prefix and all eight ordered relocations exactly. The reviewed
baseline is **16,618 / 16,622 bytes exact (99.975936%)** and **146 / 147 functions
exact (99.319728%)**.


## v28: recover the 58-byte Yuuka6 move-to-center helper

The next target helper begins at `0x2A503` and ends at `0x2A53C`. Fresh Ghidra
constructs all 58 body bytes, raw decode terminates in `RET`, and the next target
Ghidra entry begins exactly at `0x2A53D`. A direct scan of the target MZ finds two
near calls resolving to the helper (`0x2B697` and `0x2B791`), so the boundary does
not depend on the reconstruction-generated TLINK public.

Target semantics are simple but source-shape-sensitive: when the sprite state is
vanished the helper calls the existing appear animation; otherwise it clears the
private auxiliary flag and adjusts `boss.pos.cur.x` by one pixel until it lies in
the target's 192px/193px center window. The natural C++ implementation extends
`MAIN_034_TEXT` from 0x47C to **0x4B6 bytes**. Focused
`gptweb-yuuka6-center-v28-001` and final aggregate
`gptweb-yuuka6-center-v28-precommit-001` both pass two-cold raw bytes, map extent,
ordered relocation overlap, deterministic valid OMF, and zero-code layout-anchor
checks. The reviewed baseline is now **16,676 / 16,680 bytes exact
(99.976019%)** and **147 / 148 functions exact (99.324324%)**; the same four
`snd_load` bytes remain the sole reviewed authored mismatch.


## v29: recover the eight Yuuka6 compiler-switch animation helpers

The next target range `0x2A53D..0x2A906` contains eight adjacent sprite-animation
helpers totaling **0x3CA = 970 bytes**. ReC98 still keeps these implementations in
`b6_anim.asm`; natural C++ `switch` statements reproduce the entire family in a
dedicated `MAIN_034_TEXT` TU. Focused `gptweb-yuuka6-anims-v29-004` and the
67-unit aggregate `gptweb-yuuka6-anims-v29-final-web-001` are raw/map/ordered-
relocation/OMF/determinism exact in both cold materializations.

Function boundary accounting must include compiler-owned trailing data. Ghidra
starts all eight functions correctly but stops at their final `RET`, omitting the
TC86 switch representation. Depending on the function, the remaining bytes are
`compare-word table + near-jump table`, `zero alignment byte + compare table +
jump table`, or for the dense 40-frame switch `zero alignment byte + 40-entry
jump table`. The fail-closed exact-extent reviewer validates this entire sequence,
checks sparse compare constants, resolves each jump word via CS base `0x23A90`
to a decoded instruction start, and requires the final table byte to be exactly
the next target/TASM function boundary.

The independent TU is also a compiler-layout control: file-start `#pragma option
-a` reproduces the target's selective switch-table alignment bytes. Three long
`extern "C"` animation identifiers exceed TC86's 32-character source-name
limit and therefore appear in OMF/TLINK truncated; replay hash-binds the residual
ASM references to those exact truncated names without emitting or patching code
bytes. The reviewed baseline is now **17,646 / 17,650 bytes exact (99.977337%)**
and **155 / 156 functions exact (99.358974%)**. `snd_load` remains the sole
reviewed nonexact function, with four blocked bytes.

## v30: recover five Yuuka6 gather-pattern helpers

The next target/TASM range `0x2A907..0x2AB5C` contains five adjacent helpers
with exact extents `0xAE`, `0x15`, `0x7B`, `0xA0`, and `0x78`, totaling
**0x256 = 598 bytes**. ReC98 still keeps the implementations inside
`th04_main.asm`; the maintained reconstruction was derived from target raw
semantics and existing typed `gather_template`, `gather_add_only()`, and
`circles_add_shrinking()` APIs rather than from a high-level upstream source.

The compiler source shape is observable. The first 0xAE-byte sparse switch
matched total size and compare/jump-table shape before it matched control flow:
placing the shared gather tail after case `0x12` made TC86 emit a forward short
jump, while the target jumps backward. Moving the common label before that case
and using a natural `goto` changes only the shared-tail layout and reproduces the
target branch direction and jump-table words. The final TU emits publics at the
target offsets `0x000/0x0C3/0x13E/0x1DE`; the 0x15 shared helper remains static
between the first and second public.

Ghidra demonstrates two different failure modes in the same authored owner. It
creates entries at `0x2A907`, `0x2A9CA`, `0x2AA45`, and `0x2AAE5` but reports
only their code/CFG addresses, excluding trailing alignment/compare/jump data.
It creates no function at `0x2A9B5`. The exact-extent reviewer accounts for the
four compiler switch representations byte-for-byte, while the missing helper is
reviewed with exact-owner containment, raw `RET`, the next Ghidra/TASM entry,
and target near call `0x2AA14 -> 0x2A9B5`.

Focused replay `gptweb-yuuka6-gather5-v30-web-001` and 68-unit aggregate
`gptweb-yuuka6-gather5-v30-precommit-web-001` reproduce all 598 bytes, exact map
placement (`13A9:6E77 0256`), all ten ordered overlapping MZ relocations, and a
deterministic normalized TC86 OMF in both cold materializations. The reviewed
baseline is now **18,244 / 18,248 authored C/C++ bytes exact (99.978080%)** and
**160 / 161 reviewed functions exact (99.378882%)**. `snd_load` remains the sole
reviewed nonexact function with four blocked bytes.

The v30 rescreen also invalidates the old linker-public-only queue as an exhaustive
candidate universe. The next live target-first frontier is `0x2AB5D`; pinned TASM
already exposes further local Yuuka6 procedures before `yuuka6_update()` and then
an Elly local-procedure family, so future boundary screening must continue from
raw/TASM evidence beyond public symbols.


## v31-v36: continue target-first through Yuuka6 attack/update and the first Elly locals

The v30 local-PROC scan was deliberately continued rather than treating the >99% baseline as complete. The next exact sequence is:

- **v31:** five Yuuka6 attack helpers, `0x2AB5D..0x2AE8E`, 0x332 bytes. Raw-exact standalone C++ exposed a different MZ relocation order; one fused TC86 producer with the prior chase/animation/gather source matches both bytes and ordered relocations.
- **v32:** eight late Yuuka6 helpers, `0x2AE8F..0x2B42E`, 0x5A0 bytes. Target TASM falsifies ReC98's one-byte `thicklaser_t::unused_2`; the target needs four bytes.
- **v33:** corrected 0x52D ownership at `0x2B42F..0x2B95B`: separate 0x4F `YUUKA6_PHASE_NEXT`, then `yuuka6_update()` plus four compiler switch-table regions. Ghidra cannot define either complete boundary.
- **v34:** `elly_scythe_update()`, `0x2B95C..0x2BC3B`, 0x2E0 bytes. Raw code ends at `0x2BC2B`, then an eight-entry jump table fills the owner. Ghidra false-splits the target into several functions. Natural TC86 source recovers exact bytes through source-level block placement and reload/branch semantics rather than emitted bytes.
- **v35:** `elly_scythe_init()`, `0x2BC3C..0x2BC72`, 0x37 bytes, exact on the first natural C++ form.
- **v36:** `elly_orbit_update()`, `0x2BC73..0x2BD22`, 0xB0 bytes. Signed target branches recover the hidden `int` type, and retaining a redundant `>=768` condition reproduces the final eight target bytes.

Final aggregate `gptweb-elly-v36-precommit-web-002` cold-builds **74 default owners twice** and reports zero raw/map/ordered-relocation/OMF/determinism failures. The reviewed denominator is **22,794 / 22,798 authored bytes exact (99.982455%)** and **178 / 179 reviewed functions exact (99.441341%)**; only four `snd_load` bytes remain nonexact.

The next target-first frontier is **`0x2BD23`**, not a linker-public queue. Further local starts before public `elly_update()` are `0x2BD4B`, `0x2BDB4`, `0x2BE43`, `0x2BE78`, `0x2BF52`, `0x2BFAB`, `0x2C044`, `0x2C0BF`, `0x2C164`, `0x2C1CF`, and `0x2C251`. Re-establish every extent from target raw/TASM/control flow and treat Ghidra bodies as provisional.


## v37-v48: finish the Elly local-PROC family

Continuing the target-local TASM screen from `0x2BD23` recovers every remaining
local Elly procedure before public `elly_update()`. The twelve exact extents are
`0x28`, `0x69`, `0x8F`, `0x35`, `0xDA`, `0x59`, `0x99`, `0x7B`, `0xA5`,
`0x6B`, `0x82`, and `0x94` bytes, totaling **0x5C2 = 1,474 bytes** and tiling
`0x2BD23..0x2C2E4` without overlap. Each has a maintained natural-C++ source and
focused A/B cold replay; the 86-owner aggregate
`gptweb-elly-local-family-v48-precommit-web-002` passes raw/map/ordered-
relocation/OMF/determinism for the complete default cohort twice.

This family is another strong negative control against Ghidra-only boundary
classification. Some entries are complete, but `0x2BE78`, `0x2BF52`,
`0x2BFAB`, `0x2C044`, `0x2C0BF`, and `0x2C164` are sparse or internally
false-split. `elly_gather_update()` at `0x2BDB4` ends raw code at `0x2BE31` yet
owns compiler data through `0x2BE42`: `00` alignment, four compare words
`1/8/16/32`, and four near-jump words. The exact-extent reviewer validates every
trailing byte and jump target before admitting the function.

Exact source work also exposed three reusable TC86 constraints. Struct ABI is
sensitive to the compiler alignment state at header parse time, so `-a` must be
enabled after ABI headers when the target packed layout requires it. DOS 8.3
output naming applies to overlay basenames and can silently change object names.
And direct consumption of a call result in AX can be required to avoid a
compiler-selected SI temporary. None of these fixes uses inline assembly,
codestrings, `__emit__`, object patching, or target-byte injection.

The reviewed result after v48 is **24,268 / 24,272 authored bytes exact
(99.983520%)** and **190 / 191 functions exact (99.476440%)**. `snd_load` is
still the sole reviewed nonexact function with four blocked bytes. Candidate
expansion now resumes at public **`elly_update()` `0x2C2E5`**, whose current
Ghidra body is cross-linked and cannot define the target extent by itself.


## v49: recover `elly_update()` and close `MAIN_034_TEXT`

The next public target entry after the v37-v48 local family is `elly_update()`
at runtime `0x2C2E5`. Ghidra creates the correct entry but cross-links its body
to unrelated later code, so the accepted `0x3E9` extent is derived independently:
`0x3AD` bytes of gap-free raw code through `RETF 0x2C691`, followed by three
contiguous TC86 switch regions ending at `0x2C6CD`. All decoded switch targets
land on instruction starts. The next exact TLINK public, `bullet_turn_x`, begins
at `0x2C6CE`.

`src/main/boss/elly_update.cpp` is ordinary maintained C++. The final aggregate
integration fixes are ABI/linkage facts rather than byte emission: the callback
is `pascal far`, matching the already-exact boss setup TU, and residual TASM
uses the corresponding `@ELLY_UPDATE$QV` OMF external spelling. Focused
`gptweb-elly-update-v49-focused-final-web-004` and 87-owner aggregate
`gptweb-elly-update-v49-precommit-web-003` reproduce the target slice SHA
`33eec33c...b7cce`, both ordered relocation sites, containing TLINK placement,
and deterministic normalized `ellyall.obj` OMF in both cold builds.

A segment-level re-audit then verifies that `MAIN_034_TEXT` is no longer an open
candidate frontier. Its target span is exactly `0x2647` bytes; 22 exact authored
owners tile the complete `13A9:65F7..8C3D` range with no gaps or overlaps, and
residual ASM contributes zero bytes at the segment end. A separate local-PROC
scan finds 38 numeric TASM procedure starts and zero omissions from the exact
function ledger. Candidate discovery can therefore move away from this segment
without relying on Ghidra completeness.

After v49, the reviewed result is **25,269 / 25,273 authored bytes exact
(99.984173%)** and **191 / 192 functions exact (99.479167%)**. `snd_load`
remains the only reviewed nonexact function, with four blocked bytes.

## v50-v66: Stage 4 Marisa and TC86 producer-boundary recovery

A whole-artifact coverage audit after v49 deliberately ignored the fact that
MAIN_034 itself was exhausted. It found that `MAIN_033_TEXT` remained a large
0x32B7-byte residual compiler segment. Target TASM identifies its prefix as the
Stage 4 Marisa boss implementation, beginning with local `marisa_16C05` at
runtime `0x26C05`. ReC98 does not provide high-level implementations for these
local phases, so all accepted source here was reconstructed from target
instructions/control flow and verified with the pinned TC4.02 toolchain.

v50-v66 recover **4,334 bytes / 17 functions** through public `marisa_update()`.
The code-generation work yielded several reusable natural-C++ rules: declaration
order controls BP-local placement independently of execution order; `volatile`
can prevent loop-index promotion; `register` declaration order selects SI/DI;
function-scope register lifetime can force target callee-saved prologues; and
explicit `signed char` is required where target signed byte comparisons are
observable. None of these sources uses inline assembly, codestrings, `__emit__`,
object patching, or target-byte injection.

Raw-byte equality alone was insufficient to recover physical TU boundaries.
With v50-v65 in one object, v60/v61 had identical relocation sites but the wrong
ordered MZ relocation list. TC4-only object probes plus Borland TDUMP showed
that one FIXUPP record lists higher offsets first, while distinct LEDATA/FIXUPP
records preserve record order. Starting a new producer at v59 `0x2717D` makes
both v60 sound-call relocations share the first record and splits the two v61
relocations across the 0x400 boundary. A second producer start at v64 `0x2788E`
puts both v64 sound-call relocations in one record. The accepted split is
0x578-byte `m4bits.cpp`, 0x711-byte `m4late.cpp`, and 0x465-byte `m4tail.cpp`.
A tested B4M+MAIN_033 fusion was rejected because it necessarily misplaces one
of the two target segments and does not change MAIN_033 LEDATA chunking.

`marisa_update()` is a 0x2FF-byte reviewed owner: 0x2CB code bytes through RETF
plus 0x34 compiler switch data. The trailing region is exactly an 11-value
compare table `[0,1,2,3,4,5,6,7,10,11,255]`, its 11 near jump targets, and a
four-entry phase jump table, ending immediately before `enemies_add` at
`0x27CF3`. The function reviewer validates every table target instead of using
Ghidra's cross-linked body.

Focused `gptweb-marisa-main033-v66-focused-final-web-001` and aggregate
`gptweb-marisa-main033-v66-precommit-web-009` are current-manifest two-cold
PASS receipts. The aggregate covers **104 default exact owners** with no prior
owner regression. The reviewed result after v66 is **29,603 / 29,607 authored
bytes exact (99.986490%)** and **208 / 209 reviewed functions exact
(99.521531%)**. The only reviewed nonexact function remains `snd_load`, with
four blocked bytes. Candidate expansion continues in the same MAIN_033 segment
at the Mugetsu local family beginning at `0x2802F`.
