# TH04 `MAIN.EXE` FIXUPP / code-generation probe log

## Purpose

This note records diagnostic experiments that intentionally **do not** promote
any new exact byte owner. They exist to stop later reconstruction passes from
repeating source, translation-unit, compiler-option, and assembler hypotheses
that have already been falsified against the pinned TH04 target.

The target remains the hash-attested Japanese `MAIN.EXE`. ReC98 revision
`b6ba5b0a529edbb31efdf8c0e939263804f8ee47` is build scaffolding and candidate
provenance only. Every experiment below was rerun locally against target bytes,
TLINK layout, Intel OMF, or the ordered MZ relocation table.

No experiment below inserts target opcodes, edits compiler-generated assembly,
patches OMF records, or adds inline assembly to maintained C/C++ source.

## A pinned DOS TASM exists inside the already-attested TASM 5.0 media

The pinned TASM 5.0 floppy set contains `CMD16.PAK`. The package was extracted
only in ignored `.analysis` space with the media's own `UNPAK.EXE` under the
pinned MS-DOS Player. Relevant private identities are:

| Surface | SHA-256 |
| --- | --- |
| `CMD16.PAK` | `47c2f590d3ea2f81d837005108013a9e17581bfc0be72c086154ce4bef092809` |
| TASM-media `UNPAK.EXE` | `dc278696b27aa63bd63fed0920cdeb986e84963c971ea0c0c9cc5b67a9e3cee1` |
| extracted `TASM.EXE` | `cafc42bbd1df39ab36e775be74ccb82c0a80da7d2a6dff4dcc2f16ba0e220f95` |

`TASM.EXE` reports `Turbo Assembler Version 4.1`. This is the DOS assembler that
Turbo C++ can invoke for `TCC -B` (compile via assembly). It is diagnostic until
and unless it is promoted into the formal portable toolchain manifest.

### `TCC -B` changes FIXUPP without changing code

`slowdown.cpp` is a useful control because the direct TC86 object is already
known exact. Compiling the same pure C++ source through `TCC -B` and the pinned
DOS TASM produced identical LEDATA machine code:

```text
55 8B EC A1 0000 3B 06 0000 72 F7 C7 06 0000 0000 C7 06 0000 0100 5D C3
```

but a different FIXUPP subrecord order. Direct TC86 orders the four relevant
fixups from the highest location back toward the lowest; TASM orders them from
low to high. The object hashes are intentionally different:

```text
direct TC86: cf167cdcb73a2b0913a8735a7e85f1df3f149305c57f4b309192d9009ab74cb6
TCC->TASM41: 4d7c4abb73efddbc267988acab6a20b4bd5e68cbdfcbedf4c4c61cf1a9fe8ba2
```

This is direct evidence that identical x86 code does **not** imply identical
Borland FIXUPP ordering, and that the producer path itself is a binary input.
It does not mean TASM ordering is automatically the target ordering.

## `dialog_op`: natural TU boundaries rotate the same relocation set

`dialog_op` is raw-identical in all useful probes below. Its target relocation
sequence can be grouped as follows:

```text
A = d26e d263 d228 d21d d1cb
B = d522 d513 d506
C = d4a1 d493 d48e d486 d476 d46f d40e d3e1 d3d3 d3ac d363 d34b
X = d32d d2f9 d2ec d2e5 d2b4 d2a9

target = A B C X
```

Changing only how much naturally generated DIALOG_TEXT precedes `dialog_op` in
its object rotates this same set without changing the function bytes:

| `dialog_op` object-local start | Structural probe | Ordered groups |
| ---: | --- | --- |
| `0x27F` | current/historical merged prefix | `X A B C` |
| `0x0F2` | move `shared.cpp` code to preceding TU | `C X A B` |
| `0x0029` | also move first script-number helper | `B C X A` |
| `0x0000` | also move second script-number helper | `B C X A` |

None matches target `A B C X`. The `0x0F2` experiment causes unrelated prefix
code drift outside `dialog_op`, so it is diagnostic only. The important result
is the rotation itself: object/TU boundaries affect FIXUPP emission, but the
obvious natural boundaries tried so far do not solve `dialog_op`.

