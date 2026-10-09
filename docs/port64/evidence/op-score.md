# OP saved-score reading and Extra availability

v1317 adds `op_score.*` and joins it to startup and every fresh OP. The process
opens the physical `GENSOU.SCR` after the preceding writer has closed, scans
both characters across five ranks, repairs rejected input at writer-close and
uses the observed flags for the title menu and character/shot selection.
All native launches use `--mute` without opening an audio backend.

## Independent target observations

Packed OP is 42,290 bytes, SHA-256
`8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f`.
The original decompressor executes at loads 1000/2000 and produces 69,028
bytes, SHA-256
`13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`,
with 804 relocation sites. Preflight and live OP Ghidra attestation pass.
Candidate-local-attested provenance remains a gap.

The instruction Oracle executes relative `0A74:1E3A..205D` (decode, encode,
recreate, dual-column load), `24A3..2556` (scan/clear-sprite requests), and
the complete `2FC8..32D0` character/shot menu at both relocated loads. Original
LCG instructions execute at relative `0000:204E..2077`. File-byte stores,
selection key polls, graphics/sound/resource consumers remain guarded adapters.
The menu's uninitialized previous-input stack byte is explicitly supplied zero.
Resident canaries and stack return/argument widths are checked.

Unlike MAINE's low-byte checksum, OP requires the complete first checksum WORD.
Failure leaves the second buffer untouched. The second checksum only uses its
low byte. Recreation writes ten separately encoded first buffers and calls
the two-column decoder after each write, transforming even the unwritten second
buffer. A failed rank stops scanning after recreation; previously accepted rank
flags and the accumulated global Extra flag survive within that OP process.
Successful loads sanitize cleared bytes greater than three to zero. Configured
rank is restored after scanning.

Global Extra ORs Normal, Hard, Lunatic and Extra, excluding Easy. Character/shot
availability only ORs Normal, Hard and Lunatic. An Extra-only clear therefore
opens the title choice while all four combinations remain locked. The original
menu still selects Marisa, then B on confirmation. The portable constructor's
former empty-mask exception and its old contract are superseded by this observed
behavior; no defensive replacement is invented.

## Physical host and process boundary

`FrontEnd::read_op_scores()` recreates `HostStore` from its directory for each
new OP and resets both score buffers/flags to the process's fresh state. It
consumes recorded file operations through the real host writer. A valid file
does not advance the OP LCG; missing or bad input recreates with twenty draws.
The OP menu frame seed and the per-process LCG remain separate owners.
The existing host policy treats an incomplete ten-section file as missing;
the component Oracle separately preserves original unchecked short-read/stale
buffer behavior. Initial repair failure now propagates before MAIN launch.

The physical join checks 34 original-produced inputs: all sixteen Normal masks,
Easy/Hard/Lunatic/Extra-only flags, invalid cleared bytes, first/second checksum
failure, failure after prior accepted ranks, missing/host-short and trailing
data. Each scene checks the full two work buffers, flags, rank, LCG, selection,
physical repair bytes and a separate frontend restart. Ordinary selection
remains available independently of the Extra mask.

Six explicitly seeded registration child scenes (both characters at Normal,
Hard and Lunatic) drive the real wait, letter, Esc, host writer-close and full
blackout. Fresh OP reads exactly the saved clear bit and starts the only unlocked
Extra combination through actual selection and ST06 resource installation.
A separate frontend restart repeats that result. Original OP independently
decodes all ten sections of each saved file. These are child-scene controls;
they do not establish natural full-game survival.

## Replay and acceptance limits

Use fresh directories. Completed references may be hardlinked and are immutable.

```sh
python3 port64/verify_op_score.py --target ../../targets/th04/op.exe \
  --decoded-dir ../../port64/op-unlock-v1317/decoded-original \
  --exe .analysis/port64/linux-live-v1251/th04-port64-op-score-contracts \
  --output-dir NEW
python3 port64/verify_op_score_join.py --target ../../targets/th04/op.exe \
  --decoded-dir ../../port64/op-unlock-v1317/decoded-original \
  --exe .analysis/port64/linux-live-v1251/th04-port64 \
  --hdi ../../runtime/images/zun.hdi --font-bmp SUPPLIED-FONT \
  --output-dir NEW
```

The 556-case instruction comparison covers codec/recreation, dual-column loads,
dirty work buffers, invalid/partial rank scans and full selection/cancel inputs.
A private source-only `rank<4` to `rank<5` availability mutant is rejected by
the original Extra-only menu case. Callback failures must propagate explicitly.
Native glyph/palette output is cross-host evidence; original whole-scene pixels,
DOS filesystem/timing/audio, actual Windows runtime, pristine provenance and
byte-exact DOS acceptance are outside this claim. Full HUD, OP score display,
Music Room, demo, audio/config persistence and complete natural routes remain.

