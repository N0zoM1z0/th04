# Native PMD external FM effects

v1333, 2026-10-09. `pmd_fm_effects.hpp/.cpp` owns the supplied MIKO.EFC
scripts independently of the musical sequence. It interprets resource-relative
notes, gates, voices, volume, detune, transposition, ties, finite loops,
triangle LFO and portamento, then emits ordered FM register writes. Timer A
advances effects; Timer B alone does not. Restart releases the previous effect.
The original channel masks and stopped-music release behavior are preserved.

GNU8, optimized UBSan and actual Windows AMD64 each agree with the unchanged
original drivers on **30,192 rows**: 42 selected effect fields, six musical
occupation masks, all 512 register-mirror cells and complete ordered effect
writes. All 52 component contracts pass on each host. This is bounded effect
ownership with music stopped. Musical voice restoration, musical FM chip
state, synthesis, physical timer scheduling, frontend PMD capability and full
natural game routes remain unfinished. No audio device or backend is opened.

## Target ownership

`directory_files()` verifies the full pinned HDI and the original driver
size/SHA before execution. These drivers are auxiliary flat COM programs with
entry PSP:0100 and service PSP:0103, not the MZ-format ZUN container. Their
header/relocation check is explicitly not applicable. Target canonicality
remains `candidate-local-attested`.

| Driver | Bytes | FM effect start | Effect work | ID/active | Primary/extended ports | Borrowed channel |
| --- | --- | --- | --- | --- | --- | --- |
| PMD.COM | 20,379 | PSP:2A71 | PSP:3698 | PSP:31E9/31EA | 0088/008C | FM3 |
| PMD86.COM | 28,871 | PSP:3962 | PSP:46A6 | PSP:40B5/40B6 | 0188/018C | FM6 |
| PMDB2.COM | 25,730 | PSP:3580 | PSP:42AE | PSP:3CBD/3CBE | 0088/008C | FM6 |

MIKO.EFC is 1,044 bytes, SHA-256
`8b313b87b27741d09c7f83b35e6a98ae0769dbe52ea281b425d4c7f7acb7ad69`.
The first 127 WORDs point to effects; the WORD at offset254 points to the
voice bank. Unlike musical resources, this resource has no leading prefix
byte. Voice entries contain an ID and 25 semantic parameters, with an FF
terminator. The native source decodes the external resource; it contains no
original executable bytes, CPU interpreter or captured-write playback.

Raw, anchored Capstone views establish bounded target ownership; executing
the original CPU bytes in Unicorn is the independent native comparator.
Those raw views are not independent Oracles. Flat COM addresses include the
driver identity and PSP-relative offset, and every original scenario records
its actual load segment. An early private PMDB2 tick probe used the wrong
work base4206; the maintained verifier uses the observed42AE. That early
probe is exploratory and does not supply accepted state.

## Independent replay and rejecting observations

`verify_pmd_fm.py` produces original references at PSP1000 and PSP2000 for
all three drivers. Each of the 17 supplied game effects gets B-only and
zero-status interrupts, 256 A-only interrupts, simultaneous A/B interrupts,
same-effect restart, next-effect replacement and explicit stop. IDs0/16 are
empty. The longer interval observes completion beyond v1329's 32-tick
controls, including the 192-tick note. All 5,032 rows per case agree across
the two loads after converting script pointers to resource offsets.

DOS installation, board detection/readback, resource buffers and injected
interrupt flags remain explicit adapters. PIC and register27 timer
ACK/enable writes are outside the effect-event owner; they are excluded from
its event stream. **All 512 register cells remain compared**, including27.
There is no column, bit or register-mirror exclusion. Music remains stopped
and the caller's voice-restoration callback is a future integration seam.

The first native run rejected the assumed physical operator order1,2,3,4:
PMD.COM row583 differed at total-level registers46/4A and ordered writes.
The observed mask order is1,3,2,4. After that repair, PMDB2 row0 still
rejected because the original adapter captured raw008C/008E writes but
omitted them from its selected-register mirror and readback. The mirror
includes these ports now. The correction also recovers PMD.COM's extended
initialization register10. Full original-row readback proves that the changed
fields are confined to the extended mirror; effect fields and ordered writes
remain identical. PMD86's reference is unchanged. No old receipt is restamped.

Fresh original replay after the adapter correction matches the immutable
earlier references byte for byte: 144 all-music/installation files, old
FM/fade/restart controls, 79,488 SSG effect rows and 3,942 SSG/music-sharing
rows. The earlier musical owners therefore retain their independent input
observations. The 104 older GNU/UBSan program hashes also remain unchanged.

Two source-only variants reject the corrected independent reference:
unsigned LFO step at PMD.COM row1176 (original -80, variant176), and omitted
positive portamento remainder at row2360 (original slide13, variant12).
Private variant sources, compiler commands, binary digests and first failures
remain. Targets and original references are never patched for these controls.

## Replay and retention

```sh
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_fm.py \
  --hdi ../../runtime/images/zun.hdi \
  --output .analysis/port64/pmd-new/fm-original
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_fm.py \
  --reference .analysis/port64/pmd-new/fm-original \
  --binary .analysis/port64/linux-live-v1251/th04-port64-pmd-fm-contracts \
  --binary .analysis/port64/ubsan-live-v1251/th04-port64-pmd-fm-contracts \
  --output .analysis/port64/pmd-new/fm-native
```

The source manifest has 399 maintained files and binds 159 AMD64 programs,
53 per cache. All current MinGW products have freshly attested identities and
only Windows system imports. `verify_windows_current.ps1` also accepts typed
FM component trace plans; its six actual Windows trace files compare in full
against the immutable original reference, with product/input hashes before
and after. It does not enable an audio backend. Prior v1332's nine muted
frontend/physical-save controls retain their own source/product identities;
v1333 does not claim those launches were rerun on its relinked Windows GUI.

Private `.analysis/port64/pmd-fm-v1333/` retains distinct original producer
and terminal consumer source archives, compiler/cache/link/input/product
profiles, unchanged-reference comparisons, negatives and actual Windows
receipts. Terminal duplicate outputs share immutable files only after full
byte/hash comparison. Failed traces are compressed with exact decompressed
readback; mutant programs and the owned NTFS stage are retired. Replaying
requires fresh output directories. Readback shares235 identical files and
reclaims325,083,136 allocated bytes (about310MiB); all730 protected hashes
remain unchanged. DOS exactness acceptance is unchanged.

Both final repository CIs and `git diff --check` pass. Afterwards, retiring
1,015 source-backed CPython caches in root/native public script/test/port64
trees reclaims another17,125,376 bytes without changing1,130 Python source
hashes. The root cleanup receipt is
`.analysis/cleanup/pmd-fm-source-backed-caches-20261009.json`; combined terminal
reclamation is342,208,512 bytes (about326MiB). Current CMake caches and programs
remain live.

Next recover the musical gate/pitch/LFO/envelope/register owner and actual
musical voice handover, then synthesis and physical scheduling. PMD capability
and real scene measure waits must follow those owners. Continue to keep all
application launches muted.

Current musical FM state/register progress is separately verified in
[musical FM evidence](pmd-musical-fm.md). This note retains the stopped-effect
profile; running voice handover is still pending.

The bounded running music/effects join is now verified separately in
[FM player evidence](pmd-fm-player.md). Earlier receipts and historical open
questions above retain their original scope and source identities.
