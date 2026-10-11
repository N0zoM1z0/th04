# Recorded demo and idle OP integration

v1322, 2026-10-09. Real native OP now starts the four archived demos after idle,
plays their recorded controls with ordinary player-hit consumption, and returns
to fresh OP on physical input or expiration. All launches remain muted. This
is bounded semantic/native acceptance; DOS exactness, complete original gameplay
pixels, physical timing/audio and current Windows execution are unaccepted.

## Inputs and target contracts

MAIN is156258 bytes, SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
OP is42290 bytes, SHA-256
`8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f`.
Its stub-restored payload is69028 bytes, SHA-256
`13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`,
with804 relocations. Fresh MAIN/packed OP Ghidra attestation and both preflights
pass. The packed OP database is not a decoded-function Oracle. Provenance stays
candidate-local-attested. Original execution uses load segments1000 and2000;
addresses below identify relative executable segments, not linear addresses.

DEMO1..4.REC are8000-byte members of the MAIN archive in the pinned HDI,
SHA-256 `0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd`.
They are not loose FAT files. Each has4000 input bytes then4000 raw shift bytes.
Their digests, private extraction and archive/input hashes are retained in the
original replay receipt. Raw shift includes45 near the unused tail; keep the
byte through the callback and convert to a host boolean only at gameplay input.
No original assets or executables are stored in public source.

Observed OP0A74:0289..032D prepares resident lives/Bombs3 and numeric stage0,
then rotates demo number1..4: stages3/0/2/1, Reimu/Marisa/Reimu/Marisa and
shotsA/A/B/B. Resource stage ASCII is prepared before MAIN's live numeric stage.
The outgoing owner requests palette blackout1, resource release, cfg_save,
gaiji restore and MAIN execution. It does not request a song fade. Audio
continuation remains a request; configuration persistence still needs its owner.

Observed OP0A74:0D11..0D3A checks the previous signed idle SI against640
before the current input can reset it. A nonzero sample at that main-menu
boundary still starts the demo. Options accumulate idle without launching it;
their return sample belongs to the previous option frame. Signed16 wrap is
preserved. Resident seed increments only on continuing menu iterations, not
the trigger iteration, demo gameplay or its fades.

Observed MAIN0AAF:0213..03D4 forces local Hard/Turbo for demo and writes
playperf28 transiently; the common Hard branch at035E overwrites it with20.
Configured resident difficulty/Turbo stay unchanged. Highest-score loading
uses the incoming resident RNG seed. Only afterward does demo_load
0AAF:08FE..0948 install the archive banks, live demo stage, power128 and
DemoPlay callback, then reseed318. The ordinary runtime ring/drop/spark prefix
consumes353 draws from that seed. Moving318 before score loading changes
bad-file repair ciphertext; a source-only mutation is independently rejected.

Observed DemoPlay0AAF:0949..0997 aborts on any nonzero physical key_det before
reading either bank. Shift alone is overwritten by replay. Otherwise input is
zero-extended and raw shift copied. At frame3996 both writes happen before
expiration, but that gameplay frame does not update. Exit frees the replay,
requests palette blackout10, then GameExecl("op"). The original probe stops
at this execution request; it does not validate the entire DOS process teardown.

Original blackout waits one refresh before the first tone100, then speed
between tone100/94/.../4/0 writes. Speed1 uses18 refreshes; speed10 uses171,
not180. OP and MAIN blackout bodies execute separately in the Oracle.

## Native owners and independent checks

`demo.hpp/.cpp` own the two replay banks, signed idle gate and fade clock.
`application_state` separates preparation, process entry and post-score demo
initialization. `MainState` owns callback ordering, demo Hard/Turbo/performance,
physical score reading and fresh Stage2/3/4 setup. Higher starting stages use
their maintained setup helpers directly, without advancing synthetic prior
stages or adding another runtime initialization RNG prefix.

`FrontEnd` loads the requested demo stage from immutable decoded assets,
installs the physical HostStore and common GameOver/Continue callbacks, freezes
the MAIN view through exit fade and releases scene owners before fresh OP.
Ordinary, Extra and demo entry share the maintained MAIN installation helper.
Fresh OP restores menus and score-derived availability while preserving resident
configuration and the next demo number. Known host controls, including Q, can
abort; this does not establish an exhaustive PC-98 physical keyboard mapping.

`verify_demo.py` executes the attested original independently at both loads:
16576 replay controls,96 signed idle boundaries,5 rotation entries,2 fades
and96 initialization controls. Initialization covers four demo numbers, ranks
0/3, four resident seeds and valid/bad-checksum/missing physical scores.
It compares local rank/Turbo/power/performance, live stage/ASCII, RNG ring,
drop cursor, spark angles, complete initial TRAM and persisted score bytes.
GNU and optimized UBSan consume the completed independent reference, preserving
the earlier producer manifest rather than restamping it.

`verify_demo_join.py` drives actual options/idle/menu/demo/fresh OP/ordinary
MAIN. Each Linux host completes16 visits: eight full recorded demos to3996
and eight input aborts at120, all with ordinary hit consumption. Rank0 uses
Turbo on; rank3 explicitly disables it in the actual menu. Demo still forces
Turbo and subsequent ordinary MAIN restores that setting. Four abort controls
cover movement, fire, Esc and Q.35664 callback observations and64 BMPs per
host are retained; GNU/UBSan agree on all72 scene files. Original component
receipts independently guard replay bytes, startup RNG and terminal ordering.
The frontend capture comparison is between native hosts; it does not execute
complete original actors or establish original complete gameplay pixels.

Repaint consumes no RNG or gameplay frames. Options idle650 does not launch;
Cancel resets through the prior option branch. Each full run keeps valid scores
unchanged and returns to a new OP generation with MAIN resource owners released.
Both characters/shots are exercised. The initial original rotation probe stopped
before the branch target032E and failed closed; its corrected bound passes.
Initial compiler invocation errors and their logs also remain private.

All three builds produce44 AMD64 executables each, bound to352 source files;
43 CTests pass on GNU and optimized UBSan. Shared MAIN/menu extraction is checked
against existing Music Room, ranking and score-only MAINE routes. Detailed
current receipts, source/product profiles and failures live under native
`.analysis/port64/demo-v1322/`. Cross-build success does not accept current
Windows runtime. Git shared index metadata remains read-only; full uncommitted
source/evidence/root-document recovery is retained separately, with no commit
or push claimed.


The v1322 terminal-output cleanup shares1996 duplicates after complete byte/hash
readback and retires13 regenerable Python caches plus the early-seed mutant
binary. It reclaims939974656 allocated bytes (about896MiB), with6445 protected
file hashes unchanged. Current three build caches, all132 products, sources,
private inputs and replay/failure references remain.

## Replay and remaining work

