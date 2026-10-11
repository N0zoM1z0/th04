# TH04 native DOS build readiness

2026-09-27 compiler and source-graph observation. This is a product-build
investigation, not a new exactness or runtime acceptance claim. The two MAIN
authored-function residuals remain deferred for this lane.

## Acceptance model

The TH095 Windows i386 product build supplies the useful separation: close the
production source graph, compile every declared translation unit with the
pinned toolchain, link without unresolved symbols, verify the output format,
then validate the reconstructed executable with the same legal game data and
runtime scenarios as the original. Function-level raw matching has its own
ledger. TH04 needs this model with 16-bit OMF, DOS MZ, segment groups, real-mode
relocations, DIET containers, and PC-98 hardware behavior.

A playable TH04 build need not reproduce target file bytes or target relocation
table order. Its own relocation table must be structurally valid and must
resolve the intended code/data owners. Check MZ entry and stack, fixup sites,
segment/group layout, linker MAP ownership, and load-segment variation before
runtime acceptance. A successful TLINK exit alone cannot establish those facts.

## TH01 build reference, with separate evidence scope

The local ReC98 `Tupfile.lua` declares TH01's `zunsoft`, `op`, `reiiden`, and
`fuuin` as four explicit ordered object lists. Its link rule writes a separate
TLINK response file per artifact with the memory-model startup object,
ordered objects, output and MAP paths, then `emu.lib`, the matching math
library, and the matching C runtime library. The rule explains that letting
TCC spawn TLINK would reuse the fixed `turboc.$ln` response filename and
conflict with parallel builds. The local `build_dumb.bat` gives a serial
fallback, and ReC98's README reports that TH01 source reconstruction was
completed in 2022. We have inspected these build descriptions, not executed
or attested a TH01 output in this workspace.
In that TH01 graph, the large-model OP/REIIDEN/FUUIN object lists do not
name the shipped `masters.lib`; their required support is supplied through
declared source objects. The tiny ZUNSOFT link does name that library.

For TH04, reuse the explicit response-file and ordered-object method, and
keep TC4J/TASM32/TLINK work serial against shared outputs. The exact TH01
object lists, libraries, headers, and source topology are cross-game
corroboration only. TH04's manifest and data owners must be local and checked
against the pinned TH04 artifacts.

## Repository-only compiler probe

`python3 scripts/attest_toolchain.py` passed. An isolated private directory
contained a copy of this repository's `src/` only. The compiler runner and
installed TC4J/TASM32 binaries were pinned external tools; no ReC98 source or
header tree was copied into the probe. For OP/MAINE C++ the flags were
`-c -I. -O -b- -3 -Z -d -DGAME=4 -ml`, with the artifact's `BINARY` definition.
Each translation unit had a separate object output directory. The observation
is one serial compile pass, with strict OMF parsing of each emitted object.

| Source group | Observed result | Limit |
| --- | --- | --- |
| `src/op/**/*.cpp` | 48/48 compiled to valid OMF | No OP entry TU or product link yet |
| `src/maine/**/*.cpp` | Initial 26/26 compiled to valid OMF | The entry and SCORE EGC owners were added later; no product link yet |
| `src/shared/**/*.{cpp,c}` under OP flags | Initial 14/19 directly; current 19/19 with BGIMAGE assembly backend | Four formerly blocked sources now use TH04-owned headers |
| `src/shared/hardware/bgimage.cpp` | TC4J `-B` emitted symbolic ASM; pinned TASM32 assembled valid OMF | The assembler reported one segment-alignment warning, as in the existing focused producer workflow |

The private compiler receipts are
`.analysis/native-product-probe-20260927/{op-compile,maine-compile,shared-op-compile}.json`.
Their SHA-256 values are respectively
`d61930ae38017a386de3dfca92d6647edaae5f691c45b3ffd6eeba74b3a94d05`,
`c79bb00d6504627a2519d31d82b6371732897a99d147710103db3d0487e`, and
`21ffec05e1f5c67168b656db27cb3980a25883bfd93fc28d65fa5664f3169a21`.
They are ignored host-local diagnostics, not checked-in build receipts. A
checked-in product builder must reproduce this test before accepting it.

TC4J maps long source basenames to DOS 8.3 aliases and emits object files with
those aliases. The product builder must isolate output per input and record the
actual generated object name; deriving it from the long source name produced a
false failure in the first diagnostic pass.

The four initial direct shared compile blockers were `vram_planes.cpp`
(`planar.h`), `determine_modes.cpp`, `pmd_resident.c`, and `mmd_resident.c`
(`x86real.h` and `th04/snd/snd.h`). They now include the existing TH04-owned
PC-98, x86, and sound interfaces. `vram_planes.hpp` declares only the four far
VRAM pointers needed by that producer. Two cold OP and MAINE scaffold links
preserve zero raw differences in each of the four accepted function slices;
these replays are function Oracles, not standalone product links. The MMD replay
continues to record one aggregate image difference in each artifact outside
its accepted function slice.

`python3 scripts/probes/probe_th04_native_source_compile.py --output-dir
.analysis/reconstruction/probes/native-th04-source-compile-20260927` then
compiled a fresh copy of only this repository's `src/`: 48 OP, 26 MAINE, and
19 shared C/C++ translation units, all producing valid OMF. BGIMAGE took the
verified TC4J `-B`/TASM32 producer path. The private receipt SHA-256 is
`b1d7a182c0803eeab92bd20effb383c783b1cbc4979237d9e6f9ccb6da42cfd0`.
The pinned MS-DOS runner and installed Borland/TASM tools are external tool
inputs; no ReC98 source or headers enter this compile snapshot.

A second cold source-only compile has receipt SHA-256
`9b9ea408617c7c88aa89f31994b0c8136ec35b1ec3955c4a290b8947034c1255`.
`scripts/probes/compare_th04_native_source_compile.py` compares both receipts
and their objects: 92/93 raw OMF files match; BGIMAGE differs only in TASM's
dependency timestamp comment. All 93 timestamp-normalized objects and all 93
link-relevant OMF record sequences match. The compiler evidence input digest
hashes ordered lines of `source path`, one space, `source_sha256`, and newline
from the first receipt.

## MAINE link diagnosis and reusable Borland lessons

`src/maine/end/entry.cpp` now includes the MAINE entry body and owns its
resident pointer. `src/maine/score/egc_copy.cpp` includes the SCORE EGC setup
and rectangle-copy bodies as one TH04-only translation unit. Both compile with
the pinned TC4J flags above and pass OMF integrity parsing. Their local object
SHA-256 values are `547be4f2446453ea843ea2f0fb15d3876b025bd46be01bb4b4ee5fca3ceac991`
and `eead836896e4b428c596441e1cce7a70c82b5d3cb41f979075ac0a112b69814a`.

An isolated TLINK diagnostic under
`.analysis/reconstruction/probes/native-th04-maine-link-20260927/` uses
28 MAINE C++ objects, 19 shared C/C++ objects, and 25 repository-owned ASM
objects. It uses the pinned startup and runtime libraries plus the external
`_reference/ReC98/bin/masters.lib` as a **calibration support library** (SHA-256
`6be41dbcfcf4504977165ccc44443525a29a01f85a1580e6ad0c620bf802faf6`).
This is not a repository-only product dependency closure. Replay it with
`python3 scripts/probes/probe_th04_native_maine_link.py --output-dir
.analysis/reconstruction/probes/<new-run-id>`. The script copies only this
repository's `src/`, validates every OMF, writes the ordered TLINK response,
and records the unresolved-symbol vector. The final diagnostic
`maine-link-after-score-egc.log` (SHA-256
`cdc95608a6a9c120210e7cc9f4f2328d216fb52e496704e98ef4f931a983e028`)
fails with 45 unresolved symbols. They are principally TH04-owned state plus
unattached cutscene/end/registration bodies. TLINK also warns that the
calibration library has an invalid extended dictionary, which it ignores.
TLINK wrote an incomplete MZ despite its failure: its header parses, and it
lists 204 relocation entries, but unresolved addresses make it unusable.
Neither MZ-header validity nor this relocation count is product or runtime
acceptance.

