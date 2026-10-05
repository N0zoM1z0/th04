# Stage 6 Render Flow evidence

Historical bounded results, preserved from `docs/PORT64.md`. Current state is
[the port overview](../../PORT64.md). Original CPU execution and adapter scope
remain explicit; successful component controls do not accept complete gameplay.

## Yuuka6 foreground dispatch

v1287 ports MAIN0AAF:712A..72A5 (380 bytes) as a separate `Foreground`
owner. The original DATA46C3/46C4 flash counters are independent of the core
update dispatcher. A visible hit uses red on even parity, normal on odd parity,
then increments its BYTE counter and clears that body's damage. A frame without
hits retains parity. Hidden sprite0 preserves both damage bytes and both
counters, even with an active mirror. The optional auxiliary sprite precedes
the two body halves and the mirror. Sprite255's second half remains WORD256;
negative subpixel positions use signed SAR4 rounding rather than host division.
Red requests attest the original erase-mask0/planeFFCD arguments, distinct
from the custom crosses' white planeFFC0. Actual plane pixels remain separate.

Phase255 returns immediately. Phase254 emits only zoom factor3 and returns;
neither branch ages common explosions or dying crosses. Ordinary phases retain
small-explosion2D9C, big-explosion2E65, thick-laser37D3, custom7054 order.
`prepare_render()` consumes hit bytes and advances those render-owned states
once per simulation frame; cached `draws()` repaints do not advance them again.
Safety-circle GROW's mode/color/disc requests deliberately omit disable, while
its ring path includes disable. A separate render owner preserves the existing
core Snapshot layout and update ABI. These comments name original ownership
and widths without reopening general semantic work or changing DOS source.

One fresh original CPU producer matches3,522fixtures/4,458 complete records,
covering phase/hidden/aux/mirror combinations, flash BYTE parity/wrap, signed WORD
positions, original explosion controls, laser modes, all31 simultaneous custom
slots and24 retained40-frame sequences. Records include boss35/additional16,
explosion48, laser72, custom832 bytes, flash/damage/palette/hit globals and the
ordered8-field graphics requests. Original foreground and all four rendering
owners execute; sprite/zoom/circle/color callees are explicit request adapters.
Fresh callback rejection, one-byte comparator rejection and an actual two-input
body-parity control distinguish red from normal while mirror parity stays red.
The original reference is produced before native comparison and retains its
source manifest. Wine, optimized GNU UBSan/bounds and actual Windows consume
and match that independent reference. Windows does not claim original CPU
execution. Full raster pixels, physical PC98 page/alias/VRAM, frame pacing,
ordinary final battle and Ending remain separate requirements.

The three incremental builds pass28CTests/29products each. All28 preceding GNU
products remain raw-identical. Restoring eight retained timestamp/checksum
bytes recovers all28 preceding PE hashes.25 oldUBSan products are raw-identical;
the three changed motion/attack/core contracts pass36,045/39,757/90,702 retained
independent records. No debug-only or raw equality is claimed for those changed
products. All product architectures and compiler/cache identities are checked.
The no-font Linux resource smoke also passes. No DOS exact acceptance changes.
Source manifest: `0b47d197a1899f132dc4e2594b56c16670674d5493d629095df0419b07d6d2eb`.
Receipts: `.analysis/port64/yuuka6-render-v1287/`. Replay with
`port64/verify_yuuka6_render.py --target MAIN --exe CONTRACT --output-dir OUT`;
add `--reference-dir ORIGINAL_DIR` for a hash-checked consumer or `--runner wine`
for PE execution. Actual Windows uses the private
`port64-preview/v1287-yuuka6-foreground/verify-foreground.ps1` streaming gzip
control. GUI staysv1282; all23 published root game/config/save/script files
remain hash-identical. Next: actual foreground pixels, checkerboard/particle
background and ordinary final-battle join, followed by remaining complete-game
owners. Semantic remains stopped except for a concrete port ambiguity.

## Yuuka6 checkerboard and particle background

v1288 ports MAIN0AAF:7586..7632 checkerboard, 7901..7934 center clip,
7937..7970 wrap clip, 7971..7D8B particles and 7DC9..7E88 background prefix.
7D8D..7DC8 is jump-table data; adjacent alignment bytes remain separate.
No DOS source, authored-unit ledger or exact acceptance changes. The original
Japanese target remains candidate-local-attested.

