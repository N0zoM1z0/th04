# Semantic readability before the native port

The DOS `semantic/readable` branch began at `8d20492`. Its purpose was to
make contracts clear enough for Linux/Windows x64 porting while retaining the
preceding DOS source as the regression baseline. That stopping condition is
met for the implemented native owners. General semantic work is paused;
clarify another bounded owner only when it blocks the port.

## Completed contracts and evidence

| Area | Clarified behavior | Focused evidence |
| --- | --- | --- |
| PI | Command units, packed pixels/history, DOS allocation, returned-pointer lifetime | [PI](reconstruction/product/TH04_NATIVE_PI_DECODE_V869.md) |
| PAR/CDG | Archive offsets, compression, plane/mask order and hardware ownership | [PAR](reconstruction/product/TH04_NATIVE_PF_ARCHIVE_V867.md), [CDG](reconstruction/op-maine/TH04_SHARED_CDG_PUT_V799.md) |
| BFNT | Header, pattern ownership/rollback, packed pixels, clipping and palette units | [Sprites](reconstruction/product/TH04_NATIVE_SUPER_SPRITE_V870.md) |
| Heap | Paragraph headers, exact handles, splitting/coalescing and DOS reassignment | [Heap](reconstruction/product/TH04_NATIVE_HEAP_V863.md) |
| Input/timing | Latches, release/press budgets, joystick I/O, IRQ versus polling | [Wait](reconstruction/packed/TH04_SHARED_INPUT_WAIT_V565.md), [VSync](reconstruction/product/TH04_NATIVE_VSYNC_V864.md) |
| Scroll | Q12.4 accumulation, 400-line wrap, map/tile ring, two-frame copy handoff | [Scroll](reconstruction/product/TH04_NATIVE_SCROLL_BOX_V858.md) |
| Bullet groups | Byte-angle units, spread/ring member order, synchronous spawn scratch | [Bullets](reconstruction/product/TH04_SEMANTIC_BULLET_GENERATION_V1236.md) |
| Enemy VM | 49 destinations, compiler-sensitive case order, ES operands, timing/loops/fire | [VM](reconstruction/main/TH04_MAIN_ENEMY_SCRIPT_NATURAL_V330.md) |
| Shots/items | Lifetime, collision/damage/score ordering, drop/RNG order and overflow | [Shots](reconstruction/main/TH04_MAIN_SHOTS_SEMANTIC_V1239.md), [Items](reconstruction/main/TH04_MAIN_ITEM_SEMANTICS_V1248.md) |
| Random ring | One 256-byte ring/shared cursor, overlapping words and index-255 boundary | [Ring](reconstruction/main/TH04_MAIN_RANDRING_SEMANTICS_V1244.md) |
| LCG | Unsigned 32-bit update, process-local stream versus persistent resident seed | [LCG](reconstruction/product/TH04_SHARED_RANDOM_LCG_SEMANTICS_V1246.md) |
| Ranking | Ten sections, insertion/no-entry, name repeat/confirm, clear bits and re-key | [Score](reconstruction/op-maine/TH04_MAINE_SCORE_CPP_V479.md) |
| Process handoff | ZUN resident lifetime, config segment, publish/cleanup and fresh executable | [Handoff](reconstruction/product/TH04_SEMANTIC_PROCESS_HANDOFF_V1242.md) |

Naming/comments/constants retain 16-bit promotions, signedness/truncation,
near/far ABI, physical case order, translation-unit composition and external
symbols. Native host arithmetic uses explicit widths; Linux and Windows have
different `long` widths. Record undefined source behavior before choosing a
safe representation (for example, big-power's pre-clamp table read).

## What validation establishes

Each subject note records its own producer and baseline. Dependency-validated
incremental DOS builds compare complete files and ordered relocations to the
preceding source. Changed/control objects compare timestamp-normalized and
link-relevant OMF. PI also has two isolated cold service-harness comparisons;
input and bullet owners have bounded cold target replays. Runtime service
probes add pixel, lifecycle or state confidence where recorded.

These are distinct claims: a before/after source comparison is not original
whole-file exactness. Historical replay attempts for CDG, VM, shots and bullet
performance encountered missing snapshots or stale scaffold/dependency staging.
Their rejection is recorded; prior exact states are not promoted or silently
re-attested. See the notes and `config/evidence.csv` for the failed commands.

## Remaining work

- Resolve only ambiguities needed for registration scene/persistence, Bomb/
  death/Continue, Extra, full HUD/audio/config or another specific native owner.
- Repair old exact replay staging separately if fresh exact acceptance is in
  scope; do not make it a gate for native functionality.
- Keep bounded runtime validation for structural rewrites and ABI/layout
  changes. A successful build or readable name alone proves neither behavior
  nor original bytes.

The native done/TODO and currently published preview are in
[porting status](PORTING_STATUS.md). Detailed batch history remains in subject
notes, ledgers and Git; it is not an endless semantic queue.
