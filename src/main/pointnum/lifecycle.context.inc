; Standalone assembly declarations for the adjacent maintained body.
; Point-number lifecycle for TH04.
;
; These three public near routines share one physical assembler include. The
; two EVEN directives own layout bytes between logical function bodies; those
; bytes are physical source ownership, not function-body credit.

	.186
	.model use16 large
	locals

POINTNUM_H = 8
POINTNUM_W = 8
POINTNUM_TIMES_2_W = 16
POINTNUM_POPUP_DISTANCE = (12 shl 4)
POINTNUM_POPUP_FRAMES = 24
POINTNUM_FRAMES = 36
POINTNUM_DIGITS = 4
POINTNUM_YELLOW_COUNT = 200
POINTNUM_WHITE_COUNT = 200
POINTNUM_COUNT = 400
POINTNUM_SIZE = 16
F_FREE = 0
F_ALIVE = 1
F_REMOVE = 2

PN_FLAG = 0
PN_CENTER_CUR_X = 2
PN_CENTER_CUR_Y = 4

Point struc
	x dw ?
	y dw ?
Point ends

pointnum_t struc
	flag db ?
	age db ?
	PN_center_cur Point <?>
	PN_center_prev_y dw ?
	PN_digits_lebcd db POINTNUM_DIGITS dup(?)
	PN_width dw ?
	PN_times_2 db ?
	db ?
pointnum_t ends

extrn _pointnum_white_p:byte
extrn _pointnum_yellow_p:byte
extrn _pointnum_first_yellow_alive:word
extrn _pointnums:byte
extrn _pointnums_alive:word
extrn _pointnum_times_2:byte
extrn _tile_invalidate_box:Point
extrn TILES_INVALIDATE_AROUND:near

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

; TH04_NATIVE_BODY
even

CIRCLE_TEXT ends
end
