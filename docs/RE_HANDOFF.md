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
| OP.EXE | 70 / 15 / 8 | 64 | 29 / 0 | 6,277 |
| MAINE.EXE | 72 / 0 / 0 | 63 | 9 / 0 | 12,553 |
| ZUN.COM | 13 / 0 / 0 | 0 | 11 / 2 | 404 |

These are decoded-function/source-owner counts, not packed-file coverage.
There is still no honest packed-file authored-source denominator for OP, MAINE,
or ZUN.

The accepted decoded-source bytes represented by the acceptance ledger are
5,840 for OP and 11,187 for MAINE. The remaining tracked MAINE source-owner
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
- SCORE codecs: shift/or rotate expressions stay expanded; tested Borland
  rotate-intrinsic variants did not produce the target byte-memory ROR form.
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

The same caution applies to sub_B9F2: its current automated body is
non-contiguous, so the apparent span to the next MAP public is not yet a valid
function extent.

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
