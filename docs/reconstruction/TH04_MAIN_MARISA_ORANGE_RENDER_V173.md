# TH04 MAIN Marisa / Orange renderer seam v173

## Scope

This packet reviews and reconstructs the immediate `MAIN__TEXT` / `MAIN_TEXT`
renderer seam preceding the exact v172 HUD/score producer in
`th04-main / MAIN.EXE`. It closes two natural TC4J physical producers while
keeping one target layout byte explicitly outside authored C++ credit.

The selected private target remains read-only operator input with canonicality
`candidate-local-attested`. Nothing here proves independently pristine release
provenance, standalone TH04 product closure, or runtime behavior.

## Target, analysis, and toolchain identity

Factory provider `th04-ghidra` passed target attestation for repository `th04`,
target `target:th04-main`, size 156,258 and SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The provider exposes ten registered read-only operations and no `get_metadata`
operation, so no undiscovered schema was invented. Repository-native
`python3 scripts/ghidra.py th04-main check` independently passed the MZ header and
load mapping, entry point, all 1,136 relocation-table records, load-module
identity, and sampled target bytes.

Pinned TC86 Borland C++ 4.02, TASM32 5.0, and TLINK 6.10 attestation passed. The
optional host `wine64` file hash remains informational under the documented
policy; the required portable identities and execution probes passed.

## Target-first physical ownership

The previous v172 cold MAP still placed one historical target-derived
`th04_main.asm` `MAIN__TEXT` contribution at `0AAF:419E`, size `0x178`, covering
load `0xEC8E..0xEE05`. Target/TASM/raw review splits that physical window into:

| Physical item | Map/load extent | File extent | Size | Target SHA-256 |
| --- | --- | --- | ---: | --- |
| Marisa renderer producer | `0AAF:419E`, `0xEC8E..0xEDE0` | `0x1048E..0x105E0` | `0x153` | `e093297e7cc146a4af6e96338761ca2e99a4f9148a074e2499195fe0131b9f35` |
| independent zero seam | `0AAF:42F1`, load `0xEDE1` | `0x105E1` | `0x1` | `6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d` |
| Orange backdrop producer | `0AAF:42F2`, `0xEDE2..0xEE05` | `0x105E2..0x10605` | `0x24` | `6c6d3dbd230171ca2fbc2615720705382fb61868865ade815f8e1be9b1abf07f` |

Exact v172 begins immediately afterward at load `0xEE06`. The combined historical
window SHA-256 is
`295e05adacd481cb7567f3d511df3d3f02491d5a574b1229079ece8202ba18a1`.

The target has seven MZ relocations in the Marisa producer, preserving original
table order:

`0xEDD5, 0xEDB7, 0xEDA2, 0xED5D, 0xED47, 0xECF2, 0xECC4`.

The zero seam and Orange producer have no overlapping MZ relocations.

## Authored function boundaries

Three logical authored functions become reviewed exact:

| Function | Analysis address | Load address | Size | Boundary anchor |
| --- | ---: | ---: | ---: | --- |
| `marisa_bits_render()` | `0x1EC8E` | `0xEC8E` | `0xE3` | complete Ghidra/raw body + target near CALL at `0x1EDBE` |
| `marisa_fg_render()` | `0x1ED71` | `0xED71` | `0x70` | complete Ghidra/raw body + target callback word at `0x2E369` |
| `orange_backdrop_colorfill()` | `0x1EDE2` | `0xEDE2` | `0x24` | Ghidra-missed; TASM/raw + target callback word at `0x2E07C` |

Fresh target-bound Ghidra constructs `marisa_bits_render()` as one contiguous
227-byte body and `marisa_fg_render()` as one contiguous 112-byte body. The only
direct caller of the internal bit renderer is `marisa_fg_render()`. Ghidra has no
function at the Orange entry.

The maintained exact boss stage-setup owner independently anchors both callbacks:
its target code stores MAIN_01 offset `0x4281` at analysis `0x2E369`, resolving to
`0x1ED71`, and stores offset `0x42F2` at `0x2E07C`, resolving to `0x1EDE2`.
The Orange body ends at `0x1EE05`; exact v172's first target Ghidra entry begins at
`0x1EE06`.

