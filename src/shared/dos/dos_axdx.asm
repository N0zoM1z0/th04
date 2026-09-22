; Invoke one MS-DOS function with AX and a near DS:DX string pointer.
; Near Pascal ABI: string offset followed by AX value; callee removes four bytes.
; Returns absolute AX on error with DX=-1, or AX with DX=0 on success.

.8086

_DATA segment word public 'DATA' use16
_DATA ends
DGROUP group _DATA

_TEXT segment word public 'CODE' use16
assume cs:_TEXT, ds:DGROUP
public DOS_AXDX

STRING_OFF equ 4
AX_VALUE   equ 6

DOS_AXDX proc near
    push bp
    mov bp, sp
    mov dx, [bp+STRING_OFF]
    mov ax, [bp+AX_VALUE]
    int 21h
    sbb dx, dx
    xor ax, dx
    sub ax, dx
    pop bp
    ret 4
DOS_AXDX endp

even
_TEXT ends
end
