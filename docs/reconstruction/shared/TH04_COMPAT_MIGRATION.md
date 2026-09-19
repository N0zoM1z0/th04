# TH04 compatibility dependency migration

This is the working recipe for removing `compat/rec98/` dependencies from
TH04 product source without weakening exact replay. Product declarations and
names use TH04 concepts. `src/shared/` means shared only by TH04 artifacts such
as MAIN, OP, MAINE, and ZUN.

Old TH01/TH02/TH03/TH05 paths may appear in the exact replay manifest as
attested identities of the pinned build scaffold. They must not appear as
product interfaces under `src/`.

## Current baseline

After the overlap/sound/shot batch, the dependency audit reports 23 forwarding
headers and 34 include sites in 27 product files, down from the original 43
headers and 261 sites in 138 files. There are no missing, invalid, unused, or
direct cross-game includes.

The first batch removed these nine adapters:

| Old adapter | TH04-owned replacement |
| --- | --- |
| `th01/hardware/vplanset.h` | `src/shared/hardware/vram_planes.hpp` |
| `th01/sprites/pellet.h` and `th02/sprites/bullet16.h` | `src/main/bullet/sizes.hpp` |
| `th02/core/initexit.h` and `th03/core/initexit.h` | `src/main/core/initexit.hpp` |
| `th02/hardware/frmdelay.h` | `src/shared/hardware/frame_delay.hpp` |
| `th02/main/entity.hpp` | `src/main/core/entity.hpp` |
| `th02/main/execl.hpp` | `src/main/core/gameexecl.hpp` |
| `th03/math/polar.hpp` | `src/main/math/polar.hpp` |

The v347 default MAIN replay builds twice and keeps all 253 accepted owners raw,
MAP, relocation, and OMF exact. Receipt:
`.analysis/reconstruction/exact-unit-replay/gpt-5-6-sol-v347-compat-leaf-aggregate-004/receipt.json`
(SHA-256 `5612e132cdcb487cdca003d7604348e607e1a8e464856dc809ea3554999ff9f2`).
The disabled, unaddressed `th04-main-boss-prefix` replay entry has no promotable
extent; its new localized-fragment path is covered by replay unit tests and is
not presented as a byte-exact unit claim.

## Runtime and graphics batch

The second batch removes both high-reach vendor adapters:

| Old adapter | TH04-owned replacement |
| --- | --- |
| `libs/master.lib/master.hpp` | `src/shared/runtime/api.hpp` |
| `libs/master.lib/pc98_gfx.hpp` | `src/shared/hardware/graphics.hpp` |

The local interfaces use checked-in foundations under `src/shared/platform/`:
16-bit compiler and memory-model ABI, PC-98 types/constants, and x86 real-mode
operations. Product code contains no direct vendor or cross-game include. The
external function and variable names remain unchanged because they are part of
the target ABI.

This batch changes 132 include sites across 106 product files. Exact replay
also rewrites 13 runtime and 14 graphics include lines still present in the
pinned TH04 scaffold, recording every original and patched file hash. The local
headers retain the vendor include guards so an indirect pinned-scaffold include
cannot redeclare inline bodies. This guard compatibility is replay plumbing;
the checked-in product paths and organization remain TH04-owned.

The v348 default MAIN replay builds twice and keeps all 253 accepted owners raw,
MAP, relocation, and OMF exact. Receipt:
`.analysis/reconstruction/exact-unit-replay/gpt-5-6-sol-v348-runtime-gfx-aggregate-004/receipt.json`
(SHA-256 `5ef3de5246fd967ecb863ba907b2c61521fba34be8e66a0668d4d7ce9841b785`).
This proves the exercised declarations preserve the accepted MAIN producers;
it does not grant independent exact credit to unused API declarations.

## Randring and GRCG batch

The third batch removes the two queued families and the two smaller GRCG
adapters that the TH04 hardware interface supersedes:

| Old adapter | TH04-owned replacement |
| --- | --- |
| `th03/math/randring.hpp` | `src/main/math/randring.hpp` and `randring_ranges.hpp` |
| `th04/hardware/grcg.hpp` | `src/main/hardware/grcg.hpp` |
| `th01/hardware/grcg.hpp` | `src/main/hardware/grcg.hpp` |
| `platform/x86real/pc98/grcg.hpp` | `src/main/hardware/grcg.hpp` |

