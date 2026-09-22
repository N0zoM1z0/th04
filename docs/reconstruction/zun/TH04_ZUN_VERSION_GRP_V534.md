# ZUN VERSION / GRP pure-data library replacement (v534)

This packet replaces two external MASTER pure-data members with maintained
symbolic TASM source. Both are library support; neither changes authored ZUN
exactness.

## Physical owners

The VERSION member owns target decoded _DATA payload 0x219A..0x21F6,
0x5D / 93 bytes, SHA-256
4d3224b4a9686c99aa134fdce59b2fc11d6576931ee8351573a97433789cd4ba.
It exports _Master_Version_NEAR, _Master_Version, and _Master_Copyright.
Payload 0x21F7=00 is the following TLINK word-alignment byte and is outside
the VERSION owner.

The GRP member owns target decoded _DATA payload 0x21F8..0x2202,
0x0B / 11 bytes, SHA-256
76f94dec73b8bddc3f93da96b0cddfe96880b05680b4d8f4899825f2f348e2ab.
It holds the PC-98 VRAM segment/word/line/width/zoom state and mesh byte.
Payload 0x2203=00 is linker alignment outside the GRP owner.

## Dependency topology

src/shared/runtime/master_version.asm keeps the historical empty _TEXT plus
_DATA topology and reproduces the complete 93-byte VERSION payload.

src/shared/hardware/graph_state.asm reproduces the complete 11-byte GRP
payload and deliberately retains one unresolved _Master_Version EXTDEF.
The extracted historical GRP member has the same dependency. VERSION
therefore remains pulled from the archive by a real link dependency rather
than being manually forced into the product.

Stable link-relevant OMF SHA-256 values:

- VERSION: aa110fcf787d004e35e9e16e27ce31954a26d32651467c9d0ce6da50232ff0bc
- GRP: 162a24b820624c37dcf701a91c6baf0ea34be15b82fc4af0714a56bb2b79cfb7

## Cold replay

Run:

    python3 scripts/probes/replay_th04_zun_version_grp.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay preserves every previously localized support member, assembles
VERSION and GRP twice with pinned TASM32 5.0, reconstructs the 640-member
MASTER archive in physical order, and replaces VERSION at zero-based archive
index 0 and GRP at index 91.

The accepted v534 receipt is
.analysis/reconstruction/probes/v534-zun-version-grp-003/receipt.json,
SHA-256
2372c0638a34c3abf2905db8c4626db6e04e75463ca0e31b454165144f62d18a.

Both cold rounds retain resident MAP SHA-256
9798e11f400727f4c5b2a0e22d9fd72f5d202f48eb79ffb4b24f68e3bbb07053
and 6360-byte candidate component SHA-256
a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab.
Both DATA owners and both excluded alignment bytes raw-match target.

The resident target residual remains 4241 bytes. This packet only shrinks the
external support surface.

## Next support surface

The next coherent MASTER owner is fil: it contributes four initialized DATA
bytes and 0x14 BSS bytes holding the shared file state used by the already
localized file helpers. Treat initialized and uninitialized ownership
separately and preserve physical archive order before moving farther into CRT
or libc support.
