# TH04 reconstruction handoff

Updated 2026-09-26 after repository cleanup. Reconstruction is paused at the
v816 ZUN resident-source negative. This is the current resume index; use
`python3 scripts/status.py`, `config/units.csv`, and the function-boundary and
decoded-acceptance ledgers for live counts. `docs/RE_ROADMAP.md` gives the next
work order; `docs/reconstruction/README.md` routes focused evidence. Versioned
notes and historical receipt paths are snapshots, not current acceptance.

## Resume checks

```sh
git status --short --branch
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/audit_compat_dependencies.py --check
python3 scripts/boundary_review/validate_function_boundary_ledger.py
```

The four local targets pass size, SHA-256, format, and MZ-structure checks.
Their provenance is still `candidate-local-attested`, not proof of pristine
release media. Re-attest the active Ghidra database before new target
observations. Run only one writable Borland/Wine replay at a time, with builds
constrained to CPUs 0-1.

## Accepted state and remaining blockers

| Artifact | Reviewed authored boundaries | Exact authored functions | Blocked | Original-ASM observations |
| --- | ---: | ---: | ---: | ---: |
| OP.EXE | 93 / 93 | 85 | 8 | 16 reviewed |
| MAIN.EXE | 495 / 495 | 492 | 3 | 73 attestation entries; 6 provisional |
| MAINE.EXE | 72 / 72 | 63 | 9 | 15 reviewed |
| ZUN.COM | 3 / 3 | 1 | 2 | 12 reviewed |

MAIN's reviewed file-backed authored extent has 83,442 / 83,469 exact bytes.
Its 27-byte remainder belongs to `carpet_lighting_put_new` (23), checkerboard
(2), and `snd_load` (2). OP has 13,847 accepted decoded source-owner bytes of
14,284 tracked; MAINE has 11,187 / 12,553; ZUN has 38 / 442. These decoded
counts do not give a packed-file byte denominator or whole-artifact exactness.
Original-ASM observations are outside the authored C/C++ counts.

OP's eight blocked functions and MAINE's nine blocked functions have reviewed
physical boundaries. Current natural-source/compiler probes do not close their
byte or admissibility gaps. The exact names, decoded payload offsets, and
negative probes are in the [OP strict frontier](reconstruction/op-maine/TH04_OP_STRICT_FRONTIER_V766.md)
and [MAINE strict frontier](reconstruction/op-maine/TH04_MAINE_STRICT_FRONTIER_V732.md).
Do not substitute target-derived inline ASM, explicit register forcing, or
inert optimizer barriers without independent provenance. All 16 OP and 15
MAINE original-ASM function-like entries now have reviewed boundaries and
source-backed raw-identical modules; the prior MAINE provisional-cut statement
is superseded by v815.

| Shared/original-style ASM source | OP load segment:offset | MAINE load segment:offset | Focused evidence |
| --- | --- | --- | --- |
| `CDG_LOAD`, `0x164` | `0DA1:0B6A` | `0CC7:0B08` | [v797 and v815](reconstruction/op-maine/TH04_SHARED_CDG_LOAD_V797.md) |
| `CDG_PUT_8`, `0x9E` | `0DA1:05FE` | `0CC7:06E6` | [v799](reconstruction/op-maine/TH04_SHARED_CDG_PUT_V799.md) |
| `INPUT_S`, `0x10A` | `0DA1:07CC` | `0CC7:081A` | [v802](reconstruction/op-maine/TH04_SHARED_INPUT_V802.md) |
| `BGIMAGE_PUT_RECT_16`, `0x82` | `0DA1:0AE8` | `0CC7:0A86` | [v805](reconstruction/op-maine/TH04_SHARED_BGIMAGER_V805.md) |
| `_hflip_lut_generate`, `0x1E` | `0DA1:0134` | `0CC7:01EC` | [v808 and v812](reconstruction/op-maine/TH04_OP_HFLIP_LUT_V808.md) |
| `GRAPH_PUTSA_FX`, `0x15A` code + `0x40` data | `0DA1:04A4`, data `0F34:0A00` | `0CC7:058C` | [v809 and v813](reconstruction/op-maine/TH04_OP_GRAPH_PUTSA_FX_V809.md) |

