# Shared CDG loader ownership, v797

The maintained TASM translation unit `src/shared/formats/cdg_load.asm` now
provides the same CDG loader for MAIN, OP, and MAINE. Its CDG slot layout and
far Pascal stack access are declared locally. The source no longer includes
TH03 paths.

| Artifact | Target load-module extent | TLINK contribution | Raw result | Module relocations |
| --- | --- | --- | --- | ---: |
| MAIN.EXE | `0x13938..0x13A9B` (file `0x15138..0x1529B`) | `130E:0858`, `0x164` | zero differences in focused MAIN cold replay | checked by MAIN replay |
| OP.EXE | `0xE57A..0xE6DD` | `0DA1:0B6A`, `0x164` | zero differences in two isolated source builds | 14/14 ordered overlap |
| MAINE.EXE | `0xD778..0xD8DB` | `0CC7:0B08`, `0x164` | zero differences in two isolated source builds | 14/14 ordered overlap |

The OP and MAINE target MZ images are DIET packed. Their target comparison is
against separately hash-attested decoded load modules. The focused replay
reassembles the checked-in source with pinned TASM32 5.0 in independent A/B
worktrees, cold-links each artifact, checks the entire linker contribution,
all ordered MZ relocation entries, and identity with the retained complete
candidate program. Its receipt is
`.analysis/reconstruction/probes/v797-op-maine-cdg-load-local-002/receipt.json`.
The pinned candidate is link scaffolding, not independent target evidence.

The source move and local declaration replacement preserve the module's
link-relevant OMF hash in OP and MAINE. MAIN's source path and declarations
are replay inputs. The v798 accepted-unit replay passes A/B cold builds with
receipt SHA-256 `ff7a7b0b5b49031c60f4ddf46e5e99abd3dc71572eac7fdd1d7f7f338fa33379`.
The OP/MAINE receipt SHA-256 is
`527cd555ff07457bbed2b16cfa5dad7bc41193b6e47720b26770ac425785d2c8`.
The generalized probe's default `cdg_load` mode was rechecked after the
`cdg_put` extension in v801 (receipt SHA-256
`04bfa2bad5f5cde580651b9ac9e5dd0520b19401b94da1f3270958c89d9dd9df`).
This proves the decoded module
extent, while several MAINE internal Ghidra function cuts remain provisional and
the packed-file offsets and complete product builds remain unresolved. The
function-exact C/C++ denominators do not include this original-ASM module.

## OP internal boundaries, v810

The attested OP target bytes and MAP tile `0DA1:0B6A..0CCD` without gaps:

| OP offset | Entry | Source-owned extent |
| --- | --- | ---: |
| `0B6A` | `CDG_LOAD_SINGLE_NOALPHA` flag-setting entry, falls through | `0x06` |
| `0B70` | `CDG_LOAD_SINGLE`, ends `RETF 8` | `0x5F` |
| `0BCF` | alignment NOP | `0x01` |
| `0BD0` | internal near single-image reader, ends `RETN` | `0x58` |
| `0C28` | `CDG_LOAD_ALL_NOALPHA` flag-setting entry, falls through | `0x06` |
| `0C2E` | `CDG_LOAD_ALL`, ends `RETF 6` | `0x5C` |
| `0C8A` | `CDG_FREE`, ends `RETF 2` | `0x35` |
| `0CBF` | alignment NOP | `0x01` |
| `0CC0` | `CDG_FREE_ALL`, ends `RETF` | `0x0E` |

The two `NOALPHA` labels are shared-entry prefixes, not standalone return
paths. Ghidra omitted those entry functions; the target byte stream, MAP
publics, and complete cold-linked module delimit them. All seven OP
function-like observations now have reviewed entry extents. This boundary
review does not change the accepted decoded module state or authored C/C++
exact count.

## MAINE internal boundaries, v815

MAINE's independently attested `0CC7:0B08..0C6B` module has the same
source-owned partition under its own link addresses: `0B08+6` NOALPHA
prefix, `0B0E+0x5F` SINGLE body, `0B6D` alignment, `0B6E+0x58`
internal near reader, `0BC6+6` ALL_NOALPHA prefix, `0BCC+0x5C` ALL body,
`0C28+0x35` FREE body, `0C5D` alignment, and `0C5E+0x0E` FREE_ALL body.
Target return opcodes and fallthroughs close all seven MAINE observations;
the complete MAINE module already passed its own v797 A/B cold raw and
relocation comparison. Its packed-file offset remains unknown.

Replay:

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_th04_op_maine_cdg_load.py \
  --output-dir .analysis/reconstruction/probes/NEW-CDG-REPLAY
taskset -c 0,1 nice -n 10 python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-module-th04-cdg-load-asm-13938 --run-id NEW-MAIN-CDG-REPLAY
```
