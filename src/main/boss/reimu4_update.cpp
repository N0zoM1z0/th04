#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/player/shot.hpp"
#include "th04/snd/snd.h"

enum reimu_orb_flag_t {
    OF_FREE = 0,
    OF_MOVEOUT_SPIN = 1,
    OF_MOVE = 2,
};
struct reimu_orb_t {
    reimu_orb_flag_t flag;
    unsigned char angle;
    PlayfieldPoint center;
    PlayfieldPoint origin;
    PlayfieldPoint velocity;
    unsigned int spin_time;
    Subpixel distance;
    int unknown;
    signed char unused[4];
    SubpixelLength8 move_speed;
    char angle_speed;
};

extern reimu_orb_t orb_template;
extern unsigned char orb_patnum_base;
extern unsigned char reimu_orbs_visible;
extern signed char reimu_bg_pulse_direction;
extern bool palette_changed;
extern nearfunc_t_near bg_render_bombing_func;
extern unsigned char tiles_bb_col;
#pragma codeseg MAI_TEXT main_01
extern void pascal near reimu_marisa_bg_render(void);
#pragma codeseg
extern unsigned char bullet_zap;
extern unsigned char player_invincibility_time;
extern SPPoint homing_target;
extern void pascal near hud_hp_update_and_render(int hp_cur, int hp_max);
extern void pascal near boss_explode_big(unsigned int type);

extern "C" void near reimu_orbs_update(void);
extern "C" void near reimu_bg_pulse(void);
extern "C" void near reimu_phase_spread_yellow(void);
extern "C" void near reimu_phase_special_blue(void);
extern "C" void near reimu_phase_orb_spawn(void);
extern "C" void near reimu_phase_cloud_ring_stack(void);
extern "C" void near reimu_phase_pellet_and_cloud(void);
extern "C" void near reimu_phase_random_aimed(void);
extern "C" void near reimu_phase_orb_stream(void);
extern "C" void near reimu_phase_stack_octet(void);
extern "C" void near reimu_phase_dual_special(void);
extern "C" void near reimu_phase_stack_fan(void);
extern "C" void near reimu_phase_move_a(void);
extern "C" void near reimu_phase_move_b(void);

