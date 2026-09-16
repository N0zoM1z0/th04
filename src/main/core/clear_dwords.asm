; Shared TH04 state-clear helper.
;
; The target uses a register ABI around REP STOSD that legal TC4J source does
; not reproduce. TH05 preserves the same helper with only the zeroing register
; widened to EAX, supporting an original-style assembly producer.

.386
.model use16 large _TEXT

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

public CLEAR_DWORDS
CLEAR_DWORDS proc near
    mov bx, sp
    push di
    mov di, ss:[bx+4]
    mov cx, ss:[bx+2]
    push ds
    pop es
    xor ax, ax
    rep stosd
    pop di
    ret 4
CLEAR_DWORDS endp

CIRCLE_TEXT ends
end
