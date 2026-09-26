# TH04 OP shared sound cross-game hybrid closure (v827)

## Result

v827 promotes both remaining OP sound-effect functions:

- SND_SE_PLAY at payload 0xE2F2, 57 bytes.
- _snd_se_update at payload 0xE32C, 76 bytes.

The complete physical th04/snd_se.cpp SHARED contribution remains 0x86 bytes
at 0xE2F2..0xE377, with one unclaimed producer-layout NOP between the reviewed
function bodies.

After v827, OP is 92/93 exact. The only remaining authored-function blocker is
the 234-byte SND_LOAD.

This is decoded-function exactness. It does not claim packed-file exactness or
literal recovery of ZUN's original source spelling.

## New cross-game evidence

v822 proved the TH04 MAIN/OP/MAINE fixed producer and exact diagnostic code
shape, but conservatively kept source credit blocked because the frame-free
parameter and BL/BH helper spelling was known through ReC98 decompilation
history.

v827 adds independent release-target evidence. Restored TH05 OP and MAINE each
contain exactly one copy of the complete TH04 fixed 0x86 producer after masking
the same 20 legal OMF link operands.

Fixed producer SHA-256:
2300d500c2b4d9701f49ffec4647cb4e199296543253796ddb1f6804603dae9f

TH05 target locations:
- TH05 OP: 0xD602
- TH05 MAINE: 0xEAE6

The v401 MAP files bind both contributions to M=th04/snd_se.cpp.

## Narrow hybrid boundary

Normal maintained C++ still owns the sound-mode guards, SE_NONE checks,
priority comparison, selected-effect writes, driver dispatch, frame increment,
and expiry updates.

Only two compiler/register primitives are retained as low-level hybrid source:

1. Frame-free Pascal parameter retrieval: BX=SP; DX=SS:[BX+4].
   Target bytes: 8B DC 36 8B 57 04.
2. Current-effect index construction: BL=snd_se_playing; XOR BH,BH.
   Fixed shape: 8A 1E <addr16> 32 FF.

The current-index primitive occurs at the same two relative positions in both
TH05 fixed producers, +0x1B and +0x6B. This is machine-code provenance for the
primitive, not a claim that the modern helper names or comments are original.

## Historical context

ReC98 commit 16899204dfaca4ba8a1bced93c5bff88941d8345 is
[Decompilation] [th04/th05] Sound effect playback and already reconstructs the
frame-free parameter and BL/BH forms.

Later commit 6fa8bf0f671b95f976eebe775a3330c822d71ca2 removes ASM-style parameter
peeking and explicitly notes that ordinary Turbo C++ parameter handling adds a
stack frame. This explains the older 60-byte natural negative. These commits
remain reconstruction history, not original-source proof; acceptance rests on
the independent TH05 release-target producer identity.

## Focused replay

Replay driver:
scripts/probes/replay_th04_op_snd_se_crossgame_v827.py

Two isolated TC4.02/TLINK rounds reproduce:
- fixed object CODE SHA-256
  2300d500c2b4d9701f49ffec4647cb4e199296543253796ddb1f6804603dae9f
- SND_SE_PLAY SHA-256
  fea779b877971c519c0729a6f0546e60f37225a2a675cd3fa4dc0975eef884b8
- _snd_se_update SHA-256
  a9e451577270f1d448bd39c71b2c4e69570357b1090111740df0b440931cf5f5
- complete target producer SHA-256
  83a91c2784779561c19afb76b307a99ab0d92974be0b2004354d5116c27bb297
- accepted linked OP EXE SHA-256
  c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274
- all 804 ordered MZ relocations.

Focused receipt SHA-256:
33962357744f6b3e3983c37622de9f474bc283f67710a9dd0fa77549f898c002

## Canonical acceptance

Canonical current-ledger replay contains 92 accepted OP decoded functions.
All 92 have raw_difference_count = 0.

Canonical receipt SHA-256:
c0d1684341c87dcf156907e2b8304a4d1918ce8c2b69da6f3f4827471aa2aa98

## Remaining OP blocker

Only SND_LOAD remains blocked. v823 already bounds its complete 234-byte body
to one equivalent MOV BX,AX encoding: target 89 C3 versus ordinary TC4J 8B D8.
Integrated inline assembly produces the target encoding, but the known spelling
is still target-derived reconstruction evidence. Future OP work should seek
independent historical source or producer provenance for that instruction.
