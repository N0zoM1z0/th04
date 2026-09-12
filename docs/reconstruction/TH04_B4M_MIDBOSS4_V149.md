# TH04 B4M Stage 4 midboss producer (v149)

## Result

v149 target-reviews and reconstructs the Stage 4 midboss pattern/update cohort in
`th04-main / MAIN.EXE` as one maintained natural-C++ logical owner.

The exact owner is:

- segment: `B4M_UPDATE_TEXT`;
- map: `13A9:14E8..1ABE`;
- load: `0x14F78..0x1554E`;
- target file: `0x16778..0x16D4E`;
- size: `0x5D7 / 1495` bytes;
- target slice SHA-256:
  `95a328f06ee5b713ba532d5814352755e7587f58892346a507cf6087da6cdf21`.

The selected private target remains read-only and only
`candidate-local-attested`.

## Boundary review

The owner contains four near pattern helpers followed by one FAR dispatcher:

| Entry | Reviewed extent | Result |
| --- | ---: | --- |
| `midboss4_pattern_random_spreads` load `0x14F78` | `0xAF` | Ghidra has no function entry; TASM/raw/dispatcher call close the body. |
| `midboss4_pattern_stack` load `0x15027` | `0xF6` | Ghidra is sparse; target/TASM close the complete body through the next PROC. |
| `midboss4_pattern_aimed` load `0x1511D` | `0xE5` | Ghidra/TASM/raw agree on the complete body. |
| `midboss4_pattern_spiral` load `0x15202` | `0xB2` | Ghidra/TASM/raw agree on the complete body. |
| FAR `midboss4_update()` load `0x152B4` | `0x29B` physical | Ghidra omits internal code/table ownership; target-first review closes the compiler tail. |

Fresh recovery-time Ghidra still has no function at image `0x24F78`. It reports
only 209 body bytes for the `0xF6` stack helper and 479 body bytes for
`midboss4_update()`. The dispatcher database body ends at image `0x25539` and
reports no callers. These are provisional navigation observations only.

Pinned TASM and gap-free target decode show that `midboss4_update()` executes
through `RETF` at load `0x15539`. Load `0x1553A` is one compiler-owned zero
metadata byte. A five-value switch table and five-word jump table occupy
`0x1553B..0x1554E`; every jump word targets an instruction start inside the
reviewed dispatcher. The next PROC, `ENEMY_POS_UPDATE`, starts exactly at load
`0x1554F`.

Target Stage 4 setup stores the FAR dispatcher into `_midboss_update_func`, while
the dispatcher's switch cases directly call the four near helpers. Those
storage/control-flow anchors explain the empty Ghidra caller/xref results and are
part of the target-local boundary evidence.

The ten ordered MZ relocation sites owned by the `0x5D7` slice are:

```text
0x15281 0x15226 0x151D6 0x151A0 0x150B4
0x1509D 0x1504C 0x14FFC 0x154E8 0x1546A
```

## Natural source and physical layout

Maintained source is `src/main/midboss/m4_update.cpp`, SHA-256
`163b085dee1eae0e4898cc3c67c4610bda7800d148db4da3b0e33c693a2f157f`.
It preserves the historical memory model, FAR dispatcher ABI, Pascal-near helper
ABIs, B4M segment/group ownership, and Borland register/code-segment behavior.
`#pragma samecodeseg midboss_reset` selects the target same-group far-call
optimization through ordinary source semantics; it emits no hand-authored bytes.
The renderer declaration is explicitly assigned to `M4_RENDER_TEXT / MAIN_01`
so the target cross-group near function pointer remains correctly linked.

There is no inline assembly, `#pragma codestring`, copied target byte array,
inert padding, fake return, object patch, target patch, or ABI lie.

This owner sits in the middle of the historical monolithic assembler
contribution. Exact replay therefore uses
`config/replay/th04_b4m_prefix_v149.asm.in` (SHA-256
`2f0c0d9ffa530757508469c874d86d9d5bb13dc327ae9c029b1dcb188b2dbd2f`)
to hash-extract the untouched preceding assembler span. The final map tiles the
segment as:

```text
13A9:0522 0FC6 B4M_UPDATE_TEXT th04\b4mpre.asm   # replay-only, zero credit
13A9:14E8 05D7 B4M_UPDATE_TEXT th04/m4u.cpp     # maintained natural C++
13A9:1ABF 1636 B4M_UPDATE_TEXT th04_main.asm     # residual assembler suffix
```

The extracted prefix and untouched suffix are layout plumbing only and receive
no authored-source reconstruction credit.

## OMF and replay

Both final `m4u.obj` files are valid single TC86 Borland C++ 4.02 OMF modules.
Their raw SHA-256 is
`ff0e17730287699014eac1174735bd0e3c216243f7bf60adfe505cb79696a568`;
dependency-timestamp-normalized SHA-256 is
`d133e3c7b4ae458363ae880a517a00bd96d4e17c0eda795c9c71465458b2d963`.
TLINK contributes exactly:

```text
13A9:14E8 05D7 C=CODE S=B4M_UPDATE_TEXT G=MAIN_03 M=th04/m4u.cpp ACBP=28
```

Current-source focused replay:

- `gptweb-v149-midboss4-focused-candidate-009`;
- 91-owner dependency closure;
- receipt SHA-256
  `aa9db7af3bb0f57b497d642111c6eb4ccace759a211eced0b1e46ea0e71575d3`;
- two isolated cold builds, `failures=[]`;
- raw bytes, map placement, all ten ordered relocations, OMF validity, and
  determinism pass.

Candidate-state aggregate replay:

- `gptweb-v149-midboss4-aggregate-candidate-001`;
- all 183 default owners twice;
- receipt SHA-256
  `8d663002e73da722e19d5bd885fde84fc146642512e7154a892ff97dfd38f3b1`;
- `failures=[]`.

Post-promotion aggregate replay:

- `gptweb-v149-midboss4-aggregate-final-001`;
- all 183 default owners twice;
- receipt SHA-256
  `e84ce9c41248d53808acda34dfcabb2fccc5e574103959e111af85b3db1e9c48`;
- `failures=[]`;
- both candidate MAIN images have SHA-256
  `d3ad291274f83186849a93ed89e3b551789f7cf42ea6e86a75a9ce033d01f4af`.

Receiptless focused runs 002 through 006 and 008 are intermediate compiler/layout
experiments and receive no exactness credit. Focused run 007 has a retained
failure receipt bound to a superseded manifest and deterministically causes
broad downstream layout drift. It remains negative producer-routing evidence;
it is not a rejection of the final maintained source.

## Accounting and verification planes

v149 adds 1,495 reviewed authored bytes and five reviewed functions, all exact
under the complete repository-native promotion chain. The live MAIN ledger is
therefore 53,154 / 53,158 exact reviewed authored bytes (99.992475%) and
326 / 327 exact reviewed functions (99.694190%). The only reviewed blocked
function remains the four-byte `snd_load` remainder. Boundary discovery remains
open, so these percentages are not a completion claim.

The focused and aggregate receipts establish repository-native function/extent
exactness only. They do not establish standalone TH04 production-source/link
closure, runtime-storage identity, a runtime scenario, whole-image exactness,
independently pristine target provenance, or Factory Truth Kernel acceptance.
