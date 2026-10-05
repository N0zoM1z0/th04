# Stage 2 evidence

Historical bounded results, preserved from `docs/PORT64.md`. Current state is
[the port overview](../../PORT64.md). Original CPU execution and adapter scope
remain explicit; successful component controls do not accept complete gameplay.

## Stage2 midboss and actor integration

The native Stage2 owner now implements all four attack patterns, the96-frame
entry, three direction bytes,52-frame movement/gather gaps, damage rewards,
timeout and upward retreat. It retains the same shared bullet scratch and
random ring. The four quad directions tune only the first producer; later
shots inherit the adjusted group/count. The hit wrapper's10 argument is a
sound ID, not a damage cap. Entry consumes colliding shots but remains
invulnerable. Timeout after17 patterns branches before collision/rewards;
actual defeat adds the unsigned16 bonus product, point requests, a Bomb,
zap/shake and48 sparks. Retreat uses private phase2 and16-frame spark requests.

Rendering follows original0AAF:214A: Y<=0 or phase>2 produces no sprite;
otherwise idle146..149, left150..151 or right152..153 is drawn at the
actual signed/rolled position. Damage flash is consumed only when the sprite
call runs. Invalid sprite>2 leaves the target's SI undefined; native rejects
that state explicitly and excludes it from gameplay equivalence claims.
The Stage2 BFNT bank still needs to join the GUI.

Pinned MAIN13A9:1062..14E7 owns four patterns, the far126D dispatcher and
compiler switch data. Actual original tuning/regular-special producers,
gather3stack/only, shot-hit wrapper, score bonus/random, HP, activation/reset
and sprite geometry execute in the CPU comparator. There are9,282 controls
and13,512 records:2,542 updates,6,720 render cases,16 activation/reset cases,
and four retained Normal/Lunatic timeout/defeat update+render sequences.
These retained sequences preserve all midboss/bullet/gather owners and ring
between steps; ordinary other-actor updates are deliberately omitted.
Full22-byte state, three private bytes,440 bullet records,16 gather records,
both templates, RNG cursor, pending awards and ordered requests/draws compare.
Shot damage is injected at the real collision boundary. Spark requests,
point popups, Bomb requests, audio, HP pixels and sprite pixels are adapters.
No full original Stage2 route, GUI timing or DOS exactness claim follows.
The callback-rejection control prevents ctypes exceptions from being swallowed:
store the error, stop Unicorn and rethrow after the emulation call.

MAIN now chooses the actual Stage2 callback at2600. STD pauses scheduled waves
while that midboss is active. Shot collisions, gathers, sparks, items, score
drain and native drawing requests join the existing owners in frame order.
Four native Reimu/Marisa Normal/Lunatic routes continue natural Stage1 into
real ST01.STD/MAP, defeat the Stage2 midboss and reach the pre-Kurumi dialog
gate at6982. They hold there until dialog/Kurumi join. These are native actor
routes, separate from the selected original CPU comparisons.

The GUI remains Stage1 because stage sprites/map/palette/portrait/dialog
resources have not been replaced yet. `port64-preview/v1265` is the build/
verification package; the root GUI remains v1263 and DOS launchers/assets stay
unchanged. General semantic work remains stopped. Next connect Stage2 resource
ownership and dialog, then Kurumi; do not call this full Stage2 gameplay yet.

```bash
python3 port64/verify_midboss2.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-midboss2-contracts \
  --output-dir .analysis/port64/midboss2-v1265/cpu-linux-final
```

Receipts: `.analysis/port64/midboss2-v1265/target-owners.json`,
`cpu-{linux,windows,ubsan}-final/receipt.json`,
`session-{linux,windows,ubsan}-final/receipt.json`, `native-windows-midboss2.json`,
`native-windows-receipt.json`, `integration-review.json`, and
`.analysis/port64/verification-midboss2-v1265-final/receipt.json`.

## Stage2 visual resources and dialog

This advances the preceding backend-only slice. Both SDL and Win32 windows now
consume the actual Stage1 departure request, validate Stage2 assets before actor
mutation and continue through real Stage2 STD/MAP, its midboss and pre-Kurumi
dialog. The preview holds after that dialog; Kurumi battle remains unported.
Semantic readability stays paused at the user's stopping condition.

