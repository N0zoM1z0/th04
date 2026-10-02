; Independent real-mode DIV-zero fixture for the private emulator observer.
; Its own handler restores INT 0 and exits; it is never installed in game media.
bits 16
org 100h

    push cs
    pop ds
    mov ax,3500h
    int 21h
    mov [old_ip],bx
    mov [old_cs],es
    mov dx,fault_handler
    mov ax,2500h
    int 21h
    xor dx,dx
    mov ax,1
    xor bx,bx
    div bx
    mov ax,4c01h
    int 21h

fault_handler:
    mov dx,[cs:old_ip]
    mov ds,[cs:old_cs]
    mov ax,2500h
    int 21h
    mov ax,4c00h
    int 21h

old_ip dw 0
old_cs dw 0
