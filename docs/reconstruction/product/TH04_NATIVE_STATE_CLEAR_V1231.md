# Native state clear and the playfield corner pellet

## Confirmed initialization defect

The 2026-10-03 Windows screenshots show a small white/blue-purple mark at the
playfield's upper-left corner. The supplied original and reconstruction images
have different sizes and gameplay states, so they cannot establish whole-screen
equality. An independent ordinary Reimu/Normal Linux replay reproduces the
native mark at playfield coordinate (32,16) at seconds 70 through 110, while
the pinned original has none at all seven recorded checkpoints. The native mark
also disappears by second 120 without a bomb. This excludes a necessary bomb
dependency; it does not prove identical world state between the two runs.

The unmodified normal MAIN is 192,351 bytes, SHA-256
`1b10fdef0df1597b5c340752d500ac2135489680c1df16eed447d80eeb29a385`.
Both scenarios use GAME.BAT, the same original-data image, rank 1, six lives,
two bombs, identical timed inputs, built-in DOS, and the pinned Linux DOSBox-X
SDL2 binary at 24,000 cycles. Complete preparation, input, emulator, font and
frame identities live under:

```text
.analysis/runtime/candidates/top-corner-{native,original}-20261003/{prepared,run}/receipt.json
.analysis/render-corner-20261003/visual-comparison.json
```

Read-only hardware watchpoints identify the native write chain at load segment
1100h (DGROUP 337Fh):

1. `CLEAR_DWORDS`, relative MAIN_01 0708:1178, executes REP STOSD at guest
   1808:1187 with EAX=000E0000, CX=0B2C and DI=4572. Its complete loaded
   22-byte body matches the attested native executable.
2. Before the first bullet update, the complete 11,440-byte bullet array is
   repeated dwords 000E0000. With the 26-byte bullet stride, 220 flags are zero
   and 220 are 14. The update skips F_FREE and F_REMOVE; other values enter
   the active update path. Of these entries, 120 lie in the pellet partition.
3. At stage frame zero, the first 120 render-list entries are all (28,12), and
   `pellets_render_count` is 120. The pellet top renderer writes the corner
   at guest 251F:3183, relative MAIN_03 141F:3183. The border leaves the
   bottom-right quarter of this overlapping pellet visible at (32,16).

The target and native pellet sprite data are identical. This is an
initialization defect that produces repeated invalid draws, rather than a
corrupt sprite asset. The wider nine-block initialization uses the same clear
helper; effects on other entities need separate runtime controls.

Private watch receipts and snapshots:

```text
.analysis/runtime/candidates/top-corner-native-20261003/run-watch/
.analysis/runtime/candidates/top-corner-native-20261003/run-state-clear-ready/
.analysis/render-corner-20261003/writer-evidence.json
```

The first interrupt-conditioned debugger attempt never reached usable MAIN
state and is rejected. The first state watch failed to decode a DWARF array
field and is also rejected. The successful watches use the unchanged pinned
emulator with separately hashed diagnostic scripts; they do not inherit the
fault observer's calibration or establish frame pacing.

## Independent CPU control and proposed native repair

The pinned target's CIRCLE_TEXT 0AAF:185E helper also uses XOR AX,AX followed
by REP STOSD. It clears only the low half of EAX. A 54-case independent Unicorn
control executes complete target/native helper calls with all nine actual
clear counts and upper EAX seeds 0000, 000E and DEAD. Both pre-repair bodies
are byte-identical and fill every dword with the retained upper half. Stack
cleanup, preserved DI and both memory guards pass. A native-zero assertion
fails on the current build, providing the repair's rejecting baseline.

```text
python3 scripts/probes/probe_th04_native_clear_dwords.py --build-dir .analysis/build/th04-normal --output-dir .analysis/reconstruction/probes/clear-dwords-v1231-before
```

The repaired helper uses XOR EAX,EAX under `TH04_LARGE_PRODUCT`; the historical
branch retains XOR AX,AX. All 54 complete-call controls pass with
`--expect-native-zero`. Two cold default objects preserve their full
link-relevant OMF records and all 22 accepted target bytes with zero raw
differences. These are regression controls, without new exact promotion.

The repaired ordinary Normal replay has no old corner mark at any of the seven
70..140-second checkpoints. Four installed executable identities, input success
and absence of early exit are checked separately from the screenshots. Receipts:

```text
.analysis/reconstruction/probes/clear-dwords-v1233-final/receipt.json
.analysis/reconstruction/probes/clear-dwords-default-v1232/target-raw-control.json
.analysis/runtime/candidates/planar-v1233-normal/run/corner-control.json
```

## Yuuka follow-up

The user separately reports that the Stage 6 top stripe is now absent. Image
10 shows the late chase-cross attack and reports slower movement only during
that attack. The target helper MAIN_034_TEXT 13A9:779B, file 1CA2B + 0057,
spawns two custom crosses every eight stage frames after attack frame 48;
its direct stores affect boss sprite/frame/mode only. The maintained attack
and custom update/render code contain no deliberate player-speed reduction
or special half-speed setting. Player movement can be halved by Shift, and
the generic bullet-count slowdown remains a distinct policy when Turbo is off.
Turbo is one in the recorded native ordinary replay; this does not attest
the user's later Stage 6 state.

Rendering load is a plausible explanation for the user's transient slowdown,
but no timed Stage 6 trace or controlled original/native comparison has yet
distinguished missed frames, Shift input or generic slowdown in that session.
Do not accept the screenshot alone as proof of intended slowdown or performance.
