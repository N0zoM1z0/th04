# TH04 MAIN CIRCLE item-splash renderer v188

## Scope and recovery

This packet continues target-first review of the `MAIN.EXE` CIRCLE_TEXT render
cohort. The private target remains ignored operator input with canonicality
`candidate-local-attested`; it is never modified, relocated, published, or
committed. Ghidra output is target-bound provisional evidence and receives no
exactness credit by itself.

The session starts from clean committed HEAD
`7343d926e55daa10824f1dd1abbc5072707fab5b`, tree
`9da184bb172ca14ae9f37a0db0038b2d49df8ab3`, branch `main`, upstream
`origin/main`, ahead 1 / behind 0. `.analysis/` measured **8,870,791,896 bytes**
at entry. Mandatory preflight/status/boundary gates passed. The live reviewed
MAIN denominator was 75,064 / 80,549 exact authored bytes and 454 / 482 exact
reviewed functions. OP.EXE, MAINE.EXE, and ZUN.COM remained separate active
queues with 94, 72, and 13 unreviewed authored candidates respectively.

All required repository and Factory contracts were read before editing.
`th04-ghidra` discovery exposed ten operations and no `get_metadata`. Provider
`check {}` passed for repository `th04`, target `target:th04-main`, SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
Repository-native Ghidra independently passed the 6,144-byte MZ header, entry,
1,136 ordered relocations, load mapping/digest, and sampled bytes. Required
TC4J/TASM/TLINK toolchain surfaces passed; optional host `wine64` drift remains
informational.

The stale `sub_11DE6` prompt route was not reopened. The live repository already
classifies that physical shot seam through the accepted v143 original-style ASM
owner.

## Render-cohort boundary review

Fresh target-bound Ghidra `function`, `callers`, `callees`, and decompiler
queries were used only as navigation. They reconfirmed the v186 reviewed
boundaries:

- `ITEM_SPLASHES_RENDER`: linear `0x1C17C`, load `0xC17C`, size `0x83`;
- `@spark_render`: linear `0x1C200`, load `0xC200`, size `0x65`;
- `_sparks_render`: linear `0x1C2B2`, load `0xC2B2`, size `0x3B`;
- `@item_splash_dot_render`: linear `0x1C332`, load `0xC332`, size `0x1C`;
- `sub_C34E`: load `0xC34E`, size `0x16`, still has no Ghidra function entry.

The call graph forms one coherent render-side packet: gameplay calls
`_sparks_render`, which calls `@spark_render`; item-splash rendering calls the
splash-dot primitive. The three bytes at load `0xC1FF`, `0xC265`, and `0xC2ED`
remain separate source-owned layout rather than function bodies.

## Independent TH05 target cross-check

The TH05 MAIN target was used as an independent target observation, not through
ReC98 source authority. TH05 preserves the complete architectures of all four
render entries. In particular, `@item_splash_dot_render` is byte-identical
between TH04 and TH05, while the higher-level routines vary only where expected
for game-local constants and linked addresses. TH05 uses 32 splash dots and 64
sparks; TH04 uses 64 splash dots and 96 sparks.

Retained target-slice SHA-256 values are:

- TH04 item-splash renderer: `d1a0dce276dcc8dadf49cedf2229c4ef2d4308e533fe674fad3ad9da99d59d87`;
- TH04 spark renderer: `b5e6cc168a07ac05aa5931c03e10d9e0b87a47d9511cced1a887e5fe100bf32e`;
- TH04 spark loop: `e83d1980d89cf5e35d236d42df2db372709757b9b0d67c7da5c7e5f8f6c8baa8`;
- TH04/TH05 splash-dot primitive: `4898597cc5a5db17fa9565240b3a28784cb27361dc207996af2cafde6510b313`;
- TH05 item-splash renderer: `aca75a762c0a8b59154df0978e331fe13a9fc0beac3156c17296af3ce894f71e`;
- TH05 spark renderer: `d5843cf2c40ad227d9556a3db59975f017d8d07f41828d47e7f4e8f6ad806f78`;
- TH05 spark loop: `25e68508049261d24bbaa17416410a3a323cb0dd30b47895e48016f46c101623`.

ReC98 history shows that the relevant `.asm` files are reconstruction-era
reverse-engineering sources. Their extension or cross-game include reuse is not
accepted as proof of the historical source language.

## Natural ITEM_SPLASHES_RENDER source

