# Knowledge base

The knowledge base is durable project memory for future agents.  It records
facts, recipes, reusable patterns, hazards, negative results, and open
questions without converting uncertainty into folklore.

`config/knowledge.csv` is the canonical index.  This document explains how to
use it and expands only the entries that need context.  Evidence remains in
`config/evidence.csv`; falsifiable unsettled claims remain in
`config/hypotheses.csv`.

## Entry contract

Every knowledge row has:

- a stable ID and one kind: `fact`, `recipe`, `pattern`, `hazard`,
  `negative-result`, or `open-question`;
- the narrowest portability scope (`th04-main`, `th04`, `pc98-borland`,
  `control-plane`, and so on);
- one of the controlled confidence terms from `AGENTS.md`;
- evidence IDs when the fact was established locally;
- source references for reproducibility;
- a concise statement and verification date.

Do not create an entry merely because a decompiler emitted a plausible name.
Do create one when a result will change how the next agent searches, probes,
builds, compares, or avoids a known dead end.

## Current target knowledge

- The public manifest pins the extracted Japanese HDI and executable hashes,
  not the private outer archive.  Canonicality is
  `candidate-local-attested` until independent confirmation.
- The Anex86 HDI header is 4096 bytes.  The `TOUHOU` FAT12 boot sector begins
  at file offset 38912 and uses 1024-byte logical FAT sectors even though the
  HDI geometry reports 512-byte physical sectors.
- TH04 `OP.EXE`, `MAIN.EXE`, and `MAINE.EXE` are MZ.  `ZUN.COM` is also MZ;
  extensions are not reliable format evidence across the five games.
- TH02 and TH05 `ZUN.COM` are flat COM in the local corpus, while TH03 and TH04
  launcher containers begin with MZ.  Parser routing must inspect bytes.

## Current Oracle knowledge

- Raw equality is the only exact verdict.
- Relocation-normalized equality is useful for isolating changed linked
  segment words, but it is explicitly diagnostic.
- Header, ordered relocation table, relocation set, load module, normalized
  load module, and overlay are separate dimensions.
- The TH01-TH05 original corpus plus injected mutations validates parsing and
  failure routing over real artifact diversity.
- The locally pinned build-chain candidate passes 16 identity surfaces and two
  deterministic C-to-OMF-to-MZ plus ASM-to-OMF execution rounds.  This proves
  what local bytes executed, not universal canonicality of the HTTP-only TC4J
  source.
- OMF producer comments and dependency records provide cheap, high-signal
  contamination checks before final linking.  They supplement binary hashes;
  they do not prove semantics or source correctness.
- Borland COMENT `E9` records carry DOS time/date metadata.  Retain the raw OMF
  digest and compare a second digest that normalizes only those four bytes.
  Never normalize LEDATA: ReC98 research probes intentionally compile
  `__DATE__`/`__TIME__` into data, and that is a real build difference.
- Three isolated ReC98 cold builds agree on all 20 selected TH01-TH05 outputs.
  All 416 generated OMF objects validate.  Strict comparison finds three
  raw-exact COM files and rejects all four TH04 candidates.
- Per-game dependency-timestamp-normalized OMF identities are stable across
  all three builds.  The combined Research/Pipeline-inclusive identity is not,
  because those probes retain real source-level build-date strings in LEDATA.
- The pinned known TH01 vector is a regression Oracle for build/comparator
  stability.  It must never be interpreted as three waived exact failures.
- The all-game vector is a fast routing Oracle: it pins every compact numeric
  dimension and candidate byte identity, yet the default command remains a
  strict raw gate.  TH02's 2/17/1-byte MZ differences are good narrow-probe
  controls; TH04 `OP`/`MAINE` require broader ownership/layout work.
- Exact evidence is artifact-scoped unless the Oracle policy explicitly marks
  it global.  A generic clean toolchain replay is valuable calibration but
  cannot satisfy a TH04 unit's own compilation replay or raw-byte gate.

