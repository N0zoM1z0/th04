# Extra entry, dialogs and bosses

## Ordinary Extra OS route and controller comparison (v1357)

`verify_window_extra.py` requires an independently checked, physically earned
six-stage Normal/Reimu A window receipt and separate Scores restart. It copies
only that route's own files into fresh private test saves and uses actual OP
Extra selection. No unlock, actor, hit, life, score, clock or transition is
injected. Live const advice supplies observations to an external OS controller;
original ordinary input remains the game's only key source. Every launch is
muted on a checked private Xvfb server, never the Windows host display.

The first ordinary xdotool trial reaches MAIN stage6/rank4 Game Over at frame
25,595 with eight actual misses and no Continue. This is a failed no-Continue
clear; full-name/clear-file/restart acceptance does not follow. Preserve its
terminal/trace/actions/files and 486-input consumer source archive.

The controller now has an optional `--key-driver xtest`: one persistent X11
connection sends the same release-before-press ordinary OS events and completes
one server round trip per changed key set. Independent private server keymap
checks pass 270 changes per driver across directions, Z/X, Shift, Return/keypad
Enter/Escape and releases. Changed DISPLAY and unsupported keys reject; closing
releases held keys. Measured request-cost median/p95 is 36.38/89.69ms for the
original per-key subprocesses versus 0.163/0.224ms for the persistent driver.
This demonstrates controller cost, not the cause of a particular death, game
survival, game FPS or physical-key timing. libX11/libXtst identities are pinned.

The second GNU trial completes its terminal/independent checks: 30,388 route
refreshes, 228 registration refreshes and 790 separate Scores restart refreshes.
Every MAIN row is program1/generation2/stage6/rank4/ReimuA/credit0; Game Over
never occurs. Last MAIN frame27,832 has lives5/misses3 and5,293,250 score units.
A complete eight-A-gaiji entry (`aa` repeated8) with credit0 and rank4 clear flag
appears in the actual physical IN_MOVED_TO snapshot and final saved score.
Nine other decoded checksum/payload partitions, including earned Normal
admission, and CFG remain unchanged. Fresh OP and the separately launched Scores
process preserve full physical file hashes. All terminal E/audio checks pass.

The actual gameplay's 5,963 changed key sets have controller request median/
p95/p99/max0.254/0.511/1.390/9.101ms. The complete schedule has no resync, maximum
404 bullets and12,638 MAIN after-update slowdown2 records. Those include stage
transition/fade/battle work; they do not establish dense Lunatic or physical
keyboard timing. Only native GNU ReimuA/Extra is accepted by this window route;
other host/character/shot combinations and original whole-route equivalence
remain open. The first failed Extra still fails.

The compiled native `maine_extra_route.cpp` orders MAIN fade, delay100,
registration, congratulations, verdict and fresh OP. Generic window trace
directly distinguishes registration/MAINE/fresh OP; the inner MAINE phases are
source-routed and supported by preceding bounded component Oracles, not
separately identified by this generic window trace. No new original full-pixel
or inner-phase timing claim follows.

```sh
xvfb-run -a -s '-screen 0 800x600x24 -nolisten tcp -noreset' \
  python3 port64/verify_window_extra.py --key-driver xtest \
  --exe .analysis/product-v1356/linux/th04-port64 --exe-sha256 PINNED_SHA256 \
  --hdi /path/to/zun.hdi --font /path/to/FREECG98.bmp \
  --normal-route /path/to/passed-normal-route --output FRESH_DIRECTORY
```

Receipts, complete launch vectors, first failed trace, server keymap probe and
source bridges: `.analysis/port64/window-route-v1357/`. Actual Normal routes
and complete deadline-reducer scope are in [host-window evidence](host-window.md).

