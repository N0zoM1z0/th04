# Stage 1 evidence

Historical bounded results, preserved from `docs/PORT64.md`. Current state is
[the port overview](../../PORT64.md). Original CPU execution and adapter scope
remain explicit; successful component controls do not accept complete gameplay.

## Stage 1 midboss

`midboss` owns fixed-width Stage 1 state, activation at frame3100, the four
emergence-tile writes, the two invulnerable unfolding phases, the paired
special-bullet pattern, shot damage, five-unit score bonus, scroll timeout and
the common defeat lifecycle. It preserves HP800 versus displayed HP maximum620,
signed frame/HP wrap, retained damage bytes, and the second bullet's reuse of
the once-tuned shared template. The phase-zero Y compensation adds the prior
frame's subpixel scroll delta, not the physical scroll origin. STD dispatch
uses the previous active flag before activation, matching the original loop.
Enemy homing selection is overridden by the midboss after enemy updates;
next-frame shots consume that result. Hit sparks consume one shared sample
per free attempt with radius128/count1 at the original call boundary.

`prepare_render` caches normal/white split sprites and the 16-sprite expanding
defeat ring once per simulation frame. Refreshing the host window does not
clear damage twice or advance the defeat angle. `stage1_setup` appends twelve
64x32 `ST00.BMT` patterns at global140 after twelve 32x32 `ST00.BFT` patterns
at128. The host now loads both sheets. Original setup installs BMT's palette
and overrides color zero's R/G to FF; native RGB is FF/FF/70 before DAC
quantization. Earlier MAIN fixture `a6341ebd...` becomes `4cbbe895...` for this
specific correction. Four earlier combat BMPs change only their80/85 color-zero
pixels; their geometry and counters are unchanged. OP/selection/handoff hashes
remain unchanged. This supersedes the earlier incomplete Stage 1 palette.

The prior-image delta probe is replayable from the private v1256 baseline
and the new cross-host receipt's `combat-linux` directory:

```python
import hashlib, json
from pathlib import Path
old = Path('.analysis/port64/verification-effects-v1256-final2/combat-linux')
new = Path('.analysis/port64/verification-midboss-v1257-final/combat-linux')
baseline = json.loads((old.parent / 'receipt.json').read_text())
for path in sorted(old.glob('*.bmp')):
    before, after = path.read_bytes(), (new / path.name).read_bytes()
    assert hashlib.sha256(before).hexdigest() == baseline['combat_fixture_bmp_sha256'][path.stem]
    expected = bytearray(before)
    for at in range(54, len(before), 3):
        if before[at:at+3] == bytes((170, 204, 170)):
            expected[at:at+3] = bytes((119, 255, 255))
    assert expected == after, path.name
```

The new independent CPU oracle executes pinned original MAIN at load2000,
DS8000, checking699 isolated update/activation/reset/render cases, including
all440 packed26-byte bullet records, the22-byte midboss state, full scratch,
HP/animation globals, random cursor and ordered effects/draw coordinates.
An additional450 controls execute original tile initialization, scroll driver
and the actual tile setter at six checkpoints, comparing the complete25x24
ring. A separate original `stage1_setup` call verifies initial state, the BMT
filename and palette overrides with an explicit file-palette adapter. Scope:
main_03 13A9:0522/0587/642C/6454/6486/64DE/65B7/A55F;
main_01 0AAF:1C88/6FAA/0B92/0FB2/21E6. Ghidra database attestation and
target identity pass; canonicality remains candidate-local-attested.

Midboss CPU controls inject damage at the hittest boundary and intercept
tile/circle/point-number/audio/HP-pixel calls. Tune/add/bonus and defeat
geometry execute; independent tile controls execute the setter itself.
These are bounded runtime observations, not byte equality or full-route
original video comparison. MAIN retains pending sound, point, HP and shake
requests in `midboss_events`; audio, point-number rendering, HUD and screen
shake remain to be connected. Host redraw does not yet emulate the exact
PC-98 page/dirty-tile publication schedule or every edge-roll case.

