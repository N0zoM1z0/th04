# TH04 native branch handoff

## Native registration numeral requests and WORD slots (v1429)

The actual Renderer now consumes recovered numeral requests. Original MAINE
0A05:24B6..2599 uses signed IDIV/remainder after zero-extending the highest
byte and subtracting A0; high bytes0,10,...150 therefore have legal remainder0.
The former negative-high guard incorrectly rejected these rows. Lower seven
bytes still pass raw WORD patterns. SUPER0000:275E..290F doubles that WORD
with16-bit wrap before reading DGROUP0E53 pointer0F0C and dimensions130C.
Pattern8000 aliases0; FF60 reads pointer0DCC and dimensions11CC. The original
has no zero-size early return and can read low memory. The portable renderer
accepts only slots owned by loaded SCNUM2; unowned RAM remains an explicit
boundary. No blank pixels, invented memory, or malformed-file acceptance.

Cold548/fc9b02eb GNU Release and optimized UBSan/bounds each build84 programs
and pass82 CTests. Original instructions agree at loads1000/3333 for131,072
slot controls and16,384 complete row controls. Each native compiler agrees
on65,536 slots and8,192 rows (every byte value at each digit position, both
characters/banks, alternating row0/9).64 new complete graphics captures agree
on both pages, raw palette/TRAM and composed RGB against original drawing/
SUPER at loads1000/2000. BFNT/CGROM/GRCG and RGB scanout remain explicit
adapters. Both actual frontends pass30 seeded registration/save/restart routes.
Four compiled mutations reject signed remainder, byte clamping, incorrect WORD
wrap and the old high-byte guard; unchanged compiled control passes.
Historical exact remains661/663; physical video/CPU timing remains open.
Initial producer548/e1668317 passed the first load but its callback compared
Unicorn memory-hook linear EIP as segment IP at load3333 and rejected its own
control. Failed source/programs/logs remain distinct; current Oracle normalizes
EIP against the recorded load segment and traps callback errors explicitly.

Replay: `.analysis/reconstruction/probes/native-numeral-slot-v1429/`;
producer: `.analysis/worktrees/native-numeral-slot-v1429/.analysis/port64/native-numeral-slot-v1429-v2/`.
`verify_numeral_slots.py` executes original row/SUPER lookups; `pixels.py`
owns the new actual Renderer image controls. Verified archive/content/CRC/
mode/nsmtime/temp-restore retirement saves525.26 MiB net;
all source/programs/receipts/fixtures remain live, retired cache/captures and
stream aliases restore with `verify_retention.py --restore --prefix`.
The reader also verifies/restores `supplement-retention` registration captures
against their original protected hashes.
Continue source recovery and migration. Unsafe unowned score RAM, other waits,
active-PMD paired timing, physical scanout, broader gameplay and Windows remain
open. The full goal stays active.

## Native elapsed registration and all three callers (v1428)

Actual registration now uses shared elapsed Animation for black-in2,
input_wait0 and black-out1, and live Count1-only frame_delay1 for editing.
Alphabet/cursor and accepted command drawing precede keyboard reset. Sense
ORs the pre-wait and post-wait samples; BYTE repeat keeps its30/even/wrap rule.
File operations are consumed one at a time, with writer-close before free/
clear/fade. A failed host operation freezes the scene and Score/Extra parent;
later admissions neither retry I/O nor advance registration ticks/RNG/route.
The outer clock can continue. Successful completion returns unused time.

Normal Ending begins registration on its delay100 completion admission;
Score and Extra pass time directly to registration and then verdict or
Congratulations. Clock/audio service occurs once, and new process counter BSS
keeps raster phase. Legacy no-clock helpers remain separate logical models.

Pinned MAINE decoded0A05:27C4..2B5F menu, score0A05:20F9..24B5 and process
RNG0000:1C5A..1C83 execute unchanged. Fades0000:0622..06A3, frame_delay
0CC7:0033..0047, input_wait0CC7:020A..025F and full0000:2206..222B wait execute
with DGROUP0E53/live0EFA/0EFC/0F02 and ideal IRQ at loads1000/3333.
The62414-byte decompressor payload/559 relocation observations retain their
candidate-derived container topology gap; target canonicality remains
candidate-local-attested. Graphics, keyboard, successful file/sound have
guarded ABI seams; CPU/I/O/audio/loader costs and physical scanout are unmeasured.

