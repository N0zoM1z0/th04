; Standalone symbolic producer probe for the TH04 rolling tiny-sprite blitters.
.386
.model use16 large _TEXT

SCREEN_HEIGHT = 400
ROW_SIZE = 80
PLANE_SIZE = 32000
GC_TILEREG = 07Eh

extrn super_patdata:word

MRETURN macro
    pop di
    pop si
    pop ds
    ret 2
    even
endm

GRCG_SETCOLOR_DIRECT macro reg
    rept 4
        shr reg, 1
        sbb al, al
        out GC_TILEREG, al
    endm
endm

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

srpt32x32_vram_topleft dw 0

public Z_SUPER_ROLL_PUT_TINY_32X32_RAW
Z_SUPER_ROLL_PUT_TINY_32X32_RAW proc near
    mov bx, sp
    push ds
    push si
    push di
    mov bx, ss:[bx+2]
    shl bx, 1
    mov ds, super_patdata[bx]
    mov bx, dx
    shl bx, 2
    add bx, dx
    shl bx, 4
    mov cx, ax
    and cx, 7
    shr ax, 3
    add bx, ax
    mov cs:srpt32x32_vram_topleft, bx
    xor si, si

    lodsw
    cmp al, 80h
    jnz short z32_return
    mov dl, 0ffh
    shr dl, cl
    test bl, 1
    jnz short z32_odd_color_loop

z32_even_color_loop:
    call z32_grcg_setcolor
    mov ch, 32
    mov di, cs:srpt32x32_vram_topleft
    cmp di, (SCREEN_HEIGHT - 32 + 1) * ROW_SIZE
    jb short z32_even_yloop2
z32_even_yloop1:
    call z32_put_even
    cmp di, PLANE_SIZE
    jb short z32_even_yloop1
    sub di, PLANE_SIZE
    even
z32_even_yloop2:
    call z32_put_even
    jnz short z32_even_yloop2
    lodsw
    cmp al, 80h
    jz short z32_even_color_loop
z32_return:
    MRETURN

z32_odd_color_loop:
    call z32_grcg_setcolor
    mov ch, 32
    mov di, cs:srpt32x32_vram_topleft
    cmp di, (SCREEN_HEIGHT - 32 + 1) * ROW_SIZE
    jb short z32_odd_yloop2
z32_odd_yloop1:
    call z32_put_odd
    cmp di, PLANE_SIZE
    jb short z32_odd_yloop1
    sub di, PLANE_SIZE
    nop
z32_odd_yloop2:
    call z32_put_odd
    jnz short z32_odd_yloop2
    lodsw
    cmp al, 80h
    jz short z32_odd_color_loop
    MRETURN

z32_grcg_setcolor:
    GRCG_SETCOLOR_DIRECT ah
    ret
    even

z32_put_even:
    xor bl, bl
    mov bh, 2
    lodsd
z32_even_word_loop:
    ror ax, cl
    mov dh, al
    and al, dl
    xor dh, al
    or al, bl
    mov bl, dh
    or ax, ax
    jz short z32_even_skip_blank_word
    mov es:[di], ax
z32_even_skip_blank_word:
    add di, 2
    shr eax, 16
    dec bh
    jnz short z32_even_word_loop
    or bl, bl
    jz short z32_even_skip_blank_5th
    mov es:[di], bl
z32_even_skip_blank_5th:
    add di, (ROW_SIZE - 4)
    dec ch
    ret
    even

z32_put_odd:
    mov bh, 2
    lodsd
    ror al, cl
    mov bl, al
    and al, dl
    jz short z32_odd_skip_blank_1st
    mov es:[di], al
z32_odd_skip_blank_1st:
    xor bl, al
    inc di
    shr eax, 8
z32_odd_word_loop:
    ror ax, cl
    mov dh, al
    and al, dl
    xor dh, al
    or al, bl
    mov bl, dh
    or ax, ax
    jz short z32_odd_skip_blank_word
    mov es:[di], ax
z32_odd_skip_blank_word:
    add di, 2
    shr eax, 16
    dec bh
    jnz short z32_odd_word_loop
    add di, (ROW_SIZE - 5)
    dec ch
    ret
Z_SUPER_ROLL_PUT_TINY_32X32_RAW endp

public Z_SUPER_ROLL_PUT_TINY_16X16_RAW
Z_SUPER_ROLL_PUT_TINY_16X16_RAW proc near
    even
    mov bx, sp
    push ds
    push si
    push di
    mov bx, ss:[bx+2]
    shl bx, 1
    mov ds, super_patdata[bx]
    mov bx, dx
    shl bx, 2
    add bx, dx
    shl bx, 4
    mov cx, ax
    and cx, 7
    shr ax, 3
    add bx, ax
    xor si, si
    lodsw
    cmp al, 80h
    jnz short z16_return
    mov dl, 0ffh
    shr dl, cl
    test bl, 1
    jnz short z16_odd_color_loop
    even
z16_even_color_loop:
    GRCG_SETCOLOR_DIRECT ah
    mov ch, 16
    mov di, bx
    cmp di, (SCREEN_HEIGHT - 16 + 1) * ROW_SIZE
    jb short z16_even_yloop2
    even
z16_even_yloop1:
    lodsw
    ror ax, cl
    mov dh, al
    and al, dl
    mov es:[di], ax
    xor al, dh
    jz short z16_even_yloop1_skip_blank_3rd
    mov es:[di+2], al
z16_even_yloop1_skip_blank_3rd:
    add di, ROW_SIZE
    dec ch
    cmp di, PLANE_SIZE
    jb short z16_even_yloop1
    sub di, PLANE_SIZE
    even
z16_even_yloop2:
    lodsw
    ror ax, cl
    mov dh, al
    and al, dl
    mov es:[di], ax
    xor al, dh
    jz short z16_even_yloop2_skip_blank_3rd
    mov es:[di+2], al
z16_even_yloop2_skip_blank_3rd:
    add di, ROW_SIZE
    dec ch
    jnz short z16_even_yloop2
    lodsw
    cmp al, 80h
    je short z16_even_color_loop
z16_return:
    MRETURN

z16_odd_color_loop:
    GRCG_SETCOLOR_DIRECT ah
    mov ch, 16
    mov di, bx
    cmp di, (SCREEN_HEIGHT - 16 + 1) * ROW_SIZE
    jb short z16_odd_yloop2
    even
z16_odd_yloop1:
    lodsw
    ror ax, cl
    mov dh, al
    and al, dl
    mov es:[di], al
    xor al, dh
    xchg ah, al
    mov es:[di+1], ax
    add di, ROW_SIZE
    dec ch
    cmp di, PLANE_SIZE
    jb short z16_odd_yloop1
    sub di, PLANE_SIZE
    even
z16_odd_yloop2:
    lodsw
    ror ax, cl
    mov dh, al
    and al, dl
    mov es:[di], al
    xor al, dh
    xchg ah, al
    mov es:[di+1], ax
    add di, ROW_SIZE
    dec ch
    jnz short z16_odd_yloop2
    lodsw
    cmp al, 80h
    je short z16_odd_color_loop
    MRETURN
Z_SUPER_ROLL_PUT_TINY_16X16_RAW endp

CIRCLE_TEXT ends
end
