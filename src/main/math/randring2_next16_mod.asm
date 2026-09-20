; TH04 MAIN_032_TEXT randring2 modulo producer.
;
; This is the second instance of the same cross-game RANDRING_NEXT_DEF family.
; The trailing zero byte is the explicit layout byte immediately following the
; macro invocation in the TH04 source and is outside the 25-byte function credit.

.8086
.model use16 large _TEXT

extrn _randring:byte
extrn _randring_p:word

MAIN_032_TEXT segment word public 'CODE' use16
MAIN_032_TEXT ends
main_03 group MAIN_032_TEXT

MAIN_032_TEXT segment word public 'CODE' use16
assume cs:main_03

public @RANDRING2_NEXT16_MOD$QUI
@randring2_next16_mod$qui proc near
	mov	bx, _randring_p
	mov	ax, word ptr _randring[bx]
	inc	byte ptr _randring_p
	xor	dx, dx
	mov	bx, sp
	div	word ptr ss:[bx+2]
	mov	ax, dx
	retn	2
@randring2_next16_mod$qui endp
	db	0

MAIN_032_TEXT ends
end
