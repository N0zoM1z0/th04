# TH04 B4M Yuuka5 first-four natural reconstruction (v157)

## Scope

This packet covers the first four contiguous Yuuka5 helper functions in
`th04-main / MAIN.EXE`, `B4M_UPDATE_TEXT`, under the attested
`target:th04-main` local Japanese target. The target remains
`candidate-local-attested`; this packet does not establish independent pristine
release provenance.

The natural owner is `src/main/boss/yuuka5_patterns.cpp` and occupies exactly:

- segment `B4M_UPDATE_TEXT`, map address `13A9:243E..2812`;
- load-module offsets `0x15ECE..0x162A2`;
- target file offsets `0x176CE..0x17AA2`;
- analysis image addresses `0x25ECE..0x262A2` under the registered load mapping;
- size `0x3D5` / 981 bytes;
- target slice SHA-256 `49a1200656a7fcc0aa59431fe988b7716c358f828c54d0f8179e1e57d29b4537`.

The immediately preceding `0x15D74..0x15ECD` thicklaser cohort remains a
separate generic laser subsystem and receives no natural-source exactness credit
from this packet. The suffix beginning at `yuuka5_162A3` is likewise retained as
zero-credit replay plumbing and remains a reconstruction frontier.

## Reviewed function boundaries

The four physical extents tile the natural owner without gaps:

| Function | Load extent | File extent | Size | Target SHA-256 |
| --- | --- | --- | ---: | --- |
| `yuuka5_move_transition(unsigned int)` | `0x15ECE..0x15F96` | `0x176CE..0x17796` | `0xC9` | `8a9d707f1a43f0462d3ba9aceba39d9246bb0a97bbc94302dcc8a6d34b2597ac` |
| `yuuka5_pattern_sweep()` | `0x15F97..0x160A4` | `0x17797..0x178A4` | `0x10E` | `c9cf939222165cd0a851f28f2f28d476f89bdc0610c58dcd7302a8cb73629fcb` |
| `yuuka5_pattern_clouds()` | `0x160A5..0x161D6` | `0x178A5..0x179D6` | `0x132` | `cbdc4ef4f45c7c931ae02862933574c735a32a65f20bf4b2780cf3fa0ab58740` |
| `yuuka5_pattern_gather()` | `0x161D7..0x162A2` | `0x179D7..0x17AA2` | `0xCC` | `11d9f2bbedabf9668c8a417caa090c9f286346974912e0cb8ccfc2d38c991569` |

Fresh Ghidra observations were treated as provisional. Its entries at load
`0x15F56` and `0x15F8F` are not authored function starts. `0x15F8F` is the
shared `mov al,0` return tail of the first helper, reached by ordinary in-function
branches. The apparent Ghidra call to `0x15F56` originates at load `0x1830C`,
which is data inside the already reviewed exact 33-word `mugetsu_1821E` dense
jump table. TASM has no PROC at either internal address.

Ghidra also truncates the final helper before its compiler switch metadata.
Target bytes and the TASM listing close the physical extent through
`0x162A2`. The switch values are `{1, 3, 5, 0x11}` and its four jump words
resolve to load addresses `0x161FA`, `0x16221`, `0x1621C`, and `0x16228`, all
decoded instruction starts.

## Natural source and historical ABI

`src/main/boss/yuuka5_patterns.cpp` uses the historical large-model TH04 build
profile and preserves the observed near/Pascal ABI where required. It expresses
the state machine, sweep, cloud pattern, gather sequence, and switch in natural
C++ without inline assembly, copied target bytes, `#pragma codestring`, inert
padding, fake returns, or target patching.

The cold TC86 Borland C++ 4.02 object is valid OMF with module name
`th04/y5p1.cpp`. Both focused cold builds produced object SHA-256
`126d0103fe9329cc1f3c4e59b4bfe077496125469ca9854646ced38948377e50`
and dependency-timestamp-normalized SHA-256
`da49f408c4937baca809ab77e9633f3ba46d2734893a3a3942809af3031dad49`.

The owner has six ordered target relocations, reproduced in the same order by
both focused and aggregate candidates: load `0x1628E`, `0x16233`, `0x161BE`,
`0x16170`, `0x16147`, and `0x160A1`.

## Replay seam

The previous v156 explosion reconstruction left one TASM suffix beginning at
`sub_15D74`. v157 splits that suffix around the new natural owner into:

- `th04/b4mthick.asm`, the unchanged preceding thicklaser cohort;
- `th04/y5p1.cpp`, the maintained natural Yuuka5 owner;
- `th04/b4msuf2.asm`, the unchanged suffix beginning at `yuuka5_162A3`.

The old v156 `th04/b4msuf.asm` is still cold-built as an Oracle-only OMF object
but is not linked. This preserves the v156 auxiliary-object integrity check
instead of weakening or deleting a predecessor gate.

The resulting TLINK map places the physical producers consecutively at:

- `th04/eadd.cpp`: `13A9:21DD`, size `0x107`;
- `th04\b4mthick.asm`: `13A9:22E4`, size `0x15A`;
- `th04/y5p1.cpp`: `13A9:243E`, size `0x3D5`;
- `th04\b4msuf2.asm`: `13A9:2813`, size `0x8E2`.

## Exactness Oracles actually run

Focused cold replay:

`python3 scripts/replay_th04_main_exact_units.py --unit th04-main-yuuka5-first4-v157 --run-id gptweb-v157-yuuka5-probe-006`

- PASS for the 98-owner dependency closure;
- two isolated serial cold builds;
- raw owner bytes, map placement, ordered relocations, OMF validity, and object
  determinism all pass;
- both focused candidate MAIN images have SHA-256
  `e9b492f7c47b83707f65382c9e3bde62d3bef157736bb1c91a88934d8ba31dca`.

Candidate-state aggregate replay:

`python3 scripts/replay_th04_main_exact_units.py --run-id gptweb-v157-yuuka5-aggregate-candidate-001`

- PASS for all 190 default owners in two isolated cold builds;
- v157 remains raw/map/relocation exact;
- both candidate MAIN images have SHA-256
  `a71bea187f61f7d1a55bce02d83a1a6893482cf565d4842ff713a43329b79717`.

Post-promotion aggregate replay:

`python3 scripts/replay_th04_main_exact_units.py --run-id gptweb-v157-yuuka5-aggregate-final-001`

- PASS for all 190 default owners in two isolated cold builds with
  `failures=[]`;
- v157 remains exact for all 981 bytes, map placement, all six ordered
  relocations, and deterministic normalized OMF;
- both candidate MAIN images again have SHA-256
  `a71bea187f61f7d1a55bce02d83a1a6893482cf565d4842ff713a43329b79717`.

## Verification-plane boundaries

This packet establishes repository-native reviewed boundary ownership and exact
natural-source reconstruction for the four functions and 981-byte owner above.
It does **not** establish standalone TH04 production compile/link closure,
runtime storage identity, runtime scenario validation, independent pristine
release provenance, or Factory Truth Kernel acceptance. Those remain separate
verification planes.

## Next frontier

The immediate evidence-connected continuation is the adjacent Yuuka5 cohort:
`yuuka5_162A3`, `yuuka5_1630D`, `yuuka5_16389`, `yuuka5_1653D`, followed by FAR
`@yuuka5_update$qv` at load `0x16610`. `yuuka5_16389` is structurally important:
its current Ghidra body is noncontiguous and the TASM listing owns a 20-case
switch value/jump-table region after executable code. `yuuka5_162A3` and
`yuuka5_1653D` are TASM-visible entries with no corresponding Ghidra function,
so the next packet should remain target-first rather than inheriting database
boundaries.