Two fresh script runs have receipt SHA-256
`847a894387ce866bd1ec957bb2788515d68e33179f77d007c5511fe05a00595c`
and `01208ca1b7be5b1920c1692620c3a50680f22b385f943eededdef7a18efa681b`.
All 72 source hashes and all 72 link-relevant OMF object records agree. Of the
raw OMF files, 71/72 agree; BGIMAGE differs only in non-link comment metadata.
Both links report the same 45 unresolved symbols and warning and write the
same incomplete MZ SHA-256
`ce9c023058be27bccd0d60da6c33ffb9666e77aed8cb21edce5411083050e9c9`.
This repeatability makes the frontier reproducible; it does not make that MZ
usable. The link gate must check TLINK exit status and unresolved externals
before interpreting the MZ relocation table.

The 45-symbol vector currently has four unattached C++ bodies
(`cutscene_animate`, `verdict_animate`, `regist_menu`, and
`staffroll_animate`), 39 underscore-decorated state/data symbols, and two
public ASM data names (`DOTS16_MASK_UNALIGNED`, `cdg_images_to_load`). The
receipt gives each requesting object. The next ownership pass must establish
real definitions and initialization from TH04 evidence; merely adding storage
to silence TLINK would not establish working behavior.

The diagnostic exposed three rules worth replaying in TH05 rather than
assuming its source or binary has the same layout:

1. **C++ parameter identity and C/Pascal linkage matter at link time.**
   MAINE's `box_1_to_0_masked()` caller used a 16-bit enum while its owner
   used `unsigned int`; equal storage width did not make their decorated names
   equal. One TH04-local `box_mask_t` declaration now serves both. The caller
   also used a C++ declaration for `egc_off`, while the hardware header's
   `extern "C"`/Pascal interface names the actual provider. These two repairs
   remove two unresolved symbols. The focused v833 cutscene EGC replay still
   passes its complete accepted body and all 559 ordered MAINE relocations
   (receipt SHA-256 `4b0cbfd0f6746105843b4de8b7b566690500e91da0a96b07be272253bcd8f23a`).
2. **TC4J binds a function to the segment at its first declaration.** A first
   attempt declared `box_1_to_0_masked()` in a header before `#pragma codeseg`.
   It compiled but moved the producer out of `CUTSCENE_TEXT`, so the focused
   v833 standalone producer failed the segment-byte check. Keeping the shared
   enum in the header and the caller's function prototype in its wrapper
   restored the 134-byte `CUTSCENE_TEXT` producer. Check OMF `SEGDEF`, `PUBDEF`,
   and `FIXUPP` after moving prototypes; source order is a link input.
3. **One named code segment needs one group assignment.** Seven independent
   cutscene/SCORE wrappers previously supplied different group names for
   `CUTSCENE_TEXT` and `SCORE_TEXT`. TLINK reported 11 cross-group warnings.
   Assigning `cutscene_01` and `score_01` consistently removes all 11 without
   changing the remaining unresolved count. A TH05 product graph must verify
   its own segment/group pairing before accepting its MAP or relocations.

After these wrapper changes, `python3 scripts/decoded_function_acceptance.py
--artifact th04-maine --output-dir
.analysis/reconstruction/probes/native-th04-maine-accepted-after-group-20260927`
cold-replayed all 72 current MAINE accepted decoded slices at zero difference.
The receipt SHA-256 is
`a6d345acd4d49b413ead40bb7dca18d7c6a4430a5d500d980def71a01bd26973`.
This preserves their existing slice acceptance, not packed-file or native
product acceptance.

The failure count is a closure metric, not an exactness metric: the initial
71-object link had 99 unresolved symbols, adding the calibration library left
48, the ABI repair left 46, and the SCORE EGC owner left 45. The library step
establishes only which declarations it offers; it does not attest TH04 product
ownership. Each newly attached `.inl` must be chosen by an actual owner and
ABI review.

### Cutscene state owner

`src/maine/cutscene/state.hpp` and `state.cpp` now declare and define the
cutscene script buffer/pointer, cursor, text timing, fast-forward flag,
background pointer, default script parameter, and five EGC box masks. The
cursor and background-plane structures have explicit 4-byte and 8-byte
compiler size checks. The `BOX_MASKS` table is a semantic 5-by-4 word mask:
`scripts/probes/probe_th04_maine_box_masks.py` finds its exact 40 bytes only
once in the attested decoded MAINE image at load offset `0xEB5C` (SHA-256
`82be2a7b8e42f643e7912bbd106d55480fa74435a0a5c1fdf58c0fd8f5ca236c`).
The candidate MAP's `_BOX_MASKS` at `0E53:062C` corroborates the address but
does not establish the original source name. The probe receipt SHA-256 is
`e50f0ea6b9c84e85f3c19e9447ec58110a95717621ac297ecd97de68b0c0e71f`.

A fresh 73-object native diagnostic compiles this source and reduces the
unresolved vector from 45 to 37, resolving precisely `_BOX_MASKS`, `_box_bg`,
`_cursor`, `_fast_forward`, `_script`, `_script_p`,
`_script_param_number_default`, and `_text_interval` with no new undefineds.
The new 37-symbol frontier is still a failed link; TLINK again writes an
incomplete MZ with 204 relocation entries. Its receipt SHA-256 is
`17f012a22b7d8f1a9699c346878f6ddde7ae1bcb467b415dbe4a92ca4dbaea0a`.
The BSS initialization and cutscene behavior still require runtime checks.
A second cold 73-object build has receipt SHA-256
`8c4ac21cc00176345e4f0eed91f4af30464ac6459061faebc09351ca0e38e569`.
Both rounds have identical source hashes, all 73 link-relevant OMF records,
the 37-symbol unresolved vector, warning vector, and incomplete MZ. BGIMAGE
is the sole raw OMF difference, again confined to non-link comments.
`scripts/probes/compare_th04_native_maine_link.py` checks the two receipts,
including the ordered source/object identities, unresolved vector, linker
result, warning vector, and incomplete MZ hash.

The remaining 37 symbols split into four unattached cutscene/end/score C++
bodies, eight graphics/input state symbols (four VRAM pointers, BGIMAGE,
`key_det`, `shiftkey`, and the flip LUT), nine sound state symbols, and sixteen
MAINE score/PI/CDG/memory data symbols. This groups owner searches; it does
not authorize data definitions without width, initialization, and consumer
checks. The link receipt retains every requesting object and exact symbol.

One integration attempt moved existing cutscene wrappers' declarations into
the new state header. The native all-source compile passed, but the v585
accepted `box_bg_free` Oracle failed before comparison: its historical
isolated-source replay copied the wrapper, body, and HMem header, not the new
header (`compile-v585-box-bg-free-standalone-a.log` SHA-256
`92f09d692ba35ca984f41f83b2b523208b923984eb156f7b56f9ddcdef348b19`).
The state owner retains its local header, while established accepted wrappers
retain their self-contained declarations. Focused v585 A/B replay then
raw-matched the complete 31-byte function with 559 ordered relocations
(receipt SHA-256 `3100e6d3ec70c392562fdd3988dcd60db5e8a4206d19b2f84e180bdd3be0ab7f`).
For a future TH05 declaration migration, update the isolated replay's
transitive source-copy closure and rerun accepted extents; a product compile
alone cannot establish that an accepted unit remains reproducible.

After the cutscene-state wrapper composition stabilized, a fresh cold
`decoded_function_acceptance.py --artifact th04-maine` run again passed all
72 accepted MAINE slices. Receipt SHA-256:
`80e101f5308e2755c9225035cc83fb66371c55e1501f37db0216c12872238ad5`.
This run precedes the subsequent hardware, sound, score, and CDG data owners;
their layout changes require another aggregate replay before promotion.

### TH04 state closure and the DGROUP trap

Four TH04-local ASM state owners now provide the four far VRAM plane pointers,
the 8-byte BGIMAGE segment set, the keyboard detection/shift state, and the
256-byte generated bit-flip lookup table. Their widths and consumer order are
declared in this repository's hardware headers and ASM users. A 77-object
TC4J/TASM32 diagnostic removed precisely eight unresolved hardware symbols,
37 to 29, without new undefineds (receipt SHA-256
`7edac4c567adb598b5f57a92334c8bb5eab986ce38424acc1f540d835d9970fb`).

