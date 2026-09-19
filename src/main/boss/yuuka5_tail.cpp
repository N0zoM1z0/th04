#ifndef TH04_YUUKA5_COMBINED
#pragma option -zCB4M_UPDATE_TEXT -zPmain_03

#include "src/shared/runtime/api.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/v_colors.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/laser_t.hpp"
#include "th04/main/circle.hpp"
#include "th04/main/gather.hpp"
#include "th04/main/player/player.hpp"
#include "th04/snd/snd.h"

#pragma codeseg B4M_UPDATE_TEXT main_03
#pragma option -a

extern unsigned char bullet_special_speed_delta;
extern unsigned char yuuka5_move_state;
#endif
extern unsigned char yuuka5_palette_tone;
extern bool palette_changed;
extern unsigned int __cdecl PaletteTone;
extern int midboss_frames_until;
extern func_t_near stage_vm;
extern "C" void pascal far nullfunc_far(void);
extern nearfunc_t_near bg_render_bombing_func;
extern unsigned char tiles_bb_col;
extern unsigned char bullet_clear_time;
extern unsigned char bullet_zap_active;
extern unsigned char player_invincibility_time;
extern SPPoint homing_target;

#pragma codeseg MAI_TEXT main_01
extern void pascal near yuuka5_bg_render(void);
#pragma codeseg B4M_UPDATE_TEXT main_03

extern "C" void near thicklaser_add(void);
extern "C" void near thicklasers_update(void);
extern void pascal near hud_hp_update_and_render(int hp_cur, int hp_max);
extern void pascal near boss_explode_big(unsigned int type);

extern unsigned char pascal near yuuka5_move_transition(unsigned int centered);
extern void near yuuka5_pattern_sweep(void);
extern void near yuuka5_pattern_clouds(void);
extern void near yuuka5_pattern_gather(void);

void near yuuka5_pattern_speedup_ring(void)
{
    if(boss.phase_frame == 1) {
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_CROSS_YELLOW;
        bullet_template.group = BG_RING_AIMED;
        bullet_template.delta.spread_angle = 6;
        bullet_template.speed.v = TO_SP(1);
        bullet_template.special_motion = BSM_SPEEDUP;
        bullet_template.count = 8;
        bullet_special_speed_delta = 1;
    } else if(boss.phase_frame == 170) {
        boss.mode = -1;
        boss.phase_frame = 0;
    }

    if((boss.phase_frame % 16) == 15) {
        bullets_add_special();
        bullet_template.count += 3;
        snd_se_play(3);
    }
}

void near yuuka5_pattern_aimed_spread(void)
{
    if(boss.phase_frame == 1) {
        bullet_template.angle = static_cast<unsigned char>(iatan2(
            (player_pos.cur.y.v - bullet_template.origin.y.v),
            (player_pos.cur.x.v - bullet_template.origin.x.v)
        ));
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 5;
        bullet_template.delta.spread_angle = 0x42;
        bullet_template.speed.v = TO_SP(5);
        bullet_template_tune();
    } else if(boss.phase_frame == 128) {
        boss.mode = -1;
        boss.phase_frame = 0;
    }

    if((boss.phase_frame % 8) == 7) {
        bullet_template.delta.spread_angle -= 4;
        bullets_add_regular();
        snd_se_play(3);
    }
}

void near yuuka5_pattern_laser_burst(void)
{
    switch(boss.phase_frame) {
    case 0x10:
        gather_template.angle_delta = 3;
        break;

    case 0x30:
        bullet_template.angle = 0;
        snd_se_play(8);
        yuuka5_palette_tone = 100;
        // fallthrough
    case 0x38:
    case 0x40:
    case 0x48:
    case 0x50:
        circles_color = V_WHITE;
        circles_add_shrinking(
            bullet_template.origin.x.v,
            bullet_template.origin.y.v
        );
        // fallthrough
    case 0x28:
        gather_template.angle_delta = -gather_template.angle_delta;
        gather_template.center.x.v = bullet_template.origin.x.v;
        gather_template.center.y.v = bullet_template.origin.y.v;
        gather_template.ring_points = 8;
        gather_template.col = 9;
        gather_template.radius.v = TO_SP(256);
        // fallthrough
    case 0x2C:
    case 0x34:
    case 0x3C:
    case 0x44:
    case 0x4C:
    case 0x54:
    gather_add:
        gather_add_only();
        break;

    case 0x2A:
    case 0x32:
    case 0x3A:
    case 0x42:
    case 0x4A:
    case 0x52:
        gather_template.col = 8;
        goto gather_add;

    case 0x60:
        thicklaser_template.origin.x.v = bullet_template.origin.x.v;
        thicklaser_template.origin.y.v = bullet_template.origin.y.v;
        thicklaser_template.radius_max = boss_statebyte[0];
        thicklaser_template.radius_speed = 6;
        thicklaser_template.line_frames = 32;
        thicklaser_template.static_frames = 144;
        thicklaser_template.col_outline = 8;
        thicklaser_add();
        break;
    }

    if(boss.phase_frame < 128) {
        return;
    }
    if(boss.phase_frame <= 160) {
        yuuka5_palette_tone += 2;
        PaletteTone = yuuka5_palette_tone;
        palette_changed = true;
    } else if(yuuka5_palette_tone > 100) {
        _AL = static_cast<unsigned char>(boss.phase_frame & 1);
        _DL = yuuka5_palette_tone;
        _DL -= _AL;
        yuuka5_palette_tone = _DL;
        PaletteTone = yuuka5_palette_tone;
        palette_changed = true;
    }

    if(boss.phase_frame < 128) {
        return;
    }
    if((boss.phase_frame % 32) == 0) {
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.group = BG_RING;
        bullet_template.count = 32;
        bullet_template.patnum = PAT_BULLET16_D_BLUE;
        bullet_template.speed.v = (TO_SP(4) + 8);
        bullet_template_tune();
        bullets_add_regular();
        bullet_template.angle += 2;
        snd_se_play(9);
    }

    if((boss.phase_frame >= 192) && (stage_frame_mod2 != 0)) {
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.group = BG_RANDOM_ANGLE;
        bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_BLUE;
        bullet_template.speed.v = TO_SP(2);
        bullet_template.count = 2;
        bullet_template_tune();
        bullets_add_regular();
    }
}

