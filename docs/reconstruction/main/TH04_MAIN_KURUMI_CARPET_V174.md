# TH04 MAIN Kurumi backdrop / carpet-lighting seam (v174)

## Scope

This packet reviews the `MAIN_TEXT` / `STAGES_TEXT` seam immediately after the
exact Yuuka5 foreground renderer and before the exact Stage 4 renderer in the
attested local `MAIN.EXE` target. The private target remains ignored operator
input with `candidate-local-attested` canonicality. It is not modified, copied
into the repository, or treated as independently proven pristine media.

The packet deliberately has two outcomes:

- `kurumi_backdrop_colorfill()` is reconstructed as maintainable natural TC4J
  C++ and promoted to exact after focused and aggregate cold replay.
- `carpet_lighting_put_new()` receives a reviewed authored boundary and
  maintainable natural C++ semantics, but remains blocked because its linked raw
  bytes do not match. Boundary, layout, relocation topology, object validity, and
  determinism are independently closed; the remaining mismatch is code shape.

## Physical seam

Target-first MAP/raw review separates five adjacent regions instead of treating
an old `main.obj` suffix as one source owner:

| Load range | File range | MAP owner | Classification |
| --- | --- | --- | --- |
| `0xEA6F` | `0x1026F` | historical `MAIN_TEXT` tail | one zero layout byte; zero reconstruction credit |
| `0xEA70..0xEA88` | `0x10270..0x10288` | `MAIN_TEXT 0AAF:3F80` | `kurumi_backdrop_colorfill()`, 0x19 natural-C++ exact |
| `0xEA89` | `0x10289` | historical `MAIN_TEXT` tail | one NOP layout byte; zero reconstruction credit |
| `0xEA8A..0xEAE3` | `0x1028A..0x102E3` | `STAGES_TEXT 0AAF:3F9A` | `carpet_lighting_put_new()`, 0x5A reviewed/blocked |
| `0xEAE4...` | `0x102E4...` | `STAGES_TEXT` | previously exact `stage4_render()` begins |

The v167 replay object historically materialized the first three rows together.
v174 narrows the v167 auxiliary contract to the leading zero, builds the 0x19
callback from maintained C++, and hash-extracts only the trailing NOP into a
separate Oracle-only TASM object. Neither one-byte seam receives natural-source
or function exactness credit.

## Kurumi boundary and source evidence

Ghidra has no function entry at analysis `0x1EA70`, so no Ghidra boundary is
promoted by itself. The independent evidence is:

- pinned TASM/TLINK expose the near public at `MAIN_TEXT 0AAF:3F80`;
- raw target decoding closes exactly 25 bytes through the RET at load `0xEA88`;
- the preceding byte is the independent v167 zero seam and the following byte is
  the independent NOP seam;
- attested target disassembly of independently exact `stage2_setup()` observes
  `MOV word ptr [boss_backdrop_colorfill],0x3F80` at analysis `0x2E141`, matching
  the physical public rather than relying on candidate naming;
- the 25-byte target slice SHA-256 is
  `f814c1bd6eb1547a9193b911f9e9dd83a9ae47cccdbcc01c02ba753e001f2b31`;
- there is no target MZ relocation overlap inside the owner.

Maintained source is `src/main/boss/kurumi_backdrop.cpp`, SHA-256
`9f7244be236c370163307ff2ca9efa99f97af6b5f1728649402cf9b66ca3f515`.
It uses ordinary Turbo C++ pseudo-register assignments and two calls to
`grcg_fill_playfield_rows()` under `#pragma option -k-`; it contains no inline
assembly, target-derived byte array, codestring, fake return, inert padding,
target patch, or ABI lie.

A production-profile compiler-only probe emitted the exact 25-byte CODE shape
with only the two near-call displacement fields left at zero for normal OMF
fixups. The probe object SHA-256 is
`b7b1154bbd865ad101d53ef7877e5c16aa483192ff463b8388204b4429e8197c`.
The final cold-replay object is valid deterministic TC86 OMF with dependency-
normalized SHA-256
`46e704c9a8a71a901fcc90fd21eb0dab9c7809aaf8a4e29aa966f43f78e3b3b2`.

## Carpet boundary and negative evidence

Attested Ghidra constructs one contiguous near function at analysis `0x1EA8A`,
size `0x5A`, with exact `stage4_render()` as its sole direct caller and no
callees. The MAP starts `STAGES_TEXT` at `0AAF:3F9A`; raw decoding closes `RET 4`
at load `0xEAE3`, and exact `stage4_render()` begins at `0xEAE4`. The target
slice SHA-256 is
`d06f7b07a8e6a162a9c211f1014ff514f9df053d9c5594f814bbc19bb14dc5c9`
and has no MZ relocation overlap.

Maintained semantic source is `src/main/stage/carpet_lighting.inl`, SHA-256
`cbd3e93a4ba08aa58b0d922c24104816f6eb3208a92b1afb0e5478ac3682526e`.
It intentionally expresses the tile-column update with ordinary arrays and loops
rather than copying the ReC98 inline-assembly implementation.

A bounded production-profile codegen probe gives durable negative evidence for
five historical instruction-selection mechanisms:

- natural `_ES = _DS` emits `MOV AX,DS; MOV ES,AX`, not target `PUSH DS; POP ES`;
- natural dereference/increment emits `MOV AL,[SI]; INC SI`, not `LODSB`;
- natural pseudo-register shift emits `ADD DI,DI`, not target `SHL DI,1`;
- natural loop control emits `DEC CX` plus test/branch, not target `LOOP`;
- the target uses unsigned `MUL BX` in its two index calculations.

The maintained-source cold replay `gptweb-v174-carpet-lighting-negative-001`
compiles twice. Both builds have exact MAP placement, empty ordered relocation
overlap, valid OMF, deterministic normalized objects, and deterministic linked
slices. Raw equality alone fails: target SHA-256 is `d06f7b...c5c9`, candidate
SHA-256 is
`9ab61cb3e7b0db0e88edd991e4147775a81f635b949cb01d2fe2930a857df20a`.
Receipt SHA-256 is
`1e2950804f9165fc926cdc03c97062b1f607f4ebfd4d8453ecdefeab1b3d8c49`.
No exactness credit is granted.

## Exact replay

Focused exact replay for Kurumi is
`gptweb-v174-kurumi-backdrop-focused-candidate-003`. It closes a 127-owner
dependency cohort twice with `failures=[]`; the 0x19 owner is raw/MAP/empty-
relocation exact and both one-byte auxiliaries are independently raw/MAP exact.
Receipt SHA-256 is
`90e8d4dc4db7d74d0fbb824144f6d9ca28f199ff470fc04292f8f857987d7151`.

Before ledger promotion, aggregate replay
`gptweb-v174-kurumi-backdrop-aggregate-candidate-001` closes all 206 default
owners twice with `failures=[]`; receipt SHA-256 is
`30e018bd5e1febff9bad7f05be81309106a8d9090c7b7c22d18a5183d3da7ed7`.

After boundary/function/unit promotion, aggregate replay
`gptweb-v174-kurumi-carpet-aggregate-final-001` again closes all 206 default
owners twice with `failures=[]`; receipt SHA-256 is
`369cafd0949041e8cd038c8dfb2e31cf17a0e5363974bfc204f7ba8cf28ff3d5`.
The non-default blocked carpet unit is intentionally outside the exact aggregate
cohort.

Two earlier Kurumi trials receive no exactness credit. The first stopped before
building because the new unit was not yet registered in `config/units.csv`. The
second proved the new owner exact but exposed that the v167 auxiliary ledger
still claimed the entire historical 0x1B tail; v174 correctly narrows that older
auxiliary credit to the leading zero byte. The failed second build tree was
removed as current-session reproducible output after confirming no tracked
reference or active producer.

## Accounting and verification planes

This packet expands, rather than shrinks, the reviewed authored denominator.
After promotion MAIN has 69,350 exact reviewed authored bytes out of 72,944
(95.072933%) and 411 exact functions out of 425 reviewed authored functions
(96.705882%). There are 14 reviewed blocked MAIN functions and 112 unreviewed
MAIN authored candidates. The lower percentage versus v173 is expected: v174
adds 25 exact Kurumi bytes and 90 reviewed-but-blocked carpet bytes.

The repository-native exactness plane is PASS for the Kurumi owner and for the
206-owner default post-promotion cohort. Standalone TH04 production compile/link
closure is not established. Runtime-storage identity is not established. No
runtime scenario is executed by this packet. Whole-image exactness and portable
runtime validation are not established. No Factory Truth-Kernel acceptance is
submitted or claimed.

OP.EXE, MAINE.EXE, and ZUN.COM remain independent active boundary queues and
receive no MAIN v174 credit. `ZUN.COM` remains an MZ executable despite its
extension.

## Continuation

The first evidence-connected hard continuation is the blocked
`carpet_lighting_put_new()` producer itself. Its 0x5A physical/function boundary,
caller, MAP owner, and relocation topology are closed, so a future packet can
focus narrowly on source-language/origin evidence: test only genuinely new legal
TC4J mechanisms or cross-game original-target analogues for the `PUSH DS/POP ES`,
`MUL BX`, `LODSB`, `SHL DI,1`, and `LOOP` sequence. If no natural mechanism is
demonstrated, keep the function blocked or reclassify origin only with independent
evidence; do not use inline assembly as a shortcut to C++ exactness.

## v405 all-artifact provenance scan

The earlier cross-game work concentrated on MAIN-style code and the accepted
TC86 object corpus. v405 broadens the origin check to **every registered
TH01-TH05 artifact image**, including OP, MAINE, and ZUN-family executables.
The eight DIET-wrapped inputs are first restored from private copies using the
pinned DIET 1.45f / DOSBox-X PC-98 toolchain; scans operate on the restored
program image, never on the packer stub.

The structural carpet signature is deliberately stronger than any single
opcode: a near-function prologue followed within 96 bytes by `PUSH DS/POP ES`,
at least two `MUL BX`, `LODSB`, `SHL DI,1`, and `LOOP`. Across all 20 registered
artifact images it has exactly one hit, TH04 MAIN load `0xEA8A`, the reviewed
`carpet_lighting_put_new()` owner. No OP/MAINE/ZUN image supplies an independent
homologous producer.

Private receipt SHA-256:
`86de803fe7b93f0b66b26e33004ab1c0535f936187eb370fa8f7bd7447a02913`.

This is a stronger negative provenance result, not a source-language proof. It
does not authorize target-derived inline assembly; the 90-byte function remains
reviewed/source-present/blocked.
