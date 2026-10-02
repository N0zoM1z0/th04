; Standalone assembly declarations for the adjacent maintained body.
; TH04 16x16 four-plane .MPN image renderer.
;
; Target/raw/TASM review closes this game-owned FAR routine between JS_SENSE and
; the MASTER.LIB BGM block. Independent TH05 target code preserves the same
; 16-row MOVSW/LOOP plane-copy architecture, while legal TC4J 4.02 far-pointer
; source expands to ES-only accesses and ordinary loop control. Keep this as
; evidence-backed original-style symbolic assembly rather than manufacturing a
; C++ spelling for the target's DS/FS/GS/ES register allocation.

	.386
	.model use16 large
	locals
ROW_SIZE = 80
TILE_H = 16
SEG_PLANE_B = 0A800h
SEG_PLANE_R = 0B000h
SEG_PLANE_G = 0B800h
SEG_PLANE_E = 0E000h

mpn_t struc
	MPN_images dd ?
	MPN_count dw ?
	db 48 dup(?)
	db 10 dup(?)
mpn_t ends

extrn _mpn_slots:byte

_TEXT segment word public 'CODE' use16
_TEXT ends

_TEXT segment word public 'CODE' use16
assume cs:_TEXT

; TH04_NATIVE_BODY
_TEXT ends
end
