# Native PMD running FM music and external effects

v1335, 2026-10-09. `FmPlayer` joins the separately verified `MusicalFm` and
`FmEffects` owners. Their ordered requests share one logical register mirror;
external effects borrow the final musical FM channel. No executable code,
CPU interpreter or recorded-playback array enters the native implementation.

GNU8, optimized UBSan and actual Windows AMD64 each compare **427,308 complete
original-backed rows**, with all 54 component contracts passing per host.
There are 407 maintained source inputs and 165 AMD64 products, 55 per cache.
This accepts the bounded FM ownership join. Musical SSG/FM3 extra subtracks,
ADPCM/hardware rhythm, synthesis, physical clocks, frontend PMD capability,
complete startup and full natural routes remain unfinished. All launches stay
muted; no audio device/backend is opened. DOS acceptance and the known
`candidate-local-attested` provenance gap remain unchanged.

## Original evidence and ownership

Unchanged PMD.COM, PMD86.COM and PMDB2.COM are read from the pinned HDI;
[the musical FM note](pmd-musical-fm.md) records their full size/SHA identities.
These are auxiliary flat COM programs, PSP:0100 entry/0103 service, with no MZ
header or relocation table. Each reference records PSP load1000 or2000.
Raw anchored Capstone views guide hypotheses; original CPU execution under
the recorded Unicorn build supplies the native comparison. A disassembler
view is not an independent second Oracle, and no target is patched.

PMD86.COM masked FM body PSP:12F1..1364 decrements the remaining length and
clears mask bit2 only at a parse boundary after the effect becomes inactive.
The external effect start at PSP:3962 borrows part5; stop at PSP:39C4..39F6
marks it inactive, silences it and, when music is playing, invokes the musical
voice restoration at PSP:1AA8..1B18. Voice parameters and noncarrier total
levels are restored immediately; music continues only at its next parse
boundary. Restoration emits no premature key-on. The native occupation mirror
is synchronized from the canonical sequence masks after each operation.

PMD.COM borrows part2 and retains bit2 in disabled parts3..5 (mask34 rather
than32), including across restart. Its masked voice path PSP:1447..1492 stores
the surviving AL voice ID in the part algorithm field, while PSP:3193 keeps
the actual FM3 algorithm. The separate global resets at music start and is
used during restoration. This observed distinction must not be normalized
into one supposedly cleaner algorithm field.

Stopping music leaves the occupied effect channel's release-rate/key registers
untouched. Starting music while an effect runs preserves the final86/B2 pan,
while26 still emits all three startup pan writes. Effect completion restores
pan only on86/B2. Rest/repeat-last handling preserves low-nibble15 as rest;
masked DA consumes its original byte without inventing a portamento note.

For86/B2, pan/PMS commands update the musical field but skip hardware requests
while masked. PMD86.COM E1 at PSP:1FF1..2039 checks work mask at PSP:2026;
EC at PSP:2363..23B3 checks it at PSP:239E, and C3 at PSP:23C1 branches into
the same handler. PMD.COM ignores these commands through its attested dispatch
entries. The SHARE2 restart row4697 rejected the initial extra B6 request.

## Comparison and observer controls

Four supplied songs (LOGO, OP, ST05B, STAFF) and three independently authored
sharing/delay/voice fixtures per format execute through all three drivers at
both PSPs:42 cases,10,174 rows each. Every timeline starts music, tries all17
MIKO effects, repeats/replaces effects, issues explicit stops, stops/restarts
music during effects, and applies positive/negative fade. It includes B-only,
zero-status, A-only and simultaneous interrupts; original Timer B precedes A.
There are244,176 supplied-song and183,132 constructed row comparisons per host.

Each row retains all five musical globals, six72-field musical FM parts,
272 owned mirror cells,42 external-effect fields, and every ordered owned FM
write. Owned mirrors include both banks30..B6 and primary22/28. No owned field,
mask bit, mirror or event is excluded. Musical SSG, extra FM3 subtracks,
ADPCM/rhythm, global timer ACK requests, physical chip behavior and audible
samples remain outside this comparison.

The producer caches published work/resource pointers and reads the globals
returned by services500/800/A00 at independently attested offsets. Every
control operation and every257th interrupt compares the **entire selected row**
against the actual service-based observer. Original interrupt execution is
never replaced. The receipt records the crosscheck count and pinned engine.

During a positive fade, PMD86.COM PSP:0612 emits byte A8 to portA466 at
row10110. The adapter now records that external board-volume seam; it does not
simulate physical PCM. With the revised observer, all earlier original music,
constructed music, SSG, sharing and FM effect corpora replay completely and
remain byte-identical to their immutable v1331/v1333/v1334 references. Older
receipts retain their original tool/source identities.

The producer archives its whole starting source before execution and freezes
all Python producer tools until completion. Native C++ may advance with its
own archived consumer identity; the original does not derive expected state
from those hypotheses. Final consumers bind the complete current source.

Actual Windows executes21 CPU-only traces/213,654 unique rows, whose bytes are
read back and compared against all42 original cases for427,308 comparisons.
All55 PE32+ product hashes and inputs are checked before/after execution;
imports remain limited to the recorded system DLLs. No GUI launches occur in
this batch. Earlier bounded frontend receipts keep their own identities.

## Negative results and replay

The first producer rejected an unhandled A466 write. Its partial output and
original tool archive remain. A later authored fixture accidentally encoded
note77 (pitch13) in part5, outside the ordinary chromatic profile; native
normalization and the target's raw table access disagreed. That producer was
deliberately stopped for the fixture defect, with exit143 confirmed. Its21
closed traces, one excluded partial trace, authored resources, source archive
and rejecting consumer remain. The accepted fixture uses69+p, all ordinary
pitches. Neither target nor comparator was changed to make the invalid note
appear equivalent.

Three source-only counterfactuals reject the complete LOGO.M26 reference:
omitting musical voice restoration at row78; clearing mask2 immediately at
row78; and overwriting the borrowed release-rate/key registers when music
stops at row522. Full base source, variant code/build/compiler/binary hashes,
complete failed traces and first differences remain. Targets/references stay
unchanged. The masked-pan development rejection is independently retained.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_fm_player.py \
  --hdi ../../runtime/images/zun.hdi \
  --output .analysis/port64/pmd-new/fm-player-original
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_fm_player.py \
  --reference .analysis/port64/pmd-new/fm-player-original \
  --binary .analysis/port64/linux-live-v1251/th04-port64-pmd-fm-player-contracts \
  --binary .analysis/port64/ubsan-live-v1251/th04-port64-pmd-fm-player-contracts \
  --output .analysis/port64/pmd-new/fm-player-native
```

`verify_windows_current.ps1` accepts a typed `pmd-fm-player` plan including
separate music/EFC inputs. Run its owned NTFS copy with `-NoProfile -File`;
no execution-policy override is used. Private current receipts live in
`.analysis/port64/pmd-fm-join-v1335/` with distinct original/consumer archives,
full compressed traces, product/cache/link/compiler profiles, observer replay,
GNU/UBSan musical/sequence/SSG/effects regressions and Windows readback.
Terminal cleanup persists its journal before mutation and rechecks protected
identities afterward. Shared captures are immutable; use fresh replay paths.

Next finish the remaining musical chip owners and synthesis while muted,
then physical clocks/frontend capability/startup and complete ordinary/Extra
Linux/Windows routes, saves/restarts and dense Lunatic timing/performance.

Final whole-output readback verifies1569protected hashes; persisted interim/
terminal cleanup journals measure1,401,487,360allocated bytes reclaimed (1336.6MiB).
Both repository final CIs and `git diff --check` pass.