Linux ELF64, Wine-hosted Windows PE32+ and GNU UBSan/bounds pass seven
contract targets. The four4500-frame scenarios reach phases0/1/2/3 and leave
the scene; shooting kills the midboss while idle runs exercise timeout.
All24 BMPs and gameplay counters agree across hosts. Original CPU receipts:
`.analysis/port64/midboss-v1257/cpu-{linux,windows,ubsan}-final/receipt.json`.
Cross-host receipt:
`.analysis/port64/verification-midboss-v1257-final/receipt.json`.
No original executable/assets are embedded, and no DOS source or acceptance
state changes. Native Windows pacing and a complete game remain unverified.

## Stage 1 Orange state and attacks

`orange` now owns the fixed-width Stage 1 main Boss state: entrance,
four random movement/attack modes, horizontal bounce attacks, escalating
multi-direction bursts, HP thresholds, timeout, small/big explosion creation,
the final explosion animation clock, and Stage 1 clear/next-stage requests.
It uses the existing bullet, gather, spark and shared random-ring owners
synchronously. The scratch templates retain unused bytes and the second shot
of a paired producer uses the first shot's tuning. The regular random rings
intentionally do not tune. Multi-bursts use the verified fixed-speed wrapper.

This is a verified logic owner, **not yet connected to ordinary live MAIN**.
Foreground, explosion aging, circles and host background composition now
connect through the explicit diagnostic entry described below. Ordinary
pre/post-boss dialog, HUD/audio and the stage-clear consumer remain to connect.
The current live window still ends at the previous Stage 1 frontier. Original
`MAIN main_01 0AAF:2454` activates Boss callbacks only after scroll speed is
zero, the back page is 1 and the blocking pre-boss dialog has returned;
exhausting the STD wave program is insufficient. Keep that barrier when
connecting this owner. Post-boss dialog/bonus/next-stage events are ordered
requests: the progression consumer must account for resident graze before
dialog, complete the dialog before stage bonus and honor the quit/delay
boundary. These unported consumers are explicit adapters in the CPU controls.

The independent original-CPU comparator executes `MAIN main_03
13A9:6013` (complete 0x403-byte Orange update, followed by two switch tables),
its attack callees at `5B54..6012`, common hit/phase/defeat helpers
`AB48/ABBE/AC02/AC63/ACB3`, bonus `6548`, typed explosion adds `21EC/226C`,
and actual bullet/gather/spark callees. Load segment 2000, DS 8000 is recorded;
loaded code is 33A9. The local target remains candidate-local-attested,
MAIN SHA `077440a3...`, header 6144, 1136 relocations. Current Ghidra attestation
is checked separately; the database is not an independent behavioral oracle.

Two receipts supply 36,600 complete state checkpoints: 2,805 isolated controls,
ten whole-Boss sequences (five ranks, zero/19 injected damage,5,117/1,130
frames), and twenty 128-frame complete pattern controls (all four modes on
five ranks). Every sequence reaches phases 0/1/2/3/4/5/254/255 and the next-stage
request. The fixed ring does not choose aimed-cloud mode 2 in the whole-Boss
sequences; the separate full-pattern controls cover that gap explicitly.
These sequences advance Boss only; bullet/gather/spark pools deliberately
retain occupancy, so they are not natural gameplay or renderer tests.

Each checkpoint compares the full 24-byte Boss, 16 additional state bytes,
440x26-byte bullet pool,16x42-byte gather pool,96x16-byte spark pool, both
scratch templates, 48 explosion bytes, scalar globals, shared RNG cursor and
ordered hit/sound/circle/item/point/HP/progression requests. Full fields are
compared before hashing; gzip is only private trace storage. Target controls
inject damage at the actual hittest boundary and check that the against-Boss
flag is set then restored. They intercept circle geometry, item/point
allocation, HP pixels, audio, dialog/bonus and host delay, without claiming
those adapters have been migrated.

Preserved target details include damage-word-to-byte truncation before HP
subtraction (even 256 damage can play a hit sound but remove zero HP),
wrapped 16-bit target subtraction before movement division, retained velocity
inside the center dead band, phase 4's second 600-frame test **after** hittest
increments the clock, and assigning the final bonus byte directly to zap
(including zero). `Subpixel::None()` is `-15984` (−999 pixels), not INT16_MIN.
Small explosion creation selects slot 1 whenever slot 0 is alive, overwriting
slot 1 if necessary; its unused byte survives. State updates do not age these
explosions; the separate `prepare_render()` step below owns render-side aging.

