# TH04 TILE Stage 3 / Stage X midboss renderer reconstruction (v163)

## Scope

This packet reconstructs two adjacent authored near functions in `th04-main / MAIN.EXE / TILE_TEXT` as separate natural TC4J objects:

- `midboss3_render()`: `0AAF:1D95..1E59`, load `0xC885..0xC949`, target file `0xE085..0xE149`, size `0xC5 / 197`, target slice SHA-256 `8eff8ea44f86b9f3d2978d76c54a5715a966723abb84d50710c1be1211c904e8`;
- `midbossx_render()`: `0AAF:1E5A..1EAA`, load `0xC94A..0xC99A`, target file `0xE14A..0xE19A`, size `0x51 / 81`, target slice SHA-256 `6194e35df530d0ee97e2cf932144c2e5f851fc1e9a7c583ea1b8e8c9a400a67a`.

Together the two function bodies cover `0x116 / 278` bytes and target file `0xE085..0xE19A`, SHA-256 `4ca7083efaf8e02ebb1f29280dda7be7e1ffe5828ccb91500d1879e335af46dc`. Load `0xC99B` is an independent zero layout byte, not function credit. The exact v161 pellet ASM owner begins at load `0xC99C`.

Fresh target-bound Ghidra reports complete contiguous bodies for both functions. TLINK publics, pinned TASM, raw target decoding, and Stage 3 / Stage X callback installation independently agree on both boundaries. The v163 function reviewer admits both only through explicit `[[new_exact]]` policy after exact-owner replay; historical function-ledger rows are preserved unchanged.

## Physical producer result

The important result is that equal combined size is not enough to recover the original producer split. A first natural combined-TU probe emits exactly `0x116` CODE bytes with public offsets `0` and `0xC5`, and can reproduce the linked function bytes, but it emits MZ relocations in order `[0xC997,0xC93F,0xC92D]`. The target order is `[0xC93F,0xC92D,0xC997]`.

Compiling the two maintained functions as separate TC4J objects restores the target relocation topology:

- `m3r.obj`: ordered target/candidate relocations `[0xC93F,0xC92D]`;
- `mxr.obj`: ordered target/candidate relocations `[0xC997]`.

This is evidence for two original physical translation-unit contributions, not permission to merge the functions merely because their combined code size is exact. Replay therefore splits the old monolithic `TILE_TEXT` scaffold into its prefix, natural Stage 3 object, natural Stage X object, one hash-bound zero-byte seam object at load `0xC99B`, and the suffix containing the independently exact v161/v162 ASM owners. The seam and suffix are layout/Oracle plumbing and receive no authored C++ byte or function credit.

Maintained sources are `src/main/midboss/m3_render.cpp` (SHA-256 `2f29422c92bec09ff1f3a33f0028506595b5c56eab099933afe2241cc7e3b50f`) and `src/main/midboss/mx_render.cpp` (SHA-256 `10ad57cd96a76e7a6004f34853e4d990d525940e401d1994d7a1dfd8fc0c4316`). They use ordinary natural C++ only. No inline assembly, target-derived byte arrays, `#pragma codestring`, fake returns, inert padding, object patching, target patching, or ABI lies are used.

Focused A/B objects are valid TC86 Borland C++ 4.02 OMF. Stage 3 raw object SHA-256 is `c6f4c6cd3ce062c7cac4ebce45df55f57f142c5990523edbdf0a282b305892ef`, dependency-normalized SHA-256 `0b0c7b05b77306dc02d5fba63b577e4dc408b064b79720a827040c3bf31a8372`. Stage X raw object SHA-256 is `a29afcb73c4b8b228113b5a478035a9d97c95e7bd0e4c783b79837c4b536fec5`, dependency-normalized SHA-256 `7fd1b60de7ac74f7605221ba681c0199dc9e556ed051eb1bfa3db1b04cab62ba`.

## Exactness Oracles actually run

Focused `gptweb-v163-midboss3x-focused-candidate-001` selects the 117-owner dependency closure and passes two isolated cold builds with `failures=[]`. Receipt SHA-256 is `9ae731115f73dee2f32d6639c999812c08fc4280d9f5ba06ca70ad122a6b26a4`. Both new owners are raw exact, map exact, and ordered-relocation exact; the independent zero seam is also raw/map exact. Both focused candidate MAIN images have SHA-256 `2903f6732689a1c19d0b48d93bc66f7052c3ff1f4d4290588ef58761d7214305`.

Candidate-state aggregate `gptweb-v163-midboss3x-aggregate-candidate-001` passes all 196 default owners twice with `failures=[]`; receipt SHA-256 is `96208d620904828077b91fd446941b24b497642e5d23c30bfbd8a5138b2a6233`. After exact-unit promotion, `gptweb-v163-midboss3x-aggregate-final-001` passes the same 196-owner cohort twice again; receipt SHA-256 is `cd4d14e9f573768901817122f49aeb4682e9226f86cce20c5364ba40fc569ba6`. Both aggregate runs produce deterministic candidate MAIN SHA-256 `53609b5b30d8c42cb23eb78702dbd2d1d4eb098f89b3546ea9952a2ab7d430fd`.

The post-promotion function ledger contains 375 reviewed authored C/C++ functions, 368 exact and seven blocked. The v163 promotion also exposed three stale `reviewed_nonexact` entries in `config/th04_main_function_review.toml` for functions reclassified to original-style ASM in v140/v142; those obsolete authored-C/C++ policy requirements are removed without changing their ASM evidence or accepted owners.

## Verification-plane boundaries

This packet establishes repository-native natural-source function/extent exactness for the two renderer functions and their two separate TC4J physical objects. It does not establish standalone TH04 production compile/link closure, runtime-storage identity, a runtime scenario, whole-image exactness, independent pristine-release provenance, or Factory Truth Kernel acceptance.
