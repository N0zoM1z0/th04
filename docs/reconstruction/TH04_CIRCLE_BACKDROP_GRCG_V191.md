# TH04 CIRCLE backdrop and GRCG producer reconstruction (v191)

## Scope

v191 closes the complete residual CIRCLE_TEXT window left by v190 before the
exact v188 item-splash renderer:

- map `0AAF:1658..168B`;
- MZ load-module `0xC148..0xC17B`;
- target file `0xD948..0xD97B`;
- physical size `0x34 / 52` bytes;
- target SHA-256
  `fddd050002423d2c6b72e78bde962a78d23a1305a0442ce6818e825ea528fbae`.

The window has no MZ relocation and contains exactly four logical functions plus
two source-owned alignment bytes:

- `mugetsu_gengetsu_backdrop_colorfill()`: load `0xC148..0xC155`, 14 bytes;
- `grcg_setmode_rmw()`: load `0xC156..0xC15A`, 5 bytes;
- TASM `EVEN` NOP at load `0xC15B`;
- `grcg_setmode_tdw()`: load `0xC15C..0xC160`, 5 bytes;
- TASM `EVEN` NOP at load `0xC161`;
- `grcg_setcolor_direct_raw()`: load `0xC162..0xC17B`, 26 bytes.

Exact `ITEM_SPLASHES_RENDER` begins at the next byte, load `0xC17C`. Fresh
Ghidra constructs the RMW and direct-color functions but misses the backdrop and
TDW entries. These are analysis observations only and receive no exactness
credit.

## Natural backdrop owner

Maintained natural source is
`src/main/boss/mugetsu_gengetsu_backdrop.cpp`, SHA-256
`125342bca05cf8aeae6f037fe2bb4fa9648ad46fb112570c409ddfd4800278ea`.
It uses the same ordinary Borland pseudo-register mechanism already proven by
other exact TH04 backdrop callbacks, with the target-proved Pascal near ABI.

A bounded TC4J probe emits exactly 14 CODE bytes. All fixed bytes are already
identical to target; the only pre-link difference is the ordinary 16-bit near
call fixup. The linked target slice SHA-256 is
`a7926eb6c970a266b1c437a8cd6137fb9715f73b9990f660d2e17fbdb068c184`.
The independent TH05 original target preserves the same 14-byte producer shape
and constants with only the linked call displacement changed.

The first focused replay attempt is retained only as control-plane negative
evidence. The definition initially omitted `pascal`, so TC4J emitted the correct
body but TLINK could not resolve the existing Pascal caller symbol
`@MUGETSU_GENGETSU_BACKDROP_COLORF$QV`. Existing TH04 caller declarations and
OMF EXTDEF evidence prove the Pascal ABI; adding the real calling convention
fixed linkage without changing the body or manufacturing a symbol alias.

Target Ghidra still has no function entry at `0x1C148`. A fail-closed
`reviewed_exact_no_ghidra` trial binds exact owner, TLINK public, gap-free raw
16-bit decode through RET, and the next exact public at `0x1C156`. The function
review report SHA-256 is
`e5591b30d05760dadceb1a9cb97a9f68e4adda3200a95f3dcbfd8c8014e1e24c`.
Only the intended `th04-main-fn-1c148` row is merged into the maintained
function ledger; the semantic ledger keeps the full `colorfill()` name rather
than the Borland/TLINK truncated public spelling.

## Original-style GRCG owner

Maintained symbolic source is `src/main/hardware/grcg_modecolor.asm`, SHA-256
`626042137517600f06a8c3722a6d40cc78ef31c1fa00473feafcb2a91d4477e4`.
It owns the complete physical `0x26` region from RMW through direct-color,
including both real `EVEN` bytes.

Independent TH04 and TH05 original targets contain byte-identical complete
38-byte producers, SHA-256
`d1e7db8acfd42ce47f3a01dce663ab89809b05b4684ab47b534ad8577418bc44`.
TH04 also repeats the same RMW and direct-color instruction shapes in its
segment-3 copy. ReC98 assembly is used only to form symbolic hypotheses, not as
historical-source authority.

