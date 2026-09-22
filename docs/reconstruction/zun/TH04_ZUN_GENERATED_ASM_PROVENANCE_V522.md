# ZUNINIT / MEMCHK generated-assembly provenance (v522)

This packet closes one source-provenance route for the two target-derived
assembly components in ZUN.COM. It does not identify the original source form.

## Pinned ReC98 history

Run:

    python3 scripts/probes/probe_th04_zun_generated_asm_provenance.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The probe reads only immutable blobs and commit metadata below pinned ReC98
revision b6ba5b0a529edbb31efdf8c0e939263804f8ee47. It never treats the current
reference worktree as source authority.

ZUNINIT enters the pinned ancestry in commit
f54cd0fe95d393b793d521b0df08f16dd725b1d5, subject
[th04/zuninit] Initial state. The imported file already contains the standard
IDA-generated header. The commit message explicitly says these small binaries
would still need RE attention. There is no later ZUNINIT path commit in the
pinned ancestry.

MEMCHK enters in commit
90b7ace180c23bfb9b5b23e61ef8a1cb431a18da, subject
[th04/memchk] Initial state, also already carrying the IDA-generated header.
Its only later path commit is
6212a4c21ba7c0acb8652f676ca2c31ac565a916, which changes the literal spelling
0FFh to 255 to avoid a position-independence false positive. It does not
replace the decompiled assembly with independently sourced original code.

The v522 receipt
.analysis/reconstruction/probes/v522-zun-generated-asm-provenance-001/receipt.json
has SHA-256
083cc34c9c016f33ef8d444c063c9d4d92b3e4746a315d95d507ce28067d884d.

## Consequence

The candidate ZUNINIT and MEMCHK assembly can corroborate labels, entries,
layout, and linked bytes, but it is not independent original-source
provenance. Raw-equal candidate-linked components do not change that fact.

Keep the eleven ZUN target-derived-asm entries unresolved. Do not copy these
files into maintained product source as original ASM merely to gain exactness.
A future source acceptance needs independent provenance or a natural
reconstruction justified from target behavior and compiler/assembler evidence.