The function reviewer was narrowly extended so an explicit
`[[reviewed_exact_internal]]` callback may name a separately exact pointer owner,
require an exact reconstruction-only MAP public, and close at the exact code-owner
end when there is no immediately following public. Existing policies retain their
previous defaults. A focused regression test covers the new separate-pointer-owner
and owner-end route; the complete function-review test module passes.

Candidate-state and post-promotion function reviews are byte-identical, report
SHA-256
`e2833f96888051658ed9aaef9819f8edcfd587981c6b93e438dd6a860c996ec3`.
The maintained function ledger adds exactly the three v173 IDs. Generic reviewer
output also normalizes unrelated historical fields; those rewrites are not
adopted.

## Natural source and compiler diagnosis

Maintained natural source is:

- `src/main/boss/marisa4_render.cpp`, SHA-256
  `dcc815b90eefe4445fc9b2928752b87280f47cf4e271036d7e84c461f61373cc`;
- `src/main/boss/orange_backdrop.cpp`, SHA-256
  `1d2496b62fe66e6f7edec384cbabc6050c6018d67e8825957071009cab73e9bd`.

The Marisa source preserves the independently established 26-byte bit-entity ABI,
GRCG line topology, clipping, damage-flash behavior, boss renderer phases, and
near callback ABI. Production-profile TC4J naturally emits exactly `0x153` CODE
bytes with `marisa_fg_render()` at relative offset `0xE3`.

Compiler-only target comparison exposed two semantic corrections before linked
replay: the bit sprite's left coordinate is offset by half its width, and the
ordinary no-damage boss path reuses the live AX top coordinate while the big
explosion path still uses DI. After those corrections every non-fixup code byte
has target shape; linked cold replay closes the fixups and all seven relocations.

The first Orange source shape emitted `0x28` bytes. Its only four-byte structural
excess was a BP frame (`PUSH BP; MOV BP,SP` / `POP BP`). The source-level Borland
`#pragma option -k-` mechanism selects the target frameless function. `_AL ^= _AL`
selects target `XOR AL,AL`. The resulting natural function emits exactly `0x24`
CODE bytes; linked replay resolves its two same-segment fill calls to target
operands.

No maintained v173 source uses inline assembly, `__emit__`, target-derived byte
arrays, `#pragma codestring`, fake returns, inert padding, copied target bytes,
target/object patching, or an ABI lie.

## Physical-producer negative evidence

A deliberately combined natural Marisa+Orange translation unit is retained as
negative compiler evidence. TC4J emits `0x177` CODE bytes, places Orange directly
at relative `0x153`, and emits no byte between the two natural functions. The
target physical window is `0x178`, with byte `0x00` at relative `0x153` and
Orange at relative `0x154`.

Therefore the target zero at load `0xEDE1` is not credited to either natural C++
producer. Replay hash-extracts the historical one-byte seam into
`th04/m4gap.asm` through
`config/replay/th04_main01_marisa_orange_gap_v173.asm.in`. This is layout/Oracle
plumbing only and receives zero authored-function and zero natural-C++ byte
credit. The combined-TU result is recorded as
`ev-th04-main-marisa-orange-producer-split-negative-v173`.

The initial focused attempt failed before any build because an over-strict transform expected a second Orange public after
the historical body had already been removed. That replay-harness error has zero
exactness credit; the unnecessary transform was removed before the successful
run.

## Focused cold replay

Focused `gptweb-v173-marisa-orange-focused-candidate-002` passes a 126-owner
dependency closure twice with `failures=[]`. Receipt SHA-256 is
`03a1cdcea9416b47c24b40babd88fdc201f79773387a8a5843dc8661573d59ad`.
Both focused candidate MAIN images are
`689a7978340b95602d2d9d727ed76c2628baca48343265d53c290b13413c2494`.

Marisa A/B results:

- raw/map/seven-ordered-relocation exact;
- `m4rend.obj` raw SHA-256
  `542a52312cef859442d77a2ebaa4fba673d46584734d5d8c3a46fd8c050b0b56`;