A follow-up sweep closes the remaining natural `shared.cpp` function boundaries
without splitting any function body. Each diagnostic relink keeps the final
`dialog_op` and `dialog_run` program-image bytes exact. The `dialog_op`
relocation column below is the cyclic rotation index relative to target order
(`0` would be exact):

| Split after natural source function | `dialog_op` object-local start | `dialog_op` rotation | `dialog_run` rotation |
| --- | ---: | ---: | ---: |
| current / no split | `0x27F` | 20 | 2 |
| `std_update_done` | `0x278` | 20 | 2 |
| `std_update_frames_then_animate_dialog_and_activate_boss_if_done` | `0x1FE` | 17 | 2 |
| `dialog_box_put` | `0x1A6` | 14 | 2 |
| `playfield_copy_front_to_back` | `0x16E` | 14 | 2 |
| `dialog_face_unput_8` | `0x124` | 9 | 2 |
| `dialog_box_fade_in_animate` / all shared definitions moved | `0x0F2` | 8 | 2 |
| first script-number helper also moved | `0x0029` | 5 | 2 |
| both script-number helpers also moved | `0x0000` | 5 | 2 |

This covers every current natural function boundary immediately preceding
`dialog_op`, including the two compiler-emitted script-number helpers. None
produces target rotation 0, and `dialog_run` never leaves rotation 2. Do not
repeat these boundaries as proposed fixes; a future solution needs materially
different source/IR or producer evidence.

### Compare MZ program images, not borrowed file offsets

The five new diagnostic relinks have a `0x1600` MZ header while the target has a
`0x1800` header. Their `dialog_op` / `dialog_run` load-module bytes and public
addresses are nevertheless exact. An initial diagnostic that cut candidate
bytes at the target's file offsets therefore produced a false mismatch. Always
parse each candidate's own `e_cparhdr` and compare program-image offsets. The
formal replay driver already does this correctly.

## `dialog_run`: ending the object at RET is not enough

A natural split that makes `dialog_run` its own `0x17F`-byte DIALOG_TEXT object
and moves `dialog_animate` to the following TU preserves every `dialog_run`
code byte and every final public address. The ordered relocation list remains:

```text
target:    d642 d617 d6df d6c0
candidate: d6df d6c0 d642 d617
```

Therefore a simple FIXUPP flush at the function's RET does not explain the
target order. The two target pairs correspond to the earlier box/inner-loop
block (`text_putca` / `input_reset_sense`) and the later regular-kanji block
(`text_putsa` / `frame_delay`). Within each pair TC86 already has the target's
reverse-address ordering; the unresolved difference is the order of the two
high-level fixup groups.

### Source-shape probes

A run-only C++ TU was minimized until its generated code group contained only
`DIALOG_TEXT`. Direct TC86 still emits exactly the same 383 LEDATA bytes as the
accepted run-only object. This gives a cheap source-shape oracle.

The following transformations were tested without inline assembly:

- structured `while` loops -> explicit labels/gotos matching the old assembly
  CFG: **383-byte LEDATA exact, FIXUPP unchanged**;
- `dialog_text_put` inline function -> macro: **383-byte LEDATA exact, FIXUPP
  unchanged**;
- `dialog_box_wipe` macro -> inline function: code grows to 402 bytes;
- `dialog_delay` macro -> value/reference/const-reference inline function:
  code changes (390 or 384 bytes).

The two exact-code transformations prove that merely changing between these
surface source forms does not alter the direct TC86 fixup queue.

## TC86 option matrix for `dialog_op` / `dialog_run`

The existing split dialog source was recompiled one object at a time and
relinked with the same TLINK response/order. Only variants that keep target code
bytes are useful for a relocation-order hypothesis.

- baseline: op/run raw exact, relocation sets exact, order wrong;
- `-X`: same bytes and same wrong relocation order;
- `-d-`: same bytes and same wrong relocation order;
- `-y`: `dialog_op` remains raw exact but `dialog_run` no longer does;
- `-v`, `-G`, `-O-`, `-Z-`, `-k-`, 80186/286 modes, and tested combinations
  change code and/or relocation sets.

No tested TC86 option preserves both function byte slices while repairing the
ordered relocations.

## `TCC -B` is not the `dialog_run` answer

