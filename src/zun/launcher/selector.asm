; ZUN.COM embedded-program selector. The builder appends the fixed-size
; directory after this stub, then the four COM components and mover tail.

.8086
.model tiny
.code
org 100h

start:
    jmp short dispatch

saved_name_offset dw 0
missing_program db 'No COM-Soft !!!', 13, 10, 10, '$'

dispatch:
    cld
    mov cx, word ptr program_count
    or cx, cx
    jz short print_missing
    mov si, 80h
    lodsb
    or al, al
    jz short list_programs

skip_leading_space:
    lodsb
    cmp al, 13
    jz short list_programs
    cmp al, 32
    jz short skip_leading_space
    jmp short find_program

list_programs:
    mov cx, word ptr program_count
    mov si, offset program_names
    mov dl, 13
    mov ah, 2
    int 21h
    mov dl, 10
    int 21h
next_program_name:
    push cx
    mov dl, 32
    int 21h
    mov cx, 8
next_name_character:
    lodsb
    mov dl, al
    int 21h
    loop next_name_character
    mov dl, 32
    int 21h
    pop cx
    loop next_program_name
    mov dl, 13
    int 21h
    mov dl, 10
    int 21h
    mov ah, 4Ch
    int 21h

find_program:
    mov bx, offset program_entries
    mov cx, word ptr program_count
    mov si, offset program_names
compare_name:
    mov word ptr saved_name_offset, si
    mov di, 5Dh
    push cx
    mov cx, 8
    repe cmpsb
    jz short prepare_program
    add bx, 2
    mov si, word ptr saved_name_offset
    add si, 8
    pop cx
    loop compare_name

print_missing:
    mov dx, offset missing_program
    mov ah, 9
    int 21h
    mov ah, 4Ch
    int 21h

prepare_program:
    mov di, 5Ch
    mov si, 6Ch
    mov cx, 10h
    rep movsb
    mov si, 80h
    lodsb
    mov dl, al
skip_selected_name_space:
    lodsb
    dec dl
    cmp al, 32
    jz short skip_selected_name_space
skip_selected_name:
    lodsb
    dec dl
    cmp al, 13
    jz short copy_remaining_args
    cmp al, 32
    jnz short skip_selected_name
copy_remaining_args:
    inc dl
    mov di, 80h
    mov al, dl
    stosb
    or dl, dl
    jz short end_args
    dec si
    mov cl, dl
    xor ch, ch
    rep movsb
end_args:
    mov byte ptr [di], 13
    mov ax, [bx]
    mov cx, [bx+2]
    mov si, ax
    sub cx, ax
    mov di, 100h
    jmp mover_call

; These ORGs reserve the directory supplied by the ZUN composite builder.
; They do not emit file bytes in the standalone 223-byte selector stub.
program_count:
    org $+2
program_names:
    org $+8*32
program_entries:
    org $+2*33
mover_call:
    org $+3

end start
