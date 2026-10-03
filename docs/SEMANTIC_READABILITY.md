# Semantic readability before the native port

The `semantic/readable` branch starts from the latest local DOS `main`,
commit `8d20492`. It improves the maintained source while retaining a DOS
build as the behavioral baseline for future Linux/Windows x64 work. The
native port remains a separate product; this branch does not require every
historical exactness gap to be closed first.

Each batch should make one subsystem easier to understand in its source:

- Name values by meaning and unit: pixel coordinates, packed-byte offsets,
  paragraph segments, frame ticks, or fixed-point velocities.
- Explain the state transition, input/output ownership, failure behavior,
  and visible side effects at the point where they matter.
- Replace unexplained selectors with named constants and expose algorithm
  stages without changing their order or translation-unit composition.
- Preserve 16-bit promotions, signedness, truncation, near/far calls,
  segment ownership, global layout, and hardware timing. Record surprising
  behavior before deciding whether the native port should change it.
- Separate source-derived explanations from target observations, compiler
  checks, and runtime coverage. A plausible name is not a verified contract.

The validation baseline is the preceding DOS source, not the x64 prototype.
Use the smallest existing probe that can reject a regression. For each
naming/comment/constant batch, use dependency-validated incremental compilation and compare the complete linked bytes and ordered relocations
against the preceding source build. Reserve cold builds for cache uncertainty,
ABI/layout changes, historical acceptance gates, and stronger replay claims.
For structural rewrites, also exercise the relevant runtime transitions; build success alone is insufficient. If a
shared ABI/layout or an accepted historical owner changes, replay all affected
owners under the repository's Oracle policy. Avoid a repository-wide rename
or replacing assembly before its observable contract is understood.

## Queue

| Area | Readability objective | Current coverage |
| --- | --- | --- |
| PI image decoding | Commands, pixel packing, adaptive history, allocation and returned-pointer ownership | First bounded batch completed; independent DOS decoder and cold before/after equality pass |
| PAR and CDG/BFNT assets | Archive offsets, compression, plane order, masks, row direction and palette units | PAR and CDG contracts clarified; three full DOS products remain byte-identical; BFNT names, packed pixels, mask/color planes, clipping and lifecycle clarified; independent DOS hashes pass |
| OP/MAIN/MAINE handoff and score registration | Resident-state transfer, resource lifecycle, page/palette transitions and saved-file writes | Existing bounded scenarios; user confirms Normal Ending/save before the planar batch, and optimized seeded registration/save passes; source readability pass remains pending |
| Segmented memory | Paragraph headers, exact segment handles, hole splitting, coalescing and DOS ownership | Names and lifecycle comments clarified; full fast DOS equality and handle-reuse runtime controls pass |
| Graphics, input, timing and sound | Separate software state from device/interrupt side effects and preserve update ordering | Input latch/release/press budgets, joystick register protocol and IRQ-versus-polling waits clarified; remaining graphics and sound pending |
| Gameplay and bullet generation | Fixed-point arithmetic, RNG updates, pattern parameters and entity lifetimes | Bullet angle/group/spawn-lifetime batch completed; enemy-script VM opcode, timing, loop, ES operand and template-transfer contracts clarified; broader gameplay and RNG ownership remain |

This queue describes work to do, not a new completion percentage. Begin the
next native-port slice once its own source contracts and regression probes
are adequate; other subsystems can continue on this branch independently.

The first result and replay commands are recorded in
[the PI decoder note](reconstruction/product/TH04_NATIVE_PI_DECODE_V869.md).

The PAR/CDG batch and its limits are recorded in [the archive note](reconstruction/product/TH04_NATIVE_PF_ARCHIVE_V867.md) and the existing shared CDG ownership notes.

The BFNT batch and its bounded coverage are recorded in [the sprite note](reconstruction/product/TH04_NATIVE_SUPER_SPRITE_V870.md).

The allocator batch is recorded in [the native heap note](reconstruction/product/TH04_NATIVE_HEAP_V863.md).

The input/timing batch continues [the input-wait note](reconstruction/packed/TH04_SHARED_INPUT_WAIT_V565.md)
and [the native VSync note](reconstruction/product/TH04_NATIVE_VSYNC_V864.md).
It retains separate MAIN and OP/MAINE translation units and declaration
surfaces. The 2026-10-03 fetch/rebase confirms local `main` at `8d20492` is
already an ancestor; no remote main update or commit rewrite was needed.
Existing runtime fixes on `semantic/readable` remain in place. This batch
does not replace the Windows package while the user tests it.

The first bullet-generation batch records the one-byte clockwise angle unit,
group-member angle pipeline, synchronous spawn scratch state, byte-sized group
provenance and half-turn directional-sprite period. The complete native MAIN
remains byte-identical, the header ABI probe is OMF-equivalent, and the accepted
2,139-byte `bullet_a.cpp` owner passes two cold exact replays. A rejected signed
`% 0x80` form grew TC4J output by five bytes; the retained period constant is
explicitly unsigned. See [the bullet semantic note](reconstruction/product/TH04_SEMANTIC_BULLET_GENERATION_V1236.md).

The enemy-script VM batch names all 49 switch destinations without changing
their physical case order. It explains ES-relative unaligned word operands,
same-frame setup chains, the timed instruction's inclusive final update,
absolute/backward loops, template transfer and performance-scaled autofire.
The final complete native MAIN and all ordered relocations equal the preceding
source build. In one identical compiler context, the pre-batch exact source and
the semantic source produce byte-identical timestamp-normalized OMF and retain
the target's 1,680-byte body/table topology. The historical exact replay is
currently stopped before compilation by an unrelated stale v148 scaffold
digest, so this batch records source-to-source preservation rather than a fresh
cold target replay. See [the enemy-script note](reconstruction/main/TH04_MAIN_ENEMY_SCRIPT_NATURAL_V330.md).