v1349 narrows the former natural-survival gap: a key-only ordinary prototype
clears Reimu Extra in29611 route advances on GNU/UBSan/actualWindows after a
same-host physically earned Normal unlock. Three misses/eight Bombs occur;
no hit suppression, unlock injection or Continue. Registration/save/fresh OP
and whole recorded streams/final saves agree. This is a logical prototype
route, with deferred presentation; complete public-runtime/rank/shot/timing
acceptance remains. See [route ownership/replay](stage-lifecycle.md#ordinary-key-only-logical-routes-v1349).

The v1310 source joins actual OP Extra selection, ST06 resources and STD waves
to the complete timed midboss. The v1310 stop boundary was the Mugetsu dialog; v1312 below supersedes
that frontier. Gengetsu, unlock persistence and complete ordinary Extra play
remain required. The long fixtures change only the OP unlock bit and explicitly
disable player-hit consumption. Two ordinary 120-tick entry smokes are narrower
controls. Every launch is muted without opening an audio backend.

## Target and ownership

Pinned MAIN SHA-256 is
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
Its candidate-local-attested provenance remains a gap. Session preflight and
the live MAIN Ghidra database attestation pass before target execution.

Observed setup is relative `13A9:AA88..AB48`; the midboss body/helpers are
`13A9:0C1F..1008`, foreground `0AAF:1E5A..1EAB`, and activation/reset
`13A9:6454/642C`. The actor starts at frame 5400. Its HP field is an orbit
radius; the original owner never consumes shot-hit damage. Seven phases drive
orbit/ring/cloud/bounce/dual-ring/drop/exit behavior. A complete retained
midboss-only sequence takes 2594 ticks and drops four dream, four big-power
and one one-up items. The field is not a portable kill threshold.

`stagex.*` owns partial setup/reset and resource requests; `midbossx.*` owns
the actor, shared RNG/bullet scratch and cached foreground geometry. ST06 has
24 stage patterns at global128..151, no BMT, 64 MPN tiles, a384x192 backdrop,
one128x128 portrait and the common `_DM06.TXT` dialog script. Private independent
FAT/PAR input extraction records every used resource's size and digest in
`.analysis/port64/extra-v1310/resource-manifest.json`. The dialog is loaded but
not executed by this batch.

## Render boundary findings

Observed original gameplay `0AAF:0098..0213` calls bullet rendering at013C
and score update at0204. An independently executed score update at load2000
extends lives3 to4, sets clear0 to20 and leaves the bullet pool unchanged.
The native completed render therefore retains its own clear/zap state before
the score tail; the next update consumes the new clear state. Repaint cannot
substitute the already advanced score state for completed foreground state.

During clear, enemies can spawn an unconverted pattern after bullet update.
Observed raw tiny entry `0AAF:1A56` checks the first planar byte for0x80 before
drawing. Session conversion starts at global20; globals0..19 retain planar
data. The native renderer resolves their real sheet/image ownership and applies
the raw header predicate. All 23 unique player/death/enemy inputs tested here
begin with0 and legitimately produce no writes. This is not an invented empty
sprite: original kernel execution at two loads proves the return. The helper's
header0x80 branch is not exercised by these asset inputs; converted tiny
kernels have separate existing controls.

## Replays and limits

Run into a fresh private directory:

```sh
python3 port64/verify_extra.py --target ../../targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-extra-contracts \
  --setup-exe .analysis/port64/linux-live-v1251/th04-port64-stage5-contracts \
  --score-exe .analysis/port64/linux-live-v1251/th04-port64-score-contracts \
  --hdi ../../runtime/images/zun.hdi --output-dir NEW
.analysis/port64/linux-live-v1251/th04-port64 \
  --hdi ../../runtime/images/zun.hdi --font-bmp SUPPLIED-FONT \
  --extra-checks NEW-FRONTEND --mute
```

GNU8.4 and optimized UBSan each pass35 contracts,1466 actor cases/6652 records,
256 setup cases, and138 complete raw tiny screens/35,328,000 pixels. Original
instructions execute at loads1000/2000. Full22-byte actor, template,440x26
bullet pool, shared cursor, regular/special parameter, events and draw requests
agree. Independent resource/item/sound/sprite-request and DS/SS adapters remain
explicit; isolated retained sequences omit other actors.

Each host's eight character/shot/repaint actor scenarios reaches the genuine
stopped-STD/scroll/back-page gate at frame11196, with2593 active midboss frames,
nine drops and six phase changes. Held pending ticks freeze state/RNG/resources;
native crosshost/repaint complete BMP and journal comparisons are distinct
from original complete Extra VRAM. Two ordinary startup scenes pass per host.
Source-only radius-decrement and erroneous raw-header-draw mutants are rejected.
The prior two-load Bomb join is separately regressed after shared state/render
changes; its captured pre-state/page/resource and hardware adapters still apply.

Private `platform-review.json` binds291 maintained files and108 AMD64 products.
Current MinGW Windows builds, but PowerShell fails before startup at WSL vsock;
Windows execution is pending. Git metadata is read-only, so code/evidence remain
uncommitted; full recovery patches preserve preceding v1308/v1309 changes too.
No GUI publication, full-route/timing/audio or historical exact promotion follows.

## Mugetsu core and render requests

v1311 implements `mugetsu.*`: three entrance/teleport transitions, seven
attacks, phase2 selection/cycles, final attack, shot/Bomb invincibility, reward
and explosion ownership. `mugetsu_contracts.cpp` serializes every retained
field and pool; `verify_mugetsu.py` executes independent original instructions.
This component is not yet dispatched by the frontend. Ordinary Extra still
holds at the stopped-STD Mugetsu dialog gate11196. Joining `_DM06`/battle sprites,
actual shots/palette/pages, then Gengetsu remains the next coherent batch.

Observed MAIN core is relative `13A9:459F..4F5F`: fifteen bounded functions,
including near transitions462B/469A/478E, callbacks4884..4BF4, hit4C29 and far
update4C5B. Foreground is `0AAF:6AC6..6B57`, wing helper6B57..6BA2;
shared background is **`0AAF:7E89..7F1A`**, not13A9. Original setup
`13A9:AA88..AB48` installs the0AAF:1658 lower filler atDS:BA8C. The background
harness must install that callback; a null callback is a different initial
state and loses the phase2 filler request. DS/SS and downstream graphics
consumers are explicit adapters, not a claim to emulate original video hardware.

The original intro circle callee is0AAF:1BA6 (request flag0), not1B5A (flag1).
A first flag1 candidate fails record113/field43; the retained source-only mutant
reproduces the rejection. Frame36 retains the preceding gather color. The short
teleport's frame32 sound check occurs inside its>=48 branch and is unreachable.
Do not repair this control flow in the native semantic owner. Phase2 selection
may consume repeated RNG words until the new mode differs from the last; a
constant RNG fixture can hang and is not a valid full-sequence test stream.

Original bonus multiplication wraps its16-bit product before adding to the
32-bit score:100 units produce62464,200 produce59392. Original cases3038 and2812
respectively confirm these values at two loads. Point requests still emit
100/200 points of1280 each. Bomb refreshes the private invincibility to32, then
decrements it before hit consumption; hidden/teleport sprites keep their own
clock path. Foreground damage advances a byte flash cycle, clears damage and
omits wings in that branch. Wings136/137 draw at left-15/left+33 only for a
nonzero counter>=32 or odd; body128..135 and the large explosion use their
own paths. Two independent mutation controls reject the circle flag and wing
blink changes. Unsupported post-Mugetsu phase dispatch fails explicitly rather
than invoking the normal next-stage departure; the Gengetsu dialog owns it next.

Complete original controls run at loads1000/2000, DS8000 and SS7000.3499 core
cases yield16251 records, including retained timed/hit sequences and dense/sparse
allocation. Core functions, actual regular/special tune/add, gathers, RNG,
shot wrapper, score multiplication and explosion initialization execute.
Injected damage and circle/HUD/item/point/sound consumers remain adapters.
The zero-damage owner-only timeout reaches phase255 in9299 ticks, omitting
ordinary actors and per-frame pool aging/rendering. It is not a full Extra route.

1610 foreground and5120 background cases independently execute original caller,
wing and shared explosion code, comparing full damage/flash/explosion/palette
state and ordered draw requests. Sprite/CDG/BB/filler/color/video consumers are
request adapters; no complete original Mugetsu pixel comparison is accepted.
The current GNU8.4 and optimized UBSan each pass36 contracts and both core and
render reference replay. All36 preceding products on each of these hosts are
byte-identical to v1310, preserving its scoped reference evidence. MinGW13
cross-builds37 current products, but actual Windows is unexecuted here: WSL
`UtilBindVsockAnyPort` rejects PowerShell before startup. Git staging separately
rejects a read-only `index.lock`. No commits/push or GUI publication is claimed.

Fresh-output commands:

```sh
python3 port64/verify_mugetsu.py --target ../../targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-mugetsu-contracts \
  --output-dir NEW-CORE
python3 port64/verify_mugetsu_graphics.py --target ../../targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-mugetsu-contracts \
  --output-dir NEW-GRAPHICS
# Repeat with the UBSan executable; retained original references may be read
# using --reference-dir PRODUCER. Never overwrite the producer directory.
ctest --test-dir .analysis/port64/linux-live-v1251 --output-on-failure
ctest --test-dir .analysis/port64/ubsan-live-v1251 --output-on-failure
```

The private core producer manifest4237808a... differs from current9dad439f...;
`platform-review.json` binds the current296-file manifest and111 AMD64 products.
Consumer receipts link the independently produced original receipt and verify
its full fixtures/record digest. The verifier now streams gzip rather than
writing an expanded449911018-byte native trace before compression. Cleanup
removes45051904 allocated bytes of own superseded streams, temporary source,
compiled mutants and copied logs;3887 protected files remain unchanged. Final
original/native references, three caches, pinned inputs and existing recovery
remain. Logs are retained with hash readback; copied logs consume space and
this figure is not summed with earlier cleanup. Recovery patches cover the
complete current diff, including earlier v1308/v1309/v1310 changes and untracked
files. No exact state or whole-game/audio/timing/Windows acceptance follows.

## Actual first Extra dialog and Mugetsu battle

v1312 joins the ordinary frontend gate at frame11196 to non-EMS resource init,
retained `_DM06.TXT`, resource exit and the next MAIN tick11197. The first dialog
retains offset987. The original script independently reaches1736/1961 for the
remaining two scenes; these are producer controls, not integrated Gengetsu or
Extra completion. The observed original entries are relative MAIN
`0AAF:2A7C`, init`2C39..2CFE` and exit`2CFE..2D9C` at load segments1000/2000.
All512 character×byte-counter cases agree, including wrap255→0. Init frees
Bomb CDG slot0, loads player faces at2; exit frees2..7 and8..10, chooses BSS7
on prior counter0 and BSS8 otherwise, then reloads character Bomb at0.
BSS7 contains three portraits; Marisa's KAO1 contains five, Reimu's KAO0 six.
Cached native files replace EMS/file allocation; EMS execution is unaccepted.

The first script loads ST06.BB1 body128..135 (64×96) and BB3 wings136/137
(48×96), cleaning previous Extra stage globals138..255. The shared Extra
background consumes cached pre-update phase/clock, picture, lower filler and BB
requests. Foreground caches body/wings, damage flash and explosions after the
actual Bomb lifecycle. During Bomb the two physical pages retain49..176;
frame176 restores the background callback for the following update. Existing
ordinary Bomb original/state/indexed/RGB controls regress at both loads.
No full original Mugetsu body/background pixels or full MAIN loop is accepted.

GNU/optimized UBSan each execute16 real OP/Extra STD/first-dialog/Mugetsu scenes:
two actual characters×two shots×idle/shoot×paint modes. Actual resident fields
and resource tuples must match the requested character/shot. All208 outputs,
including192 full BMPs, agree across hosts and repaint pairs. Shot scenes
consume real shots and one227-frame Bomb; HP clears through real damage.
Idle scenes reach the timer. Ten phase edges end at254/255, then20 held
shoot/X ticks cannot advance frames/RNG, reload resources or take the ordinary
next-stage/Ending path. The first699 dialog requests and13 resource requests
agree with the independent original. Long controls explicitly disable player
hit consumption and adapt only the OP unlock bit; these are not survival routes.

The independent comparator rejects a missing first dialog request, wrong Bomb
slot and advanced cursor. Its resource comparison exposed the earlier fixture
error: character selection responds to left/right, but v1310 and initial v1312
used down. Marisa-labelled scenes actually selected Reimu. Old receipts remain
historical; their frontend character scope is narrowed to Reimu, while isolated
component claims are unchanged. Corrected fixtures use right and assert resident
character/shot plus original character-specific resources. Negative traces remain.

```sh
python3 port64/verify_extra_dialog.py --target ../../targets/th04/main.exe \
  --hdi ../../runtime/images/zun.hdi \
  --resource-exe .analysis/port64/linux-live-v1251/th04-port64-mugetsu-contracts \
  --dialog-exe .analysis/port64/linux-live-v1251/th04-port64-dialog-contracts \
  --output-dir NEW_DIALOG_DIR
.analysis/port64/linux-live-v1251/th04-port64 --hdi ../../runtime/images/zun.hdi \
  --font-bmp PRIVATE_FONT --mugetsu-checks NEW_FRONTEND_DIR --mute
python3 port64/verify_mugetsu_join.py --original-dir NEW_DIALOG_DIR \
  --linux-dir NEW_FRONTEND_DIR --ubsan-dir NEW_UBSAN_FRONTEND_DIR \
  --output-dir NEW_REVIEW_DIR
```

Private `.analysis/port64/mugetsu-join-v1312/` binds current301 source files,
111 AMD64 products,36 contracts per executed host, original request/component
regressions, failed environment commands, protected cleanup and complete recovery.
Windows cross-build succeeds; actual execution still fails before PowerShell
with WSL UtilBindVsockAnyPort. Git add fails with read-only index metadata, so
no new commit/push is claimed. Root CI requires writable repository-local
XDG_CONFIG_HOME/XDG_CACHE_HOME; the default external user config is read-only.
All launches are muted with no audio backend. Historical exact ledgers are unchanged.

Next: independently recover Gengetsu state/patterns, wave raster, custom columns
and thick lasers; join second/third retained dialog/resource boundaries, Extra
completion and unlock/save publication. Full HUD/OP/audio/config, ordinary
Linux/Windows routes and dense Lunatic timing/performance remain separate gates.

## Gengetsu core, foreground and wave components

v1313 is a component preparation for the real Extra continuation. It does not
advance the frontend past its frozen Gengetsu-dialog gate. The complete goal
still includes second/third retained dialogues, ordinary Gengetsu combat,
Extra completion/unlock/save publication, HUD/OP/audio/config and Linux/Windows
full-route/save/timing tests.

Target SHA-256 remains
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`,
size156258, MZ header6144, relocations1136. MAIN database attestation and root CI
pass with repository-local Ghidra XDG directories. Canonicality remains
candidate-local-attested; no DOS exact ledger is promoted.

Observed original ownership is relative MAIN13A9:BE5E..CC5B for core helpers,
all12 patterns, waveform movement, hit shielding,16 columns and full update
(including the10-word table after CC47 RETF); foreground is0AAF:846F..85FC;
shared background0AAF:7E89..7F1A and Bomb wings0AAF:6B57..6BA2 are retained from
v1312. Wave kernel0000:3FD0..40F3 includes its local row renderer at40AA and
self-modified height byte40AE. Raw ranges/digests are under
`.analysis/port64/gengetsu-v1313/target-functions.json` and bounded disassemblies.

Two-load original execution establishes3,884 core cases/47,535 records,
including full pools/RNG/column padding/laser scratch+two slots, signed and
byte-wrap edges, all12 retained160-tick pattern scenarios and complete isolated
phase0..255 sequences. These sequences omit foreground and gameplay aging.
Original hit/RNG/tune/add/gather/laser/explosion/score helpers execute; shot
payload and circle/HUD/item/point/sound consumers are explicit adapters.

The3,458 foreground cases compare damage/flash/angle, explosion aging/palette,
ordered two-part body/wave/Bomb-wing/zoom/laser/column requests and immutable
column padding/laser records. A wave call pushes the WORD at DS24B8, including
adjacent24B9, but the raster reads only its signed low byte. Damage is retained
while waving; visible columns truncate signed Q12.4 division toward zero.
Sprite/wave/zoom/geometry and common explosion GRCG-disable calls are request
or hardware adapters, not accepted full-scene original pixels.

The independent waveform producer executes all original kernel instructions
without semantic callee interception.774 complete640x400 indexed screens agree
at loads1000/2000 and with both maintained native consumers:198,144,000 pixels
per load. ST06.BB1(64x96),BB2(48x96),BB3(48x96), every angle, all amplitude low
bytes except the explicit zero-wavelength fault, signed coordinates, negative
lengths and high-word arguments are covered. BFNT plane staging and visible
A800 GRCG shadows remain adapters; physical aliases/pages/scroll/timing are
outside this kernel proof. Odd-byte rows and heights above96 are explicitly
unsupported by this Gengetsu consumer.

Independent mathematical generation `min(127,trunc(128*sin(a)))` with quarter
symmetry agrees with all256 observed sine bytes; no target byte array is
embedded. A rejected candidate incorrectly alternated amplitude only for
negative lengths. Original AH is retained as the flip byte, so positive
lengths>=256 alternate too; case750 exposes pixel13537. The corrected candidate
and maintained raster pass. Zero wavelength produces original DIV faults at
both loads and a host domain_error. Hardware callback rejection preserves its
cause. Four private mutations reject wrapped-subtraction order, wave hit
shielding, phase2 pattern-count selection and positive-length alternation.

Replay from the native worktree, always with NEW output directories:

```sh
python3 port64/verify_gengetsu.py --target ../../targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-gengetsu-contracts \
  --output-dir NEW_CORE
python3 port64/verify_gengetsu_graphics.py --target ../../targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-gengetsu-contracts \
  --output-dir NEW_FOREGROUND
python3 port64/verify_super_wave.py --target ../../targets/th04/main.exe \
  --hdi ../../runtime/images/zun.hdi \
  --exe .analysis/port64/linux-live-v1251/th04-port64-wave-contracts \
  --output-dir NEW_WAVE
```

`--reference-dir` replays an attested original producer and preserves its
receipt/source identity separately. Core producer manifest71212510... differs
from current1d15d270...; foreground/wave prototypes retain their own candidate
and producer script hashes. GNU/optimized UBSan each pass38 CTests; current
117 AMD64 products bind312 source/verifier files. Full core/foreground/wave
replays and four mutations pass. Prior37 GNU/UBSan products are byte-identical,
so the existing bounded Mugetsu actor-control frontend remains applicable;
no new Gengetsu frontend or GUI publication claim follows.

`.analysis/port64/gengetsu-v1313/platform-review.json` SHA-256
`a496e170dd257983244bbed05005d1276df36c066d8d5e68e645a87f256692cd`
binds the current proof. Cleanup retires only own superseded fixtures/streams/
probe binaries and shares complete equal immutable gzip streams after full
raw readback:198,160,384 allocated bytes reclaimed,4,872 protected files.
Negative JSONs, replay sources, pinned inputs, three current caches, all earlier
references/recovery and current final references remain. Never replay a writer
in those completed directories. Windows cross-build succeeds but actual
PowerShell still fails at UtilBindVsockAnyPort; Git add rejects read-only
index metadata. Complete recovery preserves all current changes versus HEAD;
no new commit/push, audio backend or exact acceptance is claimed.


## Second dialogue and live Gengetsu join (v1314)

Original MAIN relative `13A9:ACB3..AE86` and reset `13A9:A4D1..A517`
are reviewed against the pinned 156,258-byte MZ (SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`).
At the second-dialogue branch, 256 cases at loads `1000` and `2000` agree
with both native contract executables. `verify_extra_handoff.py` executes the
bounded original instructions; clean/dialogue/CDG/BB/callback consumers are
explicit request adapters. The accepted fixtures do not exercise third-dialogue
all-clear/end-extra hooks. Initial BSS zero is an observer adapter, not startup
execution evidence. No whole MAIN or full resource-consumer claim follows.

