# TH04 native branch handoff

Both final CIs pass, including root live Ghidra replay/mutations. Final readback
checks 8,640 retained hashes. Post-CI cleanup separately retires 1,014 public
source-backed Python caches and preserves their source hashes, reclaiming
16,433,152 allocated bytes net. Cache journal/receipt:
root `.analysis/cleanup/audio-output-post-ci-caches-v1353{,-before}.json`.

Updated 2026-10-10. Current phase: host transport is implemented and fake-API
verified; continue physical timing/input, dense Lunatic and GUI delivery.
Native source remains on `port/modern-64`; DOS acceptance remains separate.

## Verified frontier

v1353 builds 201 AMD64 programs cold from 475 inputs; GNU8, optimized UBSan
and actual Windows pass 66 contracts each. Production SDL/WinMM audio transport
owns one lazy application device. Resident mixed stereo is submitted once;
nonresident mono is duplicated. Queue bounds/failures never clock the game.
Default output stays muted, interactive `--audio` is opt-in, and `--mute` wins
in either argument order. Every game/check replay stays muted; deliberate
unmuted diagnostics reject before entry. All device API/PCM transport tests
use explicit fakes. No physical backend/device was opened.

Three driver profiles by nine settings preserve 195 complete frontend files
per host against the preceding GNU producer. Two real Continue regressions
preserve 16 captures and physical final files per host. All preceding 103 GNU
and 103 MinGW core objects are raw-equal. Three wrong transport variants and
four early CLI controls reject. MinGW test typedef and Windows mutable-input
plan failures remain; corrected fresh runs pass. Current source manifest:
`95ce37f3cfd2a17ec3547e38f5aae71226b2616623e0a79b6cada1772f66ec36`.

Replay and ownership: [host output](port64/evidence/audio-output.md),
`port64/verify_audio_output.py`; receipts `.analysis/port64/audio-output-v1353/`.
Independent compiled materialization is `../port64-audio-v1353-fix/`.
Three recovery archives retain terminal candidate intermediates, both owned
Windows stages and final static link inputs. Two cleanup passes report
1,494,827,008 allocated bytes reclaimed; all 1,915 members and protected hashes
read back. Current/preceding programs, frozen sources and failed evidence stay.

## Earlier accepted scopes

- v1352: two ordinary 1,551-advance Continue/quit/registration/fresh-OP cases
  per host, ranked/unranked files and two-load original Game Over component
  replays (58,424 requests under documented adapters).
- v1351: four ordinary A routes on three hosts (270,193 advances/49 captures
  per host), Normal-earned saves admitting fresh Extra; separate GNU full
  Hard/Reimu B. Their source vector remains `e3448a63...`.
- v1350: complete supplied music, 138 original two-load cases/69 unique native
  runs/1,654,542 configured rows per host; corrected terminal window repaint.
- v1346/v1347: original startup control/pixel component corpora, distinct from
  full startup across sound modes or physical host timing.

[Current and historical scopes](PORT64.md), [lifecycle](port64/evidence/stage-lifecycle.md),
[music](port64/evidence/pmd-musical-fm.md), [startup](port64/evidence/op-startup.md).
Previous receipts retain their own producer/source identities.

## Remaining gates

Full startup across sound modes, remaining rank/shot/Continue routes,
physical input/refresh/slowdown, dense Lunatic timing/performance, physical
sound-device validation and current GUI delivery remain. Last installed native
GUI is v1296. General semantic renaming is paused unless a concrete port owner
is blocked. No whole-original-route, whole-game, physical audio or DOS exactness
acceptance follows. Target provenance stays `candidate-local-attested`.

## Finish and replay

```sh
python3 scripts/preflight.py
python3 scripts/ci.py
git diff --check
```

Use fresh output directories. Keep one Borland/Wine writer and preserve pinned
inputs, source/program vectors and recovery archives. Commits use English
`gpt-6.1-sol: ...`; push this native branch separately from the root index.
