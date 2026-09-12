# TH04 CIRCLE_TEXT point-number render/put review (v138)

## Scope

Artifact: `th04-main / MAIN.EXE` (`candidate-local-attested`). Target SHA-256:
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The private target remains ignored operator input; it is not committed, patched,
relocated, or published by this packet.

This packet deepens the v136 review of the two final point-number routines in
`CIRCLE_TEXT`:

| Entry | CIRCLE_TEXT | Load | File | Body | Target SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `POINTNUMS_RENDER` | `0AAF:1274` | `0xBD64` | `0xD564` | `0x9A` | `050de3154e84536347926fc05edef5a5a5f1db0d67de4c4fa11f6702c45a1c2f` |
| `@pointnum_put` | `0AAF:130E` | `0xBDFE` | `0xD5FE` | `0x6A` | `e5f760af38c2a844797b17a2052359a819736e69997df376252a91f2a1c9e63d` |

The combined `0x104`-byte target extent has SHA-256
`f289ee26229eb41450a56e81e784563015c3ee16a3a757f54877a4e00230eff0`.
No MZ relocation site overlaps either body. The next TLINK public begins at load
`0xBE68`.

## Boundary and ABI evidence

Fresh attested `th04-ghidra` observations reconstruct both entries contiguously:
`POINTNUMS_RENDER` covers image `0x1BD64..0x1BDFD` (154 bytes), and
`@pointnum_put` covers `0x1BDFE..0x1BE67` (106 bytes). Fresh caller/callee
observations show one caller for the renderer; the renderer calls the scroll
conversion extent and `@pointnum_put`; the put routine has no call edge of its
own. Ghidra names and calling conventions remain provisional target
observations and receive zero exactness credit.

Pinned TASM and the v137 172-owner aggregate TLINK MAP expose matching near
publics at `0AAF:1274` and `0AAF:130E`. Independent 16-bit raw decoding reaches
`RET` at the end of each configured extent: 72 instructions for the renderer
and 49 for put. The retained v138 reviewer report is
`.analysis/gpt-web/th04-main-20260912-v138/function-review-v138.json`
(SHA-256 `f273fe41d3983854d8b0ece617fa2d4f505ced1b40e68be3e5ac430abe4c949c`); it admits both entries only as `reviewed_nonexact` and
reports zero strict rejections.

## Renderer code-owned immediate

The renderer contains a material source/origin seam rather than an ordinary
high-level store. At load `0xBDC1`, target code writes the current numeral width
to `CS:0x12E9`. That address is the immediate word of the later instruction at
load `0xBDD6` that stores the point-number width. The target therefore modifies
an operand in its own executable code before reaching that instruction.

This is direct target evidence, not a Ghidra inference. Ordinary natural TC4J
C++ has no demonstrated mechanism that emits this code-owned write. Explicit
self-modifying source, inline assembly, `#pragma codestring`, copied target
bytes, or instruction patching would violate the campaign rules and are not
used. The observation is strong evidence against treating the routine as an
ordinary standalone C++ translation, but it does not independently prove that
the original source was handwritten assembly.

## `@pointnum_put` natural-source probes

The target put routine is a compact register-resident blitter. Inputs arrive in
AX/DX/CX; it computes the VRAM offset, selects the preshifted numeral bitmap,
clips at the bottom of the 400-line plane, uses `LODSW`, writes one or two bytes
through ES, advances by `ROW_SIZE`, wraps by `PLANE_SIZE`, and terminates with a
`LOOP`. It saves SI, DI, AX, and DX without a BP frame, restores the incoming
AX/DX pair, increments DX by `POINTNUM_W`, and returns.

Two bounded natural TC86 Borland C++ 4.02 probes were compiled through the
pinned ReC98 MS-DOS player with `-O -b- -3 -Z -d -DGAME=4 -ml`. Neither uses
inline assembly, codestrings, target bytes, or object patching.

The first diagnostic treated the final DX:AX side effect as a natural 32-bit
return hypothesis. It compiled to valid TC86 OMF but also carried a header
redefinition warning, so it is diagnostic only. Its CIRCLE_TEXT body is 135
bytes (code SHA-256
`2dbe1ba9f138eeaaf0134f9268350205c3358559d9f2348ab45901b10d0e51d6`)
and immediately establishes `ENTER 0xA` with BP-relative parameter spills.

The warning-free v2 probe keeps the declared `void __fastcall` surface and
models the final register state explicitly. Source SHA-256:
`70b3e648549988225105e1c1f696e2192a6ef43ed31f899854d142ce80fb7dc0`.
The generated object is 590 bytes, raw SHA-256
`b8dfd26eb96852873c3d660654f7163134adba1eaf1c7a3bcfaba4e41938f93f`,
with dependency-normalized SHA-256
`03edf66cd094fdee62c84e1e170dae6b72decf2ffe9198ba2bf6f575f96b7462`.
Its function body is still 135 bytes, SHA-256
`30e17e0728e4dae91cd41d15487051b610b29178b0cc928eea2fdbe7e50f9925`.

The mismatch is structural, not a single spelling choice:

- candidate: `ENTER 0xA` and BP spills for incoming AX/DX; target: no frame and
  explicit `PUSH AX; PUSH DX`;
- candidate: `MOV AX,[SI]; ADD SI,2`; target: `LODSW`;
- candidate: `DEC CX; OR CX,CX; JNZ`; target: `LOOP`;
- candidate: BP-temporary moves for the wrap counter exchange; target:
  `XCHG CX,BX`.

The 32-bit-return and void-fastcall variants therefore fail the same producer
class in independent ways. Further expression-only editing is not justified
without a new compiler mechanism.

## Accounting

v138 deliberately expands the reviewed denominator rather than preserving a
higher percentage. Both routines now have reviewed `blocked` function entries and source-empty
blocked byte-accounting units. Their boundary `source_form` remains
`target-derived-asm` because pinned TASM is part of the observation set, but the
`source_ref` and maintained-source fields are intentionally empty. The residual
assembler is evidence, not accepted source, and receives no source-presence
credit.

Live accounting after admission is:

- reviewed authored bytes: **47,564 / 48,031 exact (99.027711%)**;
- reviewed authored functions: **300 / 307 exact (97.719870%)**;
- exact natural C/C++ owners: **172**;
- reviewed nonexact bytes: **467** across seven blocked functions.

No v138 focused replay or aggregate replay is run because there is no legal
exact producer to promote. No v138 Factory exact claim exists. Standalone TH04
product closure, runtime-storage identity, runtime-scenario validation, and
whole-image exactness remain unestablished.

## Origin status and continuation

ReC98 reconstructs both routines as assembly in 2020 reverse-engineering
commits. That is useful source-shape evidence, not original-language authority.
The correct current classification is therefore a durable source/origin unknown,
not a forced original-ASM verdict.

The strongest evidence-connected continuation is to revisit the v135
`pointnums_add_yellow()` / `pointnums_add_white()` shared-tail owner with this
new subsystem-local evidence. That physical PROC has two public Pascal-near
entries and a delayed shared BP frame that ordinary TC4J C++ probes could not
produce. v138 now adds two independent low-level point-number observations: a
renderer that modifies its own instruction immediate and a put blitter whose
legal natural TC4J forms do not reproduce the frameless `LODSW`/`LOOP` register
shape. A next origin packet should compare the TH04 shared-tail/add/render/put
family against same-era TH02/TH05 target code, physical TASM/TLINK ownership,
and any independently attested original-style signatures. ReC98 assembly alone
must not decide the classification.
