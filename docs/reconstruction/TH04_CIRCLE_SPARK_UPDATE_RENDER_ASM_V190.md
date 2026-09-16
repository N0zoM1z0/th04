# TH04 CIRCLE spark update/render original-style assembly (v190)

## Scope

v190 reviews and reconstructs one contiguous low-level CIRCLE_TEXT producer in
`th04-main / MAIN.EXE`:

- map `0AAF:1776..17FD`;
- MZ load-module `0xC266..0xC2ED`;
- target file `0xDA66..0xDAED`;
- physical size `0x88 / 136` bytes;
- target SHA-256
  `90362bf610678578e72834baf8890f341978149bb7e75188641c76f0d860c389`.

The physical owner contains two logical near functions and one source-owned
alignment byte:

- `_sparks_update`: load `0xC266..0xC2B1`, `0x4C / 76` bytes;
- `_sparks_render`: load `0xC2B2..0xC2EC`, `0x3B / 59` bytes;
- TASM `EVEN` NOP: load `0xC2ED`, one byte outside both logical bodies.

Exact v189 `@spark_render` plus its own EVEN byte end immediately before this
owner at load `0xC265`. Exact natural-C++ `sparks_invalidate()` begins at the
next byte, load `0xC2EE`. The v190 owner has no overlapping MZ relocation.

Fresh target-bound Ghidra constructs both logical bodies contiguously at the
same target extents. `_sparks_update` has one direct caller (`gameplay_loop()`)
and calls `PlayfieldMotion::update_seg1()`. `_sparks_render` has the same direct
caller and calls the exact scroll helper, the GRCG color helper, and v189
`@spark_render`. These database observations are navigation evidence only and
receive no exactness credit.

## Origin review

Independent original-target comparison provides the primary origin signal.
TH05 contains the corresponding 76-byte updater at load `0xE086`. Relative to
TH04, only five bytes differ: the game-specific `SPARK_COUNT` immediate, the
linked `_sparks` offset word, and the near-call displacement to
`PlayfieldMotion::update_seg1()`. Every other instruction byte is identical.

TH05 contains the corresponding 59-byte renderer at load `0xE0D2`. Only seven
bytes differ: two near-call displacement words, the game-specific `SPARK_COUNT`
immediate, and the linked `_sparks` offset word. The remaining instruction bytes
are identical. The independently maintained TH04 structure declaration explains
the count difference: TH04 uses 96 sparks while TH05 uses 64.

The ReC98 file is not provenance authority. Its first historical appearance is
commit `d9e9b3873614a32eb4594ebde836b41a0f60a627`, subject
`[Reverse-engineering] [th04/th05] Spark animation`. v190 therefore uses that
source only to form symbolic hypotheses, not to infer historical source language.

## Legal TC4J negatives

v190 rebinds two earlier bounded legal-TC4J results to this physical producer
question rather than restarting source-spelling matrices.

For `_sparks_update`, the v186 natural source emits 71 bytes instead of target
76. TC86 merges the two distinct target `F_REMOVE` stores into one shared tail,
even when the source contains distinct control-flow labels. The candidate code
SHA-256 is
`d88ff9de4135b034b25aa0cfe5d671418683333173c39ba019b336926314ca2c`.

For `_sparks_render`, v188 probe 001 emits the target 59-byte high-level skeleton,
but ordinary Borland three-argument fastcall allocation passes the age/cel value
through BL and preserves the scroll return differently. Probe 002 explicitly
keeps the age value in CL, but Borland then inserts `MOV BX,CX` and selects
`SHR AX,4` rather than target `SAR AX,4`, producing 61 bytes. Their CODE
SHA-256 values are
`f91e074277952e14566fa167810388989670a57c25e4d2e8a5895aedbc2ca6e5`
and
`dc3362d5ff3609cdd5c73121464332ae43abc74ee2f50dcd59b56ae2fdd3ca99`.

These are producer/mechanism negatives. v190 does not use inline assembly,
`__emit__`, a target-derived byte array, `#pragma codestring`, padding, an ABI
lie, or a target/object patch to force C++ equality.

## Maintained symbolic source

Maintained source is `src/main/spark/update_render.asm`, SHA-256
`17982f9968b26b7b2bd4c625951561ae000ac8c136fac020e69d9012aa811470`.
It names the spark structure fields, gameplay constants, external storage, calls,
control flow, and the genuine final `EVEN` directive. It does not contain a copy
of the target byte stream.

A standalone TASM32 5.0 probe emits one valid OMF module, SHA-256
`87488cdb8f169211660dc3bba16c9a910be55d57144b8ed2b85db0203b238a1e`,
dependency-timestamp-normalized SHA-256
`208272fb8f9da8c9f904970f1e8a9d950b6538b973fb12b0e296695ff0e85bd6`.
It contains one `0x88` CIRCLE_TEXT LEDATA contribution, with PUBDEF
`_sparks_update` at `0x0000` and `_sparks_render` at `0x004C`. Before linking,
all 124 non-fixup code/layout bytes already match target; the twelve differing
bytes are six ordinary 16-bit OMF-resolved fields. `EVEN` naturally emits the
final NOP.

