; TH04 shot-velocity lookup and shot-level selector.
;
; The two adjacent routines preserve a low-level producer architecture that is
; independently visible in the TH05 original target. The first routine uses the
; historical Pascal-near stack layout; the second deliberately keeps the
; same-segment far HUD call as NOP + far-declared call, which TASM lowers to
; NOP / PUSH CS / CALL near without weakening the callee ABI.

	.386
	.model use16 large _TEXT
	locals

SHOT_LEVEL_MAX = 9

	extrn _VELOCITY_192_AT_ANGLE:dword
	extrn _power:byte
	extrn _shot_level:byte
	extrn _SHOT_LEVEL_TO_POWER:word
	extrn playchar_shot_funcs:word
	extrn playchar_shot_func:word
	extrn HUD_POWER_PUT:far

MAIN_TEXT segment byte public 'CODE' use16
MAIN_TEXT ends
MAIN_012_TEXT segment byte public 'CODE' use16
MAIN_012_TEXT ends
main_01 group MAIN_TEXT, MAIN_012_TEXT

MAIN_012_TEXT segment byte public 'CODE' use16
	assume cs:main_01

public @SHOT_VELOCITY_SET$QP7SPPOINTUC
@shot_velocity_set$qp7sppointuc proc near
	mov	bx, sp
	push	si
	mov	si, ss:[bx+4]
	mov	bl, ss:[bx+2]
	xor	bh, bh
	shl	bx, 2
	mov	eax, _VELOCITY_192_AT_ANGLE[bx]
	mov	[si], eax
	pop	si
	retn	4
@shot_velocity_set$qp7sppointuc endp

public sub_11DE6
sub_11DE6 proc far
	xor	bx, bx
	xor	ax, ax
	mov	al, _power
	mov	cx, SHOT_LEVEL_MAX

@@level_loop:
	cmp	ax, _SHOT_LEVEL_TO_POWER[bx]
	jb	short @@level_ready
	add	bx, 2
	loop	@@level_loop

@@level_ready:
	mov	dx, bx
	shr	dx, 1
	mov	_shot_level, dl
	add	bx, playchar_shot_funcs
	mov	ax, [bx]
	mov	playchar_shot_func, ax

	; PC-98 compatibility prefix for a same-group FAR call; not padding.
	nop
	call	main_01:HUD_POWER_PUT
	retf
sub_11DE6 endp

MAIN_012_TEXT ends
	end
