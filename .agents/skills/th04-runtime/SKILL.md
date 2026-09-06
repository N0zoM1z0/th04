---
name: th04-runtime
description: Build and run deterministic TH04 runtime differential scenarios across PC-98 emulators using input, memory, event, VRAM, palette, audio-state, and metamorphic checkpoints. Use for behavioral validation, hardware/timing ambiguity, or portable-runtime preparation.
---

# TH04 runtime differential validation

Read `docs/ORACLES.md`.  Runtime evidence supports semantics but never waives a
byte mismatch.

## Scenario requirements

1. Pin target/candidate artifacts, game-data image, emulator build/config,
   starting save/config files, clock, memory, sound mode, and input timeline.
2. Prefer deterministic frame/tick checkpoints over wall-clock sleeps.
3. Capture raw memory summaries, file and interrupt/I/O events, RNG/state
   variables, planar VRAM, palette, and PMD/MMD state before rendered media.
4. Replay original and candidate from identical reset snapshots.
5. Repeat on DOSBox-X and a debug Neko Project II build; label emulator-specific
   observations.
6. Add one-variable metamorphic runs for load segment, EMS availability, CPU
   timing, GDC rate where supported, sound mode, or data path.
7. Store bulky traces under `.analysis/`; check in scenario definitions,
   digests, reducers, invariants, and concise conclusions.

Do not compare screenshots alone and do not infer general equivalence from one
successful play path.
