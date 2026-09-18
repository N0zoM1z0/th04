; Buffered or direct MS-DOS file read used by the TH04 ZUN resident program.
; Near Pascal ABI: far buffer pointer, byte count; callee removes six bytes.

.8086

_DATA segment word public 'DATA' use16
extrn file_BufferSize:word
extrn file_InReadBuf:word
extrn file_BufPtr:word
extrn file_BufferPos:dword
extrn file_Buffer:dword
extrn file_Handle:word
extrn file_Eof:word
_DATA ends
DGROUP group _DATA

_TEXT segment word public 'CODE' use16
assume cs:_TEXT, ds:DGROUP
public FILE_READ

BUF_PTR   equ 6
READ_SIZE equ 4

FILE_READ proc near
    push bp
    mov bp, sp
    push si
    push di

    cmp file_BufferSize, 0
    je short direct_read

    mov bx, [bp+READ_SIZE]
    les di, [bp+BUF_PTR]
read_loop:
    mov ax, file_InReadBuf
    cmp file_BufPtr, ax
    jb short buffer_has_data

    add word ptr file_BufferPos, ax
    adc word ptr file_BufferPos+2, 0

    push bx
    push ds
    mov cx, file_BufferSize
    mov bx, file_Handle
    lds dx, file_Buffer
    mov ah, 3Fh
    int 21h
    pop ds
    pop bx
    cmc
    sbb dx, dx
    and ax, dx
    mov file_InReadBuf, ax
    jz short eof

    mov file_BufPtr, 0
buffer_has_data:
    mov si, file_InReadBuf
    sub si, file_BufPtr
    sub si, bx
    sbb ax, ax
    and si, ax
    add si, bx
    mov ax, es
    or ax, di
    je short loop_end
    or si, si
    je short loop_end

    push si
    push ds
    mov cx, si
    mov ax, file_BufPtr
    lds si, file_Buffer
    add si, ax
    shr cx, 1
    rep movsw
    adc cx, cx
    rep movsb
    pop ds
    pop si
loop_end:
    add file_BufPtr, si
    sub bx, si
    jne short read_loop
    jmp short exit_loop

even
direct_read:
    push ds
    mov cx, [bp+READ_SIZE]
    mov bx, file_Handle
    lds dx, [bp+BUF_PTR]
    mov ah, 3Fh
    int 21h
    pop ds
    add word ptr file_BufferPos, ax
    adc word ptr file_BufferPos+2, 0
    mov bx, cx
    sub bx, ax
    je short exit_loop
eof:
    mov file_Eof, 1
exit_loop:
    mov ax, [bp+READ_SIZE]
    sub ax, bx
    pop di
    pop si
    pop bp
    ret 6
even
FILE_READ endp

_TEXT ends
end
