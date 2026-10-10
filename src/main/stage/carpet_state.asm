; MAIN-owned Stage 4 carpet image offsets and lighting animation mask.
;
; The image table is expressed through the tile-image addressing contract,
; rather than copied linked bytes: each entry names the source tile image and
; the assembler derives its VRAM offset from the maintained geometry.

.8086

RES_Y = 400
TILE_H = 16
ROW_SIZE = 80
TILE_VRAM_W = 2
TILE_AREA_VRAM_LEFT = 72
TILES_X = 24
TILES_Y = 25

TILE_IMAGE_0  = TILE_AREA_VRAM_LEFT + ((0  / TILES_Y) * TILE_VRAM_W) + ((0  mod TILES_Y) * (TILE_H * ROW_SIZE))
TILE_IMAGE_34 = TILE_AREA_VRAM_LEFT + ((34 / TILES_Y) * TILE_VRAM_W) + ((34 mod TILES_Y) * (TILE_H * ROW_SIZE))
TILE_IMAGE_35 = TILE_AREA_VRAM_LEFT + ((35 / TILES_Y) * TILE_VRAM_W) + ((35 mod TILES_Y) * (TILE_H * ROW_SIZE))
TILE_IMAGE_36 = TILE_AREA_VRAM_LEFT + ((36 / TILES_Y) * TILE_VRAM_W) + ((36 mod TILES_Y) * (TILE_H * ROW_SIZE))
TILE_IMAGE_37 = TILE_AREA_VRAM_LEFT + ((37 / TILES_Y) * TILE_VRAM_W) + ((37 mod TILES_Y) * (TILE_H * ROW_SIZE))
TILE_IMAGE_38 = TILE_AREA_VRAM_LEFT + ((38 / TILES_Y) * TILE_VRAM_W) + ((38 mod TILES_Y) * (TILE_H * ROW_SIZE))
TILE_IMAGE_39 = TILE_AREA_VRAM_LEFT + ((39 / TILES_Y) * TILE_VRAM_W) + ((39 mod TILES_Y) * (TILE_H * ROW_SIZE))
TILE_IMAGE_48 = TILE_AREA_VRAM_LEFT + ((48 / TILES_Y) * TILE_VRAM_W) + ((48 mod TILES_Y) * (TILE_H * ROW_SIZE))
TILE_IMAGE_49 = TILE_AREA_VRAM_LEFT + ((49 / TILES_Y) * TILE_VRAM_W) + ((49 mod TILES_Y) * (TILE_H * ROW_SIZE))
TILE_IMAGE_50 = TILE_AREA_VRAM_LEFT + ((50 / TILES_Y) * TILE_VRAM_W) + ((50 mod TILES_Y) * (TILE_H * ROW_SIZE))
TILE_IMAGE_51 = TILE_AREA_VRAM_LEFT + ((51 / TILES_Y) * TILE_VRAM_W) + ((51 mod TILES_Y) * (TILE_H * ROW_SIZE))
TILE_IMAGE_52 = TILE_AREA_VRAM_LEFT + ((52 / TILES_Y) * TILE_VRAM_W) + ((52 mod TILES_Y) * (TILE_H * ROW_SIZE))
TILE_IMAGE_53 = TILE_AREA_VRAM_LEFT + ((53 / TILES_Y) * TILE_VRAM_W) + ((53 mod TILES_Y) * (TILE_H * ROW_SIZE))

_DATA segment word public 'DATA' use16
public _CARPET_TILE_IMAGE_VOS, _CARPET_LIGHTING_ANIM

; Dark, mid, and bright carpet image IDs across the 24-tile row.
_CARPET_TILE_IMAGE_VOS label word
    dw TILE_IMAGE_0,  TILE_IMAGE_0,  TILE_IMAGE_0,  TILE_IMAGE_48
    dw TILE_IMAGE_0,  TILE_IMAGE_48, TILE_IMAGE_0,  TILE_IMAGE_0
    dw TILE_IMAGE_0,  TILE_IMAGE_0,  TILE_IMAGE_0,  TILE_IMAGE_0
    dw TILE_IMAGE_0,  TILE_IMAGE_0,  TILE_IMAGE_0,  TILE_IMAGE_0
    dw TILE_IMAGE_0,  TILE_IMAGE_0,  TILE_IMAGE_49, TILE_IMAGE_0
    dw TILE_IMAGE_49, TILE_IMAGE_0,  TILE_IMAGE_0,  TILE_IMAGE_0

    dw TILE_IMAGE_36, TILE_IMAGE_35, TILE_IMAGE_34, TILE_IMAGE_50
    dw TILE_IMAGE_34, TILE_IMAGE_50, TILE_IMAGE_34, TILE_IMAGE_34
    dw TILE_IMAGE_34, TILE_IMAGE_34, TILE_IMAGE_34, TILE_IMAGE_34
    dw TILE_IMAGE_34, TILE_IMAGE_34, TILE_IMAGE_34, TILE_IMAGE_34
    dw TILE_IMAGE_34, TILE_IMAGE_34, TILE_IMAGE_51, TILE_IMAGE_34
    dw TILE_IMAGE_51, TILE_IMAGE_34, TILE_IMAGE_35, TILE_IMAGE_36

    dw TILE_IMAGE_39, TILE_IMAGE_38, TILE_IMAGE_37, TILE_IMAGE_52
    dw TILE_IMAGE_37, TILE_IMAGE_52, TILE_IMAGE_37, TILE_IMAGE_37
    dw TILE_IMAGE_37, TILE_IMAGE_37, TILE_IMAGE_37, TILE_IMAGE_37
    dw TILE_IMAGE_37, TILE_IMAGE_37, TILE_IMAGE_37, TILE_IMAGE_37
    dw TILE_IMAGE_37, TILE_IMAGE_37, TILE_IMAGE_53, TILE_IMAGE_37
    dw TILE_IMAGE_53, TILE_IMAGE_37, TILE_IMAGE_38, TILE_IMAGE_39

; 2 = untouched, 1 = replace on this cel, 0 = already replaced.
_CARPET_LIGHTING_ANIM label byte
; Cel 0 is dark. Cel 1 replaces the middle pair; subsequent cels
; reach two more columns on each side, finishing at the outermost pair.
; MAIN DGROUP(2134):199C retains one nonmonotonic cell: cel 5/column 2
; is already-replaced before its normal replacement at cel 6.
CARPET_CEL = 0
rept 8
    CARPET_COLUMN = 0
    rept TILES_X
        if CARPET_COLUMN lt (TILES_X / 2)
            CARPET_REPLACE_CEL = (14 - CARPET_COLUMN) / 2
        else
            CARPET_REPLACE_CEL = (CARPET_COLUMN - 9) / 2
        endif
        if (CARPET_CEL eq 5) and (CARPET_COLUMN eq 2)
            db 0
        else
            if CARPET_CEL lt CARPET_REPLACE_CEL
                db 2
            else
                if CARPET_CEL eq CARPET_REPLACE_CEL
                    db 1
                else
                    db 0
                endif
            endif
        endif
        CARPET_COLUMN = CARPET_COLUMN + 1
    endm
    CARPET_CEL = CARPET_CEL + 1
endm

_DATA ends
DGROUP group _DATA
end