Pinned target observations: MAIN main01 `0AAF:055B..0580` is the second case in
the seven-word switch at `0AAF:06D2`. It requests `BSS1.CD2` at slot8,
`ST01.BFT`, actual `13A9:A623` setup and `ST01.MPN` without a character-dependent
map branch. The setup requests `ST01.BMT`, `ST01BK.CDG` image0/slot16 and
`ST01.BB`; five rank seeds execute these original requests through adapters.
`0AAF:07AE..07DE` frees stage sprites128..255 and CDG slots8..30. These are
selected relocated target observations with load2000/isolated DS8000, not new
whole-function exactness claims. Asset headers establish18 32x32 BFT images,
16 64x64 BMT images,75 MPN tiles and four128x128 boss portraits. Thus native
stage slots128..145 belong to BFT and146..161 to BMT. The Stage2 BMT palette
replaces the Stage1 palette without its color-zero override.

The native stage resource object owns its byte vectors on the heap. CDG views
reference these vectors and sprite slots reference its sheets; disable whole
object copying and move only the owning pointer. Clear every dynamic stage slot
before destroying Stage1 dialog sheets. Common player/items/enemy sheets remain
owned. Allocate and validate the next background/script before preparing actors,
then publish resident resource_stage1 only after installing the resource bank.
The same MAIN generation continues and initialization consumes353 LCG draws.

Four native character/Normal-Lunatic routes run natural Stage1, enter Stage2,
render its map/midboss/retreat and reach the pre-Kurumi gate at6982. Dialog holds
gameplay frames, player/shot actors and shared RNG; its completion holds the
unported battle frontier without restarting the script. Script offsets end at
566 for Reimu and585 for Marisa. Eight checkpoints per route give32 BMPs and36
counters, identical on Linux GCC8.4, MinGW13 PE32+ under Wine, actual Windows
and optimized GNU UBSan/bounds. Fourteen contracts pass; the previous64 natural
Stage1 BMPs/72 counters remain identical to v1265 across Linux/Wine/Windows.
The Windows verification script includes both stage suites and reports96 images.

Independent checks execute all48 existing original dialog controls/76 scenes /
18,768 events on Linux and Wine, including both Stage2 scripts with held and
released input. Font decoding uses the supplied FREECG98 bitmap. Original
graphics/file/audio/wait consumers remain intercepted; the native frame pacing
is not an original-game timing claim. A separate Python FAT/PAR/CDG/BFNT path
checks57,188 opaque Kurumi portrait pixels against the native screenshots and
Stage2 palette. It rejects a disposable BMP with one opaque pixel changed at
(298,112); transparent background lies outside this portrait-only comparator.
Original hook rejection also has an explicit negative control. These checks do
not compare complete original VRAM or establish full Stage2 gameplay/FPS.

```sh
cmake --build .analysis/port64/linux-live-v1251 --parallel 4
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-stage2-v1266/receipt.json
python3 port64/verify_stage2_resources.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --frames .analysis/port64/verification-stage2-v1266/stage2-linux \
  --output .analysis/port64/stage2-v1266/resources-final.json
```

Source manifest:
`3e229f60bb2e8095508ee7da56b469b39f67908b035aabfda30f3124fabcd7f3`.
Receipts: `.analysis/port64/stage2-v1266/target-resources.json`,
`resources-final.json`, `negative-pixel.json`, `dialog-cpu-{linux,windows}/receipt.json`,
`native-windows-receipt.json`, `integration-review.json`, `windows-export-receipt.json`,
and `.analysis/port64/verification-stage2-v1266/receipt.json`.
Windows package `port64-preview/v1266` and root native launcher use this preview,
with a versioned backup. DOS executables, normal/invincible launchers, assets and
saved files are retained. Next implement Kurumi state/attacks/render and connect
the post-dialog continuation before expanding later-stage gameplay.

## Kurumi state and attack core

The Stage2 Kurumi logic is now a portable owner in `port64/kurumi.cpp` and
`kurumi.hpp`. Original MAIN main03 `13A9:4F84..56CC` owns the spawnray,
orbit and attack helpers; `56CD..5B32` owns the far update. Byte `5B33`
precedes three switch-word tables at `5B34..5B53`; these are data, not more
instructions. Selected relocated slices, setup `A623..A6F5`, boss reset
`A4D1..A517` and shared defeat `ACB3..AE86` are recorded separately from
runtime comparisons. Provenance remains candidate-local-attested.

Kurumi uses six 26-byte records at original DATA2134:B204. The byte flag owns
allocation; the other byte and twelve-byte tail survive reuse. Phase0 clears
only flags. The ray updater counts free entries before updating, so a newly
freed ray delays the all-free result until the next call. It writes SPEEDUP
into the bullet template but invokes the regular fixed-speed producer; preserve
that original call and its retained group. Orbit writes current coordinates
without moving previous coordinates or velocity. Seeking retains velocity
inside its dead band. Phase0 tests the old clock before invulnerable hit advances
it. Later hit damage is truncated to a byte after the clock increments.

