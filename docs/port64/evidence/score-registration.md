# Score Registration evidence

Historical bounded results, preserved from `docs/PORT64.md`. Current state is
[the port overview](../../PORT64.md). Original CPU execution and adapter scope
remain explicit; successful component controls do not accept complete gameplay.

## Score-file engine

v1297 implements the MAINE score-file owner as byte sections, with English
comments explaining the cipher, layout, ranking and shared-buffer lifetime.
`score_file::File` owns the ten encoded 196-byte sections and an ordered I/O
trace; it preserves trailing bytes and the unread buffer suffix after a short
read. It currently models successful file operations in memory. Registration
rendering/input, host disk persistence and the fresh OP return are still next;
the playable Windows GUI remains v1296, with no save-completion claim.

The six recovered MAINE bodies at `0A05:20F9..24B6` cover decode, encode,
recreate, load, save and insert. All complete extents are hash-attested in
`verify_score_file.py`; full original LCG instructions run at `0000:1C5A`.
The original producer executes 1,288 distinct cases at load segments1000/2000:
35 encode,245 decode,28 recreate,140 load,140 save and700 insertion cases.
Guards check resident bytes, surrounding HI storage, stack cleanup, selection,
RNG state/draw count and closed-file state. File calls use explicit successful
byte-store adapters, so this does not prove physical DOS filesystem behavior.
The native GNU/Wine/optimized UBSan/actual Windows consumers reproduce the full
ordered operation/data/result streams. One-byte stream mutations reject.

Important observed semantics for the registration caller:

- Decode validates only the low checksum byte, while encode stores a full
  16-bit sum. The ascending decoder reads the next still-encoded byte.
- A missing file or bad selected checksum recreates and writes all ten
  sections immediately, consuming20 RNG draws. This contradicts the older
  DOS `load_for.inl` comment saying only the in-memory table is replaced.
  Recreate preserves eleven unused payload bytes from the decoded buffer.
- Save consumes22 RNG draws and rekeys all ten sections. It ignores decode
  failures in other sections and ends with section9 encoded in the shared HI
  buffer. Keep editable rendering state before saving; do not render that
  final buffer as the selected table.
- Equal scores insert before existing equals. Stored gaiji-minus-A0 is signed;
  only eight name bytes, eight digits and stage shift, while each row's ninth
  name byte, cleared mask and unused storage retain their original positions.

A separate wrapper probe executes real `file_append` and `file_read` under
successful INT21 open/seek/read adapters:15 cases at both loads cover DWORD
append positions and direct/buffered short reads. Append seeks to EOF; reads
leave unread HI bytes intact. Original internal buffer cursors can remain stale
when valid-count becomes zero; no complete internal buffer equivalence is
claimed. Native seek-created holes use zero bytes as an explicit byte-store
adapter convention, not a claim about DOS unallocated file contents.

Three fast builds produce32 AMD64 executables and pass31 CTests each. All62
preceding GNU/UBSan products stay raw-identical;31 prior Windows products differ
only in eight allowed PE timestamp/checksum bytes. The new Windows contract
initially missed static runtime flags because it followed CMake's policy loops;
that failed interop run is retained. Moving the declaration before the loops
and adding it to both policy lists fixes it; imports are only KERNEL32/msvcrt.
Actual Windows reruns all31 contracts and the1,288-case full trace. The frozen
228-file source manifest is
`b9b003db4aded7d257c5f70e43721a5fc04c26fb5761bf21012ab8cef2320766`.
Receipts and exact commands: `.analysis/port64/score-file-v1297`.
The current GUI/launcher hashes are unchanged. DOS source, target inputs and
historical unit/function exactness are unchanged. Continue the concrete
registration owner rather than expanding general semantic work.

## Registration menu control owner

v1298 implements the complete logical registration menu in `registration::Menu`.
It owns character/rank selection, other/current table snapshots, insertion and
clear-mask updates, the51-cell gaiji keyboard, eight-character editing, input
lock/repeat and the save/acknowledgement/resource-release request sequence.
English source comments explain these lifetimes and the distinction between
TH04 gaiji codes and host text. Graphics, palette timing, sound, wait0 and host
persistence still need a scene/backend. The Windows GUI remains v1296 at
registration entry; no rendered or integrated save-completion claim follows.

