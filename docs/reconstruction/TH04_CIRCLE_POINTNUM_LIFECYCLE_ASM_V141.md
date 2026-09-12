# TH04 CIRCLE_TEXT point-number lifecycle original-style assembly (v141)

## Scope

Artifact: `th04-main / MAIN.EXE` (`candidate-local-attested`). Target SHA-256:
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The private executable remains ignored operator input and was not patched,
replaced, relocated, staged, or published.

v141 revisits the three lifecycle functions left blocked by v136. Their logical
function boundaries remain unchanged:

| Entry | CIRCLE_TEXT | Load | File | Body |
| --- | --- | --- | --- | ---: |
| `POINTNUMS_INIT` | `0AAF:11C2` | `0xBCB2..0xBCBC` | `0xD4B2..0xD4BC` | `0x0B` |
| `pointnums_invalidate()` | `0AAF:11CE` | `0xBCBE..0xBCF2` | `0xD4BE..0xD4F2` | `0x35` |
| `POINTNUMS_UPDATE` | `0AAF:1204` | `0xBCF4..0xBD63` | `0xD4F4..0xD563` | `0x70` |

The NOP bytes at load `0xBCBD` and `0xBCF3` are not function-body bytes. They
are physical layout results of `TASM EVEN` after the first two functions.
Therefore one maintained physical source owner covers load `0xBCB2..0xBD63`,
file `0xD4B2..0xD563`, size `0xB2`. Its target slice SHA-256 is
`9950ed036143e1bb2b0b613b7259c009169e7dde08d8b07f53099bbf9644a9c4`.
No MZ relocation overlaps the owner.

## Why the v136 C++ result stays negative

`src/main/pointnum/lifecycle.cpp` was a useful legal TC86 Borland C++ 4.02
experiment. It reproduced the semantic stores and most SI/DI/BX/AX/CL dataflow,
but all tested natural countdown forms inserted zero-testing instructions rather
than the target bare `DEC DI; JNZ`, and TC4J merged two source-level `F_REMOVE`
stores that the target keeps distinct. That compiler-negative evidence remains
durable. The superseded C++ product source is removed rather than retained next
to the evidence-supported assembler owner.

No inline assembly, `#pragma codestring`, target byte array, fake return, ABI
lie, target patch, or hand-authored inert padding is used in v141.

## Independent TH05 target corroboration

The independently attested TH05 target is `.analysis/targets/th05/main.exe`,
size 149,990, SHA-256
`c41f6e6b9a97b2433acc576ceaee800707c8d4ea7e498150a259663c8fa7d4f0`.
A bounded target search uniquely identifies the corresponding lifecycle entries
at TH05 load `0xE16E`, `0xE17A`, and `0xE1A6`.

The comparison is structural rather than a false raw-identity claim. TH05 uses
`POINTNUM_COUNT=0x118` instead of TH04's `0x190`, has no per-point `times_2`
field, and links its globals and call target at different offsets. Despite those
differences:

- init is the same pair of byte-zero stores followed by `RET`;
- invalidate preserves `PUSH SI/PUSH DI`, the point-number cursor loop, the call
  ABI, `ADD SI,0x10`, and bare `DEC DI; JNZ`, while naturally omitting the TH04
  `times_2` adjustment;
- update preserves the two distinct `F_REMOVE` stores, age/Y motion, alive-list
  publication, register-resident loop state, and bare `DEC DI; JNZ`;
- the same `EVEN` architecture naturally yields a NOP after TH05 init and TH05
  update, while TH04 needs NOPs after init and invalidate because the
  game-specific function lengths differ.

This is independent original-target evidence. ReC98's reconstructed assembly is
routing evidence only, not original-source authority.

The maintained v141 source is also included by the focused cold scaffold's TH05
build. Candidate TH05 MAP places `POINTNUMS_INIT` at `0AE1:148E` (program load
`0xC29E`). Comparing target and candidate at their own MAP coordinates gives
148/168 bytes directly equal. All 20 differing bytes belong to linked absolute
operands or one near-call displacement. Masking only those diagnostic operand
bytes yields identical encoded skeleton SHA-256
`4847ab23126bb7814247bb55cfa46c2a5ee54c234335d4c4da021300a1fe1c63`.
This cross-build result is corroboration only and grants no TH04 exactness.

## Maintained source and failed first probe

The maintained source is `src/main/pointnum/lifecycle.asm`, SHA-256
`f457a1bc62b23cbb08505fcd2874773273e068c13b782cfe3b1bc55a53e71181`.
It keeps the TH04-only `times_2` branch under `if GAME eq 4` and expresses both
layout bytes through `EVEN`.

The first focused run,
`gptweb-v141-pointnum-lifecycle-focused-candidate-001`, failed during scaffold
compilation before any exactness verdict. The initial source had incorrectly
made TH04-only `PN_times_2` / `POINTNUM_TIMES_2_W` references unconditional, so
the shared TH05 scaffold could not assemble them. Git status was inspected
immediately. The source was corrected with the target-supported `GAME eq 4`
conditional; no TH04 instruction or target byte was changed to force equality.

## Exact replay

The corrected candidate passed the complete promotion sequence:

1. Focused candidate-state two-cold replay:
   `gptweb-v141-pointnum-lifecycle-focused-candidate-002`, 111-owner dependency
   closure, receipt SHA-256
   `4fab3c29611b1ee0ceca882251ac7b3095ab4aecd1930e3a577af0e72e5f474a`.
   Both builds are raw/map/ordered-relocation exact for all `0xB2` bytes. The
   focused `th04_main.obj` dependency-normalized OMF SHA-256 is
   `7b7d3e3fbaed56ff912dc0c22574d1d08f78c2d1e4dba8c3a054edbf825dc0b1`.
2. Candidate-state aggregate two-cold replay:
   `gptweb-v141-pointnum-lifecycle-aggregate-candidate-001`, all 176 default
   owners PASS, receipt SHA-256
   `78377211b16eb8cdb1848e6fb476d6102dab83f07014c6af77a43adacbbad00b`.
3. Post-promotion aggregate two-cold replay:
   `gptweb-v141-pointnum-lifecycle-aggregate-final-001`, all 176 default owners
   PASS again, receipt SHA-256
   `9809f03159d1490ccf5931f13537809b93c75b08330b1f94b430877bd697ca0c`.

Both final aggregate builds produce candidate MAIN SHA-256
`ad3892d8093df45c1fb6452e288dcd6e9f8cfb0b900909c3686827fa9efc47f8`.
The aggregate `th04_main.obj` dependency-normalized OMF SHA-256 is
`9bb4c6e5422eb938b48f5b2e522c4d77841fefa1e5ed53e18099e2f3f74f2c73`.
Target and candidate ordered relocation overlaps are both empty.

## Accounting and verification planes

The three logical observations move from authored C/C++ reconstruction into the
separate original-style ASM attestation queue. This does not add three authored
exact functions. The exact unit is one physical `0xB2` ASM owner; the two
alignment bytes remain outside logical function-body accounting.

The current reviewed authored C/C++ ledger becomes 47,564 / 47,595 exact bytes
(99.934867%) and 300 / 302 exact functions (99.337748%). Exact original-style
ASM becomes 13 units / 2,025 bytes. These are reviewed ledger denominators, not
coverage claims for MAIN.EXE or the game, and continued boundary discovery may
change them.

Repository-native function/extent exactness passes for the new owner. Standalone
TH04 production-source/link closure is not established. Runtime storage identity
is not established. No runtime scenario is validated here. No Factory
acceptance receipt is claimed for v141. Target provenance remains
`candidate-local-attested`.
