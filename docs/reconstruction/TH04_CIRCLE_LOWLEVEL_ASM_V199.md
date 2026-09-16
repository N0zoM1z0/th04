# TH04 CIRCLE_TEXT low-level blitter assembly reconstruction (v199)

## Scope

v199 exactly reconstructs three source-distinct low-level `CIRCLE_TEXT` owners
covering load `0xBFF8..0xC0FB` (0x104 bytes, no MZ relocations) in the locally
attested TH04 `MAIN.EXE` target. The complete target-window SHA-256 is
`74629610fa3c200eeeedf8b09b73ab4d97b1360898bcc2dc8929b4b2995090f5`.

The reviewed producers are:

- `yuuka5_backdrop_colorfill()`: `0AAF:1508`, load `0xBFF8..0xC019`, file
  `0xD7F8..0xD819`, 0x22 bytes, SHA-256
  `4e9e2e4ddd4904858b16f9db67f866f28259afa2224b5b6cb9ae978ae0a4fae0`;
- `z_super_put_16x16_mono_raw(int)`: `0AAF:152A`, body `0xC01A..0xC098`
  plus source-owned `EVEN` at `0xC099`, physical size 0x80, SHA-256
  `46037ebc43636103454622fd9ebf48c3b47b4a02a20bf867822006f5037ad152`;
- `bb_txt_put_8_raw(unsigned int,unsigned int)`: `0AAF:15AA`, body
  `0xC09A..0xC0FA` plus source-owned `EVEN` at `0xC0FB`, physical size 0x62,
  SHA-256
  `83f725d818187b5d3d92270af50b04d47bcd89a2c75959a31c320b2906bf5eda`.

Exact natural `items_invalidate()` starts immediately at `0xC0FC`.

## Boundary, origin, and source form

The cold scaffold independently proves three source seams: Yuuka was inline in
`th04_main.asm`, while z-super and BB-text were separate includes. Fresh
attested Ghidra constructs no function containing any of these three entries, so
no database boundary receives exactness credit. Gap-free target decoding,
TASM PROC/include seams, TLINK publics, alignment ownership, and cold replay
close the extents instead.

The Yuuka inline replacement is fail-closed. Replay accepts only focused
scaffold SHA-256
`19449d4a05b906ef2905514ba574a029fb030cbbd5cc2c973e6eb31f7e791ec8`
or aggregate scaffold SHA-256
`ad927fde01b2d7af69e091f1adaf67c1f974769b7442c827d6e8281b08162935`.
The removed 427-byte span is bound to SHA-256
`6e5eee96e1e50273d031043faa32756352373de909fbed4c399d1f2f86727041`.

ReC98 source is hypothesis only: the relevant z-super and BB-text assembly was
introduced in reverse-engineering-era commits. A bounded legal TC86 Borland C++
4.02 mechanism probe instead tests the natural producer hypothesis directly.
Probe source SHA-256 is
`5f6e9edfbaabd7cb9c99fd8270883903d8c162666169ca12e5804cd0fe514316`;
valid OMF SHA-256 is
`86ee179e33a5cc66af973638828b09dbcb4c83f5262ae76260d49a43abab1d0c`.

The mechanism results are structural negatives:

- Yuuka typed far-pointer C++ emits 64 bytes versus target 34 and adds BP/far-
  pointer state, `LES`, explicit zero stores, and expanded loop control;
- typed z-super emits 122 bytes versus target 127 but uses three explicit
  arguments, BP/LES, and `RET 6`; the target consumes implicit AX/CX plus one
  Pascal stack argument, uses DS/ES string-register state, and returns `RET 2`;
- typed BB-text emits 105 bytes versus target 97 with BP/LES and DEC/OR/JNZ;
  the target consumes AX/DX plus implicit CX and caller-supplied ES, using
  `LODSD`, `MOVSD`, and `LOOP`.

The maintained sources are therefore evidence-backed irreducible/original-style
symbolic assembly, not natural C++ and not a claim of historical source text:

- `src/main/boss/yuuka5_backdrop.asm` SHA-256
  `67baeaefa2221ce6caeea13f3cdc24d81dacc8de8027db74e663cfed13e36833`;
- `src/main/formats/z_super_put_16x16_mono.asm` SHA-256
  `ecb076cbe6952aa3a2bade09a82fda1d7203ef378a480f644a3e173079a545dc`;
- `src/main/formats/bb_txt_put.asm` SHA-256
  `63edd4b19f45fc83b0c1aa05f7e5c7f34a1040d7a3775aa4c21fa3a27cf641b4`.