OP also has its local `CDG_PUT_NOCOLORS_8` (`0DA1:0282`, 0x52-byte module)
and shared `CDG_PUT_NOALPHA_8` (`0DA1:0766`, 0x66-byte module). MAINE has local
`CDG_PUT_PLANE` (`0CC7:0408`, 0x9A-byte module). Their [v806](reconstruction/op-maine/TH04_OP_CDG_NOCOLORS_V806.md),
[v807](reconstruction/op-maine/TH04_OP_CDG_NOALPHA_V807.md), and
[v814](reconstruction/op-maine/TH04_MAINE_CDG_PLANE_V814.md) focused A/B links
match complete decoded module bytes and ordered relocations. All OP/MAINE
packed-file offsets remain unknown. The shared CDG and input modules also
passed focused MAIN cold replay; source placement and include composition are
replay inputs, so changes require affected-unit cold replay.

ZUN's natural Tiny-model MEMCHK `_main` at COM payload `0x26A7` is its one exact
authored function (38 bytes). Its complete 4,066-byte component cold-links
raw-identically with maintained `DOS_PUTS2` and `DOS_MAXFREE`; those helpers are
library support, not authored-function credit. See the [MEMCHK note](reconstruction/zun/TH04_ZUN_MEMCHK_NATURAL_EXACT_V773.md).

Maintained symbolic original-style ASM cold-links the 1,141-byte ZUNINIT
component at decoded `0x6F3..0xB67`, 223-byte launcher selector, 8-byte mover,
68-byte outer stub, and 926-byte ONGCHK component. The source-driven composite
replay rebuilds these groups and reproduces the 13,422-byte decoded flat
payload. It still uses an external usage asset and a resident ReC98 candidate
with inert barriers, so this is a diagnostic flat comparison, not complete
source acceptance. Earlier mixed flats repacked with pinned DIET 1.45f to a
byte-identical 7,754-byte MZ target; that does not make the product source
exact. See [ZUNINIT](reconstruction/zun/TH04_ZUNINIT_SYMBOLIC_COMPONENT_V785.md)
and the [composite note](reconstruction/zun/TH04_ZUN_MIXED_COMPOSITE_V788.md).

Resident `cfg_init` at COM payload `0xDCF` and `_main` at `0xE67` remain blocked.
Natural `_main` is six bytes short of the target print-call shape; `cfg_init`
retains linked fixup differences downstream. The v816 genuine-inline-helper
probe also failed; see [ZUN resident notes](reconstruction/zun/TH04_ZUN_MAIN_V241.md).
A new source-origin observation or compiler mechanism is needed before retry.

## Private inputs and cleanup

The canonical cold aggregate receipts in
`.analysis/reconstruction/receipt-archive/` remain verified:

| Artifact | Receipt | SHA-256 |
| --- | --- | --- |
| OP | `v755-op-zunsoft-natural-canonical-receipt.json` | `14a85e9330db6b1728bf7264ab5e8eebf608deb54a5d9dc427d6c17fd2a146f2` |
| MAINE | `v727-maine-staff-dissolves-canonical-receipt.json` | `d86732f3c46baf5c8b9fe79d65abf4476cdd870353c1de96483bc48b5a632287` |
| ZUN | `v776-zun-memchk-canonical-receipt.json` | `809e567a3b1822b9865522e9d8e89e3f016d62036f29c339c073bdafd83dd1b7` |

Preserve `.analysis/targets/`, `.analysis/toolchain/`, `.analysis/ghidra/`,
`.analysis/runtime/images/zun.hdi`, the v401/v402/v489 source snapshots,
DIET replay inputs, and the configured v546 ZUN runtime inventory. Expanded
focused probes and exact-unit build worktrees were archived as top-level
results/receipts in `focused-probe-heads-v817-20260926.tar.zst`, with an
adjacent per-file SHA-256 manifest, then pruned. Historical paths into those
worktrees are provenance, not live input promises. Use
`scripts/prune_analysis.py` in dry-run mode before future cleanup.

Finish future changes with the focused comparison, `python3 scripts/ci.py`,
`git diff --check`, and an updated handoff when phase or blockers change.
