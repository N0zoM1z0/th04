# Stage 4 evidence

Historical bounded results, preserved from `docs/PORT64.md`. Current state is
[the port overview](../../PORT64.md). Original CPU execution and adapter scope
remain explicit; successful component controls do not accept complete gameplay.

## Stage4 resources, midboss and NPC dialogue

The v1272 native batch advances the preceding Elly frontier. Stage4 loads only
after the actual Stage3 departure request, preserves MAIN generation2, consumes
the common353 process draws, installs ST03's28x32x32 plus8x64x64 sprites,89 MPN
tiles and STD/MAP streams, and runs to the genuine pre-boss dialog at frame12808.
The first route uses KAO3/Marisa and ST03BK2; the second KAO2/Reimu and ST03BK.
The dialog clears the stage sprite bank, loads the character-dependent BBT
sheets/palette and holds after completion. Reimu/Marisa Boss battles remain the
next owner; the port does not manufacture a replacement fight or completion.

Observed MAIN ownership is13A9:14E8..1ABE (four pattern helpers and dispatcher),
0AAF:2316..23A2 (foreground) and13A9:A7B5..A931 (retained setup). The dispatcher
ends with RETF at1AA9;1AAA is alignment and1AAB..1ABE is its phase table. Stage4
midboss starts2800 at144,-32 with4,2 pixel velocity and1200HP. Entrance takes48
updates and clears only its selected private counters. Fresh DATA2134:185E has
an aim-toggle value1; setup does not reset it. The shared HP bar, flash, angle
and other untouched22-byte actor fields retain preceding-stage state.

First termination, whether defeat or timeout, re-arms the same actor for5600 at
240,-32 with-4,2 velocity,1200HP and frame0. Second termination clears active/HP
without rearming. Defeat rewards30 minus completed patterns, emits shake before
explosion setup, and dropsBomb first/one-up second. All four pattern helpers
preserve signed clock IDIV, byte wrap, tune-before-fixed-shot overrides,
retained aim state and separate shot requests. Homing precedes movement; a
lethal hit after a bounds exit still wins. Foreground preserves small-point
clipping,64x64 append slots156..163 and read/clear flash ownership.

Carpet0AAF:3F9A..3FF3 is a near RET4 helper; its last two bytes are the RET
operand, not alignment. Callback3FF4..40FD owns ring corrections, lighting
columns/dirty flags, initial full invalidation and final callback disable.
Target DATA2134:190C..199B supplies image offsets and199C..1A5B the8x24 mask.
The lower seams use columns18/20, unlike the quarantined DOS source candidate's
19/21. Cel5 leaves only left column2 already lit; right column21 stays2. Native
source derives the meaningful tile IDs/masks with explicit asymmetry, and an
independent full-table comparison checks every entry before CPU controls.
This batch does not change or reopen the deferred DOS carpet exactness unit.
Native full redraw consumes the same25x24 ring; physical dirty-page transients
remain outside the accepted rendering scope.

12,362 independent original CPU controls produce31,410 complete actor/private/
HP/RNG/score/template/440-bullet/16-gather state and ordered event/draw records.
16 retained sequences cover Normal/Lunatic, injected damage0/10, ring cursors
0/255 and first/second encounter starts. Original expectations are preserved
before native reference replay; each replay explicitly reports no original
reexecution. Each of the three builds independently reexecutes436 carpet
controls/4,012 records and256 retained setup controls. Original callback
rejections propagate. Independent archive pixels verify NPC portrait0 and the
active character-dependent palette in all eight native routes.

The initial carpet checkpoint0 mismatch disproved regularized seam columns.
A separate core control588 failure exposed an observer counting9512 and its
inner regular wrapper twice; the native pool/template was already correct.
Only the observer was corrected, retaining the failed comparison. Neither
failure is relabeled a pass. These findings stay separate from the selected
original CPU and native integration results.