## Current toolchain knowledge

- The Borland DPMI loader fails with `Loader error (0000)` from the deep Wine
  `Z:` repository path.  A project-local prefix and short `C:\TC4` path are
  part of the reproducible environment.
- Turbo C++ 4.02 reads `TURBOC.CFG` for the include/library configuration used
  here.  The plausible `TCC.CFG` filename does not supply `dos.h` and caused a
  failed first cold build.
- TC4J BIN, INCLUDE, LIB, and startup source trees are independent attestation
  surfaces.  Pinning only `TCC.EXE` would miss ABI-affecting headers, startup
  objects, emulation libraries, and linker inputs.
- Detailed acquisition, automatic installation, focused invocation, cold-build
  usage, and recovery instructions are in `docs/TOOLCHAIN.md`.
- Headless analysis uses Ghidra 12.1.3 and Temurin JDK 21.0.12.1+1. Downloads,
  versioned trees, and stable `ghidra`/`jdk` symlinks belong under ignored
  `.tools/`; private databases belong under ignored `ghidra-project/`; only
  generated cache/export/receipt state belongs under `.analysis/ghidra/`.
- Ghidra refuses a project path with the dot-prefixed `.analysis` component.
  This negative result is why `ghidra-project/` is an explicit repository
  safety exception rather than an arbitrary second private-state convention.
- The headless wrapper validates the target and analysis tools on every run.
  A fresh nonce plus an external Python MZ parser prevents a stale Java export
  from passing even if Ghidra reports a script failure with process status 0.
- Ghidra's MZ loader applies relocation words for load segment `0x1000` and
  maps the header into a `HEADER` overlay. Full database bytes, relocation
  records, source mapping, entry point, and samples are attestable; inferred
  block/function topology is not.
- The database Oracle has real-corpus controls for both 0-relocation TH04 OP
  and 625-relocation TH01 OP, plus a 1,136-relocation analyzed TH04 MAIN. The
  loaded-byte, relocation, mapping, and nonce negative mutations all fail.
- Complete headless installation, import, read-only check, calibration, path
  layout, failure recovery, and limitation instructions are in
  `docs/GHIDRA.md`.

## Reference knowledge boundary

ReC98 is strong evidence for PC-98 hardware behavior, target-specific
semantics, compiler patterns, source partition candidates, and the known
toolchain family.  Its names and source are corroboration until checked against
the selected TH04 target.  Its public reverse-engineered/finalized/position-
independent metrics are not per-unit byte-match states.

Upstream work is always quarantined as candidate material.  Even a ReC98 unit
described as finalized or matching must pass local boundary review, an attested
cold rebuild, the full required Oracle vector, and affected-unit replay before
this repository can call it exact.

TH08/TH095/TH105 provide control-plane patterns and examples of strict
promotion, but PE/COFF/MSVC assumptions do not transfer to 16-bit MZ code.

## Negative-result discipline

When a plausible experiment fails:

1. keep bulky raw output below `.analysis/`;
2. record the exact target/tool/input and what observation rejected the idea;
3. add an evidence row with `fail` or `inconclusive`;
4. add a `negative-result` knowledge row only when it rules out a reusable
   search path;
5. state the narrow scope so another artifact, memory model, or TU is not
   incorrectly constrained.

This is the highest-leverage form of agent memory: it prevents future sessions
from repeating source-shape guesses that the target or compiler already
falsified.

## Query recipes

```bash
# Live reconstruction state
python3 scripts/status.py --json

# All durable knowledge (CSV remains deliberately grep-friendly)
column -s, -t < config/knowledge.csv

# Evidence for one knowledge entry
rg 'ev-oracle-smoke-corpus' config/evidence.csv config/knowledge.csv
```

Before handoff, update the index and this document only when the routing map or
entry contract changes.  Detailed target discoveries should live in focused
notes linked from `source_refs`, not in an ever-growing monolith.
