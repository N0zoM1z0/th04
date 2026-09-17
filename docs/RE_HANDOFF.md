# TH04 reconstruction handoff

Updated 2026-09-17. This is a current-state index. Historical experiments
belong in the ledgers and focused notes, not here. Before target-dependent work,
read [AGENTS.md](../AGENTS.md), [architecture](ARCHITECTURE.md),
[workflow](RE_WORKFLOW.md), and the relevant local skill; inspect git status and
run python3 scripts/preflight.py. Use LeanToken for repository archaeology and
python3 scripts/status.py for live counts.

The user goal is approximately 99% exact authored reconstruction across TH04,
a standalone compile/rebuild from checked-in source, and playable DOSBox-X
execution. Exact unit and artifact claims still use the strict zero-difference
gate below; no rounded percentage can replace it.

## Target and acceptance

The pinned Japanese MAIN.EXE is 156,258 bytes, SHA-256
077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b.
The pinned OP.EXE, MAINE.EXE, and ZUN.COM are DIET-packed MZ files. All used
targets pass manifest size/SHA-256, format, and MZ checks; canonicality remains
**candidate-local-attested**, not a proven pristine retail dump. Re-run
python3 scripts/ghidra.py th04-main check for MAIN database attestation.

Exact acceptance needs the complete source-owned extent to pass two cold
builds, raw zero-difference bytes, MAP/segment ownership, ordered MZ
relocations, valid OMF, ledger checks, and cold aggregate replay. Target
unpacked payload equality is a diagnostic for packed artifacts, not
packed-file equality. Do not synthesize equality with target-derived bytes,
inert padding, ABI changes, or false assembly ownership.

## Current state

MAIN has **462/485 reviewed authored C/C++ functions** and
**75,665/81,324 reviewed authored C/C++ bytes** exact; 39 accepted
original-style ASM units add 5,525 bytes. The last complete native aggregate,
gptweb-v212-randring2-and-aggregate-final-001, passes all 248 default
exact MAIN owners twice (receipt SHA-256
dd5e63fbc838f722643b55744c7e319d60d23cb38ae7d5f326ddf2843b77a38b).
All 51 boss-named MAIN authored candidates are exact. None of these counts
means whole MAIN.EXE or whole TH04 is exact.

| MAIN physical owner | Target extent | Current blocker |
| --- | --- | --- |
| Dialog | DIALOG_TEXT load 0xCF3D..0xD728, 0x7EC bytes | Raw bytes/MAP/sites match, ordered relocs fail. Target has three descending MZ runs; current dialog.obj has two LEDATA/FIXUPP groups and two runs. Target OMF unknown. [Evidence](reconstruction/TH04_MAIN_DIALOG_BOUNDARY_V180.md) |
| Stage session | DEMO_TEXT load 0xAED0..0xB3ED, 0x51E bytes | Raw bytes/MAP/sites match; target orders site 0xB2DA first, candidate FIXUPP/MZ last. [Evidence](reconstruction/TH04_DEMO_FIXUP_ORDER_V214.md) |
| Item update | MAIN_035_TEXT load 0x1DA1B..0x1DF60, 0x546 bytes | Two compiler SUB encodings, four differing bytes. [Evidence](reconstruction/TH04_MAIN035_ITEMS_V154.md) |
| Thick laser update | B4M_UPDATE_TEXT load 0x15D74..0x15ECD, 0x15A bytes | Eight-byte template-copy setup-order difference. [Evidence](reconstruction/TH04_MAIN_THICKLASER_UPDATE_V181.md) |
| Gameplay init/loop | DEMO_TEXT load 0xAD03..0xAECF / 0xAB88..0xAD02 | Init misses one metadata byte; loop differs in code shape. [Evidence](reconstruction/TH04_DEMO_INTERNAL_BOUNDARIES_V165.md) |

The [target-stub payload comparison](reconstruction/TH04_PACKED_PAYLOAD_FRONTIER_V218.md)
leaves OP 7 bytes, MAINE 5 bytes, and ZUN 0/13,422 bytes different from two
cold ReC98-overlay candidates. [DIET 1.45f replay](reconstruction/TH04_DIET145F_ROUNDTRIP_V228.md)
round-trips isolated target copies raw exact with `-B -G` for OP/MAINE
and `-B` for ZUN. Candidate ZUN also packs raw equal; candidate
OP/MAINE remain 42,251/42,290 and 37,985/38,035 bytes. This is packer
calibration, not authored-source acceptance.

