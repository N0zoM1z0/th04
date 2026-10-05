# Stage 6 Core evidence

Historical bounded results, preserved from `docs/PORT64.md`. Current state is
[the port overview](../../PORT64.md). Original CPU execution and adapter scope
remain explicit; successful component controls do not accept complete gameplay.

## Stage6 resources, waves and pre-battle dialogue

The v1282 join carries a normal Stage5 departure into ST05.MPN/MAP/STD/BFT,
BSS5.CD2 and the character-specific _DM05/_DM15 script, without restarting
MAIN or replacing its process LCG. Stage6 has16 initial32x32 BFT images and14
MPN tiles. Actual MAIN13A9:A9EC..AA87 loads only ST05.BB: there is no BMT,
new CDG picture or stage/midboss callback. CDG16 and the colorfill pointer
retain their preceding Stage5 ownership. Boss HP/endHP/angle, most additional
bytes, big explosion and midboss motion/phase metadata survive reset; the
new position is192x80 and hitbox radii24x48. Rank0..3 replace additional[0/1]
with48/64/80/96 and1/1/2/4. Native rejects rank4 here; Extra uses stagex_setup.
The original18A6 rank selector indexes stack arguments unchecked, and rank4
reads the far return CS instead of providing a Normal fallback. The rejected
initial assumption is retained in setup-linux.log; it does not describe the
final executable.

Before dialogue, actual0AAF:2454..24CD releases CDG31, STD and MAP for stage5/6
only when speed0/back-page1. Native frees the STD actor program and MAP/order/
speed streams, retaining the displayed tile ring and MPN bank. A released
background stream rejects updates; a pending Yuuka6 owner freezes simulation.
The original complete scene consumes cursor1044/910, rather than stopping at
the first inner '#'. Both scripts load BB1/2/3, close boxes, release CDG1..31,
load BB4/5/6/7/9 and request ST05B music before the final outer '#'. Native
invalidates live CDG handles and guards future portrait/backdrop use; cached
read-only archive bytes are not treated as live handles. The final sprite bank
is128..189: seven48x96 sheets plus eight32x32 BB9 images. No inert free callback
or prematurely activated boss substitutes for these requests.

Independent original CPU controls cover1,024 retained setups,42 resource gate
cases and four complete dialogue traces (two characters x held/released,
1,895 ordered events). Linux/Wine/optimized UBSan agree; actual Windows consumes
the retained setup/four dialogue references. Independent archive pixels check
217,744 opaque portrait pixels in16 native captures. File, video, waits, audio
and free consumers are explicit original-CPU adapters. These controls do not
prove original whole-route video or physical PC-98 timing.

--stage6-screenshots traverses Stage1..5 naturally and then16 Stage6 routes
(two characters x Normal/Lunatic x A/B x shot/idle). All reach frame5198's
stopped scroll/dialog gate and complete the pre-battle scene.112BMP/128counter
records agree GNU/Wine/actualWindows/optimizedUBSan, including353 LCG reset
draws, resource generation, callback ownership and dialogue/repaint/frontier
freeze. The full cross-host GUI passes with all34 preceding image/counter
groups unchanged; actual Windows checks23 contracts/1,660 route BMPs. Three
incremental builds each pass23 CTests/24 products. This is native integration
evidence, not an original full-route or FPS claim.
The changed Stage5-contract consumer also replays the retained v1277 original
reference:1,024 setups/1,820 stars/504 rolling-plane cases pass GNU/Wine/UBSan.
Only CRT CRLF is normalized in text;16,128,000 pixel bytes compare raw per
host. This reuses the independent reference without reexecuting original CPU.

Receipts are under .analysis/port64/stage6-v1282. Producer manifest68eda7fd;
final manifest08a9891b differs only in verify.py receipt.limit prose. The
reporter-continuity receipt verifies the otherwise identical AST and all24
complete products per host unchanged; completed producer receipts keep their
original manifest. Windows publishes native EXE c2542286 and the English
launcher, retains previous-v1281 and leaves21 DOS/HDI/config/font/build files
unchanged. No GUI is launched. Completed validation BMPs are losslessly gzip
archived after readback; restore private images with gzip -d before replay.

