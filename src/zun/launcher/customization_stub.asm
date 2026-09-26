; Outer ZUN.COM help display and in-place inner COM relocation.
; The COMCSTM header at PSP:0103 supplies usage start/size and program size.

.8086
.model tiny
.code
org 100h

start:
    cmp byte ptr ds:80h, 0
    jz short relocate_inner
    mov ax, word ptr ds:82h
    cmp ax, 3F2Dh
    jz short print_usage
    cmp ax, 0D3Fh
    jnz short relocate_inner

print_usage:
    mov bx, 1
    mov dx, word ptr ds:103h
    mov cx, word ptr ds:105h
    mov ah, 40h
    int 21h
    mov ax, 4C00h
    int 21h

relocate_inner:
    mov di, 100h
    push di
    mov si, word ptr ds:103h
    add si, word ptr ds:105h
    mov cx, word ptr ds:107h
    inc cx
    shr cx, 1
    rep movsw
    mov ax, cx
    mov si, ax
    mov di, ax
    ret

end start
