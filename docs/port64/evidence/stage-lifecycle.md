# Stage Lifecycle evidence

Historical bounded results, preserved from `docs/PORT64.md`. Current state is
[the port overview](../../PORT64.md). Original CPU execution and adapter scope
remain explicit; successful component controls do not accept complete gameplay.

## Stage-clear and all-clear bonus

`port64/stage_bonus.*` now owns both original reward calculations, the ordered
text/gaiji/performance/HUD requests, Bomb increment and all-clear extend-disable
side effect. Ordinary native Stage1 consumes this owner exactly once after its
post-boss dialog and shows a colored bonus TRAM layer over graphics tone60.
This advances the v1260 frontier above: the preview now stops on the actual
bonus screen. Score drain, leave overlay, persistent resident statistics and
next-stage resource handoff remain the next integration work; freezing there
does not establish a complete stage transition.

Independent original MAIN CPU controls execute main03 13A9:9C31 (ordinary),
9E06 (all clear),99FE/9A89 formatters,9AFF/9B59 multiplier helpers and actual
main01 0AAF:1874/188E performance arithmetic. At load2000, CS33A9/2AAF,
DS8000 copied from relocated DATA, all1,837 cases agree on complete score delta,
Bomb count, performance, extends and palette tone, plus ordered text/gaiji
bytes/coordinates/colors and performance/HUD calls. There are986 ordinary and
851 all-clear controls, including the complete modifier matrix, five ranks,
Extra, unhandled byte values, word component wrapping, byte Bomb/performance
wrapping, life underflow, pre-modifier threshold neighbors and score-delta
overflow. Linux ELF64, Wine/MinGW PE32+ and optimized GNU UBSan/bounds all
execute the same original CPU producer independently. Video consumers are
intercepted; these controls prove math/state/requests, not complete rendering.

Preserve these original details:

- Reward units are ten points; value gaiji append the final zero. Component
  values first wrap as unsigned16-bit values, then widen. This includes
  graze×5 and `(remaining_lives-1)×1000/3000`; zero lives is not clamped.
- Life-credit, Continue and rank multipliers each perform their own unsigned
  multiply/divide-by10 and truncate. Extra has no rank multiplier. A zero final
  defeat-bonus byte applies a zero multiplier and skips the other descriptions.
- Ordinary performance thresholds use the unmodified subtotal, even when
  timeout zeros the award. The Bomb byte increments on every ordinary clear,
  including timeout/zero point items; then no-miss/low-Bomb performance raises
  run in order. All clear sets extends10 and does not grant a Bomb or change
  performance.
- Raise performs wrapped byte addition plus unsigned upper clipping; lower
  performs wrapped byte subtraction plus signed lower comparison. The target
  arithmetic executes, rather than being replaced by an Oracle adapter.

`bonus_text.hpp` localizes the maintained MAIN DATA strings with readable
Japanese comments. The CPU Oracle found the candidate timeout description at
`src/main/stage/bonus_state.asm` has eight full-width spaces before ×; pinned
MAIN DATA2134:1F79 has seven. The portable table corrects this one character.
The DOS owner is unchanged because changing its data extent would require
separate layout/build validation. Candidate DATA observations are not inherited
as original facts. Negative receipt: `bonus-v1261/candidate-text-mismatch.json`.

Native fixtures still start eight natural Stage1 routes from the OP handoff
with real gameplay and no injected reward or Boss start. Their final snapshot
now includes the actual bonus; the first four images/counters and all prior
shot/combat/midboss/diagnostic Orange images remain unchanged. Three extra ticks
leave delta/Bomb unchanged, proving the front end does not award repeatedly.
The current native prototype has no death/Bomb/Continue consumers, so those
live counters remain zero; only the isolated original CPU cases cover their
nonzero reward effects. Colored TRAM uses actual font/game gaiji and cell
replacement, including blank glyphs. Blink and complete original color/page
composition are not established by the snapshot controls.

