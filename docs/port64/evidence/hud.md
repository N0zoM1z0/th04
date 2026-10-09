# MAIN HUD owners and text consumers

v1318 component and v1319 bounded live join, 2026-10-09. Complete natural
routes and original physical displays remain unaccepted. This is not a DOS
exact claim. The pinned Japanese MAIN remains
`candidate-local-attested` (156258 bytes, SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`).
Preflight and MAIN database attestation are retained under root
`.analysis/ghidra/hud-v1318-*`.

`port64/hud.cpp` owns ordered initial labels, score rows, life/Bomb icons and
high-count labels, point/Dream/graze numerals, power and HP bars, all five rank
rows and the retained HP animator. `registration::TextPlane` now stores the
HUD's standard Shift-JIS labels as actual PC-98 character/attribute WORDs and
consumes their paired ROM halves, alongside its existing gaiji and ANK paths.
None of these functions consumes random state or advances on repaint.

Original instruction controls execute MAIN relative `0AAF:43F8..484B`,
`0AAF:6BA2..6BD3`, `13A9:6486..64DD` and `13A9:9A89..9AFE`.
Original `0000:1B0C..1BA5` gaiji kernels and `0000:22F6..2367` text_putsa
execute their stores and returns; no HUD or text ABI return adapter substitutes
for these bodies. Loads1000 and2000 agree on all requests, score HUD bytes,
retained HP, resident canaries and complete8000-byte TRAM banks.
DS8000, SS7000, resident9000, TRAM A000 and supplied starting fields are
explicit context adapters. Undefined original table/stack inputs are rejected.

Observed behavior retained:

- Lives subtract one in BYTE width before a signed comparison; zero and
  signed-negative results blank all five icons. Bomb's small-count comparison
  is unsigned, while its high-count digit arithmetic is signed BYTE.
- Dream multiplies by10 with WORD wrap. Count numerals use five positions
  and leading blank glyphs, without adding a score-style trailing zero.
- The generic zero bar draws a partial2F glyph. HP zero instead clears its
  label and all eight cells. HP rises one unit per call, falls directly to its
  computed target, and uses signed current/maximum with a32-bit numerator.
  hud_put's visual clear does not reset the shared previous value.
- Target DS1A68 contains five eight-byte rank rows, including EXTRA at1A88.
  The maintained DOS hud_data.asm currently defines four rows before its next
  declaration. This is an observed source/target gap to investigate if DOS
  HUD reconstruction is reopened; this native batch changes no DOS source.

Each GNU/optimized UBSan replay passes5926 cases:5564 isolated controls and
362 commands in two independent retained HP sequences (360 subsequent calls).
Full trace SHA-256 is
`65b434e364721d546345c8cdfb21f3263ed6ed7d6977fb30f38209aaafe87be9`;
47,408,000 TRAM bytes hash to
`a77bde1627a61c49ae4d01d4ae6cdbdf98f636a239aa6eb1d80e7ce885c9429f`.
Seventy-five complete TRAM/RGB controls compare58,200,000 bytes per host.
Their aggregate hash is
`60a395f137067d984e46e622a28e3283c9831f670c6e3a4ef286970cd10498c4`.
RGB uses the supplied hash-attested font/GAMEFT, independently addressed ROM
rows and explicit transparent-mask/video/background adapters; it does not
establish original physical pixels. Changing the zero-bar glyph to blank in
private authored source is rejected at original case798.

Replay from the native branch, always into fresh directories:

```sh
python3 port64/verify_hud.py --target ../../targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-hud-contracts \
  --hdi ../../runtime/images/zun.hdi --font-bmp PRIVATE_FONT \
  --output-dir FRESH_OUTPUT
```

Receipts: `.analysis/port64/hud-v1318/original-{linux,ubsan}-sequences/`.
These producer manifests remain distinct from the subsequent Game Over fixture
correction: only `gameover_frontend_checks.inl` changes; HUD binaries and all
four HUD producer sources remain identical. No receipt is restamped.
Existing200 Game Over renderer and158 registration snapshots also re-agree.
The first registration replay selected a retired expanded reference path;
the retained original reference is used for the successful replay.

The old Game Over failure fixture blocked startup before OP physically read
its scores. Merely moving that blocker later also failed to test a writer:
an unranked Continue with a valid file only reads, as the original dictates.
The revised fixture supplies an explicitly authored valid tied-zero score
file, selects Turbo through actual OP options, then blocks its owned directory
after MAIN entry. Its default Turbo was initially toggled off; exercising both
option changes retains the enabled state. These failed attempts remain
retained. The corrected GNU/optimized UBSan controls each independently replay
20 scenes at two original loads:322 complete displays and157 output files
agree, including both ranked writer failures before Continue reset.

## v1319 live MAIN and Continue join

`gameplay::State` now retains the complete text bank and shared HP previous
value. Its actual lifecycle, score/extend, per-slot item and per-bullet graze
events paint their owning HUD rows. Midboss calls use the shared previous and
emit their already animated result; boss requests supply raw signed HP and
maximum to the animator once. Stage initialization clears the displayed bar
without resetting the previous value. Repaint overlays these retained banks
through the same gaiji/ANK/Shift-JIS walker directly onto ARGB pixels.
Frozen Game Over copies the right HUD rectangle after the real Continue
resource/score events, preserving its menu and frozen playfield.

Fresh physical MAIN score loading precedes random-ring, drop and spark
initialization. The original `0AAF:81D7..81F4` wrapper subtracts A0 from the
selected highest eight digits with BYTE wrap; no normalization is added.
GNU original execution at loads1000/2000 passes3240 score controls/30980
records. Optimized UBSan consumes the independent original reference; these
two score executables remain byte-identical to their original producer.

`verify_main_hud_join.py` executes the original first-stage caller prefix
`0AAF:03E0..0488`, including gameplay_session_init, score_reset, hiscore_load
and stage_runtime_init, stopping at0489 before subsequent caller work.
All150 character/rank/seed/file cases pass at both relocated loads; current
GNU and fresh optimized UBSan physical HostStore/public MAIN construction agree
on complete8000-byte TRAM, local/highest digits, process RNG,256-byte ring,
drop cycle,96 spark angles, complete file bytes and commit count. Valid tails,
missing/short files and selected checksum low/high-byte changes are covered.
High-score repair consumes its draws before the later353 runtime draws.
Physical short files follow the documented host missing-file policy; original
DOS short reads remain separate component cases.

The initial probe incorrectly seeded BIOS `0000:0712` with4. Original
text_fillca uses `(last_row_index+1)*80`, so a25-row display requires24.
That failed TRAM observation, the four input controls and the corrected full
replay remain separate; the correction changes probe context, not original
instructions. Resource loading, palette, clipping and tile invalidation are
guarded adapters. This does not accept complete original MAIN startup or DOS I/O.

Twenty-four actual OP/authored finite-STD Game Over scenes agree with original
scene and text-store execution at both loads:386 complete displays,
398352000 bytes. Optimized UBSan matches this independent reference without
re-executing the original CPU. Four added character/repaint controls retain
three OP lives, lose two through actual contact, press X, then enter last-life
Game Over with lives/Bombs1/1; Continue restores3/2. Omitting only the Continue
Bomb HUD consumer in private source leaves logical events/files unchanged but
is rejected at snapshot171, refresh114, complete-stream byte176729888
(TRAM byte1888 within the snapshot's text bank). Prior input/fade/frozen-frame,
ranked writer-failure and single resumed suffix controls remain.
The initial frozen native display/font/hardware/audio/score-I/O adapters still
limit this to a bounded join, not an original complete interrupted MAIN frame.

Current GNU/optimized UBSan also match the retained5926 HUD traces/TRAM and75
complete RGB references through both RGB and ARGB paths; opaque ARGB alpha is
checked. Prior200 Game Over renderer and158 registration snapshots regress,
as do34 physical OP cases/6 registration-close Extra entries and24 Quit
routes/4 failed writers on both hosts. GNU's12 Bomb scenes/2724 frames/252
Bomb-layer captures re-agree with two-load original controls. Shared HP has
component/public-owner coverage; complete ordinary boss/Extra routes and their
full displays remain pending, alongside OP rankings/Music Room/demo/audio/config
and actual Windows/dense Lunatic timing. Every launch stays muted.

Replay the caller from the native branch into a fresh directory:

```sh
python3 port64/verify_main_hud_join.py --target ../../targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-live-contracts \
  --output-dir FRESH_OUTPUT
```

Current receipts, negative controls and product review are under
`.analysis/port64/hud-join-v1319/`. Source manifests preserve original producer
versus current consumer identities; no historical receipt is restamped.
Current builds contain123 AMD64 products/332 sources, with40 contracts per
executed Linux host. Current Windows interop still fails before PowerShell.
Git metadata remains read-only; complete source/evidence recovery is retained.

The v1318 final build review records123 AMD64 products/331 sources and40 CTests per
Linux host. Root/native CI and both diff checks pass;
Windows execution and Git writes remain rejected. Cleanup reclaims
241,385,472 allocated bytes (about230 MiB);20,293 protected files pass
hash readback. Completed captures are immutable aliases and replay outputs
must be fresh. Full v1308..v1318 recovery is under
`.analysis/port64/hud-v1318/recovery/`.
