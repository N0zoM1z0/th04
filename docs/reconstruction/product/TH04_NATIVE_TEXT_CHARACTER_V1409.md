# Ordinary text character writers

## Combined DOS text and VSync source (v1411)

The current DOS source includes both the mutable text-segment recovery below
and the installed-owner VSync wait from v1408. Its 1,425-file fingerprint is
`82ade79057e0fd632f8e6c3437d136bd0e805481ba41f41b650efae19f7b87b7`.
A serial rebuild reuses 191/193 MAIN C++ objects, 162/165 OP objects and
136/139 MAINE objects after validating their cached inputs. Changed source is
compiled freshly; all links, IRQ audits and MAIN bullet tables pass.
MAIN/OP/MAINE products are 199,617 / 79,534 / 72,408 bytes.

The combined products pass the same 3,156 ordinary-text and 2,656 Gaiji
memory/write/ABI comparisons. All four complete ordinary-text bodies retain
their original MAIN match after the single text-variable operand mapping.
VSync passes 176 controls per artifact, including 24 actual ISR/IRET injections
and eight midwait owner changes in each. The START/IRQ/END lifecycle passes
108 controls per artifact. These checks execute the linked bodies at both
loads; no game campaign is needed for this integration.

The text-only 451a46f7 and wait-only d9383fa5 producers remain frozen.
Their 776 and 858 closed-file hashes pass independently. Their predecessor
failures and Demo results retain their original producer identities. The
combined wait is still a 49-byte compiled consumer of the original 38-byte
contract; historical authored exact remains 661/663.

Private replay index from the root repository:
`.analysis/worktrees/dos-text-vsync-join-v1411/.analysis/reconstruction/probes/dos-text-vsync-join-v1411/`.
`commands.json` retains the eleven comparison commands. `controls.json` binds
the current source archive, products/MAPs, three wait OMFs, original inputs,
oracle sources and complete transcripts. `verify_closure.py` checks those
identities, all memory/write streams, wait/lifecycle rows and both frozen
source archives. Archived compiler inputs can be restored with
`verify_retention.py --restore --prefix <owned path>`. Retirement reclaims
33.45 MiB net from 8,721 owned cache paths; original proof identities
and the three selected wait OMFs remain live.

## Frozen DOS mutable text segment (v1410)

`src/shared/runtime/text_putca_large.asm` and
`src/main/hardware/text_putsa.asm` now load the shared `_TextVramSeg` word.
Its C++ owner remains in `gaiji_text.cpp`, initialized to A000h. Both functions
read it before any far-string DS change. Their conversion, store order and
far Pascal cleanup stay intact.

A fresh serial build compiles all 360/165/139 MAIN/OP/MAINE objects. All links,
IRQ audits and MAIN bullet tables pass. Product sizes remain 199,585 / 79,502 /
72,376 bytes. The 1,425-file input fingerprint is
`451a46f7ee569bfe9c55c8f65fd8dbcb4cb966eb84c3a0439c67ebe106b09209`.

The complete character function is 87 bytes in each product; MAIN's string
function is 114 bytes. Each matches the original MAIN extent after rewriting
only the WORD operand at byte 21 from original DGROUP:0768 to its linked
`_TextVramSeg` offset. Neither extent contains a loader relocation. This is a
complete mapped code comparison; historical authored exact stays 661/663.
OP/MAINE use the shared MAIN character contract here, rather than a claim of
separate original OP/MAINE text-function observations.

`scripts/runtime/verify_dos_text_character.py` executes actual original and
linked bodies. MAIN passes all 840 fixtures at loads 1000/3333: 1,680 complete
80000h..DFFFFh memory, ordered WORD write and far-call state comparisons.
OP and MAINE each pass 369 character fixtures at both loads, for another
1,476 comparisons. The 3,156 comparisons cover coordinates, attributes,
alternate text bases, WORD characters, NUL, malformed pairs and long strings.
Existing text Gaiji retains all 2,656 original MAIN/MAINE comparisons.

The string fixture uses 6500:0000 RAM, beyond each loaded image and below the
return trampoline/stack. DF is clear and a second zero follows the C terminator.
Fresh original execution with this pointer agrees with every retained original
record. The first fixture rejected a buffer inside MAIN's load image; its
source and partial output remain retained. An initial MAINE regression lacked
its decoded-original input; the existing hash-attested input was linked into
the isolated tree before the successful replay.

The compiled v1407 MAIN control differs in all 80 alternate-base fixtures.
All 80 have a different return ES; final memory differs in 0/8/16/24 bytes.
The zero-memory cases still expose the wrong segment through ES. The reader
checks these failures and both sides' complete writes.

Replay index in the root repository:
`.analysis/worktrees/dos-text-character-v1410/.analysis/reconstruction/probes/dos-text-character-v1410/`.
Selected products and MAPs remain in that tree's `.analysis/build/` and producer
folders. The source freeze and complete compressed transcripts are retained.
CI passes 451 tests. Retirement archives 3,572 owned paths / 1,438 blobs and
removes 547 source-backed Python caches, reclaiming 21.14 MiB net. Gzip CRC,
every blob, temporary mode/nsmtime restoration and 778 protected files pass.
The closure reader verifies full current transcripts and 30 frozen DOS files.

```sh
python3 scripts/runtime/verify_dos_text_character.py --artifact main \
  --exe PRIVATE_MAIN_EXE --map PRIVATE_MAIN_MAP \
  --reference RETAINED_V1409_DRAFT_ORIGINAL --output FRESH_OUTPUT
```

