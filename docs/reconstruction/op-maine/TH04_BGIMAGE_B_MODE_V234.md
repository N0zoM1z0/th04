# BGIMAGE TCC assembly-output producer (v234/v235)

## Falsifiable producer hypothesis

The [v233 control](TH04_BGIMAGE_FIXUP_PRODUCER_V233.md) showed that the
ReC98-overlay `bgimage.obj` emits 27 descending FIXUPP locations while
the OP/MAINE target-restored eight-site projection is ascending. This packet
tests whether **TCC's `-B` assembly output, assembled with pinned TASM32**,
can change that order without changing the linked BGIMAGE code or layout.

The isolated input is the v214 cold ReC98-overlay
`th04/bgimage.cpp`, SHA-256
`01fbba051c29cd25f297a0465171f382a0d50d1c9e18a512fd6ee5723183415f`.
It is untrusted candidate source. It directly includes
`th04/hardware/bgimage.cpp`, which contains explicit inline assembly
and a `#pragma codestring` padding byte. Those source forms cannot enter
maintained TH04 product source or receive authored-source exact credit.

The same TC86 4.02 flags as the cold build were used with `-B` added:
`-c -I. -O -b- -3 -Z -d -DGAME=4 -ml -DBINARY='O'`. TCC wrote
assembly but then reported `Unable to execute command 'tasm.exe'`.
The generated assembly, SHA-256
`d9ef07588b216f0024e68f01ffa0cc1a5e2131882220051d65bf03e5c8e70af7`,
was assembled separately with the pinned TASM32 5.0
`/m /mx /kh32768 /t`. No tool installation or target byte was patched.
The valid resulting OMF SHA-256 is
`95ea5e2c29792ee1ee1730306db4ad9c1a80c6b06999033d4d66f1e05b98951e`.

## Object and linked result

Both original and `-B`/TASM objects contribute exactly `0xD0`
SHARED CODE bytes with the same SHA-256
`efb4f7170ae577f5f18df689baffeeaad9fb34db3766d01ebdb25209d1f8f554`.
The original object's 27 FIXUPP LOCATs are strictly descending; the
two-stage object's are the exact **reverse**, strictly ascending. The eight
relocation-producing locations consequently have the target-restored order.

Replaced only this object in an isolated v214 build copy and relinked OP and
MAINE with pinned TLINK 6.10. Both linked MZs keep the complete program image,
all header fields, relocation-site multiset, BGIMAGE MAP start/size, and every
other module's ordered relocation projection. Exactly the eight BGIMAGE
entries reverse. Their bytes at OP load `0xE428..0xE4F7` and MAINE load
`0xD626..0xD6F5` equal the target-restored payload. The MAP module
label changes to the generated ASM path; historical target MAP ownership is
unknown.

| Artifact | Relinked MZ SHA-256 | DIET packed candidate | Target packed | Verdict |
| --- | --- | ---: | ---: | --- |
| OP | `6f61356adf7dfcd76fbfbff4ad436fd99732f9c4a24e1ce262cfabce2083adbc` | 42,250 | 42,290 | different |
| MAINE | `ec05efc76a1e7d28c3661e7d4a805587c4301e2d62779cfc21fed77754404b31` | 37,985 | 38,035 | different |

The v234 compact receipt is
`.analysis/reconstruction/probes/v234-bgimage-B/receipt.json`,
SHA-256
`378bc5fd6d453affdaa0ec594f046e4f22dae0ef11a225cb67d8049710b4e7f8`.
It retains generated ASM/OMF, linked MZs/MAPs, and tool logs. Pinned DIET
`-B -G` two-copy packing receipts are
`.analysis/reconstruction/diet-replay/v235-{op,maine}-bgimage-B/receipt.json`,
SHA-256
`5529b51f4a7468c24cd20c80654a4bc7b7a1d13ae78eaf0084d1e46af1956eec`
and `1a207e367a9f1f6722615dfdd42dadf094970948d681a00ab057765ab28debbc`.
The 26 MB isolated build copy and superseded pack outputs were removed after
these compact receipts and inputs were retained.

This establishes a **natural compiler/assembler fixup-order mechanism** for
one shared physical contributor. It does not resolve the other OP/MAINE
payload, relocation, or header/tail differences; it does not make either
packed artifact exact. A maintained TH04 implementation still needs
source-form and ownership review without ReC98's inline assembly or
`codestring` shortcut, then two cold builds and the full exact Oracle
vector.
