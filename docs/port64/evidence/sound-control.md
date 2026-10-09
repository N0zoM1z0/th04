# Sound control seam

v1325, 2026-10-09. `sound_control.cpp` now maintains the resident-probe/mode,
driver-command, sound-effect arbitration and sound-resource request contracts.
It is a component owner for the unfinished audio port. It does not synthesize
PMD music or FM effects and is not yet attached to the native frontend timeline.
All application launches remain muted and no audio device is opened.

## Original evidence

Pinned OP is 42290 bytes, SHA-256
`8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f`.
Restored payload is 69028 bytes, SHA-256
`13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`,
with 804 relocations. Fresh target preflight and packed OP database attestation
pass; provenance remains `candidate-local-attested`. Addresses below use
relative segment identities; independent CPU runs load at 1000 and 2000.

Original code executes PMD/MMD signature probes 0DA1:0206..0262,
command dispatch 0264..027F, mode selection 02D4..036F, load 03BA..04A1,
SE reset 08D6..08E0, SE play 08E2..091A and update 091C..0967. Separate code
between these functions is not imported or executed as a sound owner.
Interrupt replies, DOS file operations and beeper library calls are guarded
adapters. Full driver synthesis, physical residency and DOS I/O are outside
this claim. Load tests check DS restoration and destination-pointer requests;
the native owner emits the portable requests rather than reproducing DOS ABI.

Mode detection resets mode flags and inspects actual interrupt-vector magic.
The original still issues PMD function9 when the probe fails. Given a driver
reply, it selects FM26/FM86/off before applying user preference. FM SE is
determined before BGM is turned off, so BGM-off can retain FM SE. MIDI selection
uses MMD availability, but FM SE and SE resource loading still use PMD. A
disabled BGM command returns the incoming AX register, not its formal argument.

SE priorities and durations are 17-byte DATA tables at 0F34:09BE and 09CF.
Playing255 is idle. An idle slot accepts a request without resetting its
existing frame; an occupied slot permits equal-or-higher priority replacement
and resets frame0. Update submits the effect only on frame0, increments a BYTE,
then releases when the duration is strictly less than the incremented frame.
Off mode freezes this state. This preserves stale frames, BYTE wrap and the
final table sentinel. Unsupported WORD/table indices are explicit host errors;
arbitrary DS reads are not presented as supported native effects.

Resource loading copies its 13-byte input and writes a filename before checking
off modes. Song load stops music before selecting m26/m86/mmd. FM SE selects
efc; beeper SE selects efs and bypasses DOS/PMD requests. FM load opens the file,
requests the driver's address, requests at most5000h bytes, restores DS, then
closes. First setup and raw config numeric values are unchanged.

Fresh target text corrects a prior documentation error: DATA0F34:0DB3 labels
BGM2 stereo FM (FM86); 0DC4 labels BGM1 standard FM (FM26). The v1324 note's
former FM26(2) label was wrong. Source requests, setup trace and pixels used
the correct numeric value and retain their original evidence. ZUN's six
defaults FF0302010101 therefore request stereo FM, not FM26.

## Controls and product boundary

`verify_sound_control.py` executes the original functions at both relocated
loads for 13198 cases and 73751 records. Cases cover resident signatures,
requested WORD values, driver replies, commands and incoming registers,
all valid effects/priorities, stale and wrapping frames, duration boundaries,
all four music modes, all SE modes and 1..8-character resource bases. Complete
state, 13 filename bytes and ordered requests agree; return stack, DS, table
and unrelated canaries remain guarded. GNU and optimized UBSan agree with
the immutable independent reference. There is no physical playback claim.

A source-only mutant changes occupied-slot replacement from <= to <. The
independent trace rejects it at line14569. Its source, driver, compile command,
hashes and first difference remain; its terminal experimental binary is
retired after digest verification. No target bytes were changed.

370 registered source files bind141 AMD64 products,47 per GNU/UBSan/MinGW.
46 CTests pass per Linux host. The prior92 GNU/UBSan products are byte-identical
to v1324; MinGW's46 prior products have new link identities and receive only
current build/AMD64 checks. Real setup and config menu/restart controls regress
unchanged. MinGW is not actual Windows runtime acceptance.

## Next audio owners

Join actual game/OP/MAINE requests in their original order, including SE update
after the completed MAIN refresh and resource/mode changes across processes.
Implement retained PMD/OPN music and FM SE state/synthesis, plus EFS beeper
resource parsing and scheduler. Query real driver measures for cutscene waits;
do not invent measure advancement or claim that recording requests completes
audio. Verify offline samples/register state while every launch stays muted.
Complete natural ordinary/Extra routes, actual Windows save/restart and dense
Lunatic timing/performance remain part of the active goal.

Private original/native references, failures, source/product profiles and full
uncommitted v1308..v1325 recovery live under native
`.analysis/port64/audio-v1325/`. Historical DOS acceptance is unchanged.
