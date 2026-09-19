# TH04 compatibility dependency migration

This is the working recipe for removing `compat/rec98/` dependencies from
TH04 product source without weakening exact replay. Product declarations and
names use TH04 concepts. `src/shared/` means shared only by TH04 artifacts such
as MAIN, OP, MAINE, and ZUN.

Old TH01/TH02/TH03/TH05 paths may appear in the exact replay manifest as
attested identities of the pinned build scaffold. They must not appear as
product interfaces under `src/`.

## Current baseline

After the first batch, the dependency audit reports 34 forwarding headers and
235 include sites in 133 product files, down from 43 headers and 261 sites in
138 files. There are no missing, invalid, unused, or direct cross-game
includes.

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

   - If an unchanged pinned TH04 scaffold header still includes the old
     cross-game declaration, add a hash-bound `[[scaffold_header_rewrites]]`
     entry. This is replay plumbing only. It is gated by the presence of the
     selected local product header and only rewrites one attested include line.

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
