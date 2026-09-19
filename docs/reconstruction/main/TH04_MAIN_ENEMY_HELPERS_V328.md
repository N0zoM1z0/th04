# MAIN enemy-script helpers v328

The hash-attested Japanese MAIN.EXE has three contiguous near helpers at
B4M_UPDATE_TEXT `13A9:1ABF..1B4C`, MZ load `0x1554F..0x155DC`, target file
`0x16D4F..0x16DDC`. Their 142 bytes have SHA-256
`46d83fc5c58ef4e69ce48ee67f6df02aeafb31ffe13ca3b770001cde0763df2d`.
The [v327 boundary review](TH04_MAIN_ENEMY_SCRIPT_BOUNDARY_V327.md) attests
the adjacent dispatcher and 144-word switch table through load `0x15C6C`.
Target provenance remains `candidate-local-attested`.

The maintained [C++](../../../src/main/enemy/script_helpers.cpp) implements
the position/clipping helper, velocity helper, and aim-at-player helper. The
product source SHA-256 is
`541f7e991afaff1f3ed8b2c852867f7a27589b328774299f86b7c6d1d6ab4caf`.
It uses the B4M_UPDATE_TEXT segment and the existing `enemy_t`, motion,
vector, and player declarations. This source covers the complete three-helper
extent but does not implement the following dispatcher.

Replay with the pinned TC4J 4.02 compiler and strict OMF parser:

    python3 scripts/probes/replay_th04_enemy_helpers_natural.py \
      --output-dir .analysis/reconstruction/probes/v342-enemy-es-explicit-helpers-002

The probe also checks the frozen compiler snapshot tree digest
`ae9105c56ff94cd6823ad365c03016a0106d923e0b0f653610cf1170e151a3e8`.
The private receipt SHA-256 is
`76ad7bb362ed1e1f2f33dbd20d984a4e1d8f03e0709035736fe07f88e5c2d8d5`.
The valid object has one 142-byte B4M_UPDATE_TEXT LEDATA. Its three helper
lengths are the target 67, 24, and 51 bytes:

| Helper | Compiler observation | Linked result |
| --- | --- | --- |
| Position | Saving the pre-call `enemy_cur`, calling through the global, and assigning the post-call register alias reproduces all 67 instruction bytes after masking two address words and one unresolved near call. | Exact inside the complete linked owner. |
| Velocity | All 24 instruction bytes agree after masking the absolute `enemy_cur` word and unresolved near-call word. | Exact inside the complete linked owner. |
| Aim | All 51 instruction bytes agree after masking five address words. | Exact inside the complete linked owner. |

Two bounded v340/v341 Oracles narrow the remaining aim gap. The attested TH05
target independently contains the same `PUSH ES` / calls / `POP ES` pattern at
three enemy-script sites, including an aim helper and bullet calls. In TC4J,
an ordinary unsigned ES temporary instead emits a 56-byte helper with a BP
local, a register temporary emits 55 bytes using DI, and `__saveregs` emits 67
bytes by saving every general and segment register. None produces the target
51-byte helper. Receipts:

- `.analysis/reconstruction/probes/v340-enemy-es-preservation-001/receipt.json`
  SHA-256 `8f4529c1de197a4d97561828ac5fea3b19d8588bb950af014627df1480f4424a`;
- `.analysis/reconstruction/probes/v341-enemy-es-save-codegen-001/receipt.json`
  SHA-256 `3e99cf2e7d125116f4d52d59aa07f5b003a4f1265bfaef26b8c5489d200b4466`.

The independently hash-attested TH03 target contains a matching 41-byte enemy
velocity helper at load `0x13EA8`; its masked compiler shape agrees with the
TH03 source idiom `asm { push es; }` / `asm { pop es; }`. Together with the
TH04 and TH05 target patterns and the failed natural save matrix, this supports
classifying the two one-instruction statements as genuine handwritten ABI
preservation rather than compiler output. This is an inferred source-level
classification; it supplies no exact credit by itself.

Strict replay:

    python3 scripts/replay_th04_main_exact_units.py \
      --unit th04-main-enemy-script-helpers-v328 \
      --run-id gpt-5-6-sol-v342-enemy-helpers-candidate-001

The focused A/B receipt has SHA-256
`9ae8e9038cf882aeef42d6cb10e31d4dbe8ab4804bf18ff33085af8b3e555ec1`.
Both cold builds produce valid deterministic OMF, the exact
`13A9:1ABF 008E` MAP contribution, the ordered relocation at load `0x155C4`,
and zero raw differences. The 251-owner aggregate
`gpt-5-6-sol-v343-enemy-dispatch-aggregate-final-004` also passes twice; its
receipt SHA-256 is
`8addd30b7e420cab0bf1709fc3d275310c80fd4e5b4eed2debd8317813f17898`.
The complete 142-byte helper owner is therefore exact. No separate runtime
scenario has yet been recorded.
