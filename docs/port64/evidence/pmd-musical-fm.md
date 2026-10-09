# Native PMD musical FM state and register requests

v1334, 2026-10-09. `pmd_musical_fm.hpp/.cpp` adds a typed musical FM
owner above `Sequence`: embedded voices, frequency/block, detune and slide,
fixed/proportional/minimum/random release gates, ties, temporary volume,
both LFOs and modulation depth, Timer A synchronization, key delay and
hardware LFO/PMS delay. It emits ordered logical register requests. No CPU
interpreter, executable byte array or captured-write playback is in this owner.
Unsupported musical commands and external voice banks fail closed.

GNU8, optimized UBSan and actual Windows AMD64 each compare **175,140
original-backed rows**: 134,274 supplied-song rows and 40,866 constructed
rows. Each host passes all 53 component contracts. There are 403 maintained
source inputs and 162 AMD64 programs, 54 per cache. The selected musical
owner is verified; effects/music handover, musical SSG, FM3 extra subtracks,
ADPCM/hardware rhythm, synthesis, physical clocks, frontend PMD capability,
complete startup and full natural game routes remain separate work. All
launches stay muted; no audio device or backend is opened. DOS exactness and
target provenance remain unchanged.

## Independent target and ownership

The unchanged drivers come from the size/SHA-attested original HDI,
SHA-256 `0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd`.
`verify_pmd_driver.py` pins each driver's full size/SHA. PMD.COM is 20,379
bytes, PMD86.COM 28,871 and PMDB2.COM 25,730. These are auxiliary flat COM
programs, entry PSP:0100/service PSP:0103, with no MZ header or relocation
table. They are distinct from the MZ-format ZUN.COM container. Canonicality
remains `candidate-local-attested`.

Raw anchored Capstone views guide the hypothesis; unchanged original CPU
execution under the recorded Unicorn build supplies the independent native
comparison. No disassembler database supplies a second Oracle. PMD86.COM's
reviewed musical FM body is PSP:1150..1364, with gate handling at PSP:1295,
transpose/frequency helpers at PSP:2502/2559, pitch helpers at PSP:25C0/272A,
volume at PSP:2820, key handling at PSP:2A01/2A9D, voice at PSP:2AF5 and
LFO work at PSP:2C30..2F16. These are bounded observation surfaces, not new
accepted exact unit boundaries.

The original service1000 returns the published work-pointer table. Each
scenario records the driver identity and actual PSP load1000 or2000.
PMD.COM musical work has 96-byte parts; PMD86/PMDB2 have 98-byte parts.
The six selected FM pointers, globals, resource buffers and initial register
mirrors are independently read from the executing driver. Script pointers
are converted only to resource offsets. DOS installation, board detection,
readback and explicit Timer A/B interrupt injection remain adapters; these
controls do not measure a physical chip clock or another PC-98 emulator.

## Comparison surface and controls

Every row compares five globals (measure, fade, status, Timer B/A), 72 fields
for each of six musical FM parts, 272 mirror cells and every ordered write
in the declared FM ownership. The mirror covers both banks30..B6, including
holes, and primary22/28. Each LFO includes current/preset delay, speed, signed
step, count, value, shape, mask and modulation-depth counters. Gates, voices,
key flags, hardware/key delay, slot/carrier masks and all four total levels
are compared. No owned field, bit, mirror cell or ordered event is dropped.
SSG, ADPCM/hardware rhythm, FM3 extra subtracks and global timer ACK writes
are explicitly outside this owner. All complete row bytes compare, rather
than independent per-field tolerances.

All 23 supplied songs in M26/M86 execute through their three applicable
drivers at both PSPs: 138 cases, 973 rows each. The interrupt timeline has
128 A-only ticks, 384 simultaneous A/B ticks, positive fade plus128 A ticks,
negative fade plus64 A ticks, stop plus128 simultaneous ticks, then restart,
zero-status interrupts and128 B-only ticks. This covers resource parsing,
voices, notes, fades, stopped preservation and restart. Supplied musical
resources contain their own typed voice directories; no game assets enter
checked-in native source.