Ten contracts and40 natural checkpoints agree Linux/Wine/UBSan. Native Windows
headless replay also passes ten contracts and the40 BMPs/48 counters. The
Windows root native executable and English launcher are refreshed with a
versioned backup under `port64-preview/v1261`; DOS files/launchers/assets are
unchanged. No native Windows GUI pacing or original full-route claim.

```bash
python3 port64/verify_bonus.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-bonus-contracts \
  --output-dir .analysis/port64/bonus-v1261/cpu-linux-attested
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-bonus-v1261-final/receipt.json
```

Receipts: `bonus-v1261/cpu-{linux,windows,ubsan}-attested/receipt.json`,
`integration-review.json`, `native-windows-receipt.json` and
`verification-bonus-v1261-final/receipt.json`. The same independent rejecting
adapter control checks that a Unicorn callback exception cannot silently pass.
Semantic remains stopped; next implement score drain and actual stage leave /
resource transition, not additional naming work.

## Score drain and extends

The current native MAIN ends each ordinary simulation frame with the original
score owner, after its frame counter and periodic performance raise. Actor/item
awards enter one pending accumulator. Score update transfers that amount into
eight little-endian decimal bytes, preserves continues in digit0, compares the
complete high score and dispatches extends. Life/performance changes and the
20-frame bullet-clear minimum feed the actual simulation; sound, life-HUD and
popup remain requests pending their consumers. HUD score rows56:4/6 now use
the original game gaiji and remain bright over dimmed graphics.

Pinned MAIN main01 0AAF:6BD4..6CA2 (update),6BA2..6BD3 (HUD),4316..43B5
(extend) and actual1874 performance raise are independently executed at load2000,
CS2AAF, isolated DS8000 copied from target DATA2134, resident9000:0000.
All4,690 transitions agree Linux GCC8.4, MinGW13 PE32+ under Wine and optimized
UBSan/bounds:3,759 isolated controls plus five retained-state sequences926 steps
and their five initial calls. Subsequent awards are injected into each owner's
retained state; target outputs are not reseeded into native after each tick.
Complete decimal/high-score/temp/HUD bytes, pending/frame dwords, life/clear/
performance/extend/popup state and ordered requests agree. The rejection control
also proves a failed Unicorn callback cannot silently pass. Identity remains
candidate-local-attested; no DOS exact claim follows from portable equality.

Keep the target's low-word-only frame-delta assignment even when a fixture's
high word is nonzero. Preserve the five temporary-digit writes and six AAA
iterations, including nondecimal AF/two-byte carry controls. The highest score
byte remains unnormalized. Extend predicates compare digit6/7 directly rather
than a total integer threshold, then raise performance/increment extends before
the life-cap check. Granting a life from99 produces100; the next grant is
suppressed. Continue and score digit0 share target DATA2134:4349 (confirmed by
0AAF:3CDA increment and43C0 reset skipping digit0). Maintained DOS storage
places a separate `_continues_used` byte before `_score`; that candidate layout
cannot establish the native ownership contract. DOS source is unchanged.

The live900-frame pickup/drain control conserves all awards, grants two extends
once, emits SE7 requests and publishes a20-frame clear timer. Eleven contracts
pass Linux/UBSan/Wine/native Windows. Forty natural Normal/Lunatic character/
shot-idle snapshots and counters agree Linux/Wine/UBSan/native Windows. The
old60-frame BMP is independently recreated with the saved v1261 PE; exactly960
pixels change inside the two new HUD rows, with every other pixel retained.
This pixel mask justifies the new MAIN fixture hash; other fixture changes may
also reflect real extends/performance changes, not just HUD.

At the end of the score batch this Stage1 preview still froze at the bonus;
the following departure batch connects its same-frame continuation and clocks.
Saved high-score loading, life-HUD, popup/audio, death/Bomb/Continue lifecycle,
resident publication and later resources/Ending/save remain separate work.
Current source/build receipts and English native launcher are packaged under
Windows `port64-preview/v1262`; the root native executable is refreshed only
after delivered hash checks. DOS products/launchers/assets are unchanged.
No full-route, original TRAM/palette composition or GUI frame-pacing claim.