`src/shared/sound/state.cpp` supplies the driver flags, SE playing/frame
state, 17-entry priority and frame tables, 13-byte load filename, and the
four extension pointers. The 34 table bytes occur uniquely at decoded MAINE
load offset `0xEA8E`; the target has `FF 00` at SE playing/frame offset
`0xEB30`, and the extension strings occur uniquely at `0xEAE4`. The target
probe receipt SHA-256 is
`c51ec3721f819bc3a1abd5c3e29ea3ad1e9ff65a578bd64de1ac23c0fb366aed`.
The 78-object native link reduced 29 unresolved symbols to 20 (receipt
SHA-256 `91f3d4740f1fedd4f5765b593396ce561e9ec110a16b49e21146721bbe12e0ee`).
The same 34 table bytes occur uniquely in the independently attested OP
decoded load image at `0xFCFE`; OP also has `FF 00` at `0xFD80` and the same
extension strings uniquely at `0xFD34`. Its target-only probe receipt SHA-256
is `17df17d971985aa32c2d53348d5b3b57d6c3b394e6ffa02c71ab6546c2caa97f`.
This supports a shared TH04 sound-state definition without claiming an OP
product link or runtime behavior.

Score state, six PI slots, the 16-bit allocation-limit variable, and CDG
storage/mask owners then removed the other sixteen data symbols. The target
probe uniquely locates the 51-byte registration alphabet at `0xED5C`, four
consecutive `GENSOU.SCR` strings at `0xED8F`, and the 32-byte first-word CDG
mask table at `0xEAB0` (receipt SHA-256
`1a4f688275cbea794867cdfcc209fa95f330ecd90f949de2f2d65f392020a3a1`).
The v489 candidate MAP labels these positions as `0E53:082C` alphabet,
`0E53:085F..0880` score filenames, and `0E53:0580` CDG masks; those names
and segment assignments are corroboration, while the unique decoded bytes
are the target observations.
The score section remains a 196-byte BSS structure with compiler-checked
field offsets; uniqueness of the initialized bytes does not attest its BSS
runtime contents.

The first 83-object link reported **zero** unresolved symbols but failed with
`Group DGROUP exceeds 64K`, produced no MZ, and exited 2 (receipt SHA-256
`4332ba7e6c3969c80d81a43a83004202e5629fda9a87d924bc81aaceebd3c247`).
The cause was ASM `DGROUP group _TEXT, ...` declarations: Borland combines
all like-named `_TEXT` contributions before applying group membership, which
pulled program code into the 64 KB data group. This was latent while
unresolved-symbol errors kept the earlier links incomplete. The local
historical MASTER archive's 40 candidate support objects declare 921 bytes
of explicit DGROUP data and **zero** `_TEXT` members; the candidate MAINE MAP
also lists `_TEXT` outside any group. Correct large-model product declarations
group only `_DATA` and `_BSS`. This is a segment ownership requirement, not
a cosmetic linker-warning fix.

Three older TH04 ZUN support modules (`master_version.asm`, `graph_state.asm`,
`file_state.asm`) had accepted OMF identities with `_TEXT` grouped for their
resident replay. A direct edit to their group declaration failed that
replay's VERSION OMF check. They now select data-only DGROUP when
`TH04_LARGE_PRODUCT` is defined by the native product assembler and retain
their earlier declaration otherwise. A cold ZUN file-state replay restored
the accepted 6360-byte component SHA-256
`a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab`
(receipt SHA-256 `28cca84065f20929c50719b2c1e4e6874012633d4aefa49ba1591d2ffbe1b272`).
The first data-only group diagnostic, before the explicit macro was added,
linked without overflow and left exactly four unresolved C++ bodies. Its
parsable MZ has 369 relocations but is incomplete because TLINK exited 1
(receipt SHA-256 `a721b0ae176bce78ed18e95352ef953c34738854a83a6b970167cd6fa943699c`).
Two further cold builds with the explicit large-product assembler flag
reproduce this four-symbol frontier. All 83 link-relevant and
timestamp-normalized OMF objects agree; BGIMAGE's raw OMF alone contains a
dependency timestamp difference. The unresolved vector, warning vector,
linker response, incomplete MZ SHA-256, and 369 relocation entries are the
same. A/B receipt SHA-256 values are
`2c7b4ce38b6b9b86a591dd4d18623f41d69e930efa38d29837410d0242402b74`
and `b9d72312efa3fe55b730fcc84b30c7113d08efeab9b23f8448015b83f03c1a54`.
TLINK's nonzero exit still forbids interpreting that MZ as runnable.

Dropping the external `masters.lib` from that same 83-object response reveals
55 unresolved symbols: the four C++ bodies plus 51 PC-98 runtime/library
names supplied by 40 historical archive members. The no-library link log
SHA-256 is `f00147c200a300cd611b2382e7fdb2089b6ed8b69bc20aa6dc12eeb9e069834f`.
Earlier archive analysis also found that this support library's extracted
objects use an ABI unsuitable as a drop-in large-model product dependency.
It remains a link-frontier diagnostic; TH04's runnable product still needs
local, ABI-checked runtime owners.

The native link probe now has `--without-support`, which performs the entire
serial TH04 source/OMF build and omits the historical archive from the TLINK
response. Its fresh 83-object run reproduces the 55-name frontier with zero
warnings and a nonzero linker exit (receipt SHA-256
`6211764483f4996991d6d11ee91f4e13cbf521322364bf84b13b9979adbcf17f`).
The receipt records `support_lib_sha256 = null`, so the omitted archive is
visible in the replay identity rather than inferred from a manually edited
response.

For the next body-owner pass, a target-only probe attests 21 contiguous
staffroll resource filenames at MAINE load `0xEB88` and the verdict image
name `ude.pi` uniquely at `0xED54` (receipt SHA-256
`bd5a62aca5c3c1ca2255e1614452e4e032b683ca6ec6e355fecedcdcec27e1e7`).
The v489 MAP supplies candidate names and segment addresses for these bytes;
their source owners and successful asset loads remain open.

The first TH04-local body-owner pass attaches the seven staffroll dissolve
helpers and `staffroll_animate` in `src/maine/end/staff.cpp`. A new local CDG
header checks the 16-byte slot structure against the TH04 ASM field offsets.
`staff_resources.cpp` owns 21 addressable filenames; their concatenated
193-byte block appears once in the freshly compiled OMF and equals the
target-observed block hash
`a3228d034412eb1d9611eb6a136cd7f30a98a0b1c4f818b691ae0993798db55a`.
The first staff compile exposed a missing declaration for the already owned
`BGIMAGE_PUT_RECT_16` ASM routine. A local FAR Pascal four-word declaration,
checked against its `proc far` and argument list, closed that compile error.
With no historical support archive, the 85-object link still has 55 undefined
names: `staffroll_animate()` disappears and `GRCG_SETCOLOR` appears as an
additional runtime dependency. Comparing only the count would hide this
progress; compare symbol identities without the `in module` suffix because TLINK also changes
which referencing module it names when object order changes. TLINK still exits
nonzero, so this is not a runnable or relocation-accepted product.
Two fresh 85-object no-archive builds match in every link-relevant and
dependency-timestamp-normalized OMF record, unresolved vector, warning vector,
and incomplete MZ. Their receipt SHA-256 values are
`14e158222412736dce205941083dc512cfe3801ccab4da76f3fdda31928bef39`
and `3b39e4efba3e6189d607e37442283938b785dd8934d3729a1f50ebc3a11d1af1`.
Only BGIMAGE's raw OMF dependency timestamp differs. This is a deterministic
link failure, not product acceptance.
With the same 85 TH04 objects and the pinned historical archive added solely
for calibration, TLINK reports the three remaining C++ bodies:
`cutscene_animate`, `verdict_animate`, and `regist_menu`. Its nonzero exit also
reports the archive's invalid extended-dictionary warning. The partial MZ has
468 relocation entries, which cannot enter load-segment acceptance. Calibration
receipt SHA-256:
`b77239850bc753f6972bbae6dc20634a69808ab32c00c70707620c02d83c7c77`.

