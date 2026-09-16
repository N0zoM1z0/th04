# TH04 MAIN CIRCLE low-level render pair v189

## Scope and recovery

This packet continues target-first review of the `MAIN.EXE` CIRCLE_TEXT render
cohort from clean committed HEAD
`2fb7a7d757bea56b1bd950b1e6dc7d69b5358830`, tree
`4f024734550c3b9a62ce4b5de3a21be868f3035a`. The private target remains
ignored operator input with canonicality `candidate-local-attested`; it is never
modified, relocated, published, or committed.

The `.analysis/` tree measured **9,072,648,150 bytes** at entry. Mandatory
preflight, live status, and the function-boundary validator passed. All required
repository and Factory recovery/verification documents were mounted and read
before editing. `th04-ghidra` again exposed ten allowlisted operations and no
`get_metadata`; provider `check {}` passed for target `target:th04-main`, SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The repository-native read-only Ghidra check independently passed the 6,144-byte
MZ header, load mapping/digest, entry, 1,136 ordered relocations, and sampled
bytes. Required TC4J/TASM/TLINK surfaces passed; the optional host `wine64`
identity mismatch remains informational.

OP.EXE, MAINE.EXE, and ZUN.COM remain independent active queues. This packet
transfers no MAIN evidence or progress credit to them.

## Reviewed target extents

Fresh target-bound analysis was used as navigation only and receives no
exactness credit by itself:

- `@spark_render`: logical function CIRCLE_TEXT `0AAF:1710..1774`, load
  `0xC200..0xC264`, file `0xDA00..0xDA64`, size `0x65 / 101`; caller
  `_sparks_render`; no callees.
- load `0xC265`: the separate source-owned alignment NOP immediately following
  the logical spark renderer.
- `@item_splash_dot_render`: CIRCLE_TEXT `0AAF:1842..185D`, load
  `0xC332..0xC34D`, file `0xDB32..0xDB4D`, size `0x1C / 28`; caller exact
  `ITEM_SPLASHES_RENDER`; no callees.
- `sub_C34E`: load `0xC34E`, size `0x16`, still has no Ghidra function entry and
  remains a separate origin/source seam.

Neither low-level renderer contains an overlapping MZ relocation. The wider
CIRCLE seam keeps its previously reviewed source/layout boundaries intact.

## Independent cross-game producer evidence

Independent TH05 target evidence is unusually strong for this pair.
`item_splash_dot_render` is byte-identical in TH04 and TH05: both complete
28-byte bodies have SHA-256
`4898597cc5a5db17fa9565240b3a28784cb27361dc207996af2cafde6510b313`.

The TH04 and TH05 `spark_render` logical bodies are both exactly 101 bytes and
differ only at offsets `0x1F..0x20`, the linked `_sSPARKS` address word. After
zeroing only that link-resolved word, both original targets have normalized
SHA-256
`7d5119907caee763471fe69f3b9f07cc8896467419c1a45c7bc10141d94ce970`.
The remaining 99 bytes preserve the same register setup, `LODSW`, `LOOP`, ES
writes, vertical wrap, and return architecture.

ReC98 `.asm` files were used only as hypotheses and replay scaffolding. Git
history shows that the relevant files were introduced during later
reverse-engineering work; their file extension is not historical-source
authority.

## Bounded legal TC4J negatives

Natural C++ was tested before accepting an original-style assembly origin.
These probes contain no inline assembly, emitted byte arrays, `codestring`, fake
returns, target patches, or ABI aliases.

For `item_splash_dot_render`:

- an ordinary typed implementation with a local VRAM offset emits 48 bytes;
- removing the local emits 40 bytes;
- a named-parameter pseudo-register lifetime hypothesis emits 50 bytes;
- an unnamed fastcall/pseudo-register hypothesis reaches 32 bytes but TC4J
  still emits `MOV DX,AX; SAR DX,3; MOV AX,DX` instead of the target direct
  `SAR AX,3`;
- a C++ reference alias to the pseudo-register is rejected because TC4J cannot
  take an address of that register location;
- a natural `register` copy intended to preserve the X coordinate instead emits
  a 55-byte framed/spilled body.

