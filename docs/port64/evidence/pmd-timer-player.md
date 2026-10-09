# Native PMD resident timer register ownership

v1340 adds `TimerPlayer` around the existing FM/SSG/effect/rhythm owner.
GNU8, optimized UBSan and actual Windows each compare **80,040 complete
original rows**: 174 cases at PSP segments `1000` and `2000`, with 23 supplied
songs and six authored tempo/order fixtures per format across three drivers.
Windows executes 87 unique traces/40,020 rows and compares both original PSPs.
All 59 component contracts pass per host. 426 maintained inputs bind 180
AMD64 products, 60 per cache. Every run remains muted and opens no audio device.

## Recovered behavior

- The installed drivers have committed Timer B = 200. Music start initializes
  musical owners, conditionally commits a changed B value, then writes primary
  `25=00`, `24=00`, `27=3F` in that order. An unchanged B value is not written.
- A nonzero explicit IRQ writes `27=3F` before musical/effect work. A zero-status
  IRQ writes nothing. Stop does not disable resident timers: Timer A effects
  and its byte counter continue while music is stopped.
- Timer B visits all musical parts before committing the final tempo. This
  commit precedes Timer A effects in a simultaneous interrupt. Committing at
  the end of the combined IRQ incorrectly places the write after SSG effects.
- On FM26, an active FM effect's release restores its musical voice and then
  writes `27=0F` while music is playing. Original PMD.COM `PSP:2B2F..2B3F`
  loads its saved mode, clears acknowledge bits and calls the port writer.
  The observed data output is `PSP:23A2`. This recovers the default FM3 mode
  restoration; FM3 extra-part ownership remains unfinished.

`Sequence::timer_b_completed` marks the real dispatch boundary;
`FmPlayer::effect_released` marks the real voice-release boundary. Empty
callbacks preserve legacy explicit-IRQ consumers. These callbacks carry live
state, not prerecorded traces or fake measure replies.

## Evidence and replay

The unchanged HDI and driver identities are those in
[the independent original driver note](pmd-driver.md#target-and-observer-contract).
Auxiliary drivers are flat COM files with `PSP:0100` entry and `PSP:0103`
service; no MZ header or relocation table applies. No disassembler database is
used or target byte changed. Read-only raw views and executing the original
COM are different observation surfaces; neither is a DOS exact promotion.

Private scope: `.analysis/port64/pmd-clock-v1340/`. The original producer has
manifest `8d8a70c1c75ecec7de4987a639fd5dac4f39d988857bf5a994c38c3c26e5732f`.
The final consumer has manifest
`72b9b679a1abfcb295246b276eb89a91ef4e52322c2222080b6042fac9168111`.
Complete independent producer and final consumer source archives are read back.
2,088 direct service-view crosschecks validate the fast original observer.

The comparison retains all v1339 configured FM/SSG/fade/rhythm fields and
chronological banked writes, adding primary `24..27` mirrors and timer writes.
Count columns are 1134 for FM26 and 1140 for the other boards. Source-only
variants reject omitted acknowledge (END1 row 2), reversed startup (row 0),
omitted FM3 release (row 154), and tempo committed after Timer A (row 261).

```sh
python3 port64/verify_pmd_timer_player.py --hdi ../../runtime/images/zun.hdi --output .analysis/port64/NEW-original
python3 port64/verify_pmd_timer_player.py --reference .analysis/port64/NEW-original --binary .analysis/port64/linux-live-v1251/th04-port64-pmd-timer-player-contracts --binary .analysis/port64/ubsan-live-v1251/th04-port64-pmd-timer-player-contracts --output .analysis/port64/NEW-native
```

Use fresh output paths. Actual Windows uses `verify_windows_current.ps1` with
an attested typed `pmd-timer-player` plan. Final full readback compares every
Windows row with both original loads and checks all 180 product hashes.
GNU/UBSan replay previous rhythm primary/supplement, commands, combined,
musical SSG, running FM, musical FM, sequence and independent effect corpora.
Their original producer identities remain unchanged. The previous regression
consumer manifest differs only in the subsequently repaired PowerShell script;
its archived C++ inputs equal the final source.

## Retained rejected observations

The first original timeline sampled the legacy native player's unaccepted
pre-start state. Its first candidate rejects row 0, and the exact original
producer PID is stopped with terminal status 143. Complete/partial captures
and its original source archive remain; acceptance begins at explicit start.
Initial candidates omitted FM3 mode restoration and committed tempo after
Timer A. Their differing complete streams remain. The first Windows script
selected the legacy FM-player binary for the new trace kind; all 59 contracts
passed, but that trace attempt failed. Its script, plan, log and outputs remain.
The corrected typed script runs in a fresh stage; no failed receipt is restamped.

## Clock routing and limits

The pinned die-derived [YM2608-LLE source](https://github.com/nukeykt/YM2608-LLE/tree/7a2aca7b6830b96e48e3a4e1a40d15525993fa60)
reproduces repeated 144-master-cycle Timer A and 2304-cycle Timer B overflows
at `A=1023`, `B=255`, default prescaler. The raw prescaler selector is 2, the
reset encoding for divide-by-six, not a divisor of two. Private `lle-timers.c`
and complete downloaded-source hashes preserve the standalone CPU-only probe.
The pinned [ymfm timer implementation](https://github.com/aaronsgiles/ymfm/blob/81aec25ccbb98f4873a255f7551ac4dadac59b4a/src/ymfm_fm.ipp)
also derives these OPNA periods from 24 operators and prescale six. The local
DOSBox-X PC-98 timer source uses 18/288 microseconds, consistent at 8 MHz.

The [translated Yamaha manual](https://manualmachine.com/yamaha/ym2608/5410883-user-manual/)
page 35 gives formulas with half those periods. Retain this documentation
conflict. The executed chip model is corroboration, not measurement on physical
hardware or a cross-emulator game timing acceptance. Installation observations
show no prescaler addressing in the recorded three-driver/two-PSP setup.

This owner supplies correct register order for a future scheduler. It does not
yet convert nanoseconds into real IRQs, synthesize FM/SSG/rhythm audio, recover
ADPCM/PPS/FM3 extras, advertise frontend driver capability, provide real measure
waits, complete logo/startup, or accept complete natural Linux/Windows routes.
The Linux GUI hash remains unchanged from v1339; Windows relinks are current
bounded CPU products. No GUI launch/publication occurs. Target provenance
remains `candidate-local-attested` and historical DOS acceptance is unchanged.

Full cleanup readback checks 2426 protected hashes and reclaims
646,873,088 net allocated bytes (616.9 MiB), with all 180 current
products preserved. Terminal raw/probe outputs have verified lossless
successors; native objects/static archives regenerate from source.
`cleanup-before.json` records every identity, successor and Windows-stage
restore command. Current source and independent references remain live.