The next local owner is `src/maine/score/regist.cpp`, which includes the
accepted 924-byte `regist_menu` body in `SCORE_TEXT` with TH04 declarations.
A target-only probe identifies one 126-byte registration resource block at
MAINE decoded load `0xEDBB`: `hi01.pi`, `scnum2.bft`, two separately
addressable copies of the 50-byte Shift-JIS slow-mode notice, and `name`.
`regist_resources.cpp` emits the same contiguous block once in its freshly
compiled OMF. The local input flag values agree with owned `input_s.asm`, and
the `graph_putsa_fx` declaration follows the owned FAR Pascal ASM's `RETF 10`.
TC4J confirms `playchar_t` occupies one byte in the current profile; the
product state now uses that type. The first focused compile failed because
`resident.hpp` relies on `types.hpp` for the 16-bit Borland `bool`; the new
wrapper includes the latter first and then compiles. Keep this include order
when migrating TH05 wrappers, or explicitly update and cold-replay all old
isolated snapshot closures before changing a shared header.

The fresh 87-object no-archive link resolves `regist_menu()` and exposes
`SUPER_ENTRY_BFNT` and `SUPER_FREE`; the total unresolved vector is now 56
with zero warnings and TLINK exit 1 (receipt SHA-256
`a6b3ee7260f06bc59979bd187d07c171e8723e33b24baca4a825f9ca821e94cd`).
No partial MZ or relocation count from this failed link is product evidence.
The affected MAINE 72-slice cold aggregate passed all accepted raw-zero
comparisons after the input/playchar/score declaration changes (receipt
SHA-256 `871e1398afab56d030e7d0ea04688ca497cc0f40bc01df466cdd00a5ed2726be`).
An independent second 87-object no-archive build agrees on every
link-relevant and timestamp-normalized OMF object, the 56-name unresolved
vector, warning vector, and incomplete MZ. Its receipt SHA-256 is
`ae12c7fe1ce0fd1b7d056937671b0abf4eb369cee3eb15a66f27b9b547c91a31`;
only BGIMAGE's raw OMF dependency timestamp differs. This remains a
deterministic failed product link.
An independently recorded TLIB public-name inventory maps 54 of those 56
names to 43 members of the pinned historical archive. Only the two remaining
C++ bodies have no archive public-name provider. This gives a bounded local
runtime porting queue; a public-name match does not attest memory model,
calling convention, fixups, or suitability for a standalone product.
`scripts/probes/inventory_th04_maine_support.py` checks the no-archive receipt,
archive digest, and TLIB listing digest before reporting this mapping.

For the following verdict owner, a target-only probe identifies a unique
274-byte display data block at MAINE decoded load `0xEC4A` (candidate MAP
`0E53:071A`). It checks eight CP932 label/file anchors, including `_ude.txt`
and the slowdown verdict text; SHA-256 is
`6d588142d2da59f6b695df4bf51f6e77ca1fc3ca36e206278ae2f5774324a8aa`.
This prepares an ownership boundary only. The verdict's helper code, state,
resource arrays, and runtime reads have not yet been attached to the product.

The verdict owner now compiles seven TH04-local bodies in `verdict.cpp`, with
separate state and named CP932 resources. Its text-buffer terminator is an
alias of byte 28 inside the 30-byte buffer, matching the candidate v489 MAP's
overlapping addresses; it is not a second allocation. A focused OMF Oracle checks
all 25 resource public names and the complete 271 semantic bytes of gaiji
labels and strings against the attested target, excluding three zero-valued
state/alignment bytes from the target's 274-byte block (receipt SHA-256
`ca2d417736b1c8fcf25d2303cc65582d37b75c82e41004797e1cec9b3f66e948`).
The first wrapper compile found `V_WHITE` missing; including the existing
TH04 color owner closed the compiler error. The current 90-object no-archive
link resolves `verdict_animate()` and exposes `_random_seed`; it still has 56
unresolved names, zero warnings, and TLINK exit 1 (receipt SHA-256
`84bf73b78043832507c2cb2e786784fa3bc16aa90e7097b32906beaad20f4604`).
Its 407-entry partial-MZ relocation table is diagnostic only. The pinned TLIB
public-name inventory now maps 55 of the 56 names to 44 historical members;
`cutscene_animate()` alone lacks an archive public-name provider. These
members remain ABI-unaccepted calibration inputs.
Two 90-object no-archive cold builds agree in every link-relevant and
timestamp-normalized OMF object, the 56-name unresolved vector, warnings,
and incomplete MZ. The second receipt SHA-256 is
`a2226805c0f0c149dab115d531e6c1cdb194917b69b16d7abaf2afa9cbd250e6`;
BGIMAGE's raw OMF differs only in a dependency timestamp.

The cutscene product owner now compiles the maintained
`cutscene_animate.inl`, `script_op.inl`, `box_bg_snap.inl`, and
`pic_put_both_masked.inl` through TH04-local translation units. The accepted
function bodies themselves were not edited. A target and OMF probe checks
`PI_MASKS` at MAINE `0E53:060C` (decoded load `0xEB3C`), the adjacent
`BOX_MASKS` at `0E53:062C`, and the initial `CUTSCENE_KANJI` buffer at
`0E53:0654`: the PI mask object matches all 32 target bytes, while the state
object matches 44 contiguous mask and glyph bytes with publics at offsets 0
and 40. Its receipt SHA-256 is
`07c4ede8d1812ae9346f51e14d41320217536f66deaeea6ca016931bf034a6cd`.
The buffer begins with two ASCII spaces and two zero bytes; the target's
decoded load, rather than the candidate MAP alone, establishes those bytes.

The first 92-object product probe attached the glyph loop and background
snapshot, replacing the unresolved `cutscene_animate()` name with
`script_op(unsigned char)`. Adding the local script interpreter, PI masks,
and masked blit yields 95 objects. The no-archive link now has 62 distinct
unresolved names, no warnings, TLINK exit 1, and a parsable but incomplete MZ
with 430 relocation entries (receipt SHA-256
`669aa2d33aa0c90bbbbedb12611a6609771f158299b94c1d36200d2e64cc525d`).
The seven new names are the previously unreachable masked-pixel writer,
scroll, byte-box fill, GRCG disable, white fades, and SE update; the cutscene
C++ bodies themselves are resolved. A second cold build agrees on all 95
link-relevant and timestamp-normalized OMF objects and the full failure
signature (receipt SHA-256
`72b724ec69114d9650f8ae6965e6b6e00e74e847d9f2036bde231466272e5ba4`).
Only BGIMAGE's raw object dependency timestamp differs. A pinned archive
public-name inventory routes 60 of the 62 remaining names to 48 historical
members. `GRAPH_PACK_PUT_8_NOCLIP` and `_snd_se_update` have no archive
provider; the first has a separate upstream candidate assembly implementation,
and the second has a TH04 OP accepted source body. Neither is yet a MAINE
product owner. The archive remains calibration evidence, not a product input.
After restoring the accepted box-background wrapper composition, the complete
MAINE cold aggregate passes all 72 accepted function slices raw-zero (receipt
SHA-256 `a1fff45cf81442a1aa3e0a6ae6c253c958a283e4c1aa1be028dc841fcd118471`).

This exposes two useful TH05 checks: an accepted body can reveal additional
support calls only after its real caller and command parser are linked, so
compare symbol identities across cold links; and initialized masks next to
mutable glyph storage should be checked through both target bytes and OMF
public offsets before merging them into one data owner. This TH04 cutscene
wrapper is TH04-only; ReC98's shared TH01–TH05 build response supplied no
standalone artifact manifest.

The first aggregate repeated the previously recorded v839 isolated-header
closure failure after a temporary `state.hpp` include in two accepted wrappers.
Those changes were reverted; both wrapper backends and the complete aggregate
then passed. The v839 knowledge row remains the reusable TH05 warning.
The two link receipts above were generated again from this final wrapper
composition: all 95 link-relevant objects, the 62-name unresolved vector,
warnings, and failed-link MZ agree. The prior v844 receipts remain historical
diagnostics with a different wrapper source hash.

The next two local support owners compile without TC4J warnings. A shared
product TU includes the already accepted TH04 sound-effect updater body; a
TH04-local C++ routine unpacks 4-bit PI pixels into B/R/G/E VRAM planes without
rejecting the cutscene's temporary row 400. This byte-to-plane order follows
the historical rotation-table semantics, but has not yet been checked in an
emulator. The first 97-object no-archive link removes both prior missing
publics and exposes `BGM_SOUND`, called for beep-mode effects. It fails with
61 unique unresolved names, zero warnings, and 432 relocation entries in its
incomplete MZ (receipt SHA-256
`2694f49f38ba4647a0f2fa33d6afbb9f7d368f8059a0f16de593dfd3723509b9`).
A second cold build agrees on all 97 link-relevant and timestamp-normalized
OMF objects, the full unresolved vector, and the failed MZ; only BGIMAGE's
raw dependency timestamp differs (receipt SHA-256
`2beae6a0adc076f03d61b0179dbedd3752a6507a412dbd888871251be28bd18c`).
Every remaining name routes by public name to 49 historical archive members.

