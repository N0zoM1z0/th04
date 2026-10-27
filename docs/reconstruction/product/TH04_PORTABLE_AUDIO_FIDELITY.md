# Portable audio synthesis fidelity — 2026-10-27

## Current scope

This batch follows the user's Music Room/noisy and missing-voice report. The
preceding audio-profile/WinMM fix remains valid transport work, but its shared
ymfm PCM comparator did not independently establish chip/mix fidelity. This
batch uses independent models and ordered original-driver register events.
DOS reconstruction, original assets, user saves and system/session volume are
unchanged. There is no physical-board or speaker equivalence claim.

## Verified causes and changes

1. **Lost repeated FM attacks.** The IRQ adapter emits ordered register writes
   at one logical interrupt timestamp. ymfm normally samples key bits on a
   generated FM sample, so a key-off/key-on pair inside that batch disappears.
   ST02 has154 such channel0 pairs in32seconds. The first bass attack agrees
   with independent models, but later attacks vanish and its envelope keeps
   decaying. The adapter now explicitly commits each key-register edge before
   accepting the next one, without advancing chip time. A small opt-in BSD
   ymfm extension exposes channel preparation; ordinary upstream clients retain
   deferred behavior. Its two modified header hashes are separately recorded
   in `port64/vendor/ymfm/UPSTREAM.json`; pinned upstream identities remain.
2. **Incorrect relative mix.** A full-level single FM sine measures about1444
   RMS in the old path versus2889 in libopna; the SSG square measures2718
   versus1134. The SSG/FM ratio is about13.6dB too large. Remove the arbitrary
   final half gain, normalize the distinct OPN/OPNA DAC widths and apply the
   independent-model-calibrated SSG contribution. No per-song/voice gain, automatic
   compression or peak normalization is used.
3. **Audible aliasing and quiet-signal distortion.** The old box integration
   lets high SSG harmonics fold into48kHz audio; integer DC feedback also
   distorts quiet samples and removes unnecessary bass. An authored256-tap
   causal Kaiser-windowed sinc operates on MED-fidelity chip samples above the
   SSG clock, evaluates only at48kHz outputs and uses mathematical coefficients.
   A fractional DC blocker keeps an approximately5Hz corner. The authored
   SSG period23 control has a5426.087Hz fundamental and a37982.609Hz seventh
   harmonic that folds to10017.391Hz: old−28.94dB, fixed−73.79dB relative to
   fundamental (about44.8dB reduction).

Runtime CLI profiles use the externally corroborated3993600/7987200Hz board
clock settings instead of rounded4/8MHz. Fixture APIs still accept explicitly requested clocks. PMD86
song-start also restores three original observed writes before SSG start:
bank1:10=80, bank1:10=18, bank0:29=83. No target bytes are modified.

## Independent evidence and negative controls

Private replay root: DOS-root `.analysis/audio-fidelity-20261027/`; actual
Windows root: `C:\Users\21992\AppData\Local\Temp\TH04-audio-fidelity-20261027`.
`inputs.json` attests the HDI, extracted songs, EFC,512-register mirror and
56 installation writes. PMD86.COM SHA-256 is
`34b7381d66400b89fca833e08fb30f315b9092eb3883f137538dcf18477fd77f`,
flat COM PSP1000, entry0100/service0103. No disassembler database is used.
The original driver runs through the attested Unicorn adapter, with IRQ
cycles/flags supplied by the native timer adapter; these are not independent
physical port-cycle timestamps. All ordered unmasked bank/address/value events
for32seconds match after the three startup writes are restored: ST02:16601,
ST00:12275, OP:20370. LF-normalized event identities are recorded; Windows CRLF
is not described as byte-identical to Linux LF.

The first native sequence omits the three writes and fails at row87; preserve
`driver-mismatch.json`. `driver-readback.json` records the corrected passes.
The initial operator-pipeline-delay hypothesis is disproved: a scratch-only
pipeline-delay change leaves the missing voice levels essentially unchanged.
It is not included in the product. Committing key edges restores them instead.
The focused new envelope regression passes for FM26 and OPNA; linking the same
check against the mix/filter-only core fails the repeated-attack assertion.
Repeated key-on without a release must still sustain/decay normally.

Independent chip references, retained only in private scratch:

- [98fmplayer/libopna](https://github.com/myon98/98fmplayer/tree/4fa914e4b2b994cb3ccf92d571a20a7cdf1fe36a/libopna), revision
  `4fa914e4b2b994cb3ccf92d571a20a7cdf1fe36a`, native7987200/144Hz;
  explicit original YM2608 SSG mode and canonical rhythm ROM.
- [libOPNMIDI historical MAME FM](https://github.com/Wohlstand/libOPNMIDI/tree/43b6bee61c943ebf91f50dbea649da04aa87fca2/src/chips/mame), revision
  `43b6bee61c943ebf91f50dbea649da04aa87fca2`, a third FM-only48kHz control.
  Its common normalization differs from libopna by about−3dB, but relative
  voice levels agree and independently reproduce the missing-voice diagnosis.
- Pinned current MAME PC98 soundboard routing corroborates clocks/mixing only;
  current MAME shares ymfm and is not counted as an independent FM arithmetic
  implementation. Its26K divider is explicitly unverified and its86 clock is
  rounded7.987MHz; libopna documents7987200Hz. Analogue board mix can differ,
  so the mix is calibrated to an independent player, not physically attested.

No GPL reference implementation, chip ROM or original music is imported into
product source. `oracle.cpp` replays identical ordered **original** events to
both product OpnPcm and libopna; masks isolate key-ons/SSG/rhythm identically.
`third.cpp` supplies the same events to the historical MAME core. Compare native
48kHz and reference native-rate statistics after0.2seconds; no PCM equality
between independent models is asserted.

| ST02 isolated voice RMS,32seconds | Old product | Mix/filter only | Corrected key edges | libopna |
| --- | ---: | ---: | ---: | ---: |
| FM0 bass | 26.75 | 56.17 | 421.26 | 424.34 |
| FM1 | 88.40 | 177.97 | 288.62 | 287.89 |
| FM2 | 85.98 | 176.03 | 282.88 | 283.16 |
| FM3 | 79.98 | 161.45 | 161.45 | 161.53 |
| FM4 | 79.62 | 161.17 | 161.17 | 161.13 |
| SSG | 1243.67 | 547.37 | 547.37 | 550.30 |
| Rhythm | 479.86 | 1000.68 | 1000.68 | 1024.43 |

## Replay and current validation

Affected-only release compile/link plan: `final/plan.json`, serial bounded
`final/run.py`; product plus waveform/contracts/corpus/silent-WinMM controls.
The PCM contracts retain sample counts, time partitions, mono routing, three
SSG channels, absent-bank behavior, ROM and prescaler rejection; add independent
mix/alias limits and the repeated-attack versus held-note negative control.

Windows replay scripts retain process handles and real exit codes, use owned
console-free idle processes on one CPU, and open no output device for waveform
controls. `run-quality.ps1` uses a separate actual WinMM control: every owned
block is verified zero before `waveOutWrite`, preserving real OS completions
without audible playback. Both profiles accept288000/288000 generated frames,
zero dropped/suppressed, one successful open;562 verified silent writes.

All23 songs/profile start cleanly. ST02 reaches two loops in243seconds (M26)
and162seconds (M86); ST02B takes196seconds in both. All1213 one-second windows
retain zero fade/fade-speed; maximum peaks13250/22470 remain below clipping.
This tests sustained synthesis and state, not constant musical loudness.

Actual Music Room navigation selects No.7 Bad Apple, plays through repeated
attacks, switches to No.8/ST02B and returns to OP; comments/screenshots are
inspected. Fresh fixtures skip locked Extra when navigating the main menu:
the first three-down controller mistakenly opens Options and is rejected in
`rejected-music-navigation.json`; the maintained two-down fixture passes.
All nine resident/transport modes produce65 files;27 bitmap outputs remain
identical. Hooked input/Shift/fire/Bomb/pause/focus/close passes with zero audio
opens. Protected Normal87454 and same-session-earned Extra27871 strictly clear,
register scores and return to fresh OP with zero misses/respawns. Their complete
state/input/physical CFG/SCR files remain identical to the earlier transport
release. Full routes use logical rendering; the separate Music Room/window
controls are actually rendered. `game-readback.json` records both scopes.

The released sole `th04-port64.exe` has SHA-256
`8a178d24c284e1703c4ffa71e0b68c4a4f0845481604b7e2655dae16c9752940`.
The initialized no-death marker remains A4→A5, now mapped at RVA2AB060;
GetForegroundWindow IAT is RVA327D78. Both helpers use hash guards for these
new addresses. Physical listening remains the user's final check.

The actual delivered no-death BAT exits0 through CMD, verifies A4/A5 and
produces the muted title image with all three existing CFG/SCR digests intact.
`deployed-bat-smoke-final.ps1` writes a plain completion marker; a read-only
Linux finalizer records hashes. Earlier richer PowerShell report wrappers reach
all product/save guards but stall during report generation and are rejected;
only their explicitly identified owned wrapper processes are stopped, after
all game children have already exited. No user process is stopped. Root/native
`python3 scripts/ci.py` and `git diff --check` pass.
