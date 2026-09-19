# TH04 TILE bullet/gather invalidation original-style ASM reconstruction (v162)

## Scope

This packet reviews and reconstructs `bullets_and_gather_invalidate()` in `th04-main / MAIN.EXE`, `TILE_TEXT`. The logical function is map `0AAF:1FA8..203C`, load `0xCA98..0xCB2C`, target file `0xE298..0xE32C`, size `0x95 / 149` bytes. TASM `EVEN` owns the following NOP at load `0xCB2D`; the maintained physical owner is therefore `0x96 / 150` bytes through target file `0xE32D`. Exact `tiles_invalidate_reset()` begins at the next byte, load `0xCB2E`.

The physical target slice SHA-256 is `27f4964c7ff23550748c558fb32ff007aea13a0160454748a17e24605612e028`; the logical function SHA-256 is `a7e27948ae6d01b28dcd9a5e3e6afa51b2da48cf96a33f91ccf5a5aea35456b6`.

## Boundary and origin review

Fresh target Ghidra, the candidate MAP public, pinned TASM PROC, gap-free raw decode, and the exact next owner agree on the 0x95 function body. There is no MZ relocation overlap in the complete 0x96 physical owner.

Independent original-target evidence supports original-style assembly rather than a forced C++ claim. The attested TH05 `MAIN.EXE` contains the corresponding invalidation producer at load `0xE40E..0xE4B5`; it preserves the same SI/DI bullet/gather traversal and direct packed `SHL/SHR dword [tile_invalidate_box],1` architecture, with game-specific counts and structure sizes.

A production-profile TC86 Borland C++ 4.02 probe recovers the surrounding register allocation and loop shape but emits 161 function bytes instead of 149. All twelve excess bytes are localized to the two packed box shifts: TC4J expands each target direct memory shift into EAX load/shift/store, adding six bytes per occurrence. `volatile` and multiplication/division variants do not recover the target form. This is durable negative compiler evidence, not permission for inline assembly or byte injection.

Maintained `src/main/bullet/invalidate.asm` is symbolic TASM. It uses semantic symbols and ordinary assembler instructions, contains no copied target-byte arrays or target patching, and lets TASM `EVEN` emit the layout byte naturally.

## Exactness Oracles actually run

Focused `gptweb-v162-bullets-gather-focused-candidate-001` selects the 115-owner dependency closure and passes two isolated cold builds with `failures=[]`. The complete 0x96 owner is raw exact, lies inside the exact containing `TILE_TEXT` map contribution, has empty target/candidate relocation overlap, and emits valid deterministic TASM OMF. The focused receipt SHA-256 is `a2be963470582af571d5d6a6e1512bae350aa424fe0f4474953d937c4fac5889`; A/B dependency-normalized `th04_main.obj` SHA-256 is `78374e905a2f4ba260b4cc4d7dc96fd273f7dd5b6fb8fbd9f834a3a64b76c0c1`.

Candidate-state aggregate `gptweb-v162-bullets-gather-aggregate-candidate-001` passes all 194 default owners twice with `failures=[]`; receipt SHA-256 is `ec501007cc5582797cf083cdd7a54f659bc8c742761612c303c41f4cee781a1d`. Post-promotion aggregate `gptweb-v162-bullets-gather-aggregate-final-001` passes the same 194-owner cohort twice again; receipt SHA-256 is `fe89825f13007bccf7f6d3d0bb57d514c976b8f487ca0ab98fd1560dff5b5250`. Both aggregates produce deterministic candidate MAIN SHA-256 `03eef452d5be04dd225fd401a6829f52e5a364d5d7445cbc5c5c9ff4d13647ff`, and normalized aggregate `th04_main.obj` SHA-256 `cf4afa6f593f0cfe167d011bd2a6319ab867f9011c3c6d293b4c70fb2d26e0e8`.

## Verification-plane boundaries

This packet establishes repository-native boundary/origin classification and exact symbolic-ASM ownership only for this 150-byte physical extent. It does not establish standalone TH04 production-source link closure, runtime-storage identity, runtime scenario validation, whole-image exactness, independent pristine-release provenance, or Factory Truth Kernel acceptance.