The original sets Gengetsu-started before reset, positions both cur/prev at
`3072,1536`, selects sprite 128/hitbox `384,768`, resets only small-explosion
alive flags, frees CDG16/BB then loads `ST06BK2.CDG`/`ST06B.BB`, and enables
Bomb. Shared shield, wave/private fields, column padding and 72 laser bytes
remain preserved; a source-only shield-reset mutant is rejected at case 1.
The native shared-prefix/dialogue suspension resumes its suffix exactly once;
clock 0 is retained until the next MAIN update. Cached foreground preparation
and repaint preserve state/RNG and complete captures. BGM-title/overlay/HUD
consumers remain unjoined adapters.

`verify_gengetsu_join.py` passes 16 actual OP actor controls per GNU/optimized
UBSan: both characters/shots, idle/shoot, repaint/no repaint. 464 files/448 BMPs
agree across hosts, and 699/501 first/second dialogue events agree with the
independent v1312 original-script producer. Timed and shot-driven trajectories
reach both boss phase ends; shooting cases run two genuine 227-frame Bombs.
Held release/press pauses freeze MAIN/RNG; the third-dialogue gate freezes
MAIN while holding X/shot. Player-hit consumption is disabled and only the
unlock bit adapted. This is native cross-host pixel equality, not original
whole-scene equality or natural survival.

