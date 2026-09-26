# ZUN.COM `cfg_init` source recovery (v239)

## Target and boundary

The pinned Japanese `ZUN.COM` is a DIET-packed MZ file, SHA-256
`0a12e9a489d3b704a77cf04ca3062ee48f298a9df6d237dc7dad46986e2d116e`,
with `candidate-local-attested` provenance. The target identity, MZ structure,
and live Ghidra database passed this session's checks. Independent target-stub
replay gives a 13,422-byte load-invariant payload, SHA-256
`baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.

`cfg_init(resident_t __seg *)` occupies payload `_TEXT` `0xDCF..0xE66`,
`0x98 / 152` bytes, SHA-256
`8fc23f22f653db2afd65ad4cdab19776f5e9f1cdbbfa9de2dd407426fed9bfa2`.
Gap-free 16-bit decode ends at `RET` at `0xE66`; `_main` begins with `ENTER`
at `0xE67` and calls `cfg_init` from `0xF3E`. The body has an internal create
path, a checksum-failure jump back to it, and eight call targets. Its writes
cover the default options, resident segment, debug flag, and stored checksum.
The newly created-file path writes an uninitialized checksum byte; the source
preserves that observed behavior.

## Current status (v819)

`cfg_init` is now **decoded-exact**. Its 152-byte direct TC4J CODE had
already been closed outside OMF FIXUPP fields; v817 closes the actual link
context by pairing it with the exact resident `_main` producer. Both
complete resident component rounds are byte-identical to target, so every
formerly shifted `cfg_init` fixup resolves to the target value. Canonical
v819 acceptance reports zero raw differences across the complete function.

## Maintained source and replay

[Source](../../../src/zun/config/cfg_init.cpp) is a complete natural C++
translation unit for this function and its default options/debug data. It uses
the observed near 8086/Tiny ABI and checked-in `compat/rec98/` forwarding
headers for still-unlocalized declarations. It contains no copied target code,
inline assembly, inert padding, or cross-game source include. The ReC98 source
was treated as a hypothesis and checked against the target's body and an
independently compiled object.

The pinned TC4J 4.02 command profile is `-c -I. -O -b- -3 -Z -d -DGAME=4 -mt`
with source `#pragma option -2`. In two isolated v214 source snapshots,
compiling the maintained TU yields valid OMF and identical 152-byte `_TEXT`
CODE, SHA-256
`4c80c1405ba9994053738757cbdad5478425ff6ff92baf455c8f2f4c32383fd4`.
Replacing only `cfg_init` plus its owned data in the diagnostic ReC98
`res_huma.cpp` wrapper leaves the complete 404-byte C++ CODE contribution
identical to the original candidate. Pinned TLINK then produces identical A/B
6,360-byte `RES_HUMA.COM` components, SHA-256
`cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110`.
The component's file bytes `0x267..0x2FE` match the independently decoded
target `cfg_init` slice exactly; the `0x100` COM load bias explains its MAP
offset `0x367`.

Two downstream `zungen`/`comcstm` replays give identical 13,422-byte ZUN flat
payloads, raw equal to the target-stub payload. DIET 1.45f `-B` packs the A/B
payloads to identical 7,754-byte files, raw equal to the packed target. The
private probe receipt is
`.analysis/reconstruction/probes/v239-zun-res-huma/receipt.json`, SHA-256
`62762a101340346c210e0309df051e4bef98db6780734b7a8083918920426449`;
the DIET A/B receipt is
`.analysis/reconstruction/diet-replay/v239-zun-product-cfg-ab/receipt.json`,
SHA-256 `bc1e44c46f603d6f8d7c4ade84bc88c4e504edfe93383ca326d24855d2e59d01`.
The checked-in diagnostic replay is
`python3 scripts/probes/replay_th04_zun_cfg_init.py`; its independent v240
A/B rerun passed with receipt SHA-256
`ffa2e671a54c71d91df1abdc13cabfdab8edd052c855cd4f4a804e28fdfdf525`.

## v239 acceptance boundary (historical; superseded by v819)

This promotes one ZUN unit to **source-present** and its target function
boundary to reviewed. It does not promote unit or artifact exactness. The
diagnostic composite still gets `_main` from ReC98's `th02/res_init.cpp`,
ZUNINIT/MEMCHK from target-derived assembly, ONGCHK from an external binary,
and support/pipeline code from ReC98. Removing `_main`'s three no-op source
barriers shrinks its C++ CODE contribution from 404 to 398 bytes, so that
upstream form cannot be credited as natural maintained source. A standalone
checked-in TH04 build and a packed-artifact unit-coordinate acceptance route
remain to be built before exact promotion.

## v519 function-local codegen closure and raw link blocker

