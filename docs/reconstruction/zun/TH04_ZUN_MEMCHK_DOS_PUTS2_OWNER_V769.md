# ZUN MEMCHK DOS_PUTS2 source-owner correction (v769)

The old ZUN function ledger classified MEMCHK payload 0x26CE..0x26F4 as an
authored target-derived-ASM function named sub_38E because the diagnostic
th04_memchk.asm file and its MAP/TASM listing placed a PROC there.

That source attribution is wrong.

The 39-byte target body at 0x26CE..0x26F4 is byte-identical to the resident
DOS_PUTS2 function at payload 0x1344..0x136A. In both locations the function is
followed by the same 0x90 alignment byte. The complete body-plus-padding module
at each location has SHA-256:

c346fe75402242d9b1348e634244efb9e94ba1b8dc637602d8767f0c6c5fb3d9

Maintained shared source already exists at:

src/shared/dos/dos_puts2.asm

v769 assembles that source twice with the pinned TASM32 5.0 toolchain. Both
rounds emit the same 40-byte module and the same link-relevant OMF digest. The
maintained body SHA-256 is exactly the target body SHA-256:

90259993539788eb6cc440e98400c1551f6502aa42c64d1fe8d5860539b9c981

Receipt:
.analysis/reconstruction/receipt-archive/v769-zun-memchk-dos-puts2-receipt.json

Receipt SHA-256:
b2a26f0a595bfa5410c43809ea0971003cff163767bd8b65d318f39b65b7ab8f

Ledger consequence:

- MEMCHK 0x26CE is reclassified from authored/target-derived-asm to
  library/maintained-shared-asm.
- The historical sub_38E TASM PROC remains useful boundary corroboration only.
- A library source-present unit records the MEMCHK DOS_PUTS2 instance.
- The following byte at 0x26F5 remains function-external EVEN padding.
- No authored ZUN exactness credit is created.

This correction reduces the real authored ZUN reconstruction queue from
13 functions to 12 and the unresolved target-derived-ASM subset from 11 to 10.
It is a source-ownership correction, not a denominator trick: the removed entry
is independently proven shared library code.