For a minimal run-only TU, TCC-generated assembly can be made self-contained by
removing header-only declarations that introduce empty `MAI_TEXT` and
`HUD_OVRL_TEXT` group members. Direct TC86 then still emits the same 383 code
bytes.

Compiling that same minimal C++ source through the extracted TASM 4.1 produces
identical 383-byte LEDATA but reverses FIXUPP ordering. The direct and
via-assembler object hashes are:

```text
direct TC86: ab93abd29ccd0d60a0085e866d07bb080724539972ca14878c0d1d6bbbc1e924
TCC->TASM41: 2b706fe23e1b58b0bdda6da8f5cb50debd4278959fc1c03b3f17e1731944f150
```

The TASM ordering is not the target ordering: it reverses the order *inside*
the two relevant fixup pairs as well as their group order. Replacing the normal
run object with this diagnostic object also changes group/frame fixup semantics
because the minimized object no longer carries the two empty MAIN_01 member
segments. It is therefore not an accepted reconstruction.

TCC's generated assembly for the normal multi-segment TU references
`MAIN_01 group DIALOG_TEXT,MAI_TEXT,HUD_OVRL_TEXT` but omits assembly
SEGDEF declarations for zero-length `MAI_TEXT` / `HUD_OVRL_TEXT`. Both TASM 4.1
and TASM32 5.0 reject that generated assembly. Source-level empty `#pragma
codeseg` switches and declaration-only anchors do not make TCC emit those empty
SEGDEFs. Compiler-generated assembly and OMF were **not** hand-edited to bypass
this limitation.

## `snd_load`: stronger compiler/assembler negatives

This section records the probe state when the reviewed middle gap was still
41 bytes. Later v8 natural-source recovery below promotes 37 of those bytes and
leaves only four blocked; the negative `89 C3` / DS-save observations here
remain applicable to those residual bytes.

### DOS TASM 4.1 still emits `8B D8`

A normal standalone TASM 4.1 `mov bx, ax` probe emits:

```text
8B D8 CB    ; MOV BX,AX / RETF
```

so the newly discovered DOS assembler does not recover target `89 C3`. This
agrees with the earlier TASM32 5.0 probes.

### PC-98 IDE Integrated Compiler 4.0 also emits `8B D8`

The original PC-98 `TC.EXE` in the same attested TC4J media is now a replayable
producer control rather than an assumption. `scripts/probe_tc4j_pc98_ide.py`
privately extracts `TCPC98.PAK` plus Borland's official `TCALC.PAK` sample and
batch-builds it under the pinned DOSBox-X `machine=pc98` profile. The IDE banner
says `Turbo C++ Version 4.0`, but generated OMF reports
`TC86 Borland C++ 4.02`. A natural `_BX = _AX` probe emits exactly:

```text
55 8B EC 8B D8 5D CB
```

not target `89 C3`. Private run `gptweb-producer-v9-002` has receipt SHA-256
`d917b6d0ecf26c75633d3ceb1b060372ffb5217b7ec16e3ab82fe21c3a0037d6`.
As a corroborating release-media check, all 13 C++ members extracted from
small-model `BIDSS.LIB` contain zero decoded register-register `89 /r` in CODE
LEDATA. IDE-versus-command-line producer switching therefore does not explain
the TH04 encoding and should not be repeated without materially new evidence.

### Scan only CODE SEGDEFs, not raw OMF bytes

An earlier raw-object search for `89 /r` is methodologically unsafe: OMF data,
comments, names, and non-code LEDATA can contain byte sequences that look like
x86 instructions. The corrected survey parses LNAMES + SEGDEF, keeps only
LEDATA whose segment class is `CODE`, decodes that payload with `ndisasm -b16`,
and excludes source trees containing `_asm`, `asm`, `__emit__`, or
`#pragma codestring`.

Across the current cold TC86 corpus, that corrected **clean C/C++ CODE** survey
finds **zero decoded register-register `MOV` instructions using opcode `89 /r`**.
In particular there is no clean compiler precedent for destination BX. This is
a corpus observation, not a theorem about every possible Turbo C++ source.

### `_BX` cannot be routed through an addressable C++ lvalue

A focused pure-C++ matrix tested whether Borland's pseudo-register could be
forced through a generic store-lvalue backend rather than the normal
register-destination path. The legal baseline remains:

