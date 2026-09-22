# OP and MAINE shared sound-mode acceptance (v515)

The maintained natural C++ source src/shared/sound/determine_modes.cpp now has
artifact-local decoded acceptance in both OP.EXE and MAINE.EXE.

This is a decoded-function claim only. units.csv remains source-present because
the DIET-packed files do not expose honest direct file extents for these
decoded bodies. No packed-file or whole-product exactness is inferred.

## Reviewed extents

OP owns the complete 0x9C-byte FAR Pascal snd_determine_modes function at
decoded 0xDCE4..0xDD7F, mapped by TLINK as SHARED 0DA1:02D4 009C.

MAINE owns the corresponding complete 0x9C-byte body at
0xCFAA..0xD045, mapped as SHARED 0CC7:033A 009C.

Target function SHA-256:
- OP: cac0e3747f3e5c540bbe10d6211b5dddff44034b2b88365d6e40c5b5f6ccc00f
- MAINE: b1526d1652adcb1491dd52d3885b9ff499bf4586278d9624703099a13c2adb98

Both boundaries were independently reviewed in the target before this packet.
The following delay-until-measure function is not included.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_shared_mode.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay makes two isolated copies of each retained v489 link scaffold,
replaces only th04/snd_mode.cpp with maintained source, compiles under the
pinned TC86 4.02 profile, validates OMF, relinks with TLINK 6.10, checks the
exact MAP contribution, compares all ordered MZ relocations, raw-compares all
156 function bytes, and requires the complete linked program and EXE to remain
identical to the retained v489 control.

Focused receipt v515-shared-mode-001/receipt.json has SHA-256
0325c4d08828d6a6da0e6ea94bcf676d49db89bb9973cabbc99311d91fb259f9.
Maintained source SHA-256 is
248aca155a313409bb76bfc397837b91ce1b0f792443d9ed71a14f9390903a82.
Non-COMENT link-relevant OMF SHA-256 is
63f2034e2ce28a6eef0829859a9f5d45aa29d7fbb434b1c9242989441a72bc24
in both rounds and both artifacts.

OP is raw-zero over the complete body, preserves all 804 ordered relocations,
and reproduces v489 EXE SHA-256
c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274.

MAINE is raw-zero over the complete body, preserves all 559 ordered
relocations, and reproduces v489 EXE SHA-256
d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c.

## Aggregate decoded replay

The fail-closed decoded wrapper now executes nine explicit backends.
Fresh OP receipt v515-op-acceptance-001/receipt.json has SHA-256
150ede57f9fb51d6a7737d16c509cc4e0a0302c37c17a274fb0016da67c4c604.
Fresh MAINE receipt v515-maine-acceptance-001/receipt.json has SHA-256
57d63a188c2599a16a1790e44e900f909defa5a2d441c601da5980faf0c03450.
All twelve accepted decoded functions in each artifact remain raw-zero.

## Next sound owner

The last reviewed maintained shared sound owner in this cohort is
snd_delay_until_measure, 0x31 bytes per artifact. It still requires its own
source-compiling backend and artifact-local cold acceptance.
