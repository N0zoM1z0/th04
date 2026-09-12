# TH04 MAIN_033_TEXT enemy bullet-template copy original-style assembly (v142)

## Scope

Artifact: `th04-main / MAIN.EXE` (`candidate-local-attested`). Target SHA-256:
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The private executable remains ignored operator input and was not patched,
replaced, relocated, staged, or published.

v142 resolves the reviewed `enemy_bullet_template_push(enemy_t&)` origin and
its physical producer seam with the immediately following exact natural-C++
`ENEMIES_UPDATE` owner:

| Entry | MAIN_033_TEXT | Load | Ghidra image | File | Body |
| --- | --- | --- | --- | --- | ---: |
| `enemy_bullet_template_push(enemy_t&)` | `13A9:43AE` | `0x17E3E..0x17E58` | `0x27E3E..0x27E58` | `0x1963E..0x19658` | `0x1B` |
| `ENEMIES_UPDATE` | `13A9:43C9` | `0x17E59..0x1802E` | `0x27E59..0x2802E` | `0x19659..0x1982E` | `0x1D6` |

Fresh target-bound Ghidra, pinned TASM/TLINK ownership, and gap-free raw decode
agree on both boundaries. The helper slice SHA-256 is
`c312f5b7884b72eadeb71d31df900ecac93e7f5d8667a6e2a06d2a53e5061fb7` and has
no overlapping MZ relocation. The update slice SHA-256 is
`0184a3ba5b510c76075380c3f4a6a5ba673fa0fc1badd5122264d731b17b3613`;
its ordered overlapping relocations are `[98201, 98150, 98074]` in both target
and final candidate.

## Origin evidence

The TH04 helper uses a stable low-level copy shape: `MOV CX,9`, source from the
Pascal-near enemy pointer plus member offset `0x2C`, global destination in DI,
`PUSH DS; POP ES`, `REP MOVSW`, and `RET 2`. The v69 legal natural TC86 C++
probes remain durable negative evidence. Struct assignment, intrinsic-copy, and
helper-call forms can reach the same semantics or size, but do not reproduce
this register-setup order. Inline assembly, `#pragma codestring`, target-byte
emission, fake returns, ABI lies, target patching, and inert padding are not
used.

Independent target evidence strengthens the origin classification. The attested
TH05 `MAIN.EXE` target (SHA-256
`c41f6e6b9a97b2433acc576ceaee800707c8d4ea7e498150a259663c8fa7d4f0`) contains
exactly one corresponding 24-byte producer at load `0x16BCF`, SHA-256
`887b6eaea28b836f2f31275b676b9e0cb92edaf66e22a1a8a970d64850391b19`.
It preserves `PUSH BP; MOV BP,SP; PUSH SI; PUSH DI`, CX-first setup, source in
SI, destination in DI, `PUSH DS; POP ES`, `REP MOVSW`, and `RET 2`, while using
seven words and a direct template pointer. TH02 and TH03 contain no full match
to this bounded producer skeleton. TH04's extra `ADD SI,0x2C` and nine-word
count are game-local semantic differences, not a raw cross-game identity claim.
ReC98 is routing material, not source-language authority.

The maintained source is `src/main/enemy/bullet_template_push.asm`, SHA-256
`fab7c41170934b1c4c2af5f92f1f3f2ff64e24c2aa04c5fe0a098a65ff1ce188`. It
expresses the validated nine-word template size and enemy member offset 44 as
symbolic constants. `original-asm` denotes the independently-supported
irreducible symbolic-assembly producer class; it does not claim recovery of the
historical author's exact source text.

## Physical producer correction

Before v142, `src/main/enemy/enemies_update.cpp` carried a natural-C++ lowering
of the helper solely as a physical-layout prefix. Those 27 bytes were already
excluded from exact credit, but the arrangement obscured ownership. v142 removes
that prefix, leaves only the semantic declaration in the update source, and
links maintained `th04/enbtpush.asm` immediately before standalone
`th04/enupd.cpp`.

The resulting `ENEMIES_UPDATE` source SHA-256 is
`d5c2e05084401ca1a1c16e0582f46603b30ae2f722dbd9c964f0e625fa268fcf`. Its
complete 470-byte body remains exact at `13A9:43C9`; the dependency-normalized
TC86 OMF SHA-256 is
`70d6742ee22763cad7000409934eeb3907689ab450bbbd33c2c62430dbee101a`. The helper
TASM object dependency-normalized SHA-256 is
`f7ad9019aa9574fa47cf314709aeb79f5c7240cf97d4b061dbce345e4b721768`.

## Exact replay

The final source/ownership form passed the complete configured promotion chain:

1. Focused candidate-state two-cold replay:
   `gptweb-v142-enemy-btpush-focused-candidate-001`, 43-owner dependency closure,
   receipt SHA-256
   `4ee4961d02444570efffa374a19e78834d4148987f6d7f44cdbb229c70a0abeb`.
2. Candidate-state aggregate two-cold replay:
   `gptweb-v142-enemy-btpush-aggregate-candidate-001`, all 177 default owners
   PASS, receipt SHA-256
   `fc08ef7eba3e94bfab54666abea80d2dbd6caf5fa62a34b9423886f625e03443`.
3. Post-promotion aggregate two-cold replay:
   `gptweb-v142-enemy-btpush-aggregate-final-001`, all 177 default owners PASS
   again with `failures=[]`, receipt SHA-256
   `2360b81d24e0637f99d6552ce4f24283e9671ce9c6d30661ec932dbcff5eb608`.

Both final aggregate builds produce candidate MAIN SHA-256
`87b62fa0ba11f043d0138f5512940f45fc8393c76b1ab002ea28b9adbbd26800`.
The helper is 27/27 raw-byte exact at an exact standalone map contribution with
empty relocation overlap. `ENEMIES_UPDATE` remains 470/470 raw-byte exact at its
exact map position and preserves the complete ordered relocation overlap.

## Accounting and verification planes

The helper moves from the reviewed authored-C/C++ blocked denominator to the
separate original-style ASM attestation track. This does not add authored exact
bytes or an authored exact function; it corrects origin ownership. The live
reviewed authored ledger becomes **47,564 / 47,568 exact bytes (99.991591%)** and
**300 / 301 exact functions (99.667774%)**. Exact original-style ASM becomes
**14 units / 2,052 bytes**. These are moving reviewed-ledger denominators, not
MAIN.EXE, whole-product, or game-completion percentages.

Repository-native function/extent exactness passes for the helper and the
re-owned adjacent update producer. Standalone TH04 production-source/link
closure is not established. Runtime-storage identity is not established. No
runtime scenario is validated by this packet. No Factory acceptance receipt is
claimed here. Target provenance remains `candidate-local-attested`.