```bash
python3 port64/verify_score.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-score-contracts \
  --output-dir .analysis/port64/score-v1262/cpu-linux-attested
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-score-v1262-attested/receipt.json
```

Receipts: `score-v1262/cpu-{linux,windows,ubsan}-attested/receipt.json`,
`target-owners.json`, `render-review/receipt.json`, `integration-review.json`,
`native-windows-receipt.json`, and `verification-score-v1262-attested/receipt.json`.
Stop naming work here; next resume the actual boss-update frame after blocking
dialog, then port the416/488 leave/next-stage handoff without skipping it.

## Stage enter and departure

Ordinary Stage1 now enters through the original black TRAM gaiji mask, completes
its blocked post-boss dialog inside the same actor frame, awards/drains its
bonus, and executes the416/488 leave sequence. The actor prefix runs once;
paused dialog ticks do not move actors or consume RNG. On continuation the
saved contexts feed items/gathers/render, overlay, frame/periodic performance
and score. Deferred tone60 is applied when that frame completes; the dialog
snapshot retains the palette previously displayed. Removing the former extra
front-end dim prevents the bonus scene from being dimmed twice.

Observed pinned MAIN owners at load2000: main01 CS2AAF, unloaded0AAF:
enter62B3..6348, leave6349..63B4, black6287..62B2; main03 CS33A9,
unloaded13A9: common defeatACB3..AE86. Isolated DS8000 is copied from
relocated DATA2134; resident9000:0000. Gameplay-loop0AAF:0098..0212/fileC388
places player/shots/bullets/enemies before the far boss callback at0105,
items/gathers after it, overlay0148 before clock01A8 and score0204. Database
attestation is the root `.analysis/ghidra/database-attestations/th04-main.json`.
These are target/runtime observations, not a new DOS exact promotion; pinned
target provenance remains candidate-local-attested.

Enter/leave share DATA2134:1B62. Enter draws at nonzero multiples of8 using
byte gaiji64-time/8 and retains72 when it changes callback to titles. Leave
decrements first; at416 it starts72→71, at488 zero-time black fill clears the
callback. TRAM is replaced across24×23 gaiji cells, not blended over retained
bonus letters; the score rows outside the playfield remain bright. Actual
GAMEFT gaiji57 independently explains all8,726 changed pixels in the60-frame
fixture relative to the saved v1262 PE; all other pixels remain identical.
Title/BGM/demo overlay consumers and original complete video timing are separate.

Common defeat adds wrapped stage graze before dialog, then calls bonus exactly
once. At416 it requests sound fade10; at488 it increments resident stage/ascii,
sets quit2 and requests one delay frame before finishing the ordinary frame.
TH04 ordinary leave does not flush pending score; remaining score carries into
the next session. The live application publishes graze/lives/Bombs/stage/ascii
without replacing MAIN, reseeding its LCG or falsely loading Stage2 resources.
Further input is held at that unloaded request. The current preview ends with
black playfield and bright score, pending the actual Stage2 loader and actors.

Independent original CPU controls cover all256 timer bytes, interval/wrap
boundaries and1,929 departure cases. Original machine context pauses at the
far dialog callee and resumes at its actual return address; held ticks preserve
the caller state. Three retained489-tick original departure→leave→score sequences
exercise pending1,20,000,000 and2,000,000,000, including nonzero pending at
stage advance. In total4,331 input commands/7,265 complete state and ordered
request records match GCC8.4 Linux, MinGW13 PE32+ under Wine, optimized
UBSan/bounds and actual Windows PE execution. A rejecting callback remains a
required negative control. Forty focused original Orange phase255 snapshots
also preserve the prior serialized boss/pool/global/RNG contract.