```text
_BX = _AX;  ->  8B D8
```

Binding `_BX` to a local reference, passing it by reference (directly or through
a template), and using comma- or conditional-lvalue expressions are all rejected
by TC4J with `Must take address of a memory location` (plus the expected
reference type mismatch where applicable). Pseudo-registers are compiler
lvalues, but they are not addressable C++ objects. This closes the
reference/alias route to a hypothetical `89 /r` store encoding without using
inline assembly or byte emission.

The embedded TCC option help also describes `-O` specifically as `Optimize
jumps` and `-Z` as `Suppress register reloads`; no separate documented
register-MOV direction optimizer switch surfaced. Do not invent an `-O*`
peephole matrix without new tool evidence.

### `-Z` versus `-Z-` does not recover the final bytes

A dedicated v12 control closes the remaining register-reload option gap. In a
minimal official-TC4J probe, `#pragma option -Z` and `#pragma option -Z-` produce
identical instruction LEDATA: `_BX = _AX` is `8B D8` in both, while a
block-scoped `unsigned saved_ds = _DS` still lowers to
`MOV [BP-2],DS ... MOV DS,[BP-2]` rather than `PUSH DS ... POP DS`.

The real-function control is stricter. Starting from the latest isolated cold
source (including the accepted natural `MOV AX,[BP+6]` replacement), changing
only the first pragma from `-Z-` to `-Z` leaves the middle `MOV BX,AX` as
`8B D8`. It additionally changes two previously exact instructions at function
relative `+0x96` and `+0xAC` from `LES BX,[BX+8F8h]` to
`MOV BX,[BX+8F8h]`, so the target mismatch count rises from two bytes to four.
The private probe receipt is
`.analysis/reconstruction/probes/snd-load-zreload-v12/receipt.json`.


A similarly decoded survey found no clean TH04 C/C++ precedent for an isolated
mid-function `PUSH DS ... POP DS` save across arbitrary statements; apparent
raw-byte hits were largely non-code/data or interrupt-style full-register save
patterns. Keep the current `snd_load` gap nonexact rather than manufacturing the
sequence.


## `snd_load` v8: 37 middle bytes recovered naturally

The old 41-byte umbrella is now split into explicit non-overlapping byte owners.
Fresh two-cold replay accepts three maintained natural-source regions totaling
37 bytes, reducing the true `snd_load` residual to four bytes.

### Preventing `func` parameter promotion

Full-function TC4J probes explain the old inline `mov ax, func` comment.
Direct `_AX = func`, an explicit cast, and an inline identity helper all make
TC4J keep `func` in DI. The normal variants grow the function from 234 to 237
bytes and emit `8B C7` (`MOV AX,DI`). Rewriting the high-byte condition does not
help; it still promotes the parameter.

Taking the parameter address at the load site changes the allocator decision:

```cpp
_AX = *reinterpret_cast<snd_load_func_t near *>(&func);
```

The full object returns to 234 bytes, keeps the target prologue, and emits
`8B 46 06` exactly. `gptweb-sndload-func-load-001` verifies the three-byte slice
through two isolated complete builds. `source_mode=replace` is deliberately
fail-closed on the whole scaffold SHA plus old-span offset/size/SHA, so this
natural replacement does not make adjacent upstream inline assembly maintained
source.

### DS save/restore: broader negative evidence

A new segment-aware scan parses LNAMES/SEGDEF, restricts decoding to `CODE`
LEDATA, and filters translation units whose C/C++ implementation dependencies
contain `_asm`, `asm {}`, `#pragma codestring`, or `__emit__`. Among **239 clean
C/C++ objects**, 16 apparent `PUSH DS ... POP DS` pairs were found. The genuine
pairs are only full `__saveregs`/interrupt-style register-save prologues. The
TH01 `main_01` appearances use `PUSH DS` as far-pointer argument setup and then
hit compiler switch-table data when linearly decoded; they are not DS restore
precedents.

