; Standalone assembly declarations for the adjacent maintained body.
; TH04 Yuuka 5 backdrop color fill.
;
; This low-level producer writes through ES with 32-bit string stores whose
; source value is irrelevant while the GRCG is active. Legal typed TC4J far-
; pointer code expands into a framed pointer loop instead, so this is maintained
; as evidence-backed irreducible/original-style symbolic assembly.

.386
.model use16 large
locals
GRAM_400 = 0A800h
ROW_SIZE = 80
PLAYFIELD_TOP = 16
PLAYFIELD_VRAM_LEFT = 4

extrn _grcg_fill_playfield_rows:near

GRCG_FILL_PLAYFIELD_ROWS macro y:req, num_rows:req, scratch_seg:=<ax>
	mov	scratch_seg, GRAM_400 + (((y + PLAYFIELD_TOP) * ROW_SIZE) shr 4)
	mov	es, scratch_seg
	mov	di, ((num_rows - 1) * ROW_SIZE) + PLAYFIELD_VRAM_LEFT
	call	_grcg_fill_playfield_rows
endm

BOSS_BG_TEXT segment word public 'CODE' use16
BOSS_BG_TEXT ends
main_01 group BOSS_BG_TEXT
BOSS_BG_TEXT segment word public 'CODE' use16
assume cs:main_01

; TH04_NATIVE_BODY
BOSS_BG_TEXT ends
end