The first fixture was rejected at frame1 because Python native-aligned Bh
inserted a padding byte, writing256 to target53DA. Explicit packed little-endian
<Bh restores the intended phase/frame bytes. Keep the rejecting observation;
an adapter packing error is not permission to change target semantics.

Twelve contracts pass Linux/UBSan/Wine/native Windows. Eight natural Normal/
Lunatic character/shot-idle Stage1 routes produce64 identical BMPs and72
counters across all hosts, through bonus,416 fade, late mask and488 request.
Controls check actors/RNG do not repeat on dialog resume, bonus/fade/next-stage
requests occur once, and the unloaded Stage2 request freezes further updates.
These are headless behavior/picture controls, not measured GUI frame pacing.
Windows package `port64-preview/v1263` and root native launcher are refreshed
after delivered hashes; DOS products/assets and normal/invincible launchers
are unchanged.

Stage2 session/resource initialization, midboss/Kurumi, final/Extra Ending
dispatch, saved high score/life HUD/popup/audio/death/Bomb/Continue/Ending/save
remain outside this slice. Later run initialization must reset accumulated
resident graze at its actual owner; these scenarios start a fresh application.
When loading Stage2, preserve global pending score while resetting only the
proved stage-owned counters/pools, then activate the correct resources/boss.
Do not merely relabel Stage1 or reuse Orange as a placeholder.

```bash
python3 port64/verify_transition.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-transition-contracts \
  --output-dir .analysis/port64/leave-v1263/cpu-linux-attested-final
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux-live-v1251 \
  --windows-dir .analysis/port64/windows-live-v1251 \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --font-bmp .analysis/port64/dialog-v1260/FREECG98.bmp \
  --output .analysis/port64/verification-leave-v1263-final/receipt.json
```

Receipts: `leave-v1263/cpu-linux-attested-final/receipt.json`,
`cpu-{windows,ubsan}-attested-final/receipt.json`, `target-owners.json`,
`gameplay-loop-owner.json`, `render-review/receipt.json`,
`orange-departure-cpu-linux/receipt.json`, `integration-review.json`,
`native-windows-cpu.json`, `native-windows-receipt.json`, and
`verification-leave-v1263-final/receipt.json`. Semantic remains stopped;
next port the actual Stage2 session/resource/actor boundary.

## Stage actor-session preparation

This section records the v1264 preparation frontier. The following Stage2
midboss section advances that actor integration beyond2600 to the Kurumi gate.

The next-stage actor API now operates on the existing MAIN owners instead of
creating a new gameplay session. It clears the seven implemented entity pools,
resets player current/previous position, firing time/style, stage point/dream
counts, graze/zap and gather/circle setup. It preserves process-wide score/
pending score, power/overflow/performance, input latch/velocity, shot volley and
hit-spark cycles, bullet clear timer/template/counters, gather center and spark
ring-offset high byte. Score HUD refresh does not drain pending awards.

The original random call order is ring256 → item drop1 → spark angles96,
all from the existing process LCG. Twenty-four double resets retain the same
original machine and native owners between calls:706 draws, with no reseeding
from target output. Stage2 preparation validates its STD before mutating owners
or consuming RNG. The actual departure request is required; MAIN generation,
resident statistics and score remain in the same application.

Observed pinned MAIN load2000/isolated DS8000 owners: main01 unloaded0AAF
runtime06E0..07AD, stage-state73DB..74A5, shots-reset593A..5953,
ring1168..117F and sparks1824..1841; main03 unloaded13A9
items9F8B..9FA7, midboss-reset642C..6453 and Stage2 setupA623..A6F5.
Actual library IRand2000:2172 and score HUD6BA2 execute. Original stage-state
clears nine complete physical extents, checked independently with upper EAX0
on entry to the register-ABI REP STOSD helper. Native custom-entity/point-popup
owners are absent; these target clear checks do not claim their implementation.
Clipping/hardware, shot-level dispatch, item splashes, Bomb, thick lasers,
point numbers and remaining HUD callees use explicit adapters.

