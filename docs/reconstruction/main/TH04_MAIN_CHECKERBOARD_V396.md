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

## v398 natural source-form matrix

A follow-up compiler probe now closes the remaining obvious source-spelling
escape hatch rather than repeating optimizer flags. The checked-in
`scripts/probes/probe_tc4_checkerboard_loop_forms.py` compiles fourteen legal
C++ countdown forms around the exact architectural core
`MOV ES,DX / ES:[DI] dword store / ADD DI,8`:

- `_CX` and ordinary-local counters;
- `do`, `while`, and `for` loops;
- pre-decrement and post-decrement conditions;
- explicit C++ `goto` backedges.

All fourteen compile under the production `-ml -O -b- -3 -Z -d` profile and
zero emit x86 `LOOP`. The normal maintained shape still lowers through
`DEC CX; MOV AX,CX; OR AX,AX; JNZ`. The shortest newly tested form,
`_CX--; if(_CX) goto label`, removes the AX copy but still emits
`DEC CX; OR CX,CX; JNZ`, so it cannot match the target two-byte backedge.

The pinned `TCC.EXE` no-argument help independently describes its exposed
`-O` switch as `Optimize jumps`; it exposes no separate loop-optimization
switch. This is consistent with the earlier v396 rejection of BCC-style
`-O1/-Os/-O2/-Ot/-Ol` spellings and keeps the PC-98 compiler observation
separate from documentation for other Borland driver variants.

Private receipt:
`.analysis/gpt-web/v398-checker-loop-forms-001/receipt.json`, SHA-256
`e915db190969a5792670695664a45c11fcc1d48f9458882a4a64779d18750a2e`.

The conclusion remains deliberately bounded: natural source spelling and
exposed compiler switches have no demonstrated path to the historical
counted `LOOP`. This does not prove every possible TC4J program incapable of
emitting `LOOP`, and it still does not establish provenance for target-derived
inline assembly.

## v405 all-artifact provenance scan

v405 extends the earlier TH01-TH05 MAIN-target search to every registered
artifact image. DIET-wrapped OP/MAINE/ZUN inputs are restored with the pinned
toolchain before inspection, so the scan is over executable payload code rather
than compression stubs.

The exact compact core `MOV ES,DX; MOV CX,6; MOV ES:[DI],EAX; ADD DI,8; LOOP`
(`8E C2 B9 06 00 66 26 89 05 83 C7 08 E2`) occurs exactly once across the 20
images: TH04 MAIN load `0x120AF`. No OP/MAINE/ZUN target adds independent
producer provenance for the counted `LOOP`.

Private receipt SHA-256:
`86de803fe7b93f0b66b26e33004ab1c0535f936187eb370fa8f7bd7447a02913`.

The function therefore stays blocked. This closes another provenance search
surface but does not prove that every possible original source form is assembly
or permit copying the target `LOOP`.
