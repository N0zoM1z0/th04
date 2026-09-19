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

MAIN has **476/491 reviewed authored C/C++ functions** and
**79,183/83,441 reviewed authored C/C++ bytes** exact; 40 accepted
original-style ASM units add 5,615 bytes. The last complete native aggregate,
gpt-5-6-sol-v349-randring-grcg-aggregate-001, passes all 253 default exact MAIN
owners twice (receipt SHA-256
72369ca8835e52bf356e9fe6c9c4c26553024ae80957ad63cbaccfdf61fccb21).
All 51 boss-named MAIN authored candidates are exact. None of these counts
means whole MAIN.EXE or whole TH04 is exact.

The [enemy helpers](reconstruction/main/TH04_MAIN_ENEMY_HELPERS_V328.md) and
[script VM](reconstruction/main/TH04_MAIN_ENEMY_SCRIPT_NATURAL_V330.md) now own
the complete B4M_UPDATE_TEXT load range `0x1554F..0x15C6C`: 1,822 bytes,
four reviewed functions, and all three ordered relocations are exact.
The [item producer](reconstruction/main/TH04_MAIN035_ITEMS_V154.md) owns
MAIN_035_TEXT load `0x1DA1B..0x1DF60`: all 1,350 bytes, six reviewed
functions, both switch-table tails, and fifteen ordered relocations are exact.
The [thick-laser producer](reconstruction/main/TH04_MAIN_THICKLASER_UPDATE_V181.md)
owns B4M_UPDATE_TEXT load `0x15D74..0x15ECD`: all 346 bytes, four reviewed
functions, and both ordered relocations are exact.

| MAIN physical owner | Target extent | Current blocker |
| --- | --- | --- |
| Dialog | DIALOG_TEXT load 0xCF3D..0xD728, 0x7EC bytes | Raw bytes/MAP/sites match, ordered relocs fail. Target has three descending MZ runs; current dialog.obj has two LEDATA/FIXUPP groups and two runs. Target OMF unknown. [Evidence](reconstruction/main/TH04_MAIN_DIALOG_BOUNDARY_V180.md) |
| Stage session | DEMO_TEXT load 0xAED0..0xB3ED, 0x51E bytes | Raw bytes/MAP/sites match; ordered relocations fail. A [function split and mid-function segment controls](reconstruction/main/TH04_DEMO_PAUSE_SPLIT_V282.md), plus [simple object reordering](reconstruction/main/TH04_DEMO_LINK_ORDER_V291.md), cannot reproduce the target order. |
| Gameplay init/loop | DEMO_TEXT load 0xAD03..0xAECF / 0xAB88..0xAD02 | Init misses one metadata byte. A [v346 compiler/cross-game candidate](reconstruction/main/TH04_DEMO_GAMEPLAY_TERNARY_V248.md) emits all 379 loop bytes at the object level with target instruction positions; focused linking is down to one case-sensitive `SHOTS_RENDER()` external. No linked exact claim yet. |

The [decoded-payload frontier](reconstruction/packed/TH04_PACKED_PAYLOAD_FRONTIER_V218.md)
is 7 OP bytes, 5 MAINE bytes, and 0 ZUN bytes against the cold overlay
candidates. DIET round-trip and relocation/header partitioning are recorded in
the linked note; no OP/MAINE/ZUN artifact-local exact cohort is accepted.
BGIMAGE remains 269 versus 208 target CODE. ZUN `cfg_init` and `_main` compile
from checked-in source and local headers, and three local support units match
bounded decoded extents, but the 6360-byte diagnostic component still differs
from target at 4241 bytes and depends on an external support library.

MAIN [`sub_CCD6` and `sub_B835`](reconstruction/op-maine/TH04_END_SCROLL_MPN_V195.md)
now have maintained product-only C++ source and reviewed 96- and 199-byte
target extents. TC4J emits 105 and 215 bytes respectively; exactness and
link ownership remain open.

The [gather-point renderer](reconstruction/main/TH04_MAIN_GATHER_POINT_RENDER_V326.md)
is now a checked-in 90-byte original-style ASM owner at B4M_UPDATE_TEXT
`13A9:1008`, raw/MAP/relocation exact. Its old replay wrapper is retired.
The [VRAM color header](reconstruction/shared/TH04_VRAM_COLORS_LOCAL_V287.md) is now
TH04-owned across 37 source files; cold replay freezes product headers. The
ongoing [compatibility migration](reconstruction/shared/TH04_COMPAT_MIGRATION.md)
has replaced fifteen adapters. The former `master.hpp`, `pc98_gfx.hpp`,
cross-game randring, and three GRCG boundaries now use TH04-owned runtime,
graphics, platform, math, and hardware interfaces. The remaining boundary is
28 forwarders and 59 include sites in 38 product files; the audit has no
missing, unused, invalid, or direct cross-game includes. The pinned ReC98
overlay remains. Standalone checked-in TH04 build closure, full
packed-file matching, runtime scenarios, and independent provenance remain
open. Track exact owners and the remaining 6 unreviewed MAIN functions from
config/units.csv, config/th04_main_authored_functions.csv,
config/th04_function_boundaries.csv, and python3 scripts/status.py.

## Next work and finish gate

Continue standalone source closure with the migration recipe above. The next
high-reach boundaries are `th03/formats/cdg.h` (7 include sites) and
`th05/resident.hpp` (5), followed by the 4-site overlap, sound, and player-shot
families. Recover each declaration set under its TH04 or shared owner and run a
complete default aggregate after every shared-header batch.

The independent MAIN byte frontier remains the gameplay loop from retained run
`gpt-5-6-sol-v346-gameplay-symbolic-focused-004`: bind the final case-sensitive
`SHOTS_RENDER()` external without altering the 379-byte object, then run
focused A/B, raw/MAP/ordered-relocation checks, function review, and a complete
default aggregate. The v346 result is evidence, not a promotion.

After gameplay, find a natural OMF producer for dialog/DEMO ordered
relocations without changing raw bytes or MAP. For OP/MAINE/ZUN, continue the
decoded payload and standalone source/link closure before packed-file and
runtime acceptance.

For any promotion, run focused two-cold comparison and a complete cold
aggregate of affected accepted owners. Finish each bounded packet with
python3 scripts/preflight.py, python3 scripts/ci.py, and git diff --check;
record artifact, segment:offset, evidence class, command/receipt, exact result,
and unknowns in the focused note and ledgers.

## Private workspace

Targets, toolchains, Ghidra/IDA projects, generated builds, and receipts stay
ignored under `.analysis/` or `ghidra-project/`. The cleanup retains the v349
randring/GRCG aggregate, v213 dialog diagnostic, v214 DEMO snapshot required
by gameplay probes, and v346 focused-004 continuation tree. Never commit
original executables or assets.
