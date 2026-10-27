# Portable audio profile and Stage 3 quiet passage — 2026-10-27

Historical profile/transport batch. The later [synthesis investigation](TH04_PORTABLE_AUDIO_FIDELITY.md) finds shared waveform defects and supersedes any general audio-quality conclusion; the bounded transport/profile observations below retain their original scope.

## Scope and diagnosis

The audio-profile baseline AMD64 executable is:
`2dfd38e8eafefde4f0f428633c6dc3c31c1dd1ca6ff1211bfedc8d6d37f2e4a2`.
The preceding BATs passed only `--audio`, so `main.cpp` selected its default
`pmd` / three-FM-channel YM2203 profile and `.M26` arrangements even when the
saved BGM option requested FM86. No OPNA ROM was packaged. This is a launch
configuration limitation, not a newly proved PMD decoder or 26K parity failure.

Both maintained BAT paths now explicitly select `--pmd-driver pmd86` and the
external `ym2608_adpcm_rom.bin`, enabling six FM channels, SSG and rhythm with
the `.M86` resources already supported by the executable. The invincible
launcher still patches only the owned process data byte; the no-death gate
and collision semantics do not change. The final WinMM transport correction
below produces a new executable identity. No mixer gains, compression, host
volume, Windows audio sessions or user save/configuration bytes are changed.
An explicit saved 26K BGM option remains a user choice; both existing delivery
profiles requested mode2 when inspected.

## Muted component observations

The same current core/chip archives are linked into a CPU-only Windows probe.
Five 40-second controls per profile cover separate ST00/ST01/ST02 starts,
ST00→boss→ST01→boss fades followed by ST02, and repeating FM sound effects for
the first six seconds of ST02 followed by release. They open no audio device.
Their PCM RMS measurements are signal statistics, not LUFS or physical speaker
measurements, and different arrangements are not expected to be byte-equal.

| First 40 seconds, stereo PCM RMS | Previous PMD/26K | PMD86/OPNA |
| --- | ---: | ---: |
| Stage 1, ST00 | 3331.81 | 1779.11 |
| Stage 2, ST01 | 1720.28 | 1138.29 |
| Stage 3, ST02 / Bad Apple | 1260.21 | 1373.06 |
| Stage 3 after earlier songs/fades | 1260.32 | 1364.11 |
| Stage 3 with early effects/release | 1272.72 | 1376.43 |

Stage3/Stage1 RMS is about −8.45 dB in the 26K controls and −2.25 dB in the
OPNA controls. The minimum one-second Stage3 window is159.44 in the cold26K
control versus715.98 in coldOPNA. These observations support the user's quiet
passage report and a less uneven default arrangement. They do not establish
that original hardware used the same analogue mix. In both profiles all
post-admission fade/speed samples are0, and sound-effect occupation releases.
The retained fade hypothesis is not reproduced by these component controls.

The first long-probe wrapper reports failure because its Start-Process object
returned no usable ExitCode after exit, despite all five data cases completing.
It is not accepted as an exit-status pass. The corrected wrapper retains the
process handle, waits and checks an actual zero exit for both full profiles.

## Private replay surface

DOS-root `.analysis/audio-stage3-20261027/` owns bounded probe sources, compile
plans, assets digests, canonical-ROM restoration identity and readback receipts.
Actual Windows cases are under
`C:\Users\21992\AppData\Local\Temp\TH04-audio-stage3-20261027`.
`run-profiles.ps1` uses an owned console-free idle/CPU1 process. The external
ROM has the previously pinned8192-byte SHA-256
`53afd0fa9c62eda3e2be939e23f3adf48a2af8ad37bb1640261726c5d5adeba8`;
`rom.json` records a pinned upstream header and exact digest extraction.
No ROM or original game data is checked in.

The background controller now accepts an explicit pinned sound profile/ROM.
Existing plans retain their previous per-mode defaults. New profile plans
continue to require mute, owned inactive desktops and the attested product;
full OPNA plans additionally require the canonical ROM digest. No global
keyboard, desktop, volume or sound-session calls are added.

## Full-flow, loop and transport checks

Both current profiles traverse the complete user Stage3: native resident stage
indices are zero-based, so Stage3 is index2. The original ST02 load/start occurs
at admission20330, ST02B/start at28258, the only stage-local fade command is
020A at34077 after boss defeat, and the next song starts at34150. All231
third-stage aggregate PCM/state windows retain zero fade/speed until that
expected departure. The sequence is identical between profiles. The first
observer summary incorrectly labelled index3 PCM as Stage3; it is rejected in
`rejected-stage-index-readback.json`. The corrected acceptance uses index2's
complete aggregate statistics/actions, without claiming a separate Stage3 PCM.