void near yuuka5_pattern_mirrored_streams(void)
{
    if(boss.phase_frame == 48) {
        circles_add_shrinking(
            bullet_template.origin.x.v,
            bullet_template.origin.y.v
        );
        circles_color = V_WHITE;
        boss.angle = 16;
        boss_statebyte[15] = 0x10;
        bullet_template.special_motion = BSM_NONE;
        return;
    }
    if(boss.phase_frame < 64) {
        return;
    }
    if((boss.phase_frame % 8) != 0) {
        return;
    }

    bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
    bullet_template.count = 5;
    bullet_template.delta.spread_angle = 1;
    bullet_template.group = BG_SPREAD;
    bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
    bullet_template.speed.v = (TO_SP(2) + 8);
    bullet_template_tune();

    bullet_template.origin.x.v += TO_SP(32);
    bullet_template.angle = boss.angle;
    bullets_add_special();
    bullet_template.origin.x.v -= TO_SP(64);
    bullet_template.angle = static_cast<unsigned char>(0x80 - boss.angle);
    bullets_add_special();
    boss.angle -= 16;

    bullet_template.spawn_type = BST_PELLET;
    bullet_template.count = 3;
    bullet_template.speed.v = (TO_SP(1) + 8);
    bullet_template_tune();
    bullet_template.angle = boss_statebyte[15];
    bullets_add_special();
    bullet_template.origin.x.v += TO_SP(64);
    bullet_template.angle = static_cast<unsigned char>(0x80 - boss_statebyte[15]);
    bullets_add_special();
    boss_statebyte[15] += 9;
    snd_se_play(3);
}

