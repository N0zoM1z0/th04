# TH04 current handoff

Updated 2026-10-02. The active goal is a standalone PC-98 game build:
checked-in TH04 source, successful builds, and normal gameplay. Whole-build
byte equality is not required. The two remaining MAIN function exactness
cases are intentionally deferred and retain their nonexact ledger states.
ReC98 public implementations may be adapted into the owning TH04 subsystem;
no upstream exactness claim is inherited.

## Current state

| Artifact | Accepted authored functions | Native build/runtime |
| --- | ---: | --- |
| OP | 93/93 | TH04-only link; OP-to-MAIN handoff observed with an entry shim |
| MAIN | 493/495 | Diagnostic link; removing master.lib and debugging gameplay |
| MAINE | 72/72 | TH04-only link and static ABI checks; ending entry unverified |
| ZUN | 3/3 | Source-only packed build; normal launcher reaches original demo |

These function counts describe the historical reconstruction acceptance plane,
not whole executable or native runtime completion. Live counts:
`python3 scripts/status.py`. Targets remain `candidate-local-attested`.

The last committed MAIN diagnostic, v1136, links 193 C/C++ roots, 130 ASM
roots, eight state owners and four generated sprite owners. It still uses
`masters.lib`. Local v1143 stage-0 instrumentation records EMS completion,
resource conversion completion and entry into the gameplay loop, ending at
`player_render()` with no after-call marker. Its screen has HUD/STOP text but
no normal playfield. The instrumented overlay changes layout and is diagnostic.

Current scratch receipts:
- `.analysis/reconstruction/probes/native-main-link-v1143-stage0-20260930/receipt.json`
- `.analysis/runtime/candidates/native-main-v1143-stage0-20260930/run-60s/receipt.json`

## Build and validation

Only one Borland/Wine build may run at a time. Use new private output paths.

```sh
python3 scripts/preflight.py
python3 scripts/probes/probe_th04_native_main_link.py --without-support \
  --output-dir .analysis/reconstruction/probes/NEW-main
python3 scripts/probes/probe_th04_native_op_link.py --without-support \
  --output-dir .analysis/reconstruction/probes/NEW-op
python3 scripts/probes/probe_th04_native_maine_link.py --without-support \
  --output-dir .analysis/reconstruction/probes/NEW-maine
python3 scripts/probes/probe_th04_native_zun_composite.py \
  --output-dir .analysis/reconstruction/probes/NEW-zun
python3 scripts/ci.py
git diff --check
```

MAIN runtime preparation uses `prepare_th04_main_diagnostic_hdi.py`; execution
uses `run_th04_maine_diagnostic_hdi.py`. Always replace files in disposable
images. Preserve original executables, pinned data and active tools/databases.

## Next work

1. Close MAIN's source-only link and validate its near/far call edges.
2. Run MAIN normally: rendering, movement, shots, stages, sound and exit.
3. Run all four rebuilt artifacts together, including MAINE and score/config
   persistence. Test actual input and state progression, not one screenshot.
4. Provide a straightforward product build entrypoint with local source inputs.

## Navigation

- [Architecture](ARCHITECTURE.md): artifact/ABI and source ownership.
- [Runtime](RUNTIME.md): pinned emulator and image setup.
- [Progress](PROGRESS.md): generated historical function acceptance.
- [Evidence index](reconstruction/README.md): focused historical investigations.
- `config/evidence.csv` / `config/knowledge.csv`: durable receipts and findings.

Historical checkpoints remain in Git and the evidence ledgers. Do not use an
old note's missing-header count or blocker as a current work queue. The product
include audit currently has zero compatibility forwarders and forbidden edges.
