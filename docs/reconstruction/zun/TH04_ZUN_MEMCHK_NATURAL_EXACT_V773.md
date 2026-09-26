# ZUN MEMCHK natural-source exact reconstruction (v773)

The historical reconstruction represented the complete MEMCHK-owned code region
as target-derived th04_memchk.asm. Current target/source review now replaces
that assumption with three independently justified source owners:

- authored MEMCHK _main: natural Tiny-model C++ in src/zun/memchk/main.cpp;
- DOS_PUTS2: shared MASTER-compatible support in src/shared/dos/dos_puts2.asm;
- DOS_MAXFREE: shared MASTER support in src/shared/dos/dos_maxfree.asm.

## DOS_MAXFREE ownership

The exact 20-byte MEMCHK helper at payload 0x26F6 occurs in the pinned
historical masters.lib member dosmaxfr, whose OMF module name is DOSMAXFR.ASM
and whose public symbol is DOS_MAXFREE. The historical member contains exactly
one 20-byte CODE LEDATA and no FIXUPP records.

Maintained symbolic TASM source expresses the same DOS AH=48h semantics and
emits the same 20 target bytes in two independent rounds. This establishes
library ownership; the old sub_3B6 name from target-derived ASM remains boundary
corroboration only.

## Natural MEMCHK _main

TC4J Tiny model compiles the maintained C++ _main to exactly 38 bytes before
link fixups. Its control flow naturally matches the target: call DOS_MAXFREE,
print the banner through Pascal DOS_PUTS2, compare against 30000 paragraphs,
print the low-memory message and return 255 on failure, otherwise return 0.

The same C++ translation unit naturally emits the complete 0x50-byte CP932
MEMCHK data segment. The second message begins exactly 0x1B bytes after the
first, matching target data addresses 0x0E8E and 0x0EA9.

## Complete component link

v773 links three maintained modules in target order: 38-byte natural C++ _main,
39-byte shared DOS_PUTS2, and 20-byte shared DOS_MAXFREE. TLINK naturally
inserts the one 0x00 alignment byte after _main, while DOS_PUTS2 retains its
EVEN-generated 0x90 module-tail alignment.

The final MAP places _main at 0000:0367, DOS_PUTS2 at 0000:038E,
DOS_MAXFREE at 0000:03B6, and MEMCHK _DATA at 0000:0E8E size 0x50.

Both cold rounds produce a 4066-byte memchk.com that is byte-for-byte identical
to the retained target MEMCHK component:

2531795670b5cafb65bf261f499d5d77b71aeaf26015f8481000cdbb96272dfc

Focused receipt:
.analysis/reconstruction/receipt-archive/v773-zun-memchk-natural-focused-receipt.json

Focused receipt SHA-256:
a75c33a06d6e87976a8a3d79a1d350c3a8e796c61d3ab1cb435f0eab14094306

## Canonical decoded acceptance

v775 first checked the new _main row in isolation and obtained 38/38 raw-zero
bytes. After the checked-in ledger was updated, v776 replayed the full current
ZUN decoded ledger.

The canonical v776 receipt intentionally contains mixed states: cfg_init and
resident _main remain source-present diagnostics with their known linked
differences, while MEMCHK _main is decoded-exact with zero raw differences.
Only decoded-exact rows are raw-zero acceptance gates.

Canonical receipt:
.analysis/reconstruction/receipt-archive/v776-zun-memchk-main-canonical-receipt.json

Canonical receipt SHA-256:
9d8f9e15e968b8fb93641915fe296db3cb2c0dd7dda63dca0a9dae63789609d6

## Ledger consequence

- MEMCHK _main is the first authored ZUN function accepted exact.
- MEMCHK DOS_PUTS2 and DOS_MAXFREE are library support and are excluded from the
  authored denominator.
- The authored ZUN queue is now 11 functions: 1 exact, 2 blocked natural C++
  functions, and 8 unresolved target-derived-ASM source/origin candidates.
- No full ZUN.COM or packed-file exactness is claimed.
