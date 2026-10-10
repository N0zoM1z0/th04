# Host window admission and input

## Clear-mask correction and natural Lunatic preparation (v1358)

The previous bit-only admission oracle was insufficient: a fresh unplayed
score section has mask0x19, including bit0. `op_score.cpp` normalizes values>3
to0 before unlock/availability; registration converts a sentinel to a real
shot-bit mask only on qualifying good/Extra/Easy completion. `has_clear()` now
requires mask<4 and the requested shot bit at both the final file and physical
rename boundary. No gameplay/compiler source changes.

The stronger oracle still accepts actual GNU Normal/Extra mask1. It rejects
the retained UBSan Normal result: all final masks remain0x19. Its last MAIN
frame11,440 is Final Stage with miss13/respawn33/invincibility154, immediately
followed by MAINE. Native `gameover::Scene` sends Stage5 death directly to Bad
Ending without a Game Over menu, so absence of scene='gameover' is insufficient
for all-clear. That ending interpretation is source-routed; the generic trace
does not report end_sequence or inner ending pixels. Revoke the old UBSan
all-clear/admission claim; retain its actual reached-stage/save/registration/
freshOP/restart/clock/zeroaudio evidence. Original v1357 green receipt and its
producer/consumer sources remain immutable historical comparator evidence.

`verify_clear_admission.py` replays the actual GNU positive, UBSan negative and
five complete checksum-valid clones: flags0,2,0x19,0x41 and physical snapshots
whose flags are0x19 while final file remains valid1. Each rejects at the intended
admission or physical boundary gate; immutable trace hardlinks are never written
and all scratch clones retire after their verdict/hash capture. Both original
routes/files remain unchanged. The first private readback assumed both old
positives survived and failed; corrected v2 records the narrower result.

`verify_window_route.py --adaptive --rank 3 --character 0 --shot 0 --key-driver
xtest` runs a natural six-stage Lunatic candidate with fresh legal options,
ordinary OS keys and no reference-route dependency. It requires six actual
stages, credit0 throughout MAIN, real mask<4/shot bit in the selected
rank+5*character partition, nine other decoded payload/checksums, unchanged CFG,
fresh OP and separate Scores restart. New startup selection supports Marisa via
Right and Shot B via Down. The ReimuA trial was pending in v1358 and completes in v1359 below; do not
accept another rank/shot merely because its argument is implemented. Legacy fixed/
position modes still require the original attested Normal ReimuA reference.

The complete read-only reducer now reports rank3 MAIN density>=320/>=400, each
contiguous span, slowdown2, advance/presentation/deadline-lag distributions and
CPU advance over its after-update admission period. Normal440/dialog440 are
excluded by independent category controls; exact320/400 boundary samples are
included. Previous complete GNU Normal/UBSan ending/GNU Extra clock checks still
pass and report zero Lunatic samples. Update timings exclude subsequent advice/
trace work; virtual display/shared-machine/observer timing is not uninstrumented
FPS, physical Windows or original hardware timing acceptance.

```sh
python3 port64/verify_clear_admission.py --normal-route PASSED_GNU_NORMAL \
  --rejected-route PREVIOUS_UBSAN_SENTINEL_ROUTE --output FRESH_DIRECTORY
```

Receipts and full launch/source vectors: `.analysis/port64/lunatic-window-v1358/`.
No Windows GUI/foreground/host keys or audio backend/device opens are permitted.
Both CIs pass (root includes live Ghidra replay/mutations), as does diff check.
No new build/program is generated; all 489 consumer inputs are fully archived
and read back, with compiled inputs equal the old producer. Source-backed
post-CI caches retire with full source/hash readback under root
`.analysis/cleanup/lunatic-source-caches-readback-v1358.json`; live outputs are excluded.

## Complete native Normal window routes and trace controls (v1357; narrowed by v1358)