Current source identity is `94e9ca771bceb68e433be8c4fc073443e979695ef740a0107c34f24e5303e14c` (315 files).
117 AMD64 products build; GNU/UBSan each pass 38 contracts. Current replays
retain 3,884 core cases/47,535 records and 3,458 foreground scenes; unchanged
wave executables retain v1313's bounded 774-screen original proof. All 192
v1312 Mugetsu-prefix BMPs agree. Each host's 12-scene Bomb regression matches
all 387,072,000 stream bytes/2,724 frames (SHA-256
`e9cadcc4e9bdb03fb94e2012cb07d9c5be7e5bae55c446458b2245909237cc78`).
A first core replay rejected a changing source manifest after its trace checks;
only the fresh frozen-source `core-linux-replay-final` receipt is accepted.

Private receipts under `.analysis/port64/gengetsu-join-v1314/` include
`platform-review.json` (SHA-256 `87deb19fefde3a10650be8d451bb0eaeafdcc5188257e70657a2b911fbbcccbb`),
`frontend-review/receipt.json`, handoff/core/graphics receipts, source-guard
negative, mutation and cleanup. Cleanup reclaims 1,510,817,792 allocated bytes
with 5,921 protected files passing readback; completed hardlinked outputs must
never be written again. Current inputs, three cache closures, prior references
and complete recovery remain. Windows fails before PowerShell at
`UtilBindVsockAnyPort`; Git add rejects read-only metadata. No current Windows
runtime, commit/push, audio backend or exact acceptance is claimed.

