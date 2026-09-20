# TH04 END_TEXT tile-ring update v386

## Scope

This packet narrows the remaining reviewed 0xC7 / 199-byte scroll helper at
load `0xB835..0xB8FB` (`th04-main-scroll-tile-ring-v270`). It does
not promote the owner. The current maintained source remains
`src/main/scroll/tile_ring_update.cpp`.

## Pure C++ codegen closure to exact size

The v270 maintained source compiled to 215 bytes. A bounded v384 dataflow
variant keeps the scroll row in AX, loads `std_seg` into ES before the
section-speed logic, uses DL for the speed byte, and precomputes the tile
destination/source offsets before Borland `__memcpy__`. With a near
destination pointer the pinned TC4J 4.02 compiler emits exactly **199 bytes**
with every branch target aligned to the target function.

The remaining differences are not size or CFG differences. They are the
register-direction / zeroing choices `89 C7 / 31 C0 / 30 FF / 00 DB /
89 C6 / 01 DE` and the exact DS/ES save/setup order around the single
`REP MOVSW`. Register-option (`-r/-rd/-r-`), `-Z-`,
speed-bias `-G`, ordinary register locals, pointer locals, standard
`memcpy()`, and `movmem()` bounded probes do not recover them.

## Producer mechanism

A TC4J built-in inline-assembler control using only the symbolic mnemonics
`mov di,ax; xor ax,ax; xor bh,bh; add bl,bl; mov si,ax; add si,bx`
emits exactly the target byte directions. The same mnemonics assembled by
TASM32 5.0 emit the opposite candidate-style encodings. TASM default,
`NOSMART`, `QUIRKS`, and `VERSION T400/T300/M510` all
produce the same non-target direction bytes.

A private full-function diagnostic then replaces only those low-level
operations plus the DS/ES `REP MOVSW` setup with symbolic TC4J inline
assembly. It emits one 199-byte END_TEXT contribution, CODE SHA-256
`5e81bdc5fc30915b90fb80904cb7ee65267862f8ede40a0436de9a0a3692dbba`.
Compared with the target, all non-link fixed bytes are identical. The
remaining object-vs-target differences are unresolved data/call fields in the
unlinked OMF object. Linked raw/MAP/relocation exactness is **not** claimed.

Private mechanism receipt SHA-256:
`f80b5d3eb5170c2800ffc0db3fde6f06263db792b357e78b8085328e8f883f75`.

## Independent TH05 corroboration

The attested TH05 MAIN target contains a homologous scroll/tile-ring helper at
load `0xC43A..0xC505`. Its copy block independently preserves target
`89 C7`, `31 C0`, `30 FF`, `89 C6`, `01 DE`
and the exact segment-copy order:

`PUSH DS; POP ES; PUSH DS; MOV AX,[map_seg]; MOV DS,AX; MOV CX,18h;
REP MOVSW; POP DS`.

TH05 has game-specific stage conditions and section indexing, so this is
producer-lineage corroboration rather than byte transfer or exact evidence.

## Provenance decision

The repository permits independently justified genuine handwritten low-level
source; it does not permit adding target-derived inline assembly merely to
manufacture equality. TH02 tile code supplies a broader historical example of
C++ plus inline assembly for compact low-level tile loops, and TH05 confirms
the exact producer architecture. However, no direct historical source or
candidate low-level idiom for this specific TH04/TH05 helper has been
recovered from ReC98 history.

Therefore v386 records **mechanism reproduced, provenance still open**. The
tracked function remains reviewed/authored/blocked. Do not convert it to
standalone TASM: the tested TASM toolchain does not reproduce the target
encoding choices anyway. A future promotion requires independent source-origin
justification plus focused linked raw/MAP/ordered-relocation replay and a
complete aggregate.
