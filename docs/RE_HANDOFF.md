# TH04 native branch handoff

Updated 2026-10-10. Current phase: host scheduling/input validation and current
experimental muted GUI delivery. The full native goal stays active; DOS exact
acceptance remains separate. General semantic work resumes only for a concrete
port blocker. Both final CIs pass, including root live Ghidra replay/mutations.

## Native x64 frontier

v1354 fixes SDL keypad Enter held input and catchup resync losing slowdown.
GNU8, optimized UBSan and actual Windows pass 67 contracts each; 204 AMD64
programs build cold from 480 producer inputs. Preceding 104 GNU/MinGW core
objects remain raw-equal; GNU/UBSan's 195 fake-audio frontend files equal v1353.

GNU8/UBSan real SDL/X11 callbacks under private Xvfb pass ordinary Marisa B
entry, Return/keypad Enter, movement/Shift, shots/release and focus gating.
Normal/Shift movement is 64/32 Q12.4 units per frame. Both traces record zero
audio-device opens. Windows foreground acquisition rejects before sending
keys; passing Windows contracts do not accept Windows held-input behavior.

Producer manifest: `e2974686f86f22d2a2a7caaf736b664dd33aac3eae4703aeefbf93a7e9e6ac75`.
Final verifier: `04ec21c37c2039c549b4130b8432693940c9bf53109e1765174204f8dfe4c4c7`.
Only two verifier scripts differ; every compiled input is raw-identical.
Producer receipts and corrected consumer archives retain distinct identities.
Native replay/limits: `docs/port64/evidence/host-window.md`; private current
receipts: `.analysis/port64/host-window-v1354/` in the native worktree.

Earlier scopes remain: four complete A logical routes/Normal-earned Extra,
bounded real Continue/physical host saves/fresh OP, ten-section registration,
Extra/HUD/Scores/Music Room/demo/configuration, supplied PMD music and production
SDL/WinMM transport tested through explicit fake APIs. These do not establish
an original whole route, physical audio, or host timing. No backend/device opens.

Remaining: actual Windows input, startup across sound modes, other rank/shot/
Continue routes, physical refresh/slowdown2, dense Lunatic performance and
physical audio output. The full native goal stays active. A new experimental
muted GUI is delivered in `native-port64-v1354/` under the private demo folder;
all 21 preceding files/saves are unchanged. It is not final GUI acceptance.

Scoped cleanup retires 1,190 build intermediates and 225 terminal owned stage
files after three full archives/299 members read back, reporting 628,129,792
allocated bytes net reclaimed. Current programs/source vectors/captures,
failures, inputs and saves remain. Additional immutable capture sharing keeps
324 paths/hashes and reclaims 210,509,824 allocated bytes net. Post-CI cache
pruning retires 957 files with 15,585,280 allocated bytes net. Both subtract
their journals; final receipt overhead is excluded.

## Finish and replay

```sh
python3 scripts/preflight.py
ctest --test-dir ../port64-window-v1354/.analysis/product-v1354/linux --output-on-failure
python3 scripts/ci.py
git diff --check
```

See [current native status](PORT64.md), [host replay](port64/evidence/host-window.md)
and [retention](ANALYSIS_RETENTION.md). Private receipts retain exact commands,
source/compiler/product identities, failed attempts and whole recovery hashes.
One Borland/Wine writer at a time; no concurrent shared output. All launches
remain muted. Never open an audio backend/device during these validations.
