#pragma option -zCMAIN_033_TEXT -zPmain_03

#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

extern "C" void near kurumi_bullet_stacks_phase(void)
{
    if(boss.phase_frame < 16) {
        return;
    }

    if(boss.phase_frame == 16) {
        boss_statebyte[15] = static_cast<unsigned char>(
            -0x20 - randring2_next16_and(0xF)
        );
        boss_statebyte[14] = static_cast<unsigned char>(
            randring2_next16_and(0xF) + 0xA0
        );
        boss_statebyte[13] = 0;
        bullet_template.patnum = PAT_BULLET16_D_BLUE;
    }

    if((boss.phase_frame % 8) == 0) {
        bullet_template.speed.v = TO_SP(1);
        boss_statebyte[15] += 0x10;
        boss_statebyte[14] -= 0x10;
        boss_statebyte[13]++;
        if(boss_statebyte[13] > 10) {
            boss_statebyte[15] = static_cast<unsigned char>(
                -0x20 - randring2_next16_and(0xF)
            );
            boss_statebyte[14] = static_cast<unsigned char>(
                randring2_next16_and(0xF) + 0xA0
            );
            boss_statebyte[13] = 0;
        }
        snd_se_play(15);
    }

    bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
    bullet_template.group = BG_SINGLE;
    bullet_template.origin.y.v = (boss.pos.cur.y.v - TO_SP(10));
    bullet_template.origin.x.v = (boss.pos.cur.x.v + TO_SP(12));
    bullet_template.angle = boss_statebyte[15];
    bullets_add_regular_fixedspeed();

    bullet_template.origin.x.v -= TO_SP(24);
    bullet_template.angle = boss_statebyte[14];
    bullets_add_regular_fixedspeed();

    bullet_template.speed.v += 10;
    if((boss.phase_frame % boss_statebyte[0]) != 0) {
        return;
    }

    bullet_template.group = BG_SPREAD_AIMED;
    bullet_template.count = 5;
    bullet_template.delta.spread_angle = 9;
    bullet_template.angle = 0;
    bullet_template.spawn_type = BST_PELLET;
    bullet_template.speed.v = (randring2_next16_and(0xF) + TO_SP(2));
    bullet_template.special_motion = BSM_NONE;
    bullet_template_tune();
    bullets_add_special();
}