The Stage2 midboss seed changes start2600, HP750, sprite0, current/previous
position3072,-512 and velocity0,16; inactive phase/frame/damage metadata stays.
All256 phase-byte controls execute actual original midboss_reset and stage2_setup
and compare the22-byte midboss state plus active flag. Boss/Kurumi callbacks,
rank-dependent boss fields and resource consumers are not ported by this seed.
Native MAIN holds before frame2600 so it cannot invoke the Stage1 callback
under a Stage2 identity.

All928 selected original CPU controls agree Linux GCC8.4, Wine-hosted MinGW13
PE32+, optimized UBSan/bounds and actual Windows x64. There are648 isolated
actor resets,24 retained double resets and256 midboss seeds. The checkpoints
include selected persistent metadata, all96 spark angles, all256 ring samples,
post-clear actor flag/position emptiness and score/HUD bytes. Rejected callback
control remains mandatory; these are bounded state claims, not whole-session
or DOS exactness claims. Identity remains candidate-local-attested.

Four controlled native Normal/Lunatic character routes finish natural Stage1,
retain its actual awards and then load original ST01.STD/ST01.MAP. They execute
10,400 total Stage2 frames, reject invalid STD before mutation and stop at2600
with midboss2 pending. Their counters agree Linux/Wine/UBSan/native Windows.
This is actor/STD/background-state integration without Stage2 visual resources,
full original gameplay or GUI pacing comparison. Thirteen contracts and the
previous64 Stage1 BMPs/72 counters agree all hosts and remain identical to v1263.

The GUI still ends at the unloaded Stage2 request. The new actor API is used
only by controlled integration until its caller replaces stage-owned sprites,
MAP/MPN/palette/portraits/dialog state and joins midboss2/Kurumi. Shared player
resources remain resident. Test package `port64-preview/v1264` contains current
x64 executables, native Windows verification and private stage fixtures; the
root GUI executable remains v1263. DOS source/assets/launchers are unchanged.
Do not advertise full Stage2 gameplay based on this preparation API.

```bash
python3 port64/verify_session.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-session-contracts \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --output-dir .analysis/port64/session-v1264/cpu-linux-final
```

Receipts: `session-v1264/target-owners.json`,
`cpu-{linux,windows,ubsan}-final/receipt.json`, `native-windows-session.json`,
`native-windows-receipt.json`, `integration-review.json`, and
`verification-session-v1264-final/receipt.json`. Initial invalid-style fixtures
were rejected by the existing shot-checkpoint guard; valid styles are now seeded
explicitly. The target/native actor code was not weakened to accept corruption.
Semantic remains stopped. Next implement Stage2 resources and midboss2.

## Player hit, death and Bomb state producer

v1301 introduces `player::Lifecycle`, using the existing movement and shot
trigger owners. It implements original player-update, miss-update, Bomb entry
and Bomb render-state dispatch. This is a component, not live MAIN integration:
character Bomb graphics and the blocking Game Over/Continue scene must join
before gameplay consumes the hit latch. Fire, miss-item, HUD and sound requests
retain order; a missing last-life consumer throws instead of accepting a fake
Game Over return. All verification remains silent.

Original MAIN relative `0AAF:54C4..553A` (player_bomb), `571A..581D` (Bomb
render-state dispatch), and `5E98..610D` (miss/player update) execute at loads
1000/2000, with explicit DS8000/SS7000/resident9000 adapters. Actual movement,
position clamp, point motion, trigger branches and performance-lower instructions
execute. Fire/items/HUD/sound/Game Over/character-graphics calls have guarded
ABI adapters and do not accept those consumers. Header/file identity and root
live MAIN Ghidra attestation pass. Targets remain candidate-local-attested.
Use the boundary ledger's payload offset or authored ledger's file_offset;
analysis_linear/address fields include the analysis load base and are not file
positions. An early scratch disassembly read the wrong region through that
confusion; no state, name or source claim was accepted from it.

