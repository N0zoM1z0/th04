# TH04 reconstruction handoff

Updated 2026-09-25 after accepting the remaining MAINE staff-roll helpers. This file is the concise
resume index. Do not infer current progress from historical experiment
directories, old probe paths, candidate source names, or previous session
prose.

Authoritative live state comes from:

- config/th04_function_boundaries.csv
- config/th04_decoded_function_acceptance.csv
- config/units.csv
- config/evidence.csv
- python3 scripts/status.py
- generated docs/PROGRESS.md and docs/BOUNDARY_REVIEW.md

The active campaign order is **MAINE.EXE → OP.EXE → ZUN.COM**. Do not spend
reconstruction time on MAIN.EXE in this campaign unless materially new
evidence requires reopening it.

## Resume checks

Before target-dependent work:

~~~sh
git status --short
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/audit_compat_dependencies.py --check
python3 scripts/boundary_review/validate_function_boundary_ledger.py
~~~

Run a cold decoded-function aggregate only when promoting a function; it is too
expensive to use as a routine status command.

Current target canonicality is candidate-local-attested. This validates the
local target identity and reconstruction surfaces; it is not a claim that the
inputs are independently proven pristine release media.

## Current non-MAIN state

| Artifact | Boundary reviewed / corroborated / provisional | Function exact | Pending / blocked | Tracked decoded source-owner bytes |
| --- | ---: | ---: | ---: | ---: |
| OP.EXE | 93 / 0 / 0 | 85 | 8 / 0 | 14,284 |
| MAINE.EXE | 72 / 0 / 0 | 63 | 9 / 0 | 12,553 |
| ZUN.COM | 13 / 0 / 0 | 0 | 11 / 2 | 404 |

These are decoded-function/source-owner counts, not packed-file coverage.
There is still no honest packed-file authored-source denominator for OP, MAINE,
or ZUN.

The accepted decoded-source bytes represented by the acceptance ledger are
13,847 for OP and 11,187 for MAINE. The remaining tracked MAINE source-owner
bytes are source-present/nonexact diagnostics, not partial exact credit.

## What changed in the MAINE campaign

The campaign started this pass at 41/72 accepted MAINE functions and now sits
at 63/72. The following natural-source owners were independently re-reviewed,
cold-built, producer-checked, relocation-checked, aggregate-gated, and accepted:

- script_op at 0xA847: 1,397-byte body plus adjacent compiler switch table;
- cutscene_animate at 0xADFC: 212 bytes;
- box_bg_allocate_and_snap at 0xA4AE: 209 bytes;
- pic_put_both_masked at 0xA37F: 303 bytes;
- pi_put_quarter_8 at 0xCDAB: 177 bytes;
- MAINE _main at 0xA102: 400 bytes;
- staff background expansion helper at 0xB25B: 54 bytes;
- staffroll_animate at 0xB44D: 826 bytes;
- graph_3_digit_put at 0xB787: 150 bytes;
- skill-percentage owner at 0xB886: 245 bytes;
- graph_fraction_of_million_put at 0xB97B: 119 bytes.
- sub_B81D at 0xB81D: 105 bytes.
- sub_B9F2 at 0xB9F2: 386-byte body plus 13 compiler auxiliary bytes.
- sub_BB81 at 0xBB81: 1,376-byte body plus 23 compiler auxiliary bytes;
- verdict_animate at 0xC0F8: 81 bytes.
- SCORE rectangle-copy helper at 0xCBF3: 134 bytes (isolated natural-source v723 replay).
- three staff dissolve renderers at 0xAED0/0xB02D/0xB144: 349 / 279 / 279 bytes;
- three staff dissolve loops at 0xB291/0xB31E/0xB3AC: 141 / 142 / 161 bytes.
The strict-source current-ledger MAINE aggregate is v727: 63 unique registered
slices, all 63 raw-zero. Its preserved private receipt is:

.analysis/reconstruction/receipt-archive/v727-maine-staff-dissolves-canonical-receipt.json