A separate historical-library calibration link resolves all 61 names, yet
TLINK still exits 1. It reports an invalid extended dictionary warning and
nine near-call `Fixup overflow` errors from `MAINE_E_TEXT` to cutscene,
staffroll, verdict, and registration functions. Its 573-entry MZ relocation
table is an incomplete diagnostic. The four product code segments in this
MAP occupy only `0x2C1C` bytes combined, but their OMF owners currently place
them in four distinct groups. For TH05, symbol closure and near-call
relocation closure are separate acceptance gates; inspect both the segment/group
MAP and TLINK's fixup diagnostics before booting any MZ.

The product-only code-group branch now compiles all 35 MAINE wrapper TUs for
these four segments into `GROUP_01`. Their original pragma branch remains the
default for isolated exact replay. The C++ build selects the new branch with
`-DTH04P`; the existing TASM `TH04_LARGE_PRODUCT` flag controls DGROUP
separately. A first attempt used the long C++ define name, which made TC4J
misread the longest MAINE source path as a `.16S` file before compilation.
The shorter flag removes that MS-DOS command-tail failure. For TH05, leave
room for the longest 8.3-translated path when adding compiler switches.

The current no-archive 97-object link still fails on 61 support names with
zero warnings. Its two cold rounds agree on every link-relevant and
timestamp-normalized OMF object and the failure signature (receipt SHA-256
`df10f66ff6cbc67cdc463f804e835efd0a18f782b8324c7ba88341f6d678fc6a`
and `e73c77892a0c301f3fa7711fe17d618f0ca4bb6d00490a3964d8b3baf3c50e39`).
The MAP assigns `MAINE_E_TEXT`, `CUTSCENE_TEXT`, `MAINE_01_TEXT`, and
`SCORE_TEXT` to `GROUP_01` without duplicate-group warnings. The historical
archive calibration now links with TLINK exit 0, no unresolved names, and no
near-fixup errors. Its sole warning says the archive's invalid extended
dictionary was ignored. Its 573-relocation MZ is structurally valid (receipt
SHA-256 `d50e0ab235b6b9ff405c3bf07c7ca505254db9697f2461945a256d63ba008596`).
That executable is a calibration artifact because the archive is not an
accepted TH04-local runtime implementation.

An independent static audit of this calibration MZ confirms all 573
relocation sites are unique, nonoverlapping, and inside its 63,540-byte load
image. Their five distinct segment-word values stay within its 3,972 image
paragraphs. Entry `CS:IP` points into the image; the initial stack top at
76,544 bytes fits the 76,560-byte minimum allocation. Relocation arithmetic
does not wrap at DOS load segments `0x2000` and `0x6000` (receipt SHA-256
`aced2ad9a422a35c6a7b12837330c23daa019f4aafc1ba29f7b50153f1d695a1`).
This establishes static relocation structure for the calibration artifact;
runtime behavior and a complete TH04-only link remain open.

Changing wrapper pragmas also changed the two pinned SCORE codec wrapper
source hashes in their replay guard. After updating those hashes to the current
checked-in wrappers, a cold focused replay matched decode, encode, and the
complete `SCORE_TEXT` bytes while preserving all 559 target MAINE relocations
(receipt SHA-256 `cc3d0cc4b6059b5375b8cb3228fa87b7545aed71a34d779671677555af6e990e`).
The full cold MAINE aggregate then passed all 72 accepted function slices
against the original target (receipt SHA-256
`fda5aab5ce3d50fba8f8693f34915896657cd95999b55e9b86bd96e25ceefe03`).
For TH05, a source-hash guard failure after a controlled wrapper edit needs
both an updated guard and a fresh byte-and-relocation replay; a hash edit alone
does not establish preservation.

The next TH04-local hardware owner is `src/shared/hardware/display_control.asm`.
Its four far Pascal entry points perform the PC-98 BIOS graphics show/hide
calls, disable the GRCG, and set the GRCG mode and four color tile registers.
The tile update preserves the caller's interrupt flags and the callee-saved
`BP`, `CX`, and `DX`; `GRCG_SETCOLOR` returns with `retf 4` for its two word
arguments. This is hardware assembly, not a target-byte reconstruction.
The PC-98 BIOS service numbers and GRCG register sequence were corroborated
against `_reference/ReC98/libs/master.lib/{graph_hide,graph_show,grcg_setcolor}.asm`;
that source does not establish TH04 target-byte identity.
TASM32 produced a valid OMF object with four matching public names and no
fixups. A disassembly of its 54 code bytes verified the far returns and the
parameter offsets. Behavior on PC-98 hardware remains to be observed.

The 98-object TH04-only no-archive link now has 57 unresolved support names,
down exactly four, and zero warnings. Two cold rounds agree on every
link-relevant and timestamp-normalized OMF object; the BGIMAGE raw dependency
timestamp is the only object drift (receipt SHA-256
`7d98c10359530f11e59d15ec787d1d9bad4d1bf133f3ab8811dbf9d93f384da4`
and `8e546500f151bd70f10772674cd0e2d91a5a14e3568113a50f4b3ee72aabbfa7`).
The historical-library calibration still links with no unresolved names or
near-call fixup errors. Its 573-relocation MZ passes the static load audit at
both tested DOS segments (receipt SHA-256
`1d3600369c7c7aa66e9a1ae4e107f9cbde005e2aa87db47de167d62dd24f6c99`
and `f35dd54632ceffc437c957690b29a96cb1e15a660da3da05aa65528a6c7d28a7`).
The archive warning and product/runtime limits remain.

The next two TH04-local support owners cover EGC mode initialization and PC-98
text controls. `egc_control.cpp` uses TC4J port intrinsics for far Pascal
`EGC_ON`, `EGC_OFF`, and `EGC_START`; its 119-byte code segment contains the
expected port writes and far returns. `text_control.asm` uses TASM32 for
`KEY_BEEP_OFF`, `TEXT_CURSOR_HIDE`, and `TEXT_SYSTEMLINE_HIDE`, preserving `ES`
or `DX` as needed and sending the text escape commands through BIOS `int 29h`.
The hardware operations were corroborated against the bounded ReC98
`egc.asm`, `keybeep.asm`, and `txesc.asm` references; this is not target-byte or
runtime acceptance. The first focused EGC compile exposed TC4J's include
lookup rule: `#include "graphics.hpp"` did not resolve relative to the TU, so
the maintained source uses its TH04-local repository path.

The current 100-object no-archive link has 51 unresolved support names, down
exactly six, and zero warnings. Both cold rounds agree on every link-relevant
and timestamp-normalized OMF object; BGIMAGE again has dependency timestamp
drift only (receipt SHA-256
`9a5efe8200a540cdcd619c5b3e15f96bc982f2172dd7992776ca6e21940c8351`
and `ddb96942d77f415c7b6117ae49be9c03cd276b84237b130eb9e87f5d0c60eeab`).
Historical-library calibration TLINK still exits 0, with its invalid
extended-dictionary warning. The resulting MZ has 570 relocation sites and
six segment-word values; all sites, entry, stack, and both DOS load checks
pass the static audit (receipt SHA-256
`56aa098280592dd56deb3929c4bd50d48da52472e222ad751654e8a7e3d4a93a`
and `8ea0a7a6cf53b2be071667b4336a4e2be9a9c463d75e32a18c0c38b0ed4dfa7a`).
The old 573-relocation count belonged to the preceding source graph.

