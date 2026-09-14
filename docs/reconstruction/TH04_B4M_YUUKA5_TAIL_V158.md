# TH04 B4M Yuuka5 tail and dispatcher reconstruction (v158)

## Scope

This packet continues the v157 Yuuka5 reconstruction in `th04-main / MAIN.EXE`,
`B4M_UPDATE_TEXT`, under the attested `target:th04-main` local Japanese target.
The target remains `candidate-local-attested`; this work does not establish
independent pristine-release provenance.

The newly credited logical owner is:

- map extent `13A9:2813..2F89`;
- load-module extent `0x162A3..0x16A19`;
- target file extent `0x17AA3..0x18219`;
- size `0x777` / 1,911 bytes;
- target slice SHA-256
  `7299efa9e4e1eed70986172ad3333f5a0cd6daaa35ae518c9356c9ed5257326b`.

Target relocation order and compiler-object structure additionally prove that
this tail and the preceding exact v157 first-four helper owner are one original
physical TC4J translation-unit producer:

- map extent `13A9:243E..2F89`;
- load-module extent `0x15ECE..0x16A19`;
- target file extent `0x176CE..0x18219`;
- size `0xB4C` / 2,892 bytes;
- target SHA-256
  `3214d14fe355ca36f65fecf204bae0485ef6cc02d96b9d0ebbd7048804be4e91`.

Exactness accounting deliberately remains non-overlapping. v157 retains its
existing `0x3D5` logical credit, while v158 adds only the following `0x777`.

## Reviewed function boundaries

Five authored functions tile the new logical tail without gaps:

| Function | Load extent | File extent | Size | Target SHA-256 |
| --- | --- | --- | ---: | --- |
| `yuuka5_pattern_speedup_ring()` | `0x162A3..0x1630C` | `0x17AA3..0x17B0C` | `0x6A` | `798909189f0f18b72f66cd1f7e2d86af9acc9202aad2964965ff0ccbaa8a27ca` |
| `yuuka5_pattern_aimed_spread()` | `0x1630D..0x16388` | `0x17B0D..0x17B88` | `0x7C` | `dcaf8cc4012f0446a4ab93b92ad7eeb05ea676e11d7226798cc2e19fff304903` |
| `yuuka5_pattern_laser_burst()` | `0x16389..0x1653C` | `0x17B89..0x17D3C` | `0x1B4` | `660c8aeb0ba91bd1da21384c242cc9a36482e5eba9223f90746e3deef4cae2e2` |
| `yuuka5_pattern_mirrored_streams()` | `0x1653D..0x1660F` | `0x17D3D..0x17E0F` | `0xD3` | `d17cabfd47f4f602162be7125268ed0b0d57338d86cb7fe602d5f5ff2b335da9` |
| `yuuka5_update()` | `0x16610..0x16A19` | `0x17E10..0x18219` | `0x40A` | `8e7e5f73b7e5a4ab1c839736070fbd7bfe5e21b8e056a12554c384dfa2817971` |

Fresh Ghidra is not authoritative for this cohort. It has no function at
`0x162A3` or `0x1653D`, does not construct the complete `0x16389` body, and
truncates FAR `yuuka5_update()` to 13 bytes. The target/TASM/raw seams and the
natural generated public offsets instead define the reviewed extents.

`yuuka5_pattern_laser_burst()` owns compiler data after executable RET at load
`0x164EC`. Twenty compare values and twenty jump words fill
`0x164ED..0x1653C`. The values are:

`0x10, 0x28, 0x2A, 0x2C, 0x30, 0x32, 0x34, 0x38, 0x3A, 0x3C,
0x40, 0x42, 0x44, 0x48, 0x4A, 0x4C, 0x50, 0x52, 0x54, 0x60`.

All twenty target words were independently decoded from target bytes and resolve
to raw instruction starts.

FAR `yuuka5_update()` likewise owns its complete RET-following compiler region.
After executable control flow comes one zero metadata byte, two four-case
mode compare/jump tables, and a nineteen-entry phase jump table. Every target
word was independently checked against raw instruction starts. The next real
TASM PROC is `marisa_16A1A` at load `0x16A1A`.

Ghidra-only `0x1665A` is an internal dispatcher block, not a function entry.
Ghidra case artifact `0x16A01` lies inside the nineteen-entry phase table and is
compiler data, not authored code.

