# TH04 native branch handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

Updated 2026-10-11. The full reconstruction/native goal stays active. DOS main
indexes all four bundled demos in complete compared state/video regions;
scanout, ordinary Boss/death/process and full native pairing remain open.
Historical exactness remains separate; target canonicality is candidate-local-attested.

v1385 restores MAIN text blink from an independent persistent display clock.
All 15,984 original master/slave GDC triples agree at rate32. Modulo128 deltas
include zero at Demo1/2 and Demo3/1968 and two at Demo3/1954,1963; the Demo
frame number cannot replace display refreshes. Original absolute epoch is open.

Native mask0x02 blanks the glyph before reverse0x04. 80 complete controlled
text layers and eight attribute controls match the unchanged pinned DOSBox-X
emitter; both RGB/ARGB APIs agree. Explicit black-graphics and reconstructed
BMP/GAMEFT adapters do not attest live CG RAM or physical scanout.

The clock persists through OP, waits and MAIN replacement. Headless admission
includes slowdown; host source paths use monotonic elapsed time. All 15,988
native rows replay the unchanged GDC counter. Separate instrumented FrontEnd
logical/host-time/repaint/double-admission/backwards controls pass, retaining
all 127 ordinary capture hashes. Phase-inversion/per-Demo reset controls reject.
Captured-phase diagnostic mismatches grow from five to eight with the distinct
native epoch; phase agreement is not accepted. Other TextPlane callers
keep the visible default; physical Windows remains untested.

Four inputs change among 509 (manifest a47f0496…). Fresh whole cold GNU has
71 programs and 69 passing CTests; optimized UBSan cold-builds game/trace/shake.
Actual muted SDL-dummy OP→four demos→OP has 127 identical variant files.
All 40 entire indices/TRAM and six parent trace/save hashes stay unchanged;
prior full-pool producers retain their identities. Blink changes 2,780
sampled RGB pixels. Full captured-phase raw RGB has 12/40 zeros; explicit
DAC diagnostics have 32/40 zeros. Native-phase projection has 40/40
zeros, without raw/whole-picture/original-phase/scanout acceptance.

Next capture live CG RAM and text-scroll/CRT surfaces, recover original
absolute refresh/scanout timing, and extend paired ordinary Boss/death/process
routes. Full fidelity remains active. Candidate-local-attested provenance and
deferred historical carpet/checkerboard exactness remain separate.

Recipes: DOS-root .analysis/reconstruction/probes/native-blink-v1385/;
native receipts: .analysis/port64/native-blink-v1385/. First receipt-write type
error is retained; corrected v2 passes. Restore retired inputs before replay.
Frozen v1384 ba6eff48 cannot attest current a47f0496 source.

All jobs are terminal. Main 441/live Ghidra and native 345/target CI pass.
Lossless retirement checks pass for 1,280 complete files and 1,044
source-backed caches; 27,535 protected hashes and 509 source pins pass.
Net 334.5 MiB is reclaimed after the 15.6 MiB archive, before
journal cost. Programs, frozen sources, original references and both private
probe failures remain retained. From DOS root, restore before reader replay:

```sh
python3 .analysis/reconstruction/probes/native-blink-v1385/verify_retention.py --restore
```

Without --restore it checks all recoveries temporarily. Old proofs keep their
original source scopes; see ANALYSIS_RETENTION.md.

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