Original v1357 comparison reported GNU/optimized-UBSan Normal Reimu A via
ordinary OS keys on private Xvfb. Both old verifiers reject a visible Game Over menu/Continue and
observe every MAIN row as program1/generation2/rank1/character0/shot0/credit0.
Six actual stages lead to MAINE program2/generation3, Ending, registration Esc,
physical IN_MOVED_TO score snapshots, fresh OP and a separate Scores process.
The v1358 correction above revokes UBSan all-clear/admission; its final mask
is0x19. GNU good-clear remains accepted. Nine other decoded partitions preserve
checksum/payload bytes2..195; encoding
keys0/1 can change. Physical CFG remains the legal Normal/lives6/Bombs2/BGM2/
SE1/Turbo configuration. Ending/save/restart acceptance is native runtime
observation; original whole-route or physical device equivalence remains open.

| Recorded native observation | GNU8 | Optimized UBSan |
| --- | --- | --- |
| Outcome under corrected admission gate | accepted good-clear | rejected all-clear/admission |
| Route refreshes | 89,008 | 86,333 |
| Separate Scores restart refreshes | 794 | 795 |
| Last MAIN frame / lives / misses | 13,607 / 2 / 11 | 11,440 / 1 / 13 |
| Maximum observed bullets | 402 | 361 |
| MAIN records with after-update slowdown2 | 3,245 | 2,765 |
| Recorded resyncs | 2 | 505 |
| Advance p95 / p99 (ms) | 7.13 / 11.69 | 15.11 / 23.10 |
| Presentation p95 / p99 (ms) | 11.74 / 13.14 | 8.28 / 11.01 |

The rows include natural gameplay, stage transitions and fades; slowdown2 here
is not by itself a dense-bullet timing result. Advance duration ends before the
separate advice/trace work. Deadline lag includes whole-loop lateness. Shared
machine load, private display and full observer work affect the measurements;
they do not establish uninstrumented FPS or dense Lunatic acceptance. OS timing
changes native keys/RNG/survival between hosts; raw cross-host equality is not
asserted.

`reduce_window_route.py` reads complete traces without launching a game. It
couples v1/v2/v3 headers to 29/38/40-token R bodies, checks every sequence,
audio/focus invariant, after-update deadline/resync, presentation ordering and
terminal R/P/D counts. Historical v1/v2 traces also pass. Five independent
consumer mutants reject a +1ns deadline, v3 body truncated to v1, missing E,
a declared six-stage report lacking actual Stage6, and a correctly checksummed
physical score whose Normal admission bit is absent. The first control recipe
failed because its last cloned fixture omitted physical snapshots; that failed
consumer remains failed. Corrected v2 rejects the admission mutation for the
intended reason.

Receipts: GNU Normal `.analysis/port64/full-window-v1356/linux-normal-adaptive-v5/`;
independent GNU/UBSan trace/storage, controls and failed Extra evidence under
`.analysis/port64/window-route-v1357/`. All four complete route/restart processes
are muted with zero device opens/failures through terminal E. See
[Extra OS route and trials](extra.md) for its separate no-Continue/full-name gate.

Only Python consumers/file list change. The 488-input consumer manifest is
`4307e19f6f25038d01cd01e115c2f5bfd851a5d3631fe9f0b417b8fef0a6c3ef`;
the frozen compiled producer remains `00af24f7…` with 485 inputs. Full archived
source vectors read back; every C++/header/CMake input is raw-identical. No new
build or Windows execution is accepted. Two unused failed-fixture trace copies
retire 18,128,896 allocated bytes after full equality/recovery readback against
the retained complete GNU Normal traces. Original/user files are preserved.

```sh
python3 port64/reduce_window_route.py /path/to/window.tsv --output FRESH.json
```

## Natural startup and full-window control candidates (v1356)

The user is using the Windows host. Windows GUI launches, foreground
activation and host key injection are prohibited. No Windows game GUI is
launched for this batch after that instruction. Linux windows use private Xvfb;
`private_x11.py` checks the server PID, user, argv and disabled TCP before
starting a controller. The program itself has no input injection interface.

Two 27-case matrices on the unchanged v1355 GNU/UBSan programs pass natural
startup to menu: PMD/PMD86/PMDB2 times all nine BGM/SE configurations. They
produce 16,070/16,077 refreshes, preserve each initial physical CFG and report
zero audio opens/failures through terminal E. This is current native startup
integration, separate from earlier original-component pixel comparisons.
The Windows v2 startup batch retains 19 native exit-code-zero cases before
`Owned window exited before menu`; no aggregate 27-case acceptance follows.
The first Windows consumer failed its nullable `.ExitCode` check; keep that
failure and its trace rather than replacing its verdict with later receipts.

