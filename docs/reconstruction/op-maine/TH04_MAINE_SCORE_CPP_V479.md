# TH04 MAINE SCORE_TEXT natural C++ frontier (v479)

## Scope

v478 fully closes MAINE_01 internal relocation order. MAINE then has only 42
target-constrained relocation-order differences:

- 34 inside the reconstructed `SCORE_TEXT` owner;
- 8 in shared BGIMAGE.

The residual SCORE owner begins at load `0xC3B2`. Its first private function is
`0x154` bytes long. Although its original symbol name is not target-attested,
its semantics are unambiguous from target code and the maintained scoredat
structures: insert `resident->score_last` into `hi`, shift lower entries, fill
the new name with `gs_DOT`, copy the score digits, and write either `gs_ALL` or
the current stage.

The replay calls this helper `score_insert()` descriptively. That name is not a
historical-source claim.

## Natural C++

The checked template uses ordinary C++ only:

- nested descending score-digit comparisons;
- the same signed integer-promotion behavior present in the target;
- explicit place/name/score shift loops;
- direct `resident` and `hi` field accesses;
- ordinary stage/end-sequence selection.

Pinned TC86 4.02 emits **340 / 340 raw CODE bytes exactly**. Raw SHA-256:

`978e0eb303d2875ed00983f0ea3fc9d48136949afbcd677190a7447eeba2d09c`.

The function has only data-offset fixups; it contributes no segment relocation
whose order can change the 42-entry packed frontier by itself.

## Linked replacement

`probe_th04_maine_score_insert_cpp_v479.py` starts from the retained v478 source
snapshot only after checking its EXE, MAP, response-file owner token, and SCORE
owner identities. Two independent copies then:

1. compile the `0x154` C++ prefix;
2. assemble the unmodified TASM remainder as a separate SCORE_TEXT owner;
3. bridge the later `regist_menu()` call through a same-segment near external;
4. relink TH04 MAINE.

The TASM remainder keeps its exact size `0x774`. Its raw OMF addends are allowed
to differ at normal SCORE_TEXT fixup fields after the physical split; final
linked bytes and the entire relocation table are the fail-closed acceptance
surface.

Both A/B builds produce:

- MAINE SHA-256 unchanged from v478:
  `45aa099ecb29aee883c29ea37c7ad8493ed1871e8b3694a19b63b8e28c331989`;
- MAP SHA-256
  `8bef805e5d3d83081860375d50b5120d978da1486aa632741d14b51f1dc21a2a`;
- unchanged program-image SHA-256
  `0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1`;
- linked helper SHA-256
  `ed7880a5a1cd7aa721c2a95bafb819da15768fd660cf6dd96dbccc9fdc30c093`;
- complete 559-entry relocation table byte-for-byte unchanged from v478;
- ordered residual still **42** (`517 / 559` same-index).

Private receipt SHA-256:
`a4b9e232547cea85c09be6316c1c05a83ff502e2b570366486ad4ce53e07c400`.

## Next work

Continue forward through the adjacent SCORE_TEXT helpers (`sub_C506`,
`sub_C5EC`, `sub_C665`, `sub_C711`, `sub_C7C9`, `sub_C7E3`, registration menu,
and the final EGC helper pair). The goal is to grow one natural TC86 SCORE_TEXT
producer until its internal segment-FIXUPP order matches the remaining 34 target
indices. Do not permute MZ relocation entries.