Next: port Yuuka6's actual core, attack helpers, animation/entities and
checkerboard/background/foreground, then join the ordinary battle. Extra,
player death/Continue/Bomb, remaining HUD, audio, Ending and save I/O also
remain required. Semantic work stays bounded to ambiguities needed by those
owners; the complete native game is not finished.

## Yuuka6 animation and motion helpers

v1283 recovers the eight animation entries and four movement entries at
MAIN13A9:6933..6E76 into port64/yuuka6.hpp/.cpp. This is the next dependency
for the final boss; the ordinary GUI still stops before its first update.
No DOS source or accepted extent changes. Semantic work only clarifies the
specific state ownership needed by this native slice.

All animation entries share the signed16-bit animation_frame. They increment
before testing cels and retain the incoming sprite on a terminal frame;
close/open stamp flags1/2 on every call, while the other six only replace the
flag on completion. A switch of animation does not implicitly reset its clock.
The caller separately owns phase_frame. Teleport animation executes before
clock64's position/mirror publication and clock128's completion. Mirror X is
wrapped6144-X, enabled for any nonzero mirror state, then the state becomes2.
Flight uses two actual five-node BYTE angle paths; every sixth patterns residue
returns to the center through the teleport helper. The112 completion does not
also move. Only legitimate paths0/1 are accepted when the table is accessed;
malformed native snapshots reject instead of reading adjacent original DATA.

Horizontal motion adds wrapped velocity before inclusive48/336-pixel reversal,
never clamps, evaluates the actual integer sine/polar displacement and advances
its BYTE angle by2. Centering accepts the subpixel interval[3072,3088); entering
that interval by a step still returns false. A just-completed appearance also
returns false and retains aux_flag until the following call. Source comments
explain these timing and retention boundaries for the later battle owner.

Three fresh original-CPU producers each pass20,463 fixtures/36,045 full state
records against GNU, Wine and optimizedUBSan. The comparator includes all24
boss bytes,10 contiguous animation/mirror bytes, the mirror-state BYTE and
return BYTE. Every patterns BYTE, both valid flight tables, all256 wave angles,
animation cels/negative/overflow clocks, mirror modes and retained helper
sequences are covered. Actual vector/polar callees execute; no downstream
file/video/shot/audio/timing consumer is invoked. DS writes outside these
owners fail closed. Callback exceptions and a one-variable return mutation
are rejected. Actual Windows consumes the independent reference and matches
all36,045 records; it does not execute the original CPU producer.

The three incremental builds each provide25 products and pass24 CTests.
All24 preceding GNU and optimizedUBSan executables are raw-identical to v1282.
All24 preceding MinGW products differ only in COFF timestamp/PE checksum
bytes; the complete remaining bytes agree. The no-font GNU/Wine integration
smoke passes the updated verifier, including the new contract. This does not
repeat the previously accepted full dialogue/route image matrix or prove
whole-battle rendering, physical PC-98 timing, FPS or DOS exactness.

Receipts live in .analysis/port64/yuuka6-motion-v1283; final source manifest
269abf2dc769c274edd4b4c847b0f52700ea67653ddf44729789d14634823134.
accepted-{linux,windows,ubsan} retains original fixtures/compressed traces;
native-windows-review,product-continuity,build-receipt and integration-smoke
record the distinct checks. The initial CTest configuration mistakenly passed
the new executable name to the old Yuuka5 contract; ctest-linux.log retains
the failure, and all three accepted CTest replays pass after fixing that
registration. Initial producer9479b49b is retained without relabeling it.
The Windows v1283-yuuka6-motion package contains only the new private contract,
fixtures, manifest and control script, avoiding25 duplicate full executables.
The published GUI/launcher and protected DOS/config/saves remain untouched.

Next: chase-cross/safety-circle entity ownership, gathering and attack helpers,
then the dispatcher and foreground/checkerboard join. Extra, player death,
Continue, Bomb, HUD, audio, native Ending and score save remain unfinished.

