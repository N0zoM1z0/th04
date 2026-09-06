# 東方幻想郷 ～ Lotus Land Story

This repository is an agent-first reconstruction of the original Japanese
PC-98 release of **Touhou 4: Lotus Land Story (TH04)**.  The immediate goal is a
reproducible, evidence-backed source reconstruction of `OP.EXE`, `MAIN.EXE`,
`MAINE.EXE`, and `ZUN.COM`.  Original executables and game data are supplied
locally by the owner and are never committed.

The framework deliberately does not copy ReC98's workflow.  ReC98 is an
important source of PC-98, Borland, and game-specific knowledge; N0zoM1z0's
TH08/TH095/TH105 repositories are useful control-plane references.  This
project combines those lessons with stricter machine-readable evidence and a
multi-dimensional Oracle stack designed for short, resumable agent sessions.
Nothing from an upstream reconstruction is accepted on reputation: imported
source must pass this repository's own target, build, layout, relocation, raw-
byte, and replay gates.

## Exact targets

Supply your own legal copy.  The importer selects the Japanese `zun.hdi` and
requires these artifacts:

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| `OP.EXE` | 42,290 | `8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f` |
| `MAIN.EXE` | 156,258 | `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b` |
| `MAINE.EXE` | 38,035 | `670de6ba907a2edbc1592de810acd92e5b89541d3dc35b70210171166d1713f8` |
| `ZUN.COM` | 7,754 | `0a12e9a489d3b704a77cf04ca3062ee48f298a9df6d237dc7dad46986e2d116e` |

These hashes currently have `candidate-local-attested` provenance: they
identify the supplied Japanese image exactly, while independent pristine-dump
confirmation remains open.  That qualification is kept separate from whether
a candidate build exactly matches the pinned bytes.

## Quick start

```bash
python3 scripts/check_environment.py
python3 scripts/import_targets.py \
  /path/to/your/legal-copy.rar \
  --include-all-games-smoke
python3 scripts/preflight.py
python3 scripts/smoke_oracles.py
```

The imported files live below `.analysis/targets/`.  They are ignored by Git.
The checked-in target manifest pins their expected size and digest.  A private
receipt additionally records the source archive and disk geometry.

For a candidate build:

```bash
python3 scripts/compare_artifacts.py \
  .analysis/targets/th04/main.exe build/th04/main.exe --json

# Export private relocation/address facts for an analysis backend.
python3 scripts/export_analysis_bundle.py th04-main --load-segment 0x2000

# Mine cross-game navigation candidates (never exact evidence).
python3 scripts/mine_shared_blocks.py th04-main th05-main-smoke
```

Exit status is zero only for raw byte identity.  Structural or
relocation-normalized similarities are diagnostic evidence, never a substitute
for exact acceptance.

## Project map

- `AGENTS.md` — mandatory target, evidence, safety, and session rules.
- `config/targets.toml` — legally supplied target identity and provenance.
- `config/oracles.toml` — Oracle definitions and exact-acceptance policy.
- `config/units.csv` — bounded code/data ownership and reconstruction state.
- `config/evidence.csv` — replayable observations, commands, and digests.
- `config/hypotheses.csv` — falsifiable claims and their current disposition.
- `docs/ARCHITECTURE.md` — PC-98-specific architecture and address model.
- `docs/ORACLES.md` — independent Oracle stack and acceptance matrix.
- `docs/RE_WORKFLOW.md` — bounded agent loop.
- `docs/REFERENCE_ANALYSIS.md` — findings from TH08/TH095/TH105 and ReC98.
- `docs/KNOWLEDGE_BASE.md` — scoped durable facts, hazards, and negative results.
- `.agents/skills/` — task routers for RE, Oracle work, matching, and runtime.
- `scripts/` — target import, verification, comparison, status, and CI tools.

## Status

The control plane and target-ingestion layer are bootstrapped.  No authored
TH04 function is claimed as reconstructed or exact yet.  Run:

```bash
python3 scripts/status.py
```

to derive live status from the ledgers.  Prose never overrides those records.

## Credits and provenance

Deep thanks to [ReC98](https://github.com/nmlgc/rec98) for its extensive PC-98
Touhou research and to [mzdiff](https://github.com/nmlgc/mzdiff) for its MZ-
aware comparison model.  [98imgtools](https://github.com/tsdko/98imgtools)
helped corroborate the Anex86 HDI geometry, and the existing
[TH08](https://github.com/N0zoM1z0/th08),
[TH095](https://github.com/N0zoM1z0/th095), and
[TH105](https://github.com/N0zoM1z0/th105) reconstructions informed the agent
control plane.  Their results are references and candidates, not automatically
trusted TH04 evidence.  Inspected revisions are pinned in
`docs/REFERENCE_ANALYSIS.md`; reference repositories and game files are not
redistributed here.

## License

Repository-authored code and documentation are provided under the MIT License.
This does not grant rights to the original game, its assets, or referenced
third-party work.
