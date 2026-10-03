; TH04 PC-98 VSync interrupt ownership. Public entries are far Pascal.
; A single code-resident INT 18h tail retriggers VSync after CRT BIOS calls.

    .8086
    .model use16 large SHARED

PIC_COMMAND_PORT = 0
PIC_MASK_PORT = 2
PIC_END_OF_INTERRUPT = 20h
VSYNC_IRQ_MASK = 4
VSYNC_IRQ_OTHER_MASK_BITS = 0FBh
VSYNC_REARM_PORT = 64h
DOS_GET_VSYNC_VECTOR = 350Ah
DOS_SET_VSYNC_VECTOR = 250Ah
DOS_GET_CRT_VECTOR = 3518h
DOS_SET_CRT_VECTOR = 2518h
PC9821_FEATURE_BITMAP = 045Ch
PC9821_EXTENDED_GDC = 40h
CRT_QUERY_GDC_MODE = 31h
GDC_31KHZ_BITS = 0Ch
GDC_31KHZ_SKIP_INCREMENT = 13311

    .data
public _vsync_Count1, _vsync_Count2, _vsync_Proc
_vsync_Count1       dw 0
_vsync_Count2       dw 0
_vsync_Proc         dd 0
cadence_skip_increment     dw 0
cadence_skip_accumulator   dw 0
saved_irq_mask_merge       db 0
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

    ; Even an already installed start resets counters and cadence phase.
    ; Hook ownership is decided later, using the nonzero mask sentinel.
    xor ax, ax
    mov _vsync_Count1, ax
    mov _vsync_Count2, ax
    mov cadence_skip_accumulator, ax
    mov cadence_skip_increment, ax

    ; PC-9821 GDC extension reports 31 kHz in AL bits 2-3.
    mov es, ax
    test byte ptr es:[PC9821_FEATURE_BITMAP], PC9821_EXTENDED_GDC
    jz short mode_done
    mov ah, CRT_QUERY_GDC_MODE
    int 18h
    and al, GDC_31KHZ_BITS
    cmp al, GDC_31KHZ_BITS
    jne short mode_done
    mov cadence_skip_increment, GDC_31KHZ_SKIP_INCREMENT
mode_done:
    cmp saved_irq_mask_merge, 0
    jne start_done

    mov ax, DOS_GET_VSYNC_VECTOR
    int 21h
    mov word ptr vsync_old_vect, bx
    mov word ptr vsync_old_vect+2, es

    push ds
    push cs
    pop ds
    mov dx, offset vsync_irq
    mov ax, DOS_SET_VSYNC_VECTOR
    int 21h
    pop ds

    pushf
    cli
    in al, PIC_MASK_PORT
    mov ah, al
    and al, VSYNC_IRQ_OTHER_MASK_BITS
    out PIC_MASK_PORT, al
    popf
    ; Save only the original IRQ mask bit. Ones elsewhere preserve the
    ; current other bits when END merges with AND; nonzero also owns hooks.
    or ah, VSYNC_IRQ_OTHER_MASK_BITS
    mov saved_irq_mask_merge, ah

    mov ax, DOS_GET_CRT_VECTOR
    int 21h
    mov word ptr cs:crt_old_vect, bx
    mov word ptr cs:crt_old_vect+2, es

    push ds
    push cs
    pop ds
    mov dx, offset crt_bios_return
    mov ax, DOS_SET_CRT_VECTOR
    int 21h
    pop ds

    xor al, al
    out VSYNC_REARM_PORT, al
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
    out VSYNC_REARM_PORT, al
    iret
crt_bios_return endp

crt_old_vect dw 0, 0

vsync_irq proc far
    push ax
    push ds
    mov ax, seg _vsync_Count1
    mov ds, ax

    ; Unsigned 16-bit fractional cadence: an addition carry skips both
    ; logical counters and the callback, but still acknowledges/rearms IRQ.
    mov ax, cadence_skip_increment
    add cadence_skip_accumulator, ax
    jc short irq_done
    ; Count1 is reset by frame_delay; Count2 continues until VSYNC_START.
    inc _vsync_Count1
    inc _vsync_Count2

    ; A zero segment disables the callback, regardless of its offset.
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
    mov al, PIC_END_OF_INTERRUPT
    out PIC_COMMAND_PORT, al
    out VSYNC_REARM_PORT, al
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
    cmp saved_irq_mask_merge, 0
    je end_done

    push ds
    mov dx, word ptr cs:crt_old_vect
    mov ax, word ptr cs:crt_old_vect+2
    mov ds, ax
    mov ax, DOS_SET_CRT_VECTOR
    int 21h
    pop ds

    pushf
    cli
    in al, PIC_MASK_PORT
    or al, VSYNC_IRQ_MASK
    out PIC_MASK_PORT, al
    popf

    push ds
    mov dx, word ptr vsync_old_vect
    mov ax, word ptr vsync_old_vect+2
    mov ds, ax
    mov ax, DOS_SET_VSYNC_VECTOR
    int 21h
    pop ds

    pushf
    cli
    in al, PIC_MASK_PORT
    and al, saved_irq_mask_merge
    out PIC_MASK_PORT, al
    popf
    xor al, al
    out VSYNC_REARM_PORT, al
    mov saved_irq_mask_merge, al
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
