# TH04 OP nopoly_B_put cross-game hybrid closure (v826)

## Result

OP nopoly_B_put at decoded payload 0xBFA7 is decoded-exact. The reviewed body
is 30 bytes. v826 raises OP from 89/93 to 90/93 accepted authored functions.
The remaining three blockers are SND_LOAD, SND_SE_PLAY, and _snd_se_update.

This remains decoded-function exactness. It does not claim a packed-file offset,
whole-OP.EXE exactness, or exact original source spelling.

## Why the old blocker changed

The earlier v670/v766/v820 work correctly showed that ordinary TC4.02 memcpy
and __memcpy__ forms do not reproduce the target segment setup and XOR encoding
direction. That negative remains valid for those source forms.

v826 adds new evidence that did not exist in that decision: independently
restored TH03, TH04, and TH05 OP release targets each contain the same complete
GAME>=3 30-byte producer after masking only the linked _nopoly_B address word.
The normalized body SHA-256 is:

ec0ca0d388011a3a96e3c34b10d0f8c26e176a86de11bae5271d530f8bfac9a3

Each target contains exactly one normalized match at the reviewed/map-owned
function location. TH02 is a useful negative control: its GAME<3 implementation
uses a different loop and does not match this producer.

This is independent release-target machine-code provenance for the complete
low-level mechanism, not a claim that the maintained source text is ZUN's
literal source.

## Maintained source boundary

The maintained source is src/op/music/nopoly_put.inl.

Ordinary TC4J pseudoregister expressions own:

- the SEG_PLANE_B value and ES assignment;
- the _nopoly_B segment load and DS assignment;
- the PLANE_SIZE / 2 word count.

Symbolic low-level source is limited to:

- PUSH DS / POP DS around temporary source-segment selection;
- XOR DI,DI and XOR SI,SI with the release-target encoding direction;
- REP MOVSW.

The source contains no __emit__, codestring, target-byte array, object rewrite,
or post-link patch, and it removes the historical decompilation __memcpy__
helper surface.

## Focused cold replay

scripts/probes/replay_th04_op_nopoly_b_put_hybrid_v826.py performs two isolated
TC4.02/TLINK builds inside the complete th04/op_music.cpp translation-unit
context.

Both rounds reproduce:

- the 30-byte linked body, SHA-256
  f9af3bf25fe94b1ca89ef5ad9bdacd77a87cfc401450a378a12428ea1f409083;
- the complete 0x6A5-byte OP_MUSIC_TEXT producer;
- the accepted OP EXE/MAP;
- all 804 ordered MZ relocations.

Archived focused receipt:

.analysis/reconstruction/receipt-archive/v826-op-nopoly-hybrid-focused-receipt.json

SHA-256:

26405281b33c09142e3eec074fe62791614717bd25ef12e27178c4a5232102ca

## Canonical acceptance

The canonical current-ledger replay contains 90 OP accepted functions. All 90
have raw_difference_count = 0, including nopoly_B_put, the v825 EGC outer
copier, and the v824 EGC helper.

Archived canonical receipt:

.analysis/reconstruction/receipt-archive/v826-op-nopoly-canonical-receipt.json

SHA-256:

cab1b089612158f70a983e9f277e3c9146b9b937c6d5c515785257fcd70adcde

## New OP frontier

The OP queue is now three functions, all already narrowed to source-provenance
questions rather than unexplained machine code:

- SND_LOAD — 234 bytes; exact integrated-assembler mechanism known, but the
  required 89 C3 spelling has no independent authored-source witness;
- SND_SE_PLAY — 57 bytes; exact helper-shaped producer known, but its frame-free
  parameter/current-index spelling is decompilation-derived;
- _snd_se_update — 76 bytes; same shared-sound provenance issue.

Future OP work should therefore search for independent historical source or
producer evidence for those three rather than repeat the closed compiler-form
matrices.
