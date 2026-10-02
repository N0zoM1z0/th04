; TH04 PAR DOS file hook. The interrupt frame is owned by this ASM unit;
; PF_DISPATCH in pf_archive.cpp handles only the game's virtual read handle.

    .8086
    .model use16 large SHARED

extrn _bbufsiz:word

    .code SHARED
extrn PF_DISPATCH:far

    ; Keep the DOS vector and CS-resident hook state outside C++ code groups.
    .code TH04_PF_INT21_TEXT
public PF_HOOK_INSTALL, PF_HOOK_REMOVE

PF_HOOK_INSTALL proc far
    push bx
    push dx
    push ds
    push es
    cmp word ptr cs:pf_old_vector+2, 0
    jne short hook_installed

    mov ax, 3521h
    int 21h
    mov word ptr cs:pf_old_vector, bx
    mov word ptr cs:pf_old_vector+2, es

    push cs
    pop ds
    mov dx, offset pf_int21
    mov ax, 2521h
    int 21h
hook_installed:
    mov ax, 1
    pop es
    pop ds
    pop dx
    pop bx
    retf
PF_HOOK_INSTALL endp

PF_HOOK_REMOVE proc far
    push ax
    push dx
    push ds
    cmp word ptr cs:pf_old_vector+2, 0
    je short hook_removed

    mov dx, word ptr cs:pf_old_vector
    mov ax, word ptr cs:pf_old_vector+2
    mov ds, ax
    mov ax, 2521h
    int 21h
    mov word ptr cs:pf_old_vector, 0
    mov word ptr cs:pf_old_vector+2, 0
    mov byte ptr cs:pf_busy, 0
hook_removed:
    pop ds
    pop dx
    pop ax
    retf
PF_HOOK_REMOVE endp

pf_int21 proc far
    cmp byte ptr cs:pf_busy, 0
    jne pf_chain
    cmp ah, 4Ch
    je pf_terminate

    ; SS:BP points to a 24-byte PfFrame, followed by IP, CS, FLAGS.
    ; Offsets: ES 0, DS 2, BP 4, DI 6, SI 8, DX 10, CX 12,
    ; BX 14, AX 16, IP 18, CS 20, FLAGS 22.
    push ax
    push bx
    push cx
    push dx
    push si
    push di
    push bp
    push ds
    push es
    mov bp, sp

    mov ax, seg _bbufsiz
    mov ds, ax
    inc byte ptr cs:pf_busy
    push word ptr [bp+22]
    popf
    push ss
    push bp
    call PF_DISPATCH
    or ax, ax
    jz short pf_forward

    dec byte ptr cs:pf_busy
    pop es
    pop ds
    pop bp
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    iret

pf_forward:
    dec byte ptr cs:pf_busy
    push word ptr [bp+22]
    popf
    pop es
    pop ds
    pop bp
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    cli
pf_chain:
    jmp dword ptr cs:pf_old_vector

pf_terminate:
    ; DOS may retain INT 21h after the process exits. Restore its vector
    ; before forwarding AH=4Ch so it never points into released game memory.
    push ax
    push dx
    push ds
    mov byte ptr cs:pf_busy, 1
    mov dx, word ptr cs:pf_old_vector
    mov ax, word ptr cs:pf_old_vector+2
    mov ds, ax
    mov ax, 2521h
    int 21h
    pop ds
    pop dx
    pop ax
    mov byte ptr cs:pf_busy, 0
    jmp dword ptr cs:pf_old_vector
pf_int21 endp

pf_old_vector dw 0, 0
pf_busy db 0

end