void pascal far reimu_update(void)
{
    bullet_template.origin.x.v = (boss.pos.cur.x.v + TO_SP(4));
    bullet_template.origin.y.v = (boss.pos.cur.y.v - TO_SP(28));

    switch(boss.phase) {
    case 0:
        if(boss.phase_frame == 0) {
            reimu_orbs_visible = 0;
        }
        boss_hittest_shots_invincible();
        if(boss.phase_frame <= 96) {
            goto update_tail;
        }
        boss.phase++;
        Palettes[0].c.r = 128;
        Palettes[0].c.g = 0;
        Palettes[0].c.b = 224;
        palette_changed = true;
        boss.phase_frame = 0;
        snd_se_play(13);
        bg_render_bombing_func = reimu_marisa_bg_render;
        tiles_bb_col = V_WHITE;
        goto update_tail;

    case 1:
        reimu_bg_pulse();
        boss.phase_frame++;
        boss_hittest_shots_invincible();
        if(boss.phase_frame < 128) {
            goto update_tail;
        }
        boss.pos.velocity.x.v = 0;
        boss.phase_end_hp = 9100;
        boss_phase_next(ET_NONE, 7900);
        goto update_tail;

    case 2:
        switch(boss.mode) {
        case 0: reimu_phase_spread_yellow(); break;
        case 1: reimu_phase_special_blue(); break;
        case 0xFF: reimu_phase_move_a(); break;
        }
        reimu_bg_pulse();
        if(boss.phase_state.patterns_seen < 9) {
            if(!boss_hittest_shots()) {
                goto update_tail;
            }
            boss_score_bonus(10);
        }
        boss_phase_next(ET_CIRCLE, 6300);
        boss.sprite = 129;
        reimu_orbs_visible = 0;
        goto update_tail;

    case 3:
        if(boss.pos.cur.x.v < TO_SP(192)) {
            boss.pos.velocity.x.v = TO_SP(2);
        } else if(boss.pos.cur.x.v > TO_SP(192)) {
            boss.pos.velocity.x.v = -TO_SP(2);
        } else {
            boss.pos.velocity.x.v = 0;
        }
        if(boss.pos.cur.y.v < TO_SP(96)) {
            boss.pos.velocity.y.v = TO_SP(1);
        } else if(boss.pos.cur.y.v > TO_SP(96)) {
            boss.pos.velocity.y.v = -TO_SP(1);
        } else {
            boss.pos.velocity.y.v = 0;
        }
        boss.pos.update_seg3();
        reimu_bg_pulse();
        boss_hittest_shots();
        if(boss.phase_frame < 64) {
            goto update_tail;
        }
        boss.phase++;
        boss.phase_frame = 0;
        boss.phase_state.patterns_seen = 0;
        boss.mode = 0;
        boss.sprite = 129;
        orb_template.angle_speed = 4;
        orb_patnum_base = PAT_REIMU_ORB_BLUE;
        boss_statebyte[10] = 0;
        goto update_tail;

    case 4:
        switch(boss.mode) {
        case 0:
        case 1:
        case 2:
            reimu_phase_orb_spawn();
            break;
        case 3:
            reimu_phase_cloud_ring_stack();
            break;
        case 0xFF:
            boss.phase_state.patterns_seen++;
            if(boss_statebyte[10] <= 2) {
                if(randring2_next16_and(1) != 0) {
                    boss_statebyte[10]++;
                } else {
                    boss_statebyte[10] = 3;
                }
            } else {
                boss_statebyte[10] = 0;
            }
            boss.mode = boss_statebyte[10];
            boss.phase_frame = 0;
            break;
        }
        reimu_bg_pulse();
        if(boss.phase_state.patterns_seen < 18) {
            if(!boss_hittest_shots()) {
                goto update_tail;
            }
            boss_score_bonus(10);
        }
        boss_phase_next(ET_NW_SE, 4500);
        boss.pos.velocity.x.v = 0;
        goto update_tail;

    case 5:
        if(boss.pos.cur.y.v < TO_SP(128)) {
            boss.pos.velocity.y.v = TO_SP(1);
        } else if(boss.pos.cur.y.v > TO_SP(128)) {
            boss.pos.velocity.y.v = -TO_SP(1);
        } else {
            boss.pos.velocity.y.v = 0;
        }
        boss.pos.update_seg3();
        reimu_bg_pulse();
        boss_hittest_shots();
        if(boss.phase_frame < 64) {
            break;
        }
        boss.phase++;
        boss.phase_frame = 0;
        boss.phase_state.patterns_seen = 0;
        boss.mode = 0;
        boss.sprite = 129;
        orb_template.angle_speed = 4;
        goto update_tail;

    case 6:
        switch(boss.mode) {
        case 0: reimu_phase_pellet_and_cloud(); break;
        case 1: reimu_phase_random_aimed(); break;
        case 0xFF: reimu_phase_move_b(); break;
        }
        reimu_bg_pulse();
        if(boss.phase_state.patterns_seen < 11) {
            if(!boss_hittest_shots()) {
                goto update_tail;
            }
            boss_score_bonus(10);
        }
        boss_phase_next(ET_SW_NE, 2700);
        boss.sprite = 129;
        reimu_orbs_visible = 0;
        goto update_tail;

    case 7:
        if(boss.pos.cur.x.v < TO_SP(192)) {
            boss.pos.velocity.x.v = TO_SP(2);
        } else if(boss.pos.cur.x.v > TO_SP(192)) {
            boss.pos.velocity.x.v = -TO_SP(2);
        } else {
            boss.pos.velocity.x.v = 0;
        }
        if(boss.pos.cur.y.v < TO_SP(96)) {
            boss.pos.velocity.y.v = TO_SP(1);
        } else if(boss.pos.cur.y.v > TO_SP(96)) {
            boss.pos.velocity.y.v = -TO_SP(1);
        } else {
            boss.pos.velocity.y.v = 0;
        }
        boss.pos.update_seg3();
        reimu_bg_pulse();
        boss_hittest_shots();
        if(boss.phase_frame < 64) {
            goto update_tail;
        }
        boss.phase++;
        boss.phase_frame = 0;
        boss.phase_state.patterns_seen = 0;
        boss.mode = 0;
        boss.sprite = 129;
        orb_template.angle_speed = 0x12;
        orb_patnum_base = PAT_REIMU_ORB_YELLOW;
        goto update_tail;

    case 8:
        switch(boss.mode) {
        case 0: reimu_phase_orb_stream(); break;
        case 1: reimu_phase_dual_special(); break;
        case 0xFF:
            boss.phase_state.patterns_seen++;
            boss.mode = (boss.phase_state.patterns_seen & 1);
            boss.phase_frame = 0;
            break;
        }
        reimu_bg_pulse();
        if(boss.phase_state.patterns_seen < 10) {
            if(!boss_hittest_shots()) {
                goto update_tail;
            }
            boss_score_bonus(10);
        }
        boss_phase_next(ET_HORIZONTAL, 900);
        boss.pos.velocity.x.v = 0;
        orb_template.angle_speed = 3;
        goto update_tail;

    case 9:
        switch(boss.mode) {
        case 0: reimu_phase_pellet_and_cloud(); break;
        case 1: reimu_phase_stack_fan(); break;
        case 0xFF: reimu_phase_move_a(); break;
        }
        reimu_bg_pulse();
        if(boss.phase_state.patterns_seen < 12) {
            if(!boss_hittest_shots()) {
                goto update_tail;
            }
            boss_score_bonus(10);
        }
        boss_phase_next(ET_VERTICAL, 0);
        boss.pos.velocity.x.v = 0;
        orb_template.angle_speed = 3;
        Palettes[0].c.r = 60;
        goto update_tail;

    case 10:
        if(boss.pos.cur.x.v < TO_SP(192)) {
            boss.pos.velocity.x.v = TO_SP(2);
        } else if(boss.pos.cur.x.v > TO_SP(192)) {
            boss.pos.velocity.x.v = -TO_SP(2);
        } else {
            boss.pos.velocity.x.v = 0;
        }
        if(boss.pos.cur.y.v < TO_SP(96)) {
            boss.pos.velocity.y.v = TO_SP(1);
        } else if(boss.pos.cur.y.v > TO_SP(96)) {
            boss.pos.velocity.y.v = -TO_SP(1);
        } else {
            boss.pos.velocity.y.v = 0;
        }
        boss.pos.update_seg3();
        Palettes[0].c.r = (Palettes[0].c.r + 3);
        Palettes[0].c.b = (Palettes[0].c.b - 2);
        palette_changed = true;
        boss_hittest_shots();
        if(boss.phase_frame < 64) {
            goto update_tail;
        }
        boss.phase++;
        boss.phase_frame = 0;
        boss.phase_state.patterns_seen = 0;
        boss.mode = 0;
        boss.sprite = 129;
        orb_template.angle_speed = 4;
        goto update_tail;

    case 11:
        bullet_template.origin.x.v = boss.pos.cur.x.v;
        bullet_template.origin.y.v = boss.pos.cur.y.v;
        reimu_phase_stack_octet();
        if(boss_hittest_shots()) {
            goto defeat_trigger;
        }
        if(boss.phase_frame < 1000) {
            goto update_tail;
        }
    defeat_trigger:
        boss_explode_small(ET_HORIZONTAL);
        boss.phase++;
        boss.phase_state.patterns_seen = 0;
        if(boss.phase_frame < 1000) {
            boss.phase_state.patterns_seen = 1;
        }
        boss.phase_frame = 0;
        goto update_tail;

    case 12:
        boss.phase_frame++;
        if(boss.phase_frame == 16) {
            boss_explode_small(ET_VERTICAL);
        }
        if(boss.phase_frame == 32) {
            boss_explode_big(static_cast<unsigned int>(ET_SW_NE));
            boss.phase = PHASE_EXPLODE_BIG;
            bullet_zap = boss.phase_state.defeat_bonus;
            if(boss.phase_state.defeat_bonus != 0) {
                boss_score_bonus(40);
            }
            boss.sprite = PAT_ENEMY_KILL;
            boss.phase_frame = 0;
            snd_se_play(12);
            Palettes[0].c.r = 0;
            Palettes[0].c.b = 0;
            palette_changed = true;
            player_invincibility_time = BOSS_DEFEAT_INVINCIBILITY_FRAMES;
        }
        goto update_tail;

    default:
        boss_defeat_update();
        return;
    }

update_tail:
    homing_target.x.v = boss.pos.cur.x.v;
    homing_target.y.v = boss.pos.cur.y.v;
    reimu_orbs_update();
    hud_hp_update_and_render(boss.hp, 9100);
}
