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
