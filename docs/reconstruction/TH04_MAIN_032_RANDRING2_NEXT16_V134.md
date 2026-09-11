# TH04 MAIN_032 randring2_next16 reconstruction (v134)

## Scope

This packet reconstructs the target-authored `randring2_next16()` near function
in `MAIN_032_TEXT` for the local Japanese `MAIN.EXE` whose SHA-256 is
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
Target canonicality remains only `candidate-local-attested`.

The reviewed executable function is exactly:

- TLINK group/segment: `MAIN_03 / MAIN_032_TEXT 13A9:02C2`;
- Ghidra image: `0x23D52..0x23D5E`;
- load module: `0x13D52..0x13D5E`;
- file: `0x15552..0x1555E`;
- size: `0xD / 13` bytes;
- target slice SHA-256:
  `c27e97be00882e3e236241c44b423c0e1fb9b7d237e0c83ec209674e4993efc4`;
- overlapping MZ relocations: none.

Fresh target-attested Ghidra constructs exactly those 13 bytes through terminal
`RET` at image `0x23D5E`. The following target byte at `0x23D5F` is a `NOP` and
is not part of the function or the v134 exact owner. It remains target-derived
residual layout before the next public at `0x23D60`.

## Natural source

Maintained source is `src/main/math/randring2_next16.cpp`, SHA-256
`f9c0e49de9a435f7c59c3691fae73489d211bb8c72ae6513e481afa11ec1f7ce`.
It uses ordinary Turbo C++ source plus the repository's established 16-bit
pseudo-register source idiom; there is no inline assembly, target-derived byte
array, `#pragma codestring`, inert padding, fake return, target patch, or copied
target byte sequence.

TH04 keeps `randring_p` in a word while this routine advances only its low byte.
Expressing that storage explicitly gives TC86 the historical instruction shape:

- `MOV BX, [randring_p]`;
- `MOV AX, word ptr [randring + BX]`;
- `INC byte ptr [randring_p]`;
- `RET`.

The candidate OMF is a valid `TC86 Borland C++ 4.02` object with one
`MAIN_032_TEXT` segment whose SEGDEF and LEDATA are both exactly `0xD` bytes.
Raw object SHA-256 is
`9cf924571faef27c988f7a7650f42220a3e432946ead413e94418c629fb1ae40`;
dependency-timestamp-normalized SHA-256 is
`50916f22ce49baba7ec02ed9c2df951dff93e494cf9eb2e4b35ae19d29e6d388`.

## Residual ownership and interrupted replay recovery

The pinned residual assembler originally owns the same function plus the
following alignment `NOP`. v134 moves only the 13-byte `instance == 2`
`randring2_next16()` producer to C++ and leaves the target `NOP` plus all later
randring2 and pointnums code in residual assembler with zero reconstruction
credit. The source transform is hash-bound from scaffold
`6f36c64ef467bb30255becc4f888e3b6f9a292c67f804eb5e447cac7fc39b4f5`
to
`fb40b549a732c164b6899af73535b5e1639505c33bb75333e8a1083dc6b4d026`.

Recovery found two earlier receiptless focused materializations. In
`gptweb-v134-randring2-next16-focused-001`, TLINK reported `Group MAIN_03 exceeds
64K`. That materialization is not evidence against the current source: its
materialized `th04_main.asm` visibly predates a large set of already-accepted
source transforms and restores substantial old `MAIN_034_TEXT`,
`MAIN_036_TEXT`, and other target-derived bodies. Its `rr2next.obj` itself is
still exactly a 13-byte segment. `focused-002` is also receiptless and receives
no exactness credit. Neither run is reused as an Oracle result.

The final current-manifest focused run is
`gptweb-v134-randring2-next16-focused-003`. Its manifest SHA-256 is
`79011d46991036f1db4e944c66960fc45ac1ddd6e0b4a8b908d957844046d146`,
which matches the live v134 manifest used for promotion. The receipt SHA-256 is
`18f02eec9c38c863b38c68429913d7a0e1cd0ad79ed8aeddc0d13e419e0f1512`.
It selects the complete 106-owner dependency closure, and both isolated builds
pass exact map placement at `13A9:02C2`, all 13 raw bytes, empty ordered
relocation overlap, valid deterministic OMF, and identical candidate MAIN
SHA-256
`9a4c3a12dac1e2d5cfe4d482544a0d4104f2c2b5a6cfc6b249c395d30f0280cd`.

The required complete aggregate then passes at
`gptweb-v134-randring2-next16-aggregate-001`. Receipt SHA-256 is
`730508ad10f6c4edd2a810f3e44835fb74a4eed29e54322b6a81a36063ff496d`.
All 170 default exact owners pass twice with no regression; aggregate A/B
candidate MAIN SHA-256 is
`c807ba0d2320d744d20f18c711a7409b5af13c7b6bd8d8eab69e05055f4ef51a`.

## Independent function review

Fresh Ghidra metadata reports body min/max `0x23D52..0x23D5E` and 13 body
addresses. The v134 aggregate TLINK map independently places the public
`randring2_next16()` at `13A9:02C2`, and the exact byte owner has the identical
0xD extent. The ordinary automatic exact gate therefore admits this function;
no sparse/cross-linked override is needed.

The retained review reports **298/300 exact reviewed authored functions
(99.333333%)**, automatic=149, manual=149, strict rejections=0. Report SHA-256 is
`96aa76d9bde070cf141758952fa8f861eb35c2d8f9d8c3a2c4582969ae5665e6`.

## Shared-tail negative evidence

The same recovery packet deliberately investigated the nearby
`pointnums_add_yellow()` / `pointnums_add_white()` seam instead of collecting
only another easy helper. The target shows a dual-entry physical procedure:
yellow begins at image `0x23D90`, but its instruction at `0x23DA8` jumps to
`0x23DBE`, a shared tail also reached by the white entry at `0x23DAA`, and that
shared code continues through `RET 6` at `0x23DEE`.

A straightforward natural two-function candidate emitted `0xB6` bytes and did
not model the historical ownership. White-only pseudo-register candidates emit
`0x49` bytes rather than the target `0x47`, with the BP-frame prologue owned by
the public entry rather than by the shared tail. Production-profile variants
including optimization and `-k` changes preserve the mismatch. These are
source-shape negative results, not permission to duplicate the tail or force an
overlapping exact extent. The yellow boundary therefore remains provisional.
Evidence is recorded in `ev-th04-main-pointnums-shared-tail-v134` alongside the
older target-first `ev-th04-main-pointnums-shared-tail-v104`.

## Scope limits

This packet establishes repository exact-unit evidence for the 13-byte
`randring2_next16()` owner and independent function exactness for that function.
It does not establish standalone TH04 product closure, runtime-storage identity,
a runtime scenario, whole-image exactness, or pristine-release provenance.
Factory Truth-Kernel acceptance remains a separate post-commit plane.
