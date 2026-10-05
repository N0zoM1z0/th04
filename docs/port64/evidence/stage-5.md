# Stage 5 evidence

Historical bounded results, preserved from `docs/PORT64.md`. Current state is
[the port overview](../../PORT64.md). Original CPU execution and adapter scope
remain explicit; successful component controls do not accept complete gameplay.

## Stage5 resources, stars and Yuuka pre-dialogue

The native GUI now consumes the actual Stage4 departure request and continues
through Stage5 STD waves, the scrolling star layer and both characters' Yuuka
pre-dialogue. Sixteen Normal/Lunatic, Reimu/Marisa, A/B-shot, shooting/idle
routes run 6,080 Stage5 simulation frames each. The GUI then holds at the
ordinary Yuuka battle boundary; that Boss owner is the next implementation.
Semantic work remains limited to concrete port ambiguities.

MAIN `13A9:A932..A9EB` disables the midboss callbacks and sets start frame 60000.
Its `boss_reset` retains HP/endHP/angle, additional bytes 1..15 and explosion
metadata; setup overwrites only position/sprite/hitbox, interval byte0 and
three star centers. Actual `midboss_reset` also clears HP and active; it retains
other actor metadata. 1,024 original CPU controls compare complete 24-byte boss storage,
16 additional bytes, 48 explosion bytes and 22-byte midboss storage. Five separate original
activation controls confirm the null callback set still becomes active at 60000;
this is a metadata probe, not a natural route reaching that frame.

The bounded original session case4 arm `0AAF:05E4..0653` independently confirms
BSS4.CD2, ST04.BFT, ST04BK.CDG, ST04.BB, ST04.CDG and ST04.MPN request order.
There is no BMT append. Stage5 initially owns 12 sprites at 128..139 and its BFT
palette; dialogue replaces them with ST04.BB1's one 64x64 sprite and BB2's
eight 48x96 sprites, ending at 137. Sixteen independent archive portrait/palette
checks compare 197,728 opaque pixels after the dialogue resource replacement.
File and hardware consumers are bounded adapters; the session arm is entered
after bootstrap, not a complete original session execution claim.

Stars start at Q12.4 centers at 320/40/190 pixels, move 4 pixels per completed frame,
and wrap once at 400. `0AAF:40FE..4168` skips updates during phases 1..253.
Signed WORD addition/SAR and one-row correction preserve malformed-state edge
requests; the physical raster accepts ordinary placements only. The invalidator
`4169..419D` records 96x80 boxes at the preceding center. 1,820 actual CPU star/
invalidation controls include signed edges and 800 trajectory checkpoints.

Original `130E:063A..06BB` ORs CDG source plane B into destination plane I/E000,
with bottom-up rows and physical 400-row wrapping. It preserves other colors;
a four-plane opaque sprite replacement is wrong. 504 actual CPU controls compare
16,128,000 complete plane bytes across aligned left edges, wrap points, display
origins and retained color backgrounds. Native lower-color/OR invariants also
pass. This flat visible VRAM model does not prove physical aliases/pages/scroll
hardware or frame pacing. Host redraw replaces the original dirty rectangles.
Cached star requests make repaint and blocking dialogue side-effect free.

Linux/Wine/actual Windows pass 21 contracts, 850 total natural BMP checkpoints and
926 counters. The 112 new Stage5 BMPs / 128 counters also agree under optimized
UBSan/bounds; all 30 preceding image/counter groups remain identical. Dialogue
and the pending Boss boundary freeze simulation, both RNG owners, score and
star centers. This is a bounded native frontier, not full-game or DOS exactness.

