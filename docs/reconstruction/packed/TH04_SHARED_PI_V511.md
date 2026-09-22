# OP/MAINE shared PI acceptance (v511)

The maintained natural C++ PI producers now have artifact-local decoded
acceptance in both OP.EXE and MAINE.EXE:

- src/shared/formats/pi_put.cpp: pi_palette_apply() plus pi_put_8()
- src/shared/formats/pi_load.cpp: pi_load()

These remain decoded-function claims only. The DIET-packed files provide no
honest direct file offsets for these function bodies, and the retained ReC98
tree is link scaffolding rather than accepted TH04 product source.

## Producer extents

OP's pi_put.cpp producer is SHARED 0DA1:0040, decoded 0xDA50..0xDAFC
(0xAD bytes). It tiles exactly into pi_palette_apply() at 0xDA50..0xDA74
(0x25) and pi_put_8() at 0xDA75..0xDAFC (0x88). OP's independent
pi_load.cpp producer is SHARED 0DA1:00ED, decoded 0xDAFD..0xDB42 (0x46).

MAINE's pi_put.cpp producer is SHARED 0CC7:0048, decoded 0xCCB8..0xCD64
(0xAD), tiled by pi_palette_apply() at 0xCCB8..0xCCDC and pi_put_8() at
0xCCDD..0xCD64. Its pi_load.cpp producer is SHARED 0CC7:00F5, decoded
0xCD65..0xCDAA (0x46).

## Cold replay

Run either producer with a new private output directory:

    python3 scripts/probes/replay_th04_shared_pi_put.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME
    python3 scripts/probes/replay_th04_shared_pi_load.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

Each replay copies the retained v489 artifact-local scaffold twice, replaces
only the producer TU with maintained TH04 source plus checked-in shared
headers, cold-compiles with the pinned TC86 4.02 profile, validates OMF,
relinks with TLINK 6.10, checks the exact MAP producer contribution, compares
every ordered MZ relocation, raw-compares the complete producer, and requires
the complete linked program image and EXE to remain equal to the retained
v489 baseline.

Borland dependency timestamps can change the raw OMF file hash between cold
compilations. The replay therefore uses the repository's existing
dependency-timestamp-normalized OMF SHA-256 only for object determinism. Raw
decoded producer/function bytes, linked EXE identity, MAP ownership, and
ordered relocations are not normalized.

Focused receipts:

- PI put: v511-shared-pi-put-001/receipt.json, SHA-256
  6028479ac3c2d7d90874de1c6ad77a8e0269c87de0ae6c2fffa7f588d625bf02;
  source SHA-256
  63908b162249094597ddbe40ed92459f093a64720ca505ab7b5fc3d3fc5c1f7e;
  normalized OMF SHA-256
  9b21e129c7f7619323ed08ede79dabf9aeda2e3f9a6bf8e3825720f2fd54579c.
- PI load: v511-shared-pi-load-001/receipt.json, SHA-256
  72bdb11ccc8d7554bd01aac11799cbae1f516a007689f12116f3c737ce0a84f7;
  source SHA-256
  959d66c21616163ed71dd0a88653f7a2a960ee5e5056369b380357f85959a6ff;
  normalized OMF SHA-256
  57358b1e2d25c47ef68e824f0d6bdb546606c38400c541fb6088b99a4eb01dc6.

Both focused replays are raw-zero in both cold rounds. OP keeps all 804
ordered relocations and linked EXE SHA-256
c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274.
MAINE keeps all 559 ordered relocations and linked EXE SHA-256
d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c.

The complete function SHA-256 values are:

| Artifact | Function | SHA-256 |
| --- | --- | --- |
| OP | pi_palette_apply() | bc409d28b557694fc8adbff346e64a587386f9eff5b3a2054f68d5c1e105c52e |
| OP | pi_put_8() | d55b65521b50511ea04753bda1d156d15e497a36a395752dfc6ac94503400336 |
| OP | pi_load() | e6a3995b1a1e4e10437fa44e495062ade4030882298175ee33c1f5cf2d27c811 |
| MAINE | pi_palette_apply() | bf121432df2e76fc7991d580c615748f36898e662b89a23b6636ce2dd65173c4 |
| MAINE | pi_put_8() | 9e0724a079563b41971a9801b3c1e6e91bd4c373c346120d0ecfba804c728757 |
| MAINE | pi_load() | d0745829d42677ef9d29623565f63b4030b00ebb4f17522df847e3d5fd2d1daa |

The complete decoded acceptance wrapper was re-run after correcting a
fail-open dispatcher bug: PI backend IDs had previously fallen through to the
BGIMAGE command. The focused PI receipts above were always genuine maintained
source replays and remain the ledger evidence, but the old
v511-decoded-*-001 receipts must not be used as proof that PI backend commands
ran.

The corrected dispatcher names every backend explicitly and rejects unknown
IDs. Corrected OP receipt v511-decoded-op-002/receipt.json has SHA-256
47c262bfa044664711a4595c6ac0f9362e4531da7c70405e1dce9e2379c1d6e0;
corrected MAINE receipt v511-decoded-maine-002/receipt.json has SHA-256
76ae7f03b7340a9b09c69f5f6f6b7a978e5c41f3ea9e40efbac29e408e166754.
Both execute BGIMAGE, VRAM, frame-delay, PI-put, and PI-load replay scripts,
retain 804/559 ordered relocations in every backend, and report raw zero
differences for all eight accepted functions.

The new units.csv rows remain source-present; function-level exact state is
carried by the reviewed boundary and decoded-acceptance ledgers. No MAIN
credit, packed-file exactness, or whole-artifact exactness is inferred. The
remaining mature shared-source packet is the five sound functions
PMD/MMD/KAJA/mode/measure, 328 decoded bytes per artifact.