The bounded origin/codegen/OMF report is
`.analysis/gpt-web/th04-main-20260916-v190/origin-codegen-omf-v190.json`,
SHA-256
`354cba28dc076868848b0c036e5aeb096cf37dd4fd265af1db1a49ba3d69f6e6`.

## Replay ownership

The v189 accepted map left exactly this `0x88` window in zero-credit
`th04\cirsuf188.asm` between exact v189 spark-render and exact v186
`sparks_invalidate()`. v190 replaces only that residual contribution with
`th04\spkur.asm`; the old residual object remains a valid zero-CODE structural
object.

The older v188 and v189 units retain their historical auxiliary-extent contracts
when replayed without v190. When v190 is selected, trigger-scoped auxiliary
ownership redirects the same `0xDA66..0xDAED` extent to `spkur.obj`. The replay
driver therefore supports an ordered list of fail-closed auxiliary-extent
overrides. Existing single-override behavior is unchanged; later selected
triggers may supersede earlier ownership only when the manifest names a nonempty
list of exact auxiliary extents. Focused regression tests cover historical,
precedence, missing-extents, and malformed-entry behavior.

## Exact Oracle results

Focused replay
`gptweb-v190-sparks-update-render-focused-candidate-001` selects 120 owners and
passes two isolated cold builds with `failures=[]`. Receipt SHA-256 is
`f34fc3b9a37d2c5dcd78f15168fc619c255ecf84109c377dd7c58b0bc68ccde7`.
The pre-promotion extent is read through the fail-closed `manifest-candidate`
route. A/B v190 raw bytes, exact map placement, empty ordered relocation overlap,
valid OMF, zero-CODE residual, and dependency owners pass. The focused map
SHA-256 is
`9112c827c9a5f5aaf45f7f2705f7a36e4f7bc1ceaa5628e637f27346bfd3df64`;
focused candidate MAIN SHA-256 is
`518811db1bf863343e7bf69fdad4613c537cd08113b8a40538e0519ee46512df`.

Candidate-state aggregate
`gptweb-v190-sparks-update-render-aggregate-candidate-001` temporarily enables
v190 and passes all 224 default owners twice. Receipt SHA-256 is
`58261e6f9af4fbd8d83b260937fa5a2480912a4f77137686228b98d17298654b`.
The temporary enabled manifest SHA-256 is
`3173b5688f63999c8fc12ed62599a2c4ca18cd0835a202088e6937553e3890d8`;
the pre-promotion tracked manifest is restored byte-for-byte afterward.

After promotion, aggregate
`gptweb-v190-sparks-update-render-aggregate-final-001` again passes all 224
tracked default owners twice from ledger extents with `failures=[]`. Receipt
SHA-256 is
`4b6aa7e19c379c6a512e1dfbd9e432e3712e119f6e9b9d0e27c0acfa4f083b5b`.
A/B `spkur.obj` SHA-256 is
`2b509ae087a7378a7eccc75aec1e91616d8d3868d52e2620842d1db9c3dec879`;
A/B map SHA-256 is
`c20d18bcbb9cd0729e356d071c5e96fc372eb3c5767c2a2195343b7f40b205f3`;
and A/B candidate MAIN SHA-256 remains
`205e42067b0eb3534dc83deba125ebf845c1c153f6515ebe60430d3a79f21bd9`.
The promoted tracked replay-manifest SHA-256 is
`3173b5688f63999c8fc12ed62599a2c4ca18cd0835a202088e6937553e3890d8`.

## Accounting and limits

The two logical functions move from the reviewed authored-C/C++ blocker set to
the separate original-style ASM attestation plane. This does not grant C/C++
function exactness and does not change the authored-C/C++ byte numerator.

`sub_C34E` is deliberately not reclassified in this packet. It remains a
reviewed Ghidra-missed 0x16-byte source/origin question. Exact searches of the
TH02, TH03, and TH05 original targets found no complete copy of its TH04
`REP STOSD` skeleton, so v190 has no independent cross-original basis for an
ASM-origin claim there.

v190 establishes repository-native exact symbolic-ASM ownership only for the
`0x88` producer above. It does not establish standalone TH04 product
compile/link closure, whole-image exactness, runtime-storage identity,
runtime-scenario validation, portable-runtime validation, independent pristine
release provenance, or Factory Truth-Kernel acceptance. OP.EXE, MAINE.EXE, and
ZUN.COM remain independent artifact queues and receive no MAIN credit.
