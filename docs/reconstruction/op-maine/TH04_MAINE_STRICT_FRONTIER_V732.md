# MAINE strict-source frontier after v730-v732

The live MAINE ledger is 63/72 exact with all 72 authored-function physical
boundaries reviewed. Nine functions remain source/codegen/provenance blockers.

This note records three new compiler-mechanism probes that do not change exact
counts, but close previously untested routes.

## v730 regist_menu local optimizer surface

regist_menu remains 920/924 under ordinary C++. The target four-byte frontier
is the zero test at function offsets 0x345/0x346/0x348/0x349:

- target: direct-memory CMP against zero, followed by JZ and a redundant JMP;
- best ordinary switch: MOV AX,[key_det] / OR AX,AX, followed by the target
  double-jump topology.

A new current-producer probe tested local pragma option -O- / restore around
only this branch. Direct if/goto forms do make TC86 choose the target direct
memory CMP, but the optimizer/layout result drops the redundant jump and shifts
later branches. Keeping switch topology under local -O- returns to the same
four-byte MOV/OR frontier. Boolean-switch variants over-expand by 6-16 bytes.

Private results:
.analysis/reconstruction/probes/v730-regist-local-optimizer-surface-001/results.json

SHA-256:
a884d20a78c04c7ba0a73421535a912894abe82857305c158b2d245906142850

No exact credit is granted.

## v731 snd_se_update index-lowering surface

The natural _snd_se_update candidate is 77 bytes against the reviewed
76-byte target. The known difference is byte-array indexing:

- natural TC86: load snd_se_playing through AL/AH, then move AX to BX;
- target: load BL directly and clear BH.

New tests covered direct indexing, pointer arithmetic, int casts, local
unsigned-char/unsigned-int temporaries, register temporaries, and a union word
construction.

Direct/pointer/cast forms all reproduce the same 77-byte natural candidate.
Local/register/union forms grow to 79-89 bytes. Only the previously known
explicit BL/BH register helper reaches target shape, and that remains diagnostic
rather than acceptable authored-source evidence.

Private results:
.analysis/reconstruction/probes/v731-se-update-index-surface-002/results.json

SHA-256:
5d2062ec71acc37d0782caed5ee8f7d3bd6f2379fbeb4d93a2500c8215b003e1

No exact credit is granted.

## v732 EGC / box optimizer surface

The maintained natural forms of egc_start_copy and box_1_to_0_masked remain
blocked by TC86 word-port write lowering:

- ordinary outport loads DX=port before AX=value;
- the targets load AX=value before DX=port;
- ordinary zero writes select XOR AX,AX where relevant.

New production-profile probes tested source-level optimizer/register-allocation
settings without changing source semantics:

- -O-;
- -O- -y;
- -Z-;
- combined -O- -Z-.

For egc_start_copy, all tested settings preserve the same 51-byte natural
candidate; none changes DX-before-AX or XOR-zero lowering. For
box_1_to_0_masked, -O- and -O- -y preserve the same 134-byte candidate,
while -Z- variants grow it to 137 bytes. The historical outport2 helper is
still explicit decompilation inline assembly and receives no source credit.

Private results:
.analysis/reconstruction/probes/v732-egc-box-optimizer-surface-001/results.json

SHA-256:
d9e51f7d519a85e57a4f1552db92b946c31d4ce5a7cc25502f59a7d62ddf34de

No exact credit is granted.

## Current MAINE frontier

The remaining nine reviewed/nonexact functions are:

- egc_start_copy, 52 bytes;
- box_1_to_0_masked, 134 bytes;
- scoredat_decode / scoredat_encode, 88 / 101 bytes;
- regist_menu, 924 bytes;
- SCORE EGC-start, 67 bytes;
- SND_LOAD, 234 bytes;
- SND_SE_PLAY, 57 bytes;
- _snd_se_update, 76 bytes.

The new v730-v732 probes do not justify relaxing the source-admissibility bar.
Further MAINE progress requires a materially new compiler mechanism or
independent provenance, not another spelling matrix.
