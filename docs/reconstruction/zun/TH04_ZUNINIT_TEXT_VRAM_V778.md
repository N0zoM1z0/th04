# ZUNINIT text VRAM writer runtime behavior (v778)

## Target and hypothesis

The reviewed ZUNINIT function at `th04-zun / com-payload / 0x7C2..0x7FC`
(runtime COM `0x1CF..0x209`) is 59 bytes, SHA-256
`0c5a90f8b85153d3c668f033651cddedbe2a635e2cfdcf8345e4ec5f8f8c6fb6`.
It receives a PC-98 text VRAM offset in AX and a CS-relative `$`-terminated
Shift-JIS string offset in DX. The hypothesis is that it converts each
two-byte character with the adjacent `0x1BD` helper and writes two character
words plus two `0x0041` attribute words per character.

## Focused runtime Oracle

Run:

```sh
python3 scripts/probes/probe_th04_zuninit_text_vram.py \
  --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME
```

The probe attests the ZUN target and complete 1,141-byte ZUNINIT component,
including the 59-byte function and its seven embedded 34-byte messages. It
executes the real target code in Unicorn x86 16-bit mode, with CS at `0x1000`,
DS/SS at `0x2000`, empty PC-98 VRAM, and each original message tested at all
three caller row offsets (`0x650`, `0x6F0`, `0x790`).

An independent strict Shift-JIS/EUC-JP calculation supplies each JIS row and
cell. The expected character words are `(cell << 8) | (row - 0x20)` and that
word with bit 15 set; the attribute plane receives `0x0041` twice. All 21
scenarios match the complete ordered VRAM write trace, resulting character
and attribute bytes, and BX/CX/DX/DI/ES end state: **357 character pairs and
1,428 VRAM word writes**, with no mismatch.

Receipt: `.analysis/reconstruction/probes/v778-zuninit-text-002/receipt.json`,
SHA-256 `63c2a2dd10e877bd6e67868e3e067cb3b9043c0663abd0186055ad6b89ac1d79`.
It records each message digest, row offset, complete write-trace digest,
register setup, target slice, probe source, emulator binary, and Python version.

## Reconstruction consequence

The target helper's text VRAM behavior and register interface are now
runtime-observed for all embedded messages. The experiment does not establish
behavior for arbitrary malformed strings or empty strings. Its target-derived
ASM candidate still has no independent original-source authority, so no source
or exact state changes.
