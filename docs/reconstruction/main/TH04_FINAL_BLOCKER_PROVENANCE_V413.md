# TH04 final blocker local-HDI provenance search (v413)

## Scope

After v408-v412 reduced MAIN to 27 nonexact bytes, the remaining legal route
for checkerboard, Stage 4 carpet, and `snd_load` is independent producer/source
provenance rather than additional target-shaped compiler spelling. v413 asks a
narrow local question: does the already supplied, hash-attested `zun.hdi` retain
a second recoverable TH04 executable build in deleted directory entries or
unallocated FAT clusters?

This is target-side forensic routing only. Carved bytes remain below ignored
`.analysis/`, and the result grants no source or exactness credit.

## FAT12 scan

`scripts/probes/probe_th04_hdi_deleted_builds.py` verifies the runtime-image SHA,
parses the PC-98 FAT12 volume at the attested file offset `38912`, and walks the
FAT directly. The volume is `TOUHOU`, uses 1024-byte sectors and 8 sectors per
cluster, and contains the active `GENSO` directory.

The active TH04 executable set is exactly the four registered artifacts:
`MAIN.EXE`, `OP.EXE`, `MAINE.EXE`, and `ZUN.COM`; each is hash-checked against
`config/targets.toml`. There are no deleted entries inside `GENSO`. The only
deleted root directory entries are two NP2 memory-driver SYS files:
`?P2EMS.SYS` and `?P2HMA.SYS`.

Across 1,083 FAT-free clusters, only cluster 1694 begins with an MZ header. Its
DOS-declared MZ image is 1,702 bytes and is followed by an LHA stream. Parsing
the stream yields only:

| member | packed | original | CRC16 |
| --- | ---: | ---: | ---: |
| `GAMECB.BAT` | 243 | 301 | `0x112E` |
| `PMDPPZ.COM` | 16,173 | 28,587 | `0x66CC` |

The active `GENSO/CANBE.LZH` contains the same PMDPPZ payload identity (same
original size, CRC, and compressed SHA-256) plus a newer 219-byte `GAMECB.BAT`.
Thus the sole recoverable free-cluster MZ is an old CanBe/PMD compatibility
self-extractor, not an alternate TH04 game executable. No direct LZH/ZIP file
head exists at any other free cluster start.

Private receipt SHA-256:
`b322f20595c89ce1de0c8449a60d2433505cd3d774b9092402b2b08368a23a43`.

## Result and limit

The supplied HDI provides no second *recoverable file-start* TH04 build that can
independently corroborate `snd_load` `89 C3`, checkerboard `LOOP`, or carpet's
remaining low-level sequence. This closes the local deleted-file route without
changing the 27-byte MAIN gap.

The conclusion is intentionally bounded: FAT forensics cannot rule out partial
fragments of a deleted file whose original first cluster was later overwritten
or reallocated. Such fragments would not form a self-identifying executable and
are not sufficient provenance for exact reconstruction anyway.