The original decrements invincibility before checking the retained hit byte.
A newly accepted hit limits the laser clock to33 before the separate shots
update, arms miss40/invincibility192/respawn72 and clears velocity. The same
player update advances respawn and decrements miss, giving eight opportunities
to deathbomb before the miss32 loss. Shot-trigger time stays frozen during
respawn. At miss32, item drops precede power loss, dream loss, HUD/shot-level,
sound2, performance cap/lower and wrapped resident miss count. At miss0, position
becomes192,368 with velocity0,-32; remaining lives>1 decrements lives, resets
bomb stock and arms clear32. The remainder of the72-refresh motion reaches y304.
Valid dream indices0..7 are controlled; invalid host death indices are rejected.

Bomb entry rejects bombing, no stock, disabled and miss<=32. A deathbomb clears
miss/hit/respawn; stock/HUD precede bombing/frame0/invincibility255/background,
clear192/sound13/pull/used count. Render dispatch preserves BB cel0..15, frame48
scroll-off/palette14 backup and replacement, frame176 restore/sound15/scroll-on,
frame177 hardware scroll request, tone recovery through225 and cleanup at226.
There are227 render updates from frame0 through226. All byte/word wraps and
retained option/palette fields are explicit; host X is translated to MAIN Bomb
bit10 rather than its old dialog bit800/keypad movement meaning.

8,235 isolated controls and four retained260-refresh sequences produce10,319
complete state/request records at each original load. GNU/optimized UBSan/actual
Windows agree byte-for-byte with the same reference. These include corrupt-but-
representable byte flags, timer/stock/counter wraps, movement/trigger boundaries,
all256 Bomb frames, invincibility1-hit behavior, same-refresh deathbomb, last-life
call boundaries and full respawn/Bomb cleanup. An altered Shot fixture changes
clock/requests and is rejected by the untouched original comparison.

Three builds retain35 AMD64 products each and pass34 contracts. The250-file
manifest is `dc88a3e9e12c79f7f64b1b8561a7c2455af4dbe12f6e177dbf49ddf1a7b13496`.
Receipts are under `.analysis/port64/player-lifecycle-v1301/`:
`original-linux-final/receipt.json`, `actual-windows-final/receipt.json`,
`platform-review.json`, native traces, CTest logs and `comparator-mutation.json`.
Replay `verify_player_lifecycle.py --target ../../targets/th04/main.exe --exe
.analysis/port64/linux-live-v1251/th04-port64-player-lifecycle-contracts
--output-dir FRESH`; the Windows verifier consumes that pinned two-load reference
and runs all34 contracts. No physical timing/audio, live player death/Bomb,
Continue, pixel or DOS exact claim. Next implement the missing graphics and
blocking scene, then join this producer and real hit/stock/ranking publication.

## Game Over clock and Continue file ownership

v1302 adds `gameover::Scene`, `gameover::Menu` and separate MAIN score-file
operations. This remains a component: live MAIN suspension, Game Over TRAM
rendering, actual Continue host persistence and Bomb character graphics have
not joined. Target and original CPU observations are separate from native host
observations. Root MAIN database attestation and pinned file/MZ checks pass;
canonicality remains candidate-local-attested. No DOS exact claim follows.

Original MAIN relative `0AAF:3971..3CEE` executes the cell fades, full Game Over
owner/menu and actual score-reset body at loads1000/2000. The original
`130E:0133..0187` release/press loop and `00D7..00EA` frame-delay body execute;
keyboard samples and a recorded refresh counter replace device/IRQ consumers.
Original `0000:0666..06A3` black-out instructions execute with explicit vsync and
palette-show adapters. TRAM, ranking-save, HUD, shot-level, song and process
execution are guarded consumers, not accepted implementations in this control.

