# TH04 MAIN_TEXT thick-laser renderer v168

## Scope

This packet reviews the target-internal thick-laser renderer in `th04-main /
MAIN.EXE / MAIN_TEXT` and recovers maintainable natural C++ without claiming a
linked exact owner.

The reviewed logical extent is `0AAF:37D3`, MZ load `0xE2C3..0xE460`, target
file `0xFAC3..0xFC60`, size `0x19E / 414` bytes. The target slice SHA-256 is
`217a422e808e1d86bd6bd5ccd9439b1bb263ca8f829bb19074d04ae614849159`.
Fresh attested Ghidra constructs one contiguous 414-byte near body. Pinned TASM
opens `sub_E2C3` at the same entry and closes it at the same terminal `RET`;
`sub_E461` begins at the next byte. Exact `yuuka5_fg_render()` calls the entry
from target load `0xEA68`. The body has four callees and thirteen MZ relocation
entries.

## Natural source

Maintained source is `src/main/bullet/thicklaser_render.cpp`, with the currently
unlocalized TH04 laser layout explicitly quarantined through
`compat/rec98/th04/main/bullet/laser_t.hpp`. Exact earlier TH04 evidence already
proved that the pinned ReC98 `thicklaser_t` declaration is three bytes too short:
the target has four unknown bytes after `origin`. Exact replay applies the
existing hash-bound v32 layout transform before compiling source that depends on
this ABI. This packet does not weaken or replace that target-local layout fact.

The first ordinary source form compiled to 412 CODE bytes. Its only structural
mismatch was the function prologue: TC4J selected four-byte `ENTER 0Ah,0`, while
the target uses six-byte `PUSH BP; MOV BP,SP; SUB SP,0Ah`. The repository already
has an independently exact same-toolchain precedent for this mechanism in
`bullets_render()`. Adding `#pragma option -G` selects the target classic BP
frame without changing semantics.

The maintained source then emits exactly 414 CODE bytes. It naturally allocates
the laser pointer to SI, the clamped quarter-radius to DI, and the five integer
locals to the target BP slots. Signed `/4` and `/2` expressions reproduce the
target IDIV and signed-halving sequences. Ordinary `_DX`, `_AL`, and `outportb`
produce the target GRCG shutdown without inline assembly or byte emission.

The final source SHA-256 is
`c9530cb8fd03aa1a1e75681586947e31f1fe0243a9df64e7374502029e8fa6b7`.
The standalone TC86 object raw SHA-256 is
`bf0a8389d72044d03dda825ddea8927f087681e147968ba858aae31d2207fec5`;
its dependency-timestamp-normalized SHA-256 is
`92879b77749959e138af22bd6569c66ea16212ea3bf0e4f66156f7d085a2b72f`.
After masking only the `_thicklasers` offset word and the 13 far-call pointer
operands, all 360 fixed code bytes match target. The normalized code SHA-256 on
both sides is
`61192d0090b16bb17bb9849d95d0d905a8dcaa0357729ff9e65fd18272a3a5c0`.
This is compiler/codegen evidence, not linked exactness.

## Physical-owner blocker

The target renderer sits in the middle of the historical `main.obj` MAIN_TEXT
contribution. The following corroborated functions `sub_E461`, `sub_E4D1`,
`sub_E541`, `sub_E67A`, `sub_E7DE`, and FAR `GameExecl()` remain in the same
assembler contribution through load `0xE8A2`; exact v167 `yuuka5_fg_render()`
begins at `0xE8A3`.

Simply removing `sub_E2C3` and appending a C++ object would move the renderer
after that residual suffix and fail target map ownership. A legal isolated exact
promotion would therefore require a large hash-bound replay-only suffix wrapper
with many external dependencies. This packet deliberately does not manufacture
that plumbing merely to promote one function. A later packet should first audit
the complete `0xE2C3..0xE8A2` MAIN_TEXT cohort and determine whether a natural
physical producer can replace the residual functions together.

Accordingly `thicklasers_render()` is reviewed, authored, source-present, and
blocked. No focused exact-unit replay or aggregate replay is claimed for v168.