Reproduce the complete current control set from this worktree:

```bash
cmake --build .analysis/port64/linux-live-v1251 --parallel 4
python3 port64/verify_orange.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-orange-contracts \
  --output-dir .analysis/port64/orange-v1258/regenerated
```

Historical original traces are under `orange-v1258/cpu-linux` (34,040
checkpoints) and `pattern-linux` (2,560). The final Linux, Wine/Windows PE32+
and optimized GNU UBSan/bounds executables replay both original traces with
`--native-only --reference-dir`; these host replays do not reexecute the CPU.
Receipts are`orange-v1258/replay-{linux,windows,ubsan}/receipt.json` and
`pattern-{linux,windows,ubsan}-final/receipt.json`. Both trace digests agree
on every host: `ebfb2fd4...` and `6e80f57d...`. Native product formats and
the existing OP/resource/player/shot/enemy/midboss image regressions are
independently replayed by `port64/verify.py`; eight contract targets pass.
The current cross-product receipt is
`.analysis/port64/verification-orange-v1258-final/receipt.json`, source
manifest`717f96b9...`.
No DOS source or exact-acceptance state changes. Native Windows pacing,
complete original-scene video equality and game routes remain unverified.

## Stage 1 Orange foreground and native integration

`orange_render.cpp` adds the cached foreground plan and two small/one big
explosion lifecycles. `circles` owns the sixteen ten-byte logical records and
the default PC-98 midpoint circle outline. `State::update()` advances these
once per simulation frame; host repaints only read cached draws. Circle updates
precede sparks/player updates, Boss shot hits and immediate effects precede
items/gathers, and Boss foreground precedes midboss/enemies. Outline circles
render after enemy bullets. Background selection uses the **pre-update** Boss
phase/frame, matching the original loop order.

Independent original CPU execution compares 900 foreground/explosion controls
and 918 circle controls on GNU Linux, MinGW PE32+ under Wine and optimized GNU
UBSan/bounds. Scope is `MAIN main_01 0AAF:6E7B` foreground, `2D9C/2E65`
explosion render, `1B5A/1BA6` circle add, `1BF2` update and `1C28` render;
load2000 gives CS2AAF, DS8000. Draw adapters capture ordered sprite/circle
geometry, white-plane arguments and scale requests. All 48 explosion bytes,
160 circle bytes, damage retention, palette tone/change flag and big-explosion
clock are compared. Of the circle controls, 150 execute the actual library
`0000:11EC` GRCG circle routine and compare its 32,000-byte write mask, including
default-rectangle edges, zero radius and row399. This is independent pixel-mask
evidence; it is not a hardware color/page/timing claim.

Preserve these observed quirks:

- Circle center division uses signed IDIV (negative fractions truncate toward
  zero), while sprite coordinates use SAR (floor). Age17 sets flag2 and is
  absent from rendering, despite an older DOS source comment suggesting it draws.
- Small explosions use 64 points at angle increments4 and strict screen
  bounds; the big explosion uses16 points/increments16 and inclusive bounds.
  MIKOD is actually48x48 although the target clips/transforms it as64x64.
- The final Boss explosion sprite uses the library's real twofold enlargement;
  it is distinct from the48x48 MIKOD sheet. Damage flashing does not clear the
  Boss damage byte. White-plane arguments are FFC0/mask0.
- Big-explosion flash advances its retained signed clock only while alive,
  resets the clock on an inactive render, and preserves tone until another
  palette action. Repainting does not age explosions or change this clock.

Native MAIN now consumes real shot hits, homing, bullet/gather/spark effects,
item allocations, circle requests and Boss bonus deltas. Private MIKOD.BFT,
ST00BK.CDG and ST00.BB are decoded with explicit geometry checks. The host
composes entrance masks, backdrop/color-zero changes, white damage sprites,
explosions and palette tone. Background BB/palette composition follows the
maintained DOS owners; this batch does not independently compare complete
original background/color VRAM or PC-98 dirty-page behavior. It uses full host
redraw rather than EGC copies and invalidated tiles.