## Physical translation-unit ownership

The v157 packet originally reconstructed the first four helpers as a standalone
logical owner because that was the smallest proven packet. v158 supplies the
missing physical-owner evidence.

The fused natural object emits nine B4M publics at relative offsets:

`0x000, 0x0C9, 0x1D7, 0x309, 0x3D5, 0x43F, 0x4BB, 0x66F, 0x742`.

Every offset exactly equals a target/TASM function seam. The B4M segment length
is exactly `0xB4C`.

The target MZ relocation sequence is also continuous across the previous
logical split: v157 owns relocation-table indices 380..385 and v158 owns
indices 386..396. This is strong target-local evidence that all nine functions
came from one original object rather than two independent source producers.

The maintained physical wrapper is `src/main/boss/yuuka5.cpp`. For readability,
the function bodies remain split into:

- `src/main/boss/yuuka5_patterns.cpp`, SHA-256
  `d0311989de396522f5ce9e1e03151e5529f17e168eeadab7c50e4bf9c58232c9`;
- `src/main/boss/yuuka5_tail.cpp`, SHA-256
  `c9f0b9f991dc4085a3f93681b8a1c02e6ab06a783e208fce611d2b11aafbb8fa`.

The wrapper SHA-256 is
`2e31775c7e990b76a7296e8f39ecd9998b8b982b1147d10bc00df8a067ea9dfa`.
This mirrors the already-established fused Yuuka6 producer pattern: the split
files remain independently understandable, while exact replay compiles the
historical combined translation unit.

## Natural source and historical ABI

The reconstruction uses ordinary Turbo C++ source and the historical TH04 large
memory model. It does not use inline assembly, target-derived byte arrays,
`#pragma codestring`, fake returns, inert padding, target patching, or copied
target bytes.

The FAR dispatcher ABI is preserved. A source-level detail that mattered was
`boss_explode_big()`: the exact v156 producer defines the historical overload as
`void pascal near boss_explode_big(unsigned int type)`, while the older header
surface exposes an enum declaration. v158 therefore carries the same explicit
unsigned-int declaration pattern already used by exact TH04 boss update source.
This is an ABI correction backed by the existing exact owner, not a linker lie.

The fade path inside `yuuka5_pattern_laser_burst()` uses Borland register
surfaces `_AL` and `_DL` to express the target evaluation order. These are
ordinary compiler register intrinsics already used by repository exact C++;
they are not inline assembly. The natural data flow is: compute frame parity in
AL, load the palette tone into DL, subtract AL from DL, then store the result.

The final cold fused object has raw SHA-256
`cf94234a52ca8967cc70baeedf6cdba747fb918892ac26bbadbdf1eeab43a5b9`
and dependency-timestamp-normalized SHA-256
`b0aab468b834c64b6f7c1f50d427b9a29d2b022bbe2fd01b7271dc720f3dc4af`.
It is valid OMF translated by TC86 Borland C++ 4.02.

## Ordered relocations

The newly credited `0x777` tail owns eleven target relocation-table entries in
target order:

`0x1666D, 0x16643, 0x1660C, 0x16552, 0x164B9, 0x163D6, 0x163BF,
0x16385, 0x1632A, 0x16309, 0x16996`.

Focused and aggregate candidates reproduce this exact ordered sequence. Set
equality alone was not used as acceptance evidence.

## Replay seam

When v158 is selected, the exact replay uses the physical producer order:

- exact v156 explosion owner;
- zero-credit preceding thicklaser TASM producer;
- fused natural `th04/y5all.cpp` producer for the complete `0xB4C` Yuuka5 TU;
- zero-credit TASM suffix beginning at `marisa_16A1A`.

`config/replay/th04_b4m_post_yuuka5_v158.asm.in` is a hash-bound extraction
template for that Marisa suffix. Its SHA-256 is
`ef37e1787f9d004e5eed679b41802dd5e80cb1dd0ab2021aa1fce4bafc8277d0`.
It is replay plumbing and receives no reconstruction credit.

The old v157 residual `b4msuf2.asm` is still cold-built as an Oracle-only OMF
object but is no longer linked when v158 is selected. The even older v156
residual remains cold-built as well. This preserves predecessor gates rather
than weakening them.

