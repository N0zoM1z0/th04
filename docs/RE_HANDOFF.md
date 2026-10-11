# TH04 native branch handoff

v1402 restores IATAN2's complete signed displacement behavior in native
`motion::angle_to()`, replacing the blanket -32768 rejection with original
signed magnitude comparison, low-byte lookup and DIV fault handling. All
184,908 original-instruction vectors agree, including 514 original faults.
See [core evidence](port64/evidence/core.md) and the scoped native receipt under
`.analysis/port64/native-motion-v1402/`. DOS source and historical exact counts
are unchanged. Continue function migration before long game campaigns.

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

The latest remote port/modern-64 is ce48946 and separately adds GRCG circle /
stage-line recovery. Its renderer changes are not part of this514-file verified
snapshot. This snapshot is published on review/startup-motion-join-v1403;
merge it only after selecting one writable source session and attesting the
combined producer. Both incoming histories are preserved. The older v1401
startup implementation itself already reached port/modern-64 through fffcc83.

v1403 integrates remote motion recovery a0b6149 with the independently
validated startup waits. Verified integration producer514/c2f8d689 is frozen;
CMake's new motion contract and its verifier are now both included in the
complete source manifest. Fresh GNU builds73 programs/71CTests; optimized
UBSan builds10 programs/7 contracts. Unchanged original MAIN0000:1DA8..1E13
and table2134:021E execute at load1000:184908 vectors per compiler agree,
including514 original DIV faults. Complete expanded comparison transcripts
match between GNU/UBSan. The compiled old blanket -32768 rejection fails.
This accepts the bounded corpus and explicit native fault surface; it is not
an exhaustive four-coordinate Cartesian product or historical byte exactness.

Eight fresh current startup/fourDemo/freshOP profiles each match original
selected state at15988 boundaries and every129 frozen v1401 output hashes.
Startup/IRQ code itself is unchanged. Physical timing, default resource/CPU
costs, full pictures and broader Boss/death/process remain open. Continue
bounded source recovery before long game campaigns. Windows GUI/focus/host
keys/audio opens remain excluded while the host is in use.

The original native push encountered a concurrent non-fast-forward remote
motion commit. Both histories were merged without force pushing. v1401 proofs
remain frozen at512/60cf4491, including its132 frontend fixture cases and
70GNU/6UBSan checks; their strict live-source reader correctly rejects current
source. A new reader verifies its archive/1150-file closure independently.
No old receipt was edited to claim the new producer. Root DOS source stays
unchanged at a34c1357; historical exact counts/canonicality are unchanged.

Current replay index: .analysis/reconstruction/probes/native-startup-motion-join-v1403/
(DOS root); native .analysis/port64/native-startup-motion-join-v1403/.
Use build.py, validate.py and verify_retention.py in a fresh namespace;
check_frozen_parent.py reads old proofs and the expected strict-reader rejection.
All current source/program/vector/capture inputs are pinned. The read-only
original MZ target, complete1136 relocation topology and two separate compiler
outputs remain distinct evidence. Runs are CPU1/nice19, serial and muted.

Additional owned cleanup 468.70MiB after 16.93MiB archive. Full current
path/hash/size/mode/nsmtime journal is persisted before any archive/deletion.
CRC/EOF, all blobs, every temporary metadata restore and protected proofs pass.
No prior producer is retired. The v1401 initial auxiliary-metadata caveat remains
explicit in retention notes; current v1403 paths have full recovery metadata.

Final current-tree CI passes root451/native345, tracking and diff checks.
Root's actual private target/database/Oracle mutations pass; native private DB
checks skip absent projects. Additional post-CI source-backed caches reclaim
16.52MiB. v1403 total net cleanup is
485.22MiB; disjoint v1401+v1403 retirement/caches total 1318.54MiB
(1.29GiB), excluding temporary review-worktree removal.

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