The maintained TH04 declaration surface is `src/main/item/splash.hpp`, SHA-256
`1fc0ed49dab1dd65164113ab482c3512e3bafe38a3258c73f7ca33fcccc63118`.
It preserves the target-local splash structure and game-specific dot count, and
uses the target-proved mixed ABI for the low-level primitive. A minimal TC4J
caller probe proves that

`extern "C" void __fastcall near item_splash_dot_render(screen_x_t, vram_y_t)`

emits the exact target/TASM external public `@item_splash_dot_render`, with the
two arguments in AX/DX and no C++ `$qii` suffix. The retained ABI probe object
SHA-256 is
`5c46bda648c2eaeb7660e3e6d57742b84e215935fe686aae613b6dba407c877b`.
No alias, symbol rewrite, or ABI lie is used.

The maintained natural renderer is `src/main/item/splashes_render.cpp`, SHA-256
`3610cfb382260aef5c418641ad147cbf6adaee05686a9f70fb8e9efb83fe3c3e`.
It contains no inline assembly, target-derived byte arrays, `#pragma codestring`,
fake returns, inert padding, or target patching.

Target extent:

- segment: CIRCLE_TEXT;
- map: `0AAF:168C..170E`;
- load: `0xC17C..0xC1FE`;
- file: `0xD97C..0xD9FE`;
- size: `0x83 / 131` bytes;
- target SHA-256:
  `d1a0dce276dcc8dadf49cedf2229c4ef2d4308e533fe674fad3ad9da99d59d87`.

A calibrated production-profile TC86 probe emits exactly 131 CODE bytes. After
ordering the two natural local declarations according to the observed stack
frame, every fixed instruction byte matches the target. The only pre-link byte
differences are ordinary relocatable/link-resolved fields for the GRCG call,
`item_splashes`, `drawpoint`, FAR `vector2_at`, scroll conversion, and the
splash-dot call. The final probe CODE SHA-256 is
`56c630bdab005208bc7aa039bb78002615a669bbbf7165ab068f73e5e06444fe`.

## Physical CIRCLE_TEXT split and layout ownership

The v185/v186 replay residual had the item renderer, its following `db 0`, the
spark renderer, spark update/render, and later code in one target-derived
scaffold object. v188 separates only the reviewed natural renderer while
preserving zero-credit replay ownership of all surrounding bytes.

The final physical order is:

- `th04\cirsuf185.asm`: CIRCLE_TEXT `0AAF:1658`, size `0x34`;
- `th04/isprend.cpp`: CIRCLE_TEXT `0AAF:168C`, size `0x83`;
- `th04\itemrendgap188.asm`: CIRCLE_TEXT `0AAF:170F`, size `0x01`;
- `th04\cirsuf188.asm`: CIRCLE_TEXT `0AAF:1710`, size `0xEE`;
- then the existing v186/v187 natural owners beginning at `0AAF:17FE`.

The one-byte owner is extracted hash-bound from the original source seam; the
replay does not hand-write a target byte. This is required because the following
TASM residual is word-aligned. An earlier v188 experiment left that byte inside
the residual, causing TLINK to align the contribution at `0x1710` while still
retaining the byte, shifting every downstream target by two bytes. That failed
replay was diagnostic only and received no exactness credit.

The v188 residual wrapper `config/replay/th04_circle_render_suffix_v188.asm.in`,
SHA-256
`6749178894e2a720e0a6382b51c151e0add14fbbd8c1bd1f7aa62d206c055e5a`,
adds only the external symbol declaration required after separating the previous
same-object GRCG helper reference. It remains replay-only, target-derived
scaffold plumbing and receives zero reconstruction credit.

## Exact Oracles

Final focused replay:

- run: `gptweb-v188-item-splashes-render-focused-candidate-005`;
- 117 selected owners, two isolated cold builds;
- receipt SHA-256:
  `8f8670c8c1c5b28e4dc92f44b8bb7710d5b8fc6e56af22e67f50234694399f3e`;
- natural A/B `isprend.obj` SHA-256:
  `484a63c6a6e846afc40e61893b27fa416aaab1352117f9d273daa76cfe2cfdd5`;
- dependency-timestamp-normalized object SHA-256:
  `f92dd3b2c94d645df5221fae2377f65f9c5ac8bae865f828e0e627f5abbdcd0a`;
- target/candidate renderer SHA-256:
  `d1a0dce276dcc8dadf49cedf2229c4ef2d4308e533fe674fad3ad9da99d59d87`;
