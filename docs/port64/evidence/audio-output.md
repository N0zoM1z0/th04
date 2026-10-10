# Native host audio transport

v1353 owns the last step from CPU PCM to a host device. It does not recover
new DOS semantics. The original-game/control/PCM corpora retain their earlier
producer identities; physical speaker output is outside this verification.
Every game/check replay stays muted. Deliberate unmuted diagnostics reject
before entry; no audio backend/device is opened.

## Ownership and policy

`audio_output` owns one lazy device for the application, spanning sound scene
changes. With resident PMD, `FrontEnd` submits only the final stereo callback;
its mono observer describes beeper before mixing and must not be submitted
again. Without resident PMD, mono is duplicated into both channels. Existing
observers remain independent. Repaint never submits PCM or advances its clock.

The host format is 48,000 frames/s, two signed16 channels. A 9,600-frame queue
cap is a host policy, not an inferred original hardware timing rule. Full/busy
queues drop new output blocks; they never change PMD, SE or game time. Empty
blocks do not open a device. A failed open/query/write closes/disables output
and reports once; reporting failure cannot stop gameplay. Statistics count
generated, submitted, suppressed and dropped frames, not physically played
frames. Application exit clears pending output rather than delaying exit.

Linux uses a non-callback SDL queue. The API counts bytes and copies the
buffer; it has no built-in queue cap, so admission is owned here.
[SDL queue contract](https://wiki.libsdl.org/SDL2/SDL_QueueAudio).
Windows prepares eight stable 2,048-frame buffers, copies submitted PCM into
them, and returns ownership only on the completion callback. Reset/unprepare/
close precede memory release. A driver refusing cleanup leaves its bounded
header/sample/callback allocation quarantined until process exit.
[WinMM reset contract](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/nf-mmeapi-waveoutreset).

Default output is muted. Interactive `--title --audio` opts in; `--mute` wins
in either argument order. Unmuted diagnostics reject before assets, saves or
backend entry. Verification never exercises a physical device, even a dummy
audio backend. API tables used by tests have no implicit native defaults.

## Replay and result

Current 475-input source manifest:
`95ce37f3cfd2a17ec3547e38f5aae71226b2616623e0a79b6cada1772f66ec36`.
Independent compiled materialization:
`../port64-audio-v1353-fix/.analysis/product-v1353/`, with source archive,
compiler/CMake/link inputs, 201 AMD64 programs and 66 contracts per host.

```sh
cmake -S port64 -B .analysis/audio-checks -DCMAKE_BUILD_TYPE=Release
cmake --build .analysis/audio-checks -j2
ctest --test-dir .analysis/audio-checks --output-on-failure
python3 port64/verify_audio_output.py --help
```

`audio-output-contracts` checks mute/lazy factory admission, stereo identity,
real beeper mono PCM, capacity/busy handling, failure cleanup and accounting.
`audio-device-contracts` compiles the production backend against exclusively
fake API tables and checks format, byte/frame units, buffer completion/reuse,
partial initialization/write failure and teardown. The Windows refused-cleanup
case invokes a completion after owner destruction to check retained context.

Maintained `--resident-sound-checks` runs the real frontend with explicit fake
transport factories. All 27 settings across three profiles pass on GNU8,
optimized UBSan and actual Windows. All 195 prior capture/save files per host
equal the preceding GNU producer. Extra checks cover muted factory admission,
nonresident mono, repaint and one device over OP/MAIN plus a separately declared
registration MAINE/fresh-OP child. No natural MAINE route is inferred from this
child. Two ordinary Continue regressions preserve all 16 capture files and
physical final saves per host; the earlier intermediate-write observations
and original component Oracles keep their own v1352 identity.

Three wrong output variants (mute, mono channels, queue cap) reject. Four GNU/
UBSan unmuted diagnostic controls reject before output creation. Windows passes
all 66 contracts and five explicitly muted frontend launches. All preceding
103 core objects are raw-equal on GNU/MinGW; the new transport is a 104th core
object. UBSan path-bearing debug objects are excluded from byte equality.

Private replay recipes, whole receipts, negative results and recovery are under
`.analysis/port64/audio-output-v1353/`. The first MinGW fake test used an absent
`WAVEOUTPROC` typedef and failed compilation; its frozen source/log remain.
The first Windows plan incorrectly pinned a mutable ranked save as immutable:
all comparisons passed before final input readback rejected it. Fresh v3 pins
immutable initial snapshots and separately validates writable save finals.
Neither failed aggregate is relabeled accepted.

Remaining: physical device output/latency, input/refresh/slowdown, dense Lunatic
performance, full startup across sound modes and current GUI delivery. This
batch does not promote whole-game, original-waveform, DOS exactness or target
canonicality claims.