The observation executable has only View-side collection added and retains the
current game core/main/audio/chip objects. Its first collection guard assumed a clean stage-local frame counter on the
entry admission; the trace still exposes the preceding stage counter then, so
index3 entry incorrectly exceeded2400 before its first ordinary update.
`observation-bound.json` records the reviewed native test-only comparison,
source mirror, before/after bytes and full binary readback for a60000 collection
bound; an explicit38000-admission plan ends both retained observations.
The D: executable is never altered by this diagnostic adjustment.

All23 supplied songs/profile have ten-second start controls. Third-stage ST02
and ST02B additionally reach two global loops in both profiles:242/196 seconds
for M26 and162/196 for M86. No unsolicited fade or sample clipping occurs in
those component cases; peak is24578. No equality between arrangements is claimed.

Actual inactive Windows input/Shift/fire/Bomb/pause/focus/close controls pass
with PMD86 active and zero real audio opens. All nine existing resident/mixed
transport fixtures pass. Protected Normal87454 and same-session-earned
Extra27871 both finish ending/registration/save/fresh OP with zero deaths or
respawns. Complete inputs, states, physical CFG and SCR equal the preceding
PMD/26K clear controls byte-for-byte. Full gameplay routes use logical rendering.

A separate actual WinMM transport control keeps the production Output/Device
implementations and clocks real ST02→ST02B PCM in real time. A test-only API
shim replaces each owned output block with verified zeros immediately before
`waveOutWrite`, so the OS driver and completion callbacks are exercised silently.
It neither changes host volume nor mutes another session. Its bounded result is
recorded in `winmm-readback.json`; this does not test audible speaker quality.

The user's recollection of a mid-song gradual reduction remains unconfirmed:
no retained fade, stuck effect mask or cumulative loop attenuation is reproduced
in these cases. Selecting the complete profile addresses the verified launch
limitation and lessens the especially quiet M26 passages; it must not be
reported as a proved fix for every possible physical-playback symptom.

## Final WinMM resource-fragment packing correction

A second independent finding is an actual Windows transport admission loss.
The previous WaveDevice spent a full2048-frame header on every `push`, even a
single-frame resource-time fragment. Eight tiny admissions therefore consumed
all eight slots while only eight frames were queued, below Output's9600-frame
budget. A same-source old/new fragment counterproof submits5000 one-frame chunks:
the old object rejects at the ninth; the fixed object preserves all frames.
The maintained contracts additionally compare the complete ordered PCM prefix
across fragmented joins, queued/pending/completed counts, atomic busy returns,
slot reuse and failing/refusing-driver cleanup.

The actual old WinMM timing probe also accepts only287199 of288000 generated
frames, dropping801. With the corrected transport, PMD and PMD86 each accept
288000/288000 with zero dropped/suppressed frames and one successful device
open. The562 actual `waveOutWrite` calls receive verified zeros from the test
shim; nonzero original PCM is independently observed before zeroing. Output's
submitted counter includes the pending owned tail, not just completed OS blocks.
The final partial block is discarded only on application shutdown along with
other queued sound, as the existing reset/close policy already permits.

The fixed device coalesces into1024-frame blocks and uses16 stable headers.
The queued-frame total includes the pending tail. This preserves the approximately
64KiB driver pool, with a further4KiB staging array, and makes the200ms Output
budget usable even for resource fragments. Pending-tail latency is bounded by
one1024-frame block (21.3ms at48kHz). The SDL path, PCM synthesis, mixer gains,
game clock and process sound ownership are unchanged.

Only `audio_device.cpp` is cold-compiled for the product and replaced in the
four-member app archive; the same current main/view/joystick and complete core/
chip archives are freshly relinked. The final packaged executable SHA-256 is
`c0d1ca7deaa6a22697fa3926dd1218c08a6b3a88efded89255b04945365b8adc` (no-death gate still RVA2AC060; input hook IAT328D78).
The focused contracts are rebuilt separately. No sanitizer or historical
reconstruction promotion occurs. Final receipts are `final-build/plan.json`,
`driver-contracts-readback.json`, `winmm-readback.json`, and `final-readback.json`.

## Final delivery and review boundary

`D:\Entertainment\Game\Touhou\th04-reconstruct` contains one final
`th04-port64.exe`. Both actual BAT paths use audio plus the complete profile;
the invincible BAT additionally passes the marked data-patch/muted screenshot/
normal-exit smoke at the deployed path. Existing scores/configuration are
hash-unchanged; no user process is stopped. Immutable delivery identities are
in `deployment.json` and `bat-readback.json`. Physical speakers and the user's
recalled gradual reduction still require manual confirmation; the verified
buffer loss and launch limitation have concrete fixes and rejecting controls.

Both root and native `python3 scripts/ci.py`, tracking validation and
`git diff --check` pass. `checks.json` records the two serial CI results;
`finish.json` indexes the accepted receipts after scoped retention/readback.
Superseded initial/duplicate/fourth-stage PCM is retired explicitly in
`retention.json`; selected Stage3 music/effect controls remain independent.