Initial out32 + in36 + the27-refresh letter slide reaches acknowledgement at
refresh95. Wait0 has no timeout and ORs two samples; a held acknowledgement key
cannot also accept Continue. The menu supports one vertical toggle per released
press; simultaneous directions toggle once, and Cancel takes priority. Final
Stage (stage_id5) dispatches Bad Ending immediately. Extra (stage_id6) still
shows/acknowledges Game Over, then skips Continue. Used-credit byte subtraction
wraps exactly; ordinary three-credit exhaustion skips the menu. Continue saves
before resetting power1/dream-items0/lives/bombs and score digits1..7/deltas/
extends/popup; dream_score, high score and unrelated buffers remain under their
original ownership. A failed save prevents reset. Continue fades take32+36
refreshes. Quit publishes ES_SCORE before song-fade4 and palette-blackout4;
initial synchronization plus17 four-refresh steps totals69, then requests MAINE.

MAIN file ownership differs materially from the previously attested MAINE
owner. Original relative `0AAF:18BA..1939`, `7F1A..81D7` and original TC4J LCG
`0000:2172..219C` execute with guarded byte-store adapters and actual memory-copy
instructions. MAIN encode takes low/high bytes of ONE RNG word. Its recreate
uses10 draws and writes ten sections; save uses ONE draw and writes only the
selected section. MAINE instead uses two RNG draws per key and save re-keys all
ten sections with22 draws. MAIN character selection tests resident ASCII'1'
exactly. Continue always loads/recreates, including non-turbo; turbo inserts the
8-gaiji CONTINUE name if ranked, marks ordinary stage1+stage_id or Extra stage1,
and writes only then. Ties precede existing equal rows; name terminators, unused
bytes, cleared mask, nonselected sections and trailing bytes retain ownership.

Final-source controls: 2,003 menus /43,661 records, 64 full scenes /677,160
records, and2,985 MAIN file cases /27,710 records. Each agrees between two
original loads, GNU, optimized UBSan and actual Windows. All34 contracts pass
per host. Retained10,319 lifecycle and1,288 MAINE score controls also agree on
all three hosts. Altering a Continue fixture's turbo flag changes the trace and
is rejected by the untouched reference. Initial development streams passed
comparison but were rejected by source-manifest guards after concurrent source
edits; final producers reran against the frozen257-file manifest. No rejected
run enters accepted evidence.

One first actual-Windows contract run reported `cannot replace native score
file` in the separate host-store consumer. Three isolated16-case retries and
the complete34-contract/differential rerun pass. The original error code and
cause are unknown; this is not a diagnosed Windows/antivirus defect. The failed
command/log remains under `actual-windows-failed-first/`. Keep failure
propagation and verify real Continue saves/restarts when the live owner joins.

Manifest: `85bfb562d43d6328cf738530a13c9320a90ffb2ab21fb0ffb3dda05aa29f3a7c`.
Receipts under `.analysis/port64/gameover-v1302/`: `menu-linux-final/`,
`scene-linux-final/`, `main-score-linux-final/`, `actual-windows-final/`,
`platform-review.json`, `comparator-mutation.json`. Replay checked-in
`verify_gameover.py`, `verify_gameover_scene.py`, `verify_main_score.py` with
`--target ../../targets/th04/main.exe --exe CACHE/CONTRACT --output-dir FRESH`;
`verify_gameover_windows.ps1` consumes the three fresh original references and
runs all34 contracts. All launches remain silent; no audio device is opened.

Periodic storage cleanup, requested by the user, reclaimed980,566,016 allocated
bytes this batch. Completed v1300 graphics/frontend and current v1302 traces
were independently read back before immutable hard-link deduplication. Failed
or superseded development streams were retired with path/size/hash records.
Final capture paths and receipts remain; original targets/HDI, source and three
build caches are unchanged. `cleanup-receipt.json` / `final-capture-storage.json`
record protection checks and reclaimed bytes. Never overwrite a shared capture
inode; use fresh replay directories. This is storage maintenance, not new game
acceptance or permission to delete pinned tools/inputs.

## Character Bomb state and graphics

