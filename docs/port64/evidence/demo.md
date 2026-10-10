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
