; Print one near NUL-terminated string to DOS standard output.
; Convert LF to CR/LF and preserve SI.
; Near Pascal ABI: one near pointer argument, callee removes two bytes.

.8086

_DATA segment word public 'DATA' use16
_DATA ends
DGROUP group _DATA

_TEXT segment word public 'CODE' use16
assume cs:_TEXT, ds:DGROUP

public DOS_PUTS2

STRING_OFF equ 2

DOS_PUTS2 proc near
    mov bx, sp
    mov cx, si
    mov si, ss:[bx+STRING_OFF]
    lodsb
    or al, al
    jz short puts_done
    mov ah, 2

puts_loop:
    cmp al, 0Ah
    jne short puts_char
    mov dl, 0Dh
    int 21h
    mov al, 0Ah

puts_char:
    mov dl, al
    int 21h
    lodsb
    or al, al
    jne short puts_loop

puts_done:
    mov si, cx
    ret 2
DOS_PUTS2 endp

even
_TEXT ends
end
