# TH04 shared CDG no-alpha renderer reconstruction (v204)

## Scope

v204 reviews the low-level four-plane `CDG_PUT_NOALPHA_8` producer that the
current ReC98 scaffold links into both TH04 `MAIN.EXE` and `OP.EXE`.

The reviewed MAIN extent is:

- artifact: `MAIN.EXE`;
- link segment/offset: `SHARED 130E:05D4`;
- MZ load-module logical body: `0x136B4..0x13718`;
- source-owned alignment byte: `0x13719` (`NOP`);
- complete physical owner: `0x136B4..0x13719`, size `0x66 / 102` bytes;
- target file extent: `0x14EB4..0x14F19`;
- complete target slice SHA-256:
  `39f73c57a235238c10102d69915aa45904474413da0dfb1122c4dcf2ee3a1e23`.

Fresh target-bound Ghidra constructs one contiguous 101-byte FAR body at
analysis `0x236B4`, reports five callers and no callees, and closes at the
`RETF 6` ending at load `0x13718`. The next byte is not a second function: the
cold MAP assigns a complete `0x66` contribution to the producer translation
unit, and the compiler/assembler evidence below reproduces that final alignment
NOP as a genuine `EVEN` result. No MAIN MZ relocation overlaps the complete
`0x66` extent. Ghidra remains provisional navigation evidence; physical
ownership comes from raw bytes, MAP, object format, and cold replay.

## TH04 multi-artifact ownership

This packet deliberately reviews another TH04 artifact rather than inheriting a
MAIN-only conclusion.

The independently attested retained OP payload contains `CDG_PUT_NOALPHA_8` at
payload/load `0xE176..0xE1DA`, followed by the same `NOP` at `0xE1DB`. Its
complete `0x66` SHA-256 is
`7800e4c7f6a339a9f4c504ff14d9712bc8a8fb22c70609a949bdeb33d48d3333`.

MAIN and OP differ at only two of the 101 logical body bytes: offsets `+0x29`
and `+0x2A`, the ordinary linked near offset of `_cdg_slots`. The cold MAP binds
those values independently:

- MAIN: `_cdg_slots = 0x3978`;
- OP: `_cdg_slots = 0x2716`.

All other 99 logical-body bytes are identical, and the source-owned final NOP is
identical. Neither artifact has an MZ/payload relocation overlapping this
producer. This is direct TH04-local evidence for a shared source producer with
artifact-local link context, not a transfer of MAIN exactness into OP.

A bounded scan of the independently attested MAINE and ZUN payloads finds no
matching producer after masking only that ordinary `_cdg_slots` word. Therefore
`src/shared/` ownership is currently proved for MAIN + OP only; MAINE and ZUN
receive no source, boundary, or exactness credit from this packet.

Retained payload identities remain:

- OP: 69,028 bytes, SHA-256
  `13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`;
- MAINE: 62,414 bytes, SHA-256
  `7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c`;
- ZUN: 13,422 bytes, SHA-256
  `baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.

Packed `ZUN.COM` remains an MZ container despite its extension.

## Cross-game lineage

The independently retained TH05 MAIN target contains the same complete producer
shape at load `0x14C70`: all fixed bytes of the 101-byte body and the following
NOP match after masking only TH05's own `_cdg_slots` word. This is cross-game
lineage corroboration only. The current TH05 candidate link layout is not a
TH05 exactness Oracle for this TH04 claim.

The older TH03 ReC98 producer is maintained as assembler and its history calls
the separated non-alpha display translation unit "undecompilable". That history
is useful mechanism lineage, not authority over TH04 source form.

## Why the ReC98 C++ is not admissible maintained source

The current ReC98 `th04/formats/cdg_p_na.cpp` was introduced by the 2021
`[Decompilation] [th04/th05] cdg_put_noalpha_8()` change. It recreates the target
shape with explicit inline assembly, `REP MOVSD` supplied through `__emit__`, and
`#pragma codestring "\\x90"` for the final byte. Those mechanisms are useful as
reverse-engineering scaffolding but are forbidden exactness tricks for maintained
TH04 C/C++ in this repository.