Legal natural-C++ probes do not reproduce this producer. Standard `outportb()`
mode setters emit 14 bytes and load port `0x7C` through DX rather than the
target immediate-port form. A legal arithmetic direct-color expansion emits 42
bytes using `MOV AL,AH; AND AL,1; NEG AL` rather than the target
`SHR AH; SBB AL,AL` sequence. Historical `_outportb_()` and carry-to-tile
helpers rely on byte-emission intrinsics and are excluded by campaign policy.

Standalone TASM32 5.0 emits one 38-byte CIRCLE_TEXT LEDATA contribution that is
byte-identical to both original targets, with three public entries and no
external/fixup dependency. Focused and aggregate linked object SHA-256 is
`3407ea75991bb274ab66dcab984ef26c92bfdefb7e7889f34ffd2eb9263c60c1`.

## Replay ownership and exact Oracles

The v190 map previously assigned the entire `0x34` window to zero-credit
`cirsuf185.asm`. v191 splits the natural 14-byte backdrop first, retaining the
GRCG tail as an auxiliary residual, then transfers the remaining 38 bytes to the
symbolic GRCG owner. The residual assembler object becomes zero-CODE after both
units are active.

Older v188/v190 auxiliary contracts remain intact when v191 is absent. The
ordered fail-closed override mechanism introduced by v190 redirects the prefix
only when the corresponding v191 unit is selected, so historical cold replay is
not weakened.

Authoritative focused replay
`gptweb-v191-circle-backdrop-grcg-focused-candidate-002` selects 122 owners and
passes two isolated cold builds with `failures=[]`. Receipt SHA-256 is
`4a2c62dd3b93e517911bceb76f0c67916ff42edf44f62c9c1332c20066edc373`.
A/B `mgbd.obj` SHA-256 is
`cf6488438d5bb6886f3721be3091c90ea3b97bc42943efd37256f498cc0bc638`;
A/B `grcgmc.obj` SHA-256 is
`3407ea75991bb274ab66dcab984ef26c92bfdefb7e7889f34ffd2eb9263c60c1`;
focused MAP SHA-256 is
`b9d44e7e349a3a60e53748020b4b803e73f3f05eada9b4d2c2c867bab975e92a`.

Candidate-state no-unit aggregate
`gptweb-v191-circle-backdrop-grcg-aggregate-candidate-001` passes all 226
candidate-state defaults twice. Receipt SHA-256 is
`187eb7c9cee1c020a01a192f77bc8eeeb5d0bfb152bbd80f41a42504bf33e850`.
The temporary enabled manifest SHA-256 is
`5a36c51af2223f247ea3904fa7ab018c7a0b46490976ba9d9698afd0f6581fcf`;
the pre-promotion manifest is restored byte-for-byte to
`df84193236f394fd6ba6bd4cbacd8eeeff582d7c1333af4aff6cc19c85490c08`.

Post-promotion no-unit aggregate
`gptweb-v191-circle-backdrop-grcg-aggregate-final-001` again passes the tracked
default cohort twice from ledger extents with `failures=[]`. Receipt SHA-256 is
`7f99af8665ff9cb31959706e3bf7c1d6e537594d4bc0531163ab1e6729ac938a`.
Tracked manifest SHA-256 is
`5a36c51af2223f247ea3904fa7ab018c7a0b46490976ba9d9698afd0f6581fcf`;
A/B MAP SHA-256 is
`41dfb776c3ed81209e5ce3aaf89fdec00b41245506b8d8456933c2ef9acdfa9f`;
candidate MAIN SHA-256 remains
`205e42067b0eb3534dc83deba125ebf845c1c153f6515ebe60430d3a79f21bd9`.

## Accounting and limits

The natural backdrop adds 14 exact authored-C/C++ bytes and one exact reviewed
function. The three GRCG logical entries move from the C/C++ reconstruction
queue to the separate original-style ASM attestation plane; the two NOPs belong
to that physical ASM owner.

Repository-native exact ownership is established for the two v191 physical
owners. This does not establish standalone TH04 product compile/link closure,
whole-image exactness, runtime-storage identity, runtime-scenario validation,
portable-runtime validation, independent pristine provenance, or Factory
Truth-Kernel acceptance. OP.EXE, MAINE.EXE, and ZUN.COM remain independent
artifact queues and receive no MAIN credit.