A focused type matrix also tests `unsigned`, `register unsigned`, `void __seg *`,
and `unsigned __seg *` saved-DS variables. Stack-backed forms emit
`MOV [BP-2],DS` / `MOV DS,[BP-2]`; the register form emits `MOV DX,DS` /
`MOV DS,DX`. None produces the target isolated `PUSH DS` / `POP DS` pair.
Finally, TC4J's own `DOS.H` defines `geninterrupt(i)` as `__int__(i)` with no
segment clobber declaration. Do not repeat generic segment-local variants unless
new compiler evidence surfaces.

The remaining `snd_load` bytes are therefore exactly `1E`, `89 C3`, and `1F`.

## Official TC4J `TDUMP 4.1` confirms FIXUPP semantics

The already-attested TC4J media contains `TDUTIL.PAK` with Borland's own
`TDUMP.EXE` (`Turbo Dump Version 4.1`). It is extracted only below ignored
`.analysis/` with the same-media `UNPAK.EXE`; the proprietary executable is not
checked into this repository. Private identities from this machine are:

```text
TDUTIL.PAK  e6bef8e7389fc0089273afc7e182fef4b62d55877ce9878ff3a0bd0d827d9fe3
TDUMP.EXE   d255173de8de3dbf77967bbc0fbda3603c199ba71022c0265d71053f7991b480
```

TDUMP exposes LNAMES/SEGDEF/GRPDEF, LEDATA, and FIXUPP in the compiler's native
terms. For the Pointer16 fixups relevant here, the DOS MZ segment relocation is
the *segment word* of the far pointer, i.e. LEDATA base + FIXUPP location + 2.
This mapping was first calibrated against the current `dialog.obj` and its known
linked relocation list before being used on historical objects.

### Pre-decomp ReC98 ASM is not the target producer oracle

ReC98 parent `e8a0b3ef4315dc82998b45ae384c85d0ddb44dd3` still contains `dialog_op`
and `dialog_run` in the monolithic `th04_main.asm`. The source was assembled in
ignored analysis space with the pinned TASM32 5.0. The resulting object preserves
the relevant target relocation *sets*, but TDUMP shows different FIXUPP order:

```text
dialog_run target:     d642 d617 d6df d6c0
historical TASM object: d642 d617 d6c0 d6df
```

`dialog_op` is likewise a different permutation of the same 26 sites. Therefore
the historical ReC98 ASM is useful archaeology, not evidence that the original
game used that producer/order. Do not substitute it for the ordered-relocation
Oracle.

### Exact-code wrappers do not reorder `dialog_run`

Three pure-C++ run-only variants wrap only `input_reset_sense`, only
`frame_delay`, or both in inline helpers. All three retain the exact same
383-byte LEDATA as the direct source. TDUMP nevertheless reports the same four
Pointer16 locations in all variants:

```text
candidate: 0x171 0x152 0x0D4 0x0A9
required:  0x0D4 0x0A9 0x171 0x152
```

So adding an inline helper boundary does not alter TC86's two high-level fixup
groups when code is held exact.

## `#pragma samecodeseg`: object frame hint, final-link bridge enabler

`samecodeseg` appears in TCC's own pragma keyword table. At the **TC86 object
layer**, the earlier observation remains correct: an external far call stays a
five-byte `CALL FAR` in LEDATA while the Pointer16 FIXUPP frame changes from
`TARGET` to the current group (`GI[...]`). This is why object-only probes looked
negative.

The missing layer is TLINK. Turbo Link 6.10's own help says `/f` means
`Inhibit optimizing far calls to near`; TH04's normal `main.@l` does not contain
`/f`. In a formal full TH04 rebuild with the normal `th04/bullet_u.cpp` wrapper,
natural `sparks_add_random(...)`, and local
`#pragma samecodeseg sparks_add_random`, TLINK resolves the callee in `MAIN_03`
and translates the five-byte far call to the same-length target sequence
`90 0E E8 85 73` (`NOP; PUSH CS; CALL near`). The segment relocation is removed.
The `BULLET_U_TEXT` contribution remains 0x565 bytes at its target location.

A `/P` code-segment packing relink without `samecodeseg` leaves the call as
`CALL FAR` with its relocation, so packing alone is not the answer. This is a
reusable warning: for Borland far-call reconstruction, inspect both OMF FIXUPP
and final MZ bytes before rejecting a source-level frame hint.
## Natural TC4J far-call bridge rule

