# Host window admission and input

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