Receipts are under `.analysis/port64/stage5-v1277/`; `final-linux/receipt.json`
contains the fresh original producer and independent portrait checks.
`session-arm.json`, `null-midboss-activation.json`, `target-review.json`,
`integration-review.json`, and native reference-consumer receipts retain their
scopes. `test-config-continuity.json` records a final CTest-only argument fix:
all 22 products stayed byte-identical after three incremental rebuilds, and the
proper 21 test invocations passed. Earlier scenario/reference receipts keep their
original source manifest; the explicit continuity receipt bridges to the final
manifest 581547d4f74da59a984ad83f6a247bdc38735b923820e9765b8621a31b9a2115.
No historical receipt is relabeled as a new run.

Replay the component claim with:

```sh
python3 port64/verify_stage5.py --target /path/to/pinned/MAIN.EXE \
  --hdi /path/to/legal/zun.hdi --exe /path/to/th04-port64-stage5-contracts \
  --output-dir .analysis/port64/stage5-controls
```

Optional `--frames` names the 112 Stage5 BMP directory and enables independent
portrait checks. `--stage5-screenshots DIR` on the main executable generates
sixteen natural routes from the title; no injected phase/damage/spawn/RNG.
Windows v1277 exports only the GUI/English launcher and retains v1276 backup;
21 root DOS/HDI/config/font/build files stay unchanged. The native preview
still lacks player death, Bomb, complete HUD/audio, subsequent Bosses/stages,
Ending and save. DOS exact ledgers and maintained DOS source stay unchanged.

After final readback, 3,078 private validation BMPs are losslessly archived,
reclaiming 2.15 GiB. `media-archive-receipt.json` records every original and
compressed hash; restore the historical image paths with `gzip -d -- FILE.gz`
before replaying image comparisons. Original CPU references remain live.

## Thick-laser state and graphics producer

The v1278 dependency batch ports the complete two-slot laser owner into
`port64/thick_lasers.{hpp,cpp}`. MAIN 13A9:22E4..243D supplies initialization,
24-byte template transfer, first-free allocation, lifecycle and collision;
0AAF:37D3..3970 supplies the ordered graphics producer. Original target identity,
fresh database attestation and raw instruction review precede the CPU controls.
The DOS sources and accepted exact extents are unchanged. Target provenance
remains `candidate-local-attested`.

The native record explicitly names Q12.4 origins, pixel radii, signed WORD
clocks and all retained bytes. Initialization clears only the two actor flags
and scratch flag/clock/radius/speed. Template transfer retains the four bytes
after the origin and all other metadata. A full pool makes no allocation or
sound request. Transitions reset the clock and then increment it; the final
shrinking frame also increments after becoming free. Unknown nonzero BYTE
states preserve the original unsigned collision gate. The hit latch is retained
until the owning game frame clears it, and invincibility is consumed elsewhere.
Each shift/add/sub wraps before signed comparisons. Collision is narrower than
the displayed radius and begins below half the rounded cap.

The graphics producer preserves SAR4 coordinate flooring, signed IDIV width
rounding, upper-only quarter-width clamp, original outer/middle/white layer
ordering and unconditional GRCG disable. The outline successor is a WORD;
color 255 requests 256. Draw commands record the original FAR callee arguments,
including signed edge requests. This establishes command equivalence, not
circle/box/vline pixel equivalence, physical VRAM or frame pacing. Pixel
consumers and Yuuka foreground/background require separate controls when the
battle is joined.

Independent original CPU execution passes 8,464 cases and 13,975 checkpoints:
64 retained initializations, 64 full template copies, 144 allocations, 4,851
state/collision controls, 3,332 draw controls and nine retained lifecycle
sequences. Each checkpoint compares all 72 storage bytes, hit latch and ordered
sound/graphics requests. GNU Linux, static MinGW under Wine, optimized
UBSan/bounds and an actual PowerShell Windows process agree. Original callback
rejection and independent fixture-identity/trace-byte/extra-record negatives
are required and pass. The final source manifest is
`05e8bd69c1dc36bee294f661affce9e49db3ed5fbfa02c78c1d833dddea060be`.