Next recover/replay the third-dialogue/all-clear/end-extra path and actual MAINE
Extra dispatch. Current native ScoreRoute accepts only ES_SCORE and Ending only
Good/Bad; neither owns Extra completion. Maintained DOS MAINE proposes Extra
registration -> congratulations -> verdict, a source candidate awaiting target
execution. Fresh OP currently creates `menu::State(false, resident.config)`;
its saved-score unlock reader is concretely unjoined. These source findings
route the next batch without claiming original dispatch acceptance. Then finish
full HUD/OP scores/Music Room/demo/audio/config and complete Linux/Windows
routes/save-restart/dense Lunatic timing. All launches remain muted.


## Third dialogue and Extra all-clear (v1315)

Original MAIN `13A9:ACB3..AE86` executes at loads `1000` and `2000` against
`verify_extra_departure.py`: 216 frame/graze/palette/homing boundary cases agree
with GNU/optimized UBSan. Clock 0 wraps resident graze before dynamic clean and
third dialogue; `AE0B..AE13` calls all-clear and increments to 1, then returns
without resetting homing. Subsequent calls clear homing; clock 416 stops at
original `0AAF:0D1F` with the original far-call stack. No fake return into leave
fade/next-stage suffix is accepted. Clean/dialogue/bonus children are explicit
request adapters, not full reward pixels. An early-homing-reset source mutant
is rejected at case 48. The initial observer probe accidentally used host
struct alignment for the BYTE+WORD fixture; explicit `<Bh` corrected it before
acceptance. A later hook probe's stopped Unicorn IP reflects the translated
address; accepted nonreturning boundary checks use the observed callback pair,
actual CS and six-byte caller stack instead. Failed directories are diagnostic.

