; Register/flags adapters for the original SMEM Pascal ABI.
; Typed allocation policy lives in heap.cpp. DX:AX is its ordinary long result;
; these adapters publish carry and preserve the registers required by callers.

    .8086
    .model use16 large _TEXT

; Keep externals outside the caller segment so TASM emits far fixups.
extrn TH04_SMEM_WGET_CORE:far, TH04_SMEM_RELEASE_CORE:far

TH04_SMEM_ABI_TEXT segment word public 'CODE' use16
assume cs:TH04_SMEM_ABI_TEXT
public SMEM_WGET, SMEM_RELEASE

SMEM_WGET proc far
    push bp
    mov bp, sp
    push bx
    push cx
    push dx
    push si
    push di
    push ds
    push es
    push word ptr ss:[bp+6]
    call far ptr TH04_SMEM_WGET_CORE
    cmp dx, 0
    pop es
    pop ds
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop bp
    jne smem_get_failed
    clc
    retf 2
smem_get_failed:
    stc
    retf 2
SMEM_WGET endp

SMEM_RELEASE proc far
    pushf
    push bp
    mov bp, sp
    push ax
    push bx
    push cx
    push dx
    push si
    push di
    push ds
    push es
    push word ptr ss:[bp+8]
    call far ptr TH04_SMEM_RELEASE_CORE
    pop es
    pop ds
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    pop bp
    popf
    retf 2
SMEM_RELEASE endp

TH04_SMEM_ABI_TEXT ends
end
