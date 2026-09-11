#pragma option -zCMAIN_033_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/gather.hpp"
#include "th04/main/circle.hpp"
#include "th04/main/spark.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

extern bool palette_changed;
extern nearfunc_t_near bg_render_bombing_func;
extern unsigned char tiles_bb_col;
extern unsigned char bullet_zap;
extern unsigned char player_invincibility_time;
extern SPPoint homing_target;
extern void pascal near hud_hp_update_and_render(int hp_cur, int hp_max);
extern void pascal near boss_explode_big(unsigned int type);

#pragma codeseg MAI_TEXT main_01
extern void pascal near orange_bg_render(void);
#pragma codeseg

extern "C" void near orange_phase_random_rings(void);
extern "C" void near orange_phase_aimed_clouds(void);
extern "C" void near orange_phase_ring16(void);
extern "C" void near orange_phase_side_rings(void);
extern "C" void near orange_phase_bounce_random(void);

static void near orange_phase_multi_burst(void)
{
    if(
        (boss.phase_frame == 96) ||
        (boss.phase_frame == 160) ||
        (boss.phase_frame == 224) ||
        (boss.phase_frame == 288)
    ) {
        gather_template.center.x.v = bullet_template.origin.x.v;
        gather_template.center.y.v = bullet_template.origin.y.v;
        gather_add_only();
    }

    if(
        (boss.phase_frame == 112) ||
        (boss.phase_frame == 160) ||
        (boss.phase_frame == 240) ||
        (boss.phase_frame == 304)
    ) {
        circles_add_shrinking(
            bullet_template.origin.x.v,
            bullet_template.origin.y.v
        );
        circles_color = V_WHITE;
    }

    if(stage_frame_mod4 != 0) {
        return;
    }

    bullet_template.spawn_type = BST_PELLET;
    bullet_template.group = BG_SINGLE;
    boss.angle -= 7;
    bullet_template.speed.v = TO_SP(2);
    bullet_template.angle = boss.angle;
    bullet_template_tune();
    bullets_add_regular_fixedspeed();

    if(boss.phase_frame < 128) {
        return;
    }
    if(boss.phase_frame < 192) {
        goto add_last_regular;
    }
    if(boss.phase_frame < 256) {
        goto add_two_regular;
    }
    if(boss.phase_frame >= 320) {
        goto add_extra;
    }

    bullet_template.angle += 0x40;
    bullets_add_regular_fixedspeed();
add_two_regular:
    bullet_template.angle += 0x40;
    bullets_add_regular_fixedspeed();
add_last_regular:
    _AL = static_cast<unsigned char>(bullet_template.angle + 0x40);
    goto add_last;

add_extra:
    bullet_template.angle += 0x40;
    bullets_add_regular_fixedspeed();
    bullet_template.angle += 0x40;
    bullets_add_regular_fixedspeed();
    bullet_template.angle += 0x40;
    bullets_add_regular_fixedspeed();
    bullet_template.speed.v += TO_SP(1);
    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_WHITE;
    bullet_template.angle = static_cast<unsigned char>(
        -bullet_template.angle - 0x20
    );
    bullets_add_regular_fixedspeed();
    _AL = static_cast<unsigned char>(bullet_template.angle + 0x80);

add_last:
    bullet_template.angle = _AL;
    bullets_add_regular_fixedspeed();
}

