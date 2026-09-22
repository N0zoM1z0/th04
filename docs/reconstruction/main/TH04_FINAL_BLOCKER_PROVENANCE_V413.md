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

## v414 partial-archive remnant scan

v413 could only rule out intact deleted directory entries and file starts at a
free-cluster boundary. v414 addresses the remaining forensic loophole: a deleted
LHA self-extractor whose first cluster was later overwritten while later archive
member headers survived in physically free clusters.

`scripts/probes/probe_th04_hdi_partial_trial_remnants.py` verifies the same pinned
HDI and FAT12 geometry, groups all 1,083 free clusters into four physically
contiguous runs, and scans each complete run. This intentionally crosses 8 KiB
cluster boundaries rather than searching clusters independently. It searches for
`GEN_TS1`, `TAIKEN`, CP932 `体験版` / `３面まで`, and the four TH04 executable
filenames, and independently parses plausible level-0/1 `-lh?-` headers at every
offset.

No trial or executable marker is present. Exactly six LHA member headers survive:

| file offset | member | method | packed | original |
| ---: | --- | --- | ---: | ---: |
| `0xD3ECDF` | `OMAKE.TXT` | `-lh5-` | 8,551 | 21,523 |
| `0xD45267` | `怪綺談.txt` | `-lh5-` | 8,259 | 27,195 |
| `0xD4C6CC` | `README.TXT` | `-lh5-` | 2,996 | 7,145 |
| `0xD502A6` | `GAMECB.BAT` | `-lh5-` | 243 | 301 |
| `0xD503BB` | `PMDPPZ.COM` | `-lh5-` | 16,173 | 28,587 |
| `0xD55DB7` | `RESET.BAT` | `-lh0-` | 70 | 70 |

Only `GAMECB.BAT` has its computed next-member offset exactly equal to another
surviving header, `PMDPPZ.COM`, matching the old CanBe SFX classified in v413.
The other four are isolated archive remnants and none is a TH04 executable.

Private receipt SHA-256:
`2c1cc47ac78c4718f44781d61b1c45f122749d89bdabb82753927a18299f1112`.

This strengthens the local-disk negative: neither an intact alternate TH04 file
nor a surviving trial/executable LHA member table is recoverable from free FAT
data. Anonymous compressed fragments without a surviving filename/header remain
unattributable and therefore cannot serve as independent reconstruction
provenance. The MAIN byte count is unchanged.

## v415 anonymous raw-code remnant scan

v413/v414 closed intact deleted files, free-cluster file starts, surviving LHA
member headers, and trial/executable text markers. One narrower loophole remained:
a deleted build could have lost all metadata while one or more **uncompressed code
fragments** survived in FAT-free clusters.

`scripts/probes/probe_th04_hdi_raw_code_remnants.py` verifies the same pinned HDI
and FAT geometry, concatenates each of the four attested free-cluster runs, and
searches their raw bytes for four final-blocker signatures:

- a short `snd_load` DOS-open sequence with the filename word wildcarded and
  either `89 C3` or `8B D8` accepted for the handle copy;
- a longer form continuing through driver dispatch, DOS read, `POP DS`, and close,
  again with data-symbol words wildcarded;