Use fresh output directories; completed output hardlinks are immutable.

```sh
python3 port64/verify_demo.py --target ../../targets/th04/main.exe \
  --op-target ../../targets/th04/op.exe \
  --op-decoded-dir ../../port64/op-unlock-v1317/decoded-original \
  --hdi ../../runtime/images/zun.hdi \
  --exe .analysis/port64/linux-live-v1251/th04-port64-demo-contracts \
  --output-dir NEW
```

The frontend verifier also requires the independently completed original demo
directory, supplied CGROM BMP and a private physical score fixture or prior
frontend reference. Its launch always includes `--mute`.

Next are audio/config persistence, complete natural ordinary/Extra routes,
physical save/restart, current Windows runtime and dense Lunatic timing and
performance. Recorded demo completion does not waive those requirements or
change any DOS accepted extent.

## v1374 original/native MAIN state pairing

A headless ordinary MAIN adapter now runs all four original replays with their
zero-based ST00..ST03 STD/MAP assets and valid starting score/configuration files.
The DOS reference is the independently completed v1365 original capture, whose
full executable relocation image, caller log, input banks, disk contents and
emulator/profile identities are revalidated by the existing DOS reader.

The first correctly mapped native run completes all four demos. Its selected
fields agree for Demo 1/3/4; Demo 2 first differs at before-update frame 3533.
Original shots 7/15 have hit flags and divided velocities; native leaves them
alive for another tick. The Stage 1 midboss is three subpixels too high.

Observed MAIN MAIN_032_TEXT(13A9):065C..0669 subtracts 64 from midboss Y, loads
DGROUP(2134):4276 as a BYTE, zero-extends it, then adds it to Y at 53B6. This is
the fractional scroll accumulator. DGROUP:427A is the distinct WORD whole-pixel
scroll distance. The native component correctly consumed its supplied value,
but MAIN supplied the distance. `Background::fraction()` and the separate
`midboss::Context::scroll_fraction` now preserve this caller ownership. Other
midbosses and scroll-relative enemies still receive the distance.

`demo_state_trace.cpp` advances the actual ordinary gameplay owner and background
once per update, with normal hit consumption and actual replay callback checks.
It stops after the frame3996 terminal callback, without advancing actors. It
renders no host picture and dispatches no physical audio. The separate original
input sample used to label a row must agree with the callback actually consumed
by MAIN. Valid scores remain byte-identical and no writer commits.

`verify_demo_state.py` compares every one of 15,984 gameplay boundaries and four
terminal boundaries. Its 23 fields include consumed input/raw Shift, score bytes
and both score accumulators, player position/power/hit/invincibility/respawn,
resource/miss/Bomb counters, process LCG, all 256 ring bytes, ring cursor and
exact post-initialization LCG/ring draw counts. Native counters observe actual
central sampler calls; a wrapped cursor alone cannot satisfy the comparison.
DOS caller-family identities/operands remain retained diagnostic evidence.

GNU and optimized nonrecovering UBSan agree with the original on every compared
field in all four demos. A source-only wrong-distance adapter completes all
15,988 rows and is rejected first at Demo 2 frame3533, with ring calls697 versus
696 and score differences. Eight reader controls reject missing/duplicate rows,
wrong terminal decisions, changed ring bytes, score differences and extra draws
hidden by cursor wrap. They do not substitute for the independent DOS run.

The initial scratch adapter wrongly selected one-based ST01..ST04 files and
stopped early. Its source/log/full output remain a probe negative, not a product
failure. Correct zero-based assets reproduce the real frame3533 differential.
Initial default-option adapters are frozen separately; final adapters load the
exact ten original MIKO.CFG bytes through the maintained configuration owner.
Their receipts and producer identities are never restamped.

```sh
nice -n 15 taskset -c 0 env PYTHONDONTWRITEBYTECODE=1 \
  python3 port64/verify_demo_state.py \
  --dos-root /path/to/the/DOS-main-worktree \
  --original /path/to/dos-demo-v1365-original \
  --exe .analysis/port64/native-demo-v1374/build-gnu/th04-port64-demo-state-trace \
  --output-dir .analysis/port64/native-demo-v1374/FRESH-pair
```

Original scalar/caller/terminal rows and imported reader dependencies are frozen
with each current 498-file native source manifest. Compressed original rows
restore exactly. Complete actor/effect pools, original/native VRAM/palette and
scanout, physical timing, actual OP/fade/process handoffs, ordinary Boss/death
routes, broader native routes and Windows acceptance remain open. This does not
promote historical exactness or accept the older natural-route producer anew.

Final v1374 checks pass main 441/live Ghidra and native 321/target gates; native
private Ghidra/tool gates skip when unavailable. The frozen current reader
replays all 15,988 boundaries independently. GNU 70/68 CTests and focused UBSan 3
retain 498 sources/current manifest ff0b3bde…. Five pictures per host match as smoke
evidence. Complete 699 original midboss controls, 450 tile controls and setup pass
per host; original load2000/DS8000 adapters remain explicit. All handles terminal.

Lossless retention retires 26 streams and 1041 source-backed caches, reclaiming
166055936 allocated B (about 158.4 MiB) before journals. Full restoration/readback
and 8904 protected hashes pass; current source pins and DOS fingerprint agree.
Sources, failures, current build objects and old Windows/DOS products remain.
Use native `.analysis/port64/native-demo-v1374/restore_streams.py` with no options
to verify all recoveries, or `--restore` before unchanged old raw-path readers.

### v1375 complete native demo actor/effect pools

The new read-only actor observer runs immediately after native frame increment,
before periodic performance and score/extend. The original DGROUP stream seam
also follows actors, rendering, input reset and sound update but precedes modulo
counters and score. Observer-enabled stdout must remain byte-identical to a
separate complete ordinary selected-state run with actual CFG/scores/assets.
The independent DOS reader validates all original stream/ordinary/consumer/
target/process/load/CPU/page-map identities and complete gzip EOF/CRC.

The first eight-pool GNU pair accepts shots, enemies, sparks, bullets, custom
entities, circles and gather circles. Only pointnums differ, first at demo1/2/3/4
frames3379/3709/1952/3059, for618/288/2045/938 frames. Full captures retain this
failure. Original 13A9:64DE..6547 zeroes DGROUP988, consumes both position RNG
calls and calls yellow_add0300 with1280. Native Midboss actors already emit those
positions/rewards and update score/RNG, but MAIN's sink ignored the point event.
Adding the yellow consumer at that synchronous boundary repairs the full pool.
The item owner additionally retains unused/unknown bytes and sprite WORD16;
original items_add13A9:9FA8..A03D clears byte15/pullWORD18 and selects patterns44..50
from DGROUP2134:2322 while preserving byte1 and previous coordinates.

