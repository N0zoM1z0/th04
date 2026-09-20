# TH04 sub_B835 / scroll tile-ring exact closure v393

## Result

The reviewed 199-byte `sub_B835` function at load `0xB835` / file `0xD035`
is exact as maintained authored C++ with evidence-classified handwritten
low-level statements.

The earlier v386 pure-C++ body already reached the target 199-byte size and
control-flow graph but still differed in TC4J-selected register direction and
copy setup. Independent TH05 target evidence preserves the same low-level
architecture, including the register-direction choices and the DS/ES
`REP MOVSW` tile-row copy. Following the repository's accepted hybrid-C++
precedents, those statements are classified as genuine handwritten low-level
source rather than target-derived byte patches.

## Native replay

Focused staged replay `gpt-web-sub-b835-v393-focused-005` passes two isolated
cold builds with `failures=[]`. Receipt SHA-256:

`a50474a06f906ab1e783205d178152ef44d6fa6b6c0ead69db472ca3693954c2`

The maintained `th04/tilering.cpp` object is valid TC86 OMF and contributes
exactly `0xC7` bytes at `END_TEXT 0AAF:0D45`. All 199 linked bytes match
target, and target/candidate each contain the same sole relocation at load
`0xB8F6`.

The 267-owner candidate aggregate
`gpt-web-sub-b835-v393-aggregate-candidate-001` passes twice. After promotion,
the independent final aggregate `gpt-web-sub-b835-v393-aggregate-final-001`
again passes all 267 default MAIN owners twice with `failures=[]`; final
receipt SHA-256:

`8274430e750c707f368e547fe24cb20d2f8b8e2aa6c35f5e53e2b79c5d04835f`

This closes both the historical TC4J code-shape blocker and the physical
END_TEXT/link-ownership blocker without target-byte arrays or post-link
patching.
