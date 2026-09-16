# TH04 CIRCLE score-tail producer reconstruction (v192)

## Scope

v192 reviews the connected CIRCLE_TEXT packet after the exact splash/spark
lifecycle owners and before the 32x32 rolling sprite blitter. The target window
is:

- map `0AAF:185E..193B`;
- MZ load-module `0xC34E..0xC42B`;
- target file `0xDB4E..0xDC2B`;
- size `0xDE / 222` bytes;
- target SHA-256
  `c0be83d38160eced77ac07f5f5279d02bd2bbb3e3a4f10b805e8ff1ca63c277c`.

The window is not one function and is not all executable code. Target-first raw
review closes these owners in order:

- `CLEAR_DWORDS` / historical `sub_C34E`: load `0xC34E..0xC363`, `0x16` bytes;
- `PLAYPERF_RAISE`: `0xC364..0xC37C`, `0x19` bytes;
- source-owned `EVEN` NOP at `0xC37D`;
- `PLAYPERF_LOWER`: `0xC37E..0xC395`, `0x18` bytes;
- `SELECT_FOR_RANK`: `0xC396..0xC3A9`, `0x14` bytes;
- `scoredat_decode()`: `0xC3AA..0xC3E8`, `0x3F` bytes;
- source-owned `EVEN` NOP at `0xC3E9`;
- `scoredat_encode()`: `0xC3EA..0xC428`, `0x3F` bytes;
- source-owned `EVEN` NOP at `0xC429`;
- `srpt32x32_vram_topleft dw 0` at `0xC42A..0xC42B`, owned by the following
  rolling-blitter producer and deliberately left in replay-only residual
  ownership by v192.

The sole ordered MZ relocation inside the v192 ASM owners is target load
`0xC40A`, relocation-table index 190. It belongs to the segment word of
`scoredat_encode()`'s far `IRand` call.

The review corrects two old provisional zero-size observations:
`scoredat_decode()` and `scoredat_encode()` are each complete `0x3F`-byte near
Pascal bodies. Neither entry is constructed by target Ghidra. Raw target calls
corroborate each entry twice.

## Analysis coverage and callers

Fresh target Ghidra constructs only the three far helpers in this packet:
`PLAYPERF_RAISE`, `PLAYPERF_LOWER`, and `SELECT_FOR_RANK`. It misses
`CLEAR_DWORDS`, both score codecs, and the following 32x32 blitter entry.
Ghidra's caller counts are also incomplete: target raw decoding finds three far
calls to `PLAYPERF_LOWER` where Ghidra reports two, and eleven far calls to
`SELECT_FOR_RANK` where Ghidra reports four. These are retained as analysis
coverage negatives, not repaired by inventing Ghidra functions or xrefs.

`CLEAR_DWORDS` has nine direct near-call anchors in the already exact
`stage_state_init()` owner. That caller's real TC4J object carries the external
symbol `CLEAR_DWORDS`, so v192 preserves the established link contract rather
than manufacturing an alias.

## Producer classification

All four maintained physical owners are classified as evidence-backed
original-style symbolic assembly rather than forced C++.

Bounded legal TC4J probes were tried before that classification. A typed
`clear_dwords()` loop emits 32 bytes with a BP frame and ordinary loop versus
the target 22-byte `REP STOSD` register ABI. A truthful SS-parameter-pointer
`SELECT_FOR_RANK` emits a framed 29-byte function versus the target 20-byte
`BX/SP` selector. A second PLAYPERF hypothesis using Borland `_AL`
pseudo-registers still retains BP frames; the signed lower clamp additionally
expands through integer-promotion code absent from the target. Typed score-codec
loops emit 121-byte decode and 136-byte encode functions instead of the two
63-byte target bodies and replace the target's `LOOP` register pipelines with
ordinary framed loops. No spelling matrix, inline assembly, byte emission,
codestring, padding, ABI lie, or target patch is used to cross these negatives.

Independent TH05 original-target evidence preserves the same producer family.
Its clear helper uses the same stack/register/`REP STOSD` architecture with the
zero register widened to EAX. PLAYPERF and rank selection preserve the fixed
instruction skeleton modulo linked data addresses; the TH05 rank selector also
shares its tail with the preceding TH05-only selector. TH05 score decoding and
encoding at its target load `0xC812` / `0xC849` preserve the same
`ROR`/`XOR`/`LOOP` architecture with GAME5-specific score-structure sizing.
ReC98 assembly history is therefore corroboration and symbolic scaffolding, not
historical-source authority.

The attested decompressed TH04 `OP.EXE` and `MAINE.EXE` payloads were also
searched as independent artifact evidence. Neither contains an exact copy of
the MAIN pointer-taking helper bodies, and the score-codec core signatures are
absent from both payloads. This is negative routing evidence only; no MAIN
source or exactness credit transfers to OP, MAINE, or ZUN.

## Maintained sources and physical ownership

v192 adds:

- `src/main/core/clear_dwords.asm`, SHA-256
  `9f00af8d88a16d01c0be777a5fbb6d35ff9bc0b018a13608b81038f5f35b15fa`;
- `src/main/playperf.asm`, SHA-256
  `00db4ae2fda7d7a32f711ed0ceea5fc42a17385bcf5f0380a58b5203bf6e6e01`;
- `src/main/select_for_rank.asm`, SHA-256
  `aeca5c51f411c1bfafe594d6a85eab02f39cf11e4dba4042a868a4b2fc3f7143`;
- `src/main/score/scoredat_code.asm`, SHA-256
  `c406e8656a71befc76672428df60fbcd0d0d477050efdbda865a77d8e9042c67`.