`Background` owns 56 active Q12.4 shapes and a retained sentinel, BYTE state,
fade and palette latch, WORD pattern/flyout speed, symbolic clip callback and
opaque 16-bit BB resource tokens. It receives the existing shared random ring;
a private RNG would change subsequent combat. Initialization only occurs at
phase0 clock2 and consumes112 samples. Entry fade0 selects wrap for states0/8/12
and center for6/10; a same-frame transition retains that entry callback.
Transition arms may increment fade before their threshold and again in the
common tail. Incoming255 wraps before the comparison, while transition reset255
becomes0 at the tail. Palette-zero parity retains untouched components; the
late-state latch retains the previous palette after it sets.

The checkerboard preserves paragraph arithmetic, WORD offsets, BYTE pass count,
partial top rows and alternating dark columns. Its numeric store addresses never
become host pointers. Original flat visible writes include row384 below the
playfield: host playfield clipping would reject the independent pixel controls.
The mono16 kernel preserves unsigned X shift, WORD row offsets and visible-byte
filtering rather than host XY clipping. Every background update advances once;
cached requests and checker stores can repaint without consuming RNG or state.

One fresh original CPU producer passes2,220fixtures/5,711 complete state/request
records. These include two retained1,571-step caller-driven phase sequences,
clip boundaries, fade parity/threshold/wrap, palette latch, initialization,
negative entrance clocks, RNG cursor wrap and retained sentinel/resource tokens.
Actual RNG, atan/vector, clip and checker owners execute; state fixtures adapt
fill, BB and mono calls into ordered requests. Separately114 pixel fixtures
execute actual checker/mono/color kernels through an independent GRCG shadow:
80 retained checker frames and107 mono frames, including the eight actual
MIKO16 particle masks, all eight X alignments and selected signed WORD edges.
All187 full640x400 screen buffers agree byte-for-byte (47,872,000 pixel bytes
plus640 checker descriptor bytes). GNU, Wine PE, optimized UBSan/bounds and
actual Windows consume the same independent original reference. Each Python
control rechecks callback rejection; a one-byte comparator mutation rejects.
A fresh two-input incoming fade0/1 control changes the selected clip callback;
correct native records agree and swapping them rejects.

These controls do not prove combined BB/fill/particle composition, physical
PC98 VRAM alias/page/palette hardware, frame pacing, whole combat or DOS exactness.
Checker inputs are bounded to visible-layout paragraphs A850..AF6C; stored pass0
means256 passes in the implementation but is outside this pixel matrix. Existing
atan INT16_MIN displacement remains an explicit excluded/rejected input.

Three incremental builds pass29CTests/30 AMD64 products each. All29 previous
GNU and UBSan products remain raw-identical; restoring eight retained PE
metadata bytes recovers all29 previous PE full hashes. No cold DOS exact claim.
GUI/launcher stayv1282 and all23 published Windows root files are unchanged.
Only the private background contract package is added. Source manifest:
`aea4d05ef79705449c5883fe582861003528177a6cee6784b8a98c8ea8d0bf8f`.
Receipts: `.analysis/port64/yuuka6-background-v1288/`. Replay:
`python3 port64/verify_yuuka6_background.py --target MAIN --hdi HDI --exe CONTRACT
--output-dir OUT`; add `--reference-dir ORIGINAL_DIR` for a hash-checked consumer
or `--runner wine` for PE. Actual Windows uses private
`port64-preview/v1288-yuuka6-background/verify-background.ps1` with binary-stream
gzip capture. Root fresh Ghidra is READY; native private database replay skips.
Root/native CI and diff-check pass.
Next: actual foreground red/white/zoom pixels and ordinary final-battle join,
then remaining complete-game owners. Semantic stays stopped except for a
concrete native ambiguity; this dependency batch does not complete the port.

## Yuuka6 foreground sprite pixels

