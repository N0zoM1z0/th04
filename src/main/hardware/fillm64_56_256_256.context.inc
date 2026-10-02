; Standalone assembly declarations for the adjacent maintained body.
; TH04/TH05-style 64,56,256,256 playfield backdrop filler.
;
; With the GRCG already in TDW mode, the source value in EAX is irrelevant to
; VRAM. The target deliberately reuses EAX and instruction flags while using
; STOSD/LOOP. Defined natural TC4J dword-store loops expand those mechanisms,
; so keep this shared low-level producer as symbolic original-style assembly.

	.386
	.model use16 large
	locals
GRAM_400 = 0A800h
ROW_SIZE = 80
PLAYFIELD_TOP = 16
PLAYFIELD_VRAM_LEFT = 4
PLAYFIELD_VRAM_W = 48

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

; TH04_NATIVE_BODY
    even

CIRCLE_TEXT ends
end