The live native third dialogue uses retained `_DM06` offset 1736 -> 1961 and
non-EMS resource counter 2 -> 3 (BSS8 reload/Bomb slot restoration). It suspends
MAIN after its real player/shot/bullet prefix, resumes its suffix once, applies
all-clear once and drains ordinary score tails through clock 415. At 416 it
publishes an `extra_ending_requested` frontier and holds before MAIN blackout.
Eight actual OP shooting controls (both characters/shots, paint/no-paint) per
GNU/optimized UBSan agree on 264 files/256 BMPs and all original three-dialogue
requests. Each scene runs two 227-frame Bombs; held release/press waits and
post-exit X/shot ticks preserve MAIN/RNG. Hit consumption is suppressed and
unlock selection adapted. All 224 preceding-battle BMPs match the attested
v1314 producer. This is native capture equality, not original whole-scene
pixels or ordinary survival.

Current `effd292d9301d6920fcbce0cfb200abd3472a5b58bf252c901163646f993eb4f` binds 316 source/verifier files and 117 AMD64 products.
Both executed hosts pass 38 contracts. Replays retain 3,884 core cases/47,535
records, 3,458 foreground scenes and 256 second-handoff cases at two loads;
unchanged wave executables retain their bounded v1313 proof. Ordinary score
route regression re-agrees on 24 OP/STD/Quit/save/verdict/fresh-OP/second-MAIN
routes and four failed writers. Private receipts live under
`.analysis/port64/extra-clear-v1315/`; `platform-review.json` SHA-256
`006e0c5f61ad88d08ee03f93f53bbf84ae7ee6927ec3c1ed44f1252299466ccb` binds this batch.

