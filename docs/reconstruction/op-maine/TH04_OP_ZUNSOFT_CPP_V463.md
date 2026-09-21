# TH04 OP ZUNSOFT natural C++ frontier (v463)

## Scope

The current OP relocation frontier leaves 35 target-constrained segment
relocations inside the 0x490-byte `OP_MUSIC_TEXT` ZUNSOFT owner. v453 rules out
pinned TASM5 option/version emulation as the cause of their reversed FIXUPP
order. The ReC98 tree already contains a C++ ownership shell in
`th04/op/zunsoft.cpp`, but the ZUNSOFT functions are declaration stubs while
`th04/zunsoft.asm` owns the executable bodies.

v463 asks the smallest non-circular question: can the first 0x84-byte function,
`zunsoft_pyro_new()`, be recovered as ordinary TC86 C++ while preserving the
linked OP bytes and physical entry point?

## Natural source shape

The checked replay template uses only C++ language/ABI constructs already
present elsewhere in the tree:

- `pascal near` function ABI;
- a `pyro_t near *` iterator kept in `SI`;
- one register coordinate kept in `DI`;
- two ordinary integer locals, naturally producing `ENTER 4`;
- ordinary `for`/`if`, structure stores, `% 224`, `irand()`, and pointer
  increment.

No inline ASM, codestring, `__emit__`, object patch, or MZ relocation editing is
used.

The source-level declaration order matters only through normal TC86 register
and stack allocation. The resulting 0x84 object CODE is byte-equal to the old
TASM body except at raw object offset `0x1F`: the C++ object defines `_pyros` in
the same TU and therefore carries a local near-offset addend, while the old ASM
owner references `_pyros` externally. Both forms carry an OMF offset FIXUPP and
resolve to the same linked word.

## Linked replay

`scripts/probes/probe_th04_zunsoft_pyro_cpp_v463.py` starts twice from the
retained v402 source snapshot, reconstructs the accepted v461 physical OP
layout, then:

1. compiles the natural C++ `zunsoft_pyro_new()` owner with pinned TC86 4.02;
2. assembles the remaining three ZUNSOFT functions as a 0x40C-byte TASM tail;
3. places the C++ contribution immediately before that tail in
   `OP_MUSIC_TEXT`;
4. relinks TH04 OP only, avoiding unrelated TH05 reuse of the shared object.

Both A/B runs produce:

- OP SHA-256
  `b73e54f2e2c751a9c9fec040ab7ec60dcc0beb785cbed17661df1b91f9d17235`;
- MAP SHA-256
  `e975808eadbfe5a50e82a654b626a6f825d1aeb9c5d08010d56071583d9075cf`;
- `ZUNSOFT_PYRO_NEW` at the original `0A74:1305` / load `0xBA45` entry;
- exact linked 0x84 function SHA-256
  `df2adf09d0e2a577192d3d8ee54bcbd7f33336ce8d6ec2a404139eec9cb3f28e`;
- the complete v461 program image unchanged, so the only payload residual is
  still shared `snd_load` `89 C3` versus natural `8B D8`;
- the same target-equal 804-site relocation multiset.

TC86's function-local segment FIXUPPs are emitted at code offsets `0x59` then
`0x48`, i.e. high address before low address. Replacing the first TASM body with
the C++ owner therefore reverses exactly OP relocation indices `271..272`
without changing any linked code byte. The total ordered residual remains 105,
because the remaining 0x40C TASM tail is still a separate physical producer.
This is positive producer evidence: if the entire 0x490 ZUNSOFT owner is
recovered as one TC86 C++ TU, the compiler has the observed direction needed by
the target's whole-block reversal.

Private receipt SHA-256:
`595785b5a78118da20b33db4ac3efaba899c0ffbb247c453392d32004f1331dd`.

## Remaining work

Continue with `zunsoft_update_and_render()`, then the palette/update/animate
functions. Do not promote the OP-music relocation block by manually reversing
FIXUPP or MZ entries. This packet proves one linked-exact natural function and a
compiler direction fingerprint; it does not yet establish the remaining source
text or packed-file exactness.