- dependency-timestamp-normalized OMF SHA-256
  `ed52a5e26246406b50e0b310351930022132f83c63c69eeb2d5a0501b6fcc89a`.

Orange A/B results:

- raw/map/empty-relocation-overlap exact;
- `orange.obj` raw SHA-256
  `dbb0d41e218906c29fdcfa4752b823339a9d2b7ea55c121704de2954d1d23b85`;
- dependency-timestamp-normalized OMF SHA-256
  `537206cb63a8dda4b3feab316d08730979a24fa3cb56083a006f932867b35570`.

The one-byte auxiliary gap is raw/MAP exact in both builds. TASM dependency-time
metadata makes its raw object identity differ between A/B, while the narrowly
normalized object identity is deterministic; no code/data byte is normalized.

## Aggregate promotion gates

Candidate-state aggregate
`gptweb-v173-marisa-orange-aggregate-candidate-001` passes all 205 default owners
twice with `failures=[]`. Receipt SHA-256 is
`ad865e66d5d5f56df4f0116d6210395d147c050e1cad73c7aa996d38ac6d1a66`.

Post-promotion aggregate
`gptweb-v173-marisa-orange-aggregate-final-001` passes the same 205-owner cohort
twice from ledger extents, again with `failures=[]`. Receipt SHA-256 is
`6cb676f05c3e85d2aa1e4ce07aa377869489fbec1676cd10d85f32f85d4f9882`.
Replay manifest SHA-256 is
`6edb2fe027383c52b6770a2295368453a8df67724387bf9244fd787e94791aa4`.
Both aggregate A/B candidate MAIN images are
`931ad9d05c41397d145c85ef531dbdd4d544dc40ae95d99c60caade5c89270e1`.

## Accounting and verification planes

After v173, live MAIN reviewed authored accounting is:

- exact bytes: **69,325 / 72,829 (95.188730%)**;
- exact functions: **410 / 423 (96.926714%)**;
- reviewed blocked functions: **13**;
- unreviewed MAIN authored candidates: **114**;
- exact original-style ASM remains a separate plane at 17 units / 2,526 bytes.

The one-byte `0xEDE1` seam is excluded from natural-source exact-byte credit.
These are moving reviewed denominators, not percentages of `MAIN.EXE` or TH04 as
a whole product, and they remain below the campaign pressure target.

Repository-native owned-extent/function exactness is established for both v173
natural producers and the complete post-promotion 205-owner cohort. Standalone
TH04 production-source/link closure is not established. Runtime-storage identity
is not established. No runtime scenario was executed. Whole-image exactness and
portable-runtime validation are not established. No v173 Factory Truth-Kernel
acceptance is claimed here. Independent pristine-release provenance remains open.

`OP.EXE`, `MAINE.EXE`, and `ZUN.COM` remain independent artifact queues and gain
no MAIN-derived source or exactness credit from v173. `ZUN.COM` remains an MZ
artifact despite its extension.

Full repository CI passes on the maintained v173 state, including the complete
function-review regression suite, tracking/ledger validation, private target
checks, cross-game Oracle calibration, Ghidra/JDK identity, live Ghidra database
replay, and Ghidra mutation smoke. `git diff --check` passes.

## Next boundary-connected packet

The next hard packet should continue left across the segment/TU seam immediately
after exact `yuuka5_fg_render()`:

- Ghidra-missed `kurumi_backdrop_colorfill()` begins at load `0xEA70`; target
  TASM closes its function before the NOP at `0xEA89`;
- load `0xEA89` is an independent one-byte NOP seam;
- `STAGES_TEXT` `carpet_lighting_put_new(int,unsigned int)` is a fresh contiguous
  `0x5A` Ghidra body at `0xEA8A..0xEAE3`, with exact `stage4_render()` as its sole
  direct caller;
- the complete `0xEA70..0xEAE3` physical window has no MZ relocation overlap and
  ends exactly before accepted `stage4_render()` at `0xEAE4`.

Review this as a cross-segment physical-producer/source-language question rather
than reconstructing the small backdrop alone. Determine whether the backdrop is
natural C++, original-style assembly, or another frame-option case, and preserve
the NOP seam separately unless compiler/link evidence proves ownership.