SHA-256:
d86732f3c46baf5c8b9fe79d65abf4476cdd870353c1de96483bc48b5a632287

All 72 authored MAINE candidates now have reviewed physical boundaries. No
corroborated-only or provisional authored rows remain. The remaining 9
functions are source/codegen blockers, not boundary-ownership blockers.

v721/v722 remain diagnostic 59-slice raw-equality evidence for the SCORE tail;
they do not override the strict source-admissibility decision for regist_menu
or the SCORE EGC-start helper.

## Important remaining MAINE work

Nine reviewed functions remain nonexact:

- regist_menu at 0xC814, 924 bytes: ordinary C++ remains 920/924; v720 raw
  equality requires optimization_barrier() and is diagnostic only;
- SND_LOAD at 0xD112, 234 bytes;
- box_1_to_0_masked at 0xA78F, 134 bytes;
- scoredat_decode / scoredat_encode at 0xC149 / 0xC1A1, 88 / 101 bytes;
- _snd_se_update at 0xD5DA, 76 bytes;
- SCORE EGC-start at 0xCBB0, 67 bytes: ordinary source remains 66/67; raw
  equality requires keep_0(0) and is diagnostic only;
- SND_SE_PLAY at 0xD5A0, 57 bytes;
- egc_start_copy at 0xA2D6, 52 bytes.

Physical ownership is no longer the bottleneck in MAINE. Continue with natural
source/codegen experiments, mixing the large regist_menu/SND_LOAD/box owners
with smaller codec, EGC, and sound leaves. Do not lower the source-admissibility
bar merely because target bytes can be forced.

## Reusable negative results

Do not retry these without a materially new compiler mechanism or provenance:

- egc_start_copy: ordinary C/C++ forms still fail to reproduce the target
  AX/DX port-write ordering. Reversed inline-helper arguments collapse back to
  the direct form; assignment-expression variants add variable-preservation
  instructions.
- SCORE codecs: shift/or rotate expressions stay expanded. v760 additionally
  checks TC4.02 itself: _crotr and _rotr remain FAR RTL calls, direct __rotr__
  emits 16-bit ROR AX,3, and pragma-intrinsic forcing is rejected. No tested
  compiler surface emits the target byte-memory ROR form.
- MAINE/OP sound-effect code: pseudo-register forcing is diagnostic evidence,
  not acceptable authored-source provenance.
- box_1_to_0_masked still differs in low-level EGC setup ordering under
  natural source.
- v730 local-optimizer probes do not close regist_menu: local -O- can select
  the target direct-memory CMP, but then loses the target redundant JMP and
  shifts later branch layout; local switch remains the same four-byte MOV/OR
  frontier.
- v731 _snd_se_update indexing probes keep direct/pointer/cast source at
  77 bytes versus target 76; local/register/union index forms grow to 79-89.
  Only explicit BL/BH shaping reaches target and remains diagnostic only.
- v732 -O-/-O- -y/-Z- probes do not change egc_start_copy's DX-before-AX
  outport lowering. Box remains 134 bytes under -O- and grows to 137 under
  -Z-. No new optimizer setting closes either function.

Target-derived assembly, decompiler helper assembly, pseudo-register forcing,
or copying target instructions never earns authored C/C++ exact credit by
itself.

## Boundary and ownership hazards

Use reviewed physical ownership, not raw auto-function spans. The resolved
script_op case is the reference example: Ghidra exposed incomplete ranges,
while target-first review closed one 0x575-byte owner and later natural C++
reproduced the complete body, switch table, producer, and all ordered
relocations.

The historical sub_B9F2 auto-function was another example: Ghidra exposed two
ranges, but target-first TASM review closed the real 0x182-byte function body
plus a separate 0x0D compiler switch-table extent before sub_BB81. Do not
reopen that resolved boundary from the old auto-function span.


## OP campaign after the MAINE strict frontier