Separate outgoing MAIN instruction controls execute `0AAF:0D1F..0D44`, the
actual fade16 body and GameExecl publication at two loads, 12 cases per load.
They observe ES_EXTRA `FD` before fade, 273 refreshes/final tone 0, unchanged
end-type and pending score, actual resident statistics and resource-release
order. Release/EMS/sound/palette/VBlank consumers are adapters; execl takes an
explicit FAILURE return solely to inspect the ABI. It is not a successful
process transition. `main-extra-original.json` and its replay script retain
inputs, full fields and fade traces.

Original decoded MAINE main dispatch/congratulations at two loads, both
characters/five held-key profiles, confirms delay100 -> registration ->
CONG04/14 -> verdict -> fade4 -> OP. Actual congratulations fade/delay/key
loops execute; init/registration/verdict duration-zero/PI/sound/exec consumers
are adapters. Packed MAINE SHA-256
`670de6ba907a2edbc1592de810acd92e5b89541d3dc35b70210171166d1713f8`, payload
`7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c` and main
extent `9a44bbf57b6d60fa16f8a78415d969b62c6bf1c596c36fc20a779749cedd92a8`
are checked by the producer. `maine-extra-original.json` records this order;
it supersedes the earlier source-only ordering question, without claiming a
native Extra MAINE, saved-score unlock or complete child/pixel proof.

Next join native MAIN blackout16 and a dedicated Extra MAINE owner. Preserve
registration before congratulations before verdict and the original fresh
process RNG boundaries. Do not route through normal Ending/Staff or ES_SCORE.
Fresh OP still needs actual saved-score clear-bit reading. Then complete
HUD/OP scores/Music Room/demo/audio/config and full Linux/Windows routes,
save/restart and dense Lunatic timing. All launches remain muted. Windows
interop still rejects before PowerShell; Git index metadata is read-only.
Complete recovery includes all tracked/untracked v1308..v1315 changes.
Cleanup reclaims 390803456 allocated bytes with
6744 protected files passing full hash readback. Equal completed
captures/streams are immutable aliases; future replay writers require fresh
output directories. No exact acceptance or commit/push follows.


## Extra MAIN blackout and dedicated MAINE route (v1316)

`maine_extra_route.cpp` owns the actual exit request at Gengetsu clock416.
MAIN sets only ES_EXTRA `FD`, preserves end-type/pending score and keeps its
resources/RNG frozen during 273 original-scheduled fade16 refreshes. Publication
then releases MAIN once and enters fresh MAINE LCG1. Registration begins after
100 further refreshes; real `HostStore` writer-close precedes its 18-refresh
blackout, Extra `CONG04.PI`/`CONG14.PI`, verdict and song fade4/fresh OP LCG1.
Congratulations preserves registration LCG; verdict publishes STD completion
and reseeds at its independently verified gaiji boundaries. Writer exceptions
latch in MAINE and subsequent refreshes never retry or escape to OP.

Eight actual OP shooting/Bomb actor routes per GNU/optimized UBSan (two
characters/shots, paint/no-paint) reach real end_extra, save, congratulations,
verdict, fresh OP and second MAIN. All 328 flat output files/312 BMPs agree,
including eight actual independently stored `GENSOU.SCR` files reopened to
check every one of ten sections, Extra cleared bit/stage ALL and outgoing score
digits. Shot A types a letter then Esc; shot B explicitly confirms eight letters.
Inherited shot waits cannot skip children; repaints consume no clock/RNG.
This joins existing independently controlled registration/congratulations/
verdict components; it does not establish original complete scene pixels or
ordinary survival. Hit consumption and initial unlock selection remain adapters.

