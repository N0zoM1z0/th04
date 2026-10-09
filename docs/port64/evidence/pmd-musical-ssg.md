# Native PMD musical SSG

v1336, 2026-10-10. `MusicalSsg` supplies three musical tone/noise parts,
normal and extended software envelopes, two LFOs per part, gates, slides,
volume/fade, mixer requests and built-in effect sharing. It consumes the
same `Sequence` as musical FM and uses that owner's random stream and Timer A
baseline. This is maintained C++ state, without a CPU interpreter, executable
byte arrays or recorded playback. Every launch remains muted; no audio
backend or device opens.

GNU8, optimized UBSan and actual Windows AMD64 each match **192,654 complete
original-backed SSG rows**: 138 supplied-song cases and 60 constructed cases,
at PSP1000 and2000 across the unchanged26/86/B2 drivers. All55 component
contracts pass on each host.412 maintained source inputs bind168 AMD64
products,56 per cache. This accepts the bounded musical SSG state/register
owner. DOS exactness and candidate-local-attested provenance remain unchanged.

## Target and ownership evidence

The pinned HDI and three auxiliary flat COM targets retain their independently
attested size/SHA identities in the private target profile. Their entry is
PSP:0100, service PSP:0103; they have no MZ header or relocation table. No target
bytes or database are edited. Anchored raw instruction views guide source
hypotheses; unchanged original CPU execution supplies comparison observations.
See [musical FM](pmd-musical-fm.md) for the full target identities and
[FM handover](pmd-fm-player.md) for the prior shared occupation owner.

PMD86.COM musical SSG body PSP:1364..1500 supplies the channel state and
masked recovery boundary. Ordinary envelopes at PSP:2F16..2FA0 retain signed
eight-bit attenuation and counter reloads; extended envelopes at
PSP:2FA1..3085 use four phases and signed rate delays. Timer A synchronized
envelopes and LFOs use the shared previous Timer A count, not a second clock.
Pitch conversion at PSP:2590..25BF rounds the period after octave shifts;
pitch requests at PSP:276D..281F retain normal/proportional detune and LFO
arithmetic. Volume at PSP:2958..2A00 preserves the distinct normal/extended
scaling, rounding, full SSG fade and signed LFO saturation.

Key/mixer/noise ownership is observed at PSP:2A4F..2A9A; key-off at
PSP:2ADE..2AF4 releases the envelope. Music stop at PSP:3107..31A0 emits mixer
BF when no effect owns the channel, otherwise preserves channel C with
`(mixer & 3F) | 9B`. Stop does not invent writes clearing all volumes. Start
emits noise6=0 after the stop mixer and before FM startup pan/LFO writes.
The missing startup noise request rejected the first development candidate.

Music's requested noise and the previous hardware-noise cache are distinct.
Original memory-write hooks observe effect-frame and sweep updates to the
cache: PMD.COM PSP:0254/031B, PMD86.COM PSP:0C9D/0D64 and PMDB2.COM
PSP:089C/0963. PMD86 frame PSP:0C98 and sweep PSP:0D5F write register6, then
publish DL to PSP:40B4. Music writes its own requested noise only when effect
ownership permits it and the previous cache differs. Omitting effect cache
updates rejected OP.M26 at row129; it must not be normalized away.

Secondary-LFO depth count B7 uses bit7 to select the LFO and low7 for count;
zero becomes FF. SSG B4 dispatch at PSP:1840 consumes16 ignored bytes, including
the fallthrough increments after `add si, 0A`; FM consumes10. The decoder now
retains that part-specific distinction. Direct EF requests entering musical
FM's primary SSG register range update the same SSG mirror and request sink.
Constructed channel-C fixtures also exercise direct SSG6 writes, the B4 extent,
ordinary/rest notes, drum/effect occupation, masked slides and stop/restart.

## Complete bounded comparison

