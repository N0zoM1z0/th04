# Native PMD hardware rhythm ownership

v1339 joins hardware rhythm to the existing musical FM/SSG/effect owner.
GNU8, optimized UBSan and actual Windows each compare **199,266 complete
original rows**: 174 primary cases/172,434 rows and 24 supplemental cases/
26,832 rows, at PSP segments `1000` and `2000`. Each host passes 58 contracts.
Windows executes 99 unique traces/99,633 rows and compares them with both
original PSPs. 422 maintained inputs bind 177 AMD64 products (59 per cache).
All runs are CPU-only and muted; no audio backend/device opens.

This recovers chip requests and driver state, not synthesized rhythm samples,
physical clocks or complete natural music/game routes. FM3/PPS/ADPCM,
synthesis, frontend capability/real measure waits and logo/startup remain.
Native evidence never promotes DOS exactness. Target provenance remains
`candidate-local-attested`.

## Target and observation identities

The unchanged Japanese HDI has SHA-256
`0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd`.
The auxiliary drivers are flat COM files, with entry `PSP:0100` and resident
service `PSP:0103`; they have no MZ header/relocation table.

| Driver | Size | SHA-256 |
| --- | ---: | --- |
| PMD.COM | 20379 | `cbbe9bd610aedda586d8bd7f6dd13d21f037a089458a21ddda0b11a53b4b29e4` |
| PMD86.COM | 28871 | `34b7381d66400b89fca833e08fb30f315b9092eb3883f137538dcf18477fd77f` |
| PMDB2.COM | 25730 | `dfebbfd6e82916dfc4d8d01f2fcd938e215cc16cbd5ce2f19bce37cdc3841437` |

Private receipts are below `.analysis/port64/pmd-rhythm-v1339/`. The primary
original producer manifest is
`80a9f3f39be923477bbdfdb6bb1ef66ae96f5321d8353b6870f9096f83a83501`;
the final consumer and supplemental producer manifest is
`2dda95c473d5aeb8fa27e062f630a3f67aa47ec65b5bc9a6fc39e91b8519e256`.
Separate complete source archives preserve those identities. Supplementary
original execution uses unchanged COM code and authored music buffers, not
the native implementation. Original injected IRQs, DOS, board/readback and
calibration adapters retain [their existing limits](pmd-driver.md).

Capstone raw views are target evidence, not independent semantic Oracles. No
COM database or target executable is modified. The root OP database was
attested before target work; root CI also re-attests MAIN and its negative
database controls. GNU8/MinGW13, Unicorn engine, cache/link and product identities
are recorded in the producer receipts and `product-profile.json`.

## Recovered ownership

All addresses below are PMD86.COM offsets relative to the recorded PSP segment.

- Rhythm parsing at `1502..1646` selects 14-bit requests. Track mask/rest clears
  the last request. Eleven drum bits choose semantic voice/pan/level tuples;
  unused high bits can still request built-in SSG effects. The drum map starts
  at `4062`; PMD.COM/PMDB2 use a different table-relative displacement.
- The eighth drum bit writes voice 3's pan/level, emits key `84` to stop voice 2,
  then key `08`. Hardware writes precede the built-in SSG effect request.
  Macro drums do not update stored levels, active keys or explicit-key counters.
- Commands EB/EA/E9/E8/E6/E5 retain original byte arithmetic and ordering.
  Explicit EB key-on restores selected stored levels before the key request;
  key-off only writes the key. Selected on/off counters wrap as bytes and
  survive music restart. EB is a global command even when the issuing musical
  part is masked. Macro track masks remain separate.
- EA/E9 packed indices 0 and 7 alias active-key and total-volume storage;
  indices 1..6 own the six stored pan/level bytes. Register mirrors and stored
  command fields are separate. E5 preserves the upper three bits; E6 and E5
  wrap their additions before the target's bit-7 clipping rule. Indices above
  7 are not accepted as arbitrary original memory aliases.
- C0 F9/F8 set, adjust or restore rhythm attenuation. E8 scales its stored
  total by attenuation, then scales the emitted register value by music fade.
  E6 updates the stored total directly. FM26 keeps disabled hardware rhythm
  state and skips hardware commands, while the shared attenuation commands
  still execute.
- Start resets gain to its installed baseline, clears active keys/request,
  initializes the six stored levels to CF and total to attenuated 48 on enabled
  boards, then writes `10=FF`, `11=total` after the FM LFO reset. Stop leaves
  rhythm globals intact; explicit key counters survive restart. FM26 retains
  its disabled-board defaults.
- Negative fade underflow at `30B7..30D2` clears fade/speed and calls `24D4`
  to restore the stored total before Timer A effect processing. Exact zero
  does not take that call. Read-only execution at both PSPs records the call
  through `30CF` and `11=35` at END1 row 933. The initially missing write
  rejects the first native candidates; `Sequence::fade_restored` now delivers
  the ordered hardware callback.

