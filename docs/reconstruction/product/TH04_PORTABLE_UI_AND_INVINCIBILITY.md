# Portable MAINE UI and seamless invincibility — 2026-10-27

## Product and user scope

Current Windows x64 product SHA-256 is `2dfd38e8eafefde4f0f428633c6dc3c31c1dd1ca6ff1211bfedc8d6d37f2e4a2`.
Both D:\Entertainment\Game\Touhou\th04-reconstruct BAT launchers retain audio.
`Play.bat` uses ordinary hits; `Play-no-life-loss.bat` now suppresses accepted
hits, death animation, power loss and respawn. Existing saves are preserved.
Tests use muted owned inactive desktops, process-local input adapters, and fresh
private save directories. No global input/volume changes or further UBSan work.
Earlier [render/Extra](TH04_PORTABLE_RENDER_PERFORMANCE.md) and
[functional smoke](TH04_WINDOWS_FUNCTIONAL_SMOKE.md) results keep their historical
artifact identities. This batch is not a DOS exactness promotion.

## Ending, registration and saving

The earlier DOS planar batch used bulk page copying and packed-pair processing
for title/Ending work; see [its measured scope](TH04_NATIVE_SUPER_SPRITE_V870.md#native-planar-performance-batch-2026-10-03).
The portable equivalent now batches enclosed full-mask page rectangles and
unmasked packed PI rows. Masked, clipped and unusual addressing paths keep the
preceding implementation. Full pictures retain physical Y wrapping.

`dialog::Font::row/ank_row` read a complete monochrome glyph scanline; existing
pixel methods remain independent controls. MAINE graphics text and TRAM overlay
use rows instead of repeated per-dot ROM/address decoding. Per-half attributes,
mismatched Kanji halves, blink-before-reverse, graphics font effects and WORD
aliases are preserved. Registration converts its 16 live colors once per redraw.

A public asset-driven `th04-port64-ui-performance-probe` target checks all 65536
character codes at 17 rows/16 pixels and 256 ANK codes at 17 rows/8 pixels against
the unchanged pixel API. Before/after byte comparisons accept 11 complete graphics/
state/save files for all eight Good/Bad character/shot Ending scripts and 112
registration controls/files across 30 fixtures. No pixel tolerance/masking is used.
The graphics probe bypasses only PMD measure waits; it is a seeded component
fixture. Independent real Windows Ending windows keep the sound clock and run
through story, staff/verdict, name entry, save and fresh OP on both products.

| Component observation | Before | After |
| --- | ---: | ---: |
| Registration redraw median | 1.0480 ms | 0.4608 ms |
| Registration redraw p95 | 1.2899 ms | 0.6228 ms |
| Ending script/graphics update p95 | 0.1014 ms | 0.0680 ms |
| Largest Ending component update | 0.6385 ms | 0.1819 ms |
| Actual final score-writer close | 2.7474 ms | 3.1039 ms |

Host timing is noisy: live PMD window registration p95 is 2.0775→1.9516 ms in
the direct registration fixture, while the post-Ending registration sample is
2.4311→4.3147 ms. No universal live-window latency or physical-display improvement
is inferred. Both full Ending window controls take about 115 seconds; intentional
story/music/fade timing is retained. Cursor taps change coordinates at the first
refresh that samples the direction. Both products repeat a held direction after
33 refreshes (about 0.585 s), then every 3 refreshes. This initial delay is the
existing input-lock/repeat policy, not storage I/O. Cursor actions do not write
the score file; writer-close remains synchronous and keeps error propagation.
All ten reopened score checksums pass after each actual window save.

## Seamless invincibility

The user referenced TH095's `run-no-death-test.ps1`, which returns before its
player-death handler changes mode/effects. That is cross-game design evidence,
not a TH04 target Oracle. TH04 now gates its shared collision predicate, used
by both the frame prefix and resumed/frame-end suffix. Every ordinary bullet,
enemy/body and beam collision source reaches that predicate. The underlying
ordinary lifecycle, movement, firing, Bomb and rendering continue normally.

A single native initialized control byte `th04_suppress_player_hits` has marker
A4 with bit0 clear in the ordinary executable. The guarded launcher checks the
exact executable hash and owned mapped image, then writes A5 at RVA `0x2AC060`
in its new suspended process and reads it back. This is a process-only data
patch, not an on-disk or original-DOS patch. The character is not made permanently
blinking by forcing the ordinary invincibility timer. Foreground IAT RVA for
this product's private test adapter is `0x328D78`.

A fixed-shot contact control demonstrates 6 misses/616 respawn samples in the
ordinary mode versus 0 misses/0 respawn samples over 18000 protected admissions;
protected lives never fall below 6. The ordinary state trace still equals the
preceding ordinary control byte-for-byte. Actual hooked Windows movement,
half-speed Shift, shooting/release, Bomb, pause/resume and focus controls pass.
Protected Normal Reimu A 87454 and same-run Normal-earned Extra Reimu A 27871
complete expected stages/endings/registration/physical masks/checksums/fresh OP
with no misses or respawn samples. These complete gameplay routes use logical
render_every0; they are not full continuous-GDI route acceptance.

An initial prefix-only gate is deliberately rejected: it reports a successful
memory patch but still has 6 misses, equal to ordinary. The hypothesis that
startup reset its BSS flag is disproved by post-window memory readback 01. The
actual cause is the unguarded frame-end latch. The final shared predicate covers
both callers; the initialized marker makes wrong-address checks explicit and
is not credited as the cause of the behavioral repair. Rejected candidates were
never deployed. A first seeded UI attempt also omitted the deferred HostStore;
its initialization rejection is fixture preparation, not a product regression.

## Build, replay and delivery

The native worktree retains the maintained sources/tools. View compiles cold
once for the muted/traced environment-gated UI inspection entry. Four core
translation units change: `main_state`, `dialog`, `registration_render`, and
`cutscene_scene`; 109 core members retain identity. The final gate correction
recompiles/relinks only `main_state`. Additive font methods preserve class layout.
`TH04_UI_TEST_SCENE=registration|ending` requires explicit mute and window trace;
normal launchers never set it. Registration trace frame/x/y mean menu admissions
and grid coordinates in that scene. The baseline uses the same inspection entry.

Private root: `.analysis/ui-perf-20261027/`; actual Windows cases:
`C:\Users\21992\AppData\Local\Temp\TH04-ui-perf-20261027`.
`release/` retains the accepted UI/graphics product and rejected prefix-only
no-death experiment; `final/` owns the corrected no-death controls. Keep those
artifacts distinct. Key receipts are `build/receipt.json`, `build/changed-core.json`,
`gate-fix-v2/receipt.json`, `ui-readback.json`, `verification.json`, `cases.json`,
`god-final-cases.json`, `rejected-gate.json`, and `final-candidate.json`.

```sh
# From native worktree, with fresh output:
python3 -B port64/verify_ui_performance.py --root /ABS/WINDOWS/TH04-ui-perf-20261027 --god-root /ABS/WINDOWS/TH04-ui-perf-20261027/final --output /ABS/FRESH-ui-readback.json
```

The actual BAT also passes guarded no-death patch, muted title BMP and normal
exit both in a private package copy and at the deployed D: entrypoint
(`bat-receipt.json`). Both root and native `scripts/ci.py` and `git diff --check`
pass (`checks.json`). The final package contains only `th04-port64.exe`, shared by both BAT
launchers. The earlier temporary smooth/ordinary filenames have been consolidated
without changing the accepted executable bytes. Packaging readback is retained
in `.analysis/package-cleanup-20261027/`. Existing
user saves and configuration are not replaced. Audible hardware/input/display
feel remain for manual review.