Final GNU/optimized UBSan compare all15984 updates on all nine complete pools
(24952 bytes/update) with zero differences. All inactive/padding fields remain;
enemy native IDs become actual STD-relative offsets, never masked pointers.
Complete15988 selected scalar/terminal fields and exact RNG counts also pass.
Removing only the Midboss consumer reproduces all four first pool differences;
selected scalar state and the other eight pools still pass. Eight public reader
controls reject inactive-tail/pointer/missing/duplicate/truncated/wrong-demo rows.
Frozen current native+DOS reader dependencies replay the same full acceptance.

GNU cold baseline plus bounded MAIN/item/trace rebuild yields70 programs/68 CTests.
Final UBSan core/trace is cold-built, one program; no full UBSan CTest claim.
Current producer has500 files, manifest656a05d9…. No DOS source/product or
historical exactness change. Other globals, original/native pictures/scanout,
ordinary Boss/death/process and Windows remain open. Older component and natural
route producers are retained with their own identities.

From the native worktree, with absolute DOS_ROOT pointing to the main worktree:

```sh
nice -n 15 taskset -c 0 env PYTHONDONTWRITEBYTECODE=1 \
  python3 port64/verify_demo_pools.py --dos-root "$DOS_ROOT" \
  --original "$DOS_ROOT/.analysis/runtime/candidates/dos-demo-v1365-original" \
  --original-dgroup "$DOS_ROOT/.analysis/runtime/candidates/dos-demo-v1367-original-dgroup-v2" \
  --original-consumer "$DOS_ROOT/.analysis/reconstruction/probes/demo-dgroup-v1367/consumer-source-v2/scripts/probes" \
  --exe .analysis/port64/native-pools-v1375/build-gnu/th04-port64-demo-state-trace \
  --output-dir FRESH
```

`ubsan-nine/` pins the sanitized program. `initial-pair/` preserves the rejected
8-pool/v1 reader and its producer; `mutant-pair/` preserves the new9-pool control.
`frozen-source/` retains500 native files plus actually imported DOS dependencies.
Every complete native pool stream is compressed and fully restored/read back
before its expanded copy is removed. Original streams and consumer sources stay
immutable. All runtime claims remain scenario-specific and locally attested.

Final CI passes main441/live Ghidra and native329/target checks (unavailable
private native gates skip). Retention reclaims2038489088 allocated B before
journals, preserving/restoring five full pool streams and ten text streams,
retiring1042 source-backed caches.8904 prior protected hashes,500 current source
pins,71 programs and DOS fingerprint pass. Current builds and failures stay;
verify recovery with native native-pools-v1375/verify_retention.py. All jobs terminal.

## Actual FrontEnd pictures and DEMO PLAY text (v1376)


The new `--demo-pictures DIR` runs ordinary idle OP entry, four bundled demos
and natural return to OP without a host window or audio. It copies the attested
starting score/CFG files and checks both unchanged after the route. The public
reader validates the full original ordinary trace, complete15984 video records,
CRC/EOF/load/CPU/ABI/consumer identities and pinned legal HDI before comparison.
All15988 selected scalar/count boundaries agree on the actual FrontEnd.

The initial GNU/optimized UBSan v3 captures retain28 full displays each. Their
complete selected state passes, but each of16 post-curtain samples lacks54 of72
DEMO PLAY text code/attribute bytes. This is a specific missing renderer owner;
score-tail timing cannot explain this constant middle-of-playfield label.
The original stage-enter owner, MAIN_01_TEXT0AAF:62B3..6348 (file125A3,150 bytes),
checks the72 timer, demo resident byte and writes nine gaiji at column18/row12
with attributeC3. DGROUP2134:1C20 retains the actual terminated label. Native
`main_text_plane` now applies these semantics on demos after enter completion,
including the frozen demo exit display. Ordinary-play callers keep their mode.
GNU/optimized UBSan v4 accept all40 complete72-byte spans, including frames72/73/74 in each
demo. All15988 scalar/count boundaries still pass. Eight public controls test
complete sample order, last bytes, TRAM banks, bit order, page selection, address
wrap/partitions and unsupported GDC modes. Earlier initial adapter failure
omitted `enable_registration`; no MAIN actor ran, so it is a probe failure.

The full640×400 graphics comparison remains diagnostic: original samples at
frame-counter write before score/background tail, native after complete
FrontEnd update. Retain full256000 indexed bytes,768000 text-composited native
RGB bytes,8000 canonical TRAM bytes, and complete279809-byte original snapshots.
Do not crop or mask invisible graphics to manufacture equality. Original MPN
uploader MAIN_01_TEXT0AAF:0E0C..0E80 (fileD0FC,117 bytes) populates100 image slots
in both physical pages at left576..639. Original reverse blank TRAM can cover
this cache. Native first-frame black curtain likewise follows reverse blank
TRAM; the earlier graphics-only original PNG omitted this text layer. All12
initial full canonical TRAM samples agree. Later score/HUD differences need aligned
sampling; physical blink/FIFO/scanout and original composited RGB stay open.

Programmed GDC decoding uses the pinned emulator's partition SAD/LEN, pitch40,
row-height1 and analog four-plane display-page model. It rejects unsupported
IM/WD/mode/extent. Its28 overlapping original hashes independently match the
earlier NumPy decoder; this is model cross-checking, not physical scanout proof.
Fresh Ghidra/target/header/entry/relocation/load and raw owner witnesses are
retained in root `.analysis/reconstruction/probes/native-pictures-v1376/`.
Use its `attest_picture_owners.py --target TARGET --database ATTESTATION
--output FRESH.json` to replay both owners. Earlier scratch address-base mistakes
are retained and rejected; complete corrected owner digests agree with the
existing accepted extents. Target provenance remains candidate-local-attested.

From the native worktree, using absolute DOS_ROOT:

```sh
nice -n15 taskset -c 0 env PYTHONDONTWRITEBYTECODE=1 \
  python3 port64/verify_demo_pictures.py --dos-root "$DOS_ROOT" \
  --original "$DOS_ROOT/.analysis/runtime/candidates/dos-demo-v1365-original" \
  --original-video "$DOS_ROOT/.analysis/runtime/candidates/dos-demo-v1369-original-video-v2" \
  --original-consumer "$DOS_ROOT/.analysis/reconstruction/probes/demo-video-v1369/producer-source-v2/scripts/probes" \
  --hdi "$DOS_ROOT/.analysis/runtime/images/zun.hdi" \
  --exe .analysis/port64/native-pictures-v1376/build-gnu-v4/th04-port64 \
  --output-dir FRESH
```