## Yuuka6 cross and safety-circle entities

v1284 ports four bounded owners at MAIN13A9:65F7..6932 and
MAIN0AAF:7054..7129 into `port64/yuuka6_entities.hpp/.cpp`: cross allocation,
safety-circle initialization, update and drawing requests. The final-boss
dispatcher has not yet joined these owners to the ordinary GUI. DOS source,
acceptance and the published v1282 preview remain unchanged.

The original DATA:B204 pool contains32 records of26 bytes. Cross allocation
scans all32, but update and render scan31 and reinterpret the last record as
the circle. Allocation retains spare words, previous-position bytes and
padding; a last-slot cross must not acquire a separate native lifetime.
Circle centers use screen pixels, while cross centers use subpixels. Its
polar position subtracts literal32/16 from the pixel intermediate before
scaling by16. Converting those offsets into2/1 pixels changes the attack.

Cross motion precedes its inclusive offscreen flag clear. The iteration still
executes contact, homing and ordinary-shot damage after that clear; a kill
can replace flag0 with death flag16. Age below56 turns one BYTE step toward
the player, including+1 when already aimed exactly. WORD damage and signed
HP subtraction wrap, score accumulation wraps as DWORD, and kill requests
consume the actual shared spark/RNG owners before a BigPower item request.
These are ordinary shots, with against-boss=false; a boss damage callback
would incorrectly add Bomb damage. The raw player-hit BYTE is retained until
new cross or spawned-bullet contact writes1. The eventual live caller must
bridge that shared process state with the bullet/boss owners each frame.

Circle growth reaches136 before a separate frame switches to shrink, retaining
the shrink clock. Shrink emits the original paired stack/spread pellets and
tuned aimed rings, including rank/performance, pool saturation and clear/zap
branches. Death flags advance during rendering, so `prepare_render()` runs
once per simulated frame and `draws()` can serve cached repaints. The growth
draw deliberately leaves GRCG enabled; the ring draw disables it. The native
API publishes ordered graphics requests here, rather than claiming actual
sprite/circle pixels or physical video timing.

One fresh original-CPU producer passes6,089 fixtures/9,031 checkpoints against
GNU. Wine and optimizedUBSan consume its independently produced reference;
all three also execute a fresh five-rank MAIN0AAF:0312..03D1 switch-tail
probe. This verifies the actual indirect add/tune callbacks, including the
shared Normal/Extra tail, without running the preceding resident/file/score
initialization. Actual Windows consumes the same fixtures and agrees on all
9,031 full state/request records. It does not execute the original CPU.
Checks include832 custom bytes, complete440-bullet/96-spark pools, scratch
template, RNG/score/hit globals, ordered events and draws. Allocation793,
circle initialization112, update2,131, render3,041 and12 retained224-frame
sequences cover dense pools, signed/unsigned wrap and all raw flag BYTEs.
Actual polar/atan, spark/RNG, tune and bullet-spawn callees execute; ordinary
shot damage, graphics, item and sound consumers are explicit request adapters.
Callback exceptions and a one-variable comparator mutation reject. Existing
atan excludes INT16_MIN displacement; extreme movement fixtures use age>=56.
These controls do not establish whole-battle behavior, frame pacing or exactness.

Two rejecting runs are retained. The initial reference used Normal callbacks
for an Easy fixture; its checkpoint2393 bullet-count mismatch was an Oracle
context error, not evidence of a native gameplay bug. After fixing the context,
checkpoint2830 found a native shared-state defect: spawned-bullet contact
left an incoming hit BYTE127 instead of writing1. The repaired bridge detects
each spawn's new contact before restoring the bullet bool. The rejected
f40959a5 source closure and GNU product are retained together in
`contact-negative-source-and-product.tar.gz`, with their hashes recorded in
`contact-negative-identity.json`; the passing product has a distinct identity.

