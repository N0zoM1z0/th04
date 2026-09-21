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

## v464 `zunsoft_update_and_render()`

The second ZUNSOFT body at load `0xBAC9` is `0x12B` bytes. Its TASM body has no
irreducible low-level instruction sequence: it is a 256-entry near-pointer
particle loop with four integer locals, three age ranges, two `polar()` pairs,
and `super_put_rect()` calls.

The first natural C++ baseline was 349 bytes because assigning/adding the
`Subpixel` wrappers selected floating-point conversion helpers. The target uses
the underlying Q12.4 words directly. Replacing only those operations with

```cpp
pyro->distance_prev.v = pyro->distance.v;
pyro->distance.v += pyro->speed.v;
```

removes exactly the floating-point temporaries and produces the target compiler
shape: `ENTER 8`, `SI` as a `pyro_t near *` iterator, `DI` as the loop index,
and four ordinary stack locals.

The resulting TC86 function is **299 / 299 bytes**. At raw OMF level, 298 bytes
already equal the old TASM owner; relative offset `0x07` differs only because
the C++ TU owns `_pyros` locally and carries its near-offset fixup addend. The
linked word resolves identically.

`probe_th04_zunsoft_update_cpp_v464.py` rebuilds the v461 baseline twice,
recovers both first functions as one TC86 owner, keeps only the final two
ZUNSOFT functions in the TASM tail, and relinks TH04 OP. Both runs produce:

- OP SHA-256
  `6668546c64d9f00e61338fea93df401ce3a65485a8a94fb805cc943a717599e2`;
- MAP SHA-256
  `65e596ca2f0914ecf3468cd1549fb808aeffe89c97a8621a0da3d74ff1144447`;
- exact linked update body SHA-256
  `a2ecb4e9a3c07ff4bb8cf81f539d642a0622b871ce2c456d25a91793e1d5b6b7`;
- combined C++ `OP_MUSIC_TEXT` contribution size `0x1AF`;
- remaining TASM tail size `0x2E1`;
- the complete v461 program image unchanged and the 804-site relocation
  multiset target-equal.

TC86 now emits the eight segment relocations from the first two functions as
one descending-address block:

`0xBBE2, 0xBBC3, 0xBBA5, 0xBB7C, 0xBB5E, 0xBB3A, 0xBAA0, 0xBA8F`.

The total ordered residual remains 105 only because these exact C++ functions
and the two remaining ASM functions are still separate physical OMF owners. The
result strengthens the single historical TC86-TU explanation for the complete
0x490-byte ZUNSOFT block.

Private receipt SHA-256:
`ae10a6bc0bbfe25eb76340fc9710c18b58c514e8568c6cd5475d81dd6d1422b3`.

Next recover `zunsoft_palette_update_and_show()`, then `zunsoft_animate()`.

## v465 `zunsoft_palette_update_and_show()`

The third body spans load `0xBBF4..0xBC34` (`0x41` bytes). A direct natural C++
translation is enough: `SI` is the color index, `DI` the RGB component index,
and the assignment is simply

```cpp
Palettes[color].v[component] =
    (zunsoft_palette[color].v[component] * tone) / 100;
```

followed by `palette_show()`. TC86 emits **all 65 raw OMF CODE bytes exactly**
on the first bounded source shape, including loop branches, multiply/divide,
and `ret 2`.

The v465 A/B replay links this function after the v463/v464 C++ bodies and
keeps only `zunsoft_animate()` in TASM. Both runs produce OP SHA-256
`1e87ecbf564a5ef522c52fc94370ff78f2d917d084fafd249c33ebf91228819b`,
MAP SHA-256
`f026e0bc299a49d9ffd376d51683085a5f8bc5182a7a73e4f3249a03d7ca62bd`,
and exact palette-body SHA-256
`08fc22f1c1142e43cb2ce54b09a86b1472f5788c1287637847f6b0e7ee90e04c`.
The complete v461 program image is unchanged and the relocation multiset remains
804-site exact.

The natural C++ owner now covers `0x1F0` bytes. Its nine segment relocation
sites are emitted in descending address order:
`0xBC2D, 0xBBE2, 0xBBC3, 0xBBA5, 0xBB7C, 0xBB5E, 0xBB3A, 0xBAA0, 0xBA8F`.
Only the final `0x2A0` animate body remains as a separate TASM producer.

Private receipt SHA-256:
`d083f02938b3e2deeb53fb65ced27118724f55cee4364eb0334514f0389ba543`.