The best direct-register probe therefore remains four bytes longer than the
28-byte target for a compiler-allocation reason rather than a link/layout
reason. No spelling matrix was pursued after the distinct mechanisms were
exhausted.

For `spark_render`, a typed/register pointer plus two-stage wrap loop emits
**165 bytes** with a BP frame. TC4J lowers source traversal to `MOV [SI]` plus
`ADD SI,2` and loop counters to `DEC/OR/JNZ`; it emits neither target `LODSW`
nor target `LOOP`. ES writes are the only low-level mechanism naturally shared
with the target. The probe CODE SHA-256 is
`c5073b0f64b87ff6c57a824b0cbef27a8d7c1ffcfe83520a4cd71ac00f5c297d`.

Together with the independent cross-game target invariants, these bounded
compiler negatives meet the same evidence standard already used by accepted
TH04 original-style assembly owners such as the v184 CIRCLE tile core.

## Maintained symbolic assembly

v189 adds two maintained symbolic TASM sources:

- `src/main/spark/render.asm`, SHA-256
  `fabd1630eb20f3f99ecbed6ba92e2c45c886ac3cd7777fd0f313b39a19432b0d`;
- `src/main/item/splash_dot_render.asm`, SHA-256
  `b0e63104c53d7fd112bfec1c1a1126b7c56a32e46f03408da6bac35aa08d7417`.

They contain symbolic instructions, labels, constants, and the external
`_sSPARKS` symbol only. They do not contain target-derived byte arrays or
patching directives.

The spark physical owner intentionally includes the genuine assembler `EVEN`
byte after the logical function. Its physical extent is therefore CIRCLE_TEXT
`0AAF:1710 size 0x66`, load `0xC200..0xC265`, file `0xDA00..0xDA65`: the
101-byte function plus its source-owned alignment NOP. This is real source
layout ownership rather than inert padding.

Standalone TASM32 5.0 probing emits a valid spark OMF with one EXTDEF/FIXUPP for
`_sSPARKS` and exactly `0x66` CIRCLE_TEXT bytes. All fixed bytes match the target;
the only pre-link difference is the ordinary `_sSPARKS` offset fixup word. The
symbolic logical body normalized the same way as the two original targets also
hashes to `7d511990...`.

The splash-dot standalone TASM object emits exactly `0x1C` CIRCLE_TEXT bytes and
matches all 28 target bytes before linking because it has no external fixup.

## Physical ownership transfer and replay contract

Before v189, replay-only `cirsuf188.asm` physically owned load
`0xC200..0xC2ED`, and `cirsuf186.asm` physically owned the later splash-dot and
following residual. v189 transfers only the proven prefixes:

- `sprendr.asm`: `0xC200..0xC265`, `0x66` physical bytes;
- remaining `cirsuf188.asm`: `0xC266..0xC2ED`, `0x88` zero-credit residual;
- existing v186/v187 natural owners remain at their exact locations;
- `spldot.asm`: `0xC332..0xC34D`, `0x1C` bytes;
- remaining `cirsuf186.asm`: starts at `0xC34E` and preserves all later bytes.

The first focused replay exposed an important control-plane issue rather than a
source-byte failure. Both new owners already passed raw/MAP/relocation gates,
but the accepted v188 item-splash unit still required its old monolithic
`cirsuf188.asm` auxiliary extent at `0xDA00 size 0xEE`. That receipt is retained
as diagnostic evidence only and receives no exactness credit.

The exact replay driver now supports a fail-closed, trigger-scoped auxiliary
extent replacement. `auxiliary_extents_override_when_unit` selects a complete
`auxiliary_extents_override` list only when the splitting unit participates in
the replay. Without the trigger, the historical baseline auxiliary extent list
is unchanged. An active missing/empty/malformed override fails closed. Unit
tests cover baseline, active override, and missing-active-override behavior.
This transfers zero-credit physical ownership without deleting an older unit's
layout checks.

A dedicated baseline regression, `gptweb-v189-v188-baseline-regression-001`,
then replays v188 without selecting v189. All 117 selected owners pass twice
with `failures=[]`, receipt SHA-256
`53821bf6c346605d9c2ce5503dd8a4263675820c6b8c18e36963586641cfb09d`.
Both builds use the historical `cirsuf188.asm` auxiliary extent at CIRCLE_TEXT
`0xC200 size 0xEE`, proving the trigger-scoped override preserves the baseline
path as well as the split path. This is control-plane regression evidence, not
additional byte-exactness credit.

