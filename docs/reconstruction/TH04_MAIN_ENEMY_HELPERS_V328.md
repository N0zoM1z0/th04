# MAIN enemy-script helpers v328

The hash-attested Japanese MAIN.EXE has three contiguous near helpers at
B4M_UPDATE_TEXT `13A9:1ABF..1B4C`, MZ load `0x1554F..0x155DC`, target file
`0x16D4F..0x16DDC`. Their 142 bytes have SHA-256
`46d83fc5c58ef4e69ce48ee67f6df02aeafb31ffe13ca3b770001cde0763df2d`.
The [v327 boundary review](TH04_MAIN_ENEMY_SCRIPT_BOUNDARY_V327.md) attests
the adjacent dispatcher and 144-word switch table through load `0x15C6C`.
Target provenance remains `candidate-local-attested`.

The maintained [natural C++](../../src/main/enemy/script_helpers.cpp) implements
the position/clipping helper, velocity helper, and aim-at-player helper. The
product source SHA-256 is
`e3a9eeb1bd9232882fa9aec9751c1e121daf1692b71eeb1e7a3363f98bab8320`.
It uses the B4M_UPDATE_TEXT segment and the existing `enemy_t`, motion,
vector, and player declarations. This source covers the complete three-helper
extent but does not implement the following dispatcher.

Replay with the pinned TC4J 4.02 compiler and strict OMF parser:

    python3 scripts/probes/replay_th04_enemy_helpers_natural.py \
      --output-dir .analysis/reconstruction/probes/v339-enemy-helpers-natural-001

The probe also checks the frozen compiler snapshot tree digest
`ae9105c56ff94cd6823ad365c03016a0106d923e0b0f653610cf1170e151a3e8`.
The private receipt SHA-256 is
`4488ff3dea283479004b8214ac83f0c081c3650d3033c7220fe368ee29abc06a`.
The valid object has one 140-byte B4M_UPDATE_TEXT LEDATA. Its three helper
lengths are 67, 24, and 49 bytes against target lengths 67, 24, and 51:

| Helper | Compiler observation | Remaining difference |
| --- | --- | --- |
| Position | Saving the pre-call `enemy_cur`, calling through the global, and assigning the post-call register alias reproduces all 67 instruction bytes after masking two address words and one unresolved near call. | Linked placement and raw extent have not been tested. |
| Velocity | All 24 instruction bytes agree after masking the absolute `enemy_cur` word and unresolved near-call word. | Linked placement and raw extent have not been tested. |
| Aim | Its 49 instruction bytes agree after masking five address words and removing the target `PUSH ES` / `POP ES` pair. | Natural TC4J source does not emit that ES preservation pair. |

The target and candidate helper group have unequal lengths (142 versus 140)
before linking. No exact or runtime claim follows from these normalized
compiler observations. The v327 superowner remains a historical boundary
record; two nonoverlapping v328 units now account for the source-present
helpers (`0x8E`) and source-absent dispatcher/table (`0x690`). The complete
`0x71E` owner still needs the two ES-preservation bytes in the aim helper and
the equivalent two bytes in dispatcher opcode `0x20`, three ordered MZ
relocations, linked raw/MAP identity, and the aggregate exact gate.
