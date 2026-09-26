# TH04 reconstruction roadmap

Updated 2026-09-26 after the v825 OP EGC rectangle-copy hybrid closure. This is the
current next-work map. Use
`python3 scripts/status.py` and the live ledgers for counts; versioned
experiments and rejected approaches remain in `docs/reconstruction/` and
`config/evidence.csv`.

## Current baseline

| Artifact | Exact authored functions | Remaining | Reviewed boundaries |
| --- | ---: | ---: | ---: |
| OP.EXE | 89 / 93 | 4 | 93 / 93 |
| MAIN.EXE | 492 / 495 | 3 blocked | 495 / 495 |
| MAINE.EXE | 63 / 72 | 9 | 72 / 72 |
| ZUN.COM | 3 / 3 | 0 | 3 / 3 |

OP has 14,295 accepted decoded source-owner bytes out of 14,458 tracked;
MAINE has 11,187 out of 12,553; ZUN has 442 out of 442. These are not
packed-file coverage denominators. MAIN's 83,442 / 83,469 exact authored C/C++
bytes cover only its reviewed file-backed owner extents.

ZUN now has all three reviewed authored functions decoded-exact. OP and MAINE
have completed their current original-ASM boundary reviews. v820 remains a valid
negative for the ordinary TC4J / `-B` compiler paths, but v821 adds independent
TH03 OP/MAINL machine-code provenance for the SCORE byte-rotate primitive.
Keeping only that irreducible 8-bit ROR symbolic closes OP `scoredat_decode`
and `scoredat_encode`; focused replay and the canonical current-ledger replay
are raw-zero. v824 closes the internal 63-byte `egc_start_copy` helper,
and v825 closes the adjacent 111-byte `egc_copy_rect_1_to_0_16` outer body.
Both use narrow hybrid boundaries backed by independently restored release
targets rather than wholesale decompilation spelling. Two cold v825 OP links
preserve the complete `0xB0` `egcrect.cpp` producer and all 804 relocations,
and canonical replay passes 89/89 accepted OP slices. OP is therefore 89/93
with four blockers. Do not reopen the SCORE codecs or either accepted EGC
function without evidence that changes these accepted boundaries.

v822 then revisits `SND_SE_PLAY` and `_snd_se_update` without promoting them.
MAIN and OP independently share the complete 0x86 `th04/snd_se.cpp` fixed
producer, and a decompilation-shaped helper candidate reproduces both target
functions plus the full OP link raw-zero in two cold rounds. However the exact
frame-free parameter and BL/BH helper spelling first appears in a pinned ReC98
`[Decompilation]` commit and is explicitly marked as modder-facing bloat.
Those two functions are therefore narrowed to source-provenance blockers, not
decoded-exact functions.

v823 similarly closes the machine-code mechanism for the much larger 234-byte
SND_LOAD blocker without promoting it. Two cold wrapper builds that change only
the decompilation candidate _BX=_AX to TC4J integrated inline assembly reproduce
the complete target function raw-zero; relative to the natural OP baseline,
exactly the two bytes at 0xDE8B..0xDE8C change and all 804 ordered relocations
plus MAP ownership remain unchanged. A scan of 345 unique TC86 objects in the
pinned v401 snapshot finds only one other 89 C3, also from explicit asm in a
ReC98 [Decompilation] commit. Thus SND_LOAD is now a source-provenance-only
blocker: the exact compiler mechanism is known, but no independent ZUN source
witness justifies adopting that spelling.

The next bounded work should stay on one artifact at a time: pursue materially
new OP source/compiler/provenance evidence for the four remaining blockers
(`nopoly_b_put`, `SND_LOAD`, `SND_SE_PLAY`, `_snd_se_update`), or move to
MAINE if no such OP hypothesis exists. MAIN remains a side lane unless shared
source changes require replay.

## ZUN.COM: authored-function source authority closed

The natural Tiny-model MEMCHK `_main` at payload `0x26A7` is the first exact
ZUN authored function. Together with maintained shared `DOS_PUTS2` and
`DOS_MAXFREE`, it cold-links a raw-identical 4,066-byte MEMCHK component. The
helpers are library support, not authored-function credit. See
`docs/reconstruction/zun/TH04_ZUN_MEMCHK_NATURAL_EXACT_V773.md`.

The complete 1,141-byte ZUNINIT component now cold-links raw-identically from
six maintained symbolic original-style ASM units. The 223-byte launcher
selector also cold-links raw-identically from maintained ASM. These decoded
component results do not grant packed `ZUN.COM` exactness. The 8-byte selector
mover and 68-byte outer customization stub also have raw-identical maintained
ASM. The embedded 926-byte ONGCHK third-party library component now cold-links
raw-identically from maintained symbolic ASM. The generated selector directory,
external usage asset and DIET product build remain on the
artifact-closure path. The checked-in composite builder reproduces the
directory and complete decoded flat payload with maintained ONGCHK. A serial
source-driven replay now rebuilds all five maintained component groups before
the same raw-identical flat comparison; the external usage asset and older
resident-candidate integration path keep that composite replay diagnostic. Pinned
DIET 1.45f repacked the earlier mixed flats to byte-identical MZ targets; its
source-acceptance verdict remains none. Treat historical
disassembler-generated assembly as a candidate, not original-source evidence.

Resident cfg_init and _main are now decoded-exact. v817 found the missing
producer mechanism without importing inert barriers: maintained _main makes
the real /R not-resident path jump to the no-space failure return, and TC4J's
-B assembly backend followed by pinned TASM32 emits the target 252-byte
selective-tail body. Direct TC4J remains a 246-byte negative control. Two cold
v817 rounds link the complete 6,360-byte resident component raw-identically,
which also resolves every cfg_init FIXUPP value. v819 canonical decoded
acceptance raw-compares cfg_init, resident _main, and MEMCHK _main at zero
differences. This closes ZUN's authored-function queue, not whole ZUN.COM:
packed byte ownership, the composite product route, DIET closure, and runtime
validation remain separate artifact-closure work.

