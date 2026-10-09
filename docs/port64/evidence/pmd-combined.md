# Native PMD combined FM and SSG requests

v1337, 2026-10-10. The running musical FM/SSG owner and both effect owners
now share a comparison of their state and chronological chip requests.
Native `FmPlayer` exposes built-in SSG effect admission/stop alongside external
FM effects; musical recovery still happens at each masked parse boundary.
Diagnostic serialization is shared between the separate and combined checkers,
while the implementation retains typed state without target work addresses.
No CPU interpreter, executable byte arrays or recorded playback enter the
product. All launches remain muted and open no audio device/backend.

The configured combined comparison covers four supplied songs and seven
independently authored mixed modulation/occupation fixtures per format,
through26/86/B2 at PSP1000 and2000.66 cases of7415 rows compare489,390 complete
rows per host;33 native executions produce244,695 unique rows. The acceptance
claim is bounded by those resources and control inputs. FM3 extra tracks,
ADPCM/hardware rhythm, additional driver commands, synthesis, physical clocks,
frontend capability/full startup and complete natural routes remain separate.
No DOS exactness or target provenance promotion follows.

## Target and comparison ownership

The pinned Japanese candidate-local-attested HDI and auxiliary PMD.COM,
PMD86.COM and PMDB2.COM retain their independently checked full size/SHA
identities; see [musical FM](pmd-musical-fm.md). The auxiliary targets are flat
COM programs with PSP:0100 entry and0103 service, no MZ header or relocations.
A fresh OP Ghidra identity check passes in the root checkout. Raw anchored COM
instruction views and original CPU/memory/I-O observations remain distinct
from native source hypotheses. No database or target byte is edited.

Every combined row has the prior751-field FM view (five musical globals,
six72-field musical FM parts,272 mirrors and42 external-effect fields), followed
by the prior322/328-field SSG view (globals, full96/98 work bytes for each of
three parts,11 built-in effect fields and14 mirrors). The count and all
chronological `(bank,address,value)` requests follow. Only original resource/
work pointers become relative. FM-owned registers are bank30..B6 plus primary
22/28; SSG-owned registers are primary0..13. Bank identity, duplicate writes,
mask bits, envelope counters and order within the union remain compared.
Hardware timer ACK, ADPCM/rhythm and other unowned requests remain outside.

Four supplied songs are LOGO, OP, ST05B and STAFF. Seven mixed fixtures have
FM and SSG parts active together, two LFOs, all seven shapes, synchronized
clocks, depth counts, notes/rests/ties/slides and distinct voice/PAN delays.
Their rhythm track starts a built-in effect. Control timelines run all17
MIKO FM effects and all40 built-in SSG effects, priority rejection/replacement,
explicit stops, music stop/restart while either effect runs, positive/negative
fade, zero-status, A-only, B-only and simultaneous interrupts. They preserve
Timer B before A, the shared random stream and the original musical Timer A
baseline. No original asset or executable is modified to create these fixtures.

Producer Python tools freeze while original CPU execution runs. Its whole
starting source is archived before execution; C++ may advance under separate
consumer archives. Cached published views are checked against full original
service observations at every control operation and every257th IRQ
(27192 full-row crosschecks). Original
execution is never replaced with native logic. Receipts retain their own
source, compiler, engine, target, resource and output identities.

## Recovered restart and command boundaries

The first combined candidate rejects LOGO.M26 row6613: music restart during
built-in effect24 emits an extra noise6=0 and changes the previous-noise cache
from29 to0. Original PMD86.COM PSP:0F8C resets requested musical noise, then
PSP:0F91 tests effect priority at PSP:0D73; PSP:0F96 skips the noise6 write and
cache reset at0F98..0F9E when the effect remains active. Direct original probes
confirm preservation during active priority1 and priority2 effects on all
three boards. Inactive restart still writes6=0. The native guard preserves
requested versus previous-hardware noise, including the ordered write seam.
See [musical SSG](pmd-musical-ssg.md) for the earlier frame/sweep cache boundary.

