# ZUN compact local MASTER archive (v536)

This packet closes the resident link dependency on the external 640-member
MASTER archive. It does not make the ZUN resident target-exact and does not
change authored ZUN exactness.

## Local archive

The resident link now needs only fifteen already localized MASTER members:

1. VERSION
2. GRP
3. RESDATA
4. FIL
5. FILREAD
6. FILCLOSE
7. FILROPEN
8. FILWRITE
9. FILCREAT
10. FILSEEK
11. FILAPEND
12. DOSFREE
13. DOSC
14. DOSPUTS2
15. FONTOPEN

GRAPH_CLEAR remains a checked-in standalone local object and is not inserted
into this archive.

The compact archive is 8192 bytes, SHA-256
2397a43369b879a61c248b6a4671378f6502fcfc6456664b63782ad3cf937284.
Both cold rounds reproduce the same archive byte-for-byte.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_zun_compact_master.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay does not copy, read, or link the external 640-member masters.lib.
It compiles the maintained ZUN C++ sources, assembles every local support
producer, builds a fresh 15-member archive in explicit physical order, and
links the resident using the original link response.

The accepted strict replay is
.analysis/reconstruction/probes/v536-zun-compact-master-002/receipt.json,
SHA-256
bd7737cfb59ac20a208f55273116c59b5a078488ddfafaad61d5056c11a93843.

Both cold rounds produce resident component SHA-256
a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab
and compact-link MAP SHA-256
ebe1475b9e8775e712e0e3ebd045cb1fa578b74592ea0c1dcef3c6e341d329db.

The target residual remains 4241 bytes. This is therefore external dependency
closure, not target exactness.

## Remaining external link surface

The resident link response still uses four Borland/runtime inputs:

- c0t.obj
- emu.lib
- maths.lib
- ct.lib

Those should be inventoried before replacing anything else. Do not copy CRT or
libc members merely to reduce a dependency count; first identify which members
are actually pulled into the resident, their physical ownership, and whether
their provenance is compiler/runtime or game-authored.

The natural resident _main and cfg_init blockers remain unchanged. ZUNINIT and
MEMCHK source provenance also remains open.
