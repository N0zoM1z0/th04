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

[Maintained source](../../../src/zun/resident/main.cpp) expresses the complete
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

## v315 semantic branch-shape controls

`python3 scripts/probes/probe_th04_zun_main_branch_shapes.py --output-dir
.analysis/reconstruction/probes/v315-zun-main-branch-shapes-ab` compiles five
ordinary C++ alternatives from checked-in ZUN source and headers only. It
attests the pinned packed target, decoded `_main` at `_TEXT` `0xE67..0xF62`,
and TC4J; two isolated rounds produce identical valid OMF for every variant.
The target body is 252 bytes. Shared error-label forms emit 248 and 249 bytes;
a local message pointer and a const local return value each emit 251 bytes;
a mutable local return value emits 257 bytes. All fail the size gate, so none
can be a raw-exact producer. The last form does retain a separate bad-option
print call, but adds a stack store and reload absent from the target.

Receipt SHA-256:
`5f0ae65c3a52c92d50ce517c844de58c70c4fecc5825c40cec4fe93de79452c3`.
This eliminates those source-shape hypotheses only. The maintained `_main`
remains 246 bytes, source-present, and nonexact; no ZUN exact state changes.

## v517 branch-shape replay maintenance

The v315 branch-shape driver had retained a stale import of the former static
HEADERS list after the maintained ZUN source-only compiler route moved to a
transitive checked-in source closure. This was tooling drift, not new target
evidence. The driver now derives the _main header set through the same
source_closure() helper and still materializes no ReC98 source or header.

A fresh two-round replay at
.analysis/reconstruction/probes/v517-zun-branch-shapes-002/ has receipt
SHA-256
acace69547c0f0f5b69338d98b77f56a39d28f2746a2d9bf64a29427fe0e4332.
The five ordinary C++ controls reproduce the v315 CODE sizes exactly:
248, 249, 251, 251, and 257 bytes against the 252-byte target. This restores
the negative experiment's current replayability without changing maintained
_main, cfg_init, or any ZUN acceptance state.

## v518 selective-tail compiler and provenance bound

Fresh target/object alignment localizes the entire six-byte natural-source gap.
The 252-byte target does not merely disable tail merging globally. Its four
error paths have a selective print-call fingerprint:

- /R not-resident: push the message, then jump to the later no-space print call;
- bad option: keep its own dos_puts2 call, then jump to the shared return 1;
- already resident: keep its own dos_puts2 call, then jump to the shared return 1;
- no-space: keep the later dos_puts2 call immediately before the shared return 1.

The maintained 246-byte build instead folds bad-option and already-resident
into that later call, accounting exactly for two missing three-byte CALL
instructions.

The checked-in optimizer-profile driver
scripts/probes/probe_th04_zun_main_optimizer_profile.py compiles the maintained
source twice per supported PC-98 TC4J profile and also attests this target-local
fingerprint with ndisasm. Receipt
.analysis/reconstruction/probes/v518-zun-main-optimizer-profile-001/receipt.json
has SHA-256
9f70a971b1943cea0aa8c6850f9628fd7628eb2abf4804b275bc1ecd6ed71cb8.
Baseline is 246 bytes; -O- is 248; -Z- is 258. Those three retain the excessive
jmp/jmp/jmp/call tail merge. -v is 254, -y is 256, -G is 280, and -y with
-O- is 260; these preserve all four print calls or change other codegen.
None reproduces both 252 bytes and the target selective call placement.
The active 16-bit TCC frontend exposes no finer common-tail optimizer switch.

The separate upstream-provenance driver
scripts/probes/probe_th04_zun_main_barrier_provenance.py binds pinned ReC98
history rather than treating its current source as authority. Receipt
.analysis/reconstruction/probes/v518-zun-main-barrier-provenance-001/receipt.json
has SHA-256
9336932190f1b9b9a63b82ea03e0501d6c331c835a2851ff5e604de326f78007.
The self-assignment statements first appear in ReC98 commit b8ca607c as
decompilation work; its commit message describes them as no-ops used to block
TCC tail folding and only speculates that ZUN could have written them. Later
resident splits and the C++ wrapper migration preserve those barriers as
maintenance. This is upstream reconstruction provenance, not independent
original-source evidence.

Therefore maintained _main stays natural and source-present at 246 bytes.
Do not add inert self-assignments, codestrings, target-derived assembly, or
other optimizer barriers for equality. Reopen the six-byte source shape only
with materially new provenance or a compiler mechanism outside the now-bounded
supported profile surface. Work on cfg_init and independent ZUN
boundary/origin/component questions can continue without claiming that this
blocker is solved.

## v538 pragma optimizer-scope negative

English Borland manuals distinguish full optimizer controls from the older
Turbo C frontend, but the pinned Japanese Turbo C++ 4.02 command-line driver
has a smaller surface. Existing v399 toolchain evidence proves that this TCC
accepts plain -O while rejecting the tested BCC-style -O suboptions, including
-Od; the active TC4 BIN also contains no BCC.EXE. Therefore -Od is not an
available TH04 product compiler switch.

The remaining legitimate local-control idea is pragma option -O-. The
checked-in v538 probe tests it against maintained _main without adding inert
statements or changing behavior:

- before the function: 248 bytes, identical to the already-known command-line
  -O- build;
- inside _main, then reset with pragma option -O.: 246 bytes, identical to the
  baseline;
- inside _main without the reset: 248 bytes, again identical to the global
  no-jump build.

All three variants retain the natural error-tail fingerprint
jmp / jmp / jmp / call for not-resident / bad-option / already-resident /
no-space. The target remains jmp / call / call / call. Thus pragma placement
does not provide statement-level control of the two missing calls.

Run:

    python3 scripts/probes/probe_th04_zun_main_pragma_optimizer_scope.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

Accepted receipt v538-zun-main-pragma-optimizer-001/receipt.json has SHA-256
27bc5a25b41a176156f33698703882b67c1bcb0df767c53679eaa3ca0415b8c2.

This closes the available pragma jump-optimization scope route only. _main
remains source-present at 246/252 bytes and must not gain inert barriers,
codestrings, or target-derived assembly for equality.

## v792 local speed-pragma scope negative

`#pragma option -G` is a legitimate Borland source-level compiler control,
and full-function `-G` was already known to retain too many error-print calls.
A new isolated source-only probe places the pragma before `_main`, before the
bad-option print with a restore after the already-resident branch, before that
print without a restore, and around only the bad-option branch. The source
contains the same operations and returns in all four variants.

Two pinned low-priority, two-core TC4J cold builds per variant agree on OMF and
CODE. Function-wide `-G` and the inner unrestored form each emit 280 bytes and
four direct print CALLs. Both restored inner forms emit the 246-byte baseline
and retain the excessive `jmp / jmp / jmp / call` tail merge. The target remains
252 bytes with `jmp / call / call / call`. A local `-G` spelling therefore does
not selectively restore the two missing calls. No maintained source or exact
state changes.

Run `taskset -c 0,1 nice -n 10 python3
scripts/probes/probe_th04_zun_main_pragma_speed_scope.py --output-dir
.analysis/reconstruction/probes/NEW-UNIQUE-NAME`. Focused receipt:
`.analysis/reconstruction/probes/v792-zun-main-pragma-speed-001/receipt.json`,
SHA-256 `2c2f79c0a38e3a245f01ce402342b2f067fc7bd27bd7a37144401bac6a80c7a3`.