- target/candidate overlapping relocation: load `0xC1AE`;
- A/B focused MAP SHA-256:
  `5513d701fcca461bfc486337fe75c5f158626380c58c3ee4161c72af7e1a57b6`;
- A/B focused candidate MAIN SHA-256:
  `518811db1bf863343e7bf69fdad4613c537cd08113b8a40538e0519ee46512df`;
- natural raw/MAP/relocation verdicts: exact;
- zero-credit prefix, one-byte layout owner, and render residual:
  raw/MAP/relocation verdicts all exact.

Candidate-state aggregate:

- run: `gptweb-v188-item-splashes-render-aggregate-candidate-001`;
- 221 owners, twice;
- receipt SHA-256:
  `7a1c0c2fafb95930bb8f77a3a5f9958836a9414dc1581f53b4af50c00cf40787`;
- A/B MAP SHA-256:
  `b3199896ae52684f03ac8b154e701178d2fcc9187442736174d95afc5741e6a7`;
- A/B candidate MAIN SHA-256:
  `205e42067b0eb3534dc83deba125ebf845c1c153f6515ebe60430d3a79f21bd9`;
- every candidate-state default owner passes raw/MAP/ordered-relocation gates,
  including accepted owners affected by the maintained item-splash header.

Post-promotion tracked aggregate:

- run: `gptweb-v188-item-splashes-render-aggregate-final-001`;
- 221 tracked default owners, twice;
- receipt SHA-256:
  `cc8b4b635f74d1f7cbad11b370ec22b25a799c4944bfa7364a287916e90c95f2`;
- tracked manifest SHA-256:
  `4fdf0859833367615419ad2279685abf285f52b938ed1a8285894b72e0b8adb7`;
- A/B MAP SHA-256:
  `b3199896ae52684f03ac8b154e701178d2fcc9187442736174d95afc5741e6a7`;
- A/B candidate MAIN SHA-256 remains
  `205e42067b0eb3534dc83deba125ebf845c1c153f6515ebe60430d3a79f21bd9`;
- natural owner plus all three zero-credit physical extents remain exact.


Recovery rebind after the interrupted checkpoint found a later post-promotion
aggregate, `gptweb-v188-item-splashes-render-aggregate-final-002`. It binds
the same tracked manifest SHA-256
`4fdf0859833367615419ad2279685abf285f52b938ed1a8285894b72e0b8adb7`,
passes all 221 default owners twice with `failures=[]`, and reproduces the same
natural `isprend.obj`, MAP, and candidate MAIN identities as final-001. Its
receipt SHA-256 is
`86dd3de8f957a5dc93c067c9ae12d765dae153908dd1d008bd337cd1fa24cbff`.
Raw hashes of several auxiliary Borland/TASM objects differ between the two
cold runs because dependency timestamp records are intentionally retained in
the raw OMF identity; normalized/link/raw-owner/MAP/ordered-relocation verdicts
remain passing. This is a recovery/current-manifest confirmation, not a new
source or exactness scope.

## Function review

The fail-closed function review uses the 221-owner candidate aggregate MAP,
target-bound metadata that contains the v186-reviewed `0x1C17C` entry, the
pinned target, and an independently validated raw linear decode. Report SHA-256
is `cc5e2795324c2cc543d00709874dd230c8a92b287b4fa1fb7d1180806c3e3eba`.
The target row is a 131-byte, 48-instruction body ending in `RET`; Ghidra min/max,
TLINK public, exact owner, source, and file mapping agree. The generic writer
would modify 45 historical rows, so only `th04-main-fn-1c17c` is manually merged
from blocked to exact. No neighboring render function receives exactness credit.

## Negative evidence: `_sparks_render`

The same packet deliberately tested a structurally meaningful blocked caller
rather than stopping at the easy win. A natural typed TC4J probe emits a 59-byte
skeleton matching the target size and most control flow. A second
register-lifetime hypothesis closes most remaining instruction structure but
emits 61 bytes because Borland's three-integer `__fastcall` convention places
the third argument in BX and inserts `MOV BX,CX`, while the target caller only
loads CL. The pseudo-register expression also yields SHR where the target uses
SAR. The two retained CODE SHA-256 values are
`f91e074277952e14566fa167810388989670a57c25e4d2e8a5895aedbc2ca6e5`
and `dc3362d5ff3609cdd5c73121464332ae43abc74ee2f50dcd59b56ae2fdd3ca99`.

