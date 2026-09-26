; ZUNINIT COM command loop, interrupt installation/removal, and DOS exit.
; The process starts with CS=DS=PSP and keeps its first 0x30C bytes resident.

.8086

_TEXT segment byte public 'CODE' use16
assume cs:_TEXT

extrn ZUNINIT_RESIDENT_CHECK:near
extrn ZUNINIT_STOP_HANDLER:far
extrn ZUNINIT_COPY_HANDLER:far
extrn ZUNINIT_VECTOR_SLOT_1:dword
extrn ZUNINIT_VECTOR_SLOT_2:dword
extrn ZUNINIT_MSG_INSTALLED:byte
extrn ZUNINIT_MSG_UNINSTALLED:byte
extrn ZUNINIT_MSG_NOT_INSTALLED:byte
extrn ZUNINIT_MSG_BAD_OPTION:byte
extrn ZUNINIT_MSG_FREE_ERROR:byte
extrn ZUNINIT_MSG_RESIDENT_SIZE:byte

public ZUNINIT_MAIN

ZUNINIT_MAIN proc near
    mov si, 81h

scan_command:
    lodsb
    cmp al, 0Dh
    jz short check_resident
    cmp al, '/'
    jz short parse_option
    cmp al, '-'
    jz short parse_option
    cmp al, ' '
    jbe short scan_command

check_resident:
    call ZUNINIT_RESIDENT_CHECK
    test ax, ax
    jz short install
    jmp already_installed

parse_option:
    lodsb
    cmp al, ' '
    ja short parse_remove
    jmp bad_option

parse_remove:
    and al, 0DFh
    cmp al, 'R'
    jz short check_remove
    jmp bad_option

check_remove:
    call ZUNINIT_RESIDENT_CHECK
    test ax, ax
    jnz short uninstall
    jmp not_installed

install:
    mov ah, 35h
    mov al, 6
    int 21h
    mov word ptr cs:ZUNINIT_VECTOR_SLOT_2, bx
    mov word ptr cs:ZUNINIT_VECTOR_SLOT_2+2, es
    mov dx, offset ZUNINIT_STOP_HANDLER
    mov ax, 2506h
    int 21h
    mov ah, 35h
    mov al, 5
    int 21h
    mov word ptr cs:ZUNINIT_VECTOR_SLOT_1, bx
    mov word ptr cs:ZUNINIT_VECTOR_SLOT_1+2, es
    mov dx, offset ZUNINIT_COPY_HANDLER
    mov ax, 2505h
    int 21h
    mov dx, offset ZUNINIT_MSG_RESIDENT_SIZE
    mov ah, 9
    int 21h
    mov dx, offset ZUNINIT_RESIDENT_CHECK
    mov cl, 4
    shr dx, cl
    inc dx
    mov ax, 3100h
    int 21h

uninstall:
    push ds
    mov dx, word ptr es:ZUNINIT_VECTOR_SLOT_2
    mov ds, word ptr es:ZUNINIT_VECTOR_SLOT_2+2
    mov ax, 2506h
    int 21h
    mov dx, word ptr es:ZUNINIT_VECTOR_SLOT_1
    mov ds, word ptr es:ZUNINIT_VECTOR_SLOT_1+2
    mov ax, 2505h
    int 21h
    pop ds
    push es
    mov es, word ptr es:2Ch
    mov ah, 49h
    int 21h
    pop es
    mov ah, 49h
    int 21h
    mov dx, offset ZUNINIT_MSG_UNINSTALLED
    jnc short print_remove_result
    mov dx, offset ZUNINIT_MSG_FREE_ERROR

print_remove_result:
    mov ah, 9
    int 21h
    jmp short exit

already_installed:
    mov dx, offset ZUNINIT_MSG_INSTALLED
    mov ah, 9
    int 21h
    jmp short exit

not_installed:
    mov dx, offset ZUNINIT_MSG_NOT_INSTALLED
    mov ah, 9
    int 21h
    jmp short exit

bad_option:
    mov dx, offset ZUNINIT_MSG_BAD_OPTION
    mov ah, 9
    int 21h
    jmp short exit

exit:
    mov ax, 4C00h
    int 21h
ZUNINIT_MAIN endp

_TEXT ends
end
