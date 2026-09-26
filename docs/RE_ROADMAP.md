# TH04 reconstruction roadmap

Updated 2026-09-26. This is the current work order. Use
`python3 scripts/status.py` and the live ledgers for counts; versioned
experiments and rejected approaches remain in `docs/reconstruction/` and
`config/evidence.csv`.

## Current baseline

| Artifact | Exact authored functions | Remaining | Reviewed boundaries |
| --- | ---: | ---: | ---: |
| OP.EXE | 85 / 93 | 8 | 93 / 93 |
| MAIN.EXE | 492 / 495 | 3 blocked | 495 / 495 |
| MAINE.EXE | 63 / 72 | 9 | 72 / 72 |
| ZUN.COM | 1 / 3 | 2 blocked | 3 / 3 |

OP has 13,847 accepted decoded source-owner bytes out of 14,284 tracked;
MAINE has 11,187 out of 12,553; ZUN has 38 out of 442. These are not
packed-file coverage denominators. MAIN's 83,442 / 83,469 exact authored C/C++
bytes cover only its reviewed file-backed owner extents.

The active reconstruction queue is **ZUN.COM source and component ownership**.
The remaining OP and MAINE functions are reviewed source/codegen frontiers;
MAIN remains a side lane unless new evidence changes a blocker.

## ZUN.COM: establish source authority

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
ASM. The generated selector directory, remaining external component ownership,
and DIET product build remain on the artifact-closure path. The checked-in
composite builder reproduces the directory and complete decoded flat payload
with explicitly mixed maintained/external inputs; this is a diagnostic
integration Oracle, not product-source closure. Treat historical
disassembler-generated assembly as a candidate, not original-source evidence.

Resident `cfg_init` and `_main` remain blocked. The natural `_main` is six bytes
short of the target selective print-call shape; `cfg_init` still has linked
fixup differences downstream of that layout shift. Continue from the recorded
compiler and provenance negatives rather than importing inert optimizer
barriers. Keep component equality, function equality, and whole ZUN.COM file
equality separate.

## OP.EXE and MAINE.EXE: strict source frontiers

All authored candidate boundaries in both artifacts are reviewed. OP has eight
nonexact functions: `nopoly_b_put`, both SCORE codecs, `SND_LOAD`,
`SND_SE_PLAY`, `_snd_se_update`, `egc_copy_rect_1_to_0_16`, and the internal
`egc_start_copy` candidate at payload `0xE3E8`. MAINE has nine: `regist_menu`,
`SND_LOAD`, `box_1_to_0_masked`, both SCORE codecs, `_snd_se_update`, the SCORE
EGC-start helper, `SND_SE_PLAY`, and `egc_start_copy`.

Current natural-source and compiler-profile probes do not close their recorded
register, segment-order, rotate, port-write, or optimizer shapes. Do not
promote byte-forcing inline assembly, pseudo-registers, copied instructions,
or inert optimizer barriers as authored C/C++ without independent source
provenance. Resume a blocker only with a materially new compiler mechanism or
source-origin observation. See
`docs/reconstruction/op-maine/TH04_OP_STRICT_FRONTIER_V766.md` and
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
