# FM3 slot and subtrack ownership

v1345, 2026-10-10. Maintained native code implements C6, CF, C7 and C8 with
shared algorithm/feedback, per-operator pitch, two LFO masks, masked restore,
effect borrowing and restart. This is bounded semantic/runtime acceptance,
not DOS exactness or complete audio/game acceptance. All launches stay muted;
no audio device/backend is opened.

## Target and ownership

The complete Japanese HDI is SHA256
`0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd`.
The three unchanged flat-COM originals retain their pinned identities:

| Artifact | Complete size | SHA256 | C6 / CF / C7 / C8 PSP offsets |
| --- | ---: | --- | --- |
| PMD.COM |20379|`cbbe9bd610aedda586d8bd7f6dd13d21f037a089458a21ddda0b11a53b4b29e4`|0FDE /11D6 /10AD /10DD|
| PMD86.COM |28871|`34b7381d66400b89fca833e08fb30f315b9092eb3883f137538dcf18477fd77f`|1B78 /1D70 /1C47 /1C81|
| PMDB2.COM |25730|`dfebbfd6e82916dfc4d8d01f2fcd938e215cc16cbd5ce2f19bce37cdc3841437`|177A /1972 /1849 /1883|

Addresses name the artifact and PSP-relative segment identity; runtime PSPs
are1000 and2000. Dispatch tables are data at PSP:0AE2/1666/1268. Their words
anchor handlers; decoding these tables as executable entries was an early
failed probe. No disassembler database or decompiler supplies an independent
Oracle. `profile.json`, `anchors-v2.asm` and the bounded release/helper views
retain the raw-target context; excerpts do not accept exact unit boundaries.

Observed and runtime-observed ownership:

- FM26 C6 repurposes primary D/E/F works at PSP:3398/33F8/3458. PMD86 appends
  works4580/45E2/4644; PMDB2 appends4188/41EA/424C. Three nonzero LE offsets
  add the music base; zero skips without erasing an already active track.
  C6 can originate outside primary FM3. Initialization preserves fields not
  written by the original, including note counters through restart.
- CF high bits own logical operators; low bits select carriers, falling back
  to shared algorithm carriers when zero. Slot0 masks parsing. Logical
  bits10/20/40/80 become duplicated physical voice masks88/22/44/11.
  Parameter writes use physical mask bits, while volume keeps logical order.
  Changed extension ownership re-key-ons earlier parsed, unmasked FM3 tracks.
- Four signed16 detunes are shared. C8 assigns, C7 adds with16-bit wrap; they
  are ignored outside FM3. Special pitch walks owned operators4/3/2/1 and
  emits A6/A2, AC/A8, AE/AA, AD/A9. Each LFO mask rotates only for an owned
  operator. A zero low nibble means wildcard slots for pitch.
- Contributor bits1/2/4/8 track the primary/three extensions. Stored mode is
 3F/7F; transitions write27 as0F/4F and the next IRQ acknowledges3F/7F.
  For full slots, the primary mask low nibble gates the secondary LFO mode
  branch. Preserve this target short circuit, not a symmetric LFO OR.
- FM26 effect start saves deferred mode, borrows all four FM3 works and
  switches current mode to3F. PSP:2AE6 release silences all hardware slots,
  calls PSP:0F1C to restore primary C and D/E/F in that order, then restores
  deferred mode. PSP:1CE1 owns the shared key mask; clearing only the effect
  object's separate native mask leaves wrong restore writes. Deferred mode
  survives song restart. FM86/B2 effect borrowing uses its separate sixth
  hardware channel. Slot-aware FF preserves shared feedback without op1;
  masked FF retains the original surviving-AL part-field quirk.

The semantic owner uses14 sequence works and9 musical FM parts. FM26 aliases
its old disabled works;86/B2 have three appended works. Hardware channel keys
are shared by every logical FM3 track. The prior eleven-track and TimerPlayer
trace formats remain compatible; the new checker adds the FM3 observation
surface rather than weakening earlier comparators.

## Independent controls and acceptance

`verify_pmd_fm3.py` executes unchanged originals in Unicorn1.0.2 at two PSPs,
with full HDI/COM/engine pins, explicit IRQ/board/file adapters and archived
producer inputs. Every prior TimerPlayer field and chronological owned write
remains compared. The added surface is nine FM3 globals and72 scalar fields
for each of three tracks (225 fields). Service versus PublishedView snapshots
cross-check the observer, but are views of one original engine, not independent
semantics Oracles. There is no state/write normalization or added exclusion.

| Retained reference | Cases / complete rows | Coverage and identity |
| --- | ---: | --- |
| original-maintained |48 /40,608|Eight constructed resources, all three drivers, both PSPs; MFd9d1ca4f...|
| original-corners |12 /10,152|PARTLFO and SUBDETUNE; MF1689400f...|
| original-corners-live |12 /10,152|PARTLFO C8 detune reduced32767->1; unchanged SUBDETUNE repeats; MF1689400f... plus separate recipe hash|

