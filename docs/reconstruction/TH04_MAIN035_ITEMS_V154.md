# TH04 MAIN_035 item update producer (v154)

## Result

v154 target-reviews the contiguous item-management producer in `th04-main / MAIN.EXE`
and recovers maintainable natural C++ for it, but deliberately does **not** promote
it to exact.

The reviewed physical producer is:

- segment: `MAIN_035_TEXT`;
- map: `13A9:9F8B..A4D0`;
- load: `0x1DA1B..0x1DF60`;
- target file: `0x1F21B..0x1F760`;
- size: `0x546 / 1350` bytes;
- target slice SHA-256:
  `a0949b541b517ba4be1cb7afd1094b60017235eefd777630b20c038a030f6531`;
- focused candidate slice SHA-256:
  `de372a92ed989ee5d5f1ee8ad556b381f754a5cc76f263110854f67563dd886d`.

The selected private target remains read-only and only
`candidate-local-attested`.

## Recovery and target-first boundary review

The session started by recovering an interrupted v154 source experiment rather
than opening a new packet. The pre-existing dirty paths all belonged to this
same item producer: its exact-unit manifest entry, source-present unit row,
maintained item source, one compatibility forwarder, and a symbol-only public
alias in the already-exact v143 shot selector assembly. No unrelated or unknown
tracked work was present.

The owner contains six reviewed authored functions:

| Function | Load extent | Physical size | Fresh Ghidra observation |
| --- | --- | ---: | --- |
| `items_init()` | `0x1DA1B..0x1DA37` | `0x1D` | Complete contiguous body. |
| `items_add(int,int,item_type_t)` | `0x1DA38..0x1DACD` | `0x96` | Complete contiguous body. |
| `items_miss_add()` | `0x1DACE..0x1DBAD` | `0xE0` | Truncated to the first `0x0B` bytes. |
| `item_collect(item_t near*)` | `0x1DBAE..0x1DDF6` | `0x249` | Sparse body; compiler table ownership omitted. |
| `item_lower_playperf(item_t near*)` | `0x1DDF7..0x1DE5C` | `0x66` | Gross cross-link from image `0x200B4` to `0x2DE50`. |
| `items_update()` | `0x1DE5D..0x1DF60` | `0x104` | Complete contiguous body. |

Pinned TASM, its included `th04/main/item/miss_add.asm`, target bytes, gap-free
16-bit decoding, caller/callee anchors, and the exact next-owner seam close the
physical extents without trusting the bad database ranges. Exact `boss_reset()`
begins at load `0x1DF61`.

Two compiler-owned switch tails are part of the reviewed physical extents:

- `item_collect`: executable through load `0x1DDE8`, followed by seven words at
  `0x1DDE9..0x1DDF6`. They resolve to loads `0x1DBD0`, `0x1DC33`, `0x1DC8F`,
  `0x1DCCC`, `0x1DD35`, `0x1DD47`, and `0x1DD6F`.
- `item_lower_playperf`: executable through load `0x1DE50`, followed by six
  words at `0x1DE51..0x1DE5C`. They resolve to loads `0x1DE11`, `0x1DE17`,
  `0x1DE21`, `0x1DE11`, `0x1DE2B`, and `0x1DE2F`.

Every table target was independently checked against a decoded instruction
start. The complete `0x546` owner contains fifteen MZ relocation entries in
original target order:

```text
0x1DDDD 0x1DD8E 0x1DD60 0x1DD59 0x1DD4C
0x1DD43 0x1DD01 0x1DCB1 0x1DC8A 0x1DBFC
0x1DA21 0x1DF40 0x1DEB2 0x1DE4A 0x1DE34
```

## Maintained natural source

Maintained source is `src/main/item/items_update.cpp`, SHA-256
`bfb87a0ee1a702870cd731050ad6636d52aded80ede5938b88985ddd1c92d7fb`.
The source keeps the historical FAR/near ABIs, the `MAIN_035_TEXT` / `MAIN_03`
code owner, byte-sized item state, 16-bit item counters where target storage is
word-sized, and the `PlayfieldMotion::update_seg3()` `DX:AX` return convention.
No inline assembly, `#pragma codestring`, copied target bytes, inert padding,
fake return, object patch, target patch, or ABI lie is used.

Three target-local declaration/storage corrections are replay-only plumbing, not
new storage owners:

1. ReC98 currently declares `items_miss_add()` as near even though target TASM
   and machine code use a FAR entry/return. Replay corrects that declaration to
   FAR for this translation unit.
2. Target BSS declares `stage_point_items_collected` as one byte, while the
   current ReC98 header declares `unsigned int`. Replay corrects the declaration
   to `unsigned char`; storage remains in the original BSS owner.
3. The real word `_total_max_valued_point_items_collected` has a symbol name too
   long for the historical command-line compiler/linker surface used by this
   isolated overlay. Replay adds the zero-byte word alias
   `_max_valued_point_items` at the same original `dw` storage; no byte is moved
   or duplicated.

The maintained v143 original-style shot selector already owns the required FAR
entry at `sub_11DE6`. v154 only exports the additional spelling `SUB_11DE6` at
that same address so the recovered item source can resolve the historical call;
the v143 instruction bytes are unchanged and the default exact aggregate
revalidates them.

## Focused replay: source-present but blocked

The final current-source focused run is
`gptweb-v154-items-update-focused-candidate-010`:

- dependency closure: 96 owners;
- receipt SHA-256:
  `77c5a1bc3a9a30f02d16b5029990a2d9483a3d1c29d4a5009140804d70bc56ce`;