The v157 logical unit uses a producer override whenever v158 is selected, so
its existing `0x3D5` exact extent is verified from the same `y5all.obj`. This
proves the physical ownership correction without double-counting v157 bytes.

## Negative compiler and source-shape evidence

Several failed probes were useful and receive no exactness credit:

- The first focused exploratory probe reached the linker and failed
  on an enum-decorated `boss_explode_big()` symbol.
- The second probe confirmed that a call-site cast alone could not select the
  historical unsigned-int overload because that declaration was absent from the
  active header surface.
- The third probe compiled and linked with exact MAP placement, ordered
  relocations, valid deterministic OMF, and exact v157 prefix, but the new tail
  still differed at 125 bytes in nine runs. Target/candidate disassembly
  localized those differences to palette-tone register evaluation and two
  duplicated dispatcher control-flow blocks.
- cheap object probes rejected a three-register spelling that grew the producer
  by two bytes and a direct memory compound-assignment spelling that shrank it
  by six bytes.
- The fourth probe reduced the linked result to one wrong byte: the displacement of
  the repeated `< 128` branch in `yuuka5_pattern_laser_burst()`. Restoring the
  explicit redundant early return made the branch target the function RET,
  matching the target without padding or byte injection.

These failures are retained as source-shape evidence. Only candidate 005 and the
subsequent aggregates support exactness.

## Exactness Oracles actually run

Focused cold replay:

`python3 scripts/replay_th04_main_exact_units.py --unit th04-main-yuuka5-tail-v158 --run-id gptweb-v158-yuuka5-tail-focused-candidate-005`

- PASS for the 99-owner dependency closure;
- two isolated serial cold builds;
- v158 raw bytes, map placement, all eleven ordered relocations, OMF validity,
  and determinism pass;
- the v157 logical prefix also remains raw/map/relocation exact through the
  fused producer;
- both focused candidate MAIN images have SHA-256
  `1b981138fef86f8f7285044c13476398ccf1e3dc612c3a12fafbab96f9cfed27`.

Candidate-state aggregate replay:

`python3 scripts/replay_th04_main_exact_units.py --run-id gptweb-v158-yuuka5-tail-aggregate-candidate-001`

- PASS for all 191 default owners in two isolated cold builds;
- both candidate MAIN images have SHA-256
  `b973c2696e7b27640b4d68b098ba7a8a083f6808d28bc8c53781bf54e08f2cc4`.

Post-promotion aggregate replay:

`python3 scripts/replay_th04_main_exact_units.py --run-id gptweb-v158-yuuka5-tail-aggregate-final-001`

- PASS for all 191 default owners in two isolated cold builds with
  `failures=[]`;
- v158 and the overridden v157 prefix remain raw/map/relocation exact;
- normalized `y5all.obj` remains
  `b0aab468b834c64b6f7c1f50d427b9a29d2b022bbe2fd01b7271dc720f3dc4af`;
- both candidate MAIN images again have SHA-256
  `b973c2696e7b27640b4d68b098ba7a8a083f6808d28bc8c53781bf54e08f2cc4`.

## Verification-plane boundaries

This packet establishes repository-native reviewed boundary ownership and exact
natural-source reconstruction for the five new functions and the non-overlapping
1,911-byte logical tail. It also corrects physical producer ownership for the
complete 2,892-byte Yuuka5 TU.

It does **not** establish standalone TH04 production compile/link closure,
runtime-storage identity, runtime-scenario validation, whole-image equality,
independent pristine-release provenance, or Factory Truth Kernel acceptance.
Those remain separate verification planes.

## Next frontier

The immediate evidence-connected continuation is the residual seam beginning at
`marisa_16A1A` in the same `B4M_UPDATE_TEXT` segment. The current boundary ledger
still has two authored unreviewed entries before the already-exact Marisa cohort:

- `marisa_16A1A` at load `0x16A1A`, currently represented by a suspiciously tiny
  Ghidra body;
- `marisa_16AE9` at load `0x16AE9`, currently a `0x9C` corroborated near entry.

The v158 replay residual already begins exactly at `marisa_16A1A` and exports
aliases for both entries. The next packet should therefore reconcile the true
physical extent from `0x16A1A` through the independently exact
`marisa_flystep_pointreflected()` boundary at `0x16B85`, audit relocations and
callers/callees, and only then decide whether one natural Marisa producer can
replace that residual prefix.
