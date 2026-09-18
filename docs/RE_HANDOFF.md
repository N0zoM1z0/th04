# TH04 reconstruction handoff

Updated 2026-09-19. This is a current-state index. Historical experiments
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

MAIN has **462/487 reviewed authored C/C++ functions** and
**75,665/83,441 reviewed authored C/C++ bytes** exact; 40 accepted
original-style ASM units add 5,615 bytes. The last complete native aggregate,
gpt-5-6-sol-v326-gather-aggregate-final-001, passes all 249 default exact
MAIN owners twice (receipt SHA-256
371425f1e165a56ea88dd35f3b4db9ae6b4bcefce786eee059fd13101af42421).
All 51 boss-named MAIN authored candidates are exact. None of these counts
means whole MAIN.EXE or whole TH04 is exact.

| MAIN physical owner | Target extent | Current blocker |
| --- | --- | --- |
| Enemy script VM and helpers | B4M_UPDATE_TEXT load 0x1554F..0x15C6C, 0x71E bytes | The [three helpers](reconstruction/TH04_MAIN_ENEMY_HELPERS_V328.md) and [full VM](reconstruction/TH04_MAIN_ENEMY_SCRIPT_NATURAL_V330.md) have natural C++ (134/142 and 1,627/1,680 target bytes). The VM's 42-byte entry shape and all 144 switch-case destination groups agree after address masking; raw bytes and three ordered relocations remain open. |
| Dialog | DIALOG_TEXT load 0xCF3D..0xD728, 0x7EC bytes | Raw bytes/MAP/sites match, ordered relocs fail. Target has three descending MZ runs; current dialog.obj has two LEDATA/FIXUPP groups and two runs. Target OMF unknown. [Evidence](reconstruction/TH04_MAIN_DIALOG_BOUNDARY_V180.md) |
| Stage session | DEMO_TEXT load 0xAED0..0xB3ED, 0x51E bytes | Raw bytes/MAP/sites match; ordered relocations fail. A synthetic split and [simple object reordering](reconstruction/TH04_DEMO_LINK_ORDER_V291.md) fail the global byte/layout/relocation gates. |
| Item update | MAIN_035_TEXT load 0x1DA1B..0x1DF60, 0x546 bytes | Two compiler SUB encodings, four differing bytes. [Evidence](reconstruction/TH04_MAIN035_ITEMS_V154.md) |
| Thick laser update | B4M_UPDATE_TEXT load 0x15D74..0x15ECD, 0x15A bytes | Eight-byte template-copy setup-order difference. [Evidence](reconstruction/TH04_MAIN_THICKLASER_UPDATE_V181.md) |
| Gameplay init/loop | DEMO_TEXT load 0xAD03..0xAECF / 0xAB88..0xAD02 | Init misses one metadata byte; maintained loop compiles to 373/379 bytes. A [compiler probe](reconstruction/TH04_DEMO_GAMEPLAY_TERNARY_V248.md) produces both target `EB 00` jumps from void conditional expressions, but their no-op arms lack source provenance; the dead DX copy remains open. |

The [decoded-payload comparison](reconstruction/TH04_PACKED_PAYLOAD_FRONTIER_V218.md)
leaves 7 OP bytes, 5 MAINE bytes, and 0 ZUN bytes different from the cold
ReC98-overlay candidates. The [DIET replay](reconstruction/TH04_DIET145F_ROUNDTRIP_V228.md)
round-trips the target copies and packs candidate ZUN raw equal, but OP/MAINE
packed outputs still differ. Their [MZ partition](reconstruction/TH04_DIET145F_MZ_PARTITION_V231.md)
and [relocation projection](reconstruction/TH04_DIET_RELOCATION_OWNERS_V232.md)
identify payload, ordered-relocation, and header/tail differences; the original
pre-DIET MZ/OMF remain unknown. No OP/MAINE/ZUN artifact-local exact cohort is
accepted.

