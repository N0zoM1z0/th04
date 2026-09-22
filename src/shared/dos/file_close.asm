; Flush and close helpers for the MASTER single-file state.
; Both functions use near no-argument ABIs.

.8086

_DATA segment word public 'DATA' use16
extrn file_Handle:word
extrn file_BufPtr:word
extrn file_InReadBuf:word
extrn file_Buffer:dword
extrn file_BufferPos:dword
extrn file_ErrorStat:word
_DATA ends
DGROUP group _DATA

_TEXT segment word public 'CODE' use16
assume cs:_TEXT, ds:DGROUP

public FILE_FLUSH, FILE_CLOSE

FILE_FLUSH proc near
    mov bx, file_Handle
    cmp bx, -1
    je short flush_ignore

    mov ax, file_BufPtr
    cmp file_InReadBuf, ax
    jae short flush_read

    push ds
    mov cx, file_BufPtr
    lds dx, file_Buffer
    mov ah, 40h
    int 21h
    pop ds
    jc short flush_error
    add word ptr file_BufferPos, ax
    adc word ptr file_BufferPos+2, 0
    cmp file_BufPtr, ax
    je short write_done

flush_error:
    mov file_ErrorStat, 1

write_done:
    mov file_BufPtr, 0
    ret

flush_read:
    cmp file_InReadBuf, 0
    je short flush_ignore

    mov dx, ax
    mov cx, 0
    add dx, word ptr file_BufferPos
    mov file_InReadBuf, cx
    mov file_BufPtr, cx
    adc cx, word ptr file_BufferPos+2
    mov ax, 4200h
    mov bx, file_Handle
    int 21h

    mov word ptr file_BufferPos, ax
    mov word ptr file_BufferPos+2, dx

flush_ignore:
    ret
FILE_FLUSH endp

even

FILE_CLOSE proc near
    call FILE_FLUSH
    mov ah, 3Eh
    int 21h
    mov file_Handle, -1
    ret
FILE_CLOSE endp

_TEXT ends
end