Cold545/b4519b50 GNU Release and optimized UBSan/bounds each build84 programs
and pass82 CTests. Each agrees with544 original controls and272 coarse plus
272 one-ms partitions: full E/K/palette/edit-loop/file/RNG/counter/time streams,
ranked/unranked/Extra, WORD wrap/carry skips, held-repeat BYTE wrap, chords,
missing/partial/corrupt file recreation and blocked input. Each actual frontend
passes24 score-return routes/four writer failures,30 seeded saves/restarts,
8 Extra actor-control routes and24 Ending-to-registration/fresh OP/second MAIN
routes. Independent checks retain576 Ending pages/288 original-DAC RGB frames
and48 pages each for Staff/verdict/Congratulations. Existing432 Game Over and
576 MAINE controls pass. Eight default Demo profiles preserve129 prior hashes
each, original selected states and GNU/UBSan parity. No general-game or exact
promotion follows; historical exact stays661/663.

Compiled actual Scene fade-counter clear, pre-draw reset and lost-remainder
mutations reject whole original streams; unchanged compiled control passes.
Native CI345 passes. First probe omitted constructor tone0 palette-show; its
short137 input also let zero HI pass checksum after an empty read, producing
invalid numeral indices rejected by the native renderer. Original core/control
continued with drawing as an adapter; actual unsafe drawing is unmeasured.
This remains an explicit renderer/input boundary, not accepted equivalence.
Valid partial and corrupt selected sections separately recreate and pass.
Second development passed272 controls but the failed Score owner threw on its
next elapsed admission; the new frozen failure matches the retained native
no-retry policy. All failed source/program/trace/journals remain distinct.

Replay: `.analysis/reconstruction/probes/native-registration-elapsed-v1428/`;
producer: `.analysis/worktrees/native-registration-elapsed-v1428/.analysis/port64/native-registration-elapsed-v1428/`.
`verify_registration_elapsed.py` owns full original/candidate streams;
`focused.py` owns actual parent routes and image commands. Verified journal/
SHA/CRC/content/mode/nsmtime/temp-restore retirement saves2435.09 MiB net,
plus42.04 MiB from three preliminary caches. Source/all programs/
fixtures/receipts/failures remain live; archived raw aliases/captures restore
with `verify_retention.py --restore --prefix`. Stage reader is under
`native-registration-stage-retention-v1428`. Only owned intermediates retired.

Other wait owners, malformed-score unsafe graphics, real active-PMD paired
timing, physical CPU/I/O/scanout, broader gameplay and Windows remain open.
Continue source recovery and migration; the full goal stays active.

## Retained native producer routing

Earlier Cutscene, Staff, MAINE, Demo, palette, IRQ and text producers
retain their original source/evidence identities. See the [VSync note](reconstruction/product/TH04_NATIVE_VSYNC_V864.md), [porting status](PORT64.md), and the subject index. Prior handoff detail remains in Git;
current open owners are listed above. Archives restore into fresh paths.

## Comparison priority for the next agent

The user's primary comparison is **original Japanese DOS versus reconstructed
DOS**, both through the PC-98 game route. Native x64 must also preserve gameplay
state and effects. Native-host equality and successful native clears do not
replace either comparison. Start with the four bundled demos, then bounded
recorded ordinary play; compare score, consumed input, RNG and actor state at
the same logical boundary, followed by VRAM/palette/effects and process/save
transitions. See [paired demo evidence](port64/evidence/demo.md).

TH08 is a read-only workflow reference, not TH04 evidence. Its active worktree
is dirty; do not edit it, run its builds, change its database or launch its game.
Complete trace/end/input-consumption guards and first-divergence diagnostics
are the useful parts to adapt. Retained DOS demos accept complete selected scalar/pool/video comparisons.
Retained native producers accept selected scalar/RNG/count fields and nine
complete pools. v1385 preserves the six parent trace/save hashes and 40 entire
index/TRAM samples; whole pictures, original display epoch and broader
gameplay/process routes remain open.

## Replay and finish

```sh
python3 scripts/preflight.py
python3 scripts/ci.py
git diff --check
```

Use [status](PORT64.md), [host-window evidence](port64/evidence/host-window.md)
and [retention](ANALYSIS_RETENTION.md). Source/program/profile archives retain
producer identities; restore into fresh paths. One Borland/Wine writer at a
time. Never open an audio backend/device in these validations.