Use build-ubsan-v4 for the instrumented FrontEnd. v3 cold main/view (and UBSan
audio) TUs and v4 cold view TUs reuse the unchanged v1375 core/ymfm libraries;
this is explicitly a bounded frontend build, not whole-current cold/CTest or
Windows acceptance. All producer sources and actual link dependencies are
pinned separately. Retained v1375 nine-pool acceptance keeps its own producer;
no DOS input, original bytes, physical Windows product or historical exactness
state changes in this batch. Next align the full presentation boundary before
claiming pictures; do not treat every raw diagnostic difference as a source bug.

Final502-source producer manifest is6a997fe129eda10206e39323891f13da65187adc2aed5e91af4cf9bf45141db0.
GNU/optimized UBSan final capture bytes agree completely; frozen reader imports
reproduce2×15988 selected boundaries and2×40 label spans while consuming all
15984 original records. Main441/live Ghidra and native337/target CI pass; absent
native private gates skip. No Windows or DOS product launch/build occurs here.

All jobs terminal. Native native-pictures-v1376 retention reclaims291966976
allocated B before journals, fully preserving671 archived raw display/state/
intermediate files and retiring1043 source-backed caches. Full restored hashes,
modes/nsmtimes and gzip CRC/footer/EOF pass;8904 older protected hashes,502 source
pins and4 new/71 old programs remain equal. Use verify_retention.py for temporary
restored readback, or --restore before frozen_readback.py/verify_initial_label.py
and old object reuse. The public reader uses fresh outputs and retained programs.

## Aligned complete text planes (v1377)

`capture_demo_present.py` projects only the donor format/boundary constants
and selects a distinct GDB scalar-header observer. TH04VP3 cannot accept old
TH04VD2 streams. Original 0AAF:00B7 / :0975 samples follow the previous complete
MAIN iteration, aligning score/background-tail work with actual FrontEnd.
The pinned ELF header site is CoreNormal+0x1DE; its19-byte witness and raw
IP/CS/DS offsets32/8/24 are checked against actual instructions and symbols.
The observer preserves every ordinary scalar/caller record.

`verify_demo_present.py` consumes all15984 original records and compares retained
GNU/optimized UBSan actual FrontEnd traces (15988 selected state/count boundaries
each). All40 selected full canonical TRAM planes (8000 bytes each), and all40
complete72-byte DEMO PLAY spans, agree per host. Canonical TRAM means the4000
code bytes plus4000 attribute bytes, rather than the entire16384-byte raw area.
Graphics indices compare every256000 pixels diagnostically. No crop or byte
mask accepts a picture; original composited RGB/font/blink/scanout stays open.

Compiled products remain502-source v1376/6a997fe1; new consumer sources are
separately pinned. Read complete captured native bytes directly from verified
v1376 retention archives; no native process, C++ rebuild or physical Windows
launch is needed for this new reader. Current receipts are in native
`.analysis/port64/native-presentation-v1377/`.

The paired original/reconstructed DOS TH04VP3 replay also passes all38 compared
regions at4×3996 records with exact ordinary parent controls. Full raw GDC
clock/FIFO internals stay diagnostic; neither byte exactness nor scanout is
promoted. Consumer505/8b0f702a is frozen separately from producer502/6a997fe1.
Eight public controls and a retained real TH04VD2 stream reject wrong protocol,
seam, mixed ELF bias, site bytes, projection-marker drift, archive last-byte
digests and duplicate members.

Frozen consumer replay produces a byte-identical complete receipt, including
each full text/graphics diagnostic row and all15988 scalar/count boundaries.
Graphics location reducer retains every256000-pixel comparison:30/40 samples
agree within x32..415/y16..383, while ten differ there. The nonzero samples are
Demo1 frames1/1952/3379/3996, Demo2 1952/3379/3709/3996 and Demo3 3379/3709.
Every full graphics frame still differs. These diagnostic rectangles/maps
do not accept cropped pictures. Check displayed/pending pages and physical
scanout timing before treating any remaining indexed difference as a renderer
source defect. Native graphics-diagnostic.json retains full hashes, counts,
80×80 location maps and colour histograms; original/raw native pixels stay pinned.

Final main441/live Ghidra and native345/target CI pass; unavailable native private
gates skip. Retirement reclaims153010176 allocated B (145.9 MiB) before journals:
128 complete HDI/raw snapshot copies and1044 source-backed caches. All9692
protected hashes,505 source pins, unchanged DOS fingerprint and complete archive
restore/SHA/mode/nsmtime/gzip EOF pass. Recovery is root
.analysis/reconstruction/probes/native-presentation-v1377/verify_retention.py;
add --restore before reading retired HDIs/snapshot paths. Complete VP3 streams,
original references, programs, source snapshots and failures stay pinned.

## Native Midboss shake consumer (v1378)

The display-page hypothesis does not explain the retained forty samples:
current and pending selectors agree, pending wait is zero, and GDC first line
agrees with native scroll. Choosing the other page increases most differences.
Both original physical MPN cache banks agree with all128 bytes of every asset
image at every sample. Demo2 uses Marisa ST10.MPN, not Reimu ST00.MPN; the first
wrong-asset cache experiment is retained separately as a rejected hypothesis.

Target-observed MAIN_01_TEXT0AAF:2246..2315 (fileE536..E605,208B) consumes
DGROUP2134:427E/4280/4282 signedWORD x/y/timer and :185C signedBYTE redraw.
Nonzero timer writes x=-2 for mod2 zero, otherwise+2; y=-2 for unsignedmod4<=1,
otherwise+2, then decrements the WORD. Four far EGC calls (MAIN_00_TEXT0000:
0A22/0B24/0C34/091C) pass the complete32,0,415,399 rectangle and shift count.
Horizontal movement precedes vertical. Movement sets redraw2; a nonzero redraw
decrements, executes actual tiles_invalidate_all0AAF:2052, and clears x/y.
Counter wrap remains16/8-bit. Stage session clears x/y but preserves timer and
redraw; a fresh MAIN instance starts zero. These are target observations,
not a new exactness promotion or a physical EGC pixel acceptance.

Native Midboss producers already emitted twelve-frame shake events; MAIN only
recorded them. The new playfield_shake owner consumes the timer, updates at the
original modulo phase, and retains the applied shifts separately from cleared
post-state globals. Final graphics movement precedes Bomb page retention and
text overlay. It moves physical x32..415/y0..399 through the400-line scroll
ring, X thenY, retaining vacated strips. That physical edge model is inferred
and invariant-tested; the CPU Oracle records EGC requests rather than executing
hardware blits. Ordinary Boss direct offsets and Bomb interaction remain open.