Segment-aware CODE-corpus mining found genuine compiler-generated `PUSH CS;
CALL near` examples. Minimal controls isolate the required condition:

1. external far declaration only, even in the caller's code segment -> `CALL FAR`;
2. far callee **definition already visible earlier in the same TU and same
   logical code segment** -> `PUSH CS; CALL near`;
3. callee definition in another logical code segment of the same group ->
   `CALL FAR`.

This matches clean examples such as TH02 `key_delay()` calling the earlier
same-TU/same-SHARED `key_delay_sense()` definition, and the analogous TH05
`dialog_load()` overload pair. Same final TLINK selector is not sufficient;
compiler-time logical-segment knowledge matters.

Near/far function-pointer casts and constant pointer variants were also tested.
Near indirect calls do not acquire the required return-segment push, while far
pointer calls remain far. None yields the target bridge without low-level code.


### `alloc_text` and compiler-only controls

TC4J accepts `#pragma alloc_text(f)` for an external far function, but a minimal
control retains the same `CALL FAR` LEDATA/Pointer16 call shape as the baseline.
The current cold object corpus also contains no OMF `ALIAS` records, and TCC's
pragma keyword table exposes neither `alias` nor `weak`.

A separate compiler-only control with the far callee definition already visible
in the same TU and logical code segment naturally emits `PUSH CS; CALL near`
without a leading `NOP`. That observation remains useful for understanding TC86
codegen, but it does **not** describe the final TH04 solution: the target leading
`NOP` comes from TLINK preserving the original five-byte CALLF footprint during
far-to-near translation after `samecodeseg` changes the frame.

## `bullets_update`: full natural reconstruction

The former 17-byte low-level region is no longer a blocker. The maintained
natural call reproduces the first 12 argument bytes directly, and the
`samecodeseg`/TLINK mechanism above reproduces the final five-byte call form at
link time. The complete 0x36B reviewed extent is raw exact, including trailing
switch metadata/table, and is now owned by `src/main/bullet/update_body.inl`.

The full exact function is deliberately accepted only at the final-linked
artifact layer as well as OMF/layout layers. Object LEDATA alone would still show
`CALL FAR`, so treating that intermediate representation as the exact-binary
verdict would be a category error.
## Next useful experiments

The remaining work should focus on information not already falsified here:

1. recover a materially different original C/C++ control-flow/IR shape for the
   two dialog relocation groups, while requiring raw code equality before
   considering relocation order;
2. investigate whether another *legally available and independently attested*
   compiler producer is justified by target evidence before testing it;
3. treat the remaining four `snd_load` bytes as focused producer/source
   archaeology: target `89 C3` plus isolated `PUSH DS` / `POP DS`. Do not repeat
   `_BX = _AX`, parameter-promotion, TASM mode, `-B`, generic DS-save, or `__seg`
   local probes without new evidence.

Do not solve any of these with target-derived byte directives, `__emit__`,
inline assembly, hand-edited compiler assembly, or patched OMF records.

## v19: `dialog_run` producer and metadata-batching negatives

The pinned target MZ relocation table was re-read directly. Inside
`dialog_run`, target segment-relocation words occur at function-local
`0xD6, 0xAB, 0x173, 0x154`, corresponding to Pointer16 fixup starts
`0xD4, 0xA9, 0x171, 0x152`. Direct TC86 instead emits the same four sites in
`0x171, 0x152, 0xD4, 0xA9` order.

A same-media PC-98 `TC.EXE` integrated-compiler nodebug object keeps the exact
same 0x17F `DIALOG_TEXT` LEDATA as direct TCC, but Borland TDUMP still reports
Pointer16 order `171,152,D4,A9`. Thus PC-98 IDE producer switching preserves the
wrong cyclic rotation even when machine code is exact.

Additional exact-code batching probes are also negative: inserting `#line`
between the early and late call groups leaves both LEDATA and the complete
FIXUPP payload byte-identical; local `-y` or `-v` still produce one LEDATA and
one FIXUPP record while changing tail machine code. Reversing only the first
declaration order of four external far functions keeps call LEDATA identical and
FIXUPP locations `13,0E,09,04`; only EXTDEF target indices change.

