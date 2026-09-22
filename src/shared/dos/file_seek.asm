; Seek and tell helpers for the MASTER single-file state.
; FILE_SEEK uses the near Pascal ABI: long offset + word origin, RET 6.
; FILE_TELL returns the logical position in DX:AX.

.8086

extrn FILE_FLUSH:near

_DATA segment word public 'DATA' use16
extrn file_BufPtr:word
extrn file_BufferPos:dword
extrn file_Eof:word
_DATA ends
DGROUP group _DATA

_TEXT segment word public 'CODE' use16
assume cs:_TEXT, ds:DGROUP

public FILE_SEEK, FILE_TELL

SEEK_DIR    equ 4
SEEK_POS_LO equ 6
SEEK_POS_HI equ 8

FILE_SEEK proc near
    call FILE_FLUSH
    cmp bx, -1
    je short seek_error

    push bp
    mov bp, sp

    mov al, [bp+SEEK_DIR]
    mov ah, 42h
    mov dx, [bp+SEEK_POS_LO]
    mov cx, [bp+SEEK_POS_HI]
    int 21h
    pop bp

    mov ax, 4201h
    mov dx, 0
    mov cx, dx
    int 21h
    mov file_Eof, 0
    mov word ptr file_BufferPos, ax
    mov word ptr file_BufferPos+2, dx

seek_error:
    ret 6
FILE_SEEK endp

even

FILE_TELL proc near
    mov ax, file_BufPtr
    xor dx, dx
    add ax, word ptr file_BufferPos
    adc dx, word ptr file_BufferPos+2
    ret
FILE_TELL endp

_TEXT ends
end