MAINE remains at the strict-source frontier of 63/72: its remaining nine
functions all have reviewed physical boundaries but are blocked on natural
source/codegen/provenance. OP work has therefore resumed without lowering the
MAINE acceptance bar.

The first current OP promotion takes two large natural-source functions:

- op_animate at 0xCCD2: 652 bytes;
- playchar_menu at 0xD708: 777 bytes.

Both functions end exactly at their own TLINK producer boundaries. v735
replaces only their maintained bodies inside the pinned current OP translation
units and reproduces the complete bodies, producers, linked program image, and
all 804 ordered relocations in two cold rounds.

The second OP promotion closes the remaining natural m_char.cpp functions:

- raise_bg_allocate_and_snap at 0xCF5E: 417 bytes;
- raise_bg_put at 0xD0FF: 244 bytes;
- pic_put at 0xD3A2: 195 bytes;
- shottype_titles_put at 0xD465: 304 bytes;
- shottype_title_box_put at 0xD595: 187 bytes.

v738 replaces only those five bodies and preserves the complete 0xAB3
m_char.cpp producer, full linked OP program image, and all 804 ordered
relocations in two cold rounds.

The third OP promotion closes the six remaining op_main.cpp functions and
corrects five old provisional multi-range boundaries using TC86-generated
PROC/ENDP plus target switch-table ownership:

- start_demo at 0xA9C9: 228-byte body plus 8 compiler table bytes;
- main_unput_and_put at 0xAAB5: 277-byte body plus 13 compiler bytes;
- option_unput_and_put at 0xABD7: 576-byte body plus 17 compiler bytes;
- main_update_and_render at 0xAE96: 432-byte body plus 12 compiler table bytes;
- option_update_and_render at 0xB052: 780-byte body plus 25 compiler bytes;
- OP _main at 0xB377: 296 bytes.

v742 preserves the complete 0xD53 OP_MAIN_TEXT producer, full linked OP image,
and all 804 ordered relocations in two cold rounds. The final current-ledger OP
aggregate is v744: 77 unique registered slices, all 77 raw-zero. Preserved
receipt:

.analysis/reconstruction/receipt-archive/v744-op-main-remaining-canonical-receipt.json

SHA-256:
e24181d3572c50ff6948e7db0fd761b867ff4a8251ae299d3ae0c204f16a3b7f

The fourth OP promotion closes the two remaining natural setup submenus:

- setup_bgm_menu at 0xB794: 285 bytes;
- setup_se_menu at 0xB8B1: 285 bytes.

v745 preserves the complete 0x5A6 OP_SETUP_TEXT producer, full linked OP image,
and all 804 ordered relocations in two cold rounds.

The final current-ledger OP aggregate is v747: 79 unique registered slices, all
79 raw-zero. Preserved receipt:

.analysis/reconstruction/receipt-archive/v747-op-setup-submenus-canonical-receipt.json

SHA-256:
30294667ce38d0a1aef1871ffd0b36128dfcea4858fbe5553e5b399e022ec910

The fifth OP promotion closes two large Music Room functions:

- polygons_update_and_render at 0xC04E: corrected 502-byte physical body
  (Ghidra had only 397 reachable bytes across the same span);
- musicroom_menu at 0xC3B7: 451 bytes.

v748 preserves the complete 0x6A5 OP_MUSIC_TEXT producer, full linked OP image,
and all 804 ordered relocations in two cold rounds.

The final current-ledger OP aggregate is v751: 81 unique registered slices, all
81 raw-zero. Preserved receipt:

.analysis/reconstruction/receipt-archive/v751-op-music-remaining-canonical-receipt.json

SHA-256:
47cd2eb24d5318e826f65ed2ad971c257bf4935f160e4fb89417a659f1bda448

The sixth OP promotion replaces a stale source-ownership assumption for the
complete ZUNSOFT block. The current MAP has a zero-sized historical th04_op.asm
contribution and a real 0x490-byte th04/zunsoft.cpp owner at the same address.
Current natural C++ is independently cold-replayed for:

