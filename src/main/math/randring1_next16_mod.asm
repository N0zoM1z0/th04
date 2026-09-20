; TH04 CIRCLE_TEXT randring1 modulo producer.
;
; ReC98 commit 4b8baf14 reverse-engineered one RANDRING_NEXT_DEF macro family
; across TH02/TH03/TH04/TH05, and TH05 directly includes the TH04 macro source.
; Independently attested TH04 and TH05 targets preserve the same 25-byte MOD
; instruction skeleton. This is symbolic original-style assembly; linked data
; addresses remain external symbols and no target byte array is embedded.
;
; The trailing NOP is the source-owned EVEN/layout byte after the macro in
; TH04. It is outside the 25-byte logical function credit.

.8086
.model use16 large _TEXT

extrn _randring:byte
extrn _randring_p:word

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

public @RANDRING1_NEXT16_MOD$QUI
@randring1_next16_mod$qui proc near
	mov	bx, _randring_p
	mov	ax, word ptr _randring[bx]
	inc	byte ptr _randring_p
	xor	dx, dx
	mov	bx, sp
	div	word ptr ss:[bx+2]
	mov	ax, dx
	retn	2
@randring1_next16_mod$qui endp
	nop

CIRCLE_TEXT ends
end
