# TH04 MAIN DEMO_TEXT FIXUPP order diagnostic (v214)

## Claim and evidence

The selected local MAIN.EXE remains `candidate-local-attested`, SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The active Ghidra database passed `python3 scripts/ghidra.py th04-main check`.
The reviewed `stage_session_init` physical TC86 producer is MAIN.EXE / DEMO_TEXT
`0AAF:03E0`, load `0xAED0..0xB3ED`, target file `0xC6D0..0xCBED`, 0x51E bytes.
Its source is `src/main/stage/session_init.cpp`. The four logical functions and
post-return switch table are recorded in the v165 boundary review and v166
ledger entries.

A fresh two-cold focused replay ran:

```sh
python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-demo-session-v166 \
  --run-id gptweb-v214-demo-fixupp-diagnostic-001
```

Receipt SHA-256 is
`d223b5abead753bb057972c390492a03c5520f88ade05c49d7ab63d501d078ae`.
A/B both pass complete raw bytes, MAP placement, OMF validity, deterministic
object and slice checks, auxiliary extents, and all 52 relocation *sites*.
Ordered relocation comparison alone fails: target orders load `0xB2DA` first;
candidate orders it last, with the other 51 sites retaining relative order.
Every target relocation in this physical extent is the segment word of a far
CALL (`9A` at site minus three). `0xB2DA` belongs to the far call of
`input_reset_sense()` in `pause()`.

The read-only OMF probe ran:

```sh
python3 scripts/probes/inspect_dialog_fixup_order.py \
  gptweb-v214-demo-fixupp-diagnostic-001 \
  --unit th04-main-demo-session-v166 \
  --segment DEMO_TEXT --object-path th04/sess.obj \
  > .analysis/reconstruction/v214-demo-fixup-order.json
```

Probe JSON SHA-256 is
`737673034169e88c3958e22f2a1680b1ffd638663cfeb43793b964b351f4e9c5`.
A/B `sess.obj` SHA-256 is
`3816b5f0aaabe5e8646243d22fbe13d40e97f53f012a398ae95ec76ae426f6ad`.
Each object has DEMO_TEXT LEDATA `0x000..0x3FF` followed by FIXUPP record 83,
and LEDATA `0x400..0x51D` followed by FIXUPP record 85. All 52 candidate
relocations map uniquely to FIXUPP LOCAT locations: 40 in record 83 and 12 in
record 85. In both builds, candidate FIXUPP order equals candidate linked MZ
order. `0xB2DA` is the last mapped LOCAT in record 85, at byte offset 154.
The candidate sequence rotates by 51 entries to equal the target sequence.

This localizes the **candidate** ordering before TLINK. The target object is
unavailable, so its FIXUPP record structure and why its MZ relocation order
starts with `0xB2DA` remain unknown. A compiler or object-history hypothesis
must predict the observed rotation while keeping all 0x51E linked bytes, MAP,
and relocation values unchanged. The prior v166 header/EXTDEF reorder, adjacent
TU fusion, and IDE compiler experiments did not. No exactness is promoted.

The later [v236 `-B`/TASM diagnostic](TH04_MAIN_B_MODE_V237.md) changes the
same v214 `sess.cpp` contribution from 1310 to 1306 bytes, failing the raw
extent gate before linking. Its modified generated ASM is diagnostic only.
