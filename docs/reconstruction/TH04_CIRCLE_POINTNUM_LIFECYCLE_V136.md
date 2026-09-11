# TH04 CIRCLE_TEXT point-number lifecycle/render review (v136)

## Scope

Artifact: `th04-main / MAIN.EXE` (`candidate-local-attested`). Target SHA-256:
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The private executable remains ignored operator input and is not a repository
artifact.

This packet reviews the five consecutive point-number entries in `CIRCLE_TEXT`:

| Entry | CIRCLE_TEXT | Load | File | Body |
| --- | --- | --- | --- | --- |
| `POINTNUMS_INIT` | `0AAF:11C2` | `0xBCB2` | `0xD4B2` | `0x0B` |
| `pointnums_invalidate()` | `0AAF:11CE` | `0xBCBE` | `0xD4BE` | `0x35` |
| `POINTNUMS_UPDATE` | `0AAF:1204` | `0xBCF4` | `0xD4F4` | `0x70` |
| `POINTNUMS_RENDER` | `0AAF:1274` | `0xBD64` | `0xD564` | `0x9A` |
| `@pointnum_put` | `0AAF:130E` | `0xBDFE` | `0xD5FE` | `0x6A` |

The five bodies total `0x1B4` bytes. Two independent one-byte `NOP` alignment
slots at load `0xBCBD` and `0xBCF3` make the physical window
`0xBCB2..0xBE67` `0x1B6` bytes. The alignment bytes are not function body
ownership and are not reconstructed with padding source.

The complete physical target window has SHA-256
`25566256a973ee21113c417c4349ce578524f19341b5c31ecdfec069ba0cf2d8`.
No MZ relocation site overlaps the window.

## Boundary evidence

Fresh attested Ghidra observations construct all five entries with the same
contiguous body sizes as the raw target. The current cold MAP has the same five
TLINK publics in `CIRCLE_TEXT`, and pinned TASM starts the same five near
PROCs. Raw 16-bit decoding reaches the expected terminal `RET` for every body,
and `SHOT_LASER_PUT_RAW` begins immediately at load `0xBE68` after the final
point-number body.

Fresh caller/callee observations are used only as provisional target evidence:

- `POINTNUMS_INIT`: one caller, no callee.
- `pointnums_invalidate()`: one caller and one near call to the
  `tiles_invalidate_around` extent at analysis linear `0x1B9D6`.
- `POINTNUMS_UPDATE`: one caller, no callee.
- `POINTNUMS_RENDER`: one caller; calls the scroll conversion extent at
  `0x1BC10` and internal `@pointnum_put`.
- `@pointnum_put`: called only by `POINTNUMS_RENDER` and has no call edge of
  its own.

Ghidra naming, ABI and function construction remain provisional and receive no
exactness credit.

## Natural-source probe

`src/main/pointnum/lifecycle.cpp` is a maintained natural C++ candidate for the
first three functions only. It does not contain inline assembly, target byte
arrays, `#pragma codestring`, fake returns, inert padding or target patching.
Borland register pseudo-variables are used where the target dataflow is itself
register-resident; this is an existing natural-source technique in the
repository.

Three direct TC86 Borland C++ 4.02 probes were compiled through the pinned
ReC98 MS-DOS player with the production `-O -b- -3 -Z -d -ml` profile. The
most useful v3 candidate emits the desired `SI` point-number cursor, `DI=400`,
`BX` alive-pointer cursor, `AX` Y/X temporaries and `CL` age, including
compiler-generated `PUSH DI`/`POP DI`. It is still not exact.

The decisive mismatch is the countdown tail. Target invalidate and update both
end their loops with bare `DEC DI; JNZ`. TC4J emits
`DEC DI; MOV AX,DI; OR AX,AX; JNZ` for the pre-decrement expression used by
v3. A separate six-function microprobe tested pre-decrement, subtraction,
`for`, explicit `goto`, split decrement/test and post-decrement idioms. None
emitted bare `DEC DI; JNZ`; the shortest tested alternative emitted
`DEC DI; OR DI,DI; JNZ`.

For update, TC4J also merges the two source-identical `flag = F_REMOVE` paths,
while the target contains two separate stores followed by jumps to the common
loop tail. These are compiler/source-shape mismatches, not an excuse to inject
bytes or use inline assembly.

The maintained `src/main/pointnum/lifecycle.cpp` candidate was then compiled
directly through the same pinned TC86 runner using the real ReC98 header closure.
It compiles without warnings to a valid 1,961-byte OMF object and 179 CODE bytes.
The maintained source SHA-256 is
`0f02652f0579601b7ead446752d29ac32e82ef60e2d8ad99ae5650aa1a1b8981`; the
CODE SHA-256 is
`ef72078470abf6a76966e1b5cb05f0b32e138050a132e8ac9881ce416e227464`. The
target function bodies total 176 bytes, with the two target alignment NOPs
outside those bodies. Source presence therefore receives zero exactness credit.

## Render/put seam

`POINTNUMS_RENDER` and `@pointnum_put` are boundary-reviewed but remain source
and origin unknown. The target renderer carries values to `@pointnum_put`
through AX/DX/CX, and the put routine saves/restores its working register set
while writing PC-98 VRAM. The renderer also modifies the immediate operand of
an instruction in its own code path to carry the current numeral width. These
facts explain why a conventional standalone C++ function model is not yet
justified, but they do not independently prove original assembly.

ReC98 represents this area as reconstructed assembly. That remains a source
shape hypothesis, not original-language authority.

## Accounting and exactness

`POINTNUMS_INIT`, `pointnums_invalidate()` and `POINTNUMS_UPDATE` enter the
reviewed authored function/byte denominator as blocked nonexact functions.
Their three nonoverlapping bodies total `0xB0` bytes. `POINTNUMS_RENDER` and
`@pointnum_put` are boundary-reviewed but remain `unreviewed` for accepted
source/exactness accounting until a natural producer or independently supported
original-style classification is available.

No focused or aggregate exact replay is claimed for v136 because there is no
exact-promotion candidate. No Factory exactness claim is created by this
packet.
