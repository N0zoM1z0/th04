; ZUNINIT STOP/COPY interrupt UI. Register ABI and INT 18h interaction are
; reconstructed from the reviewed target control flow and shared-game lineage.
; The two FAR entry points return with IRET; their shared modal is NEAR.

.8086

_TEXT segment byte public 'CODE' use16
assume cs:_TEXT
org 100h

extrn ZUNINIT_MAIN:near
extrn ZUNINIT_BUSY:byte
extrn ZUNINIT_TEXT_PUT:near
extrn ZUNINIT_STOP_LINE1:byte
extrn ZUNINIT_STOP_LINE2:byte
extrn ZUNINIT_STOP_LINE3:byte
extrn ZUNINIT_COPY_LINE1:byte
extrn ZUNINIT_COPY_LINE2:byte
extrn ZUNINIT_COPY_LINE3:byte
extrn ZUNINIT_CLEAR_LINE:byte

public ZUNINIT_START
public ZUNINIT_STOP_HANDLER
public ZUNINIT_COPY_HANDLER
public ZUNINIT_MODAL

ZUNINIT_START proc near
    jmp ZUNINIT_MAIN
ZUNINIT_START endp

ZUNINIT_STOP_HANDLER proc far
    cmp cs:ZUNINIT_BUSY, 0
    jnz short stop_done
    mov cs:ZUNINIT_BUSY, 1
    call ZUNINIT_MODAL
stop_done:
    iret
ZUNINIT_STOP_HANDLER endp

ZUNINIT_COPY_HANDLER proc far
    cmp cs:ZUNINIT_BUSY, 0
    jnz short copy_done
    mov cs:ZUNINIT_BUSY, 2
    call ZUNINIT_MODAL
copy_done:
    iret
ZUNINIT_COPY_HANDLER endp

ZUNINIT_MODAL proc near
    pushf
    push ax
    push bx
    push cx
    push dx
    push ds
    push di
    push es
    mov ah, 41h
    int 18h
    cmp cs:ZUNINIT_BUSY, 2
    jz short show_copy

    mov ax, 650h
    mov dx, offset ZUNINIT_STOP_LINE1
    call ZUNINIT_TEXT_PUT
    mov ax, 6F0h
    mov dx, offset ZUNINIT_STOP_LINE2
    call ZUNINIT_TEXT_PUT
    mov ax, 790h
    mov dx, offset ZUNINIT_STOP_LINE3
    call ZUNINIT_TEXT_PUT
    mov bl, 1
    jmp short wait_release

show_copy:
    mov ax, 650h
    mov dx, offset ZUNINIT_COPY_LINE1
    call ZUNINIT_TEXT_PUT
    mov ax, 6F0h
    mov dx, offset ZUNINIT_COPY_LINE2
    call ZUNINIT_TEXT_PUT
    mov ax, 790h
    mov dx, offset ZUNINIT_COPY_LINE3
    call ZUNINIT_TEXT_PUT
    mov bl, 2

wait_release:
    mov ah, 4
    mov al, 0Ch
    int 18h
    test ah, bl
    jnz short wait_release

wait_press:
    mov ah, 4
    mov al, 0Ch
    int 18h
    test ah, bl
    jz short wait_press
    mov ah, 40h
    int 18h

    mov ax, 650h
    mov dx, offset ZUNINIT_CLEAR_LINE
    call ZUNINIT_TEXT_PUT
    mov ax, 6F0h
    mov dx, offset ZUNINIT_CLEAR_LINE
    call ZUNINIT_TEXT_PUT
    mov ax, 790h
    mov dx, offset ZUNINIT_CLEAR_LINE
    call ZUNINIT_TEXT_PUT
    mov ah, 6
    int 18h
    pop es
    pop di
    pop ds
    pop dx
    pop cx
    pop bx
    pop ax
    popf
    mov cs:ZUNINIT_BUSY, 0
    ret
ZUNINIT_MODAL endp

_TEXT ends
end ZUNINIT_START