`--orange-screenshots DIR` is an **explicit diagnostic start**, bypassing the
unported blocking pre-boss dialog with stopped scrolling. It retains normal
initial power1, actual shots/items and the shared RNG. Eight scenarios cover
Normal/Lunatic, Reimu/Marisa and shot/idle. Fifteen screenshots per scenario
include all eight phases, entrance circles/mask, active attack snapshots and
explosion frames8/16. Linux/Wine/UBSan agree on all120 BMPs and gameplay
counters. Idle reaches the pending dialog at frame4628 with Boss bonus0;
shots reach it at4225 Normal/4231 Lunatic with bonus12800. Repaint and three
additional pending-dialog ticks leave simulation clocks unchanged.

Ordinary STD still does not activate Orange: its original stopped-scroll,
back-page and completed-dialog contract must be implemented first. The native
diagnostic stops at phase255/frame0 before the post-boss dialog instead of
silently skipping it. Resident graze, dialog, clear bonus, stage progression,
audio/HUD/point numbers and player death/Bomb remain unported. Invincibility
requests reach the bullet context but the player countdown consumer is still
absent. These fixtures establish native integration, not a complete playable
Stage1 or original full-scene equality. Windows execution is via Wine, not
native Windows pacing validation. Semantic remains paused.

Reproduce from this worktree (create the screenshot directory first):

```bash
cmake --build .analysis/port64/linux-live-v1251 --parallel 4
python3 port64/verify_orange_render.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-orange-contracts \
  --output-dir .analysis/port64/orange-render-v1259/cpu-linux-final
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --output .analysis/port64/verification-orange-render-v1259/receipt.json
```

CPU receipts: `orange-render-v1259/cpu-{linux,windows,ubsan}-final/receipt.json`.
Render trace SHA`bb6b250a...`; circle trace SHA`d46f3ed2...`. The current
executables also retain all36,600 earlier Boss state/pattern checkpoints:
`regression-{state,pattern}-{linux,windows,ubsan}/receipt.json` under that
directory. Cross-product receipt: `verification-orange-render-v1259/receipt.json`,
source manifest`1e1e0fbe...`. `integration-review.json` records unchanged prior
shot/combat/midboss images/counters, UBSan image agreement and a negative
control that deliberately rejects an original-CPU hook. The callback wrapper
stops Unicorn explicitly and rethrows; callback errors cannot silently pass.

## Dialog VM and natural Stage 1 Boss flow

Native Stage 1 now reaches Orange through the real stopped-scroll/back-page
activation gate, blocking pre-boss dialog and resource reload. Defeat/timeout
then resumes the same script cursor for the post-boss dialog. This replaces
the v1259 ordinary-flow limitation above. The stage-clear bonus/transition
consumer is still absent, so simulation stays frozen after the post-dialog.

`port64/dialog.*` owns the immutable script buffer, retained consumed offset,
16-bit cursor/side/default parameter, command events and asynchronous waits.
An inner `#` exits a text box; the outer `#` ends the scene. `$` waits for key
release followed by a new press before stopping its current command level.
Held input speeds text but cannot dismiss a wait. Three-digit optional numbers
and inherited second-argument defaults preserve original consumption. Filenames
consume their separator and are limited to12 bytes. Fades retain six-unit tone
steps; palette TRAM text remains a separate white layer. Full host fade/input
latency is not inferred from the intercepted CPU wait/fade controls.

An independent original CPU Oracle executes pinned MAIN at load2000, DS8000,
CS2AAF (unloaded main01 0AAF), including2A7C dialog parse,26CC commands,
25DA/26A3 parameters and2454 activation. All16 actual dialog files and8
synthetic controls are tested with held/released input:48 cases,76 complete
scenes and18,768 ordered events agree, including final consumed offsets and
cursor/side/default state. Another768 speed/page controls compare the actual
dialog call and STD counter side effect, including invalid/nonactivating page2.
Input, rendering, file/CDG, audio, waits and fades are explicit boundary adapters;
this is command/state equivalence, not original complete-video equality.
The receipt attests both target and Unicorn engine. Hook failures explicitly
stop/reject the CPU; the native consumer does not generate expected traces.

