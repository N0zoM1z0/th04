# TH04 current handoff

Updated 2026-10-18. Complete maintained DOS four-product and faithful native x64
goals remain active. Use one low-priority CPU (`taskset -c 1 nice -n 19`), muted
headless runs and serialized Borland/Wine builds. No host focus or key injection.
Code, documentation and `gpt-6.1-sol: ...` commits are English. Push both main
and native `HEAD:port/modern-64`; read actual Git heads and current finish receipts.

## Current native collision repair (v1473)

The batch starts from main `67076b1` and native `4b082b8`. Native source closure
is566 files, `a7606e662f68a60abbd0e50b6b7d0177dc11fab7154099d1edf4edf5da23352c`.
Current GNU/UBSan programs and link inputs are at
`.analysis/native/port64-recovery-v1445/.analysis/port64/stage3-hit-bridge-v1473-final`.
Fresh GNU87 programs/83 CTests and UBSan2 programs/session checks pass.

Elly's existing private scythe hit now joins main_state.cpp's composite player
hit and resets when the player prefix consumes that latch. No collision math,
invulnerability, input route or RNG behavior changes. Both unmodified cold
frontends replay the actual failed original inputs: all8082 complete init/actor
snapshots of nine whole pools and21 stable fields agree. All8086 available raw
loop/completed-score state, resident and RNG-count rows agree. First hit after
8000 is8046 and the first Continue block is8085, matching original GameOver.
The requested8086-update fixture deliberately exits1 at that block; it does not
clear Stage3. Keep716 post-actor input differences separate.

Both roles preserve all79 complete old8000 output hashes, retaining the existing
8001 pool snapshots,8010 stable rows and nine full RGB/TRAM/DAC sample gates by
output identity. All78 extended output hashes agree between GNU and UBSan.
The before-fix actual native hit8046/pool8047 divergence remains a causal
negative control. Use `elly-hit-bridge-v1473/compare_replay.py --role gnu|ubsan`
and `verify_replays.py`; their data are under `.analysis/reconstruction/probes/`.

## Actual original endpoint and evidence limits

`dos-elly-v1472-original` is terminal/incomplete, not timed out: exit1 after
801.680s at MAIN0AAF:3A51/GameOver8085, load10FC/DS3230. No emulator remains.
All8086 loop inputs matched plan. The sole physical/readback difference is known
7835 Shot32/Enter8192. Its complete29146871-byte old8000 raw prefix and8001
pool/state snapshots reproduce. Actual scythe(2932,4621) overlaps player(3312,4976)
at8046. Independent original MAIN13A9:8165..8199 execution writes global DS4669
at8195; four exact24-pixel boundaries reject among six synthetic unit fixtures.
Those fixtures are not a second live run or whole-helper proof.

Actor data has8081 complete records plus35710 trailing bytes, no gzip footer;
metadata last flushed8000. Never invent original actor8082..8085. Full error RAM,
two literal player/fullRAM witnesses and nine font/video/RAM samples remain.
The earlier defective-bridge private forecast of defeat12991/departure13576 and
Stage4 initialization is contradicted as a safe target route. No actual Elly
defeat/Stage4 original/source acceptance is claimed. Source Stage3 full RGB,
continuous display, natural IRQ/UI timing, NP2/Windows and campaigns stay open.

## Original/source DOS frontier

The MAIN-only source replay completes Stage1/Stage2 at9837/10394 and8000 Stage3
updates in2939.763s. Original OP/MAINE/ZUN/assets remain installed. Source MAIN
is200279 bytes/1183 relocations, SHA256
`778641ab845bcd67c6888bacc049e2cfa20fddda844681d3d2fd164f8386abc9`.
Original MAIN is156258 bytes/1136 relocations, SHA256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The maintained four-product cohort remains `.analysis/build/dos-four-products-v1443`.
Provenance is `candidate-local-attested`, not an official pristine-dump claim.
No DOS source or artifact/unit exactness state changes in this batch.

All8001 nine-pool/22-state/private3 snapshots,8000 actual inputs and28231 common
loop/resident80/RNG observations pass; nine configured video regions agree.
Strict aggregate remains false for49 post-actor keys and nine raw GDC samples.
Original score8000 has no terminal loop; source has an extra loop8000. Final
RAM binds LCG1062/ring16467. Literal player after dialogue7834 reads8192 in both
own-MZ contexts (original0AAF:5FCF/return00F4; source0708:7463/return06AA), distinct
from earlier loop32. It is not an every-player-call trace or attested save state.

The own-MAP sparse source Micro passes300 loops/301 pool-state snapshots and six
full live-font/RGB samples. Original literal-tap Micro retains39 stack-address
and five post-actor bytes in its strict whole-DGROUP failure; seven init offsets
precede taps and their cause is unknown. See the focused differential note.

## Recovery and next work

Use current `elly-hit-bridge-v1473/recover.py` and `verify_restoration.py`.
It carries287 inherited plus396 new exact aliases. All new aliases restore SHA,
size,mode,nsmtime; four restored frontend output maps and both real/archive
paired readers reproduce. Current builds and inherited providers stay physical;
15 superseded build files and269 duplicate replay files now use exact providers.
Restore only an explicitly needed alias with `--restore --path EXACT`, then
verify and retire it after use. Earlier readers may need such explicit restores.
Never overwrite retired paths by rebuilding in an old directory.

The current journal carries65734 inherited identities, all parent/late/finish
identities and providers. Charge current closed-file compression, extra duplicate/
build cleanup and whole-phase new retained costs separately. No earlier cleanup
is credited again. Continue intermediate cleanup during long work and after each
batch; keep required compressed RAM/pool/font/video evidence.

Preserve the passing8000 vector and failed aggregates. Next forecast a legal
input route using the fixed collision bridge, then obtain fresh actual original
and source observations of Elly defeat and Stage4 initialization. Do not weaken
collision or invulnerability. Do not rerun the old unsafe plan or completed
8000 producer. Stored RAM is not an emulator save-state resume.

Continue [the differential note](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md).
Finish focused comparisons, `python3 scripts/ci.py`, tracking and `git diff --check`
before each batch closes. Both complete goals remain active.
