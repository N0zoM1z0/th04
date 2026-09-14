# TH04 B4M Marisa phase helpers natural reconstruction (v159)

## Scope

This packet covers the two Marisa helpers immediately following the exact Yuuka5 producer in `th04-main / MAIN.EXE`, `B4M_UPDATE_TEXT`. The private target remains `candidate-local-attested`; this packet does not establish independent pristine-release provenance.

The maintained natural owner is `src/main/boss/marisa4_phase.cpp` at map `13A9:2F8A..30F4`, load `0x16A1A..0x16B84`, target file `0x1821A..0x18384`, size `0x16B / 363` bytes. Target slice SHA-256 is `189e83b7c5d207767a8f814315450e73bca9bbcbe5e876804b6c7a90739594e1`.

## Boundary correction

`marisa_phase_entry()` is physically `0x16A1A..0x16AE8`, size `0xCF`, SHA-256 `3788bf6829a6004bfbb349569dce0e812232ae4b8d4485cbbaab515c9b3a3e91`. Fresh Ghidra recognizes only the three-byte `PUSH BP; MOV BP,SP` prologue. Pinned TASM and independent raw decode close the full helper through the AL=0/1/2 returns. It owns three target relocations, at load `0x16AD4`, `0x16A9E`, and `0x16A82`.

`marisa_phase_move()` is `0x16AE9..0x16B84`, size `0x9C`, SHA-256 `4fa42506bb39594d05a48fc330f856b9e6312719c75bf1b172be0664ad4cf64b`. Target, Ghidra, TASM, and raw decode agree on the complete helper. The next byte, load `0x16B85` / map `13A9:30F5`, is independently exact `marisa_flystep_pointreflected(int)`, so no trailing-data seam is inferred.

## Natural source and negative codegen evidence

The final source is ordinary C++ with C linkage for both near helpers. It uses no inline assembly, `__emit__`, copied target bytes, `#pragma codestring`, inert padding, fake returns, target patching, or ABI lies.

Two deterministic failed source shapes are retained as compiler evidence. Candidate 001 used direct per-branch velocity stores; TC4J emitted a `0x167` producer, four bytes shorter than target, even though the first helper and all three relocations already matched. Candidate 002 used a `register int` random-y temporary; TC4J allocated SI and emitted `PUSH/POP SI`, producing `0x16E`, three bytes longer than target. The final nested conditional expressions naturally keep the random velocity result in AX and emit the target common store without a saved register.

Focused candidate 003 emits valid TC86 Borland C++ 4.02 OMF. Raw object SHA-256 is `6a104da2b0c668460abfad28360e2e13d3e2907dc90e872d8b47da7b52139537`; dependency-timestamp-normalized SHA-256 is `c33fa95efd8324e7dd1a07698d8c81743e99cd060c910b578ce927be18e86778`.

## Exactness Oracles actually run

Focused `gptweb-v159-marisa-phase-focused-candidate-003` passes twice for the 100-owner dependency closure. Both candidate MAIN images are SHA-256 `de5de5f666d3ea45005ad4dac6ddaaceb6b3ff5ed73b1f5d20f39ea0462e4ca8`; owner bytes, exact map placement, all three ordered relocations, valid deterministic OMF, the predecessor `b4msuf3.obj` Oracle, and all dependencies pass.

Candidate-state aggregate `gptweb-v159-marisa-phase-aggregate-candidate-001` passes twice for all 192 default owners. Post-promotion aggregate `gptweb-v159-marisa-phase-aggregate-final-001` passes twice again with `failures=[]`. Both aggregates produce deterministic MAIN SHA-256 `03eef452d5be04dd225fd401a6829f52e5a364d5d7445cbc5c5c9ff4d13647ff`, and v159 remains exact for all 363 bytes, map placement, ordered relocations, and normalized OMF.

## Verification-plane boundaries

This packet establishes repository-native reviewed boundary ownership and natural-source exactness only for these two functions / 363 bytes. It does not establish standalone TH04 production-source link closure, runtime-storage identity, runtime scenario validation, independent pristine-release provenance, or Factory Truth Kernel acceptance.
