; TH04 large-model text_putca support.
;
; The pinned ReC98 masters.lib member is assembled for the small/near model
; and returns with RET 8.  MAIN declares TEXT_PUTCA as a far Pascal function,
; so keep the text-RAM algorithm local with the large-model RETF 8 ABI.  This
; is a maintained ABI owner, not a target-byte exactness claim.

    .8086
    .model use16 large SHARED
    .data
    extrn _TextVramSeg:word
    .code SHARED

public TEXT_PUTCA

TEXT_PUTCA proc far
    mov dx, bp
    mov bp, sp
    mov cx, di

    ; Far return address: atrb at [BP+4], chr at [BP+6],
    ; y at [BP+8], and x at [BP+10].
    mov ax, ss:[bp+8]
    mov di, ax
    shl ax, 1
    shl ax, 1
    add di, ax
    shl di, 1
    add di, _TextVramSeg
    mov es, di
    mov di, ss:[bp+10]
    shl di, 1

    mov ax, ss:[bp+6]
    mov bx, ss:[bp+4]

    mov bp, dx

    ; Convert a Shift-JIS lead/trail pair to the JIS cell when needed.
    ; ANK and right-half bytes use the original value directly.
    or ah, ah
    jz short text_putca_ank_or_right
    cmp ah, 080h
    jb short text_putca_jis
text_putca_kanji:
    shl ah, 1
    cmp al, 09Fh
    jnb short text_putca_kanji_skip
    cmp al, 080h
    adc ax, 0FEDFh
text_putca_kanji_skip:
    sbb ax, 0DFFEh
    and ax, 07F7Fh

text_putca_jis:
    xchg ah, al
    sub al, 020h
    mov es:[di+2000h], bx
    stosw
    or al, 080h

text_putca_ank_or_right:
    mov es:[di+2000h], bx
    stosw

    mov di, cx
    retf 8
TEXT_PUTCA endp

end
