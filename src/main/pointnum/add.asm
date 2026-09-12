; Point-number ring-buffer insertion for TH04.
;
; The two public Pascal-near entries intentionally share one physical tail.
; The BP frame is established only after the yellow/white ring slot has been
; selected. Independent TH04 and TH05 target bytes preserve this architecture.

	.186
	.model use16 large
	locals

POINTNUM_DIGITS       = 4
POINTNUM_YELLOW_COUNT = 200
POINTNUM_WHITE_COUNT  = 200
F_ALIVE               = 1

PN_FLAG         = 0
PN_CENTER_X     = 2
PN_CENTER_Y     = 4
PN_DIGITS_LEBCD = 8
PN_WIDTH        = 12
PN_TIMES_2      = 14
POINTNUM_SIZE   = 16

	extern _pointnum_yellow_p:byte
	extern _pointnum_white_p:byte
	extern _pointnums:byte
	extern _pointnum_times_2:byte
	extrn POINTNUM_DIGITS_SET:near

main_03 group MAIN_032_TEXT
MAIN_032_TEXT segment word public 'CODE' use16
	assume cs:main_03

public @POINTNUMS_ADD_YELLOW$QIIUI, @POINTNUMS_ADD_WHITE$QIIUI
pointnums_add proc near

@@number   = word ptr 4
@@center_y = word ptr 6
@@center_x = word ptr 8

@pointnums_add_yellow$qiiui:
	mov	bl, _pointnum_yellow_p
	inc	_pointnum_yellow_p
	cmp	bl, (POINTNUM_YELLOW_COUNT - 1)
	jb	short @@yellow_index_ready
	mov	_pointnum_yellow_p, 0

@@yellow_index_ready:
	xor	bh, bh
	add	bx, POINTNUM_WHITE_COUNT
	jmp	short @@add

@pointnums_add_white$qiiui:
	mov	bl, _pointnum_white_p
	mov	bh, 0
	inc	_pointnum_white_p
	cmp	bl, (POINTNUM_WHITE_COUNT - 1)
	jb	short @@add
	mov	_pointnum_white_p, 0

@@add:
	shl	bx, 4
	add	bx, offset _pointnums
	mov	word ptr [bx+PN_FLAG], F_ALIVE
	push	bp
	mov	bp, sp
	mov	ax, [bp+@@center_x]
	mov	[bx+PN_CENTER_X], ax
	mov	ax, [bp+@@center_y]
	mov	[bx+PN_CENTER_Y], ax
	mov	word ptr [bx+PN_WIDTH], 0
	mov	al, _pointnum_times_2
	mov	[bx+PN_TIMES_2], al
	lea	ax, [bx+PN_DIGITS_LEBCD + (POINTNUM_DIGITS - 1)]
	push	ax
	push	word ptr [bp+@@number]
	call	POINTNUM_DIGITS_SET
	pop	bp
	retn	6
pointnums_add endp
	even

MAIN_032_TEXT ends
	end