Standalone TASM32 5.0 probes emit the exact declared lengths. The clear helper's
22 bytes are already target-identical. The combined PLAYPERF/rank probe differs
from target only in ordinary unresolved linked data-address words. The score
probe differs only at the linked `IRand` far-call offset before final linking.

The exact linked physical owners are:

- `th04-main-clear-dwords-asm-v192`: map `0AAF:185E`, file `0xDB4E`, size
  `0x16`, target SHA-256
  `6ad88fa26720fcd93fcb85609d05930b846ff5a61dcaebe86198acf3215e58cd`;
- `th04-main-playperf-asm-v192`: map `0AAF:1874`, file `0xDB64`, size `0x32`,
  target SHA-256
  `b038840ef8d2db0e64731326b52428dea764ed61e08bd7546e5744a6246ce224`;
- `th04-main-select-for-rank-asm-v192`: map `0AAF:18A6`, file `0xDB96`, size
  `0x14`, target SHA-256
  `31d746a92680ce62e23498a247e6cb0ff761ba4bdcf00f7cca9bcbf9155138ae`;
- `th04-main-scoredat-code-asm-v192`: map `0AAF:18BA`, file `0xDBAA`, size
  `0x80`, target SHA-256
  `0600f2cd4cc03e13b0162cd2d2ef3bcc116f864018414ad814108f7b3d7cf65e`.

After all four owners are active, replay-only `cirsuf186.asm` resumes at map
`0AAF:193A`, file `0xDC2A`, size `0x220`. Its first word is the reviewed zsuper
private state rather than part of the score encoder.

## Replay and Oracle closure

The first focused replay,
`gptweb-v192-circle-score-tail-focused-candidate-001`, is retained only as
control-plane negative evidence. All four new owners already passed their own
raw/MAP/ordered-relocation/OMF checks, but the older units still expected larger
monolithic `cirsuf186.asm` auxiliary extents after downstream v192 owners had
split bytes out of those residuals. No byte or producer mismatch occurred.

v192 therefore extends the existing fail-closed ordered auxiliary-extent
mechanism. Each historical baseline remains unchanged when a downstream v192
unit is absent; when that unit is selected, the old residual is replaced by the
new exact owner plus the shorter residual. No historical gate is dropped.

Authoritative focused replay
`gptweb-v192-circle-score-tail-focused-candidate-002` selects 126 owners and
passes both isolated cold builds with `failures=[]`. Receipt SHA-256 is
`3ba5203b4f10e1cd3e3077df0a68fdb2698d0d03169190e67f5edd56029e826a`.
A/B focused object SHA-256 values are:

- `clrdw.obj`: `b329d877625a01e66a90ff69e72c2ae9bd86782db17b4664650d18eb82877c44`;
- `pperf.obj`: `7e120e26fbe0c0c5eda1ecafcee514c07e0a7805a4d903605153f3d9b92800f2`;
- `selrank.obj`: `0da9fca6bc01f5bee432c4800420eee0980faeeb3daec341e25d7db1c6b4d8db`;
- `scode.obj`: `cb9358bbd8ef507efffe7cfb89941d4f192f7e1e5ee348c7eeff7e381bee3347`.

Focused MAP SHA-256 is
`b1eb1a53a1214bc1feb204e7475f6c08bc40fbb343bcd5367cafb9be1d75e1b9`.

Candidate-state no-unit aggregate
`gptweb-v192-circle-score-tail-aggregate-candidate-001` temporarily enables the
four candidates and passes all 230 candidate-state defaults twice. Receipt
SHA-256 is
`4919758f588ad0d03105de46a0475c47af828e0e97bf7eb56cddb75abf3f77f9`.
Enabled manifest SHA-256 is
`d30ff50e233ed00584d0bedd81a76a997bde1b2c3fa59f994f4a0843d6d930db`;
the pre-promotion manifest is restored byte-for-byte to
`8468d6747e816fd2ba72289068a34427950720f7b76c39458a68d476575ac091`.

Post-promotion no-unit aggregate
`gptweb-v192-circle-score-tail-aggregate-final-001` passes the tracked default
cohort twice from promoted ledger extents with `failures=[]`. Receipt SHA-256 is
`8c762e9f0f81aa96af016d69cbffbbfc38f153dc975f8dcaf05c6603312c74ec`.
Tracked manifest SHA-256 is
`d30ff50e233ed00584d0bedd81a76a997bde1b2c3fa59f994f4a0843d6d930db`;
A/B final MAP SHA-256 is
`db4d76df7b16132043a4130e2d3c81ad09ec22409e697562896689d158407165`;
candidate MAIN SHA-256 remains
`205e42067b0eb3534dc83deba125ebf845c1c153f6515ebe60430d3a79f21bd9`.

## Accounting and limits

The six logical entries were not present in the maintained authored-C/C++
function ledger, so v192 does not change the reviewed C/C++ numerator or
denominator. MAIN remains `75,209 / 80,694` exact reviewed authored C/C++ bytes
and `456 / 479` exact reviewed functions. Instead, six boundary observations
move from the C/C++ reconstruction queue to the separate ASM-attestation plane,
and the two score-codec provisional boundaries become reviewed.

Generated progress now reports 27 exact original-style ASM physical units /
3,652 bytes. OP.EXE, MAINE.EXE, and ZUN.COM remain independent queues and receive
no MAIN credit.

Repository-native exact ownership is established for the four v192 physical ASM
owners. This does not establish standalone TH04 product compile/link closure,
whole-image exactness, runtime-storage identity, runtime-scenario validation,
portable-runtime validation, independent pristine provenance, or Factory
Truth-Kernel acceptance.