The first recorded/path controllers incorrectly translated bits 1/2/4/8 to
Left/Right/Up/Down. Correct values are Up/Down/Left/Right, independently
confirmed by actual single-bit SDL/X11 movement: 7/7/6/7 consecutive pairs at
64 Q12.4 units on the corresponding signed axis. The first axis consumer
failed its final str/Path digest readback after assertions; corrected v2
repeats and closes the complete check. No original target claim is added.
Wrong-map failures cannot diagnose asynchronous delivery. Correct-map fixed
and position-tracking attempts also reach actual Game Over, respectively
Stage 1 frames 7,839 and 8,278. Original wrong-map attempts remain failed at
Stage 1 frame 7,266 and Stage 2 frame 3,121. All raw traces/keys/files survive.

`route_advice.hpp` extracts the existing key-only headless policy into a const
observer. `--window-route-advice` requires a muted fresh window trace, emits
`advice_held`/`advice_shift` in v3, and never feeds them to gameplay. External
`verify_window_route.py --adaptive` sends ordinary X11 keys chosen from those
observations. It retains Game Over rejection, six actual loaded stages,
Ending/registration/fresh OP, the physical rename clear flag, nonselected
partition checksum/payload invariance and a separate Scores restart. No
actor, hit, life, score, clock or transition is written by the observer.
Without explicit advice, both new fields are zero. Observer CPU/I-O cost
precludes an uninstrumented performance claim. Parsers retain v1/v2 support.

Cold v1356 products retain 485 inputs (`00af24f7…`) and 204 program
identities. GNU/UBSan pass 67 contracts each plus manual held-input
regressions with advice disabled. Windows is cross-compiled only; its
new execution remains unverified. 104/105 GNU/MinGW core objects equal
v1355; only trace serialization changes. Both control-plane CIs pass
(root includes live Ghidra replay/mutations). Historical acceptance
and target provenance are unchanged.

The GNU logical Normal Reimu A replay preserves all 88,934 input/state ticks,
startup/menu inputs, Ending name and physical saves compared to v1351. It
uses render_every0 versus the old every-refresh1; it makes no wall or pixel
identity claim. GNU good-clear and UBSan save/restart were recorded in v1357; v1358 above
revokes the broader UBSan all-clear/admission claim. No complete Windows
route, dense Lunatic timing/performance or physical audio acceptance follows.

```sh
xvfb-run -a -s '-screen 0 800x600x24 -nolisten tcp -noreset' \
  python3 port64/verify_window_route.py --adaptive \
  --exe .analysis/product-v1356/linux/th04-port64 --exe-sha256 PINNED_SHA256 \
  --hdi /path/to/zun.hdi --font /path/to/FREECG98.bmp \
  --reference .analysis/port64/public-routes-v1351/linux-v3/normal-reimu \
  --output .analysis/port64/window-normal-NEW
```

`verify_window_startup.py` also needs a pinned ELF digest and `--rom` for the
27-case matrix. Receipts, full source vectors, failed recipes and recovery
archives are under `.analysis/port64/full-window-v1356/`. Only two terminal
owned Windows staging directories were removed after complete archive/member
readback: 155 files, net 36,333,457 logical bytes (receipt overhead excluded).
All original inputs, preceding products and user saves remain untouched.

## Ordinary window Continue and physical restart (v1355)

v1355 adds a read-only trace v2 score/life/statistics snapshot and an ordinary
X11 Continue/save/restart verifier. 204 AMD64 programs build cold from 481
producer inputs; GNU8, optimized UBSan and actual Windows pass 67 contracts each.
Among 105 GNU/MinGW core objects, only trace serialization changes; 104 remain
raw-equal to v1354. GNU/UBSan's 195 fake-audio frontend files per host also equal
v1354. No audio backend/device opens.

