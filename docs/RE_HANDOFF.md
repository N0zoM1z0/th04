# TH04 current handoff

Updated 2026-10-18. Complete maintained DOS four-product and faithful native x64
goals remain active. Use `taskset -c 1 nice -n 19`, muted headless runs,
serialized Borland/Wine and no host keys/focus. Keep English code/docs and
`gpt-6.1-sol: ...` commits; push main and native `HEAD:port/modern-64`.

## Sampled PC-98 input reaches MAIN/player (v1479)

MAIN now consumes pc98_input::Snapshot directly. Latch::snapshot() captures the
complete action word and Shift by value; the real player lifecycle receives
that value. Keypad diagonals retain their high bits. The existing integer/Shift
entry remains the host-key adapter and delegates to the same MAIN body.

An independent Oracle executes unchanged original input reset/sense/joystick
and movement instructions, then compares 15209 fresh MAIN/player updates:
12288 controlled sample calls and 2921 actual original BIOS samples. GNU and
optimized UBSan agree. Repeating host translation at this boundary fails 11073
cases. Keypad movement, sampled Bomb, Shift, Enter persistence and demo Q exit
also pass direct contracts. Each movement comparison starts a fresh game;
prior conflicting chords, clamps and full-route timing are outside that Oracle.

Fresh GNU 89 programs/85 CTests and four selected UBSan programs pass. Both
unmodified new game programs replay all 13377 actual loop words with every one
of the prior 130 complete output hashes unchanged. This preserves the stock
scenario's 407 blinking-text pixels and 1805 volatile keys; it does not repair
physical input delivery. The v1477 device scenario still has two failed literal
player inputs and 1803 keys. Keep these scenarios separate.

The existing original poll evidence shows Enter present at the head sample,
then BIOS Enter clear with key_det8192 at players7835/12889, 1.544944/1.594111ms
after sampler return. Frontend MAIN/UI polling and physical-device/BIOS IRQ
admission remain to be integrated. No fitted hold, expected-latch/clock/phase
assignment, new Stage4 observation or full-campaign acceptance is introduced.

## Actual original/source Elly defeat and Stage4 (v1475)

The maintained normal source MAIN completes the actual Elly route and reaches
Stage4 initialization/score1 in 929.884s, without timeout, exit0. Original
OP/MAINE/ZUN and all assets remain installed; all 17 other starting game files
match the original image. This is a MAIN-only DOS comparison, not a full
four-source campaign. No owned emulator remains.

All 13378 complete init/actor snapshots of nine whole pools, 22 pointer-free
states and three independently bound Midboss3 bytes agree with the original.
All 13377 physical/actual loop words, 33609 common raw-loop configured-field,
resident80 and ordered RNG observations agree. No extra raw loops occur.
Four independently attested literal-player pairs agree: 7834/7835=8192,
12888=32 and 12889=8192. Source player 0708:7463/near return06AA is owned by its
own MZ/MAP, separate from original 0AAF:5FCF/00F4.

Both actual score13377 CMP operands read quit2 (original DS:5392, source
DS:CB4C), followed by actual own-init Stage4/frame 0 and score1. At both Stage4
points, nine pools, 22 states, configured stable fields and resident80 agree.
Midboss3 private-byte ownership is claimed only for Stage3. This directly
observed departure does not rely on a native forecast or the planned budget.

All 23 full640x400 RGB, complete 528384-byte live-font, active8000-byte TRAM,
48-channel DAC, text-palette and own-MAP raw-tone samples agree, including
post-dialogue12889 and Stage4 score1. Each side supplies its own fonts and raw
GDC; no phase fitting, glyph masks or expected-state writes. All 23 raw GDC
records differ and 19 volatile postactor keys remain separate. The strict DOS
aggregate stays false. This observer differs from the older dense8000 vector
with 49 keys; do not subtract or merge their counts.

## Native comparison and current products