Original CPU execution compares3262 complete globals/EGC-request cases with
the native checker, including signedWORD timer and signedBYTE redraw wrapping;
an injected adapter rejection propagates. Thirty-six labelled full256000-pixel
shift/scroll cases check every exterior, vacated-strip and wrapped-row pixel.
Actual headless FrontEnd idleOP→four demos→OP captures retain every shake state:
all15984 updates agree on the complete7-byte original globals and actualCPU-
derived applied x/y/invalidation. The reader uses original DGROUP modulo bytes;
only observed12-frame Midboss requests are inferred from timer transitions,
and unexpected transitions reject. Existing15988 selected scalar/count
boundaries and all nine complete pools at every update remain compared.

Demo1 frame3379 diagnostic playfield differences fall55357→430. All430 remaining
pixels lie at y16/17, consistent with the native background clipping before
vertical motion; that ownership is not repaired or accepted here. All forty
full8000-byte canonical TRAM samples remain equal. Every complete graphics
frame is retained/compared diagnostically; fullRGB/font/blink/scanout and the
initial carpet, laser and circle pixel differences remain open. No crop/mask
accepts pictures. Private recipes and immutable producer sources live under
root .analysis/reconstruction/probes/native-pages-v1378/ and native
.analysis/port64/native-pages-v1378/. Public owner Oracle:

```sh
nice -n 15 taskset -c 0 python3 port64/verify_playfield_shake.py \
  --target "$DOS_ROOT/.analysis/targets/th04/main.exe" \
  --exe .analysis/port64/native-pages-v1378/build-gnu-v2/th04-port64-shake-checks \
  --output-dir FRESH
```

The full GNU cold build has71 programs and69 passing CTests. Final producer
pins509 inputs, manifest9346e9513312ac094a289e3da52ee2706f7a6d854941b81dde8a03ac168d97dd.
The first standalone Oracle Path-versus-bytes error, whole-build missing
namespace alias and complete-reader wrongROOT import failure remain retained.
Do not reuse the old whole DGROUP consumer as an import prefix: import actual
DOS-root scripts/probes first and pass old sources as attestation only.

Optimized UBSan cold core/game/trace/shake yields3 programs with no fullUBSan
CTest claim. Both hosts pass complete shake/scalar/nine-pool controls and all40
canonical textplanes; their125 entire capture files agree byte for byte.
Removing only MAIN's timer event consumer from frozen producer source rejects
13 updates/demo, first3379/3710/1953/3059, while selected scalar/counts stayequal.
The mutant program/source/link/capture/receipt remain pinned. Six trace controls
reject missing/duplicate rows, lastframe/lasttimer/appliedshift/invalidation drift.
Frozen native509 and actual importedDOS/producer-attestation sources reproduce
both complete shake receipts, with only their separatelypinned ownsourceSHA
different. Frozen/imported consumer identities do not restamp older binaries.

## v1378 terminal validation and recovery

All v1378 jobs are terminal. Main441/liveGhidra and native345/target CI pass;
unavailable private native gates skip. Initial unregistered Oracle label and
cleanup log-lifetime failures stay retained: archive restoration passed before
retirement; final gate rejected its own writing log, then a distinctv2 journal
pinned that log after terminal. No archive/program/source bytes were repaired.
Lossless retirement reclaims324722688 allocated B (309.7MiB) before journal
cost:1390 full raw/sample/build-intermediate files and1044 source-backed caches.
Full restored SHA/size/mode/nsmtime/gzip EOF,15620 protected hashes,509 source
pins and unchanged DOS fingerprint pass. All71GNU/3UBSan/newmutant programs,
complete frozen sources, original references and failure receipts stay live.
Recovery from DOS root: python3 .analysis/reconstruction/probes/native-pages-v1378/verify_retention.py --restore before old raw-capture/graphics/frozen-reader paths.
Use no options for full temporary readback. v1377 restore proof retained its
then-current505 scope; its live-source check must not be restamped to509.

## Complete ordinary background ring before shake (v1379)

Target MAIN_01_TEXT0AAF:20C8..2109 (fileE3B8..E3F9,66B) starts destination
WORD7804 (physicalrow384/x32), ringWORD5340 (4D40+24*64), and iterates24 tiles
of16 rows before walking backward through25 ring rows. The unchanged explicit
EGC setup/off leaves are hardware adapters. Actual original instruction
execution produces9600 distinct WORD copy requests covering x32..415 and
all400 physical rows. A four-plane latch shadow uses each target-selected
source/destination, rather than substituting a native coordinate formula.

The original Demo1frame3379 DGROUP stream supplies the full25x32 tile ring;
ST03.MPN supplies all128bytes/image. Recorded movement(-2,+2) and displayline34
are preserved. The independently replayed fulltile page agrees on all768
pixels of y16/17; the retained oldnative page differs at430 of those pixels.
This is an adapted EGC component and actual-state edge observation, not
physical hardware, whole scene, RGB or scanout acceptance. Fresh preflight and
live MAIN database attestation pass; provenance stays candidate-local-attested.

Native view previously painted stage tiles only at y16..383. Ordinary tiles
now paint the full400-row ring before movement. Boss backdrop transition masks
retain their23-visible-row bounds, avoiding unsigned mask-row underflow. Only
view.cpp changes among509 producer inputs. GNU and optimized UBSan cold-compile
that translation unit and relink with SHA-attested unchanged v1378 main/audio/
core/ymfm inputs. This is a bounded cold frontend build, not a new whole-current
cold build or69-CTest claim. Producer manifest:
8e77830c1ca94c052e718b9f96d1ac1d6712af8abdbd6f3ced1c1167e1d21c09.

Actual muted SDL-dummy idleOP→four demos→OP compares complete selected scalar/
shake traces and all40 full canonical text planes. Full graphics/RGB samples
remain retained diagnostically. Demo1frame3379's game-area differences now
fall430→0. Nine other nonzero game-area samples are unchanged; no new game-area
difference appears. Do not crop/mask this result into a whole-picture claim.
Initialcarpet, Marisa laser and circle pixel differences, fullgraphics/RGB/
font/blink/scanout, Boss offsets/Bomb interaction and broader paired routes
remain open. Prior v1378 complete-pool and69CTest receipts retain their own
unchanged core/program producers; they are not restamped with the new view hash.

Recipes: root .analysis/reconstruction/probes/native-ring-v1379/
prove_full_ring.py, build_frontends.py, run_validations.py; evidence native
.analysis/port64/native-ring-v1379/. Each uses fresh outputs, CPU0/nice15;
all launches stay muted/dummySDL. No original/DOS source or target bytes change.

## v1379 terminal validation and recovery

