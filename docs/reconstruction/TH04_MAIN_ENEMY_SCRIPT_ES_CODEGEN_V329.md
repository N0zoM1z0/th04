# MAIN enemy-script ES:DI compiler producer v329

The attested Japanese MAIN.EXE dispatcher begins at B4M_UPDATE_TEXT
`13A9:1B4D`, MZ load `0x155DD`, target file `0x16DDD`. Its first 42 bytes
through the indirect switch jump have SHA-256
`75b50317b1b2e26344a34ce8c7d0f4bf4643c8674f788c9a8d96e5e04c9a2627`.
They load `enemy_cur` into SI and `std_seg` into ES, add `script_ip` to a DI
script pointer, read `ES:[DI]`, and dispatch through a CS-relative table.
These are target observations; provenance is still `candidate-local-attested`.

The [compiler probe](../../scripts/probes/probe_th04_enemy_script_es_codegen.py)
uses the pinned TC4J 4.02 and a frozen ReC98 source snapshot with tree digest
`ae9105c56ff94cd6823ad365c03016a0106d923e0b0f653610cf1170e151a3e8`.
It compiles the same three-case toy switch with three natural pointer forms:

| Pointer form | OMF CODE bytes | Target 21-byte SI/ES/DI entry after masking two DS symbol words |
| --- | ---: | --- |
| Ordinary far pointer | 84 | No; TC4J spills a four-byte far pointer and reloads it with `LES`. |
| `__es` pointer with one combined offset expression | 73 | No; TC4J computes the offset in AX and copies it to DI. |
| Register `__es` pointer with separate `instr += enemy->script_ip` | 71 | Yes; TC4J emits `MOV DI,[SI+script]`, `ADD DI,[SI+script_ip]`, and `MOV AL,ES:[DI]`. |

Replay:

    python3 scripts/probes/probe_th04_enemy_script_es_codegen.py \
      --output-dir .analysis/reconstruction/probes/v329-enemy-script-es-codegen-002

The private receipt SHA-256 is
`3b8f545dcde4d3b4e54fa4ec389214ba4e07f0b5cce10bf14079d0333970c53b`.
This is **compiler-observed entry-shape evidence**, not source or exact
acceptance for the 0x690 dispatcher/table owner. The target's `ENTER 4`
reflects locals not present in this toy probe, and the 144-case switch body,
ordered relocations, MAP placement, and raw bytes remain open. A natural
dispatcher should preserve the distinct `__es` pointer initialization and
offset addition, then validate the complete switch and frame-advance logic.