`verify_registration.py` attests the whole924-byte original menu at
MAINE`0A05:27C4..2B60` (payload`C814..CBB0`, SHA-256`7bef6c89...`), including its
18-byte switch table, and the51-byte keyboard at recovered DGROUP`0E53:082C`.
Original menu, alphabet-cursor helper, all six score-file bodies and the actual
LCG execute at loads1000/2000. Table/name drawing, PI/BFNT, sound, palette fades,
wait0 and successful file calls are guarded adapters. The controls cover the
logical command/input/file order; they do not prove pixels or fade/wait clocks.

All382 cases agree on GNU, Wine, optimized UBSan and actual Windows. They cover
three resident character bytes, five ranks, both shots and Turbo settings,
Good/Bad/Extra/score-only end values, missing/empty/short/trailing files, every
clear-mask branch, below-table scores, held/inherited/changing/chord input,
330-refresh navigation holds, eight-glyph entry and all keyboard commands.
Per-iteration cursor/row/column/lock/BYTE-repeat and complete HI snapshots match;
full ordered file/data requests and final RNG/draw count/table match. Original
resident bytes, HI preceding guard and near stack cleanup are checked.

Preserve these original input details when joining the host keyboard:

- A reset sample is ORed with the next sense sample. One released sample can
  still contain the previous held key. Lock starts at1; a complete release
  clears it. A different nonzero chord leaves the previous lock in place.
- The repeat counter is a BYTE, not reset on accepted repeated actions. It
  unlocks on even values above30 and retains its wrap behavior.
- Direction bits act independently before Shot/OK, then Bomb, then Cancel.
  Combined Shot/Bomb can type and erase the next cell in one iteration.
- Space writes gaiji2; left erases the current cell then moves back, right
  only moves forward. Typing the eighth glyph selects the explicit Enter cell.
  Escape saves the partial name; it does not discard the ranking entry.

The non-entry path saves then emits wait0 before resource release/blackout1.
Rendering requests carry pre-save snapshots because the final work buffer is
encoded section9. A future scene must consume fades/waits in order and persist
at the save boundary; calling the logical owner alone does not implement those
physical effects. Preserve clean page1 for name-background restoration, use a
separate PC-98 text overlay for reverse attributes, and translate all host
registration actions explicitly rather than the Ending any-key bridge.

Three incremental fast builds produce33 AMD64 products and pass32 CTests each.
All64 preceding GNU/UBSan files are raw-identical;31 prior Windows products
compare to retained v1296 bytes with only allowed PE metadata differences.
Old PE bytes/metadata for the new v1297 score-file contract were not retained,
so no complete binary-continuity claim is made for that one executable; all
three current consumers pass its retained1,288-case original reference instead.
The new registration Windows contract imports only KERNEL32/msvcrt. Actual
Windows runs all32 contracts and382 full menu traces; independent Python
readback checks every output and all99 product/source hashes.

The initial Oracle duplicated an access-page event through its instruction
observer and inherited OUT hook; a first-case probe reproduces that negative.
Only the identified development verifier was stopped; removing the duplicate
observer repairs it. An initial CTest command accidentally passed the new
contract name as an argument to the old score contract; its usage rejection is
retained and the focused CMake repair passes all32 tests. Neither negative is a
game defect. Final233-file manifest:
`2f21eb008e01c618532aec465e6c5010cb32039bf6d8e502d71b6b7922facca3`.
Receipts: `.analysis/port64/registration-v1298`. DOS source, targets and historical
exact/unit/function acceptance are unchanged. Next implement registration
pixels/text overlay, host score-file persistence and the fresh OP return;
keep general semantic expansion stopped.

After all consumers pass,30 byte-identical completed score/menu text streams
share verified hard-linked storage, reclaiming104MiB while retaining every
path/hash. Independent producers ran before deduplication; this does not create
reference equality. Use fresh output directories or atomic replacement rather
than modifying shared trace inodes. `trace-dedup-receipt.json` records every link
and post-dedup full platform readback passes.

## Registration graphics and text plane

v1299 adds `registration_render.hpp/.cpp`: a graphics consumer of the v1298
menu's retained decoded snapshots, a separate PC-98 WORD text/attribute bank,
and SCNUM2 numeral sprites. The logical menu, score cipher and DOS source are
unchanged. Scene fades/waits, audio, host score persistence and fresh OP return
still need integration; the published Windows GUI remains v1296.

