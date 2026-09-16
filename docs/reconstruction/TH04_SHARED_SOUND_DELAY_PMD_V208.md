# TH04 shared PMD residency and measure-delay reconstruction (v208)

## Scope

v208 continues the target-first SHARED sound review across TH04 `MAIN.EXE`,
`OP.EXE`, and `MAINE.EXE`. The packet has two related goals:

1. determine whether the already-exact MAIN `snd_pmd_resident()` producer is
   genuinely shared with OP and MAINE; and
2. replace the ReC98-only `SND_DELAY_UNTIL_MEASURE` source hypothesis with
   maintained natural TH04 C++ while preserving the absence of an OP/MAINE
   exactness claim.

The active exactness target remains Japanese `MAIN.EXE`, target identity
`target:th04-main`. OP and MAINE use their independently attested unpacked
payloads for boundary/source-ownership evidence. ZUN has no corresponding
producer in this packet.

## Attestation

The session started from clean HEAD
`b8a41656ddaa94d99c59378129976bfdbde1b057`. Entry preflight, status, and the
2,120-observation boundary validator passed. Provider discovery again exposes ten
read-only `th04-ghidra` operations and no `get_metadata`; the discovered
`check {}` operation was used instead of inventing the stale prompt interface.

Factory and repository-native Ghidra attestation both bind MAIN to SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`,
size 156,258, 6,144-byte MZ header, and all 1,136 ordered relocations. TC86
Borland C++ 4.02, TASM32 5.0, TLINK 6.10, MS-DOS Player, and the required Wine
execution surfaces attest. Canonicality remains `candidate-local-attested`.

Fresh MAIN Ghidra constructs one contiguous 46-byte FAR body at analysis
`0x2337E..0x233AB` for the PMD residency function. This is provisional boundary
evidence only; exactness remains bound to repository cold replay.

## PMD residency is a shared TH04 producer

The relevant target extents are:

| Artifact | Extent | Size | SHA-256 |
| --- | --- | ---: | --- |
| MAIN | load `0x1337E..0x133AB`, file `0x14B7E..0x14BAB` | `0x2E` | `cb1ec6aded8374c7bfcb1e62603e568113463f492213943f34f0fcbe3f15ce20` |
| OP | payload `0xDC16..0xDC43` | `0x2E` | `c9385a54f096070822f25bb9e305e738ae65cd87207f7bb85a4cc35329322647` |
| MAINE | payload `0xCF2E..0xCF5B` | `0x2E` | `478efa0507f44cc4eb7f82f26e7c7a67849a98b98a0288e7477f80a564542c92` |

All three raw bodies have the same instruction architecture. Each ends in
`INC AX; RETF`. OP immediately continues with `_snd_mmd_resident` at `0xDC44`;
MAINE immediately continues with `_snd_mmd_resident` at `0xCF5C`. There is no
inter-function gap and no retained OP/MAINE payload relocation overlaps either
PMD body.

Candidate Intel OMF was used only to derive normal link-resolved byte positions.
The eight positions are logical offsets
`+0x04,+0x05,+0x08,+0x09,+0x0B,+0x0C,+0x0E,+0x0F`, corresponding to linked
global offsets. Masking only those candidate-derived positions leaves zero fixed
producer differences for MAIN, OP, and MAINE. The common fixed SHA-256 is
`0f3d844a79e2a599bc6bbe10c0f424bd2bd32470613de1ba6554a08b3ba87b12`.

This establishes one TH04-local PMD producer across the three executables. It
does not transfer MAIN exactness to OP or MAINE.

The maintained pure-C source content is unchanged and moves from
`src/main/sound/pmd_resident.c` to `src/shared/sound/pmd_resident.c`, SHA-256
`2477c5197df11edc5c76d27ce023192e2c130d402c47008ae7360e982dd3af2e`.
The historical ReC98 producer was introduced in commit `4c8a3cb3` as a
`[Decompilation] [th04/th05] snd_pmd_resident()` change and originally contained
inline assembly for `LES`. The repository-maintained source is stronger: Borland
`__es` pointer semantics naturally emit the target `LES BX,ES:[0180h]` without
inline assembly or target-byte injection.

OP `0xDC16` and MAINE `0xCF2E` move from corroborated to reviewed and bind the
shared maintained source while keeping `accepted_state=unreviewed`.

## Natural `SND_DELAY_UNTIL_MEASURE`

v207 had already reviewed the complete target bodies:

| Artifact | Extent | Size | SHA-256 |
| --- | --- | ---: | --- |
| OP | payload `0xDD80..0xDDB0` | `0x31` | `99211541a77355160ece9e6fc5f631c873cda791c8c4f2616932a5071c68e02e` |
| MAINE | payload `0xD046..0xD076` | `0x31` | `b39fedd6413732f5d478dd7a57f45edbe09d50a448d52675d539d2fce86715ce` |

Both bodies implement the same FAR Pascal function: if no BGM is active, push
`frames_if_no_bgm`, perform the same-segment optimized `NOP; PUSH CS; CALL near`
to `frame_delay()`, and return. Otherwise, poll song measure through PMD/MMD
until the unsigned measure comparison reaches the requested value, then `RETF 4`.

The nine candidate-derived linked-field byte positions remain
`+0x05,+0x06,+0x0D,+0x0E,+0x0F,+0x10,+0x11,+0x1A,+0x1B`. Masking only those
positions leaves zero fixed differences between OP and MAINE and against the
candidate producer. The common fixed SHA-256 is
`01b90abb46302d79cda253a007c8015427d727bd68e74029d2c840b1a6325384`.

ReC98 commit `f539cca1` introduced this function explicitly as
`[Decompilation] [th03/th04] snd_delay_until_measure()`. That provenance is only
a source hypothesis. v208 therefore recompiled the natural form independently
with the attested TH04 command profile:

`-O -b- -3 -Z -d -DGAME=4 -ml -DBINARY='O'`

The maintained source uses only normal C++ and two quarantine forwarders:

- `compat/rec98/th02/hardware/frmdelay.h` (pre-existing), and
- `compat/rec98/th02/snd/measure.hpp` (added in v208).

The maintained file is `src/shared/sound/delay_until_measure.cpp`, SHA-256
`4b3284e07bb2be822dd8673e5b5de2dead038dd7ebdbaf19a589909ded4c13e8`.
The new `measure.hpp` adapter is one line and forwards only to the pinned ReC98
header; it is not product source authority.

A fresh TC4J probe of this exact maintained source shape produces valid Intel OMF
SHA-256
`5adeef89b0d9d0368476a5d2bc6838d51b526c2afa48cfd9608f856a2be1e690`.
Its complete OMF differs from the historical 672-byte candidate object because
THEADR/dependency metadata records the v208 source/forwarder paths. The semantic
records are stronger than that superficial raw identity: LEDATA, FIXUPP, PUBDEF,
EXTDEF, and all SEGDEF records are each byte-identical to historical
`th04/snd_dlym.obj`.

Consequently the OP and MAINE DELAY rows now bind maintained shared natural C++.
They remain `accepted_state=unreviewed`: source presence and exact compiler
producer shape do not create an artifact-local exactness Oracle.

## MAIN cold replay after PMD source migration

Focused run `gptweb-v208-pmd-shared-focused-001` replays the existing exact PMD
owner twice from the shared path. Receipt SHA-256 is
`8a4ccbabe039035b911b1b8171d3e69eff8742499985c4c2b17d1f72291952e2`.
Both builds pass `raw/map/relocs=true`; A/B `snd_pmdr.obj` SHA-256 is
`044df0a84e776c4306dfe997f89cb2873634fd2c4c559836b7b6cf37d97a2a19`.

Mandatory no-unit aggregate `gptweb-v208-pmd-shared-aggregate-001` passes all
246 default exact owners twice with `failures=[]`. Receipt SHA-256 is
`d8e99f7efb835be911bd7f623ffeda8d620ee915bd894f4ce2116188ca906787`.
The tracked exact manifest SHA-256 is
`0abb1f5a1b964a5944815b4034b04927e11755cbf72064a953d0e4846f42e9b2`.
Aggregate A/B MAP SHA-256 remains
`4bea5732094f5f08b2c37365d7cae466f063e54f7cb22cad115c973810cf59cc`
and A/B candidate MAIN remains
`1932b7feb681e3fa198d24a10cd93a70ce2cb6d400d1ecab39545cafa26b9f9b`.

This is an ownership migration of an already-exact MAIN producer, not a new
exact promotion. DELAY is outside the active MAIN link graph, so no MAIN exact
unit or byte credit is created for it.

## Accounting and verification planes

MAIN accounting is intentionally unchanged: 293 units, 75,620 / 81,279 reviewed
C/C++ bytes exact (93.037562%) and 460 / 483 reviewed functions exact
(95.238095%). OP/MAINE/ZUN still have no honest artifact-local exactness
denominator.

The generated boundary confidence table now has six reviewed OP candidates and
six reviewed MAINE candidates. This changes boundary confidence, not exactness.

Repository-native MAIN exactness is re-established for PMD from its shared path.
OP and MAINE receive reviewed PMD boundaries and maintained source ownership for
PMD and DELAY only. Standalone TH04 product compile/link closure, whole-image
exactness, runtime-storage identity, runtime-scenario validation, portable
runtime, independent pristine provenance, and Factory Truth-Kernel acceptance
remain unestablished.

## Continuation

The first evidence-connected continuation is `frame_delay(int)`, directly called
by the maintained DELAY source:

- OP payload `0xDA3B..0xDA4F`, size `0x15`, currently corroborated;
- MAIN load `0x131B7..0x131CB`, size `0x15`, already exact natural C++;
- MAINE payload `0xCCA3..0xCCB7`, size `0x15`, currently corroborated.

All three candidate maps link the same `th02/frmdely1.cpp` 21-byte SHARED
contribution. The next packet should compare target fixed producer bytes,
adjacent ownership and relocations, then decide whether
`src/main/hardware/frame_delay.cpp` can move to `src/shared/hardware/` and replace
the remaining DELAY compatibility dependency. No cross-artifact exactness should
be inferred in advance.
