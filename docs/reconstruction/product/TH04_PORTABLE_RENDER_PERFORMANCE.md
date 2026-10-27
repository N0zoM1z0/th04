# Portable rendering, frame pacing and Extra delay reset — 2026-10-27

The subsequent [UI and true no-death update](TH04_PORTABLE_UI_AND_INVINCIBILITY.md) supersedes this preview binary and its no-stock-loss-only launcher behavior.

## Earlier product and scope

The Windows x64 release is SHA-256 `eaa05bdde3c21f702df7b6d9885aa78813216a18449d34e56b296f85fe437e3a` in
`D:\Entertainment\Game\Touhou\th04-reconstruct`. Both `Play.bat` and
`Play-no-life-loss.bat` enable audio. Background plans explicitly stay muted,
use owned inactive desktops and never switch the input desktop or send global
keys. The user deleted the previous preview and requested a complete replacement.
The complete package is recreated and all delivered files are read back by hash;
see `deployment.json`. No user process was stopped.
No further UBSan work is part of this batch. Original DOS exactness ledgers
and executable files are unchanged; canonicality remains candidate-local-attested.

The current native source is in the `work/port64-recovery-v1445` worktree.
Release builds compile only changed view/main-state translation units and
relink fresh archives; 112 other core members, three app objects and ymfm are
reused by identity. Additive inline row/reset accessors leave class layouts and
existing bounded boss update bodies unchanged. Build receipts name every input,
command and changed archive member. A subsequent cold view.cpp replay with the
additive boss headers produces the identical retained app object. This is portable behavior/performance work,
not an exact promotion or a new Linux product build.

## Extra: measured half-speed leakage

The reported screenshot shows a dense Extra boss scene. Initial source review
correctly finds Extra forces Turbo and bypasses ordinary density slowdown, but
that does not rule out the separately retained boss delay request.

An actual Windows, fully rendered no-life-loss Extra route completes 29251
admissions, registration, physical scores and fresh OP before and after the fix.
Both runs reach 400 bullets and contain 1151 Gengetsu samples at or above 320.
A separate current Normal Reimu A no-life-loss regression completes all six stages,
Good Ending `_ED000.TXT`, registration and fresh OP in 90294 admissions. Its complete
state/input files equal the earlier unoptimized release.
Before the fix every one of those dense samples requests delay 2 despite Turbo 1;
afterward every one requests delay 1. Total delay-2 admissions fall from 12588
to 128: the two 64-frame boss defeat animations still request their delay.
Gengetsu handoff remains admission 15722. The independent strict-clear reader
accepts the real Extra mask/checksums and physical return flow on both products.

`orange::update_defeat()` sets the boss snapshot's delay to 2. That snapshot is
copied from Mugetsu into Gengetsu, and the old portable frame loop never clears
the request. The repaired MAIN owner resets only the selected boss's request
at the start of a new simulation frame. A suspended player/dialogue suffix keeps
the same frame's request. Boss metadata, bullet density policy, hits, speed,
phase scheduling and the defeat callback stay unchanged.

Original target evidence is independent: hash-attested MAIN
`SLOWDOWN_TEXT:0002` (MZ-relative CS `0AAF`, file `C2F2`, 26 bytes) clears
VSync count DS:2AB2 and writes 1 to delay DS:5390 before returning. The existing
unit is `th04-main-slowdown-frame-delay`; this batch does not promote it again.
A fresh Unicorn replay at load segment 2000, CS 2AAF, synthetic DS 8000 passes
six completed-wait and two still-busy controls. Skipping only the reset store
by diagnostic PC control retains 2 and is rejected. This is original-instruction
CPU evidence, not a new PC-98 full-game or physical timing measurement.

Dense Extra update plus first drawing has p95 1.7124 ms after the fix; the
separate warm redraw has p95 1.3368 ms, below the normal 17.723227 ms budget.
These diagnostic wall times include host scheduling and exclude real GDI display
presentation. They establish that this tested half speed is a delay-state leak,
not a CPU frame-budget overrun. They do not rule out other host/display hitches.

## Rendering and Windows pacing

