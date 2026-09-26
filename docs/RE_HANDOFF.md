# TH04 reconstruction handoff

Updated 2026-09-26. This is the current resume index. Live counts come from
`config/units.csv`, `config/th04_function_boundaries.csv`,
`config/th04_decoded_function_acceptance.csv`, and `python3 scripts/status.py`.
Use `docs/RE_ROADMAP.md` for work order and `docs/reconstruction/README.md`
for focused evidence. Historical receipt paths and candidate names are not
current acceptance claims.

## Resume checks

```sh
git status --short --branch
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/audit_compat_dependencies.py --check
python3 scripts/boundary_review/validate_function_boundary_ledger.py
```

All four local targets currently pass size, SHA-256, format, and MZ-structure
checks. Their canonicality remains `candidate-local-attested`, not independent
proof of pristine release media. Re-attest an active Ghidra database before new
target observations. Run only one writable Borland/Wine replay at a time.

## Accepted function state

| Artifact | Reviewed authored boundaries | Function exact | Pending / blocked | Tracked decoded source-owner bytes | Accepted decoded bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| OP.EXE | 93 / 93 | 85 | 8 / 0 | 14,284 | 13,847 |
| MAINE.EXE | 72 / 72 | 63 | 9 / 0 | 12,553 | 11,187 |
| ZUN.COM | 11 / 11 | 1 | 8 / 2 | 442 | 38 |

MAIN.EXE has 492 / 495 authored candidate functions exact. Its reviewed
file-backed authored C/C++ extent is 83,442 / 83,469 exact bytes; the remaining
27 bytes belong to `carpet_lighting_put_new` (23), checkerboard drawing (2),
and `snd_load` (2). MAIN is outside the active campaign unless new evidence
changes these provenance/codegen blockers.

OP, MAINE, and ZUN counts refer to decoded function owners. No honest packed
file authored-source denominator or whole-artifact exact claim exists for
these DIET MZ containers. The separate original-ASM attestation queue has 108
observations and is not part of the authored C/C++ denominator.

The current canonical cold-aggregate receipts are:

| Artifact | Receipt under `.analysis/reconstruction/receipt-archive/` | SHA-256 | Verdict |
| --- | --- | --- | --- |
| OP | `v755-op-zunsoft-natural-canonical-receipt.json` | `14a85e9330db6b1728bf7264ab5e8eebf608deb54a5d9dc427d6c17fd2a146f2` | 85/85 decoded-exact slices raw-zero |
| MAINE | `v727-maine-staff-dissolves-canonical-receipt.json` | `d86732f3c46baf5c8b9fe79d65abf4476cdd870353c1de96483bc48b5a632287` | 63/63 decoded-exact slices raw-zero |
| ZUN | `v776-zun-memchk-canonical-receipt.json` | `809e567a3b1822b9865522e9d8e89e3f016d62036f29c339c073bdafd83dd1b7` | MEMCHK `_main` raw-zero; two resident C++ rows remain diagnostic |

A receipt for one decoded slice cannot confer exactness on a packed file,
another function, or a complete standalone product build.

## Active ZUN work

The natural Tiny-model MEMCHK `_main` at COM payload `0x26A7` is the first exact
ZUN authored function (38 bytes). Its complete 4,066-byte MEMCHK component
cold-links raw-identically with maintained shared `DOS_PUTS2` and
`DOS_MAXFREE`. Those helpers are library support, excluded from authored
function credit. The evidence and source-owner decision are in
`docs/reconstruction/zun/TH04_ZUN_MEMCHK_NATURAL_EXACT_V773.md`.

Eight reviewed ZUNINIT entries still lack accepted source/origin authority.
Historical IDA-generated assembly is a candidate, not original-source proof.
Resident `cfg_init` at payload `0xDCF` and resident `_main` at `0xE67` remain
blocked: natural `_main` is six bytes short; `cfg_init` retains linked fixup
differences downstream of that layout shift. Prior compiler and barrier
negatives are in the ZUN focused notes and `config/knowledge.csv`. Continue
source/component ownership review before exact promotion.

## OP and MAINE strict frontiers

All current authored OP and MAINE physical boundaries are reviewed. OP's eight
nonexact entries are at decoded payload `0xBFA7`, `0xC57A`, `0xC627`,
`0xDDCA`, `0xE2F2`, `0xE32C`, `0xE378`, and `0xE3E8`. MAINE's nine are at
`0xA2D6`, `0xA78F`, `0xC149`, `0xC1A1`, `0xC814`, `0xCBB0`, `0xD112`,
`0xD5A0`, and `0xD5DA`. Names and exact blocker details are in the boundary
ledger and the focused strict-frontier notes:

- `docs/reconstruction/op-maine/TH04_OP_STRICT_FRONTIER_V766.md`;
- `docs/reconstruction/op-maine/TH04_MAINE_STRICT_FRONTIER_V732.md`.

Do not retry equivalent C++ spellings or promote target-derived inline ASM,
pseudo-register forcing, or inert optimizer barriers without materially new
compiler or source-provenance evidence. Any shared header, flag, layout, or
link-order change requires cold replay of every affected accepted owner.

## Private inputs and finish checks

Preserve `.analysis/targets/`, `.analysis/toolchain/`, `.analysis/ghidra/`,
`.analysis/runtime/images/zun.hdi`, retained v401/v402/v489 source snapshots,
DIET replay inputs, and the configured v546 ZUN runtime inventory. Historical
`.analysis/reconstruction/probes/` paths in evidence rows are replay provenance,
not retention promises; `scripts/prune_analysis.py` supports dry-run cleanup.

```sh
python3 scripts/status.py
python3 scripts/preflight.py
python3 scripts/boundary_review/report_function_boundaries.py --check
python3 scripts/progress.py --check
python3 scripts/ci.py
git diff --check
git status --short
```
