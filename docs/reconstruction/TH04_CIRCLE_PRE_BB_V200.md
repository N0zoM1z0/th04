# TH04 pre-.BB CIRCLE producer review (v200)

## Scope

v200 reviews the complete `CIRCLE_TEXT` seam immediately before the v198 `.BB`
mask producer in the locally attested TH04 `MAIN.EXE` target. The target-backed
window is `0AAF:1378..1425`, load `0xBE68..0xBF15`, file
`0xD668..0xD715`, size `0xAE / 174`, SHA-256
`fdcbf9c660c6483217e35bda7f0bde5204fb233075a5bcb7e3d9681e9b981a99`.
There are no overlapping ordered MZ relocations.

Target-first decoding and the actual cold scaffold split the window into three
source-distinct producers:

- `SHOT_LASER_PUT_RAW`: logical body `0xBE68..0xBECA` (`0x63`) plus its
  source-owned `EVEN` NOP at `0xBECB`; physical owner size `0x64`, SHA-256
  `fdee9c414a13fcd8799dedc68aafa34c724d3cd0e6b04e0e449393dde35e2268`;
- `elly_backdrop_colorfill()`: load `0xBECC..0xBED9`, size `0x0E`, target
  SHA-256 `6e1968ec26ed949a9659f9f56232985154f34111f607b4a0b8d51debb145688b`;
- the `mai_yuki_backdrop_colorfill()` / `reimu_marisa_backdrop_colorfill()`
  alias: logical body `0xBEDA..0xBF14` (`0x3B`) plus its source-owned `EVEN`
  NOP at `0xBF15`; physical owner size `0x3C`, SHA-256
  `c06ec5f14ab8d52d565e7167771006685df325631700c3d1eb328420770b930d`.

The exact v198 `.BB` mask owner starts at the next byte, load `0xBF16`.
Fresh target-bound Ghidra constructs none of the three v200 entries as
functions. Ghidra therefore receives zero boundary or exactness credit here.
The reviewed extents come from raw control flow, TASM `PROC`/include seams,
TLINK publics, alignment ownership, adjacency, and exact replay.

## Shot laser: original-style symbolic assembly

The maintained producer is `src/main/player/shot_laser.asm`, SHA-256
`d5c694ee23d108b511be2c13e577b278940b0edc3f2a86004841e46f9f503f68`.
It preserves the target's hidden AX/DX/BX/SI input ABI, direct ES VRAM writes,
`ROR`, `STOSB`/`STOSW`, `LOOP`, vertical-wrap state, and source-owned final
alignment NOP. It uses symbolic instructions and constants only; there is no
byte array, codestring, inline C/C++ assembly, fake return, target patching, or
inert padding.

A bounded natural TC86 Borland C++ 4.02 mechanism probe tests the same no-argument
hidden-register API with `_rotr`, typed `__es` writes, and vertical wrap. The
probe source SHA-256 is
`27278a91c831a816dc7f44ba01041c14a0eec52f11776f81b70ed81e3851b7fc`.
Its valid OMF is SHA-256
`74f6a491d2211d231c9acbc28725a78dd49fee9755dbe7c5e7c587796ce57f63`.
TC4J emits 204 CODE bytes versus the 99-byte target body and introduces a BP
frame, local spills, a runtime-library FAR rotate call, typed ES stores, and
`DEC`/test/`JNZ` loops rather than the target's frameless register/string-loop
architecture. The emitted CODE SHA-256 is
`24075c0c3dee02ad68f52242abe0095a468a0e12b85af1b2c15b57e0ac0f2279`.
This is bounded negative mechanism evidence, not proof by itself of historical
source form.

Independent TH05 raw-target evidence strengthens the origin classification. A
unique 16-byte target prefix locates a 99-byte homolog at TH05 load `0xDDF4`;
97/99 bytes are identical to TH04 and only body offsets `0x10..0x11`, the linked
`SHOT_LASER_DOTS` data word, differ. This location is deliberately described as
a raw-target homolog: the current TH05 candidate MAP is not whole-image exact
and is not used to assert a target public address. ReC98's candidate source was
introduced by commit `a417b016` with subject
`[Reverse-engineering] [th04] Player shots: Option laser blitting`, which is
source-lineage evidence only. Together these facts support an
irreducible/original-style ASM classification without claiming recovery of the
historical source text.