The process-local turning toggle at46B0, unknown byte at46B1 and bullet special
controls BCB7/BCB8 remain explicit state. The final stack periods are255,128,32,8
for Easy,Normal,Hard,Lunatic. Extra does not load this ordinary boss; the native
fresh constructor rejects rank4. A zero period reaches original signed division
at13A9:5695; native code throws after the preceding cloud producers instead of
executing host undefined behavior. The zero-period guard is a native contract
and static target observation, not an original CPU exception replay.

Boss defeat is shared with Orange, but Orange's unconditional gather-center
write is specific to its update and must not leak into Kurumi. The extracted
helper preserves that distinction. Boss reset retains HP, angle, end HP and
additional state. Four fresh-DS setup controls compare only the24-byte boss,
hitbox384/384 and rank period; preceding-stage retained metadata remains an
integration requirement.

Original CPU execution supplies3,436 boundary controls and eight retained
boss-only sequences. Each difficulty has an8,323-frame timeout and1,190-frame
damage19 sequence, both reaching departure. All41,488 records agree on Linux
GCC8.4, MinGW13 PE32+ under Wine, optimized GNU UBSan/bounds and actual Windows.
Comparisons include the24-byte boss,16 additional bytes, every ray including
padding, all440 bullets/16 gathers/96 sparks,48 explosion bytes, templates,
global special controls, shared RNG cursor and ordered requests. Actual original
bullet/effect/bonus/departure callees execute; shots inject damage and
graphics/audio/HUD/item/point/dialog/delay consumers remain adapters. Retained
sequences advance only this owner and retain pool occupancy. They do not replay
ordinary actor motion, GUI rendering or frame pacing.

The comparator rejects a disposable first-checkpoint BOSS byte mutation and
propagates an injected original hook rejection. Fifteen contracts pass on all
build variants and actual Windows. Orange's prior34,040-record state trace
including ten retained sequences remains identical on Linux/Wine/UBSan after
the shared-helper extraction. The previous64 Stage1 and32 Stage2 BMPs and
108 counters remain unchanged across Linux/Wine/UBSan/actual Windows.

```sh
python3 port64/verify_kurumi.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-kurumi-contracts \
  --output-dir .analysis/port64/kurumi-v1267/cpu-linux-complete
```

Source manifest:
`803e9fbbab64f3b3edd1ac30043aa9b475dfb52c277eef44f4a47afdfeeb0c76`.
Receipts: `.analysis/port64/kurumi-v1267/target-state.json`,
`cpu-linux-complete/receipt.json`, `cpu-{windows,ubsan}-final/receipt.json`,
`native-windows-kurumi.json`, `negative-trace.json`, `integration-review.json`
and `.analysis/port64/verification-kurumi-v1267/receipt.json`.
Windows package `port64-preview/v1267` contains the checked core and15 contract
executables. Root Windows files remain byte-for-byte on v1266. Kurumi foreground,
backdrop, GUI battle and post-dialog continuation are the next bounded slice;
the live preview still holds after the pre-Kurumi dialog. No new DOS exactness
or complete original Stage2/gameplay claim follows. Semantic remains stopped.

## Kurumi foreground and ray raster

`port64/kurumi_render.cpp` now implements the original foreground at MAIN
main01 `0AAF:6CA3..6E7A` and the backdrop request plan at `76FB..7756`.
The next byte starts Orange's foreground. Shared explosion rendering is
extracted into `orange::prepare_explosions`; both bosses retain their own
foreground, sprite bank and circle geometry.

Boss sprite coordinates use signed arithmetic shifts, while ray coordinates
truncate signed division by16 before adding playfield32/16. Flag0 suppresses
a ray; every other flag draws, including values the updater does not advance.
Sprites0/12 animate with frame-mod16; sprites4/6 use frame-mod8; other sprites
remain fixed. Damage selects white rendering and is retained. The phase254
register expression pushes the calculated top before loading the sprite byte,
so its Y is defined. Phase0 circles begin only after clock128, with color7
and two color6 rings.

The native ray raster orders endpoints byX and accumulates a slope quantized
to16 fractional bits from8000h. Actual ray endpoints stay within the default
640x400 screen clip; generalized clipped endpoints are outside this helper's
scope and are rejected. Independent original CPU line controls execute
`0000:1562..16FE` with in-screen endpoints and compare all32,000 mask bytes.
Memory writes model RMW masks, not physical GRCG color/page/scroll state.
Only this default-clip path is selected; adjacent alignment at16FF, the next
function at1700 and the clipping helper are separate ownership.

