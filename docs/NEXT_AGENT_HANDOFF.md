# TH04 current handoff

Updated 2026-10-17. The complete maintained DOS four-product and native x64
fidelity goals remain active. Code/docs are English. Use one low-priority CPU
(`taskset -c 1 nice -n 19`), serialize Borland/Wine builds and launch muted/headless.
The user uses Windows; do not open GUI windows, change focus or inject host keys.
Clean unused intermediates during each batch and after consumers finish.

## Input intent and latch contract (v1468)

The original Pause control now explains the rejected frame-return scheduler:
Shot is queued at a completed-frame seam, but the next latch occurs0.009889ms
later, before DOSBox-X's0.572917ms UART delivery. BIOSbitmap remains clear at
that latch and becomes pressed before the following frame. These are pinned
emulator observations, not a PC-98 hardware timing claim. Derived PIC FullIndex
can move backward at its millisecond write-watch transition; preserve those rows.
Batching Shot with the real confirmation-release edge passes all400 requested
loop words. This remains a private bounded control, not a promoted UI scheduler.

Public sparse input now supports V2: each row declares `frame physical expected`.
V1 keeps its reserved-zero third column and requires latch==physical. V2 keeps
physical keys separate from an explicit expected unsigned latch; every actual
read still must match. V2 permits the six ordinary buttons plus physical Escape.
It never writes expected words into the guest. Record every physical/readback
difference. Freeze expectations from an original golden before a candidate run.

Five actual short captures validate the contract. Current V1 reproduces all
711787 parent raw bytes. Declared V2 Pause400 has physicalShot32/expected0 at81
and reproduces all764 observed raw records. Changing only expected0 to32 rejects
actual0 at81. The failed run stays incomplete; ownMZ/CPU/RAM/font/video and
physical API guards validate. Five parser tests also pass.

Receipts: `.analysis/reconstruction/probes/pause-latch-v1468`.
`stage3-v2-inputs.txt` preserves all8000 physical requests and binds expected
latches to the existing original8000 golden;7835 is explicitly32/8192.
This fixture is prepared, not a new source-DOS run. The legacy paired source-DOS
transport/reader still accepts V1 only. Do not feed V2 to it yet. Keep the
original8000 golden and native566/4787233c programs; no producer rebuild is needed.

## Verified frontier

Original/source-DOS paired MAIN remains at Stage3 completed4000 (v1462).
Original/native now has a complete 8000-update Stage3 observation in
`.analysis/runtime/candidates/dos-stage3-wait-v1467-observed-inputs`.
The enclosing original run completes in 770.517s with 9837/10394/8000 stage loops;
its own1136-relocated MAIN,CPU/RAM,physical edges and frozen sources validate.
Target provenance remains `candidate-local-attested`.

This diagnostic records actual input words separately from requested keys.
Exactly one loop differs:7835 reads Enter8192 while Shot32 was requested.
The literal post-dialogue player entry at MAIN0AAF:5FCF, own near caller00F1
and return00F4 independently bind actor7835's8192. Native consumes those
literal original words plus the declared dialogue7834 cue. This does not prove
requested-key delivery or natural UI/IRQ timing. The default public sampler
still rejects a requested/readback mismatch.

Current native source closure: 566 files,
`4787233c1074df806c6dfdef6697030b8c2885ecf2911bfaf2fb7df11c33ba7e`.
Fresh GNU 87 programs/83 CTests and optimized UBSan 2 programs/session pass.
Both real frontends agree on all 79 outputs. All8001 nine-pool snapshots,
8010 stable-state records and consumed inputs match. Keep 712 volatile
post-actor input differences separate. Nine whole 640x400 RGB pictures,
8000 active TRAM bytes and48 DAC channels/raw tone match at Stage3
1/4000/6000/7834/7835/7873/7900/7901/8000. Earlier sampled results are
historical observations; continuous display and full campaigns are unproved.

## Repaired owners and rejected approaches

Original7834 has scroll speed0/back page1 with active STD13A9:4341 and pending wave7900.
A stopped CPU at130E:00E3 and typed mixed stack prove a held-Shot release wait
inside dialogue. Native Stage3 now omits the extra STD-EOF predicate and keeps
pending waves during Elly. Other stage guards retain separate ownership.

A palette-bearing dialogue BFNT load updates the player's live palette14.
The former cache incorrectly keptAA instead of the observed post-dialogue80;
three DAC channels failed despite matching sampled RGB/TRAM. The callback now
uses the decoded asset palette, with no target-color assignment.

The old frame8000 picture failed by 105 pixels. Read-only drawing logs and
original ring snapshots localize two cells at DS4D40 to a missing enemy tile
write. Original MAIN13A9:2042..2054 calls0AAF:0B92 with a raw VRAM offset;
independent unmodified-unit execution distinguishes72/image0 from74/image25.
Native handles opcode8F's event and retains background-prefix ring inputs
before actor writes, including the later scroll-tail copies. The old failure
and all earlier raw graphics-index/GDC differences remain recorded.

Only the proven Frame/Score watch reuse is promoted publicly. A400-frame
original pressure control keeps four host watches and reproduces all711787
raw bytes. Proposed UI frame-return API scheduling failed both real Pause
controls at81 (actual0/requested32) and was reverted. V2/V3 controlled stops,
V4's requested-input rejection and the original wait capture remain incomplete.
Pixel-only, DAC-only and consumed-input-only rebased controls reject independently.

## Replay and storage

Receipts/readers/source snapshots: `.analysis/reconstruction/probes/stage3-wait-v1467`.
Current cold programs/link inputs:
`.analysis/native/port64-recovery-v1445/.analysis/port64/stage3-tiles-v1467-final`.
Retain main/session executables,main/audio/core/ymfm inputs,compressed witnesses,
source capsules and every parent backing. Disposable build objects/tests have
been removed after checks. Completed native payloads are compressed and
deduplicated;55 closed capture aliases restore exact SHA/size/mode/nsmtime and
independent readers reproduce before retirement. Use fresh build directories.

```sh
taskset -c 1 nice -n 19 python3 .analysis/reconstruction/probes/stage3-wait-v1467/recover.py
python3 scripts/preflight.py
python3 scripts/ci.py
git diff --check
```

`recover.py --restore --path EXACT` restores one explicit journal-relative
owned alias. Verify and retire it after use; avoid bulk expansion. The next
journal must merge retention,all finish.late_protected identities and finish.

## Next work and limits

Keep the recorded original8000 golden; do not restart its long prefix.
Extend the legacy paired source-DOS transport and independent route reader to
V2 without weakening V1. Validate a cheap original/source Micro, then run only
the reconstructed-DOS8000 extension against the frozen original golden and
independently verify actual consumed inputs. Include a literal post-dialogue
source player-entry CPU/RAM witness bound to its own MAP/MZ and the retained
original player witness; the earlier loop latch is a different observation. Reuse the source/layout/native pointers in the
[focused differential note](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md).
Raw post-actor keys,raw graphics indices/GDC clocks,natural IRQ/scanout timing,
NP2/Windows and complete campaigns remain open. No artifact or unit becomes exact.
Commit English messages with `gpt-6.1-sol: ...`;push main and native
`HEAD:port/modern-64`. Both global goals stay active.
