# ZUN Borland runtime inventory and unused float-library removal (v537)

This packet removes two unused Borland libraries from the resident link and
pins the runtime modules that are actually pulled. It does not reclassify any
compiler/runtime code as authored source.

## Reduced link response

The v536 resident link still named c0t.obj, emu.lib, maths.lib, and ct.lib.
v537 removes emu.lib and maths.lib entirely. The remaining runtime response is:

    c0t.obj + compact local masters.lib + ct.lib

The resulting 6360-byte resident component and MAP are byte-identical to the
v536 control:

- component SHA-256:
  a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab
- MAP SHA-256:
  ebe1475b9e8775e712e0e3ebd045cb1fa578b74592ea0c1dcef3c6e341d329db

Therefore EMU.LIB and MATHS.LIB are not required by this resident link.

## Runtime ownership

Pinned toolchain identities:

- C0T.OBJ:
  27169f062a9b77bf4accfb9550ca4ccbf0fd710d4b1232768630d53bb6305f7c
- EMU.LIB:
  e702f1f5dc95d61bdb1689af746d69ac5e303e38ebf77175cd6fd600eb3edc74
- MATHS.LIB:
  ad76cb7f5b81105d4cc83691c74c030a6f5e1a56be0d1f5b5eca43f3124693cd
- CT.LIB:
  b665d5d30f0d3bafe3023ee45eeef183811c87201e9a1876f011acf5699261af

C0T.OBJ contributes the direct startup module c0.ASM.

Fresh TLIB inventories plus the final resident MAP show zero pulled modules
from EMU.LIB and MATHS.LIB. CT.LIB contributes exactly 26 modules:

    _abort
    _pathops
    atexit
    brk
    errormsg
    exit
    fflush
    files
    files2
    flushall
    fseek
    heaplen
    ioerror
    isatty
    lseek
    n_scopy
    nearheap
    setargv
    setupio
    setvbuf
    stklen
    strlen
    sysnerr
    write
    writea
    xfflush

The receipt records each CT member's zero-based index in the 829-member
library. This list is compiler/runtime ownership, not a source acceptance list.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_zun_runtime_inventory.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The accepted v537 receipt is
.analysis/reconstruction/probes/v537-zun-runtime-inventory-001/receipt.json,
SHA-256
5218d64104c0807b7a41a310450799d5d4a30427a28da7138391d971505849e1.

Both cold rounds rebuild maintained ZUN/support source, rebuild the compact
local MASTER archive, link without EMU/MATHS, and reproduce the v536 resident
component and MAP.

The target residual remains 4241 bytes. Natural resident _main/cfg_init and
ZUNINIT/MEMCHK provenance blockers are unchanged.

## Next step

The external runtime surface is now only c0t.obj plus those 26 CT.LIB
members. Before replacing any of them, classify which are startup, heap,
stdio/file, argv/path, termination, or string primitives and whether the
repository already has legitimate maintained equivalents. Do not import
Borland runtime binaries or decompiled CRT as authored source.