18 contracts and432 BMPs/476 counters agree Linux, Wine, optimized UBSan/bounds
and actual Windows. All preceding336 BMPs/372 counters stay identical to v1271.
Eight natural Normal/Lunatic Reimu/Marisa shot/idle routes exercise actual STD
waves, both activations and two defeats or timeouts, carpet disable, NPC resource
selection and dialog freeze. Recorded player keys track the midboss on shooting
routes; no hit, phase, score or spawn is injected there. Dialog and final hold
do not repeat simulation. Native screenshots are independently guarded by
assets/state, not treated as complete original-game VRAM equivalence.

Replay with `port64/verify_midboss4.py`, `port64/verify_carpet.py` and
`port64/verify_stage4_resources.py`; each accepts the pinned `--target` and
`--exe`, plus `--runner wine` for the Windows cross-build. Resource checks also
need `--hdi` and `--frames` from `--stage4-screenshots`. The midboss reference
replay uses `--reference-dir` only after a complete original run passes.
`port64/verify.py` and `port64/verify_windows.ps1` include all six natural suites.
Receipts live below `.analysis/port64/midboss4-v1272/` and
`.analysis/port64/verification-stage4-v1272/receipt.json`.
Manifest: `0bae5caad45928c0ca67c3420ee9fff3dcd2c34b8a411dc8a7a992b83ab55888`.

Windows root native EXE/launcher use v1272. The versioned package contains19
checked static x64 PE executables;21 other root DOS/HDI/config/font/build files
remain identical. No GUI launched. Windows executes a MinGW cross-build;
Windows-host compilation, physical hardware and GUI pacing are not claimed.
Stage4 NPC Bosses onward, player death/Bomb, complete HUD/audio, Ending and
persistence remain unported. Semantic stays stopped unless a concrete ambiguity
requires a bounded clarification. Next implement the actual NPC Boss owners.


## Stage4 Reimu state and orb core

v1273 ports MAIN Reimu dispatcher13A9:B91B..BE2F, ten attack producers,
AE87/AF21 movement, AFBB gather intro, B0A1/B0FC orb allocation, B163 orb
update and B8E8 palette pulse. It adds a native core owner; GUI rendering and
activation remain the next batch. The GUI still holds after Stage4 pre-dialog
at frame12808, and the Marisa Boss owner remains unported.

Fresh target review separates AFBB..B077 code, B078 alignment, B079..B0A0
case keys/destinations, and B91B..BE2F code from BE30..BE43 mode tables and
BE44..BE5D phase destinations. DATA2134:BCFA is signed angle delta, BCFB orb
pattern and BCFC the single trail flag aliased by both old visibility names.
BCFD is alignment; BCFE..BD17 is the26-byte template. B204..B543 holds32
records. DATA24B6/24B7 start at0 and hold the alternate angle/pulse direction.

Native records use explicit fixed widths, wrap and signed shifts. Moving
allocation retains spin time, angle speed and padding; spinning allocation
retains velocity and padding. Released or unknown nonzero orb flags still run
raw shot/player collision that update. The raw shot adapter is independent of
against-Boss damage. Unsigned wrapped rectangles preserve boundary behavior.
The entrance has a double clock increment; hit wrappers own ordinary phase
increments, while defeat staging advances separately. Score/drop/clear and
shared RNG consumption order remain guarded, including discarded angle draws.

6,678 original CPU controls produce62,514 complete state/event records.
Eight retained sequences cover four ranks with injected damage0/19, visit
phases0..12/254/255 and reach departure in12,716/1,245 updates respectively.
Native GNU, Wine, optimized nonrecovering UBSan/bounds and actual Windows PE
execution compare every recorded field against those independently generated
expectations. Reference replay explicitly reports no original reexecution.
Original shot/video/audio/item/point consumers are bounded adapters; retained
sequences advance this Boss only and exclude complete stage/render/pacing.

