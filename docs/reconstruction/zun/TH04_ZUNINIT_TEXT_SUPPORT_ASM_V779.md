# ZUNINIT text support symbolic ASM owner (v779)

## Physical owner and source classification

The attested TH04 ZUN.COM decoded payload contains the contiguous 77-byte
ZUNINIT text-support span at `th04-zun / com-payload / 0x7B0..0x7FC`, SHA-256
`6bedcd29d5f95303e05e868d625f84a494b8cec386b5ba3684fd03a374256017`.
The reviewed sub-extents are the 18-byte Shift-JIS converter at `0x7B0` and
the 59-byte PC-98 text VRAM writer at `0x7C2`; neither has a relocation.

This is classified as **original-style ASM by inference**, not as recovered
literal historical source. Both routines take register arguments and use a
near call relationship with no C/C++ stack ABI. The writer directly sets ES
to the PC-98 character and attribute planes, uses `STOSW`, and accesses its
strings through CS. Independent hash-attested TH02 and TH04 release targets
contain both complete function bodies byte-for-byte; TH05 retains the same
converter and evolves the renderer. That lineage is corroboration, not source
authority. The old ReC98 `th04_zuninit.asm` remains an IDA-generated candidate.

The separately recorded runtime Oracles give the maintained instructions a
semantic check: the converter matches all 6,879 strict mapped two-byte
Shift-JIS pairs, and the writer matches 1,428 ordered VRAM word writes across
the seven target messages at three row offsets. See the v777 and v778 notes.
The `XOR AX,AX` before the writer loop is redundant for these inputs, but it
is present in both TH02 and TH04 release targets. The maintained source
retains that attested shared instruction; it is not a new filler byte.

## Focused cold assembler replay

Maintained source: `src/zun/zuninit/text_support.asm`, SHA-256
`e825b5e5529884c91d3b1ee8b77df28a22fcb7d5c9b8e3ea0dd02bc4a466c9bd`.
It has named functions, labels, and symbolic instructions. It contains no
byte/data injection directives or external includes.

Run with a fresh output directory:

```sh
python3 scripts/probes/probe_th04_zuninit_text_support_asm.py \
  --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME
```

The probe checks target and TASM32 identity, assembles two cold rounds, and
parses valid OMF. Each 311-byte object has one 77-byte `_TEXT` LEDATA, two
public near procedures at relative `0x00` and `0x12`, and no FIXUPP. Both
objects are identical with SHA-256
`e26ae2f078deec04150d2dbdff875cad0754bf947775fb2a2ddfc9e22cf5a28e`.
The complete emitted CODE is raw-equal to the 77 target bytes. The two TASM
listings differ only in their wall-clock header and `??TIME`; an initial
probe run incorrectly treated that listing digest as an OMF determinism gate.
The current probe preserves both listings and gates deterministic OMF/CODE.

Focused receipt: `.analysis/reconstruction/probes/v779-zuninit-text-asm-004/receipt.json`,
SHA-256 `117ca880190d3608df5813c02424dbceaa79b2c1c91921e49d37178661750c78`.
Independent cross-game receipt:
`.analysis/reconstruction/probes/v779-zuninit-lineage-001/receipt.json`, SHA-256
`dce100d8c14bb5758d8e8d395adb3a558afb390da4cef67aba2f40c89d0a48`.

## Accepted state and next gate

The two boundary rows move from unresolved authored candidates to the
original-style ASM attestation queue. One 77-byte unit is `source-present`.
No decoded exact or whole-ZUN.COM claim is made: a maintained complete
ZUNINIT component link, position/layout agreement, and cold aggregate replay
have not been established. The remaining six ZUNINIT entries retain unresolved
source/origin authority.