- checkerboard's exact `MOV ES,DX / MOV CX,6 / ES:[DI] dword store / ADD DI,8 /
  LOOP` core;
- carpet's distinctive prologue through `PUSH DS/POP ES`, two `MUL BX`, the target
  register directions, `MOV CX,24`, and `LODSB`, with only the two data offsets
  wildcarded.

Across all **1,083** free clusters, every search returns zero hits. Private
receipt SHA-256:
`23a477e59cddd3ff4e124388ab9e11d11ed37b4581b2175a39bb5e61e40deedc`.

This closes the local anonymous-uncompressed-code route. It does not exclude
compressed fragments or bytes that have been overwritten, and therefore remains
negative provenance evidence only. The 27-byte MAIN gap is unchanged.

## v416 allocated-slack raw-code scan

v415 covers all FAT-free clusters, but DOS file replacement can leave old bytes in
the unused tail of a **still allocated** final cluster. Directory allocations can
likewise retain bytes after the first end-marker entry. v416 scans this complementary
space rather than broadening the target/source acceptance policy.

`scripts/probes/probe_th04_hdi_allocated_slack.py` recursively walks the pinned FAT12
volume and validates an inventory of **163 regular files** and **7 directories**. It
then scans 169 logically unused regions totaling **880,571 bytes**: each regular
file's final-cluster tail plus every directory tail after the first `0x00` end marker.
The patterns are exactly the v415 final-blocker signatures: wildcarded short/long
`snd_load` forms accepting either `89 C3` or `8B D8`, the exact checkerboard compact
`LOOP` core, and the distinctive carpet low-level prefix.

All four searches return zero hits. Private receipt SHA-256:
`692ea2a8e4153878b550786feccb376cedb6dd82e86a26074e43700726a30a0d`.

Together, v415 and v416 leave no anonymous **uncompressed** second-build blocker code
in either FAT-free space or logically unused allocated slack on the supplied HDI.
This remains negative provenance evidence only; compressed, overwritten, or bytes
inside unrelated live logical file contents are outside the claim, and the 27-byte
MAIN gap is unchanged.

## v419 active-file and active-archive audit

v413-v416 cover deleted directory entries, FAT-free runs, anonymous raw code,
and allocated slack. v419 closes the complementary **active logical file**
surface on the same hash-attested HDI.

`scripts/probes/probe_th04_hdi_active_dev_remnants.py` recursively walks the
active FAT12 directory tree and validates an inventory of 170 entries: 164
regular files and 6 directories. No active file uses a development/build
extension such as `.C`, `.CPP`, `.H`, `.ASM`, `.OBJ`, `.MAP`, `.PRJ`, `.MAK`,
`.LIB`, or `.BAK`, and no `GEN_TS1.EXE` trial executable is present.

The two active LZH archives are also parsed by member table. `GENSO/CANBE.LZH`
contains only `PMDPPZ.COM` and `GAMECB.BAT`; `GENSO/OMAKE2.LZH` contains music
and text data only. Neither archive contains a TH04 executable or development
artifact.

Private receipt SHA-256:
`c443839a472e66a0f199030c9abd5fa17e0348912c469362250de862f44a072f`.

Together with v413-v416, the supplied HDI offers no attributable alternate
producer through active files, active archives, deleted entries, free space, or
allocated slack. This is negative provenance evidence only and leaves the
27-byte MAIN gap unchanged.

## v495 pinned ReC98 / MAGNet source-provenance audit

v413-v419 exhausted the supplied HDI as an attributable alternate-producer
source. v495 tests a different provenance class: pinned public ReC98 history
plus the only explicitly documented TH04 source-code leak in that history.

`scripts/probes/probe_th04_final_blocker_upstream_provenance_v495.py` binds the
pinned ReC98 checkout at
`b6ba5b0a529edbb31efdf8c0e939263804f8ee47` and verifies the exact history
rather than relying on current comments or blog wording.

For checkerboard, decompilation commit
`45df9ec0c688e7e463c690112ed61d3a734b1cc6` introduces
`asm { loop put_loop; }`; its parent still carries the target-derived
`sub_12076` body in the monolithic `th04_main.asm`. For Stage 4 carpet,
decompilation commit `2aae476a855101c2d86fb192a71b2e74d34feaca`
introduces the surviving `PUSH DS / POP ES`, `MUL BX`, `LODSB`, `SHL DI,1`,
and `LOOP` statements while its parent likewise carries target-derived
`sub_EA8A` assembly. These commits are useful reconstruction history, not an
independent historical source witness.

The independently documented `[MAGNet2010]` source leak is narrower. Pinned
`CONTRIBUTING.md` states that the 2010-05-02 broadcast briefly showed TH04
`MAIN.EXE` source for demo recording and EMS setup. The pinned tree contains
13 TH04 `[MAGNet2010]`-tagged identifiers, all in demo/input/EMS material and
none in checkerboard, carpet/stages, or `snd_load`. A tempting apparent
counterexample is the `_asm` block currently present in `demo_end()`, but Git
history proves that block first appears in ReC98 commit
`4c888ee4ade6aca57b56eae3ecc5673f0dafdf9b` in 2023 rather than in the leak.

Final replay:
`v495-final-blocker-upstream-provenance-002`; receipt SHA-256
`cbf5d82e84de8209f96ed6818a72ef0cc7dfb4534ff944c544a0a76deef281d7`.
The SHA-bound source/history bundle is
`5e02464e1f31c2861ab056ff4b726775c6f696b8ef1dab19cad97cda094d0649`.

The result deliberately changes no source ownership or exact-byte accounting.
Pinned upstream history strengthens the hypothesis that checkerboard/carpet
contain hand-selected low-level instructions, but it does not provide the
independent source-origin evidence required by this repository. The complete
MAIN gap therefore remains 27 bytes: checkerboard 2, carpet 23, and `snd_load`
2. Reopen this route only if a genuinely new historical source artifact appears.
