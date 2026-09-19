# TH04 B4M explosion producer (v156)

## Result

v156 target-reviews and exactly reconstructs the complete contiguous explosion-add producer in `th04-main / MAIN.EXE` as maintained natural C++.

The physical owner is:

- segment: `B4M_UPDATE_TEXT`;
- map: `13A9:21DD..22E3`;
- load: `0x15C6D..0x15D73`;
- target file: `0x1746D..0x17573`;
- size: `0x107 / 263` bytes;
- target/candidate slice SHA-256: `ce4bde13e5ce5ef5379271a1f4d7e90210a50a407ffdf75a64b23b507caa17da`.

The private target remains read-only and only `candidate-local-attested`.

## Authored-boundary correction

Three authored functions tile the owner without gaps:

| Function | Load extent | Size | ABI |
| --- | --- | ---: | --- |
| `explosions_small_reset()` | `0x15C6D..0x15C7B` | `0x0F` | FAR |
| `boss_explode_small(explosion_type_t)` | `0x15C7C..0x15CFB` | `0x80` | Pascal near |
| `boss_explode_big(unsigned int)` | `0x15CFC..0x15D73` | `0x78` | Pascal near |

Fresh Ghidra correctly sees the reset body, but its small-explosion function is cross-linked: 316 body addresses across five ranges extend through unrelated image `0x26AE8`. The big-explosion database body ends at `0x25D6B`, covering executable code but not compiler-owned trailing data. Neither database extent is accepted as physical ownership.

Pinned TASM include structure, gap-free target decoding, the exact next-PROC seam, and switch-target validation prove the two physical tails. Small executes through `RET 2` at load `0x15CF1`; its four-word table at `0x15CF4..0x15CFB` resolves to loads `0x15CC6`, `0x15CCC`, `0x15CD2`, and `0x15CDE`. Big executes through `RET 2` at `0x15D69`; its table at `0x15D6C..0x15D73` resolves to `0x15D3E`, `0x15D44`, `0x15D4A`, and `0x15D56`. Independent 16-bit raw decoding confirms all eight destinations are instruction starts. `sub_15D74` begins at the next byte.

The target has two MZ relocation entries inside the complete owner, in table order `[0x15D65, 0x15CED]`. Focused and both aggregate replays reproduce that exact order.

## Natural source

Maintained source is `src/main/boss/explosion_add.cpp`, SHA-256 `2f94438d8d0d343ca9fbf9fa183840a8be33d23ba31c0d916fb717752fc09226`.

The source keeps reset FAR under the large model and explicitly preserves the two Pascal-near public ABIs. A normal shared C++ initialization macro expresses the common explosion semantics; ordinary `switch` statements naturally cause TC4J to emit each four-word trailing jump table. The source does not encode those tables or target bytes manually.

No inline assembly, `#pragma codestring`, copied target-byte array, inert padding, fake return, target/object patch, or ABI lie is used.

Because this owner is peeled from the historical `B4M_UPDATE_TEXT` assembler contribution, exact replay extracts the untouched suffix beginning at `sub_15D74` into hash-bound `th04/b4msuf.asm`. The suffix is zero reconstruction credit and is checked as a valid deterministic TASM OMF auxiliary object. Maintained C++ occupies the original owner position before it.

Current replay inputs are bound by:

- source SHA-256: `2f94438d8d0d343ca9fbf9fa183840a8be33d23ba31c0d916fb717752fc09226`;
- replay suffix template SHA-256: `58b5570534ed47c1a20fc1991d01efd0809c643c7677e4b9c9839313d3707199`;
- exact-unit manifest SHA-256 at replay: `cbb021b528a85436eedf0f44e30fe13ddbafe3a75a491076dcaf5e1fd8bb8f5a`.

The final cold `eadd.obj` is valid TC86 Borland C++ 4.02 OMF:

- raw SHA-256: `8a3c4aa673c90619f6adedb1347b3c7748d6422527de44b2128755baa18fe0c2`;
- dependency-normalized SHA-256: `01379b173530fc0dc2b7238d43d0c2ab4daa227f8a0bf1a91276f98c4c4fdb2a`;
- exact map contribution: `13A9:21DD 0107 C=CODE S=B4M_UPDATE_TEXT G=MAIN_03 M=th04/eadd.cpp ACBP=28`.

The auxiliary suffix object is valid TASM 5.0 OMF with dependency-normalized SHA-256 `5e609e5a6f618c3430b0e5c541c38c04b856c3820d1a23b9013e13cc3d59f250`.

## Exact replay

Focused replay:

- run: `gptweb-v156-boss-explosions-focused-candidate-007`;
- 97-owner dependency closure;
- receipt SHA-256: `3f3136dc8196c97f1e0951b3f429f0b696284a6bf55bfc06b2bb5fc0c64c3077`;
- two isolated cold builds;
- `failures=[]`;
- exact owner bytes, map, both ordered relocations, valid deterministic OMF, auxiliary suffix OMF, and dependency closure;
- both focused candidate MAIN images: `638e094b7355d358aa9cdd378de82fb315f11d67526707de0b7b2ee6458f99bb`.

Candidate-state aggregate:

- run: `gptweb-v156-boss-explosions-aggregate-candidate-001`;
- all 189 default owners twice;
- receipt SHA-256: `d1820bf1d57442a450cc1f935d5230f09daa6549601d41de5b6724aad95a4181`;
- `failures=[]`;
- both candidate MAIN images: `f3818701c914641abd9a37d78c499bdec35eae66ce1d33f1e187b39e8bd4f127`.

Post-promotion aggregate:

- run: `gptweb-v156-boss-explosions-aggregate-final-001`;
- all 189 default owners twice;
- receipt SHA-256: `633856b83024969834a7470170c2c8c7c24ea3588a85e08585d506f202bc1424`;
- `failures=[]`;
- both candidate MAIN images remain `f3818701c914641abd9a37d78c499bdec35eae66ce1d33f1e187b39e8bd4f127`.

Focused candidates 001 through 006 are receiptless exploratory source/layout builds. They receive zero exactness credit and are not used as durable acceptance evidence.

## Accounting and verification planes

v156 adds 263 reviewed authored bytes and three reviewed authored functions, all exact. The live ledger after promotion is `58,786 / 60,140` exact reviewed authored bytes and `355 / 362` exact reviewed authored functions, with 189 default exact owners. The seven pre-existing reviewed blockers are unchanged.

v156 establishes repository-native owner/function extent exactness for this three-function producer. It does not establish standalone TH04 production-source or link closure, runtime-storage identity, a runtime scenario, whole-image exactness, independently pristine release provenance, or Factory Truth Kernel acceptance.