One bounded legal natural-source probe tests the relevant compiler mechanism
without a spelling matrix. Probe source
`.analysis/gpt-web/th04-main-20260916-v204/cdg_natural_probe.cpp` has SHA-256
`1705deaf2a959448d5e2db8f964d5080b1d8f03243ee6519e7c2a1e8a2f19aa0`.
Its valid TC86 object has SHA-256
`9a1b7b48cad96f0a7ac3a62bc4598488a6d5d4f2ecef2dd9b7151ed7d97f5d62`.

Natural TC4J emits an expanded segmented-pointer implementation with a `0x10`
local frame, scalar ES accesses and ordinary compare loops. It does not emit the
target producer's DS save/restore, stacked ES plane segments, `REP MOVSD` row
copy, or compact plane iteration. This independently agrees with earlier legal
TC4J low-level copy probes. The result is source-form/origin evidence only and
receives zero exactness credit.

## Maintained shared symbolic source

Maintained source is `src/shared/formats/cdg_put_noalpha_8.asm`, SHA-256
`803a362e27932392724d1922b863066d29f5c4e98f9317610408445fbfb6eab5`.

The source is symbolic original-style / irreducible assembly. It names the
Pascal FAR parameters, CDG field offsets, VRAM planes, row size, plane count,
source segment, `REP MOVSD` row loop, and final alignment. It contains no copied
target byte array, codestring, emitter, target patch, or fake ABI. The source
records the best evidence-backed source form; it does not claim recovery of the
historical author's exact spelling.

A standalone TASM32 5.0 mechanism probe emits exactly `0x66` SHARED bytes, one
`CDG_PUT_NOALPHA_8` public, one `_cdg_slots` external fixup, and the genuine
final `EVEN` NOP. Probe source SHA-256 is
`02a574ea40e0702d1f1eddc130e585548e906d780a11d9d92be5017192fccb80`;
object SHA-256 is
`3d8ad30c972d7f47563a97f9976aec829fa57d267f6aaabe3853ff6963c4e7c0`.
After masking only the `_cdg_slots` fixup word, the complete 102-byte producer
matches TH04 MAIN, TH04 OP, and the TH05 MAIN lineage target. The common masked
SHA-256 is
`d6f788bbe22ce9dc30ec964541a36b9111be7c30fc2870459113621bb8b6aa8b`.

## MAIN exact replay

The existing stable physical-owner ID is retained rather than creating a new
overlapping unit:
`th04-main-module-th04-cdg-p-na-cpp-136b4`.
Its historical identifier is kept for receipt continuity even though its source
and origin are now correctly classified as shared original-style assembly.

The replay replaces only MAIN's old `th04/cdg_p_na.cpp` scaffold entry with the
maintained `th04/cdgpna.asm` overlay. OP is deliberately not admitted to the
MAIN exact-unit plane.

Focused run `gptweb-v204-cdg-noalpha-focused-candidate-001`:

- selected owners: 141;
- two isolated cold builds;
- `failures=[]`;
- receipt SHA-256:
  `e400d0e61151bff1c462ce5018a8e1d1f0f57e8a4bd7a1aa2955a5347df22885`;
- A/B `cdgpna.obj` SHA-256:
  `eaa26a880d0f922636bfde01c0e80d0cfddb4f4c85b322a586de35594721b505`;
- A/B MAP SHA-256:
  `a38e7e8710a2fa5edba09b6b0217e46ac579e9ed46429bf3568fd72647610889`;
- A/B focused candidate MAIN SHA-256:
  `ad51bc32345301eb9e212bc009e6ce757fe24d10c77e0dbc20de4a398648c0a6`.

The full `0x66` owner passes `raw=True`, `map=True`, and `relocs=True` in both
focused builds.

