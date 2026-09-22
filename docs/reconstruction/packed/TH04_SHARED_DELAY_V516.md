# OP and MAINE shared delay-until-measure acceptance (v516)

The maintained natural C++ source `src/shared/sound/delay_until_measure.cpp`
now has artifact-local decoded acceptance in both OP.EXE and MAINE.EXE.

This is a decoded-function claim only. `units.csv` remains `source-present`
because the DIET-packed files do not expose honest direct file extents for
these decoded bodies. No packed-file or whole-product exactness is inferred.

## Reviewed extents

OP owns the complete 0x31-byte FAR Pascal `snd_delay_until_measure` function at
decoded `0xDD80..0xDDB0`, mapped by TLINK as `SHARED 0DA1:0370 0031`.

MAINE owns the corresponding complete 0x31-byte body at
`0xD046..0xD076`, mapped as `SHARED 0CC7:03D6 0031`.

Target function SHA-256 values:

- OP: `99211541a77355160ece9e6fc5f631c873cda791c8c4f2616932a5071c68e02e`
- MAINE: `b39fedd6413732f5d478dd7a57f45edbe09d50a448d52675d539d2fce86715ce`

Both boundaries were independently target-reviewed before this packet.
MAINE target byte `0xD077` is the previously reviewed linker-alignment fill
before the word-aligned `CDG_PUT_PLANE` owner. It is outside this function and
receives no authored exact credit from v516.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_shared_delay_measure.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay makes two isolated copies of each retained v489 link scaffold,
replaces only `th04/snd_dlym.cpp` with maintained source and checked-in shared
headers, compiles under the pinned TC86 4.02 profile, validates OMF, relinks
with TLINK 6.10, checks the exact MAP contribution, compares every ordered MZ
relocation, raw-compares all 49 function bytes, and requires the complete
linked program and EXE to remain identical to v489.

Focused receipt `v516-shared-delay-001/receipt.json` has SHA-256
`882b2a71399f8b95d23e8b57b1d8facc6d3da9c9864689ffbd0886470519a19a`.
Maintained source SHA-256 is
`a8d38be8255df45c266444c841ba363025942bb3dbf0b436fa26d087c94d6053`.
The non-COMENT link-relevant OMF SHA-256 is
`fb6e59d810d3974b97c4144417071ffd3c33fdabc20181de7132ef58def2fc54`
in both rounds and both artifacts.

OP raw-matches the complete body, preserves all 804 ordered relocations, and
reproduces v489 EXE SHA-256
`c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbc9d1f421274`.

MAINE raw-matches the complete body, preserves all 559 ordered relocations, and
reproduces v489 EXE SHA-256
`33bdc485782a9fb953823155426ca7f0e6e821d6bc0cdffaaa32f91df2dc90c`.

## Aggregate decoded replay

The fail-closed decoded wrapper now executes ten explicit backends.

Fresh OP receipt `v516-op-acceptance-001/receipt.json` has SHA-256
`0576e1382d0e0523013ad59782cfaa49c7a0fb121f966958928e77000e453f74`.
Fresh MAINE receipt `v516-maine-acceptance-001/receipt.json` has SHA-256
`78ac86faed8e0fbfa4a1c8976fc2ff57d77d2de24a869e144ac6de42f6af2437`.
All thirteen accepted decoded functions in each artifact have
`raw_difference_count = 0`.

## Cohort status

This closes the currently maintained reviewed shared hardware/PI/sound cohort
for OP and MAINE: three BGIMAGE functions plus VRAM, frame delay, three PI
functions, PMD, MMD, KAJA, sound-mode detection, and delay-until-measure.
That is 13 artifact-local decoded-exact functions / 840 decoded source-owner
bytes per artifact. Packed-file accounting remains separate.
