; TH04 MAIN_033_TEXT point-number decimal digit producer.
;
; ReC98 commit c6b17b0c reverse-engineered this low-level producer together
; with the independent TH05 variant. Both targets preserve the same stack-fed
; repeated DIV/LOOP digit extraction architecture.
;
; The trailing NOP is the source-owned post-ENDP layout byte. It is outside the
; 37-byte logical function credit.

.8086
.model use16 large _TEXT

POINTNUM_DIGITS equ 4
extrn _FIVE_DIGIT_POWERS_OF_10:word

MAIN_033_TEXT segment byte public 'CODE' use16
MAIN_033_TEXT ends
main_03 group MAIN_033_TEXT

MAIN_033_TEXT segment byte public 'CODE' use16
assume cs:main_03

public POINTNUM_DIGITS_SET
pointnum_digits_set proc near
@@points     = word ptr 2
@@last_digit = word ptr 4

	mov	bx, sp
	mov	dx, ss:[bx+@@points]
	mov	bx, ss:[bx+@@last_digit]
	push	si
	mov	si, offset _FIVE_DIGIT_POWERS_OF_10 + ((5 - POINTNUM_DIGITS) * 2)
	mov	cx, (POINTNUM_DIGITS - 1)

@@loop:
	mov	ax, dx
	xor	dx, dx
	div	word ptr [si]
	mov	[bx], al
	dec	bx
	add	si, 2
	loop	@@loop
	mov	[bx], dl
	pop	si
	retn	4
pointnum_digits_set endp
	nop

MAIN_033_TEXT ends
end
