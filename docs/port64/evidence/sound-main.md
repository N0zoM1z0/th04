# MAIN sound requests and muted beeper frontend

v1327, 2026-10-09. `sound_runtime.cpp` consumes ordered MAIN SE requests,
loads the real MIKO.EFS and advances offline beeper PCM without opening an
audio device. It joins player/shot/death/Bomb, item pickup/one-up, score extend,
enemy/midboss/shared boss event seams, dialogue forced SE and retained music
requests. PMD/MMD capability defaults to absent; an unavailable backend cannot
fabricate FM availability or measure progress. OP and MAINE sound consumers,
resident PMD/OPN synthesis, physical timing and natural full routes remain.

## Original and adapter evidence

Pinned MAIN is 156258 bytes, SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
Its MZ header is 6144 bytes with 1136 relocations. Fresh target preflight and
root MAIN Ghidra database/header/entry/relocation/load/sample attestation pass.
Provenance remains `candidate-local-attested`, not independently pristine.

Observed original MAIN code at relative `130E:07C6..0857` implements reset,
play and update using DATA `2134:08F4` (SE mode), `0914` (playing) and `0915`
(frame). Original instructions run at MZ loads 1000 and 2000; beeper calls and
interrupt replies are explicit consumer adapters. Both loads agree on all
six captured frontend action streams and 4200 post-refresh control states.
This validates the SE controller for these inputs, not every producer in a
complete original MAIN execution.

The raw original gameplay loop `0AAF:0098..0212` places page OUT A6/A4 and
`snd_se_update` (`01A3`) before the stage counter and score caller (`0204`).
Eighteen guarded CPU cases vary load, initial counter 0/999/65535 and SE
mode OFF/FM/BEEP. Other callees are explicit guarded seams; a score-emitter
adapter injects the next extend queue. Original loop bytes, counters, page
writes and SE update execute. Full original actors, score arithmetic, wait
hardware and physical page presentation are outside this loop claim.

Native MAIN emits requests immediately at each component boundary. Its
ordinary SE update occurs after completed render requests and before the
counter/score drain. Item collect queues extend 7 before pickup 11. A score
extend queues 7 after the ordinary update, leaving it for the next frame.
These counters and two genuine score extends are checked by CTest. A private
source-only variant moving the update after the counter rejects with
`item collect/extend/pickup/SE update order`; its source, compiler command,
output and digest remain after its executable is retired.

The frontend uses its existing 17730496 ns refresh period and scheduled
slowdown as an explicit deterministic clock adapter. Runtime flushes pending
IRQ time before the ordinary SE update; blocked Game Over/dialogue refreshes
advance IRQ only. Dialogue forced SE retains reset/play/update ordering.
Cached repaint dispatches no audio actions and advances no timer. An owner is
retained until the current refresh completes if a process handoff releases it.
This is not original beeper initialization/finish, wall-clock timing, physical
page timing or a tested all-scene resident driver lifecycle.

## Actual muted frontend checks

Two characters × shooting/Bomb/last-life Game Over and Continue × two repaint
policies = twelve 700-refresh ordinary frontend cases per Linux build. OP
options select BEEP using the actual reversed option direction; authored
finite STD contacts drive death. Game Over freezes the ordinary SE queue for
178 refreshes, continues IRQ time, then actually resumes MAIN. Repaints and
both repaint policies retain identical actions, control/IRQ states and PCM.

Six unique streams contain 3,574,464 PCM samples per host. GNU compares them
with an independently clocked reference executing the original **OP** beeper
parser/play/IRQ instructions plus the original MAIN controller. Optimized
UBSan consumes that immutable reference and re-attests its source/target/input
identity. This OP library is a representative independent beeper Oracle; it
does not establish original MAIN library equivalence. Sample rate 48000,
mode-3 digital square-wave phase and gain remain explicit host policies.
All launches use `--mute`; SDL initialization remains VIDEO/EVENTS only.

Replay from the native checkout (use fresh output paths):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_sound_join.py \
  --exe .analysis/port64/linux-live-v1251/th04-port64 \
  --target ../../targets/th04/main.exe --op ../../targets/th04/op.exe \
  --decoded ../../port64/op-unlock-v1317/decoded-original \
  --hdi ../../runtime/images/zun.hdi --font /path/to/FREECG98.bmp \
  --output .analysis/port64/sound-join-new/original-linux
# Use the optimized UBSan executable and --reference-dir above for its consumer.
ctest --test-dir .analysis/port64/linux-live-v1251 --output-on-failure
ctest --test-dir .analysis/port64/ubsan-live-v1251 --output-on-failure
```

Current private evidence is `.analysis/port64/sound-join-v1327/`: original
producer `original-linux-accepted`, consumer `caller-ubsan`, guarded-loop and
control histories, mutant, source/product profiles and readback/recovery.
379 registered sources bind 147 AMD64 programs (49 per cache); 48 CTests pass
per Linux host. Relative to v1326, 44 GNU and 40 UBSan programs retain their
bytes; four/eight affected programs change. All 48 previous MinGW products
relink; build/AMD64 checks do not establish actual Windows execution.

Owned terminal cleanup shares 27 full-byte/hash-equal PCM duplicates and
retires six failed-fixture PCM files plus one rejected mutant executable.
It reclaims 38,944,768 allocated bytes (about 37.1 MiB); 4232 protected hashes
are unchanged at that boundary. Source, original references, inputs and all
current products remain. Earlier cleanup numbers are separate observations.
Windows interop still fails before PowerShell with WSL vsock; Git staging
fails on the read-only shared worktree index. Complete pending public-source
recovery is retained; no commit/push, current Windows run or DOS exact
promotion is claimed.
