# MAIN stage-session split diagnostic (v282)

The pinned local MAIN.EXE is SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`
and has `candidate-local-attested` provenance. This probe uses its MZ bytes and
relocation table directly; it does not use a disassembler database.

The reviewed session owner is `DEMO_TEXT 0AAF:03E0`, MZ load
`0xAED0..0xB3ED`, target file `0xC6D0..0xCBED`, `0x51E` bytes. The v214
monolithic C++ source already reproduces every owner byte and relocation site,
but puts the relocation at `0xB2DA` last where the target puts it first.

Run the checked-in bounded probe:

```sh
python3 scripts/probes/probe_th04_demo_pause_split.py \
  --output-dir .analysis/reconstruction/probes/v282-demo-pause-split-replay
```

It attests the target, retained v214 inputs, and pinned TC4J/TASM32/TLINK;
then copies those inputs into a temporary private tree. It compiles the first
three functions from `sess.cpp` separately from `pause()`, places `pause()`
in a synthetic byte-aligned `PAUSE_TEXT` segment, and places the following
demo producer in synthetic byte-aligned `DEMO_TAIL_TEXT`. It assembles the
corresponding zero-code segment anchors and links with `pause.obj` before
`sess.obj`. The temporary tree is deleted; logs and a JSON receipt remain
below the output directory.

Pinned TC4J emits `0x3FF` core bytes and `0x11F` pause bytes. Their
concatenation is **byte-identical** to the original `0x51E` monolithic
`sess.obj` CODE; the `0x9A` demo-tail CODE is also unchanged. The trial MAP
places them at `0AAF:03E0`, `0AAF:07DF`, and `0AAF:08FE` respectively. The
linked owner SHA-256 is the target's
`1c409149015a161d36078c7297e9e5fee04bb2dc4ef1b088c72ec81ed1f71e34`,
and all 52 relocation sites agree as an unordered set.

**Ordered relocation equality fails.** The target's owner sites occupy MZ
table indices `22..62` and `89..99`: `0xB2DA` first, then 40 core sites,
then 11 later pause sites. This trial places all 52 owner sites at indices
`506..557`, with the 12 pause sites before the 40 core sites. Thus a plain
function-level split can preserve code and address layout but cannot explain
the target's isolated early `0xB2DA` fixup. The target OMF and its original
segment identities are unavailable; the synthetic segments do not establish
historical ownership. No exact unit or artifact state changes.

Candidate image SHA-256:
`ce0fb6d3ce61aa922ef2411492c048cfc28d1c93081622ab0fa4b515515a0c0a`.
Private receipt SHA-256:
`ef6335bfac23cdc1f389a2ffea984aed73ec67604c438d20becfd16f4a0a0a7d`.
The next producer hypothesis must predict the **global** MZ table placement
as well as owner-local FIXUPP order while preserving the `0x51E` bytes and
verified source semantics.

## Mid-function segment control (v337)

The target order can be described as one `pause()` relocation at load
`0xB2DA`, then the 40 session-core relocations, then the remaining 11
`pause()` relocations. This suggests a three-part object topology, so the
bounded follow-up tested whether TC4J can switch code segments after the first
`input_reset_sense()` call without changing the function body:

```sh
python3 scripts/probes/probe_th04_demo_midfunction_segment.py \
  --output-dir .analysis/reconstruction/probes/v337-demo-midfunction-segment-001
```

The probe attests MAIN, the retained v214 session object, and the pinned TC4J
binary. `#pragma option -zCPAUSE_TAIL_TEXT` inside `pause()` is rejected with
an incorrect-directive diagnostic. `#pragma codeseg PAUSE_TAIL_TEXT main_01`
at the same position compiles, but all `0x11F` bytes remain in one
`PAUSE_HEAD_TEXT` LEDATA range and `PAUSE_TAIL_TEXT` receives no CODE.

Thus the source-level pragma mechanisms cannot produce the proposed
one/core/eleven FIXUPP partition inside this function. The historical object
producer remains unknown, and the unit stays blocked on ordered relocations.
Private receipt SHA-256:
`069ee4f7fc6ccbad0b6dc5f63b83eb299d5f31b49bac97c26df9a9c057c7b850`.
