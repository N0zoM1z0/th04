# ZUN DOS_FREE library replacement (v524)

This packet replaces one more external MASTER library member in the ZUN
resident diagnostic link with maintained repository source. It is library
support work, not authored ZUN exactness.

## Target extent and natural source

The decoded target contains the complete near Pascal DOS_FREE / MEM_FREE body
at payload 0x131E..0x132D, 16 bytes, SHA-256
5074e39dcddfb569b7591d0fd1011e50037012f444ab42bf95bc2b4053353d3f.

Maintained source is src/shared/dos/dos_free.asm. It expresses the 8086 DOS
AH=49h call symbolically and emits exactly those 16 CODE bytes. No codestring,
target byte array, object patch, or inline target-derived opcode block is used.

The historical library object also contains a zero-byte _DATA SEGDEF grouped
into DGROUP. A first local source with only _TEXT reproduced every linked byte
but changed the MAP by removing that zero-size contribution. v524 therefore
keeps an empty _DATA/DGROUP declaration as real OMF/link topology; it emits no
data bytes.

## Cold archive replacement

Run:

    python3 scripts/probes/replay_th04_zun_dos_free.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay cold-compiles cfg_init and _main, assembles maintained GRAPH_CLEAR,
RESDATA, FILE_READ, and DOS_FREE, extracts the pinned MASTER archive, and
rebuilds it in its original physical member order. DOS_FREE must remain at
zero-based archive index 211.

The locally assembled DOS_FREE object has 16-byte CODE SHA-256
5074e39dcddfb569b7591d0fd1011e50037012f444ab42bf95bc2b4053353d3f.
Its CODE is equal to both the extracted original member and the decoded target
extent. Replacing DOS_FREE together with the three previously localized
support owners leaves the complete resident diagnostic MAP and 6360-byte
candidate component unchanged.

The accepted v524 receipt
.analysis/reconstruction/probes/v524-zun-dos-free-002/receipt.json
has SHA-256
9ddfc0c05fe707efdde31384bb3aefb44ad5f72bf75e236db53f80ac333e2ddf.

The resident candidate still has SHA-256
a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab
and still differs from the target resident component at 4241 bytes. The
blocked natural _main/cfg link context and other external support remain.

## Acceptance boundary

units.csv records DOS_FREE as reviewed, library-origin, source-present decoded
support. It is not an authored function, not a packed-file exact extent, and
does not increment ZUN authored-function exactness.

The next small external MASTER candidates are DOS_AXDX and DOS_PUTS2, followed
by the remaining file helpers. Each still needs its own natural source,
original archive-position check, target slice, and cold aggregate replay.
