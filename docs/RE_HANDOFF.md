# TH04 reconstruction handoff

Updated 2026-09-21. This file contains only live state and the next work queue.
Use focused reconstruction notes and the CSV ledgers for experiment history.

## Resume here

Read `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/RE_WORKFLOW.md`, and the relevant
TH04 skill. Then run:

```bash
git status --short --branch
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/audit_compat_dependencies.py --check
```

## Current verified state

- Target canonicality is `candidate-local-attested`. MAIN.EXE is 156,258 bytes,
  SHA-256 `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
- MAIN has **83,375 / 83,469 reviewed authored C/C++ bytes exact** and
  **492 / 494 reviewed authored C/C++ functions exact**.
- The accepted MAIN byte gap is **27 bytes** only: checkerboard `LOOP` (2),
  Stage 4 carpet low-level residuals (23), and `snd_load` `MOV BX,AX` (2).
- Latest accepted complete MAIN aggregate is
  `gpt-web-v410-carpet-frame-aggregate-final-001`, receipt SHA-256
  `d1c5af30fe7419391e48b60156b87b8d4ccb5202ca7e7ca216f18e1c877c2487`.
- The v421 carpet hybrid is **quarantined**. It proves that TC4J integrated
  assembly can reproduce the 23 residual bytes and link the whole function
  exactly, but it lacks independent historical source provenance. v409/v410
  natural-source ownership remains authoritative: 67 exact + 23 blocked.
- Checkerboard is similarly reduced to one two-byte `E2 F7` blocked owner.
  Natural source/optimizer/IDE/cross-artifact/semantic-lineage searches do not
  justify target-derived inline assembly.
- `snd_load` is reduced to target `89 C3` versus natural TC4J `8B D8`. TH02,
  TH03, and TH05 homologs use `8B D8`; integrated assembly explains the TH04
  encoding mechanism but does not prove original inline-ASM provenance.
- The compiler/provenance searches through v424 and the supplied-HDI forensic
  searches are closed negative. Do not repeat them without a materially new
  evidence source.
- OP/MAINE diagnostic payload candidates now differ only at shared `snd_load`
  (2 bytes each) after the master/object and OP-music topology work.
- **Important v425/v427 correction:** their relocation-order reference is the
  v231 **restored-candidate inverse control**, not the DIET-restored target and
  not a historical pre-DIET MZ. OP's 804/804 ordering and MAINE's two-entry
  residual are candidate-to-candidate topology diagnostics only. Do not use
  that ordering as a target acceptance Oracle.
- MAIN has no provisional authored C/C++ boundaries. `compat/rec98` has zero
  forwarders and zero product include sites.

## Ordered work queue

1. **MAIN final 27 bytes:** continue only with genuinely new independent source
   provenance or a new legal compiler mechanism. Do not reopen already-closed
   optimizer, register-form, HDI-remnant, or cross-game scans by default.
2. **OP/MAINE packed closure:** continue from the current physical object
   topology, but treat v231 candidate-inverse relocation order as diagnostic
   only. Historical pre-DIET relocation order remains unobserved.
3. **Standalone build/runtime:** after source/link closure can produce the
   artifacts under test, add deterministic DOSBox-X runtime scenarios.

## Private evidence retention

Expanded cold-build trees are disposable once their receipt SHA-256 and checked-
in evidence rows are durable. Keep targets, toolchains, runtime image, Ghidra
database, boundary-review inputs, `receipt-archive/`, and the current DIET v218/
v228/v231 observations.

For current OP/MAINE replay dependencies, keep only these source snapshots:

- `.analysis/gpt-web/v401-master-vs-object-replay-001/a/source`
- `.analysis/gpt-web/v402-opmusic-hybrid-replay-001/a/source`

Keep receipt-only directories for current blocker/frontier evidence, especially
v391, v396, v398-v406, v411-v420, v423-v427. Superseded scratch matrices,
second A/B source copies, and expanded exact-unit replay trees can be deleted
and regenerated from checked-in source.

## Finish every packet

Run focused A/B replay and the complete affected aggregate before exact
promotion, then:

```bash
python3 scripts/preflight.py
python3 scripts/ci.py
git diff --check
```

Record artifact, segment:offset, evidence class, replay/receipt, result, and
remaining unknowns in the focused note and ledgers. Never commit original
executables, game assets, disk images, compiler installations, or private
analysis output.
