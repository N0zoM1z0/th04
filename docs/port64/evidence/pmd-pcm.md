# Native PMD PCM integration

v1342 adds CPU-only `OpnPcm` and `PcmPlayer`: the live resident parser and
master-cycle clock feed OPN/OPNA register writes into pinned BSD3 ymfm, then
produce 48 kHz signed stereo PCM. No audio device or backend is opened.

## Ownership and limits

`ClockedPlayer` retains musical/effect state, timer deadlines and resident
phase. The chip receives actual installation writes at epoch zero, followed by
timed FM/SSG/rhythm writes. Logical driver mirrors remain separate from chip
registers. Music stop/restart does not reset either clock or oscillator.

Maximum-fidelity chip outputs occur every four FM26 or eight OPNA master
cycles; the first output is at one full FM quantum, 72/144 cycles. Explicit
4 MHz/8 MHz scenarios retain the accepted clock epoch. Chip timers advance
before coincident CPU writes. These are declared adapters: physical bus
latency, initial phase, prescaler changes and CSM waveform accuracy are not
accepted. Unsupported external ADPCM reads reject instead of returning fake
samples; FM3 extras/PPS/ADPCM remain unfinished.

YM2203 has one mono FM output and three separate SSG outputs. All three SSG
channels contribute; the FM output is duplicated. Original PMD.COM installation
also writes the absent secondary bank: those writes have no YM2203 destination.
YM2608 has stereo FM/rhythm plus summed SSG. The portable output adapter
integrates held chip levels over integer master-cycle sample windows, mixes
at half gain, applies a fixed DC blocker and clips to signed 16-bit. It is
not a measured PC-98 analogue response or a finished frontend audio policy.

The frontend still owns process-local beeper `Runtime` instances. It does not
yet use `PcmPlayer`, advertise resident PMD capability, or derive scene waits
from its live musical measures. Real resident lifetime across OP/MAIN/MAINE,
beeper/FM stream mixing, complete logo/startup and ordinary routes remain.

## Evidence and independence

Three original COM drivers execute installation at PSP 1000/2000 under the
attested Unicorn/DOS observer. Their original timed register streams come from
the closed [v1341 clock corpus](pmd-clock.md). A standalone renderer uses those
streams and an independently written integration/mixer loop; the native
consumer executes its own parser and scheduling.

**Both renderers share the same pinned ymfm chip arithmetic.** This tests
driver-to-PCM integration and host routing, not independent chip waveform
accuracy. Complete original loads cover 174 scenarios and 106,088,380 stereo
frames per host. The equal second-load streams permit 87 actual renderings,
53,044,190 unique frames. GNU8, optimized UBSan and actual Windows compare
every configured byte; all 61 component contracts pass per host. 445 maintained
inputs bind 186 AMD64 programs, 62 per cache. All 61 prior GNU/UBSan program
hashes, including the GUI, remain unchanged; Windows relinks have fresh bounded
CPU identities. No new GUI or natural-route acceptance occurs.

Four source-only variants reject: SSG-A-only routing (frame 781), omitted DC
filter (782), early first chip tick (781), and muted rhythm ROM (777). The first
rhythm counterproof used TIMRHY, whose bounded clock trace has no real rhythm
key-on; equality is retained as inconclusive. END1 contains real key-on writes
and rejects. A mono/A/B/C/absent-bank contract also catches the original wrong
YM2203 output interpretation. The first two reference adapters and their
failed native comparisons remain separate rejected experiments.

The receipt serializer initially labelled the copied GAME.BAT input as a COM
driver. A fresh producer fixes that metadata and lists exactly three drivers.
All reference output bytes and compiled programs are unchanged. The final
GNU/UBSan replay and full archived Windows readback compare the corrected
producer; previous receipts keep their original identities. The only source
transition is `port64/verify_pmd_pcm.py`, verified by complete archive readback.

## Vendor and external rhythm data

The maintained vendor contains ten unchanged source/license files from
[ymfm revision 81aec25](https://github.com/aaronsgiles/ymfm/tree/81aec25ccbb98f4873a255f7551ac4dadac59b4a).
`UPSTREAM.json` records full hashes. BSD3 notices must accompany distributed
binaries. No chip ROM, original game data or GPL die-model source is imported.

OPNA requires an explicit external 8,192-byte rhythm ROM. The private canonical
input has SHA-256 `53afd0fa9c62eda3e2be939e23f3adf48a2af8ad37bb1640261726c5d5adeba8`,
SHA-1 `50b6c3e288eaa12ad275d4f323267bb72b0445df`, CRC32 `23c9e0d8`.
Its identity is corroborated by pinned MAME and two separately pinned header
copies. Those copies are not independent waveform Oracles. The raw die RSS
representation uses opposite nibble order; after conversion four bytes still
differ, at 043F/1B7F/1CFF/1F7F, the snare/cymbal/hi-hat/tom ends. Their terminal
nibble behavior remains unresolved. Preserve both representations; do not
claim die-ROM equality or silently substitute one for the other.

## Replay and retention

Private scope: `.analysis/port64/pmd-pcm-v1342/`.

- `original-v4/receipt.json`: corrected terminal producer, full compressed
  events/PCM, installation streams and current producer source archive.
- `native-final/receipt.json`, `windows/readback.json`: complete consumers.
  `windows/stage.tar.gz` restores the terminal actual Windows stage.
- `product-profile-final.json`, `source-profile-final.json`,
  `metadata-correction-readback.json`: current sources and compiled identities;
  old source manifest remains the program producer identity.
- `counterproofs-v2/receipt.json`, `counterproofs/failed-fixture.json`:
  rejecting controls and the inconclusive fixture. Earlier bank/layout/ROM
  rejections retain their sources, profiles, logs and raw-content digests.
- `cleanup-before.json`/`cleanup-receipt.json`, `dedup-before.json`/
  `dedup-receipt.json`: source-recoverable objects/libraries, lossless failed
  outputs and full Windows archive readback. Shared outputs are immutable;
  replay uses fresh directories. CMake regenerates absent intermediates.

```sh
python3 port64/verify_pmd_pcm.py \
  --reference .analysis/port64/pmd-pcm-v1342/original-v4 \
  --binary .analysis/port64/linux-live-v1251/th04-port64-pmd-pcm-contracts \
  --binary .analysis/port64/ubsan-live-v1251/th04-port64-pmd-pcm-contracts \
  --output .analysis/port64/pmd-pcm-v1342/FRESH
```

Original replay supplies the legal HDI, closed clock reference, standalone
renderer/profile and explicit external ROM/profile. Restore compressed probe
executables with their recorded execute permissions. Whole-game execution,
hardware waveform confidence and historical exactness remain separate.
