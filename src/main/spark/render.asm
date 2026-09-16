; TH04/TH05 shared low-level spark sprite renderer.
;
; Independent original-target comparison preserves this complete producer
; architecture across TH04 and TH05; only the linked sSPARKS address differs.
; Legal TC4J source probes do not emit the target LODSW/LOOP producer from
; ordinary typed pointer/loop C++. This is therefore maintained as an
; evidence-backed original-style symbolic assembler owner.

.386
.model use16 large _TEXT

RES_Y = 400
ROW_SIZE = 80
PLANE_SIZE = 32000
SPARK_H = 8
SPARK_CELS = 8

extrn _sSPARKS:word

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01
public @spark_render
@spark_render proc near
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
    and si, 7
    mov ax, si
    shl si, 7
    add si, offset _sSPARKS
    and cx, (SPARK_CELS - 1)
    shl cx, 4
    add si, cx

    cmp bx, (RES_Y - SPARK_H)
    ja short roll_needed
    mov cx, SPARK_H
    xor bx, bx
    jmp short blit_loop

roll_needed:
    mov cx, RES_Y
    sub cx, bx
    mov bx, SPARK_H
    sub bx, cx
    even

blit_loop:
    lodsw
    or ah, ah
    jz short blit_al
    mov es:[di], ax
    jmp short next_row
blit_al:
    or al, al
    jz short next_row
    mov es:[di], al
next_row:
    add di, ROW_SIZE
    loop blit_loop
    or bx, bx
    jz short done
    sub di, PLANE_SIZE
    xchg cx, bx
    jmp short blit_loop
done:
    pop di
    pop si
    retn
@spark_render endp
    even
CIRCLE_TEXT ends
end