1,024 retained Stage4 setups independently execute the original across four
ranks and256 markers for each of the three builds. Complete BOSS24/additional16/
explosions48/hitbox/timeout and private3/template26/pool832/initialized2-byte
retention are checked; callback fields are BCD8 update, BCDA segment and BCDC
foreground. Native preparation currently assumes the first fresh MAIN Reimu
encounter; it does not promise repeated-setup private-state retention.

The first native short comparison fails at2402 field24: candidate blue ball76
and special129 differ from original57/128. Original also supplies red ball61
and no-special255. The repaired full comparison passes; the original failure
remains failed. An initial scratch setup used wrong character/rank addresses,
then a candidate pointer check confused segment and offset fields; only those
observers changed. An original zero-divisor control confirms flag/spinTime and
other selected writes precede IDIV; native throws after those writes and retains
the angle. A full pool does not execute the division. The initial aggregate
comparison also rejects source drift while candidates are repaired; its
separate target-only reference remains valid. Final frozen-source replays pass.

19 contracts and432 existing BMPs/476 counters agree Linux/Wine/actual Windows;
all preceding checkpoints remain identical to v1272. A versioned20-static-PE
validation package lives in `port64-preview/v1273`; all23 recorded root files,
including existing native EXE/launcher and21 DOS/HDI/config/font/build files,
remain unchanged. No GUI launched. Windows executes a MinGW cross-build;
Windows-host compilation, physical hardware, full game and DOS exactness are
not claimed.

Replay `port64/verify_reimu.py --target TARGET --exe CONTRACT --output-dir NEW`
and `port64/verify_reimu_setup.py` with the same options. Use `--runner wine`
for the PE build. A full original run produces `original-reference.json`; only
then use `--reference-dir` for a hash-checked complete native replay. Receipts
live below `.analysis/port64/reimu-v1273/`: `target-live.json`,
`core-full-first/original-reference.json`, `core-{linux,windows,ubsan}-final/receipt.json`,
`setup-{linux,windows,ubsan}-frozen/receipt.json`, `zero-div-original.json`,
`native-windows-{core,setup,receipt}.json` and `integration-review.json`.
Cross receipt: `.analysis/port64/verification-reimu-v1273/receipt.json`.
Manifest: `38e0289f882c6867b0f4849b32cf84091fa6236481318892009a99db92d24abe`.

Next connect Reimu foreground/trail/rolling-orb rendering, the shared NPC
backdrop and actual Marisa-player battle gate; then port the Marisa Boss and
later stages. Semantic remains stopped unless a concrete ambiguity arises.


## Stage4 Reimu battle and rendering

v1274 connects the verified Reimu core to the actual Stage4 Marisa-player
pre-dialog handoff. Boss setup consumes the retained Elly metadata and four
rank parameters; there is no substituted Marisa Boss. The GUI's other character
stays at its real pre-battle gate. Main state owns body shots with
against-Boss=true and orb shots with against-Boss=false. Orb damage is discarded
while ordinary shot consumption/score/sparks still execute. Shared frame prefix,
gathers, explosions and score drain run once per simulated frame. A repaint
reads cached draw requests and cannot age explosions or clear damage twice.

Observed MAIN0AAF:8347..83A2 draws32 orb slots in ascending order, accepting
nonzero flags and signed centerY>-256. Absolute screen coordinates are
SAR(centerX,4)+16 and SAR(centerY,4); sprite base plus
`((stage_frame+slot)&7)>>1` uses the original rolling call. Foreground
83A3..846E draws the previous raw Boss sprite in B/I planes with flagsFFC6,
then the current sprite.136 alone animates with frameMod16/4. Damage selects
the white FFC0 draw and is consumed below phase254; phase254 uses the large
sprite and255 has no body/orb draw. Shared small/big explosions follow.

