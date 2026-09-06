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

Do not repeat these four boundary placements as proposed fixes.

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

The 41-byte reviewed gap remains nonexact. Two newer observations strengthen
rather than weaken the existing `89 C3` / DS-save conclusions.

### DOS TASM 4.1 still emits `8B D8`

A normal standalone TASM 4.1 `mov bx, ax` probe emits:

```text
8B D8 CB    ; MOV BX,AX / RETF
```

so the newly discovered DOS assembler does not recover target `89 C3`. This
agrees with the earlier TASM32 5.0 probes.

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

A similarly decoded survey found no clean TH04 C/C++ precedent for an isolated
mid-function `PUSH DS ... POP DS` save across arbitrary statements; apparent
raw-byte hits were largely non-code/data or interrupt-style full-register save
patterns. Keep the current `snd_load` gap nonexact rather than manufacturing the
sequence.

## Next useful experiments

The remaining work should focus on information not already falsified here:

1. recover a materially different original C/C++ control-flow/IR shape for the
   two dialog relocation groups, while requiring raw code equality before
   considering relocation order;
2. investigate whether another *legally available and independently attested*
   compiler producer is justified by target evidence before testing it;
3. continue `snd_load` source archaeology around its DOS handle and segment
   preservation rather than repeating `_BX = _AX`, TASM mode, `-B`, or generic
   DS-save probes.

Do not solve any of these with target-derived byte directives, `__emit__`,
inline assembly, hand-edited compiler assembly, or patched OMF records.