Original MAINE `0A05:24B6..2793` executes score/stage/name/row/table helpers;
`0A05:2B60..2C29` executes EGC setup and the complete name-strip copy loop.
Original `0000:0FC4..105E` executes character/attribute stores, and separate
actual `0000:275E..2910` SUPER and `0000:36B6..37F3` graphics-font kernels supply
pixels. The pinned packed target/payload/559 relocations remain attested; the
Ghidra check covers its packed wrapper, not invented payload database topology.
GRCG/EGC/CGROM, planar BFNT staging, console clear and guarded text RETF ABI
returns are explicit adapters. PI pixels retain preceding-decoder regression.

Preserve these rendering rules:

- Both tables draw onto page0; page1 retains clean HI01. Name edits copy page1
  to page0, leave access0, then redraw the graphics shadow and text cursor.
  X is shifted by3 and width divided by16: the caller's X+2 rounds down to its
  byte column. Height is exactly16; this helper differs from BGIMAGER's h+1.
- Names use color14 shadows and color12 ordinary foreground. Selected names
  use TRAM attribute41; the selected half-cell pair becomes45. Score sprites
  use bank10 for the selected row; the most significant stored byte may hold
  two decimal digits. Stage foreground is7 when selected, otherwise12.
- Keyboard attributes E1/85 and name attributes41/45 belong to a separate text
  plane. Pinned DOSBox-X video-source corroboration uses an inverted glyph mask
  for reverse, with transparent holes and fixed bright text colors. It is not
  a physical-video observation. Low-byte 56/57 codes with zero high byte take
  the supplied ANK font; preserve these gaiji0/128 encoding edge cases.
- Non-Turbo graphics text inherits the graph-font weight; all four effects
  are controlled. SCNUM2 and HI01 have identical RGB palettes in the attested
  assets. An unexpected palette or undefined numeral pattern is rejected;
  malformed-score pattern-table reads are outside the defined pixel claim.

At loads1000/2000, 2,256 helper calls, 976 sprite sites and 400 font sites per
load produce158 snapshots. Each contains two complete indexed pages,48 palette
bytes,8,000 raw TRAM bytes and a complete RGB frame:203,511,584 bytes per native
consumer. Original stores/copy loops and explicit software-video adapters agree
with GNU, Wine, optimized UBSan and actual Windows. Cases cover both characters,
all ten selected positions/no-entry, all256 gaiji codes/four registration
attributes, eight numeral alignments, inherited font weights, byte-rounded
restore windows, real menu-generated sections/input/name edits and clear/tone
checkpoints. RGB composition is separately emulator-source corroborated.

Three fast builds each retain33 AMD64 products and pass32 CTests. Thirty-two
preceding GNU products remain raw-identical;32 PEs differ only in timestamp/
checksum metadata after independent normalized digest comparison. Thirty
preceding UBSan products remain raw-identical; changed GUI/cutscene products
are checked with32 contracts and80 original verdict cases/527 full-string
kernels/160 pages, without a complete ELF continuity claim. Existing382 menu
and1,288 score cases still agree on all three native consumers. Actual Windows
runs32 contracts and158 full captures; Python independently reads every output
and all99 product hashes. All71 Windows package/save/asset files are unchanged.

The mixed hooked/real original TRAM RETF path reports inconsistent CS:IP in the
initial Unicorn control. Its exact register/stack trace is retained; the
repaired control guards original RETF8/10 immediates and applies their return
ABI after all original stores. This limits the return claim, not the recorded
text RAM bytes. The first CLI compile rejected a wrong namespace for decode_pi;
the reference-consumer receipt initially rejected a wrong nested-field lookup.
Both development errors were corrected before final readback. Page0/page1,
palette/TRAM/RGB comparator mutations all reject.

Final238-file manifest:
`e4c55fe9b3c8b02f426349cecac47c976d4a26276d3821cdc7712aba92f6177b`.
Receipts: `.analysis/port64/registration-render-v1299/platform-review.json` and
`build-products-bound.json`; the original producer is `controls-linux-final`,
and the final native consumers are `consumer-{linux,wine,ubsan}-bound` and
`actual-windows-bound`. Use the checked-in Python/PowerShell verifiers with
fresh output directories. No DOS/exact/unit/function acceptance changes.
Next implement the ordered registration scene, persist the separate host score
file at its save boundary, and enter fresh OP; keep general semantic stopped.

After independent production and full readback,33 completed duplicate capture/
trace files share verified storage. The earlier90-snapshot development pair is
archived with full member readback; net2,385,702,912 bytes are reclaimed.
Current158-snapshot original reference and all three fast caches remain
expanded. Restore old development paths before use, and never modify shared
capture inodes in place. `capture-storage-receipt.json` records the archive,
restore command, every shared path/hash and3,921 protected file hashes.

