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

## `#pragma samecodeseg`: frame hint, not call lowering

`samecodeseg` appears in TCC's own pragma keyword table. Minimal syntax probes
show that bare and identifier-list forms are accepted. TDUMP reveals the actual
binary effect for an external far call: the LEDATA remains a five-byte `CALL
FAR`, while the Pointer16 FIXUPP **frame** changes from `TARGET` to the current
group (`GI[...]`). The pragma tells the linker which segment frame to use; it
does not rewrite a far call to `PUSH CS; CALL near`.

A TH04-specific probe with `#pragma samecodeseg sparks_add_random` behaves the
same way: the fixup frame becomes `MAIN_03`, but `bullets_update` still contains
`CALL FAR`. This pragma must therefore not be proposed again as a call-bridge
solution. It is also invalid as a `dialog_run` fix, because the four relevant
callees live in SHARED/master.lib selectors rather than `MAIN_01`.

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


### `alloc_text` and the closest natural bridge still miss target `NOP`

TC4J accepts `#pragma alloc_text(f)` for an external far function, but a minimal
control retains the same `CALL FAR` LEDATA/Pointer16 call shape as the baseline.
The current cold object corpus also contains no OMF `ALIAS` records, and TCC's
pragma keyword table exposes neither `alias` nor `weak`, so there is no observed
linkage alias path hiding behind this pragma.

A separate minimal control makes the far callee definition visible earlier in
the same translation unit and same logical code segment. That is the strongest
normal C++ condition found for Borland's bridge lowering, and TC4J emits
`PUSH CS; CALL near` naturally. It still emits **no leading `NOP`**. Therefore
the TH04 target's full five-byte `NOP; PUSH CS; CALL near` form remains outside
the observed natural-C++ codegen surface; do not synthesize the missing byte or
call with inline assembly/codestring/byte directives.

## `bullets_update`: natural source narrows the gap to call form

The target 17-byte region is:

```text
FF 74 02             PUSH [SI+2]
FF 74 04             PUSH [SI+4]
66 68 02 00 20 00    PUSH dword 00200002h
90                   NOP
0E                   PUSH CS
E8 ...               CALL near sparks_add_random
```

Replacing only the old low-level block with natural
`sparks_add_random(bullet->pos.cur.x, bullet->pos.cur.y, to_sp(2.0f), 2)` keeps
the parameter setup and surrounding code but produces `CALL FAR`. A
first-declaration `SPARK_A_TEXT/MAIN_03` probe, `samecodeseg`, near/far pointer
casts, and constant function pointers do not change that conclusion. The
function stays nonexact; assembly stitching or target byte emission is not used.

Its *boundary*, however, is now independently reviewed. Raw code decodes from
`0x2C8C8` through `RETF` at `0x2CC27`; byte `0x2CC28` is switch metadata and the
five near offsets at `0x2CC29` resolve to decoded instructions at `0x2CB71`,
`0x2CB78` (three entries), and `0x2CB7F`. The next TLINK public is `0x2CC33`, so
the complete reviewed extent is 0x36B bytes. Boundary review does not waive the
five-byte nonexact call form; the preceding 12 argument bytes are now cold-exact from maintained natural C++.

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
