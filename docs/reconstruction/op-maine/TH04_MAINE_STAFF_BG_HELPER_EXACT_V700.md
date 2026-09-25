# MAINE staff background expansion helper exact replay (v700)

## Scope

The target owner at payload 0xB25B is a contiguous 0x36-byte (54-byte) near
Pascal function at loaded 1A05:120B. Ghidra reports three callers and one
callee. Its maintained reconstruction label is
staffroll_bgimage_expand_put(int,int,int,int,int); this does not claim recovery
of an original ZUN symbol spelling.

## Natural-C++ recovery

A plain C++ half-distance expression produced 52 bytes. Rewriting the local in
the natural form

    register int half = distance;
    half /= 2;

causes TC86 to emit the target's MOV SI,[BP+4] / MOV AX,SI sequence and yields
the complete target 54-byte body, with only the normal far-call fixup unresolved
at standalone-object time.

Maintained source:
src/maine/end/staff_bgimage_expand_put.inl

Focused replay:
scripts/probes/replay_th04_maine_staff_bgimage_expand_put.py

The focused replay substitutes only this helper into the pinned final
staffall.cpp translation unit, recompiles the complete staffall.obj, and relinks
MAINE twice. Both rounds preserve all 2231 bytes of the enclosing MAINE_01_TEXT
producer, the full MAINE program image, and all 559 ordered relocations.

Function SHA-256:
378435b972c228aa4a986cea65a0f2f33277c50b8e35df06d0565c740e0cda55

Focused receipt SHA-256:
ca3a787e181e3d86847fd3dcc48ae50298ca2b38d7b56b943653e9725a2df3ce

## Aggregate gate

The pre-registration 48-slice MAINE aggregate passes 48/48 raw-zero.

Receipt:
.analysis/reconstruction/probes/v701-maine-staff-bg-helper-aggregate-preaccept-001/receipt.json

Receipt SHA-256:
7b64317f5016795c3049cc8359d2184c1c6b463f8a90f49fc584023200d288d7

The exact claim is strictly function-scoped. The same staffall producer contains
three earlier dissolve helpers that still use pseudo-register forcing for GRCG
shutdown; they do not receive exact-source credit from this result.
