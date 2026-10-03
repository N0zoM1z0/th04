; TH04-local PC-98 joystick interface. The OP/MAIN/MAINE input producers
; already consume these public names. This is a product semantic owner, not
; an exact byte claim. YM2203 register 7 enables joystick input; register 14
; reads the active-low first controller on the PC-98 sound-board ports.

    .8086
    .model use16 large SHARED

; Register selectors and status masks describe the existing I/O protocol.
YM2203_ADDRESS_PORT = 188h
YM2203_DATA_PORT_DELTA = 2
YM2203_BUSY = 80h
YM2203_IO_DIRECTION_REGISTER = 7
YM2203_JOYSTICK_DATA_REGISTER = 0Eh
YM2203_JOYSTICK_SELECT_REGISTER = 0Fh
FIRST_JOYSTICK_SELECT = 80h
JOYSTICK_ACTION_BITS = 003Fh
BOARD_DETECTION_ATTEMPTS = 256

    .data
public js_bexist, _js_bexist, js_stat, _js_stat
js_bexist label word
_js_bexist dw 0
js_stat label word
_js_stat dw 0, 0

    .code SHARED
public JS_START, JS_END, JS_SENSE

JS_START proc far
    push bx
    push cx
    push dx
    ; Probe absent-board FFh at most 256 times. Presence is latched until
    ; the next start; JS_END only flushes DOS keyboard input.
    mov cx, BOARD_DETECTION_ATTEMPTS
    mov dx, YM2203_ADDRESS_PORT
detect_board:
    in al, dx
    inc al
    jnz board_present
    loop detect_board
    xor ax, ax
    jmp short start_done

board_present:
    pushf
    cli
    mov bh, YM2203_IO_DIRECTION_REGISTER
    call ym2203_read_register
    and al, 3Fh               ; preserve mixer enables, clear port A direction
    or al, 80h                ; select input direction for port B
    mov bl, al
    call ym2203_write_register
    popf
    mov ax, 1
start_done:
    mov js_bexist, ax
    pop dx
    pop cx
    pop bx
    retf
JS_START endp

JS_END proc far
    mov ax, 0C00h             ; DOS flush keyboard buffer, no input read
    int 21h
    retf
JS_END endp

; Return the fresh active-low controller sample in AX. The caller ORs it
; into key_det; this entry neither checks js_bexist nor writes js_stat.
JS_SENSE proc far
    push bx
    push dx
    pushf
    cli
    mov bh, YM2203_JOYSTICK_SELECT_REGISTER
    mov bl, FIRST_JOYSTICK_SELECT
    call ym2203_write_register
    mov dx, YM2203_ADDRESS_PORT
    mov al, YM2203_JOYSTICK_DATA_REGISTER
    out dx, al
    add dx, YM2203_DATA_PORT_DELTA
    in al, dx
    not al                   ; active-low buttons and directions
    and ax, JOYSTICK_ACTION_BITS
    popf
    pop dx
    pop bx
    retf
JS_SENSE endp

; YM2203's busy flag is status port 188h bit 7.
ym2203_wait_ready proc near
    mov dx, YM2203_ADDRESS_PORT
ready_loop:
    in al, dx
    test al, YM2203_BUSY
    jnz ready_loop
    ret
ym2203_wait_ready endp

ym2203_write_register proc near
    call ym2203_wait_ready
    mov al, bh
    out dx, al
    call ym2203_wait_ready
    add dx, YM2203_DATA_PORT_DELTA
    mov al, bl
    out dx, al
    ret
ym2203_write_register endp

ym2203_read_register proc near
    call ym2203_wait_ready
    mov al, bh
    out dx, al
    call ym2203_wait_ready
    add dx, YM2203_DATA_PORT_DELTA
    in al, dx
    ret
ym2203_read_register endp

end
