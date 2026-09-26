# TH04 OP SND_LOAD complete-producer provenance bound (v823)

## Result

OP SND_LOAD is a reviewed 234-byte FAR function at decoded payload
0xDDCA..0xDEB3. v823 does not promote it: OP remains 87/93 exact with six
blocked authored functions.

What v823 closes is the code-generation question. The maintained/candidate
natural TC4.02 producer differs from the target only at relative +0xC1,
decoded load 0xDE8B..0xDE8C:

    target       89 C3    MOV BX,AX
    natural      8B D8    MOV BX,AX

TC4J's integrated inline assembler selects the target encoding. Replacing only
the candidate line _BX = _AX; with asm { mov bx, ax; } inside a cold copy,
while still compiling the original wrapper th04/snd_load.cpp, produces the
complete target function raw-identically in two independent rounds.

This is a diagnostic mechanism result, not authored-source evidence.

## Complete producer replay

Checked-in probe:

    python3 scripts/probes/probe_th04_op_snd_load_provenance_v823.py       --output-dir .analysis/reconstruction/probes/v823-op-snd-load-provenance-001

Both natural cold rounds reproduce the existing baseline:

- 234-byte SHARED object CODE SHA-256:
  4d0e4b2577d371061f460eb53691694f4b76c23e198e88de6c9341a8a19cef40
- handle-copy bytes: 8B D8
- linked OP SHA-256:
  c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274
- SND_LOAD slice SHA-256:
  7f04ce7bae23c3805dde0bacd5e7c936797be4e2a2f1c5feb189a9c75e2d61eb
- accepted MAP SHA-256:
  65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee
- 804 ordered MZ relocations.

Both diagnostic cold rounds produce:

- 234-byte SHARED object CODE SHA-256:
  1a486ee1cde1e0766d08ce0efa316ea36002ff836644971977494920b397478e
- handle-copy bytes: 89 C3
- complete SND_LOAD target SHA-256:
  50d62cb466990971edcfe5bdbf78ce99e815af2027cc3d21951db8e73fd6659f
- linked OP SHA-256:
  b2785d3ed2203ef6e9f5af8b3817e3a0c7a248e5440fac731bfaea50769c3c5f
- the same MAP SHA-256 and module owner:
  0DA1:03BA 00EA ... M=th04/snd_load.cpp
- the same 804 ordered MZ relocations.

Comparing the natural and diagnostic decoded program images gives exactly two
different offsets, 0xDE8B and 0xDE8C. No other program byte moves or changes.
Thus the target's 234-byte body is fully explained mechanically by one
instruction-encoding choice.

## Broader TC86 corpus

v396 had scanned the accepted TH04 cold-build corpus. v823 broadens the
question to the pinned v401 reconstruction snapshot rather than assuming that
accepted TH04 objects are representative of all locally available TC86 code.

The v401 snapshot contains 437 object files, 356 files identifying as TC86
Borland C++ 4.02, and 345 unique TC86 object hashes.

Across CODE LEDATA in those 345 unique objects, exactly one 89 C3 occurs:
obj/th02/player_b.obj, PLAYER_B_TEXT+0xC6, object SHA-256
b77d06ba1ca3ed6b37202d16a6a896bd1e9d2fc1cb18501dd7615d4002c40f1c.

Its source, th02/main/player/bomb.cpp, explicitly contains:

    asm { mov bx, ax; }

No natural C/C++ 89 C3 witness exists in this pinned corpus. This does not
prove that TC4.02 can never select that encoding from every conceivable source
form; it does strongly separate the observed integrated-assembler mechanism
from the tested natural front ends.

## Source provenance

The exact mechanism still cannot receive authored-source credit.

Pinned ReC98 history binds the TH04 candidate _BX = _AX; line to commit
d9858113d8135d265b88e0325d40fc237e6b9763, whose subject is
[Decompilation] [th04] snd_load().

The sole historical v401 89 C3 witness above is introduced by commit
522976d6687603576278f1d925d9d8631748f1d2, whose subject is
[Decompilation] [th02] Bombs: Circle point rendering.

So the local history provides two target-derived reconstruction spellings, not
an independent ZUN source artifact. The fact that inline assembly is the only
locally observed producer of 89 C3 is therefore a strong mechanism clue, but
not permission to change maintained authored source to that spelling.

## Acceptance boundary

SND_LOAD remains blocked.

The new frontier is narrower than v766/v820:

- physical boundary: closed;
- cross-artifact TH04 producer sharing: closed;
- natural TC4.02 output: deterministically 8B D8;
- exact TC4J mechanism: integrated inline assembler, deterministically 89 C3;
- complete 234-byte diagnostic function: raw-zero;
- OP MAP ownership: unchanged;
- ordered relocation topology: unchanged;
- independent authored-source provenance: open.

Archived receipt:

.analysis/reconstruction/receipt-archive/v823-op-snd-load-provenance-receipt.json

SHA-256:

b958943a35c7916ab4a8bc80a9f2dd97bcc25a968ff4a315547f71d6dc37f161

Do not retry casts, aliases, register pressure, ordinary _BX=_AX, TASM syntax,
TC4J -B, or the tested compiler option matrices without materially new
evidence. Future promotion requires an independent historical source witness or
another provenance-bearing TH04 producer that justifies the inline-assembler
spelling.
