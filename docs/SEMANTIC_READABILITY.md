# Semantic readability before the native port

General semantic expansion has reached its stopping condition for the native
owners. Resume only for a concrete port blocker. Current native routes,
Continue and CPU music have separately scoped verification; v1353 adds host
transport tested with explicit fake APIs, with physical devices unopened.
See [current native frontier](PORT64.md) and
[output ownership](port64/evidence/audio-output.md).

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
| OP/MAIN/MAINE handoff and score registration | Resident-state transfer, resource lifecycle, page/palette transitions and saved-file writes | MAINE score pipeline and the OP -> MAIN -> MAINE -> OP process/resident handoff are clarified and byte-preserved; user confirms Normal Ending/save and optimized seeded registration/save passes |
| Segmented memory | Paragraph headers, exact segment handles, hole splitting, coalescing and DOS ownership | Names and lifecycle comments clarified; full fast DOS equality and handle-reuse runtime controls pass |
| Graphics, input, timing and sound | Separate software state from device/interrupt side effects and preserve update ordering | Input latch/release/press budgets, joystick register protocol and IRQ-versus-polling waits clarified; scroll accumulation, tile-ring refill and two-frame copy handoff clarified; remaining graphics and sound pending |
| Gameplay and bullet generation | Fixed-point arithmetic, RNG updates, pattern parameters and entity lifetimes | Bullet angle/group/spawn-lifetime, player-shot lifecycle/damage, shared random-ring and process-local LCG ownership, and item drop/motion/scoring batches completed; enemy-script VM opcode, timing, loop, ES operand and template-transfer contracts clarified; broader gameplay remains |

This queue is a map of remaining source topics, not a prerequisite checklist.
The user's stopping condition is sufficient clarity to implement and verify the
current x64 subsystem. Pause semantic work once that condition holds. Return
only for a concrete portability ambiguity that blocks the next native slice,
and preserve the DOS build with the existing regression gates. Do not continue
renaming or commenting unrelated owners merely to exhaust this table.

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

The player-shot batch names the collision cache, laser renderer, hit-spark
phase, hitbox bounds, hit count and total damage. It documents hit-animation
lifetime, unsigned rectangle tests, per-hit integer damage reduction, Bomb
ordering, two-column laser eligibility and score-delta ownership. The semantic
and preceding sources compile to identical timestamp-normalized OMF, and the
complete native MAIN plus all 1,181 ordered relocations remain identical. A
fresh target replay is blocked by stale cross-unit staging in the historical
dependency closure, so the existing v177 exact evidence is retained without a
new exact claim. See [the player-shot note](reconstruction/main/TH04_MAIN_SHOTS_SEMANTIC_V1239.md).

The scroll batch names the previous/current row-advance slots, previous ring
row, parallel STD map/speed cursors and graphics-row copy entry while retaining
their historical external symbols. It explains the Q12.4 scroll accumulator,
400-scanline wrap, five-row map sections, 24-word visible ring refill and the
two-frame request handoff around suspended display scrolling. Both changed C++
owners compile to byte-identical timestamp-normalized OMF, and the complete
native MAIN plus all 1,181 ordered relocations remain identical. This batch
uses dependency-validated incremental compilation because no ABI, layout or
accepted extent changed; the prior exact states remain historical evidence
rather than a fresh cold-replay claim. See [the scroll integration note](reconstruction/product/TH04_NATIVE_SCROLL_BOX_V858.md).

The MAINE score-registration batch explains the two-character/five-rank file
layout, single decoded `hi` work buffer, bottom-up score insertion, no-entry
sentinel, name-keyboard repeat/confirm behavior, clear-bit persistence and the
ten-section re-key pass performed by every save. Historical DGROUP names remain
the external ABI; readable aliases preprocess to those same symbols. The build
recompiled the four edited SCORE roots plus its BGIMAGE control owner, and all
five timestamp-normalized OMF objects remain byte-identical. The complete
72,246-byte native MAINE and
all 663 ordered relocations also remain identical. This incremental replay
preserves the existing decoded-exact evidence for the four core owners without
making a new cold target claim. See [the MAINE score note](reconstruction/op-maine/TH04_MAINE_SCORE_CPP_V479.md).

The process-handoff batch documents the ZUN.COM-owned resident block and the
fresh-process lifecycle of OP, MAIN and MAINE. OP seeds the run contract and
tears down before `execl()`; MAIN reloads the resident segment, publishes score
and run counters before cleanup, and selects OP or MAINE; MAINE dispatches the
Ending route, saves, and starts a fresh OP. Readable private aliases preprocess
to the historical binary/function symbols. Twelve recompiled/control objects
across the three products have identical timestamp-normalized OMF and
link-relevant records. Complete MAIN/OP/MAINE files, headers, program images
and all 1,181/817/663 ordered relocations remain identical to the pre-edit
baseline. This is incremental source-to-source preservation, with no fresh
cold target claim. See [the process-handoff note](reconstruction/product/TH04_SEMANTIC_PROCESS_HANDOFF_V1242.md).

The random-ring batch establishes that `randring1_*` and `randring2_*` are two
code-segment-local accessor families over one 256-byte ring and one shared
word cursor. Samples are overlapping little-endian words and advance only the
cursor's low byte. The index-255 sample deliberately crosses into the adjacent
cursor byte and therefore has `0xFF` as its high byte before wrapping to zero.
The source now records descending fill order, AND/MOD range preconditions and
the absence of a zero-divisor guard. The header dependency closure recompiles
53 C++ roots plus three edited ASM objects; all 56 timestamp-normalized OMF
streams and link-relevant records agree with the pre-edit build. The complete
199,455-byte MAIN and all 1,181 ordered relocations also remain identical. See
[the random-ring note](reconstruction/main/TH04_MAIN_RANDRING_SEMANTICS_V1244.md).

The shared-LCG batch separates each executable's initialized `random_seed`
from the persistent resident `rand` seed source. It records TC4J's unsigned
32-bit modulo update and 15-bit result, OP's menu-frame accumulator, MAIN's
single startup copy and demo override, cross-Stage call-stream continuity, and
MAINE's route-dependent verdict/save ordering. The portable contract uses
explicit `uint32_t` state so Linux and Windows x64 agree despite their different
`long` widths. Nine changed/control OMF objects and the complete MAIN, OP and
MAINE executables remain identical to the pre-edit semantic build. See
[the shared-LCG note](reconstruction/product/TH04_SHARED_RANDOM_LCG_SEMANTICS_V1246.md).

The item-lifecycle batch names miss-drop slots, velocity fields, pool indices,
base score values, popup color selection and attraction angle. It records the
automatic-drop half-rate table, the miss routine's discarded but observable
random draw, last-life override ordering, inclusive overflow table, dream-score
saturation, Bomb multiplier, asymmetric performance accumulators, deferred
removal and unsigned pickup rectangle. The portable contract calls out the
full-power big-item table read that precedes clamping and must be represented
without an out-of-bounds host access. Twenty C++ dependency roots and one ASM
owner retain identical normalized/link-relevant OMF, and the complete
199,455-byte MAIN plus all 1,181 ordered relocations remain identical. See
[the item semantic note](reconstruction/main/TH04_MAIN_ITEM_SEMANTICS_V1248.md).
