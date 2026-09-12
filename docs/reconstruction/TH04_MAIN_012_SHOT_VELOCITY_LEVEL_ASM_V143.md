# TH04 MAIN_012_TEXT shot velocity / level original-style assembly (v143)

## Scope

Artifact: `th04-main / MAIN.EXE` (`candidate-local-attested`). Target SHA-256:
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The private executable remains ignored operator input and was not patched,
replaced, relocated, staged, or published.

v143 closes the two adjacent functions that v117/v118 deliberately left as an
unaccepted replay-only seam:

| Function | MAIN_012_TEXT | Load | File | Body |
| --- | --- | --- | --- | ---: |
| `shot_velocity_set(sppoint near*, unsigned char)` | `0AAF:72DA` | `0x11DCA..0x11DE5` | `0x135CA..0x135E5` | `0x1C` |
| `sub_11DE6` | `0AAF:72F6` | `0x11DE6..0x11E11` | `0x135E6..0x13611` | `0x2C` |

The physical owner is the contiguous 0x48-byte window at file
`0x135CA..0x13611`, target slice SHA-256
`23795f7fc0a402f6baa4273dda0c3e0d4957ad16166abb86dd583a128bf3824a`.
No MZ relocation overlaps either logical function or the physical owner.

Fresh target-bound Ghidra still has no function at `0x21DCA`; the 0x1C velocity
boundary is therefore manual target review based on the TLINK public, pinned
TASM PROC, gap-free raw decode, terminal `RET 4`, and the immediately following
selector entry. Ghidra does construct the complete 44-byte FAR selector at
`0x21DE6..0x21E11`.

## Origin evidence

The v117/v118 legal compiler evidence remains negative rather than being erased.
For the velocity helper, natural TC4J stack-peek forms reproduce semantics and
size but emit `PUSH SI; MOV BX,SP` and `MOV BH,0`, not target `MOV BX,SP; PUSH SI`
and `XOR BH,BH`. For the selector, ordinary/register integer and byte counters,
`for`/`while`/`do`, explicit `_CX`, `-k-`, `-G`, and CPU-level probes never emit
the target source-level DS threshold `CX=9` / `LOOP`. The accepted natural-C++
`LOOP` corpus consists only of compiler-generated CS switch-table scanners.

v143 adds independent original-target evidence. The attested TH05 `MAIN.EXE`
(SHA-256 `c41f6e6b9a97b2433acc576ceaee800707c8d4ea7e498150a259663c8fa7d4f0`)
contains the same adjacent architecture:

- load `0xE3C4` begins with `MOV BX,SP; PUSH SI`, reads both arguments through SS,
  indexes the same dword velocity-table shape, stores the dword through SI, and
  returns with `RET 4`; TH05 uses `MOVZX BX` and one game-specific angle-field
  store where TH04 uses `MOV BL; XOR BH,BH`;
- load `0xE3E2` uniquely preserves the TH04 selector architecture: `XOR BX,BX`,
  power in AL, `MOV CX,9`, DS-resident threshold compare, `ADD BX,2; LOOP`,
  shot-level derivation, callback-table selection, then
  `NOP; PUSH CS; CALL near; RETF`, modulo linked addresses and displacement.

The attested TH03 target contains no full match for either combined producer
shape. ReC98 assembly is used only as routing/scaffold material and does not
supply the origin verdict.

## Maintained source and physical seam migration

The maintained source is `src/main/player/shot_velocity.asm`, SHA-256
`99202dd10eb180f5e2774bd834903af5ea75474ea4c8339dadf8e3aebb2589fc`.
It contains symbolic constants and external symbols only; it contains no target
byte array, `#pragma codestring`, target patch, fake return, inert padding, or ABI
lie. `HUD_POWER_PUT` remains declared FAR. A standalone TASM probe emits exactly
72 LEDATA bytes before link fixups. The call site models the established PC-98
same-group compatibility prefix explicitly and preserves the FAR callee type;
TASM resolves the call itself as `PUSH CS; CALL near`, yielding the target
`NOP; PUSH CS; CALL near; RETF` sequence without weakening the ABI.

