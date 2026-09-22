# OP/MAINE shared MMD resident acceptance (v513)

The maintained natural C source `src/shared/sound/mmd_resident.c` now has
artifact-local decoded acceptance in both OP.EXE and MAINE.EXE.

This is a decoded-function claim only. The DIET-packed files do not expose an
honest direct file extent for these decoded bodies, so `units.csv` remains
`source-present` and no packed-file or whole-product exactness is inferred.

## Reviewed extents and external padding

OP owns the complete 0x2F-byte FAR `snd_mmd_resident` body at decoded
`0xDC44..0xDC72`, mapped by TLINK as `SHARED 0DA1:0234 002F`.

MAINE owns the corresponding complete 0x2F-byte body at
`0xCF5C..0xCF8A`, mapped as `SHARED 0CC7:02EC 002F`.

The target function SHA-256 values are:

- OP: `eb7eaab9861678838294fdd13ffa0a7b7cb754775c53ded1cd8c0cf0d720f04a`
- MAINE: `b8a71dc62bbf236c51510c4545b96abbfa9a402b7194cdbdbbefe93b34c05ed9`

The following target byte is outside the function in both artifacts:
OP `0xDC73=0x90`, MAINE `0xCF8B=0x90`. Existing v207 target-local review and
the already accepted MAIN MMD owner classify this as padding rather than
authored MMD source. It is therefore deliberately excluded from the MMD
function claim.

## Compiler and layout mechanism

`snd_mmd_resident` must compile without `-WX`;
producer this preserves the target's two distinct RETF paths. The following
SHARED owner nevertheless starts on a word boundary.

The replay therefore also compiles the existing checked-in
`src/main/sound/mmd_align.c`. That translation unit contains no C body.
TC86 emits a word-aligned SHARED SEGDEF and zero LEDATA; TLINK consequently
preserves the downstream contribution start without the alignment TU emitting
or owning any target byte. The target `0x90` gap remains excluded and the
natural link contains `0x00` at that position.

This is an already attested Borland layout mechanism used by MAIN, not a
codestring, object patch, target-derived byte array, inline assembly, or
authored padding claim.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_shared_mmd.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay makes two isolated copies of each retained v489 link scaffold,
replaces `th04/snd_mmdr.c` with the maintained shared source, compiles the
zero-code alignment TU separately, validates both OMF streams, inserts only
that object into the response-file order, relinks with TLINK 6.10, checks MAP
ownership, compares all ordered MZ relocations, and raw-compares the complete
47-byte function.

Focused receipt `v513-shared-mmd-002/receipt.json` has SHA-256
`4ae42ffacebf2d5a200c8c360bf7508f5edc02a8ac0ef08e66a2a4070823f18a`.
Both cold rounds agree. The MMD source object's link-relevant OMF SHA-256 is
`bcf7b17b812ec081dbe485a2f6240a6ec4a10646cdaeb4da8066a5cd34426b14`;
the zero-code alignment object's link-relevant SHA-256 is
`53e283ddebe9081db29ac9adecc2202b8331d81b3790f5459a8ff4739756e971`
with zero LEDATA in both artifacts.

OP raw-matches the complete 47-byte function and preserves all 804 ordered
relocations. Relative to the retained v489 program image, its only linked
program difference is excluded padding offset `0xDC73` (`0x90` target/baseline,
`0x00` natural link).

MAINE likewise raw-matches the complete 47-byte function and preserves all 559
ordered relocations. Its only linked program difference is excluded padding
offset `0xCF8B` (`0x90` target/baseline, `0x00` natural link).

## Aggregate decoded replay

The fail-closed decoded wrapper now executes seven explicit backends:
BGIMAGE, VRAM, frame delay, PI put, PI load, PMD, and MMD.

Fresh OP receipt `v513-op-acceptance-001/receipt.json` has SHA-256
`c11a4f9f5139bda9e599cd92c44c189b4d5bd0034e1d9eba99b444c8019784e10`.
Fresh MAINE receipt `v513-maine-acceptance-001/receipt.json` has SHA-256
`e5ff7cbf0fabe14faf387e32a862daa2361b25a86adba25728a43cbc96965cce`.
All ten accepted decoded functions in each artifact remain raw-zero.

## Next sound owners

The remaining reviewed maintained sound owners are KAJA interrupt,
mode detection, and delay-until-measure: 235 decoded bytes per artifact.
Handle them as separate producer-backed checkpoints so a downstream layout
effect cannot be mistaken for function exactness.