Current final review: GNU/optimized UBSan each pass 39 contracts and agree on
280 OP frontend files/80BMPs,220 Quit-route files/134BMPs and 336 Extra-tail files/
312BMPs.304 previous Extra BMPs are unchanged;8 fresh OP title captures now
display the saved unlock. The GNU original/frontend producer manifest differs
only in correction of the superseded empty-mask contract. 117 other products
remain bit-identical; no receipt is restamped. 120 AMD64 products bind 327 sources.
Full original outgoingMAIN/MAINE caller order replays use the existing explicit
child/resource/timing/exec adapters. Final receipts and complete recovery live
under native `.analysis/port64/op-unlock-v1317/`.


## OP ranking viewer v1320

`op_ranking.*` now owns relative OP `0A74:2354..24A2`, including score
reload/render helpers at `205E..2353` and the original `0000:0622..06A2`
black-in/out loops. The first VBlank precedes the initial tone application;
speed1 takes18 refreshes. Left and right inspect the same sample even across
left black-in. Exit masks precede arrows; held arrows repeat. Exit restores
OP1 into page1, copies to page0, black-ins and waits for **all** keys to release
before STOP/load OP/PLAY. Sound requests are observed without an audio backend.

The renderer uses OP GAMEFT, SCNUM's ten16x16 numerals and HI_M's ten64x16
rank-label halves. Names start at8/320 with color7 for the highest row and2 for
others; shadows14 and stage foreground7 are retained. StageFF becomes EF;
single glyph0 still executes, unlike the string terminator. Highest score
BYTE minusA0 promotes to signed16-bit before division/remainder. Undefined
pattern indices are preserved as logical requests and explicitly rejected by
the graphics consumer, rather than normalized.

Original OP0000:2D5A..2F0B SUPER and3D8A..3EC6 string/single font kernels
execute at loads1000/2000. Actual self-modifying widths and GRCG writes use
supplied BFNT planar staging and GAMEFT CGROM adapters. Independent indexed
composition then compares both complete pages, palette and scalar RGB on640
refresh snapshots (819230720bytes); current GNU and optimized UBSan both agree.
PI decode and initial native title pages remain explicit dependencies. This
is not a complete original OP video capture or physical palette timing.

135 complete caller fixtures cover five initial ranks, held/combined arrows,
SHOT/OK/CANCEL, release, twenty RNG draws in missing/bad-file recreation,
retained decoded buffers/flags and checksum/short-read paths. Raw unbounded
name reads exposed in the first arbitrary-ciphertext probe cross from the
second196-byte section into adjacent DS globals. The native name consumer
rejects that unbounded range; positive recovery fixtures deliberately provide
a defined zero-key second buffer. The failed arbitrary-input trace and exception
remain under `caller-linux-debug/`; this policy is not claimed equivalent to
all original undefined reads. Pixel fixtures use valid pattern requests.

12 real options/Scores/menu/MAIN scenes per Linux host retain the OP process,
configured difficulty and unlock flags, reopen physical scores, restore the
selected title item and start ordinary MAIN after browsing.179 output files/
131BMPs agree across GNU/UBSan; GNU independently compares107 sampled BMPs.
A source-only change that polls again after left fade instead of testing the
retained RIGHT sample is rejected at trace line4748 (refresh74).556 previous
OP reader cases,34 physical restart+6 registration child controls, full retained
HUD and24 Game Over scenes regress. Current126 AMD64 products bind339 sources;
41 CTests pass per Linux host. Earlier original producer manifests and current
consumers remain separate, with executable identity/reference bytes checked.

Use fresh output directories:

```sh
python3 port64/verify_op_ranking.py --target ../../targets/th04/op.exe \
  --decoded-dir ../../port64/op-unlock-v1317/decoded-original \
  --exe .analysis/port64/linux-live-v1251/th04-port64-op-ranking-contracts \
  --output-dir NEW
python3 port64/verify_op_ranking_pixels.py --target ../../targets/th04/op.exe \
  --decoded-dir ../../port64/op-unlock-v1317/decoded-original \
  --exe .analysis/port64/linux-live-v1251/th04-port64-op-ranking-contracts \
  --hdi ../../runtime/images/zun.hdi --font-bmp SUPPLIED-FONT \
  --reference-dir CALLER-RESULT --output-dir NEW
python3 port64/verify_op_ranking_join.py --target ../../targets/th04/op.exe \
  --decoded-dir ../../port64/op-unlock-v1317/decoded-original \
  --exe .analysis/port64/linux-live-v1251/th04-port64 \
  --hdi ../../runtime/images/zun.hdi --font-bmp SUPPLIED-FONT \
  --pixel-reference-dir PIXEL-RESULT --output-dir NEW
```

Receipts/recovery live under `.analysis/port64/op-ranking-v1320/`.
The640-refresh stream is losslessly compressed; raw/decompressed hashes agree,
reclaiming792883200allocatedbytes. Earlier accepted hardlinks remain immutable.
Windows execution still fails before PowerShell under restricted WSL sockets;
Git index.lock is read-only, so commits/push remain pending with full recovery.
Music Room/demo/audio/config persistence and complete ordinary/Extra routes
remain; DOS acceptance is unchanged and all launches stay muted.
