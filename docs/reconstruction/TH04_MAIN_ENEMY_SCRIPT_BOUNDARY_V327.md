# MAIN enemy-script physical boundary v327

The pinned Japanese MAIN.EXE (SHA-256
077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b)
contains one contiguous B4M_UPDATE_TEXT ownership range at
13A9:1ABF..21DC, MZ load 0x1554F..0x15C6C, target file
0x16D4F..0x1746C. Its 1,822 bytes have SHA-256
d91178267e210fe59dcb9cde54ce0c90ced3e9a81efd7eebc366a99e515b6b4a.
The target remains only candidate-local-attested.

The target-bound Ghidra database was re-attested before this review. Raw MZ
decode, the pinned TASM listing, adjacent exact B4M owners, and the exact
enemies_update() caller close the following physical pieces:

| Piece | MZ load extent | Bytes | Target SHA-256 |
| --- | --- | ---: | --- |
| ENEMY_POS_UPDATE | 0x1554F..0x15591 | 67 | 7d52b03b965de465c31ec64d1b7593a3848e99d63089b7486a67b42797991dc3 |
| ENEMY_VELOCITY_SET | 0x15592..0x155A9 | 24 | 02a1110b57064847e41baaa65729a58eb99c419c664893e128e6be1c6d1fa368 |
| sub_155AA | 0x155AA..0x155DC | 51 | 92972f0ba6797be9a7e5a3d16573dc6bb424093f7e0bfb26b8b7b803d3913571 |
| sub_155DD executable body | 0x155DD..0x15B4C | 1,392 | f583bdf96bc51605e14fc90ab7978eed5a00e1be7c9a205096bdf2ac8878480e |
| compiler switch table | 0x15B4D..0x15C6C | 288 | cb58fa8c99025a19e513c4752041f5332389a6feeac66d0e4388958816645556 |

All four executable bodies end in near RET; the next exact explosion owner
begins immediately at 0x15C6D. The exact enemies_update() contains near
CALL E8 3E D7 at load 0x17E9C, resolving to 0x155DD. The switch table
contains 144 words and 49 distinct destinations. Every destination resolves
inside the executable body to an instruction start under an independent
16-bit ndisasm decode. The complete range has three ordered MZ relocation
sites: 0x155C4, 0x15AE2, 0x15A00.

Ghidra omitted the first function and exposed only 23 of 51 bytes for
sub_155AA and 42 of 1,392 executable bytes for sub_155DD. The corrected
function-boundary ledger records the full bodies but leaves them unreviewed
for acceptance. The physical owner is boundary-reviewed in config/units.csv;
the 288 table bytes belong to that owner and receive no separate function
credit. No maintained source or exact acceptance exists for any of these
bytes. The local ReC98 TASM text is target-derived candidate material, not
original-source or exactness evidence.

Replay:

    python3 scripts/preflight.py
    python3 scripts/ghidra.py th04-main check
    python3 scripts/probes/review_th04_enemy_script_boundary.py \
      --output-dir .analysis/reconstruction/probes/v327-enemy-script-boundary

The private receipt SHA-256 is
0da840c3d271ff62d549580def2d2a1346506d71c0c57c8406d4bea94a0273f6.
The decoder binary SHA-256 is
6a85a9d1c8f05c8528895e091ed6b9c5b92b726a66ab0bf263199619663e4dc6.
This is target-analysis evidence only. The next source task is a natural
compiler producer for the three helpers and 144-case script dispatcher,
preserving the complete 0x71E physical ownership, table layout, and all
three ordered relocations. An isolated function or semantically equivalent
VM cannot be promoted while the physical extent differs.