## Elly backdrop: maintainable natural C++, linked exactness withheld

The maintained candidate is `src/main/boss/elly_backdrop.cpp`, SHA-256
`f31dad909a71fc89ecf3db7da549a1cbfc32efda53dc038a7aeb115583570159`.
It follows the same ordinary pseudo-register shape already proven exact for
other TH04 backdrop callbacks: set `_ES` and `_DI`, then call
`grcg_fill_playfield_rows()`.

A standalone production-profile TC4J probe compiles this natural source into a
valid 412-byte OMF, SHA-256
`35b3fc247c6d7fa20afe480f0bff5ccd142aaac7d86a59a1d3ef6c8a7d10818b`.
The generated `CIRCLE_TEXT` public is exactly 14 CODE bytes:

`57 B8 80 AA 8E C0 BF B4 4F E8 00 00 5F C3`

The target is:

`57 B8 80 AA 8E C0 BF B4 4F E8 90 61 5F C3`

All 12 fixed bytes are identical. The only two pre-link differences are the
ordinary `CALL rel16` field, and the object contains one FIXUPP record covering
that call. Generated CODE SHA-256 is
`94fa6b7918e003447ae4a7842c049ed44d6c62925000a4c90e37ba781da25f16`.
This establishes strong natural-source codegen evidence, but not linked
exactness.

v200 intentionally leaves Elly source-present and blocked. The accepted v198 and
v199 CIRCLE owners still compare contained extents of the monolithic
`obj/th04/main.obj`. Physically extracting this internal 14-byte C++ function
would require a reviewed producer split that preserves those already accepted
ownership bindings. v200 does not silently migrate them and does not link the
old scaffold assembly while claiming natural-C++ exactness. Thus Elly adds 14
reviewed source-present bytes to the honest C/C++ denominator and receives zero
exact numerator credit.

## 64/56/256/256 backdrop fill: original-style symbolic assembly

The maintained producer is `src/main/hardware/fillm64_56_256_256.asm`, SHA-256
`aedc820bea26eca909c805ff3a22027210666ae7a804e821790333bbb666bcab`.
The target relies on GRCG TDW semantics while reusing EAX, `STOSD`, `LOOP`, and
flags from `SUB DI,...`; its physical owner includes the final `EVEN` NOP at
`0xBF15`.

A defined natural TC4J probe using `_EAX` and typed `__es` dword stores emits 81
CODE bytes versus the 59-byte target body. TC4J expands `STOSD` into explicit
`MOV ES:[DI],EAX` plus `ADD DI,4`, expands `LOOP` into
`DEC`/`MOV`/`OR`/`JNZ`, and inserts `OR DI,DI` instead of directly reusing
`SUB` flags. Probe CODE SHA-256 is
`77bc755727b66535199182a604eb469cf515306ad8f0d7b9840910711efef60a`.

The independent TH05 raw target contains the complete 59-byte body byte-for-byte
at load `0xBF24`. This is a raw search result rather than a claim derived from
the nonexact candidate MAP. ReC98 introduced the shared candidate in commit
`789c910c`, `[Reverse-engineering] [th04/th05] Playfield fill-around function
names`. Combined with the compiler-mechanism negative, this supports maintained
original-style symbolic assembly without treating ReC98 as authority.

## Other TH04 artifacts

OP, MAINE, and ZUN remain independent artifacts. Their previously attested
unpacked payload SHA-256 values are respectively:

- OP: `13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`;
- MAINE: `7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c`;
- ZUN: `baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.

A bounded exact-run scan finds shot runs of only 6/6/3 bytes, Elly 2/2/2, and
fill 3/3/2 across OP/MAINE/ZUN. This is negative routing evidence only and
transfers no MAIN source, boundary, or exactness credit.

## Exact replay

Focused replay `gptweb-v200-circle-prebb-focused-candidate-001` selects 137
owners twice and passes with `failures=[]`; receipt SHA-256 is
`00474852b3bc8ca771f426b3e00c96ce14b0cbaae264c3377e3d07b4dc9ac921`.
Both v200 ASM owners are `raw=True`, `map=True`, `relocs=True`. Focused A/B
`th04_main.obj` dependency-normalized SHA-256 is
`489004aa4f13c15b6527d2dd2bc4b1c902f5b506aaa3a84758dd85aab40c9348`.

Candidate aggregate `gptweb-v200-circle-prebb-aggregate-candidate-001` selects
241 default owners twice and passes; receipt SHA-256 is
`fc8054e0a4a0eaf007b0c72cc56ef171b5c32edd6d6cf13f885afb7b8a134933`.
Post-promotion aggregate `gptweb-v200-circle-prebb-aggregate-final-001` passes
the same 241 tracked defaults twice; receipt SHA-256 is
`ae07c088f3e354246b105080f755e6dba58f99a96bca8d54e42fdaa011193457`.
All three replays bind manifest SHA-256
`3b618394cc61469ae2ea20ff49aa012f157c152de01f508b2c110ba023bbe73b`.

The aggregate A/B MAP SHA-256 is
`0465b4e10041a2c2dd718e89c8432a97a7668a53af171f2c52285e191676c375`;
A/B candidate MAIN SHA-256 is
`a07df1577dae48c3513627f5fd5c593f037bc1a4d103e8e7a010386024e8b759`;
final A/B monolithic `th04_main.obj` dependency-normalized SHA-256 is
`f17dd6106bc34437bb6308eb91c731b62df382e402e435b299e5c5157e38c04d`.
Raw OMF E9 dependency timestamp differences remain visible rather than being
hidden.

## Accounting and continuation

The two low-level logical rows move from `reconstruct` to the separate
`attest-asm` plane. Elly remains `authored / reconstruct / blocked` with
maintained natural source. MAIN status is therefore:

- C/C++ reviewed exact bytes: `75,482 / 81,155` (`93.009673%`);
- reviewed exact functions: `458 / 481` (`95.218295%`);
- MAIN reconstruction queue: 503 authored candidates, of which 25 are blocked
  and 20 unreviewed;
- MAIN ASM attestation observations: 65;
- generated exact original-style ASM physical owners: 36 / 5,146 bytes.

The function ledger remains 481 rows. Fresh Ghidra has no Elly function entry,
and there is not yet an exact physical natural-source owner from which the
strict no-Ghidra function-review path could admit it. Adding a function row by
hand would overstate the reviewed function denominator.

## Analysis lifecycle and final validation

`.analysis/` started at **3,804,202,716 bytes** and peaked at
**3,995,620,847 bytes** after the three v200 cold replays. After proving no
active producer, the focused and candidate replay trees were compacted to
receipt-only state while the complete 241-owner post-promotion aggregate was
retained as the current cold baseline. Pre-CI size was **3,883,271,203 bytes**.
Full final `python3 scripts/ci.py` returns `CI: PASS`; after its live Ghidra
replay, `.analysis/` is **3,883,277,336 bytes**, net growth **79,074,620 bytes**
from entry. Older baselines, targets, toolchains, Wine/Ghidra state, unrelated
ignored objects, and legacy/unknown content remain untouched.

Repository-native physical-owner exactness is established for the shot and
fillm64 ASM owners only. Elly remains natural-source codegen-exact but linked
exactness is unestablished. Standalone production closure, whole-image exactness,
runtime-storage identity, runtime scenarios, portable runtime, independent
pristine provenance, and Factory Truth-Kernel acceptance remain separate and
unestablished by this packet.

The first concrete continuation should be the CIRCLE physical-producer split
around Elly. It should extract the internal 14-byte natural object while
explicitly preserving or migrating every v198/v199/v200 contained `main.obj`
ownership binding and proving parity under focused and aggregate cold replay.
This is an integration/owner problem, not another C++ spelling search.
