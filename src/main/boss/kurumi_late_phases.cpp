#pragma option -zCMAIN_033_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "compat/rec98/th03/math/randring.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/circle.hpp"
#include "th04/snd/snd.h"

void pascal near kurumi_spawnrays_add(
    subpixel_t distance_from_center_x, unsigned char angle
);
bool near kurumi_spawnrays_update(void);

extern unsigned char bullet_special_turns_max;
extern unsigned char kurumi_special_turn_toggle;
extern "C" void near kurumi_orbit_step_reverse(void);

extern "C" void near kurumi_turning_bullets_phase(void)
{
    kurumi_orbit_step_reverse();

    if(boss.angle > 0x80) {
        boss.sprite = 4;
    } else {
        boss.sprite = 6;
    }

    if((stage_frame % 57) != 0) {
        return;
    }

    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_BLUE;
    bullet_template.origin = boss.pos.cur;
    bullet_template.group = BG_RING_AIMED;
    bullet_template.count = 16;
    bullet_template.special_motion = BSM_DECELERATE_THEN_TURN;
    bullet_template.speed.v = TO_SP(3);
    bullet_template.angle = randring2_next16();
    bullet_special_turns_max = 1;

    if(kurumi_special_turn_toggle & 1) {
        _AL = 0x40;
    } else {
        _AL = -0x40;
    }
    bullet_template_special_angle.turn_by = _AL;

    bullet_template_tune();
    bullets_add_special();

    bullet_template_special_angle.turn_by += 0x80;
    bullet_template.speed.v = TO_SP(2);
    bullet_template.angle = randring2_next16();
    bullets_add_special();
    kurumi_special_turn_toggle++;
}

extern "C" void near kurumi_spawnray_pattern_left(void)
{
    if(boss.phase_frame == 16) {
        boss.sprite = 8;
        return;
    }

    if(boss.phase_frame == 48) {
        circles_add_shrinking(
            (boss.pos.cur.x.v - TO_SP(12)),
            (boss.pos.cur.y.v - TO_SP(10))
        );
        circles_color = V_WHITE;
        snd_se_play(8);
        return;
    }

    if(boss.phase_frame == 64) {
        boss.sprite = 0;
        kurumi_spawnrays_add(-TO_SP(12), 0x18);
        return;
    }

    if(boss.phase_frame <= 64) {
        return;
    }

    if(boss.phase_frame == 80) {
        kurumi_spawnrays_add(-TO_SP(12), 0x10);
    } else if(boss.phase_frame == 96) {
        kurumi_spawnrays_add(-TO_SP(12), 0x08);
    }

    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_BLUE;
    bullet_template.angle = 0;
    bullet_template.group = BG_RING_AIMED;
    bullet_template.count = 12;
    bullet_template_tune();
    if(kurumi_spawnrays_update()) {
        boss.phase_frame = 0;
        boss.mode = 0;
    }
}

extern "C" void near kurumi_spawnray_pattern_right(void)
{
    if(boss.phase_frame == 16) {
        boss.sprite = 9;
        return;
    }

    if(boss.phase_frame == 48) {
        circles_add_shrinking(
            (boss.pos.cur.x.v + TO_SP(12)),
            (boss.pos.cur.y.v - TO_SP(10))
        );
        circles_color = V_WHITE;
        snd_se_play(8);
        return;
    }

    if(boss.phase_frame == 64) {
        boss.sprite = 0;
        kurumi_spawnrays_add(TO_SP(12), 0x68);
        return;
    }

    if(boss.phase_frame <= 64) {
        return;
    }

    if(boss.phase_frame == 80) {
        kurumi_spawnrays_add(TO_SP(12), 0x70);
    } else if(boss.phase_frame == 96) {
        kurumi_spawnrays_add(TO_SP(12), 0x78);
    }

    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_BLUE;
    bullet_template.angle = 0;
    bullet_template.group = BG_RING_AIMED;
    bullet_template.count = 12;
    bullet_template_tune();
    if(kurumi_spawnrays_update()) {
        boss.phase_frame = 0;
        boss.mode = 0;
    }
}

extern "C" void near kurumi_spawnray_pattern_dual(void)
{
    if(boss.phase_frame == 16) {
        boss.sprite = 10;
        return;
    }

    if(boss.phase_frame == 48) {
        circles_add_shrinking(
            (boss.pos.cur.x.v - TO_SP(12)),
            (boss.pos.cur.y.v - TO_SP(10))
        );
        circles_add_shrinking(
            (boss.pos.cur.x.v + TO_SP(12)),
            (boss.pos.cur.y.v - TO_SP(10))
        );
        circles_color = V_WHITE;
        snd_se_play(8);
        return;
    }

    if(boss.phase_frame == 64) {
        boss.sprite = 0;
        kurumi_spawnrays_add(-TO_SP(12), 0x18);
        kurumi_spawnrays_add(TO_SP(12), 0x68);
        return;
    }

    if(boss.phase_frame <= 64) {
        return;
    }

    if(boss.phase_frame == 80) {
        kurumi_spawnrays_add(-TO_SP(12), 0x10);
        kurumi_spawnrays_add(TO_SP(12), 0x70);
    } else if(boss.phase_frame == 96) {
        kurumi_spawnrays_add(-TO_SP(12), 0x08);
        kurumi_spawnrays_add(TO_SP(12), 0x78);
    }

    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_BLUE;
    bullet_template.angle = 0;
    bullet_template.group = BG_RING_AIMED;
    bullet_template.count = 6;
    bullet_template_tune();
    if(kurumi_spawnrays_update()) {
        boss.phase_frame = 0;
        boss.mode = 0;
    }
}