All three incremental builds provide26 x64 products and pass25 CTests each.
All25 preceding GNU/optimizedUBSan products are raw-identical. For all25
preceding PEs, restoring only the retained eight COFF timestamp/checksum bytes
recovers the complete previous SHA-256; no other byte changes. GNU/Wine
no-font integration smoke passes; the full preceding font/route image matrix
is not repeated. The actual-Windows private package contains only the new
entity contract, fixtures, manifest and streaming gzip control, avoiding
duplicated old executables or expanded250MB state traces. The published GUI,
launcher and21 protected DOS/config/save files remain unchanged; no GUI launched.
Root and native `scripts/ci.py`, tracking validation and `git diff --check`
pass. Native CI skips its absent private Ghidra project; the fresh root MAIN
database attestation is retained separately. The304 completed no-font BMPs
are losslessly gzip-archived with SHA-256 readback, reclaiming218MiB; current
builds, caches, original CPU references and user saves remain available.

Receipts: `.analysis/port64/yuuka6-entities-v1284/`, including `target-review`,
`root-ghidra-attestation`, `accepted-{linux,windows,ubsan}`, `native-windows-review`,
`build-receipt`, `product-continuity` and `integration-smoke`. Source manifest:
dce4e3835be08c885c02b928fe21831183c069f3b18fcda62c4f0fa5c0c517f6.
Replay with `python3 port64/verify_yuuka6_entities.py --target TARGET --exe EXE
--output-dir NEW`; add `--runner wine` for MinGW or `--reference-dir REFERENCE`
to consume the independently produced fixtures/trace.

Next: gather and attack helpers, then final-boss core and foreground/checkerboard
integration. Extra, player death/Continue/Bomb, HUD, audio, Ending and save I/O
remain required. Reopen semantic only for a concrete port ambiguity.

## Yuuka6 gathering and attack helpers

v1285 ports17 bounded entries at MAIN13A9:6E77..7951: five gathering entries
and twelve attack entries, including four sparse compare/jump tables. The
existing `yuuka6::System` owns the methods in `port64/yuuka6_attacks.cpp`;
`Gathering` and `Attack` select explicit behaviors without changing its stored
layout. DOS source and acceptance remain unchanged. The ordinary preview still
holds before Yuuka6's first update; this dependency batch does not publish a
new playable battle or launch a GUI.

The same gather and bullet scratch templates persist across calls. Gather-only
allocation retains the saved bullet fields except spawn_type0, and retained
velocity/spare bytes survive even on a full pool. Side gathering ends at the
left center; dual gathering ends at the mirror center. Later circles use the
original shrinking entry0AAF:1BA6, with ordered requests and color publication.
The helpers do not advance the attack clock or update allocated entities.
Animation executes before later branch/gather tests; a terminal attack may
reset phase_frame before the final gather call. Cached repaints cannot replay
these calls.

Attack comments explain special/fixed-speed spawning, distinct mirrored origin
and heading, two laser origins, retained speed growth, random consumption even
when cross allocation is full, and the BYTE rotation's outward/return ordering.
The rotating-ring initializer aims boss-minus-player, opposite ordinary aim,
before its16-unit rotation. The spin attack changes the second origin angle
without replacing the retained template heading. BYTE count/speed/angle and
signed WORD quotients preserve their original widths. New spawn contact writes
the shared player-hit BYTE1, including over an incoming127; the future core
must bridge it with the entity/laser/frame owners.

One independent original-CPU producer passes5,305 fixtures/39,757 checkpoints:
375 gather fixtures,4,822 isolated attacks and108 retained320-frame sequences.
The comparator includes35 boss/animation/mirror bytes,16 additional bytes,
circle color, hit/RNG/special globals, both templates, complete440-bullet,
16-gather, two-laser plus scratch and32-custom pools, and ordered requests.
Actual animations, vector/atan, RNG/tune/regular/special spawn, gather and
laser/cross/safety-circle allocation execute. Circle and sound consumers are
request adapters; spark/ordinary-shot ownership is also checked unchanged.
Sequences do not advance ordinary actors, pool updates, pixels or the battle
dispatcher. Five ranks, density, performance, clear/zap, raw flag/angle and
signed clock/coordinate boundaries are covered within the recorded domain.