Direct original service300 admits an SSG effect and sets channel-C mask2 only
when priority admission succeeds; service400 stops it without clearing that
mask. PMD86.COM PSP:0C3B..0C65 performs the priority check and sets work mask
at0C5A; musical recovery remains delayed. The native service API retains that
behavior and shares the effect register mirror with running music.

Legal mixed music exposed an unsupported FM B7 depth-count command. PMD86.COM
FM dispatch entry PSP:16F6 points to1EB3. Its handler selects the secondary LFO
with bit7, uses low7 as the count and maps zero toFF; the two current/initial
counts occupy work51/52 or53/54. Musical FM now handles the same attested
semantics already recovered for SSG. Source-only unsupported-command failure
and complete early candidate traces remain recorded; fixtures are not weakened.

## Counterfactuals and regression

Source-only variants reject the unchanged complete combined reference:
unconditional active SSG noise reset at row6613; an independent SSG LFO random
stream at MIX3.M26 row2; and Timer A before B at MIX1.M26 row1. Full base and
variant source/compiler/build/binary identities, first differences and complete
compressed rejecting outputs remain.

An initial random counterfactual changed only SSG's gate-random callback.
M26 has no random gate command, so its MIX3.M26 trace remained identical:
that trial is **inconclusive** for LFO sharing. LFOs use the shared advance
callback; the accepted final counterfactual intercepts that callback and
rejects. The initial source, binary, identical output and failed proof script
remain. Neither a passing wrong-path mutation nor a failed assertion is
reported as comparator acceptance.

The extracted diagnostic serializers retain the entire prior FM and SSG
outputs. GNU/UBSan replay134,274 supplied and58,380 constructed SSG rows;
427,308 FM handover rows;134,274 supplied and40,866 constructed musical FM
rows;134,274 short/49,164 long sequence rows;3,942 SSG sharing,79,488 SSG effect
and30,192 FM effect rows. Original references and older receipt identities
remain unchanged. Actual Windows executes the current56 component contracts
and33 combined CPU-only traces, with57 PE products and inputs hash-guarded
before/after and recorded system DLL imports only. This batch launches no GUI;
prior bounded frontend receipts retain their documented limits.

The Windows plan can use all33 **closed first-load** original captures while
the second PSP still executes. A distinct snapshot binds those inputs and the
producer source archive; it does not claim the original aggregate is already
terminal. Final readback requires the completed66-case receipt and compares
all Windows bytes against both original PSPs. No process is restarted because
an observation timed out.

## Replay and remaining work

```sh
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_combined.py \
  --hdi ../../runtime/images/zun.hdi --output .analysis/port64/FRESH/combined-original
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_pmd_combined.py \
  --reference .analysis/port64/FRESH/combined-original \
  --binary .analysis/port64/linux-live-v1251/th04-port64-pmd-combined-contracts \
  --binary .analysis/port64/ubsan-live-v1251/th04-port64-pmd-combined-contracts \
  --output .analysis/port64/FRESH/combined-native
```

Actual Windows uses the typed `pmd-combined` plan with separate music/EFC
inputs and an owned NTFS copy of `verify_windows_current.ps1`, invoked with
`-NoProfile -File`. Private receipts, distinct original/consumer archives,
complete compressed references/outputs, source/product/cache/link/compiler
profiles, raw anchored views, negative probes and pre-mutation cleanup journals
live under `.analysis/port64/pmd-combined-v1337/`. Current executables, sources,
independent references and necessary failed evidence remain protected.
Terminal raw copies, Windows staging and rebuildable native objects/archives
retire after full equality/readback. Future writers use fresh output paths.

Continue with additional SSG command ownership, FM3 extras, ADPCM/hardware
rhythm and synthesis while muted, then physical clocks/frontend capability/
complete startup and full Linux/Windows ordinary/Extra routes, physical saves/
restarts and dense Lunatic timing/performance. Bounded component results and
actor controls do not establish full natural survival. The full goal stays active.

Whole archive/trace readback verifies 2111 protected hashes; persisted
pre-mutation journals reclaim 1,112,240,128 allocated bytes (1.04 GiB).
The original producer and both Linux consumers are terminal and pass; final
Windows readback covers all 66 cases after the second load completes.
