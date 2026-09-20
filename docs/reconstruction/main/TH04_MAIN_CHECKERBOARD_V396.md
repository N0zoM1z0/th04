# TH04 checkerboard v396 negative closure

The remaining checkerboard blocker is the compact counted `LOOP` in the
174-byte target body. The maintained natural source is deterministic, but TC4J
lowers the same countdown to `DEC CX; MOV AX,CX; OR AX,AX; JNZ`, growing
the body to 179 bytes.

## Pinned compiler surface

v396 compiled the same maintained source under every additional legacy
optimization strategy accepted by the pinned TCC 4.02 driver:

- production `-O`
- `-O -G`
- `-O -G-`
- `-O -G- -r`

All four emit byte-identical OMF objects, SHA-256
`58857caf5d1c7abba278662439f81db406deacbb1376ec87fe8b3cdd7800705c`.
The pinned TCC rejects `-O1`, `-Os`, `-O2`, and `-Ot`;
earlier probes already established that it rejects `-Ol` on both the
command line and through `#pragma option`. Therefore no exposed optimizer
strategy changes this loop lowering.

## Independent-target provenance scan

The target loop core is:

`MOV ES,DX; MOV CX,6; MOV ES:[DI],EAX; ADD DI,8; LOOP`

Registered attested TH01, TH02, TH03, TH04, and TH05 MAIN targets were scanned
for this complete unusual architecture while allowing surrounding addresses to
differ. It occurs exactly once, in TH04 at load `0x120AF`, and nowhere
in the other four targets.

No TH05 checkerboard function/TU reuse exists. ReC98 introduced
`asm { loop put_loop; }` in TH04-only decompilation commit
`45df9ec0`.

Private v396 receipt SHA-256:
`672313ceb853ce12a76bb8c814f2b8939b1faabdfbbe991620d12777d13cd2f4`.

## Result

The function remains reviewed/source-present/blocked. The historical inline
`LOOP` is still routing evidence only: neither the pinned compiler surface
nor independent target provenance currently justifies hybrid authored-source
promotion.