All three incremental builds pass 22 CTests. Their 22 preceding Linux and UBSan
executables are raw-identical; all 22 preceding MinGW executables differ only
at their COFF timestamp and associated checksum. No previous GUI scenario is
relabelled as a new run, and no byte-exact DOS claim is made. Aggregate Linux/
Windows verification now requires the 23rd product and new laser contracts.
Root Windows game/launcher/saves/HDIs remain v1277. Only the new laser validation
program, fixtures, frozen manifest and verifier are exported under
`port64-preview/v1278-laser-controls`; no GUI launched.

Replay from the native worktree root:

```sh
cmake --build .analysis/port64/linux-live-v1251 --parallel 4
cmake --build .analysis/port64/windows-live-v1251 --parallel 4
python3 port64/verify_lasers.py \
  --target ../../targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-laser-contracts \
  --output-dir .analysis/port64/yuuka5-v1278/laser-linux-final
```

Receipts live under `.analysis/port64/yuuka5-v1278/`: `target-review.json`,
`producer-source/manifest.json`, `laser-{linux,windows,ubsan}-final/receipt.json`,
`native-windows-receipt.json`, `oracle-negative-controls.json`,
`windows-link-continuity.json`, `previous-binary-continuity.json`,
`integration-review.json` and `windows-test-export.json`. The raw continuity
receipt deliberately reports Windows differences; the separate full-file
comparison proves their exact header-only locations. Original references and
current builds remain expanded. Next: Yuuka's phase/attack dispatch, then its
rendering and ordinary Stage5 battle join. The GUI still stops after pre-dialog.

## Stage5 Yuuka core and seven attacks

The native `yuuka5` owner now implements MAIN13A9:243E..2F89: the movement
transition, sweep/cloud/gather/speedup-ring/aimed-spread/laser-burst/mirrored
attacks and ordinary boss phase dispatch. The original extent includes two
alignment bytes, four gather cases, twenty laser cases, two mode tables and
nineteen phase destinations. Target/header/relocations and a fresh root Ghidra
attestation precede execution. DOS product source and exact acceptance remain
unchanged; provenance stays `candidate-local-attested`.

Named attack/state fields expose retained ownership. Movement wraps the WORD
coordinate difference before signed division by64; its caller advances the
clock and skips shot damage during movement. Entry refreshes only bullet
origin before motion. Early pair exits subtract800 from the next threshold;
late pairs retain it. Gather timeout bypasses the hit wrapper, whereas the
final phase advances/hits before evaluating its1000-frame bonus cutoff.
Default defeat dispatch omits the laser/HUD tail. The VM callback is represented
as a null/retained dispatch token, without treating a16-bit FAR pointer as a
native address. Phase0 writes that token and clears the midboss countdown.

Original shrinking-circle calls use0AAF:1BA6, not the adjacent growing entry;
mirrored-stream setup writes special-motionFF. Cloud counters and private tone
wrap as BYTEs; published palette tone remains a WORD. Bullet spawn contact and
laser contact share a player-hit BYTE: new contact writes1 even over a retained
127. The native join preserves that write while retaining the bullet owner's
separate bool. The game frame must clear both representations at its boundary.

Fresh original CPU production and GNU Linux comparison pass7,330 fixtures and
69,652 checkpoints:1,620 isolated moves,2,408 helper edges,3,259 dispatcher
edges,35 complete attack sequences across five rank settings and eight retained
whole-boss controls. Each Easy/Normal/Hard/Lunatic win/timeout control visits
phases0..18/254/255 and reaches the departure request. Timeout controls traverse
both pair attacks and all four mode tokens. These controls retain all boss,
additional/private, template, bullet/gather/spark/explosion/laser storage,
shared counters, VM classification and ordered requests. Injected shot damage
and downstream circle/HUD/item/point/dialog/audio/delay consumers are explicit
adapters; ordinary actor updates, render and actual stage loading are absent.
This is not a completed native Stage5 gameplay claim.