The first control omitted BCC2, the special producer callback, despite setting
regular BCC0 and tune BCC4. Guarded execution rejected the resulting unrelated
code path at fixture388; this was an Oracle context defect. The corrected
five-rank switch-tail probe executes MAIN0AAF:0312..03D1 and checks all three
callbacks. A one-field BCC2 mutation reproduces the rejection. A separate zero
dual-spread-range control reaches original MAIN13A9:02F6 DIV WORD SS:[BX+2]
after two random samples; GNU/Wine/UBSan explicitly reject the zero divisor.
Native partial state is not exposed or compared on that exception. Existing
INT16_MIN atan and count-zero ring fault/portable-repair limits remain separate.

The fresh full CPU producer retains manifest8b4343e0. Final685c4c37 names
pattern constants, explains reverse aim and splits a terminal return to remove
a warning; its final header comment distinguishes attack completion from
`animate()` alone. All27 GNU/UBSan products match the already-passing ff96
files raw, and all27 PEs preserve every nonmetadata byte. The no-font smoke
keeps its ff96 producer identity, linked through `comment-continuity`; the
complete new GNU contract remains raw-identical to the8b43 producer. Final GNU,
Wine and optimizedUBSan consume the independently produced reference, each
also executing a fresh three-callback rank probe. Actual Windows consumes the
fixtures and agrees on all39,757 records. Original CPU is not executed on
Windows; do not relabel the retained producer as three fresh full replays.

Three incremental builds provide27 x64 products and pass26 CTests each.
All26 preceding GNU products are raw-identical; all26 preceding PEs retain
every byte outside the eight timestamp/checksum bytes. Of26 preceding UBSan
products,25 are raw-identical; the rebuilt motion contract differs and passes
the full retained independent20,463-case/36,045-record motion control. No
raw or debug-only equality is claimed for that changed file. The initial
all-products raw assertion rejects and remains retained. GNU/Wine no-font
integration smoke passes; the published v1282 GUI/launcher and21 protected
DOS/config/save files remain unchanged. The actual-Windows private package
copies only the new attack contract, fixtures and streaming gzip control.
Root and native CI pass; the root also freshly attests the MAIN Ghidra database.
All304 completed smoke BMPs are losslessly gzip-compressed after receipt-hash
and decompressed SHA-256 checks, reclaiming229,971,858 bytes. Current builds,
CPU references and protected files remain available; see `bmp-compression.json`.
No whole-battle, original pixels, physical timing, FPS or DOS exact claim.

Receipts: `.analysis/port64/yuuka6-attacks-v1285/`, including `target-review`,
`root-ghidra-attestation`, `development-linux-full`, `accepted-{linux,windows,ubsan}`,
`producer-continuity`, `native-windows-review`, `missing-special-context`,
`zero-angle-range`, `build-receipt`, `product-continuity`,
`motion-ubsan-regression` and `integration-smoke`. Source manifest:
685c4c37b677e42dfe0ae5105ac4c1e28437730bf38c4c47b1ac7536fae772c3.
Replay with `python3 port64/verify_yuuka6_attacks.py --target TARGET --exe EXE
--output-dir NEW`; use `--runner wine` or `--reference-dir REFERENCE` as needed.

Next: mirror hit-test and final-boss core/phase dispatch, then foreground and
checkerboard integration. Extra, player death/Continue/Bomb, HUD, audio, Ending
and save I/O remain required. Semantic stays bounded to concrete port ambiguities.

## Yuuka6 mirror and core dispatch

v1286 ports MAIN13A9:7952..799E mirror hit-test,799F..79EB phase transition,
and79EE..7ECB FAR dispatcher. The latter owns executable code through7E77,
three sparse four-case tables and one18-entry phase table;79EC..79ED is
alignment. `port64/yuuka6_core.cpp` calls the existing twelve attacks,
animations, movement, shared explosion/defeat, lasers and custom entities.
Ordinary GUI still holds before Yuuka6 update; no new GUI is published.

