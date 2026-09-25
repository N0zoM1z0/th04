# TH04 reconstruction roadmap

Updated 2026-09-25 after the MAINE cleanup pass. This is a current plan, not a
chronological experiment log. Historical packets live in config/evidence.csv,
config/knowledge.csv, and docs/reconstruction/. Numeric truth always comes from
python3 scripts/status.py and the generated progress report.

## 1. Current baseline

| Artifact | Exact functions | Pending / blocked | Boundary reviewed / corroborated / provisional |
| --- | ---: | ---: | ---: |
| OP.EXE | 64 | 29 / 0 | 70 / 15 / 8 |
| MAINE.EXE | 52 | 20 / 0 | 59 / 10 / 3 |
| ZUN.COM | 0 | 11 / 2 | 13 / 0 / 0 |

MAINE currently has 8,129 tracked decoded source-owner bytes, of which 7,754
are in accepted exact functions. OP has 6,277 tracked source-owner bytes, of
which 5,840 are exact. These are not packed-file denominators.

The active reconstruction order is **MAINE.EXE → OP.EXE → ZUN.COM**.
MAIN.EXE is outside this campaign.

## 2. Finish MAINE deliberately

Keep both boss-sized and leaf-sized work active. For every candidate:

1. re-check physical ownership against the target;
2. independently re-check source/origin rather than trusting an old label;
3. use natural C/C++ source, not target-derived instruction transcription;
4. cold-build the complete producer in two isolated rounds;
5. require full function raw equality, producer equality, OMF/layout checks,
   and ordered relocation equality;
6. bind the replay backend fail-closed;
7. run one current-ledger aggregate before exact promotion.

Good next source-led targets include the 105-byte sub_B81D candidate in the
pinned gv.cpp producer. The natural sub_B9F2 candidate is also visible there,
but its physical owner is still provisional/non-contiguous and must be reviewed
before source promotion.

Do not spend routine cycles on known low-level blockers (egc_start_copy,
box_1_to_0_masked, SCORE rotate codegen, sound pseudo-register shapes) without
a materially new mechanism.

## 3. Continue resolving ownership in parallel

MAINE still has 10 corroborated and 3 provisional authored boundaries. Some
rows marked target-derived-asm now have independently located natural candidate
source in retained producers; update source ownership only after the target
boundary is re-reviewed.

Keep authored C/C++ reconstruction separate from ASM attestation. Raw-equal ASM
does not become authored-source progress without provenance.

## 4. Then OP.EXE

After the MAINE queue is materially reduced, apply the same target-first and
producer-complete process to OP. The OP SCORE codecs, SND_SE_PLAY,
_snd_se_update, and nopoly_B_put remain useful codegen blockers, not targets to
force exact with pseudo-registers or copied instructions.

Continue correcting corroborated/provisional OP boundaries before estimating
work from automatic analysis spans.

## 5. Then ZUN.COM

All 13 current authored physical ZUN boundaries are reviewed. The hard part is
source/component provenance:

- 11 candidates still lack accepted source/origin ownership;
- two C++ items remain blocked;
- generated/disassembler-derived assembly remains zero-credit provenance for
  authored-source exactness;
- support-library/component replacement evidence must remain separate from
  authored-function credit.

Resolve provenance and component ownership first; exactness follows only after
a source-authoritative cold replay.

## 6. Artifact closure comes last

Function exactness is not whole-file exactness. After the function queues close:

1. cold replay all maintained producers;
2. verify segment/group topology and ordered relocations;
3. establish an honest file-backed authored-source coverage denominator;
4. evaluate DIET packing separately from decoded-function exactness;
5. run runtime invariants in the pinned PC-98 environment.

## 7. Hygiene

docs/RE_HANDOFF.md is the current resume document. docs/PROGRESS.md and
docs/BOUNDARY_REVIEW.md are generated current-state views. Versioned
reconstruction notes are historical unless explicitly listed as active.

Probe worktrees under .analysis/reconstruction/probes/ are scratch output.
Archive receipts and digests, then prune them with scripts/prune_analysis.py.
Do not delete pinned targets, toolchains, Ghidra databases/exports, retained
source snapshots, runtime images, or DIET inputs merely because they are
ignored by Git.
