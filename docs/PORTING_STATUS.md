# Semantic and x64 port status

Tracking issue: [#1](https://github.com/N0zoM1z0/th04/issues/1).

Updated 2026-10-08. Native development has resumed. DOS semantic work merges with the
DOS baseline; unfinished native source remains on `port/modern-64`.
General readability expansion stops here unless a specific port contract
cannot be represented safely. Native executable bytes need not be exact.

## Completed

- Semantic contracts: PI/PAR/CDG/BFNT, segmented heap, input/IRQ timing,
  scroll/tile ring, bullet angles/groups, enemy script VM, shots/items,
  process handoff, ranking, random ring and process-local LCG. See
  [the bounded semantic results](SEMANTIC_READABILITY.md).
- Linux SDL2 and Windows Win32/GDI frontend; private original HDI/PAR/CD2/PI
  resources, OP main/options/selection state and fixed-width resident handoff.
- Normal Stages 1–6 waves, both Stage 4 character bosses, stage bosses/dialogues/
  departures, Yuuka lasers/crosses/checkerboard, score/extends. Implemented and
  bounded component/integration controls exist; full game acceptance is pending.
- All eight Ending script/graphics routes; Staff Roll, verdict and
  congratulations integrated into normal-route preview controls (v1296).
- Score-file core (v1297): 1,288 original CPU cases, including ten-section
  recreate/re-key and retained RNG/unused-byte behavior.
- Registration logical owner (v1298): 382 original CPU cases, input repeat/lock,
  partial-name Esc save and retained decoded render requests.
- Registration graphics/text (v1299): 158 complete two-page/palette/TRAM/RGB
  captures agree on GNU, Wine, optimized UBSan and actual Windows. Explicit
  hardware/ROM/PI/return adapters limit the original-execution claim.
- Registration scene/save (v1300): ordered refresh/input/render/I-O boundaries,
  separate host score commits and fresh OP/second MAIN. Thirty seeded fixtures
  per GNU/optimized UBSan/actual Windows produce 112 identical output files;
  original fades agree at two loads (35-refresh in/18-refresh out).
- Current native builds: 34 AMD64 products and 33 contracts per GNU/MinGW/
  optimized-UBSan build. Actual Windows contracts and current component captures
  also pass. This is not full routes, physical hardware, audio or DOS exactness.

## Remaining, in order

- [x] Join registration requests to the scene with original ordered waits,
  fades and explicit keyboard actions; retain pre-save decoded snapshots.
- [x] Persist a separate host score file at the real save boundary, then
  return to fresh OP. Cover no-entry, Esc, full name, corrupt/missing file,
  both characters and all score sections. Do not overwrite DOS saves.
- [ ] Complete Bomb, hit/death/lives, game-over and Continue transitions.
- [ ] Port Extra gameplay/boss; a tested Extra postgame dispatch is not Extra play.
- [ ] Complete HUD, OP score/Music Room/demo/unlock flows, audio, configuration
  and refresh/input integration. Account for deliberate slowdown separately.
- [ ] Run complete ordinary routes on actual Linux and Windows, both characters,
  difficulties, good/bad endings, Extra and score/config persistence; benchmark
  dense Lunatic scenes and compare original behavior with explicit adapter scope.
- [ ] Independently replay historical exact scaffolds if exact acceptance is
  reopened. MAIN's two deferred cases are not a native-port prerequisite.

## Published preview versus retained source

The last published Windows `th04-port64.exe` and launcher were
**v1296-congratulations**, with `previous-v1295` rollback. Those packages were
archived outside the DOS demo directory on 2026-10-08. That GUI reaches
`registration_pending`; current v1300 source joins registration/save with
seeded child-scene controls. Full natural routes and a new published GUI remain
pending. Native commits `43946c3` and `6c90c1a` are pushed on `port/modern-64`.
DOS testing scripts/saves are separate. All new launches stay muted.

The native branch's [PORT64.md](https://github.com/N0zoM1z0/th04/blob/port/modern-64/docs/PORT64.md)
routes detailed component contracts and replay receipts. Its evidence and
knowledge ledgers are branch-local; root DOS ledgers do not inherit native
acceptance. Private tools/assets are required for original CPU controls.
