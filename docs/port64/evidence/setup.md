# Native first audio setup

v1324, 2026-10-09. Missing, short, bad-checksum or unsafe host configuration
now requests the actual two-menu OP setup before score reading or ordinary
menus. All application launches remain muted; no audio backend is opened.
This accepts bounded setup behavior and its native integration, not full
original startup, audible playback, complete natural routes or DOS exactness.

## Target and ownership

Pinned OP is 42290 bytes, SHA-256
`8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f`.
Its restored 69028-byte payload is SHA-256
`13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`,
with 804 relocations. Preflight and packed OP/ZUN database checks pass;
canonicality remains `candidate-local-attested`. Relative segments identify
addresses below; CPU load segments are 1000 and 2000.

Original OP setup executes 0A74:0D5F..1304, input release/press wait
0DA1:0152..01A7 and fades 0000:0622..06A2. Original instructions determine
window geometry, roll animations, default selections, wrapping, confirmation
priority, waits, palette tones and resident writes. Guarded file, PI/BFNT,
graphics, SUPER, EGC, input and refresh consumers remain explicit adapters.
Unexpected consumer calls reject the comparison. Captions/help/choices are
legitimate target UI data; the maintained implementation contains no copied
instruction arrays. DATA 0F34:A3C initially selects text effect 2.

BGM starts at stereo FM86 (2); UP increments and DOWN decrements. SE starts at FM (1)
with the opposite arrow direction. OK/SHOT confirmation precedes both retained
arrow tests. Esc is ignored. The wait first requires release, then accepts a
press indefinitely, OR-ing its before/after refresh samples. Help rolls up
before the choices, then mode selection publishes. A caller delay and page
copy separate the menus. Final blackout precedes sprite freeing.

Fresh static observations at OP 0A74:0C7C..0CA9 show the rankFF test, setup
call, rank=Normal publication and sound-mode re-detection call. This is
`observed` target code, not a CPU replay of the complete startup caller.
Native setup orchestration consumes that contract; audio re-detection and
Zunsoft/title startup remain outside this acceptance.

Fresh ZUN stub decoding produces 13422 bytes, SHA-256
`baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`,
zero relocations. Its six bytes at 2067..206C are FF 03 02 01 01 01.
The host now repairs to these six defaults plus zero metadata and defined
wrapping checksum 07. ZUN's full cfg_init and undefined missing-file checksum
are not replayed. Raw original OP configuration codec behavior is unchanged.

## Independent controls

`verify_op_setup.py` executes original instructions at both loads. 84 cases
and 303829 complete ordered requests cover eight text effects, all nine mode
combinations, chords, held-key release, two input samples and waits beyond
9999 refreshes. Final geometry, resident canaries and balanced return stacks
agree. GNU and optimized UBSan consume the immutable original reference.

`verify_op_setup_pixels.py` independently executes original graph_putsa_fx
0DA1:04A4..05FD and SUPER 0000:2D5A..2F0B kernels at both loads. Transparency
is checked on zero and varying nonzero backgrounds. 4174 original kernel calls
produce five complete setup cases: 780 two-page/palette/RGB frames and
998437440 compared bytes. PI decoding, EGC, CGROM, GRCG shadow and palette
scaling are explicit adapters. Both current Linux hosts match that reference.
Frame streams are compressed as consumed; no gigabyte raw stream is retained.

A source-only mutant reverses BGM arrow direction while retaining SE behavior.
The independent trace rejects it at line 1077. Mutant source, driver, compile
command, digest and first difference are retained. This is a comparator
negative control, not target modification.

## Native lifecycle and replay

Both interactive entry paths enable configuration before registration. Pending
rankFF blocks score-derived menus and MAIN. Finishing setup changes resident
Normal/BGM/SE only; the physical file waits for its existing save boundary.
Closing midway preserves rankFF, so restart begins setup again. Fresh OP
reloads the closed file and can request setup again before score reading.

Per Linux host, two separate muted application processes exercise all nine
BGM/SE selections, missing/bad/short/unsafe/pending startup forms, interruption
and restart, a failed writer, fresh OP from a recorded demo, real selection
and MAIN entry. Full file/capture maps compare across GNU and UBSan. An injected
directory at the config path rejects close without advancing out of OP or
leaking a temporary writer. Completing setup does not advance parent RNG.

2112 independent original config controls and seven physical host cases still
pass. Configuration-enabled menu regression covers 16 ordinary/demo cases,
one physically unlocked Extra entry and four failed save boundaries. Its
missing-file failure fixtures now complete actual setup before those saves;
the first failed old fixture is retained. Prior demo and Music Room references
remain separate from setup-enabled integration.

Current source manifest contains 366 files; three builds bind 138 AMD64
programs, 46 each. 45 CTests pass per Linux host. MinGW is a cross-build only.
Actual Windows probing still fails before PowerShell at UtilBindVsockAnyPort.
Full natural ordinary/Extra routes, audio, current Windows save/restart and
dense Lunatic timing/performance remain required. DOS acceptance is unchanged.

Private receipts, source/product profiles, initial failures and complete
uncommitted v1308..v1324 recovery live under native
`.analysis/port64/setup-v1324/`. Original producer manifests remain immutable;
reviewed consumers bind the later frontend-fixture correction separately.

The v1324 cleanup shares907 terminal duplicate files after full-byte and hash
comparison, retiresone experimental executable and reclaims628629504allocated
bytes (about599.5MiB).5793protectedfilehashes remain unchanged; sources,
private inputs, replay/failure references andall138currentprograms remain.


Correction v1325: fresh target text at DATA0F34:0DB3 labels setup value2
as stereo FM; 0DC4 labels value1 standard FM. The former FM26(2)
description was wrong. Numeric scene/config traces and captures are unchanged.