Maintained native source now has 569 files, closure
`32693566eebbbdc961f139c1b7dca736fc81f8b14d6e620304b358eafe9575d0`.
Current cold products and link inputs are at main-input-owner-v1479-final:
GNU 89 programs/85 CTests; UBSan game, session, input and MAIN-input programs.
DOS game source and the maintained four-product cohort remain unchanged.
The old stage3-hit-bridge-v1473-final cache is superseded and archived through
the latest recovery below. Use a fresh directory for subsequent builds.
The v1473 repair propagates/consumes/resets Elly's existing hit flag; retain
original hit8046/GameOver8085 and its partial actor-stream failure as evidence.

The v1474 original completes in 996.426s. Both unchanged stock native roles replay
all actual 13377 loop words with 130 identical files. Nine-pool/state and four
literal-player gates pass. Stock exit1 is its final natural-departure diagnostic
guard; native Stage4 uses a separate normal-advance GNU observer. Native RGB
passes 22/23;12889 has 407 blinking-text pixels despite matching TRAM/DAC/tone.
Keep 1805 native postactor keys separate from the 19 source-DOS keys. Original
GDC phase2 is visible and native reports hidden; clock divergence is unresolved.

Original MAIN 156258/1136 relocations remains
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
Normal source MAIN 200279/1183 relocations remains
`778641ab845bcd67c6888bacc049e2cfa20fddda844681d3d2fd164f8386abc9`.
Four-product cohort: `.analysis/build/dos-four-products-v1443`.
Phase entry heads: main `ec3f7c6`, native `a75d43e`; read actual heads and the
latest finish receipt. Target provenance stays `candidate-local-attested`.
No artifact/unit exactness changes.

## Prior source Elly recovery (v1475)

The source-elly-v1475 parent carries the seven terminal source aliases and
identity/state/RGB/transition readers. Its Micro300 inactive-byte and full-route
RNG-return controls remain preserved. Use the latest recovery below for all
inherited aliases; do not rerun completed DOS captures or treat RAM as a resume.

## Current recovery and next work

Phase entry heads are main 55cbb1a/native ad7f42c; read actual heads and the finish
publication. Code commit 65e6115 adds the typed MAIN consumer. Both complete goals
remain active. Current main-input-owner-v1479/recover.py carries 4513 exact
aliases:1825 inherited plus 2688 newly closed files. Keep 72700 parent identities
and all current/late/finish identities and providers. Every new alias restores
SHA, size, mode and nsmtime. Ten actual regular raw wires restore individually
to limit disk peak. Three real/archive readers reproduce both 130-output maps,
83 old contracts, two old exact GNU/UBSan relinks and the typed-consumer Oracle.

The new current cohort and link inputs, private consumer controls, sparse target
evidence and all inherited providers remain physical. Old receipts/logs and
providers remain; the old cache is recovery provenance, not an incremental
build. Named restoration is available for historical readers. The stock
frontend rejects precreated FIFO output directories; that failed harness is
preserved. Successful producers use fresh directories and immediately compress,
verify and unlink their five real regular raw wires after termination.

Actual file deallocation is 1982.83984375MiB. New archives cost 14.51953125MiB;
all cleanup artifacts cost 16.79296875MiB. After 2MiB metadata reserve, local release
is 1964.046875MiB. Whole-phase retained costs, including the current full build,
plus 32MiB reserve are separate. No prior cleanup, rejected-FIFO raw avoidance or
temporary restore-write credit. No producer is live.

CTest inspection also writes LastTest.log: this phase's --show-only query
replaced the old protected log. The final chain rejected it. All 73472 original
bytes were recovered using retained same-run stdout and CTest format; the full
SHA remained exactly the immutable original value. This is historical log byte
recovery, not a fresh execution or original-nsmtime claim. Keep the failed-chain
record, damaged bytes and recovery provenance. Use saved old-ctest.json or a
copied build for future queries; do not invoke CTest in protected build trees.

Next connect frontend MAIN/UI sampling and physical-device/BIOS delivery to the
verified latch/Snapshot consumer. Preserve the host adapter's recorded scenario
and all 52 device edges/four UI tails. Use the existing raw PIC/poll/player
witnesses first; isolate genuinely missing IRQ/scheduler evidence. Never seed
expected key_det, carry a previous host word blindly or fit a hold/clock phase.
Continue the existing differential note. Finish focused checks, tracking, both
CIs and git diff --check. Continuous timing/display, NP2/Windows and complete
four-source/native campaigns remain open. No exactness state changes.