v1303 reconstructs the two character render bodies at MAIN relative
`0AAF:555D..5623` and `5623..571A`, and the retained48-star producer at
`581D..593A`. Target identity is the pinned156,258-byte MAIN; independent
original execution uses loads1000/2000, explicit DS8000 and guarded stack
returns. Actual RNG, polar-vector and growing-circle instructions execute.
The logical comparison adapts fill/CDG/mono and sound calls into ordered
requests; it compares the complete288-byte star array,160-byte circle pool,
shared-ring cursor, tone/change/color and all requests.

The graphic control executes original BB553A/1426/74D8, fill751A/7578,
CDG130E:05D4..0639, mono152A..15A9 and GRCG setup/color instructions. An
explicit visible640x400 shadow handles GRCG TDW/RMW and direct B/R/G/I plane
stores. Independent HDI/PAR and BFNT input decoding supplies BB0/1.BB,
BB0/1.CDG and MIKO16.BFT; the native raster never produces the reference.
Both loads agree on full retained indexed screens. Physical display pages,
scroll registers, pacing and audio remain outside this claim.

Observed behavior retained by the native implementation:

- BB has16 cells,24 columns and23 rows; one bits replace16x16 tiles. Physical
  rows wrap at400, including scroll offsets383/384/399.
- The character picture is384x274 at(32,56). The fill kernel replaces only
  rows16..55 and330..383:94 rows, preserving the central picture rectangle.
- At frame48 each of48 stars draws X/Y from the shared ring. Reimu rejects
  the inclusive X band2048..4096 and derives speed by signed division by9;
  Marisa adds160 to a byte-sized random value, preserving byte wrap.
- Updates preserve signed-WORD position wrapping and arithmetic-right-shift
  pixel coordinates. Reimu retains X at an out-of-bounds respawn and sets Y6144;
  Marisa alternates left-edge and bottom-edge respawn by star-index parity.
- Growing-circle calls at frames81..160 depend on the retained mod4 byte,
  rather than recomputing it from a convenient host counter. Reimu creates two
  polar points; Marisa consumes the additional bounded RNG draw. Full pools
  preserve attempted requests even when allocation fails.
- State advances once per render dispatch. Repaints consume const cached draws;
  they do not repeat particle motion or shared RNG consumption. Circle drawing
  remains the existing separate foreground owner.

Final controls:1,236 state cases/2,252 records, including independently retained
128-refresh character sequences;294 pixel cases/548 full screens,
140,288,000 compared pixels. GNU8.4, optimized undefined/bounds UBSan and actual
Windows AMD64 all agree;34 contracts pass per host.105 products bind263 source
files to manifest
`c0fbe950be3e6f7a4bf794ea357d0c92d6d1859e8c4684296e77137b47d11751`.
A one-bit star-speed fixture mutation is rejected against the unchanged original
state reference. This accepts a Bomb component, not live death/Bomb gameplay.

One development pixel fixture omitted caller GRCG setup for a standalone star
entry. The bounded negative replays a first mismatch at pixel402 (wrong original0,
native2). Executing actual1666/1672 caller setup restores complete pixel equality.
The correction changes Oracle preconditions, not product behavior. Preserve
this distinction; a mono graphics callee does not own its caller's hardware mode.

Replay with fresh output directories using `verify_player_bomb.py`,
`verify_player_bomb_pixels.py` and `verify_player_bomb_windows.ps1`. Final receipts,
source/product hashes and recorded actual Windows command live under
`.analysis/port64/bomb-v1303/`; `review_results.py` reads back the complete native
streams. Captures use gzip; actual Windows hashes binary stdout without creating
an additional140MB raw dump. Eight superseded generated streams are retired
with hashes, reclaiming13,643,776 allocated bytes while2,379 protected source,
cache, input and final-reference files remain unchanged.

Next join these graphics with the player lifecycle and Game Over TRAM owner,
then suspend live MAIN at its actual last-life boundary, save Continue before
resetting resources, and resume the remaining frame once. Extra, full HUD/OP,
audio/configuration and complete natural route/performance validation remain
in the full goal; all launches remain muted.
