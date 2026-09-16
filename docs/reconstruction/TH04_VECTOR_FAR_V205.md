# TH04 MAIN far vector producer reconstruction (v205)

## Scope

v205 reviews the complete TH04 `MAIN.EXE` `th03/vector.cpp` SHARED physical
contribution as one producer rather than treating its two public entries as
independent leaf functions.

The reviewed target extent is:

- artifact: `MAIN.EXE`;
- link segment/offset: `SHARED 130E:0037`;
- MZ load-module extent: `0x13117..0x131B6`;
- target file extent: `0x14917..0x149B6`;
- physical size: `0xA0 / 160` bytes;
- target SHA-256:
  `0761c1bb2d84e4b3353831a50ad34b9d8385166ab2264beb2c7e9eddc7df85ca`.

The contribution contains three ownership pieces:

1. `VECTOR2` at load `0x13117`, size `0x45 / 69` bytes;
2. the translation-unit alignment `NOP` at `0x1315C`;
3. `VECTOR2_BETWEEN_PLUS` at load `0x1315D`, size `0x5A / 90` bytes.

Exactly one ordered target MZ relocation overlaps the producer: relocation
index 106 at load `0x13175`, the segment word of the FAR `IATAN2` call inside
`VECTOR2_BETWEEN_PLUS`.

Fresh target-bound Ghidra independently constructs complete contiguous FAR
bodies at analysis `0x23117` and `0x2315D`. It reports six direct callers for
`VECTOR2`, no callees, no direct callers for `VECTOR2_BETWEEN_PLUS`, and one
callee (`IATAN2`) for the latter. A raw target FAR-call search finds seven
`VECTOR2` call sites, demonstrating that the Ghidra caller inventory is itself
incomplete. No direct target FAR call to `VECTOR2_BETWEEN_PLUS` is observed.
The cold MAP nevertheless exposes it as a real public entry inside the complete
physical producer. Ghidra therefore remains navigation evidence only.

## Cross-artifact and cross-game review

The other TH04 artifacts were checked independently rather than inheriting a
MAIN conclusion. Bounded masked searches of the independently attested OP,
MAINE, and ZUN payloads find neither vector body. Therefore this source remains
`src/main/` ownership: it is not proved TH04 multi-artifact shared code.

Independent TH03 MAIN and TH05 MAIN targets do preserve both fixed instruction
skeletons. The comparison masks only ordinary linked table displacement words
and the FAR-call operand fields. TH03 and TH05 therefore corroborate the low-level
producer lineage but transfer no source or exactness into TH04.

The compact cross-target receipt is
`.analysis/gpt-web/th04-main-20260916-v205/cross-artifact-vector-scan.json`,
SHA-256
`e5d54972c36e73f426af69a790a2bb8d65f67acd87bd1336e9982b31bac99abd`.

## Natural TC4J feasibility

The current ReC98 `th03/math/vector.cpp` is not treated as authoritative source.
Its history identifies commit
`8d953dc42e1b31eee572299475c6012e68490992` as the 2021
`[Decompilation] [th03/th04/th05] 2D direction vector construction` change, and
the commit message explicitly describes the result as an "impossible"
decompilation. The current C++ forces two `MOVSX` instructions through raw inline
opcodes and forces the inter-function NOP with a codestring. Those mechanisms
are forbidden for maintained exact C/C++ in this repository.

Three bounded legal TC4J 4.02 mechanisms were tested without inline assembly,
byte emitters, codestrings, fake ABI, or target bytes:

- direct pseudo-register table assignment naturally emits `MOVSX` through EAX,
  followed by extra EAX-to-EDX/ECX moves;
- direct multiply expressions naturally emit a target-shaped EDX table load,
  but recompute the angle index and reload the length for the Y component,
  yielding 79 bytes versus the 69-byte target `VECTOR2`;
- `register long` cosine/sine caches allocate an 8-byte stack frame rather than
  preserving the values in EDX/ECX, yielding 91 bytes.

The compact negative receipt is
`.analysis/gpt-web/th04-main-20260916-v205/vector-codegen-negative.json`,
SHA-256
`e40d688696d13a6b694a134d5629bd042968071beb76cf6f793d2cd78175638f`.
No source-spelling matrix was pursued after these three distinct compiler
mechanisms eliminated the plausible natural C++ routes.

## Maintained symbolic producer

Maintained source is `src/main/math/vector_far.asm`, SHA-256
`58442c35f1d08d3c6d5ceb7cadfe187fd3ee559461969209bb3fd341e9873750`.

It is evidence-backed irreducible/original-style symbolic assembly. It names the
Pascal FAR parameters, `_SinTable8`, `_CosTable8`, `IATAN2`, the two public
functions, and the genuine `EVEN` alignment. It contains no target byte array,
codestring, emitter, C++ inline assembly, fake return, inert padding, target
patch, or ABI lie. It records the supported source form, not the historical
author's exact spelling.

A standalone TASM32 probe emits exactly 160 SHARED LEDATA bytes, two PUBDEF
entries, one EXTDEF record containing `_SinTable8`, `_CosTable8`, and `IATAN2`,
and one FIXUPP record. The complete pre-link LEDATA is byte-identical to the
current exact scaffold C++ object, SHA-256
`aa8542332b365b8b2bf9a773fa8362a6d71da12105be845c02fdef587e3e75a3`.

### Alignment negative and correction

The first integration used a word-aligned TASM SHARED segment (`ACBP=48`). The
historical C++ producer uses byte alignment (`ACBP=28`). Because the preceding
SHARED contribution ends at odd offset `0x0037`, TLINK inserted one byte before
the new producer, moving `VECTOR2` to `0x0038` and shifting all later SHARED
owners. Focused candidate 001 therefore failed broadly even though the 160-byte
instruction LEDATA itself was already correct.

