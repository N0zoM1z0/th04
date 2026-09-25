# MAINE cutscene_animate natural-C++ exact replay (v687)

## Target-first boundary

The decoded MAINE function at payload `0xADFC` is a contiguous `0xD4`
(212-byte) body loaded at `1A05:0DAC..0E7F`. A fresh attested Ghidra inventory
reports one range, one caller, and seven callees. The next code contribution
begins at `1A05:0E80`, so it is not folded into this function.

This target review is independent of the retained ReC98 source label.

## Maintained source and focused replay

Maintained natural C++ lives in:

`src/maine/cutscene/cutscene_animate.inl`

Replay command:

    python3 scripts/probes/replay_th04_maine_cutscene_animate.py \
      --output-dir .analysis/reconstruction/probes/v687-maine-cutscene-animate-focused-002

Two isolated TC86 Borland C++ 4.02 / TLINK rounds reproduce all 212 function
bytes with zero differences. They also preserve the complete `0xC3E`
`CUTSCENE_TEXT` producer at payload `0xA292`, the retained MAINE MAP/program
image, and all 559 ordered MZ relocation entries.

Function SHA-256:

`7229d2bd0dc77c3664592cc7b9a6576d88aeef8f25fba919bc444c69f654d6c2`

Maintained source SHA-256:

`a7ff640a1f1c24b34703b76525547383690fa02ca7bdc81085f12ad36bd10d1a`

Focused receipt SHA-256:

`7b1b8a77146a99e73d6fd281be545e54dc15e5116a82d2b8b05dcfe9eae103c3`

## Aggregate gate

Before registering the new acceptance row, it was injected only into the
in-memory replay list so every already-accepted backend could still run its
checked-in preflight without circular evidence. The complete MAINE aggregate
then passed **43 / 43** decoded slices raw-zero.

Receipt:

`.analysis/reconstruction/probes/v688-maine-cutscene-animate-aggregate-preaccept-001/receipt.json`

Receipt SHA-256:

`06a1964569469285a9854245e12df734e70a08da7d86d8b0cb8601524739ae1e`

After registration, normal preflight and ledger validation pass with MAINE at
43 / 72 function-level exact.

## Scope limit

This is decoded-function exactness and maintained reconstructed-source
ownership. It does not claim a packed-file offset, whole-`MAINE.EXE` exactness,
or recovery of the literal historical source file used by ZUN.
