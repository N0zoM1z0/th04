# Knowledge base

This file explains how to use TH04's durable knowledge. It is intentionally
short: individual discoveries live in `config/knowledge.csv`, observations in
`config/evidence.csv`, and current reconstruction state in the ledgers. Do not
append batch diaries or duplicate the current work queue here.

## Authority and routing

Use these sources in order:

1. `config/targets.toml` for artifact identity and provenance;
2. `config/units.csv` for accepted byte-owner state;
3. `config/th04_main_authored_functions.csv` for reviewed MAIN functions;
4. `config/th04_function_boundaries.csv` for the all-artifact candidate queue;
5. `config/evidence.csv` for replayable observations;
6. `config/knowledge.csv` for reusable facts, hazards, recipes, and negative
   results;
7. `docs/PROGRESS.md` and `docs/BOUNDARY_REVIEW.md` for generated summaries;
8. `docs/RE_HANDOFF.md` for the current phase and blockers.

Historical evidence IDs, paths, and batch numbers preserve provenance. They
are not a current queue and must not override the ledgers. In particular,
`module`, `partial`, or an old `vNN` frontier in an ID does not authorize a
source directory or determine what to reconstruct next.

## Entry contract

Every `config/knowledge.csv` row has:

- a stable ID and one kind: `fact`, `recipe`, `pattern`, `hazard`,
  `negative-result`, or `open-question`;
- the narrowest portability scope (`th04-main`, `th04`, `pc98-borland`,
  `control-plane`, and so on);
- one controlled confidence term from `AGENTS.md`;
- evidence IDs when the result was established locally;
- source references for reproducibility;
- one concise routing statement and a verification date.

Do not add a row merely because a decompiler emitted a plausible name. Add one
when a verified result changes how a later agent should search, test, build,
compare, or avoid a disproved approach.

## Query recipes

```bash
# Live reconstruction state
python3 scripts/status.py --json

# Remaining authored candidates
python3 - <<'PY'
import csv
with open("config/th04_function_boundaries.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["work_queue"] == "reconstruct" and row["accepted_state"] != "exact":
            print(row["artifact"], row["segment_identity"], row["segment_offset"],
                  row["boundary_state"], row["name"])
PY

# Scoped durable knowledge and linked evidence
rg 'snd_load|enemy_bullet_template_push|dialog_run' \
  config/knowledge.csv config/evidence.csv
```

Prefer `boundary_state=reviewed` or `corroborated`. A provisional entry needs
focused raw control-flow, return/shared-tail, table, alignment, and adjacent
ownership review before source work.

## Current global guardrails

- Target canonicality is `candidate-local-attested` until independently
  confirmed; a local legal image is not proof of an official pristine dump.
- `OP.EXE`, `MAINE.EXE`, and `ZUN.COM` are DIET-packed MZ containers. Their
  target stubs expose load-invariant payloads, but OP/MAINE analysis images use
  candidate-derived header/relocation topology and remain diagnostic views.
- Raw zero difference over the complete accepted extent is the only exact byte
  verdict. Normalized equality, source presence, a successful build, a Ghidra
  function, or upstream ReC98 status cannot promote a unit.
- Exact evidence is global, artifact-scoped, or unit-and-extent scoped as
  declared by `config/oracles.toml`; evidence for one unit cannot be borrowed
  by another.
- Turbo C++ memory model, near/far ABI, segment/group ownership, TASM/TLINK
  order, OMF FIXUPP order, and MZ relocation order are binary inputs.
- Whole-artifact function counts come from
  `config/th04_function_boundaries.csv`, never raw Ghidra totals or a linker
  public count.
- ReC98 and adjacent games are candidate/corroborating material. Product source
  belongs under `src/main/`, `src/op/`, `src/maine/`, `src/zun/`, or proved
  `src/shared/`; temporary declarations cross only `compat/rec98/`.

## Negative-result discipline

When a plausible experiment fails:

1. record the exact target, tool, input, and rejecting observation;
2. add an evidence row with `fail` or `inconclusive`;
3. add a scoped `negative-result` knowledge row only when it rules out a
   reusable search path;
4. update the focused blocker note if the result changes next-step routing;
5. delete bulky private build trees after the durable row and necessary digest
   have been validated.

Private `.analysis` paths in old evidence rows are historical receipt
locations, not a retention promise. The checked-in command, hashes, ledger
state, and current aggregate replay are the durable record; an old private
materialization may be regenerated when deeper archaeology is actually needed.

Current unresolved producer/code-generation negatives are summarized in
`docs/reconstruction/TH04_MAIN_FIXUP_CODEGEN_PROBES.md`. Resolved exact owners
and the replay contract are summarized in
`docs/reconstruction/TH04_MAIN_EXACT_BATCH.md`.
