; Zero-code TH04 MAIN layout metadata for incremental authored reconstruction.
; This object must contain SEGDEF/GRPDEF records only and no LEDATA.
.386
SLOWDOWN_TEXT segment word public 'CODE' use16
SLOWDOWN_TEXT ends
DEMO_TEXT segment word public 'CODE' use16
DEMO_TEXT ends
EMS_TEXT segment byte public 'CODE' use16
EMS_TEXT ends
TILE_SET_TEXT segment byte public 'CODE' use16
TILE_SET_TEXT ends
STD_TEXT segment byte public 'CODE' use16
STD_TEXT ends
END_TEXT segment byte public 'CODE' use16
END_TEXT ends
CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
TILE_TEXT segment word public 'CODE' use16
TILE_TEXT ends
mai_TEXT segment word public 'CODE' use16
mai_TEXT ends
PLAYFLD_TEXT segment byte public 'CODE' use16
PLAYFLD_TEXT ends
M4_RENDER_TEXT segment byte public 'CODE' use16
M4_RENDER_TEXT ends
DIALOG_TEXT segment byte public 'CODE' use16
DIALOG_TEXT ends
BOSS_EXP_TEXT segment byte public 'CODE' use16
BOSS_EXP_TEXT ends
main_TEXT segment byte public 'CODE' use16
main_TEXT ends
STAGES_TEXT segment byte public 'CODE' use16
STAGES_TEXT ends
main__TEXT segment byte public 'CODE' use16
main__TEXT ends
PLAYER_M_TEXT segment byte public 'CODE' use16
PLAYER_M_TEXT ends
PLAYER_P_TEXT segment byte public 'CODE' use16
PLAYER_P_TEXT ends
main_0_TEXT segment word public 'CODE' use16
main_0_TEXT ends
HUD_OVRL_TEXT segment byte public 'CODE' use16
HUD_OVRL_TEXT ends
main_01_TEXT segment byte public 'CODE' use16
main_01_TEXT ends
main_012_TEXT segment byte public 'CODE' use16
main_012_TEXT ends
CFG_LRES_TEXT segment byte public 'CODE' use16
CFG_LRES_TEXT ends
main_013_TEXT segment word public 'CODE' use16
main_013_TEXT ends
CHECKERB_TEXT segment byte public 'CODE' use16
CHECKERB_TEXT ends
MB_INV_TEXT segment byte public 'CODE' use16
MB_INV_TEXT ends
BOSS_BD_TEXT segment byte public 'CODE' use16
BOSS_BD_TEXT ends
BOSS_BG_TEXT segment word public 'CODE' use16
BOSS_BG_TEXT ends
SCORE_TEXT segment byte public 'CODE' use16
SCORE_TEXT ends
BOSS_FG_TEXT segment byte public 'CODE' use16
BOSS_FG_TEXT ends
SHARED segment byte public 'CODE' use16
SHARED ends
GATHER_TEXT segment byte public 'CODE' use16
GATHER_TEXT ends
SCROLLY3_TEXT segment word public 'CODE' use16
SCROLLY3_TEXT ends
MOTION_3_TEXT segment word public 'CODE' use16
MOTION_3_TEXT ends
main_032_TEXT segment word public 'CODE' use16
main_032_TEXT ends
VECTOR2N_TEXT segment byte public 'CODE' use16
VECTOR2N_TEXT ends
SPARK_A_TEXT segment byte public 'CODE' use16
SPARK_A_TEXT ends
GRCG_3_TEXT segment byte public 'CODE' use16
GRCG_3_TEXT ends
IT_SPL_U_TEXT segment word public 'CODE' use16
IT_SPL_U_TEXT ends
B4M_UPDATE_TEXT segment word public 'CODE' use16
B4M_UPDATE_TEXT ends
main_033_TEXT segment byte public 'CODE' use16
main_033_TEXT ends
MIDBOSS_TEXT segment byte public 'CODE' use16
MIDBOSS_TEXT ends
HUD_HP_TEXT segment byte public 'CODE' use16
HUD_HP_TEXT ends
MB_DFT_TEXT segment byte public 'CODE' use16
MB_DFT_TEXT ends
main_034_TEXT segment byte public 'CODE' use16
main_034_TEXT ends
BULLET_U_TEXT segment byte public 'CODE' use16
BULLET_U_TEXT ends
BULLET_A_TEXT segment byte public 'CODE' use16
BULLET_A_TEXT ends
main_035_TEXT segment byte public 'CODE' use16
main_035_TEXT ends
BOSS_TEXT segment byte public 'CODE' use16
BOSS_TEXT ends
main_036_TEXT segment byte public 'CODE' use16
main_036_TEXT ends
main_01 group SLOWDOWN_TEXT, DEMO_TEXT, EMS_TEXT, TILE_SET_TEXT, STD_TEXT, END_TEXT, CIRCLE_TEXT, TILE_TEXT, mai_TEXT, PLAYFLD_TEXT, M4_RENDER_TEXT, DIALOG_TEXT, BOSS_EXP_TEXT, main_TEXT, STAGES_TEXT, main__TEXT, PLAYER_M_TEXT, PLAYER_P_TEXT, main_0_TEXT, HUD_OVRL_TEXT, main_01_TEXT, main_012_TEXT, CFG_LRES_TEXT, main_013_TEXT, CHECKERB_TEXT, MB_INV_TEXT, BOSS_BD_TEXT, BOSS_BG_TEXT, SCORE_TEXT, BOSS_FG_TEXT
main_03 group GATHER_TEXT, SCROLLY3_TEXT, MOTION_3_TEXT, main_032_TEXT, VECTOR2N_TEXT, SPARK_A_TEXT, GRCG_3_TEXT, IT_SPL_U_TEXT, B4M_UPDATE_TEXT, main_033_TEXT, MIDBOSS_TEXT, HUD_HP_TEXT, MB_DFT_TEXT, main_034_TEXT, BULLET_U_TEXT, BULLET_A_TEXT, main_035_TEXT, BOSS_TEXT, main_036_TEXT
end