Candidate no-unit aggregate
`gptweb-v204-cdg-noalpha-aggregate-candidate-001` passes all 245 candidate-state
default owners twice with `failures=[]`.
Receipt SHA-256 is
`aa4798f1211a120ca2da6ca774950ab7a1e0693b98807572b323d56204aa04ee`.
A/B MAP SHA-256 is
`a0d1f5d71213121f0d8fbec2c542e409fe94227e11604f74111df69fa4cd993a`;
A/B candidate MAIN SHA-256 is
`1932b7feb681e3fa198d24a10cd93a70ce2cb6d400d1ecab39545cafa26b9f9b`.

After promotion, no-unit aggregate
`gptweb-v204-cdg-noalpha-aggregate-final-001` passes the same 245 tracked default
owners twice with `failures=[]`.
Receipt SHA-256 is
`3f6a77a264551eb5d3021bbf4d6c7ee5605ece5d8d9b10fbcf96a8c8635093c2`.
Tracked replay-manifest SHA-256 is
`0850c2aed66c8426c75d716555916d574432196dde58583f5aec782feba126f3`.
The final A/B object, MAP, and candidate MAIN identities remain exactly the
values above, and the shared CDG owner remains raw/MAP/empty-MZ-relocation exact.

## Accounting

The MAIN and OP logical observations move from C/C++ reconstruction routing to
the separate original-style ASM attestation plane. Only the MAIN physical unit
is exact-replayed by the current MAIN Oracle.

Current accounting after v204 is:

- MAIN C/C++ exact reviewed bytes: `75,620 / 81,279` (`93.037562%`);
- MAIN C/C++ exact reviewed functions: `460 / 483` (`95.238095%`);
- MAIN reconstruction candidates: 501;
- MAIN unreviewed reconstruction candidates: 17;
- MAIN ASM-attestation observations: 67;
- OP reconstruction candidates: 93;
- OP ASM-attestation observations: 16;
- exact original-style ASM units: `38 / 5,365 bytes`.

The two artifact boundary rows keep `accepted_state=unreviewed`, matching the
ASM-attestation convention. MAIN physical exactness is recorded in the exact
unit/evidence plane; OP receives no accepted exactness from MAIN replay.

## Analysis lifecycle and verification planes

v204 entered with `.analysis/` at **4,124,534,669 bytes** and peaked at
**4,316,467,571 bytes** while the focused, candidate aggregate, and final
aggregate trees coexisted. After proving no active TCC/TASM/TLINK/replay producer,
the focused and candidate aggregate trees were compacted to receipt-only form
after their receipts, A/B object/MAP, and candidate MAIN evidence were copied to
v204 durable scratch. The complete 245-owner post-promotion aggregate remains the
current cold baseline. Pre-final-CI `.analysis/` is **4,205,486,183 bytes**. Full final `python3 scripts/ci.py` returns `CI: PASS`; after its live Ghidra replay, `.analysis/` is **4,205,492,764 bytes**, net growth **80,958,095 bytes** from v204 entry.

Repository-native exact physical ownership is established for the MAIN instance
of the shared symbolic producer. OP source/origin/boundary routing is supported
by independent target evidence, but OP exactness remains unestablished.
Standalone TH04 product compile/link closure, whole-image exactness,
runtime-storage identity, runtime-scenario validation, portable runtime,
independent pristine provenance, and v204 Factory Truth-Kernel acceptance remain
unestablished.

## Continuation

The next evidence-connected structural packet is the complete `th03/vector.cpp`
SHARED contribution in MAIN. Cold MAP ownership is `SHARED 130E:0037 +0xA0`,
load `0x13117..0x131B6`, target SHA-256
`0761c1bb2d84e4b3353831a50ad34b9d8385166ab2264beb2c7e9eddc7df85ca`.
It contains `VECTOR2` at load `0x13117` (`0x45` bytes), one alignment NOP at
`0x1315C`, and `VECTOR2_BETWEEN_PLUS` at `0x1315D` (`0x5A` bytes). Review both
logical bodies, the NOP owner, the second entry's lack of direct Ghidra callers,
its one callee, OMF/link context, and the actual `th03/math/vector.cpp` natural
source lineage as one packet before assigning shared/local ownership or exactness.