The following TH04-local batch closes six more names. `file_exist.asm` probes
DOS with a far filename pointer, closes an opened handle, preserves `DS` and
`BX`, and returns via `retf 4`. `text_control.asm` now also emits `ESC[2J`
for `TEXT_CLEAR`. `random.cpp` owns the 32-bit seed initialized to one and a
modulo-2^32 LCG step with multiplier `0x015A4E35`, returning bits 16–30.
TC4J emitted `_random_seed` and far Pascal `IRAND` without external symbols.
`trig_tables.asm` generates its 320 words from rounded
`256*sin(2*pi*t/256)` using quarter-wave symmetry; `_CosTable8` aliases
`_SinTable8` at byte offset 128, so the two 256-entry views consume 640 bytes.
The computed words agree with the ReC98 `sin8[data].asm` reference, but are
not yet attested against TH04 target data. These ports are behavioral source
candidates, not exact reconstructions.

The current 103-object no-archive link has 45 unresolved names, down exactly
six, and zero warnings. Both cold rounds agree on every link-relevant and
timestamp-normalized OMF object, with BGIMAGE raw timestamp drift only
(receipt SHA-256 `5b3ec148ce6b08f0b9ade4fd4b24613270a4aa9a0ce9dffdeb11c73c51528e1a`
and `046ed60ebb7d557db54b570559338da9e69dbca1a242926a001632b9e498aa21`).
Historical-library calibration TLINK still exits 0; its MZ now has 569
relocation sites and seven distinct in-image segment words. The independent
static audit passes site, entry, stack, and two DOS load checks (receipt
SHA-256 `d3349459f11fbb10a5c0f3008534e2a2bef18b7c8985ca7564506f992ef49bc4`
and `4f201a0c988d8cacec3bdc0777fb0fa975d1e061072a215a15f0013e5244d27f`).
The archive warning and product/runtime limits remain.

The MAINE probe now reads `config/native_maine_sources.toml` as its explicit
TH04 source and object-order manifest. Its first revision listed 68 C/C++ and 35 ASM TUs from
`src/maine/` and `src/shared/`; a missing, duplicate, stale, or unlisted TU
fails before Wine starts. A negative probe with `random.cpp` removed from the
manifest was rejected with that exact missing path. The manifest-only check
is now part of `scripts/ci.py`. A fresh cold link from the manifest matched
the preceding scan-based 103 objects after dependency-timestamp normalization,
including the identical TLINK response SHA-256
`1d559857f525cb908d7d4b7a6debec7cbcfbc857308e922cf8d265670ce145e4`,
identical incomplete MZ SHA-256
`bb037ff2bdea2efbf30befaf21e7a3cf189d672da601d0a7da8d6593d0e4af2a`,
and the same 45 unresolved names (manifest-link receipt SHA-256
`070f538a166f4c753f409a0b4afa15f7acc012f0ede25f8590928939b07137b6`).
For TH05, guard complete source-set membership and explicit link order before
interpreting a successful compiler pass as product coverage. The other TH04
artifacts still need their own explicit manifests.

The first palette support owner adds `palette_state.asm` and
`palette_show.cpp` to that manifest, now 69 C/C++ and 36 ASM TUs. The state
exports both C and Pascal spellings for `PaletteTone` and the 48-byte
`Palettes` array. `PALETTE_SHOW` writes 16 analog palette entries through
PC-98 ports `0xA8`, `0xAC`, `0xAA`, and `0xAE`; tone 0..100 scales each
component's high nibble toward black and 100..200 toward white. That first owner followed only the analog branch of the bounded ReC98
reference. The complete LCD branch is recovered below under v1415; physical display timing remains open.

### Indexed native Demo entry palette (v1420)

The remaining `FrontEnd::render(demo_start)` path scaled expanded RGB8 pixels.
It now saves the menu's raw palette alongside its complete pixel indices and
uses `pc98_palette::argb()` to apply the recovered DAC4 conversion once to
the sixteen colors. The menu comes from the current title resources, including
the retained background after Music Room reload. Indices preserve duplicate
palette colors without attempting to recover them from RGB.

Actual frontend capture covers preparation and seventeen pending OP refreshes;
MAIN receives no update. GNU/optimized UBSan each agree on eighteen complete
640x400 frames with the original OP palette function's DAC projection:
4,608,000 pixels per compiler. The original executes its full 266-byte body at
two loads for each palette/tone, retaining all 36 I/O/return controls. The old
RGB8 formula projection fails on sixteen of the frames. This is a component
palette projection, not a complete original menu/scanout claim.

Cold 537/08ff3fc2 and final 537/6175165a keep separate archives. The final
reader uses the actual reset-receipt schema, and the capture include enables
normal physical-score storage before demo preparation. Only that include
recompiles in each frontend; both core library hashes remain the original
cold hashes. The old executables and both initial failures stay retained.
Two related CTests per compiler and native CI 345 pass. The private reader in
`.analysis/worktrees/native-demo-palette-v1420/.analysis/port64/native-demo-palette-v1420/`
checks both input sets, full images/I/O and inherited palette/counter proofs.

### Native shared palette recovery and counter integration (v1418/v1419)

`pc98_palette::show()` now models the complete original analog and notebook
LCD function. It truncates the caller's tone to a signed WORD before the
0..200 clamp. This replaces the separate calculations in startup, Setup,
ranking, Music Room, registration, Game Over and the frontend. DAC conversion
runs once on the sixteen palette entries before indexed pixels become RGB8.
The startup renderer also accepts the explicit notebook flag/query inputs.

Both fresh compilers agree with all 20,832 original v1415 ordered port records,
including the real startup DAC and query dispatch. Compiling the actual
c2d8363 startup owner rejects 288 of 1,368 analog controls because its wider
host integer is clamped before WORD truncation. Its missing notebook API is
outside that negative comparison.

The initial 534/c61549d2 producer and joined 536/3ba0ba42 producer retain
separate source archives and outputs. The join contains counter-delay source
dcbe8f7 and palette source 3add0fd. Its fresh GNU/optimized UBSan builds each
cover the complete core/frontend and nine selected component programs, with
nine CTests and the original counter/integer vectors. Both native CI gates
pass 345 tests. The earlier full 82-program/80-CTest counter graph keeps its
own producer. The join's closure checks 5,945 frozen parent pins and reads the
complete palette streams; physical LCD scanout remains separate.

Private replay is in `.analysis/worktrees/native-palette-show-join-v1419/`
under `.analysis/port64/native-palette-show-join-v1419/`; source and component
commands are recorded. Continue live scene-wait consumers after this shared
function recovery. Historical authored exact counts are unchanged.

### Complete palette output, including notebook LCD (v1415)

The three originals contain the same 266-byte control flow with different
data operands: MAIN 0000:1F04..200E, OP 0000:1DE0..1EEA, and MAINE
0000:19EC..1AF6 (ends exclusive). `PaletteNote` is a WORD: zero selects
analog RGB; nonzero takes the LCD path. `PaletteTone` is interpreted as a
signed WORD and clamped to 0..200.

The recovered LCD path writes A0h to port F6h and reads 871Eh. An FFh
response triggers the fallback read at AE8Eh, shifted right two. The selected
low bit controls polarity. For each color, the original masks red's high
nibble and blue's **low** nibble with the inversion byte; green uses its high
nibble. After tone scaling, it weights the components as
`2*r + 4*g + b + max(r,g,b)` and quantizes them to eight levels. Port output
is A8h for the color index, then AEh, ACh, AAh for the three shade bits.
The typed implementation preserves these masks and the complete I/O order.
The original patches one CS byte per LCD call to apply polarity; its full
instructions, including that write, execute in the comparison.

Producer 1425/491e4afa changes only `palette_show.cpp` and
`palette_state.asm` from the frozen v1411 product inputs. It cold-builds
MAIN, OP and MAINE with no historical palette archive. All three link and
pass IRQ audits; MAIN's bullet switch tables also pass. The new exported
`PaletteNote` storage defaults to zero. Hardware selection is supplied as an
explicit input in the function comparisons.

The maintained `scripts/runtime/verify_dos_palette_show.py` captures the
complete original functions, then executes each linked replacement. Each
artifact has 3,472 palette/tone/query fixtures at two DOS loads: 6,944 ordered
port transcripts. Fixtures cover signed/truncated WORD boundaries, zero and
nonzero notebook flags, both query routes/polarities, and all 4,096 RGB
high-nibble combinations with varied low nibbles. All 20,832 comparisons
agree, including far-return stack and preserved palette/tone/note storage.
The actual v1411 MAIN predecessor fails 6,488 LCD comparisons while all 456
analog controls agree. Rebuilt VSync waits and lifecycle functions pass
528 and 324 additional controls, respectively, after the DGROUP change.
This is instruction-level I/O recovery; it does not promote historical bytes
or measure physical LCD scanout.