This is durable negative evidence, not a reason to manufacture an ABI. The
existing `_sparks_render` reviewed function remains blocked. The low-level
`@spark_render` and `@item_splash_dot_render` functions also remain blocked;
TH05 target similarity alone does not decide C++ versus original/shared ASM
origin.

## Failed intermediate replays

Intermediate failures are retained as diagnostic history only:

1. candidate-001 failed before building because the candidate had not yet been
   registered in `units.csv`; no byte verdict existed.
2. candidate-002 compiled the natural C++ but the newly split TASM residual
   lacked an external GRCG helper declaration; no byte verdict existed.
3. candidate-003 compiled/TASM-assembled but TLINK exposed the initial wrong C++
   linkage declaration for `item_splash_dot_render`; the direct ABI probe then
   proved target-consistent C-fastcall linkage.
4. candidate-004 produced a real failing receipt and exposed incorrect physical
   ownership of the `0xC1FF` layout byte. Keeping that byte inside the
   word-aligned residual shifted subsequent link targets by two bytes. The final
   byte-aligned one-byte owner corrects the physical model.

No failed run is exactness evidence.

## Accounting and verification planes

After promotion, live MAIN accounting is:

- exact reviewed authored bytes: **75,195 / 80,680 = 93.201537%**;
- exact reviewed authored functions: **455 / 482 = 94.398340%**;
- blocked functions: 27;
- unreviewed authored candidates: 50;
- original-style ASM attestation observations: 36.

OP.EXE, MAINE.EXE, and ZUN.COM remain independent active queues with 94, 72, and
13 unreviewed authored candidates. No MAIN credit transfers to them. ZUN.COM is
still treated as an MZ executable despite its extension.

This packet proves exact natural-C++ ownership of `ITEM_SPLASHES_RENDER` and
revalidates the complete current exact cohort under the maintained splash header.
It does not establish standalone TH04 product compile/link closure, whole-image
exactness, runtime-storage identity, runtime-scenario validation, portable
runtime validation, independent pristine-release provenance, or Factory
Truth-Kernel acceptance.

## Analysis retention

Before bounded cleanup the v188 replay/probe work raised `.analysis/` to
9,177,319,742 bytes. With no active producer, compact durable evidence was
retained for the focused/candidate/final receipts, final `isprend.obj` and MAP,
function-review outputs, compiler/ABI negative probes, and independent TH04/TH05
target slices. Only explicit current-session failed/superseded replay trees,
the successful focused/candidate full trees, and the current-session Wine probe
workspace/symlink were deleted. The complete post-promotion aggregate remains as
the current cold baseline.

After recovery rebind and the full final CI:

- `.analysis/`: **9,008,251,083 bytes**;
- net growth from entry: **137,459,187 bytes**;
- v188 compact scratch: **9,485,385 bytes**;
- compact `durable-final`: **8,535,548 bytes**;
- retained `aggregate-final-001`: **63,954,856 bytes**;
- retained later current-manifest `aggregate-final-002`: **63,946,664 bytes**.

Both full post-promotion aggregates are retained because they are bounded v188
reproducible evidence and the packet remains below the 256 MiB soft growth
trigger. `final-002` is the latest current cold baseline. The reconstructed
ignored session manifest SHA-256 is
`20a1095b5b416369c4df489aef75767c17a0ffd762ea363a7fd585a0ca39cec3`; it records
that an earlier local probe bootstrap had overwritten the ignored scratch
manifest before recovery classification, so its contents were rebuilt only from
actual retained files and receipts. v187 and older baselines, the retained v187
Factory lock-failure reproducer, private targets, toolchains, Wine/Ghidra state,
and legacy or unknown analysis content were untouched.

## Next structural packet

Continue the same render cohort, but do not force source language. The strongest
next origin/source question is the pair `@item_splash_dot_render` and
`@spark_render`: the splash-dot body is byte-identical in TH04/TH05, and the
spark-render body has a cross-game invariant instruction skeleton. Test whether
legal natural TC4J can produce their LODS/LOOP/ES-override register ABI; if not,
use the independent cross-game target evidence to classify original/shared ASM
only when the evidence is sufficient. Keep `_sparks_render`'s v188 fastcall
negative and `_sparks_update`'s v186 71-vs-76 negative intact unless a genuinely
new compiler/ABI mechanism appears. `sub_C34E` remains the adjacent Ghidra-missed
source/origin seam.