The comparison preserves all previous FM/SSG fields and fade globals, then
adds the rhythm track, attenuation/baseline/mask/enabled/active/total/request,
six stored levels, twelve counters and primary mirrors `10..1F`. Every owned
FM/SSG/rhythm write remains in chronological order with bank and duplicates.
Primary rows have count columns 1130 (FM26) or 1136 (other boards).
3,306 primary full-service snapshot crosschecks pass; supplemental rows use
the original service observer throughout.

## Coverage and counterfactuals

Primary inputs include all 23 supplied songs per format and six authored
resources, across all three drivers. RHYMACRO exercises drum bits/retrigger;
RHYMASK exercises masked requests; RHYFADE exercises fades; RHYFM/RHYSSG/
RHYTRACK issue global commands from three different part owners.

The primary timeline restarts after 256 ticks and does not reach every command
tail. Supplemental 512-tick intervals execute the complete long command
programs, including all EB bytes, EA/E9 indices and pans, E5 deltas, attenuation
and E8/E6 controls. RHYBOUND explicitly exercises total `255+1`, total
`200+100`, level `31+255` and its subsequent byte overflow. Full rows agree
at both PSPs and on all three hosts; no field/write exclusion is introduced.

| Source-only counterfactual | First rejected row |
| --- | ---: |
| Omit negative-fade total restore | END1 933 |
| Omit hat retrigger stop | RHYMACRO 22 |
| Clear explicit counters on restart | RHYFM 374 |
| Widen total addition before clipping | supplemental RHYBOUND 1 |
| Widen voice-level addition before clipping | supplemental RHYBOUND 3 |
| Ignore macro track mask | RHYMASK 1 |
| Emit hardware rhythm after SSG effects | RHYMACRO 1 |

GNU/UBSan also replay v1338's 101,082 command rows, v1337's 489,390 combined
rows and all retained musical SSG/FM, FM handover, short/long sequence,
effect and sharing corpora. Original receipt identities remain unchanged.
Linux frontend products retain their previous binary hashes. MinGW relinks
have new identities and current CPU controls; this batch launches no GUI and
does not extend v1332's bounded frontend/storage claims.

## Diagnostic results retained separately

- The first reference view normalized rhythm positions against the EFC base
  instead of the music base, shifting positions by 8192. Its producer was
  identified, stopped, and confirmed terminal (143); 60 complete gzip captures
  remain with an inconclusive receipt. Fresh `original-v2` fixes the view.
- The first table-relative drum-map read used the FM86 displacement on FM26/B2.
  Corrected raw profiles agree on semantic tuples; the initial view remains
  inconclusive. The initial dispatcher scan also omitted FM26's B2 lower bound.
- Widened-add and signed-clamp mutants initially equalled the short RHYFM
  corpus because its command tail was not reached. Those results are
  inconclusive, not proofs of correctness. The longer producer supplies the
  independent discriminating input; widened additions now reject.
- A private Windows recipe adaptation named a nonexistent cache and changed
  the `st_blocks` multiplier. Both helper/log versions remain. The completed
  byte readback is valid; space accounting is corrected from every persisted
  action using 512-byte blocks in `cleanup-windows-stage-accounting.json`.

The earlier FM3 usage probe executed all 23 supplied M86 songs for 1024 IRQs
and observed 6467 hardware-rhythm writes with no selected FM3-extension
handler entries. That changes priority only; it proves no absence over full
songs, other drivers or complete game routes. Its source/profile/raw evidence
remains under `.analysis/port64/pmd-fm3-v1339/`.

## Replay and retention

From the native worktree, use fresh output directories:

```sh
python3 port64/verify_pmd_rhythm.py --hdi ../../runtime/images/zun.hdi --output NEW_ORIGINAL
python3 port64/verify_pmd_rhythm.py --reference NEW_ORIGINAL --binary .analysis/port64/linux-live-v1251/th04-port64-pmd-rhythm-contracts --output NEW_NATIVE
```

The retained supplemental source, `supplement.py`, defines its complete input
timeline and authored resource; `supplement_consume.py` compares both native
hosts. Typed Windows plans use `verify_windows_current.ps1` and full input/
product hashes. Source-only variants, compile commands, failed streams and
complete source archives remain recoverable. Historical writers reject or
must avoid existing immutable capture paths.

Full archive/trace readback checks 3915 protected hashes. Persisted journals
measure **850,616,320 allocated bytes** reclaimed (about 811 MiB), including
terminal raw copies, counterfactual executables, two owned Windows stages and
557 CMake objects/static archives. All 177 products, independent original
references, sources and failed/inconclusive observations remain. Raw successors
are losslessly compressed and verified; CMake recreates absent intermediates.

After both final CIs pass, a source-backed cache journal retires 1015
generated Python caches, reclaims another 17,125,376 allocated bytes,
and verifies 1015 unchanged Python source hashes. Measured batch
total is 867,741,696 bytes (827.5 MiB). Receipt:
root `.analysis/cleanup/pmd-rhythm-post-ci-caches-20261010.json`.