Private receipts and replay commands are under
`.analysis/worktrees/dos-palette-note-v1415/.analysis/reconstruction/probes/dos-palette-note-v1415/`.
`commands.json` and `hardware-commands.json` retain each invocation;
`verify_closure.py --require-ci` reads full comparison streams, source and
parent pins. The first producer completed MAIN before an OP input-link
failure; its original verifier and MAIN transcript remain bound to that run.
Fresh OP/MAINE producers follow the repaired input link.

The 105-object no-archive link now has 42 unresolved names, down exactly
`PALETTE_SHOW`, `_PaletteTone`, and `_Palettes`, with zero warnings. Two cold
rounds agree on every link-relevant and timestamp-normalized object, again
with only BGIMAGE raw dependency timestamp drift (receipt SHA-256
`7ca23d5e7ff847cfa4e20db0d6dbdc3c75931b5f838d039f28e6e18b95e84c77`
and `c0eb881b9214cd8eccbf863be7246ce5cee56d5c8836783e6157014442895b99`).
Historical-library calibration TLINK still exits 0 without duplicate palette
storage or near-call fixup errors. The 569-site MZ relocation audit passes
with eight distinct in-image segment values (receipt SHA-256
`72fc5d894f69be49ed440fef2245ccec076cc8f1f2ce47dbee136dbaef303b10`
and `afe4b0f6603834d1c0309dcc8d0ece114ea2d39e512b6456c04ba2651e93fd1c`).
The historical archive and its dictionary warning still limit this artifact
to calibration.

`palette_fade.cpp` now owns the four black/white fades in the TH04 product
source. Each begins at its reference tone, aligns to the next vertical blank,
calls `PALETTE_SHOW` at six-tone steps, waits the signed 16-bit speed in
vertical blanks, and forces the endpoint tone. `vsync_wait.cpp` uses the
PC-98 GDC status port `0xA0` bit `0x20` to wait for the next rising edge;
TC4J emitted two real `in` polling loops and a far return. This is the
port-polling path only; interrupt-backed timing and actual emulator behavior
remain unobserved.

The 107-object no-archive link has 38 unresolved names, down exactly the
four fade entry points, and zero warnings. Both cold rounds agree on every
link-relevant and timestamp-normalized OMF object, with BGIMAGE raw
dependency timestamp drift only (receipt SHA-256
`1864605bef36322beb1e0c767e0797833b1cd5cf1b29846f74146a7ae136cdbf`
and `0997164f68ed9958ad3918d38f2ae82648badf90c47358bafe198f801abd17b4`).
The historical-library calibration links without near-call fixup errors;
its 573-site MZ passes the static relocation, entry, stack, and two DOS load
checks (receipt SHA-256
`a7a1e11638a557e7b8900a83704c67240b9e4e4f4bbeb5ec613a014be6517149`
and `0a74cd716243c54b36c918ef8b75438999c4bb708b097a409a7e59159f0c6827`).
The archive dictionary warning persists. The source manifest now lists 71
C/C++ and 36 ASM TUs.

`src/shared/hardware/joystick.asm` adds TH04-local first-controller detection,
YM2203 port I/O, DOS keyboard-buffer flush, and the two joystick state words.
It exports C and Pascal data names needed by the existing TH04 input producer.
The implementation follows the bounded TH04 branch of the local historical
library as semantic candidate evidence; its hardware behavior and target-byte
identity have not been tested. The 108-TU manifest has 71 C/C++ and 37 ASM
sources. Two cold no-archive links each leave 33 unresolved names, down exactly
`JS_START`, `JS_END`, `JS_SENSE`, `js_bexist`, and `js_stat`, with zero warnings.
All 108 link-relevant and timestamp-normalized OMF objects agree; BGIMAGE's
raw dependency timestamp alone differs (receipt SHA-256
`5a00760eaa7c64a2ba45640db384e959309020b36784659f05a6315d0ed030f2`
and `398da81efc01c1f6ce7c72220938b208b0f173ac04e0c90999dafca5119cd3ae`).
Historical-library calibration TLINK exits 0 with only its existing dictionary
warning; its 569 MZ relocations, entry, stack, and two DOS load tests pass
(link/audit receipts
`c44fe1f7287eca9386b7b8ed7a849c39acf54fbe7103bc5fc65bffa5ca9bc980`
and `114b891d372119d7c2446d28070130f05fe11892a55fe1a5ff3723a006c3a83a`).

The product link then exposed a separate, more serious ABI blocker: TLINK
accepted MAINE's far calls into seven existing near-return `FILE_*` owners
and into near-return `GRAPH_CLEAR`. Ordinary MZ relocation checks also passed.
The [far-call ABI note](TH04_NATIVE_FAR_CALL_ABI_V856.md) records the
rejecting MZ instructions, the conditional TH04 large-model repair, a
negative-control auditor, and replay commands. `FILE_SIZE` now has a local
owner as well. The 109-TU no-archive link at that checkpoint had 32 unresolved names and
zero warnings; two cold OMF builds agree after the known BGIMAGE timestamp
normalization. Historical-library calibration passes 569-site static MZ
relocation checks and the new nine-entry, 44-call ABI audit. This removes one
known stack corruption path; it is not runtime acceptance or product closure.

TH04-local clip defaults, `GRAPH_400LINE`, and the `GRAPH_START` plus
`PALETTE_INIT` C++ owner now close two more names. An initial TASM graph
startup attempt failed TLINK with a near-call fixup overflow into
`GRAPH_CLEAR`; the separate ASM palette initializer exposed the same problem
calling `PALETTE_SHOW`. These negative compiler observations are recorded in
the [far-call ABI note](TH04_NATIVE_FAR_CALL_ABI_V856.md). The maintained
startup uses a C++ producer and checked-in TH04 palette and clip data.
Two cold 112-TU no-archive builds agree on all link-relevant and
timestamp-normalized OMF objects, with BGIMAGE raw timestamp drift only;
both leave 30 names and zero warnings. Historical-library calibration TLINK
exits 0, its 594 MZ relocation sites pass the two-load audit, and the
expanded ABI audit checks 12 entries, 48 relocated direct far calls, and one
same-segment `push cs; call rel16`. Neither these static gates nor the earlier
OP boot diagnostic proves MAINE runtime behavior.

The next two TH04-local PC-98 graphics owners implement vertical GDC scroll
and byte-aligned GRCG rectangle fill. The
[focused hardware note](TH04_NATIVE_SCROLL_BOX_V858.md) records their
boundaries and static limits. The current 114-TU no-archive MAINE link has
28 unresolved names and zero warnings; two cold builds agree on all
link-relevant OMF records. Historical-library calibration links and passes
594 MZ relocation sites plus the expanded 14-entry call ABI audit. No
MAINE runtime checkpoint has exercised these hardware paths yet.

The [TH04-local PI cleanup owner](TH04_NATIVE_PI_FREE_V859.md) adds a 115th
source unit. Two cold no-archive builds leave 27 unresolved names with zero
warnings and agree on link-relevant and timestamp-normalized OMF objects.
Historical-library calibration passes 597 MZ relocation sites and 15 far
entry ABIs, including `GRAPH_PI_FREE` with `RETF 8`. `HMEM_FREE` remains a
separate TH04-owned requirement; no runtime PI cleanup observation exists.

The [TH04-local text gaiji writers](TH04_NATIVE_GAIJI_TEXT_V860.md) add one
translation unit and close two further names. Two cold 116-TU no-archive
builds leave 25 unresolved names with zero warnings and agree on
link-relevant and timestamp-normalized OMF records. Historical-library
calibration passes 597 MZ relocation sites and 17 far entry ABIs, including
the two gaiji returns. The PC-98 display path remains untested at runtime.

The [TH04-local graphics gaiji writers](TH04_NATIVE_GRAPH_GAIJI_V861.md)
add one source unit and close two more names. Two cold 117-TU no-archive
builds leave 23 unresolved names with zero warnings and agree on
link-relevant and timestamp-normalized OMF records. Historical-library
calibration passes 597 MZ relocation sites and 19 far entry ABIs. The CG,
GRCG, and VRAM behavior has not been exercised in a MAINE runtime scenario.

