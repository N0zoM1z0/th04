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
- v1354 fixes SDL keypad Enter held input and resync losing slowdown. GNU8,
  optimized UBSan and actual Windows pass 67 contracts each; 204 programs build
  cold from 480 producer inputs. Preceding 104 GNU/MinGW core objects are raw-equal;
  GNU/UBSan retain all 195 fake-audio frontend files against v1353.
- Actual SDL/X11 window trials pass on GNU/UBSan under private Xvfb: ordinary
  Marisa B/Lunatic entry, Enter/keypad Enter, movement/Shift, shots/release and
  focus gating. Windows foreground acquisition fails before any injected key;
  Windows real input is not accepted by its passing headless contracts.

Cold producer:
`e2974686f86f22d2a2a7caaf736b664dd33aac3eae4703aeefbf93a7e9e6ac75`.
Final verifier recipe:
`04ec21c37c2039c549b4130b8432693940c9bf53109e1765174204f8dfe4c4c7`.
Only two host verifier scripts changed; all compiled inputs are identical.
Keep producer and consumer identities separate. Focused native evidence lives
in `docs/port64/evidence/{host-window,stage-lifecycle,op-startup,pmd-musical-fm,audio-output}.md`;
private current receipts: `.analysis/port64/host-window-v1354/` in that worktree.

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

Periodic cleanup keeps inputs, tools, source/program vectors, physical saves and
failures. This batch retires 1,190 regenerable build files and 225 terminal
owned Windows-stage files after three full recovery archives/299 members are
read back, reporting 628,129,792 allocated bytes net reclaimed. A separate
pre-build pass prunes 12 source-backed Python caches (278,528 allocated bytes).
Immutable capture sharing retains 324 BMP/PCM paths/hashes and reclaims
210,509,824 allocated bytes net after its journal. Post-CI cache pruning retires
957 source-backed files with 15,585,280 allocated bytes net after its journal.
Receipt overhead is excluded. Both final CIs pass, including root live Ghidra
replay/mutations. Follow [retention](ANALYSIS_RETENTION.md); never blanket-delete `.analysis/`.

Detailed historical batch evidence remains in ledgers, subject notes and Git.
Use [handoff](RE_HANDOFF.md), [semantic contracts](SEMANTIC_READABILITY.md) and
`python3 scripts/status.py` for current authority instead of old progress labels.