Mirror state2 uses ordinary shots with384x768-subpixel half-radii, stores the
returned AL as a BYTE and tests HP<0. Main-body AB48 checks the whole shot WORD
for audio, then ABBE truncates before damage/HP. Thus WORD256 sounds on the
main body but subtracts zero HP, while the mirror does not sound. A retained
wrong BYTE-conditioned native variant rejects against the actual original
complete record; corrected native matches. Shot/Bomb and ordinary callbacks
are separate. Neither callback's injected damage proves real shot consumption.

The dispatcher has no shared clock increment. Hit wrappers, hidden branches
and explicit transition arms each advance their own clock; an attack can
reset it before a hit. Random movement destinations are sampled on every call,
including frames without teleport. Dual-mode selection rejects repeats with
the same RNG. Phase transitions clamp bullet clear to20, restore the preceding
end HP and reset attack/animation state. Entity tail bridges raw player-hit,
pending-score DWORD and shot scratch around the existing owner; shared defeat
returns before laser/custom/HUD tail. Drawing and death-flag aging remain
separate and must occur once per simulated frame in the future join.

One fresh independent original producer matches3,137fixtures/90,702records:
252 mirror,960 phase transitions,1,917 isolated core and eight retained
Easy/Normal/Hard/Lunatic win/timeout sequences. Each traverses phases0..17
and stops on entry to254; zero-damage sequences take19,654/19,639/19,664/19,800
frames, damage19 sequences2,204. Checkpoints include35 boss/animation/mirror
bytes,16 additional bytes, complete bullet/gather/laser/custom/spark pools,
templates, explosions48, shot scratch, homing, VM/background tokens, HP,
palette/score/hit/RNG globals and ordered requests. Actual callees execute;
shots and sound/circle/HUD/point/item consumers are adapters. `stage_id=0`
is the recorded owner-only fixture context; short default255 clocks stop at63,
before the stage-dependent Ending branch. No whole-route or Ending I/O claim.

Initial Original adapter inheritance rejected a `super()` type check; the
correct MRO includes both attack and boss adapters. This is a control-context
failure, distinct from the native sound bug. Final verifier adds a one-byte
comparator rejection. Exact AST checks preserve Original/fixture/fixtures/seed/
execute from producer fcf45d46, and all28 products per host remain raw-identical.
Final GNU/Wine/optimizedUBSan consume that independent reference and freshly
check five-rank regular/special/tune callbacks. Actual Windows agrees all90,702
records under the retained fcf producer identity. Final source manifest:
2d4df41ae2fbe6c094723e8c0491291de7acf9f0271999ee69abdc343e6e0b54.

Three incremental builds pass27CTests/28x64 products each.25 preceding GNU/
UBSan products are raw-identical;25 preceding PEs preserve all nonmetadata
bytes. Two changed animation/motion and attack contracts pass their independent
36,045 and39,757 retained records on all three hosts. Those receipts keep the
fcf manifest, linked by verifier-only continuity. GUI/launcher remainv1282;
21 protected Windows DOS/config/save files remain unchanged. No pixel, physical
hardware/pacing/FPS, original whole-route or DOS byte-exactness claim.
Root/native CI pass. Two verified duplicate native outputs are removed,
reclaiming185,082,796 bytes; the original reference and WSL actual-Windows
records remain. `duplicate-cleanup.json` records hashes and the Windows restore
path. `build-review-final.json` checks all28 product architectures and hashes.

Receipts:.analysis/port64/yuuka6-core-v1286, including target-review,
root-ghidra-attestation,development-linux-full-callbacks,accepted-{linux,windows,ubsan},
native-windows-review,verifier-continuity,sound-word-negative,
build-review-producer and motion/attacks-{linux,windows,ubsan}.
Replay `python3 port64/verify_yuuka6_core.py --target TARGET --exe EXE
--output-dir NEW`; add `--runner wine` or `--reference-dir REFERENCE` as needed.
Next: foreground/checkerboard and ordinary final-battle join, then remaining
Extra/death/Continue/Bomb/HUD/audio/Ending/save owners. Semantic stays bounded.