The [TH04-local graphics page copy](TH04_NATIVE_GRAPH_COPY_V862.md) adds one
source unit and closes one more name. Two cold 118-TU no-archive builds leave
22 unresolved names with zero warnings and agree on link-relevant and
timestamp-normalized OMF records. Historical-library calibration passes 599
MZ relocation sites and 20 far entry ABIs. It borrows temporary memory from
the still-unresolved TH04 heap owner; page-copy runtime behavior is untested.

The [TH04-local segmented heap](TH04_NATIVE_HEAP_V863.md) adds one source
unit and closes four MAINE-used names. Two cold 119-TU no-archive builds
leave 18 unresolved names and agree on link-relevant and timestamp-normalized
OMF records. Historical-library calibration passes 604 MZ relocation sites
and 27 far entry ABIs. An isolated DOS runtime probe passes allocation,
reuse, split, coalescing, and release; it also records a TC4J return-path
code-generation counterexample that the current source avoids. MAINE itself
still has no PC-98 runtime checkpoint.

The [TH04-local VSync interrupt owner](TH04_NATIVE_VSYNC_V864.md) adds one
assembly unit and closes three further names. Two cold 120-TU no-archive
builds leave 15 unresolved names. Its isolated DOS runtime probe checks the
INT 0Ah counters, far callback, and INT 0Ah/18h vector restoration. The
historical-library calibration passes 604 MZ relocation sites and 29 far
entry ABIs; PC-98 interrupt timing remains untested.

The [TH04-local gaiji storage and BFNT loader](TH04_NATIVE_GAIJI_STORAGE_V865.md)
add one C++ unit and close three more names. Two cold 121-TU no-archive
builds leave 12 unresolved names. A synthetic BFNT DOS probe passes the
backup/restore lifecycle and file validation using test-only DOS adapters;
the real CG port image and product file hook remain untested. Historical-
library calibration passes 613 MZ relocation sites and 32 far entry ABIs.

The [TH04-local packed-row renderer](TH04_NATIVE_PACK_PUT_V866.md) adds one
C++ unit and closes `GRAPH_PACK_PUT_8`. Two cold 122-TU no-archive builds
leave 11 unresolved names and agree on all link-relevant OMF records. An
isolated DOS probe verifies packed color planes and both clipping directions
against fake VRAM. The historical-library calibration passes 614 MZ
relocation sites and 33 far entry ABIs. PI decompression, hardware VRAM,
and MAINE runtime behavior remain separate gates.

The [TH04 PAR archive probe and local state owner](TH04_NATIVE_PF_ARCHIVE_V867.md)
recover 290 entries from the pinned HDI and private PI/BFNT fixtures. The
data owner closes `_bbufsiz`; two cold 123-TU no-archive builds leave 10
unresolved names and agree on link-relevant OMF. Historical-library
calibration still passes 614 MZ relocations and 33 far entry ABIs. The
TH04-local `PFSTART`/`PFEND` DOS INT 21h service remains unimplemented.

## Private PC-98 boot diagnostics

`scripts/probes/prepare_th04_maine_diagnostic_hdi.py` creates disposable
FAT12 HDIs from the hash-pinned private disk. It attests the original
`GENSO/MAINE.EXE` against `config/targets.toml`, checks both FAT mirrors,
and can install the relocation-audited historical-library calibration MZ.
The default AUTOEXEC invokes the disk's `GAME.BAT`, which first runs ZUN
initialization and then OP. An explicit `--original-maine` control uses the
same disk and AUTOEXEC with the original executable. The `--startup
direct-maine` mode exists only to reproduce a negative control. The script
never changes the pinned source HDI or commits game assets.

The paired `game-bat` preparations have private receipt SHA-256 values
`815b1b6b1da05fd3b6f196696f7fa20bd7e73c1cd44460e21af0f54262ee8ef5`
(original) and
`0dc9d005de02eea6cb1bc3a9979e4531bc1baa4f3cbbb7126b550de51aea1a33`
(calibration). `scripts/probes/run_th04_maine_diagnostic_hdi.py`, under
`xvfb-run -a`, copies each prepared image for execution, pins the DOSBox-X
binary and base configuration, records a 10-second X11 frame, and extracts
the DOS marker from the executed FAT12 image. Its receipts are
`859d2f2620912e8d9c760e66d1486737e0f45e4c12853e13c31ec1e081f07f4c`
and `ef3267998e2dad3ae0f0d1c2dc6d9c322cd5ea2c13e0342df1d357741a7084d8`.
Both executions reached the OP title sequence with pixel-identical frames,
identical emulator logs, passing boot markers, and only `START` in
`DIAG.TXT`. This is runtime-observed OP boot availability, **not** evidence
that the calibration MAINE MZ executed or behaved correctly.

Directly invoking the hash-attested original MAINE from AUTOEXEC, with the
same DOS environment but without the normal OP transition, displayed DOS's
invalid-interrupt `60H` error. The reproducible original direct-run receipt
is `aa900623c88145125268faa689fde4ced5786ef66ade995e0657a9741ecdedea`.
Therefore a direct MAINE launch is an invalid acceptance scenario: a candidate
failure there cannot be assigned to its link or relocations. A future runtime
Oracle must reach MAINE through the original `GAME.BAT → OP → MAIN → MAINE`
state transition and record a checkpoint proving MAINE was entered. The
calibration build still depends on historical `masters.lib`; even a successful
run would not close the TH04-only product link.

## Current build-graph gaps

The [BGM batch](TH04_NATIVE_BGM_V871.md) closes MAINE's four remaining
external BGM providers with TH04-local source. The 130-object no-support
MAINE link now succeeds; its MZ passes 656 static relocations and the expanded
far-call ABI gate. This is a standalone MAINE build candidate, with PC-98
game-entry runtime acceptance still open.

- MAIN C/C++ source has 764 quoted include sites whose paths do not resolve
  inside this repository, covering 102 distinct include paths, including
  headers and source fragments. This is a source-graph observation, not a
  count of missing semantic declarations.
- No checked-in OP product translation unit includes `src/op/main/main.inl`.
  MAINE now has `src/maine/end/entry.cpp` for `main.inl`; other bounded
  `.inl` fragments also lack a product TU; some are historical overlapping
  replay fragments and must be selected by ownership rather than bulk-included.
- MAINE now has an explicit 130-TU source/order manifest. The other artifacts
  still need manifests, and the four-artifact product link control plane must
  assign startup objects, system libraries, segments, and outputs. ReC98
  linker responses remain calibration evidence.
- OP, MAINE, and ZUN still need a product DIET/container route. ZUN's source
  composite additionally retains the documented usage-asset input.
- The private calibration disk has reached OP, but its MAINE entry remains
  unobserved. The new TH04-only MAINE MZ has not yet passed that game-entry
  scenario or the packed-container route.

## Build lane

TH095's local `scripts/build-whole.py` checks the manifest against all source
TUs before a real link and reports unique unresolved names separately from
their diagnostic line count. Its `audit-owner-relocations.py` inventories
relocation targets in writable and zero-fill data. The TH04 equivalent should
retain these ownership gates but use OMF PUBDEF/EXTDEF/FIXUPP, TLINK MAP, MZ
segment:offset relocation sites, and two DOS load segments rather than PE
DIR32/import-section rules. The TH095 scripts are method evidence only; their
addresses and libraries are unrelated to TH04.

Start with an explicit OP/MAINE source and object graph, then attach the
missing entry bodies and shared producers. Compile all declared TUs serially
with TC4J or TC4J `-B` plus TASM32 as required; validate each OMF record and
fixup. Link with TLINK without unresolved externals, duplicate storage, fake
stubs, or target-byte patches. Record flags, ordered objects/libraries, MAP,
MZ header, entry/stack, relocation sites and resolved symbol owners in a
repeatable receipt. The output may differ bytewise from the target.

After the unpacked programs link, package the three DIET artifacts and test
each candidate in a disposable copy of the legal game image. Boot the original
first under the same emulator configuration. Compare startup, menu, gameplay,
input, sound, save/config state, and transitions using memory, event, VRAM,
palette, and audio checkpoints. Repeat with a changed DOS load segment where
the emulator supports it. Freeze a runnable candidate by source revision and
artifact hashes; later source changes need fresh runtime validation.