`verify_extra_maine_join.py` executes original MAIN `0AAF:0D1F..0D44`, fade16
and GameExecl at loads1000/2000 with all eight captured outgoing field sets.
ESFD/end-type/pending delta/statistics/release order and fade273/tone0 agree.
EMS/resources/sound/palette/VBlank are adapters; execl takes an explicit FAILURE
return only for ABI inspection. Decoded original MAINE `_main` selects CONG04/14
and orders delay100/register/tone0/congratulations/verdict/fade4/OP. Native child
durations are explicit adapters in this caller comparator; v1315 separately
executes actual congratulations fades/key loops. No successful original whole
process replacement or complete child timing is claimed. Packed MAINE/payload/
main digests remain checked by the retained producer. A private source-only
`delay_left_=99` mutant enters registration at372 instead of373; the original
caller independently observes100 at both loads and rejects this mutant. The
private probe initially omitted GCC8's matching `-lstdc++fs` and failed with
`bad_alloc`; linking that archive, as product CMake already does, repairs the
probe. This reuses the v1296 filesystem-ABI negative, not game semantics.

The first full route exposed a genuine second-MAIN reset gap: resident graze
survived and local score digits imported the preceding resident publication.
`initialize_main_gameplay()` now owns original resident graze/miss/Bomb/ES
resets; MAIN's local eight score digits start at zero. Resident published score
digits remain unchanged until publication of a later run. Original raw prefix
`0AAF:0213..024F` (moduleAD03..AD3F; SHA-256
`43e5bd3246661adef1884c7a1158f5684a429519bcaf0dce40b0b84084e78705`)
executes without child adapters at two loads,24 dirty marker/character/shot/
normal-or-Extra states. All resident canaries and 21 selected fields agree with
GNU/optimized UBSan public MAIN construction. This is the bounded prefix;
full startup high-score loading is still separate. The headless route's initial
missing registration resource gate and picture-event filter error were fixed
before acceptance; terminal failed runs retain diagnostic logs, not success.

Current manifest `cab817e6def6924b12a52d604395fd96c463cae6ce6b527203b32247baf9189e` binds321 source/verifier files and117 AMD64
products. Both hosts pass38 contracts, including8 synthetic Extra child routes
and a real failed writer. 3,884 core cases/47,535 records,3,458 foreground scenes,
256 second-handoff,216 departure and24 ordinary score routes/4 failed writers
regress. 224 v1314 battle BMPs and248 v1315 pre-exit BMPs remain identical;
eight end_extra captures intentionally now show original fade-initial tone100
instead of the old frozen leave tone60. Unchanged wave products inherit v1313
proof. Component receipts retain their producer manifest
`08331530efcbc29a11ef43d4849336728982b797915d019d3f292a2a8d3b7389`; only the picture-event filter in
`verify_extra_maine_join.py` changed before final original caller/frontend review.
No component receipt is rewritten to impersonate a later source manifest.
Private `.analysis/port64/extra-maine-v1316/platform-review.json` SHA-256
`7289984503b401753237a1af0e2c622f2bf239da0ac4642344613aa90f4359e8` binds the batch; all output writers finish
before immutable whole-file/stream deduplication. Own total reclamation is
528068608 allocated bytes; 7786 final protected
source/input/cache/prior-reference/recovery/current-result files pass hash
readback. Complete recovery includes every tracked/untracked v1308..v1316 diff.

Next join actual OP saved-score clear-bit reading and character/shot selection:
`clear_sprites_load` combines Normal/Hard/Lunatic/Extra ranks for global Extra
availability, while Extra character/shot availability uses Normal..Lunatic only.
This distinction currently remains candidate source material until the OP
reader/selection target Oracle is recovered; do not just set one global bit.
Fresh OP still has its unlock reader unset. Then finish full HUD/OP scores/
Music Room/demo/audio/config and complete Linux/Windows ordinary routes,
save/restart and dense Lunatic timing. Every run stays muted. Actual Windows
fails WSL vsock before PowerShell; read-only Git metadata prevents commit/push.
No complete game/natural full Extra/original whole-scene pixels/current Windows/
audio/physical timing/DOS exact acceptance follows.

Terminal failed Extra trace/actions materializations are compressed in
`.analysis/port64/window-route-v1357/gnu-extra-failed-trace-v1.tar.gz`.
Every member SHA reads back before/after retirement (net4,526,080 allocated B);
restore under a fresh private directory for failed-trace replay. The failed
verdict remains failed. Both final CIs/diff checks pass; root includes live
Ghidra replay/mutations. Post-CI caches retire only with source/hash readback;
root `.analysis/cleanup/window-extra-final-caches-readback-v1357.json`.