Static MinGW under Wine, optimized UBSan/bounds and an actual PowerShell Windows
process match the independently produced records. Three comparator mutation
controls, callback rejection and invalid native argument checks pass. All three
incremental builds pass23 CTests and validate24 ELF64/staticPE products each.
All23 GNU predecessors remain raw-identical. All23 preceding MinGW programs
differ only in COFF timestamp/checksum. Nine UBSan predecessors are identical;
fourteen differ after recompilation, so no raw continuity is claimed for those.
Fresh UBSan execution of sixteen preceding Stage5 routes preserves112 image
hashes and128 counters; their media are losslessly gzipped with readback checks.

The final source manifest is
`ce458897179e6fb05588a575119e651d07ca067d3bdcfaee7cbf3468fdef523a`.
Root Windows game/launcher/saves/HDIs remain v1277. Only validation PE, fixtures,
manifest and PowerShell/results are exported under
`port64-preview/v1279-yuuka-controls`; no GUI launched. Next is Yuuka foreground,
backdrop and laser raster validation followed by the ordinary Stage5 battle
join. Semantic work remains stopped except a concrete port ambiguity.

Replay from the native worktree root:

```sh
cmake --build .analysis/port64/linux-live-v1251 --parallel 4
cmake --build .analysis/port64/windows-live-v1251 --parallel 4
python3 port64/verify_yuuka5.py \
  --target ../../targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-yuuka5-contracts \
  --output-dir .analysis/port64/yuuka5-v1279/yuuka-linux-final
```

Use a new output path when repeating a producer. Receipts under
`.analysis/port64/yuuka5-v1279/` include `target-review.json`, frozen
`producer-source/manifest.json`, `yuuka-{linux,windows,ubsan}-final/receipt.json`,
`native-windows-receipt.json`, `oracle-negative-controls.json`,
`previous-nonwindows-continuity.json`, `windows-link-continuity.json`,
`preceding-stage5-ubsan-review.json`, `integration-review.json` and
`windows-test-export.json`. The non-Windows raw comparison deliberately records
UBSan differences; its fresh scenario receipt is separate evidence. No physical
PC-98 timing/pixels, GUI FPS, full-game or DOS exact claim is made here.

## Stage5 Yuuka foreground and raster controls

`yuuka5_render.cpp` now owns MAIN0AAF:3DB3..3F7E foreground requests and
0AAF:7874..7900 backdrop decisions. Target review records11 complete physical
spans/1,535 bytes, including the rectangle's separate1076 shared return and
zoom31A2's self-modified immediates. Root preflight and fresh root Ghidra
header/entry/relocation/full-byte checks pass. Targets retain the local provenance
gap; portable results do not promote DOS source or exact acceptance.

Idle Yuuka draws two48x96 images separated by48 pixels. The64x64 entrance image
is also used during the three movement-disc transitions. Phase254 requests
factor3 zoom, distinct from the earlier shared large-sprite path. Damage resets
only in the visible entrance/idle white branches. Shared explosions advance
once after body requests; lasers draw afterward only below phase255. Cached
requests separate simulation/render ownership from subsequent repaints.

Backdrop phase1 divides the signed clock by4, then tests only unsigned AL.
Its picture branch clears the uncovered regions before CDG; stable phases use
common7667, which puts CDG before calling the retained filler. Filler1508/7578
covers X32..127/Y128..383 plus X32..415/Y16..127. The288x256 CDG at128,128
occupies the remaining region. BB/CDG/tile consumers remain their existing
separate owners; this batch compares their ordered requests and filler pixels.

An initial original CPU comparison rejects native sprite case864: normal SUPER
uses unsigned X SHR3 and a WORD row address. Negative X can produce a different
flat visible VRAM location, whereas host coordinate clipping drops those stores.
The corrected Yuuka normal/white raster preserves that address arithmetic.
Zoom reads the four color planes, skips color0 and paints clipped inclusive3x3
rectangles. Rectangle/vline endpoints are signed-sorted, then clip-origin
subtraction wraps as WORD; an ordinary host min/max clamp differs on extreme
inputs. Filled circles use the original midpoint horizontal spans and actual
stage clip32..415/16..383. Native disc raster rejects radii above512; pixel
controls cover0..180, while arbitrary WORD radii remain request-only evidence.

