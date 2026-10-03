# OP/MAIN/MAINE process-handoff semantic pass (v1242)

This bounded pass documents the DOS overlay chain that the portable x64
runtime will have to replace. It changes comments, private preprocessing
aliases, and one MAINE local name. It does not change the resident ABI, call
order, resource order, code segments, linker inputs, or any linked byte.

## Maintained-source contract

The source expresses three process boundaries around one ZUN.COM-owned
resident block:

1. OP initializes a new run in the resident block, saves `MIKO.CFG`, releases
   OP-owned resources, and calls `execl()` for MAIN (or the debug executable).
2. MAIN reloads the resident segment from `MIKO.CFG`, runs one or more stage
   sessions, publishes the final score and run counters, releases gameplay and
   device resources, and calls `execl()` for either OP or MAINE.
3. MAINE reloads the same resident segment, selects the Ending/Extra/score-only
   route from `end_sequence`, performs registration/save, releases its ending
   resources, and calls `execl()` for a fresh OP process.

Successful `execl()` replaces the current process and therefore does not
return. The maintained source has no recovery after a failed load: each caller
has already torn down its current process state. This failure behavior is
source-derived; this pass adds no runtime failure injection.

The `MIKO.CFG` field is a real-mode segment value, not serialized resident
contents. ZUN.COM owns the paragraph block. OP, MAIN, and MAINE each install a
process-local far pointer into their own DGROUP. The comments consequently
separate persistent resident fields from assets and hardware services owned by
the current executable.

Private aliases name the roles `GAMEPLAY_BINARY`, `DEBUG_GAMEPLAY_BINARY`,
`MENU_BINARY`, `handoff_to_program`, and `next_program_fn`. They preprocess to
the historical identifiers, retaining the existing OMF symbols. Route values,
resource-release order, sound fades, page/font transitions, and `execl()`
arguments remain in their original order.

## Compiler and complete-artifact controls

The baseline and semantic builds use the same pinned TC86/TASM/TLINK product
builders with dependency-validated object reuse. The semantic build recompiles
the affected roots plus the builders' normal control owners:

- MAIN: the composite `demo_prefix.cpp` owner containing `main()`,
  `gameexecl.cpp`, and `ending.cpp`;
- OP: `entry.cpp`, all three gameplay/demo start roots, and the BGIMAGE control
  owner;
- MAINE: the resident loader, exit/exec wrapper, Ending entry root, and the
  BGIMAGE control owner.

All 12 pre/post OMF streams are equal after narrowly normalizing Borland
dependency timestamps, and all link-relevant records are equal. Aggregate
normalized identities are:

- MAIN, 3 objects / 12,242 bytes: `5502c9ec07b844ac...`;
- OP, 5 objects / 7,657 bytes: `9670b98c3b426e77...`;
- MAINE, 4 objects / 4,095 bytes: `dea263d72b80d44a...`.

The complete products are also raw-identical to the pre-edit baseline:

| Artifact | Bytes | SHA-256 | Ordered relocations |
| --- | ---: | --- | ---: |
| MAIN.EXE | 199,455 | `cb4c5b667f9a2d5a...` | 1,181 |
| OP.EXE | 79,372 | `ef37e6e890c4bfcbb...` | 817 |
| MAINE.EXE | 72,246 | `7bfd7fd594377d03c...` | 663 |

The strict comparisons cover MZ fields, header bytes, program image, overlay,
relocation-site values, and relocation order. Receipts live under
`.analysis/build/semantic-handoff-readable-v1242/`; the OMF comparison receipt
has SHA-256 `55e472fc8760c1510d348bb9760e91140a2a5f0c969191a2e1939d1fa7b8d537`.

This is compiler-observed source-to-source preservation. Existing exact and
decoded-exact owner evidence remains historical; this batch makes no fresh
cold target or packed-file exactness claim. The user's already completed
Normal routes and Ending/save returns corroborate the ordinary chain at
runtime, but they are not a new v1242 runtime Oracle.

## Native-port consequence

The x64 product cannot reproduce DOS `execl()` or pass a real-mode segment
through `MIKO.CFG`. It should model the same boundaries as explicit application
states over one long-lived resident-state object:

`OP setup/menu -> MAIN run -> optional MAINE ending/save -> OP setup/menu`.

Each transition must still publish resident fields before releasing the old
state, preserve the current cleanup order where device-visible effects depend
on it, and start the next state with fresh executable-local resources. The DOS
failure fall-through should become an explicit native launch/state-transition
error rather than an implicit return into torn-down state.
