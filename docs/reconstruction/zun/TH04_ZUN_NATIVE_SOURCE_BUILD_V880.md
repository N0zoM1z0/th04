# TH04-only native ZUN component build

`config/native_zun_resident_sources.toml` and
`scripts/probes/probe_th04_native_zun_resident.py` compile the checked-in
resident `cfg_init.cpp` and `main.cpp` in TC4J Tiny model. Sixteen maintained
TH04 shared ASM units supply DOS files, resident allocation, graph state, and
text output. TLINK uses Borland `C0T.OBJ` and `CT.LIB`, with no `masters.lib`
and no ReC98 product source/header input.

Two isolated cold runs `native-zun-resident-v880-{a,b}-20260928` produce the
same complete 6,360-byte `RES_HUMA.COM` SHA-256
`d395d140ce761c97c659c0e2d02a3a2687415f4cb9d3d16d6f14976a1231bcd0`
and the same MAP SHA-256
`4e2ea7ff00b44ec608fefcdb62854bde3a43ddac5e367b6b6d2739422ca0af8c`.
Both C++ OMF files have dependency timestamp-comment drift but identical
link-relevant records; all sixteen ASM objects agree. There are no TLINK
warnings or unresolved symbols. Against the hash-attested decoded target
resident extent `0xB68..0x243F`, the natural-source COM has 4,301 differing
bytes. No exactness claim follows from the matching size.

`src/zun/launcher/usage.txt` is an authored TH04-only DOS help asset. The
source composite probe rebuilds selector, launcher tails, ONGCHK, ZUNINIT,
MEMCHK, and the natural resident, then derives COMCSTM offsets and the four
component directory. The first A/B cold run
`native-zun-composite-v881-a-20260928` produces identical 13,356-byte flat
payloads, SHA-256
`78986f2c7bfead7d655fb8358805a3f72b00f8927bc3f6b7fa417f0eed229835`.
Pinned DIET 1.45f packs both flats into the same 7,723-byte valid MZ,
SHA-256 `d6043dce43f1d321ac9df5d0d216e045a3aceb9c8ba38f3ea1d25b73a001d916`.
The outer MZ has zero relocation entries, a 32-byte header, `0000:0000`
entry, and no overlay. The packed target has 7,754 bytes, so this is a
non-byte-exact source-only launcher candidate.

`scripts/probes/prepare_th04_native_zun_hdi.py` checks the cold composite,
DIET receipt, candidate MZ, original HDI, and original ZUN.COM identities;
then it replaces only ZUN.COM and AUTOEXEC in a disposable FAT12 image. A
45-second normal `GAME.BAT` run under the pinned DOSBox-X PC-98 configuration
reaches the demo gameplay screen with the original OP/MAIN/MAINE files still
on the image. Boot markers pass and the candidate ZUN MZ has no relocations.
This is runtime observation for the launcher path (including GAME.BAT's
`-M/-I/-S/-O` calls), not byte equality or proof of every launcher option.
Run
,
SHA-256 `64c156693a274efe1f706e9d179ada1c9ccec5fb495007d36f99d6c0de48f42b`.

To replay the resident alone:

```sh
python3 scripts/probes/probe_th04_native_zun_resident.py \
  --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

python3 scripts/probes/probe_th04_native_zun_composite.py \
  --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME
```