Before v143, exact replay generated `th04/m12seam.asm` by hash-extracting
`sub_11DE6` from the pinned ReC98 scaffold and including the upstream velocity
ASM. That file was explicit zero-credit Oracle plumbing. v143 removes the
current manifest's scaffold extraction and overlays the maintained source at the
same `th04/m12seam.asm` path. The exact physical order remains:

1. natural-C++ `shots_add()` through `0AAF:72D9`;
2. maintained TASM seam `0AAF:72DA..7321`;
3. natural-C++ `elly_fg_render()` beginning `0AAF:7322`.

The v119 source transform is split without changing its final scaffold identity:
seam-owned externalization first changes `th04_main.asm` from SHA-256
`b1aed730d150915e2e794e1ca714f4b15cf088d85acbf6d4b92b892a56d0f852`
to `49f2e695859aec0b0732db71f2f41372f7da61911f634499516e76a42970aa64`;
`shots_add` externalization then restores the historical final SHA-256
`1bac8bdb2c8b8c1b142f7fcd911763e004ed3b1e2f826a19976e6a2b44e784ed`.

The first v143 focused run exposed an older replay dependency issue rather than a
byte mismatch: `gptweb-v143-shot-seam-focused-candidate-001` reached the linker
before inspection and failed because focused downstream closure selected
`ENEMIES_UPDATE` without its v142 standalone `ENEMY_BULLET_TEMPLATE_PUSH`
definition. The manifest now co-selects that split v142 producer pair. No v143
source byte changed to address this infrastructure failure.

## Exact replay

The final source form passes the complete promotion sequence:

1. Focused candidate-state two-cold replay:
   `gptweb-v143-shot-seam-focused-candidate-002`, 91-owner dependency closure,
   receipt SHA-256
   `929b6b88e7a4731197bbf78e065687428a7df90b794cfba676a400388d0ee450`.
2. Candidate-state aggregate two-cold replay:
   `gptweb-v143-shot-seam-aggregate-candidate-001`, all 178 default owners PASS,
   receipt SHA-256
   `11baa79daaa97e436a2f526cf4bc549a6dd5d2cb5bd47cbe258277377a7347d8`.
3. Post-promotion aggregate two-cold replay:
   `gptweb-v143-shot-seam-aggregate-final-001`, all 178 default owners PASS again,
   `failures=[]`, receipt SHA-256
   `d5d4d5a28261f0a194d396ae155d15b10572963de47f1f46a5203ed72b7a924d`.

Both final aggregate builds produce candidate MAIN SHA-256
`87b62fa0ba11f043d0138f5512940f45fc8393c76b1ab002ea28b9adbbd26800`.
The owner maps exactly as
`0AAF:72DA 0048 C=CODE S=MAIN_012_TEXT G=MAIN_01 M=th04\m12seam.asm ACBP=28`.
Target and candidate relocation overlaps are both empty. The TASM object is valid
and has dependency-timestamp-normalized SHA-256
`a28ca4aafa6fee3af39e834b925182cf665f690e35fd516447c081766b87d5a1`.

## Accounting and verification planes

The two logical observations move from the authored reconstruction queue to the
separate original-style ASM attestation queue. They were unreviewed authored
candidates, so this does not change the reviewed authored C/C++ numerator or
denominator: it remains 47,564 / 47,568 exact bytes and 300 / 301 exact
functions. Exact original-style ASM gains one 0x48 physical unit. Boundary
inventory remains open; no completion claim follows.

Repository-native function/extent exactness is PASS for the maintained 0x48
owner and the 178-owner replay cohort. Standalone TH04 production-source/link
closure is not established. Runtime-storage identity is not established. No
runtime scenario is validated here. No Factory acceptance receipt is claimed by
this repository replay packet. Target provenance remains
`candidate-local-attested`.
