; Copy the selected embedded COM down to PSP:0100 and return to it.

.8086
.model tiny
.code
org 100h

start:
    rep movsb
    pop ax
    mov ax, 100h
    push ax
    ret

end start