The maintained source now declares the SHARED segment byte-aligned. A standalone
probe emits SEGDEF `28a000020301`, matching the historical C++ producer, while
retaining the same byte-identical 160-byte LEDATA. TASM warns that the segment
alignment is not strict enough because the segment contains 386 instructions,
but emits valid OMF. The focused and aggregate link Oracles below prove that
this metadata reproduces the target layout and relocation behavior.

Failed focused candidate 001 receipt SHA-256:
`0be4c88783f7780fff4813aadb1e2036fcbc58225ea6f230c7d1a737b65a3c76`.
The corrected byte-alignment standalone object SHA-256 is
`3d757670a26fb852f886489dbddacd019e2f30dcf367085c51185c323ad75bf6`.

## Exact replay

The stable historical physical-owner ID is retained for receipt continuity:
`th04-main-module-th03-vector-cpp-13117`. Its historical identifier still says
`cpp`, but its source and origin are now correctly routed to the maintained
symbolic assembler owner.

The replay changes only the TH04 MAIN link-list slot from `th03/vector.cpp` to
`th04/vectorfar.asm`. TH03, TH05, OP, MAINE, and ZUN build graphs are not changed.

Focused run `gptweb-v205-vector-far-focused-candidate-002`:

- selected owners: 142;
- two isolated cold builds;
- `failures=[]`;
- receipt SHA-256:
  `666b4856bd9cbd3b9fed990e5a80e6fe21f743f4343e9e225c8ca6a2bfdac74c`;
- A/B `vectorfar.obj` SHA-256:
  `367880d164d8c68ce6406157bb499f56eac92b9f96271e9a75b2fb8c1b6a73c5`;
- A/B focused MAP SHA-256:
  `8c2444fe366c2fd53a5f38252a6fdb2ea922c9cf8ae14a9aafcf6c9b793f0724`;
- A/B focused candidate MAIN SHA-256:
  `ad51bc32345301eb9e212bc009e6ce757fe24d10c77e0dbc20de4a398648c0a6`.

The corrected MAP places `th04\\vectorfar.asm` at `SHARED 130E:0037 +0xA0`,
`VECTOR2` at `0037`, and `VECTOR2_BETWEEN_PLUS` at `007D`, all with ACBP 28.
The complete physical owner is `raw=True`, `map=True`, and `relocs=True` in both
focused builds.

Candidate no-unit aggregate
`gptweb-v205-vector-far-aggregate-candidate-001` passes all 246 candidate-state
default owners twice with `failures=[]`. Receipt SHA-256 is
`ca5f5c44a60bc04c0eee7dbedadf2a556ee7fb9479d461463e62c4bef3633d8a`.
The aggregate manifest SHA-256 is
`f28c1631c5116821d52bb0de7f245925fa065456324f4198fd86e7ef8d7fa0c5`.
A/B MAP SHA-256 is
`4bea5732094f5f08b2c37365d7cae466f063e54f7cb22cad115c973810cf59cc`;
A/B candidate MAIN SHA-256 is
`1932b7feb681e3fa198d24a10cd93a70ce2cb6d400d1ecab39545cafa26b9f9b`.

Post-promotion aggregate `gptweb-v205-vector-far-aggregate-final-001` passes the
same 246 tracked default owners twice with `failures=[]`. Receipt SHA-256 is
`bc1931e3619916262a210afbd1390fdacdf92957f9be02274e743a406c12d8e8`.
The A/B object, MAP, candidate MAIN, raw slice, and ordered relocation results
remain identical to the candidate aggregate.

## Accounting and verification planes

The two logical vector observations move from the C/C++ reconstruction queue to
the independent original-style ASM attestation plane. They do not enter
`config/th04_main_authored_functions.csv`.

After v205:

- MAIN C/C++ exact reviewed bytes remain `75,620 / 81,279` (`93.037562%`);
- MAIN C/C++ exact reviewed functions remain `460 / 483` (`95.238095%`);
- MAIN reconstruction candidates: 499;
- MAIN unreviewed reconstruction candidates: 15;
- MAIN ASM-attestation observations: 69;
- all-artifact remaining reconstruction queue: 217 observations;
- exact original-style ASM physical units: `39 / 5,525 bytes`.

Repository-native exact physical ownership is established for this 160-byte
MAIN producer only. Standalone TH04 product compile/link closure, whole-image
exactness, runtime-storage identity, runtime scenario validation, portable
runtime, independent pristine provenance, and v205 Factory Truth-Kernel
acceptance remain unestablished.

## Continuation

The next evidence-connected multi-artifact packet is `SND_LOAD`. The boundary
ledger has independent `0xEA` target observations in MAIN, OP, and MAINE:

- MAIN: load `0x13496`, reviewed/blocked;
- OP: load `0xDDCA`, corroborated/unreviewed;
- MAINE: load `0xD112`, corroborated/unreviewed.

All three cold candidate link graphs contain a `th04/snd_load.cpp` `0xEA`
SHARED contribution. The current MAINE candidate MAP resolves that contribution
at `0CC7:04A0` (linear load approximately `0xD110`), two bytes before the ledger
target observation. The next packet should reconcile that seam rather than
assuming one shared boundary, compare all three target bodies/fixups, reuse the
existing MAIN partial exact subextents, and determine whether the remaining
41-byte MAIN gap can be naturally recovered without inline-assembly/codestring
tricks. ZUN has no corresponding candidate contribution.
