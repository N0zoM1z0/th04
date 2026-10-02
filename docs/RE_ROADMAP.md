# TH04 build roadmap

Current goal: independently build and run the Japanese PC-98 game from the
checked-in source. Built executables need not be byte-identical to originals.
MAIN's carpet and checkerboard exactness cases are deferred indefinitely;
leave their ledgers nonexact. ReC98 implementations may be extracted and
adapted for local TH04 source and ABI ownership.

Use [RE_HANDOFF.md](RE_HANDOFF.md) for live build commands and blockers.
`python3 scripts/status.py` reports historical function acceptance, currently
OP 93/93, MAIN 493/495, MAINE 72/72, ZUN 3/3. This is separate from playable
product completion.

## Completion requirements

- Every product compiles/links from checked-in TH04 source and generated local
  inputs with the pinned Borland tools; no ReC98 source/header build dependency
  or historical master.lib is needed.
- ZUN, OP, MAIN and MAINE work together in a disposable original-data image.
- Menu/setup, gameplay input and rendering, stages/bosses, sound, game-over,
  endings/staff roll and score/config persistence have recorded runtime checks.
- One documented build entrypoint produces all four deliverables, reports
  failures, and can be rerun from a clean output directory.
- CI and source dependency checks pass. Existing exact ledgers remain truthful;
  native behavior work never automatically promotes a historical unit to exact.

Keep new documentation short. Prefer fixes, executable probes and concise
handoff updates over versioned session narratives.