Eight real SDL/X11 processes under private Xvfb pass two stationary Lunatic
Reimu A Continue/Quit/registration/fresh OP cases and two physical-file Scores
restarts per GNU8/UBSan. MAIN freezes at frames 432/630 during Game Over and
resumes at 433; Continue resets score/power/lives/credit. Missing-score/unranked
and declared zero-score/ranked leaderboard fixtures are distinct. Ranked
writer-close/rename snapshots contain CONTINUE 500 units with credit 0 while
MAIN resets to credit 1/score 0. Nine other decoded partitions preserve checksum
and payload; encoding keys legitimately change. Restarts preserve file hashes.
All launches are muted. These are bounded OS-input trials, not complete clear
routes, original whole-route equivalence, physical devices or dense timing.

Producer manifest: `cce4f0fd683c5166f798303e2ebfb83a4fbbe8baef1ee56a862c024c25dbe3be`.
Final verifier: `d027a9701ce8c6168c408bd18a93b72806e60079e87cbf39b7ab8d0ef9267f5c`.
Only the route verifier differs; every compiled input is raw-identical.
Keep the first missing-verdict-key and key-header comparator failures failed.
Current evidence/recovery: native `.analysis/port64/host-route-v1355/`;
replay/limits: native `docs/port64/evidence/host-window.md`.

Actual Windows still rejects before SendInput. PID/class selection now excludes
an early ConsoleWindowClass handle. Same-session WinSta0/Default diagnostics
observe foreground-lock timeout 2147483647 ms; three owned-window activation
attempts fail. No desktop/global policy/input-queue workaround was used.
Passing Windows contracts do not accept Windows held input.

`verify_window_continue.py` uses only ordinary X11 held keys on a private display.
Legal configuration is Lunatic/lives 1/Bombs0/BGM2/SE1/Turbo. The ranked fixture
changes the selected rank 3 leaderboard to zero scores; it injects no gameplay
state. Inotify IN_MOVED_TO captures complete physical score snapshots after
HostStore flushes/closes its reserved temp file and renames it. Observation
occurs after the operation; it does not timestamp the exact internal close.
Both ranked captures arrive during first Game Over (observed refresh 1212),
contain the previous 500 committed score units/credit 0, and persist through
registration and a separate process. Unranked runs contain no CONTINUE entry.

Both Game Over blocks freeze MAIN frame/x/y for 199 and 232 refreshes. Physical
restart naturally runs startup, opens Scores via four Up events, returns to
menu and exits; files remain identical. GNU/UBSan second-life scores can differ
because OS input delivery and menu wall timing differ; no cross-host raw route
identity is asserted. Complete terminal E records verify zero audio opens.
Existing Marisa B held-input regressions also pass with v2 traces: GNU 960 R /
1166 P, UBSan 955 R /954 P, normal/Shift 64/32 Q12.4 movement and focus zeroing.

First attempt omitted fresh Z for the score-only MAINE verdict and hit the
180-second watchdog. Second attempt completed fresh OP but its comparator
wrongly compared the decoded key bytes 0/1, which every save regenerates.
Corrected checks retain raw files and checksum validation, comparing 2..195 of
nine nonselected sections. Frozen source archives keep each failed recipe and
all compiled inputs identical; neither failure is retrospectively promoted.
Independent comparator controls reject a bad checksum and a checksum-valid
changed nonselected payload, while accepting valid rekey-only raw differences.

Windows diagnostic selection must enumerate PID plus TH04Port64Title class:
early Process.MainWindowHandle may refer to ConsoleWindowClass. Desktop open
succeeded; the reported error 203 is a stale GetLastError and proves no failure.
The current foreground timeout and denial are observations, not a causal proof
that changing the timeout would solve admission. Empty Generic.List emits no
actions file; the private postprocessor initially expected one and failed.
Missing action output is accepted only alongside the pre-Action focus rejection.
[SetForegroundWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow)
corroborates that activation can be denied; no global timeout edits or
[AttachThreadInput](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-attachthreadinput)
keyboard-state side effects are used to bypass the user's foreground work.

```sh
xvfb-run -a -s '-screen 0 1400x900x24' python3 port64/verify_window_continue.py \
  --exe ../port64-window-route-v1355/.analysis/product-v1355/linux/th04-port64 \
  --hdi ../../runtime/images/zun.hdi --font /path/to/FREECG98.bmp \
  --ranked-fixture .analysis/port64/natural-continue-v1352/ranked-initial-GENSOU.SCR \
  --output .analysis/port64/window-continue-NEW
```

