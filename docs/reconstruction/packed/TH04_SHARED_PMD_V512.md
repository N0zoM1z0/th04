# OP/MAINE shared PMD resident acceptance (v512)

The maintained natural C source src/shared/sound/pmd_resident.c now has
artifact-local decoded acceptance in both OP.EXE and MAINE.EXE.

This is a decoded-function claim only. The DIET-packed files do not expose an
honest direct file extent for these decoded bodies, so units.csv remains
source-present and no packed-file or whole-product exactness is inferred.

## Reviewed extents

OP owns a complete 0x2E-byte FAR snd_pmd_resident function at decoded
0xDC16..0xDC43, mapped by TLINK as SHARED 0DA1:0206 002E.

MAINE owns the corresponding complete 0x2E-byte function at
0xCF2E..0xCF5B, mapped as SHARED 0CC7:02BE 002E.

The target function SHA-256 values are:

- OP: c9385a54f096070822f25bb9e305e738ae65cd87207f7bb85a4cc35329322647
- MAINE: 478efa0507f44cc4eb7f82f26e7c7a67849a98b98a0288e7477f80a564542c92

## Cold replay

Run:

    python3 scripts/probes/replay_th04_shared_pmd.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay makes two isolated copies of each retained v489 link scaffold,
replaces only th04/snd_pmdr.c with maintained PMD source plus checked-in
shared headers, compiles under the pinned TC86 4.02 profile, validates OMF,
relinks with TLINK 6.10, checks the exact MAP contribution, compares all
ordered MZ relocations, raw-compares the entire 46-byte function, and requires
the complete candidate linked program and EXE to remain equal to v489.

Borland OMF COMENT records vary between cold builds even after dependency
timestamp normalization. They are non-linking metadata. The PMD replay uses
the repository's established link-relevant OMF identity for determinism: it
hashes every non-COMENT OMF record, while raw decoded bytes, MAP ownership,
linked EXE identity, and ordered relocations are still checked without
normalization. The resulting link-relevant OMF SHA-256 is
9e5e7ca090bcd90e70c7a9fff4bfa21639bee2d28c7db072b0517808793eac2c
in both rounds and both artifacts.

Focused receipt v512-shared-pmd-002/receipt.json has SHA-256
33c738b70fd2bb77dc4bef8fedbd67a44a455bd70e4a0a5438b0841f15c638a1.
Both artifacts are raw-zero in both rounds. OP preserves all 804 ordered
relocations and the v489 EXE SHA-256
c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274.
MAINE preserves all 559 ordered relocations and v489 EXE SHA-256
d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c.

The fail-closed decoded wrapper then executed six explicit backends
(BGIMAGE, VRAM, frame delay, PI put, PI load, PMD). OP receipt
v512-decoded-op-001/receipt.json has SHA-256
7c952ef30f019a69f411da217c63f30a3e270a7813c321c5a958aae99210fe08.
MAINE receipt v512-decoded-maine-001/receipt.json has SHA-256
67af6e1d199caa535639d863fccd456ca0f8726d58c4ea2a7030f402cf8d94bf.
All nine accepted functions in each artifact remain raw-zero.

## Next sound seam

The next MMD function is not a request to restore the historical codestring.
The maintained 0x2F-byte snd_mmd_resident body already raw-matches both
targets. Its following target byte is separate padding: OP 0xDC73=90 and
MAINE 0xCF8B=90. Existing repository evidence already classifies that byte as
function-external padding.

A manual cold probe using the maintained zero-code src/main/sound/mmd_align.c
translation unit restores the following module addresses and restores all
804/559 ordered relocations without emitting or claiming that padding byte.
The resulting linked program differs from v489 at exactly that one excluded
padding byte (candidate 00 versus target 90) and nowhere else. Therefore the
next MMD backend should preserve this separation and prove function exactness
without codestring, target-byte emission, or padding credit.
