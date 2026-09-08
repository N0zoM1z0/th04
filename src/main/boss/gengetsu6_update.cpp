#pragma option -zCMAIN_036_TEXT -zPmain_03
#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/player/player.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

static const pixel_t WAVE_TARGET_MARGIN = (PLAYFIELD_W / 12);

extern bool bombing;
extern unsigned char boss_bomb_invincibility_frames;
extern unsigned char gengetsu_wave_amp;
extern Subpixel gengetsu_wave_target_x;
extern nearfunc_t_near bg_render_bombing_func;
extern unsigned char tiles_bb_col;
extern bool palette_changed;
extern unsigned char player_invincibility_time;
extern unsigned char bullet_zap;
extern unsigned int __cdecl PaletteTone;
extern SPPoint homing_target;

#pragma codeseg MAI_TEXT main_01
extern void pascal near mugetsu_gengetsu_bg_render(void);
#pragma codeseg

extern void pascal near hud_hp_update_and_render(int hp_cur, int hp_max);
extern void pascal near boss_explode_big(unsigned int type);
extern "C" void near thicklasers_update(void);

extern "C" void near gengetsu_ring_phase(void);
extern "C" void near gengetsu_spread_pair_phase(void);
extern "C" bool near gengetsu_wave_step(void);
extern "C" void near gengetsu_bounce_phase(void);
extern "C" void near gengetsu_turn_gather_phase(void);
extern "C" void near gengetsu_cycle_phase(void);
extern "C" void near gengetsu_aimed_spread_phase(void);
extern "C" void near gengetsu_mirror_spread_phase(void);
extern "C" void near gengetsu_columns_phase(void);
extern "C" bool near gengetsu_wave_bounce(void);
extern "C" void near gengetsu_random_ring(void);
extern "C" void near gengetsu_dual_clusters(void);
extern "C" void near gengetsu_random_cloud_ring(void);
extern "C" bool near gengetsu_hittest(void);
extern "C" void near gengetsu_blue_ring(void);

