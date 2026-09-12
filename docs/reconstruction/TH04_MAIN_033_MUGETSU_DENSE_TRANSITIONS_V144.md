# TH04 MAIN_033_TEXT Mugetsu dense transition callbacks (v144)

## Scope

Artifact: `th04-main / MAIN.EXE` (`candidate-local-attested`). Target SHA-256:
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The private executable remains ignored operator input and was not patched,
replaced, relocated, staged, or published.

v144 reviews the two adjacent Mugetsu transition callbacks that v109 had only
probed as a rolled-back natural-C++ near match. The complete target-owned
physical extents are:

| Function | MAIN_033_TEXT | Load | File | Code | Trailing compiler data | Physical extent |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `mugetsu_1812A` | `13A9:469A..478D` | `0x1812A..0x1821D` | `0x1992A..0x19A1D` | `0xB1` | `0x43` | `0xF4` |
| `mugetsu_1821E` | `13A9:478E..4883` | `0x1821E..0x18313` | `0x19A1E..0x19B13` | `0xB3` | `0x43` | `0xF6` |

Together they own `0x1EA / 490` authored bytes. Each trailing `0x43` region is
one zero compiler metadata byte followed by a 33-word dense switch jump table.
The first physical slice SHA-256 is
`e66b1df5c3055181bd157386fcacd951a08a3daf63c58dd5a04aba25237a6735`;
the second is
`836ba3c3796c9ec195882e1b6679254b2bb1b3cf028b926dab9f46e9adace143`.

## Boundary review

Fresh attested Ghidra is not an extent authority for either callback.
`0x2812A` is cross-linked into a 14-range function whose min/max escape this
Mugetsu producer by a large distance. `0x2821E` has no Ghidra function entry at
all. Pinned TASM and raw target decoding instead close the first executable body
at `RET 13A9:474A` and the second at `RET 13A9:4840`; the next TASM PROC entries
are exactly `13A9:478E` and `13A9:4884` respectively.

The target bytes independently validate the trailing compiler ownership. All 33
jump words after `mugetsu_1812A` resolve to eight valid instruction starts in
that function's code, and all 33 words after `mugetsu_1821E` resolve to eight
valid instruction starts in the second function. No table entry escapes its
physical owner. The first owner has one overlapping MZ relocation at load
`0x181A0`; the second has one at load `0x18295`.

The boundary ledger therefore moves both observations from provisional/unreviewed
to reviewed/blocked authored functions. The first function's old Ghidra span is
explicitly rejected; the second is admitted through target/TASM/raw/table review
without inventing a Ghidra entry.

## Maintained natural source

`src/main/boss/mugetsu_transitions.cpp` is the maintained natural-C++ source.
Its SHA-256 is
`1317f688d5a63fc622d220a217797d1165e4fba1b006ac104011a0a768358866`.
It uses the same TH04-local `boss`, frame, sound, Mugetsu gather-offset, and
anchor surfaces already used by adjacent exact Mugetsu source. It contains no
inline assembly, target-derived byte arrays, `#pragma codestring`, fake return,
inert padding, ABI lie, or target patching.

The source expresses both dense animation switches, the target-visible
sprite/position state transitions, the alternating sprite phase, the three
return states, and the sound-call conditions. `#pragma option -a` is the ordinary
TC4J source-level requirement that generates the one-byte switch metadata and
word-aligned 33-word tables.

After a fresh `scripts/attest_toolchain.py` pass, the maintained source compiles
under the production `-O -b- -3 -Z -d -DGAME=4 -ml` profile to a valid TC86
Borland C++ 4.02 OMF. The fresh object has SHA-256
`b637ea09f4fe5b778de1d959cfe1836b478ae7cc6a7cdf17d1322d1dfa45838d`,
dependency-timestamp-normalized SHA-256
`537746a2d57d1c4a637d52268dea09091bfd7518365982c83312d2140b5a29d1`,
and one 486-byte CODE LEDATA contribution. This is source-present compiler
evidence only. The target owner is 490 bytes, and the current maintained source
is not instruction-shape exact.

