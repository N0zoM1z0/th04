; TH04 gather-point sprite blit. The shifted and byte-aligned loops copy the
; eight-row sprite from DS into the active PC-98 VRAM plane in ES. The source
; and destination wrap independently at the bottom of the 400-row playfield.
;
; The EVEN before the shifted loop aligns its entry in B4M_UPDATE_TEXT. This
; produces the target's single alignment NOP, not an arbitrary filler byte.

.386
.model use16 large _TEXT

ROW_SIZE = 80
RES_Y = 400
PLANE_SIZE = (ROW_SIZE * RES_Y)
PELLET_H = 8
BYTE_MASK = 7

extrn _sPELLET:byte

B4M_UPDATE_TEXT segment word public 'CODE' use16
B4M_UPDATE_TEXT ends
main_03 group B4M_UPDATE_TEXT

B4M_UPDATE_TEXT segment word public 'CODE' use16
assume cs:main_03

public @gather_point_render$qii
@gather_point_render$qii proc near
    push si
    push di
    mov si, ax
    mov bx, dx
    sar ax, 3
    shl dx, 6
    add ax, dx
    shr dx, 2
    add ax, dx
    mov di, ax
    and si, BYTE_MASK
    mov ax, si
    shl si, 4
    add si, offset _sPELLET
    mov cx, PELLET_H
    cmp bx, (RES_Y - PELLET_H)
    ja short roll_needed
    xor dx, dx
    jmp short check_alignment

roll_needed:
    mov dx, cx
    mov cx, RES_Y
    sub cx, bx
    sub dx, cx

check_alignment:
    or ax, ax
    jz short bytealigned_loop
    even

shifted_loop:
    movsw
    add di, (ROW_SIZE - 2)
    loop shifted_loop

check_roll:
    or dx, dx
    jz short done
    sub di, PLANE_SIZE
    xchg cx, dx
    jmp short shifted_loop

bytealigned_loop:
    movsb
    add di, (ROW_SIZE - 1)
    inc si
    loop bytealigned_loop
    jmp short check_roll

done:
    pop di
    pop si
    retn
@gather_point_render$qii endp

B4M_UPDATE_TEXT ends
end
