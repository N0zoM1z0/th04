# Point-number pool and foreground adapter

v1373 adds MAIN's two 200-slot point-number rings to the native product. Item
pickups insert white or yellow numbers with their base score and pull multiplier;
bullet-zap events insert white numbers. The update prefix gathers live slots
before those insertions, so a newly inserted number first appears on the next
update. A ring overwrite keeps its previous-Y and padding bytes, and a retained
alive pointer still refers to that slot. Stage preparation clears the pool.

## Original observations

The locally pinned Japanese MAIN passes target/MZ checks and fresh database
attestation. Its provenance stays `candidate-local-attested`. The bounded
original producers are MAIN CIRCLE_TEXT(0AAF):11C2 (cursor initialization),
1204 (update), 1274 (renderer), 130E (glyph put), 1120 (scroll transform), and
MAIN_032_TEXT(13A9):0300/031A (yellow/white insertion), with the original digit
callee at main_03(13A9):4F5E. These are target observations; the database is a
consistent view of them, not an independent semantics Oracle.

The pool is DGROUP(2134):9634, 400*16 bytes. Cursors are 3ECE/3ECF, the 401-entry
near-pointer list is 3ED0, and the first-yellow pointer is 41F2. The 16-byte
record retains flag, age, X/Y, previous Y, four decimal bytes, width, multiplier
and padding. Original cursor initialization changes only its two bytes.

Update keeps the initial 24 ticks stationary, subtracts eight Q12.4 units on
later ticks, clips Y<=-64, marks age 37 for deferred removal, and frees removed
slots on the next update. The list preserves unused tail entries. White entries
precede yellow entries; the GRCG color switches from index 15 to index 11 at the
first-yellow pointer. Rendering skips leading zero cells, centers the remaining
digits, appends the implicit final zero, writes the resulting width, and appends
glyphs 10/11 for the multiplier. Rendering follows its retained list even after
an insertion overwrites a listed slot.

## Maintained native owner

`port64/point_numbers.hpp` and `.cpp` express the ring, lifecycle and glyph
requests with fixed-width fields. Near pointers become checked index+1 values;
zero remains the list terminator. No pool field or unused list entry is masked
from the component comparison. `main_state.cpp` updates this owner before
player/bullet/item updates and prepares its render once per simulation tick.
`view.cpp` consumes the cached requests after items and before enemy bullets,
mapping physical rolling rows into the visible display. A host paint does not
update ages, cursors, RNG or widths.

The mono font remains an external asset read from `GENSO/MAIN.EXE` on the
user-supplied HDI. The supported original MZ topology owns all 12*128 preshifted
bytes at DGROUP(2134):098A. The loader checks every shift against its unshifted
row before using it. No executable or glyph byte array enters the repository.

All-zero decimal rendering and a leading glyph outside the 12-cell font have
explicit native errors. Original's constructed all-zero renderer does not
return within the recorded 200000-instruction bound. This is a separate negative
input, not accepted ordinary gameplay. Values 10000/11000 retain the original
in-font leading glyph 10/11 behavior; insertion preserves all 16-bit values.

## Independent component comparison

`port64/verify_point_numbers.py` executes the actual original add/digit/update/
render/put/scroll instructions at load 1000 and 2000. DS 8000 and SS 7000 are
declared component adapters. The renderer inherits foreground GRCG RMW; the
existing independent hardware shadow processes actual ports and VRAM stores
onto a nonzero patterned 640*400 indexed background. It executes the original
self-modifying width instruction and glyph kernels without replacing them.

The final corpus has 830 cases: one cursor initializer, 128 insertions, 207 pool
updates and 494 render frames. Each case compares all 6400 pool bytes, both
cursors, all 401 list entries, first-yellow and a four-byte neighboring sentinel.
Only pointer representation is translated; no pool bytes are normalized.
Every numeral, both multiplier cells, all eight bit alignments, lower-edge
rolling, color order, overwritten/removed listed slots, integer wrap and a
39-tick lifecycle are exercised. All 494 complete indexed screens compare, not
just cropped glyphs or hashes.

Actual gameplay CTests also cover ordinary white pickup, yellow max-value
pickup, pull doubling, deferred render-list admission and multiplier requests.
They do not claim complete original gameplay or picture parity. Headless MAIN
and combat pictures are integration smoke/host-consistency evidence only.

Final receipts, sources, raw states and compressed complete screens are under
native `.analysis/port64/pointnum-v1373/`. The first 766-case run retains its own
496-file executed source snapshot; its receipt is never relabeled as the
expanded 830-case corpus. Final source freezing and build/validation receipts
separate the new native producer from old v1356 natural-route evidence.

```sh
nice -n 15 taskset -c 0 env PYTHONDONTWRITEBYTECODE=1 \
  python3 port64/verify_point_numbers.py \
  --target .analysis/targets/th04/main.exe \
  --exe .analysis/port64/pointnum-v1373/build-gnu/th04-port64-pointnum-contracts \
  --output-dir .analysis/port64/pointnum-v1373/FRESH-comparison
ctest --test-dir .analysis/port64/pointnum-v1373/build-gnu \
  --parallel 1 --output-on-failure
```

GNU's 69 programs pass 68 CTests; focused UBSan contracts/frontend pass the same
830/494 original component corpus. Two extra 400-entry list cases each emit 1892
glyph requests and match complete state/pixels on both hosts and loads. Five
wrong source variants complete 830 rows but reject. Five headless MAIN/combat
images agree across hosts as smoke evidence. Imported 22-file public Python
dependencies are also frozen; a fresh frozen-reader 300-case replay passes.
Retention is recorded in the final handoff and immutable private receipts.
Original dirty-page invalidation, scanout timing, palette-to-physical-display
behavior, complete natural DOS/native state/pictures, cross-emulator parity
and actual Windows acceptance remain open. Historical DOS exactness and all
old product/route receipts retain their original scope.

Final main CI 441/live Ghidra and native CI 313/target checks pass; the native
private Ghidra/tool gates skip where unavailable. All jobs are terminal. Lossless
retention reclaims 502460416 allocated file B (about 479.2 MiB).23 full raw/text/
mutant streams restore byte-exactly with modes and nsmtimes; 3093 protected
hashes and 496 current source pins read back. Successful current build objects
stay available. Retired 1040 public caches are source-backed. CI's explicit
compileall creates them despite PYTHONDONTWRITEBYTECODE; the initial absence
assertion rejects after complete archives succeed. Its source/log and partial
journal remain; a separate v2 reader resumes, restores all streams and passes.
Use native `.analysis/port64/pointnum-v1373/restore_streams.py` without options
for full verification, or `--restore` before unchanged old-reader commands.
Restoration refuses different existing files; private evidence is never
normalized or restamped. Retention/readback journals remain immutable.