All v1379 jobs are terminal. Main441/live Ghidra and native345/target CI pass;
private unavailable native gates skip. Frozen full-reader replay reproduces
both complete shake receipts, apart from its separately pinned source hash.
Lossless retirement reclaims153083904 allocated B (146.0MiB) before journalcost:
342 complete sample/capture/build files and1044 source-backed caches. All16713
protected hashes,509 source pins, full restoration/SHA/size/mode/nsmtime/gzip
EOF and unchanged DOS fingerprint pass before and after deletion. The active
cleanup producer log is explicitly excluded until terminal; old proofs remain
immutable. Two new FrontEnd programs and all older programs/sources stay live.
From DOS root, use python3 .analysis/reconstruction/probes/native-ring-v1379/verify_retention.py --restore before reading retired captures, fulltile pixels or relink objects;
without --restore it performs temporary complete readback. Old v1378 proof
retains its then-current509/9346e951 scope and cannot attest live8e77830c source.

## Marisa laser presentation color phase (v1380)

Observed MAIN_01_TEXT 0AAF:3704..37C7 (file F9F4..FAB7, 196 bytes)
loads DGROUP 2134:538C at 3786 and adds 8 for the GRCG color. It renders
before the complete update tail increments the frame modulo. The actual raw
laser blitter is 0AAF:1378..13DA (file D668..D6CA, 99 executable bytes);
the following alignment byte is outside this executable extent.

Runtime-observed execution of this caller and its actual STOSB/STOSW blitter
uses four complete, attested original Demo 2 DGROUP states. Recorded display
scroll selects the visible row; GRCG color/masks use an explicit adapter.
Every former game-area difference is palette index 8 versus 9 with the same
beam geometry: frames 1952/3379/3709/3996 differ at 4216/2967/2186/2015
pixels. All 11,384 pixels equal the original CPU beam color; the old native
pixel equals that color XOR 1. Full 256,000-pixel beam outputs are retained.
This accepts an adapted component observation, with physical scanout open.

Native State::frames() already includes the update tail. Using
8 + ((frames - 1) & 1) repairs this color phase. GNU and optimized UBSan
actual muted SDL-dummy idle OP→four demos→OP captures now have zero game-area
differences in all ten sampled Demo 2 frames. The five other nonzero samples
remain unchanged: Demo 1 frames 1/1952/3996 and Demo 3 frames 3379/3709.
All 40 full canonical text planes, 15,988 selected scalar/count boundaries
and 15,984 complete shake states/requests pass. All 125 complete files agree
between variants; complete parent state/shake traces remain byte-identical.
Full graphics/RGB samples remain diagnostic, with no crop or mask acceptance.
Initial background and circle effects, broader routes and scanout remain open.

Only view.cpp differs from v1379 among 509 producer inputs. Manifest:
f5791751c2473da2efaa4bf86e7265ce5c99f6ab23c4f1dc166248cd2b555cbf.
Both variants cold-compile that TU and relink attested unchanged dependencies;
this is a bounded build. Previous whole cold/69-CTest and complete-pool receipts
keep their original producers. The first parent receipt-path failure is retained
with its source and log. Frozen imported DOS/native readers independently
reproduce both complete shake receipts except their pinned source hashes.
No DOS product inputs, target bytes or historical exact acceptance change.
Fresh preflight and live MAIN database attestation pass; target provenance
remains candidate-local-attested.

Recipes: DOS-root .analysis/reconstruction/probes/native-shot-render-v1380/
attest_laser.py, build_frontends.py, run_validations.py, freeze_readers.py.
Receipts: native .analysis/port64/native-shot-render-v1380/. All heavy jobs use
CPU0/nice15 serial execution; all launches remain muted and headless.

## v1380 terminal validation and recovery

All v1380 jobs are terminal. Main 441/live Ghidra and native 345/target CI pass;
unavailable private native gates skip. Full parent/current sample hashes show
36 complete index/RGB samples unchanged. All 11,384 pixel changes in the other
four complete index pictures equal the actual original CPU beam and original
pixels on both variants. This further bounds the repair; whole pictures stay open.

Lossless retirement reclaims 156,069,888 allocated bytes (148.8 MiB) before
journal cost: 354 complete sample/capture/build files and 1,044 source-backed
caches. Full restoration/SHA/size/mode/nsmtime/gzip EOF, 17,815 protected
hashes, 509 source pins and unchanged DOS fingerprint pass before and after
deletion. The cleanup log is excluded while writing. Two new FrontEnd programs,
all old programs, frozen sources, original references and failures stay live.
From DOS root, restore retired inputs before CPU/graphics/reader/relink replay:

```sh
python3 .analysis/reconstruction/probes/native-shot-render-v1380/verify_retention.py --restore
```

Without --restore, it performs temporary complete readback. Old v1379 proof
retains its then-current 8e77830c scope and cannot attest live f5791751 sources.

## Whole-pool pellet color passes (v1381)

Observed MAIN_01_TEXT 0AAF:81F5..82FF (file 144E5..145EF, 267 bytes)
calls the complete white top pass before the complete purple bottom pass.
The actual leaves are 1EAC..1F3C (file E19C..E22C, 145 bytes) and
1F3E..1FA7 (file E22E..E297, 106 bytes). The intervening EVEN byte belongs
to the physical ASM owner and is outside either executable body.

Target instructions 1F2E/1F30 overwrite DGROUP 2134:86D2 coordinate pairs
with bottom VRAM and shifted-sprite offsets. The retained post-render DGROUP
list cannot be passed directly to the top renderer as left/top coordinates.
A bounded inverse recovers byte-column plus shift from sprite base 181C and
physical top row from bottom row minus three modulo 400. Executing the actual
top body must reconstruct every original post-top pair. Complete roundtrips
pass for all 60/98 pellets at Demo 1 frames 1952/3996.

Runtime-observed GRCG write-mask adaptation executes the same raw target leaves
with whole-pool passes and with per-pellet interleaving. The latter lets a later
white top overwrite an earlier purple bottom. All 8/32 changed pixels equal
original color 9 and former native color 15. Full 256,000-pixel results from
both target-body execution orders are retained. This does not accept physical
GRCG timing or complete original pictures.

Native view now finishes the 16px bullet sprites, draws all procedural white
pellet pixels, then all procedural purple pixels. GNU and optimized UBSan
actual muted SDL-dummy idle OP→four demos→OP close Demo 1 frame3996 32→0 and
frame1952 34→26. All 40 changes in the two complete index pictures agree with
the original CPU and original pixels; the other 38 full index/RGB hashes are
unchanged. All 40 full canonical text planes, 15,988 selected scalar/count
boundaries and 15,984 complete shake states/requests pass. All 125 capture files
agree between variants; complete parent state/shake trace bytes remain equal.

An independent negative probe executes the ordinary circle caller 0AAF:1C28
at all five formerly nonzero natural samples. Its pool has no alive records
and all calls issue zero raw GRCG circle requests. This excludes that ordinary
pool here; it does not exercise or accept the raw circle leaf. Remaining game-area
samples are Demo 1 frames 1/1952 (124439/26 pixels) and Demo 3 frames 3379/3709
(60/17). Their white-pixel and initial-background causes remain unproved;
full graphics/RGB/scanout and broader routes remain open.

