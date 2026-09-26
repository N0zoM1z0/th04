# TH04 reconstruction roadmap

Updated 2026-09-26 after the v821 OP SCORE codec closure. This is the
current next-work map. Use
`python3 scripts/status.py` and the live ledgers for counts; versioned
experiments and rejected approaches remain in `docs/reconstruction/` and
`config/evidence.csv`.

## Current baseline

| Artifact | Exact authored functions | Remaining | Reviewed boundaries |
| --- | ---: | ---: | ---: |
| OP.EXE | 87 / 93 | 6 | 93 / 93 |
| MAIN.EXE | 492 / 495 | 3 blocked | 495 / 495 |
| MAINE.EXE | 63 / 72 | 9 | 72 / 72 |
| ZUN.COM | 3 / 3 | 0 | 3 / 3 |

OP has 14,121 accepted decoded source-owner bytes out of 14,284 tracked;
MAINE has 11,187 out of 12,553; ZUN has 442 out of 442. These are not
packed-file coverage denominators. MAIN's 83,442 / 83,469 exact authored C/C++
bytes cover only its reviewed file-backed owner extents.

ZUN now has all three reviewed authored functions decoded-exact. OP and MAINE
have completed their current original-ASM boundary reviews. v820 remains a valid
negative for the ordinary TC4J / `-B` compiler paths, but v821 adds independent
TH03 OP/MAINL machine-code provenance for the SCORE byte-rotate primitive.
Keeping only that irreducible 8-bit ROR symbolic closes OP `scoredat_decode`
and `scoredat_encode`; focused replay and the canonical current-ledger replay
are raw-zero. OP is therefore 87/93 with six blockers. Do not reopen the SCORE
codecs without evidence that changes this accepted boundary. The next bounded
work should stay on one artifact at a time: pursue a materially new OP source or
compiler hypothesis for the six remaining blockers, or move to MAINE if no such
OP hypothesis exists. MAIN remains a side lane unless shared source changes
require replay.

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

All authored candidate boundaries in both artifacts are reviewed. OP has six
nonexact functions: `nopoly_b_put`, `SND_LOAD`, `SND_SE_PLAY`,
`_snd_se_update`, `egc_copy_rect_1_to_0_16`, and the internal
`egc_start_copy` candidate at payload `0xE3E8`. MAINE has nine: `regist_menu`,
`SND_LOAD`, `box_1_to_0_masked`, both SCORE codecs, `_snd_se_update`, the SCORE
EGC-start helper, `SND_SE_PLAY`, and `egc_start_copy`.

For OP, v820 still proves that the ZUN-successful TC4J `-B`/TASM32 path by
itself does not alter `nopoly_b_put`, the SCORE natural bodies, `SND_SE_PLAY`,
or `_snd_se_update`. v821 supersedes only the OP SCORE acceptance decision by
adding independent TH03 codec-machine-code corroboration and restricting
symbolic low-level source to the irreducible byte ROR. The remaining six OP
blockers still lack comparable source/compiler evidence. Do not promote
byte-forcing inline assembly, pseudo-registers, copied instructions, or inert
optimizer barriers without independent provenance. Resume a blocker only with
a materially new compiler mechanism or source-origin observation. See
`docs/reconstruction/op-maine/TH04_OP_SCORE_CODECS_HYBRID_V821.md`,
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
