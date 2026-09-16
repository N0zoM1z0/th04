# TH04 multi-artifact SND_LOAD ownership review (v206)

## Scope

v206 reviews the complete TH04 `SND_LOAD` producer across the artifacts that
actually contain it, while keeping byte exactness artifact-local.

The independently attested target bodies are:

- `MAIN.EXE`: load `0x13496..0x1357F`, target file `0x14C96..0x14D7F`, size `0xEA`;
- `OP.EXE`: unpacked payload `0xDDCA..0xDEB3`, size `0xEA`;
- `MAINE.EXE`: unpacked payload `0xD112..0xD1FB`, size `0xEA`;
- `ZUN.COM`: no corresponding candidate or bounded target producer.

`MAIN.EXE` remains the active exactness artifact. OP and MAINE receive reviewed
boundary and shared-source ownership evidence only; no MAIN exactness is
transferred into another executable.

## MAIN target observation and caller inventory

Fresh target-bound Ghidra constructs one contiguous 234-byte FAR function at
analysis `0x23496..0x2357F` and reports two callers (`_main` and
`stage_session_init`) plus two callees. Its body terminates in `RETF 6`.

An independent raw target scan finds three instruction-aligned FAR calls to
`SHARED 130E:03B6`: load sites `0xAB66`, `0xB1A2`, and `0xD46C`. The third site
lies inside reviewed `dialog_op(unsigned char)`. The MAIN boundary ledger caller
count is therefore corrected from two to three. This is a callgraph correction,
not exactness evidence.

Exactly one MAIN MZ relocation overlaps the complete producer: relocation index
120 at load `0x134F2`, the segment word of the FAR `BGM_READ_SDATA` call.

## OP and MAINE target boundaries

OP target `SND_LOAD` at payload `0xDDCA` linearly decodes for exactly `0xEA`
bytes through `RETF 6` and ends immediately before target `GRAPH_PUTSA_FX` at
`0xDEB4`. Ten instruction-aligned raw FAR calls target the OP `SND_LOAD` entry.
The OP boundary is therefore promoted from corroborated to reviewed while
remaining unreviewed/nonexact in its own artifact plane.

MAINE target `SND_LOAD` at payload `0xD112` likewise decodes for exactly `0xEA`
bytes through `RETF 6` and ends immediately before target `GRAPH_PUTSA_FX` at
`0xD1FC`. Three instruction-aligned raw FAR calls target the MAINE entry. The
MAINE boundary is promoted from corroborated to reviewed, again with no exact
credit.

The cold candidate MAP places the MAINE `th04/snd_load.cpp` contribution at
`0CC7:04A0`, load `0xD110`, two bytes before the target function. Bounded seed
alignment proves that this is an upstream SHARED layout differential rather than
a target boundary at `0xD110`:

- target `SND_KAJA_INTERRUPT` `0xCF8C` matches candidate `0xCF8B` (`+1` target delta);
- target `SND_DETERMINE_MODES` `0xCFAA` matches candidate `0xCFA9` (`+1`);
- target `SND_DELAY_UNTIL_MEASURE` `0xD046` matches candidate `0xD045` (`+1`);
- target `CDG_PUT_PLANE` `0xD078` matches candidate `0xD076` (`+2`);
- target `SND_LOAD` `0xD112` matches candidate `0xD110` (`+2`);
- target `GRAPH_PUTSA_FX` `0xD1FC` matches candidate `0xD1FA` (`+2`).

Thus the first unresolved one-byte seam is at target `0xCF8B` immediately before
`SND_KAJA_INTERRUPT`, and a second one-byte seam exists at target `0xD077`
(immediately before `CDG_PUT_PLANE`; observed byte `00`). Their ownership and
source form remain deliberately unknown for the next packet.

The compact MAINE seam receipt is
`.analysis/gpt-web/th04-main-20260916-v206/maine-snd-load-seam.json`, SHA-256
`c40a9b7ce5067f85e6ef2349aa51de2ec91e97be675e213c2371599746cce5d4`.