A fresh checked-in-source-only compiler Oracle now separates cfg_init source
shape from the resident component layout. The maintained function and target
are both 152 bytes. The standalone TC4J object contains 15 kind-1 two-byte OMF
FIXUPP fields, emitted in descending code-address order. The raw target/object
comparison has exactly 30 differing bytes, and they are exactly the two bytes
of those 15 FIXUPP words. No difference occurs outside a link field.

Masking only those 15 words is diagnostic, not acceptance, but it is complete:
the target and natural object then have the same full 152-byte SHA-256
57e30f5075b690ceb8a797039fd108138e408e3d273cc09963c31022f4ac8eea.
The natural object CODE itself remains
4c80c1405ba9994053738757cbdad5478425ff6ff92baf455c8f2f4c32383fd4;
the raw target function remains
8fc23f22f653db2afd65ad4cdab19776f5e9f1cdbbfa9de2dd407426fed9bfa2.

The same v519 driver then runs the current natural separate resident component
link. That link leaves 13 raw cfg_init byte differences at function-relative
offsets 0x15, 0x19, 0x21, 0x2B, 0x37, 0x3A, 0x6A, 0x73, 0x7D, 0x86, 0x90,
0x93, and 0x94. Every one lies inside the same standalone FIXUPP words.
The resolved downstream calls/data addresses are six bytes early because the
natural resident _main remains 246 bytes instead of the target 252 bytes.
Therefore the current raw failure is a link-context consequence of the blocked
_main layout, not evidence for changing cfg_init source.

Replay with:

    python3 scripts/probes/probe_th04_zun_cfg_function_local.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The v519 receipt
.analysis/reconstruction/probes/v519-zun-cfg-function-local-001/receipt.json
has SHA-256
0125bb834cb5e1cfa1147d73a53bfad2d1b539e509ae9c79f893e583de5151a5.

Function-level acceptance is now marked blocked, while the unit deliberately
remains source-present. A fixup-normalized equality cannot waive the raw-byte
gate. Reopen cfg_init exact promotion only after an artifact-local natural
resident link resolves those FIXUPP words raw-zero; do not tune the already
closed non-fixup source bytes.

## v539 current-link revalidation

v519 proved the 152-byte standalone natural cfg_init object differs from the
target only in its 15 two-byte OMF FIXUPP fields. v539 repeats the link-side
part against the current resident path rather than the old external-MASTER
scaffold: all maintained support is local, MASTER is the compact 15-member
archive, EMU/MATHS are gone, and the only remaining external runtime inputs
are c0t.obj and CT.LIB.

Run:

    python3 scripts/probes/probe_th04_zun_cfg_current_link.py \
      --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

Accepted receipt v539-zun-cfg-current-link-001/receipt.json has SHA-256
25b880efe3580b1ab0461babf96dfd7332a1537eba574a3529a294defd642ca5.

The v539 linked cfg_init still had exactly 13 raw differing bytes. The
15 FIXUPP words split cleanly:

- offsets 0x06, 0x0F, and 0x81 already equal target;
- the other 12 FIXUPP words are each exactly target minus 6.

Those twelve shifted words produce exactly the 13 differing byte offsets
0x15, 0x19, 0x21, 0x2B, 0x37, 0x3A, 0x6A, 0x73, 0x7D, 0x86, 0x90, 0x93,
and 0x94. No linked difference escapes these fields.

This directly ties the current cfg_init residual to the six-byte short _main
layout. It does not waive the raw gate: at v539 cfg_init remained source-present and
blocked until an artifact-local natural link became raw-zero. Do not patch or
normalize relocation values to claim exactness.

## v817-v819 link-context closure

The old v519/v539 diagnosis was correct about *where* the remaining differences
lived but not a permanent blocker. Once resident `_main` is generated
through the exact TC4J `-B` + pinned TASM32 path, the six-byte downstream
layout shift disappears. No `cfg_init` source change is needed.

The checked-in `scripts/probes/replay_th04_zun_resident_bmode.py` compiles
`cfg_init` directly with pinned TC4J, generates/assembles the exact
252-byte `_main`, rebuilds the maintained compact resident support, and
links the complete 6,360-byte `RES_HUMA.COM` twice. Both outputs are
raw-identical to target SHA-256
`cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110`.
The linked `cfg_init` slice at component `0x267..0x2FE` / payload
`0xDCF..0xE66` is therefore raw-identical to target SHA-256
`8fc23f22f653db2afd65ad4cdab19776f5e9f1cdbbfa9de2dd407426fed9bfa2`.

v818 preacceptance and canonical v819 acceptance both compare the complete
152-byte function at zero differences. The canonical receipt is
`.analysis/reconstruction/receipt-archive/v819-zun-resident-canonical-receipt.json`,
SHA-256
`fe59d4624229bdc111a427d41144b6b6ca93973d729f570831c28805bba03508`.

This promotes decoded function acceptance only. The unit remains
`source-present` in the packed-file ledger because no honest direct packed
`ZUN.COM` file offset has been established.
