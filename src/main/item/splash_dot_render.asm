; TH04/TH05 shared low-level item-splash dot renderer.
;
; The independently attested TH04 and TH05 targets contain the same complete
; 28-byte producer. Bounded legal TC4J probes preserve the semantics but do not
; reproduce its direct register allocation without inline assembly. This source
; records the evidence-backed original-style symbolic assembler owner.

.386
.model use16 large _TEXT

ROW_SIZE = 80
BYTE_MASK = 7
BYTE_BITS = 3

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01
public @item_splash_dot_render
@item_splash_dot_render proc near
    mov cx, ax
    sar ax, BYTE_BITS
    shl dx, 6
    add ax, dx
    shr dx, 2
    add ax, dx
    mov bx, ax
    mov al, 80h
    and cl, BYTE_MASK
    shr al, cl
    mov es:[bx], al
    retn
@item_splash_dot_render endp
CIRCLE_TEXT ends
end