- manifest SHA-256:
  `7dcd56f5ca9e1432a533fa7c48ffca98c9128312a26f9b33b094b3a5977c24e7`;
- two isolated cold builds;
- exact map contribution:
  `13A9:9F8B 0546 C=CODE S=MAIN_035_TEXT G=MAIN_03 M=th04/itemsu.cpp ACBP=28`;
- all fifteen ordered owner relocations match target in both builds;
- valid deterministic TC86 Borland C++ 4.02 OMF;
- `itemsu.obj` raw SHA-256:
  `73f5c71cc5c61ac3779d17eb3e7201c46316922a57626dfca7712292710209f2`;
- dependency-normalized OMF SHA-256:
  `d29f351c6010cfcc2fe3fc713b3a49890e8770cc2f2f443aa4571340891679ac`;
- both candidate MAIN images have SHA-256
  `d46e64c7e1e6a76950667d0566f5f0abce4306e30021278dcd81699837d17670`;
- all selected dependency owners pass.

The run still fails `raw_exact`, and therefore the unit is intentionally
non-default and blocked rather than promoted.

After target/candidate load-module comparison, the complete `0x546` owner differs
in exactly four bytes, at two instructions inside `items_update()`:

```text
load 0x1DF1F: target 29 C3   candidate 2B D8   ; both SUB BX,AX
load 0x1DF2F: target 29 D3   candidate 2B DA   ; both SUB BX,DX
```

These are semantically equivalent x86 encodings with reversed ModR/M source/
destination opcode forms. Equality is still false; semantic equivalence does not
satisfy the byte-exact Oracle.

A diagnostic function-slice comparison shows zero differing bytes in the first
five reviewed functions. The four bytes above are all inside `items_update()`.
Nevertheless, none of the six functions receives function exactness credit:
the repository requires the complete declared physical producer to be exact
before reviewed functions inside it may be promoted.

## Bounded negative compiler evidence

v154 did not blindly enumerate source spellings. Once the mismatch was localized,
several falsifiable hypotheses were tested and stopped when they ceased adding
information:

- direct unsigned range expressions altered the temporary-register allocation;
- a third `register unsigned int` local displaced the historical SI/DI allocation
  and increased code size;
- compound `_BX -= _AX/_DX` expressions produced the same `2B` encodings plus
  extra moves;
- the target-like stepwise BX lifetime under the actual cold command-line profile
  emits the correct `0x546` CODE size but consistently selects `2B D8 / 2B DA`.

The actual command-line probe for the final source shape is
`itemsu-probe-019.cpp` (the same SHA-256 as the maintained source). Its object
SHA-256 is
`6afa0b0cc65af1fd4540dbe6f71c206ea07a9f88da7261a159475fea3fa3b752`;
the extracted CODE SHA-256 is
`d402522822e87b54b43e349a489567abf13fbd03accb9511004026fad0d2f520`.

A genuinely different historical compiler mechanism was also tested rather than
continuing a source-spelling matrix. The source-driven original PC-98 IDE
integrated compiler used successfully by v147 was run under the same pinned
TC4J/DOSBox-X profile. The final source's ReC98 `_EAX` pseudo-register surface is
not defined inside the integrated IDE environment, so that exact spelling cannot
compile there. An `_EAX`-free ordinary-`unsigned long` source variant does compile,
but emits 1380 CODE bytes and still chooses `2B D8 / 2B DA` rather than the target
`29 C3 / 29 D3`. Its IDE object identities are:

- source SHA-256:
  `5c686f0a3d06d3db6a17584fc3126b3f1962b7ff35dbe73202cb8e29c011f542`;
- raw OMF SHA-256:
  `4d78cb4e64ddcb7d9bc9d8206289d485d20ad0f16b215ba480a7e88b7dda80d6`;
- dependency-normalized OMF SHA-256:
  `a598a64d95c25829eac52e72df530b2e2b397dd772f2e45f0e4082153606b931`.

This is retained as negative mechanism evidence. No further compiler/source
spelling matrix is justified without a genuinely new hypothesis.

## Exact baseline regression replay

Because the blocked v154 unit is `default_enabled = false`, it does not contaminate
the accepted exact cohort. After the source/header/alias changes, the complete
default exact cohort was replayed separately as
`gptweb-v154-items-blocked-baseline-001`:

- selected default owners: 187;
- blocked v154 owner selected: no;
- receipt SHA-256:
  `3b2f770fab5bb0830a4e0243f0a02ce8787de5e9778645c625dea939632e456b`;
- two cold builds, `failures=[]`;
- both candidate MAIN images retain SHA-256
  `49118749258855f0c6b51f73ffeee76697274f353b6176b7898775c695cafc32`.

This proves that v154 plumbing does not regress any previously accepted exact
owner. It is not an aggregate acceptance or promotion of the blocked item owner.

## Accounting and verification planes

After reviewing this packet, the live MAIN denominator is intentionally larger:

- `57,102 / 58,456` exact reviewed authored bytes (`97.683728%`);
- `346 / 353` exact reviewed authored functions (`98.016997%`);
- seven reviewed blocked functions: the six v154 item functions plus the existing
  `snd_load` blocker;
- 187 default exact replay owners remain accepted.

The drop in reviewed exactness is a denominator correction and a durable hard
result, not a regression of any accepted exact owner.

v154 establishes target-first boundary ownership and maintainable source presence.
It does **not** establish v154 function/owner byte exactness. The replay also does
not establish standalone TH04 production-source/link closure, runtime-storage
identity, a runtime scenario, whole-image exactness, independently pristine target
provenance, or Factory Truth Kernel acceptance.