Final comparison passes9,936 request controls:4,446 foreground,5,120 backdrop,
370 original disc write masks. Another1,804 controls compare461,824,000 indexed
pixels:972 normal/white/factor3 sprite cases across all nine real BFNT images,
eight alignments, signed Y edges and selected negative X;832 rectangle/vline/
disc/filler cases retain16-color backgrounds and WORD color256. GRCG ports and
visible A800 writes use an explicit software shadow. General physical page/
alias/scroll/timing, GUI rendering and full Stage5 gameplay remain separate.

The initial frozen Oracle completed all972 original sprite screens before its
native mismatch. `original-pixel-production.json` records that production only;
it does not pass the rejected initial consumer. Final native consumers replay
those unchanged screens after the address fix. `producer-continuity.json`
proves identical ASTs for Original/Shadow/input/expected producer components and
identical bytes for five base/staging helpers. Final832 primitive screens and
all9,936 requests freshly execute original code. Each receipt records per-control
fresh-production/reference provenance; no old native pass is relabelled.

GNU Linux, static MinGW under Wine, optimized UBSan/bounds and an actual
PowerShell/native Windows process agree. The unchanged preceding Yuuka core
also replays7,330 fixtures/69,652 independent original checkpoints on final GNU
and actual Windows. Seven reference/output/native rejection controls plus
fresh callback rejection pass. Three incremental builds each pass23 CTests and
validate24 ELF64/staticPE products. All23 preceding GNU and23 UBSan programs
remain raw-identical;23 preceding MinGW files differ only at timestamp/checksum.
No prior GUI screenshot run is relabelled as a new run.

Final source manifest:
`7e410b8eff20d4f912f2c9e895a5c25e9e80e4c95ef18e388794d97810d91778`.
The root Windows GUI/launcher/saves/HDIs stay at v1277. Only diagnostic executable,
fixtures, assets, manifest and PowerShell/results are exported under
`port64-preview/v1280-yuuka-render-controls`; no GUI launched. Next is the ordinary
Stage5 battle join, including hit-latch clearing, palette/background phase
ownership and post-dialog/bonus/departure. Player death/Bomb/HUD/audio/Stage6/
Extra/Ending/save are still pending native work. Semantic work stays stopped
unless a concrete ambiguity prevents that implementation.

Replay from the native worktree root, using new output directories:

```sh
cmake --build .analysis/port64/linux-live-v1251 --parallel 4
cmake --build .analysis/port64/windows-live-v1251 --parallel 4
python3 port64/verify_yuuka5_render.py \
  --target ../../targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-yuuka5-contracts \
  --output-dir .analysis/port64/yuuka5-render-v1280/NEW-render
python3 port64/verify_yuuka5_pixels.py \
  --target ../../targets/th04/main.exe --hdi ../../runtime/images/zun.hdi \
  --exe .analysis/port64/linux-live-v1251/th04-port64-yuuka5-contracts \
  --output-dir .analysis/port64/yuuka5-render-v1280/NEW-pixels
```

Receipts under `.analysis/port64/yuuka5-render-v1280/` include target-review.json,
producer-source-initial/manifest.json, producer-source/manifest.json,
original-pixel-production.json, producer-continuity.json,
render-{linux,windows,ubsan}-accepted/receipt.json,
pixels-{linux,windows,ubsan}-accepted/receipt.json,
core-linux-accepted/receipt.json, native-windows-receipt.json,
oracle-negative-controls.json, previous-nonwindows-continuity.json,
windows-link-continuity.json, integration-review.json and windows-test-export.json.
`pixels-linux-final/pixel-mismatch.json` retains the rejecting initial observation.
Large redundant native outputs are gzip-archived with complete readback; current
original pixel/reference buffers stay live. Restore archived private output paths
with `gzip -d -- FILE.gz` before replay.