## Registration scene and host save

v1300 resumes the native port and resolves the v1299 scene-integration question.
`registration::Scene` consumes drawing, I/O, song/sound, wait and fade requests
in order. Startup stops at black-in; only after its35th refresh are the initial
input sample and keyboard/no-entry save evaluated. Menu input retains the
original two-sample release, repeat lock and direction/Shot/OK/Bomb/Esc order.
The renderer receives each decoded snapshot before save re-encodes HI. The
inherited graphics text weight is retained across Ending/Staff/verdict.

`verify_registration_scene.py` executes the original MAINE decoded-relative
`0000:0622..06A3` palette-black-in/out bodies at loads1000 and2000. VBlank and
palette output are explicit adapters: black-in(2) takes35 refreshes and
black-out(1)18. This establishes a refresh schedule, not physical PC-98 timing.
The previously attested packed target and decoded payload remain pinned;
`candidate-local-attested` is still a provenance gap. Root `ghidra.py th04-maine
check` passes full bytes/header/entry/relocations/samples. The native worktree's
missing `.tools` prevents a local database check and is not counted as a pass.

`score_file::HostStore` replays each ordered operation into a pending file,
committing only at a dirty writer close. A uniquely reserved temporary directory
prevents truncating another file. Replacement uses same-filesystem rename on
Linux and `MoveFileExW(REPLACE_EXISTING|WRITE_THROUGH)` on Windows. Failure
propagates before fresh OP. This does not claim power-loss durability on Linux.
Scores are separate from the read-only HDI, using the documented host data
folder or `--save-dir`. An explicit native repair treats files shorter than
1960bytes as absent: original unchecked short reads can accidentally pass an
all-zero checksum and later address an undefined numeral. The core File's
original short-read semantics and1288 original cases remain unchanged. Larger
files retain their trailing bytes.

Sixteen scene controls cover all ten partitions, partial/full names, inherited
held keys, missing/truncated/deterministically bad-checksum files, no-entry
acknowledgement, retained tails, failed replacement and render/RNG isolation.
They run with public synthetic assets and separately the original PI/BFNT/font.
`--registration-checks DIR` drives30 seeded child scenes through real resident
and process ownership, save/reload, blackout, fresh OP(gen+1/LCG1), release of
MAINE resources and a second actual MAIN handoff(gen+2). These are integration
controls, not natural full-game routes. Linux, optimized UBSan and actual
Windows generate112 identical BMP/score files. Both GUI source backends join
this owner; the published GUI remains v1296 until later route acceptance.
All runs use `--mute`; no audio device is opened and ordered requests remain.

Each host passes33 contracts. The245-file manifest
`635698a758e590316b03ebd4d4e45ee222bff3b90cb649e651a2df2af1aa1f58`
binds102 AMD64 products. Final-source original consumers pass1288 file cases,
382 menu cases and158 complete graphics/text/palette/RGB snapshots
(203511584bytes each); GNU/optimized UBSan/actual Windows graphics agree.
Private receipts live in `.analysis/port64/registration-join-v1300/`:
`source-manifest.json`, `platform-review.json`, `fades-original-source-final`,
`score-source-final`, `menu-source-final`, `render-source-final`,
`render-ubsan-source-final`, `render-windows-source-final`, and
`actual-windows-source-final`. `review_results.py` independently reads outputs,
source/product hashes and source-HDI identity. PowerShell commands are recorded
as structured argument arrays. An initial collector failed because an enclosing
JavaScript string consumed a backslash; the checked-in collector now uses
`[char]92/[char]47`, and final Windows readback passes. That failure is a host
verification-script issue, not target evidence.

Replay the checked-in scene verifier with `--target`, `--decoded-dir`, `--exe`
and a fresh `--output-dir`; use `verify_registration_join_windows.ps1` with the
current executable directory, HDI/font, v1299 graphics reference, manifest and
fresh output. Existing score/menu/graphics verifier commands retain their
original references. Final closure uses `scripts/ci.py` and `git diff --check`.
No historical exact/unit/function acceptance changes. Next implement the actual
MAIN Bomb, hit/death/lives/game-over/Continue owners, then Extra/HUD/OP auxiliary
flows/audio/config and full Linux/Windows route/performance acceptance.