## Cross-artifact producer identity

The cold ReC98 scaffold links the same `th04/snd_load.cpp` `0xEA` SHARED
translation-unit contribution into MAIN, OP, and MAINE. Candidate Intel OMF was
used to derive the actual link-resolved byte positions: 53 byte positions differ
between pre-link LEDATA and one or more linked artifact bodies. Masking exactly
that OMF-derived set, rather than target mismatches, yields:

- candidate MAIN/OP/MAINE fixed producer SHA-256:
  `f372dd28b7e8405436ddb04ab48671db383b0934febbd666978b55fc7e8d443e`;
- target MAIN/OP/MAINE fixed producer SHA-256:
  `67f05625db1478d9a106ca24fe32e33ae42a007db3a2031b2f487a0bcb280bfd`.

All three target pairs have zero remaining fixed-byte differences after that
mask. Every target-versus-candidate comparison has the same sole fixed mismatch:
logical offsets `+0xC1..+0xC2`, where all three TH04 targets encode
`MOV BX,AX` as `89 C3` and the current TC4J producer encodes the same operation
as `8B D8`.

The compact comparison receipt is
`.analysis/gpt-web/th04-main-20260916-v206/snd-load-cross-artifact.json`, SHA-256
`b312a4fe7e7c5b9e5084f8d7f9b1e986fe2c517f291b59bbe0278c000c70d12c`.

This establishes TH04 multi-artifact source/producer sharing for the fixed
`SND_LOAD` logic. It does not prove the historical source filename or grant OP or
MAINE exactness.

## Natural-source boundary

MAIN already had 230 of the 234 authored function bytes accepted from maintained
natural C++ subspans. v206 changes their ownership location only; contents are
unchanged:

- `src/shared/sound/load_prefix.inl`, 184 target bytes;
- `src/shared/sound/load_open.inl`, 8 target bytes;
- `src/shared/sound/load_func.inl`, 3 target bytes;
- `src/shared/sound/load_dispatch_read.inl`, 26 target bytes;
- `src/shared/sound/load_tail.inl`, 9 target bytes.

The four blocked target bytes remain unchanged:

- `PUSH DS` at MAIN file `0x14D4E`;
- target `89 C3` (`MOV BX,AX`) at `0x14D57..0x14D58`;
- `POP DS` at `0x14D76`.

Existing compiler evidence already rejects ordinary `_BX = _AX`, aliases,
register-pressure variants, TCC option matrices, the PC-98 integrated compiler,
ordinary DS temporaries, segment-pointer rewrites, and other natural mechanisms.
No synonymous spelling matrix was repeated.

ReC98 history is useful only as provenance. The earliest tracked
`th04/snd/load.asm` entry is 2014 commit
`46b2d671432cf21dbfa86bf0dd6dc8c9f06445a7`, explicitly titled
`[Reverse-engineering] Music and sound effect loader`; it is not original source.
The 2021 `d9858113d8135d265b88e0325d40fc237e6b9763`
`[Decompilation] [th04] snd_load()` change converted that symbolic reverse-
engineering assembly to C++ while retaining inline assembly for the DS pair and,
historically, the parameter reload.

A v206 symbolic TASM control confirms that switching the whole function to
assembly is not an honest shortcut. The probe emits a valid 234-byte SHARED
producer, but ordinary symbolic `mov bx, ax` still encodes as `8B D8`, not target
`89 C3`. Probe source SHA-256 is
`af6eefc6bff9c35d1acee21ea706b9bfedc494ee6ec50d70332c67dde956025a`;
object SHA-256 is
`8cc1b69f545333a6422d1fb9753536a0125b742c284cedcab5e37421db9bed1b`.
Therefore the complete function remains authored C++ with four blocked bytes; it
is not reclassified as exact original-style assembly.

