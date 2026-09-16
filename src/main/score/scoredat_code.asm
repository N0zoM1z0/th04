; GENSOU.SCR score-section decoder and encoder for TH04 MAIN.EXE.
;
; The target uses LOOP-driven register pipelines for both byte transforms and
; checksum passes. A legal typed TC4J implementation expands to framed
; 121/136-byte functions instead of the two 63-byte target bodies. TH05 retains
; the same ROR/XOR/LOOP architecture with its game-specific score structure.

.386
.model use16 large _TEXT

extrn IRAND:far

SCOREDAT_KEY1 = 0
SCOREDAT_KEY2 = 1
SCOREDAT_SUM = 2
SCOREDAT_SCORE = 4
SCOREDAT_SIZE = 0C0h

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

public @SCOREDAT_DECODE$QP18SCOREDAT_SECTION_T
@SCOREDAT_DECODE$QP18SCOREDAT_SECTION_T proc near
    mov bx, sp
    push si
    mov bx, ss:[bx+2]
    mov si, bx
    mov cx, SCOREDAT_SIZE - 1
    mov ah, [bx+SCOREDAT_KEY2]
    add bx, SCOREDAT_SCORE
decode_loop:
    mov al, [bx+1]
    ror al, 3
    xor al, ah
    add al, [si+SCOREDAT_KEY1]
    add [bx], al
    inc bx
    loop decode_loop
    mov al, [si+SCOREDAT_KEY1]
    add [bx], al
    xor bx, bx
    mov cx, SCOREDAT_SIZE
    xor dx, dx
    mov ax, [si+SCOREDAT_SUM]
    add si, SCOREDAT_SCORE
decode_sum:
    mov bl, [si]
    add dx, bx
    inc si
    loop decode_sum
    sub ax, dx
    pop si
    ret 2
@SCOREDAT_DECODE$QP18SCOREDAT_SECTION_T endp
    even

public @SCOREDAT_ENCODE$QP18SCOREDAT_SECTION_T
@SCOREDAT_ENCODE$QP18SCOREDAT_SECTION_T proc near
    mov bx, sp
    push si
    mov bx, ss:[bx+2]
    mov si, bx
    xor dx, dx
    xor ax, ax
    add bx, SCOREDAT_SCORE
    mov cx, SCOREDAT_SIZE
encode_sum:
    mov dl, [bx]
    add ax, dx
    inc bx
    loop encode_sum
    mov [si+SCOREDAT_SUM], ax
    call IRAND
    mov word ptr [si+SCOREDAT_KEY1], ax
    xor dx, dx
    add si, SCOREDAT_SCORE + SCOREDAT_SIZE - 1
    mov cx, SCOREDAT_SIZE
encode_loop:
    add dl, al
    sub [si], dl
    mov dl, [si]
    ror dl, 3
    xor dl, ah
    dec si
    loop encode_loop
    pop si
    ret 2
@SCOREDAT_ENCODE$QP18SCOREDAT_SECTION_T endp
    even

CIRCLE_TEXT ends
end
