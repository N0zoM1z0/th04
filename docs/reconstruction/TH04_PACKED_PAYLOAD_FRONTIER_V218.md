# OP, MAINE, and ZUN unpacked payload frontier (v218)

## Claim boundary

The three pinned local targets are DIET-packed MZ files. This packet compares
their load-invariant, independently emulated payloads with the **v214 A/B cold
ReC98-overlay candidates**. Payload offsets below are not packed-file offsets.
The target DIET stub's relocation *application* order is not evidence of the
original unpacked MZ relocation-table order. None of this packet promotes a
product unit or proves original packed-file equality.

Run `python3 scripts/preflight.py`, then, for each `th04-op`, `th04-maine`, and
`th04-zun`, run `python3 scripts/boundary_review/unpack_diet.py ARTIFACT
--output-dir .analysis/reconstruction/v218-ARTIFACT-diet`. This runs the target
stub at load segments 1000h and 2000h and requires identical unrelocated bytes
and relocation sites. `scripts/probes/compare_diet_payloads.py` checks the
target manifest, DIET receipt, candidate MZ/COM integrity, raw payload, and
relocation-site multiset; supply the A/B candidate and, for OP/MAINE, its MAP.
The retained reports are `.analysis/reconstruction/v218-th04-{op,maine,zun}-payload-compare-{a,b}.json`.

| Artifact | Attested target payload SHA-256 | Size | DIET relocs | A/B candidate difference |
| --- | --- | ---: | ---: | --- |
| `OP.EXE` | `13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74` | `0x10DA4` | 804 | 7 raw bytes; relocation-site multiset equal |
| `MAINE.EXE` | `7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c` | `0xF3CE` | 559 | 5 raw bytes; relocation-site multiset equal |
| `ZUN.COM` | `baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e` | `0x346E` | 0 | 0 raw bytes; payload equals candidate flat COM |

A and B candidate files are byte-identical for each artifact. The candidate
files are generated from pinned ReC98 plus overlay, not from a standalone
checked-in TH04 product tree. OP and MAINE DIET application order differs from
candidate MZ table order; the original unpacked target table is unavailable.
For ZUN, the candidate composite contains an external ONGCHK binary plus
ReC98's IDA-derived ZUNINIT/MEMCHK assembly. Its payload equality is a useful
format/layout control but grants **no authored-source credit** for those
components. This classification comes from pinned ReC98 commit
`b6ba5b0a529edbb31efdf8c0e939263804f8ee47`, its `Tupfile.lua`
composite inputs, and the ASM file headers. The separate RES_HUMA C++
producer is still candidate source.

## Remaining raw positions

The owner names are from the **candidate MAP**, so target ownership at padding
seams remains provisional.

| Payload offset | Target → candidate | Candidate owner / interpretation |
| --- | --- | --- |
| OP `0x2D59`, `0x34AF` | `00 → 90` each | `th04_op.asm` `_TEXT` `EVEN` before `SUPER_PUT` and `_BGM_BELL_ORG`; current TASM listing offsets `2AE7`, `323D` |
| OP `0xBFB7`, `0xBFB9` | `31 → 33` each | `th04/op_music.cpp` `OP_MUSIC_TEXT`, `nopoly_B_put()` at payload `0xBFA7`; two equivalent XOR-register opcode directions from the `__memcpy__` intrinsic |
| OP `0xDE8B..0xDE8C` | `89 C3 → 8B D8` | shared `SND_LOAD` at payload `0xDDCA`; also blocks MAIN and MAINE; see [shared review](TH04_SND_LOAD_SHARED_V206.md) |
| OP `0xFB97` | `90 → 00` | `th04_op.asm` `_DATA` `EVEN`, current TASM listing offset `0357` |
| MAINE `0x0CBD`, `0x2D11` | `00 → 90` each | `th04_maine_master.asm` `_TEXT` alignment bytes |
| MAINE `0xD1D3..0xD1D4` | `89 C3 → 8B D8` | shared `SND_LOAD` at payload `0xD112` |
| MAINE `0xE933` | `90 → 00` | `th04_maine_master.asm` `_DATA` alignment byte |

The OP `nopoly_B_put()` source currently comes through the ReC98 wrapper
`th04/op_music.cpp` from `th02/op/m_music.cpp`; it is candidate material. A
bounded TC4J `#pragma option -G` probe just before this function preserved both
`33` bytes but changed later code: candidate `OP_MUSIC_TEXT` grew from 1701 to
1704 bytes. Its baseline wrapper reproduced the original 1701-byte CODE
contribution exactly. A TASM 5.0 `xor di,di; xor si,si` control also emits
`33 FF 33 F6`. These are negative controls, not license to encode target bytes
manually. The retained source/object probe SHA-256 values are
`4e592007ed62c611fc31360a9546306b07346f1697394b18d86360ab50e9ec34`
and `ec8dbc3e9b576a33dafdde1174bcb7868cc037a9b904e1dec372d46f5b51bdbd`.
The probe inputs and objects are under
`.analysis/reconstruction/probes/v219-op-music-option-g/`.

## Next acceptance work

Recover natural source and physical boundaries for OP/MAINE owners, starting
with the shared `SND_LOAD` producer and OP music function. For ZUN, reconstruct
component ownership/source independently; do not bulk-port the IDA-derived
assembly or embedded ONGCHK binary as authored code. Establish standalone
checked-in product builds. A genuine whole-file exact claim also needs a
replayable DIET packer/configuration and raw comparison of the packed file.
The later [v228 packer round trip](TH04_DIET145F_ROUNDTRIP_V228.md) calibrates
the DIET options, [v231](TH04_DIET145F_MZ_PARTITION_V231.md) partitions the
OP/MAINE candidate MZ residual, and
[v232](TH04_DIET_RELOCATION_OWNERS_V232.md) projects ordered relocations onto
candidate MAP owners. ZUN's ReC98-overlay candidate packs raw equal, but
payload equality alone still grants no authored-source credit.
