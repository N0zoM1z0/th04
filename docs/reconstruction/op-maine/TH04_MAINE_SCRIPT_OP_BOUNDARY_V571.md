# MAINE indirect-dispatch function boundary at payload 0xA847 (v571)

## Claim and limits

The target-decoded MAINE load-module function beginning at payload offset
`0xA847` occupies the contiguous extent `[0xA847, 0xADBC)`, or `0x575` bytes.
The loaded address is `1A05:07F7..1A05:0D6B`; the next bytes are a 64-byte
switch table beginning at `1A05:0D6C` / payload `0xADBC`. The entry returns
through one common `RET 2` epilogue. This closes physical function ownership
only. The candidate name `script_op(unsigned char)`, meaning, source provenance,
and any byte-exact source reconstruction remain unverified.

The target remains `candidate-local-attested`, not independently proven to be
an official pristine dump. Preflight passed for all four TH04 artifacts.
Configured MAINE packed-target SHA-256 is
`670de6ba907a2edbc1592de810acd92e5b89541d3dc35b70210171166d1713f8`.
The target-derived decoded payload SHA-256 is
`7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c`, matching
the retained boundary-review payload. The diagnostic Ghidra image is not the
original packed executable: it combines target-restored load bytes with a
candidate-derived MZ header/relocation topology.

## Candidate provenance (not target evidence)

The local ReC98 path corresponding to `candidate:th04/cutscene.cpp` is a
38-byte forwarding file containing only
`#include "th03/cutscene/cutscene.cpp"`; the referenced TH03 source defines a
function named `script_op(unsigned char)`. This explains the candidate label,
but does not prove that its semantics, source ownership, or generated code
match this MAINE target. No upstream source was imported or used to close the
target boundary.

## Boundary evidence

The v569 Ghidra image SHA-256 is
`332cbf172dec3394410f9d43844b2a81f8909a6b7ec48e989602d014a5aebcbc`; its
attested function inventory SHA-256 is
`c82e4500191cc066a7e18bd6d3d4ceefe698127dd787993a8fff01ee510f8fd0`. A fresh
read-only inventory check passed against that exact diagnostic image. Its
function row identifies entry `1A05:07F7`, one caller and one callee, but only
58 body bytes in two ranges: the 51-byte dispatcher at `07F7..0829` and the
7-byte tail at `0D65..0D6B`. The 58-byte figure is retained as Ghidra's raw
auto-analysis result, not the full function extent.

The target byte stream independently decodes linearly from payload `0xA847`
through `0xADBB` as 1,397 bytes / 462 NDISASM 2.16.01 instructions. At the
dispatcher, `BX` starts at `CS:0D6C` and scans 16 opcode words; the indirect jump
at `CS:0826` loads a target from `CS:0D8C + 2*i`. The adjacent 64-byte table
hashes to
`0da2437ab6e353c87305c94b220533f7be6ec78785447922a71da84d0f480087`. Its
opcode-to-target payload mapping is:

| Opcode | Target | Opcode | Target |
| --- | ---: | --- | ---: |
| `$` | `0xADB1` | `=` | `0xAC3F` |
| `@` | `0xAB48` | `b` | `0xA8FC` |
| `c` | `0xA8E5` | `e` | `0xAD95` |
| `f` | `0xAA38` | `g` | `0xAA9F` |
| `k` | `0xAB26` | `m` | `0xAD02` |
| `n` | `0xA87A` | `p` | `0xAB61` |
| `s` | `0xA88F` | `t` | `0xAA0E` |
| `v` | `0xA9D2` | `w` | `0xA913` |

All 16 targets land on instruction starts inside the proposed extent. The
handlers use the entry's frame (including `[BP+4]` and locals), and their
direct paths converge on the tail at `0xADB5` or the `AL=0xFF` path at
`0xADB1`; both reach the single `pop si; leave; ret 2` epilogue. The function
extent hash is
`bfe8e1a9a3aaa823807f3e3e2053ed2eae6e47fbe6cdc1406ba5d432acf7eb15`.

## Reproduction and next step

The function-boundary evidence is recorded as
`ev-th04-maine-script-op-boundary-v571`; its reusable warning is
`th04-maine-script-op-indirect-boundary-v571`. The boundary ledger now marks
this candidate `reviewed`, while `accepted_state` remains `unreviewed` and no
decoded-function exactness is claimed.

Commands used after target preflight:

```sh
python3 scripts/boundary_review/export_ghidra_inventory.py th04-maine \
  .analysis/reconstruction/probes/v569-polar-ghidra-prepare/th04-maine/analysis.exe \
  --format mz --project-name TH04-polar-boundary-maine-v569 \
  --export-dir .analysis/reconstruction/probes/v569-polar-ghidra-prepare/ghidra/maine check
dd if=.analysis/reconstruction/probes/v569-polar-ghidra-prepare/th04-maine/payload.bin \
  bs=1 skip=43079 count=1397 status=none | ndisasm -b16 -o0xa847 -
dd if=.analysis/reconstruction/probes/v569-polar-ghidra-prepare/th04-maine/payload.bin \
  bs=1 skip=43079 count=1397 status=none | sha256sum
dd if=.analysis/reconstruction/probes/v569-polar-ghidra-prepare/th04-maine/payload.bin \
  bs=1 skip=44476 count=64 status=none | sha256sum
```

Next, recover a natural MAINE source owner and compiler/TU context for this
whole dispatcher before attempting decoded acceptance. Do not split the 16
handlers into independent functions, treat the following table as code, or
transcribe target bytes/assembly as a shortcut. Candidate names and semantic
claims need caller/callee and target behavior corroboration.
