# TH04 MAIN DIALOG_TEXT boundary review v180

## Scope

This packet reviews two long-standing source-present but nonexact DIALOG_TEXT
functions without weakening their ordered-relocation blockers:

- `dialog_op(unsigned char)` at `th04-main / MAIN.EXE / DIALOG_TEXT`
  `0AAF:26CC`, MZ load `0xD1BC`, target file `0xE9BC`;
- `dialog_run()` at `DIALOG_TEXT 0AAF:2A7C`, MZ load `0xD56C`, target file
  `0xED6C`.

The selected private target remains SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`
and only `candidate-local-attested`. The target file is read-only operator input
and is not source, a build input, or a commit candidate.

## `dialog_op()` boundary correction

Fresh target-bound Ghidra still creates one sparse function at analysis linear
`0x1D1BC`: `body_min=0x1D1BC`, `body_max=0x1D52F`, but only 60 addresses in
two ranges. The old boundary ledger incorrectly carried that body-address count
as `body_size=0x3C` and the min/max span as `body_span=0x374`.

Gap-free target decode establishes the executable body instead:

- entry: analysis `0x1D1BC`, load `0xD1BC`;
- terminal `RET 2`: load `0xD52D..0xD52F`;
- executable size: `0x374 / 884` bytes;
- executable target SHA-256:
  `7e0aeed3988903370d9b1a9f5c6480fbe7416a3c26c867a910e6a5d6cd7af043`.

The following `0x3C / 60` bytes are compiler switch ownership rather than
function-body credit. Load `0xD530..0xD54D` contains fifteen 16-bit sorted
opcode values:

`#`, `$`, `=`, `b`, `c`, `d`, `e`, `f`, `g`, `k`, `l`, `m`, `n`, `t`, `w`.

Load `0xD54E..0xD56B` then contains fifteen 16-bit jump words. Interpreted through
DIALOG_TEXT CS base `0x1AAF0`, all fifteen resolve to decoded instruction starts
inside the executable body:

`0xD524`, `0xD51D`, `0xD350`, `0xD3B0`, `0xD498`, `0xD50A`, `0xD47B`,
`0xD22D`, `0xD2B9`, `0xD337`, `0xD4A5`, `0xD3E6`, `0xD1F0`, `0xD20A`,
`0xD273`.

Thus the complete physical producer extent is `0x3B0 / 944` bytes through load
`0xD56B`, target SHA-256
`1643a72bd7d6c411a5686efd6da2ae77385953fe509b289af623d21df71ddd67`.
`dialog_run()` begins at the immediate next byte `0xD56C`. The target contains
26 MZ relocation entries inside the physical `dialog_op()` owner.

Maintained natural source is `src/main/dialog/op.inl`, SHA-256
`2626af35399e82f88edfbb7c2679cd50c2af14f6adeab2047e145a59e6f2cfa7`.
Git history confirms that this file is byte-identical to the pre-layout-migration
partial source at commit `62a56f41b763b2cab9c78fe852e05f9a8801844d`; the source-tree move did not
rewrite its text.

## `dialog_run()` boundary

Fresh target-bound Ghidra constructs all 383 body bytes contiguously from
analysis `0x1D56C` through `0x1D6EA`. Gap-free raw decode ends in `RET` at load
`0xD6EA`; exact `dialog_animate()` begins at the next byte `0xD6EB`.

The reviewed extent is therefore exactly `0x17F / 383` bytes, target SHA-256
`52036afb6ec9c1fea4087cff75482a80908eed66b60e5e45caf4296f5892c2db`, with four
target MZ relocation entries. Fresh target callers form the expected dialog
chain: `dialog_animate()` calls `dialog_run()`, which calls `dialog_op()`.

Maintained natural source is `src/main/dialog/run.inl`, SHA-256
`897fc631b6bc2a6116a85eb873aff3ef6b203d33340616ea7da87211b4470b03`. It is
also byte-identical to its pre-layout-migration partial source at commit
`62a56f41b763b2cab9c78fe852e05f9a8801844d`.

## Exactness remains blocked

The historical two-cold replay `gptweb-partials-001` remains useful negative
linker evidence. Receipt SHA-256 is
`05e4bd1e7cbe1652e9fec6578147a0c9adf1f6729b3b35a994c999d210e533de`.
For both dialog units, A/B builds passed raw bytes, MAP placement, valid OMF,
normalized object determinism, and slice determinism, but failed ordered MZ
relocations. The target and candidate relocation *sets* are equal while their
orders are cyclically different.

Existing mechanism negatives are preserved rather than retried:

- five natural shared-TU boundary variants leave `dialog_op`/`dialog_run` raw
  bytes exact but do not restore target relocation order;
- the pre-decomp historical standalone assembly reproduces relocation-site sets,
  not target order;
- wrapper/inlining boundaries do not fix `dialog_run` FIXUPP grouping;
- the source-driven PC-98 IDE integrated compiler preserves the wrong
  `dialog_run` relocation rotation;
- `#line`, local debug switches, and external declaration order do not solve the
  ordering while keeping target bytes.

No v180 focused exact replay or aggregate promotion replay is run for this packet.
The units are known nonexact under a required Oracle, so promotion gates cannot
honestly pass. v179's post-promotion aggregate remains the current exact baseline.

## Function-review control plane

`reviewed_nonexact` already validates logical versus physical size, raw terminal
RET/RETF, next-public boundaries, compare tables, jump tables, and jump-target
instruction alignment. v180 adds one backward-compatible projection rule:
`owner_unit`, `source`, and `owner_name` supplied explicitly by a nonexact policy
are preserved in the emitted function ledger. Policies that omit these fields
retain the historical blank projection.

The v180 trial reviewer uses the current v179 final MAP, the target-bound Ghidra
function inventory, and the private attested target. It adds exactly two function
IDs and removes none:

- `th04-main-fn-1d1bc`, logical size `0x374`, blocked;
- `th04-main-fn-1d56c`, logical size `0x17F`, blocked.

The generic writer proposes unrelated historical normalization changes, so only
the two validated new rows are adopted into the maintained ledger.

## Verification planes

This packet establishes reviewed target boundaries and maintained source presence
for both dialog functions. It does **not** establish exact function/owner status,
standalone TH04 production closure, whole-image equality, runtime-storage
identity, runtime-scenario validation, portable-runtime validation, Factory
Truth-Kernel acceptance, or pristine-release provenance.

## Live accounting after review

Repository `scripts/status.py` reports the non-overlapping reviewed MAIN ledger as
`74,881 / 79,802` exact authored bytes (`93.833488%`) and `450 / 466` exact
reviewed authored functions (`96.566524%`). The two newly reviewed dialog
functions are blocked, so the exact numerator does not change. MAIN routing is
450 exact, 16 blocked, 71 unreviewed, and 31 original-style ASM attestation
observations. This denominator expansion is the intended authored-boundary result,
not an accepted-owner regression or a percentage of MAIN.EXE as a whole.
