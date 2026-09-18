; MS-DOS resident-data search and allocation for the TH04 ZUN program.
; The three near Pascal arguments are ID offset, ID length, and paragraph size.
; This is the tiny-model form of Koizuka's historical master-library routine:
; the identifier is in DS, and the callee removes all three arguments.

.8086

_DATA segment word public 'DATA' use16
RESDATA_ResPalID db 'pal98 grb', 0
_DATA ends
DGROUP group _DATA

_TEXT segment word public 'CODE' use16
assume cs:_TEXT, ds:DGROUP
public RESDATA_EXIST, RESDATA_CREATE

MCB_FLAG  equ 0
MCB_OWNER equ 1
MCB_SIZE  equ 3
ID_STR    equ 8
ID_LEN    equ 6
PARASIZE  equ 4

RESDATA_EXIST proc near
    push bp
    mov bp, sp
    push si
    push di

    mov ah, 52h
    int 21h
    cld
    mov bx, es:[bx-2]
find_mcb:
    mov es, bx
    inc bx
    mov ax, es:[MCB_OWNER]
    or ax, ax
    je short skip_mcb
    mov ax, es:[MCB_SIZE]
    cmp ax, [bp+PARASIZE]
    jne short skip_mcb
    mov cx, [bp+ID_LEN]
    mov si, [bp+ID_STR]
    mov di, 10h
    repe cmpsb
    je short found_mcb
skip_mcb:
    mov ax, es:[MCB_SIZE]
    add bx, ax
    mov al, es:[MCB_FLAG]
    cmp al, 'M'
    je short find_mcb
    mov bx, 0
found_mcb:
    mov ax, bx

    pop di
    pop si
    pop bp
    ret 6
RESDATA_EXIST endp

even

RESDATA_CREATE proc near
    push bp
    mov bp, sp
    push si
    push di

    push word ptr [bp+ID_STR]
    push word ptr [bp+ID_LEN]
    push word ptr [bp+PARASIZE]
    call near ptr RESDATA_EXIST
    or ax, ax
    jnz short already_present

    mov ax, 5800h
    int 21h
    mov dx, ax

    mov ax, 5801h
    mov bx, 1
    int 21h
    mov ah, 48h
    mov bx, [bp+PARASIZE]
    int 21h
    mov cx, 0
    jc short allocation_failed
    mov bx, cs
    cmp bx, ax
    jnb short allocated

    mov es, ax
    mov ah, 49h
    int 21h
    mov ax, 5801h
    mov bx, 2
    int 21h
    mov ah, 48h
    mov bx, [bp+PARASIZE]
    int 21h
allocated:
    mov cx, ax
    push ax
    dec cx
    mov es, cx
    mov ax, -1
    mov es:[MCB_OWNER], ax
    inc cx
    mov es, cx
    xor di, di
    mov cx, [bp+ID_LEN]
    mov si, [bp+ID_STR]
    rep movsb
    pop cx

allocation_failed:
    mov ax, 5801h
    mov bx, dx
    int 21h
    mov ax, cx

already_present:
    pop di
    pop si
    pop bp
    ret 6
RESDATA_CREATE endp

even
_TEXT ends
end
