; Native planar rendering kernels. These are semantic product implementations,
; not original-target byte owners. Independent CS, no self-modifying operands.
.386
.model use16 large _TEXT

.data
extrn _VRAM_PLANE_B:dword, _VRAM_PLANE_R:dword
extrn _VRAM_PLANE_G:dword, _VRAM_PLANE_E:dword

TH04_PLANAR_BLIT_TEXT segment word public 'CODE' use16
assume cs:TH04_PLANAR_BLIT_TEXT

; Far Pascal copy_words(destination far*, source far*, word_count).
; Caller guarantees each complete interval fits within its segment.
public TH04_COPY_WORDS
TH04_COPY_WORDS proc far
    push bp
    mov bp, sp
    push ds
    push es
    push si
    push di
    pushf
    cld
    les di, ss:[bp+12]
    lds si, ss:[bp+8]
    mov cx, ss:[bp+6]
    mov dx, cx
    shr cx, 1
    rep movsd
    test dl, 1
    jz short copy_words_done
    movsw
copy_words_done:
    popf
    pop di
    pop si
    pop es
    pop ds
    pop bp
    retf 10
TH04_COPY_WORDS endp

; Far Pascal sprite_unclipped(left, top, packed_size, pattern_segment).
; C++ validates the slot, four plane pointers and full-screen enclosure.
; Width is 1..32 bytes, height 1..255. Alpha is followed by B/R/G/E planes.
; Locals: source_row=-2, destination_row=-4, plane_bytes=-6, width=-8,
; rows=-10, pixel_shift=-12, source_segment=-14, plane_index=-16,
; far plane pointers=-34..-19, one shifted alpha row=-68..-36.
public TH04_SPRITE_UNCLIPPED
TH04_SPRITE_UNCLIPPED proc far
    push bp
    mov bp, sp
    sub sp, 68
    push si
    push di
    push ds
    push es
    mov eax, _VRAM_PLANE_B
    mov ss:[bp-34], eax
    mov eax, _VRAM_PLANE_R
    mov ss:[bp-30], eax
    mov eax, _VRAM_PLANE_G
    mov ss:[bp-26], eax
    mov eax, _VRAM_PLANE_E
    mov ss:[bp-22], eax
    mov ax, ss:[bp+6]
    mov ss:[bp-14], ax
    mov ax, ss:[bp+8]
    mov dl, ah
    xor dh, dh
    mov ss:[bp-8], dx
    xor ah, ah
    mov ss:[bp-10], ax
    mul dx
    mov ss:[bp-6], ax
    mov word ptr ss:[bp-2], 0
    mov ax, ss:[bp+12]
    mov dx, ax
    and dx, 7
    mov ss:[bp-12], dx
    shr ax, 3
    imul dx, ss:[bp+10], 80
    add ax, dx
    mov ss:[bp-4], ax
    mov ds, ss:[bp-14]
    test byte ptr ss:[bp-8], 1
    jz sprite_word_row

sprite_row:
    mov si, ss:[bp-2]
    lea bx, [bp-68]
    mov cl, byte ptr ss:[bp-12]
    mov ch, byte ptr ss:[bp-8]
    xor dx, dx
sprite_alpha:
    mov al, [si]
    inc si
    mov ah, dl
    mov dl, al
    shr ax, cl
    mov ss:[bx], al
    or dh, al
    inc bx
    dec ch
    jnz short sprite_alpha
    test cl, cl
    jz short sprite_alpha_done
    xor al, al
    mov ah, dl
    shr ax, cl
    mov ss:[bx], al
    or dh, al
sprite_alpha_done:
    test dh, dh
    jz sprite_row_done
    mov word ptr ss:[bp-16], 0
    mov si, ss:[bp-2]
    add si, ss:[bp-6]

sprite_plane:
    lea bx, [bp-34]
    add bx, ss:[bp-16]
    les di, ss:[bx]
    add di, ss:[bp-4]
    lea bx, [bp-68]
    mov cl, byte ptr ss:[bp-12]
    mov ch, byte ptr ss:[bp-8]
    test cl, cl
    jz short sprite_color_begin
    inc ch
sprite_color_begin:
    xor dl, dl
sprite_color:
    ; Only the final unaligned carry has no current source byte. Reading
    ; the next row there would leak its leading bits into this sprite row.
    cmp ch, 1
    jne short sprite_color_read
    test cl, cl
    jz short sprite_color_read
    xor al, al
    jmp short sprite_color_compose
sprite_color_read:
    mov al, [si]
    inc si
