# Resident PMD and native frontend

v1343 installs one CPU-only `ResidentPmd` per application and joins it to
`Timeline`/`Runtime`. The driver persists across OP, MAIN, MAINE and fresh OP;
controls and EFS beeper buffers are process-local. No audio device/backend opens.

## Service and ownership contract

The native owner computes installation register writes and implements recovered
KAJA start, stop, fade, measure, buffer, fade/status, version and FM-effect
services. Music and EFC reads have typed destinations, validated capacities and
explicit failure boundaries. Missing/invalid resources close the typed file;
refresh unwinding cancels the pending clock advance. This is native failure
policy, not original failed-DOS-call equivalence.

Actual driver identity determines capability and the M26/M86 extension:

| Original driver | Service type | Existing Board value |
| --- | --- | --- |
| PMD.COM | 4800 | 0 (`fm26`) |
| PMDB2.COM | 4801 | 1 (`fm86`) |
| PMD86.COM | 4802 | 2 (`speakboard`) |

The legacy enum labels are not hardware identity names. CLI profiles use the
original driver names; default `pmd` is mono/4 MHz. `pmd86` and `pmdb2` require
an explicit external 8192-byte rhythm ROM and use 8 MHz. `none` explicitly
selects the earlier absent-driver fixture. MMD remains absent in these cases.
Original ROM representation and chip-accuracy limits remain in [PCM](pmd-pcm.md).

Fresh OP/MAIN load their own SE resources. MAINE does not reload EFS or EFC:
its beeper is empty, while the resident EFC/effect state survives. Pending
outgoing refresh time drains before the next generation loads or starts music;
sample attribution stays with the outgoing owner. One resident PCM epoch
supplies FM/beeper frame counts; beeper phase/reset and signed stereo mixing
are explicit host adapters. Repaint does not advance time.

Ending queries measures after preceding song load/start requests. Staff Roll
also queries the real new-song provider. Inactive BGM retains original frame
fallbacks. No refresh means no fabricated musical progress. The frontend loads
sound resources from both MAIN and OP/MAINE archives; duplicate members must
agree completely. MAIN-only loading missed NAME and is a retained failure.

## Independent evidence and limits

The original OP sound bodies at relative 0DA1:0206..0280, 02D4..036F,
03BA..04A2 and 08D6..0968 execute against the attested decoded payload. Original
COM installation/services/IRQs execute on a separate original CPU engine at
PSP1000/2000. Typed service/file-buffer adapters couple them; these are not a
single physical DOS address space or natural OP/MAIN/MAINE startup. Fresh
control data uses a declared seed. Complete original installation writes,
requests, control state, measures/fade/status and 512 register mirrors compare.

Three drivers, four BGM and three SE choices at two PSPs yield 72 cases and
9204 records. GNU8, optimized UBSan and actual Windows each execute 36 unique
streams and compare both original loads. FM-mode PCM compares all 21103632
configured stereo frames per host (24 unique renders/10551816 frames). SE2
requests/state/frame counts compare independently; its mixed waveform compares
hosts only. The original driver timeline and standalone host renderer are
independent of the native player, but both PCM paths share pinned ymfm chip
arithmetic. This is integration evidence, not physical or independent chip
waveform accuracy.

Actual frontend controls use three profiles by nine BGM/SE choices. Each
profile yields 65 files, including mixed PCM, Music Room/ordinary MAIN and
physical registration/save/fresh OP captures. Both characters occur across
these choices; this is not the full character-by-option cross-product.
The registration child is a separate declared seeded application and uses the
fixture's defaults, not all parent options through a natural full route.
An authored legal Ending script uses actual LOGO data; actual STAFF resources
exercise the measure provider. Previous songs first acquire real measures
3/7, so wrong retention is observable. All profile files agree on GNU/UBSan/
actual Windows. Per host the three parent groups capture 1953180 mixed frames.

All 62 contracts pass per host. 451 maintained inputs bind 189 current AMD64
programs. Existing absent-driver MAIN controls compare 3574464 samples per
Linux host; OP/MAINE controls retain 216 options, 32 entries, 8834 snapshots and
1150 equal files. Their separate earlier manifests are preserved. The final
source is fded844658566dd8bb32f1298a68664a0f45e55d22676f2e979efe5380cf9964.

## Counterproofs and rejected experiments

Six source-only variants reject: constant-zero measure (row81), fake mono
capability (61), omitted installed stop state (41), MAINE EFC reload (84),
omitted outgoing refresh drain (contract), and retained previous-song measure
(actual frontend). Targets are never patched.

Moving the Ending query before scene advance is inconclusive for the stale
release claim: four text-box mask delays cause subsequent fresh queries. Its
assertions accept, while its timing record differs by one refresh under the
host adapter. Both observations remain; it is not one of the six rejects.
The first probe checked before the four mask waits and rejected a valid scene.
A rebuild during source editing left an older UBSan probe object; cross-host
readback rejected it. Fresh objects fix the mismatch, and source remains frozen
through final builds/runs. Maintained consumers check program/input identities
before and after runs. The first actual Windows run rejected CRLF diagnostic
text; trace/measure writers now use binary mode. Full raw comparisons remain.

## Replay and remaining work

Private scope: `.analysis/port64/pmd-resident-v1343/`.
`original/receipt.json` and its source archive remain the independent producer;
`native-final-v4/receipt.json`, `frontend-final-v3/receipt.json` and
`windows-v2/readback.json` bind final consumers. `product-profile-final.json`
contains compiler/cache/link identities. Counterproofs are in
`counterproofs-final/receipt.json`; earlier failures and
`counterproofs-v2/inconclusive.json` keep their own inputs. No receipt is restamped.

```sh
python3 port64/verify_pmd_resident.py \
  --reference .analysis/port64/pmd-resident-v1343/original \
  --binary .analysis/port64/linux-live-v1251/th04-port64-pmd-resident-contracts \
  --binary .analysis/port64/ubsan-live-v1251/th04-port64-pmd-resident-contracts \
  --output .analysis/port64/pmd-resident-v1343/FRESH-SERVICE
python3 port64/verify_resident_sound_join.py \
  --hdi ../../runtime/images/zun.hdi \
  --font /mnt/d/Entertainment/Game/Touhou/th04-reconstruct/FREECG98.bmp \
  --rom .analysis/port64/pmd-pcm-v1342/ym2608_mame_adpcm_rom.bin \
  --original-reference .analysis/port64/pmd-resident-v1343/original \
  --binary .analysis/port64/linux-live-v1251/th04-port64 \
  --binary .analysis/port64/ubsan-live-v1251/th04-port64 \
  --output .analysis/port64/pmd-resident-v1343/FRESH-FRONTEND
```

Windows uses the maintained typed `verify_windows_current.ps1`; private
`windows-v2.py` and `windows-v2/plan.json` record generation and invocation.
Replay requires fresh output/staging paths. Restore archived outputs before
reusing paths listed in historical receipts; retention journals give members.

Terminal cleanup verifies 2012 protected hashes and all archived members/modes;
5141 stage/control/intermediate files retire and 648 equal compressed paths share
immutable storage. Net allocated reclamation is 1514315776 bytes (1444.2 MiB).
The initial active-self-log guard failure remains; independent final readback
passes. `final-retention.json` binds journals and restore commands.

FM3/PPS/external ADPCM, full original logo/startup, complete natural ordinary/
Extra survival on Linux/Windows, restart/persistence route matrices and host
refresh/input/slowdown/Lunatic performance remain. The last published GUI is
v1296. Historical exactness and candidate-local-attested provenance are unchanged.
