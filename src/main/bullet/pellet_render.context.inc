; Standalone assembly declarations for the adjacent maintained body.
; TH04 pellet renderer pair.
;
; The top and bottom near routines share one symbolic assembler include. The
; EVEN byte between them belongs to this physical source owner but is not part
; of either logical function body.

.386
.model use16 large
locals

RES_Y = 400
ROW_SIZE = 80
PLANE_SIZE = 32000
PELLET_H = 8
PELLET_TOP_H = 6
PELLET_BOTTOM_H = 4
PELLET_BOTTOM_Y = (PELLET_H - PELLET_BOTTOM_H)

pellet_render_t struc
    PRT_left dw ?
    PRT_top dw ?
pellet_render_t ends
PRB_vram_offset equ 0
PRB_sprite_offset equ 2

extrn _pellets_render_count:word
extrn _pellets_render:byte
extrn _sPELLET:word
extrn _sPELLET_BOTTOM:word

B4M_UPDATE_TEXT segment word public 'CODE' use16
B4M_UPDATE_TEXT ends
main_03 group B4M_UPDATE_TEXT

B4M_UPDATE_TEXT segment word public 'CODE' use16
assume cs:main_03

ifdef TH04_LARGE_PRODUCT
PELLET_PROC_DISTANCE textequ <far>
PELLET_RETURN macro
    retf
endm
else
PELLET_PROC_DISTANCE textequ <near>
PELLET_RETURN macro
    retn
endm
endif

; TH04_NATIVE_BODY
B4M_UPDATE_TEXT ends
end