sprite_color_compose:
    mov ah, dl
    mov dl, al
    mov dh, ss:[bx]
    test dh, dh
    jz short sprite_color_next
    shr ax, cl
    and al, dh
    cmp dh, 0FFh
    je short sprite_color_store
    not dh
    and dh, es:[di]
    or al, dh
sprite_color_store:
    mov es:[di], al
sprite_color_next:
    inc bx
    inc di
    dec ch
    jnz short sprite_color
    mov ax, ss:[bp-6]
    sub ax, ss:[bp-8]
    add si, ax
    add word ptr ss:[bp-16], 4
    cmp word ptr ss:[bp-16], 16
    jb sprite_plane
sprite_row_done:
    mov ax, ss:[bp-8]
    add ss:[bp-2], ax
    add word ptr ss:[bp-4], 80
    dec word ptr ss:[bp-10]
    jnz sprite_row
    jmp sprite_done

; Even widths combine two destination bytes at a time. Byte swapping makes
; the high-bit-first pixel order a big-endian word for SHRD; swapping back
; restores the little-endian VRAM word. DX carries the preceding source word.
sprite_word_row:
    mov si, ss:[bp-2]
    lea bx, [bp-68]
    mov cl, byte ptr ss:[bp-12]
    mov ch, byte ptr ss:[bp-8]
    shr ch, 1
    xor dx, dx
    mov word ptr ss:[bp-16], 0
sprite_word_alpha:
    mov ax, [si]
    add si, 2
    xchg al, ah
    mov ss:[bp-18], ax
    shrd ax, dx, cl
    mov dx, ss:[bp-18]
    xchg al, ah
    mov ss:[bx], ax
    or ss:[bp-16], ax
    add bx, 2
    dec ch
    jnz short sprite_word_alpha
    test cl, cl
    jz short sprite_word_alpha_done
    xor ax, ax
    shrd ax, dx, cl
    mov al, ah
    mov ss:[bx], al
    or byte ptr ss:[bp-16], al
sprite_word_alpha_done:
    cmp word ptr ss:[bp-16], 0
    je sprite_word_row_done
    mov word ptr ss:[bp-16], 0
    mov si, ss:[bp-2]
    add si, ss:[bp-6]

sprite_word_plane:
    lea bx, [bp-34]
    add bx, ss:[bp-16]
    les di, ss:[bx]
    add di, ss:[bp-4]
    lea bx, [bp-68]
    mov cl, byte ptr ss:[bp-12]
    mov ch, byte ptr ss:[bp-8]
    shr ch, 1
    xor dx, dx
sprite_word_color:
    mov ax, [si]
    add si, 2
    xchg al, ah
    mov ss:[bp-18], ax
    shrd ax, dx, cl
    mov dx, ss:[bp-18]
    xchg al, ah
    and ax, ss:[bx]
    ; Zero masks leave both destination bytes untouched. Other masks
    ; preserve background bits and replace only this sprite's coverage.
    cmp word ptr ss:[bx], 0
    je short sprite_word_color_next
    push dx
    mov dx, ss:[bx]
    cmp dx, 0FFFFh
    je short sprite_word_color_store
    not dx
    and dx, es:[di]
    or ax, dx
sprite_word_color_store:
    mov es:[di], ax
    pop dx
sprite_word_color_next:
    add bx, 2
    add di, 2
    dec ch
    jnz short sprite_word_color
    test cl, cl
    jz short sprite_word_plane_done
    xor ax, ax
    shrd ax, dx, cl
    mov al, ah
    mov ah, ss:[bx]
    test ah, ah
    jz short sprite_word_plane_done
    and al, ah
    cmp ah, 0FFh
    je short sprite_word_tail_store
    not ah
    and ah, es:[di]
    or al, ah
sprite_word_tail_store:
    ; The final carry is a byte, including at physical column 79.
    mov es:[di], al
sprite_word_plane_done:
    mov ax, ss:[bp-6]
    sub ax, ss:[bp-8]
    add si, ax
    add word ptr ss:[bp-16], 4
    cmp word ptr ss:[bp-16], 16
    jb sprite_word_plane
sprite_word_row_done:
    mov ax, ss:[bp-8]
    add ss:[bp-2], ax
    add word ptr ss:[bp-4], 80
    dec word ptr ss:[bp-10]
    jnz sprite_word_row

sprite_done:
    pop es
    pop ds
    pop di
    pop si
    mov sp, bp
    pop bp
    retf 8
TH04_SPRITE_UNCLIPPED endp
TH04_PLANAR_BLIT_TEXT ends
end