The batch removes 44 audited compatibility include sites. It also changes the
remaining maintained TH04 randring and GRCG includes, for 75 affected product
files in total. The random-ring interface keeps the target word cursor and
near/Pascal ABI; the range helpers used only by bullet addition have their own
bounded header. The GRCG interface owns TH04 mode switching, direct color
setup, and the segment-3 inline implementation without cross-game product
names.

Exact replay keeps these changes in TH04 product overlays. The `grcg3` fragment
uses one explicit localized-fragment mapping from the local header to its two
old scaffold includes. Do not tree-rewrite these pinned TH04 headers: the
all-game calibration also consumes some of them while compiling TH05, which
would leak the TH04-only interface into another artifact's build.

The v349 default MAIN replay builds twice and keeps all 253 accepted owners raw,
MAP, relocation, and OMF exact. Receipt:
`.analysis/reconstruction/exact-unit-replay/gpt-5-6-sol-v349-randring-grcg-aggregate-001/receipt.json`
(SHA-256 `72369ca8835e52bf356e9fe6c9c4c26553024ae80957ad63cbaccfdf61fccb21`).
No new exact owner is claimed by this dependency migration.

## CDG and resident batch

The fourth batch removes the next two queued adapters and localizes the
remaining TH04 resident includes at the same time:

| Old dependency | TH04-owned replacement |
| --- | --- |
| `th03/formats/cdg.h` | `src/main/formats/cdg.hpp` |
| `th05/resident.hpp` and `th04/resident.hpp` | `src/shared/config/resident.hpp` and `score.hpp` |

The CDG header exposes the eight load, free, and blit entries used by maintained
MAIN source with the target memory-model Pascal ABI. The resident header keeps
the attested 0x100-byte layout and offset assertions shared by MAIN and ZUN.
The local score header uses the historical `TH04_SCORE_H` guard so remaining
pinned TH04 headers cannot redeclare `score_lebcd_t`.

This batch removes 12 audited compatibility include sites and changes 21
remaining `th04/resident.hpp` includes, touching 24 product source files. The
disabled `boss_prefix` fragment maps its two resident include occurrences and
one CDG include back to their exact pinned-scaffold positions; replay tests
cover the occurrence-qualified mapping. The fragment has no current promotable
extent and receives no exact claim.

The two-owner v350 smoke replay passes raw, MAP, relocation, and OMF checks for
the resident and CDG surfaces. The v350 default MAIN replay then builds twice
and keeps all 253 accepted owners exact. Receipt:
`.analysis/reconstruction/exact-unit-replay/gpt-5-6-sol-v350-cdg-resident-aggregate-002/receipt.json`
(SHA-256 `06dde8c2982b09aeaa235d9bcaba7867bef82181ef45185e8b598ffd8f8e5fa6`).
No new exact owner is claimed by this dependency migration.

## Overlap, sound, and player-shot batch

The fifth batch removes the three tied four-site adapters:

| Old dependency | TH04-owned replacement |
| --- | --- |
| `th01/math/overlap.hpp` | `src/main/math/overlap.hpp` |
| `th02/snd/snd.h` | `src/shared/sound/api.hpp` |
| `th04/main/player/shot.hpp` | `src/main/player/shot.hpp` and local player/playfield/math foundations |

The overlap header keeps the four macro forms required by the complete boss,
bullet-add, and bullet-update producers, including their in-place evaluation
order. The sound header owns the TH04 mode enums, KAJA constants, globals, and
calling conventions. The player-shot header keeps the 68-entry layout, forced
byte enums, collision ABI, and option-laser declarations on local Q12.4 motion
types. Product paths and public API names contain no source-game identity;
legacy include guards only prevent duplicate pinned-scaffold declarations.

The shared KAJA implementation now overlays the TH04 wrapper instead of the
lower-game implementation, so the all-game calibration build remains
untouched. The unchanged `snd_se_reset` body is an identity fragment. The two
overlap fragments map the local include back to the pinned scaffold include.