void pascal far orange_update(void)
{
    register int i;

    gather_template.center.x.v = boss.pos.cur.x.v;
    gather_template.center.y.v = boss.pos.cur.y.v;

    switch(boss.phase) {
    case 0:
        if(boss.phase_frame == 0) {
            boss.hp = 3050;
            boss.phase_end_hp = 1950;
            Palettes[0].c.r = 0;
            Palettes[0].c.g = 0;
            Palettes[0].c.b = 96;
            palette_changed = true;
        }
        boss.phase_frame++;
        if(boss.phase_frame == 192) {
            boss.sprite += 2;
            snd_se_play(8);
            gather_template.center.x.v = boss.pos.cur.x.v + TO_SP(8);
            gather_template.center.y.v = boss.pos.cur.y.v - TO_SP(40);
            gather_template.radius.v = TO_SP(320);
            gather_template.ring_points = 32;
            gather_template.angle_delta = 3;
            gather_template.col = 7;
        } else if(boss.phase_frame > 320) {
            if(boss.phase_frame == 336) {
                gather_template.col = 6;
            }
            if((boss.phase_frame & 7) == 0) {
                gather_add_only();
            }
            if(boss.phase_frame >= 352) {
                boss.phase++;
                boss.phase_frame = 0;
                snd_se_play(13);
                boss_statebyte[15] = 0;
                boss_statebyte[14] = static_cast<unsigned char>(-1);
                bg_render_bombing_func = orange_bg_render;
                tiles_bb_col = 0;
            }
        }
        boss_hittest_shots_damage(TO_SP(16), TO_SP(16), 10);
        goto update_tail;

    case 1:
        boss.phase_frame++;
        if(boss.phase_frame >= 32) {
            gather_template.radius.v = TO_SP(64);
            gather_template.angle_delta = 2;
            gather_template.ring_points = 8;
            boss.phase = 2;
            boss.phase_frame = 0;
            boss.mode = 0;
            boss.sprite += 2;
            bullet_template.spawn_type = BST_PELLET;
            bullet_template.origin.x.v = boss.pos.cur.x.v;
            bullet_template.origin.y.v = boss.pos.cur.y.v;
            bullet_template.group = BG_RING;
            bullet_template.count = 16;
            bullet_template.speed.v = TO_SP(4);
            bullet_template.angle = 0;
            bullet_template_tune();
            for(i = 0; i < 3; i++) {
                bullets_add_regular();
                bullet_template.speed.v -= TO_SP(1);
            }
            snd_se_play(6);
        }
        boss_hittest_shots_damage(TO_SP(16), TO_SP(16), 10);
        goto update_tail;

    case 2:
        switch(boss.mode) {
        case 0:
            boss.phase_frame = 0;
            do {
                boss.mode = static_cast<unsigned char>(randring2_next16_and(3) + 1);
            } while(boss_statebyte[14] == boss.mode);
            boss_statebyte[14] = boss.mode;
            boss_statebyte[15]++;
            if(boss_statebyte[15] >= 16) {
                goto phase_2_next;
            }
            break;
        case 1:
            orange_phase_random_rings();
            break;
        case 2:
            orange_phase_aimed_clouds();
            break;
        case 3:
            orange_phase_ring16();
            break;
        case 4:
            orange_phase_side_rings();
            break;
        }
        if(!boss_hittest_shots()) {
            goto update_tail;
        }
        boss_score_bonus(5);
    phase_2_next:
        boss_phase_next(ET_NW_SE, 450);
        Palettes[0].c.r = 112;
        Palettes[0].c.b = 112;
        palette_changed = true;
        goto update_tail;

    case 3:
        switch(boss.mode) {
        case 0:
            if(boss.phase_frame > 128) {
                boss.phase_frame = 0;
                boss.mode = 1;
            }
            break;
        case 1:
            orange_phase_bounce_random();
            break;
        }
        if(boss.phase_frame <= 1500) {
            if(!boss_hittest_shots()) {
                goto update_tail;
            }
            boss_score_bonus(5);
        }
        boss_phase_next(ET_NW_SE, 0);
        boss.sprite += 4;
        Palettes[0].c.r = 144;
        Palettes[0].c.b = 32;
        palette_changed = true;
        gather_template.col = 9;
        goto update_tail;

    case 4:
        bullet_template.origin.x.v = boss.pos.cur.x.v + TO_SP(8);
        bullet_template.origin.y.v = boss.pos.cur.y.v - TO_SP(16);
        switch(boss.mode) {
        case 0:
            if(boss.phase_frame == 96) {
                gather_template.center.x.v = bullet_template.origin.x.v;
                gather_template.center.y.v = bullet_template.origin.y.v;
                gather_add_only();
            }
            if(boss.phase_frame == 112) {
                circles_add_shrinking(
                    bullet_template.origin.x.v,
                    bullet_template.origin.y.v
                );
                circles_color = V_WHITE;
            }
            if(boss.phase_frame > 128) {
                boss.phase_frame = 0;
                boss.mode = 1;
            }
            if(boss.pos.cur.x.v < TO_SP(191)) {
                boss.pos.velocity.x.v = 24;
            } else if(boss.pos.cur.x.v > TO_SP(193)) {
                boss.pos.velocity.x.v = -24;
            }
            if(boss.pos.cur.y.v < TO_SP(79)) {
                boss.pos.velocity.y.v = 12;
            } else if(boss.pos.cur.y.v > TO_SP(81)) {
                boss.pos.velocity.y.v = -12;
            }
            boss.pos.update_seg3();
            break;
        case 1:
            orange_phase_multi_burst();
            break;
        }
        if(boss.phase_frame <= 600) {
            if(!boss_hittest_shots()) {
                goto update_tail;
            }
        }
        if(boss.phase_frame <= 600) {
            boss.phase_state.defeat_bonus = true;
        } else {
            boss.phase_state.defeat_bonus = false;
        }
        boss_explode_small(ET_HORIZONTAL);
        boss.phase++;
        boss.phase_frame = 0;
        boss.mode = 0;
        sparks_add_circle(boss.pos.cur.x, boss.pos.cur.y, TO_SP(8), 48);
        goto update_tail;

    case 5:
        if(boss.pos.cur.x.v < TO_SP(191)) {
            boss.pos.velocity.x.v = 24;
        } else if(boss.pos.cur.x.v > TO_SP(193)) {
            boss.pos.velocity.x.v = -24;
        }
        if(boss.pos.cur.y.v < TO_SP(79)) {
            boss.pos.velocity.y.v = 12;
        } else if(boss.pos.cur.y.v > TO_SP(81)) {
            boss.pos.velocity.y.v = -12;
        }
        boss.pos.update_seg3();
        boss.phase_frame++;
        if(boss.phase_frame == 16) {
            boss_explode_small(ET_VERTICAL);
        }
        if(boss.phase_frame == 32) {
            boss_explode_big(static_cast<unsigned int>(ET_CIRCLE));
            boss.phase = PHASE_EXPLODE_BIG;
            bullet_zap = boss.phase_state.defeat_bonus;
            if(boss.phase_state.defeat_bonus != 0) {
                boss_score_bonus(10);
            }
            boss.sprite = 4;
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
    hud_hp_update_and_render(boss.hp, 3050);
}
