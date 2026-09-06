---
name: th04-kb
description: Record or retrieve durable TH04 reconstruction knowledge with scoped confidence, linked evidence, negative results, and agent-routing metadata. Use after a verified discovery, reusable experiment, disproved approach, changed blocker, or when starting work that should reuse prior experience.
---

# TH04 knowledge capture and retrieval

Read `docs/KNOWLEDGE_BASE.md`, then query `config/knowledge.csv` by artifact,
subject, and kind before beginning a new experiment.

## Capture

1. Decide whether the result is a fact, recipe, pattern, hazard,
   negative-result, or open-question.
2. Give it the narrowest scope where the evidence is valid.
3. Use the controlled confidence terms from `AGENTS.md`.
4. Link local observations through `config/evidence.csv`; link focused notes or
   external corroboration through `source_refs`.
5. State what changes for the next agent.  Avoid transcript summaries and raw
   decompiler output.
6. Run `python3 scripts/validate_tracking.py`.

Keep contradictions as separate evidence or open hypotheses.  Never overwrite
an older fact silently when stronger evidence invalidates it; update its state
with an explanation in a focused note or Git history.
