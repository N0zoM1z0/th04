# OP and MAINE sound scene ownership

v1328, 2026-10-09. `sound_scenes.cpp` owns one sound runtime per OP, MAIN or
MAINE process generation. Actual menu, Scores, Music Room, cutscene, Staff
Roll and registration events reach that runtime. Completed MAIN refreshes
retain their old runtime until pending IRQ time is drained. No launch opens
an audio device; PMD/MMD capabilities still default to absent.

## Target evidence and adapters

Pinned original Japanese targets remain `candidate-local-attested`:

| Artifact | Size | SHA-256 |
| --- | --- | --- |
| OP | 42290 | `8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f` |
| MAIN | 156258 | `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b` |
| MAINE | 38035 | `670de6ba907a2edbc1592de810acd92e5b89541d3dc35b70210171166d1713f8` |

Fresh preflight and root OP/MAINE Ghidra MZ/header/entry/relocation/load/sample
checks pass before raw target work. Private copies of those receipts are in
`.analysis/port64/sound-scenes-v1328/`. A database is a target view, not an
independent Oracle; raw instructions below execute with Unicorn at loads
1000 and 2000.

Original OP options `Code 0A74:0912..0C1D` and vertical navigation
`06E8..0755` execute for 216 BGM/SE option combinations, rows and input masks.
The options renderer is a guarded adapter; sound callees record requests and
perform their attested resident writes. SE editing is deferred. Restarting
BGM stops, determines modes, loads OP music and plays, without reloading EFS.
The actual native options controller executes these same operations.

Original MAINE `_main`, `Code 0A05:00B2..0241`, executes for 32 unique
character/rank/end configurations at each load. Other children and process
transfer are guarded adapters. Mode determination runs, and an unexpected
SE resource load rejects. Fresh native MAINE has no effects loaded; it does
not inherit MAIN's MIKO.EFS. A source-only variant that reloads EFS in MAINE
fails with `fresh MAINE must not borrow MAIN effects`; source, command,
compiler/library/output digests and rejection receipt remain privately.

Original MAIN SE reset/play/update at `Shared 130E:07C6/07D2/080C` and MAINE
at `Shared 0CC7:0924/0930/096A` independently check their local controller
tuples. For full control-state snapshots, the original OP sound controller
is a representative Oracle initialized from each scene's explicit state.
This does not establish full library equivalence across the three artifacts.
Beeper calls, resident replies and initialization are explicit adapters;
physical driver initialization/finish and hardware timing remain unverified.

## Joined native behavior

Fresh OP configures modes and loads MIKO effects. Its post-logo title entry
stops/loads/plays OP music; returning from a demo skips that restart. Original
logo/startup audio ordering remains unfinished. Main/options/character/shot
forced SE, BGM restart, retained Scores and both Music Room visits use the
same OP runtime. Cached repaint advances neither actions nor IRQ time.

MAIN keeps its existing ordered SE/PCM consumer. On actual MAIN completion,
the pending runtime remains alive through its completed refresh, then MAINE
gets a new generation and empty EFS. Normal Ending/Staff Roll, score-only
Quit, Extra congratulations/verdict and registration route their existing
sound/song events. Cutscene forced SE uses reset/play/immediate-update;
immediate-update does not flush a pending refresh wait. Registration sound
events are BGM commands. Verdict `_UDE.TXT` is commentary text, not a cutscene
script, and receives no invented script/audio observer. Physical registration
save stays at writer-close; final MAINE fade precedes exec into fresh OP and
the next MAIN generation.

Measure requests are recorded with their original goal and fallback. The
absent PMD/MMD backend supplies no synthetic measure progress. Real driver
measure queries and PMD/OPN synthesis are still required for complete audio.

## Verification and replay

GNU and optimized UBSan each execute the original CPU checks anew: 216 OP
option cases, 32 MAINE entry cases and 8,834 control snapshots at two loads.
They agree on all 1,150 emitted files, including 134 BMPs and physical host
scores/config. Four menu controls exercise both characters/repaint policies,
deferred SE/BGM restart, two Music Room visits, Scores, seeded registration,
fresh OP and second MAIN. Twenty-four successful and four failed score-only
routes also carry the full scene trace. Seeded registration skips preceding
natural MAIN/Ending gameplay.

Both Linux hosts retain the MAIN regression: twelve ordinary frontend cases,
six unique streams and 3,574,464 PCM samples against the original OP beeper
representative plus original MAIN controller. Twenty-four Ending routes
agree with independent Ending/Staff/verdict/congratulations galleries and
fresh verdict CPU checks. Eight Extra routes agree on complete outputs and
original outgoing MAIN/MAINE control order. These long routes explicitly use
actor control with hit consumption disabled. The legacy Ending receipt field
`natural_routes` counts these controls; it does not accept natural survival.

384 registered sources bind 150 AMD64 programs, 50 per GNU/UBSan/MinGW cache.
All 49 CTests pass on both Linux hosts. MinGW is a cross-build check; current
Windows execution fails before PowerShell with WSL `UtilBindVsockAnyPort`.
Shared Git metadata rejects staging with a read-only index; complete pending
public-source recovery is retained, with planned English commits.

Both checkouts finish with preflight, `scripts/ci.py` and `git diff --check`
passing. The terminal output cleanup shares 6,357 identical files after full
byte/hash checks and retires the rejected mutant program: 1,508,634,624
allocated bytes reclaimed, 13,175 protected hashes unchanged at that boundary.
After CI, 1,013 source-backed Python caches reclaim another 17,068,032 bytes.
Current caches/products and unique replay evidence remain.

From the native checkout, use fresh output directories:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_sound_scenes.py \
  --exe .analysis/port64/linux-live-v1251/th04-port64 \
  --op ../../targets/th04/op.exe --main ../../targets/th04/main.exe \
  --maine ../../targets/th04/maine.exe \
  --op-decoded ../../port64/op-unlock-v1317/decoded-original \
  --maine-decoded ../../port64/maine-ending-v1291/decoded-original \
  --hdi ../../runtime/images/zun.hdi --font /path/to/FREECG98.bmp \
  --output .analysis/port64/sound-scenes-new/original-linux
# Repeat with the UBSan executable and --reference-dir pointing to that producer.
```

Replay commands, source/product manifests, private target receipts, regression
receipts, mutant rejection, cleanup and complete pending recovery live in
`.analysis/port64/sound-scenes-v1328/`. Accepted old producers keep their own
manifests. Use fresh outputs after immutable hardlink compaction. Historical
DOS unit/decoded-function acceptance is unchanged. Complete natural ordinary
and Extra routes, current Windows save/restart, dense Lunatic timing, PMD/FM
and full startup audio remain separate TODOs.