Seven constructed resources per format independently exercise both LFOs,
all seven shapes, modulation depth, Timer A synchronization, gate modes,
key/hardware delay, PMS/LFO register writes, ties, rests, repeat-last note
and portamento: 42 cases at both PSPs, 40,866 rows. Only legal music data is
constructed; original executable bytes remain unchanged. Random gate is
present only for M86 drivers because the original 26 dispatcher stops at B2.

Native consumers reuse one execution for the two load-invariant references:
69 supplied-song runs and21 constructed runs per host. Actual Windows runs
90 processes, producing **87,570 unique rows**, all compared against both
original PSPs for 175,140 row comparisons. Complete Windows bytes are read
back in Linux before verified lossless compression. The Windows receipt
binds all 54 PE32+ products and all inputs before and after execution. There
are no frontend/GUI launches in this batch.

## Rejecting observations

The initial candidate rejected disabled 26-board part slots/voice masks and
startup register22. A later candidate with only board-default gain still
rejected actual musical total levels. Original PMD86 global attenuation is
at PSP:40A3, initial attenuation at PSP:40FC; C0 FF/FE handlers at PSP:187D/
1898 implement set and signed saturating add/reset. **SSG part6 executes
these global commands before FM**, so the musical owner processes them from
all parts. Initial attenuation is16 for PMD.COM and0 for86/B2. Preserved
candidate2 source and its rejected row log document this failed approach.

The first constructed comparison rejected 26-board hardware LFO/PMS/delay:
row129 expected pan192 and delay0, candidate pan195/delay2 and register22=8.
The 26 driver ignores E4/E1/E0;86/B2 execute them. The native branches now
preserve this observed distinction. The 26 dispatcher at PSP:0ACB compares
against B2;86 dispatcher at PSP:164F accepts B1, the random-gate field at
work offset60. The native 26 parser rejects unsupported B1 explicitly.

Three source-only variants independently reject without changing original
inputs or references:

| Variant | First rejection |
| --- | --- |
| Ignore global gain | PMD.COM END1.M26 row129: total-level mirror19 becomes21 |
| Omit last Timer A count | PMD.COM LFO1.M26 row130: primary LFO value16 becomes32, with pitch/level write differences |
| Omit proportional gate | PMD.COM LFO0.M26 row129: gate5 becomes2 |

Variant source, exact build commands, compiler/binary hashes and complete
first differences remain. An initial private variant build used the wrong
SSG source filename and failed compilation; it is not a comparator result.
An exploratory directory-iteration probe also crashed; its cause is not
established and supplies no accepted musical evidence.

GNU/UBSan regress against immutable earlier original producers on all
134,274 short sequence rows, 49,164 long sequence rows, 3,942 SSG/music
sharing rows, 79,488 SSG effect rows and 30,192 external FM effect rows per
host. Existing consumers retain their original comparison scope. Relative
to v1333, 52 GNU and51 UBSan program hashes remain identical; changed sequence
and UBSan SSG programs have new identities and are replayed. All Windows
programs relink and are independently attested/executed. System-only PE
imports remain verified.

## Replay and retained evidence

```sh
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_musical_fm.py \
  --hdi ../../runtime/images/zun.hdi \
  --output .analysis/port64/pmd-new/music-original
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_musical_fm.py \
  --hdi ../../runtime/images/zun.hdi --challenge \
  --output .analysis/port64/pmd-new/music-challenge-original
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_musical_fm.py \
  --reference .analysis/port64/pmd-new/music-original \
  --binary .analysis/port64/linux-live-v1251/th04-port64-pmd-musical-fm-contracts \
  --binary .analysis/port64/ubsan-live-v1251/th04-port64-pmd-musical-fm-contracts \
  --output .analysis/port64/pmd-new/music-native
```

Repeat the consumer with the constructed reference and fresh outputs.
`verify_windows_current.ps1` accepts typed `pmd-musical-fm` plans. Its owned
NTFS script, products, inputs and original receipt hashes are bound by the
private plan; no execution-policy override is used.