## OP.EXE and MAINE.EXE: strict source frontiers

OP's `CDG_PUT_NOCOLORS_8` now has a target-reviewed 0x51-byte FAR body and
an OP-local maintained original-style ASM unit whose complete 0x52-byte
contribution cold-links raw-zero. Its final byte is alignment and its ReC98
starting source retains candidate provenance. See the v806 focused note.

The complete `CDG_LOAD` and `CDG_PUT_8` original-ASM contributions are now
backed by maintained sources under `src/shared/formats/`. MAIN, OP, and MAINE
cold-link the respective 0x164-byte loader and 0x9E-byte renderer raw-identically,
with all ordered relocation positions preserved. OP/MAINE have decoded
`source-present` units; this does not alter authored-function counts or prove
packed-file offsets. See the v797 and v799 focused CDG notes under
`docs/reconstruction/op-maine/`. All 16 OP and 15 MAINE original-ASM
function-like observations now have reviewed boundaries and source-backed
modules; this does not grant authored C++ or packed-file credit.

The 0x10A-byte `INPUT_S` shared original-ASM contribution also cold-links
raw-identically across MAIN, OP, and MAINE from
`src/shared/hardware/input_s.asm`; see the v802 input note in the same
directory. The OP/MAINE rows remain decoded `source-present` units.

The separate 0x82-byte `BGIMAGE_PUT_RECT_16` ASM contribution now cold-links
raw-identically in OP and MAINE from `src/shared/hardware/bgimager.asm`.
Its ReC98 source origin remains candidate provenance; the local v805 replay
establishes artifact-specific bytes and layout. It does not change the C++
BGIMAGE producer or its accepted function count.

All authored candidate boundaries in both artifacts are reviewed. OP has four
nonexact functions: `nopoly_b_put`, `SND_LOAD`, `SND_SE_PLAY`, and
`_snd_se_update`. The internal `egc_start_copy` at payload `0xE3E8` is
decoded-exact as of v824, and `egc_copy_rect_1_to_0_16` is decoded-exact as
of v825. MAINE has nine: `regist_menu`,
`SND_LOAD`, `box_1_to_0_masked`, both SCORE codecs, `_snd_se_update`, the SCORE
EGC-start helper, `SND_SE_PLAY`, and `egc_start_copy`.

For OP, v820 still proves that the ZUN-successful TC4J `-B`/TASM32 path by
itself does not alter `nopoly_b_put`, the SCORE natural bodies, `SND_SE_PLAY`,
or `_snd_se_update`. v821 supersedes only the OP SCORE acceptance decision by
adding independent TH03 codec-machine-code corroboration and restricting
symbolic low-level source to the irreducible byte ROR. v824 applies the same strict hybrid rule to OP's internal EGC-start helper
using complete 63-byte identity in independently restored TH05 OP and MAINE
targets. v825 then narrows and accepts the adjacent 111-byte rectangle-copy
function using TH05 descendant outer-body evidence plus bounded release-target
lineage for the retained x86/PC-98 primitives. v822 adds materially new
same-game producer evidence for `SND_SE_PLAY` and `_snd_se_update`: their exact
machine-code shape is now reproducible, but the required helper spelling is
target-derived decompilation provenance, so both remain blocked. The remaining OP blockers now need new independent source provenance or materially
new compiler evidence. Do not promote byte-forcing
inline assembly, pseudo-registers, copied instructions, or inert optimizer
barriers without independent provenance. Resume a blocker only with a
materially new compiler mechanism or source-origin observation. See
`docs/reconstruction/op-maine/TH04_OP_SCORE_CODECS_HYBRID_V821.md`,
`docs/reconstruction/op-maine/TH04_OP_SND_SE_SHARED_V822.md`,
`docs/reconstruction/op-maine/TH04_OP_EGC_START_HYBRID_V824.md`,
`docs/reconstruction/op-maine/TH04_OP_EGC_COPY_HYBRID_V825.md`,
docs/reconstruction/op-maine/TH04_OP_SND_LOAD_PROVENANCE_V823.md,
`docs/reconstruction/op-maine/TH04_OP_STRICT_FRONTIER_V766.md`, and
`docs/reconstruction/op-maine/TH04_MAINE_STRICT_FRONTIER_V732.md`.

For a new exact function, review the complete physical owner, build its
natural source in isolated cold rounds, compare producer OMF/layout/ordered
relocations and every raw byte, bind the backend to the maintained source,
then replay the affected aggregate. A decoded match is not a packed-file match.

## Artifact closure

After source ownership and function queues close:

1. Cold-replay all maintained producers and affected shared dependencies.
2. Establish honest file-backed authored-source coverage for packed artifacts.
3. Reconstruct and compare complete MZ containers, DIET packing, relocation
   order, runtime/library bytes, padding, and overlays.
4. Check deterministic PC-98 runtime invariants under pinned scenarios.
5. Remove remaining calibration-scaffold build dependencies before claiming a
   standalone TH04 build.

The four original files and toolchain are locally attested candidates, not
independently proven pristine release media. Function exactness never implies
whole-artifact exactness.

## Handoff and hygiene

`docs/RE_HANDOFF.md` is the concise current-state index.
`docs/PROGRESS.md` and `docs/BOUNDARY_REVIEW.md` are generated views.
`docs/reconstruction/README.md` routes bounded historical evidence and
negative results. Private probe worktrees are disposable after required
receipts and digests are retained; preserve pinned targets, tools, databases,
runtime images, and configured replay inputs.