The B/I trail writes alpha-covered pixels as destination index OR9, retaining
R/G. Reversing RGB loses plane identity when palette colors duplicate, so the
Reimu frame keeps palette indices through composition and post-dialog capture.
Actual original SUPER1PLANE0000:2838 and rolling0000:2D3E execute against
all12 64x64 Reimu and eight32x32 orb BFNT images, eight X alignments, retained
16-color backgrounds and seven negative/top/bottom Y positions.640 controls
compare complete640x400 indexed surfaces:163,840,000 pixels. The shadow models
GRCG output ports and visible A800:0000..7CFF writes; it does not emulate physical
page/scroll timing or aliasing outside that visible plane. Negative rows are
outside visible VRAM; only bottom overflow rolls to row0. Invalid extreme
coordinates remain outside this pixel claim.

Observed shared NPC backdrop0AAF:77E7..7873 divides signed phase clock by8,
truncates toward zero and stores AL as the BB cel. Phase1 cels0..7 use stage
tiles plus BB, later cels use the256x256 CDG at(96,72), color1 filler and BB.
Phases2..253 use the picture and filler. The BB consumer paints one bits with
color15 instead of invalidating zero-bit tiles. Filler13EA..1424 writes top and
bottom384x56 borders and left/right64x256 borders; actual CPU write addresses
match75,776 pixels. Phase0/255 signed clocks and254 retain their tile behavior.
Host full redraw replaces the original dirty-copy hardware.

9,188 original foreground controls compare ordered body/trail/orb/explosion
requests, damage consumption, complete private/template/pool retention and
explosion aging/flash clocks.5,888 original backdrop controls compare call
order, signed clocks, byte cels and BB pointer copies. GNU, Wine, optimized
UBSan and actual Windows native builds reproduce the full original expectations.
Original production and hash-guarded native-only reference replay are labeled
separately. Earlier6,678 Reimu core controls/62,514 records still pass all four
hosts;1,024 retained setups pass Linux and actual Windows.

Eight natural Normal/Lunatic Marisa-player A/B shot/idle scenarios enter through
title selection and the complete preceding stages. They capture phases0..12,
defeat, post-dialog, clear bonus, fade417 and next-stage489 without injecting
damage/phases/spawns/RNG. Idle routes visit every attack. Post-dialog freezes
simulation and RNG, bonus/fade/departure occur once, resident stage advances to4
while loaded resource stage remains3, and the Stage5 request freezes pending
actors/RNG/score until its resource owner exists.144 new BMPs/152 counters agree
Linux/Wine/optimized UBSan/actual Windows.19 contracts and576 total BMPs/628
counters agree Linux/Wine/actual Windows; all old432 BMPs/476 counters remain
identical. This is headless deterministic coverage, not GUI pacing or an
original ordinary-route equivalence claim.

The versioned20-static-PE package is `port64-preview/v1274`. Root Windows
`th04-port64.exe` and `start-th04-port64.bat` are refreshed after comparison,
with21 DOS/HDI/config/font/build file hashes unchanged. No GUI is launched;
MinGW cross-building and actual Windows execution are distinct observations.
Death/Bomb/full HUD/audio/Ending/save and later stages remain unported.

Replay foreground/background using `port64/verify_reimu_render.py --target
TARGET --exe CONTRACT --output-dir NEW`; only after an original run succeeds,
use `--reference-dir ORIGINAL_DIR` for a complete hash-checked native replay.
Use `port64/verify_reimu_pixels.py` with the same three options plus `--hdi HDI`;
`--runner wine` selects PE execution. `--reimu-screenshots DIR` runs the eight
natural routes. `port64/verify.py` and `verify_windows.ps1` include those routes.
Receipts are under `.analysis/port64/reimu-render-v1274/`; the cross-platform
receipt is `.analysis/port64/verification-reimu-render-v1274/receipt.json`.
Native source manifest: 10c0073624a213552cdf27bf6ee58ac663f27a8f7a77646232cdf63a4fe35127.

