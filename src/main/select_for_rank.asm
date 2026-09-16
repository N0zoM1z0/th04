; Return the rank-selected value from four Pascal far arguments.
;
; TH04 and TH05 preserve this exact stack-indexing skeleton. In TH05 the entry
; additionally shares its tail with the preceding playchar selector, while a
; legal TC4J parameter-pointer implementation emits a framed 29-byte function.

.386
.model use16 large _TEXT

extrn _rank:byte

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

public SELECT_FOR_RANK
SELECT_FOR_RANK proc far
    mov al, _rank
    xor ah, ah
    add ax, ax
    mov bx, 0Ah
    sub bx, ax
    add bx, sp
    mov ax, ss:[bx]
    retf 8
SELECT_FOR_RANK endp

CIRCLE_TEXT ends
end