v1355 scoped cleanup keeps all 204 programs, producer/consumer source archives,
compiler/CMake metadata, traces, physical files, captures and failed attempts.
It retires 1190 regenerable build files / 70 completed contract-stage files after
two full recovery archives / 144 members read back, net 596836352 allocated bytes.
An independent replay verifies 2847 protected hashes and all 1260 absent files.
The three earlier desktop stages retire 20 files, net 35110912 bytes; the terminal
GUI stage and archived failed consumer materialization retire 494 files,
net 22450176 bytes. Immutable capture sharing keeps 324 complete BMP/PCM paths
and hashes, net 210509824 bytes. Counts subtract their journals/archives but
exclude final receipt size. No original input, accepted program or save deleted.

## Previous scheduling frontier (v1354)

v1354 owns host scheduling, focus and the optional read-only window observer.
It fixes SDL keypad Enter missing from held input and preserves slowdown when
a four-step catchup resynchronizes its next deadline. The 17,730,496 ns period,
four-step limit and after-update slowdown are explicit native host policy.
They are not a new claim about original PC-98 hardware refresh.

`port64/host_window.{hpp,cpp}` has no simulation or sound clock ownership.
Win32 still reads GetAsyncKeyState's high bit on the active desktop; SDL still
reads pumped scancodes. Focus gates the complete held/Shift result. Menu key
messages and per-refresh held state remain separate. SDL accepts Return and
keypad Enter in both paths. The window title now describes the current product.
Sound Refresh retains its before-update slowdown factor, whereas host admission
uses after-update slowdown. Both factors are observed separately in the trace;
this preserves the existing transition policy rather than asserting hardware equality.

`--title --mute --window-trace FRESH_DIR` records input, scene, generation,
MAIN frame/entities, CPU advance/render duration, host presentation duration,
resyncs and output-device attempts. Snapshot collection does not write state
or supply input. Trace flushes add observer cost; presentation is measured
separately from existing MAIN host timing. Unmuted, diagnostic, headless and
existing-output requests reject before asset/save entry. Eight GNU/UBSan
negative controls preserve marker files and never create saves.

## Build and evidence identities

All 204 AMD64 programs build cold from the 480-input producer
`e2974686f86f22d2a2a7caaf736b664dd33aac3eae4703aeefbf93a7e9e6ac75`.
GNU8, optimized UBSan and actual Windows pass 67 contracts each. All preceding
104 core objects are raw-equal on GNU and MinGW; `host_window.cpp` adds one.
The existing fake-audio frontend's complete 195 files per GNU/UBSan host equal
v1353. Fake backend contracts never open a physical device.

The final consumer recipe manifest is
`04ec21c37c2039c549b4130b8432693940c9bf53109e1765174204f8dfe4c4c7`.
Only two host verifier scripts changed after the producer freeze. Every
compiled source/header/CMake input remains byte-identical, and both complete
source archives are retained. Do not restamp product receipts with the consumer
identity. Earlier Linux/PCM consumer receipts keep their own recipe identities.

Two source-only wrong policies reject: unscaled resync and leaked background
input. The independent fake-clock contract exercises slowdown2 and bounded
catchup. The actual short window runs do not establish natural dense slowdown2.

## OS window observations

GNU8 and optimized UBSan run real SDL/X11 callbacks under private Xvfb displays.
Natural startup and ordinary menu keys select actual Marisa B/Lunatic. Each
short Stage 1 trial checks Return/keypad Enter, movement, Shift, repeated Z,
release and a separately owned focus sink. Normal X displacement is 64 Q12.4
units per completed frame; Shift is 32. Background input is zero. Output opens
and failures remain zero. GNU observes 936 refreshes/1,132 presentations;
UBSan observes 934/1,128. Exact wall durations are in the private receipts.

A retained completed GNU observation also exercises one resync. Its initial
comparator failed by comparing a wake timestamp with later catchup begin
values. Corrected replay associates D with the next R in file order, verifies
the recorded next deadline, and preserves the failed verdict separately.