Only view.cpp changes among 509 producer inputs; manifest:
fb26d5099584000e576c66c9dc5a7822ec64745c2b05058de6404e15b3481440.
Both variants cold-compile that TU and relink SHA-attested unchanged dependencies.
This is a bounded build; earlier whole cold/69-CTest/full-pool receipts retain
their own producers. Frozen imported DOS/native readers reproduce both complete
shake receipts except their separately pinned source hashes. Fresh preflight
and live MAIN database attestation pass; provenance remains candidate-local-attested.
No DOS inputs, target bytes or historical exact acceptance change.

Recipes: DOS-root .analysis/reconstruction/probes/native-circle-v1381/
inspect_circles.py, prove_pellet_passes.py, build_frontends.py, run_validations.py,
verify_pixel_change.py, freeze_readers.py. Receipts: native
.analysis/port64/native-circle-v1381/. Jobs run CPU0/nice15 serial; launches stay
muted/headless. The batch path preserves its initial circle investigation.

## v1381 terminal validation and recovery

All v1381 jobs are terminal. Main 441/live Ghidra and native 345/target CI pass;
unavailable private native gates skip. Full parent/current sample hashes show
38 complete index/RGB samples unchanged. All 40 pixel changes in the other
two complete index pictures equal the actual original CPU pellet passes and original
pixels on both variants. This further bounds the repair; whole pictures stay open.

Lossless retirement reclaims 156,139,520 allocated bytes (148.9 MiB) before
journal cost: 354 complete sample/capture/build files and 1,044 source-backed
caches. Full restoration/SHA/size/mode/nsmtime/gzip EOF, 18,924 protected
hashes, 509 source pins and unchanged DOS fingerprint pass before and after
deletion. The cleanup log is excluded while writing. Two new FrontEnd programs,
all old programs, frozen sources, original references and failures stay live.
From DOS root, restore retired inputs before CPU/graphics/reader/relink replay:

```sh
python3 .analysis/reconstruction/probes/native-circle-v1381/verify_retention.py --restore
```

Without --restore, it performs temporary complete readback. Old v1380 proof
retains its then-current f5791751 scope and cannot attest live fb26d509 sources.

## Item-spawn splash state and foreground dots (v1382)

Observed MAIN_03 13A9:0486..049F clears 80 bytes at DGROUP 2134:41F6
and the separate cursor at 4250. The ten bytes at 4246..424F are separate
storage. 04A0..04E5 admits the selected eight-slot ring entry and advances
its cursor even when busy; admitted state has radius/previous32 and time16.
The physical suffix includes the two following alignment bytes. 04E8..0521
ages nonfree records by32, retaining previous radius and removing at512;
flag2 becomes free on the next update. The time byte remains unchanged.
Original items_add creates a splash only after admitting an ordinary item.
The separate miss-drop producer does not use that path. items_update ages
splashes after the complete item-slot loop.

Actual original render 0AAF:168C..170E (file D97C..D9FE,131 bytes) uses
64 four-angle increments, actual vector2_at, signed-word coordinate wrap,
subpixel playfield rejection and the actual scroll helper. Its raw dot leaf
0AAF:1842..185D (file DB32..DB4D,28 bytes) issues one byte mask per point.
The GRCG color/mask adapter retains full256000-pixel output and ordered dots.
Native typed Splashes now joins item Pool allocation/update/reset and draws
white dots before item sprites, retaining all record fields and ring admission.

311 original CPU state/ordered-dot controls per GNU/optimized UBSan compare
full81-byte state, wrapped/negative radius/center/flag cases and three captured
natural states; ten reserved sentinel bytes remain unchanged. Actual muted
SDL-dummy idle OP→four demos→OP agrees on all15984 full81-byte records,
including inactive fields and cursor. Active frames are1146/688/1192/904;
all eight cursors occur per demo. Missing/duplicate lastrow, lastcursor,
lastinactive-radius and firstframe controls all reject. Frozen imported DOS/
compiled-native readers reproduce splash and shake receipts on both variants
except separately pinned ownsourceSHA.

All103 changes across three full256000-index actual samples equal original
white dots: Demo1frame1952 26→0, Demo3frames3379/3709 60/17→0. The other37
entire index/RGB sample hashes remain unchanged. All40 full canonical text
planes,15988 selected scalar/count boundaries and15984 full shake states/
requests pass. All126 entire capture files match between hosts; complete parent
state/shake trace bytes remain identical. Fresh current-producer nine full
actor/effect pools pass15984x24952B, retaining inactive/spare bytes and translating
only enemy script IDs to original STD-relative offsets. The missing splash
owner was outside those nine pools; scalar equality could not detect it.

The first direct CPU-mask decode with recorded GDC line rejected. Actual helper
DGROUP4278 reads drawing scroll300/40/275, while programmed display lines are
301/41/276 at these seams. Drawing-relative dot geometry explains the pixels;
physical GDC command/scanout mapping remains unaccepted. The failed assertion,
subsequent owner-size decode failure and frozen-source ROOT import failure
remain retained with their source/logs. The successful replay uses a freshv3
owner and distinctv2 component directories, preserving all failed artifacts.
No copied bitmap, original DS painting or picture crop/mask enters the product.

The producer pins509 inputs, manifest
add39f3c33de91719b93c0510350b09223ec973612ebaf45b317b1dec400b44c.
Five inputs change: item_pool.cpp/.hpp,view.cpp,demo_picture_frontend_checks.inl
and verify_demo_pictures.py. The Pool header/layout change invalidates earlier
native core binaries. Fresh GNU cold build has71 programs and69 passing CTests;
optimized UBSan cold core/game/trace/shake yields3 programs with no fullUBSan
CTest claim. All new programs and full source snapshots retain this producer.
Older products keep their own source identities. DOS inputs/fingerprint,
original targets and historical exact acceptance remain unchanged; provenance
stays candidate-local-attested. Fresh preflight/live MAIN attestation pass.

39 of40 sampled game areas now have zero differences. Demo1frame1 remains
124439 pixels; initial background and all complete picture margins/cache/RGB/
physical scanout, broader Boss/death/process/Windows pairing remain open.
Recipes: DOS-root .analysis/reconstruction/probes/native-white-v1382/
inspect_splashes-v3.py,build_native.py,verify_splashes-v2.py,validate_remaining.py,
compare_splashes.py,verify_pixel_change.py,reader_controls.py,freeze_readers.py.
Receipts: native .analysis/port64/native-white-v1382/. Jobs stay CPU0/nice15,
serial, muted/headless. Full pools are already gzip-restoration verified.

## v1382 terminal validation and recovery

