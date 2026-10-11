# TH04 native branch handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

Updated 2026-10-12. The full reconstruction/native goal stays active. DOS main
indexes all four bundled demos in complete compared state/video regions;
scanout, ordinary Boss/death/process and full native pairing remain open.
Historical exactness remains separate; target canonicality is candidate-local-attested.

Updated 2026-10-12. Reconstruction and native development remain active.
v1401 connects OP startup in the native FrontEnd to the independent unsigned
IRQ counter/raster clock. Ordinary frame waits clear Count1 before waiting;
Logo inherits Count1 and clears it after passing. Inactive BGM executes the
frame_delay(0) clear; active PMD is serviced at resident timer deadlines inside
an elapsed admission, without adding a logical refresh. Resource/drawing work
advances the same clock. OP process entry clears counts while preserving raster
phase and cadence accumulator. The default adapter uses ideal24kHz raster
edges with zero CPU/command/ISR latency; it does not fit captured elapsed times.

Original OP decoded DA1:002B(21bytes), DA1:0370(49bytes), A74:16DD(25bytes)
and 0000:25C6 IRQ prefix are re-attested from the pinned payload. Frozen complete
v1397 CPU24000/36000 witnesses retain first active Logo Count1=104/100 and zero
counted IRQ progress; BGM-off clears10->0, then first Logo waits1->2. These
are reused original runtime observations, not fresh emulator runs. The new
native tests reject compiled clear-before-Logo, missing zero fallback and
once-per-refresh PMD mutants. Elapsed batching and fractional PMD deadlines
pass; timer deadlines are checked on three boards at three frequencies.

Native producer512/60cf4491 is frozen. A complete cold GNU build passes70
CTests; optimized UBSan builds9 programs and passes6 selected contracts.
Original legacy startup control15 fixtures executes at loads1000/2000;
GNU/UBSan retain identical scripted-wait event/state traces. This legacy adapter
is separate from timed FrontEnd acceptance. Actual muted frontend matrix passes
132 configuration/restart cases (three PMD profiles, two phases, two compilers,
11 cases each), including six fixture GameOver/MAINE/freshOP paths. These finite
STD fixtures are not new natural six-stage routes.

Eight actual full startup/fourDemo/freshOP captures pass direct original15988
selected-state comparisons each. GNU/UBSan match all129 output hashes per
profile. With PMD enabled only startup-events.txt and text-refreshes.txt differ
from frozen v1399; the other127 outputs, including indexed/RGB/text samples,
shake and splash states, agree. No-driver captures retain all129 baseline files.
No full original picture, physical scanout or elapsed-time equality is claimed.

Root DOS source is unchanged at product fingerprint a34c1357; v1400 retains
its three108-case linked lifecycle comparisons and four-product/Demo proof.
Historical exactness is unchanged; canonicality remains candidate-local-attested.

Replay index: .analysis/reconstruction/probes/native-startup-waits-v1401/
(DOS root) and .analysis/port64/native-startup-waits-v1401/ (native worktree).
Use build.py/validate.py in a fresh namespace, with the frozen source and actual
HDI/font/ROM pins. original-witness.json binds unchanged v1397 ownership;
original-legacy-v1 is the newly executed scripted-wait corpus. check_parent.py
verifies immutable v1399/v1400 archives and closure separately from current
source; do not restamp their strict live-source readers. Restore narrowly with
verify_retention.py --restore --prefix; all proofs/source/selected executables
stay retained. Cleanup recovery caveat: the first deletion stopped at a missing compiler
object. All archive blobs had passed CRC/SHA and temporary readback, but the
full original path/mtime journal had not been persisted before deletion.
Receipt-pinned Demo/program contents were recovered; regenerated files have
new filesystem attributes. The final journal is written before deletion and
supports full current-path metadata recovery. 511 auxiliary blobs retain
content SHA/size without original path/mtime metadata. They remain in the final
content union; compiler intermediates can be cold-regenerated. Failed scripts
and logs, cleanup-recovery.json and the complete blob union are retained.
Concurrent source commits/motion work were observed during this interval;
causation of the object disappearance is unproved. Avoid overlapping writers.

Archive 26.28MiB; net cleanup 817.00MiB before post-CI caches.

Final isolated-checkout CI passes root451/native345, plus tracking and diff
checks. Borrowed pinned targets pass identity/format checks; private Ghidra
project replay skips because those isolated checkouts have no project. Source
and runtime proof identities remain separately pinned. Source-backed review CI
caches reclaim 16.32MiB separately, for 833.32MiB net this batch;
review worktrees are temporary and their tracked document state is preserved.

Next model default resource/graphics/CPU work and validate timed startup
boundaries against independent original IRQ/PMD observations. Other scenes
retain refresh adapters. Full pictures, Boss/death/process parity, a second
emulator, physical31kHz/scanout and Windows input/audio remain open. Runs use
CPU1/nice19, one serial writer, SDL dummy and mute; no Windows focus or host
keys/audio device. Goal stays active.

Prior demo/point-number/presentation experiments are indexed in
[demo evidence](port64/evidence/demo.md) and their immutable private receipts.
Historical producer502/v1376 and consumer505/v1377 keep their original identities.
Earlier ordinary GNU Reimu A Normal/Lunatic/Extra clear/save/restart routes and
dense slowdown observations retain their v1356 producer; see
[host-window evidence](port64/evidence/host-window.md). The prior UBSan Normal
clear remains revoked (mask0x19 is a sentinel), and the v1360 route and first
late Bomb probe remain failed. Require mask<4 plus the selected shot bit.

## Comparison priority for the next agent

The user's primary comparison is **original Japanese DOS versus reconstructed
DOS**, both through the PC-98 game route. Native x64 must also preserve gameplay
state and effects. Native-host equality and successful native clears do not
replace either comparison. Start with the four bundled demos, then bounded
recorded ordinary play; compare score, consumed input, RNG and actor state at
the same logical boundary, followed by VRAM/palette/effects and process/save
transitions. See [paired demo evidence](port64/evidence/demo.md).

TH08 is a read-only workflow reference, not TH04 evidence. Its active worktree
is dirty; do not edit it, run its builds, change its database or launch its game.
Complete trace/end/input-consumption guards and first-divergence diagnostics
are the useful parts to adapt. Retained DOS demos accept complete selected scalar/pool/video comparisons.
Retained native producers accept selected scalar/RNG/count fields and nine
complete pools. v1385 preserves the six parent trace/save hashes and 40 entire
index/TRAM samples; whole pictures, original display epoch and broader
gameplay/process routes remain open.

## Replay and finish

```sh
python3 scripts/preflight.py
python3 scripts/ci.py
git diff --check
```

Use [status](PORT64.md), [host-window evidence](port64/evidence/host-window.md)
and [retention](ANALYSIS_RETENTION.md). Source/program/profile archives retain
producer identities; restore into fresh paths. One Borland/Wine writer at a
time. Never open an audio backend/device in these validations.