Background phase0/254 and early departure request all tiles. Phase1 requests
the picture at32/96 with fill color0, copies the actual BB segment and requests
mask cel from the arithmetic phase-clock shift. Later battle phases request
the picture; later departure requests dirty tiles. The original colorfill
`0AAF:3F80..3F98` and row kernel `7578..7584` write384x192 pixels from32/208
and384x80 from32/16, covering104,448 pixels. This is a TDW address-footprint
observation: that mode ignores CPU value bits. Using the RMW mask collector
for this fill was rejected by the footprint comparison. Host background
composition has not yet consumed this geometry.

Across Linux GCC8.4, MinGW13 PE32+ under Wine, optimized GNU UBSan/bounds and
actual Windows,7,204 foreground controls,2,816 backdrop request controls and
620 line masks agree with the original. Compare complete48-byte explosions,
156 ray bytes including retained padding, flash/aging/tone clocks and ordered
sprite/circle/ray geometry. Original BOSS/additional-byte invariance is also
asserted; native comparisons cover damage and the listed render state.
Sprite/CDG/tile/color consumers remain adapters. A disposable one-bit change
in a native ray mask fails immediately, and original hook rejection propagates.
The shared extraction also passes900 original Orange foreground controls.
Kurumi's41,488-record prior state trace replays on current Linux. Fifteen
contracts and the previous96 BMPs/108 counters remain identical across hosts.

```sh
python3 port64/verify_kurumi_render.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-kurumi-contracts \
  --output-dir .analysis/port64/kurumi-render-v1268/cpu-linux-full
```

Source manifest:
`e0bf7972efdead82ba50d555011c9c873f47afc7ea75c690cfb2b97bd6ef0a02`.
Receipts: `.analysis/port64/kurumi-render-v1268/target-render.json`,
`cpu-{linux,windows,ubsan}-full/receipt.json`, `native-windows-render.json`,
`negative-line.json`, `orange-render-linux/receipt.json`, `integration-review.json`
and `.analysis/port64/verification-kurumi-render-v1268/receipt.json`.
Windows package `port64-preview/v1268` contains the checked core. Root Windows
files remain on v1266. Next account for preceding-stage retained Boss metadata,
compose the Stage2 backdrop and connect Kurumi battle/post-dialog/departure.
No new DOS exactness, physical GRCG or full Stage2/gameplay/FPS claim follows.
Semantic remains stopped; the existing DOS source was sufficient for this slice.

## Migration order

Semantic work stops when the current subsystem is clear enough to port and
verify. Motion/items/background/shots/enemies required no further DOS-source edits.
For each next module, stop readability work once state ownership, arithmetic,
control flow and hardware boundaries support an independently checked native
implementation. Resume only for a concrete ambiguity exposed by integration.
Enemy bullets, gathers, sparks and the Stage 1 midboss now use that synchronous boundary.
Orange state/attacks/foreground and pre/post-boss dialog now run in ordinary Stage1.
Ordinary Stage1 now also consumes the actual clear bonus and displays its tally.
Ordinary frame score drain and extends now join MAIN.
Post-dialog frame continuation and stage-leave overlay now reach the next-stage
request. Actor-session preparation and Stage2 midboss/STD/MAP integration through the
pre-Kurumi dialog gate are checked separately. Stage2 visual resources and its
pre-battle dialog now join the live window. Kurumi state/attacks have independent
CPU controls. Foreground/explosion/ray raster and backdrop requests now have
independent controls and now join the live battle/post-dialog/departure. Stage3
resources/STD/midboss, Elly battle, post-dialog and departure also run in the live window.
Next connect Stage4 and the remaining stages,
HUD, death/Bomb transitions and audio. Add saved
configuration and route-level gameplay/Ending/score checkpoints as those
systems become runnable. Full gameplay is the completion condition, not an
exhaustive source-renaming pass.


## Kurumi battle and departure integration

The native GUI now continues from the actual Stage2 pre-dialog gate through
Kurumi battle, post-dialog, clear bonus and departure. Previously it held after
the pre-dialog despite the separately verified boss and renderer. The next held
frontier is Stage3 resource loading. This is a native integration slice; player
death/Bomb, full HUD/audio, later stages, Ending and saving remain incomplete.
Semantic stays paused unless a specific port ambiguity needs clarification.

