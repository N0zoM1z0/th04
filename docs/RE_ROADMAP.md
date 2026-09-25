# TH04 reconstruction roadmap

Updated 2026-09-25. This is a current plan, not a chronological experiment log.
Historical versioned experiments live in `config/evidence.csv`,
`config/knowledge.csv`, and `docs/reconstruction/`. Current counts always come
from `python3 scripts/status.py`.

## 1. Current baseline

Active non-MAIN state:

| Artifact | Exact functions | Pending / blocked | Boundary reviewed / corroborated / provisional |
| --- | ---: | ---: | ---: |
| OP.EXE | 64 | 29 / 0 | 70 / 15 / 8 |
| MAINE.EXE | 41 | 31 / 0 | 47 / 20 / 5 |
| ZUN.COM | 0 | 11 / 2 | 13 / 0 / 0 |

OP has 6,277 decoded source-owner bytes, of which 5,840 are in exact accepted
functions. MAINE has 4,037 decoded source-owner bytes, of which 3,662 are exact.
No packed-file authored-source denominator is currently honest for OP, MAINE,
or ZUN.

MAIN remains a side lane unless materially new evidence requires reopening it.

## 2. Finish small and medium natural-source functions

Select work by reviewed physical `body_span`, evidence maturity, and producer
isolation. Do not sort by Ghidra auto-function size alone.

For each candidate:

1. target-first boundary/control-flow review;
2. source/origin review independent of candidate names;
3. natural C/C++ codegen probe;
4. focused A/B cold build;
5. complete function raw-byte comparison;
6. complete producer/OMF/layout/ordered-relocation comparison;
7. fail-closed acceptance backend binding;
8. full artifact aggregate replay before exact promotion.

Known small low-level gaps are already recorded and should not consume routine
retry cycles: MAINE `egc_start_copy`, MAINE `box_1_to_0_masked`, OP
`SND_SE_PLAY`, OP `_snd_se_update`, and OP `nopoly_B_put`.

The OP SCORE codecs and MAINE SCORE codecs remain maintained/source-present but
nonexact. Do not make them exact by transcribing target rotate/register forms.

## 3. Transition deliberately into large owners

Once the remaining small/medium natural-source queue is exhausted, large
functions become the primary work rather than a reason to stop.

Large-owner workflow:

1. close the full physical extent, including shared tails and interleaved data;
2. identify jump tables, tables, embedded data and indirect targets;
3. partition the function into independently understood semantic regions;
4. reconstruct natural source region by region without claiming partial exact
   credit for the whole function;
5. build focused codegen probes for difficult regions;
6. only after the complete function closes, run producer/link/relocation/raw
   exactness and the aggregate gate.

MAINE payload `0xA847..0xADBB` demonstrates this workflow end to end. v571
closed the `0x575`-byte physical owner and adjacent 16-entry CS-relative table
despite Ghidra's truncated two-range auto-function; v685 then reproduced the
complete body, table, `CUTSCENE_TEXT` producer, and all 559 ordered relocations
from maintained natural C++. The reconstruction label `script_op(unsigned char)`
is retained, without claiming recovery of ZUN's original symbol spelling.

Current reconstruction order is **MAINE.EXE → OP.EXE → ZUN.COM**. `MAIN.EXE`
is outside the current campaign; progress there should not distract from the
remaining packed-artifact work.

## 4. Boundary, origin and ASM ownership continue in parallel

OP still has corroborated/provisional boundaries and four origin-open authored
candidates. MAINE still has corroborated/provisional boundaries and 18
origin-open candidates. Continue boundary/source-origin review alongside code
reconstruction; do not wait until the end to resolve ownership.

Keep authored C/C++ reconstruction separate from ASM attestation. A raw-equal
ASM slice does not become authored C/C++ progress without independent source
ownership.

## 5. ZUN provenance/component work

All 13 current authored physical ZUN boundaries are reviewed. The remaining
problem is not routine disassembly:

- 11 candidates still lack accepted source/origin ownership;
- two C++ items remain blocked;
- generated/disassembler-derived assembly is provenance evidence only;
- the 36-byte graph-clear/library-origin result is support evidence, not
  authored-function exact credit.

Resolve ZUNINIT/MEMCHK provenance, runtime/library component ownership, and the
two blocked C++ items before exact promotion. Do not use generated assembly as
a substitute for source authority.

## 6. Artifact closure

After function queues close:

1. cold replay all accepted producers from maintained source;
2. verify OMF identity, segment/group ownership and ordered MZ relocations;
3. establish an honest file-backed authored-source coverage denominator;
4. evaluate DIET-packed reconstruction separately from decoded-function
   exactness;
5. run runtime invariants under the pinned PC-98 environment;
6. add cross-emulator evidence only when a separately pinned secondary runtime
   exists.

Function exactness is not whole-program exactness. Packed bytes, runtime
behavior, component provenance and source coverage remain distinct claims.

## 7. Hygiene rules

`docs/RE_HANDOFF.md` is the concise current-state resume file. Do not append
chronological “latest cohort” sections indefinitely. Put bounded historical
findings in reconstruction notes and evidence ledgers.

`.analysis/reconstruction/probes/` is scratch output unless a checked-in script
or retention config explicitly depends on a directory. Use
`scripts/prune_analysis.py` to review and prune ignored outputs. Preserve pinned
targets, toolchains, runtime images, Ghidra inputs/exports, retained source
snapshots and explicitly configured dependencies. Literal paths embedded in
historical evidence or diagnostic scripts are provenance records, not a promise
that the old expanded worktree still exists; rebuild or restore those snapshots
before intentionally rerunning an old diagnostic.