The third batch repeats six SUBDETUNE cases/5,076 rows. Thus there are
**66 distinct cases/55,836 rows**, across33 distinct service streams on each
native host; the Linux consumers additionally repeat those six cases.
Eight main resources cover all256 CF bytes, all16 C7/C8 selectors with eight
word corners, full-slot dual LFO masks, three C6 extensions, remasking,
zero pointers, activation from part0 and non-FM3 ignored detunes. Corners add
partial-slot dual LFO pitch and detunes issued by extensions. This is selected
axis/corner coverage, not every argument Cartesian product or every FM3
command combination. Constructed usage is not supplied-song usage evidence.

GNU8, optimized UBSan and actual Windows agree on the full declared rows and
ordered writes. All63 contracts pass per host.453 maintained files bind192
current AMD64 programs (64 per host), with compiler/cache/link/product hashes.
Each Linux host additionally regresses783,936 earlier operator, supplied-song,
dual-LFO, joined-effect and timer rows. Resident regression compares9,204 rows
and21,103,632 FM-mode stereo frames per host; three muted frontend profiles
produce195 equal files/1,953,180 mixed frames per host on all three hosts.
SE2 waveform/frontends are host-consistency evidence; FM synthesis shares
pinned ymfm, so this does not prove physical chip accuracy. Registration is a
seeded child, not a complete natural parent route.

Current source MF: `1689400f6154f6ef377d41357a802a1d6a75129e19449068c81a431e26ef50b0`. The main original producer retains MF
`d9d1ca4f45ab2e28e5541c27ac23e3a6674d028a0db5deada383bfdc4a294599`;
the earlier private v3 producer retains81260ae... . `producer-equivalence.json`
proves all48 complete observations equal through the maintained refactor;
they are not separately independent references. No receipt is restamped.

## Rejections and limits

Nine distinct source-only wrong implementations reject: wrong86 C6 work
aliasing (row1), logical instead of physical voice mask (17), symmetric LFO
mode (1), resetting deferred mode at restart (525), restoring only primary
FM3 after an effect (331), key-off instead of re-key-on (1), emitting unowned
operator pitches (17), restricting detunes to primary (1), and rotating masks
through unowned slots (2 with small detune). The final two are separate corner
controls. The mask rotation variant first agrees in the32767-detune corner:
pitch clipping hides its LFO difference. Retain that inconclusive result.

Original-v1 has a wrong PMDB2 global offset; v2 lacks default voice0 during
restore and fails to patch a repeated C6 marker. Neither full corpus is
accepted. Corrected v3 and the maintained producer agree. Candidatev1-v8
receipts retain progressive rejections; v7 passed86/B2 but failed five FM26
release scenarios, and v8 restored four tracks but retained wrong shared keys.
The first new standalone contract fixture also omitted default voice0; it
failed before acceptance and was corrected without changing the runtime owner.
These are fixture/candidate failures, not evidence against the original driver.

PPS/external ADPCM, original logo/startup completion, natural Linux/Windows
Normal/Extra routes and save/restarts, refresh/input/slowdown/Lunatic timing
and updated GUI delivery remain. Broader FM3 combinations remain untested.
Target canonicality stays candidate-local-attested. Historical DOS acceptance
and the deferred MAIN carpet/checkerboard units are unchanged.

## Replay and recovery

Use fresh output directories and one source revision throughout each run:

```sh
python3 port64/verify_pmd_fm3.py --hdi ../../runtime/images/zun.hdi --output FRESH
python3 port64/verify_pmd_fm3.py --hdi ../../runtime/images/zun.hdi --corners --output FRESH
python3 port64/verify_pmd_fm3.py --reference ORIGINAL --binary CURRENT_FM3_CHECKER --output FRESH
```

The live-mask recipe changes only eight constructed PARTLFO C8 operands;
it does not alter the original target, observer, comparator or native source:

```python
import verify_pmd_fm3 as v
fixtures = v.corners()
data = fixtures['PARTLFO']
assert data.count(bytes([200, 15, 255, 127])) == 8
fixtures['PARTLFO'] = data.replace(bytes([200, 15, 255, 127]), bytes([200, 15, 1, 0]))
v.corners = lambda: fixtures
# Call v.main() with --hdi ... --corners --output FRESH, or v.produce().
```

Private scope: `.analysis/port64/fm3-recovery-v1345/`. It retains original
references, recipe/source archives, failed attempts, manifests, command logs
and consumer receipts. `corner-reference-live.py` and `corner-live-recipe.tar.gz`
bind the full recipe. `windows.py` and `windows-lfo.py` drive the maintained
PowerShell checker with typed hashed plans; readbacks compare complete files
against both PSPs. Streaming regression compresses/round-trips equal raw
outputs before retirement. Terminal storage cleanup retains necessary inputs,
receipts and recovery archives; archive member paths restore into the roots
recorded by retention journals. Current sources/programs/compiler/cache/link
identities are protected. No original target or user DOS package is deleted.

Final verified retention retires3,189 files across15 archive groups and
regenerable intermediates.1,391 protected hashes remain unchanged; net
764,350,464 allocated bytes (728.94 MiB) are reclaimed. `retention.json` and
`retention-journal.json` bind members, roots, costs and recovery.
