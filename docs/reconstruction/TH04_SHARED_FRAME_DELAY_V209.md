# TH04 shared frame-delay producer reconstruction (v209)

## Scope

v209 reviews `frame_delay(int)` as a TH04-local producer across `MAIN.EXE`,
`OP.EXE`, and `MAINE.EXE`, then localizes the declaration consumed by the v208
shared `SND_DELAY_UNTIL_MEASURE` source. The active exactness target remains
`target:th04-main`; OP and MAINE receive boundary/source ownership evidence only.

## Recovery and attestation

The session started from clean HEAD
`7966869d0a5c9b10c18c64735a9dbd8e5647da70`, branch `main`, seven commits
ahead and zero behind `origin/main`. The completed v208 ignored manifest was
bound to that checkpoint and no Borland/replay producer was active. The recovery
inventory was 4,496,175,740 bytes below `.analysis/`; the v209 manifest entry
after fresh attestation was 4,496,223,696 bytes.

All required repository and Factory guidance was reread. The registered
`th04-ghidra` provider still exposes ten operations and no `get_metadata`, so the
discovered `check {}` operation was used. Provider and repository-native Ghidra
attestation pass against the 156,258-byte MAIN MZ, SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`,
with the 6,144-byte header/load mapping, entry point, and all 1,136 ordered MZ
relocations. Required TC86 Borland C++ 4.02, TASM32 5.0, TLINK 6.10, MS-DOS
Player, and Wine execution surfaces attest. Canonicality remains only
`candidate-local-attested`.

Fresh MAIN Ghidra constructs a contiguous 21-byte FAR body at analysis
`0x231B7..0x231CB`, reports eight callers and zero callees. This remains
provisional navigation evidence and grants no exactness credit.

## Target-first cross-artifact boundary

The complete target bodies are:

| Artifact | Extent | Size | SHA-256 |
| --- | --- | ---: | --- |
| MAIN | load `0x131B7..0x131CB`, file `0x149B7..0x149CB` | `0x15` | `3c79ff0bb4e74ee6e2aa9ac688bf1b849c015acd31c7d7ff135b2ca455b7c26f` |
| OP | payload `0xDA3B..0xDA4F` | `0x15` | `1683f148a8bda60e6dbbe69510b3d79544e84057d6b7721facfaed4820f134aa` |
| MAINE | payload `0xCCA3..0xCCB7` | `0x15` | `0d77d41527daea4e009dcbcdbf7fb8fc956243a9cc04dfd9dc2a289468243d2b` |

All three close at `RETF 2`. OP and MAINE are gap-free between the preceding
`vram_planes_set()` and following `pi_palette_apply(int)` boundaries. MAIN starts
immediately after the exact v205 vector producer and ends immediately before the
next SHARED contribution. No MAIN MZ relocation and no retained OP/MAINE payload
relocation overlaps any frame-delay body.

The cold candidate `obj/th02/frmdely1.obj`, SHA-256
`2ca007754e9f68f87a145339e94e1ef72051fc96ae665a0099c36a22482e3403`,
is valid Intel OMF. Its FIXUPP record independently identifies exactly two
16-bit `_vsync_Count1` operands, at logical code offsets `+5..+6` and `+10..+11`.
Those four bytes are the only bytes that vary across the three TH04 targets.
Masking only those OMF-derived fields yields the common fixed producer SHA-256
`b25bd556ae297ead66b7869049beb7d5a20ab0a599047e78c65f742eda78f55b`.

This proves TH04-local shared producer ownership. It does not transfer MAIN
exactness to OP or MAINE.

## Maintained source and declaration surface

The natural implementation moves to
`src/shared/hardware/frame_delay.cpp`, SHA-256
`6e721bcebcfb25afff531b733fd869591307ee15bf7d514f598ef5f187ad26a8`.
The function remains the ordinary source shape:

`vsync_Count1 = 0; while(vsync_Count1 < frames) {}`

The old self-declaration include through `compat/rec98/th02/hardware/frmdelay.h`
is removed from this implementation. `src/shared/hardware/frame_delay.hpp`,
SHA-256 `ecb110bb9ae12ca45053fef81582262f56234933ad6d462e24214b6c880a7931`,
now provides the maintained TH04 declaration used by shared code.

`src/shared/sound/delay_until_measure.cpp` now includes that maintained header
instead of the ReC98 frame-delay forwarder. Its new SHA-256 is
`fa9ab668a21c26e049732f1e40a15605d13d0bbd4f80abf96dbfce774b43a075`.
A fresh production-profile TC4J probe produces valid OMF SHA-256
`e81a89bd55eb15634ba09063e61ec579deb1d97efbd4e97c2dea8c1dac1b8e3b`.
LEDATA, FIXUPP, PUBDEF, EXTDEF, and SEGDEF records remain byte-identical to the
historical `th04/snd_dlym.obj`. Thus the declaration localization changes no
producer semantics and creates no OP/MAINE exactness claim.

ReC98 history remains provenance only: `frame_delay()` entered through historical
C-decompilation / translation-unit commits. The v209 verdict comes from TH04
target bytes, OMF fixups, maintained natural source, and local exact replay.

## MAIN exact replay

Focused run `gptweb-v209-frame-delay-shared-focused-001` passes two isolated cold
builds with `raw/map/relocs=true`. Receipt SHA-256 is
`de289a7a6a39ea291bab1c2c0223b0397bd6b008af898112f702092559b3b859`.
A/B `frmdely1.obj` SHA-256 is
`0e43271ceeed4fd71714bb5c055f34db79035b7b98222568461cd3d6bb4a46ff`.
The current object's LEDATA, FIXUPP, PUBDEF, EXTDEF, and SEGDEF are each
byte-identical to the historical candidate object; raw object identity changes
because the redundant header dependency metadata is removed.

Mandatory no-unit aggregate `gptweb-v209-frame-delay-shared-aggregate-001`
passes all 246 default exact owners twice with `failures=[]`. Receipt SHA-256 is
`e8d261784d2c44e3181c4eb43acbc64d557c93f89320a622f60f28a01acf9031`.
The live exact-manifest SHA-256 is
`b11a7b3aeddeb1aa162c01e3f712c30e3f1903e0e864d60002e17a838296531f`.
A/B aggregate MAP remains
`4bea5732094f5f08b2c37365d7cae466f063e54f7cb22cad115c973810cf59cc`
and A/B candidate MAIN remains
`1932b7feb681e3fa198d24a10cd93a70ce2cb6d400d1ecab39545cafa26b9f9b`.

This is an ownership/declaration migration of an already-exact MAIN function,
not a new exact promotion; no post-promotion aggregate is claimed.

## Accounting and verification planes

MAIN accounting is unchanged: 293 units, 75,620 / 81,279 reviewed authored
C/C++ bytes exact (93.037562%) and 460 / 483 reviewed functions exact
(95.238095%). OP and MAINE `frame_delay` boundaries move from corroborated to
reviewed while keeping `accepted_state=unreviewed`; generated confidence becomes
7 reviewed OP candidates and 7 reviewed MAINE candidates. OP/MAINE/ZUN still
have no honest artifact-local exactness denominator.

Repository-native MAIN exactness is re-established from the shared source path.
Standalone TH04 product compile/link closure, whole-image equality,
runtime-storage identity, runtime-scenario validation, portable-runtime
validation, independent pristine provenance, and v209 Factory Truth-Kernel
acceptance remain unestablished.

## Recovery controls and continuation

The session failed closed on several control-plane mistakes: one guessed
`obj/th04/frmdely1.obj` path (the real object is `obj/th02/frmdely1.obj`), one
initial `git mv` before creating the destination directory, one evidence writer
using obsolete column names, one unsupported boundary-report `--write` flag, and
one knowledge-row write using obsolete fields. Status/diffs were re-audited after
each failure and only current-session v209 data was corrected. Two read-only
Factory output-pagination calls also hit transient transport failures; Git was
re-audited before continuing. None grants semantic or exactness credit.

The next structural packet should not be another isolated leaf. Review the
remaining OP/MAINE SHARED front cohort around this producer: `vram_planes_set()`
(OP `0xDA12`, MAINE `0xCC7A`, `0x29` each; MAIN already exact natural C++) plus
`pi_palette_apply()` (`0x25`), `pi_put_8()` (`0x88`), and `pi_load()` (`0x46`).
The three PI functions form `0xF3` bytes per artifact immediately after
`frame_delay`; all are currently corroborated cross-game C++ candidates. Close
their combined TU/ownership, relocations, target fixed bytes, and source lineage
before localizing source or transferring any claim.
