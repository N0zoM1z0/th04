# Build and matching bring-up

## Known toolchain family

ReC98 documents Turbo C++ 4.0J for C/C++, TASM 5.x for 16-bit assembly, and
TLINK for the final DOS executables.  ReC98 commonly uses the
large memory model and flags equivalent to `-O -b- -3 -Z -d`, with artifact-
specific inputs and ordering.  Those facts are high-value corroboration, not a
license to assume every original TH04 translation unit used one profile.

The local exact tool binaries are not installed or hash-attested yet.  Put
user-supplied tools under `.analysis/toolchain/` and update
`config/toolchain.toml` with their digests before claiming compiler evidence.

## Bring-up order

1. Attest all tool binaries and the DOS/Windows runner.
2. Rebuild an unchanged ReC98 TH01 checkout as a positive whole-image control.
3. Compare all TH01 outputs with this repository's comparator and mzdiff.
4. Change one header, relocation, segment order, code byte, and overlay in
   controlled negative tests; confirm the intended Oracle fails.
5. Rebuild ReC98 TH04 as a second positive/reference control and compare it to
   the locally attested targets.
6. Freeze the environment and record exact commands/digests.
7. Only then add TH04 unit/object adapters and exact ledger rows.

ReC98 source is not imported into `src/`; its build is an untrusted calibration
fixture.  Upstream success or finalized status is never copied into our ledger.
Only outputs produced locally from the attested environment can become local
evidence, and they still must pass every required Oracle.

## Required build receipt

Every exact comparison receipt must include:

- target artifact ID and SHA-256;
- source revision and dirty-state digest;
- compiler, assembler, linker, and runner SHA-256;
- complete flags, macros, response-file contents, and environment whitelist;
- ordered source/object/library/link inputs and their SHA-256;
- output, map, object, and comparison-report SHA-256;
- whether the build was cold and serial;
- accepted extent and every relocation/layout rule;
- comparator version/commit and command.

Incremental builds may diagnose.  They may not publish aggregate exact totals.
