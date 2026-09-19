#ifndef TH04_YUUKA5_COMBINED
#pragma option -zCB4M_UPDATE_TEXT -zPmain_03

#include "src/shared/runtime/api.hpp"
#include "src/shared/hardware/v_colors.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/circle.hpp"
#include "th04/main/gather.hpp"
#include "th04/main/rank.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

#pragma codeseg B4M_UPDATE_TEXT main_03
#pragma option -a
#endif

extern int yuuka5_sweep_x;
extern unsigned char yuuka5_cloud_step;
extern unsigned char yuuka5_cloud_accum;
extern unsigned char yuuka5_move_state;
extern unsigned char bullet_special_speed_delta;
extern unsigned char bullet_special_turns_max;

unsigned char pascal near yuuka5_move_transition(unsigned int centered)
{
    register int target_x;
    register int target_y;

    if(yuuka5_move_state == 0) {
        yuuka5_move_state = 1;
        boss.damage_this_frame = 0;
        boss.pos.cur.y.v += TO_SP(16);
    }

    if(yuuka5_move_state == 1) {
        if(boss.phase_frame < 32) {
            return 0;
        }
        boss.phase_frame = 0;
        yuuka5_move_state = 2;
        if(centered == 0) {
            target_x = (randring2_next16_mod(TO_SP(256)) + TO_SP(64));
            target_y = (randring2_next16_mod(TO_SP(64)) + TO_SP(64));
        } else {
            target_x = TO_SP(PLAYFIELD_W / 2);
            target_y = TO_SP(80);
        }
        boss.pos.velocity.x.v = ((target_x - boss.pos.cur.x.v) / 64);
        boss.pos.velocity.y.v = ((target_y - boss.pos.cur.y.v) / 64);
        return 0;
    }

    if(yuuka5_move_state == 2) {
        boss.pos.update_seg3();
        if(boss.phase_frame < 64) {
            return 0;
        }
        boss.phase_frame = 0;
        yuuka5_move_state = 3;
        return 0;
    }

    if(yuuka5_move_state == 3) {
        if(boss.phase_frame < 8) {
            return 0;
        }
        boss.phase_frame = 0;
        yuuka5_move_state = 0;
        boss.mode = -2;
        boss.pos.cur.y.v -= TO_SP(16);
        return 1;
    }
    return 0;
}

void near yuuka5_pattern_sweep(void)
{
    if(boss.phase_frame == 1) {
        yuuka5_sweep_x = (boss.pos.cur.x.v - TO_SP(32));
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_CROSS_YELLOW;
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 11;
        bullet_template.delta.spread_angle = 5;
        bullet_template.speed.v = (TO_SP(2) + 8);
        bullet_template_tune();
    } else if(boss.phase_frame == 15) {
        bullet_template.angle = 0x00;
    } else if(boss.phase_frame == 31) {
        yuuka5_sweep_x += TO_SP(64);
        bullet_template.angle = 0x80;
    } else if(boss.phase_frame == 47) {
        yuuka5_sweep_x -= TO_SP(64);
        bullet_template.angle = 0x10;
    } else if(boss.phase_frame == 63) {
        yuuka5_sweep_x += TO_SP(64);
        bullet_template.angle = 0x70;
    } else if(boss.phase_frame == 79) {
        yuuka5_sweep_x -= TO_SP(64);
        bullet_template.angle = 0x20;
    } else if(boss.phase_frame == 95) {
        yuuka5_sweep_x += TO_SP(64);
        bullet_template.angle = 0x60;
    } else if(boss.phase_frame == 111) {
        yuuka5_sweep_x -= TO_SP(64);
        bullet_template.angle = 0x30;
    } else if(boss.phase_frame == 127) {
        yuuka5_sweep_x += TO_SP(64);
        bullet_template.angle = 0x50;
    } else if(boss.phase_frame == 140) {
        boss.mode = -1;
        boss.phase_frame = 0;
    }

    if((boss.phase_frame % 16) == 15) {
        bullet_template.origin.x.v = yuuka5_sweep_x;
        bullet_template.origin.y.v = boss.pos.cur.y.v;
        bullets_add_regular();
        snd_se_play(3);
    }
}