Actual Windows passes all 67 contracts. Its active-desktop controller owns an
offscreen visible game window and guards foreground before SendInput. The
second attempt cannot establish foreground and stops before sending any key.
This is an environment rejection, not Windows held-input acceptance. An
inactive desktop or SendMessage substitute cannot satisfy this claim.

The first Linux focus controller searched xmessage by PID, but its X11 window
has no _NET_WM_PID. The corrected controller discovers its unique title only
on a private display. The first Windows finally block's Generic.List array
conversion raised ArgumentException and masked the early error; ToArray and
a preserved structured error expose the foreground rejection. All attempts
and their frozen consumer sources remain recoverable.

## Replay, delivery and limits

```sh
ctest --test-dir ../port64-window-v1354/.analysis/product-v1354/linux --output-on-failure
xvfb-run -a -s '-screen 0 1400x900x24' python3 port64/verify_host_window.py \
  --exe ../port64-window-v1354/.analysis/product-v1354/linux/th04-port64 \
  --hdi ../../runtime/images/zun.hdi --font /path/to/FREECG98.bmp \
  --output .analysis/port64/host-window-NEW
```

`verify_host_window_windows.ps1 -Plan PINNED_PLAN.json` supplies equivalent
owned-window OS input controls and stops if foreground cannot be established.
Plans pin products, original HDI/font and controller separately from writable
host saves. Current receipts, complete command vectors and recovery archives:
`.analysis/port64/host-window-v1354/`.

A new private experimental GUI is installed at
`/mnt/d/Entertainment/Game/Touhou/th04-reconstruct/native-port64-v1354/`.
Both launchers explicitly mute; new Normal/3-life/2-Bomb options and independent
host saves never replace the two DOS packages or their mutable images. All 21
preceding files retain their hashes. Product and verification source archives,
profiles and file inventory accompany it. No game/device was launched during
publication. Delivery does not accept the pending Windows input gate.

Remaining: actual Windows input, physical display/keyboard, host slowdown2 and
dense Lunatic timing/performance, complete route/config/restart combinations,
startup across sound modes and physical audio output. The full native goal
stays active. No historical exact unit or target provenance is promoted.