v1289 supplies `yuuka6::raster_sprite()` for the foreground requests accepted
in v1287. Normal, white and phase254 factor3 use the already controlled Yuuka5
kernel. Red reuses its alpha/WORD-offset walk and merges only destination bit1.
Observed MAIN0000:2838 takes planeWORD FFCD and emits GRCG modeCD/tileFF;
PC98 plane order B/R/G/I therefore enables red while retaining blue, green and
intensity. Filling indexed color2 would erase those three bits. The new source
comments make this ownership explicit; no DOS source or exact ledger changes.
Resolve each pattern to its actual sheet before drawing: all62 Stage6 body,
auxiliary and cross patterns128..189 come from ST05.BB1/2/3/4/5/6/7/9, while
phase254 death4..11 uses32x32 MIKO32 instead of the48x96 body sheet.

One fresh original CPU producer matches2,405 complete640x400 indexed screens,
615,680,000 compared pixel bytes. Controls cover all62 Stage6 images in normal,
white and red modes at all eight X alignments, selected vertical and signed
WORD edges, all eight actual death images at16 selected factor3 positions,
96 ordered six-sprite body/mirror/aux/cross overlap frames and62 retained
normal-then-red frames. Each screen retains destination pixels across its
ordered draw sequence; the original SUPER/ONEPLANE/ZOOM and downstream
color/rectangle kernels execute. BFNT alpha/four-plane staging is an explicit
input adapter; an independent GRCG shadow produces the reference, never the
portable raster. A target-only red/white pair proves destination color5 becomes
7 for red versus15 for white, and rejects a swapped screen. Fresh guarded
callback and one-byte comparator rejection also pass. GNU, Wine PE, optimized
UBSan/bounds and actual Windows consume the same independent reference.

The changed foreground contract also replays the existing3,522fixtures/4,458
complete state/request records on GNU/Wine/UBSan and actual Windows; the v1287
producer manifest remains attached to that reference. All three builds pass
29CTests/30 AMD64 products each. The other29 GNU/UBSan products are raw-identical;
restoring eight retained PE metadata bytes recovers all29 previous PE hashes.
No debug-only equality or cold DOS exactness claim. GUI remainsv1282 and all23
published Windows root game/config/save/script files remain hash-identical.
Only a private pixel-contract package is added.

Screens attest bounded visible kernel composition, not ordinary boss update/
foreground dispatch integration, safety-circle pixels, BB/background composition,
physical VRAM page/alias/scroll/palette hardware or host pacing/FPS. Selected
negative-X WORD offsets remain flat visible writes; factor3 uses original stage
clipping. Historical library exclusion/provisional zoom-boundary states remain
unchanged; a fresh raw view reaches zoom RETF8 at327A..327C inclusive.
Target provenance stays candidate-local-attested.

Source manifest: `81b816fd7b8c096832d304d615c50729fb096e037986c9f57569adcc1ff3ca9c`.
Receipts: `.analysis/port64/yuuka6-pixels-v1289/`, including original-linux,
accepted-{windows,ubsan},foreground-{linux,windows,ubsan},native-windows-review,
target-review,build-review and root-ghidra-attestation. Replay:
`python3 port64/verify_yuuka6_pixels.py --target MAIN --hdi HDI --exe CONTRACT
--output-dir OUT`; add `--reference-dir ORIGINAL_DIR` for a hash-checked consumer
or `--runner wine` for PE. Actual Windows uses private
`port64-preview/v1289-yuuka6-pixels/verify-pixels.ps1` and captures binary stdout
through streaming gzip. Root/native CI and diff-check pass; fresh root Ghidra
READY, native private database replay skips. Next: ordinary final-battle join
with the accepted core, entities, foreground and background owners, then the
remaining complete-game owners. Semantic remains limited to concrete ambiguity.

## Yuuka6 ordinary battle and Final Stage departure

v1290 connects the already controlled motion, attacks, entities, core,
foreground and background to the normal Stage6 dialogue completion. No stage
skip, seeded boss phase, forced HP or synthetic damage is used by the live
route matrix. The common Stage6 boss metadata and the same process/random
ring continue into combat; dialogue does not refill the ring or reset lasers.

