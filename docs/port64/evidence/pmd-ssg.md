# Native PMD SSG effects and music channel sharing

v1331, 2026-10-09. `pmd_ssg_effects.hpp/.cpp` implements the supplied
PMD drivers' 40 built-in SSG instruments as semantic timed segments: tone
and noise periods, tone/noise enables, volume, envelope period/shape, signed
tone/noise increments and noise update intervals. Timer A advances the segments
and sweeps; priorities reject lower-priority channel steals and permit equal
priority restarts. Stop mutes channel C while preserving the other mixer bits.
The original publishes the requested ID even when priority refuses the request;
the native owner preserves this behavior.

The source contains typed instrument parameters, rather than copied executable
bytes, an original driver interpreter or captured register streams. It emits
ordered SSG register writes to a callback. The music/chip owner must supply its
register mirror through `mirror()`/`Sequence::mirror_ssg()`. No audio device is
opened. Standalone effect register behavior is verified; complete musical chip
state, FM effects, FM/SSG waveform synthesis and physical clocks remain absent.
The frontend still reports PMD/MMD absent.

## Original ownership and independent observations

All driver bytes come from the pinned HDI, with full identities checked by
`directory_files()` before execution. They are auxiliary flat COM programs,
not the MZ-format ZUN container. The raw target view and Unicorn execute the
same locally attested files; a disassembler is not a separate semantic Oracle.
Canonicality remains `candidate-local-attested`.

| Driver | Frame loader | Effect work state | Instrument bank | SSG address port |
| --- | --- | --- | --- | --- |
| PMD.COM | PSP:022E | PSP:0320 | PSP:2DB8 | 0088 |
| PMD86.COM | PSP:0C77 | PSP:0D69 | PSP:3C83 | 0188 |
| PMDB2.COM | PSP:0876 | PSP:0968 | PSP:388C | 0088 |

Each work state owns its next segment pointer, tone/step, remaining Timer A
count, noise/step/interval/counter, priority and published effect ID. The table
has 40 entries; each entry supplies priority and a segment-list offset. The
three banks have identical observed parameter bytes. Segment pointers are
converted to instrument/segment identities for comparison, with raw originals
and their load segment still attested privately.

`verify_pmd_ssg.py` runs all 40 effects on all three drivers at PSP1000/2000
and four explicit mixer initial values (00,5A,BF,FF). It checks A-only, B-only,
zero-status and simultaneous interrupts, restarts, stops, mixer changes and
priority conflicts. All 24 cases agree across drivers/loads. GNU and optimized
UBSan each compare **79,488 rows** of effect state, register mirrors and complete
ordered writes to effect-owned registers 4,5,6,7,10,11,12,13. Mixer initial values
are explicit chip-seam inputs; DOS, board readback and injected IRQs retain the
v1329 guarded adapter. This is not a physical timing or waveform comparison.

## Joining the musical owner

`Sequence` now triggers the first selected rhythm instrument in original order,
updates SSG channel C's occupation mask and advances the effect on Timer A after
Timer B when both flags are set. A non-rest SSG note or portamento can reclaim
the channel from a lower-priority drum, stopping it if necessary; higher-priority
effects retain ownership. Restart preserves the original lower mask bits.

The supplied-song short profile did not reject a variant that retained the
occupation bit after a possible reclaim. Three constructed legal PC-98 songs
therefore overlap a drum/effect with channel C notes, rests and portamento. The
original executable stays unchanged. Eighteen original cases at two loads
compare **3,942 rows** per Linux host: all 128 selected musical fields plus all
11 normalized effect-work fields. A retained-mask variant rejects at row 3,
column 105 (original 0, variant 2). Separate signed-tone, noise-interval and
priority-steal variants also reject actual original state/register observations.

The maintained sequence comparator now compares every selected mask bit,
removing v1330's SSG bit1 exclusion. Existing immutable v1330 raw references
supply 138 short cases / **134,274 rows** per host and 12 longer LOGO/OP/ST05B/
STAFF cases / **49,164 rows** per host, all passing without the exclusion.
Unselected chip/voice/gate/LFO/envelope work remains outside the comparison.
No prior producer receipt or original row is restamped or rewritten.

## Replay and product identities

```sh
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_ssg.py \
  --hdi ../../runtime/images/zun.hdi --output .analysis/port64/pmd-new/ssg-original
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_ssg.py \
  --reference .analysis/port64/pmd-new/ssg-original \
  --binary .analysis/port64/linux-live-v1251/th04-port64-pmd-ssg-contracts \
  --output .analysis/port64/pmd-new/ssg-native
# Add --sharing to both calls; use th04-port64-pmd-sequence-contracts for
# the sharing consumer. Every output directory must be new.
```

394 registered sources bind 156 AMD64 programs, 52 per GNU/optimized UBSan/
MinGW cache. Both Linux hosts pass 51 CTests. The 100 prior non-PMD GNU/UBSan
program hashes remain unchanged; the sequence programs change and each cache
adds the SSG program. MinGW products have current relink identities, with
cross-build acceptance only. The current Windows exit0 probe again fails at
WSL `UtilBindVsockAnyPort` before PowerShell runs. All runs stay muted.

The first original effect producer retains its own 394-file source manifest
and complete read-back archive from before the native initial-ID correction
and later sharing verifier. The sharing producer and terminal consumers bind
the current manifest separately. Dependency profiles verify the same Unicorn
1.0.2 engine hash as v1329. Private originals, all native outputs, four negative
controls, source/product profiles, cleanup and complete pending-source recovery
are in native `.analysis/port64/pmd-v1331/`.

Terminal cleanup reclaims 204,918,784 allocated bytes (about 195 MiB) from
217 verified duplicate captures, 259 retired scratch outputs and 512 source-backed
Python caches. All 1,046 protected hashes are unchanged at that boundary.
Sources, current programs, pinned targets, HDI and independent references remain;
shared captures are immutable and future replay uses fresh directories.

Next implement external FM effects and musical gate/pitch/LFO/envelope/OPN
control, then FM/SSG synthesis and physical timer scheduling. Only after those
owners exist should the frontend enable PMD capability and real measure waits.
Full startup, natural Linux/Windows routes, score/config restart and dense
Lunatic timing/performance remain required. DOS acceptance is unchanged.
