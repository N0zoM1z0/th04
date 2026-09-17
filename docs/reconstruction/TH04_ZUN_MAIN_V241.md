# ZUN.COM resident `_main` source recovery (v241)

## Target and boundary

The pinned Japanese `ZUN.COM` is a 7,754-byte DIET-packed MZ file, SHA-256
`0a12e9a489d3b704a77cf04ca3062ee48f298a9df6d237dc7dad46986e2d116e`.
Its provenance remains `candidate-local-attested`. The independent target-stub
decoded payload is 13,422 bytes, SHA-256
`baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.
The target and live disassembler database passed the session identity checks.

`_main` occupies decoded payload `_TEXT` `0xE67..0xF62`, 252 bytes, SHA-256
`db04398b52ca5780c734f839e2cf3768718f7f7c65705a9cdb9e88e34aa64871`.
The previous `cfg_init` ends in `RET` at `0xE66`. Gap-free 16-bit decoding of
`_main` begins with `ENTER 0xC,0` and ends in `RET` at `0xF62`; the next function
begins at `0xF64`. Its branch targets, call at `0xF3E` into `cfg_init`, and
candidate MAP public at the corresponding `_TEXT` offset support this complete
physical boundary. The target body checks resident existence, prints and
handles `/R` and `/D`, creates the resident block, clears its tail, writes
configuration, then sets the debug byte when requested.

## Maintained source and diagnostic replay

[Maintained source](../../src/zun/resident/main.cpp) expresses the complete
control flow and resident-memory writes in ordinary C++. Japanese literals are
kept as readable UTF-8 source and converted to CP932 before the pinned Japanese
compiler runs. It includes TH04 and `compat/rec98/` declarations only; it has no
cross-game source include, inline assembly, copied target bytes, fake return,
inert statement, or artificial padding. The ReC98 `th02/res_init.cpp` source was
used as a candidate and checked against the target body, never as an exact
Oracle.

The checked-in diagnostic command is
`python3 scripts/probes/replay_th04_zun_main.py`. Its v241 run used two isolated
v214 snapshots, compiling the maintained `cfg_init` and `_main` together under
pinned TC4J 4.02 `-O -b- -3 -Z -d -DGAME=4 -mt`, then linking the component with
pinned TLINK 6.10. Both valid OMF objects have the same 398-byte `_TEXT` CODE,
SHA-256 `ffc0ba5a4ccf78526e91dc878629df87624041ac3165cb3e4fc3f4ba8d156a41`.
The first 152 bytes remain the previously verified `cfg_init`; `_main` compiles
to 246 bytes, SHA-256
`1f3a816b96887bf07213fe00d5a8432f8aaccc9251a39098f26279e1ad65627b`.
The product `_main.cpp` also compiles as its own translation unit in both
snapshots: 246-byte standalone CODE is identical, SHA-256
`24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea`.
Both MAP and linked component outputs are deterministic; their hashes are in
the private receipt
`.analysis/reconstruction/probes/v243-zun-main-final/receipt.json`, SHA-256
`556247f05ecd7f2e89c81f2703bf96c43e7068b7761df11b17d3ccce57980ebe`.

The emitted `_main` CODE matches the separately compiled ReC98 candidate after
removing its three inert statements. It is six bytes shorter than the target.
Target disassembly has separate calls to `dos_puts2` for the bad-option and
already-resident errors; TC4J merges those calls with a later error call when
the inert statements are absent. ReC98's `seg = seg` and `argv = argv` suppress
that merge, but those statements are not accepted reconstruction source. The
linked component is therefore different, despite identical A/B output.

## Acceptance boundary

This packet reviews the `_main` function boundary and adds one **source-present**
ZUN unit. It does not claim exactness. The natural source differs by six CODE
bytes, and the diagnostic link still uses ReC98 headers and support objects.
The ZUNINIT/MEMCHK/ONGCHK components and a standalone checked-in TH04 build
remain unresolved. Any future promotion needs the full packed-file Oracle and
complete source ownership, in addition to a natural producer for the two
unmerged calls.

## v242 bounded return-expression control

A single natural compiler-shape hypothesis changed the bad-option and
already-resident branches to `return (dos_puts2(message), 1)`, leaving their
behavior unchanged. Two isolated pinned TC4J builds still emit 246 bytes for
`_main`; they move
the shared `dos_puts2` call to object-relative `0x8A` instead of restoring
the target's separate calls at payload `0xEE8` and `0xEF4`. The object CODE
SHA-256 is `7e3effff00403876821b4a5e7e03aaada70f4480c76d3177e11c3e6694e93718`.
Replay with `python3 scripts/probes/replay_th04_zun_main.py
--comma-return-control`. The private source/object/log and receipt are under
`.analysis/reconstruction/probes/v242-zun-main-comma-ab/`; receipt SHA-256 is
`f309dc6135528d0a06eab9ddaecb7e8cac7fb7fc5fe404971c8769d1a45a80f5`.
This rejects comma-return lowering as the missing natural producer; the
maintained source and acceptance state do not change.

## v286 optimization-toggle control

Replacing `-O` with `-O-` in one isolated pinned TC4J source overlay emits
248 standalone `_main` CODE bytes, SHA-256
`28f26e6f6ac85ed09aeb844df72d84edf6109651e8310c443fb92fc5621854f6`.
The target remains 252 bytes, and the bad-option and already-resident branches
still share a later `dos_puts2` call instead of the two target calls. The
composite `cfg_init` plus `_main` object also changes from 398 to 402 CODE
bytes, so this toggle does not preserve the established component shape.
Private OMF, CODE, logs, and receipt are under
`.analysis/reconstruction/probes/v286-zun-O-minus/`; receipt SHA-256
`82d28ed6dcb2535a135a0d2dca1f9cb7a7382b341d5bf118ce14681f9709c3e3`.
No source or exact state changes.
