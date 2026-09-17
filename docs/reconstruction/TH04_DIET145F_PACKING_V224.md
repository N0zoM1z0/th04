# DIET 1.45f packed-file replay (v224)

This note preserves the first `-B` experiment. The subsequent
[v228 round trip](TH04_DIET145F_ROUNDTRIP_V228.md) calibrated artifact-specific
options: OP/MAINE use `-B -G`, ZUN uses `-B`. Its v226 candidate results and
v228 target-derived controls supersede this note as the current packaging
frontier.

## Claim and inputs

The public DIET 1.45f archive is pinned in
[config/diet145f.toml](../../config/diet145f.toml): archive SHA-256
`9ec134a324035a22a7509868cfd361b01aa11c7fb9bd70529a7533698540b9a7`,
DIET.EXE SHA-256
`a3fabbb9e4209ca6654c34f1d0945868732422dff6fe0a7fe0f5bcd2d48d2803`.
The archive is an external release mirror, not independent proof of the
studio's original tool copy. The bundled [author's user guide](https://files.mpoli.fi/unpacked/software/dos/compress/diet145f.zip/diet145f.doc)
documents `-B` as comparing compressed size in bytes and `-G` as changing
the self-extractor. Tool binaries remain ignored under `.analysis/toolchain/`.

`scripts/probes/replay_diet145f.py` verifies the archive member, the installed
binary, the pinned DOSBox-X PC-98 binary/configuration, each manifest target,
and both supplied candidate formats. It packs two isolated candidate copies
serially with `DIET.EXE -B`, checks the guest success message and MZ integrity,
then compares the whole packed files to each other and to the pinned target.
The v224 A/B inputs are the v214 two-cold **ReC98-overlay** outputs, not a
standalone TH04 product build. Commands, hashes, and environment are in each
receipt under `.analysis/reconstruction/diet-replay/v224-{zun,op,maine}-a-b/`.

| Artifact | Candidate A/B input | Packed A/B | Target packed | Raw target verdict |
| --- | ---: | ---: | ---: | --- |
| ZUN.COM | 13,422 identical flat COM bytes | 7,754 identical bytes, SHA-256 `0a12e9a489d3b704a77cf04ca3062ee48f298a9df6d237dc7dad46986e2d116e` | 7,754 | **equal** |
| OP.EXE | 73,636 identical MZ bytes | 42,148 identical bytes, SHA-256 `99ae75ba241163bcec6cca1168f3375fffe9c8228472074d39bf99ef1df00112` | 42,290 | different |
| MAINE.EXE | 65,998 identical MZ bytes | 37,890 identical bytes, SHA-256 `32e4b83aa583022534eac1f0601b1c77e44d31bc1283c1d9c16c791e29c2394c` | 38,035 | different |

The independent strict whole-MZ comparator also returns `raw_exact=true` for
the v224 ZUN A file; its private report is
`.analysis/reconstruction/diet-replay/v224-zun-strict-compare.json`.
A one-byte synthetic mutation of the ZUN input at flat offset `0x400` made
the packed output differ and `--require-exact` exit 1. The packer comparator
therefore rejects a real candidate difference.

The `-B` replay is a **packaging Oracle**. ZUN's equal candidate flat composite
includes external ONGCHK.COM and IDA-derived assembly, so this result gives no
authored-source credit and does not promote a unit. OP/MAINE still have
unresolved input payload bytes, and the original unpacked target MZ header and
ordered relocation table have not been recovered. Their packed length
differences cannot be assigned solely to the 7/5 unpacked payload bytes.

## Bounded controls and next work

Without `-B`, DIET reported “No files to be processed” for the ZUN candidate
under this PC-98 DOSBox-X profile. `-B -G` produced 7,849 bytes and
`-B -XC` 7,647 bytes, both different from the target. The `-B -X` control
also matched all ZUN bytes; the historical command line is not proven by these
equivalent outputs. OP/MAINE `-B -G` produced 42,251/37,985 bytes, still
different. The target and `-B` OP streams share an 8,486-byte same-offset run
beginning at packed offset `0x77`; MAINE shares 2,470 bytes there. These
support tool-family compatibility, not OP/MAINE exactness.

Use this replay as the final pack step after recovering checked-in product
source, complete link/header/relocation topology, and a cold build. The
user-facing completion target is approximately 99% exact authored code across
the artifacts, a standalone compile/rebuild, and playable DOSBox-X execution;
the current packaging success alone satisfies none of those broad gates.
