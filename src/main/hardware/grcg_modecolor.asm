; TH04/TH05 shared low-level GRCG mode and direct-color producer.
;
; Independent original-target comparison preserves this complete instruction
; sequence in both games. Legal TC4J source emits longer DX-based mode setters
; and a longer arithmetic color expansion; the exact immediate-port / carry
; expansion producer is therefore maintained as evidence-backed original-style
; symbolic assembly.

.386
.model use16 large _TEXT

GC_RMW = 0C0h
GC_TDW = 080h
GRCG_MODE_PORT = 07Ch
GRCG_TILE_PORT = 07Eh

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

public @grcg_setmode_rmw$qv
@grcg_setmode_rmw$qv proc near
    mov al, GC_RMW
    out GRCG_MODE_PORT, al
    ret
@grcg_setmode_rmw$qv endp
    even

public @grcg_setmode_tdw$qv
@grcg_setmode_tdw$qv proc near
    mov al, GC_TDW
    out GRCG_MODE_PORT, al
    ret
@grcg_setmode_tdw$qv endp
    even

public @grcg_setcolor_direct_raw$qv
@grcg_setcolor_direct_raw$qv proc near
    cli
    mov dx, GRCG_TILE_PORT
    rept 4
        shr ah, 1
        sbb al, al
        out dx, al
    endm
    sti
    ret
@grcg_setcolor_direct_raw$qv endp

CIRCLE_TEXT ends
end