void pascal far gengetsu_update(void)
{
    if(bombing != 0) {
        boss_bomb_invincibility_frames = 0x20;
    }
    if(boss_bomb_invincibility_frames != 0) {
        boss_bomb_invincibility_frames--;
    }

    bullet_template.origin.x.v = (boss.pos.cur.x.v - TO_SP(13));
    bullet_template.origin.y.v = (boss.pos.cur.y.v - TO_SP(48));
    bullet_template.spawn_type = BST_PELLET;

    switch(boss.phase) {
    case 0:
        gengetsu_hittest();
        boss.hp = 18700;
        if(boss.phase_frame <= 128) {
            goto update_tail;
        }
        boss.phase_end_hp = 14700;
        boss.phase++;
        boss.phase_frame = 0;
        snd_se_play(13);
        tiles_bb_col = V_WHITE;
        bg_render_bombing_func = mugetsu_gengetsu_bg_render;
        goto update_tail;

    case 1:
        gengetsu_hittest();
        if(boss.phase_frame < 64) {
            goto update_tail;
        }
        boss.phase++;
        boss.mode = 0;
        boss.phase_state.patterns_seen = 0;
        boss.phase_frame = 0;
        boss.pos.velocity.x.v = 0;
        goto update_tail;

    case 2:
        switch(boss.mode) {
        case 0:
            gengetsu_ring_phase();
            break;
        case 1:
            gengetsu_spread_pair_phase();
            break;
        case 0xFF:
            if(boss.phase_frame == 1) {
                if((boss.phase_state.patterns_seen & 1) != 0) {
                    gengetsu_wave_target_x.v = player_pos.cur.x.v;
                    if(gengetsu_wave_target_x.v < TO_SP(WAVE_TARGET_MARGIN)) {
                        gengetsu_wave_target_x.v = TO_SP(WAVE_TARGET_MARGIN);
                    } else if(gengetsu_wave_target_x.v > TO_SP(PLAYFIELD_W - WAVE_TARGET_MARGIN)) {
                        gengetsu_wave_target_x.v = TO_SP(PLAYFIELD_W - WAVE_TARGET_MARGIN);
                    }
                } else {
                    gengetsu_wave_target_x.v = (
                        randring2_next16_mod(TO_SP(PLAYFIELD_W - (WAVE_TARGET_MARGIN * 4))) +
                        TO_SP(WAVE_TARGET_MARGIN * 2)
                    );
                }
            }
            if(gengetsu_wave_step()) {
                boss.phase_state.patterns_seen++;
                boss.mode = (boss.phase_state.patterns_seen & 1);
                boss.phase_frame = 0;
            }
            break;
        }
        if((boss.phase_state.patterns_seen >= 18) && (boss.mode != 0xFF)) {
            gengetsu_blue_ring();
        }
        if(boss.phase_state.patterns_seen < 22) {
            if(!gengetsu_hittest()) {
                goto update_tail;
            }
            boss_score_bonus(100);
        }
        boss_phase_next(ET_CIRCLE, 12700);
        boss.mode = 0xFF;
        gengetsu_wave_target_x.v = TO_SP(PLAYFIELD_W / 2);
        goto update_tail;

    case 3:
        switch(boss.mode) {
        case 0:
            gengetsu_bounce_phase();
            break;
        case 1:
            gengetsu_turn_gather_phase();
            break;
        case 0xFF:
            if(boss.phase_frame == 1) {
                if((boss.phase_state.patterns_seen & 1) != 0) {
                    gengetsu_wave_target_x.v = player_pos.cur.x.v;
                    if(gengetsu_wave_target_x.v < TO_SP(WAVE_TARGET_MARGIN)) {
                        gengetsu_wave_target_x.v = TO_SP(WAVE_TARGET_MARGIN);
                    } else if(gengetsu_wave_target_x.v > TO_SP(PLAYFIELD_W - WAVE_TARGET_MARGIN)) {
                        gengetsu_wave_target_x.v = TO_SP(PLAYFIELD_W - WAVE_TARGET_MARGIN);
                    }
                } else {
                    gengetsu_wave_target_x.v = (
                        randring2_next16_mod(TO_SP(PLAYFIELD_W - (WAVE_TARGET_MARGIN * 4))) +
                        TO_SP(WAVE_TARGET_MARGIN * 2)
                    );
                }
            }
            if(gengetsu_wave_step()) {
                boss.mode = (boss.phase_state.patterns_seen & 1);
                boss.phase_state.patterns_seen++;
                boss.phase_frame = 0;
            }
            break;
        }
        if((boss.phase_state.patterns_seen >= 18) && (boss.mode != 0xFF)) {
            gengetsu_blue_ring();
        }
        if(boss.phase_state.patterns_seen < 22) {
            if(!gengetsu_hittest()) {
                goto update_tail;
            }
            boss_score_bonus(100);
        }
        boss_phase_next(ET_HORIZONTAL, 8900);
        boss.mode = 0xFF;
        gengetsu_wave_target_x.v = TO_SP(PLAYFIELD_W / 2);
        goto update_tail;

    case 4:
        switch(boss.mode) {
        case 0:
            gengetsu_cycle_phase();
            break;
        case 1:
            gengetsu_aimed_spread_phase();
            break;
        case 0xFF:
            if(boss.phase_frame == 1) {
                if((boss.phase_state.patterns_seen & 1) != 0) {
                    gengetsu_wave_target_x.v = player_pos.cur.x.v;
                    if(gengetsu_wave_target_x.v < TO_SP(WAVE_TARGET_MARGIN)) {
                        gengetsu_wave_target_x.v = TO_SP(WAVE_TARGET_MARGIN);
                    } else if(gengetsu_wave_target_x.v > TO_SP(PLAYFIELD_W - WAVE_TARGET_MARGIN)) {
                        gengetsu_wave_target_x.v = TO_SP(PLAYFIELD_W - WAVE_TARGET_MARGIN);
                    }
                } else {
                    gengetsu_wave_target_x.v = (
                        randring2_next16_mod(TO_SP(PLAYFIELD_W - (WAVE_TARGET_MARGIN * 4))) +
                        TO_SP(WAVE_TARGET_MARGIN * 2)
                    );
                }
            }
            if(gengetsu_wave_step()) {
                boss.mode = (boss.phase_state.patterns_seen & 1);
                boss.phase_state.patterns_seen++;
                boss.phase_frame = 0;
            }
            break;
        }
        if((boss.phase_state.patterns_seen >= 18) && (boss.mode != 0xFF)) {
            gengetsu_blue_ring();
        }
        if(boss.phase_state.patterns_seen < 22) {
            if(!gengetsu_hittest()) {
                goto update_tail;
            }
            boss_score_bonus(100);
        }
        boss_phase_next(ET_HORIZONTAL, 5500);
        boss.mode = 0xFF;
        gengetsu_wave_target_x.v = TO_SP(PLAYFIELD_W / 2);
        goto update_tail;

    case 5:
        switch(boss.mode) {
        case 0:
            gengetsu_mirror_spread_phase();
            break;
        case 1:
            gengetsu_columns_phase();
            break;
        case 0xFF:
            if(boss.phase_frame == 1) {
                if((boss.phase_state.patterns_seen & 1) != 0) {
                    gengetsu_wave_target_x.v = player_pos.cur.x.v;
                    if(gengetsu_wave_target_x.v < TO_SP(WAVE_TARGET_MARGIN)) {
                        gengetsu_wave_target_x.v = TO_SP(WAVE_TARGET_MARGIN);
                    } else if(gengetsu_wave_target_x.v > TO_SP(PLAYFIELD_W - WAVE_TARGET_MARGIN)) {
                        gengetsu_wave_target_x.v = TO_SP(PLAYFIELD_W - WAVE_TARGET_MARGIN);
                    }
                } else {
                    gengetsu_wave_target_x.v = (
                        randring2_next16_mod(TO_SP(PLAYFIELD_W - (WAVE_TARGET_MARGIN * 4))) +
                        TO_SP(WAVE_TARGET_MARGIN * 2)
                    );
                }
            }
            if(gengetsu_wave_step()) {
                boss.mode = (boss.phase_state.patterns_seen & 1);
                boss.phase_state.patterns_seen++;
                boss.phase_frame = 0;
            }
            break;
        }
        if((boss.phase_state.patterns_seen >= 18) && (boss.mode != 0xFF)) {
            gengetsu_blue_ring();
        }
        if(boss.phase_state.patterns_seen < 22) {
            if(!gengetsu_hittest()) {
                goto update_tail;
            }
            boss_score_bonus(100);
        }
        boss_phase_next(ET_HORIZONTAL, 3000);
        boss.mode = 0xFF;
        gengetsu_wave_target_x.v = TO_SP(PLAYFIELD_W / 2);
        goto update_tail;

    case 6:
        gengetsu_hittest();
        if(!gengetsu_wave_bounce()) {
            goto update_tail;
        }
        boss.phase++;
        boss.phase_frame = 32;
        goto update_tail;

    case 7:
        gengetsu_random_ring();
        if(boss.phase_frame < 1500) {
            if(!gengetsu_hittest()) {
                goto update_tail;
            }
            boss_score_bonus(100);
        }
        boss_phase_next(ET_VERTICAL, 0);
        boss.mode = 0xFF;
        gengetsu_wave_target_x.v = TO_SP(PLAYFIELD_W / 2);
        boss_statebyte[15] = 16;
        goto update_tail;

    case 8:
        if(boss.phase_frame <= 3000) {
            gengetsu_dual_clusters();
        } else {
            gengetsu_random_cloud_ring();
        }
        if(!gengetsu_hittest() && (boss.phase_frame < 5000)) {
            goto update_tail;
        }
        boss_explode_small(ET_NW_SE);
        boss.phase++;
        if(boss.phase_frame < 5000) {
            boss.phase_state.patterns_seen = 1;
        } else {
            boss.phase_state.patterns_seen = 0;
        }
        boss.phase_frame = 0;
        boss.mode = 0;
        PaletteTone = 100;
        palette_changed = true;
        goto update_tail;

    case 9:
        boss.phase_frame++;
        if(boss.phase_frame == 16) {
            boss_explode_small(ET_VERTICAL);
        }
        if(boss.phase_frame == 32) {
            boss_explode_big(static_cast<unsigned int>(ET_HORIZONTAL));
            boss.phase = PHASE_EXPLODE_BIG;
            bullet_zap = boss.phase_state.defeat_bonus;
            if(boss.phase_state.defeat_bonus != 0) {
                boss_score_bonus(200);
            }
            boss.sprite = PAT_ENEMY_KILL;
            boss.phase_frame = 0;
            snd_se_play(12);
            palette_changed = true;
            player_invincibility_time = BOSS_DEFEAT_INVINCIBILITY_FRAMES;
        }
        goto update_tail;

    default:
        boss_defeat_update();
        return;
    }

update_tail:
    if(gengetsu_wave_amp == 0) {
        homing_target.x.v = boss.pos.cur.x.v;
        homing_target.y.v = boss.pos.cur.y.v;
    }
    thicklasers_update();
    hud_hp_update_and_render(boss.hp, 18700);
}