[BGIMAGE v247/v250](reconstruction/TH04_BGIMAGE_HMEM_V250.md) has six reviewed
source-present OP/MAINE functions. Its product-only TU compiles from checked-in
headers, but natural CODE is 269 versus 208 target bytes. ZUN
[`cfg_init`](reconstruction/TH04_ZUN_CFG_INIT_V239.md) and
[`_main`](reconstruction/TH04_ZUN_MAIN_V241.md) have reviewed maintained source;
the first matches in an untrusted composite overlay, while natural `_main` is
246 versus 252 target bytes; [five semantic branch rewrites](reconstruction/TH04_ZUN_MAIN_V241.md)
also fail the size gate. Neither is exact.
Their [resident](reconstruction/TH04_ZUN_RESIDENT_LAYOUT_V309.md) and
[configuration](reconstruction/TH04_ZUN_CFG_LAYOUT_V311.md) declarations are
now TH04-owned and preserve both pinned compiler results; other external
dependencies remain. Both ZUN C++ TUs also [compile from checked-in source
and headers alone](reconstruction/TH04_ZUN_SOURCE_ONLY_V314.md). A
[separate cold link](reconstruction/TH04_ZUN_COMPONENT_LINK_V317.md) produces
a 6360-byte resident component from those two objects plus a pinned external
support library; it differs from the decoded target at 4241 bytes. Full ZUN
source, composite link, and packed product build remain open. A
[local `GRAPH_CLEAR`](reconstruction/TH04_ZUN_GRAPH_CLEAR_V319.md) TASM unit
replaces one support-library member without changing the candidate component;
its linked 36 bytes equal the target decoded extent. The
[local `RESDATA`](reconstruction/TH04_ZUN_RESDATA_V323.md) unit also matches
190 target code and ten target data bytes. Rebuilding the diagnostic library
in its original physical member order preserves the whole candidate component
and MAP. A [local `FILE_READ`](reconstruction/TH04_ZUN_FILE_READ_V325.md)
matches another 180 target code bytes with the same component and MAP. These
support units have no artifact-local exact acceptance.

MAIN [`sub_CCD6` and `sub_B835`](reconstruction/TH04_END_SCROLL_MPN_V195.md)
now have maintained product-only C++ source and reviewed 96- and 199-byte
target extents. TC4J emits 105 and 215 bytes respectively; exactness and
link ownership remain open.

The [gather-point renderer](reconstruction/TH04_MAIN_GATHER_POINT_RENDER_V326.md)
is now a checked-in 90-byte original-style ASM owner at B4M_UPDATE_TEXT
`13A9:1008`, raw/MAP/relocation exact. Its old replay wrapper is retired.
The [VRAM color header](reconstruction/TH04_VRAM_COLORS_LOCAL_V287.md) is now
TH04-owned across 37 source files; cold replay freezes product headers. Other
compat/rec98 forwarders and the pinned ReC98 overlay remain. Standalone
checked-in TH04 build closure, full
packed-file matching, runtime scenarios, and independent provenance remain
open. Track exact owners and the remaining 10 unreviewed MAIN functions from
config/units.csv, config/th04_main_authored_functions.csv,
config/th04_function_boundaries.csv, and python3 scripts/status.py.

## Next work and finish gate

Classify the 53-byte MAIN enemy VM body mismatch without breaking its exact
144-case destination partition; resolve the helper BP-local and ES-save
producers and all three ordered relocations. Find a natural OMF producer for
MAIN dialog/DEMO ordered relocations without
changing raw bytes or MAP; [current controls](reconstruction/TH04_MAIN_FIXUP_CODEGEN_PROBES.md)
rule out common switches and the simple pause split. Continue the large
gameplay-loop, item, and thick-laser owners. For OP/MAINE, recover SND_LOAD,
OP music, the remaining decoded payload bytes, and the v231 link/packer input
topology as checked-in source. For ZUN, recover ZUNINIT, MEMCHK, ONGCHK, and
natural `_main` call placement; the equal candidate composite still includes
IDA-derived assembly and an external binary.

For any promotion, run focused two-cold comparison and a complete cold
aggregate of affected accepted owners. Finish each bounded packet with
python3 scripts/preflight.py, python3 scripts/ci.py, and git diff --check;
record artifact, segment:offset, evidence class, command/receipt, exact result,
and unknowns in the focused note and ledgers.

## Private workspace

Targets, toolchains, Ghidra/IDA projects, generated builds, and receipts stay
ignored under .analysis/ or ghidra-project/. Retain v212/v213/v214 replay
inputs until superseded; v287 and v326 cold build trees were pruned after the
v326 final replay, retaining their receipts. Never commit original executables
or assets.