The user-requested cleanup removes superseded CMake and native Windows build
outputs and archives old BMP/large text with verified lossless gzip.18.53 GiB
was reclaimed before this batch's final validation. Original and compressed
hashes and removed build identities are in `cleanup-receipt.json`; current
builds, original targets, databases, toolchains, fonts, DOS products/images and
v1273 CPU references are retained. Before reusing a compressed historical
private file, restore it with `gzip -d -- FILE.gz`. Native changes do not promote
or invalidate DOS exact acceptance. Semantic stays stopped; next port slice is
the distinct Stage4 Marisa Boss.

## Stage4 Marisa core

v1275 ports the Reimu-player Stage4 Marisa Boss core, four auxiliary bits,
all ten attacks, movement, body/bit collision, HP rewards and defeat/departure.
It is a separate native owner; the GUI still holds at the pre-dialog frontier
until its foreground and backdrop are connected. The root Windows playable
EXE/launcher remain v1274. Broad semantic work stays stopped.

Fresh hash-attested MAIN review covers segment13A9:2F8A..422E, including
20 code extents and three dispatcher tables, and DATA:1A5E..1A65 HP values
220,400,280,450.32 retained26-byte custom records are explicit; Marisa owns
only the first four. Private DATA:432E..4347 fields and retained templates
are separate from common BOSS state. Code addresses become explicit dispatch
tokens, with an unknown active callback rejected instead of cast to a host
pointer. Pinned target SHA-256 is
077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b;
provenance remains candidate-local-attested.

Body damage truncates to BYTE before division by the previous update's
alive-bit count plus one. Bit damage retains WORD signed-wrap behavior and
uses the raw against-Boss=false consumer. Body hits, pattern selection and
firing occur before current bit destruction/movement and packed center writes.
Dead bit records still receive the original all-four distance/angle mutations.
Mode7 calls the phase-entry helper twice, including duplicate clock64 sounds.
Once-tuned templates retain the original angle/origin mutation order.

The original flystep13A9:30F5..3174 has IDIV divide-by-zero and quotient
overflow cases. Four independent original CPU failures and native contracts
cover both axes and sequential writes: a Y failure can leave the X velocity
committed. Controlled attack1/2 states with last-alive clock148 and current
clock152 reach duration12 and IDIV at3117. This is a controlled-state hazard,
not a reproduced natural player route. The core reports that original failure;
GUI integration must choose and test an explicit portable runtime policy.

7,759 original CPU cases compare87,031 complete state/event records across
four ranks, empty/full/sparse pools, retained bytes, signed boundaries, all
ten seeded attacks, and eight complete boss-only sequences. Without damage,
each rank reaches departure after15,411 updates; damage19 uses1,080 updates.
The traces include full440-bullet/16-gather/96-spark pools, templates, RNG,
common BOSS/explosions and private bit state. Actual original shared helpers
execute; damage/audio/video/item/point consumers are bounded adapters.
Initial CPU production is archived separately from final hash-guarded native
reference replay. Each final replay also executes the four original divide
controls afresh. GNU, MinGW under Wine, optimized UBSan and actual Windows
agree on every record.1,024 original retained setup controls per build verify
common BOSS, callbacks and retained private26/template26/pool832/initializer
bytes. Setup itself does not reset those records; native private defaults
require a first encounter or explicit caller seeding.

20 contracts pass, and576 existing natural BMPs/628 counters agree across
Linux, Wine and actual Windows with every v1274 checkpoint unchanged.
The Linux GUI binary is unchanged; all23 Windows root files are unchanged.
21 static PE validation products live in `port64-preview/v1275`. Windows
execution is observed; Windows-host compilation and GUI pacing are not claimed.
No DOS source, exact acceptance, physical hardware or complete game claim changes.

Replay `port64/verify_marisa.py --target TARGET --exe CONTRACT --output-dir
NEW` for original CPU production. Only after that succeeds, use
`--reference-dir ORIGINAL_DIR` for a complete identity-checked native replay.
`port64/verify_marisa_setup.py` uses the same three required options.
`--runner wine` selects PE execution. Default Marisa contracts additionally
exercise callback rejection and original divide failure behavior.

