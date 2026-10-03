; MAIN-owned item, item-splash, and item-score state.
;
; The storage extents follow the maintained item/splash structures and the
; target item BSS fragments. Tables with opaque gameplay distributions remain
; outside this owner until their semantic source is recovered.

.8086

_TEXT segment word public 'CODE' use16
_TEXT ends

_DATA segment word public 'DATA' use16
public _ITEM_PATNUM, _DREAM_SCORE_PER_ITEMS
; PAT_ITEM is 44 in the maintained TH04 sprite numbering.
_ITEM_PATNUM label word
dw 44, 45, 46, 47, 48, 49, 50
_DREAM_SCORE_PER_ITEMS label word
dw 0, 100, 200, 400, 600, 800, 1000, 1280

public _item_playperf_raise, _item_playperf_lower
_item_playperf_raise db 0
_item_playperf_lower db 0

public _POWER_OVERFLOW_BONUS
_POWER_OVERFLOW_BONUS label word
; Inclusive overflow-score table: indices 0..42.
dw 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
dw 20, 30, 40, 50, 60, 70, 80, 90, 100
dw 150, 200, 250, 300, 350, 400, 450, 500, 550, 600
dw 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100
dw 1200, 1250, 1280

public _ITEM_MISS_VELOCITIES
_ITEM_MISS_VELOCITIES label word
dw (-3 shl 4), (-3 shl 4) - 8, (-4 shl 4), (-4 shl 4) - 8, (-5 shl 4)
dw ( 0 shl 4), ( 0 shl 4) + 12, ( 1 shl 4) + 8, ( 2 shl 4) + 4, ( 3 shl 4)
dw (-3 shl 4), (-3 shl 4) - 8, (-4 shl 4), (-3 shl 4) - 8, (-3 shl 4)
dw (-1 shl 4) - 8, ( 0 shl 4) - 12, ( 0 shl 4), ( 0 shl 4) + 12, ( 1 shl 4) + 8
dw (-3 shl 4), (-3 shl 4) - 8, (-4 shl 4), (-4 shl 4) - 8, (-5 shl 4)
dw ( 0 shl 4), ( 0 shl 4) - 12, (-1 shl 4) - 8, (-2 shl 4) - 4, (-3 shl 4)

public _ENEMY_DROPS
_ENEMY_DROPS label byte
; items_add advances a byte counter for every automatic-drop request, emits
; only on even values, and indexes this table with (counter / 2) modulo 64.
db 0, 1, 0, 0, 1, 1, 0, 1
db 0, 1, 1, 1, 0, 0, 0, 2
db 1, 0, 1, 1, 0, 0, 1, 0
db 1, 0, 0, 0, 1, 1, 1, 2
db 0, 1, 0, 0, 1, 1, 0, 1
db 0, 1, 1, 1, 0, 0, 0, 2
db 1, 0, 1, 1, 0, 0, 1, 0
db 1, 0, 0, 0, 1, 1, 1, 3

public _power_overflow, _items_spawned, _items_collected
public _total_point_items_collected, _total_max_valued_point_items_collected
_power_overflow                  dw 0
_items_spawned                   dw 0
_items_collected                 dw 0
_total_point_items_collected     dw 0
_total_max_valued_point_items_collected dw 0

; Item attraction is a target-owned gameplay latch, not a derived constant.
public _items_pull_to_player
_items_pull_to_player db 0
                db ?
_DATA ends

_BSS segment word public 'BSS' use16
public _item_drop_cycle, _stage_point_items_collected, _dream_items_collected
_item_drop_cycle               db ?
_stage_point_items_collected   db ?
_dream_items_collected         db ?
                db 2 dup(?)

public _dream_score, _max_valued_point_items
_dream_score             dw ?
_max_valued_point_items  dw ?

; item_t is 20 bytes (flag/pad, three Points, type/unknown, patnum, and the
; 16-bit pulled flag); the target reserves four trailing unused entries.
public _items
_items db (20 * 36) dup(?)

; item_splash_t is 10 bytes under the target Point/motion packing.
public _item_splashes, _item_splash_last_id
_item_splashes       db (10 * 8) dup(?)
_item_splashes_unused db 10 dup(?)
_item_splash_last_id db ?
_BSS ends

DGROUP group _DATA, _BSS
end