This uncovered an integration error in the v1259 diagnostic. Actual `_DM00`
pre-boss commands clean slots128..255, loadST00.BB1 thenST00.BB2 and draw128.
The old diagnostic incorrectly retained midboss sprites (ST00.BFT/BMT). Native
ordinary flow now executes these commands and the diagnostic explicitly
installs the same battle bank. The BFNT headers describe four32x48 sprites
at128..131 and eight64x80 at132..139. Each file updates the active palette;
BB2 color0 is black. Previous geometry/state proofs remain valid, but the old
120 images did not establish original battle-sprite/palette correctness.

The scene composes blue stipple boxes, CDG portraits, actual script sprite
commands and Japanese text from a user-supplied2048x2048 monochrome PC-98 font
BMP. The supplied emulator font stays private. Six independent Python
SJIS-to-ISO2022JP/PIL pixel controls compare1,536 glyph pixels with the native
lookup. The Stage1 scene supports its actual resources; other routes' parsed
CDG-free/scroll/audio requests still need consumers when those routes are ported.

Eight natural scenarios start from the real OP/menu handoff at frame0:
Normal/Lunatic × Reimu/Marisa × shooting/idle. They inject no enemies, damage,
scroll stop or Boss entry. Five snapshots each cover the pre-dialog first wait,
correct battle bank, attack, post-dialog first wait and final scene. Gameplay
frames and RNG freeze throughout dialog; key release/press is explicit.
Pre-dialog starts at6652 idle or6548 shooting, both back-page1. Reimu/Marisa
retained pre/post offsets are1081/1257 and707/857. Three additional ticks after
post-dialog keep the pending stage-clear state frozen. Linux/Wine/optimized
UBSan agree40 BMPs/counters. Earlier shot/combat/midboss images are unchanged;
120 diagnostic Boss images now use the corrected battle bank. The current
Windows Orange binary was relinked, so it independently reruns1,818 original
render/circle controls and36,600 retained original state/pattern checkpoints
rather than inheriting a stale executable SHA. UBSan also reruns these gates;
Linux's unchanged Orange contract SHA permits its prior bounded CPU evidence.

Actual Windows PowerShell execution now passes all nine contracts and the40
natural BMPs/48 counters, equal to Linux/Wine. This is headless execution and
does not measure GUI pacing or Windows compiler availability. The PE32+ product
was cross-built with MinGW. No DOS source, executable, launcher or exact ledger
state changed. A versioned native package is installed at
`D:\Entertainment\Game\Touhou\th04-reconstruct\port64-preview\v1260`,
and the root `start-th04-port64.bat` opens the Stage1 preview with explicit
private font/HDI paths. The previous root native executable is backed up in
that package. No game/font assets are checked in.

Reproduce the focused original CPU and cross-product checks:

```bash
python3 port64/verify_dialog.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --exe .analysis/port64/linux-live-v1251/th04-port64-dialog-contracts \
  --output-dir .analysis/port64/dialog-v1260/cpu-linux-final
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-dialog-v1260-final/receipt.json
```

Native Windows replay (requires a fresh output directory):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File port64/verify_windows.ps1 `
  -ExecutableDirectory .analysis/port64/windows-live-v1251 `
  -Hdi D:\Entertainment\Game\Touhou\th04-reconstruct\play-normal.hdi `
  -FontBitmap D:\Entertainment\Game\Touhou\th04-reconstruct\FREECG98.bmp `
  -OutputDirectory .analysis/port64/windows-dialog-check
```

Receipts are `dialog-v1260/cpu-{linux,windows,ubsan}-final/receipt.json`,
`integration-review.json`, `native-windows-receipt.json` and
`verification-dialog-v1260-final/receipt.json`. Whole-game progression,
resident graze/clear bonus, later stages, death/Bomb/HUD/audio and Ending/save
remain unported. Stop general semantic work; port the next actual consumer.
