# TH04 `MAIN_033_TEXT` Kurumi spawn-ray cohort packet (v124)

## Scope and target identity

v124 reconstructs the two adjacent Kurumi spawn-ray functions that own the
six-record state consumed by exact `kurumi_fg_render()`. The active artifact is
`th04-main` / `MAIN.EXE`; the private target remains operator input with
`candidate-local-attested` canonicality and SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
No target bytes were patched, copied into product source, or used as padding.

The cohort is:

- `kurumi_spawnrays_add(int,unsigned char)`:
  - TLINK `13A9:4F84`;
  - load `0x18A14..0x18A78`;
  - Ghidra linear `0x28A14..0x28A78`;
  - file `0x1A214..0x1A278`;
  - size `0x65` / 101 bytes;
  - target SHA-256
    `59f51c6db0ef89946794e5eb04d0620f049c0e77830f326d3a7b043316adb9a6`.
- `kurumi_spawnrays_update()` (target TASM label `kurumi_18A79`):
  - begins at exact owner offset `0x65`;
  - load `0x18A79..0x18B67`;
  - Ghidra linear `0x28A79..0x28B67`;
  - file `0x1A279..0x1A367`;
  - size `0xEF` / 239 bytes;
  - target SHA-256
    `61b1c06f95299c7fa544a664b3126d84e65fab5b1cf9d15da247285875fcad27`.

The combined 0x154 / 340-byte target slice has SHA-256
`790cac5fa8ebfb56fc6f7db7849aa8658690d2d2d6563528324f3cbd746d1d3d`.
Fresh attested Ghidra constructs both functions as complete contiguous bodies,
and pinned TASM has the same adjacent boundaries. Both functions are called by
the same six Kurumi phase helpers at `0x28BE6`, `0x28C76`, `0x28D04`,
`0x28E43`, `0x28EE7`, and `0x28F8B`.

The allocator is Pascal-near and ends in `RET 4`; it selects a free 0x1A-byte
spawn-ray record, initializes target/origin from the boss position, calls
`vector2()`, and plays sound effect 5. The updater walks all six records,
advances growing/shrinking endpoints, converts an escaped growing ray into
three speed-up bullets plus a circle, and returns true in AL once all records
are free.

The combined extent contains four MZ relocation sites. Focused and aggregate
receipts record the same ordered target/candidate overlap at load addresses
`0x18B19`, `0x18B07`, `0x18A66`, and `0x18A5F`.

## Natural-source compiler loop

The maintained source is `src/main/boss/kurumi_spawnrays.cpp`, SHA-256
`07ac85a68574a7d6b7f6a4411f38d284a707e6565182e8c543283b55d30cab9a`.
It defines the already target-proved six-record 0x1A-byte layout locally and
implements both functions in ordinary C++.

The first probe already emitted exactly 340 bytes with two public offsets at
`0x0000` and `0x0065`, so function ownership and producer order were correct.
The updater still differed in local ordering and branch shape. Three narrow
same-toolchain source corrections closed the instruction stream:

1. put `free_count = 0` in the `for` initializer after SI/DI setup, matching the
   target local initialization order;
2. express the GROW and SHRINK bounds as positive in-bounds branches so TC4J
   emits the target update-first control flow instead of the logically
   equivalent transition-first layout;
3. use an ordinary `bool` function with explicit `if (...) return true; return
   false;`, matching same-game exact boolean source and the target AL-only
   return sequence.

The final bounded object is 340 bytes with the exact two-function instruction
and control-flow skeleton. Pre-link differences are external/data/call address
words only. The compiler probe's dependency-normalized OMF SHA-256 is
`075dfdc65d573819c686dd8367fedeb569f5b80d681a683e02d61c23799908a4`;
the formal cold replay object below has normalized SHA-256
`432885c60271e070ac3c7bc7db73c87b83c00e01aea8ba1d12f8e381ab149ec6`.
The maintained source contains no inline assembly, target-derived byte arrays,
`#pragma codestring`, fake return, inert padding, object patching, or ABI lie.

## Physical producer seam

The cohort does not sit at an edge of the original assembler contribution.
Before v124, `MAIN_033_TEXT` is physically linked as:

```text
13A9:459F  th04/m5pre.cpp     008C
13A9:462B  th04/m5tr0.cpp     006F
13A9:469A  th04_main.asm      1D92
```

The target cohort starts at `13A9:4F84`, inside the monolithic
`th04_main.asm` contribution. Appending a C++ object before or after that
object therefore cannot reproduce target layout.

v124 reuses the repository's existing hash-bound replay-only scaffold extraction
mechanism rather than copying residual assembler into product source. The
physical layout becomes:

```text
MAIN_033_TEXT prefix from transformed th04_main.asm
th04/kurrays.cpp              13A9:4F84, size 0154
replay-only th04/m33kseam.asm 13A9:50D8 through MAIN_033_TEXT end
```

The suffix extraction is bound to pinned ReC98 scaffold SHA-256
`c872e7c1d94d571fc62e6b14e0960b89ef882f46df60a1d8467d117b9e0e549b`.
It extracts the original `kurumi_18B68 proc near` through
`main_033_TEXT ends` span, 51,703 bytes of source text with SHA-256
`fbbcf785413222822a65eae4397a0700d803371e6446a7b4bf3130dca76ad4f5`.
Two symbol-only adaptations are receipted:

- nine `kurumi_18A79` references become
  `@kurumi_spawnrays_update$qv`;
- two `_bullet_zap_active` references become `_bullet_zap`, the already-public
  alias for the same byte of storage.