Use `--artifact op` or `maine` to check only their shared character consumer.
Use `--diagnostic --alternate-bases-only` for the old compiled control.
Continue the remaining hardware/native function owners before long game runs.

## Recovered native source (v1409)

Native commit 328585f replaces `TextPlane::put_ank()` with
`put_character()`, accepting the original complete WORD input. A zero high
byte writes one ANK cell. High bytes below 80h supply JIS directly; higher
values use the original Shift-JIS conversion, preserving byte and WORD carry.
Each glyph half is preceded by its attribute store.

`put_sjis()` consumes the original byte ranges: 81h..9Fh and E0h..FFh are
lead bytes. A zero trail participates in conversion; a zero read as the next
lead terminates the string. All glyphs are written before filling attributes
from the wrapped WORD end-minus-start count. Both writers use the mutable
text base and WORD row/column addresses, preserving spill and alias writes.
The shared sparse-page owner keeps normal frame copies near 8 KiB.

The actual HUD initializer, Game Over renderer and frontend use the recovered
character writer. This is typed C++ shared by the native consumers.

## Original and compiler evidence

Pinned Japanese MAIN has 156,258 bytes and packed SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The ordinary writers are 0000:229E (87 bytes) and 0000:22F6 (114 bytes);
both read `TextVramSeg` at DGROUP 2134:0768. Their attested instructions are
retained under `.analysis/reconstruction/probes/native-sjis-text-v1409/`.
The native comparison reuses `scripts/runtime/verify_dos_text_gaiji.py` to
execute the actual original bodies with their far ABI and relocation.

All 65,536 WORD characters and 65,536 two-byte strings agree on the complete
8000-byte visible banks at X20/Y10, load 1000. Attributes cover all WORD values.
A separate 840-case corpus compares the complete seeded 80000h..DFFFFh
memory window at loads 1000/3333: 1,680 comparisons. It covers coordinate
edges, alternate text bases, NUL and malformed pairs, and long ANK/Kanji
strings through WORD offset and attribute-count wrap. The string adapter
supplies DF clear and a second zero after the C terminator for dangling leads.
Guest string/output aliasing and physical scanout are outside this corpus.

Cold GNU and optimized UBSan/bounds reproduce all results. The previous
Gaiji owner retains 2,656 original comparisons. The real frontend and six
selected programs build; six component contracts and native CI 345 pass.
The compiled predecessor rejects edge, kana, bad-trail and 4,097-character
inputs, differing in 4/4/8/8,386 physical bytes. The last rejected input has
equal partial visible banks, so the proof retains full memory and exit status.

Producer 526/3e7d5e33, ten selected programs, full compressed transcripts,
source archives and the closure reader remain in the native worktree:
`.analysis/worktrees/port-motion-v1402/.analysis/port64/native-sjis-text-v1409/`.
The reader replays every original write and checks current outputs plus the
780 protected frozen v1408 files. Verified retirement reclaims 14.50 MiB net
from 250 compiler-cache paths and 515 source-backed Python caches.

```sh
python3 .analysis/worktrees/port-motion-v1402/.analysis/port64/native-sjis-text-v1409/verify_closure.py
```

## Remaining function work

The ordinary DOS text references and installed-owner VSync wait are combined
in v1411 above. Continue native scene waits and other hardware adapters.
The full reconstruction/native goal remains active.

## Joined native palette waits and text writers (v1412)

The native merge retains both parents: ordinary WORD/Shift-JIS and Gaiji text
producer `328585f`, and palette wait producer `f2a51e2`. Cold producer
528/768091dc builds all 79 programs and passes all 77 CTests under both GNU
Release and optimized UBSan/bounds. The earlier selected UBSan subset is
historical evidence; this producer checks the complete graph.

Both compilers pass 32 original OP 0000:2648 wait controls at loads 1000/3333,
432 raster/cadence vectors (1,296 waits), 2,656 MAIN/MAINE Gaiji comparisons,
all 65,536 WORD characters and 65,536 two-byte inputs, and 1,680 complete
ordinary-text memory controls. Original Gaiji entries are MAIN 0000:1B0C/1B50
and MAINE 0000:0FC4/1008; ordinary entries are MAIN 0000:229E/22F6.
Retained original transcripts keep their target/helper pins and are read in
full; their receipts are not reassigned to the new native source.

Actual old `328585f` startup source fails the Count1-clear check (expected
exit 1). Eight muted SDL dummy routes (GNU/UBSan × none/pmd/pmdb2/pmd86)
complete startup, four demos and fresh OP. Each retains all 129 prior output
hashes and passes 15,988 original selected-state boundaries. GNU/UBSan output
sets agree. This remains scoped runtime agreement, with no exact, complete
picture, physical CPU/IRQ timing or Windows acceptance claim.

Private replay: `.analysis/reconstruction/probes/native-wait-text-v1412/`;
producer: `.analysis/worktrees/native-wait-text-v1412/.analysis/port64/native-wait-text-v1412/`.
`focused.json` records commands. `verify_retention.py --restore --prefix`
restores owned archived paths; retirement reclaims 508.31 MiB net.
Source, selected programs, full comparison streams, receipts and the real
predecessor remain. Continue bounded native scene wait/hardware recovery;
broader Boss/death/process routes, complete pictures and Windows remain open.
