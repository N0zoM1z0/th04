# Semantic and x64 port status

Current Windows audio: repeated FM attacks restored, independently calibrated parts and bandlimited output; see [fidelity evidence](reconstruction/product/TH04_PORTABLE_AUDIO_FIDELITY.md). PMD86 BAT profile and coalesced WinMM buffers remain in use.

Keep the host workspace undisturbed. Authorized Windows tests use inactive
private desktops, process-local hooks and explicit mute; do not switch the
active desktop or send global keyboard input.

## Current handoff (2026-10-27)

Latest: [Ending/registration and seamless invincibility](reconstruction/product/TH04_PORTABLE_UI_AND_INVINCIBILITY.md) optimizes glyph rows and page conversion, verifies real save flow, and suppresses hits before both death-entry latches. Both BATs enable audio.

Current portable update fixes the retained Extra boss delay, batches rendering and improves Windows pacing; both D-drive BAT launchers enable audio. See [runtime evidence](reconstruction/product/TH04_PORTABLE_RENDER_PERFORMANCE.md). The earlier functional batch below retains its historical build identity.

Windows x64 functional smoke now passes a real hooked window plus complete
Normal Reimu A, Normal Marisa B and same-session earned Extra Reimu A logical
routes under a memory-only no-life-loss patch. Ordinary death/Continue, pause,
configuration and physical score flows have separate checks. Overall game flow
is the current acceptance target; original DOS pixel/timing parity is supporting
work, and further UBSan testing is deferred by the user. No game code was
rebuilt or changed in that earlier batch. Physical input/audio and continuous visual quality remain
for manual review. See [current handoff](RE_HANDOFF.md) and
[functional test scope](reconstruction/product/TH04_WINDOWS_FUNCTIONAL_SMOKE.md).

## Remaining work

Validate physical input/audio and continuous rendering where a real discrepancy
is reported. Original DOS timing, common boot epoch, other IRQ producers and
NP2/hardware agreement remain open. Native host agreement or logical clears do
not establish original timing parity.

[The comparison note](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md) retains
bounded results and useful failed approaches. Exact state is maintained in the
CSV ledgers; old build/capture cohorts need not remain on disk. Rebuild affected
targets from source in fresh output and compare complete owned extents and
relocations when exact source changes.
