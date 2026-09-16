# TH04 CIRCLE rolling tiny-sprite blitter reconstruction (v193)

## Scope

v193 closes the final replay-only CIRCLE_TEXT residual immediately before the
already exact `circle.cpp` contribution. The reviewed physical owner is:

- map `0AAF:193A..1B59`;
- MZ load-module `0xC42A..0xC649`;
- target file `0xDC2A..0xDE49`;
- size `0x220 / 544` bytes;
- target SHA-256
  `8c7fe30f73f9eb2a60cfd02b75503ed4ef46ffbea8968758539730d93a645a75`;
- ordered MZ relocation overlap: none.

The first two bytes are the private code-segment state word
`srpt32x32_vram_topleft`. `Z_SUPER_ROLL_PUT_TINY_32X32_RAW` then occupies load
`0xC42C..0xC545`, size `0x11A`, SHA-256
`058ca6591a23060076f3d2ae3f2ae71c68fec48acf68769d04a3187f2d049e76`.
`Z_SUPER_ROLL_PUT_TINY_16X16_RAW` follows at `0xC546..0xC649`, size `0x104`,
SHA-256
`76cfe5c30c8a1df177f9256e48d2e6e26a78c830d511b38d4f378b221d746cdd`.
The next byte, load `0xC64A`, is the already exact `circle.cpp` owner.

The 32x32 public contains three non-public helper return sites inside its TASM
PROC: GRCG color expansion at `0xC4C0`, the even-X row helper at `0xC4DA`, and
the odd-X row helper at `0xC50C`. They are internal control-flow labels rather
than independent authored-function entries.

## Analysis coverage and callers

Fresh target-bound Ghidra does not construct the 32x32 public at `0x1C42C`.
It does construct the complete 260-byte 16x16 body at `0x1C546..0x1C649`.
Ghidra reports one caller for the 16x16 public, while target raw call decoding
finds seven near-call anchors at load offsets `0xD914`, `0x105A3`, `0x10C99`,
`0x10CA6`, `0x12D1F`, `0x12DDF`, and `0x12E27`. The 32x32 public has one raw
near-call anchor at `0x12D8F`. These discrepancies are retained as target-analysis
coverage negatives and receive no exactness credit.

## Producer classification

The complete 544-byte physical owner is classified as evidence-backed
original-style symbolic assembly.

Independent TH05 original-target bytes preserve the same physical layout: a
private word, a 0x11A-byte 32x32 public, then a 0x104-byte 16x16 public. Across
the complete TH04/TH05 544-byte windows only ten bytes differ, grouped into five
16-bit words. Two words are the linked `super_patdata` address and three are the
private code-segment state address. All other 534 bytes are identical, including
the 32x32 GRCG, even-row, and odd-row helper bodies.

The TH02 original target independently preserves the inner blit pipeline of the
older MASTER.LIB `super_roll_put_tiny()` family. The candidate MASTER.LIB source
and ReC98 history are used only to explain lineage: the TH04/TH05 producer
changes the distance/argument ABI and contains ZUN-specific optimized/adapted
16x16 and 32x32 paths. No reconstruction-era source claim is imported as
historical authority or exactness evidence.

The attested DIET-decompressed TH04 OP.EXE, MAINE.EXE, and ZUN.COM payloads were
searched for bounded 32x32/16x16 core signatures. None contains the MAIN
producer. This is artifact-specific negative routing evidence; no MAIN credit
transfers to those artifacts.

## Maintained symbolic source and standalone producer probe

Maintained source is `src/main/formats/z_super_roll_put_tiny.asm`, SHA-256
`d8afcbeea8e2edb96bb4b9cfc80f2f121b65175f9cd427aa0a90bb8e827ad7b4`.
It is symbolic TASM source with semantic constants and labels. It contains no
target-derived byte array, inline assembly escape, codestring, padding payload,
ABI lie, or target patch.

A standalone TASM32 5.0 probe emits a valid 915-byte Intel OMF object, SHA-256
`348c7ca50f950dccf5e8b4087e94099499279e133a2b81b42c57c81df676e651`.
Its CIRCLE_TEXT contribution is exactly 544 bytes. The public offsets are +0x2
for the 32x32 routine and +0x11C for the 16x16 routine. Before linking, exactly
five unresolved 16-bit address words differ from the target and every other
fixed byte matches. This is producer evidence, not linked exactness.

The exact replay object SHA-256 is
`ed10e22742453021badd85079ae5d4dab52b9eaa5d54d2f788039b37d8e59328`.
The final split leaves `cirsuf186.obj` as a zero-code structural anchor at map
`0AAF:1B5A`; no historical auxiliary ownership gate is dropped. Trigger-scoped
ordered overrides replace the old replay residual with the exact zsuper owner
only when v193 is selected.

## Replay and Oracle closure

Focused run `gptweb-v193-zsuper-focused-candidate-001` selects 127 owners and
passes both isolated cold builds with `failures=[]`. Receipt SHA-256 is
`49f1ca8c58aef0ad6da7d593c7eb4cfda673074ae83571736d67e9389da9ed08`.
A/B `zsuper.obj` SHA-256 is
`ed10e22742453021badd85079ae5d4dab52b9eaa5d54d2f788039b37d8e59328`;
focused MAP SHA-256 is
`f8cf2159a6b335cb5073b3867e7f2b075c101c1781ce34c26a8a67a01abe47d7`.

Candidate no-unit aggregate `gptweb-v193-zsuper-aggregate-candidate-001`
temporarily enables the candidate and passes all 231 candidate-state defaults
twice. Receipt SHA-256 is
`47f8116a85c248c375166cf5ba9ad36cf035ac480b6ac7e57c51b7f732b7cc9e`.
The enabled manifest SHA-256 is
`dd41a32e183475beec6b1a03b4daaac222338c7a9b1fa0b3a1438c19e01d22a6`;
the pre-promotion candidate manifest is restored byte-for-byte to
`ab2ccf6b795c5bc52a7d7f80a8b539d8596b3c09a5d613c0cd62696239962bc8`.

Post-promotion aggregate `gptweb-v193-zsuper-aggregate-final-001` passes all
tracked default exact owners twice with `failures=[]`. Receipt SHA-256 is
`f97b53497ee3f2ec12c76760278202e3b16641b2f43c841293c993ce1c26cfcb`.
Tracked exact-manifest SHA-256 is
`dd41a32e183475beec6b1a03b4daaac222338c7a9b1fa0b3a1438c19e01d22a6`;
A/B final MAP SHA-256 is
`ec91105fd65ccf795cba7e1034485df07115b25528f7b8564d3bbe622afcb29e`;
candidate MAIN remains
`205e42067b0eb3534dc83deba125ebf845c1c153f6515ebe60430d3a79f21bd9`.

## Accounting and limits

The two logical zsuper entries are not part of the maintained authored-C/C++
function ledger, so v193 does not change that numerator or denominator. MAIN
remains `75,209 / 80,694` exact reviewed authored C/C++ bytes and `456 / 479`
exact reviewed C/C++ functions. The two logical boundary observations move from
the reconstruction queue to the separate ASM-attestation plane.

Generated progress reports 28 exact original-style ASM physical units / 4,196
bytes. OP.EXE, MAINE.EXE, and ZUN.COM remain independent reconstruction queues
and receive no MAIN credit.

Repository-native exact physical ownership is established for this v193 owner.
This does not establish standalone TH04 product compile/link closure, whole-image
exactness, runtime-storage identity, runtime-scenario validation, portable
runtime, independent pristine-release provenance, or Factory Truth-Kernel
acceptance.