The earlier DOS optimizations are reused as design evidence, not copied x86-16
code: see [planar kernels](TH04_NATIVE_SUPER_SPRITE_V870.md#native-planar-performance-batch-2026-10-03)
and [dense bullet/cloud controls](TH04_NATIVE_BULLET_LOAD_V1235.md). Those notes
separate transparent masks, fixed rows, packed pairs and emulator CPU budgets.
The portable renderer now:

- Computes 16 live RGB colors once per MAIN frame, preserving current fades,
  player palette14 and boss palette-zero updates.
- Resolves scroll/ring/carpet/mask inputs once per 16-pixel tile scanline.
- Clips ordinary packed sprites once and reads packed rows directly, removing
  per-pixel out-of-line sprite lookups; transparent color zero is preserved.
- Fills clipped rectangles by rows and expands packed PI pairs linearly.
- Uses local palette tables for dialogue and ending-page color conversion.

Before changing delay behavior, all 314 complete BMP component outputs equal
the unoptimized release: title, four shots, combat/barrage, dialogue, Stage2,
Stage4 carpet and Stage5 stars. After the delay correction 310 remain byte-equal;
four post-dialogue captures differ by exactly 407 pixels each, bounded to
x130..329/y353..366. Visual inspection identifies only the blinking `Bomb Extend!`
TRAM message. Advancing the correct number of VSync refreshes changes that blink
phase; this is retained as an explicit difference, not masked as equality.
The complete four-file Bomb state/snapshot corpus remains byte-equal.

Windows replaces the coarse SetTimer polling loop with a process-local one-shot
high-resolution waitable timer and message-aware wait. Simulation deadlines and
bounded catchup remain separate from painting. No busy spin or timeBeginPeriod
request is introduced. Failure to create/arm the timer falls back to SetTimer;
`TH04_LEGACY_WINDOW_TIMER=1` forces that path for same-binary A/B testing.
Microsoft documents the [SetTimer minimum](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-settimer),
[high-resolution timer flag](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createwaitabletimerexw)
and [message wait](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-msgwaitformultipleobjectsex).

The same timer-only executable's short A/B controls both pass input/Bomb/pause:
p95 presentation interval is 31.7519 ms with legacy versus 19.6344 ms precise;
p95 deadline lateness is 16.045665 versus 0.997147 ms. Longer original/release
Windows runs through Stage1 dialogue, boss departure/fades and real Stage2 entry
both close normally with no schedule resync. Normal-cadence MAIN p95 intervals
are 31.0809 versus 18.7665 ms; MAIN update/draw p95 is 4.6976 versus 2.2704 ms.
These longer workloads use the same frame-key fixture with asynchronous process
messages, not identical game states or an isolated causal CPU microbenchmark.
Idle menu frames repaint only on changes; their long presentation gaps must
not be reported as gameplay stalls. The existing original stage-session counter
wait to 128 overlaps loading; it is not an additional 128-tick wait after load.

## Reproduction and delivery

Private root index: `.analysis/transition-perf-20261027/`.
Actual Windows cases: `C:\Users\21992\AppData\Local\Temp\TH04-transition-perf-20261027`.
Important receipts: `release-validation.json`, `release-readback.json`,
`extra-fix-comparison.json`, `render-equivalence.json`,
`final-window-bomb-comparison.json`, `original-delay-reset.json`,
`delay-fix-picture-differences.json`, `delay-fix-v2/receipt.json` and
`release-candidate.json`. The pre-fix fully rendered Extra negative is `final/`;
the corrected product's cases are `release/`. Preserve this distinction.

```sh
python3 -B scripts/probes/probe_th04_slowdown_reset.py --output .analysis/FRESH-delay-reset.json
# From the native worktree; all output paths must be fresh:
python3 -B port64/verify_frame_pacing.py --extra-before /ABS/WINDOWS/final/extra-rendered --extra-after /ABS/WINDOWS/release/extra-rendered --output /ABS/FRESH-extra.json
```

The native controller accepts pinned candidate hashes/RVAs and muted version-1
JSON plans. `--render-components` is a controller bundle of existing inspection
flags, not a new game CLI flag; it disables PMD synthesis on both sides for the
image-only comparison. Real window and rendered Extra cases keep PMD enabled.
The no-life-loss release patch verifies `83 E8 01 88 42 19` at RVA `0xDFBD0`,
changes only its immediate at `0xDFBD2`, and reads it back. Foreground IAT RVA
is `0x326D78`. No original executable or existing user process is patched.

The manual launcher passes a separate actual-Windows muted headless startup/BMP/
exit test. A subsequent user launch exposed cmd quoting of a Directory ending
in a backslash; the BAT now lets PS1 use PSScriptRoot. The actual deployed BAT
also passes guarded patch, muted screenshot and normal exit (`bat-launcher-receipt.json`).
The two maintained wrappers are `port64/Play*.bat`. Private plans retain exact commands, target/font/seed identities and
controller hashes. Both BAT entrypoints in the delivered package use audio;
no test-only mute is inherited into them. Audible hardware and physical input/
display smoothness remain for the user's manual review.

Rejected preparation remains separate: an initial PMD-on broad screenshot
campaign was stopped before its timeout; the unmodified old Stage6 inspection
bundle misses a required Yuuka6 checkpoint and is not accepted. The admitted
image bundle ends at Stage5. One compile attempt had an orange object/pointer
typo, and one private profile adapter retained an old numeric RVA; its full
instruction guard refused the patch before resume. Fresh corrected cases pass;
none of those prefixes is relabeled as an application regression or acceptance.

Both root/native `scripts/ci.py` pass after regenerating the root script catalog.
The current Windows Normal integration replay and final tracking/diff checks
remain separate from those control-plane CI results. Scoped retirement is indexed
in `retirement.json`; accepted component BMP paths are retained using hard links.