void pascal far yuuka5_update(void)
{
    bullet_template.origin.x.v = boss.pos.cur.x.v;
    bullet_template.origin.y.v = (boss.pos.cur.y.v + TO_SP(16));

    switch(boss.phase) {
    case 0:
        if(boss.phase_frame == 0) {
            stage_vm = nullfunc_far;
            midboss_frames_until = 0;
        }
        boss_hittest_shots_invincible();
        if(boss.phase_frame <= 128) {
            goto update_tail;
        }
        boss.phase++;
        boss.phase_frame = 0;
        snd_se_play(13);
        yuuka5_move_state = 0;
        tiles_bb_col = V_WHITE;
        bg_render_bombing_func = yuuka5_bg_render;
        goto update_tail;

    case 1:
        boss_hittest_shots_invincible();
        if(boss.phase_frame == 32) {
            Palettes[0].c.r = 64;
            Palettes[0].c.g = 64;
            Palettes[0].c.b = 64;
            palette_changed = true;
        }
        if(boss.phase_frame < 64) {
            goto update_tail;
        }
        boss.phase++;
        boss.pos.velocity.x.v = 0;
        boss.phase_state.patterns_seen = 0;
        boss.mode = 0;
        boss.hp = 9000;
        boss.phase_end_hp = 7900;
        boss.phase_frame = 0;
        boss.pos.cur.y.v -= TO_SP(16);
        goto update_tail;

    case 2:
    case 5:
    case 8:
        switch(boss.mode) {
        case 0:
            yuuka5_pattern_sweep();
            break;
        case 1:
            yuuka5_pattern_clouds();
            break;
        case 0xFE:
            boss.phase_frame = 0;
            boss.phase_state.patterns_seen++;
            boss.mode = (boss.phase_state.patterns_seen % 2);
            break;
        case 0xFF:
            yuuka5_move_transition(0);
            break;
        }
        if(yuuka5_move_state == 0) {
            if(boss.phase_state.patterns_seen < 4) {
                if(!boss_hittest_shots()) {
                    goto update_tail;
                }
                boss_score_bonus(15);
                boss_items_drop();
            }
            if(bullet_clear_time < 20) {
                bullet_clear_time = 20;
            }
            boss_explode_small(ET_CIRCLE);
            boss.phase++;
            boss.hp = boss.phase_end_hp;
            boss.phase_end_hp -= 800;
            goto update_tail;
        }
        boss.phase_frame++;
        goto update_tail;

    case 3:
    case 6:
    case 9:
        boss.phase_frame++;
        if(!yuuka5_move_transition(1)) {
            goto update_tail;
        }
        boss.phase++;
        boss.phase_frame = 0;
        boss.phase_state.patterns_seen = 0;
        boss.mode = 0;
        goto update_tail;

    case 4:
    case 7:
    case 10:
        yuuka5_pattern_gather();
        if(boss.phase_frame < 500) {
            if(!boss_hittest_shots()) {
                goto update_tail;
            }
            boss_score_bonus(15);
            boss_items_drop();
        }
        if(bullet_clear_time < 20) {
            bullet_clear_time = 20;
        }
        boss_explode_small(ET_NW_SE);
        boss.phase++;
        boss.phase_frame = 0;
        boss.phase_state.patterns_seen = 0;
        boss.mode = 0;
        boss.hp = boss.phase_end_hp;
        if(boss.phase < 10) {
            boss.phase_end_hp -= 1100;
        } else {
            boss.phase_end_hp -= 1200;
        }
        goto update_tail;

    case 11:
    case 14:
        switch(boss.mode) {
        case 0:
            yuuka5_pattern_speedup_ring();
            break;
        case 1:
            yuuka5_pattern_aimed_spread();
            break;
        case 0xFE:
            boss.phase_frame = 0;
            boss.phase_state.patterns_seen++;
            boss.mode = (boss.phase_state.patterns_seen % 2);
            break;
        case 0xFF:
            yuuka5_move_transition(0);
            break;
        }
        if(yuuka5_move_state == 0) {
            if(boss.phase_state.patterns_seen < 4) {
                if(!boss_hittest_shots()) {
                    goto update_tail;
                }
                boss_score_bonus(15);
                boss_items_drop();
            }
            if(bullet_clear_time < 20) {
                bullet_clear_time = 20;
            }
            boss_explode_small(ET_CIRCLE);
            boss.phase++;
            boss.hp = boss.phase_end_hp;
            goto update_tail;
        }
        boss.phase_frame++;
        goto update_tail;

    case 12:
    case 15:
        boss.phase_frame++;
        if(!yuuka5_move_transition(1)) {
            goto update_tail;
        }
        boss.phase++;
        boss.phase_frame = 0;
        boss.phase_state.patterns_seen = 0;
        boss.mode = 0;
        goto update_tail;

    case 13:
    case 16:
        yuuka5_pattern_laser_burst();
        boss_hittest_shots_invincible();
        if(boss.phase_frame < 288) {
            goto update_tail;
        }
        boss_explode_small(ET_VERTICAL);
        if(bullet_clear_time < 20) {
            bullet_clear_time = 20;
        }
        boss.phase++;
        boss.hp = boss.phase_end_hp;
        if(boss.phase == 17) {
            boss.phase_end_hp = 0;
            Palettes[0].c.r = 128;
            Palettes[0].c.g = 64;
            Palettes[0].c.b = 64;
            palette_changed = true;
        } else {
            boss.phase_end_hp -= 1200;
        }
        boss.phase_frame = 0;
        boss.phase_state.patterns_seen = 0;
        boss.mode = 0;
        PaletteTone = 100;
        palette_changed = true;
        goto update_tail;

    case 17:
        yuuka5_pattern_mirrored_streams();
        if(!boss_hittest_shots() && (boss.phase_frame < 1000)) {
            goto update_tail;
        }
        boss_explode_small(ET_NW_SE);
        boss.phase++;
        if(boss.phase_frame < 1000) {
            boss.phase_state.defeat_bonus = true;
        } else {
            boss.phase_state.defeat_bonus = false;
        }
        boss.phase_frame = 0;
        boss.mode = 0;
        PaletteTone = 100;
        palette_changed = true;
        goto update_tail;

    case 18:
        boss.phase_frame++;
        if(boss.phase_frame == 16) {
            boss_explode_small(ET_VERTICAL);
        }
        if(boss.phase_frame == 32) {
            boss_explode_big(static_cast<unsigned int>(ET_SW_NE));
            boss.phase = PHASE_EXPLODE_BIG;
            bullet_zap_active = boss.phase_state.defeat_bonus;
            if(boss.phase_state.defeat_bonus != 0) {
                boss_score_bonus(60);
            }
            boss.sprite = PAT_ENEMY_KILL;
            boss.phase_frame = 0;
            snd_se_play(12);
            Palettes[0].c.r = 0;
            Palettes[0].c.g = 0;
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
    thicklasers_update();
    hud_hp_update_and_render(boss.hp, 9000);
}

#pragma codeseg
