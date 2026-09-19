# TH04 B4M Stage X midboss producer (v151)

## Result

v151 target-reviews and exactly reconstructs the Stage X midboss helper and
update cohort in `th04-main / MAIN.EXE` as one maintained natural-C++ logical
owner.

The exact owner is:

- segment: `B4M_UPDATE_TEXT`;
- map: `13A9:0C1F..1007`;
- load: `0x146AF..0x14A97`;
- target file: `0x15EAF..0x16297`;
- size: `0x3E9 / 1001` bytes;
- target slice SHA-256:
  `ede347aa476ff6f4ee4ed70b19fa98d2a0ace591b0303f21fa49feeb09db52a9`.

The selected private target remains read-only and only
`candidate-local-attested`.

## Boundary review

The owner contains seven near helpers followed by one FAR dispatcher:

| Entry | Reviewed physical extent | Target-first result |
| --- | ---: | --- |
| `midbossx_orbit_step_reverse` load `0x146AF` | `0x51` | Fresh Ghidra has no function at the entry; TASM/raw plus the dispatcher call and the preceding Stage 3 table seam close the helper. |
| `midbossx_wave_step` load `0x14700` | `0x6F` | Fresh Ghidra/TASM/raw and the next PROC agree. |
| `midbossx_pattern_ring` load `0x1476F` | `0x29` | Fresh Ghidra/TASM/raw and the next PROC agree. |
| `midbossx_pattern_cloud_ring` load `0x14798` | `0x43` | Fresh Ghidra/TASM/raw and the next PROC agree. |
| `midbossx_pattern_bounce_spread` load `0x147DB` | `0x4D` | Fresh Ghidra/TASM/raw and the next PROC agree. |
| `midbossx_pattern_dual_ring` load `0x14828` | `0x46` | Fresh Ghidra/TASM/raw and the next PROC agree. |
| `midbossx_pattern_events` load `0x1486E` | `0xDE` | Ghidra is sparse; executable code plus one metadata byte and a 21-value/21-jump compiler table form the physical extent. |
| FAR `midbossx_update()` load `0x1494C` | `0x14C` | Fresh Ghidra misses the entry; executable code plus one metadata byte and seven jump words form the physical extent. |

`midbossx_pattern_events` executes through `RET` at load `0x148F6`.
`0x148F7` is one zero compiler metadata byte. The 21 compare values and 21 jump
words occupy `0x148F8..0x1494B`; every jump word resolves to an instruction
start in the reviewed helper.

FAR `midbossx_update()` starts at the next byte. It executes through `RETF` at
load `0x14A88`; `0x14A89` is one zero compiler metadata byte and seven jump
words occupy `0x14A8A..0x14A97`. All seven targets are instruction starts.
Stage X setup independently installs this FAR entry through
`_midboss_update_func`.

The physical seams are target-local and explicit. The preceding Stage 3
`midboss3_update()` compiler table ends exactly at load `0x146AE`. The
independently included `gather_point_render()` starts at load `0x14A98` and
ends at `0x14AF1`; it is not absorbed into the authored Stage X owner merely by
adjacency.

The nine ordered MZ relocation sites owned by the `0x3E9` slice are:

```text
0x148E6 0x148D3 0x148A9 0x14896 0x14824
0x147D7 0x14760 0x146F1 0x146D5
```

## Natural source

Maintained source is `src/main/midboss/mx_update.cpp`, SHA-256
`37c111c9b96154af61071a1354f3292e8aef6fe8d0cb0937fb1165dcdac11d75`.
It preserves the large memory model, B4M/MAIN_03 code ownership, near helper
ABIs, FAR update ABI, ordinary TH04 bullet/item types, and the historical
`polar()` fixed-point interface. No inline assembly, `#pragma codestring`,
copied target-byte array, inert padding, fake return, object patch, target
patch, or ABI lie is used.

Target-local item-type review matters here. The target `PUSH 2` in the first
four event cases is TH04 `IT_DREAM`; inheriting TH02's enum meaning would have
misidentified it as a bomb item.

## Compiler-shape evidence

The first natural dispatcher source used early `break` exits. TC4J emitted a
`0x3E4` CODE contribution, five bytes shorter than target, while already placing
public `@MIDBOSSX_UPDATE$QV` at the exact relative offset `0x29D`. Replacing the
breaks with explicit shared `goto` exits produced the identical `0x3E4` machine
code. These two forms are therefore one durable negative result, not separate
near-matches to keep retrying.

Target/candidate disassembly localized all five missing bytes to the phase 0/1/2
threshold control flow. The target expresses each threshold as a branch to a
shared return plus a separate jump to the phase-advance block. Writing the
natural source positively instead—entering the attack block only when the
threshold is reached, then entering phase advance only at the second
threshold—makes TC4J emit exactly `0x3E9` CODE bytes while preserving the exact
FAR-public offset.

One final focused replay then differed by only two bytes in
`midbossx_pattern_bounce_spread`: target `ADD AL,0xB8` versus compiler
`SUB AL,0x48`. These are the same 8-bit angle operation modulo 256. Expressing
that natural angle delta as `+ 0xB8` instead of `- 0x48` makes TC4J select the
target instruction without changing semantics or ABI.

A final production-profile standalone probe retains exact `0x3E9` CODE and FAR
public `0x29D`; focused cold replay supplies the authoritative linked object
identity below.

## Independent gather seam and replay gate