Every SSG row retains five musical globals, attenuation/initial attenuation,
requested/previous noise, all96/98 bytes for each of the three musical work
parts,11 built-in effect fields, all14 SSG mirrors and every ordered SSG0..13
write. Only the two resource pointer words per part become resource-relative;
reserved work bytes, masks, envelope counters and ordered requests remain
compared. Nothing inside that selected ownership surface is excluded.

The original producer records all23 supplied songs per format and ten
constructed fixtures per format. Seven cover LFO shapes, two LFOs/depth counts,
normal/extended envelopes, Timer A synchronization, proportional detune,
gates, mixer/noise, rests, ties and slides. Three challenge channel-C
music/drum/effect handover. Each timeline has973 rows with A-only, B-only and
simultaneous interrupts, positive/negative fade and stop/restart.
198 original cases compare192,654 rows per host;99 native runs emit96,327
unique rows. Published-pointer observers perform1782 entire-row original
service crosschecks over the accepted supplied and constructed corpora.

Original tools freeze during production and archive their full starting
source. C++ hypotheses can advance under separate consumer source archives;
older receipts retain their own source identities. The final source manifest
is `3a59a4fb6c36a1d7e247bb52099d5b83e83a60e465133756756a6a21abe26320`.

The prior running FM/effects corpus also replays427,308 complete rows per host.
GNU/UBSan separately replay134,274 supplied and40,866 constructed musical FM
rows;134,274 short/49,164 long sequence rows;3,942 SSG sharing,79,488 SSG effect
and30,192 FM effect rows. Windows executes120 CPU-only traces:99 SSG and21
prior FM handover traces,309,981 unique rows, then Linux readback checks
619,962 complete rows against both original PSPs. All56 PE product hashes and
plan inputs are checked before/after, with recorded system DLL imports only.
This batch launches no GUI; older frontend receipts keep their identities.

Source-only counterfactuals reject the unchanged reference: missing effect
noise-cache update at row129; ignoring Timer A envelope clock at row846 in
SSG1.M86; truncating octave periods at row165. Full source/variant/compiler/
binary hashes, first differences and complete compressed rejecting traces
remain. The early startup/noise-cache development failures remain independently
recorded. Original targets and references never change to accommodate them.

## Replay and remaining work

```sh
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_musical_ssg.py \
  --hdi ../../runtime/images/zun.hdi --output .analysis/port64/FRESH/ssg-original
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_musical_ssg.py \
  --hdi ../../runtime/images/zun.hdi --challenge \
  --output .analysis/port64/FRESH/ssg-challenge-original
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_musical_ssg.py \
  --reference .analysis/port64/FRESH/ssg-original \
  --binary .analysis/port64/linux-live-v1251/th04-port64-pmd-musical-ssg-contracts \
  --binary .analysis/port64/ubsan-live-v1251/th04-port64-pmd-musical-ssg-contracts \
  --output .analysis/port64/FRESH/ssg-native
```

Actual Windows uses the typed `pmd-musical-ssg` plan and an owned NTFS copy of
`verify_windows_current.ps1`, invoked with `-NoProfile -File`. Private original,
native, Windows, source/product profiles, negative controls and cleanup
receipts live under `.analysis/port64/pmd-musical-ssg-v1336/`. Current source,
products, independent references and necessary failed evidence are retained;
terminal raw copies/staging and rebuildable intermediates retire only after
readback and a persisted allocation journal. Future writers use fresh paths.

FM and SSG ordered streams are currently compared separately. Complete combined
FM/SSG interleaving, mixed random modulation and explicit external-effect
controls across both owners still need a combined comparison. Additional SSG
D4/D3/D2 requests, FM3 extra subtracks, ADPCM/hardware rhythm, synthesis,
physical clocks, frontend capability and complete startup remain. No audible
sample, physical timing, complete natural ordinary/Extra route or dense Lunatic
performance acceptance follows from this component result. Continue with those
owners while keeping the complete original task active.

Final readback verifies1855protected hashes. Pre-mutation cleanup journals
measure1,311,682,560allocated bytes reclaimed; all168current products
remain. Both repository final CIs and `git diff --check` pass.
