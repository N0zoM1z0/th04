# TH04 native branch handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

Updated 2026-10-10. Current phase: muted startup and complete ordinary window-route
validation under private Xvfb. Full native goal stays active; historical DOS acceptance
remains separate. General semantic work resumes only for a concrete blocker.

## Native x64 frontier

v1356 adds private-Xvfb-only startup/Normal route verifiers and opt-in
read-only live key advice in trace v3. Original window input still comes
only from OS keys. GNU/UBSan v1355 products pass all 27 driver/BGM/SE
startup combinations each (32,147 total refreshes), zero audio opens,
and unchanged physical CFG. The Windows batch retains 19 completed
cases, not full matrix acceptance; no further host GUI runs are allowed.
Independent four-axis OS controls prove 1=Up, 2=Down, 4=Left, 8=Right.
Two earlier candidate scripts used the wrong map. Corrected fixed and
reference-position candidates also reach Game Over; all failures remain
failed. Live-state ordinary-key full Normal validation is now in progress
under private Xvfb and is not accepted until its physical save/restart
checks close. Current receipts: native `.analysis/port64/full-window-v1356/`.
Specific live private-Xvfb controller/game handles are recorded in
`active-window-job-v5.json`; re-poll them before deciding completion or restart.

Cold v1356 products retain 485 inputs (`00af24f7…`) and 204 program
identities. GNU/UBSan pass 67 contracts each plus manual held-input
regressions with advice disabled. Windows is cross-compiled only; its
new execution remains unverified. 104/105 GNU/MinGW core objects equal
v1355; only trace serialization changes. Both control-plane CIs pass
(root includes live Ghidra replay/mutations). Historical acceptance
and target provenance are unchanged.

The extracted policy preserves the complete 88,934-tick logical Normal
Reimu A input/state/startup/menu/Ending streams and physical saves.
This does not accept the pending window route or uninstrumented timing.

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

Remaining: actual Windows input, full startup across sound modes, complete
rank/shot/Normal/Extra/Ending/Continue window routes, physical refresh/slowdown2
and dense Lunatic performance. Physical audio stays untested under the user's
mute instruction. Existing v1354 experimental package remains available; no new
package publication or user save modification was needed for this observer.

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
Post-CI pruning retires 1020 source-backed Python caches, net 16822272 allocated
bytes; root `.analysis/cleanup/host-route-post-ci-caches-v1355.json` records
source/hash readback. Both CIs pass, including root live Ghidra replay/mutations.

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