Removing Stage X from the historical zero-credit B4M assembler prefix also
removes the literal
`include th04/main/gather_point_render.asm` line that followed it. v151 keeps
that renderer outside authored reconstruction credit by re-materializing the
unchanged include through symbolic wrapper
`config/replay/th04_b4m_gather_v151.asm`.

A standalone TASM 5.0 probe emits exactly `0x5A` CODE bytes. The final cold
object has:

- raw SHA-256:
  `4f02dd737e759bdf2fe5175a420982c3d3e2f350d875cdd4498444c3b856a111`;
- dependency-normalized SHA-256:
  `f29872764b95f021c4bfcd3ab77c897e91c1c5fa5ec67b7c651d13f5f47069b6`;
- linked target/candidate slice SHA-256:
  `a435b2f6443e99048b73017bdab8a374337ca524dc65a72640879889a8dae9af`;
- no overlapping MZ relocations.

The wrapper is replay plumbing only. It receives no authored source or function
credit.

v151 also extends `scripts/replay_th04_main_exact_units.py` with the generic
`auxiliary_extents` gate. A declared zero-credit linked extent now fails closed
unless its complete linked raw slice, MAP contribution, ordered relocation
overlap, and OMF validity pass in both cold builds. A/B determinism also binds
the candidate slice and normalized auxiliary OMF. Two unit tests cover the
positive path and rejection of a linked-byte mismatch. This prevents a
zero-credit code-bearing auxiliary object from being admitted merely because its
OMF container is valid.

The final B4M physical layout is:

```text
13A9:0522 06FD B4M_UPDATE_TEXT th04\b4mpre.asm   # replay-only, zero credit
13A9:0C1F 03E9 B4M_UPDATE_TEXT th04/mxu.cpp      # maintained Stage X C++
13A9:1008 005A B4M_UPDATE_TEXT th04\b4mgath.asm  # replay-only gather, zero credit
13A9:1062 0486 B4M_UPDATE_TEXT th04/m2u.cpp      # exact v150 Stage 2 C++
13A9:14E8 05D7 B4M_UPDATE_TEXT th04/m4u.cpp      # exact v149 Stage 4 C++
13A9:1ABF 1636 B4M_UPDATE_TEXT th04_main.asm     # residual assembler suffix
```

## Exact replay

Current-source focused replay:

- run: `gptweb-v151-midbossx-focused-candidate-003`;
- 93-owner dependency closure;
- receipt SHA-256:
  `1240e616f81f446a83294c15df8c5ebfb51fb9d904cc56fa16438e1ea9b315c5`;
- two isolated cold builds, `failures=[]`;
- target/candidate owner SHA-256:
  `ede347aa476ff6f4ee4ed70b19fa98d2a0ace591b0303f21fa49feeb09db52a9`;
- exact map `13A9:0C1F`, size `0x3E9`;
- all nine ordered target MZ relocations exact;
- `mxu.obj` raw SHA-256:
  `c16110ba58be6e291b6383953512bdc02cc03243d873a09b2153ca6cfb527853`;
- `mxu.obj` dependency-normalized SHA-256:
  `71634ab85f6870da3e6d836d1d804938df398a1b62766afa62f667a16b3691fc`;
- linked zero-credit gather raw/map/relocation/OMF checks all pass.

Candidate-state aggregate replay:

- run: `gptweb-v151-midbossx-aggregate-candidate-001`;
- all 185 default owners twice;
- receipt SHA-256:
  `c56c8838af70febf6963c3ebfaf7561e3336f21dc1e79c226a3e692069b16b26`;
- `failures=[]`;
- both candidate MAIN images SHA-256:
  `e94e9ba549c0b75a0b116fb98dd583ecf590f02681866a1df1f02d4814d8aef0`.

The first post-promotion run,
`gptweb-v151-midbossx-aggregate-final-001`, produced no receipt. Before any TH04
Oracle comparison, eleven unrelated TH01 `Pipeline/bmp2arr.com` asset-generation
commands terminated abnormally in the cold ReC98 build. Git/source status did not
change, no Borland producer remained active, and the immediately preceding
candidate aggregate had passed under the same v151 manifest. This is retained as
an infrastructure failure, not a TH04 byte rejection.

Post-promotion replay was therefore repeated without source or ledger changes:

- run: `gptweb-v151-midbossx-aggregate-final-002`;
- all 185 default owners twice;
- receipt SHA-256:
  `76ed549eb80e9e51609c99df5366ea432685914f1767f73d803b7eb81bbd9019`;
- `failures=[]`;
- both candidate MAIN images SHA-256:
  `e94e9ba549c0b75a0b116fb98dd583ecf590f02681866a1df1f02d4814d8aef0`;
- Stage X and linked gather identities are unchanged from focused replay.

## Accounting and verification planes

v151 adds 1,001 reviewed authored bytes and eight reviewed functions, all exact
under the complete repository-native promotion chain. The live MAIN ledger is
therefore 55,313 / 55,317 exact reviewed authored bytes (99.992769%) and
339 / 340 exact reviewed functions (99.705882%), with 185 default exact owners.
The only reviewed blocked function remains the four-byte `snd_load` remainder.
Boundary discovery remains open, so these percentages are not a completion
claim.

The focused and aggregate receipts establish repository-native function/extent
exactness only. They do not establish standalone TH04 production-source/link
closure, runtime-storage identity, a runtime scenario, whole-image exactness,
independently pristine target provenance, or Factory Truth Kernel acceptance.