void near yuuka5_pattern_clouds(void)
{
    if(boss.phase_frame == 1) {
        bullet_template.angle = 0;
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.patnum = PAT_BULLET16_D_BLUE;
        bullet_template.group = BG_RING;
        bullet_template.count = (rank + 1);
        bullet_template.speed.v = TO_SP(4);
        yuuka5_cloud_step = 1;
        yuuka5_cloud_accum = 0;
        return;
    }

    if(boss.phase_frame < 128) {
        if(yuuka5_cloud_accum >= 0x10) {
            bullet_template.angle += 7;
            bullets_add_regular();
            snd_se_play(3);
            yuuka5_cloud_step++;
            yuuka5_cloud_accum -= 0x10;
        }
        yuuka5_cloud_accum += yuuka5_cloud_step;
        return;
    }

    if(boss.phase_frame == 128) {
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_CROSS_YELLOW;
        bullet_template.angle = 0x80;
        bullet_template.speed.v = TO_SP(1);
        bullet_template.special_motion = BSM_SPEEDUP;
        bullet_special_speed_delta = 1;
        bullet_template.count = 32;
        bullet_template_tune();
        bullets_add_special_fixedspeed();
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.speed.v = TO_SP(4);
        bullet_template.count = (rank + 1);
        yuuka5_cloud_step = 1;
        yuuka5_cloud_accum = 0;
        snd_se_play(9);
        bullet_template.patnum = PAT_BULLET16_D_BLUE;
        return;
    }

    if(boss.phase_frame < 256) {
        if(yuuka5_cloud_accum >= 0x10) {
            bullet_template.angle -= 7;
            bullets_add_regular();
            snd_se_play(3);
            yuuka5_cloud_step++;
            yuuka5_cloud_accum -= 0x10;
        }
        yuuka5_cloud_accum += yuuka5_cloud_step;
        return;
    }

    if(boss.phase_frame == 256) {
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_CROSS_YELLOW;
        bullet_template.angle = 0;
        bullet_template.speed.v = TO_SP(1);
        bullet_template.special_motion = BSM_SPEEDUP;
        bullet_special_speed_delta = 1;
        bullet_template.count = 32;
        bullet_template_tune();
        bullets_add_special_fixedspeed();
        snd_se_play(9);
        return;
    }

    if(boss.phase_frame == 288) {
        boss.mode = -1;
        boss.phase_frame = 0;
    }
}

void near yuuka5_pattern_gather(void)
{
    switch(boss.phase_frame) {
    case 1:
        gather_template.center.x.v = bullet_template.origin.x.v;
        gather_template.center.y.v = bullet_template.origin.y.v;
        gather_template.ring_points = 32;
        gather_template.col = 11;
        gather_template.radius.v = TO_SP(256);
        gather_template.angle_delta = 3;
        gather_add_only();
        break;

    case 3:
        gather_template.col = 10;
        gather_add_only();
        break;

    case 5:
        gather_add_only();
        break;

    case 0x11:
        circles_add_shrinking(
            bullet_template.origin.x.v,
            bullet_template.origin.y.v
        );
        circles_color = V_WHITE;
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.speed.v = TO_SP(1);
        bullet_template.special_motion = BSM_BOUNCE_LEFT_RIGHT_TOP;
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 7;
        bullet_template.delta.spread_angle = 8;
        bullet_template.patnum = PAT_BULLET16_N_CROSS_YELLOW;
        bullet_template.speed.v = TO_SP(2);
        bullet_template_tune();
        bullet_special_turns_max = 1;
        break;
    }

    if((boss.phase_frame >= 32) && ((boss.phase_frame % 16) == 0)) {
        bullet_template.angle = randring2_next16();
        bullets_add_special();
        snd_se_play(9);
    }
}

#ifndef TH04_YUUKA5_COMBINED
#pragma codeseg
#endif
