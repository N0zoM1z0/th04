; MAIN-owned stage resource names and per-stage session state.
;
; Filename text is recovered from the maintained stage-session call sites and
; the target DATA combination. Mutable cursors/counters follow their declared
; TC4J widths; no stage loader code is synthesized here.

.8086

_TEXT segment word public 'CODE' use16
_TEXT ends

_DATA segment word public 'DATA' use16
public _stage_bgm_name
_stage_bgm_name dd stage_bgm_name_text
stage_bgm_name_text db 'ST00', 0

public _eye_rgb, _miko_bft, _mari_bft, _mikod_bft, _miko32_bft, _miko16_bft
_eye_rgb   db 'eye.rgb', 0
_miko_bft  db 'miko.bft', 0
_mari_bft  db 'mari.bft', 0
_mikod_bft db 'mikod.bft', 0
_miko32_bft db 'miko32.bft', 0
_miko16_bft db 'miko16.bft', 0

public _bss0_cd2, _bss1_cd2, _bss2_cd2, _kao2_cd2, _kao3_cd2
public _bss4_cd2, _bss5_cd2, _bss6_cd2
_bss0_cd2 db 'BSS0.CD2', 0
_bss1_cd2 db 'BSS1.CD2', 0
_bss2_cd2 db 'BSS2.CD2', 0
_kao2_cd2 db 'KAO2.CD2', 0
_kao3_cd2 db 'KAO3.CD2', 0
_bss4_cd2 db 'BSS4.CD2', 0
_bss5_cd2 db 'BSS5.CD2', 0
_bss6_cd2 db 'BSS6.CD2', 0

public _st00_bft, _st01_bft, _st02_bft, _st03_bft, _st04_bft
public _st05_bft, _st06_bft
_st00_bft db 'st00.bft', 0
_st01_bft db 'st01.bft', 0
_st02_bft db 'st02.bft', 0
_st03_bft db 'st03.bft', 0
_st04_bft db 'st04.bft', 0
_st05_bft db 'st05.bft', 0
_st06_bft db 'st06.bft', 0

public _st00_mpn, _st10_mpn, _st01_mpn, _st02_mpn, _st03_mpn
public _st04_mpn, _st05_mpn, _st06_mpn
_st00_mpn db 'st00.mpn', 0
_st10_mpn db 'st10.mpn', 0
_st01_mpn db 'st01.mpn', 0
_st02_mpn db 'st02.mpn', 0
_st03_mpn db 'st03.mpn', 0
_st04_mpn db 'st04.mpn', 0
_st05_mpn db 'st05.mpn', 0
_st06_mpn db 'st06.mpn', 0

public _aGAME_PAUSE_SPACES_1, _aGAME_PAUSE_SPACES_2, _aGAME_PAUSE_SPACES_3
_aGAME_PAUSE_SPACES_1 db '    ', 0
_aGAME_PAUSE_SPACES_2 db '    ', 0
_aGAME_PAUSE_SPACES_3 db '    ', 0

public _gsCHUUDAN, _gsSAIKAI, _gsSHUURYOU
_gsCHUUDAN  db 0F0h, 0F1h, 0
_gsSAIKAI   db 0F2h, 0F3h, 0
_gsSHUURYOU db 0F4h, 0F5h, 0
public _carpet_lighting_cel
_carpet_lighting_cel dw 0
_DATA ends

_BSS segment word public 'BSS' use16
public _load_playchar_resources, _stage_faceset_count, _fp_23D90, _stage_invalidate
_load_playchar_resources dw ?
_stage_faceset_count    dw ?
_fp_23D90               dw ?
_stage_invalidate       dw ?

public _player_miss_animation_frame
_player_miss_animation_frame db ?

public _player_state_unknown_0, _player_state_unknown_1
public _player_state_unknown_2, _player_state_unknown_3
_player_state_unknown_0 dw ?
_player_state_unknown_1 dw ?
_player_state_unknown_2 dw ?
_player_state_unknown_3 dw ?

; The native scroll owner exports these as aliases of its actual driver
; fields. Retain the historical standalone owner for default replay inputs.
ifndef TH04_LARGE_PRODUCT
public _scroll_row_advance_previous, _scroll_row_advance_current
_scroll_row_advance_previous db ?
_scroll_row_advance_current  db ?

public _tile_ring_scroll_row_prev
_tile_ring_scroll_row_prev dw ?
endif

public _stage5_star_center_y
_stage5_star_center_y dw 3 dup(?)

public _carpet_light_level
_carpet_light_level db ?
_BSS ends

DGROUP group _DATA, _BSS
end
