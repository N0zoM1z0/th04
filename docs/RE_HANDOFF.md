# TH04 reconstruction handoff

Updated 2026-09-25 after the strict-source MAINE SCORE-tail review. This file is the concise
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
| MAINE.EXE | 66 / 6 / 0 | 57 | 15 / 0 | 11,202 |
| ZUN.COM | 13 / 0 / 0 | 0 | 11 / 2 | 404 |

These are decoded-function/source-owner counts, not packed-file coverage.
There is still no honest packed-file authored-source denominator for OP, MAINE,
or ZUN.

The accepted decoded-source bytes represented by the acceptance ledger are
5,840 for OP and 9,836 for MAINE. The remaining tracked MAINE source-owner
bytes are source-present/nonexact diagnostics, not partial exact credit.

## What changed in the MAINE campaign

The campaign started this pass at 41/72 accepted MAINE functions and now sits
at 57/72. The following natural-source owners were independently re-reviewed,
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
The strict-source current-ledger MAINE aggregate is v724: 57 unique registered
slices, all 57 raw-zero. Its preserved private receipt is:

.analysis/reconstruction/receipt-archive/v724-maine-score-rect-canonical-receipt.json

SHA-256:
6c5da132bf829cdb3207d987066381a3c82afb8b3fbdb06588c7a9f56972c995

v721/v722 reached 59 raw-zero slices but are now diagnostic only: regist_menu
and the SCORE EGC-start helper required decomp.hpp compiler-shape circumvention
helpers. Their boundaries remain reviewed and their source remains useful, but
they are deliberately excluded from exact counts.

## Important remaining MAINE work

Do not treat the remaining queue as an ASM-only queue merely because old rows
say target-derived-asm. Re-check source ownership first.

- regist_menu at 0xC814 now has a reviewed 0x39C-byte physical boundary, but
  ordinary C++ remains 920/924. v720 reaches raw equality only via
  optimization_barrier(), explicitly documented as an anti-optimizer
  reconstruction helper, so no exact credit is granted.
- the SCORE EGC-start helper at 0xCBB0 has a reviewed 0x43-byte boundary, but
  ordinary source remains 66/67. keep_0(0) can force the target MOV AX,0 form,
  but that helper is explicitly an anti-peephole reconstruction mechanism and
  therefore receives no exact credit.
- SND_SE_PLAY (0xD5A0, 57 bytes) and _snd_se_update (0xD5DA, 76 bytes) now
  have reviewed physical boundaries. Their historical candidate source uses
  code-shape forcing and has no natural exact credit.
- SND_LOAD at 0xD112 is reviewed and 234 bytes but remains nonexact.
- egc_start_copy (52 bytes), box_1_to_0_masked (134 bytes), and the
  88/101-byte SCORE codecs remain natural-source codegen blockers.

Continue mixing large/medium owners with leaf functions. Select by physical
ownership and producer structure, not by whichever function looks easiest.

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
