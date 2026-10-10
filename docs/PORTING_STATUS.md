# Semantic and x64 port status

Updated 2026-10-10. The full native goal remains active on `port/modern-64`, in
`.analysis/worktrees/port-modern-64/`. Root `main` keeps the standalone DOS
product and indexes native findings. A root `git push` does not commit or push
native worktree changes.

## Current products and acceptance

| Product | Accepted scope | Remaining boundary |
| --- | --- | --- |
| Historical reconstruction | OP 93/93, MAIN 493/495, MAINE 72/72, ZUN 3/3 authored functions | Function acceptance is not whole-file exactness; MAIN carpet/checkerboard deferred |
| Standalone PC-98 DOS | Four local-source products, repaired normal/invincible packages; user reports complete Normal routes/save | Automated natural dense Lunatic, timing/audio and second-emulator coverage remain separate |
| Semantic readable | Assets, heap, input/timing, scroll, bullets/VM/shots/items, RNG, score and process contracts clarified | Resume only for a concrete native blocker; old exact replay failures remain failed |
| Native x64 | Typed Linux/Windows gameplay, renderer, asset, lifecycle, persistence and sound owners with scoped Oracles | Full physical host/game-route acceptance remains open |

Target files pass local identity/format checks but remain
`candidate-local-attested`; external pristine-dump provenance is unresolved.
No native observation promotes a historical exact unit.

## Native progress

- Registration waits/fades/held keys/render, ten-section score storage,
  failures and fresh OP are integrated under independent bounded controls.
- Bomb/hit/death/lives/Game Over/HUD and real Continue are integrated. Two
  ordinary Lunatic pilot1 scenarios per host traverse genuine deaths,
  Continue/resume/second Game Over/Esc, registration and fresh OP; selected
  ranked/unranked physical files are distinguished.
- Stages 1–6, Ending/Staff/Verdict, Extra, Scores, Music Room, demo, unlocks and
  configuration are implemented with component/integration evidence. Four
  ordinary A logical routes pass on three hosts; Normal-earned host saves admit
  fresh Extra. GNU has a complete Hard/Reimu B route; broader combinations remain.
- Complete supplied PMD/PMD86/PMDB2 music closes its recorded original-component
  corpus. CPU waveform comparisons share a pinned chip engine. SDL/WinMM output
  is implemented with a bounded queue and explicit fake API verification.
  Every launch remains muted; no physical audio device was opened.

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

## TODO, in order

1. Establish actual Windows owned-window input validation; finish host refresh,
   focus and deliberate slowdown2 checks. Linux's bounded virtual-display input
   trial does not establish human keyboard, physical display or complete timing.
2. Verify complete startup integration across sound modes while staying muted.
   Device transport is implemented; physical output/latency is still unverified.
3. Expand full routes across characters, shots, ranks, good/bad endings, Extra
   and Continue; verify actual host save/config/restart behavior. Native logical
   consistency and original component comparisons are different claims.
4. Benchmark natural dense Lunatic scenes with explicit timing/adaptation
   boundaries; include CPU update/render, presentation and resync behavior.
5. Accept the final GUI against those gates. The current experimental delivery
   is reviewable, but delivery alone does not close gameplay/timing acceptance.

General semantic work and the two deferred MAIN exactness cases are not a
parallel prerequisite queue. Arbitrary external sample banks remain outside
supplied-stock music acceptance.

## Delivery and storage

A fresh experimental current GUI is installed at
`/mnt/d/Entertainment/Game/Touhou/th04-reconstruct/native-port64-v1354/`.
`start-muted.bat` and `start-linux-muted.sh` explicitly mute; independent host
saves and Normal/3-life/2-Bomb defaults preserve all 21 preceding DOS/package
files. Source archives/profiles accompany the binaries. Windows input automation
remains rejected; physical audio, dense timing and full-goal acceptance remain.

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

Follow [retention](ANALYSIS_RETENTION.md); never blanket-delete `.analysis/`.

Detailed historical batch evidence remains in ledgers, subject notes and Git.
Use [handoff](RE_HANDOFF.md), [semantic contracts](SEMANTIC_READABILITY.md) and
`python3 scripts/status.py` for current authority instead of old progress labels.