All jobs are terminal. Main441/live Ghidra and native345/target CI pass;
unavailable private native gates skip. GNU cold71 programs/69CTest and UBSan
cold3 targets remain pinned; full81-byte splash/nine-pool/scalar/shake/text,
five malformed-trace rejection and frozen-reader controls pass. No Windows,
physical scanout, full pictures or historical exact promotion is accepted.

Lossless retirement reclaims 193,658,880 allocated bytes (184.7 MiB) before
journal cost: 975 complete sample/capture/build files and 1,044 source-backed
caches. Complete restoration/SHA/size/mode/nsmtime/gzip EOF, 22,622 protected
hashes, 509 source pins and unchanged DOS fingerprint pass before and after
deletion. Two complete native-pool streams already reclaimed 774,946,816
allocated bytes after full gzip restore/SHA/length/EOF verification. Combined
net allocated recovery is 968,605,696 bytes (923.7 MiB) before journal
cost. All71 GNU/3 UBSan programs, both component probes, old programs, frozen
sources, original references, full pool archives and failed attempts stay live.
The cleanup log is excluded while writing; previous proofs remain immutable.

From DOS root, restore retired samples/build inputs before CPU/graphics/reader
replay with python3 .analysis/reconstruction/probes/native-white-v1382/verify_retention.py --restore.
Without --restore it performs temporary complete readback. Old v1381 proof
retains its fb26d509 source scope and cannot attest current add39f3c inputs.
Native full pool gzip archives are already complete and require no new capture.

## Stage4 background publication and tail copies (v1383)

Target-observed MAIN_01_TEXT 0AAF:0098..0212 (file C388..C502) calls
non-Bomb background through DGROUP 2134:4268 at 00DE, before stage_render
through 432C at 0113. Actual original initial fill 0AAF:0FB2..0FFC,
full-tile loop 20C8..2109 and carpet callback 3FF4..40FD explain the first
Demo 1 discrepancy. Its fixed inactive page still contains the initial MAP;
its fixed active page adds actors to that background. The callback changes the
ring afterward. All 124,439 old game-area differences are pre-callback versus
post-callback background pixels. GDC page selection is never chosen for fit.

Runtime-observed 0AAF:0FFE..10B3 (file D2EE..D3A3, 182 B) copies the tail's
combined current/previous integer row advances using the post-callback and
refilled ring. Forty-eight actual CPU controls, heights 1..16, retain ordered
source/destination WORD requests across tile-row and 400-row wrap. EGC latch
and hardware setup are explicit adapters; larger heights and physical scanout
remain unaccepted. The snapshot-only e516f7f3 intermediate closes the 40 game
area samples but adds 2,100 incorrect edge pixels. It is retained and not
promoted. This counterexample requires preserving both publication surfaces.

Native view now retains the ordinary draw's carpet ring, then substitutes the
post-tail ring only for copied physical rows. No first-frame special case or
actor/RNG/score workaround is introduced. One input changes among 509:
port64/view.cpp; final manifest
50ca49c65df70cc75b5807df0a3e218dcdaba5a847e780092ed1618bd2fc6496.
GNU and optimized UBSan cold-compile that TU and relink with SHA-attested
unchanged v1382 core/main/audio/ymfm objects. The earlier whole cold build,
69 CTests and full nine-pool comparison keep their v1382 producer identities;
this is not a new whole-current cold/CTest/full-pool claim.

Actual muted SDL-dummy idle OP→four demos→OP agrees at all 15,988 selected
scalar/count boundaries, 15,984 full shake states/requests and 81-byte splash
records, and 40 complete 8,000-byte canonical TRAM samples. All 126 entire
capture files match between GNU and UBSan; parent scalar/shake/splash traces
remain byte-identical. All 40 standard sampled game areas now have zero
differences. First-frame full-picture differences fall 224,211→94,316 and
second-frame 97,672→94,316: all 133,251 changed pixels equal the fixed original
page, including 124,439 first-frame game-area pixels and 3,356 second-frame
edge pixels. Other 38 entire index/RGB samples remain unchanged. Full graphics,
margins/cache/RGB, physical GDC/scanout and broader routes remain open.

Three separate instrumented GNU producers retain immutable before/intermediate/
final sources and programs, changing only ten capture frame numbers. Complete
original Demo 1 VP3 stream/source/CRC/EOF checks cover all 3,996 records. The
additional lighting samples 1663/1664/1665/1666/1667/1668/1696/1697/1728/1729
all agree on game area and complete text. Frame 1666 repairs another 7,498
pixels. Their complete scalar/shake/splash traces equal final ordinary GNU.
These ten samples have separate producer identities and do not turn 40 ordinary
samples into full native video acceptance.

First incorrect callback-address assertion, omitted archived-reference path,
39-unchanged-picture assumption, and missing retired VP3 images are retained.
Separate corrected readers restore only required immutable inputs. Old producers
and recipes are not restamped. A temporarily stopped verified reader resumes
only after both compiler jobs are terminal, preserving its original live handle.

Recipes: DOS-root .analysis/reconstruction/probes/native-initial-v1383/
for ownership/counterexamples; native-initial-v1383-v2/ for final builds,
run_validations.py, verify_pixel_change.py, phase_control.py, verify_phase.py
and frozen reader replay. Receipts: native .analysis/port64/native-initial-v1383-v2/.
All heavy work uses CPU0 at low priority; all actual launches are muted/dummy.
No DOS source, original target or historical exact acceptance changes.

## v1383 terminal validation and recovery

All jobs are terminal. Main 441/live Ghidra and native 345/target CI pass;
unavailable private native gates skip. Final ordinary GNU/optimized UBSan and
separate extra GNU lighting controls, fixed-page full changed-pixel checks,
48 actual tail-copy controls and frozen reader replay pass. Only view.cpp
changes; v1382 whole-cold/69CTest/full-nine-pool producers stay separate.

Lossless retirement reclaims 455,786,496 allocated
bytes (434.7 MiB) before journal cost:
1,073 complete sample/capture/build/restored-image files and
1,044 source-backed caches. Full temporary restoration,
SHA/size/mode/nsmtime/gzip EOF, 24,916 protected hashes,
509 source pins and unchanged DOS fingerprint pass before and after deletion.
All seven new ordinary/diagnostic programs, old programs, frozen sources,
failures, complete original references and full pools remain retained. The
snapshot-only intermediate and reader failures are not restamped or promoted.

From DOS root, restore archived sample/build/image inputs before replay:

```sh
python3 .analysis/reconstruction/probes/native-initial-v1383-v2/verify_retention.py --restore
```

Without --restore it performs complete temporary readback. Old v1382 proof
keeps its add39f3c source scope and cannot attest current 50ca49c6 inputs.
Whole native pictures/cache/margins/RGB/scanout/broader gameplay remain open.
