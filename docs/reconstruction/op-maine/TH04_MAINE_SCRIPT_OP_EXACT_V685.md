# MAINE script dispatcher natural-C++ exact replay (v685)

This packet follows the target-first v571 boundary review. It does **not**
inherit v571's candidate-source assumptions as facts; the source and code
generation were re-tested against the restored MAINE target.

## Physical owner

The reviewed function owner is decoded MAINE payload
`[0xA847, 0xADBC)`, size `0x575` (1,397) bytes, loaded at
`1A05:07F7..0D6B`.

The following payload range `[0xADBC, 0xADFC)` is a 64-byte compiler-generated
switch table rather than part of the function body. Its first 16 words are the
keys:

`$`, `=`, `@`, `b`, `c`, `e`, `f`, `g`, `k`, `m`, `n`, `p`, `s`, `t`, `v`,
`w`.

The remaining 16 words are CS-relative handler destinations, all of which land
on decoded instruction starts inside the reviewed function body.

Ghidra's historical two-range / `0x3A` auto-function is retained as diagnostic
metadata only. The reviewed physical `body_size` and `body_span` are both
`0x575`.

## Independent source/codegen check

Maintained source:

`src/maine/cutscene/script_op.inl`

Focused replay:

    python3 scripts/probes/replay_th04_maine_script_op.py \
      --output-dir .analysis/reconstruction/probes/v685-maine-script-op-focused-001

The replay replaces only the dispatcher body in the pinned TH04 cutscene
translation unit, compiles it with the pinned TC86 Borland C++ 4.02 toolchain,
and relinks MAINE in two isolated rounds.

Observed identities:

- function SHA-256:
  `bfe8e1a9a3aaa823807f3e3e2053ed2eae6e47fbe6cdc1406ba5d432acf7eb15`
- switch-table SHA-256:
  `0da2437ab6e353c87305c94b220533f7be6ec78785447922a71da84d0f480087`
- maintained source SHA-256:
  `61615ed8adcb3c8ab7cf1cc5884f4254413b20e0ae1a08234790900e7ac68300`
- complete `CUTSCENE_TEXT` producer SHA-256:
  `ff3e03ee0a5cf33604810a0ab8e70555d9cf4ec680f523fac7f13e7aec7390e6`

Both cold rounds produce zero raw differences for the 1,397-byte function,
zero differences for the adjacent 64-byte switch table, zero differences for
the complete `0xC3E` producer, and preserve all 559 ordered target relocation
entries.

## Aggregate gate

A 42-slice MAINE aggregate was run through the same
`decoded_function_acceptance.replay()` engine used by the CLI, while the
on-disk ledger was deliberately left at the previously accepted 41-slice state
during the run. This avoids the circular failure where older cold backends run
`preflight.py` before the new row has evidence.

Receipt:

`.analysis/reconstruction/probes/v686-maine-script-op-aggregate-preaccept-002/receipt.json`

Receipt SHA-256:

`f6f8069d720acda4340bfb66659b34d2ee7002f665d2c565ed66968f55bd33d1`

Result: all **42 / 42** MAINE decoded-exact slices were raw-zero across 38 cold
backends.

After recording that receipt, the normal acceptance validator, preflight, and
CI all pass with `script_op` registered as exact.

## Scope limit

This is decoded-function exactness. It does not establish a packed-file offset
or whole-`MAINE.EXE` exactness.

`script_op(unsigned char)` is the maintained reconstruction label. Exact
codegen strongly supports this natural source body and behavior, but does not
recover an original ZUN debug-symbol spelling or original comments.
