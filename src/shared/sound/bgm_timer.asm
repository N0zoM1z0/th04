; TH04-local PC-98 beeper IRQ 8. The ISR owns no DOS calls or heap reads.
; BGM_TICK is a far Pascal function over resident DGROUP state.

    .8086
    .model use16 large SHARED

    .data
public _bgm_timer_divisor, bgm_timer_divisor
bgm_timer_divisor label word
_bgm_timer_divisor dw 2458
timer_hooked db 0
timer_old_mask db 0
timer_old_vect dd 0

    ; BGM_TICK belongs to the C++ SHARED segment, not the IRQ segment.
    .code SHARED
extrn BGM_TICK:far

    ; The installed CS:offset IRQ vector needs this segment's own base.
    .code TH04_BGM_TIMER_TEXT
public BGM_TIMER_START, BGM_TIMER_STOP

BGM_TIMER_START proc far
    pushf
    push ax
    push bx
    push dx
    push ds
    push es
    cmp timer_hooked, 0
    jne short start_done

    mov ax, 3508h
    int 21h
    mov word ptr timer_old_vect, bx
    mov word ptr timer_old_vect+2, es

    push ds
    push cs
    pop ds
    mov dx, offset bgm_irq
    mov ax, 2508h
    int 21h
    pop ds

    pushf
    cli
    in al, 2
    mov timer_old_mask, al
    mov al, 36h
    out 77h, al
    mov ax, _bgm_timer_divisor
    out 71h, al
    mov al, ah
    out 71h, al
    mov al, timer_old_mask
    and al, 0FEh
    out 2, al
    popf
    mov timer_hooked, 1
start_done:
    pop es
    pop ds
    pop dx
    pop bx
    pop ax
    popf
    retf
BGM_TIMER_START endp

BGM_TIMER_STOP proc far
    pushf
    push ax
    push dx
    push ds
    cmp timer_hooked, 0
    je short stop_done
    pushf
    cli
    in al, 2
    or al, 1
    out 2, al
    popf

    push ds
    mov dx, word ptr timer_old_vect
    mov ax, word ptr timer_old_vect+2
    mov ds, ax
    mov ax, 2508h
    int 21h
    pop ds

    pushf
    cli
    mov al, timer_old_mask
    out 2, al
    popf
    mov timer_hooked, 0
stop_done:
    pop ds
    pop dx
    pop ax
    popf
    retf
BGM_TIMER_STOP endp

bgm_irq proc far
    push ax
    push bx
    push cx
    push dx
    push si
    push di
    push bp
    push ds
    push es
    mov ax, seg _bgm_timer_divisor
    mov ds, ax
    mov ax, _bgm_timer_divisor
    out 71h, al
    mov al, ah
    out 71h, al
    cld
    ; TASM relaxes even CALL FAR PTR to PUSH CS / CALL rel16 here. TLINK
    ; resolved that group-relative fixup to a wrong SHARED offset in the full
    ; MAINE layout. Encode the ordinary 8086 far CALL with symbolic offset
    ; and segment fixups so TLINK retains the load-time segment relocation.
    db 09Ah
    dw offset BGM_TICK
    dw seg BGM_TICK
    mov al, 20h
    out 0, al
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
bgm_irq endp

end