The [v231 partition](reconstruction/TH04_DIET145F_MZ_PARTITION_V231.md)
localizes OP/MAINE input MZ differences to payload bytes, ordered relocation
tables, and coupled length/allocation/trailing-zero topology. The
[v232 MAP projection](reconstruction/TH04_DIET_RELOCATION_OWNERS_V232.md)
shows candidate master ASM relocation groups interleaved in the
target-restored order. A [v234 compiler probe](reconstruction/TH04_BGIMAGE_B_MODE_V234.md)
finds that TCC-generated ASM plus pinned TASM preserves all BGIMAGE CODE bytes
and gives its eight OP/MAINE relocations the target-restored order; packed
files still differ. The upstream source uses inline ASM and `codestring`,
so no exact/source credit follows. The historical pre-DIET target MZ and OMF
remain unknown; OP/MAINE/ZUN have no accepted artifact-local exact cohort.
[v247](reconstruction/TH04_BGIMAGE_NATURAL_V247.md) adds TH04-owned BGIMAGE
source for three reviewed functions in each of OP and MAINE. Two isolated
TC4J builds agree, but natural CODE is 269 bytes versus the 208-byte target
producer, so all six units remain source-present.
[v250](reconstruction/TH04_BGIMAGE_HMEM_V250.md) moves BGIMAGE's two HMem
ABI declarations into TH04 shared source; a product-only TU compiles with the
same CODE and extern names as both overlay builds, with no exact promotion.
ZUN `cfg_init` now has [target-reviewed maintained source](reconstruction/TH04_ZUN_CFG_INIT_V239.md):
two isolated overlay rebuilds and DIET packs are raw equal, with no exact
credit while the remaining composite inputs and standalone build are unresolved.
ZUN [`_main`](reconstruction/TH04_ZUN_MAIN_V241.md) also has reviewed maintained
source. Its natural TC4J CODE is 246 versus 252 target bytes: the compiler
merges two error-print calls without the inert ReC98 statements. The A/B
diagnostic builds are deterministic; the unit remains source-present.

The current product still uses compat/rec98 forwarding headers and a pinned
ReC98 overlay for replay. Standalone checked-in TH04 build closure, full
packed-file matching, runtime scenarios, and independent provenance remain
open. Track exact owners and the remaining 13 unreviewed MAIN functions from
config/units.csv, config/th04_main_authored_functions.csv,
config/th04_function_boundaries.csv, and python3 scripts/status.py.

## Next work and finish gate

Investigate a natural compiler/OMF producer that predicts the dialog or DEMO
FIXUPP order while retaining matching raw bytes and MAP. Continue the large
gameplay-loop, item, and laser owners when that producer remains unresolved. For OP/MAINE,
review the SND_LOAD and OP music physical owners against the unpacked target,
migrate source into src/op, src/maine, or proved src/shared. Reconstruct
ZUN component source independently: its equal candidate composite contains
IDA-derived assembly and an external ONGCHK binary, so payload equality gives
no authored-source credit for those components. Continue after the recovered
`cfg_init` and `_main` sources with natural `_main` call placement, ZUNINIT,
MEMCHK, and ONGCHK ownership. Resolve the natural OP/MAINE payload bytes and
linker/packer input topology identified by the v231 partition. Use the pinned
DIET replay after checked-in source and input topology are recovered;
OP/MAINE candidates have no raw packed equality yet.

The [v236–v237 MAIN `-B` probe](reconstruction/TH04_MAIN_B_MODE_V237.md)
fails the raw CODE extent for both dialog and stage session; the original
target OMF producer remains unknown.
The [v238 DEMO compiler probe](reconstruction/TH04_DEMO_INTERNAL_BOUNDARIES_V165.md)
also rejects simple odd-offset switch-table padding and two stage-frame
codegen hypotheses without changing exact counts.
A [v245 dialog OMF control](reconstruction/TH04_MAIN_DIALOG_BOUNDARY_V180.md)
shows that same-segment and empty-bounce `#pragma codeseg` switches preserve
CODE and both FIXUPP groups at a comparable size; they do not explain the
target's third relocation run.
[v248 gameplay-loop control](reconstruction/TH04_DEMO_GAMEPLAY_TERNARY_V248.md)
reproduces its 25-byte play-performance interval branch with a natural
conditional expression, but complete CODE is 372 versus 379 target bytes.

For any promotion, run focused two-cold comparison and a complete cold
aggregate of affected accepted owners. Finish each bounded packet with
python3 scripts/preflight.py, python3 scripts/ci.py, and git diff --check;
record artifact, segment:offset, evidence class, command/receipt, exact result,
and unknowns in the focused note and ledgers.

## Private workspace

Targets, toolchains, Ghidra/IDA projects, generated builds, and receipts stay
ignored under .analysis/ or ghidra-project/. Historical unreferenced worktrees
were pruned (489,112,433 logical bytes; receipt
.analysis/prune-v214-unreferenced-worktrees.json). Retain current v212/v213/v214
replay inputs until superseded. v221 archived 34 unreferenced gpt-web probe
directories (118,316,081 bytes to 7,045,790 bytes) with a verified
.analysis/prune-v221-unreferenced-gpt-web-receipt.json and recoverable
.analysis/prune-v221-unreferenced-gpt-web.tar.zst. Never commit original
executables or assets.
