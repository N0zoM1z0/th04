# Native PMD bytecode and timer state

Current update: [v1331 SSG ownership](pmd-ssg.md) removes the mask-bit exclusion
for all selected sequence fields. The following records v1330 acceptance.

v1330, 2026-10-09. `port64/pmd_sequence.hpp/.cpp` adds a native owner for the
supplied TH04 M26/M86 bytecode. It reads the part/rhythm directory, owns mutable
loop counters, visits SSG/FM/rhythm/PCM parts in driver order, and emits ordered
note, portamento, rhythm, end and command requests. Timer B runs note lengths,
finite/infinite loops, loop exits, tempo and bar commands. Timer A advances
fade independently. Stop freezes musical progress; restart resets bar/tempo/
volume while retaining note counters. Explicit widths preserve byte/word wrap.

This is a compiled component in the portable core. The frontend still reports
PMD/MMD absent. There is no native OPN register consumer, FM/SSG synthesis,
PMD sound-effect owner, physical timer scheduler or audio device. Decoded opaque
sound commands remain requests for that future consumer; emitting a request is
not evidence that its chip effect has executed. No target byte arrays, driver
binaries, captured register streams or song assets enter product source.

## Independent controls

`verify_pmd_sequence.py` executes the three unchanged auxiliary COM drivers
from the pinned HDI using the installation/DOS/board/injected-IRQ seam described
in [original driver evidence](pmd-driver.md). Fresh root/native preflight and
root OP database checks pass. The HDI and all driver identities remain those
attested in v1329. Canonicality is still `candidate-local-attested`.

The original INT60 published work table supplies eleven part pointers. Each
checkpoint records actual measure/volume/status services, Timer B setting,
bar length/tick and tempo, plus each part's music-relative position/loop,
length, loop status, note count, volume, transpose/master transpose, detune,
instrument and mask. All three drivers retain this selected work layout.
PMD.COM observes FM3 extension parts; PMD86/PMDB2 observe FM4–6 and PCM. These
are distinct board dialects, not one renamed buffer.

138 cases cover all23 songs per driver at PSP1000/2000. Each case includes128
A-only interrupts,384 simultaneous A/B interrupts, positive/negative fade,
stop/frozen IRQs, restart, zero-status IRQs and B-only playback. GNU and
optimized UBSan each compare134274 original rows. Twelve longer LOGO/OP/ST05B/
STAFF cases at PSP1000 compare49164 rows per host over4096 A/B interruptions.
They exercise later tempo/bar changes and musical loops; they do not establish
physical deadlines or complete gameplay routes.

**Comparison boundary:** raw original rows retain SSG part6/7/8 mask bit1.
That bit belongs to the unresolved original drum/SE consumer and is explicitly
excluded by `control_row()` from equality. The other selected fields and program
mask bits compare. This is control-state subset agreement, not complete driver
state, chip-request, PCM or audio equivalence. The raw references remain available
for the next sound-effect owner; no reference is rewritten to remove a mismatch.

All46 music resources additionally execute65536 native ticks each (3014656
in total) without decoder errors. This checks native termination/command
coverage only. A fixed96-tick bar mutant and a missing finite-loop-counter
increment mutant are rejected against original LOGO control state.

## Builds and reproducibility

390 registered source files bind153 AMD64 products in the existing GNU,
optimized UBSan and MinGW caches,51 per cache. Both Linux hosts pass50 CTests.
All100 previous GNU/UBSan program hashes are unchanged from v1328; MinGW
products have new relink identities and remain cross-build acceptance only.
The actual Windows exit0 probe still fails at WSL UtilBindVsockAnyPort before
PowerShell runs. Every application launch remains muted.

The original short-control producer retains its own390-file manifest and
read-back public-source archive from before the native contract correction and
explicit consumer field selector. Current consumers/products have a separate
390-file manifest. No producer receipt is restamped. The longer private probe
retains its source, input hashes and original rows. Historical DOS acceptance
ledgers are unchanged.

Private source/product profiles, raw references, native outputs, longer probes,
negative controls, cleanup and pending-source recovery:
`.analysis/port64/pmd-v1330/` in the native checkout. Replay with fresh outputs:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_sequence.py \
  --hdi ../../runtime/images/zun.hdi --output .analysis/port64/pmd-new/original
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_sequence.py \
  --reference .analysis/port64/pmd-new/original \
  --binary .analysis/port64/linux-live-v1251/th04-port64-pmd-sequence-contracts \
  --output .analysis/port64/pmd-new/native
```

Next implement the PMD drum/FM-SE ownership, gate/pitch/LFO/envelope and OPN
request consumer, then FM/SSG synthesis and hardware-clock scheduling. Only
then enable resident capability and real measure waits across startup,
Ending/Staff and process transitions. Complete natural Linux/Windows routes,
save/config restart and dense Lunatic timing/performance remain required.

Terminal cleanup reclaims 135467008 allocated bytes from 165 shared captures, 60 retired scratch outputs and 1012 source-backed Python caches. 956 protected hashes are unchanged at that boundary; current sources/programs/targets/HDI/references remain. Shared paths are immutable; future replay uses fresh outputs.
