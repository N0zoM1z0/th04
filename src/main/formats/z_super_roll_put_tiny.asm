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

; The native product targets a 386+ emulator. Fixed-size, nonrolling sprites
; can draw all rows without per-row CALL/RET or loop bookkeeping. Each macro
; retains the original mask arithmetic and ordered byte/word VRAM writes.
; The historical producer does not emit these paths.
ifdef TH04_LARGE_PRODUCT
Z32_EVEN_NATIVE_ROW macro
    local word1_blank, word2_blank, carry_blank
    xor bl, bl
    lodsd
    ror ax, cl
    mov dh, al
    and al, dl
    xor dh, al
    or al, bl
    mov bl, dh
    or ax, ax
    jz short word1_blank
    mov es:[di], ax
word1_blank:
    add di, 2
    shr eax, 16
    ror ax, cl
    mov dh, al
    and al, dl
    xor dh, al
    or al, bl
    mov bl, dh
    or ax, ax
    jz short word2_blank
    mov es:[di], ax
word2_blank:
    add di, 2
    shr eax, 16
    or bl, bl
    jz short carry_blank
    mov es:[di], bl
carry_blank:
    add di, (ROW_SIZE - 4)
endm

Z32_ODD_NATIVE_ROW macro
    local first_blank, word1_blank, word2_blank
    lodsd
    ror al, cl
    mov bl, al
    and al, dl
    jz short first_blank
    mov es:[di], al
first_blank:
    xor bl, al
    inc di
    shr eax, 8
    ror ax, cl
    mov dh, al
    and al, dl
    xor dh, al
    or al, bl
    mov bl, dh
    or ax, ax
    jz short word1_blank
    mov es:[di], ax
word1_blank:
    add di, 2
    shr eax, 16
    ror ax, cl
    mov dh, al
    and al, dl
    xor dh, al
    or al, bl
    mov bl, dh
    or ax, ax
    jz short word2_blank
    mov es:[di], ax
word2_blank:
    add di, 2
    shr eax, 16
    add di, (ROW_SIZE - 5)
endm

Z16_EVEN_NATIVE_ROW macro
    local carry_blank
    lodsw
    ror ax, cl
    mov dh, al
    and al, dl
    mov es:[di], ax
    xor al, dh
    jz short carry_blank
    mov es:[di+2], al
carry_blank:
    add di, ROW_SIZE
endm

Z16_ODD_NATIVE_ROW macro
    lodsw
    ror ax, cl
    mov dh, al
    and al, dl
    mov es:[di], al
    xor al, dh
    xchg ah, al
    mov es:[di+1], ax
    add di, ROW_SIZE
endm
endif

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
ifdef TH04_LARGE_PRODUCT
    jnb short z32_even_roll
    jmp z32_even_native
z32_even_roll:
else
    jb short z32_even_yloop2
endif
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
ifdef TH04_LARGE_PRODUCT
    jnb short z32_odd_roll
    jmp z32_odd_native
z32_odd_roll:
else
    jb short z32_odd_yloop2
endif
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

ifdef TH04_LARGE_PRODUCT
z32_even_native:
    rept 32
        Z32_EVEN_NATIVE_ROW
    endm
    xor bh, bh
    xor ch, ch
    lodsw
    cmp al, 80h
    jne short z32_even_native_return
    jmp z32_even_color_loop
z32_even_native_return:
    MRETURN

z32_odd_native:
    rept 32
        Z32_ODD_NATIVE_ROW
    endm
    xor bh, bh
    xor ch, ch
    lodsw
    cmp al, 80h
    jne short z32_odd_native_return
    jmp z32_odd_color_loop
z32_odd_native_return:
    MRETURN
endif
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
ifdef TH04_LARGE_PRODUCT
    jnb short z16_even_roll
    jmp z16_even_native
z16_even_roll:
else
    jb short z16_even_yloop2
endif
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
ifdef TH04_LARGE_PRODUCT
    jnb short z16_odd_roll
    jmp z16_odd_native
z16_odd_roll:
else
    jb short z16_odd_yloop2
endif
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

ifdef TH04_LARGE_PRODUCT
z16_even_native:
    rept 16
        Z16_EVEN_NATIVE_ROW
    endm
    xor ch, ch
    lodsw
    cmp al, 80h
    jne short z16_even_native_return
    jmp z16_even_color_loop
z16_even_native_return:
    MRETURN

z16_odd_native:
    rept 16
        Z16_ODD_NATIVE_ROW
    endm
    xor ch, ch
    lodsw
    cmp al, 80h
    jne short z16_odd_native_return
    jmp z16_odd_color_loop
z16_odd_native_return:
    MRETURN
endif
Z_SUPER_ROLL_PUT_TINY_16X16_RAW endp

CIRCLE_TEXT ends
end
