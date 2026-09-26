; Return largest free DOS memory block size in paragraphs.
; AH=48h with BX=FFFFh intentionally fails with AX=8 and returns BX.

.8086

_DATA segment word public 'DATA' use16
_DATA ends
DGROUP group _DATA

_TEXT segment word public 'CODE' use16
assume cs:_TEXT, ds:DGROUP

public DOS_MAXFREE

DOS_MAXFREE proc near
    mov ah, 48h
    mov bx, 0FFFFh
    int 21h
    cmp ax, 8
    jne short maxfree_error
    mov ax, bx
    clc
    ret
maxfree_error:
    xor ax, ax
    stc
    ret
DOS_MAXFREE endp

_TEXT ends
end
