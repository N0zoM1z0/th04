---
name: th04-oracle
description: Design and run independent TH04 target, MZ, relocation, static, compiler, runtime, cross-emulator, or metamorphic Oracles for a falsifiable reconstruction claim. Use when semantics, ABI, layout, provenance, or comparator behavior is ambiguous.
---

# TH04 Oracle validation

Read `docs/ORACLES.md` and `config/oracles.toml`.  Preserve independence
between evidence classes.

## Validate one claim

1. State one falsifiable hypothesis and the observation that would reject it.
2. Select the smallest independent Oracle set that can distinguish competing
   explanations.
3. Attest every target, database, compiler, emulator, input, and starting state
   used by the experiment.
4. Record exact commands and input/output digests under `.analysis/`, then add
   the durable result to `config/evidence.csv`.
5. When Oracles disagree, retain both observations and narrow the hypothesis.
6. Promote only the supported portion.  A normalized, structural, runtime, or
   cross-game pass cannot override raw byte inequality.

Upstream claims use the `upstream` evidence class and cannot satisfy a required
Oracle.  Treat them as hypotheses until a local attested cold build passes the
entire gate.

Use `python3 scripts/smoke_oracles.py` after changing target parsing or binary
comparison.  Reject circular validation: decompiler output and source copied
from it are one hypothesis, not two Oracles.
