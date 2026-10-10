# OP startup state and frontend ownership

v1346 implements the one-time ZUNsoft logo/fireworks and the OP title sequence.
This closes the bounded control corpus and muted frontend ownership below.
Independent full startup pixels, physical timing/audio, natural complete routes
and a newly delivered GUI remain open. Historical DOS acceptance is unchanged.
Targets retain candidate-local-attested provenance.

## Original execution and adapters

The producer executes the unchanged decoded OP at load segments 1000 and 2000:

- OP 0A74:0CB6..0CE2: resident logo decision and demo-dependent title call;
- OP 0A74:1305..1763: pyro spawn/update, palette helper and logo;
- OP 0A74:2592..281D: title sequence;
- OP 0000:204E..2077: process-local LCG;
- OP 0DA1:01A8..01C3: signed fixed-point polar calculation;
- OP 0000:0622..06A2 and 1DE0..1E48: fades and analog palette/DAC arithmetic.

PI decode/load/free, BFNT registration, indexed page/background consumers,
input samples, refresh and measure readiness, and sound calls are guarded
adapters. The shared original CPU engine is not a physical PC-98 emulator.
The original module, 804 relocation sites, packed input, HDI, decoder, engine
and producer source archive have recorded identities. The active OP database
was independently re-attested from the root worktree.

Fifteen fixtures cover title with/without demo BGM, two LCG seeds, no skip,
first-frame skip, an unsampled odd-refresh pulse, later skips, active measure
readiness, and nonzero retained raw palettes. GNU8, optimized UBSan and actual
Windows compare all 147,830 state/request text rows, including every serialized
256-slot pyro array, LCG, raw palette, DAC and access/shown page state at wait
boundaries. Windows CRT CRLF is normalized to LF; this is a semantic text-row
comparison, not historical raw-byte exactness.

Normal logo+title is 533 refreshes without a measure wait; title alone is 175.
The first-sample skip consumes 277 refreshes, fading over the original two-
refresh logo frames. An odd-refresh key pulse is not sampled. Active frontend
waits query the installed driver's real song measure, rather than a fixed logo
clock. BFNT registration changes raw RGB without showing the DAC. The title
still uses the retained PI header palette after freeing its pixel allocation.

## Actual frontend and storage boundary

Three driver profiles each run all nine BGM/SE choices plus missing and bad
configuration cases. A second invocation starts a separate host process and
reopens its own score/configuration files. Each of GNU8, optimized UBSan and
actual Windows has 336 equal capture files across 66 settings/restarts; the
final physical files also agree. All launches are muted, with no audio device
or backend. Captured mixed PCM and indexed/RGB frames establish host
consistency; they are not independent physical-chip or complete-pixel Oracles.

The first BGM/SE case per driver uses an authored legal finite STD. Real
ordinary contact reaches Game Over, Quit enters score-only MAINE, registration
and verdict return to fresh OP, and that OP runs its unskippable 175-refresh
title. No hit/life/score/MAINE completion is forced. This bounded child route
is not a natural six-stage run.

Configuration loads before setup/startup; score-file construction and scan
wait until the title returns. The logo flag publishes at logo completion,
while the final process LCG is transferred before score recreation consumes
it. Fresh OP reloads the physical configuration before its title, keeps the
resident PMD and its clock, skips the already-shown logo and resets the local
LCG. An independent process restart displays the logo again. Repaint does not
consume refreshes, LCG or PMD time.

A developmental frontend run exposed a stale MAINE screen during configuration
reload. The retained GDB backtrace names render -> enable_configuration ->
restore_fresh_op. OP now publishes its screen before that load can repaint.
Other developmental failures include a malformed authored STD and a producer
cancelled because aggregate linking replaced its decoder input. Those logs are
diagnostic failures, not accepted producers. The final original run uses a
separately frozen decoder copy and closes its source/input hashes unchanged.

Four source-only variants are rejected: immediate skip fade, wrong pyro speed
modulus, incorrect high-tone palette rounding, and wrong BFNT load order.
Resident service/frontend regressions retain all three profiles and their
prior Music Room/MAIN/declared registration-child limits on GNU and UBSan.
All 64 contracts pass on GNU, UBSan and actual Windows.

## Identity and replay

459 maintained inputs bind 195 AMD64 products (65 per host).
Source manifest: `b62c3026fcfa814ccce48906485e6c191c51c760486455421b04fee3c2aaf61f`.
Private scope: `.analysis/port64/startup-v1346/` in the native worktree.

```sh
python3 port64/verify_op_startup.py --target TARGET --decoded-dir DECODED \
  --hdi HDI --decoder FROZEN_DECODER --output FRESH_ORIGINAL
python3 port64/verify_op_startup.py --reference ORIGINAL \
  --exe STARTUP_CONTRACT --output FRESH_CONSUMER
python3 port64/verify_startup_join.py --hdi HDI --font FONT --rom ROM \
  --original-reference ORIGINAL --binary GNU --binary UBSAN --output FRESH
```

Final receipts are `original-final-v2/receipt.json`,
`control-{linux,ubsan}-final-v1/receipt.json`, `frontend-final-v1/receipt.json`,
`windows-{component,contracts,frontend}-receipt.json`,
`windows-save-readback.json`, `counterproofs-final-v1/receipt.json`,
`resident-regression-final-v1/receipt.json` and `product-profile-final-v1.json`.
Producer/consumer archives and frozen decoder remain separate. Actual Windows
uses the checked-in `verify_windows_current.ps1` with retained typed plans;
the private startup text consumer/plan are retained and hash-bound as inputs.
Cleanup journals and recovery archives supply the retired Windows stage and
experimental programs; replay always uses fresh destinations.

## Remaining gates

Implement independent original clipped SUPER/GRCG startup pixel comparisons,
then broaden setup/fresh OP failure controls and original complete startup
integration. Full natural Normal/Extra routes, audio usage/remaining owners,
host refresh/input/slowdown/Lunatic timing and GUI publication remain. This
batch does not resolve PPS/external ADPCM or prove unused ownership from the
absence of bank files in the supplied archives.

Terminal retention verifies 11 archives/2121 protected hashes, retires
2575 files and shares 886 immutable equal captures. Measured reclamation
is 1447223296 allocated bytes. The source/program/cache/input identities
remain unchanged; native objects/static libraries are regenerated by CMake.