## Exact Oracles

Focused run `gptweb-v189-circle-lowlevel-render-focused-candidate-002` selects
119 owners and passes both isolated cold builds with `failures=[]`. Receipt
SHA-256 is
`d47912741917e947d5559d1ec190d406696d0c4b792160c66d671e51c58831a8`.

A/B identities are deterministic:

- `sprendr.obj` SHA-256
  `a3a837753ddecf693b4274a4193a0c07b44b3791cd9a5663ed0fed5922fe1b76`;
- `spldot.obj` SHA-256
  `acb097364d43e724e346723e66c2dd37b11258ee39abc3f2f7a6bf72a01d68cb`;
- focused MAP SHA-256
  `b1ce9200cc25b1e4db25dd595b8be90fa1d15f63e9d8a52cdb7c8d4212d4855a`;
- focused candidate MAIN SHA-256
  `518811db1bf863343e7bf69fdad4613c537cd08113b8a40538e0519ee46512df`.

The spark physical target/candidate slice SHA-256 is
`de134fdb8ebba22790f0a6434bcd54ea2fe2d3c20a12d72b5e1ca3159b6f0fed`;
the splash-dot target/candidate slice SHA-256 is the cross-game invariant
`4898597c...`. Both have exact MAP and ordered-MZ-relocation overlap. The split
v188 and v186 residual auxiliary extents also pass raw/MAP/relocation gates.

Candidate aggregate
`gptweb-v189-circle-lowlevel-render-aggregate-candidate-001` temporarily enables
both v189 units, runs the complete default cohort with no `--unit` selection,
and restores the tracked manifest byte-for-byte. All **223** owners pass twice,
`failures=[]`; receipt SHA-256 is
`79f9e05366924ea4fabe570be52c8d2341d1d7dc573802827f49400e743857ea`.
The enabled manifest SHA-256 is
`01058995277ddf54dbc45921023cc09eb994e574d17c8b5588490d840bd853ad`;
the pre-promotion manifest restores to `73b961033cad4561e591676e3f3853291ea686dbaedf026c18523be2c8a4abc7`.
A/B MAP SHA-256 is
`11fb0d13a30807b1d02fe14b0362aa77e16ade11c137e04b5a6c355951c752d4`
and candidate MAIN remains
`205e42067b0eb3534dc83deba125ebf845c1c153f6515ebe60430d3a79f21bd9`.

After promotion, tracked aggregate
`gptweb-v189-circle-lowlevel-render-aggregate-final-001` again passes all 223
default owners twice with `failures=[]`. Receipt SHA-256 is
`e7eae826a7a0e42f4ce37a1029f8e7c5731427f3e28cd23772b02c4c60f29492`;
it is bound to tracked manifest SHA-256 `01058995...`. The same A/B new-object,
MAP, and candidate-MAIN identities remain deterministic.

### Committed LF source rebind

Before commit, Git attributes exposed that `.asm` files are stored with LF line
endings. The original reconstruction probes used CRLF working copies, so those
receipts remain historical promotion evidence but are not the final source-byte
binding. The exact bytes stored by Git have SHA-256
`fabd1630eb20f3f99ecbed6ba92e2c45c886ac3cd7777fd0f313b39a19432b0d`
for `spark/render.asm` and
`b0e63104c53d7fd112bfec1c1a1126b7c56a32e46f03408da6bac35aa08d7417`
for `splash_dot_render.asm`.

Focused run `gptweb-v189-circle-lowlevel-render-focused-lf-003` replays these
exact LF source bytes: 119 owners pass twice with `failures=[]`, receipt SHA-256
`89224f049c1ec289996daba08921093dca328f568d2fa34c05c9bc7272443d7a`.
A/B `sprendr.obj` SHA-256 is
`562fb7e7199cc10cc7605f5a3f65fc90a62dbe9724e21e29127de1dd376ba7ee`;
A/B `spldot.obj` SHA-256 is
`5895044935f549af67f9dc45950501b780675c4463beafaafcb53e60d2900d8b`.
Their normalized object identities remain `41140d66...` and `76f514c3...`, and
the focused MAP and linked MAIN identities are unchanged.

