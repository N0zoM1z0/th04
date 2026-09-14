# TH04 TILE pellet renderer original-style assembly reconstruction (v161)

## Scope

This packet reviews and reconstructs the paired pellet renderer in `th04-main / MAIN.EXE`, `TILE_TEXT`, under the attested `target:th04-main` local Japanese target. The target remains `candidate-local-attested`; this work does not establish independent pristine-release provenance.

The maintained physical owner is `src/main/bullet/pellet_render.asm`:

- map source start `0AAF:1EAC` inside the containing `th04_main.asm / TILE_TEXT` contribution;
- load-module extent `0xC99C..0xCA97`;
- target file extent `0xE19C..0xE297`;
- physical size `0xFC / 252` bytes;
- target slice SHA-256 `21006e191df5be13ca186eaee0787f681cddadc6a631c65679b2b46cdd7c77e3`;
- maintained source SHA-256 `d0fd3293b06cca6f1950feaf25ee28311a40fe721828388ee4fef811ba49426d`.

No MZ relocation overlaps the physical owner.

## Logical boundaries and source-owned alignment

`pellets_render_top()` is the Ghidra-missed TASM/TLINK entry at `0AAF:1EAC`, load `0xC99C`. Gap-free target decode closes its logical body at the `RET` at load `0xCA2C`, for `0x91 / 145` bytes. Its target SHA-256 is `fc4495f4d4df8014dea1deaf593724793ec3bb7da149f1054973e0c71ec9c8a3`.

TASM `EVEN` then emits the single target `0x90` byte at load `0xCA2D`. This byte belongs to the physical source owner but is not function-body credit.

`pellets_render_bottom()` starts at the next public/PROC, `0AAF:1F3E` / load `0xCA2E`, and closes at the `RET` at `0xCA97`, for `0x6A / 106` bytes. Its target SHA-256 is `42bdcecc2432330efeb327503857eacccd738ed5d247667d575c9d513b4d9b7d`. The independently reviewed next PROC `bullets_and_gather_invalidate()` begins at load `0xCA98`.

The two logical boundary rows remain in the separate `original-asm / attest-asm` queue with `accepted_state=unreviewed`. v161 exactness is attached to the 0xFC physical assembler owner and does not add either function to the reviewed natural-C/C++ exact denominator.

## Independent origin evidence

A bounded scan of the independently attested TH02, TH03, TH04, and TH05 original MAIN load modules finds a unique corresponding pair in TH05: top at load `0xC322` and bottom at `0xC3B4`; TH02 and TH03 have no strict prefix hit.

TH04 and TH05 top bodies share 137 of 145 bytes directly. All eight differing bytes are four linked 16-bit data operands; masking only those operand bytes yields identical normalized SHA-256 `2117800081ca6d1e68c95a44dc739675d2318f918b9ce82fbf3a6499287ba027`.

The bottom bodies share 102 of 106 bytes. All four differences are two linked 16-bit data operands; masking only those yields identical normalized SHA-256 `5bbcfa35ea3bcabc69fbf93c5753e5de6e116dbf915f4569d68276d19a926878`. Both original targets preserve the same inter-function `EVEN` NOP.

The preserved architecture is unusually low level: register-resident VRAM offsets, bare single `MOVSW` / `MOVSB` instructions under hand-shaped `LOOP` and `DEC/JB` flow, explicit plane-size wrap correction, and the same top/bottom state handoff. This is origin corroboration, not exactness evidence for TH04 by itself.

## Legal TC4J negative evidence

Current-session TC86 Borland C++ 4.02 probes used only legal pure C/C++ source and the attested toolchain. Byte/word pointer loops compile to ordinary `MOV` plus pointer arithmetic and `JNE`; a fixed six-word loop uses compare/branch control flow; ordinary `memcpy()` and `movedata()` remain FAR calls. Borland `__memcpy__` is a true intrinsic, but it emits `REP MOVSW` / `REP MOVSB` with segment setup rather than the target's single string operations under manual VRAM-wrap loops.

The TH02 cross-game C++ reference similarly requires inline assembly to obtain `MOVSW`/`LOOP`. Inline assembly is not an allowed natural reconstruction mechanism here. Combined with the independent TH05 target structure, these bounded failures support original-style symbolic assembly rather than a forced C++ claim.

## Exactness Oracles actually run

Focused cold replay:

`python3 scripts/replay_th04_main_exact_units.py --unit th04-main-pellet-render-asm-v161 --run-id gptweb-v161-pellet-render-focused-candidate-001`

- PASS for 114 selected owners in two isolated serial cold builds;
- receipt SHA-256 `ad4528909c14271a33964eb64a947012f17644f1ff79597f498aae5248c90007`;
- both candidate MAIN images SHA-256 `0b082f90365a96b5a0ca907df4c832b4d062b2792f67a69e60a51003869ca2f9`;
- all 252 owner bytes are target-identical;
- containing MAP contribution is `0AAF:1C88 03B6 C=CODE S=TILE_TEXT G=MAIN_01 M=th04_main.asm ACBP=48`;
- target/candidate ordered relocation overlap is empty;
- both `th04_main.obj` objects are valid TASM 5.0 OMF and dependency-timestamp-normalize to `7b7d3e3fbaed56ff912dc0c22574d1d08f78c2d1e4dba8c3a054edbf825dc0b1`.

Candidate-state aggregate:

`python3 scripts/replay_th04_main_exact_units.py --run-id gptweb-v161-pellet-render-aggregate-candidate-001`

- PASS for all 193 default owners twice with `failures=[]`;
- receipt SHA-256 `4f0c7eb07d35cb30c7a07ac2d3fe1ef9459b9f8ac56cedab314213ad9f07825a`;
- A/B candidate MAIN SHA-256 `03eef452d5be04dd225fd401a6829f52e5a364d5d7445cbc5c5c9ff4d13647ff`;
- v161 remains raw/map/relocation exact;
- aggregate normalized `th04_main.obj` SHA-256 `cf4afa6f593f0cfe167d011bd2a6319ab867f9011c3c6d293b4c70fb2d26e0e8`.

Post-promotion aggregate:

`python3 scripts/replay_th04_main_exact_units.py --run-id gptweb-v161-pellet-render-aggregate-final-001`

- PASS for all 193 default owners twice with `failures=[]`;
- receipt SHA-256 `06d13f298aa93dbf35ddcacbdcf8e95a8be42cd223dcd31423a22ce6fe1d51a2`;
- A/B candidate MAIN SHA-256 `03eef452d5be04dd225fd401a6829f52e5a364d5d7445cbc5c5c9ff4d13647ff`;
- all 252 owner bytes, MAP containment, empty ordered relocation overlap, and normalized TASM OMF remain exact.

## Verification-plane boundaries

v161 establishes an exact maintained original-style assembler owner for this reviewed 0xFC source region. It does not establish natural-C/C++ exactness for the two logical functions, standalone TH04 production-source compile/link closure, runtime-storage identity, runtime-scenario validation, independent pristine-release provenance, or Factory Truth Kernel acceptance. Those remain separate verification planes.