## Stage5 Yuuka ordinary battle and route-specific departure

The v1281 join activates the existing Yuuka owner only after the actual Stage5
pre-dialogue has installed the nine battle sprites. MAIN now owns its retained
boss metadata, two thick-laser records, shared bullet/laser contact latch,
shot damage, gather releases, homing, explosions and cached draw requests.
Background selection uses the pre-update phase/clock; palette0 and deferred
WORD tone come from the live Yuuka snapshot rather than the setup copy.
Phase1 uses signed clock/4 BB cels, white one-bit cells and the original
filler/CDG order. Ordinary battle freezes the stage star centers. Host full
redraw remains the replacement for dirty tile/EGC copies.

The first ordinary Easy route exposed a missing integration call: a default
laser scratch record has flag0, so add() copied inactive records and no laser
was drawn. Calling the original-shaped initialize() at stage initialization
arms LINE/radius/clock while retaining the other beam/scratch fields. The
rejected capture/log remains under development-routes; later routes observe
both line and wide lasers and transient contact writes. At each new simulation
frame, clear both representations of the shared player-hit latch; preserve it
through boss update and post-boss gather releases. Blocking dialogue resumes
the existing frame suffix, and repaint cannot clear the latch or age effects.
Player death remains a separate unimplemented consumer.

A correction to the preceding graphics discussion: phase254 actually resolves
patterns4..11 to MIKO32.BFT's eight32x32 death images. The64x64 entrance image128
is used in entrance/movement, not as the ordinary defeat zoom source. The v1280
factor3 pixel controls used the nine entrance/idle assets and therefore did
not independently cover this real death sheet. New --defeat-zoom-only controls
execute original31A2 with the eight32x32 images at16 edge/offset combinations,
comparing128 retained640x400 screens (32,768,000 indexed pixels). Historical
v1280 evidence remains scoped to its original asset set.

Original MAIN13A9:AD4D..AD6C tests stage_id4, continues-used BYTE DS4349 and
rank BYTE DS4348. Easy or any nonzero continues-used loads a separate bad
script, animates it and calls end_game_bad before normal clear bonus. Actual
0AAF:2411..242D mutates character offset3 of _DM04B.txt;0AAF:0CF4..0D1E writes
resident sequenceFE/type ASCII1, fades sound/palette and transfers to MAINE.
The independent stage/rank/continues/character matrix (96 invocations) executes these branches,
filename writes and resident publication; I/O/dialog/audio/video consumers are
explicit adapters and the transfer stops at GameExecl. Native comparison is
of the branch predicate. The natural Easy routes separately check the loaded
character-specific script, no normal bonus and no Stage6 request. Continue
statistics and actual native MAINE/Ending rendering have not joined yet, so the
GUI deliberately holds before that Ending call instead of inventing a result.

--yuuka5-screenshots traverses Stage1..4 naturally, then records18 Stage5
routes: sixteen Reimu/Marisa Normal/Lunatic A/B-shot/idle runs, plus both Easy
A-shot routes. It checks phases0..18/254/255, movement states, laser lifecycle,
all eight death frames, post-dialogue, bonus, fade417 and departure489, plus
simulation/RNG/resource/star invariants. The18 routes produce698 BMPs and716
counter lines; the16 ordinary routes request Stage6 while retaining resource
stage4 until that owner joins. Easy stops before Bad Ending. These are native
host scenarios, not independent original full-game or FPS evidence.

Receipts and source manifests live in .analysis/port64/yuuka5-join-v1281.
The Windows launcher remains English and describes the Stage6/Ending frontier.
DOS source, exact units and authored acceptance do not change. Semantic
readability remains stopped except for specific port ambiguities; Stage6 and
Extra, player death/Continue/Bomb, remaining HUD, audio, Ending and saved-data
I/O are still required for a complete native game.