Do not retry PC-98 IDE producer switching, `#line`, local debug/line-info
pragmas, or external declaration ordering for this relocation-order blocker
without materially new compiler evidence.

## v20: midboss bridge exposes a false reconstructed segment boundary

A TC4J control with a callee definition in `SEG_A`, caller in `SEG_B`, and
`#pragma samecodeseg callee` naturally emits `PUSH CS; CALL near`, but applying
that shape to the real separated MIDBOSS/MB_DFT reconstruction changes symbol
frame binding and links the call to the wrong flat function. Opcode shape alone
is therefore not sufficient.

The accepted explanation comes from target ownership instead: reconstructed
`MIDBOSS_TEXT` (0x5A), `HUD_HP_TEXT` (0x58), and `MB_DFT_TEXT` (0x119) are
perfectly contiguous, and `midboss_defeat_update` calls the earlier
`midboss_reset` with the four-byte near form. Emitting all six functions in flat
target order as one natural-C++ TU/segment makes the complete 0x1CB region exact
with an ordinary `midboss_reset()` call and leaves the following segment start
unchanged. Similar cross-boundary near calls should trigger a false-boundary
check before any attempt to coerce the instruction encoding.


## v21: `MAIN_035` / `BOSS_TEXT` producer-boundary recovery

`boss_defeat_update` initially looked like a second four-byte near-call blocker:
target `PUSH CS; CALL near` reached `bb_boss_free` in reconstructed
`MAIN_035_TEXT`, while the caller lived in `BOSS_TEXT`. Samecodeseg-only controls
again proved unsafe: they can emit the desired opcode shape while rebinding the
callee symbol to the caller segment.

Target-flat continuity instead exposes another false boundary. The 0x677 suffix
starting at `boss_reset` and the following 0x33F BOSS code compile naturally as
one TC4J TU of exactly 0x9B6 bytes. Ordinary `bb_boss_free()` then emits the
target four-byte bridge. The final link reproduces the complete 2,486-byte slice
and 60 ordered relocation entries exactly while old `BOSS_TEXT` becomes empty.

Two codegen details are reusable. First, MAIN_01 near callback declarations must
first be seen while `MAI_TEXT/main_01` is active or TC86 emits near-pointer fixups
framed to MAIN_03 and TLINK overflows. Second, `#pragma samecodeseg
explosions_small_reset` is safe here because the callee's true definition/public
address remains fixed in its real segment and TLINK performs the already-accepted
far-to-near bridge optimization; final public addresses and displacements are
still mandatory acceptance evidence.

## v22: incremental `MAIN_034` prefix migration without byte-emitting scaffolds

`chasecrosses_add(unsigned char,unsigned char)` at `13A9:65F7` provides a
positive target-driven control for code that ReC98 had not reconstructed. A
minimal C++ implementation based on target raw behavior and the checked
`chasecross_t` layout produces exactly 74 TC86 code bytes and links to the
complete target slice.

The hard part was preserving global code-segment order while replacing the
prefix of `MAIN_034_TEXT`:

1. simply linking `chase.obj` before `main.obj` failed with TLINK
   `Group MAIN_03 exceeds 64K`;
2. a zero-code anchor declaring MAIN_03 alone linked, but moved MAIN_03 before
   MAIN_01 and therefore changed the program layout;
3. a zero-code anchor declaring the original MAIN_01 code segments, `SHARED`,
   and MAIN_03 code segments/groups in target order succeeded. Its OMF has 50
   SEGDEF, 2 GRPDEF, and zero LEDATA. With link order `anchor -> chase -> main`,
   all 54 program CODE segment `(name,start,length)` tuples match the baseline,
   `chase.cpp` occupies exactly `13A9:65F7 + 0x4A`, and residual `main.asm`
   begins at `13A9:6641`.

This anchor is layout metadata, not authored source and not a byte-reproduction
shortcut. The replay driver checks that every configured zero-code object has
at least one SEGDEF, no LEDATA/LEDATA32, valid OMF framing, and deterministic
normalized identity across both cold materializations. The same mechanism can
support incremental recovery of other functions still embedded in large
`MAIN_033_TEXT`, `MAIN_034_TEXT`, and `MAIN_036_TEXT` regions without forcing an
all-at-once decompilation of those segments.