The adapted extracted span SHA-256 is
`fdfba15e55e65d6e549b571d2144644d788ffe1e348353b03be25868c790f014`.
The checked-in wrapper
`config/replay/th04_main033_kurumi_suffix.asm.in` contains only declarations,
segment/group structure, constants/types, and one `{{EXTRACTED_SPAN}}` token;
it contains no target-derived residual body. Its SHA-256 is
`c6e6fd9a02fc2ba028a9b6d96c137dde78ff9714cf24a0379ce9ecc254bc5f1a`.

The v124 source transform is separately bound to the v123-transformed scaffold
SHA-256
`989a82a4da82441d54a3e3f03ac5bf327539b6db192896887d792e15c04a9647`.
It removes the original cohort/suffix contribution from that transformed
scaffold, exposes the unchanged `byte_259F0`/`byte_259F1` BSS labels as public
without moving their storage, and transfers public ownership of the later
Kurumi/Orange FAR update dispatchers from the retained prefix object to the
suffix object. The resulting expected transformed scaffold SHA-256 is
`a71fcc828a6e1e6113cd768acb30a03ebf32f8feb563fae734f8accc0d56c0ec`.

The suffix is replay plumbing only. It receives zero authored-source, byte, or
function exactness credit.

## Fail-closed seam debugging

Three focused runs failed before the final passing run, and each failure was
inspected before retrying:

- `gptweb-v124-kurumi-spawnrays-focused-001`: after extracting the suffix, the
  retained prefix still claimed the later Kurumi/Orange FAR update symbols as
  `PUBLIC`. Their definitions lived in the suffix object. v124 moves that
  public ownership explicitly: prefix `EXTRN :far`, suffix `PUBLIC`.
- `...-focused-002`: all relevant objects compiled/assembled, but Tup rejected
  `th04_main.asm` for reading generated `pelletbt.asp` without the original
  declared `extra_inputs` dependency. The v124 build replacement now preserves
  the complete inherited pellet/sparks/pelletbt/pointnum input set.
- `...-focused-003`: TLINK reached the seam and exposed exact OMF naming and one
  duplicate absolute public. The wrapper had guessed source-case spellings for
  several existing C++ publics; their actual names were taken directly from
  accepted OMF PUBDEF records. `ReC98.inc` also publishes `_address_0` when
  `BINARY` is defined; the extracted suffix and its includes do not need
  `BINARY`, so the wrapper omits it rather than renaming or duplicating the
  symbol.

After these fixes, the seam independently assembles as valid TASM OMF and the
full link passes. These failures are build/layout evidence, not target or source
mismatches.

## Focused and aggregate replay

Focused two-cold replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-kurumi-spawnrays-v124 \
  --run-id gptweb-v124-kurumi-spawnrays-focused-004
```

passes all 96 dependency-closure owners in both isolated builds. The new unit
is raw/map/relocation exact at
`13A9:4F84 0154 ... M=th04/kurrays.cpp`. The natural object is valid TC86
Borland C++ OMF with A/B normalized SHA-256
`432885c60271e070ac3c7bc7db73c87b83c00e01aea8ba1d12f8e381ab149ec6`.
The auxiliary TASM seam is valid and has stable normalized SHA-256
`7660e494b5f34bfb348e7ef266b5f924d46638759ffbaf9a76318e8a6c26dfe4`.
Focused A/B candidate MAIN SHA-256 is
`12ae7dd33bf49505b0198c44f79bee300de8b25296e2e42ee2e4342adfb1cd79`.

Required aggregate replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --run-id gptweb-v124-kurumi-spawnrays-aggregate-001
```

passes all 160 default owners twice, with no previous accepted-owner regression.
Both candidate MAIN executables have SHA-256
`1ccab550d98514aa0f6c0b3315fa775bb2885e7d92e9d6fab71dff0b826e92c8`.
The replay manifest SHA-256 is
`12269be5b741fa5a17c31718198cd4c6112b991bf7d2746ad2ef8861b376cd60`.

## Function review and continuation

Fresh target-bound Ghidra metadata plus the v124 aggregate map admit both
functions through the ordinary complete-contiguous-Ghidra/TLINK/exact-owner
gate. The function review reports:

- reviewed authored functions: 280;
- exact functions: 278 (99.285714%);
- automatic exact acceptances: 136;
- manual exact acceptances: 142;
- strict provisional rejections: 0;
- reviewed nonexact functions: 2.

The private report SHA-256 is
`f672ad118535a3c59a49be06ed39435458090715e115c53d64d73a51e9113476`.

The current reviewed C/C++ byte total is 42,569 / 42,600 exact
(99.927230%). The only 31 reviewed nonexact bytes remain the two older blocked
functions.

The `shot_velocity_set()` / `sub_11DE6` source-origin seam is unchanged. Fresh
v124 analysis again confirms the 44-byte FAR threshold scanner and provides no
new source-level DS-`LOOP` hypothesis.

The first target-first continuation is one of the six Kurumi phase callers,
`kurumi_18BE6`. Existing ledger state correctly remains provisional: fresh
Ghidra spans `0x28BE6..0x28C75` (0x90 bytes) but includes only 0x6F / 111 body
addresses. Pinned TASM keeps the near PROC open through `RET` at `0x28C75`,
with the next PROC at `0x28C76`. The full physical target extent is load
`0x18BE6..0x18C75`, file `0x1A3E6..0x1A475`, size 0x90 / 144 bytes, SHA-256
`6e66a95d2a225303b10deaebcf1760ba774e99daa8864d592137594fab85341a`,
with MZ relocations at load `0x18C0F` and `0x18C1B`. Reconcile the sparse
Ghidra body against the full TASM/raw control flow before attempting source.