Private `.analysis/port64/pmd-music-v1334/` retains separate supplied-song
producer, constructed producer and final consumer source archives/manifests,
compiler/cache/link/product/target profiles, compressed complete references,
GNU/UBSan and Windows receipts, rejecting sources/logs and regressions.
Producer identities differ and are never restamped as the final consumer.
Full archive/source/product/input/trace readback passes with 990 protected
hashes. Terminal duplicates share only after whole-byte/digest equality;
future replays require fresh directories. Failed and Windows raw traces are
compressed with exact decompression readback; private probe/variant programs
and owned NTFS staging are retired.

Two interim receipts measure **272,588,800 allocated bytes** reclaimed
(about260MiB). The terminal cleanup completed, but its final accounting
failed on an absent interim-receipt key. The failed script/log remain;
`readback_recovery.py` independently verifies all retained inputs, archives,
programs and complete compressed outputs. No terminal-step byte estimate is
claimed. This accounting failure never changes target or comparison bytes.

Next join running music with external FM effects, proving borrowed mask/key/
voice/volume/pitch restoration. Finish other musical chip owners and synthesis,
then physical clocks/frontend capability/startup and full ordinary/Extra
host routes. Component success alone must not enable a fictional music clock.

Both final repository CIs and `git diff --check` pass. Subsequent source-backed
CPython cache retirement uses a persisted pre-deletion journal:1,013 caches,
17,059,840 allocated bytes,1,131 unchanged Python source hashes. Together with
the two interim receipts, measured reclamation is289,648,640 bytes (276.2MiB);
unrecorded terminal allocation is excluded. Root cache receipt:
`.analysis/cleanup/pmd-musical-source-backed-caches-20261009.json`.

The bounded running music/effects join is now verified separately in
[FM player evidence](pmd-fm-player.md). Earlier receipts and historical open
questions above retain their original scope and source identities.

## Primary feedback and operator total-level controls

v1344, 2026-10-10. The primary six-part owner now executes B6 feedback and
B8 total-level commands. Full-slot masked FM3 voice loading keeps the real
algorithm in shared state and stores the surviving voice-ID AL in the part
field on all three drivers; the prior FM26-only branch was too narrow.
Partial operator ownership and extra FM3 tracks are outside this acceptance.

B6 rotates an absolute byte left by three, including its low algorithm bits.
Relative feedback adds in eight bits before signed-bit/clamp decisions. FM3
uses its shared algorithm and requires operator1 ownership. FM26 disabled D-F
ignore B6 entirely, including software state. B8 selects slots from the low
selector nibble, walks logical operators1,2,3,4 at physical offsets40,48,44,4C,
and retains byte-wrap/clamp behavior. Masking suppresses B8 hardware writes
while preserving stored TL for later restore.

Anchored original COM observations are B6/B8 at PMD.COM PSP:0D6C/0DE3,
PMD86.COM PSP:18F6/196F and PMDB2.COM PSP:14F8/1571. `algorithm-tl.asm` and
`attest-v3/target-profile.json` retain full driver identities and table context.
The B8 static excerpt is bounded and truncated before its final relative return;
it is not an accepted function boundary. No database or decompiler supplies
an independent semantics Oracle; unchanged original Unicorn execution does.

The maintained `--operator-controls --ticks 800` producer creates six primary
parts by initial feedback0/56, every B6 byte, every B8 amount byte and every
B8 selector byte with alternating masks and restored voices. This is axis
coverage, not the256-by256 B8 argument Cartesian product. The72 two-PSP cases
contain100,008 complete rows. `--operator-corners` adds12 cases/1,440 rows with
all six parts active, algorithm0/7, masked restore and high-bit initial TL;
its fixed119-operation timeline yields120 rows/case. These are constructed
byte-arithmetic inputs, not supplied-song usage or compiler-emission claims.
No full-song absence claim follows from the earlier short FM3 usage probe.

