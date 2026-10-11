# Native ordinary text character writers

## Recovered source

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

## Next DOS source recovery

`src/shared/runtime/text_putca_large.asm` and
`src/main/hardware/text_putsa.asm` still add a fixed A000h text segment.
Bind both to the maintained `TextVramSeg` owner, preserve the existing far
Pascal ABI and conversion/store order, then cold-build the affected product
and compare original instructions at both loads with alternate-base controls.
Historical authored exact remains 661/663. Continue source recovery before
long game campaigns; the VSync review uses its own separate frozen producer.