Primary API contracts: [SDL keyboard state](https://wiki.libsdl.org/SDL2/SDL_GetKeyboardState),
[GetAsyncKeyState](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getasynckeystate)
and [SendInput](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput).
Their platform rules corroborate adapter design; local OS observations provide
the bounded behavior evidence.

Terminal failed Extra trace/actions materializations are compressed in
`.analysis/port64/window-route-v1357/gnu-extra-failed-trace-v1.tar.gz`.
Every member SHA reads back before/after retirement (net4,526,080 allocated B);
restore under a fresh private directory for failed-trace replay. The failed
verdict remains failed. Both final CIs/diff checks pass; root includes live
Ghidra replay/mutations. Post-CI caches retire only with source/hash readback;
root `.analysis/cleanup/window-extra-final-caches-readback-v1357.json`.

## Completed natural Lunatic and density observations (v1359)

The same v1358 GNU Reimu A job is now terminal, with independent full trace,
physical snapshot and separate Scores-restart readback. Rank3/character0/shot0
is observed in every MAIN row, with credit0/program1/generation2 and no Game
Over. All six stages complete; final MAIN Stage5 frame13,633 has lives2/misses11
and score5,179,856. MAINE/registration Esc/physical atomic rename/fresh OP and a
separate Scores reader pass. Section3 stores real clear1 at rename and final
file; nine others retain decoded2..195 and CFG stays raw-equal. Unplayed0x19
never qualifies. Generic trace does not directly label every inner Ending phase.

Route has88,927 complete refreshes and restart790; audio opens/failures remain0.
The observer visited88,206 distinct route refreshes; this controller polling
count is not the complete trace denominator. Historical terminal stdout says
“FULL NORMAL” because of a legacy label; raw rank3/receipt determines Lunatic.

| Natural MAIN density | Refreshes | Update P95 / P99 | Presentation P95 / P99 | Lateness P99 |
| --- | ---: | --- | --- | --- |
| >=320 | 700 | 5.12 / 9.54ms | 12.12 / 13.11ms | 19.15ms |
| >=400 | 369 | 5.07 / 11.04ms | 12.19 / 13.15ms | 23.49ms |

Maximum observed count is440; each category contains one update over17.73ms
(max19.89ms). Complete route has3,245 MAIN after-update slowdown2 records,
but none belong to these dense categories: legal starting CFG enables Turbo.
Dense slowdown2 stays a separate required experiment. Presentation counts735/388
can exceed refreshes700/369 because updated scene invalidations may present
more than once for a refresh. Preserve the full event association, not an FPS
inference. Advice/trace cost is outside measured update, while whole-loop lag
includes observer work and shared host lateness. Short private storage checks
ran on another Xvfb during this route. These are instrumented WSL/private-display
observations, not physical host or uninstrumented performance acceptance.

The first independent reader used singular `credit` instead of trace `credits`
and rejected with KeyError before outcome checks. Its frozen source is retained;
v2 validates the actual field and every physical/route/restart claim above.
No game/controller source changed; both complete terminal traces remain intact.

Actual route: `.analysis/port64/lunatic-window-v1358/gnu-lunatic-reimu-a-v1/`.
Independent verdict: `.analysis/port64/host-storage-v1359/gnu-lunatic-independent-readback-v2.json`.
The original485 compiled inputs remain frozen; current490 consumer source is
archived/read back separately. All owned Xvfb/game/controller jobs are terminal.
No Windows GUI, foreground activation, host keys or audio devices opened.

## Natural Turbo0 slowdown gate (v1360)

The v1359 complete GNU Lunatic route enabled Turbo1. Every >=320/>=400 sample
therefore had after-update slowdown1. That acceptance does not establish natural
dense slowdown2. Native `enemy_bullets.cpp` requests2 only with Turbo disabled,
processed bullet count >=24+performance+rank*8, and frame_mod2==0; the host
scheduler uses the after-update value for the next deadline. Counts in generic
window snapshots are post-update and do not independently recover the internal
processed `seen`/performance threshold. Do not infer the exact predicate from
post-update bullet count alone.

`verify_window_route.py --turbo 0` creates a legal physical CFG with checksum
rank+11 rather than rank+12; default1 is unchanged. `--require-dense-slowdown`
requires adaptive rank3/Turbo0 and, after the existing true-clear/file/rename
checks, a complete schedule plus nonempty slowdown2 samples in both >=320 and
>=400 natural categories. Separate physical Scores restart still follows.
The non-Turbo watchdog allows3600 seconds to accommodate intended delays.
Four wrong rank/Turbo/fixed-mode/invalid-bool CLI controls reject before opening
any display/game or save directory. Terminal stdout now names actual rank/Turbo;
old immutable logs retain their historical NORMAL label.

One ordinary private-XTest ReimuA candidate runs on unchanged v1356 GNU
executable dbe17225. Initial CFG0306020201000000000E has Turbo0, all launches are
muted, and no state/clock/actor/score writes or reference-route dependency are
introduced. Early Stage0 frame4,983 has35 slowdown2 records but only100 bullets;
this is a live prefix, not a complete route/dense verdict. Tool17095 and
controller404173/game404187 start ticks/argv are recorded and checked. Do not
edit pinned route/input/reducer helpers or restart on observation timeout.

Full490-input source/member readback a07fda7a changes only this Python route
consumer from v1359. Every C++/header/CMake input remains the old485-input
compiled producer00af24f7; no new build/Windows/physical device work. Current
launch/CLI controls/active-job/source vectors are under
`.analysis/port64/slowdown-window-v1360/`; terminal result remains pending.

Both final CIs pass; root includes live Ghidra and mutation replay. Source/CLI/
immutable-prefix independent readbacks pass. Source-backed public caches retire
955 files/net15,478,784 allocated B; active port64 helpers/outputs stay excluded.
See root `.analysis/cleanup/slowdown-source-caches-readback-v1360.json`.

## Independent natural outcome/slowdown reader (v1361)

`verify_natural_slowdown.py` is read-only: it opens no window/device and never
changes route inputs. It checks the supplied executable hash and original HDI/
font, the declared legal6-life/2-Bomb Lunatic CFG and Turbo, complete schedule,
every MAIN rank/character/shot/process/generation/credit, six actual stages,
observed registration Esc, Ending/freshOP, true requested-shot clear at physical
rename/final file, nineother decoded payload/checksums, no temporary save files,
and a separate fresh Scores process with unchanged physical hashes.

Default Turbo0 additionally requires nonempty>=320/>=400 natural MAIN samples
with after-update slowdown2. `--expected-turbo 1` is explicitly route-only and
returns `dense_slowdown_accepted=false`; the completed v1359 GNU Lunatic route
passes that control. No screen, controller PASS text or bit-only flag can replace
these checks. This is still instrumented/private-display observation, not
original whole-route or uninstrumented/physical performance acceptance.

Eight negative cases reject at intended gates: actual live/incomplete route,
actual Turbo1 requested as0, declared metadata/physical CFG0 but original dense
trace has no2, checksum-valid wrong-shot flag2, physical snapshots with unplayed
0x19 despite final1, a one-nanosecond wrong deadline with updated trace hash, and leaked pending
file/directory artifacts. The final reader requires exactly MIKO.CFG/GENSOU.SCR;
matching declared hashes cannot legitimize an extra temporary file.
The declared CFG and score mutants are comparator fixtures, not gameplay.
All original source files/traces/saves retain hashes. Trace hardlinks are never
written; the deadline mutant unlinks its own path before writing. Every scratch
clone retires after its verdict/hash. No extra game or Windows process launches.

```sh
python3 port64/verify_natural_slowdown.py COMPLETED_TURBO0_ROUTE \
  --exe-sha256 PINNED_SHA --output FRESH_VERDICT.json
# Historical Turbo1 positive accepts route only:
python3 port64/verify_natural_slowdown.py COMPLETED_TURBO1_ROUTE \
  --expected-turbo 1 --exe-sha256 PINNED_SHA --output FRESH_CONTROL.json
```

Native `.analysis/port64/slowdown-consumer-v1361/` retains positive/counterexample
receipts and frozen491-input consumer437d7e36. Only this Python reader/filelist
changes from v1360; all485 compiled inputs/programs stay unchanged. Existing
Turbo0 route490/a07fda7a remains on the same live17095/404173/404187 with every
pinned helper unchanged. Stage3 live prefix max306/4,812slowdown2 is below both
density gates; no complete Turbo0 verdict yet. Do not restart from timeout.

Both final CIs pass (root includes live Ghidra/mutation replay). Final v2 reader
source/positive/eight-control receipts supersede initial v1 snapshots while those
remain retained. Public caches retire955 files/net15,478,784 allocated B after
source/protected hash readback; active port64 helpers/outputs stay excluded.

## Turbo0 terminal rejection and separate bad-save reader (v1361)

The v1360 GNU Turbo0/ReimuA candidate is terminal and failed the true-clear
gate. Complete trace has88,267 refreshes: six stages reached, Final Stage last
frame11,267/miss13/respawn33/invincibility154 immediately enters MAINE; all physical
masks remain0x19. No all-clear/complete dense-route acceptance. Inner Bad Ending
is source-routed/inferred. Separate new private Scores reader passes795 refreshes
with unchanged physical hashes/zeroaudio; the original failed controller never
started its own reader. All owned jobs are now terminal.

Within this failed candidate, natural>=320 has416 samples/206 slowdown2 and
>=400 has125/63. Complete deadline/terminal reduction passes; >=400 update
P95/P99=8.33/12.27ms, no update exceeds its own admission period. These strengthen
bounded slowdown observations, not successful-route or uninstrumented/physical
performance acceptance. Before another Turbo0 attempt, review ordinary Bomb
input policy: fatal snapshot still has1 Bomb and advice0x20. This is a candidate
policy gap, not a proved game defect. Windows GUI/host keys/audio remain disabled.

Actual immutable failed candidate remains under `.analysis/port64/slowdown-window-v1360/gnu-lunatic-reimu-a-turbo0-v1/`. Independent failure and separately completed Scores/clock receipts are under `.analysis/port64/slowdown-consumer-v1361/`. Earlier live/active-job/prefix records remain dated observations, not current running status. No controller/helper/compiled source changes accompany this result.
