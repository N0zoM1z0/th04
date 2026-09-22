; Write bytes through the MASTER single-file buffer or directly through DOS.
; Near Pascal ABI: far buffer pointer and byte count; callee removes six bytes.

.8086

_DATA segment word public 'DATA' use16
extrn file_BufferSize:word
extrn file_BufPtr:word
extrn file_Buffer:dword
extrn file_Handle:word
extrn file_BufferPos:dword
extrn file_ErrorStat:word
_DATA ends
DGROUP group _DATA

_TEXT segment word public 'CODE' use16
assume cs:_TEXT, ds:DGROUP

public FILE_WRITE

WRITE_SIZE equ 4
BUF_OFF    equ 6
BUF_SEG    equ 8

FILE_WRITE proc near
    push bp
    mov bp, sp
    push si
    push di

    cmp file_BufferSize, 0
    je short direct_write

    mov bx, [bp+WRITE_SIZE]
    mov si, [bp+BUF_OFF]

write_loop:
    mov cx, file_BufferSize
    sub cx, file_BufPtr
    sub cx, bx
    sbb ax, ax
    and cx, ax
    add cx, bx

    les di, file_Buffer
    add di, file_BufPtr
    sub bx, cx
    add file_BufPtr, cx

    push ds
    mov ds, [bp+BUF_SEG]
    shr cx, 1
    rep movsw
    adc cx, cx
    rep movsb
    pop ds

    or ax, ax
    jns short loop_end

    push ds
    push bx
    mov cx, file_BufferSize
    mov bx, file_Handle
    lds dx, file_Buffer
    mov ah, 40h
    int 21h
    pop bx
    pop ds
    jc short write_error
    cmp file_BufferSize, ax
    jne short write_error

    mov file_BufPtr, 0
    add word ptr file_BufferPos, ax
    adc word ptr file_BufferPos+2, 0

loop_end:
    or bx, bx
    jne short write_loop

    mov ax, 1
    jmp short write_done

even
direct_write:
    push ds
    mov cx, [bp+WRITE_SIZE]
    mov bx, file_Handle
    lds dx, [bp+BUF_OFF]
    mov ah, 40h
    int 21h
    pop ds
    jnc short write_exit

write_error:
    mov file_ErrorStat, 1
    xor ax, ax

write_exit:
    add word ptr file_BufferPos, ax
    adc word ptr file_BufferPos+2, 0
    add ax, -1
    sbb ax, ax

write_done:
    pop di
    pop si
    mov sp, bp
    pop bp
    ret 6

even
FILE_WRITE endp
_TEXT ends
end