Receipts under `.analysis/port64/marisa-v1275/`: `boundary-review.json`,
`original-divide-failures.json`, `original-caller-divide-failures.json`,
`producer-attestation.json`, `core-linux-full/original-reference.json`,
`core-{linux,windows,ubsan}-accepted/receipt.json`,
`setup-{linux,windows,ubsan}-accepted/receipt.json`,
`native-windows-{core,setup,receipt}.json`, and `integration-review.json`.
Cross receipt: `.analysis/port64/verification-marisa-v1275-accepted/receipt.json`.
Native source manifest:
c7619d2c5e51200ff508ebd6057bea44b2e8c309462f668da931594a6c43cb91.
Next connect Marisa rendering and actual pre/post-dialog gates, then Stage5.
Player death/Bomb/full HUD/audio/Ending/save remain pending.

After recording the final comparisons,4,064 v1275 validation BMPs are archived
with verified gzip readback, reclaiming another2.83 GiB. Receipts and CPU
fixtures remain live; `media-archive-receipt.json` records every original and
compressed SHA. Restore a private BMP path with `gzip -d -- FILE.bmp.gz`.

## Stage4 Marisa battle and rendering

v1276 connects the Marisa owner to the actual Reimu-player Stage4 pre-dialog
handoff. Both characters now play their respective NPC battle, post-dialog,
clear bonus and departure, then hold at the Stage5 pending-resource request.
Main state owns raw bit shots with against-Boss=false and body hits with true.
Shared gathers, score, frame prefix and explosion updates run once per simulated
frame; repainting consumes cached requests and cannot clear damage or age
explosions again. The native preview still lacks player death, Bomb, complete
HUD/audio, later stages, Ending and save.

Fresh MAIN0AAF:419E..4280/4281..42F0 review and original CPU controls prove the
ordered body, line, four bit and shared explosion requests. The body uses the
raw sprite without an animation offset; damage selects white FFC0/alpha plane0
and is consumed only below phase254. The packed alive centers form an open
chain for two bits and close for three/four, color9, before drawing the slots.
Bits require nonzero flag and signed centerX>-256,<6144 and centerY>-256,<5888.
Visible nonzero WORD damage selects rolling white and resets that WORD; hidden
slots retain damage. Slots4..31 and all private26 bytes stay untouched.

Expansion can move line endpoints outside the viewport. The shared older ray
consumer required in-screen endpoints, so direct reuse could fail during an
ordinary GUI repaint. Marisa now follows original0000:079A..080C clipping and
1562..16FE line rasterization: the actual stage rectangle is32..415/16..383,
inclusive. Clip X before Y, signed IDIV toward zero, then draw the existing
16.16 accumulator line from the clipped endpoints. Clipping the finished raster
instead changes boundary rounding.1,522 original CPU write-mask controls cover
both directions, corners, edge points and wholly rejected lines. These are
selected controls within ordinary coordinate bounds, not a general extreme
16-bit coordinate or physical GRCG color/aliasing claim.

13,606 original foreground controls compare ordered requests, complete
private26/pool832 retention, visible damage consumption and shared explosion/
flash clocks;5,888 shared NPC backdrop controls verify signed eight-frame cels,
BB pointer copies and call order. All eight64x64 Marisa BFNT images from
ST03B21.BBT and four32x32 bit images from ST03B22.BBT execute original normal
and white SUPER/rolling put routines0000:2F54/2838/2D3E/2B78.1,344 controls
compare344,064,000 complete indexed pixels across eight X alignments, retained
16-color backgrounds and seven signed top/bottom positions. Normal body does
not roll; bit puts do, with white coming from alpha plane0. Negative rows are
outside visible VRAM and only bottom overflow rolls. GRCG ports and visible
A800 plane writes use a bounded software shadow; page/scroll/timing and aliases
outside the visible surface are excluded.