The observed MAIN loop0AAF:0098..0212 calls the background before player,
shots, bullets and boss, with foreground after items/gather. The native join
keeps that order: background initialization/scatter draws from the shared
ring in the frame prefix; foreground consumes body/mirror hit flashes and
ages dying crosses once in the suffix. Host repaints consume cached draws.
The byte contact latch is bridged across bullet, laser and cross owners;
body hits use boss shots and mirror/cross hits use ordinary shots.

The host consumes the actual62-image battle bank, MIKO16 mono masks,
checkerboard stores and BB transition. BB0AAF:1426..14A2 uses DATA:BA8A color
and one-bit cells, not a freed CDG16 image. Normal/white/red/death zoom use
accepted sprite kernels; circle/disc and common explosion requests reuse the
existing native primitives. Complete physical PC98 page/alias/scroll/palette
composition is not independently proved by this live join.

The first natural run rejected `released MAP/STD streams updated`: dialogue
had freed those streams, but the frontend still advanced the map after the
first boss update. Keeping the release guard and skipping the released owner
repairs the real path. Every live matrix route now reaches the actual final
battle, including checker/particle updates, safety circles, crosses, mirrored
attacks, thick lasers and both death phases.

`update_final_departure()` owns the stage_id5 arm of13A9:ACB3..AE86. Tone60
precedes clock0 graze publication and all-clear9E06. All-clear disables score
extends; no post-dialogue is opened. At416 the original calls0AAF:0CC9
`end_game()` before the actor-frame suffix, leave fade and clock/homing
increment. The native frontend exposes a Good Ending request and holds there
until MAINE is ported; it does not flush pending score early or synthesize
MAINE statistics. The independent departure controls stop at that original
nonreturning call. A preliminary injected488 fixture followed the generic
next-stage arm, which is unreachable after that call; it is outside this
Final Stage natural-path contract, not accepted native equality.

Validation:

- Three incremental builds pass29CTest/30AMD64 products each. GNU retains19
  complete previous products; restoring only eight recorded PE metadata bytes
  recovers19 previous PE hashes. UBSan retains15 raw products; changed core and
  foreground consumers also replay their independent references below.
- Sixteen Normal/Lunatic, Reimu/Marisa, A/B, idle/real-shot routes cover
  phases0..17,254,255, the attacks and all-clear. The512 Stage6 images and528
  complete counters agree GNU, Wine, optimizedUBSan and actualWindows.
  Repaint controls guard frame/RNG, background particles/checker/palette,
  body/mirror flash, custom death ages and laser clocks.
- The public GNU/Wine verifier preserves all28 earlier v1282 image/counter
  groups. ActualWindows executes29 contracts and2,060 ordinary route images;
  its22 image/counter groups agree with the public replay.
- Fresh hash-attested original departure execution passes2,052 bounded calls
  on GNU, Wine and UBSan; actualWindows consumes those original records.
  Callback rejection and Ending-versus-fade mutation fail closed. All-clear
  math, full MAINE and original whole-route comparisons remain separate.
- Changed GNU/UBSan core products pass3,137 fixtures/90,702 complete retained
  original records; the original v1286 producer identity remains distinct.
  Changed UBSan foreground passes3,522 fixtures/4,458 retained v1287 records.

Manifest: `bbe0e09ba94269e1d659d25a83aa261f0e8130fc3903230cec82fc7ad4eba7a3`.
Receipts: `.analysis/port64/yuuka6-join-v1290/`, including target-review,
source-freeze, integration-final, previous-route-review, native-windows-review,
departure-{linux,wine,ubsan}, departure-native-windows-review, core-{linux,ubsan},
render-ubsan, build-review and deploy-receipt. Reusable CPU replay:

```sh
python3 port64/verify_yuuka6_departure.py --target MAIN --exe TRANSITION_CONTRACT \
  --output-dir NEW
```

Add `--runner wine` for PE. `--stage6-screenshots DIR` exercises the whole live
route through the Ending request; supplied HDI/font and recorded binary hashes
are required. Completed generated BMPs are archived losslessly with SHA
readback to keep the earlier cleanup effective. No FPS, complete-game, original
whole-route or DOS exact claim is made. Next owners are native Ending/save,
Extra, death/Continue/Bomb, remaining HUD/audio/config persistence. Semantic
work remains limited to an ambiguity that blocks one of those owners.