Current no-unit aggregate
`gptweb-v189-circle-lowlevel-render-aggregate-final-lf-002` passes all **223**
tracked default owners twice with `failures=[]`, receipt SHA-256
`ae4ee4a28a982ee3d55b6e4128e9e94aa4c2177361a19ba493970f2479215adc`.
It binds live exact-manifest SHA-256
`a13775eb9fecc08e398e0c3fa552bce86530fcba52bd18ede24f2c5b9839e1d9`;
A/B MAP remains `11fb0d13...` and candidate MAIN remains `205e4206...`. This is
the authoritative clean-checkout source binding for v189.

## Ledger and accounting effect

The two low-level functions are no longer counted as candidate authored C/C++
functions. Their reviewed target boundaries remain in the boundary ledger but
are reclassified to `origin=original-asm`, `work_queue=attest-asm`, preserving
logical sizes `0x65` and `0x1C`. Exactness is represented by the separate
physical original-ASM unit ledger.

After v189:

- reviewed MAIN C/C++ exact bytes remain **75,195 / 80,680 = 93.201537%**;
- reviewed MAIN C/C++ exact functions are **455 / 480 = 94.791667%**;
- MAIN boundary routing is 530 authored-C/C++ candidates: 455 exact, 25 blocked,
  50 unreviewed, plus 38 ASM-attestation observations;
- exact original-style ASM ownership is **21 units / 3,258 bytes**, up by the
  v189 pair's 130 physical bytes.

The two accounting planes are intentionally not merged. Reclassifying a
function to original-style assembly must not manufacture C/C++ progress.

OP.EXE, MAINE.EXE, and ZUN.COM remain independent active queues with 94, 72, and
13 unreviewed authored candidates. No MAIN credit transfers to them.

## Analysis retention and verification planes

The four v189 replay trees raised `.analysis/` to **9,324,232,904 bytes** before
cleanup. After retaining compact failed/focused/candidate/final receipts, final
objects/MAP, cross-game target slices, bounded compiler probes, and standalone
TASM objects, the failed focused tree, successful focused tree, and candidate
aggregate tree were deleted as current-session reproducible output. The complete
post-promotion aggregate is retained as the current cold baseline. The
session-only DOS `C:\V189` probe workspace was also removed after all referenced
artifacts were retained.

After bounded cleanup `.analysis/` measures **9,152,590,464 bytes**, net growth
**79,942,314 bytes** from entry. v189 scratch measures **15,786,584 bytes**,
including **15,760,869 bytes** of compact `durable-final`; the retained current
committed-LF post-promotion aggregate `aggregate-final-lf-002` measures
**64,020,463 bytes**. The superseded pre-normalization full final tree was removed
after its receipt had been retained compactly. Older baselines,
Factory-accepted v188 provenance, private targets, toolchains, Ghidra/Wine
state, and legacy or unknown analysis content were untouched.

Repository-native exact physical ownership for the two v189 symbolic ASM units
is established. Standalone TH04 product compile/link closure, whole-image
exactness, runtime-storage identity, runtime-scenario validation, portable
runtime validation, independent pristine-release provenance, and v189 Factory
Truth-Kernel acceptance remain separate and unestablished at this checkpoint.

## Next structural packet

Continue the same CIRCLE lifecycle rather than taking an unrelated tiny helper.
The strongest next packet is `_sparks_render` plus `_sparks_update`, with
`sub_C34E` retained as the adjacent Ghidra-missed boundary/origin seam.

`_sparks_render` already has a v188 compiler negative: Borland's ordinary
three-integer fastcall ABI uses BX for the third argument while the target caller
loads only CL, and a pseudo-register expression also exposes SHR/SAR shape
drift. v189 now establishes that its callee `@spark_render` is itself an
original-style register/LODSW/LOOP producer, so the caller's CL-based interface
must be reevaluated as an origin clue rather than papered over with a fake C++
ABI. `_sparks_update` retains its v186 71-vs-76 legal-TC4J negative. Use fresh
TH04/TH05 target comparison and bounded producer probes before deciding whether
either function belongs on the natural-C++ or original-style ASM track.