Independent original producers are frozen separately from final native-only
reference replays. Linux GNU, MinGW under Wine, optimized UBSan and actual
Windows agree on all state/draw/background/line/pixel expectations. Final render
replays also regenerate all1,522 original line controls; final core replays
regenerate four original divide failures.7,759 Marisa core controls/87,031
records and1,024 retained setup controls still pass on every host.

Four fresh stage_state_init0AAF:73DB..74A5 controls execute actual REP STOSD:
all832 custom bytes clear while private DATA432E..4347 is retained. Initial
loaded private26 bytes are zero. Stage4 setup remains a separate common BOSS
reset, retaining Elly metadata. Native first encounter uses those initial
private defaults; do not generalize this to later reentry without explicit
retained owner state. Gameplay enables an explicit portable policy for attack1/
2 flystep durations12/13: extend them to14 to avoid the original zero divisor.
Default core comparisons leave this disabled, and native policy contracts
verify both callers separately. Every other duration and strict flystep error
behavior stays unchanged; no natural original-route fault reproduction claim.

Eight natural Normal/Lunatic Reimu-player A/B shot/idle routes start from title
selection and traverse all preceding stages, actual Marisa attacks/bit pool,
post-dialog, bonus, fade417 and next-stage489 without injecting damage, phases,
spawns or RNG.162 new BMPs/170 counters agree across Linux/Wine/UBSan/actual
Windows.20 contracts and738 total natural BMPs/798 counters agree across hosts;
all preceding576 BMPs/628 counters and earlier menu/shooting captures remain
identical. Dialog and the Stage5 frontier freeze simulation/RNG. This headless
coverage is separate from GUI frame pacing and original ordinary-route equality.

21 static PE validation products are in `port64-preview/v1276`. After complete
readback, the native GUI EXE/English launcher alone replace the root Windows
preview;21 DOS/HDI/config/font/build files remain identical. No GUI is launched.
Windows execution and MinGW cross-compilation are separate observations.
DOS source and exact acceptance are untouched. Semantic remains stopped.

Replay `port64/verify_marisa_render.py --target TARGET --exe CONTRACT
--output-dir NEW` for original foreground/backdrop/line controls; only after
that succeeds use `--reference-dir ORIGINAL_DIR` for complete guarded draw/
backdrop replay (line controls still execute the original CPU).
`port64/verify_marisa_pixels.py` takes the same options plus `--hdi HDI`.
`--runner wine` selects PE execution. GUI natural routes use
`--marisa-screenshots DIR`; aggregate drivers include both NPC routes.

Receipts under `.analysis/port64/marisa-render-v1276/`: target-review.json,
stage-reset-controls.json, producer-source/manifest.json,
line-producer-source/manifest.json, render-linux-full/receipt.json,
pixels-linux-full/receipt.json, render-{linux,windows,ubsan}-accepted/receipt.json,
pixels-{linux,windows,ubsan}-final/receipt.json,
core-{linux,windows,ubsan}-accepted/receipt.json,
setup-{linux,windows,ubsan}-accepted/receipt.json,
native-windows-{core,setup,render,background,line,pixels,receipt}.json,
integration-review.json and windows-export-receipt.json.
Cross receipt: `.analysis/port64/verification-marisa-render-v1276-accepted/receipt.json`.
Native manifest:3adf253ed25e0a48be20efd71e94d70ad0de70864755b752b156cd0d003bc000.
Next port Stage5 resources/midboss/boss; reopen semantic only for concrete
ambiguities needed by that implementation.

Final validation media (4,785 files: BMPs and the redundant native pixel stream)
are losslessly archived after hash/counter readback, reclaiming3.66 GiB.
`media-archive-receipt.json` records all original/compressed SHA-256 values;
original CPU pixel references, fixtures and current builds remain live.
Restore private media with `gzip -d -- FILE.gz` before an old-path replay.
