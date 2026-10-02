; TH04 PC-98 VSync interrupt ownership. Public entries are far Pascal.
; A single code-resident INT 18h tail retriggers VSync after CRT BIOS calls.

    .8086
    .model use16 large SHARED

    .data
public _vsync_Count1, _vsync_Count2, _vsync_Proc
_vsync_Count1       dw 0
_vsync_Count2       dw 0
_vsync_Proc         dd 0
vsync_delay         dw 0
vsync_delay_count   dw 0
vsync_old_mask      db 0
vsync_old_vect      dd 0

    ; CS-relative vector offsets and the saved BIOS pointer must share the
    ; entry's segment base. SHARED can be folded into a larger C++ code group.
    .code TH04_VSYNC_TEXT
public VSYNC_START, VSYNC_END

VSYNC_START proc far
    pushf
    push ax
    push bx
    push cx
    push dx
    push ds
    push es

    xor ax, ax
    mov _vsync_Count1, ax
    mov _vsync_Count2, ax
    mov vsync_delay_count, ax
    mov vsync_delay, ax

    ; PC-9821 GDC extension reports 31 kHz in AL bits 2-3.
    mov es, ax
    test byte ptr es:[045Ch], 40h
    jz short mode_done
    mov ah, 31h
    int 18h
    and al, 0Ch
    cmp al, 0Ch
    jne short mode_done
    mov vsync_delay, 13311
mode_done:
    cmp vsync_old_mask, 0
    jne start_done

    mov ax, 350Ah
    int 21h
    mov word ptr vsync_old_vect, bx
    mov word ptr vsync_old_vect+2, es

    push ds
    push cs
    pop ds
    mov dx, offset vsync_irq
    mov ax, 250Ah
    int 21h
    pop ds

    pushf
    cli
    in al, 2
    mov ah, al
    and al, 0FBh
    out 2, al
    popf
    or ah, 0FBh
    mov vsync_old_mask, ah

    mov ax, 3518h
    int 21h
    mov word ptr cs:crt_old_vect, bx
    mov word ptr cs:crt_old_vect+2, es

    push ds
    push cs
    pop ds
    mov dx, offset crt_bios_return
    mov ax, 2518h
    int 21h
    pop ds

    xor al, al
    out 64h, al
start_done:
    pop es
    pop ds
    pop dx
    pop cx
    pop bx
    pop ax
    popf
    retf
VSYNC_START endp

crt_bios_return proc far
    pushf
    call dword ptr cs:crt_old_vect
    out 64h, al
    iret
crt_bios_return endp

crt_old_vect dw 0, 0

vsync_irq proc far
    push ax
    push ds
    mov ax, seg _vsync_Count1
    mov ds, ax

    mov ax, vsync_delay
    add vsync_delay_count, ax
    jc short irq_done
    inc _vsync_Count1
    inc _vsync_Count2

    cmp word ptr _vsync_Proc+2, 0
    je short irq_done
    push bx
    push cx
    push dx
    push si
    push di
    push es
    cld
    call dword ptr _vsync_Proc
    pop es
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    cli
irq_done:
    pop ds
    mov al, 20h
    out 0, al
    out 64h, al
    pop ax
    iret
vsync_irq endp

VSYNC_END proc far
    pushf
    push ax
    push bx
    push dx
    push ds
    push es
    cmp vsync_old_mask, 0
    je end_done

    push ds
    mov dx, word ptr cs:crt_old_vect
    mov ax, word ptr cs:crt_old_vect+2
    mov ds, ax
    mov ax, 2518h
    int 21h
    pop ds

    pushf
    cli
    in al, 2
    or al, 4
    out 2, al
    popf

    push ds
    mov dx, word ptr vsync_old_vect
    mov ax, word ptr vsync_old_vect+2
    mov ds, ax
    mov ax, 250Ah
    int 21h
    pop ds

    pushf
    cli
    in al, 2
    and al, vsync_old_mask
    out 2, al
    popf
    xor al, al
    out 64h, al
    mov vsync_old_mask, al
end_done:
    pop es
    pop ds
    pop dx
    pop bx
    pop ax
    popf
    retf
VSYNC_END endp

end
