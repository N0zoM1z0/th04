# TH04 BOSS_BG MAIN_01 physical producer (v148)

## Result

v148 recovers the remaining target-derived BOSS_BG prefix as maintained natural
C++ and closes the complete BOSS_BG physical producer together with the already
exact v113 `yuuka6_bg_render()` owner.

The new logical owner is:

- artifact: `th04-main / MAIN.EXE`;
- segment: `BOSS_BG_TEXT`;
- map: `0AAF:768E..7DC8`;
- load: `0x1217E..0x128B8`;
- target file: `0x1397E..0x140B8`;
- size: `0x73B / 1851` bytes;
- target slice SHA-256:
  `866296cce626be8776ed73fa433fe768631c8e9d0e10ffa65d90ef9f7410ff69`.

The adjacent v113 `yuuka6_bg_render()` remains a separate `0xC0` byte-credit
owner beginning at load `0x128B9`. During v148 replay both logical owners are
emitted by one natural TC4J object, `th04/b6all.cpp`, whose complete BOSS_BG
contribution is:

```text
0AAF:768E 07FB C=CODE S=BOSS_BG_TEXT G=MAIN_01 M=th04/b6all.cpp ACBP=28
```

The private target remains read-only and only `candidate-local-attested`.

## Boundary corrections

Target-first review rejects several Ghidra extents rather than inheriting them:

- `orange_bg_render()` at load `0x1217E` has no Ghidra function entry; pinned
  TASM and gap-free raw decode close the complete `0x6D` near function.
- `kurumi_bg_render()` at `0x121EB` is the complete contiguous `0x5C` body.
- the Elly invalidation helper at `0x12247` is `0x28` bytes, not Ghidra's
  `0x1C` body.
- `elly_bg_render()` at `0x1226F` is the complete `0x68` body.
- `reimu_marisa_bg_render()` at `0x122D7` is `0x8D` bytes, not Ghidra's
  four-byte body.
- `yuuka5_bg_render()` at `0x12364` is the complete `0x8D` body.
- the two `bg_shape_t` clipping helpers at `0x123F1` and `0x12427` are
  complete `0x36` and `0x3A` Pascal-near functions.
- the former `sub_12461` is a complete physical `0x458` owner at load
  `0x12461..0x128B8`. Ghidra cross-links it over fifteen ranges with a gross
  `0x20000..0x246FF` image span. Target raw decode instead closes `0x41B`
  executable bytes through `RET` at load `0x1287B`, followed by one zero
  compiler metadata byte, a 17-word switch table, and a 13-word switch table.
  All thirty table words target instruction starts inside the function. The
  exact v113 renderer calls the update entry from load `0x12972`, and the next
  exact BOSS_BG owner begins at load `0x128B9`.

A fresh v148 recovery query against the re-attested Ghidra database reproduced
these diagnostic failures: no function at image `0x2217E`, only 28 Ghidra body
bytes at `0x22247`, only four bytes at `0x222D7`, and the same cross-linked
`0x20000..0x246FF` span for image `0x22461`. These are provisional target
observations and receive no independent exactness credit.

## Natural source and producer ownership

`src/main/boss/boss_bg_main01.cpp` contains the nine newly reviewed functions.
It then defines `TH04_BOSS_BG_MAIN01_COMBINED` and includes the existing v113
logical source as `th04/y6bg.cpp`. `src/main/boss/yuuka6_bg_render.cpp` only
moves its standalone preamble behind that combined-mode guard; its function body
remains the single maintained source of truth.

This arrangement preserves non-overlapping byte-credit owners while recovering
the compiler/linker's larger physical translation-unit behavior. It does not
copy ReC98 source wholesale and does not create a second copy of the v113
function body.

The final maintained source SHA-256 values are:

- `src/main/boss/boss_bg_main01.cpp`:
  `ede7cb9ebb0796d0a7fc896f2bc87e51c33a6d9fd6c51fb4994b82109d01dafe`;
- `src/main/boss/yuuka6_bg_render.cpp`:
  `41c9adb23a611f325e9f8cfebd29c8564981e135c71b575ced7887987cbd228d`.

No inline assembly, `#pragma codestring`, target-derived byte array, copied
target bytes, inert padding, fake return, object patch, target patch, or ABI lie
is used.

## OMF, layout, and relocations

The final A/B `b6all.obj` raw SHA-256 is
`fd514140713431cb8f9f29d2c8f7d4b12cb14286d7c574fcf22ec13869bec83f`;
its dependency-timestamp-normalized SHA-256 is
`847d6f99ada5789f6e16d63eb8a0a4c8dcfcbf229fe1eaf730f6b78ffbc3b851`.
It is a valid single TC86 Borland C++ 4.02 OMF module with two CODE LEDATA and
two FIXUPP records. The new logical owner reproduces all five ordered target MZ
relocations; the adjacent v113 owner also remains raw/map/relocation exact in the
same object.

## Cold replay receipts

Current-source focused replay:

- run `gptweb-v148-boss-bg-focused-candidate-001`;
- 89-unit dependency closure;
- receipt SHA-256
  `aa16b6abe1cc08f6f1a60a50c0ee2c2ca20c0fcaa492f3adcda472d442034388`;
- two isolated cold builds; `failures=[]`;
- both the new `0x73B` owner and v113 `0xC0` owner pass raw bytes, map,
  ordered relocations, OMF, and determinism.

Candidate-state aggregate replay:

- run `gptweb-v148-boss-bg-aggregate-candidate-001`;
- all 182 default exact owners;
- receipt SHA-256
  `a8ee7a5db6c3044a8bc5fac60cd0017136081d07682105ad6b5969add804e34b`;
- two isolated cold builds; `failures=[]`.

Post-promotion aggregate replay:

- run `gptweb-v148-boss-bg-aggregate-final-001`;
- all 182 default exact owners;
- receipt SHA-256
  `e7e5e507b89383be385c6c3a3f008fcab997f365dc9cda90abb91cde24006656`;
- two isolated cold builds; `failures=[]`;
- both candidate MAIN images have SHA-256
  `781e1b99f94476f7dce5fa16b340f2c830a43e8ff9945bb373d8a0d8c3e41d38`.

Two earlier v148 focused runs remain negative evidence. They bind older source
hashes and fail broadly because the initial producer composition/layout was not
yet target-correct. They are not target rejections of the final maintained
source and are not reused for exactness.

## Accounting and verification planes

v148 adds `0x73B / 1851` reviewed authored bytes and nine reviewed functions,
all exact under the complete repository-native promotion chain. The live MAIN
ledger becomes 51,659 / 51,663 exact reviewed authored bytes (99.992258%) and
321 / 322 exact reviewed authored functions (99.689441%). The only reviewed
blocked function remains the four-byte `snd_load` remainder. MAIN still has 221
unreviewed authored candidates, so this denominator expansion is not a campaign
completion signal.

The focused and aggregate receipts establish function/extent exactness for the
declared owners only. They do not establish standalone TH04 production-source
or link closure, runtime-storage identity, a runtime scenario, whole-image
exactness, independently pristine target provenance, or Factory Truth Kernel
acceptance.
