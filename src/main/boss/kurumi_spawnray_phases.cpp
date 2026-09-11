#pragma option -zCMAIN_033_TEXT -zPmain_03

#include "compat/rec98/th02/v_colors.hpp"
#include "compat/rec98/th03/math/randring.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/circle.hpp"
#include "th04/snd/snd.h"

void pascal near kurumi_spawnrays_add(
    subpixel_t distance_from_center_x, unsigned char angle
);
bool near kurumi_spawnrays_update(void);

extern "C" void near kurumi_spawnray_phase_left(void)
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
        kurumi_spawnrays_add(
            -TO_SP(12),
            (0x18 - randring2_next16_and(0xF))
        );
        return;
    }

    if(boss.phase_frame <= 64) {
        return;
    }

    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_BLUE;
    bullet_template.angle = 0;
    bullet_template.group = BG_RING_AIMED;
    bullet_template.count = 16;
    bullet_template_tune();
    if(kurumi_spawnrays_update()) {
        boss.phase_frame = 0;
        boss.mode = 0;
    }
}

extern "C" void near kurumi_spawnray_phase_right(void)
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
        kurumi_spawnrays_add(
            TO_SP(12),
            (randring2_next16_and(0xF) + 0x68)
        );
        return;
    }

    if(boss.phase_frame <= 64) {
        return;
    }

    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_BLUE;
    bullet_template.angle = 0;
    bullet_template.group = BG_RING_AIMED;
    bullet_template.count = 16;
    bullet_template_tune();
    if(kurumi_spawnrays_update()) {
        boss.phase_frame = 0;
        boss.mode = 0;
    }
}

extern "C" void near kurumi_spawnray_phase_dual(void)
{
    unsigned char angle;

    if(boss.phase_frame == 16) {
        boss.sprite = 10;
        return;
    }

    if(boss.phase_frame == 48) {
        circles_add_shrinking(
            (boss.pos.cur.x.v + TO_SP(12)),
            (boss.pos.cur.y.v - TO_SP(10))
        );
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
        angle = (randring2_next16_and(0xF) + 0x68);
        kurumi_spawnrays_add(TO_SP(12), angle);
        kurumi_spawnrays_add(-TO_SP(12), (0x80 - angle));
        return;
    }

    if(boss.phase_frame <= 64) {
        return;
    }

    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_BLUE;
    bullet_template.angle = 0;
    bullet_template.group = BG_RING_AIMED;
    bullet_template.count = 8;
    bullet_template_tune();
    if(kurumi_spawnrays_update()) {
        boss.phase_frame = 0;
        boss.mode = 0;
    }
}