## Shared-source replay

Moving the five unchanged natural fragments from `src/main/sound/` to
`src/shared/sound/` changes repository ownership only. The exact replay manifest
now binds those shared paths; tracked manifest SHA-256 is
`b0e75efa57ca360b19893a71b45144979c7605cc8f8646cb3d817af63ae85dd1`.

Focused fragment replay:

- `gptweb-v206-snd-load-prefix-focused-001`: PASS, receipt SHA-256
  `48182e6d03a943ba50eceb408eef553f155019849650930886b553bbef3546c4`;
- prefix remains `raw=True`, `map=True`, `relocs=True`, target slice SHA-256
  `d27ae9a65d4672f47608d3d29dae21d7c4f436ba839e0a3b8f196ce754d6eacb`.

Focused `source_mode=replace` replay:

- `gptweb-v206-snd-load-func-focused-001`: PASS, receipt SHA-256
  `c3126dd570e7b7850848fbd30cd457aa69d9f021ae5e7e3d98b7d185265f567b`;
- parameter-load span remains `raw=True`, `map=True`, `relocs=True`, target slice
  SHA-256 `c793770391e26089396d0ece5eae43bcc69c8a6ede470f090e4ba9a58486d14e`.

Mandatory no-unit aggregate after the ownership change:

- run: `gptweb-v206-snd-load-shared-aggregate-001`;
- selected default owners: 246;
- two isolated cold builds;
- `failures=[]`;
- receipt SHA-256:
  `efa52e2a39b652863fb7d9d03d9f70d5adb233c1f8565309ec9fd1978af8ef79`;
- A/B `snd_load.obj` SHA-256:
  `55a0f19718afc6470fc3f857b24eea4c24393eb5fe437a3fe1c8cba4140d71d2`;
- A/B MAP SHA-256:
  `4bea5732094f5f08b2c37365d7cae466f063e54f7cb22cad115c973810cf59cc`;
- A/B candidate MAIN SHA-256:
  `1932b7feb681e3fa198d24a10cd93a70ce2cb6d400d1ecab39545cafa26b9f9b`.

All five moved exact subspans remain raw/MAP/ordered-relocation exact. No new
exact promotion occurred, so this aggregate is the broad cold gate for the
source-ownership change rather than a post-promotion exactness claim.

## Accounting and verification planes

v206 changes boundary confidence and source ownership, not MAIN exactness totals.
MAIN remains:

- C/C++ exact reviewed bytes: `75,620 / 81,279` (`93.037562%`);
- C/C++ exact reviewed functions: `460 / 483` (`95.238095%`);
- `snd_load`: reviewed/blocked, 230 of 234 authored bytes exact from natural C++;
- four `snd_load` bytes still blocked.

OP and MAINE `SND_LOAD` are now reviewed boundaries with shared-source evidence,
but their exactness planes remain unestablished. ZUN has no corresponding
producer.

Standalone TH04 product compile/link closure, whole-image exactness,
runtime-storage identity, runtime scenario validation, portable runtime,
independent pristine provenance, and Factory Truth-Kernel acceptance remain
separate and unestablished.

## Continuation

The next evidence-connected packet is the MAINE SHARED sound/layout seam before
`SND_LOAD`, not another `89 C3` spelling search. Start with the two unexplained
single-byte target seams:

1. target `0xCF8B`, between the exact-length `_snd_mmd_resident` body ending at
   `0xCF8A` and target `SND_KAJA_INTERRUPT` at `0xCF8C`;
2. target `0xD077` (`00` observed), between `SND_DELAY_UNTIL_MEASURE` ending at
   `0xD076` and `CDG_PUT_PLANE` at `0xD078`.

Determine whether each byte is authored alignment/padding, compiler output, or
another owner; compare OP and MAIN counterparts; then reconcile the resulting
SHARED contribution offsets through MAINE `SND_LOAD` and later owners.
