# OP Music Room native scene and menu join

v1321, 2026-10-09. This is a bounded original-instruction, drawing and native
frontend result. Physical audio/timing, a complete OP loop, natural game routes
and current Windows execution remain unaccepted. Every launch stays muted.

## Target and recovered contracts

The Japanese OP container is 42290 bytes, SHA-256
`8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f`.
Its attested stub-restored payload is 69028 bytes, SHA-256
`13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`,
with804 ordered relocations. The packed Ghidra database is re-attested; it is
not a decoded-function Oracle. Canonicality remains candidate-local-attested.

Original relative0A74:1795..1E39 executes track rendering, comments, polygon
construction/update, page flips and the complete child caller at loads1000/2000.
Polar0DA1:01A8..01C3, LCG0000:204E..2077 and blackout0000:0666..06A2
also execute.32 independent cases compare complete ordered requests, local RNG
state/draw count, all16 polygons, selected/playing/page flags and800 comment
bytes. GNU and optimized UBSan consume the independent original reference.

Entry renders24 rows at x16/y8+track16. It performs one animated comment
refresh, then applies tone100 immediately. Held input at entry must be released
before controls. UP and DOWN are separate tests on one sample; blank row22 is
skipped. Held controls do not repeat, but release waits keep updating polygons.
PLAY fades32, changes the playing track, performs ten comment-animation
refreshes, loads that song and plays; CANCEL still tests the retained sample
after those waits. Exit waits for release, fades16, releases the saved B plane,
shows/accesses page0, blacks out over18 refreshes, frees background and restores
OP music. These are emitted requests; no sound device/backend is opened.

Initialization consumes96 LCG draws in X/Y/Vx/Vy/angle/angular-speed order.
The16 polygons and initialized/playing state survive visits within one OP
process; fresh OP resets them. Radius is64/80/96/112, with3/4/5/6 vertices.
Vertices are built before movement, bounce or five-draw respawn. Centers and
velocities preserve WORD wrap, Y uses arithmetic Q12.4 shift, and angles wrap
as BYTE. A private source-only X/Y draw-order mutation is rejected at trace
line133. All22 native song-name literals agree with the original relocated
far-pointer table at DATA0F34:0F16; this is a data observation, not playback.

## Drawing controls

Original convex polygon0000:0DC2..0FD9, linework1D76..1DAA and
trapezoid3264..3335 execute at both loads.171 cases agree on complete256000-byte
indexed pages with dirty non-B planes. Coverage includes screen clipping,
flat tops across array wrap, opposite vertex order and negative intersections.
The native renderer preserves per-edge half-unit rounding, integer clipping
before DDA setup, rounding reset at each vertex, inclusive bottom scanline and
the original one-write zero-height transition. A pixel-center fill differs.
The complete0DC2 extent is larger than the provisional small library body;
this does not promote historical library ownership or exactness.

Original graphics-string/font helpers0DA1:04A4..05FD execute for the supplied
CGROM. OP font mask words at DATA0F34:0A1C and MAINE DATA0E53:05DC are
independently observed equal; the third font mask differs from the text-box
wipe mask. The shared native Canvas now supports effects0..7. Five scenarios
compare395 complete two-page/palette/shown-page RGB displays:505618960 bytes,
including comment effects4..7, page flips, blue-plane restoration and blackouts.
GNU and optimized UBSan agree with the independent original-kernel reference.
Each stream is compressed with full decompressed SHA-256 readback before raw
retirement. The earlier producer and current consumer manifests remain separate.

Full-screen clipping/GRCG write shadows, CGROM/asset staging, PI decoding,
background/blue storage, page policy and RGB composition are explicit adapters.
They do not establish physical PC-98 VRAM timing or hardware playback.

## Real menu and retained OP

Six actual options/menu scenarios each enter twice, yielding12 visits per Linux
host. The original child caller at two loads agrees with the frontend trace;
188 sampled BMPs agree with original drawing kernels. Current GNU/UBSan outputs
agree on242 files/200 BMPs. Repaint leaves pixels, polygons and RNG unchanged.
The parent resident seed waits for the child, then increments once. Configured
difficulty and physical score bytes survive both visits, and ordinary MAIN
starts from the returned Game selection.

The original parent suffix0A74:087A..0905 independently observes main_cdg_load,
page1, OP1 load/palette/put/free, copy0 and tone100, then clears initialization/
option flags and selects Game. The native frontend rebuilds active menu CDG/PI
owners from immutable decoded archive inputs in that return path. It retains
the Music Room process state; it does not recreate OP or rerun its score reader.
This resource-cache adaptation is not DOS allocation/topology acceptance.

The first suffix probe supplied a function-entry stack despite starting after
PUSH BP/MOV BP,SP/PUSH SI; its return was rejected. The corrected live frame
and both observations are retained. Two regression commands also selected the
scene executable instead of the renderer, and an obsolete ranking receipt
directory; both failed closed before comparison. Corrected commands pass.

Shared Canvas registration rendering regresses against158 independent original
full displays per Linux host. The existing12 ranking/menu/MAIN routes also
regress per host. All three builds produce43 AMD64 products each;42 CTests
pass per Linux host.346 current source files are bound in the private profile.

The completed v1321 capture cleanup reclaims1207685120 allocated bytes
(about1.12GiB) after complete byte/hash comparisons, with5578 protected
files unchanged. Raw capture compression separately reclaims1487245312
allocated bytes after full decompressed SHA-256 readback. Completed capture
hardlinks are immutable; replays require fresh output directories.

## Replay and remaining work

Use fresh output directories; completed captures and their hardlinks are
immutable. Original inputs/assets stay private. Replay the child with:

```sh
python3 port64/verify_op_music.py --target ../../targets/th04/op.exe \
  --decoded-dir ../../port64/op-unlock-v1317/decoded-original \
  --hdi ../../runtime/images/zun.hdi \
  --exe .analysis/port64/linux-live-v1251/th04-port64-op-music-contracts \
  --output-dir NEW
```

`verify_op_music_pixels.py --geometry` guards the polygon kernel;
its ordinary mode guards complete displays. `verify_op_music_join.py` guards
real options/menu/revisit/MAIN entry and the parent suffix. Both use the pinned
HDI/font and preceding caller/pixel references. Private receipts, failures and
complete uncommitted source recovery live under `.analysis/port64/op-music-v1321/`.

Next: demo, audio/config persistence, full natural ordinary/Extra routes,
save/restart, dense Lunatic timing/performance and actual current Windows.
Windows interop still rejects before PowerShell; read-only Git metadata blocks
commit/push. DOS ledgers and historical exact acceptance are unchanged.