They contain symbolic instructions/constants and real source-level alignment,
with no target-derived byte arrays, `__emit__`, C/C++ inline assembly,
codestrings, fake returns, target patching, or inert padding.

## Independent target routing

TH05 MAIN strongly corroborates the BB-text producer. Its 97-byte homolog at
load `0xE51A` differs from TH04 only in the linked `_bb_txt_seg` word at body
offsets 0x1A..0x1B; the remaining 95/97 bytes are identical. The TH05 homolog
SHA-256 is
`29e8a3237fe4333f8bf6b42aa15da66038b2192571d2b577e2ca72ab93b6f917`.
Yuuka and this z-super variant have only shorter shared target runs, so v199 does
not claim full cross-game identity for those two.

OP, MAINE, and ZUN were checked through their independently attested unpacked
payloads. Longest exact runs for Yuuka are 3/3/2 bytes, z-super 18/18/3, and
BB-text 4/5/4 across OP/MAINE/ZUN respectively. This is bounded negative routing
evidence only; no MAIN source, boundary, or exactness credit transfers to them.

## Exact replay

Focused `gptweb-v199-circle-lowlevel-focused-candidate-001` selects 135 owners
and passes twice with `failures=[]`; receipt SHA-256 is
`4e83f8bea5428a326ae7a49e8ad99163e5aa162fe9fc94e32057e7d20798c8e1`.
All three v199 owners are `raw=True`, `map=True`, `relocs=True`. Focused A/B
`th04_main.obj` dependency-normalized SHA-256 is
`489004aa4f13c15b6527d2dd2bc4b1c902f5b506aaa3a84758dd85aab40c9348`.

Candidate aggregate `gptweb-v199-circle-lowlevel-aggregate-candidate-001`
selects 239 default owners twice and passes with receipt SHA-256
`5fbbf4dbabbe98551e9e58353f3ce34d10b54cccef9697e122496b2fac9e0dc6`.
Post-promotion aggregate `gptweb-v199-circle-lowlevel-aggregate-final-001`
passes the same 239 tracked owners twice; receipt SHA-256 is
`bf2822d8e14509305b547f214dc76557e093ac13b7ee842a4851a25c6a9c8cb1`.
Both aggregates bind manifest SHA-256
`d920aa40684ef59551118e195ec87c8c093c8a4b3d5702e7cd3de880a222717b`.
A/B final MAP SHA-256 is
`0465b4e10041a2c2dd718e89c8432a97a7668a53af171f2c52285e191676c375`;
A/B candidate MAIN SHA-256 is
`a07df1577dae48c3513627f5fd5c593f037bc1a4d103e8e7a010386024e8b759`;
final A/B `th04_main.obj` dependency-normalized SHA-256 is
`f17dd6106bc34437bb6308eb91c731b62df382e402e435b299e5c5157e38c04d`.
Raw OMF timestamp differences are retained rather than hidden.

## Accounting and lifecycle

The three logical rows move from `reconstruct` to the independent `attest-asm`
plane and deliberately remain outside `config/th04_main_authored_functions.csv`.
MAIN C/C++ accounting therefore remains **75,482 / 81,141 exact bytes
(93.025721%)** and **458 / 481 exact functions (95.218295%)**. MAIN routing is
505 reconstruction candidates and 63 ASM attestations. Generated progress
reports **34 exact original-style ASM physical units / 4,986 bytes**.

`.analysis/` began at **3,725,535,946 bytes**, peaked at
**3,916,723,352 bytes**, and after bounded cleanup is **3,804,187,834 bytes** before final CI. Full final `python3 scripts/ci.py` returns `CI: PASS` and leaves `.analysis/` at **3,804,193,967 bytes**, net growth **78,658,021 bytes** from entry. Focused and candidate replay trees are receipt-only. All three
receipts plus final OBJ/MAP/candidate MAIN are retained in bounded v199 scratch;
the complete 239-owner post-promotion aggregate remains the current cold
baseline. Older baselines, targets, toolchains, Wine/Ghidra state, and
legacy/unknown analysis content remain untouched.

Repository-native physical-owner exactness is established for all three v199
owners. Standalone product closure, whole-image exactness, runtime-storage
identity, runtime scenarios, portable runtime, independent pristine provenance,
and v199 Factory Truth-Kernel acceptance remain unestablished.

Next review the complete preceding CIRCLE seam `0xBE68..0xBF15` (0xAE bytes):
`SHOT_LASER_PUT_RAW`, NOP `0xBECB`, `elly_backdrop_colorfill()`,
`mai_yuki_backdrop_colorfill()`, and NOP `0xBF15`. v198 starts at the next byte.
Treat it as one source/include/origin packet rather than harvesting the laser
routine alone.
