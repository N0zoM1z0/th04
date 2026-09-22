; Open or create the MASTER single file for append.
; Near Pascal ABI: one near filename pointer, callee removes two bytes.

.8086

extrn DOS_AXDX:near

_DATA segment word public 'DATA' use16
extrn file_Handle:word
extrn file_InReadBuf:word
extrn file_BufPtr:word
extrn file_Eof:word
extrn file_ErrorStat:word
extrn file_BufferPos:dword
_DATA ends
DGROUP group _DATA

_TEXT segment word public 'CODE' use16
assume cs:_TEXT, ds:DGROUP

public FILE_APPEND

FILENAME_OFF equ 4

FILE_APPEND proc near
    push bp
    mov bp, sp

    mov ax, 0
    mov bx, file_Handle
    cmp bx, -1
    jne short append_exit

    mov ax, 3D02h
    push ax
    push word ptr [bp+FILENAME_OFF]
    call DOS_AXDX
    or ax, dx
    mov file_Handle, ax
    mov cx, ax

    xor ax, ax
    mov file_InReadBuf, ax
    mov file_BufPtr, ax
    mov file_Eof, ax
    mov file_ErrorStat, ax
    mov word ptr file_BufferPos, ax
    mov word ptr file_BufferPos+2, ax

    inc dx
    jz short append_exit

    mov bx, cx
    xor cx, cx
    mov dx, cx
    mov ax, 4202h
    int 21h
    mov word ptr file_BufferPos, ax
    mov word ptr file_BufferPos+2, dx
    mov ax, 1

append_exit:
    pop bp
    ret 2
FILE_APPEND endp

_TEXT ends
end