- ZUNSOFT_PYRO_NEW at 0xBA45: 132 bytes;
- ZUNSOFT_UPDATE_AND_RENDER at 0xBAC9: 299 bytes;
- ZUNSOFT_PALETTE_UPDATE_AND_SHOW at 0xBBF4: 65 bytes;
- zunsoft_animate at 0xBC35: corrected 623-byte body, followed by a 0x31-byte
  compiler-owned alignment/sparse-switch extent.

v753 preserves the complete 0x490 linked ZUNSOFT producer, current OP image,
and all 804 ordered relocations in two cold rounds. Legacy TASM PROC metadata
is retained only as boundary corroboration for the entries where it exists.

The final current-ledger OP aggregate is v755: 85 unique registered slices, all
85 raw-zero. Preserved receipt:

.analysis/reconstruction/receipt-archive/v755-op-zunsoft-natural-canonical-receipt.json

SHA-256:
14a85e9330db6b1728bf7264ab5e8eebf608deb54a5d9dc427d6c17fd2a146f2

v757 then closes the final two non-reviewed OP physical boundaries in the
0xB0 egcrect SHARED producer:

- egc_copy_rect_1_to_0_16 at 0xE378: 111-byte body;
- one compiler/code-shape NOP at 0xE3E7;
- internal egc_start_copy at 0xE3E8: 63-byte body;
- one compiler/code-shape NOP at 0xE427.

TC86 generated PROC/ENDP structure supplies the missing ownership evidence for
the internal helper. The current source deliberately uses inline ASM,
pseudo-registers, and codestring NOPs, so v757 is diagnostic boundary evidence
only and does not increase exactness.

OP now has all 93/93 authored physical boundaries reviewed and 85/93 accepted
functions. The remaining eight are source/codegen/provenance blockers rather
than unresolved boundary problems.

## Analysis/worktree hygiene

Private probe worktrees are disposable after durable evidence and digests are
recorded. A path under .analysis/reconstruction/probes/ in historical evidence
is a provenance path, not a promise that the directory still exists.

Long-lived private inputs currently required by checked-in tooling include:

- .analysis/targets/
- .analysis/toolchain/
- .analysis/ghidra/
- .analysis/runtime/images/zun.hdi
- .analysis/gpt-web/v401-master-vs-object-replay-001
- .analysis/gpt-web/v402-opmusic-hybrid-replay-001
- .analysis/gpt-web/v489-bgimage-hybrid-replay-003
- .analysis/reconstruction/diet-replay/
- .analysis/reconstruction/v218-th04-*-diet/
- .analysis/reconstruction/probes/v546-zun-runtime-inventory-001

The 2026-09-25 final cleanup archived 39 current probe receipt.json files to:

.analysis/reconstruction/receipt-archive/probes-cleanup-20260925-final.tar.zst

Archive SHA-256:
55d36ec2f03e92462f84783189af87b5b72c8b8238cb9ebc031dc18aed605b42

The v708 focused and v710 canonical receipts are also retained directly in the
receipt archive. The cleanup then removed 51 rebuildable probe directories and
five Python cache directories. Only v546-zun-runtime-inventory-001 remains
expanded under .analysis/reconstruction/probes/. Observed .analysis usage after
pruning is about 1.6 GiB.

Use the following in dry-run mode before future cleanup:

~~~sh
python3 scripts/prune_analysis.py --compact-referenced --prune-probes --prune-caches
~~~

Add --apply only after reviewing the plan.

## End-of-session checks

~~~sh
python3 scripts/status.py
python3 scripts/preflight.py
python3 scripts/boundary_review/report_function_boundaries.py --check
python3 scripts/progress.py --check
python3 scripts/ci.py
git diff --check
git status --short
~~~

Leave no untracked candidate source or stale generated documentation behind.
Checkpoint commits in this campaign use the gpt-web: ... subject format.