GNU8, optimized UBSan and actual Windows each agree on101,448 complete rows,
using42 unique streams against both PSPs. No owned field/write normalization
or exclusion is added. GNU/UBSan additionally compare602,448 earlier supplied,
dual-LFO and joined player/effect rows per host; resident services regress9,204
rows and21,103,632 FM stereo frames per host. Three actual frontend profiles
produce195 equal files/1,953,180 mixed frames per host on all three hosts.
Registration is a seeded child and its defaults do not establish all parent
options through a natural route. SE2 waveform is host-consistency evidence;
FM synthesis shares pinned ymfm and cannot establish physical chip accuracy.
All62 contracts pass per host;451 inputs bind189 current AMD64 programs.

| Source-only variant | Discriminating rejection |
| --- | --- |
| Wrong logical TL order | Main operator corpus row435 |
| Write TL while masked | Main operator corpus row396 |
| Keep masked FM3 handling FM26-only | PMD86 part2 corpus row129 |
| Shift feedback instead of rotate | Algorithm0 corner row27 on all three drivers |
| Widen TL addition before clamp | Corner row17 on all three drivers |

The last two initially agree in the first corpus and remain recorded as
inconclusive there; algorithm7 hides rotated low bits and the first timeline
does not expose the initial TL255 wrap. The later controls discriminate them.
Candidatev1 incorrectly writes/updates disabled FM26 D-F; candidatev2 removes
writes but still changes software state. Both reject and remain separate
negative observations; the final early skip corrects both effects. Initial
static dispatcher probes also had signature/table ambiguity; only v3's
FM handler context is used for the anchored observation.

Private scope: `.analysis/port64/pmd-fm3-v1344/`. The primary original producer
uses manifest60a0854c205e3e2b637b1e5e4c5e9b4d59ea9f04f41268528f7d15adf482f2c6;
its maintained fixture bytes agree with the final consumer's inputs. The private
corner producer v1 and maintained producer v2 agree on every original row,
but share an engine/observer and are not separate independent semantic Oracles.
Final consumers and maintained corner producer use
81260aeae14b62a1f175844a52a00bb25f122fa938f45524a19b103fb718912b.
Neither earlier identity is restamped. Source archives, complete compressed
original/native rows, negative sources/commands and product/compiler/cache/link
profiles remain available. Windows `windows/readback.json` binds63 products,
62 contracts,42 operator and36 resident traces plus all three frontend profiles.

```sh
python3 port64/verify_pmd_musical_fm.py --hdi ../../runtime/images/zun.hdi \
  --operator-controls --ticks 800 --output .analysis/port64/FRESH-OPERATORS
python3 port64/verify_pmd_musical_fm.py --hdi ../../runtime/images/zun.hdi \
  --operator-corners --output .analysis/port64/FRESH-CORNERS
python3 port64/verify_pmd_musical_fm.py \
  --reference .analysis/port64/pmd-fm3-v1344/original-operators-v1 \
  --binary .analysis/port64/linux-live-v1251/th04-port64-pmd-musical-fm-contracts \
  --binary .analysis/port64/ubsan-live-v1251/th04-port64-pmd-musical-fm-contracts \
  --output .analysis/port64/FRESH-OPERATOR-CONSUMERS
```

Repeat the consumer against `original-corners-v2` with a fresh destination.
`stream-regression.py` records streaming raw comparisons with immediate gzip
round-trip retirement; its old fixed output roots require fresh replay paths.
Actual Windows uses maintained typed `verify_windows_current.ps1`, generated
by private `windows.py`/`windows/plan.json`. Closed stage/capture archives and
restore commands are indexed by `retention.json`; restore each member under
its recorded `directory` before historical readback. Current executables and
independent references remain, while CMake rebuilds retired intermediates.

Next recover C6 extra FM3 subtracks, C7/C8 detune, CF partial operator ownership
and special pitch/LFO-slot interaction. PPS/external ADPCM, original complete
logo/startup, natural ordinary/Extra/save/restart routes, host refresh/input/
slowdown and dense Lunatic performance remain open. No DOS exact promotion,
physical chip/timing acceptance or new GUI delivery follows from this batch.

Terminal retention reclaims748449792 allocated bytes net (713.8 MiB):
root review cleanup retires1,610 CMake/Python intermediates; native retention
retires987 closed stage/capture files into two fully read-back archives.
Original references, source archives and current189 programs remain.