The v351 focused replay passes the overlap, sound, and shot entry owners with
raw, MAP, relocation, and OMF equality. The v351 default MAIN replay then
builds twice and keeps all 253 accepted owners exact. Receipt:
`.analysis/reconstruction/exact-unit-replay/gpt-5-6-sol-v351-overlap-sound-shot-aggregate-001/receipt.json`
(SHA-256 `f599e4b1371d1e204031b3e0f5ee16ced7a4b5beebdf628edc1271e7a9577211`).
No new exact owner is claimed by this dependency migration.

## Batch workflow

1. Establish a clean baseline.

   ```bash
   python3 scripts/preflight.py
   python3 scripts/audit_compat_dependencies.py --check
   python3 scripts/audit_compat_dependencies.py --json > .analysis/compat-before.json
   ```

2. Choose one declaration family with a bounded ABI. Put MAIN-only declarations
   below `src/main/`; use `src/op/`, `src/maine/`, or `src/zun/` for the other
   artifacts. Use `src/shared/` only after evidence shows that multiple TH04
   artifacts share the declaration or implementation.

3. Recover the smallest complete TH04 declaration. Preserve widths, packing,
   enum forcing, memory distance, calling convention, and declaration order.
   Do not copy declarations into `compat/rec98/` and do not retain the source
   game's name in the product API.

4. Change every product include in the batch, then delete each unused
   forwarder. The audit must return zero missing, unused, invalid, and direct
   includes.

5. Adapt exact replay according to the source shape:

   - A full translation-unit overlay needs no new mode; the frozen local header
     closure is copied automatically.
   - A maintained fragment whose include lines differ from the pinned scaffold
     uses `source_mode = "localized-fragment"` and an explicit mapping:

     ```toml
     source_mode = "localized-fragment"
     scaffold_include_mappings = [
       { local = "src/main/subsystem/header.hpp", scaffold = ["old/header.h"] },
     ]
     ```

     One local include may map to several old scaffold includes. Replay first
     matches the mapped old fragment, then compiles the maintained TH04 fragment.
     Both hashes and the mapping are recorded in the receipt.

     If the same local include occurs in multiple conditional branches, give
     each mapping its one-based `occurrence` so every old position stays
     explicit and independently checked.

   - If an unchanged pinned TH04 scaffold header still includes the old
     cross-game declaration, add a hash-bound `[[scaffold_header_rewrites]]`
     entry. This is replay plumbing only. It is gated by the presence of the
     selected local product header and only rewrites one attested include line.

   - A high-reach vendor include that remains across many pinned TH04 scaffold
     files uses `[[scaffold_tree_include_rewrites]]`. The rewrite is restricted
     to the pinned `th04/` tree, gated by a frozen local header, limited to one
     exact include line, and records every input/output file hash. First verify
     that another artifact's calibration build does not consume those files;
     otherwise use maintained overlays and bounded fragment mappings.

6. Run the narrow replay first, then the complete default aggregate after any
   shared header or ABI change.

   ```bash
   python3 tests/test_exact_replay.py Rec98CompatTests
   python3 scripts/replay_th04_main_exact_units.py \
     --unit UNIT_ID --run-id AGENT-BATCH-focused-001
   python3 scripts/replay_th04_main_exact_units.py \
     --run-id AGENT-BATCH-aggregate-001
   python3 scripts/audit_compat_dependencies.py --check
   python3 scripts/ci.py
   git diff --check
   ```

7. Record the before/after dependency counts, local headers, affected artifact,
   exact result, receipt path and hash, and any unit that could not make an
   exact claim. A successful compile alone is compiler evidence.

## Handoff packet template

```text
Batch:
Old forwarders:
TH04-owned headers:
Product include sites changed:
ABI facts preserved:
Replay manifest adaptations:
Focused command/result:
Aggregate command/result/receipt SHA-256:
Audit before -> after:
Remaining uncertainty:
Next self-contained family:
```

Use `python3 scripts/audit_compat_dependencies.py --json` to route later work;
each header entry includes all source and line locations. The final standalone
source gate is:

```bash
python3 scripts/audit_compat_dependencies.py --require-zero
```
