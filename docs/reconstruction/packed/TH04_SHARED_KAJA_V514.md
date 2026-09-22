# OP and MAINE shared KAJA interrupt acceptance (v514)

The maintained natural C++ source src/shared/sound/kaja_interrupt.cpp now has
artifact-local decoded acceptance in both OP.EXE and MAINE.EXE.

This is a decoded-function claim only. The DIET-packed files do not expose an
honest direct file extent for these decoded bodies, so the corresponding
units.csv rows remain source-present; no packed-file or whole-product
exactness is inferred.

## Reviewed extents

OP owns the complete 0x1E-byte FAR Pascal snd_kaja_interrupt function at
decoded 0xDC74..0xDC91, mapped by TLINK as SHARED 0DA1:0264 001E.

MAINE owns the corresponding complete 0x1E-byte body at
0xCF8C..0xCFA9, mapped as SHARED 0CC7:031C 001E.

Target function SHA-256 values:
- OP: c8828b7faad0d7743ab62b9b1bc3f1b9f00fcf0d2fc921d81cac189350d7e6d7
- MAINE: e3da400e64ccf41381397041d68aa0a7be7c39faa6550ac31af05c7db732b5c6

Both boundaries were already target-reviewed as authored before this packet.
No MMD padding byte or neighboring CDG owner is included in either extent.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_shared_kaja.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay makes two isolated copies of each retained v489 link scaffold,
replaces only th04/snd_kaja.cpp with the maintained shared source and checked-in
shared headers, compiles under the pinned TC86 4.02 profile, validates OMF,
relinks with TLINK 6.10, checks the exact MAP contribution, compares every
ordered MZ relocation, raw-compares the complete 30-byte function, and
requires the full linked program and EXE to remain identical to v489.

Focused receipt v514-shared-kaja-001/receipt.json has SHA-256
62db236f06dc75b86882c8478a526821f8fa172509992fb58cf0bc48c0267d10.
Maintained source SHA-256 is
c76ec9eb7707b302bd768a7d4680cebf0eae281cb31e63070c50984fa92bedd4.
The non-COMENT link-relevant OMF SHA-256 is
b72bc29775166721e9d204a00f0f8a685722c3b906c6e6c7e175b63de2d3eba8
in both cold rounds and both artifacts.

OP raw-matches all 30 function bytes, preserves all 804 ordered relocations,
and reproduces v489 EXE SHA-256
c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274.

MAINE raw-matches all 30 function bytes, preserves all 559 ordered relocations,
and reproduces v489 EXE SHA-256
d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c.

## Aggregate decoded replay

The fail-closed decoded wrapper now executes eight explicit backends:
BGIMAGE, VRAM, frame delay, PI put, PI load, PMD, MMD, and KAJA.

Fresh OP receipt v514-op-acceptance-001/receipt.json has SHA-256
739bee7da74363776631faae1950c7136a236e7079a3fd3340530a2eb4d2134b.
Fresh MAINE receipt v514-maine-acceptance-001/receipt.json has SHA-256
9866abda48f2cf90961aff724f4aedb1c12182e7278ad961e1c161f9b7c49a5a.
All eleven accepted decoded functions in each artifact remain raw-zero.

## Next sound owners

The remaining reviewed maintained shared sound owners are snd_determine_modes
(0x9C bytes) and snd_delay_until_measure (0x31 bytes): 205 decoded bytes per
artifact. Keep them producer-backed and artifact-local; a match in OP is not
evidence for MAINE, or vice versa.