In particular, the maintained source lets TC4J route the dense-switch selector
through AX before BX, while the target uses BX directly. The `< 48` return gate
also lowers to `CMP ...; JL ret0` rather than the target's
`CMP ...; JGE next; JMP ret0`. Exact size or normalized instruction similarity
is not accepted as raw equality.

## Historical v109 near match and new negative probes

v109 already retained a stronger but now text-unavailable source-shape result in
`ev-th04-main-mugetsu-dense-transition-negative-v109`. That SHA-bound natural
source reproduced the two compiler metadata bytes, both 33-word tables, and all
other compared code except that TC4J canonicalized one target
`CMP/JGE + JMP ret0` gate per function into `CMP/JL`, leaving a deterministic
four-byte total deficit. The v109 source snapshot itself has since been pruned by
the documented analysis-retention policy, so v144 does not pretend that the new
maintained text inherits that four-byte comparison receipt.

v144 tests three genuinely different compiler/source mechanisms instead of
repeating the old if/goto/loop spelling matrix:

1. TC4J documents `-O` as jump optimization. A minimal probe compares normal
   optimization, a function-body `#pragma option -O-` / `-O` toggle, and a
   whole-function `#pragma option -O-`. All three still emit
   `CMP x,48; JL ret0`; disabling that switch does not recover the target gate.
2. A Borland `_BX` selector variant starts with the desired BX load/subtract but
   inserts `MOV AX,BX; MOV BX,AX` before the switch and still emits `JL`.
3. A block-scoped `register int` selector happens to produce exactly 490 CODE
   bytes, but routes the value through DX and AX before BX. This is an explicit
   counterexample to treating equal code size as exactness evidence.

The compact private probe receipts are bound by evidence rows and remain below
`.analysis/gpt-web/th04-main-20260912-v144/` only as ignored working evidence.

## Origin cross-check

A bounded scan of independently attested TH02, TH03, TH04, and TH05 original
MAIN targets searched for the wildcarded dense-switch producer prefix and for
the distinctive `CMP [imm],imm; JGE +2; JMP short` gate. TH02, TH03, and TH05
contain no hit for either shape. TH04 contains exactly the two producer hits at
load `0x1812A` and `0x1821E` and exactly the two gates at load `0x18184` and
`0x18278`.

This is useful negative routing evidence, not language proof. Unlike the v139-
v143 original-style ASM corrections, v144 finds no independent cross-original-
target producer signature. The functions therefore remain authored C++
candidates with maintained natural source rather than being reclassified merely
because the compiler shape is difficult.

## Accounting and verification planes

The target-first boundary correction expands the reviewed authored denominator by
`0x1EA / 490` bytes and two functions. Live MAIN accounting becomes:

- reviewed authored bytes: **47,564 / 48,058 exact (98.972075%)**;
- reviewed authored functions: **300 / 303 exact (99.009901%)**;
- blocked reviewed functions: **3** (`snd_load` plus these two callbacks);
- authored boundary candidates: **543**, with **240** still unreviewed.

The percentage drop is deliberate denominator correction, not an exact-owner
regression. The campaign pressure target is not permission to hide newly proved
authored extents.

No v144 focused exact-unit replay or aggregate exact replay was run because the
maintained source is known nonexact. The current repository-native exact baseline
therefore remains the v143 178-owner final aggregate
`gptweb-v143-shot-seam-aggregate-final-001`, receipt SHA-256
`d5d4d5a28261f0a194d396ae155d15b10572963de47f1f46a5203ed72b7a924d`.

Function/extent exactness for these two callbacks is **not established**;
source presence and boundary ownership are established. Standalone TH04
production-source/link closure remains unestablished. Runtime-storage identity
is unestablished. No runtime scenario is validated. No v144 Factory acceptance
claim is submitted or implied. Target provenance remains
`candidate-local-attested`.

## Continuation

The directly adjacent `mugetsu_18314` callback begins at MAIN_033_TEXT
`13A9:4884` / load `0x18314`. Fresh Ghidra also misses that entry. It should be
reviewed target-first against its terminal return, next TASM PROC at load
`0x1838A`, callers or function-pointer stores, relocations, and any trailing
compiler-owned data before source work. Do not resume the v109 gate-spelling
matrix unless a genuinely new TC4J mechanism is identified.