Original MAIN13A9:A4D1..A517 `boss_reset` clears phase/mode/pattern/frame,
velocity, damage and the two small explosion alive flags. HP/angle/endHP,
other additional bytes and all remaining explosion metadata survive, including
the big alive flag. Stage2 setupA623..A6F5 installs current/previous3072,1296,
sprite0, hitbox384,384 and rank periods255,128,32,8. The portable factory retains
these owners from Orange, while the separately observed stage runtime resets
slowdown1, shake0, bombing-disabled0 and invincibility64. Common stage0675
stores palette tone100 after loading. The new BFNT palette replaces color0
before Kurumi activates; at clock320 Kurumi itself sets96,0,0 as the existing
independent core controls attest. Copying all preceding globals would retain
Orange's defeat slowdown/invincibility/palette rather than the new stage values.

1,024 original CPU retained-marker setup controls compare complete24-byte Boss,
16 additional and48 explosion bytes plus hitbox/timeout.256 controls execute
only the original player countdown prefix0AAF:5FD4..5FDE, ending before hit/death
handling. They agree Linux/Wine/UBSan/actual Windows. A separate predecessor
control actually executes stage_runtime06E0 from speed3/shake17,-19/Bomb255/
invincibility255 and observes1,0,0,0,64. File/BFNT/CDG/hardware requests remain
adapters. A private source-built driver also checks the new retained metadata
and reset globals after four natural Stage1 departures; it is an integration
check, not another independent original Oracle.

The gameplay owner now dispatches the active ordinary boss, uses real shots,
bullets/gathers/sparks/items/score and prepares the foreground exactly once per
simulation frame. Player invincibility decrements once in the frame prefix and
is shared with boss/bullet owners; a suspended post-dialog frame does not repeat
that prefix. Rendering composes Stage2's opaque picture at32,96, its own BB mask,
the TDW color0 rectangles through physical row399, actual stage sprites and the
fixed-point ray pixels already checked in the previous slice. Full host redraw
continues to replace PC-98 dirty-tile/VRAM hardware operations.

Eight natural Reimu/Marisa Normal/Lunatic routes vary held shooting during the
Kurumi battle, exercising both defeat and timeout. Neither phase/RNG/actor pools
are forced. Each records nine checkpoints and asserts frozen dialog actors/RNG/
invincibility, post-dialog continuation, exactly one bonus/fade/next request,
416/488 departure and three inert advances at the Stage3 frontier. Resident
stage/ascii become2 but resource stage remains1; MAIN generation remains2.
Timeout receives no timely-clear award. Rendering and counters agree across
Linux GNU8.4, cross-built MinGW13 PE32+ under Wine, optimized GNU UBSan/bounds
and native Windows. All15 contracts pass. Total168 BMPs/188 counters include
72 new Kurumi images/80 counters; prior96 BMPs/108 counters are unchanged.

Independent Python FAT/PAR decoding verifies57,188 opaque portrait pixels and
86,016 selected unobstructed opaque-CDG/colorfill pixels across the new battle
checkpoints. The latter uses the original phase2 red color0, lower picture side
bands, bottom physical rows384..399 and idle-route upper rows. Shooting can
cover upper rows, so those are excluded from shot controls. This checks selected
asset/palette composition, not full original VRAM. A disposable BOSS output byte
mutation and one selected backdrop pixel mutation both fail their comparators;
injected original-hook failures also propagate.

Current Linux reexecutes all7,204 foreground/2,816 backdrop/620 complete line
mask controls, matching v1268. Three current builds replay the41,488 independently
recorded original core states with identical digests; that regression does not
reexecute original updates. Actual Windows additionally runs the new setup/
countdown controls and every native visual scenario. No original full Stage2,
physical GRCG, GUI frame pacing, native Windows compiler or DOS exact claim.

```sh
python3 port64/verify_kurumi_setup.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-kurumi-contracts \
  --output-dir .analysis/port64/kurumi-live-v1269/setup-linux-final
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-kurumi-live-v1269-final/receipt.json
```

Source manifest:
`1fcba424ea85e628b7f7df71e3183bd861f0a5e920645fabccf0cc60d0df52d1`.
Receipts: `.analysis/port64/kurumi-live-v1269/{target-live,integration-review,resources-live,negative-live,native-windows-receipt,native-windows-setup,windows-export-receipt}.json`,
`setup-{linux,windows,ubsan}-final/receipt.json`,
`core-{linux,windows,ubsan}-final/receipt.json`, `render-linux/receipt.json`,
and `.analysis/port64/verification-kurumi-live-v1269-final/receipt.json`.
Windows root `start-th04-port64.bat` and native EXE now use this v1269 preview;
21 other existing files remain unchanged. No window launched. Native builds
use incremental CMake; the DOS product did not require rebuilding. Next connect
Stage3 resources/actors/midboss, then Elly and its dialogs.
